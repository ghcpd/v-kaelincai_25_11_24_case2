"""
Project A: Baseline Ride Fare API
Legacy implementation requiring multiple endpoints to get ride and fare data.
Demonstrates performance bottleneck of sequential requests.
"""
import json
import re
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class RideResponse:
    """Baseline ride response without fare breakdown"""
    rideId: str
    distance: float
    duration: int  # seconds
    status: str
    totalFare: float
    currency: str


class BaselineRideAPI:
    """
    Baseline API implementation representing legacy workflow.
    Requires multiple endpoint calls to retrieve ride + fare information.
    """

    def __init__(self, data_store: Optional[Dict[str, Any]] = None, network_latency_ms: int = 50):
        """
        Initialize the baseline API.
        
        Args:
            data_store: Pre-loaded ride and fare data
            network_latency_ms: Simulated network latency in milliseconds
        """
        self.data_store = data_store or {}
        self.network_latency_ms = network_latency_ms
        self.backend_call_count = 0
        self.total_latency_ms = 0

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
        # Allow format: ride_[alphanumeric]
        if not re.match(r'^ride_[a-zA-Z0-9_-]+$', ride_id):
            return False
        return True

    def get_ride(self, ride_id: str) -> Dict[str, Any]:
        """
        Get ride details (Endpoint 1/2 in baseline flow).
        Returns only ride summary without fare breakdown.
        
        Args:
            ride_id: The ID of the ride
            
        Returns:
            Dict containing ride details and totalFare
        """
        self.backend_call_count += 1
        self._simulate_network_latency()

        # Validate ride ID
        if not self._validate_ride_id(ride_id):
            return {
                "status": 400,
                "error_code": "INVALID_RIDE_ID",
                "error_message": "Ride ID contains invalid characters"
            }

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

        logger.info(f"Retrieved ride {ride_id}: ${ride_data['totalFare']} {ride_data['currency']}")
        return response

    def get_fare_items(self, ride_id: str) -> Dict[str, Any]:
        """
        Get fare breakdown details (Endpoint 2/2 in baseline flow).
        This is a separate call - not included in main ride response.
        
        Args:
            ride_id: The ID of the ride
            
        Returns:
            Dict containing breakdown items or error
        """
        self.backend_call_count += 1
        self._simulate_network_latency()

        # Validate ride ID
        if not self._validate_ride_id(ride_id):
            return {
                "status": 400,
                "error_code": "INVALID_RIDE_ID",
                "error_message": "Ride ID contains invalid characters"
            }

        fare_breakdown = self.data_store.get(f"{ride_id}_breakdown")
        if not fare_breakdown:
            return {
                "status": 404,
                "error_code": "BREAKDOWN_NOT_FOUND",
                "error_message": f"Fare breakdown for {ride_id} not found"
            }

        response = {
            "status": 200,
            "rideId": ride_id,
            "fareItems": fare_breakdown
        }

        logger.info(f"Retrieved fare breakdown for {ride_id}: {len(fare_breakdown)} items")
        return response

    def get_ride_with_breakdown(self, ride_id: str) -> Dict[str, Any]:
        """
        Baseline approach to get complete ride + fare info (uses 2 calls).
        This simulates what mobile clients must do in the legacy system.
        
        Args:
            ride_id: The ID of the ride
            
        Returns:
            Combined ride + breakdown data from 2 sequential calls
        """
        # Call 1: Get ride details
        ride_response = self.get_ride(ride_id)
        if ride_response.get("status") != 200:
            return ride_response

        # Call 2: Get fare breakdown (sequential - blocked until call 1 completes)
        breakdown_response = self.get_fare_items(ride_id)
        if breakdown_response.get("status") != 200:
            return breakdown_response

        # Merge responses
        ride_response["fareBreakdown"] = breakdown_response.get("fareItems", [])
        return ride_response

    def reset_metrics(self) -> None:
        """Reset metrics counters"""
        self.backend_call_count = 0
        self.total_latency_ms = 0

    def get_metrics(self) -> Dict[str, Any]:
        """Return current metrics"""
        return {
            "backend_calls": self.backend_call_count,
            "total_latency_ms": self.total_latency_ms,
            "avg_latency_per_call_ms": self.total_latency_ms / self.backend_call_count if self.backend_call_count > 0 else 0
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
