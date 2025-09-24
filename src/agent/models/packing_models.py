from __future__ import annotations

from typing import List, Literal, Optional, Dict

from pydantic import BaseModel, Field


class Dates(BaseModel):
    start: str
    end: str


class Transport(BaseModel):
    mode: Optional[str] = None
    airline: Optional[str] = None
    cabinClass: Optional[str] = None


class Accommodation(BaseModel):
    hasLaundry: Optional[bool] = False


class Constraints(BaseModel):
    capacityLiters: Optional[float] = None
    maxWeightKg: Optional[float] = None
    liquidLimitMl: Optional[int] = 100


class Preferences(BaseModel):
    style: Optional[str] = None
    tech: Optional[bool] = None
    photography: Optional[bool] = None


class TravelerProfile(BaseModel):
    nationality: Optional[str] = None
    age: Optional[int] = None


class GeneratePackingListRequest(BaseModel):
    destination: str
    dates: Dates
    tripLengthDays: int
    activities: List[str] = Field(default_factory=list)
    timeOfDayUsage: List[Literal["day", "night"]] = Field(default_factory=list)
    # Iteration 2: offline weather influence via explicit hints
    weatherHints: List[Literal["cold", "rain", "heat"]] = Field(default_factory=list)
    transport: Optional[Transport] = None
    accommodation: Optional[Accommodation] = None
    constraints: Optional[Constraints] = None
    preferences: Optional[Preferences] = None
    travelerProfile: Optional[TravelerProfile] = None


class PackingListItem(BaseModel):
    category: Literal[
        "clothing",
        "toiletries",
        "electronics",
        "documents",
        "health",
        "accessories",
    ]
    name: str
    qty: int
    estimatedVolumeL: float
    estimatedWeightKg: float
    weightClass: Literal["light", "medium", "heavy"]
    priority: Literal["must_have", "nice_to_have"]
    safetyStatus: Literal["safe", "restricted", "prohibited"]
    flags: List[str] = Field(default_factory=list)
    reason: str
    restricted: bool = False
    alternatives: List[str] = Field(default_factory=list)


class PackingListResponse(BaseModel):
    items: List[PackingListItem]
    totals: Dict[str, float]
    notes: List[str] = Field(default_factory=list)
