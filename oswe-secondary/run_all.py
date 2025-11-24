#!/usr/bin/env python3
import subprocess, sys

print('Running baseline tests...')
subprocess.run([sys.executable, 'Project_A_BaselineRideAPI/tests/runner.py'], check=False)
print('Running optimized tests...')
subprocess.run([sys.executable, 'Project_B_OptimizedRideAPI/tests/runner.py'], check=False)
print('Aggregating results...')
subprocess.run([sys.executable, 'aggregator.py'], check=False)
print('Done. see compare_report.md')
