#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPORT="$ROOT_DIR/compare_report.md"

echo "[run_all] Running baseline then optimized..."
(cd "$ROOT_DIR/Project_A_BaselineRideAPI" && bash run_tests.sh)
(cd "$ROOT_DIR/Project_B_OptimizedRideAPI" && bash run_tests.sh)

python "$ROOT_DIR/aggregate_results.py" || {
  echo "Aggregation failed; ensure Python is available." >&2
  exit 1
}

echo "[run_all] Done. Report at $REPORT"
