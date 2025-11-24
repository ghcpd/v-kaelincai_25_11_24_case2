# Ride Fare API Optimization - Full Test Suite (PowerShell)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Ride Fare API Optimization - Full Test Suite" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Get the directory where this script is located
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Create aggregated results directory
New-Item -ItemType Directory -Path "results" -Force | Out-Null

Write-Host "Step 1: Running Project A (Baseline) Tests..." -ForegroundColor Yellow
Write-Host "----------------------------------------------" -ForegroundColor Gray
Set-Location "Project_A_BaselineRideAPI"
python tests\test_baseline.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Project A tests failed!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✓ Project A tests completed" -ForegroundColor Green
Write-Host ""

Write-Host "Step 2: Running Project B (Optimized) Tests..." -ForegroundColor Yellow
Write-Host "-----------------------------------------------" -ForegroundColor Gray
Set-Location "$ScriptDir\Project_B_OptimizedRideAPI"
python tests\test_optimized.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Project B tests failed!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✓ Project B tests completed" -ForegroundColor Green
Write-Host ""

Write-Host "Step 3: Generating Comparison Report..." -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray
Set-Location $ScriptDir
python generate_comparison_report.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Report generation failed!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "All Tests Completed Successfully!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Results available at:" -ForegroundColor White
Write-Host "  - Project A: Project_A_BaselineRideAPI\results\" -ForegroundColor Gray
Write-Host "  - Project B: Project_B_OptimizedRideAPI\results\" -ForegroundColor Gray
Write-Host "  - Comparison: compare_report.md" -ForegroundColor Gray
Write-Host ""
Write-Host "Logs available at:" -ForegroundColor White
Write-Host "  - Project A: Project_A_BaselineRideAPI\logs\log_baseline.txt" -ForegroundColor Gray
Write-Host "  - Project B: Project_B_OptimizedRideAPI\logs\log_optimized.txt" -ForegroundColor Gray
Write-Host ""
