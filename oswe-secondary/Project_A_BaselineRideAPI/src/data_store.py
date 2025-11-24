"""
Simulated data store for Project A — baseline implementation.
Counts the number of downstream queries (for metrics in tests).
"""
import time
from typing import Dict, Any, List

# Simple in-memory dataset
_DATA = {
    'ride_1001': {
        'totalFare': 30.0,
        'fare_items': [
            {'type': 'base', 'label': 'Base fare', 'amount': 20.0},
            {'type': 'service', 'label': 'Service charge', 'amount': 5.0},
            {'type': 'tip', 'label': 'Tip', 'amount': 5.0},
        ]
    },
    'ride_weak1': {
        'totalFare': 40.0,
        'fare_items': [
            {'type': 'base', 'label': 'Base fare', 'amount': 30.0},
            {'type': 'surcharge', 'label': 'Airport', 'amount': 10.0},
        ]
    },
    'ride_malicious': {
        'totalFare': 15.0,
        'fare_items': [
            {'type': 'base', 'label': "<script>alert('x')</script>", 'amount': 10.0},
            {'type': 'bonus', 'label': ['Nested', ['Array']], 'amount': '5.0'}
        ]
    }
}

class BaselineDataAccess:
    def __init__(self):
        self.access_count = 0

    def _simulate_latency(self, ms: int):
        if ms and ms > 0:
            time.sleep(ms / 1000.0)

    def get_ride(self, ride_id: str, simulate_network_ms: int = 0) -> Dict[str, Any]:
        """Return the ride object (legacy: only totalFare)."""
        self.access_count += 1
        self._simulate_latency(simulate_network_ms)
        if not isinstance(ride_id, str):
            raise ValueError('invalid_ride_id')
        if ride_id not in _DATA:
            raise KeyError('not_found')
        ride = _DATA[ride_id]
        # Baseline: only return totalFare and meta
        return {'rideId': ride_id, 'totalFare': ride['totalFare']}

    def get_fare_items(self, ride_id: str, simulate_network_ms: int = 0) -> List[Dict[str, Any]]:
        """Return fare items breakdown for a ride."""
        self.access_count += 1
        self._simulate_latency(simulate_network_ms)
        if not isinstance(ride_id, str):
            raise ValueError('invalid_ride_id')
        if ride_id not in _DATA:
            raise KeyError('not_found')
        return _DATA[ride_id]['fare_items']
