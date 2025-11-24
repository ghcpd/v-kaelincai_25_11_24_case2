# Project B - Optimized Ride API

This project simulates an optimized ride-detail API that extends `GET /rides/{rideId}` with `includeFareBreakdown=true` query param to return the full fare breakdown in a single call.

Run instructions:
1. (Bash) `./setup.sh` to prepare environment or (PowerShell) `./setup.ps1`
2. (Bash) `./run_tests.sh` to execute tests or (PowerShell) `./run_tests.ps1`

Description:
- Optimized API adds `includeFareBreakdown=true` to deliver breakdown items in one call, includes caching to prevent redundant downstream calls, and includes strict validation & sanitization.
- Tests validate correctness, label sanitization, nested breakdown flattening, and show request/latency improvements.

Key files:
- `src/optimized_api.py` - Backend simulator, optimized API implementation, validation, and caching
- `tests/test_runner.py` - Runs scenarios and writes `results_post.json`, `optimized_response_snapshot.json`, and logs

