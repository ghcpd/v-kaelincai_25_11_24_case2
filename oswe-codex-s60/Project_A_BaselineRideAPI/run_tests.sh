#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$ROOT_DIR/.venv"

if [ ! -d "$VENV_DIR" ]; then
  bash "$ROOT_DIR/setup.sh"
else
  source "$VENV_DIR/bin/activate"
fi

python "$ROOT_DIR/tests/test_runner.py"
