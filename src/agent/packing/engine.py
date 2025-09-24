from __future__ import annotations

from typing import Dict, List
import re

from src.agent.models.packing_models import (
    GeneratePackingListRequest,
    PackingListItem,
    PackingListResponse,
)
from src.agent.packing.fitters import fit_to_capacity


def generate_packing_list(req: GeneratePackingListRequest) -> PackingListResponse:
    """Generate a packing list using simple deterministic rules (Iteration 1).

    Iteration 1
    - Trip-length scaling for core clothing items; reduced if laundry available.
    - Time-of-day toggles: add sunglasses/sunscreen for day; headlamp/evening wear for night.
    - Activity seeds for hiking, beach, business_dinner.

    Iteration 2
    - Weather influence via req.weatherHints: cold, rain, heat.
    """

    def mk(
        category: str,
        name: str,
        qty: int,
        vol: float,
        wt: float,
        *,
        priority: str = "must_have",
        reason: str = "",
        safety: str = "safe",
        flags: List[str] | None = None,
        restricted: bool = False,
        alts: List[str] | None = None,
    ) -> PackingListItem:
        return PackingListItem(
            category=category,  # type: ignore[arg-type]
            name=name,
            qty=qty,
            estimatedVolumeL=vol,
            estimatedWeightKg=wt,
            weightClass=("heavy" if wt >= 1.0 else "medium" if wt >= 0.3 else "light"),
            priority=priority,  # type: ignore[arg-type]
            safetyStatus=safety,  # type: ignore[arg-type]
            flags=flags or [],
            reason=reason,
            restricted=restricted,
            alternatives=alts or [],
        )

    days = max(1, int(req.tripLengthDays))
    has_laundry = bool(getattr(getattr(req, "accommodation", None), "hasLaundry", False))

    def qty_shirts() -> int:
        # Simple heuristic: without laundry ~ ceil(days/2), with laundry ~ ceil(days/3)
        import math

        return max(2 if has_laundry else 1, math.ceil(days / (3 if has_laundry else 2)))

    def qty_underwear() -> int:
        # 1 per day; with laundry reduce by ~25%
        import math

        return max(3, math.ceil(days * (0.75 if has_laundry else 1.0)))

    def qty_socks() -> int:
        import math

        return max(3, math.ceil(days * (0.75 if has_laundry else 1.0)))

    items: Dict[str, PackingListItem] = {}

    def add(item: PackingListItem) -> None:
        if item.name in items:
            # merge quantities; keep max volume/weight per unit naive assumption
            existing = items[item.name]
            items[item.name] = existing.model_copy(update={"qty": existing.qty + item.qty})
        else:
            items[item.name] = item

    # Documents
    add(
        mk(
            "documents",
            "Passport",
            1,
            0.01,
            0.05,
            reason="Required for international travel",
        )
    )

    # Core clothing
    add(
        mk(
            "clothing",
            "T-shirt",
            qty_shirts(),
            0.3,
            0.15,
            reason=(
                f"{days}d trip; {'with' if has_laundry else 'no'} laundry scaling"
            ),
            alts=["synthetic tee"],
        )
    )
    add(mk("clothing", "Underwear", qty_underwear(), 0.05 * days / 5, 0.03 * days / 5, reason=f"~1/day{' minus laundry' if has_laundry else ''}"))
    add(mk("clothing", "Socks", qty_socks(), 0.06 * days / 5, 0.04 * days / 5, reason=f"~1/day{' minus laundry' if has_laundry else ''}"))

    # Toiletries minimal
    add(mk("toiletries", "Toothbrush", 1, 0.02, 0.02, reason="Basic hygiene"))

    # Time-of-day
    tod = set(req.timeOfDayUsage or [])
    if "day" in tod:
        add(mk("accessories", "Sunglasses", 1, 0.05, 0.03, reason="Daytime usage"))
        add(
            mk(
                "toiletries",
                "Sunscreen (100ml)",
                1,
                0.12,
                0.12,
                reason="Sun protection",
                flags=["liquid"],
            )
        )
    if "night" in tod:
        add(mk("accessories", "Headlamp", 1, 0.2, 0.1, reason="Night-time visibility"))
        add(mk("clothing", "Evening wear", 1, 1.0, 0.8, priority="nice_to_have", reason="Night events"))

    # Weather hints (offline, provided explicitly)
    wh = set(getattr(req, "weatherHints", []) or [])
    if "cold" in wh:
        add(mk("clothing", "Insulated jacket", 1, 5.0, 0.9, reason="Cold weather"))
        add(mk("clothing", "Thermal base layer", 1, 0.6, 0.3, reason="Layering for cold"))
        add(mk("accessories", "Warm hat", 1, 0.3, 0.1, reason="Head warmth"))
        add(mk("accessories", "Gloves", 1, 0.25, 0.15, reason="Hand warmth"))
    if "rain" in wh:
        add(mk("clothing", "Rain jacket", 1, 2.5, 0.5, reason="Rain protection", flags=["waterproof"]))
        add(mk("accessories", "Umbrella (compact)", 1, 0.9, 0.35, reason="Rain protection"))
        add(mk("accessories", "Waterproof shoe covers", 1, 0.8, 0.2, reason="Keep shoes dry"))
    if "heat" in wh:
        add(mk("accessories", "Water bottle (1L)", 1, 1.0, 1.0, reason="Hydration in heat"))
        add(mk("clothing", "Lightweight long-sleeve", 1, 0.5, 0.18, reason="Sun coverage in heat"))
        add(mk("health", "Electrolyte tablets", 1, 0.05, 0.05, reason="Hydration support"))

    # Activities
    activities = set(req.activities or [])
    if "hiking" in activities:
        add(mk("clothing", "Hiking socks", 1, 0.1, 0.08, reason="Hiking support"))
        add(mk("accessories", "Trail shoes", 1, 4.0, 1.2, reason="Trail footwear"))
    if "beach" in activities:
        add(mk("clothing", "Swimwear", 1, 0.4, 0.15, reason="Beach activity"))
        add(mk("accessories", "Quick-dry towel", 1, 1.2, 0.3, reason="Beach activity"))
    if "business" in activities or "business_dinner" in activities:
        add(mk("clothing", "Formal shirt", 1, 0.6, 0.25, reason="Business event"))
        add(mk("accessories", "Dress shoes", 1, 3.5, 0.9, reason="Business attire"))

    final_items = list(items.values())
    # Apply transport/constraints-based restrictions (Iteration 4 - mock rules)
    liquid_limit = getattr(getattr(req, "constraints", None), "liquidLimitMl", None)
    transport_mode = getattr(getattr(req, "transport", None), "mode", None)

    restricted_names: List[str] = []
    if liquid_limit is not None and transport_mode in {None, "airline", "air", "flight"}:
        ml_pat = re.compile(r"(\d+)\s*ml", re.IGNORECASE)

        def parse_ml(name: str) -> int | None:
            m = ml_pat.search(name)
            return int(m.group(1)) if m else None

        new_list: List[PackingListItem] = []
        for it in final_items:
            if "liquid" in (it.flags or []):
                ml = parse_ml(it.name)
                if ml is not None and liquid_limit is not None and ml > int(liquid_limit):
                    it = it.model_copy(update={
                        "safetyStatus": "restricted",
                        "restricted": True,
                        "flags": list(set((it.flags or []) + ["limit-exceeded"]))
                    })
                    restricted_names.append(it.name)
            new_list.append(it)
        final_items = new_list
    totals = {
        "estimatedVolumeL": float(sum(i.estimatedVolumeL for i in final_items)),
        "estimatedWeightKg": float(sum(i.estimatedWeightKg for i in final_items)),
    }

    notes = [
        "Iteration 1 rules: scaling + time-of-day + activity seeds",
        "Iteration 2 rules: weather hints (cold/rain/heat)",
        f"Laundry: {'yes' if has_laundry else 'no'}",
    ]

    if restricted_names:
        notes.append(f"Iteration 4 restrictions: liquids exceeding {liquid_limit}ml marked restricted: {', '.join(sorted(set(restricted_names)))}")

    # Constraints fitter (Iteration 3)
    cap = getattr(getattr(req, "constraints", None), "capacityLiters", None)
    maxw = getattr(getattr(req, "constraints", None), "maxWeightKg", None)
    removed_summary = None
    if cap is not None or maxw is not None:
        before_v = totals["estimatedVolumeL"]
        before_w = totals["estimatedWeightKg"]
        # Prepare counts to compute removal summary
        before_counts: Dict[str, int] = {}
        for it in final_items:
            before_counts[it.name] = before_counts.get(it.name, 0) + it.qty

        fitted = fit_to_capacity(final_items, cap, maxw)
        final_items = fitted
        totals = {
            "estimatedVolumeL": float(sum(i.estimatedVolumeL for i in final_items)),
            "estimatedWeightKg": float(sum(i.estimatedWeightKg for i in final_items)),
        }
        # Compute removal summary
        after_counts: Dict[str, int] = {}
        for it in final_items:
            after_counts[it.name] = after_counts.get(it.name, 0) + it.qty
        deltas: Dict[str, int] = {}
        for name, cnt in before_counts.items():
            diff = cnt - after_counts.get(name, 0)
            if diff > 0:
                deltas[name] = diff
        if deltas:
            removed_summary = ", ".join([f"{k} (-{v})" for k, v in sorted(deltas.items())])
        if totals["estimatedVolumeL"] < before_v or totals["estimatedWeightKg"] < before_w:
            notes.append(
                f"Iteration 3 fitter applied: capacity={cap or '∞'}L, maxWeight={maxw or '∞'}kg"
            )
            if removed_summary:
                notes.append(f"Removed items: {removed_summary}")

    return PackingListResponse(items=final_items, totals=totals, notes=notes)
