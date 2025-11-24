#!/usr/bin/env bash
set -euo pipefail
python3 -m pip install --user -r requirements.txt || true
python3 tests/runner.py
echo 'Project B tests finished'
