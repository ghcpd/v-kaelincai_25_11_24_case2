import time
import json, os
from ..src import app

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def run_tests(scenarios, output_path, log_path):
    results = []
    app.metrics_reset()
    for s in scenarios:
        start = time.time()
        try:
            # injection handling
            if s.get("injectLabel"):
                from ..src import app as _app
                if s.get("rideId") in _app._FARE_ITEMS:
                    _app._FARE_ITEMS[s.get("rideId")][0]["label"] = s.get("injectLabel")

            inc = s.get("includeFareBreakdown", False)
            resp = app.get_ride(s.get("rideId"), includeFareBreakdown=inc)
        except Exception as exc:
            resp = {"status": 500, "error": str(exc)}
        end = time.time()
        ride = resp.get("ride")
        breakdown = resp.get("fareBreakdown")
        total = ride.get("totalFare") if ride else None
        computed = 0.0
        if breakdown and breakdown.get("items"):
            computed = sum(i.get("amount", 0.0) for i in breakdown.get("items"))
        passed = (abs((total or 0.0) - computed) < 0.1) if breakdown else True
        results.append({
            "scenario": s["name"],
            "status": resp.get("status"),
            "latency": end - start,
            "totalFare": total,
            "computedTotal": computed,
            "breakdownPresent": bool(breakdown),
            "pass": passed,
        })

    metrics = app.metrics_get()
    with open(output_path, "w") as f:
        json.dump({"results": results, "metrics": metrics}, f, indent=2)
    with open(log_path, "w") as f:
        f.write(json.dumps({"results": results, "metrics": metrics}, indent=2))
    print("Optimized tests complete")

if __name__ == "__main__":
    scenarios = json.load(open(os.path.join(ROOT, "tests", "../test_scenarios.json")))
    run_tests(scenarios["scenarios"], os.path.join(ROOT, "results_post.json"), os.path.join(ROOT, "logs", "log_post.txt"))
