"""Optimized Ride API simulation

Supports includeFareBreakdown=true to return fare breakdown in the same call.
Uses simple in-memory caching for downstream fetches and stricter validation.
"""
import time
import random
from functools import lru_cache
from typing import Dict, Any, List

# Use same data set as baseline
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

_metrics = {"downstream_calls": 0}

def _simulate_latency(base_ms: int = 30):
    jitter_ms = random.randint(0, 30)
    time.sleep((base_ms + jitter_ms) / 1000.0)

@lru_cache(maxsize=128)
def _fetch_fare_items_cached(ride_id: str):
    _metrics["downstream_calls"] += 1
    # simulate slightly higher latency on first fetch
    _simulate_latency(40)
    items = _FARE_ITEMS.get(ride_id)
    return items

def _validate_and_sanitize(items):
    out = []
    if not isinstance(items, list):
        return out
    for i in items:
        if not isinstance(i, dict):
            continue
        t = i.get("type")
        label = i.get("label")
        amount = i.get("amount")
        if not isinstance(t, str) or not isinstance(label, str):
            continue
        try:
            amt = float(amount)
        except Exception:
            continue
        # ban suspicious content
        if "<script>" in label.lower():
            # don't include potentially malicious labels
            label = "[REDACTED]"
        out.append({"type": t, "label": label, "amount": amt})
    return out

def get_ride(ride_id: str, includeFareBreakdown: bool = False) -> Dict[str, Any]:
    """Return ride details; optionally attach fareBreakdown."""
    _simulate_latency(20)
    if not isinstance(ride_id, str):
        return {"status": 400, "error": "rideId must be string"}
    ride = _RIDES.get(ride_id)
    if not ride:
        return {"status": 404, "error": "ride not found"}

    response = {"status": 200, "ride": {"rideId": ride["rideId"], "totalFare": ride["totalFare"]}}
    if includeFareBreakdown:
        items = _fetch_fare_items_cached(ride_id)
        validated = _validate_and_sanitize(items)
        # reconcile total
        comp = sum(x["amount"] for x in validated) if validated else 0.0
        if abs(comp - ride["totalFare"]) > 0.1:
            # if mismatch, attach reconciliation metadata
            response["fareBreakdown"] = {"items": validated, "reconciledTotal": comp, "warning": "total mismatch"}
        else:
            response["fareBreakdown"] = {"items": validated}
    return response

def metrics_reset():
    _metrics["downstream_calls"] = 0

def metrics_get():
    return dict(_metrics)
