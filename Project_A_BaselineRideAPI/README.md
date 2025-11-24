# Project A: Baseline Ride Fare API

## Overview

**Project A** represents the **legacy workflow** for retrieving ride and fare information in a mobile ride-sharing platform. This baseline implementation demonstrates the performance bottleneck of requiring **multiple sequential API endpoints** to fetch complete ride details.

### Current Architecture

The baseline approach requires **2 separate sequential calls** to retrieve ride information:

1. **GET /rides/{rideId}** - Returns ride summary (total fare only)
2. **GET /rides/{rideId}/fare-items** - Returns fare breakdown details

This sequential pattern causes cumulative latency, especially on weak networks where each round-trip introduces 1000+ ms of delay.

## Key Characteristics

- **Multi-Endpoint Design**: Requires separate API calls for ride data and fare breakdown
- **No includeFareBreakdown Support**: Always limited to basic ride summary
- **Sequential Data Fetching**: Breakdown requests blocked until ride fetch completes
- **Input Validation**: Prevents SQL injection via ride ID sanitization
- **Performance Bottleneck**: Demonstrates baseline latency problem (6-8 seconds on weak networks)

## Project Structure

```
Project_A_BaselineRideAPI/
├── src/
│   ├── __init__.py
│   └── baseline_api.py         # Core API implementation
├── tests/
│   └── test_baseline_api.py    # Test suite
├── logs/                        # Test execution logs
├── results/                     # JSON test results
├── requirements.txt             # Python dependencies
├── setup.sh                     # Environment setup script
└── run_tests.sh                 # Test execution script
```

## Installation & Setup

### Prerequisites

- Python 3.8 or higher
- pip package manager
- bash shell

### Quick Start

```bash
# Navigate to Project A directory
cd Project_A_BaselineRideAPI

# Run setup script (creates venv, installs dependencies)
bash setup.sh

# Activate virtual environment
source .venv/bin/activate

# Run tests
bash run_tests.sh
```

### Manual Setup

If bash is unavailable on your system:

```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (macOS/Linux)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run tests
python tests/test_baseline_api.py
```

## Running Tests

### Run All Baseline Tests

```bash
bash run_tests.sh
```

This will:
1. Verify virtual environment
2. Execute all test scenarios
3. Generate logs in `logs/log_pre.txt`
4. Produce results in `results/results_pre.json`

### Test Scenarios

The baseline test suite covers:

1. **baseline_normal_fare**: Standard ride retrieval without breakdown (legacy mode)
2. **weak_network_baseline**: High-latency scenario demonstrating bottleneck
3. **malformed_ride_id**: Invalid input handling and SQL injection prevention

### Expected Results

```
Total Scenarios: 3
Passed: 3
Failed: 0
Pass Rate: 100%
Total Backend Calls: 6 (2 per scenario)
Total Latency: ~400ms (simulated network included)
```

## API Usage Examples

### Get Ride (Legacy Endpoint)

```python
from src.baseline_api import BaselineRideAPI, load_test_data

# Initialize API
data = load_test_data("../test_scenarios.json")
api = BaselineRideAPI(data_store=data, network_latency_ms=50)

# Fetch ride details
response = api.get_ride("ride_001")
# Response: {"status": 200, "rideId": "ride_001", "totalFare": 25.50, ...}
```

### Get Fare Breakdown (Separate Endpoint)

```python
# Fetch breakdown separately (2nd call)
breakdown = api.get_fare_items("ride_001")
# Response: {"status": 200, "rideId": "ride_001", "fareItems": [...]}
```

### Combined Approach (What Clients Do)

```python
# Reset metrics to track this operation
api.reset_metrics()

# Make both calls sequentially (this is what clients must do)
ride_response = api.get_ride("ride_001")
breakdown_response = api.get_fare_items("ride_001")

# Get metrics (note: 2 backend calls)
metrics = api.get_metrics()
# metrics["backend_calls"] = 2
# metrics["total_latency_ms"] = ~100ms (network simulated)
```

## Validation & Security

### Input Validation

- **Ride ID Format**: Must match pattern `ride_[a-zA-Z0-9_-]+`
- **Prevents**: SQL injection, command injection via ID parameter
- **Invalid Examples**: `ride_'; DROP TABLE;--`, `ride_$(rm -rf /)`, `ride_<script>`

### Error Handling

- **Invalid Ride ID** → HTTP 400 "INVALID_RIDE_ID"
- **Ride Not Found** → HTTP 404 "RIDE_NOT_FOUND"
- **Breakdown Not Found** → HTTP 404 "BREAKDOWN_NOT_FOUND"

## Test Results Interpretation

### Results File: `results/results_pre.json`

```json
{
  "timestamp": "2024-11-24 10:30:45",
  "summary": {
    "total_scenarios": 3,
    "passed": 3,
    "failed": 0,
    "pass_rate": "100%",
    "total_backend_calls": 6,
    "total_latency_ms": 400.5,
    "avg_latency_per_scenario_ms": 133.5,
    "edge_case_coverage": {
      "high_latency": 1,
      "network_stress": 1,
      "security": 1
    }
  },
  "test_results": [...]
}
```

### Interpretation

- **total_backend_calls**: 6 indicates 2 calls per scenario (3 scenarios × 2 calls)
- **total_latency_ms**: Sum of all simulated network delays
- **edge_case_coverage**: Count of passed tests per edge case category

## Performance Analysis

### Baseline Metrics

- **Requests per Ride**: 2 (ride + breakdown)
- **Latency per Call**: 50-100ms (typical network)
- **Total Time per Ride**: 100-200ms (sequential)
- **Weak Network (1500ms per call)**: 3000-3500ms total

### Comparison with Optimized (see Project B)

```
Metric                  Baseline    Optimized   Improvement
─────────────────────────────────────────────────────────
Requests per Ride         2           1         -50%
Latency (normal)          100ms       50ms      -50%
Latency (weak network)    3200ms      1600ms    -50%
Backend Calls             2           1         -50%
```

## Common Pitfalls & Limitations

### Limitations of Baseline Approach

1. **Sequential Bottleneck**: Breakdown fetch blocked until ride fetch completes
2. **Mobile Performance**: 2 round-trips critical on weak networks (2G, 3G)
3. **Caching Complexity**: Clients must cache both endpoints separately
4. **Error Recovery**: Partial response if breakdown fetch fails
5. **Server Load**: Double request volume for each ride request

### Hidden Vulnerabilities in Baseline

- **No Output Sanitization**: Fare labels not escaped (potential XSS if data corrupted)
- **No Type Validation**: Missing validation of numeric fields (crash risk)
- **No Breakdown Validation**: Malformed breakdown data not caught
- **Cache Invalidation**: No built-in mechanism for stale data detection

## Configuration

### Network Latency Simulation

Adjust simulated latency to match your target network:

```python
# Initialize with custom latency (in milliseconds)
api = BaselineRideAPI(data_store=data, network_latency_ms=1500)  # 1.5 second latency
```

### Test Scenarios

Modify `test_scenarios.json` (root directory) to add custom scenarios:

```json
{
  "scenario_id": "custom_scenario",
  "description": "Custom test",
  "ride_id": "ride_999",
  "network_latency_ms": 100,
  "expected_output": {...}
}
```

## Debugging Tips

### Enable Verbose Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Now all API calls will be logged with details
api = BaselineRideAPI(data_store=data)
```

### Inspect Metrics

```python
metrics = api.get_metrics()
print(f"Backend calls: {metrics['backend_calls']}")
print(f"Total latency: {metrics['total_latency_ms']}ms")
print(f"Per-call avg: {metrics['avg_latency_per_call_ms']:.2f}ms")
```

### Check Test Data

```python
import json
with open("../test_scenarios.json") as f:
    scenarios = json.load(f)
    
# View a specific ride
ride_data = scenarios["test_data_rides"]["ride_001"]
print(f"Ride {ride_data['rideId']}: ${ride_data['totalFare']}")
```

## Known Issues

1. **No Caching**: Each request fetches fresh data (no local cache)
2. **Stale Breakdown Data**: Fare items could be out-of-sync with ride data
3. **Error Atomicity**: Partial results if breakdown fetch fails
4. **Metric Collection**: Network latency simulation may not reflect production variance

## Next Steps

1. **Review Results**: Check `results/results_pre.json` for test outcomes
2. **Compare with Project B**: See optimized implementation for improvements
3. **Run Master Suite**: Execute `run_all.sh` from root directory for full comparison
4. **Read Comparison Report**: View `results/compare_report.md` for detailed analysis

## Support & Troubleshooting

### Virtual Environment Issues

```bash
# If activation fails, recreate venv
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Import Errors

```bash
# Ensure you're in the project directory
cd Project_A_BaselineRideAPI

# Verify Python path
python -c "import sys; print(sys.path)"

# Run tests directly
python tests/test_baseline_api.py
```

### Test Failures

1. Check logs in `logs/log_pre.txt`
2. Verify `test_scenarios.json` exists in root directory
3. Confirm all dependencies installed: `pip list`
4. Review test data consistency

## References

- [Project B (Optimized API)](../Project_B_OptimizedRideAPI/README.md)
- [Comparison Report](../results/compare_report.md)
- [Test Scenarios](../test_scenarios.json)

---

**Last Updated**: 2024-11-24  
**Version**: 1.0.0  
**Status**: Baseline Implementation Complete
