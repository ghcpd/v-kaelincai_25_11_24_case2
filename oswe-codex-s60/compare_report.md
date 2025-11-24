# Compare Report

## Summary
- Baseline scenarios: 4 (passed 4/4)
- Optimized scenarios: 6 (passed 6/6)
- Avg latency delta (baseline - optimized): 242.75 ms
- Avg request-count delta: 0.75

## Pass/Fail Matrix (Common Scenarios)
| Scenario | Baseline Pass | Optimized Pass |
|---|---|---|
| hidden_vulnerability | ✅ | ✅ |
| malformed_ride_id | ✅ | ✅ |
| normal_flow | ✅ | ✅ |
| weak_network | ✅ | ✅ |

## Breakdown Integrity (Optimized)
- Breakdown cases: 4
- Mismatches vs totalFare: 0
- Sanitization failures: 0

## Edge-Case Resilience (Optimized)
- Edge-case scenarios: 5
- Edge-case success rate: 100%

### Edge-Case Details
| Scenario | Flags | Passed |
|---|---|---|
| legacy_default | backward_compat | ✅ |
| weak_network | weak_network | ✅ |
| malformed_ride_id | malformed_input | ✅ |
| hidden_vulnerability | sanitization | ✅ |
| nested_breakdown | nested_breakdown | ✅ |

## References
- Baseline snapshot: `Project_A_BaselineRideAPI/baseline_response_snapshot.json`
- Optimized snapshot: `Project_B_OptimizedRideAPI/optimized_response_snapshot.json`
- Baseline results: `Project_A_BaselineRideAPI/results/results_pre.json`
- Optimized results: `Project_B_OptimizedRideAPI/results/results_post.json`