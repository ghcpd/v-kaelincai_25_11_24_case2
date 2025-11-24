# Project B – Optimized Ride Fare API

Enhanced `GET /rides/{rideId}` supports `includeFareBreakdown=true` to return total + breakdown in one call. Defaults to legacy-compatible payload (no `fareBreakdown` when parameter is absent).

## Setup
- **Bash**: `bash setup.sh`
- **PowerShell**: `./run_tests.ps1`
- **Docker**: `docker build -t optimized-ride-api . && docker run --rm optimized-ride-api`

## Run Tests
- **Bash**: `bash run_tests.sh`
- **PowerShell**: `./run_tests.ps1`

Outputs:
- `results/results_post.json` – per-scenario outcomes & metrics
- `logs/log_post.txt` – same content for quick inspection
- `optimized_response_snapshot.json` – enriched payload sample

## Optimizations
- Single-call breakdown retrieval via `includeFareBreakdown`
- Combined data access minimizes downstream queries
- In-memory caching for ride + breakdown
- Strict validation (type/label/amount) with sanitization of labels
- Flattening of nested breakdown arrays

## Metrics
- `latency_ms`: simulated network + data processing
- `request_count`: optimized path stays at 1
- `downstream_calls`: combined fetch counts as 1
- `invalid_items`: validation rejects unsafe or malformed items
- `mismatch_total`: breakdown sum vs total fare reconciliation flag

## Scenarios & Pitfalls
- **Legacy path**: `includeFareBreakdown=false` excludes `fareBreakdown`
- **Weak network**: single call reduces latency risk
- **Malformed ride ID**: validated early
- **Hidden vulnerability**: labels sanitized
- **Nested breakdown**: flattened and validated

## Known Limitations
- Simulated latencies (no real sleeps)
- Fixtures in-memory; caching only demonstrative
- Does not persist sanitized data back to the store

## Validated Principles
- Backward compatibility preserved
- Performance gains via fewer round trips and combined fetch
- Data hygiene via validation & sanitization
