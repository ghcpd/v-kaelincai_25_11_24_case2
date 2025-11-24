import time
import math
from typing import Dict, Any, List, Tuple


class BackendSimulator:
    """Simulates downstream datastore and API calls for ride and fare items.
    Each invocation might add simulated latency and increments request counts.
    """

    def __init__(self):
        self.request_count = 0
        # Sample data
        self.rides = {
            "ride_001": {"rideId": "ride_001", "totalFare": 42.5},
            "ride_002": {"rideId": "ride_002", "totalFare": 13.2},
            "ride_injection": {"rideId": "ride_injection", "totalFare": 15.0},
            "ride_nested": {"rideId": "ride_nested", "totalFare": 20.0},
            "ride_string_amount": {"rideId": "ride_string_amount", "totalFare": 12.5},
        }
        self.fare_items = {
            "ride_001": [
                {"type": "base", "label": "Base fare", "amount": 30.0},
                {"type": "tax", "label": "Tax", "amount": 2.5},
                {"type": "fee", "label": "Service fee", "amount": 10.0}
            ],
            "ride_002": [
                {"type": "base", "label": "Base fare", "amount": 10.0},
                {"type": "tax", "label": "Tax", "amount": 3.2}
            ],
            "ride_injection": [
                {"type": "base", "label": "Base", "amount": 10.0},
                {"type": "tip", "label": "<script>alert(1)</script>", "amount": 5.0}
            ],
            "ride_nested": [
                [{"type": "base", "label": "Base fare", "amount": 12.0}, {"type": "tax", "label": "Tax", "amount": 1.0}],
                {"type": "fee", "label": "Service fee", "amount": 7.0}
            ],
            "ride_string_amount": [
                {"type": "base", "label": "Base fare", "amount": "10.0"},
                {"type": "tax", "label": "Tax", "amount": "2.5"}
            ]
        }

    def _simulate(self, latency_ms: int):
        self.request_count += 1
        if latency_ms > 0:
            time.sleep(latency_ms / 1000.0)

    def get_ride(self, ride_id: str, latency_ms: int = 0) -> Dict[str, Any]:
        self._simulate(latency_ms)
        if not isinstance(ride_id, str):
            raise ValueError("Invalid rideId")
        ride = self.rides.get(ride_id)
        if not ride:
            raise KeyError("Not found")
        return ride.copy()

    def get_fare_items(self, ride_id: str, latency_ms: int = 0) -> List[Dict[str, Any]]:
        self._simulate(latency_ms)
        if not isinstance(ride_id, str):
            raise ValueError("Invalid rideId")
        items = self.fare_items.get(ride_id)
        if items is None:
            raise KeyError("Not found")
        # flatten nested lists into a single list and return deep copies
        def _flatten(itms):
            out = []
            for el in itms:
                if isinstance(el, list):
                    out.extend(_flatten(el))
                elif isinstance(el, dict):
                    out.append(dict(el))
                else:
                    # unknown type - ignore
                    continue
            return out
        return _flatten(items)


class BaselineRideAPI:
    """Baseline API simulating legacy endpoints:
    - get_ride: returns only totalFare
    - get_fare_items: returns breakdown
    """

    def __init__(self, backend: BackendSimulator):
        self.backend = backend

    def get_ride(self, ride_id: str, latency_ms: int = 0) -> Dict[str, Any]:
        # Only returns totalFare
        try:
            ride = self.backend.get_ride(ride_id, latency_ms)
            return {"rideId": ride["rideId"], "totalFare": ride["totalFare"]}
        except ValueError:
            return {"error": "Invalid rideId", "status": 400}
        except KeyError:
            return {"error": "Not found", "status": 404}

    def get_fare_items(self, ride_id: str, latency_ms: int = 0) -> Dict[str, Any]:
        try:
            items = self.backend.get_fare_items(ride_id, latency_ms)
            return {"rideId": ride_id, "fareItems": items}
        except ValueError:
            return {"error": "Invalid rideId", "status": 400}
        except KeyError:
            return {"error": "Not found", "status": 404}
