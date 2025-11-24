#!/usr/bin/env bash
set -euo pipefail
echo "Running full comparison: baseline then optimized"

ROOT_DIR=$(pwd)

echo "Setting up Project A"
pushd Project_A_BaselineRideAPI
./setup.sh
./run_tests.sh
popd

echo "Setting up Project B"
pushd Project_B_OptimizedRideAPI
./setup.sh
./run_tests.sh
popd

echo "Aggregating results"
python compare_results.py
mkdir -p results/aggregated
cp Project_A_BaselineRideAPI/results/* results/aggregated/ 2>/dev/null || true
cp Project_B_OptimizedRideAPI/results/* results/aggregated/ 2>/dev/null || true

echo "All done. See compare_report.md and Project_*/results/ for details."
