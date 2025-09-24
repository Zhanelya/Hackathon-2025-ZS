from __future__ import annotations

from typing import List, Tuple, Dict

from src.agent.models.packing_models import PackingListItem


def fit_to_capacity(items: List[PackingListItem], capacity_l: float | None, max_weight_kg: float | None) -> List[PackingListItem]:
    """Greedy fitter: trim items to satisfy capacity and weight.

    Strategy (deterministic):
    - Work at per-unit granularity (qty=1 units) for fair trimming of multi-qty items.
    - Remove in order:
      1) nice_to_have units, then must_have only if still necessary.
      2) Within each group, sort by a score emphasizing the dimension(s) we're exceeding more.
         Score = (wt/limit_wt)*over_wt_ratio + (vol/limit_vol)*over_vol_ratio, descending.
         Ties broken by heavier weight class, then larger vol, then name for stability.
    - Stop when both constraints are satisfied or no units remain.
    - If both constraints are None, return items unchanged.
    """
    if (capacity_l is None) and (max_weight_kg is None):
        return items

    # Compute totals
    total_vol = sum(i.estimatedVolumeL * i.qty for i in items)
    total_wt = sum(i.estimatedWeightKg * i.qty for i in items)
    limit_vol = capacity_l if capacity_l is not None else float("inf")
    limit_wt = max_weight_kg if max_weight_kg is not None else float("inf")

    def within_limits(tv: float, tw: float) -> bool:
        ok_v = tv <= limit_vol + 1e-9
        ok_w = tw <= limit_wt + 1e-9
        # If a limit is inf (i.e., not set), it's always ok
        return ok_v and ok_w

    if within_limits(total_vol, total_wt):
        return items

    # Flatten to units
    units: List[Tuple[str, PackingListItem, float, float]] = []  # (name, item, vol, wt)
    for it in items:
        for _ in range(max(0, it.qty)):
            units.append((it.name, it, float(it.estimatedVolumeL), float(it.estimatedWeightKg)))

    # Helper ranks
    weight_class_rank = {"heavy": 2, "medium": 1, "light": 0}

    def compute_over_ratios(tv: float, tw: float) -> Tuple[float, float]:
        over_v = max(0.0, tv - limit_vol)
        over_w = max(0.0, tw - limit_wt)
        ratio_v = (over_v / limit_vol) if limit_vol != float("inf") else 0.0
        ratio_w = (over_w / limit_wt) if limit_wt != float("inf") else 0.0
        return ratio_v, ratio_w

    def sort_key(unit: Tuple[str, PackingListItem, float, float], over_v: float, over_w: float) -> Tuple[float, int, float, float, str]:
        name, it, vol, wt = unit
        # Score emphasizing exceeding dimensions
        score = (wt / (limit_wt if limit_wt != float("inf") else 1.0)) * over_w + (vol / (limit_vol if limit_vol != float("inf") else 1.0)) * over_v
        return (
            score,
            weight_class_rank.get(it.weightClass, 0),
            vol,
            wt,
            name,
        )

    # Removal process
    removed_counts: Dict[str, int] = {}

    def try_remove_from(group_units: List[Tuple[str, PackingListItem, float, float]]) -> bool:
        nonlocal total_vol, total_wt
        if not group_units:
            return False
        over_v, over_w = compute_over_ratios(total_vol, total_wt)
        # sort descending by score (highest first)
        group_units.sort(key=lambda u: sort_key(u, over_v, over_w), reverse=True)
        name, it, vol, wt = group_units.pop(0)
        total_vol -= vol
        total_wt -= wt
        removed_counts[name] = removed_counts.get(name, 0) + 1
        return True

    # Split units by priority
    nice_units = [u for u in units if u[1].priority == "nice_to_have"]
    must_units = [u for u in units if u[1].priority == "must_have"]

    # Loop until within limits or nothing left to remove
    while not within_limits(total_vol, total_wt):
        if not try_remove_from(nice_units):
            if not try_remove_from(must_units):
                break  # nothing left

    # Rebuild items with decremented qty
    counts: Dict[str, int] = {}
    for it in items:
        counts[it.name] = counts.get(it.name, 0) + it.qty
    for name, cnt in removed_counts.items():
        counts[name] = max(0, counts.get(name, 0) - cnt)

    new_items: List[PackingListItem] = []
    for it in items:
        new_qty = counts.get(it.name, 0)
        if new_qty > 0:
            new_items.append(it.model_copy(update={"qty": new_qty}))

    return new_items
