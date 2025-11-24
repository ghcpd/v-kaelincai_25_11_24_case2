#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR=$(cd "$(dirname "$0")" && pwd)
cd "$ROOT_DIR/Project_A_BaselineRideAPI"
./run_tests.sh || true
cd "$ROOT_DIR/Project_B_OptimizedRideAPI"
./run_tests.sh || true
python "$ROOT_DIR/run_all.py" || true
PY
import json,os,sys
root='.'
resA='Project_A_BaselineRideAPI/results/results_pre.json'
resB='Project_B_OptimizedRideAPI/results/results_post.json'
out='aggregated_results.json'
report='compare_report.md'
agg={'projectA':None,'projectB':None}
if os.path.exists(resA): agg['projectA']=json.load(open(resA))
if os.path.exists(resB): agg['projectB']=json.load(open(resB))
json.dump(agg,open(out,'w'),indent=2)
def as_map(results):
    return {r['id']: r for r in results.get('results', [])}

if agg['projectA'] and agg['projectB']:
    a=agg['projectA']; b=agg['projectB']
    amap=as_map(a)
    bmap=as_map(b)
    # compute per-scenario deltas
    scenarios = sorted(set(list(amap.keys())+list(bmap.keys())))
    with open(report,'w') as f:
        f.write('# Compare Report - Baseline vs Optimized\n\n')
        f.write('## Summary Metrics\n')
        f.write('* Baseline avg latency: **{:.1f} ms***\n'.format(a.get('average_latency_ms',-1)))
        f.write('* Optimized avg latency: **{:.1f} ms***\n'.format(b.get('average_latency_ms',-1)))
        f.write('* Latency reduction (pre - post): **{:.1f} ms***\n\n'.format(a.get('average_latency_ms',0)-b.get('average_latency_ms',0)))
        f.write('### Pass / Fail\n')
        f.write('- Baseline passed: {} / {}\n'.format(a.get('pass_count',0),a.get('total_cases',0)))
        f.write('- Optimized passed: {} / {}\n\n'.format(b.get('pass_count',0),b.get('total_cases',0)))

        f.write('## Per-scenario analysis\n')
        f.write('|scenario|baseline latency(ms)|optimized latency(ms)|baseline calls|optimized calls|baseline pass|optimized pass|notes|\n')
        f.write('|---|---:|---:|---:|---:|---|---|---|\n')
        for s in scenarios:
            arow=amap.get(s)
            brow=bmap.get(s)
            a_lat = arow['latency_ms'] if arow else '-'
            b_lat = brow['latency_ms'] if brow else '-'
            a_calls = (arow['metrics'].get('calls') if arow and 'metrics' in arow else (arow['metrics'].get('data_access_calls') if arow and 'metrics' in arow else '-'))
            b_calls = (brow['metrics'].get('calls') if brow and 'metrics' in brow else (brow['metrics'].get('data_access_calls') if brow and 'metrics' in brow else '-'))
            a_pass = arow['pass'] if arow else False
            b_pass = brow['pass'] if brow else False
            notes = []
            if arow and brow:
                # note request savings
                try:
                    delta = int(a_calls or 0) - int(b_calls or 0)
                    notes.append(f'requests_saved={delta}')
                except Exception:
                    pass
            f.write(f'|{s}|{a_lat}|{b_lat}|{a_calls}|{b_calls}|{a_pass}|{b_pass}|{";".join(notes)}|\n')

        f.write('\n## Edge-case/resilience notes\n')
        edge_cases = [k for k in scenarios if 'malformed' in k or 'malicious' in k or 'hidden' in k]
        for e in edge_cases:
            f.write(f'- {e}: baseline -> {amap.get(e)}\n')
            f.write(f'  optimized -> {bmap.get(e)}\n')

    print('Wrote',report)
else:
    print('One or both result files missing; see',resA,resB)
PY