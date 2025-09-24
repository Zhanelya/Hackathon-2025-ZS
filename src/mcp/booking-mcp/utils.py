"""Utility functions for booking MCP server with mock data."""

from typing import Dict, Any, List
from datetime import date, datetime, timedelta
import random
import uuid
from .models import (
    BookingOption, FlightOption, HotelOption, ActivityOption,
    BookingType, BookingStatus
)


def generate_mock_flights(origin: str, destination: str, depart_date: date, passengers: int, budget: float = None) -> List[FlightOption]:
    """Generate mock flight options."""
    airlines = ["AA", "UA", "DL", "BA", "LH", "AF", "KL", "VS"]
    aircraft_types = ["Boeing 737", "Airbus A320", "Boeing 777", "Airbus A350"]
    
    flights = []
    base_price = 300 + random.randint(50, 500)
    
    for i in range(3):
        airline = random.choice(airlines)
        flight_num = f"{airline}{random.randint(100, 999)}"
        
        # Generate times
        dep_hour = random.randint(6, 22)
        dep_minute = random.choice([0, 15, 30, 45])
        duration_hours = random.randint(2, 12)
        
        dep_time = f"{dep_hour:02d}:{dep_minute:02d}"
        arr_time = f"{(dep_hour + duration_hours) % 24:02d}:{dep_minute:02d}"
        
        price = base_price + random.randint(-100, 200)
        if budget and price > budget:
            price = budget - random.randint(50, 100)
        
        flight = FlightOption(
            id=f"flight_{uuid.uuid4().hex[:8]}",
            title=f"{airline} {flight_num} - {origin} to {destination}",
            description=f"Direct flight from {origin} to {destination}",
            price=max(price, 100),
            currency="USD",
            availability=BookingStatus.AVAILABLE,
            rating=random.uniform(3.5, 4.8),
            features=["In-flight WiFi", "Refreshments", "Personal entertainment"],
            cancellation_policy="Free cancellation up to 24 hours before departure",
            demo_only=True,
            provider="MockAirlines",
            airline=airline,
            flight_number=flight_num,
            departure_time=dep_time,
            arrival_time=arr_time,
            duration=f"{duration_hours}h {random.randint(0, 59)}m",
            stops=0 if i == 0 else random.randint(0, 1),
            aircraft_type=random.choice(aircraft_types)
        )
        flights.append(flight)
    
    return flights


def generate_mock_hotels(destination: str, check_in: date, check_out: date, guests: int, budget: float = None) -> List[HotelOption]:
    """Generate mock hotel options."""
    hotel_names = [
        "Grand Plaza Hotel", "Riverside Inn", "City Center Suites", 
        "Garden View Resort", "Business Tower Hotel", "Boutique Hideaway"
    ]
    chains = ["Marriott", "Hilton", "Hyatt", "Independent", "Accor"]
    amenities = [
        "Free WiFi", "Fitness Center", "Pool", "Spa", "Restaurant", 
        "Room Service", "Business Center", "Concierge", "Airport Shuttle"
    ]
    
    hotels = []
    nights = (check_out - check_in).days
    base_price_per_night = 80 + random.randint(20, 200)
    
    for i in range(4):
        hotel_name = random.choice(hotel_names)
        chain = random.choice(chains)
        stars = random.randint(3, 5)
        
        price_per_night = base_price_per_night + random.randint(-30, 100)
        total_price = price_per_night * nights
        
        if budget and total_price > budget:
            total_price = budget - random.randint(20, 50)
            price_per_night = total_price / nights
        
        hotel_amenities = random.sample(amenities, random.randint(3, 6))
        
        hotel = HotelOption(
            id=f"hotel_{uuid.uuid4().hex[:8]}",
            title=f"{hotel_name} - {destination}",
            description=f"{stars}-star hotel in {destination} city center",
            price=max(total_price, 50),
            currency="USD",
            availability=BookingStatus.AVAILABLE,
            rating=random.uniform(3.2, 4.9),
            features=hotel_amenities,
            cancellation_policy="Free cancellation up to 48 hours before check-in",
            demo_only=True,
            provider="MockHotels",
            hotel_chain=chain if chain != "Independent" else None,
            star_rating=stars,
            address=f"{random.randint(100, 999)} Main Street, {destination}",
            distance_from_center=f"{random.uniform(0.1, 2.5):.1f} km",
            amenities=hotel_amenities,
            room_type=random.choice(["Standard Room", "Deluxe Room", "Suite", "Executive Room"])
        )
        hotels.append(hotel)
    
    return hotels


def generate_mock_activities(destination: str, dates: List[date], interests: List[str], budget: float = None) -> List[ActivityOption]:
    """Generate mock activity options.""" 
    activity_types = {
        "cultural": ["Museum Tour", "Historical Walking Tour", "Art Gallery Visit"],
        "outdoor": ["City Bike Tour", "Hiking Excursion", "Boat Cruise"],
        "food": ["Food Tour", "Cooking Class", "Wine Tasting"],
        "adventure": ["Zipline Adventure", "Rock Climbing", "Kayaking"],
        "sightseeing": ["City Sightseeing Tour", "Architecture Tour", "Photography Walk"]
    }
    
    activities = []
    
    # Determine activity types based on interests
    relevant_types = []
    for interest in interests:
        for category, activities_list in activity_types.items():
            if interest.lower() in category or category in interest.lower():
                relevant_types.extend(activities_list)
    
    if not relevant_types:
        relevant_types = [act for acts in activity_types.values() for act in acts]
    
    for i in range(3):
        activity_name = random.choice(relevant_types)
        duration_hours = random.randint(2, 8)
        base_price = 30 + random.randint(20, 150)
        
        if budget and base_price > budget:
            base_price = budget - random.randint(10, 20)
        
        includes = random.sample([
            "Professional guide", "Entrance fees", "Transportation", 
            "Refreshments", "Small group size", "Hotel pickup"
        ], random.randint(2, 4))
        
        activity = ActivityOption(
            id=f"activity_{uuid.uuid4().hex[:8]}",
            title=f"{activity_name} in {destination}",
            description=f"Experience {activity_name.lower()} with local experts",
            price=max(base_price, 20),
            currency="USD",
            availability=BookingStatus.AVAILABLE,
            rating=random.uniform(4.0, 4.9),
            features=includes,
            cancellation_policy="Free cancellation up to 24 hours in advance",
            demo_only=True,
            provider="MockTours",
            activity_type=activity_name.split()[0].lower(),
            duration=f"{duration_hours} hours",
            meeting_point=f"Tourist Information Center, {destination}",
            includes=includes,
            requirements=["Comfortable walking shoes", "Weather-appropriate clothing"],
            guide_language=["English", "Spanish"] if random.random() > 0.5 else ["English"]
        )
        activities.append(activity)
    
    return activities


def create_hold_response(hold_request: Dict[str, Any], booking_option: BookingOption) -> Dict[str, Any]:
    """Create a booking hold response."""
    hold_id = f"hold_{uuid.uuid4().hex[:12]}"
    expires_at = datetime.now() + timedelta(minutes=hold_request.get("hold_duration_minutes", 15))
    
    return {
        "hold_id": hold_id,
        "booking_type": hold_request["booking_type"],
        "option_id": hold_request["option_id"],
        "expires_at": expires_at.isoformat(),
        "booking_summary": {
            "title": booking_option.title,
            "price": booking_option.price,
            "currency": booking_option.currency,
            "provider": booking_option.provider,
            "features": booking_option.features
        },
        "total_price": booking_option.price,
        "currency": booking_option.currency,
        "terms_and_conditions": "Standard booking terms apply. This is a demo booking.",
        "cancellation_policy": booking_option.cancellation_policy,
        "demo_disclaimer": "DEMO ONLY - No real booking held"
    }


def create_confirmation_response(confirm_request: Dict[str, Any], hold_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a booking confirmation response."""
    booking_ref = f"DEMO{random.randint(100000, 999999)}"
    
    return {
        "booking_reference": booking_ref,
        "booking_type": hold_data["booking_type"],
        "status": "confirmed",
        "booking_details": hold_data["booking_summary"],
        "total_charged": hold_data["total_price"],
        "currency": hold_data["currency"],
        "confirmation_email": "demo@example.com",
        "support_contact": "demo-support@example.com",
        "demo_disclaimer": "DEMO ONLY - No real booking made"
    }


# In-memory storage for demo holds (in production this would be a database)
_demo_holds: Dict[str, Dict[str, Any]] = {}


def store_demo_hold(hold_id: str, hold_data: Dict[str, Any]) -> None:
    """Store demo hold data."""
    _demo_holds[hold_id] = hold_data


def get_demo_hold(hold_id: str) -> Dict[str, Any] | None:
    """Get demo hold data."""
    return _demo_holds.get(hold_id)


def remove_demo_hold(hold_id: str) -> None:
    """Remove demo hold data."""
    _demo_holds.pop(hold_id, None)