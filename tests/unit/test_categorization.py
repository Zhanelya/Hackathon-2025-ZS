from src.agent.models.packing_models import PackingListItem


def test_item_has_required_fields():
    item = PackingListItem(
        category="documents",
        name="Passport",
        qty=1,
        estimatedVolumeL=0.01,
        estimatedWeightKg=0.05,
        weightClass="light",
        priority="must_have",
        safetyStatus="safe",
        flags=[],
        reason="required",
        restricted=False,
        alternatives=[],
    )
    assert item.category == "documents"
    assert item.priority == "must_have"
