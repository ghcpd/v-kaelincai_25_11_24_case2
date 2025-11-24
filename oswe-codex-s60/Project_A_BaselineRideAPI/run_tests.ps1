#!/usr/bin/env pwsh
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$venv = Join-Path $root '.venv'
$activate = Join-Path $venv 'Scripts/Activate.ps1'

if (-not (Test-Path $venv)) {
  python -m venv $venv
  & $activate
  python -m pip install --upgrade pip
  python -m pip install -r (Join-Path $root 'requirements.txt')
} else {
  & $activate
}

python (Join-Path $root 'tests/test_runner.py')
