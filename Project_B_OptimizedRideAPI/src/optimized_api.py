"""
Project B: Optimized Ride Fare API
Enhanced implementation supporting includeFareBreakdown parameter.
Demonstrates performance optimization with single-call fare retrieval,
caching, robust validation, and backward compatibility.
"""
import json
import re
import time
import html
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)


@dataclass
class FareItem:
    """Validated fare breakdown item"""
    type: str
    label: str
    amount: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class OptimizedRideResponse:
    """Optimized ride response with optional fare breakdown"""
    rideId: str
    distance: float
    duration: int
    status: str
    totalFare: float
    currency: str
    fareBreakdown: Optional[List[Dict[str, Any]]] = None


class FareBreakdownCache:
    """Simple cache for fare breakdowns with TTL"""

    def __init__(self, ttl_seconds: int = 300):
        """
        Initialize cache.
        
        Args:
            ttl_seconds: Time-to-live for cache entries
        """
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, tuple] = {}  # (data, timestamp)

    def get(self, key: str) -> Optional[Any]:
        """Get cached value if not expired"""
        if key in self.cache:
            data, timestamp = self.cache[key]
            if datetime.now() - timestamp < timedelta(seconds=self.ttl_seconds):
                return data
            else:
                del self.cache[key]
        return None

    def set(self, key: str, value: Any) -> None:
        """Cache a value with current timestamp"""
        self.cache[key] = (value, datetime.now())

    def clear(self) -> None:
        """Clear all cache entries"""
        self.cache.clear()


class OptimizedRideAPI:
    """
    Optimized API implementation with efficient fare breakdown retrieval.
    Supports includeFareBreakdown query parameter while maintaining backward compatibility.
    """

    def __init__(self, data_store: Optional[Dict[str, Any]] = None, network_latency_ms: int = 50):
        """
        Initialize optimized API.
        
        Args:
            data_store: Pre-loaded ride and fare data
            network_latency_ms: Simulated network latency in milliseconds
        """
        self.data_store = data_store or {}
        self.network_latency_ms = network_latency_ms
        self.backend_call_count = 0
        self.total_latency_ms = 0
        self.breakdown_cache = FareBreakdownCache(ttl_seconds=300)

    def _simulate_network_latency(self) -> None:
        """Simulate network latency for each backend call"""
        delay = self.network_latency_ms / 1000.0
        time.sleep(delay)
        self.total_latency_ms += self.network_latency_ms

    def _validate_ride_id(self, ride_id: str) -> bool:
        """
        Validate ride ID format to prevent injection attacks.
        Only alphanumeric, underscore, and hyphen allowed.
        """
        if not isinstance(ride_id, str):
            return False
        if not re.match(r'^ride_[a-zA-Z0-9_-]+$', ride_id):
            return False
        return True

    def _sanitize_label(self, label: str) -> str:
        """
        Sanitize fare item label to prevent XSS attacks.
        
        Args:
            label: The label to sanitize
            
        Returns:
            Sanitized label with HTML entities escaped
        """
        if not isinstance(label, str):
            label = str(label)
        return html.escape(label, quote=True)

    def _validate_and_normalize_breakdown(self, breakdown_items: List[Dict[str, Any]]) -> tuple[bool, List[Dict[str, Any]], str]:
        """
        Validate and normalize fare breakdown items.
        Enforces strict type checking and sanitization.
        
        Args:
            breakdown_items: Raw breakdown items from data store
            
        Returns:
            Tuple of (is_valid, normalized_items, error_message)
        """
        if not isinstance(breakdown_items, list):
            return False, [], "Breakdown items must be a list"

        normalized = []
        total_amount = 0

        for idx, item in enumerate(breakdown_items):
            if not isinstance(item, dict):
                return False, [], f"Item {idx} is not a dictionary"

            # Validate required fields
            if "type" not in item or "label" not in item or "amount" not in item:
                return False, [], f"Item {idx} missing required fields (type, label, amount)"

            # Type validation
            if not isinstance(item["type"], str):
                return False, [], f"Item {idx}: type must be string"

            # Label validation and sanitization
            if not isinstance(item["label"], str):
                return False, [], f"Item {idx}: label must be string"
            sanitized_label = self._sanitize_label(item["label"])

            # Amount validation
            try:
                amount = float(item["amount"])
            except (TypeError, ValueError):
                return False, [], f"Item {idx}: amount must be numeric"

            normalized.append({
                "type": item["type"],
                "label": sanitized_label,
                "amount": amount
            })
            total_amount += amount

        return True, normalized, ""

    def get_ride(self, ride_id: str, include_fare_breakdown: bool = False) -> Dict[str, Any]:
        """
        Get ride details with optional fare breakdown (single optimized call).
        Supports backward compatibility by omitting breakdown when not requested.
        
        Args:
            ride_id: The ID of the ride
            include_fare_breakdown: Whether to include fare breakdown
            
        Returns:
            Dict containing ride details and optional fare breakdown
        """
        # Validate ride ID
        if not self._validate_ride_id(ride_id):
            return {
                "status": 400,
                "error_code": "INVALID_RIDE_ID",
                "error_message": "Ride ID contains invalid characters"
            }

        # Fetch ride data (always 1 call)
        self.backend_call_count += 1
        self._simulate_network_latency()

        ride_data = self.data_store.get(ride_id)
        if not ride_data:
            return {
                "status": 404,
                "error_code": "RIDE_NOT_FOUND",
                "error_message": f"Ride {ride_id} not found"
            }

        response = {
            "status": 200,
            "rideId": ride_data["rideId"],
            "distance": ride_data["distance"],
            "duration": ride_data["duration"],
            "rideStatus": ride_data["status"],
            "totalFare": ride_data["totalFare"],
            "currency": ride_data["currency"]
        }

        # Optionally fetch and attach fare breakdown (no additional call needed)
        if include_fare_breakdown:
            # Check cache first
            cached_breakdown = self.breakdown_cache.get(ride_id)
            if cached_breakdown:
                response["fareBreakdown"] = cached_breakdown
                logger.info(f"Retrieved fare breakdown for {ride_id} from cache")
            else:
                # Fetch from data store
                fare_breakdown = self.data_store.get(f"{ride_id}_breakdown")
                if fare_breakdown:
                    is_valid, normalized, error = self._validate_and_normalize_breakdown(fare_breakdown)
                    if not is_valid:
                        return {
                            "status": 400,
                            "error_code": "INVALID_BREAKDOWN",
                            "error_message": f"Invalid fare breakdown: {error}"
                        }
                    
                    # Cache for future requests
                    self.breakdown_cache.set(ride_id, normalized)
                    response["fareBreakdown"] = normalized
                    logger.info(f"Retrieved fare breakdown for {ride_id}: {len(normalized)} items")
        else:
            # Legacy client - no breakdown field included
            logger.info(f"Retrieved ride {ride_id} (legacy mode): ${ride_data['totalFare']} {ride_data['currency']}")

        return response

    def reset_metrics(self) -> None:
        """Reset metrics counters"""
        self.backend_call_count = 0
        self.total_latency_ms = 0

    def get_metrics(self) -> Dict[str, Any]:
        """Return current metrics"""
        return {
            "backend_calls": self.backend_call_count,
            "total_latency_ms": self.total_latency_ms,
            "avg_latency_per_call_ms": self.total_latency_ms / self.backend_call_count if self.backend_call_count > 0 else 0,
            "cache_size": len(self.breakdown_cache.cache)
        }


def load_test_data(test_data_path: str) -> Dict[str, Any]:
    """Load test data from JSON file"""
    with open(test_data_path, 'r') as f:
        data = json.load(f)

    # Transform test data into data store format
    data_store = {}

    # Add ride data
    for ride_id, ride_info in data.get("test_data_rides", {}).items():
        data_store[ride_id] = ride_info

    # Add fare breakdown data
    for ride_id, breakdown_items in data.get("fare_breakdown_data", {}).items():
        data_store[f"{ride_id}_breakdown"] = breakdown_items

    return data_store
