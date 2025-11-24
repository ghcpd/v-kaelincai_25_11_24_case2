# Project A - Baseline Ride Fare API

## Overview
This project represents the **legacy implementation** of the ride-fare API that requires multiple endpoints to retrieve complete ride information including fare breakdown. This demonstrates the performance bottleneck that existed before optimization.

## Architecture

### Legacy Workflow
The baseline API requires clients to make **two separate HTTP requests**:

1. **GET `/rides/{rideId}`** - Returns basic ride information with total fare only
2. **GET `/rides/{rideId}/fare-items`** - Returns detailed fare breakdown

This design causes:
- **2-3 serialized requests** per operation
- **6-8 second load times** on poor network connections
- **Increased failure risk** due to multiple round trips
- **Difficulty with caching** and metric tracking

## Project Structure

```
Project_A_BaselineRideAPI/
├── src/
│   └── ride_api.py          # Core API implementation
├── tests/
│   └── test_baseline.py     # Test suite
├── logs/
│   └── log_baseline.txt     # Test execution logs
├── results/
│   ├── results_baseline.json              # Test results
│   └── baseline_response_snapshot.json    # API response example
├── requirements.txt         # Dependencies (none for baseline)
├── setup.sh                 # Environment setup script
├── run_tests.sh            # Test execution script
└── README.md               # This file
```

## Setup Instructions

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Environment Setup

#### Option 1: Using setup script (Linux/Mac)
```bash
chmod +x setup.sh
./setup.sh
source venv/bin/activate
```

#### Option 2: Using setup script (Windows)
```bash
bash setup.sh
venv\Scripts\activate
```

#### Option 3: Manual setup
```bash
# Create virtual environment
python -m venv venv

# Activate environment
# Windows:
venv\Scripts\activate
# Unix/Mac:
source venv/bin/activate

# Create directories
mkdir logs results
```

## Running Tests

### Using the test script
```bash
chmod +x run_tests.sh
./run_tests.sh
```

### Manual execution
```bash
python tests/test_baseline.py
```

## Test Scenarios

The baseline tests validate:
1. **Normal operation** - Two-call workflow with good network
2. **Network conditions** - Performance under various latency scenarios
3. **Error handling** - Invalid ride IDs, missing rides

### Validated Test Cases
- ✓ `baseline_normal` - Standard two-call workflow

## Performance Metrics

### Baseline Characteristics
- **Requests per operation**: 2 (minimum)
- **Network round trips**: 2+
- **Average latency**: ~200-400ms (good network) / 3000-6000ms (weak network)
- **Inline breakdown support**: ❌ NO
- **Backward compatible**: N/A (this is the legacy version)

### Key Limitations
1. **Multiple round trips required** - Always needs 2+ API calls
2. **No inline breakdown** - Cannot retrieve breakdown in single call
3. **Cumulative latency** - Each call adds network + processing time
4. **Higher failure probability** - More calls = more points of failure

## Output Files

### Results JSON (`results/results_baseline.json`)
Contains:
- Summary metrics (pass rate, latency, request count)
- Detailed results for each test scenario
- Timestamp and execution metadata

### Response Snapshot (`results/baseline_response_snapshot.json`)
Example of the legacy API response structure showing:
- Call 1: Basic ride info (no breakdown)
- Call 2: Separate fare breakdown call
- Performance impact metrics

### Logs (`logs/log_baseline.txt`)
Timestamped execution log with:
- Test scenario details
- Request/response information
- Performance measurements
- Pass/fail status

## API Response Examples

### Call 1: GET /rides/{rideId}
```json
{
  "status": "success",
  "data": {
    "ride_id": "ride_12345",
    "driver_id": "driver_001",
    "rider_id": "rider_001",
    "pickup": "123 Main St",
    "dropoff": "456 Oak Ave",
    "distance_miles": 10,
    "duration_minutes": 20,
    "ride_status": "completed",
    "total_fare": 25.50
  }
}
```
**Note**: No fare breakdown included!

### Call 2: GET /rides/{rideId}/fare-items
```json
{
  "status": "success",
  "data": {
    "ride_id": "ride_12345",
    "fare_breakdown": [
      {"type": "base", "label": "Base Fare", "amount": 5.00},
      {"type": "distance", "label": "Distance (10 miles)", "amount": 15.00},
      {"type": "time", "label": "Time (20 min)", "amount": 4.00},
      {"type": "tax", "label": "Tax", "amount": 1.50}
    ]
  }
}
```

## Understanding the Bottleneck

### Why This Is Slow
```
Client makes request 1  ──→  [Network Latency] ──→  Server processes
                                                      Server responds
Client receives response ←──  [Network Latency] ←──  
Client makes request 2  ──→  [Network Latency] ──→  Server processes
                                                      Server responds  
Client receives response ←──  [Network Latency] ←──

Total time = 4 × network_latency + 2 × processing_time
```

With 100ms network latency and 50ms processing:
- **Total time**: ~500ms minimum per operation

With 1500ms weak network latency:
- **Total time**: ~6000ms+ per operation

### Impact on Mobile Users
- Poor network = exponentially worse experience
- Each failed request requires retry
- Battery drain from multiple connections
- Data usage increases

## Validation Principles

The test suite validates:
1. ✓ **Functional correctness** - APIs return expected data
2. ✓ **Fare accuracy** - Breakdown sums match total fare
3. ✓ **Error handling** - Invalid inputs handled properly
4. ✓ **Performance measurement** - Latency and request counts tracked

## Common Pitfalls (Legacy Design)

1. **No inline breakdown** - Always requires second call
2. **Serialized requests** - Cannot parallelize without explicit code
3. **No caching optimization** - Each call hits backend
4. **Network dependency** - Performance degrades linearly with latency
5. **No query parameters** - Cannot customize response

## Known Limitations

- Simulated network latency (not real HTTP calls)
- Mock database (not actual DB queries)
- Simplified error scenarios
- No authentication/authorization layer
- No rate limiting or throttling

## Comparison with Optimized Version

See **Project B** for the optimized implementation that:
- ✓ Supports inline fare breakdown via query parameter
- ✓ Reduces requests from 2 to 1 (50% reduction)
- ✓ Maintains backward compatibility
- ✓ Implements caching and validation
- ✓ Handles edge cases and security concerns

## Next Steps

1. Run baseline tests: `./run_tests.sh`
2. Review `results/baseline_response_snapshot.json`
3. Note the performance metrics
4. Compare with Project B results in `compare_report.md`

---

**Note**: This baseline implementation serves as a reference point for measuring improvements in Project B.
