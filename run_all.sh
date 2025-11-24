#!/bin/bash

echo "=========================================="
echo "Ride Fare API Optimization - Full Test Suite"
echo "=========================================="
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Create aggregated results directory
mkdir -p "$SCRIPT_DIR/results"

echo "Step 1: Running Project A (Baseline) Tests..."
echo "----------------------------------------------"
cd "$SCRIPT_DIR/Project_A_BaselineRideAPI"
python tests/test_baseline.py

if [ $? -ne 0 ]; then
    echo "✗ Project A tests failed!"
    exit 1
fi

echo ""
echo "✓ Project A tests completed"
echo ""

echo "Step 2: Running Project B (Optimized) Tests..."
echo "-----------------------------------------------"
cd "$SCRIPT_DIR/Project_B_OptimizedRideAPI"
python tests/test_optimized.py

if [ $? -ne 0 ]; then
    echo "✗ Project B tests failed!"
    exit 1
fi

echo ""
echo "✓ Project B tests completed"
echo ""

echo "Step 3: Generating Comparison Report..."
echo "----------------------------------------"
cd "$SCRIPT_DIR"
python generate_comparison_report.py

if [ $? -ne 0 ]; then
    echo "✗ Report generation failed!"
    exit 1
fi

echo ""
echo "=========================================="
echo "All Tests Completed Successfully!"
echo "=========================================="
echo ""
echo "Results available at:"
echo "  - Project A: Project_A_BaselineRideAPI/results/"
echo "  - Project B: Project_B_OptimizedRideAPI/results/"
echo "  - Comparison: compare_report.md"
echo ""
echo "Logs available at:"
echo "  - Project A: Project_A_BaselineRideAPI/logs/log_baseline.txt"
echo "  - Project B: Project_B_OptimizedRideAPI/logs/log_optimized.txt"
echo ""
