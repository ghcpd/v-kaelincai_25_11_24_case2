"""
Baseline API simulation: legacy GET /rides/{id} returns only totalFare; separate get_fare_items returns breakdown.
This file exposes a client-like interface for the tests.
"""
from .data_store import BaselineDataAccess
from typing import Dict, Any, List, Optional

class BaselineAPI:
    def __init__(self):
        self.da = BaselineDataAccess()

    def get_ride(self, ride_id: str, simulate_network_ms: int = 0) -> Dict[str, Any]:
        return self.da.get_ride(ride_id, simulate_network_ms=simulate_network_ms)

    def get_fare_items(self, ride_id: str, simulate_network_ms: int = 0) -> List[Dict[str, Any]]:
        return self.da.get_fare_items(ride_id, simulate_network_ms=simulate_network_ms)

    def fetch_ride_with_legacy_flow(self, ride_id: str, simulate_network_ms: int = 0) -> Dict[str, Any]:
        """Simulate client flow: calls get_ride then get_fare_items in sequence.
        Returns combined result and metrics for tests.
        """
        metrics = {'calls': 0}
        result = {}
        try:
            r = self.get_ride(ride_id, simulate_network_ms=simulate_network_ms)
            metrics['calls'] += 1
            result.update(r)
            items = self.get_fare_items(ride_id, simulate_network_ms=simulate_network_ms)
            metrics['calls'] += 1
            result['fareBreakdown_requested_separately'] = True
            result['fareBreakdown'] = items
            return {'status': 'ok', 'payload': result, 'metrics': metrics}
        except ValueError as e:
            return {'status': 'error', 'error': str(e), 'metrics': metrics}
        except KeyError as e:
            return {'status': 'error', 'error': 'not_found', 'metrics': metrics}
