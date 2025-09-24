"""Unit tests for packing models."""

import pytest
from datetime import date, datetime
from src.agent.models.packing_models import (
    PackingListRequest,
    PackingListItem,
    TripDates,
    Transport,
    Constraints,
    TravelerProfile,
    Preferences,
    Accommodation,
    ActivityType,
    TimeOfDay,
    TransportMode,
    CabinClass,
    ItemCategory,
    SafetyStatus,
    Priority,
    WeightClass,
)


def test_trip_dates_validation():
    """Test trip dates validation."""
    # Valid dates
    dates = TripDates(start=date(2025, 1, 10), end=date(2025, 1, 15))
    assert dates.duration_days == 6
    
    # Invalid dates (end before start)
    with pytest.raises(ValueError, match="End date must be after start date"):
        TripDates(start=date(2025, 1, 15), end=date(2025, 1, 10))


def test_packing_list_item_creation():
    """Test creating a packing list item."""
    item = PackingListItem(
        category=ItemCategory.CLOTHING,
        name="Merino T-shirt",
        qty=3,
        estimated_volume_l=0.9,
        estimated_weight_kg=0.45,
        weight_class=WeightClass.LIGHT,
        priority=Priority.MUST_HAVE,
        safety_status=SafetyStatus.SAFE,
        reason="6 days with laundry once",
        alternatives=["synthetic tee"]
    )
    
    assert item.category == ItemCategory.CLOTHING
    assert item.name == "Merino T-shirt"
    assert item.qty == 3
    assert item.restricted is False
    assert len(item.alternatives) == 1


def test_constraints_validation():
    """Test constraints validation."""
    # Valid constraints
    constraints = Constraints(
        capacity_liters=28,
        max_weight_kg=8.5,
        liquid_limit_ml=100
    )
    assert constraints.capacity_liters == 28
    assert constraints.max_weight_kg == 8.5
    
    # Invalid constraints (negative values should fail)
    with pytest.raises(ValueError):
        Constraints(capacity_liters=-5)
    
    with pytest.raises(ValueError):
        Constraints(max_weight_kg=-2.0)


def test_packing_list_request_creation():
    """Test creating a complete packing list request."""
    request = PackingListRequest(
        destination="Tokyo, Japan",
        dates=TripDates(start=date(2025, 11, 1), end=date(2025, 11, 7)),
        activities=[ActivityType.MUSEUM, ActivityType.NIGHTLIFE],
        time_of_day_usage=[TimeOfDay.DAY, TimeOfDay.NIGHT],
        transport=Transport(
            mode=TransportMode.FLIGHT,
            airline="ANA",
            cabin_class=CabinClass.ECONOMY
        ),
        accommodation=Accommodation(has_laundry=True),
        constraints=Constraints(
            capacity_liters=28,
            max_weight_kg=8.0,
            liquid_limit_ml=100
        ),
        preferences=Preferences(
            style="smart_casual",
            tech_focused=True
        ),
        traveler_profile=TravelerProfile(
            nationality="US",
            age=35
        )
    )
    
    assert request.destination == "Tokyo, Japan"
    assert request.dates.duration_days == 7
    assert ActivityType.MUSEUM in request.activities
    assert request.transport.airline == "ANA"
    assert request.constraints.capacity_liters == 28
    assert request.preferences.tech_focused is True


def test_enums():
    """Test enum values."""
    assert ActivityType.HIKING == "hiking"
    assert TimeOfDay.NIGHT == "night"
    assert TransportMode.FLIGHT == "flight"
    assert CabinClass.BUSINESS == "business"
    assert ItemCategory.ELECTRONICS == "electronics"
    assert SafetyStatus.RESTRICTED == "restricted"
    assert Priority.MUST_HAVE == "must_have"
    assert WeightClass.HEAVY == "heavy"


if __name__ == "__main__":
    pytest.main([__file__])