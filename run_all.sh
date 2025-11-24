#!/bin/bash
# Master Test Runner - Executes both Project A and B, generates comparison report

set -e

ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_A_DIR="$ROOT_DIR/Project_A_BaselineRideAPI"
PROJECT_B_DIR="$ROOT_DIR/Project_B_OptimizedRideAPI"
AGGREGATED_RESULTS="$ROOT_DIR/results"

echo "=========================================="
echo "MASTER TEST RUNNER - BASELINE vs OPTIMIZED"
echo "=========================================="
echo "Root Directory: $ROOT_DIR"
echo "Project A: $PROJECT_A_DIR"
echo "Project B: $PROJECT_B_DIR"

# Create aggregated results directory
mkdir -p "$AGGREGATED_RESULTS"

# Setup both projects
echo ""
echo "========== SETTING UP PROJECT A =========="
bash "$PROJECT_A_DIR/setup.sh"

echo ""
echo "========== SETTING UP PROJECT B =========="
bash "$PROJECT_B_DIR/setup.sh"

# Run tests
echo ""
echo "========== RUNNING PROJECT A TESTS =========="
bash "$PROJECT_A_DIR/run_tests.sh"

echo ""
echo "========== RUNNING PROJECT B TESTS =========="
bash "$PROJECT_B_DIR/run_tests.sh"

# Copy results to aggregated location
echo ""
echo "========== AGGREGATING RESULTS =========="
cp "$PROJECT_A_DIR/results/results_pre.json" "$AGGREGATED_RESULTS/" 2>/dev/null || true
cp "$PROJECT_B_DIR/results/results_post.json" "$AGGREGATED_RESULTS/" 2>/dev/null || true
cp "$PROJECT_A_DIR/logs/log_pre.txt" "$AGGREGATED_RESULTS/" 2>/dev/null || true
cp "$PROJECT_B_DIR/logs/log_post.txt" "$AGGREGATED_RESULTS/" 2>/dev/null || true

# Generate comparison report
echo ""
echo "========== GENERATING COMPARISON REPORT =========="
python "$ROOT_DIR/generate_comparison_report.py"

echo ""
echo "=========================================="
echo "ALL TESTS COMPLETED!"
echo "=========================================="
echo "Aggregated Results: $AGGREGATED_RESULTS"
echo "Comparison Report: $AGGREGATED_RESULTS/compare_report.md"
echo "=========================================="
