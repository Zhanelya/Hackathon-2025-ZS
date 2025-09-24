"""Utility functions for travel requirements MCP server."""

from typing import Dict, List, Any
import json


def load_mock_data(filename: str) -> Dict[str, Any]:
    """Load mock data from JSON file."""
    # In Phase 1, we use hardcoded fixtures instead of reading files
    # This ensures deterministic behavior and no file system dependencies
    
    mock_data = {
        "security_rules.json": {
            "default": {
                "restricted_items": [
                    {
                        "item_name": "Liquids over 100ml",
                        "restriction_level": "prohibited",
                        "description": "Liquids, gels, and aerosols must be 100ml or less in carry-on",
                        "container_requirements": "Transparent plastic bag, max 1L capacity",
                        "location_requirements": "carry_on",
                        "alternatives": ["Travel-size containers", "Solid alternatives"]
                    },
                    {
                        "item_name": "Sharp objects",
                        "restriction_level": "prohibited", 
                        "description": "Knives, scissors over 6cm, and other sharp objects",
                        "location_requirements": "checked_only",
                        "alternatives": ["Travel scissors (<6cm)", "Plastic utensils"]
                    },
                    {
                        "item_name": "Batteries (lithium)",
                        "restriction_level": "restricted",
                        "description": "Lithium batteries over 100Wh require approval",
                        "allowed_quantity": "Spare batteries carry-on only",
                        "location_requirements": "carry_on",
                        "alternatives": ["Power banks <27,000mAh"]
                    }
                ],
                "liquid_rules": {
                    "container_size": "100ml maximum",
                    "bag_requirement": "Clear plastic bag, 1L capacity",
                    "bag_quantity": "One bag per passenger"
                },
                "electronics_rules": {
                    "large_electronics": "Must be removed for screening",
                    "batteries": "Spare lithium batteries carry-on only",
                    "medical_devices": "Notify security, carry documentation"
                },
                "references": ["TSA.gov", "IATA Dangerous Goods Regulations"]
            }
        },
        
        "baggage_allowance.json": {
            "default": {
                "carry_on": {
                    "max_weight_kg": 7,
                    "max_dimensions_cm": "55x40x20",
                    "max_linear_cm": 115,
                    "quantity_allowed": 1
                },
                "personal_item": {
                    "max_weight_kg": 2,
                    "max_dimensions_cm": "40x30x15",
                    "max_linear_cm": 85,
                    "quantity_allowed": 1
                },
                "checked": [
                    {
                        "max_weight_kg": 23,
                        "max_dimensions_cm": "158 linear cm",
                        "quantity_allowed": 1,
                        "additional_fees": "Included in ticket"
                    }
                ],
                "references": ["Airline official website", "IATA baggage guidelines"]
            }
        },
        
        "visa_requirements.json": {
            "default": {
                "requirements": [
                    {
                        "document_type": "passport",
                        "required": True,
                        "description": "Valid passport required for international travel",
                        "validity_required": "6 months beyond stay",
                        "processing_time": "Immediate (if valid)"
                    },
                    {
                        "document_type": "visa",
                        "required": False,
                        "description": "Visa requirements vary by nationality and destination",
                        "processing_time": "Varies (1-30 days)",
                        "exemptions": ["Tourist stays under 90 days (some countries)"]
                    }
                ],
                "references": ["Embassy websites", "VisaHQ", "Government travel advisories"]
            }
        },
        
        "documents_checklist.json": {
            "default": {
                "required_documents": [
                    {
                        "document_type": "passport",
                        "required": True,
                        "description": "Valid passport for international travel",
                        "validity_requirements": "Must be valid for 6+ months",
                        "copies_needed": 2,
                        "digital_acceptable": False
                    }
                ],
                "recommended_documents": [
                    {
                        "document_type": "travel_insurance",
                        "required": False,
                        "recommended": True,
                        "description": "Comprehensive travel insurance coverage",
                        "digital_acceptable": True,
                        "notes": ["Medical coverage", "Trip cancellation", "Lost luggage"]
                    }
                ],
                "references": ["State Department", "Embassy websites"]
            }
        }
    }
    
    return mock_data.get(filename, {})


def format_security_response(airport_code: str, country_code: str, airline: str = None) -> Dict[str, Any]:
    """Format security rules response with mock data."""
    mock_data = load_mock_data("security_rules.json")
    base_data = mock_data.get("default", {})
    
    return {
        "airport_code": airport_code.upper(),
        "country_code": country_code.upper(),
        "restricted_items": base_data.get("restricted_items", []),
        "liquid_rules": base_data.get("liquid_rules", {}),
        "electronics_rules": base_data.get("electronics_rules", {}),
        "general_guidelines": [
            "Arrive 2+ hours early for international flights",
            "Have ID and boarding pass ready",
            "Follow liquid restrictions for carry-on",
            "Remove large electronics during screening"
        ],
        "references": base_data.get("references", []),
        "last_updated": "2025-01-01",
        "mock_data": True
    }


def format_baggage_response(airline: str, cabin_class: str, route: str) -> Dict[str, Any]:
    """Format baggage allowance response with mock data."""
    mock_data = load_mock_data("baggage_allowance.json")
    base_data = mock_data.get("default", {})
    
    # Adjust limits based on cabin class
    carry_on_limits = base_data.get("carry_on", {}).copy()
    if cabin_class.lower() in ["business", "first"]:
        carry_on_limits["max_weight_kg"] = 10
        carry_on_limits["quantity_allowed"] = 2
    
    return {
        "airline": airline.upper(),
        "cabin_class": cabin_class.lower(),
        "route": route,
        "carry_on": {
            "bag_type": "carry_on",
            **carry_on_limits
        },
        "personal_item": {
            "bag_type": "personal_item",
            **base_data.get("personal_item", {})
        },
        "checked": [
            {
                "bag_type": "checked",
                **checked_item
            } for checked_item in base_data.get("checked", [])
        ],
        "special_items": {
            "musical_instruments": "Contact airline for oversized items",
            "sports_equipment": "Additional fees may apply",
            "medical_equipment": "Notify airline in advance"
        },
        "restrictions": [
            "Hazardous materials prohibited",
            "Batteries in checked luggage restrictions apply",
            "Liquids over 100ml in checked only"
        ],
        "references": base_data.get("references", []),
        "last_updated": "2025-01-01",
        "mock_data": True
    }


def format_visa_response(nationality: str, destination: str, stay_days: int, purpose: str) -> Dict[str, Any]:
    """Format visa requirements response with mock data."""
    mock_data = load_mock_data("visa_requirements.json")
    base_data = mock_data.get("default", {})
    
    # Simulate different visa requirements based on nationality/destination
    visa_required = not (nationality.upper() in ["US", "CA", "GB", "DE", "FR"] and 
                        destination.upper() in ["US", "CA", "GB", "DE", "FR"] and 
                        stay_days <= 90)
    
    requirements = base_data.get("requirements", []).copy()
    if visa_required:
        for req in requirements:
            if req.get("document_type") == "visa":
                req["required"] = True
                req["description"] = f"Visa required for {nationality} nationals visiting {destination}"
    
    return {
        "nationality": nationality.upper(),
        "destination_country": destination.upper(),
        "requirements": requirements,
        "transit_requirements": [],
        "additional_notes": [
            f"Requirements for {purpose} travel",
            f"Stay duration: {stay_days} days",
            "Check embassy website for latest updates"
        ],
        "references": base_data.get("references", []),
        "last_updated": "2025-01-01",
        "mock_data": True
    }


def format_documents_response(destination: str, nationality: str, minors: bool, driving: bool) -> Dict[str, Any]:
    """Format documents checklist response with mock data."""
    mock_data = load_mock_data("documents_checklist.json")
    base_data = mock_data.get("default", {})
    
    required_docs = base_data.get("required_documents", []).copy()
    recommended_docs = base_data.get("recommended_documents", []).copy()
    
    # Add driving documents if needed
    if driving:
        recommended_docs.append({
            "document_type": "international_driving_permit",
            "required": False,
            "recommended": True,
            "description": "International Driving Permit for car rental",
            "validity_requirements": "Valid for 1 year",
            "digital_acceptable": False,
            "notes": ["Required by most car rental companies", "Apply before travel"]
        })
    
    # Add minor-specific documents
    if minors:
        required_docs.append({
            "document_type": "birth_certificate",
            "required": True,
            "description": "Birth certificate for minors under 18",
            "copies_needed": 2,
            "digital_acceptable": False,
            "notes": ["Required for unaccompanied minors", "Notarized copy recommended"]
        })
    
    return {
        "destination_country": destination.upper(),
        "nationality": nationality.upper(),
        "required_documents": required_docs,
        "recommended_documents": recommended_docs,
        "travel_tips": [
            "Make copies of all important documents",
            "Store copies separately from originals",
            "Consider digital copies in cloud storage",
            "Check document expiration dates before travel"
        ],
        "emergency_contacts": [
            "Embassy/Consulate contact information",
            "Travel insurance emergency line",
            "Credit card company international number"
        ],
        "references": base_data.get("references", []),
        "last_updated": "2025-01-01",
        "mock_data": True
    }