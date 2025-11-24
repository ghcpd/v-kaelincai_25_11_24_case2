#!/bin/bash
# Project B: Optimized Ride Fare API - Test Runner
# Executes tests, generates logs, and produces results

set -e

PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VENV_DIR="$PROJECT_DIR/.venv"
TESTS_DIR="$PROJECT_DIR/tests"
LOGS_DIR="$PROJECT_DIR/logs"
RESULTS_DIR="$PROJECT_DIR/results"

echo "=========================================="
echo "PROJECT B: OPTIMIZED RIDE API - TEST RUNNER"
echo "=========================================="
echo "Project Directory: $PROJECT_DIR"
echo "Test Directory: $TESTS_DIR"
echo "Logs Directory: $LOGS_DIR"
echo "Results Directory: $RESULTS_DIR"

# Create log and results directories
mkdir -p "$LOGS_DIR"
mkdir -p "$RESULTS_DIR"

# Activate virtual environment
if [ ! -d "$VENV_DIR" ]; then
    echo "Error: Virtual environment not found. Run setup.sh first."
    exit 1
fi

echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Run tests with logging
LOG_FILE="$LOGS_DIR/log_post.txt"
echo "Running tests... (output to $LOG_FILE)"

python "$TESTS_DIR/test_optimized_api.py" 2>&1 | tee "$LOG_FILE"

echo ""
echo "=========================================="
echo "Test execution complete!"
echo "Logs: $LOG_FILE"
echo "Results: $RESULTS_DIR/results_post.json"
echo "=========================================="
