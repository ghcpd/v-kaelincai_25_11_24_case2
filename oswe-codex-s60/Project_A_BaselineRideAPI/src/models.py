from dataclasses import dataclass
from typing import Optional


@dataclass
class RideTotal:
    ride_id: str
    total_fare: float
    currency: str = "USD"


@dataclass
class FareItem:
    type: str
    label: str
    amount: float
    currency: str = "USD"


@dataclass
class ApiResponse:
    status: str
    data: Optional[dict]
    error: Optional[str]
    metrics: dict
