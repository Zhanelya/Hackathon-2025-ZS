from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Ensure repo root is on sys.path when running this file directly
try:
    # e.g., .../src/agent/cli/deepseek_travels_cli.py -> repo root is parents[3]
    _here = Path(__file__).resolve()
    _repo_root = _here.parents[3]
    if str(_repo_root) not in sys.path:
        sys.path.insert(0, str(_repo_root))
except Exception:
    # Best-effort; safe to ignore if not available
    pass

from src.agent.models.packing_models import (
    GeneratePackingListRequest,
    Dates,
    Constraints,
    Transport,
)
from src.agent.services.assistant_service import PackingAssistantService
from src.agent.services.llm_client import get_llm_client_from_env


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="DeepseekTravels CLI")
    sub = p.add_subparsers(dest="command", required=True)

    # simple checklist
    sp_simple = sub.add_parser("simple", help="Emit a concise checklist")
    _add_common_args(sp_simple)

    # generate full list
    sp_gen = sub.add_parser("generate", help="Generate a full categorized list")
    _add_common_args(sp_gen)

    return p


def _add_common_args(sp: argparse.ArgumentParser) -> None:
    sp.add_argument("destination")
    sp.add_argument("start")
    sp.add_argument("end")
    sp.add_argument("trip_days", type=int)
    sp.add_argument("--activities", nargs="*", default=[])
    sp.add_argument("--tod", nargs="*", default=["day"])  # day/night
    sp.add_argument(
        "--weather",
        nargs="*",
        default=[],
        help="Weather hints: cold rain heat",
        choices=["cold", "rain", "heat"],
    )
    sp.add_argument("--capacity-liters", type=float, default=None, help="Bag capacity in liters")
    sp.add_argument("--max-weight-kg", type=float, default=None, help="Max carry weight in kg")
    sp.add_argument("--liquid-limit-ml", type=int, default=None, help="Max liquid container size (ml)")
    sp.add_argument(
        "--transport-mode",
        type=str,
        default=None,
        choices=["airline", "air", "flight", "train", "bus", "car", "boat"],
        help="Transport mode (affects restrictions)",
    )
    sp.add_argument("--use-llm", action="store_true", help="Enable Phase 2 LLM explanation")
    sp.add_argument(
        "--llm-backend",
        type=str,
        choices=["mock", "azure"],
        default=None,
        help="LLM backend to use when --use-llm is set (overrides LLM_BACKEND env)",
    )
    sp.add_argument(
        "--llm-style",
        type=str,
        choices=["short", "detailed"],
        default="short",
        help="LLM explanation style",
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    constraints = None
    if args.capacity_liters is not None or args.max_weight_kg is not None:
        constraints = Constraints(capacityLiters=args.capacity_liters, maxWeightKg=args.max_weight_kg)
    # If user provided only liquid limit, still create constraints
    if args.liquid_limit_ml is not None:
        if constraints is None:
            constraints = Constraints()
        constraints = constraints.model_copy(update={"liquidLimitMl": args.liquid_limit_ml})

    transport = None
    if args.transport_mode is not None:
        transport = Transport(mode=args.transport_mode)

    req = GeneratePackingListRequest(
        destination=args.destination,
        dates=Dates(start=args.start, end=args.end),
        tripLengthDays=args.trip_days,
        activities=args.activities,
        timeOfDayUsage=args.tod,
        weatherHints=args.weather,
        constraints=constraints,
        transport=transport,
    )
    svc = PackingAssistantService()
    resp = svc.generate(req)

    # Optional LLM explanation (Phase 2)
    if getattr(args, "use_llm", False):
        expl = get_llm_client_from_env(getattr(args, "llm_backend", None)).generate_explanation(
            req, resp, style=getattr(args, "llm_style", "short")
        )
        resp = resp.model_copy(update={"notes": list(resp.notes) + [f"LLM: {expl}"]})

    if args.command == "simple":
        # concise checklist: name + qty
        checklist = [{"name": i.name, "qty": i.qty} for i in resp.items]
        print(json.dumps({"checklist": checklist}, indent=2))
    else:
        print(json.dumps(resp.model_dump(), indent=2))

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
