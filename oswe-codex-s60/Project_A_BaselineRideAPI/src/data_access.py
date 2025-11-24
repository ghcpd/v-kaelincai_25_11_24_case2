"""Simulated data access layer for the legacy baseline API.

This layer returns ride totals and fare breakdowns from in-memory fixtures
and computes simulated downstream latencies. It intentionally does not
perform strict validation to reflect a legacy system.
"""
from typing import Optional, List, Dict
from .models import RideTotal, FareItem

# In-memory fixtures used for deterministic testing
FAKE_DB_RIDES: Dict[str, RideTotal] = {
    "ride_normal": RideTotal(ride_id="ride_normal", total_fare=23.50),
    "ride_weak_network": RideTotal(ride_id="ride_weak_network", total_fare=41.75),
    "ride_malformed": RideTotal(ride_id="ride_malformed", total_fare=0.0),
    "ride_hidden_vuln": RideTotal(ride_id="ride_hidden_vuln", total_fare=19.99),
}

FAKE_DB_BREAKDOWN: Dict[str, List[FareItem]] = {
    "ride_normal": [
        FareItem(type="base", label="Base Fare", amount=5.00),
        FareItem(type="distance", label="Distance", amount=10.50),
        FareItem(type="time", label="Time", amount=3.00),
        FareItem(type="surge", label="Surge", amount=2.50),
        FareItem(type="fees", label="Service Fee", amount=2.50),
    ],
    "ride_weak_network": [
        FareItem(type="base", label="Base Fare", amount=8.00),
        FareItem(type="distance", label="Distance", amount=20.00),
        FareItem(type="time", label="Time", amount=6.75),
        FareItem(type="fees", label="Service Fee", amount=7.00),
    ],
    "ride_hidden_vuln": [
        FareItem(type="base", label="<script>alert(1)</script>", amount=10.00),
        FareItem(type="distance", label="Distance", amount=9.99),
    ],
}


def get_ride_total(ride_id: str) -> Optional[RideTotal]:
    return FAKE_DB_RIDES.get(ride_id)


def get_fare_items(ride_id: str) -> Optional[List[FareItem]]:
    return FAKE_DB_BREAKDOWN.get(ride_id)
