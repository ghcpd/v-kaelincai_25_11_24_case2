# Project A – Baseline Ride Fare API

Legacy simulation of `GET /rides/{rideId}` that returns only `totalFare`. Clients must call `GET /rides/{rideId}/fare-items` separately for a breakdown.

## Setup
- **Bash**: `bash setup.sh`
- **PowerShell**: `./run_tests.ps1` (creates venv if absent)
- **Docker**: `docker build -t baseline-ride-api . && docker run --rm baseline-ride-api`

## Run Tests
- **Bash**: `bash run_tests.sh`
- **PowerShell**: `./run_tests.ps1`

Outputs:
- `results/results_pre.json` – per-scenario outcomes & metrics
- `logs/log_pre.txt` – same content for quick inspection
- `baseline_response_snapshot.json` – example legacy payload

## Metrics
- `total_latency_ms`: sum of simulated latencies for required calls (details + fare items)
- `request_count`: number of client calls (baseline usually 2)
- `downstream_calls`: simulated data-access hits

## Scenarios & Pitfalls
- **Legacy-only flow**: no `fareBreakdown` field; clients must issue an extra call
- **Weak network**: multiple round trips amplify latency
- **Malformed ride ID**: returns error
- **Hidden vulnerability**: labels are not sanitized (legacy behavior)
- **Non-string fields / nested breakdown**: not strictly validated

## Known Limitations
- Latency is simulated (no real sleeps) for deterministic metrics
- Data and breakdowns are in-memory fixtures
- Caching is not implemented in baseline

## Validated Principles
- Backward-compatible schema (no `fareBreakdown`)
- Demonstrates performance bottleneck due to multiple calls
