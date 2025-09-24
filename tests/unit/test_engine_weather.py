from src.agent.packing.engine import generate_packing_list
from src.agent.models.packing_models import GeneratePackingListRequest, Dates


def make_req(weather_hints):
    return GeneratePackingListRequest(
        destination="TestCity",
        dates=Dates(start="2025-01-01", end="2025-01-05"),
        tripLengthDays=4,
        activities=[],
        timeOfDayUsage=[],
        weatherHints=weather_hints,
    )


def names(resp):
    return {i.name for i in resp.items}


def test_cold_weather_adds_warmth_items():
    resp = generate_packing_list(make_req(["cold"]))
    n = names(resp)
    assert {"Insulated jacket", "Thermal base layer", "Warm hat", "Gloves"}.issubset(n)


def test_rain_weather_adds_rain_protection():
    resp = generate_packing_list(make_req(["rain"]))
    n = names(resp)
    assert {"Rain jacket", "Umbrella (compact)", "Waterproof shoe covers"}.issubset(n)


def test_heat_weather_adds_hydration_and_sun_coverage():
    resp = generate_packing_list(make_req(["heat"]))
    n = names(resp)
    assert {"Water bottle (1L)", "Lightweight long-sleeve", "Electrolyte tablets"}.issubset(n)
