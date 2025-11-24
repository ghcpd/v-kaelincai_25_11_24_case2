import time
import math
from typing import Dict, Any, List
from dataclasses import dataclass


def sanitize_label(label: str) -> str:
    # Very simple sanitizer to strip angle brackets
    if not isinstance(label, str):
        label = str(label)
    return label.replace("<", "&lt;").replace(">", "&gt;")


def validate_fare_item(item: Dict[str, Any]) -> Dict[str, Any]:
    # Validate types and sanitize
    allowed_types = {"base", "tax", "fee", "toll", "surge", "tip", "discount", "other"}
    if not isinstance(item, dict):
        raise ValueError("Invalid fare item format")
    typ = item.get("type")
    if typ not in allowed_types:
        raise ValueError(f"Invalid fare item type: {typ}")
    label = sanitize_label(item.get("label", ""))
    amount = item.get("amount")
    if isinstance(amount, str):
        try:
            amount = float(amount)
        except Exception:
            raise ValueError("Invalid amount")
    if not isinstance(amount, (int, float)):
        raise ValueError("Invalid amount")
    return {"type": typ, "label": label, "amount": float(amount)}


class BackendSimulator:
    def __init__(self):
        self.request_count = 0
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
            ],
        }

    def _simulate(self, latency_ms: int):
        self.request_count += 1
        if latency_ms > 0:
            time.sleep(latency_ms / 1000.0)

    def get_ride(self, ride_id: str, latency_ms: int = 0):
        self._simulate(latency_ms)
        if not isinstance(ride_id, str):
            raise ValueError("Invalid rideId")
        r = self.rides.get(ride_id)
        if not r:
            raise KeyError("Not found")
        return dict(r)

    def get_fare_items(self, ride_id: str, latency_ms: int = 0):
        self._simulate(latency_ms)
        if not isinstance(ride_id, str):
            raise ValueError("Invalid rideId")
        items = self.fare_items.get(ride_id)
        if items is None:
            raise KeyError("Not found")
        # Flatten nested lists into a single list of dicts
        def _flatten(itms):
            out = []
            for el in itms:
                if isinstance(el, list):
                    out.extend(_flatten(el))
                elif isinstance(el, dict):
                    out.append(dict(el))
                else:
                    # ignore other types
                    continue
            return out

        return _flatten(items)


class OptimizedRideAPI:
    def __init__(self, backend: BackendSimulator, cache_enabled: bool = True):
        self.backend = backend
        self._cache = {}
        self.cache_enabled = cache_enabled

    def _flatten_breakdown(self, items):
        flattened = []
        for it in items:
            if isinstance(it, list):
                flattened.extend(self._flatten_breakdown(it))
            else:
                flattened.append(it)
        return flattened

    def _get_cached(self, key):
        return self._cache.get(key)

    def _set_cached(self, key, value):
        if self.cache_enabled:
            self._cache[key] = value

    def get_ride(self, ride_id: str, includeFareBreakdown: bool = False, latency_ms: int = 0):
        if not isinstance(ride_id, str):
            return {"error": "Invalid rideId", "status": 400}
        try:
            if includeFareBreakdown:
                # Check cache key
                cache_key = f"ride:{ride_id}:breakdown"
                cached = self._get_cached(cache_key)
                if cached:
                    return dict(cached)

                ride = self.backend.get_ride(ride_id, latency_ms)
                raw_items = self.backend.get_fare_items(ride_id, latency_ms)
                # handle nested arrays if any
                items_flat = self._flatten_breakdown(raw_items)
                validated = []
                for it in items_flat:
                    # Validate each item
                    try:
                        validated.append(validate_fare_item(it))
                    except Exception:
                        # Skip invalid items (robustness)
                        continue

                total = sum([it["amount"] for it in validated])
                # Reconcile total with stored totalFare; if differs, include discrepancy
                discrepancy = round(ride.get("totalFare", 0.0) - total, 6)
                resp = {"rideId": ride_id, "totalFare": ride.get("totalFare"), "fareBreakdown": validated}
                if abs(discrepancy) > 1e-6:
                    resp["discrepancy"] = discrepancy
                self._set_cached(cache_key, resp)
                return resp
            else:
                # Preserve legacy representation
                ride = self.backend.get_ride(ride_id, latency_ms)
                return {"rideId": ride["rideId"], "totalFare": ride["totalFare"]}
        except ValueError:
            return {"error": "Invalid rideId", "status": 400}
        except KeyError:
            return {"error": "Not found", "status": 404}
