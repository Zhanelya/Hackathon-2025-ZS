"""Data models for travel requirements MCP server."""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum


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


class BaggageLimits(BaseModel):
    """Baggage size and weight limits."""
    bag_type: BagType = Field(..., description="Type of bag")
    max_weight_kg: Optional[float] = Field(None, description="Maximum weight in kg")
    max_dimensions_cm: Optional[str] = Field(None, description="Maximum dimensions (LxWxH in cm)")
    max_linear_cm: Optional[int] = Field(None, description="Maximum linear dimensions in cm")
    quantity_allowed: int = Field(..., description="Number of bags allowed")
    additional_fees: Optional[str] = Field(None, description="Additional fees information")


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