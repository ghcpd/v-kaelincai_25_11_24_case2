#!/bin/bash

echo "=========================================="
echo "Running Project B - Optimized API Tests"
echo "=========================================="

# Ensure we're in the project directory
cd "$(dirname "$0")"

# Create output directories
mkdir -p logs
mkdir -p results

# Run tests
echo "Executing test suite..."
python tests/test_optimized.py

# Check if tests completed successfully
if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Test execution completed successfully"
    echo "Results saved to: results/results_optimized.json"
    echo "Logs saved to: logs/log_optimized.txt"
    echo "Snapshot saved to: results/optimized_response_snapshot.json"
else
    echo ""
    echo "✗ Test execution failed"
    exit 1
fi
