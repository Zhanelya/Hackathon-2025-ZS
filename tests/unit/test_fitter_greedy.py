from src.agent.packing.fitters import fit_to_capacity
from src.agent.models.packing_models import PackingListItem


def mk(name, vol, wt, qty=1, priority="must_have", category="accessories"):
    return PackingListItem(
        category=category,
        name=name,
        qty=qty,
        estimatedVolumeL=vol,
        estimatedWeightKg=wt,
        weightClass=("heavy" if wt >= 1.0 else "medium" if wt >= 0.3 else "light"),
        priority=priority,
        safetyStatus="safe",
        flags=[],
        reason="test",
        restricted=False,
        alternatives=[],
    )


def test_trims_nice_to_have_before_must_have():
    items = [
        mk("Heavy nice", 3.0, 1.2, priority="nice_to_have"),
        mk("Light must", 0.5, 0.1, priority="must_have"),
    ]
    out = fit_to_capacity(items, capacity_l=2.0, max_weight_kg=2.0)
    names = {i.name for i in out}
    assert "Light must" in names and "Heavy nice" not in names


def test_trims_until_within_limits_by_unit():
    items = [
        mk("Bulk socks", 0.4, 0.1, qty=5, priority="must_have", category="clothing"),
        mk("Big towel", 2.0, 0.4, qty=1, priority="nice_to_have"),
    ]
    # Capacity 2.5L, Weight 0.6kg — should remove the Big towel first, then 1-2 socks if needed
    out = fit_to_capacity(items, capacity_l=2.5, max_weight_kg=0.6)
    total_vol = sum(i.estimatedVolumeL * i.qty for i in out)
    total_wt = sum(i.estimatedWeightKg * i.qty for i in out)
    assert total_vol <= 2.5 + 1e-9
    assert total_wt <= 0.6 + 1e-9
    # Big towel removed
    assert all(i.name != "Big towel" for i in out)
