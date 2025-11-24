"""Legacy baseline API simulation.

Two endpoints:
- get_ride_details(ride_id): returns only total fare (no breakdown)
- get_ride_fare_items(ride_id): returns fare breakdown in a separate call

Both functions return a response dict with `status`, optional `data`, optional
`error`, and `metrics` including simulated latency and request count.
"""
import random
import time
from typing import Dict, Any, Optional

from .models import ApiResponse
from . import data_access


DEFAULT_NETWORK_MS = 120  # nominal per-request network latency
DEFAULT_DOWNSTREAM_MS = {
    "ride_total": 40,
    "fare_items": 55,
}


def _simulated_latency(base_ms: int, jitter_ms: int = 0, seed: int = 0) -> int:
    rnd = random.Random(seed)
    if jitter_ms <= 0:
        return base_ms
    return max(0, int(rnd.uniform(base_ms - jitter_ms, base_ms + jitter_ms)))


def get_ride_details(ride_id: Any, network: Optional[Dict[str, Any]] = None, seed: int = 0) -> Dict[str, Any]:
    network = network or {}
    network_ms = network.get("latency_ms", DEFAULT_NETWORK_MS)
    jitter_ms = network.get("jitter_ms", 0)
    latency_ms = _simulated_latency(network_ms, jitter_ms, seed)

    if not isinstance(ride_id, str) or not ride_id:
        return {
            "status": "error",
            "error": "Invalid ride_id",
            "data": None,
            "metrics": {
                "latency_ms": latency_ms,
                "request_count": 1,
                "downstream_calls": 0,
            },
        }

    ride = data_access.get_ride_total(ride_id)
    if ride is None:
        return {
            "status": "error",
            "error": "Ride not found",
            "data": None,
            "metrics": {
                "latency_ms": latency_ms + DEFAULT_DOWNSTREAM_MS["ride_total"],
                "request_count": 1,
                "downstream_calls": 1,
            },
        }

    processing_ms = DEFAULT_DOWNSTREAM_MS["ride_total"]
    total_latency = latency_ms + processing_ms
    return {
        "status": "ok",
        "error": None,
        "data": {
            "rideId": ride.ride_id,
            "totalFare": ride.total_fare,
            "currency": ride.currency,
        },
        "metrics": {
            "latency_ms": total_latency,
            "request_count": 1,
            "downstream_calls": 1,
        },
    }


def get_ride_fare_items(ride_id: Any, network: Optional[Dict[str, Any]] = None, seed: int = 0) -> Dict[str, Any]:
    network = network or {}
    network_ms = network.get("latency_ms", DEFAULT_NETWORK_MS)
    jitter_ms = network.get("jitter_ms", 0)
    latency_ms = _simulated_latency(network_ms, jitter_ms, seed)

    if not isinstance(ride_id, str) or not ride_id:
        return {
            "status": "error",
            "error": "Invalid ride_id",
            "data": None,
            "metrics": {
                "latency_ms": latency_ms,
                "request_count": 1,
                "downstream_calls": 0,
            },
        }

    items = data_access.get_fare_items(ride_id)
    if items is None:
        return {
            "status": "error",
            "error": "Fare breakdown not found",
            "data": None,
            "metrics": {
                "latency_ms": latency_ms + DEFAULT_DOWNSTREAM_MS["fare_items"],
                "request_count": 1,
                "downstream_calls": 1,
            },
        }

    processing_ms = DEFAULT_DOWNSTREAM_MS["fare_items"]
    total_latency = latency_ms + processing_ms
    return {
        "status": "ok",
        "error": None,
        "data": {
            "rideId": ride_id,
            "fareItems": [
                {
                    "type": it.type,
                    "label": it.label,
                    "amount": it.amount,
                    "currency": it.currency,
                }
                for it in items
            ],
        },
        "metrics": {
            "latency_ms": total_latency,
            "request_count": 1,
            "downstream_calls": 1,
        },
    }
