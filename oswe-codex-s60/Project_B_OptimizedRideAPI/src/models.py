import html
import re
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field, validator, root_validator

ALLOWED_FARE_TYPES = {
    "base",
    "distance",
    "time",
    "surge",
    "fees",
    "toll",
    "tax",
    "discount",
}


def sanitize_label(label: str, max_len: int = 100) -> str:
    # Remove control chars
    cleaned = re.sub(r"[\x00-\x1f\x7f]", "", label)
    # Strip HTML tags
    cleaned = re.sub(r"<[^>]+>", "", cleaned)
    # Remove angle brackets remnants
    cleaned = cleaned.replace("<", "").replace(">", "")
    # Collapse whitespace
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    # Escape any remaining HTML entities
    cleaned = html.escape(cleaned, quote=False)
    if len(cleaned) > max_len:
        cleaned = cleaned[:max_len]
    return cleaned


class FareItem(BaseModel):
    type: str = Field(..., min_length=1)
    label: str = Field(..., min_length=1)
    amount: Decimal
    currency: str = Field("USD", min_length=1)

    @validator("amount")
    def amount_non_negative(cls, v: Decimal) -> Decimal:
        if v < 0:
            raise ValueError("amount must be non-negative")
        return v

    @validator("type")
    def type_allowed(cls, v: str) -> str:
        if v not in ALLOWED_FARE_TYPES:
            raise ValueError(f"unsupported fare item type '{v}'")
        return v

    @validator("label")
    def label_sanitized(cls, v: str) -> str:
        return sanitize_label(v)

    class Config:
        extra = "forbid"


class RideDetails(BaseModel):
    rideId: str = Field(..., min_length=1)
    totalFare: Decimal
    currency: str = Field("USD", min_length=1)
    fareBreakdown: Optional[List[FareItem]] = None

    @validator("totalFare")
    def total_non_negative(cls, v: Decimal) -> Decimal:
        if v < 0:
            raise ValueError("totalFare must be non-negative")
        return v

    class Config:
        extra = "forbid"


class ApiResponse(BaseModel):
    status: str
    data: Optional[RideDetails] = None
    error: Optional[str] = None
    metrics: dict

    class Config:
        extra = "forbid"
