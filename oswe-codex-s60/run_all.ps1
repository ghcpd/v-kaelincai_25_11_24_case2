#!/usr/bin/env pwsh
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$report = Join-Path $root 'compare_report.md'

Write-Host '[run_all] Running baseline then optimized...'
Push-Location (Join-Path $root 'Project_A_BaselineRideAPI'); try { ./run_tests.ps1 } finally { Pop-Location }
Push-Location (Join-Path $root 'Project_B_OptimizedRideAPI'); try { ./run_tests.ps1 } finally { Pop-Location }

python (Join-Path $root 'aggregate_results.py')

Write-Host "[run_all] Done. Report at $report"
