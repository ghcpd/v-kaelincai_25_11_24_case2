# Ride Fare API Optimization – Projects A & B

Two Python simulations demonstrate legacy vs optimized ride-detail API behavior for fare breakdown delivery.

## Projects
- `Project_A_BaselineRideAPI`: legacy flow (total fare only; separate breakdown call)
- `Project_B_OptimizedRideAPI`: enhanced flow with `includeFareBreakdown=true`, validation, caching

## Run All
- **Bash**: `bash run_all.sh`
- **PowerShell**: `./run_all.ps1`

Artifacts:
- `Project_A_BaselineRideAPI/results/results_pre.json`
- `Project_B_OptimizedRideAPI/results/results_post.json`
- `compare_report.md`
- `results/aggregate_summary.json`

## Test Scenarios (`test_scenarios.json`)
| id | Description | Projects | includeFareBreakdown | Notes |
|---|---|---|---|---|
| normal_flow | Normal ride with breakdown | both | true | Compares multi-call vs single-call |
| legacy_default | Legacy payload (no breakdown) | optimized | false | Backward compatibility check |
| weak_network | High-latency network | both | true | Measures latency savings |
| malformed_ride_id | Invalid ride id | both | false | Input validation |
| hidden_vulnerability | Unsafe label attempt | both | true | Sanitization (optimized) |
| nested_breakdown | Nested breakdown structure | optimized | true | Flatten & validate |

## Environment
- Python 3.10+
- Baseline: stdlib only
- Optimized: `pydantic>=2.6,<3`

## Notes
- Latencies are simulated (no real sleeps)
- Data fixtures in-memory
- Caching is demonstrative only
