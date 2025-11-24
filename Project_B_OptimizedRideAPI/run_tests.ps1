# Project B - Run Optimized Tests (PowerShell)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Running Project B - Optimized API Tests" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Ensure we're in the project directory
Set-Location $PSScriptRoot

# Create output directories
New-Item -ItemType Directory -Path "logs" -Force | Out-Null
New-Item -ItemType Directory -Path "results" -Force | Out-Null

# Run tests
Write-Host "Executing test suite..." -ForegroundColor Yellow
python tests\test_optimized.py

# Check if tests completed successfully
if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✓ Test execution completed successfully" -ForegroundColor Green
    Write-Host "Results saved to: results\results_optimized.json" -ForegroundColor White
    Write-Host "Logs saved to: logs\log_optimized.txt" -ForegroundColor White
    Write-Host "Snapshot saved to: results\optimized_response_snapshot.json" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "✗ Test execution failed" -ForegroundColor Red
    exit 1
}
