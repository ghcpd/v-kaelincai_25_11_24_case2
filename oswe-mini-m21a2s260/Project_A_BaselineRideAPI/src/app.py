"""Baseline Ride API simulation

Endpoints simulated as functions for test harness to call. Baseline requires two separate calls
for ride and fare-items.
"""
import time
import random
from typing import Dict, Any, List

# Simulated datastore
_RIDES = {
    "ride-123": {"rideId": "ride-123", "totalFare": 23.50},
    "ride-weak": {"rideId": "ride-weak", "totalFare": 10.00},
    "ride-malformed": {"rideId": 9999, "totalFare": "NaN"},
}

_FARE_ITEMS = {
    "ride-123": [
        {"type": "base", "label": "Base Fare", "amount": 11.0},
        {"type": "distance", "label": "Distance Charge", "amount": 8.0},
        {"type": "tax", "label": "Tax", "amount": 4.5},
    ],
    "ride-weak": [
        {"type": "base", "label": "Base Fare", "amount": 5.0},
        {"type": "fee", "label": "Toll Fee", "amount": 5.0},
    ],
}

# Metrics for testing
_metrics = {"downstream_calls": 0}

def _simulate_latency(base_ms: int = 50):
    # Simulate network and processing latency
    jitter_ms = random.randint(0, 40)
    time.sleep((base_ms + jitter_ms) / 1000.0)

def get_ride(ride_id: str) -> Dict[str, Any]:
    """Return basic ride details (legacy)."""
    _simulate_latency(50)
    if not isinstance(ride_id, str):
        return {"status": 400, "error": "rideId must be string"}
    ride = _RIDES.get(ride_id)
    if not ride:
        return {"status": 404, "error": "ride not found"}
    return {"status": 200, "ride": {"rideId": ride["rideId"], "totalFare": ride["totalFare"]}}

def get_fare_items(ride_id: str) -> Dict[str, Any]:
    """Separate call that returns breakdown for baseline flow."""
    _simulate_latency(60)
    _metrics["downstream_calls"] += 1
    if not isinstance(ride_id, str):
        return {"status": 400, "error": "rideId must be string"}
    fare_items = _FARE_ITEMS.get(ride_id)
    if fare_items is None:
        return {"status": 404, "error": "fare items not found"}
    # Simple validation
    validated = []
    for item in fare_items:
        if not all(k in item for k in ("type", "label", "amount")):
            continue
        # sanitize label
        label = str(item["label"]).replace("<script>", "")
        # fix types
        type_str = str(item["type"]) if isinstance(item["type"], str) else "unknown"
        try:
            amount = float(item["amount"])
        except Exception:
            amount = 0.0
        validated.append({"type": type_str, "label": label, "amount": amount})
    return {"status": 200, "fareItems": validated}

def metrics_reset():
    _metrics["downstream_calls"] = 0

def metrics_get():
    return dict(_metrics)
