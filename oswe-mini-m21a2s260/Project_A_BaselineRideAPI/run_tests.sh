#!/bin/bash
python -m pip install -r requirements.txt >/dev/null 2>&1 || true
python - <<'PY'
from tests.test_runner import run_tests
import json, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sc = json.load(open(os.path.join(ROOT, '..', 'test_scenarios.json')))
os.makedirs(os.path.join(ROOT, 'results'), exist_ok=True)
os.makedirs(os.path.join(ROOT, 'logs'), exist_ok=True)
res_path = os.path.join(ROOT, 'results', 'results_pre.json')
log_path = os.path.join(ROOT, 'logs', 'log_pre.txt')
run_tests(sc['scenarios'], res_path, log_path)
# produce snapshot
from ..src import app as _app
snap = _app.get_ride('ride-123')
snap2 = _app.get_fare_items('ride-123')
open(os.path.join(ROOT, 'results', 'baseline_response_snapshot.json'), 'w').write(json.dumps({'ride': snap, 'fare': snap2}, indent=2))
PY
echo "Baseline run complete"