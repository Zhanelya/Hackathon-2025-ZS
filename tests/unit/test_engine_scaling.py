from src.agent.models.packing_models import GeneratePackingListRequest, Dates
from src.agent.packing.engine import generate_packing_list


def test_engine_minimal_returns_items():
    req = GeneratePackingListRequest(
        destination="Paris",
        dates=Dates(start="2025-10-01", end="2025-10-03"),
        tripLengthDays=3,
        activities=["museum"],
        timeOfDayUsage=["day"],
    )
    resp = generate_packing_list(req)
    assert len(resp.items) >= 2
    assert any(i.name == "Passport" for i in resp.items)


def test_scaling_with_and_without_laundry():
    req_no_laundry = GeneratePackingListRequest(
        destination="Rome",
        dates=Dates(start="2025-11-01", end="2025-11-06"),
        tripLengthDays=6,
        activities=[],
        timeOfDayUsage=["day"],
    )
    resp_no = generate_packing_list(req_no_laundry)
    tshirts_no = next(i for i in resp_no.items if i.name == "T-shirt").qty

    req_with_laundry = GeneratePackingListRequest(
        destination="Rome",
        dates=Dates(start="2025-11-01", end="2025-11-06"),
        tripLengthDays=6,
        activities=[],
        timeOfDayUsage=["day"],
        accommodation={"hasLaundry": True},  # type: ignore[arg-type]
    )
    resp_yes = generate_packing_list(req_with_laundry)
    tshirts_yes = next(i for i in resp_yes.items if i.name == "T-shirt").qty

    assert tshirts_yes <= tshirts_no


def test_time_of_day_night_items_added():
    req = GeneratePackingListRequest(
        destination="Vienna",
        dates=Dates(start="2025-12-01", end="2025-12-03"),
        tripLengthDays=3,
        activities=[],
        timeOfDayUsage=["night"],
    )
    resp = generate_packing_list(req)
    names = {i.name for i in resp.items}
    assert "Headlamp" in names
    assert "Evening wear" in names


def test_activity_seeds_basic():
    req = GeneratePackingListRequest(
        destination="Lisbon",
        dates=Dates(start="2025-10-01", end="2025-10-05"),
        tripLengthDays=4,
        activities=["hiking", "beach", "business_dinner"],
        timeOfDayUsage=["day"],
    )
    resp = generate_packing_list(req)
    names = {i.name for i in resp.items}
    assert {"Hiking socks", "Trail shoes", "Swimwear", "Quick-dry towel", "Formal shirt", "Dress shoes"}.issubset(names)
