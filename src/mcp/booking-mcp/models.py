"""Data models for booking MCP server."""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import date
from enum import Enum


class BookingType(str, Enum):
    """Type of booking."""
    FLIGHT = "flight"
    HOTEL = "hotel"
    ACTIVITY = "activity"


class BookingStatus(str, Enum):
    """Booking status."""
    AVAILABLE = "available"
    LIMITED = "limited"
    UNAVAILABLE = "unavailable"
    HELD = "held"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class SearchCriteria(BaseModel):
    """Base search criteria."""
    destination: str = Field(..., description="Destination location")
    budget: Optional[float] = Field(None, description="Budget limit", ge=0)


class FlightSearchRequest(SearchCriteria):
    """Flight search request."""
    origin: str = Field(..., description="Origin airport/city")
    depart_date: date = Field(..., description="Departure date")
    return_date: Optional[date] = Field(None, description="Return date (if round trip)")
    passengers: int = Field(1, description="Number of passengers", ge=1)
    cabin_class: str = Field("economy", description="Cabin class preference")


class HotelSearchRequest(SearchCriteria):
    """Hotel search request."""
    check_in: date = Field(..., description="Check-in date")
    check_out: date = Field(..., description="Check-out date")
    guests: int = Field(1, description="Number of guests", ge=1)
    preferences: List[str] = Field(default_factory=list, description="Hotel preferences")


class ActivitySearchRequest(SearchCriteria):
    """Activity search request."""
    dates: List[date] = Field(..., description="Preferred dates")
    interests: List[str] = Field(default_factory=list, description="Activity interests")
    duration_hours: Optional[int] = Field(None, description="Preferred duration in hours")


class BookingOption(BaseModel):
    """Generic booking option."""
    id: str = Field(..., description="Booking option ID")
    title: str = Field(..., description="Option title")
    description: str = Field(..., description="Detailed description")
    price: float = Field(..., description="Price", ge=0)
    currency: str = Field("USD", description="Currency code")
    availability: BookingStatus = Field(..., description="Availability status")
    rating: Optional[float] = Field(None, description="Rating", ge=0, le=5)
    features: List[str] = Field(default_factory=list, description="Features or amenities")
    cancellation_policy: str = Field(..., description="Cancellation policy")
    booking_url: Optional[str] = Field(None, description="Direct booking URL")
    demo_only: bool = Field(True, description="Whether this is demo/mock data")
    provider: str = Field("MockProvider", description="Booking provider")


class FlightOption(BookingOption):
    """Flight booking option."""
    airline: str = Field(..., description="Airline code")
    flight_number: str = Field(..., description="Flight number")
    departure_time: str = Field(..., description="Departure time")
    arrival_time: str = Field(..., description="Arrival time")
    duration: str = Field(..., description="Flight duration")
    stops: int = Field(0, description="Number of stops")
    aircraft_type: Optional[str] = Field(None, description="Aircraft type")


class HotelOption(BookingOption):
    """Hotel booking option."""
    hotel_chain: Optional[str] = Field(None, description="Hotel chain")
    star_rating: Optional[int] = Field(None, description="Star rating", ge=1, le=5)
    address: str = Field(..., description="Hotel address")
    distance_from_center: Optional[str] = Field(None, description="Distance from city center")
    amenities: List[str] = Field(default_factory=list, description="Hotel amenities")
    room_type: str = Field("Standard Room", description="Room type")


class ActivityOption(BookingOption):
    """Activity booking option."""
    activity_type: str = Field(..., description="Type of activity")
    duration: str = Field(..., description="Activity duration")
    meeting_point: str = Field(..., description="Meeting point location")
    includes: List[str] = Field(default_factory=list, description="What's included")
    requirements: List[str] = Field(default_factory=list, description="Requirements or restrictions")
    guide_language: List[str] = Field(default_factory=lambda: ["English"], description="Guide languages")


class BookingSearchResponse(BaseModel):
    """Response with booking options."""
    search_id: str = Field(..., description="Search session ID")
    booking_type: BookingType = Field(..., description="Type of booking")
    options: List[BookingOption] = Field(..., description="Available booking options")
    total_results: int = Field(..., description="Total number of results")
    search_criteria: SearchCriteria = Field(..., description="Original search criteria")
    demo_disclaimer: str = Field("DEMO ONLY - No real bookings", description="Demo disclaimer")


class BookingHoldRequest(BaseModel):
    """Request to hold a booking."""
    booking_type: BookingType = Field(..., description="Type of booking")
    option_id: str = Field(..., description="Booking option ID")
    booking_payload: Dict[str, Any] = Field(default_factory=dict, description="Additional booking details")
    hold_duration_minutes: int = Field(15, description="Hold duration in minutes", ge=5, le=60)
    customer_info: Optional[Dict[str, str]] = Field(None, description="Customer information")


class BookingHoldResponse(BaseModel):
    """Response for booking hold."""
    hold_id: str = Field(..., description="Hold ID")
    booking_type: BookingType = Field(..., description="Type of booking")
    option_id: str = Field(..., description="Original option ID")
    expires_at: str = Field(..., description="Hold expiration time (ISO format)")
    booking_summary: Dict[str, Any] = Field(..., description="Summary of held booking")
    total_price: float = Field(..., description="Total price", ge=0)
    currency: str = Field("USD", description="Currency")
    terms_and_conditions: str = Field(..., description="Terms and conditions")
    cancellation_policy: str = Field(..., description="Cancellation policy")
    demo_disclaimer: str = Field("DEMO ONLY - No real booking held", description="Demo disclaimer")


class BookingConfirmRequest(BaseModel):
    """Request to confirm a held booking."""
    hold_id: str = Field(..., description="Hold ID to confirm")
    payment_method: str = Field("demo_payment", description="Payment method")
    payment_token_or_redirect: Optional[str] = Field(None, description="Payment information")
    customer_agreement: bool = Field(False, description="Customer agreement to terms")


class BookingConfirmResponse(BaseModel):
    """Response for booking confirmation."""
    booking_reference: str = Field(..., description="Booking confirmation number")
    booking_type: BookingType = Field(..., description="Type of booking")
    status: BookingStatus = Field(..., description="Booking status")
    booking_details: Dict[str, Any] = Field(..., description="Confirmed booking details")
    total_charged: float = Field(..., description="Total amount charged", ge=0)
    currency: str = Field("USD", description="Currency")
    confirmation_email: str = Field("demo@example.com", description="Confirmation email address")
    support_contact: str = Field("demo-support@example.com", description="Support contact")
    demo_disclaimer: str = Field("DEMO ONLY - No real booking made", description="Demo disclaimer")