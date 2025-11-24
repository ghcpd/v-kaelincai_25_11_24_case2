#!/bin/bash
# Project B: Optimized Ride Fare API - Setup Script
# Sets up virtual environment and installs dependencies

set -e

PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VENV_DIR="$PROJECT_DIR/.venv"

echo "=========================================="
echo "PROJECT B: OPTIMIZED RIDE API - SETUP"
echo "=========================================="
echo "Project Directory: $PROJECT_DIR"
echo "Virtual Environment: $VENV_DIR"

# Create virtual environment
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python -m venv "$VENV_DIR"
else
    echo "Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r "$PROJECT_DIR/requirements.txt"

echo "=========================================="
echo "Setup complete! Virtual environment ready."
echo "To activate: source $VENV_DIR/bin/activate"
echo "=========================================="
