import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

# Ensure src is importable
ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
# Ensure project root is on sys.path so `src` package can be imported
sys.path.insert(0, str(PROJECT_ROOT))

from src.api import get_ride_details, get_ride_fare_items  # noqa: E402

TEST_SCENARIOS_PATH = ROOT / "test_scenarios.json"
RESULTS_DIR = PROJECT_ROOT / "results"
LOGS_DIR = PROJECT_ROOT / "logs"
RESULTS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
RESULTS_FILE = RESULTS_DIR / "results_pre.json"
LOG_FILE = LOGS_DIR / "log_pre.txt"
SNAPSHOT_FILE = PROJECT_ROOT / "baseline_response_snapshot.json"


DEFAULT_SCENARIOS = {"scenarios": []}


def load_scenarios() -> Dict[str, Any]:
    if not TEST_SCENARIOS_PATH.exists():
        return DEFAULT_SCENARIOS
    with TEST_SCENARIOS_PATH.open() as f:
        return json.load(f)


def is_for_baseline(s: Dict[str, Any]) -> bool:
    projects = s.get("projects") or s.get("project")
    if projects is None:
        return True
    if isinstance(projects, str):
        return projects.lower() in {"baseline", "both", "legacy"}
    return any(p.lower() in {"baseline", "both", "legacy"} for p in projects)


def eval_scenario(s: Dict[str, Any]) -> Dict[str, Any]:
    sid = s.get("id", "unknown")
    ride_id = s.get("ride_id")
    network = s.get("network") or {}
    seed = s.get("seed", 0)
    expectations = s.get("expectations") or {}

    detail_resp = get_ride_details(ride_id, network=network, seed=seed)
    fare_resp = None
    # Baseline always requires a second call when breakdown is expected by scenario
    if s.get("wants_breakdown", False) or s.get("includeFareBreakdown", False):
        fare_resp = get_ride_fare_items(ride_id, network=network, seed=seed + 1)

    errors: List[str] = []
    passed = True

    # Validate status
    expected_status = expectations.get("status")
    if expected_status and detail_resp.get("status") != expected_status:
        passed = False
        errors.append(f"Expected detail status {expected_status}, got {detail_resp.get('status')}")

    # Validate total fare
    expected_total = expectations.get("totalFare")
    if expected_total is not None and detail_resp.get("data"):
        actual_total = detail_resp["data"].get("totalFare")
        if abs(actual_total - expected_total) > 1e-2:
            passed = False
            errors.append(f"Expected totalFare {expected_total}, got {actual_total}")

    # Validate presence/absence of breakdown
    breakdown_expected = expectations.get("breakdown_present")
    if breakdown_expected is not None:
        has_breakdown = bool(fare_resp and fare_resp.get("status") == "ok")
        if breakdown_expected != has_breakdown:
            passed = False
            errors.append(f"Expected breakdown presence {breakdown_expected}, got {has_breakdown}")

    # Sum metrics
    total_latency = 0
    request_count = 0
    downstream_calls = 0
    for resp in (detail_resp, fare_resp):
        if not resp:
            continue
        m = resp.get("metrics") or {}
        total_latency += m.get("latency_ms", 0)
        request_count += m.get("request_count", 0)
        downstream_calls += m.get("downstream_calls", 0)

    # Additional validation: breakdown sum equals total fare (if both present)
    breakdown_sum = None
    if fare_resp and fare_resp.get("status") == "ok" and detail_resp.get("status") == "ok":
        items = fare_resp["data"].get("fareItems", [])
        breakdown_sum = sum(it.get("amount", 0) for it in items)
        if abs(breakdown_sum - detail_resp["data"].get("totalFare", 0)) > 1e-2:
            passed = False
            errors.append(
                f"Breakdown sum {breakdown_sum} does not match total {detail_resp['data'].get('totalFare')}"
            )

    scenario_result = {
        "id": sid,
        "name": s.get("name"),
        "passed": passed,
        "errors": errors,
        "responses": {
            "ride_details": detail_resp,
            "fare_items": fare_resp,
        },
        "metrics": {
            "total_latency_ms": total_latency,
            "request_count": request_count,
            "downstream_calls": downstream_calls,
            "breakdown_sum": breakdown_sum,
        },
    }
    return scenario_result


def main():
    scenarios_config = load_scenarios()
    scenarios = [s for s in scenarios_config.get("scenarios", []) if is_for_baseline(s)]
    if not scenarios:
        print("No scenarios for baseline; nothing to run.")
        RESULTS_FILE.write_text(json.dumps({"summary": {}, "scenarios": []}, indent=2))
        return 0

    results = []
    for s in scenarios:
        results.append(eval_scenario(s))

    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    avg_latency = sum(r["metrics"]["total_latency_ms"] for r in results) / total if total else 0
    avg_requests = sum(r["metrics"]["request_count"] for r in results) / total if total else 0

    summary = {
        "total_scenarios": total,
        "passed": passed,
        "failed": total - passed,
        "average_latency_ms": avg_latency,
        "average_request_count": avg_requests,
    }

    output = {
        "summary": summary,
        "scenarios": results,
    }

    RESULTS_FILE.write_text(json.dumps(output, indent=2))
    # Log file
    LOG_FILE.write_text(json.dumps(output, indent=2))

    # Snapshot: take first successful detail response
    for r in results:
        if r["responses"]["ride_details"].get("status") == "ok":
            snapshot = r["responses"]["ride_details"]
            SNAPSHOT_FILE.write_text(json.dumps(snapshot, indent=2))
            break

    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
