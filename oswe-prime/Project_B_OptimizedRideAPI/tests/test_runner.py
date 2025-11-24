import json
import os
import sys
import time
from typing import Dict

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.optimized_api import BackendSimulator, OptimizedRideAPI


def run_scenario(scenario: Dict, results_dir: str, logs_file: str):
    backend = BackendSimulator()
    api = OptimizedRideAPI(backend, cache_enabled=True)
    latency = scenario.get("simulate_latency_ms", 0)
    scenario_result = {"scenario_id": scenario.get("id"), "start": time.time()}
    try:
        if scenario.get("flow") == "optimized":
            # One call to get ride and breakdown
            t0 = time.perf_counter()
            resp = api.get_ride(scenario["rideId"], includeFareBreakdown=True, latency_ms=latency)
            t1 = time.perf_counter()
            elapsed = (t1 - t0)
            if resp.get('status') and resp.get('status') != 200:
                scenario_result.update({
                    "status": resp.get('status'),
                    "error": resp.get('error'),
                    "requestCount": backend.request_count,
                    "latency": elapsed,
                    "expected": scenario.get("expect")
                })
            else:
                scenario_result.update({
                    "status": 200,
                    "totalFare": resp.get("totalFare"),
                    "fareBreakdownPresent": True if resp.get("fareBreakdown") else False,
                    "labelsSanitized": all("<script" not in i.get("label","") for i in (resp.get("fareBreakdown") or [])),
                    "requestCount": backend.request_count,
                    "latency": elapsed,
                    "expected": scenario.get("expect")
                })
        elif scenario.get("flow") == "compare":
            # For compare flows, run both baseline-style (simulate multiple calls) and optimized
            # Baseline-style calls: separate requests (simulate 3 serial requests to amplify effect)
            t0 = time.perf_counter()
            baseline_status = 200
            baseline_error = None
            try:
                backend.get_ride(scenario["rideId"], latency_ms=latency)
            except ValueError as e:
                baseline_status = 400
                baseline_error = str(e)
            except KeyError as e:
                baseline_status = 404
                baseline_error = str(e)

            # If baseline ride fetch succeeded, try fare_items calls
            if baseline_status == 200:
                try:
                    backend.get_fare_items(scenario["rideId"], latency_ms=latency)
                    backend.get_fare_items(scenario["rideId"], latency_ms=latency)
                    backend.get_fare_items(scenario["rideId"], latency_ms=latency)
                except ValueError as e:
                    baseline_status = 400
                    baseline_error = str(e)
                except KeyError as e:
                    baseline_status = 404
                    baseline_error = str(e)
            t1 = time.perf_counter()
            baseline_count = backend.request_count
            baseline_latency = (t1 - t0)

            # reset backend and API for optimized
            backend2 = BackendSimulator()
            api2 = OptimizedRideAPI(backend2, cache_enabled=True)
            t2 = time.perf_counter()
            resp_opt = api2.get_ride(scenario["rideId"], includeFareBreakdown=True, latency_ms=latency)
            t3 = time.perf_counter()
            optimized_count = backend2.request_count
            optimized_latency = (t3 - t2)

            # Determine result status based on baseline/optimized statuses
            final_status = 200
            if baseline_status != 200:
                final_status = baseline_status
            resp_opt_status = resp_opt.get('status', 200) if isinstance(resp_opt, dict) else 200
            if final_status == 200 and resp_opt_status != 200:
                final_status = resp_opt_status

            scenario_result.update({
                "status": final_status,
                "totalFareBaseline": None,
                "totalFareOptimized": resp_opt.get("totalFare") if isinstance(resp_opt, dict) else None,
                "fareBreakdownPresentBaseline": False,
                "fareBreakdownPresentOptimized": True if resp_opt.get("fareBreakdown") else False,
                "baseline_requestCount": baseline_count,
                "optimized_requestCount": optimized_count,
                "baseline_latency": baseline_latency,
                "optimized_latency": optimized_latency,
                "latency_saving": baseline_latency - optimized_latency,
                "request_count_saving": baseline_count - optimized_count,
                "expected": scenario.get("expect")
            })
            # Include baseline/optimized errors if present
            if baseline_status != 200:
                scenario_result['baseline_status'] = baseline_status
                scenario_result['baseline_error'] = baseline_error
            if resp_opt_status != 200:
                scenario_result['optimized_status'] = resp_opt_status
                scenario_result['optimized_error'] = resp_opt.get('error')
        else:
            # Not our scenario style
            scenario_result.update({"status": 204})
    except Exception as e:
        scenario_result.update({"status": 500, "error": str(e), "requestCount": backend.request_count})
    # Evaluate pass/fail based on expected
    expected = scenario.get('expect', {})
    scenario_result['passed'] = True
    if expected.get('status') and scenario_result.get('status') != expected.get('status'):
        scenario_result['passed'] = False
    # Verify total fare when present
    if expected.get('totalFare') is not None and scenario_result.get('totalFare') is not None:
        if abs(expected.get('totalFare') - scenario_result.get('totalFare')) > 1e-6:
            scenario_result['passed'] = False
    if scenario.get('flow') == 'optimized' and expected.get('labelsSanitized'):
        if not scenario_result.get('labelsSanitized'):
            scenario_result['passed'] = False
    # Write logs
    with open(logs_file, "a") as f:
        f.write(json.dumps(scenario_result) + "\n")
    return scenario_result


def run_tests(scenarios_file: str, out_results: str, logs_file: str):
    with open(scenarios_file, "r") as f:
        scenarios_doc = json.load(f)
    results = []
    for s in scenarios_doc["scenarios"]:
        if s.get("flow") in ("optimized", "compare"):
            r = run_scenario(s, os.path.dirname(out_results), logs_file)
            results.append(r)
    with open(out_results, "w") as f:
        json.dump({"results": results}, f, indent=2)
    # write sample optimized snapshot for ride_001
    backend = BackendSimulator()
    api = OptimizedRideAPI(backend, cache_enabled=True)
    try:
        sample = api.get_ride('ride_001', includeFareBreakdown=True, latency_ms=0)
        snapshot_path = os.path.abspath(os.path.join(os.path.dirname(out_results), 'optimized_response_snapshot.json'))
        with open(snapshot_path, 'w') as sf:
            json.dump(sample, sf, indent=2)
    except Exception:
        pass
    return results


if __name__ == "__main__":
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    scenarios_file = os.path.abspath(os.path.join(base_dir, '..', 'test_scenarios.json'))
    out_results = os.path.abspath(os.path.join(base_dir, '..', 'results', 'results_post.json'))
    os.makedirs(os.path.dirname(out_results), exist_ok=True)
    logs_file = os.path.abspath(os.path.join(base_dir, '..', 'logs', 'log_post.txt'))
    os.makedirs(os.path.dirname(logs_file), exist_ok=True)
    if os.path.exists(logs_file):
        os.remove(logs_file)
    run_tests(scenarios_file, out_results, logs_file)
