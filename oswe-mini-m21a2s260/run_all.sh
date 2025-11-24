#!/bin/bash
set -e
BASEDIR=$(pwd)
echo "Running baseline tests..."
bash Project_A_BaselineRideAPI/run_tests.sh
echo "Running optimized tests..."
bash Project_B_OptimizedRideAPI/run_tests.sh

mkdir -p results
cp Project_A_BaselineRideAPI/results/results_pre.json results/ || true
cp Project_B_OptimizedRideAPI/results/results_post.json results/ || true
cp Project_A_BaselineRideAPI/logs/log_pre.txt results/ || true
cp Project_B_OptimizedRideAPI/logs/log_post.txt results/ || true

echo "Producing compare report..."
python - <<'PY'
import json
import os
pre = json.load(open('results/results_pre.json'))
post = json.load(open('results/results_post.json'))
metrics = {
    'pre_downstream': pre['metrics'].get('downstream_calls',0),
    'post_downstream': post['metrics'].get('downstream_calls',0),
}
lat_pre = sum(r['latency'] for r in pre['results'])/len(pre['results'])
lat_post = sum(r['latency'] for r in post['results'])/len(post['results'])
report = {
  'pre_avg_latency': lat_pre,
  'post_avg_latency': lat_post,
  'downstream_calls_pre': metrics['pre_downstream'],
  'downstream_calls_post': metrics['post_downstream'],
  'delta_latency': lat_pre - lat_post,
}
open('compare_report.md','w').write('# Comparison Report\n\n'+json.dumps(report, indent=2))
print('compare_report.md written')
PY

echo "All done"
