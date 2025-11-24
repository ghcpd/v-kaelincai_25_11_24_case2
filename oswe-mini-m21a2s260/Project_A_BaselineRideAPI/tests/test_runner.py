import time
import json
import os
from ..src import app

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def make_request(ride_id):
    start = time.time()
    r1 = app.get_ride(ride_id)
    r2 = app.get_fare_items(ride_id)
    end = time.time()
    return {
        "status": (r1.get("status"), r2.get("status")),
        "totalFare": r1.get("ride", {}).get("totalFare"),
        "fareItems": r2.get("fareItems"),
        "latency": end - start,
    }

def run_tests(scenarios, output_path, log_path):
    results = []
    app.metrics_reset()
    for s in scenarios:
        start = time.time()
        res = None
        try:
            # support injection of malicious labels
            if s.get("injectLabel"):
                # modify underlying dataset
                from ..src import app as _app
                if s.get("rideId") in _app._FARE_ITEMS:
                    _app._FARE_ITEMS[s.get("rideId")][0]["label"] = s.get("injectLabel")
            if s["type"] in ("baseline_normal", "baseline_weak"):
                res = make_request(s["rideId"])
            else:
                # malformed or other
                res = make_request(s.get("rideId"))
        except Exception as exc:
            res = {"status": (500, 500), "error": str(exc)}
        end = time.time()
        # simple total validation
        computed_total = sum(i.get("amount", 0.0) for i in (res.get("fareItems") or []))
        breakdown_present = bool(res.get("fareItems"))
        results.append({
            "scenario": s["name"],
            "status": res.get("status"),
            "latency": res.get("latency", end - start),
            "totalFare": res.get("totalFare"),
            "computedTotal": computed_total,
            "breakdownPresent": breakdown_present,
            "pass": abs((res.get("totalFare") or 0.0) - computed_total) < 0.01,
        })

    metrics = app.metrics_get()
    with open(output_path, "w") as f:
        json.dump({"results": results, "metrics": metrics}, f, indent=2)
    with open(log_path, "w") as f:
        f.write(json.dumps({"results": results, "metrics": metrics}, indent=2))
    print("Baseline tests complete")

if __name__ == "__main__":
    scenarios = json.load(open(os.path.join(ROOT, "tests", "../test_scenarios.json")))
    run_tests(scenarios["scenarios"], os.path.join(ROOT, "results_pre.json"), os.path.join(ROOT, "logs", "log_pre.txt"))
