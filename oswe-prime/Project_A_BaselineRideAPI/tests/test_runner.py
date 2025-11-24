import json
import os
import sys
import time
from typing import Dict

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.baseline_api import BackendSimulator, BaselineRideAPI


def run_scenario(scenario: Dict, results_dir: str, logs_file: str):
    backend = BackendSimulator()
    api = BaselineRideAPI(backend)
    latency = scenario.get("simulate_latency_ms", 0)
    scenario_result = {"scenario_id": scenario.get("id"), "start": time.time()}
    try:
        # Baseline flow: two separate calls
        t0 = time.perf_counter()
        resp_ride = api.get_ride(scenario["rideId"], latency_ms=latency)
        t1 = time.perf_counter()
        # If ride error, return early
        if resp_ride.get("status") and resp_ride.get("status") != 200:
            elapsed = (t1 - t0)
            scenario_result.update({
                "status": resp_ride.get("status"),
                "error": resp_ride.get("error"),
                "requestCount": backend.request_count,
                "latency": elapsed,
                "expected": scenario.get("expect")
            })
        else:
            resp_items = api.get_fare_items(scenario["rideId"], latency_ms=latency)
            t2 = time.perf_counter()
            elapsed = (t2 - t0)
            scenario_result.update({
                "status": 200,
                "totalFare": resp_ride.get("totalFare"),
                "fareBreakdownPresent": False,
                "requestCount": backend.request_count,
                "latency": elapsed,
                "expected": scenario.get("expect")
            })
    except Exception as e:
        scenario_result.update({"status": 500, "error": str(e), "requestCount": backend.request_count})
    # Evaluate pass/fail based on expected
    expected = scenario.get('expect', {})
    scenario_result['passed'] = True
    if expected.get('status') and scenario_result.get('status') != expected.get('status'):
        scenario_result['passed'] = False
    if expected.get('totalFare') is not None and scenario_result.get('totalFare') is not None:
        if abs(expected.get('totalFare') - scenario_result.get('totalFare')) > 1e-6:
            scenario_result['passed'] = False
    if expected.get('fareBreakdownPresent') is not None:
        if expected.get('fareBreakdownPresent') != scenario_result.get('fareBreakdownPresent'):
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
        # Run only scenarios labeled baseline or compare (we always run baseline to compare)
        if s.get("flow") in ("baseline", "compare"):
            r = run_scenario(s, os.path.dirname(out_results), logs_file)
            results.append(r)
    with open(out_results, "w") as f:
        json.dump({"results": results}, f, indent=2)
    # write sample baseline snapshot for ride_001
    backend = BackendSimulator()
    api = BaselineRideAPI(backend)
    try:
        sample = api.get_ride('ride_001', latency_ms=0)
        snapshot_path = os.path.abspath(os.path.join(os.path.dirname(out_results), 'baseline_response_snapshot.json'))
        with open(snapshot_path, 'w') as sf:
            json.dump(sample, sf, indent=2)
    except Exception:
        pass
    return results


if __name__ == "__main__":
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    scenarios_file = os.path.abspath(os.path.join(base_dir, '..', 'test_scenarios.json'))
    out_results = os.path.abspath(os.path.join(base_dir, '..', 'results', 'results_pre.json'))
    os.makedirs(os.path.dirname(out_results), exist_ok=True)
    logs_file = os.path.abspath(os.path.join(base_dir, '..', 'logs', 'log_pre.txt'))
    os.makedirs(os.path.dirname(logs_file), exist_ok=True)
    if os.path.exists(logs_file):
        os.remove(logs_file)
    run_tests(scenarios_file, out_results, logs_file)
