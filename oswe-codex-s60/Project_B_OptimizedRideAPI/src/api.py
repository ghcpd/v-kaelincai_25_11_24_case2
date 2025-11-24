"""Optimized API simulation with includeFareBreakdown support, caching, and validation."""
import random
from decimal import Decimal
from typing import Any, Dict, Optional

from .models import ApiResponse, RideDetails, FareItem
from .data_access import DATA_ACCESS, SIMULATED_DB_LATENCIES_MS
from .utils import flatten_breakdown

DEFAULT_NETWORK_MS = 120


def _simulated_latency(base_ms: int, jitter_ms: int = 0, seed: int = 0) -> int:
    rnd = random.Random(seed)
    if jitter_ms <= 0:
        return base_ms
    return max(0, int(rnd.uniform(base_ms - jitter_ms, base_ms + jitter_ms)))


def _build_error(message: str, latency_ms: int, downstream_calls: int = 0) -> Dict[str, Any]:
    return {
        "status": "error",
        "error": message,
        "data": None,
        "metrics": {
            "latency_ms": latency_ms,
            "request_count": 1,
            "downstream_calls": downstream_calls,
        },
    }


def get_ride_details(
    ride_id: Any,
    includeFareBreakdown: bool = False,
    network: Optional[Dict[str, Any]] = None,
    seed: int = 0,
) -> Dict[str, Any]:
    network = network or {}
    network_ms = network.get("latency_ms", DEFAULT_NETWORK_MS)
    jitter_ms = network.get("jitter_ms", 0)
    latency_ms = _simulated_latency(network_ms, jitter_ms, seed)

    # Validate ride_id
    if not isinstance(ride_id, str) or not ride_id.strip():
        return _build_error("Invalid ride_id", latency_ms)
    ride_id = ride_id.strip()

    if not includeFareBreakdown:
        ride = DATA_ACCESS.get_ride(ride_id)
        if ride is None:
            return _build_error("Ride not found", latency_ms + SIMULATED_DB_LATENCIES_MS["ride_only"], downstream_calls=1)

        # Legacy-compatible payload (no fareBreakdown field)
        api_resp = ApiResponse(
            status="ok",
            data=RideDetails(rideId=ride["rideId"], totalFare=ride["totalFare"], currency=ride["currency"]),
            error=None,
            metrics={
                "latency_ms": latency_ms + SIMULATED_DB_LATENCIES_MS["ride_only"],
                "request_count": 1,
                "downstream_calls": 1,
                "cache_hits": int(ride_id in DATA_ACCESS._ride_cache),
            },
        )
        payload = api_resp.dict()
        # Remove fareBreakdown if present (should be None); pydantic includes it as None; drop explicitly
        if payload.get("data"):
            payload["data"].pop("fareBreakdown", None)
        return payload

    # includeFareBreakdown path
    ride, raw_breakdown = DATA_ACCESS.get_ride_with_breakdown(ride_id)
    if ride is None:
        return _build_error("Ride not found", latency_ms + SIMULATED_DB_LATENCIES_MS["combined"], downstream_calls=1)

    flat_items = flatten_breakdown(raw_breakdown)
    valid_items = []
    invalid_items = []
    for raw in flat_items:
        try:
            item = FareItem(**raw)
            valid_items.append(item)
        except Exception as e:  # pylint: disable=broad-except
            invalid_items.append({"raw": raw, "error": str(e)})

    if not valid_items:
        return _build_error(
            "Fare breakdown invalid",
            latency_ms + SIMULATED_DB_LATENCIES_MS["combined"],
            downstream_calls=1,
        )

    total = ride["totalFare"]
    sum_breakdown = sum((it.amount for it in valid_items), Decimal("0"))
    mismatch = abs(sum_breakdown - total) > Decimal("0.01")

    ride_details = RideDetails(
        rideId=ride["rideId"],
        totalFare=ride["totalFare"],
        currency=ride["currency"],
        fareBreakdown=valid_items,
    )
    api_resp = ApiResponse(
        status="ok",
        data=ride_details,
        error=None,
        metrics={
            "latency_ms": latency_ms + SIMULATED_DB_LATENCIES_MS["combined"],
            "request_count": 1,
            "downstream_calls": 1,
            "cache_hits": int(ride_id in DATA_ACCESS._ride_cache and ride_id in DATA_ACCESS._breakdown_cache),
            "invalid_items": invalid_items,
            "mismatch_total": mismatch,
            "sum_breakdown": float(sum_breakdown),
        },
    )
    payload = api_resp.dict()
    return payload
