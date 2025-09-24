"""High-level orchestration for DeepseekTravels (mock Phase 1)."""

from __future__ import annotations

import asyncio
import os
import re
import warnings
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..models.packing_models import PackingContext
from ..packing.engine import DeepseekTravelsEngine
from .langchain_agent import build_langchain_agent
from .mcp_clients import build_mock_clients


INTERACTIVE_FIELDS = [
    {
        "field": "destination",
        "question": "Great! Where are you traveling to?",
        "required": True,
    },
    {
        "field": "destination_country",
        "question": "Which country or region is that in?",
        "required": True,
    },
    {
        "field": "nationality",
        "question": "What nationality or passport are you traveling with (for visa guidance)?",
        "required": True,
    },
    {
        "field": "trip_length_days",
        "question": "How many days will you be away?",
        "required": True,
    },
    {
        "field": "time_of_day_usage",
        "question": "Will your plans be mostly daytime, nighttime, or both?",
        "required": True,
    },
    {
        "field": "activities",
        "question": "Any key activities planned (e.g., hiking, beach, business meetings)?",
        "required": True,
    },
    {
        "field": "traveling_adults",
        "question": "How many adults are traveling (including you)?",
        "required": True,
    },
    {
        "field": "carrying_children",
        "question": "How many children (ages 2–12) are coming along? (0 if none)",
        "required": True,
    },
    {
        "field": "carrying_infants",
        "question": "Any infants under 2 traveling? (0 if none)",
        "required": True,
    },
    {
        "field": "traveling_pets",
        "question": "Are any pets traveling? If yes, how many (or say 0)?",
        "required": False,
    },
    {
        "field": "capacity_liters",
        "question": "What’s the capacity of your main bag in liters? If unsure, say skip.",
        "required": False,
    },
    {
        "field": "max_weight_kg",
        "question": "What’s the maximum weight you can comfortably carry (kg)? If unsure, say skip.",
        "required": False,
    },
]

FIELD_LOOKUP = {item["field"]: item for item in INTERACTIVE_FIELDS}


NUMERIC_FIELDS = {
    "trip_length_days",
    "capacity_liters",
    "max_weight_kg",
    "traveling_adults",
    "carrying_children",
    "carrying_infants",
    "traveling_pets",
}


def _parse_numeric(value: str) -> Optional[float]:
    value = value.strip()
    if not value:
        return None
    if value.lower() in {"skip", "n/a", "none"}:
        return None
    match = re.search(r"\d+(\.\d+)?", value)
    if not match:
        return None
    parsed = float(match.group())
    return parsed


def _missing_required_fields(context: PackingContext) -> list[str]:
    missing = []
    for item in INTERACTIVE_FIELDS:
        if not item["required"]:
            continue
        value = getattr(context, item["field"], None)
        if value in (None, "", [], {}):
            missing.append(item["field"])
    return missing


def _run_async(coro):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    else:  # pragma: no cover
        return loop.run_until_complete(coro)

"""
Helper functions for LLM usage.
"""


def _should_use_llm() -> bool:
    env_flag = os.getenv("DEEPSEEKTRAVELS_USE_LLM")
    if env_flag is not None:
        return env_flag.lower() == "true"
    required_env = [
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_API_VERSION",
        "AZURE_OPENAI_DEPLOYMENT",
    ]
    return all(os.getenv(key) for key in required_env)


@dataclass
class ConversationState:
    context: PackingContext
    awaiting_field: Optional[str] = None
    skipped_fields: set[str] = field(default_factory=set)
    ready: bool = False


@dataclass
class PackingAssistantService:
    """Facade for coordinating engine and mock MCP clients."""

    engine: DeepseekTravelsEngine
    clients: Dict[str, Any]
    history: List[str] = field(default_factory=list)
    agent_executor: Optional[Any] = None
    mcp_agent_client: Optional[Any] = None
    llm_enabled: bool = False
    state: ConversationState = field(
        default_factory=lambda: ConversationState(
            context=PackingContext(
                destination="",
                destination_country=None,
                nationality=None,
                trip_length_days=0,
                activities=[],
                time_of_day_usage=[],
                capacity_liters=None,
                max_weight_kg=None,
                traveling_adults=None,
                carrying_children=None,
                carrying_infants=None,
                traveling_pets=None,
            )
        )
    )

    @classmethod
    def create(cls) -> "PackingAssistantService":
        clients = build_mock_clients()
        engine = DeepseekTravelsEngine()
        use_llm = _should_use_llm()
        agent_executor: Optional[Any] = None
        mcp_client: Optional[Any] = None
        if use_llm:
            try:
                agent_executor, mcp_client = build_langchain_agent()
            except Exception as exc:  # pragma: no cover - integration guard
                warnings.warn(f"Falling back to mock engine due to LLM init error: {exc}")
                use_llm = False
        return cls(
            engine=engine,
            clients=clients,
            agent_executor=agent_executor,
            mcp_agent_client=mcp_client,
            llm_enabled=use_llm,
        )

    def start_conversation(self) -> str:
        self.state.awaiting_field = "destination"
        return "Hi! I’m DeepseekTravels. Before I build your packing plan, let’s gather a few quick details. First, where are you traveling to?"

    def process_conversation_turn(self, user_input: str) -> str:
        if not user_input.strip():
            return "I didn’t catch that—could you repeat?"

        if self.state.awaiting_field:
            field = self.state.awaiting_field
            info = FIELD_LOOKUP[field]
            if field in NUMERIC_FIELDS:
                numeric = _parse_numeric(user_input)
                if numeric is None:
                    if info["required"]:
                        return "Thanks! I wasn’t able to parse a number—could you provide it in digits (or say skip)?"
                    else:
                        self.state.skipped_fields.add(field)
                        setattr(self.state.context, field, None)
                    self.state.awaiting_field = None
                else:
                    if field in {"traveling_adults", "carrying_children", "carrying_infants", "traveling_pets"}:
                        setattr(self.state.context, field, int(numeric))
                    elif field == "trip_length_days":
                        setattr(self.state.context, field, int(max(1, numeric)))
                    else:
                        setattr(self.state.context, field, numeric)
                    self.state.awaiting_field = None
            else:
                if user_input.lower() in {"skip", "none", "n/a"} and not info["required"]:
                    setattr(self.state.context, field, None)
                elif field in {"activities", "time_of_day_usage"}:
                    tokens = [token.strip() for token in user_input.split(",") if token.strip()]
                    if not tokens and info["required"]:
                        return "Could you list at least one item (use commas if there are multiple)?"
                    setattr(self.state.context, field, tokens)
                else:
                    setattr(self.state.context, field, user_input.strip())
                self.state.awaiting_field = None

        missing = _missing_required_fields(self.state.context)
        if missing:
            next_field = missing[0]
            self.state.awaiting_field = next_field
            return FIELD_LOOKUP[next_field]["question"]

        if not self.state.ready:
            self.state.ready = True
            return (
                "Perfect, I have everything I need! Ask me anything about packing, weather, or bookings, and I’ll tailor the answer to your trip."
            )

        return self.chat_once(user_input, self.state.context)

    def generate_packing_list(self, context: PackingContext) -> dict[str, Any]:
        weather = self.clients["weather"].get_current(context.destination)
        requirements = self._gather_requirements(context)
        result = self.engine.generate(context, weather)
        return {
            "items": [item.__dict__ for item in result.items],
            "notes": result.notes + requirements["notes"],
            "weather": weather,
            "requirements": requirements,
        }

    def describe(self, context: PackingContext) -> str:
        weather = self.clients["weather"].get_current(context.destination)
        requirements = self._gather_requirements(context)
        result = self.engine.generate(context, weather)
        lines = [f"DeepseekTravels packing list for {context.destination}:"]
        for item in result.items:
            lines.append(f"- {item.name} x{item.quantity} ({item.category.value})")
        lines.extend(result.notes + requirements["notes"])
        lines.append(
            f"Weather reference: {weather.get('condition')} at {weather.get('temperature_c')}°C"
        )
        lines.append(f"Security notes: {'; '.join(requirements['security'])}")
        return "\n".join(lines)

    def chat_once(self, message: str, context: PackingContext) -> str:
        if self.llm_enabled and self.agent_executor is not None:
            context_blob = ", ".join(
                f"{key}={value}"
                for key, value in context.__dict__.items()
                if value not in (None, [], {})
            )
            formatted_input = (
                f"Trip context: {context_blob if context_blob else 'not provided'}\n"
                f"User question: {message}"
            )
            payload = {"input": formatted_input}
            result = self.agent_executor.invoke(payload)
            return result.get("output") or result.get("final_output") or ""

        self.history.append(f"user: {message}")
        weather = self.clients["weather"].get_current(context.destination)
        requirements = self._gather_requirements(context)
        result = self.engine.generate(context, weather)
        summary = ", ".join(f"{item.name} x{item.quantity}" for item in result.items[:5])
        reply = (
            f"DeepseekTravels: Based on your trip to {context.destination}, consider {summary}. "
            f"(Weather: {weather.get('condition')} at {weather.get('temperature_c')}°C; "
            f"Security: {'; '.join(requirements['security'])})"
        )
        self.history.append(f"assistant: {reply}")
        return reply

    def suggest_bookings(self, context: PackingContext) -> dict[str, Any]:
        booking_client = self.clients["booking"]
        flights = booking_client.search_flights(context.destination)
        hotels = booking_client.search_hotels(context.destination)
        hold_id = f"HOLD-{context.destination.upper()}-001"
        return {
            "flights": flights.get("flights", []),
            "hotels": hotels.get("hotels", []),
            "hold_id": hold_id,
        }

    def confirm_booking(self, hold_id: str, *, confirm: bool) -> str:
        if not confirm:
            return f"Booking with hold {hold_id} not confirmed."
        return f"Booking confirmed for hold {hold_id}."

    def simple_checklist(self, context: PackingContext) -> str:
        weather = self.clients["weather"].get_current(context.destination)
        result = self.engine.generate(context, weather)
        lines = [f"Quick checklist for {context.destination}:"]
        for item in result.items[:5]:
            lines.append(f"- {item.name} x{item.quantity}")
        lines.append("Pack essentials and double-check documents.")
        return "\n".join(lines)

    def _gather_requirements(self, context: PackingContext) -> dict[str, list[str]]:
        security = self.clients["requirements"].get_security_rules()
        visa = {}
        if context.nationality and context.destination_country:
            visa = self.clients["requirements"].get_visa_requirements(
                context.nationality, context.destination_country
            )
        notes = []
        if visa:
            need = "Visa required" if visa.get("visa_required") else "Visa exemption"
            notes.append(f"Visa status: {need}")
            if visa.get("notes"):
                notes.extend(visa["notes"])
        if security:
            notes.append("Security reminders: " + ", ".join(security.get("restricted", [])))
        return {
            "security": security.get("notes", []),
            "notes": notes,
        }

