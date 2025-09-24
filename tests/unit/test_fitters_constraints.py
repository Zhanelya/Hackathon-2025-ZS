from src.agent.models.packing_models import PackingListItem
from src.agent.packing.fitters import fit_to_capacity


def test_fitters_placeholder_noop():
    items = [
        PackingListItem(
            category="clothing",
            name="T-shirt",
            qty=2,
            estimatedVolumeL=0.6,
            estimatedWeightKg=0.3,
            weightClass="light",
            priority="must_have",
            safetyStatus="safe",
            flags=[],
            reason="test",
            restricted=False,
            alternatives=[],
        )
    ]
    out = fit_to_capacity(items, capacity_l=5.0, max_weight_kg=8.0)
    assert out == items
