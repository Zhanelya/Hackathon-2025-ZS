"""Travel requirements service with mocked data for Phase 1."""

from typing import Dict, Any, Optional
import logging
from .config import config
from .utils import (
    format_security_response,
    format_baggage_response,
    format_visa_response,
    format_documents_response
)

logger = logging.getLogger(__name__)


class TravelRequirementsService:
    """Service for getting travel requirements and regulatory information."""
    
    def __init__(self):
        """Initialize the service."""
        if not config.OFFLINE_MODE:
            raise RuntimeError("Phase 1: Only offline mode is supported")
        logger.info("TravelRequirementsService initialized in offline/mock mode")
    
    async def get_airport_security_rules(
        self, 
        airport_code: str, 
        country_code: str, 
        airline: Optional[str] = None, 
        cabin_class: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get airport security rules and restrictions.
        
        Args:
            airport_code: IATA airport code
            country_code: ISO 2-letter country code
            airline: Optional airline code
            cabin_class: Optional cabin class
            
        Returns:
            Security rules and restrictions
        """
        logger.info(f"Getting security rules for {airport_code}, {country_code} (MOCK)")
        
        if config.OFFLINE_MODE:
            return format_security_response(airport_code, country_code, airline)
        else:
            # Future: Real API call would go here
            raise NotImplementedError("Live API not implemented in Phase 1")
    
    async def check_baggage_allowance(
        self,
        airline: str,
        cabin_class: str,
        route: str,
        fare_brand: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Check airline baggage allowance limits.
        
        Args:
            airline: Airline code
            cabin_class: Cabin class
            route: Route (origin-destination)
            fare_brand: Optional fare brand/type
            
        Returns:
            Baggage allowance information
        """
        logger.info(f"Checking baggage allowance for {airline} {cabin_class} on {route} (MOCK)")
        
        if config.OFFLINE_MODE:
            return format_baggage_response(airline, cabin_class, route)
        else:
            # Future: Real API call would go here
            raise NotImplementedError("Live API not implemented in Phase 1")
    
    async def get_visa_requirements(
        self,
        nationality: str,
        destination_country: str,
        transit_countries: Optional[list] = None,
        stay_length_days: int = 7,
        purpose: str = "tourism"
    ) -> Dict[str, Any]:
        """
        Get visa and entry requirements.
        
        Args:
            nationality: Traveler nationality (ISO 2-letter code)
            destination_country: Destination country (ISO 2-letter code)
            transit_countries: Optional list of transit countries
            stay_length_days: Length of stay in days
            purpose: Purpose of travel
            
        Returns:
            Visa requirements information
        """
        logger.info(f"Getting visa requirements for {nationality} -> {destination_country} (MOCK)")
        
        if config.OFFLINE_MODE:
            return format_visa_response(nationality, destination_country, stay_length_days, purpose)
        else:
            # Future: Real API call would go here
            raise NotImplementedError("Live API not implemented in Phase 1")
    
    async def get_documents_checklist(
        self,
        destination_country: str,
        nationality: str,
        minors_traveling: bool = False,
        driving: bool = False,
        insurance: bool = True
    ) -> Dict[str, Any]:
        """
        Get required travel documents checklist.
        
        Args:
            destination_country: Destination country (ISO 2-letter code)
            nationality: Traveler nationality (ISO 2-letter code)
            minors_traveling: Whether minors are traveling
            driving: Whether planning to drive
            insurance: Whether travel insurance is desired
            
        Returns:
            Documents checklist
        """
        logger.info(f"Getting documents checklist for {nationality} -> {destination_country} (MOCK)")
        
        if config.OFFLINE_MODE:
            return format_documents_response(destination_country, nationality, minors_traveling, driving)
        else:
            # Future: Real API call would go here
            raise NotImplementedError("Live API not implemented in Phase 1")