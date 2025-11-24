import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List
from decimal import Decimal
def to_jsonable(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, dict):
        return {k: to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [to_jsonable(x) for x in obj]
    return obj

ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(PROJECT_ROOT))

from src.api import get_ride_details  # noqa: E402

TEST_SCENARIOS_PATH = ROOT / "test_scenarios.json"
RESULTS_DIR = PROJECT_ROOT / "results"
LOGS_DIR = PROJECT_ROOT / "logs"
RESULTS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
RESULTS_FILE = RESULTS_DIR / "results_post.json"
LOG_FILE = LOGS_DIR / "log_post.txt"
SNAPSHOT_FILE = PROJECT_ROOT / "optimized_response_snapshot.json"


DEFAULT_SCENARIOS = {"scenarios": []}


def load_scenarios() -> Dict[str, Any]:
    if not TEST_SCENARIOS_PATH.exists():
        return DEFAULT_SCENARIOS
    with TEST_SCENARIOS_PATH.open() as f:
        return json.load(f)


def is_for_optimized(s: Dict[str, Any]) -> bool:
    projects = s.get("projects") or s.get("project")
    if projects is None:
        return True
    if isinstance(projects, str):
        return projects.lower() in {"optimized", "both", "post"}
    return any(p.lower() in {"optimized", "both", "post"} for p in projects)


def eval_scenario(s: Dict[str, Any]) -> Dict[str, Any]:
    sid = s.get("id", "unknown")
    ride_id = s.get("ride_id")
    network = s.get("network") or {}
    seed = s.get("seed", 0)
    expectations = s.get("expectations") or {}
    include_breakdown = s.get("includeFareBreakdown", False)

    resp = get_ride_details(ride_id, includeFareBreakdown=include_breakdown, network=network, seed=seed)
    errors: List[str] = []
    passed = True

    expected_status = expectations.get("status")
    if expected_status and resp.get("status") != expected_status:
        passed = False
        errors.append(f"Expected status {expected_status}, got {resp.get('status')}")

    expected_total = expectations.get("totalFare")
    if expected_total is not None and resp.get("data"):
        actual_total = float(resp["data"].get("totalFare", 0))
        if abs(actual_total - expected_total) > 1e-2:
            passed = False
            errors.append(f"Expected totalFare {expected_total}, got {actual_total}")

    breakdown_expected = expectations.get("breakdown_present")
    if breakdown_expected is not None:
        has_breakdown = bool(resp.get("data") and resp["data"].get("fareBreakdown"))
        if breakdown_expected != has_breakdown:
            passed = False
            errors.append(f"Expected breakdown presence {breakdown_expected}, got {has_breakdown}")

    # Backward compatibility: when includeFareBreakdown=False, ensure fareBreakdown absent
    if not include_breakdown and resp.get("data"):
        if "fareBreakdown" in resp["data"]:
            passed = False
            errors.append("fareBreakdown should be absent in legacy path")

    # Validate sanitized labels if breakdown present
    sanitized_ok = True
    unsafe_labels = []
    if resp.get("data") and resp["data"].get("fareBreakdown"):
        for item in resp["data"]["fareBreakdown"]:
            lbl = item.get("label", "")
            if any(tok in lbl.lower() for tok in ("<", ">", "script")):
                sanitized_ok = False
                unsafe_labels.append(lbl)
    if not sanitized_ok:
        passed = False
        errors.append(f"Unsanitized labels found: {unsafe_labels}")

    total_latency = (resp.get("metrics") or {}).get("latency_ms", 0)
    request_count = (resp.get("metrics") or {}).get("request_count", 0)
    downstream_calls = (resp.get("metrics") or {}).get("downstream_calls", 0)

    scenario_result = {
        "id": sid,
        "name": s.get("name"),
        "passed": passed,
        "errors": errors,
        "response": resp,
        "metrics": {
            "total_latency_ms": total_latency,
            "request_count": request_count,
            "downstream_calls": downstream_calls,
            "sanitized": sanitized_ok,
        },
    }
    return scenario_result


def main():
    scenarios_config = load_scenarios()
    scenarios = [s for s in scenarios_config.get("scenarios", []) if is_for_optimized(s)]
    if not scenarios:
        print("No scenarios for optimized; nothing to run.")
        RESULTS_FILE.write_text(json.dumps({"summary": {}, "scenarios": []}, indent=2))
        return 0

    results = [eval_scenario(s) for s in scenarios]
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

    json_output = to_jsonable(output)

    RESULTS_FILE.write_text(json.dumps(json_output, indent=2))
    LOG_FILE.write_text(json.dumps(json_output, indent=2))

    # Snapshot
    for r in results:
        if r["response"].get("status") == "ok":
            SNAPSHOT_FILE.write_text(json.dumps(to_jsonable(r["response"]), indent=2))
            break

    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
