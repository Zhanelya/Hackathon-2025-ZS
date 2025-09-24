"""Pydantic models for packing list generation and management."""

from datetime import date, datetime
from enum import Enum
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field, validator


class TransportMode(str, Enum):
    """Transportation mode options."""
    FLIGHT = "flight"
    TRAIN = "train"
    CAR = "car"
    BUS = "bus"
    FERRY = "ferry"


class CabinClass(str, Enum):
    """Flight cabin class options."""
    ECONOMY = "economy"
    PREMIUM_ECONOMY = "premium_economy"
    BUSINESS = "business"
    FIRST = "first"


class ActivityType(str, Enum):
    """Activity type options."""
    HIKING = "hiking"
    MUSEUM = "museum"
    BEACH = "beach"
    BUSINESS_DINNER = "business_dinner"
    PHOTOGRAPHY = "photography"
    NIGHTLIFE = "nightlife"
    SHOPPING = "shopping"
    SPORTS = "sports"
    CULTURAL = "cultural"
    OUTDOOR = "outdoor"


class TimeOfDay(str, Enum):
    """Time of day usage options."""
    DAY = "day"
    NIGHT = "night"
    BOTH = "both"


class SafetyStatus(str, Enum):
    """Item safety status for travel."""
    SAFE = "safe"
    RESTRICTED = "restricted"
    PROHIBITED = "prohibited"


class Priority(str, Enum):
    """Item priority level."""
    MUST_HAVE = "must_have"
    NICE_TO_HAVE = "nice_to_have"
    LUXURY = "luxury"


class WeightClass(str, Enum):
    """Item weight classification."""
    LIGHT = "light"
    MEDIUM = "medium"
    HEAVY = "heavy"


class ItemCategory(str, Enum):
    """Item category classification."""
    CLOTHING = "clothing"
    TOILETRIES = "toiletries"
    ELECTRONICS = "electronics"
    DOCUMENTS = "documents"
    HEALTH = "health"
    ACCESSORIES = "accessories"
    EQUIPMENT = "equipment"


class TripDates(BaseModel):
    """Trip date information."""
    start: date = Field(..., description="Trip start date")
    end: date = Field(..., description="Trip end date")
    
    @validator('end')
    def end_after_start(cls, v, values):
        if 'start' in values and v <= values['start']:
            raise ValueError('End date must be after start date')
        return v
    
    @property
    def duration_days(self) -> int:
        """Calculate trip duration in days."""
        return (self.end - self.start).days + 1


class Transport(BaseModel):
    """Transportation information."""
    mode: TransportMode = Field(..., description="Transportation mode")
    airline: Optional[str] = Field(None, description="Airline code (for flights)")
    cabin_class: Optional[CabinClass] = Field(None, description="Cabin class (for flights)")
    route: Optional[str] = Field(None, description="Route information")


class Accommodation(BaseModel):
    """Accommodation information."""
    has_laundry: bool = Field(True, description="Whether laundry facilities are available")
    has_gym: bool = Field(False, description="Whether gym facilities are available")
    has_pool: bool = Field(False, description="Whether pool facilities are available")


class Constraints(BaseModel):
    """User constraints and limitations."""
    capacity_liters: Optional[int] = Field(None, description="Backpack capacity in liters", ge=1)
    max_weight_kg: Optional[float] = Field(None, description="Maximum comfortable carry weight in kg", ge=0.1)
    liquid_limit_ml: Optional[int] = Field(100, description="Liquid container size limit in ml", ge=0)
    budget_total: Optional[float] = Field(None, description="Total trip budget", ge=0)
    budget_luggage: Optional[float] = Field(None, description="Budget for luggage/baggage fees", ge=0)
    mobility_limitations: List[str] = Field(default_factory=list, description="Mobility or health limitations")


class TravelerProfile(BaseModel):
    """Traveler profile information."""
    nationality: str = Field(..., description="Traveler nationality (ISO 2-letter code)")
    age: Optional[int] = Field(None, description="Traveler age", ge=0, le=120)
    gender: Optional[str] = Field(None, description="Gender preference for clothing")
    size_clothing: Optional[str] = Field(None, description="Clothing size")
    size_shoes: Optional[str] = Field(None, description="Shoe size")


class Preferences(BaseModel):
    """User preferences and style."""
    style: str = Field("casual", description="Clothing style preference")
    tech_focused: bool = Field(False, description="Whether user needs tech items")
    photography: bool = Field(False, description="Whether user does photography")
    sustainable: bool = Field(False, description="Preference for sustainable/eco items")
    minimalist: bool = Field(False, description="Preference for minimal packing")


class PackingListRequest(BaseModel):
    """Request model for packing list generation."""
    destination: str = Field(..., description="Destination location")
    dates: TripDates = Field(..., description="Trip dates")
    activities: List[ActivityType] = Field(default_factory=list, description="Planned activities")
    time_of_day_usage: List[TimeOfDay] = Field(default_factory=lambda: [TimeOfDay.DAY], description="Time of day usage")
    transport: Transport = Field(..., description="Transportation information")
    accommodation: Accommodation = Field(default_factory=Accommodation, description="Accommodation details")
    constraints: Constraints = Field(default_factory=Constraints, description="User constraints")
    preferences: Preferences = Field(default_factory=Preferences, description="User preferences")
    traveler_profile: TravelerProfile = Field(..., description="Traveler profile")
    keep_it_simple: bool = Field(False, description="Whether to use keep-it-simple mode")


class PackingListItem(BaseModel):
    """Individual packing list item."""
    category: ItemCategory = Field(..., description="Item category")
    name: str = Field(..., description="Item name")
    qty: int = Field(..., description="Quantity needed", ge=1)
    estimated_volume_l: float = Field(..., description="Estimated volume in liters", ge=0)
    estimated_weight_kg: float = Field(..., description="Estimated weight in kg", ge=0)
    weight_class: WeightClass = Field(..., description="Weight classification")
    priority: Priority = Field(..., description="Priority level")
    safety_status: SafetyStatus = Field(..., description="Safety status for travel")
    flags: List[str] = Field(default_factory=list, description="Special flags or warnings")
    reason: str = Field(..., description="Reason for inclusion/quantity")
    restricted: bool = Field(False, description="Whether item has restrictions")
    alternatives: List[str] = Field(default_factory=list, description="Alternative items")
    estimated_cost: Optional[float] = Field(None, description="Estimated cost if buying", ge=0)


class CategorySummary(BaseModel):
    """Summary statistics for a category."""
    category: ItemCategory = Field(..., description="Category name")
    item_count: int = Field(..., description="Number of items", ge=0)
    total_weight_kg: float = Field(..., description="Total weight in kg", ge=0)
    total_volume_l: float = Field(..., description="Total volume in liters", ge=0)
    must_have_count: int = Field(..., description="Number of must-have items", ge=0)
    restricted_count: int = Field(..., description="Number of restricted items", ge=0)


class CapacityFitResult(BaseModel):
    """Result of capacity/weight fitting."""
    fits_capacity: bool = Field(..., description="Whether items fit within capacity limits")
    fits_weight: bool = Field(..., description="Whether items fit within weight limits")
    total_weight_kg: float = Field(..., description="Total weight of all items", ge=0)
    total_volume_l: float = Field(..., description="Total volume of all items", ge=0)
    removed_items: List[PackingListItem] = Field(default_factory=list, description="Items removed to fit constraints")
    alternatives_suggested: List[str] = Field(default_factory=list, description="Suggested alternatives")
    recommendations: List[str] = Field(default_factory=list, description="Fitting recommendations")


class PackingListResponse(BaseModel):
    """Response model for packing list generation."""
    items: List[PackingListItem] = Field(..., description="Packing list items")
    category_summaries: List[CategorySummary] = Field(..., description="Per-category summaries")
    capacity_fit: CapacityFitResult = Field(..., description="Capacity fitting results")
    constraints_applied: List[str] = Field(default_factory=list, description="Constraints that influenced the list")
    weather_influence: List[str] = Field(default_factory=list, description="Weather-driven decisions")
    regulatory_flags: List[str] = Field(default_factory=list, description="Regulatory warnings/flags")
    total_estimated_cost: Optional[float] = Field(None, description="Total estimated cost", ge=0)
    generated_at: datetime = Field(default_factory=datetime.now, description="Generation timestamp")
    simple_checklist: Optional[str] = Field(None, description="Simple text checklist (if requested)")


class SimpleChecklistRequest(BaseModel):
    """Request for simple checklist generation."""
    packing_request: PackingListRequest = Field(..., description="Original packing request")
    max_lines: int = Field(30, description="Maximum lines in checklist", ge=5, le=100)
    include_quantities: bool = Field(True, description="Whether to include quantities")
    priority_filter: Optional[Priority] = Field(None, description="Filter by priority level")