"""Console interface scaffold for DeepseekTravels.

Phase 1 ships with mock/offline functionality only. The CLI focuses on wiring
inputs to the assistant service and printing placeholder responses until the
domain logic is implemented.
"""

from __future__ import annotations

import argparse

from ..models.packing_models import PackingContext
from ..services.assistant_service import PackingAssistantService
def _build_context_from_args(args: argparse.Namespace) -> PackingContext:
    return PackingContext(
        destination=getattr(args, "destination", ""),
        trip_length_days=getattr(args, "trip_length_days", 1),
        activities=[],
        time_of_day_usage=["day"],
    )



def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="DeepseekTravels",
        description="DeepseekTravels packing assistant (Phase 1 scaffold).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    assist = sub.add_parser("assist", help="Interactive conversation mode")
    assist.add_argument("destination", help="Trip destination")
    assist.add_argument("trip_length_days", type=int)

    generate = sub.add_parser("generate", help="One-shot packing list")
    generate.add_argument("destination")
    generate.add_argument("trip_length_days", type=int)

    simple = sub.add_parser("simple", help="Keep-it-simple checklist")
    simple.add_argument("destination")

    sub.add_parser("book", help="Booking suggestion flow (mock only)")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    service = PackingAssistantService.create()
    ctx = _build_context_from_args(args)

    if args.command == "generate":
        print(service.describe(ctx))
    elif args.command == "simple":
        print(service.describe(ctx))
    elif args.command == "assist":
        print("Entering chat mode. Type 'exit' to quit.")
        while True:
            try:
                question = input("You: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye!")
                break
            if not question:
                continue
            if question.lower() in {"exit", "quit", "q"}:
                print("Goodbye!")
                break
            reply = service.chat_once(question, ctx)
            print(reply)
    else:
        print("DeepseekTravels interactive modes coming soon. (mock mode)")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry guard
    raise SystemExit(main())

