#!/usr/bin/env bash
set -euo pipefail
echo "Running baseline tests"
PY=.venv/Scripts/python
if [ ! -f "$PY" ]; then
  echo 'Virtualenv not found. Run setup.sh first.'
  exit 1
fi
mkdir -p results logs
.venv/Scripts/python -u tests/test_runner.py
echo "Baseline tests completed. Results in results/ and logs/."
