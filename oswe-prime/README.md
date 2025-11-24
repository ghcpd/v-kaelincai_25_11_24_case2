# Ride API Performance Optimization Projects

This workspace contains two Python-based projects to demonstrate and test a migration from a legacy ride API to an optimized endpoint that supports includeFareBreakdown.

Folders:
- `Project_A_BaselineRideAPI`: Legacy endpoints, `GET /rides/{rideId}` returns totalFare; `GET /rides/{rideId}/fare-items` returns items.
- `Project_B_OptimizedRideAPI`: Extended `GET /rides/{rideId}?includeFareBreakdown=true` to include fare breakdown in a single call, with caching and validation.

Shared artifacts:
- `test_scenarios.json`: Test cases
- `run_all.sh`: Runs both projects and aggregates results
- `compare_results.py`: Generates comparison report from results

Usage:
1. Run `./run_all.sh` from workspace root (requires bash and Python installed).
2. See `compare_report.md` and `Project_*/results/*` for outputs.
