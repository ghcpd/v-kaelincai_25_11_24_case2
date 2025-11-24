# Project A - Baseline Ride API

This project simulates a legacy ride-detail API that returns only the total fare from `GET /rides/{rideId}`. Clients must fetch fare breakdown via a separate endpoint `GET /rides/{rideId}/fare-items`.

Run instructions:
1. (Bash) Make a virtualenv and install dependencies: `./setup.sh` or (PowerShell) `./setup.ps1`
2. (Bash) Run tests: `./run_tests.sh` or (PowerShell) `./run_tests.ps1`

Description:
- Baseline API simulates multiple round-trips to fetch breakdown items separately from ride summary. The test harness simulates latency and counts downstream requests.

Key files:
- `src/baseline_api.py` - Backend simulator and API functions
- `tests/test_runner.py` - Runs baseline scenarios and writes `results_pre.json`, `baseline_response_snapshot.json`, and logs


Outputs will be in `results/` and `logs/`.
