#!/bin/bash

echo "=========================================="
echo "Running Project A - Baseline API Tests"
echo "=========================================="

# Ensure we're in the project directory
cd "$(dirname "$0")"

# Create output directories
mkdir -p logs
mkdir -p results

# Run tests
echo "Executing test suite..."
python tests/test_baseline.py

# Check if tests completed successfully
if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Test execution completed successfully"
    echo "Results saved to: results/results_baseline.json"
    echo "Logs saved to: logs/log_baseline.txt"
    echo "Snapshot saved to: results/baseline_response_snapshot.json"
else
    echo ""
    echo "✗ Test execution failed"
    exit 1
fi
