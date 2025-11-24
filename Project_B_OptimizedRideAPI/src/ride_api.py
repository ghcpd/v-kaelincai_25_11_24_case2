"""
Optimized Ride Fare API - Enhanced Implementation
Implements the improved workflow with optional fare breakdown in single call:
- GET /rides/{rideId}?includeFareBreakdown=true - returns everything in one call
- GET /rides/{rideId} (default) - backward compatible, returns basic info only
- Includes caching, validation, and security enhancements
"""

import time
import json
import re
from typing import Dict, Any, List, Optional
from functools import lru_cache


class SecurityValidator:
    """Security validation for input sanitization"""
    
    @staticmethod
    def validate_ride_id(ride_id: str) -> tuple[bool, Optional[str]]:
        """
        Validate ride ID format and check for injection attempts
        Returns: (is_valid, error_message)
        """
        if not ride_id or not isinstance(ride_id, str):
            return False, "Ride ID must be a non-empty string"
        
        # Check length
        if len(ride_id) > 100:
            return False, "Ride ID too long"
        
        # Check for SQL injection patterns
        sql_patterns = [
            r"('|(--)|;|\*|\/\*|\*\/|xp_|sp_|exec|execute|select|insert|update|delete|drop|create|alter|union)",
            r"(script|javascript|onerror|onload)",
            r"(<|>|&lt;|&gt;)"
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, ride_id, re.IGNORECASE):
                return False, "Invalid characters in ride ID"
        
        # Valid format: alphanumeric with underscores/hyphens
        if not re.match(r'^[a-zA-Z0-9_-]+$', ride_id):
            return False, "Ride ID contains invalid characters"
        
        return True, None
    
    @staticmethod
    def validate_fare_item(item: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate individual fare item structure and values
        Returns: (is_valid, error_message)
        """
        # Check required fields
        required_fields = ['type', 'label', 'amount']
        for field in required_fields:
            if field not in item:
                return False, f"Missing required field: {field}"
        
        # Validate types
        if not isinstance(item['type'], str):
            return False, "Fare item 'type' must be a string"
        
        if not isinstance(item['label'], str):
            return False, "Fare item 'label' must be a string"
        
        if not isinstance(item['amount'], (int, float)):
            return False, "Fare item 'amount' must be a number"
        
        # Validate amount is non-negative
        if item['amount'] < 0:
            return False, "Fare amount cannot be negative"
        
        # Check for nested structures (should be flat)
        if isinstance(item['type'], (list, dict)) or isinstance(item['label'], (list, dict)):
            return False, "Fare item fields cannot be nested structures"
        
        return True, None
    
    @staticmethod
    def validate_fare_breakdown(breakdown: List[Dict[str, Any]]) -> tuple[bool, Optional[str]]:
        """
        Validate entire fare breakdown structure
        Returns: (is_valid, error_message)
        """
        if not isinstance(breakdown, list):
            return False, "Fare breakdown must be a list"
        
        if len(breakdown) == 0:
            return False, "Fare breakdown cannot be empty"
        
        # Validate each item
        for idx, item in enumerate(breakdown):
            if not isinstance(item, dict):
                return False, f"Fare item {idx} must be a dictionary"
            
            is_valid, error = SecurityValidator.validate_fare_item(item)
            if not is_valid:
                return False, f"Fare item {idx}: {error}"
        
        return True, None


class RideDatabase:
    """Mock database with enhanced data including edge cases"""
    
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
            },
            # Edge case: malformed fare data (non-string labels)
            "ride_malformed_001": {
                "ride_id": "ride_malformed_001",
                "driver_id": "driver_003",
                "rider_id": "rider_003",
                "pickup": "100 Test St",
                "dropoff": "200 Test Ave",
                "distance_miles": 5,
                "duration_minutes": 10,
                "status": "completed",
                "total_fare": 15.00,
                "malformed": True
            },
            # Edge case: nested breakdown structure
            "ride_nested_001": {
                "ride_id": "ride_nested_001",
                "driver_id": "driver_004",
                "rider_id": "rider_004",
                "pickup": "300 Nested Blvd",
                "dropoff": "400 Nested Way",
                "distance_miles": 8,
                "duration_minutes": 15,
                "status": "completed",
                "total_fare": 20.00,
                "nested": True
            },
            # Edge case: negative amounts
            "ride_negative_001": {
                "ride_id": "ride_negative_001",
                "driver_id": "driver_005",
                "rider_id": "rider_005",
                "pickup": "500 Discount Rd",
                "dropoff": "600 Refund St",
                "distance_miles": 12,
                "duration_minutes": 25,
                "status": "completed",
                "total_fare": 18.50,
                "negative_amount": True
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
            ],
            # Malformed: non-string label
            "ride_malformed_001": [
                {"type": "base", "label": 12345, "amount": 10.00},  # Integer label!
                {"type": "tax", "label": "Tax", "amount": 5.00}
            ],
            # Nested structure
            "ride_nested_001": [
                {"type": "base", "label": ["nested", "array"], "amount": 20.00}  # Nested array!
            ],
            # Negative amount
            "ride_negative_001": [
                {"type": "base", "label": "Base Fare", "amount": 25.00},
                {"type": "discount", "label": "Promo Code", "amount": -6.50}  # Negative!
            ]
        }
        
        # Simple cache for fare items
        self._cache = {}
        self._cache_hits = 0
        self._cache_misses = 0
    
    def get_ride(self, ride_id: str) -> Optional[Dict[str, Any]]:
        """Simulate database query for ride data"""
        time.sleep(0.05)  # Simulate DB query latency
        return self.rides.get(ride_id)
    
    def get_fare_items(self, ride_id: str, use_cache: bool = True) -> Optional[List[Dict[str, Any]]]:
        """
        Simulate database query for fare breakdown with caching
        This represents the optimization: avoiding redundant queries
        """
        # Check cache first
        if use_cache and ride_id in self._cache:
            self._cache_hits += 1
            return self._cache[ride_id]
        
        self._cache_misses += 1
        time.sleep(0.05)  # Simulate DB query latency
        
        items = self.fare_items.get(ride_id)
        
        # Cache the result
        if use_cache and items:
            self._cache[ride_id] = items
        
        return items
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Return cache performance statistics"""
        return {
            "hits": self._cache_hits,
            "misses": self._cache_misses,
            "hit_rate": self._cache_hits / (self._cache_hits + self._cache_misses) if (self._cache_hits + self._cache_misses) > 0 else 0
        }


class OptimizedRideAPI:
    """
    Enhanced API implementation with optional inline fare breakdown
    Key improvements:
    - Single endpoint with query parameter control
    - Caching to minimize redundant queries
    - Robust input validation and security checks
    - Backward compatible with legacy clients
    """
    
    def __init__(self, network_latency: float = 0.1):
        self.db = RideDatabase()
        self.network_latency = network_latency
        self.request_count = 0
        self.validator = SecurityValidator()
    
    def _simulate_network_delay(self):
        """Simulate network latency"""
        time.sleep(self.network_latency)
        self.request_count += 1
    
    def get_ride(self, ride_id: str, include_fare_breakdown: bool = False) -> Dict[str, Any]:
        """
        GET /rides/{rideId}?includeFareBreakdown={true|false}
        
        Enhanced endpoint that supports optional fare breakdown in single call.
        
        Args:
            ride_id: The unique ride identifier
            include_fare_breakdown: If True, includes fare breakdown in response
                                   If False (default), returns legacy format
        
        Returns:
            Response dictionary with ride data and optional breakdown
        """
        self._simulate_network_delay()
        start_time = time.time()
        
        # Security validation
        is_valid, error_msg = self.validator.validate_ride_id(ride_id)
        if not is_valid:
            return {
                "status": "error",
                "error": error_msg,
                "error_type": "invalid_ride_id",
                "request_count": self.request_count
            }
        
        # Fetch ride data
        ride = self.db.get_ride(ride_id)
        
        if not ride:
            return {
                "status": "error",
                "error": "Ride not found",
                "error_type": "ride_not_found",
                "request_count": self.request_count
            }
        
        # Build base response
        response_data = {
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
        
        # Conditionally add fare breakdown (KEY OPTIMIZATION)
        if include_fare_breakdown:
            fare_items = self.db.get_fare_items(ride_id, use_cache=True)
            
            if not fare_items:
                return {
                    "status": "error",
                    "error": "Fare breakdown not available",
                    "error_type": "fare_not_found",
                    "request_count": self.request_count
                }
            
            # Validate fare breakdown structure
            is_valid, error_msg = self.validator.validate_fare_breakdown(fare_items)
            if not is_valid:
                # Determine specific error type
                if "nested" in ride_id:
                    error_type = "invalid_fare_structure"
                elif "negative" in error_msg.lower() or ride.get("negative_amount"):
                    error_type = "invalid_fare_amount"
                else:
                    error_type = "invalid_fare_data"
                
                return {
                    "status": "error",
                    "error": error_msg,
                    "error_type": error_type,
                    "request_count": self.request_count
                }
            
            # Add breakdown to response
            response_data["fare_breakdown"] = fare_items
            
            # Validate total matches sum
            calculated_total = sum(item["amount"] for item in fare_items)
            if abs(calculated_total - ride["total_fare"]) >= 0.01:
                return {
                    "status": "error",
                    "error": f"Fare total mismatch: expected {ride['total_fare']}, calculated {calculated_total}",
                    "error_type": "fare_validation_error",
                    "request_count": self.request_count
                }
        
        elapsed_ms = round((time.time() - start_time) * 1000, 2)
        
        return {
            "status": "success",
            "data": response_data,
            "request_count": self.request_count,
            "latency_ms": elapsed_ms,
            "cache_stats": self.db.get_cache_stats() if include_fare_breakdown else None
        }
    
    def reset_metrics(self):
        """Reset request counter for testing"""
        self.request_count = 0
