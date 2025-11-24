# Project A - Baseline Ride API Setup Script (PowerShell)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Project A - Baseline Ride API Setup" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Create virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet

# Create necessary directories
Write-Host "Creating project directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path "logs" -Force | Out-Null
New-Item -ItemType Directory -Path "results" -Force | Out-Null
New-Item -ItemType Directory -Path "src" -Force | Out-Null

Write-Host ""
Write-Host "✓ Setup complete!" -ForegroundColor Green
Write-Host "To activate the environment manually:" -ForegroundColor White
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor Gray
