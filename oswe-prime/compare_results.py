import json
from pathlib import Path

def load_results(path, fallback=None):
    p = Path(path)
    if not p.exists() and fallback:
        p = Path(fallback)
    if not p.exists():
        return []
    return json.loads(p.read_text()).get('results', [])

base = load_results('Project_A_BaselineRideAPI/results/results_pre.json', fallback='results/results_pre.json')
opt = load_results('Project_B_OptimizedRideAPI/results/results_post.json', fallback='results/results_post.json')

def find_by_id(arr, id):
    for a in arr:
        if a.get('scenario_id') == id:
            return a
    return None

lines = []
lines.append('# Compare Report')
lines.append('')
lines.append('## Metrics Overview')
lines.append(f'- Baseline scenarios: {len(base)}')
lines.append(f'- Optimized scenarios: {len(opt)}')
lines.append('')

total_latency_delta = 0.0
count_latency = 0
total_request_saving = 0
count_request = 0

lines.append('## Scenario Details')
for b in base:
    sid = b.get('scenario_id')
    o = find_by_id(opt, sid)
    if not o:
        lines.append(f'- {sid}: baseline only; latency={b.get("latency")}, requests={b.get("requestCount")}')
        continue
    # We have both
    baseline_latency = b.get('latency', None)
    optimized_latency = o.get('latency', None)
    baseline_requests = b.get('requestCount', b.get('requestCount') or b.get('requestCount') )
    optimized_requests = o.get('requestCount', o.get('optimized_requestCount') or o.get('requestCount'))
    lat_delta = None
    req_delta = None
    if baseline_latency is not None and optimized_latency is not None:
        lat_delta = baseline_latency - optimized_latency
        total_latency_delta += lat_delta
        count_latency += 1
    if baseline_requests is not None and optimized_requests is not None:
        req_delta = baseline_requests - optimized_requests
        total_request_saving += req_delta
        count_request += 1
    lines.append(f"- {sid}: baseline_latency={baseline_latency}, optimized_latency={optimized_latency}, latency_delta={lat_delta}, baseline_requests={baseline_requests}, optimized_requests={optimized_requests}, request_delta={req_delta}")

avg_lat_delta = total_latency_delta / count_latency if count_latency else 0
avg_req_saving = total_request_saving / count_request if count_request else 0
lines.append('')
lines.append('## Aggregate')
lines.append(f'- Average latency delta (baseline - optimized): {avg_lat_delta:.4f}s')
lines.append(f'- Average request count saving: {avg_req_saving:.2f} requests')
lines.append('')
# Pass/Fail summary
pf_lines = []
pf_total = 0
pf_pass = 0
for a in base + opt:
    pf_total += 1
    if a.get('passed'):
        pf_pass += 1
pf_lines.append('## Pass/Fail Summary')
pf_lines.append(f'- Total checks: {pf_total}')
pf_lines.append(f'- Passed: {pf_pass}')
pf_lines.append(f'- Failed: {pf_total-pf_pass}')
lines.extend(pf_lines)

# Edge cases
lines.append('')
lines.append('## Edge Cases & Security Checks')
for o in opt:
    sid = o.get('scenario_id')
    if 'hidden_vuln_label' in sid or 'injection' in sid:
        labels_sanitized = o.get('labelsSanitized')
        lines.append(f'- {sid}: labels_sanitized={labels_sanitized}')

Path('compare_report.md').write_text('\n'.join(lines))
print('compare_report.md generated')
