"""
Baseline Ride Fare API - Legacy Implementation
Represents the old workflow requiring multiple endpoints:
1. GET /rides/{rideId} - returns basic ride info with total fare only
2. GET /rides/{rideId}/fare-items - returns detailed fare breakdown
"""

import time
import json
import re
from typing import Dict, Any, List, Optional


class RideDatabase:
    """Mock database for ride information"""
    
    def __init__(self):
        self.rides = {
            "ride_12345": {
                "ride_id": "ride_12345",
                "driver_id": "driver_001",
                "rider_id": "rider_001",
                "pickup": "123 Main St",
                "dropoff": "456 Oak Ave",
                "distance_miles": 10,
                "duration_minutes": 20,
                "status": "completed",
                "total_fare": 25.50
            },
            "ride_67890": {
                "ride_id": "ride_67890",
                "driver_id": "driver_002",
                "rider_id": "rider_002",
                "pickup": "789 Pine Rd",
                "dropoff": "321 Elm St",
                "distance_miles": 18,
                "duration_minutes": 35,
                "status": "completed",
                "total_fare": 42.75
            }
        }
        
        self.fare_items = {
            "ride_12345": [
                {"type": "base", "label": "Base Fare", "amount": 5.00},
                {"type": "distance", "label": "Distance (10 miles)", "amount": 15.00},
                {"type": "time", "label": "Time (20 min)", "amount": 4.00},
                {"type": "tax", "label": "Tax", "amount": 1.50}
            ],
            "ride_67890": [
                {"type": "base", "label": "Base Fare", "amount": 8.00},
                {"type": "distance", "label": "Distance (18 miles)", "amount": 27.00},
                {"type": "time", "label": "Time (35 min)", "amount": 5.25},
                {"type": "surge", "label": "Surge Pricing", "amount": 2.00},
                {"type": "tax", "label": "Tax", "amount": 0.50}
            ]
        }
    
    def get_ride(self, ride_id: str) -> Optional[Dict[str, Any]]:
        """Simulate database query for ride data"""
        time.sleep(0.05)  # Simulate DB query latency
        return self.rides.get(ride_id)
    
    def get_fare_items(self, ride_id: str) -> Optional[List[Dict[str, Any]]]:
        """Simulate separate database query for fare breakdown"""
        time.sleep(0.05)  # Simulate DB query latency
        return self.fare_items.get(ride_id)


class BaselineRideAPI:
    """Legacy API implementation - requires multiple calls"""
    
    def __init__(self, network_latency: float = 0.1):
        self.db = RideDatabase()
        self.network_latency = network_latency
        self.request_count = 0
    
    def _simulate_network_delay(self):
        """Simulate network latency"""
        time.sleep(self.network_latency)
        self.request_count += 1
    
    def get_ride(self, ride_id: str) -> Dict[str, Any]:
        """
        GET /rides/{rideId}
        Returns basic ride information with total fare only.
        Legacy clients must make a separate call for fare breakdown.
        """
        self._simulate_network_delay()
        
        # Validate ride ID format (basic validation)
        if not ride_id or not isinstance(ride_id, str):
            return {
                "status": "error",
                "error": "Invalid ride ID format",
                "error_type": "invalid_ride_id"
            }
        
        ride = self.db.get_ride(ride_id)
        
        if not ride:
            return {
                "status": "error",
                "error": "Ride not found",
                "error_type": "ride_not_found"
            }
        
        # Legacy response - no fare breakdown included
        return {
            "status": "success",
            "data": {
                "ride_id": ride["ride_id"],
                "driver_id": ride["driver_id"],
                "rider_id": ride["rider_id"],
                "pickup": ride["pickup"],
                "dropoff": ride["dropoff"],
                "distance_miles": ride["distance_miles"],
                "duration_minutes": ride["duration_minutes"],
                "ride_status": ride["status"],
                "total_fare": ride["total_fare"]
            }
        }
    
    def get_fare_items(self, ride_id: str) -> Dict[str, Any]:
        """
        GET /rides/{rideId}/fare-items
        Separate endpoint for fare breakdown - requires additional round trip.
        """
        self._simulate_network_delay()
        
        if not ride_id or not isinstance(ride_id, str):
            return {
                "status": "error",
                "error": "Invalid ride ID format",
                "error_type": "invalid_ride_id"
            }
        
        # First verify ride exists
        ride = self.db.get_ride(ride_id)
        if not ride:
            return {
                "status": "error",
                "error": "Ride not found",
                "error_type": "ride_not_found"
            }
        
        fare_items = self.db.get_fare_items(ride_id)
        
        if not fare_items:
            return {
                "status": "error",
                "error": "Fare breakdown not available",
                "error_type": "fare_not_found"
            }
        
        return {
            "status": "success",
            "data": {
                "ride_id": ride_id,
                "fare_breakdown": fare_items
            }
        }
    
    def get_complete_ride_info(self, ride_id: str) -> Dict[str, Any]:
        """
        Convenience method that simulates what a client must do:
        Make two separate API calls to get complete information.
        This demonstrates the performance bottleneck.
        """
        start_time = time.time()
        
        # First call: get basic ride info
        ride_response = self.get_ride(ride_id)
        
        if ride_response["status"] == "error":
            elapsed = time.time() - start_time
            return {
                **ride_response,
                "request_count": self.request_count,
                "latency_ms": round(elapsed * 1000, 2)
            }
        
        # Second call: get fare breakdown
        fare_response = self.get_fare_items(ride_id)
        
        elapsed = time.time() - start_time
        
        if fare_response["status"] == "error":
            return {
                **fare_response,
                "request_count": self.request_count,
                "latency_ms": round(elapsed * 1000, 2)
            }
        
        # Combine results
        result = ride_response["data"].copy()
        result["fare_breakdown"] = fare_response["data"]["fare_breakdown"]
        
        return {
            "status": "success",
            "data": result,
            "request_count": self.request_count,
            "latency_ms": round(elapsed * 1000, 2)
        }
    
    def reset_metrics(self):
        """Reset request counter for testing"""
        self.request_count = 0
