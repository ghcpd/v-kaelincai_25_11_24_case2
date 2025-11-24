"""Optimized data access with caching and combined retrieval.

Simulates downstream data fetches and exposes counters to measure query reduction.
"""
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from .models import FareItem

FAKE_DB_RIDES: Dict[str, Dict[str, Any]] = {
    "ride_normal": {"rideId": "ride_normal", "totalFare": Decimal("23.50"), "currency": "USD"},
    "ride_weak_network": {"rideId": "ride_weak_network", "totalFare": Decimal("41.75"), "currency": "USD"},
    "ride_malformed": {"rideId": "ride_malformed", "totalFare": Decimal("0"), "currency": "USD"},
    "ride_hidden_vuln": {"rideId": "ride_hidden_vuln", "totalFare": Decimal("19.99"), "currency": "USD"},
    "ride_nested": {"rideId": "ride_nested", "totalFare": Decimal("18.00"), "currency": "USD"},
}

# Breakdown may contain nested lists (to test flattening) and unsanitized labels
FAKE_DB_BREAKDOWN: Dict[str, Any] = {
    "ride_normal": [
        {"type": "base", "label": "Base Fare", "amount": Decimal("5.00")},
        {"type": "distance", "label": "Distance", "amount": Decimal("10.50")},
        {"type": "time", "label": "Time", "amount": Decimal("3.00")},
        {"type": "surge", "label": "Surge", "amount": Decimal("2.50")},
        {"type": "fees", "label": "Service Fee", "amount": Decimal("2.50")},
    ],
    "ride_weak_network": [
        {"type": "base", "label": "Base Fare", "amount": Decimal("8.00")},
        {"type": "distance", "label": "Distance", "amount": Decimal("20.00")},
        {"type": "time", "label": "Time", "amount": Decimal("6.75")},
        {"type": "fees", "label": "Service Fee", "amount": Decimal("7.00")},
    ],
    "ride_hidden_vuln": [
        {"type": "base", "label": "<script>alert(1)</script>", "amount": Decimal("10.00")},
        {"type": "distance", "label": "Distance", "amount": Decimal("9.99")},
    ],
    "ride_nested": [
        {"type": "base", "label": "Base", "amount": Decimal("5.00")},
        [
            {"type": "distance", "label": "Distance", "amount": Decimal("8.00")},
            {"type": "time", "label": "Time", "amount": Decimal("3.00")},
        ],
        {"type": "fees", "label": "Service Fee", "amount": Decimal("2.00")},
    ],
}

SIMULATED_DB_LATENCIES_MS = {
    "ride_only": 35,
    "breakdown_only": 50,
    "combined": 60,  # cheaper than ride+breakdown separately
}


class DataAccess:
    def __init__(self):
        self._ride_cache: Dict[str, Dict[str, Any]] = {}
        self._breakdown_cache: Dict[str, Any] = {}
        self.stats = {
            "ride_calls": 0,
            "breakdown_calls": 0,
            "combined_calls": 0,
        }

    def get_ride(self, ride_id: str) -> Optional[Dict[str, Any]]:
        if ride_id in self._ride_cache:
            return self._ride_cache[ride_id]
        self.stats["ride_calls"] += 1
        ride = FAKE_DB_RIDES.get(ride_id)
        if ride:
            self._ride_cache[ride_id] = ride
        return ride

    def get_breakdown(self, ride_id: str) -> Optional[Any]:
        if ride_id in self._breakdown_cache:
            return self._breakdown_cache[ride_id]
        self.stats["breakdown_calls"] += 1
        bd = FAKE_DB_BREAKDOWN.get(ride_id)
        if bd is not None:
            self._breakdown_cache[ride_id] = bd
        return bd

    def get_ride_with_breakdown(self, ride_id: str) -> Tuple[Optional[Dict[str, Any]], Optional[Any]]:
        self.stats["combined_calls"] += 1
        ride = FAKE_DB_RIDES.get(ride_id)
        bd = FAKE_DB_BREAKDOWN.get(ride_id)
        if ride:
            self._ride_cache.setdefault(ride_id, ride)
        if bd is not None:
            self._breakdown_cache.setdefault(ride_id, bd)
        return ride, bd


# Singleton instance used by API
DATA_ACCESS = DataAccess()
