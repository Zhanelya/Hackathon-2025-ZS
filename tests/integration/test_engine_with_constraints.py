from src.agent.packing.engine import generate_packing_list
from src.agent.models.packing_models import GeneratePackingListRequest, Dates, Constraints


def test_engine_applies_fitter_and_updates_notes():
    req = GeneratePackingListRequest(
        destination="TestCity",
        dates=Dates(start="2025-10-01", end="2025-10-03"),
        tripLengthDays=3,
        activities=["beach"],
        timeOfDayUsage=["day", "night"],
        weatherHints=["cold", "rain", "heat"],
        constraints=Constraints(capacityLiters=8.0, maxWeightKg=3.0),
    )
    resp = generate_packing_list(req)
    # Should be within limits
    assert resp.totals["estimatedVolumeL"] <= 8.0 + 1e-9
    assert resp.totals["estimatedWeightKg"] <= 3.0 + 1e-9
    # Notes should mention fitter
    assert any("Iteration 3 fitter applied" in n for n in resp.notes)
