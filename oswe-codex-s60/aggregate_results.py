import json
from pathlib import Path
from typing import Dict, Any

ROOT = Path(__file__).parent
BASELINE_RESULTS = ROOT / "Project_A_BaselineRideAPI" / "results" / "results_pre.json"
OPTIMIZED_RESULTS = ROOT / "Project_B_OptimizedRideAPI" / "results" / "results_post.json"
OUTPUT_REPORT = ROOT / "compare_report.md"
OUTPUT_RESULTS_DIR = ROOT / "results"
OUTPUT_RESULTS_DIR.mkdir(exist_ok=True)
OUTPUT_AGG_JSON = OUTPUT_RESULTS_DIR / "aggregate_summary.json"


def load_json(path: Path):
    if not path.exists():
        return None
    with path.open() as f:
        return json.load(f)


def scenario_map(results: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {s.get("id", f"idx_{i}"): s for i, s in enumerate(results.get("scenarios", []))}


def compute_common_metrics(bmap, omap):
    common_ids = sorted(set(bmap) & set(omap))
    if not common_ids:
        return {}, common_ids

    lat_deltas = []
    req_deltas = []
    matrix_rows = []
    for sid in common_ids:
        b = bmap[sid]
        o = omap[sid]
        b_lat = b.get("metrics", {}).get("total_latency_ms", 0)
        o_lat = o.get("metrics", {}).get("total_latency_ms", 0)
        b_req = b.get("metrics", {}).get("request_count", 0)
        o_req = o.get("metrics", {}).get("request_count", 0)
        lat_deltas.append(b_lat - o_lat)
        req_deltas.append(b_req - o_req)
        matrix_rows.append((sid, b.get("passed", False), o.get("passed", False)))

    metrics = {
        "avg_latency_delta_ms": sum(lat_deltas) / len(lat_deltas) if lat_deltas else 0,
        "avg_request_count_delta": sum(req_deltas) / len(req_deltas) if req_deltas else 0,
    }
    return {"matrix": matrix_rows, **metrics}, common_ids


def edge_case_success(results_map, scenarios_cfg):
    # edge_case_flags reside in scenario config; map by id
    flags_total = 0
    flags_pass = 0
    details = []
    cfg_map = {s.get("id"): s for s in scenarios_cfg.get("scenarios", [])}
    for sid, res in results_map.items():
        cfg = cfg_map.get(sid) or {}
        flags = cfg.get("edge_case_flags") or []
        if not flags:
            continue
        flags_total += 1
        passed = res.get("passed", False)
        if passed:
            flags_pass += 1
        details.append((sid, flags, passed))
    rate = (flags_pass / flags_total) if flags_total else 0
    return {"edge_case_rate": rate, "edge_case_details": details, "edge_cases_total": flags_total}


def breakdown_integrity(optimized_map):
    total = 0
    mismatches = 0
    sanitization_fail = 0
    for res in optimized_map.values():
        resp = res.get("response") or {}
        data = resp.get("data") or {}
        if not data or not data.get("fareBreakdown"):
            continue
        total += 1
        metrics = resp.get("metrics") or {}
        if metrics.get("mismatch_total"):
            mismatches += 1
        if not res.get("metrics", {}).get("sanitized", True):
            sanitization_fail += 1
    return {
        "breakdown_cases": total,
        "mismatch_count": mismatches,
        "sanitization_fail": sanitization_fail,
    }


def render_markdown(baseline, optimized, common_metrics, edge_metrics_opt, breakdown_opt):
    lines = []
    lines.append("# Compare Report")
    lines.append("")
    # Summary
    lines.append("## Summary")
    lines.append("- Baseline scenarios: {} (passed {}/{})".format(
        baseline.get("summary", {}).get("total_scenarios", 0),
        baseline.get("summary", {}).get("passed", 0),
        baseline.get("summary", {}).get("total_scenarios", 0),
    ))
    lines.append("- Optimized scenarios: {} (passed {}/{})".format(
        optimized.get("summary", {}).get("total_scenarios", 0),
        optimized.get("summary", {}).get("passed", 0),
        optimized.get("summary", {}).get("total_scenarios", 0),
    ))
    lines.append("- Avg latency delta (baseline - optimized): {:.2f} ms".format(common_metrics.get("avg_latency_delta_ms", 0)))
    lines.append("- Avg request-count delta: {:.2f}".format(common_metrics.get("avg_request_count_delta", 0)))
    lines.append("")

    # Pass/fail matrix
    lines.append("## Pass/Fail Matrix (Common Scenarios)")
    lines.append("| Scenario | Baseline Pass | Optimized Pass |\n|---|---|---|")
    for sid, bpass, opass in common_metrics.get("matrix", []):
        lines.append(f"| {sid} | {'✅' if bpass else '❌'} | {'✅' if opass else '❌'} |")
    lines.append("")

    # Breakdown integrity
    lines.append("## Breakdown Integrity (Optimized)")
    lines.append("- Breakdown cases: {}".format(breakdown_opt.get("breakdown_cases", 0)))
    lines.append("- Mismatches vs totalFare: {}".format(breakdown_opt.get("mismatch_count", 0)))
    lines.append("- Sanitization failures: {}".format(breakdown_opt.get("sanitization_fail", 0)))
    lines.append("")

    # Edge case resilience
    lines.append("## Edge-Case Resilience (Optimized)")
    lines.append("- Edge-case scenarios: {}".format(edge_metrics_opt.get("edge_cases_total", 0)))
    lines.append("- Edge-case success rate: {:.0%}".format(edge_metrics_opt.get("edge_case_rate", 0)))
    lines.append("\n### Edge-Case Details")
    lines.append("| Scenario | Flags | Passed |\n|---|---|---|")
    for sid, flags, passed in edge_metrics_opt.get("edge_case_details", []):
        lines.append(f"| {sid} | {', '.join(flags)} | {'✅' if passed else '❌'} |")
    lines.append("")

    # References
    lines.append("## References")
    lines.append("- Baseline snapshot: `Project_A_BaselineRideAPI/baseline_response_snapshot.json`")
    lines.append("- Optimized snapshot: `Project_B_OptimizedRideAPI/optimized_response_snapshot.json`")
    lines.append("- Baseline results: `Project_A_BaselineRideAPI/results/results_pre.json`")
    lines.append("- Optimized results: `Project_B_OptimizedRideAPI/results/results_post.json`")

    return "\n".join(lines)


def main():
    baseline = load_json(BASELINE_RESULTS)
    optimized = load_json(OPTIMIZED_RESULTS)
    scenarios_cfg = load_json(ROOT / "test_scenarios.json") or {"scenarios": []}

    if baseline is None or optimized is None:
        print("Missing results_pre.json or results_post.json; run project tests first.", flush=True)
        return 1

    bmap = scenario_map(baseline)
    omap = scenario_map(optimized)
    common_metrics, _ = compute_common_metrics(bmap, omap)
    edge_metrics_opt = edge_case_success(omap, scenarios_cfg)
    breakdown_opt = breakdown_integrity(omap)

    # aggregate json
    aggregate = {
        "common_metrics": common_metrics,
        "edge_metrics_opt": edge_metrics_opt,
        "breakdown_opt": breakdown_opt,
        "baseline_summary": baseline.get("summary", {}),
        "optimized_summary": optimized.get("summary", {}),
    }
    OUTPUT_AGG_JSON.write_text(json.dumps(aggregate, indent=2))

    # markdown report
    OUTPUT_REPORT.write_text(
        render_markdown(baseline, optimized, common_metrics, edge_metrics_opt, breakdown_opt),
        encoding="utf-8",
    )
    print("Aggregation complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
