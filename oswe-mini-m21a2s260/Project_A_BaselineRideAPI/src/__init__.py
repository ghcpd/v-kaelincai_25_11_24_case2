"""Baseline Ride API package
Legacy behavior: two calls required to retrieve fare details: /rides/{rideId} and /rides/{rideId}/fare-items
"""

from .app import get_ride, get_fare_items
