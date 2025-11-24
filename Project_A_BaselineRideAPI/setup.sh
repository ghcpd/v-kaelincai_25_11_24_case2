#!/bin/bash

echo "=========================================="
echo "Project A - Baseline Ride API Setup"
echo "=========================================="

# Create virtual environment
echo "Creating virtual environment..."
python -m venv venv

# Activate virtual environment
if [ -f "venv/Scripts/activate" ]; then
    # Windows
    source venv/Scripts/activate
elif [ -f "venv/bin/activate" ]; then
    # Unix/Mac
    source venv/bin/activate
fi

# Install dependencies (none required for baseline)
echo "Installing dependencies..."
pip install --upgrade pip

# Create necessary directories
echo "Creating project directories..."
mkdir -p logs
mkdir -p results
mkdir -p src

echo "✓ Setup complete!"
echo "To activate the environment:"
echo "  Windows: venv\\Scripts\\activate"
echo "  Unix/Mac: source venv/bin/activate"
