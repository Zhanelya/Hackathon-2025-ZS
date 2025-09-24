"""Pydantic models for travel requirements and regulatory information."""

from datetime import date
from enum import Enum
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field


class DocumentType(str, Enum):
    """Required document types."""
    PASSPORT = "passport"
    VISA = "visa"
    ESTA = "esta"
    ETA = "eta"
    TRAVEL_INSURANCE = "travel_insurance"
    VACCINATION_CERTIFICATE = "vaccination_certificate"
    DRIVING_LICENSE = "driving_license"
    INTERNATIONAL_DRIVING_PERMIT = "international_driving_permit"
    BIRTH_CERTIFICATE = "birth_certificate"
    PARENTAL_CONSENT = "parental_consent"


class RestrictionLevel(str, Enum):
    """Level of restriction for items."""
    ALLOWED = "allowed"
    RESTRICTED = "restricted"
    PROHIBITED = "prohibited"
    QUANTITY_LIMITED = "quantity_limited"
    SIZE_LIMITED = "size_limited"


class BagType(str, Enum):
    """Baggage type classifications."""
    CARRY_ON = "carry_on"
    PERSONAL_ITEM = "personal_item"
    CHECKED = "checked"
    CABIN = "cabin"


class SecurityRuleRequest(BaseModel):
    """Request for airport security rules."""
    airport_code: str = Field(..., description="IATA airport code")
    country_code: str = Field(..., description="ISO 2-letter country code")
    airline: Optional[str] = Field(None, description="Airline code")
    cabin_class: Optional[str] = Field(None, description="Cabin class")


class RestrictedItem(BaseModel):
    """Information about a restricted item."""
    item_name: str = Field(..., description="Name of the item")
    restriction_level: RestrictionLevel = Field(..., description="Level of restriction")
    description: str = Field(..., description="Detailed restriction description")
    allowed_quantity: Optional[str] = Field(None, description="Allowed quantity if applicable")
    size_limit: Optional[str] = Field(None, description="Size limit if applicable")
    container_requirements: Optional[str] = Field(None, description="Container requirements")
    location_requirements: Optional[str] = Field(None, description="Where item must be packed")
    alternatives: List[str] = Field(default_factory=list, description="Suggested alternatives")


class SecurityRulesResponse(BaseModel):
    """Response with airport security rules."""
    airport_code: str = Field(..., description="Airport code")
    country_code: str = Field(..., description="Country code")
    restricted_items: List[RestrictedItem] = Field(..., description="List of restricted items")
    liquid_rules: Dict[str, str] = Field(..., description="Liquid carry rules")
    electronics_rules: Dict[str, str] = Field(..., description="Electronics rules")
    general_guidelines: List[str] = Field(..., description="General security guidelines")
    references: List[str] = Field(..., description="Reference sources")
    last_updated: str = Field(..., description="Last update date")


class BaggageAllowanceRequest(BaseModel):
    """Request for baggage allowance information."""
    airline: str = Field(..., description="Airline code")
    cabin_class: str = Field(..., description="Cabin class")
    route: str = Field(..., description="Route (origin-destination)")
    fare_brand: Optional[str] = Field(None, description="Fare brand/type")


class BaggageLimits(BaseModel):
    """Baggage size and weight limits."""
    bag_type: BagType = Field(..., description="Type of bag")
    max_weight_kg: Optional[float] = Field(None, description="Maximum weight in kg")
    max_dimensions_cm: Optional[str] = Field(None, description="Maximum dimensions (LxWxH in cm)")
    max_linear_cm: Optional[int] = Field(None, description="Maximum linear dimensions in cm")
    quantity_allowed: int = Field(..., description="Number of bags allowed")
    additional_fees: Optional[str] = Field(None, description="Additional fees information")


class BaggageAllowanceResponse(BaseModel):
    """Response with baggage allowance information."""
    airline: str = Field(..., description="Airline code")
    cabin_class: str = Field(..., description="Cabin class")
    route: str = Field(..., description="Route")
    carry_on: BaggageLimits = Field(..., description="Carry-on allowance")
    personal_item: BaggageLimits = Field(..., description="Personal item allowance")
    checked: List[BaggageLimits] = Field(..., description="Checked baggage allowances")
    special_items: Dict[str, str] = Field(default_factory=dict, description="Special item policies")
    restrictions: List[str] = Field(default_factory=list, description="General restrictions")
    references: List[str] = Field(..., description="Reference sources")
    last_updated: str = Field(..., description="Last update date")


class VisaRequirementsRequest(BaseModel):
    """Request for visa requirements."""
    nationality: str = Field(..., description="Traveler nationality (ISO 2-letter code)")
    destination_country: str = Field(..., description="Destination country (ISO 2-letter code)")
    transit_countries: List[str] = Field(default_factory=list, description="Transit countries")
    stay_length_days: int = Field(..., description="Length of stay in days", ge=1)
    purpose: str = Field("tourism", description="Purpose of travel")


class VisaRequirement(BaseModel):
    """Visa requirement information."""
    document_type: DocumentType = Field(..., description="Type of required document")
    required: bool = Field(..., description="Whether document is required")
    description: str = Field(..., description="Detailed requirement description")
    validity_required: Optional[str] = Field(None, description="Required validity period")
    processing_time: Optional[str] = Field(None, description="Processing time")
    cost: Optional[str] = Field(None, description="Cost information")
    application_process: Optional[str] = Field(None, description="How to apply")
    exemptions: List[str] = Field(default_factory=list, description="Exemption conditions")


class VisaRequirementsResponse(BaseModel):
    """Response with visa requirements."""
    nationality: str = Field(..., description="Traveler nationality")
    destination_country: str = Field(..., description="Destination country")
    requirements: List[VisaRequirement] = Field(..., description="List of requirements")
    transit_requirements: List[VisaRequirement] = Field(default_factory=list, description="Transit requirements")
    additional_notes: List[str] = Field(default_factory=list, description="Additional notes")
    references: List[str] = Field(..., description="Reference sources")
    last_updated: str = Field(..., description="Last update date")


class DocumentsChecklistRequest(BaseModel):
    """Request for travel documents checklist."""
    destination_country: str = Field(..., description="Destination country (ISO 2-letter code)")
    nationality: str = Field(..., description="Traveler nationality (ISO 2-letter code)")
    minors_traveling: bool = Field(False, description="Whether minors are traveling")
    driving: bool = Field(False, description="Whether planning to drive")
    insurance: bool = Field(True, description="Whether travel insurance is desired")


class DocumentRequirement(BaseModel):
    """Document requirement information."""
    document_type: DocumentType = Field(..., description="Type of document")
    required: bool = Field(..., description="Whether document is required")
    recommended: bool = Field(False, description="Whether document is recommended")
    description: str = Field(..., description="Document description")
    validity_requirements: Optional[str] = Field(None, description="Validity requirements")
    copies_needed: int = Field(1, description="Number of copies needed")
    digital_acceptable: bool = Field(False, description="Whether digital copy is acceptable")
    notes: List[str] = Field(default_factory=list, description="Additional notes")


class DocumentsChecklistResponse(BaseModel):
    """Response with documents checklist."""
    destination_country: str = Field(..., description="Destination country")
    nationality: str = Field(..., description="Traveler nationality")
    required_documents: List[DocumentRequirement] = Field(..., description="Required documents")
    recommended_documents: List[DocumentRequirement] = Field(default_factory=list, description="Recommended documents")
    travel_tips: List[str] = Field(default_factory=list, description="General travel tips")
    emergency_contacts: List[str] = Field(default_factory=list, description="Emergency contact information")
    references: List[str] = Field(..., description="Reference sources")
    last_updated: str = Field(..., description="Last update date")


# Booking-related models

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
    availability: str = Field(..., description="Availability status")
    rating: Optional[float] = Field(None, description="Rating", ge=0, le=5)
    features: List[str] = Field(default_factory=list, description="Features or amenities")
    cancellation_policy: str = Field(..., description="Cancellation policy")
    booking_url: Optional[str] = Field(None, description="Direct booking URL")
    demo_only: bool = Field(True, description="Whether this is demo/mock data")


class BookingSearchResponse(BaseModel):
    """Response with booking options."""
    search_id: str = Field(..., description="Search session ID")
    options: List[BookingOption] = Field(..., description="Available booking options")
    total_results: int = Field(..., description="Total number of results")
    search_criteria: SearchCriteria = Field(..., description="Original search criteria")
    demo_disclaimer: str = Field("DEMO ONLY - No real bookings", description="Demo disclaimer")


class BookingHoldRequest(BaseModel):
    """Request to hold a booking."""
    booking_type: str = Field(..., description="Type of booking (flight/hotel/activity)")
    booking_payload: Dict = Field(..., description="Booking details")
    hold_duration_minutes: int = Field(15, description="Hold duration in minutes", ge=5, le=60)


class BookingHoldResponse(BaseModel):
    """Response for booking hold."""
    hold_id: str = Field(..., description="Hold ID")
    expires_at: str = Field(..., description="Hold expiration time")
    booking_summary: Dict = Field(..., description="Summary of held booking")
    total_price: float = Field(..., description="Total price", ge=0)
    currency: str = Field("USD", description="Currency")
    demo_disclaimer: str = Field("DEMO ONLY - No real booking held", description="Demo disclaimer")


class BookingConfirmRequest(BaseModel):
    """Request to confirm a held booking."""
    hold_id: str = Field(..., description="Hold ID to confirm")
    payment_token_or_redirect: Optional[str] = Field(None, description="Payment information")


class BookingConfirmResponse(BaseModel):
    """Response for booking confirmation."""
    booking_reference: str = Field(..., description="Booking confirmation number")
    status: str = Field(..., description="Booking status")
    booking_details: Dict = Field(..., description="Confirmed booking details")
    total_charged: float = Field(..., description="Total amount charged", ge=0)
    currency: str = Field("USD", description="Currency")
    demo_disclaimer: str = Field("DEMO ONLY - No real booking made", description="Demo disclaimer")