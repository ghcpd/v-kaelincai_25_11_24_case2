#!/usr/bin/env bash
python -m venv .venv
.venv/Scripts/pip install -U pip
.venv/Scripts/pip install -r requirements.txt
echo 'Setup complete for Project B OptimizedRideAPI'
