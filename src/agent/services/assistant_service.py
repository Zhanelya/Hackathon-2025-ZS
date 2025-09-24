"""High-level orchestration for DeepseekTravels (mock Phase 1)."""

from __future__ import annotations

import asyncio
import os
import re
import warnings
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..models.packing_models import PackingContext
from ..packing.engine import DeepseekTravelsEngine
from .langchain_agent import build_langchain_agent
from .mcp_clients import build_mock_clients


INTERACTIVE_FIELDS = [
    {
        "field": "origin_city",
        "question": "Which city are you departing from?",
        "required": True,
    },
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
        "field": "start_date",
        "question": "When does your trip start? (YYYY-MM-DD)",
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
                origin_city=None,
                start_date=None,
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
        self.state.awaiting_field = "origin_city"
        return "Hi! I’m DeepseekTravels. Let’s build your packing plan—first, which city are you departing from?"

    def process_conversation_turn(self, user_input: str) -> str:
        if not user_input.strip():
            return "I didn’t catch that—could you repeat?"

        if not self.state.ready:
            _prefill_from_text(self.state.context, user_input)

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
                if field == "start_date":
                    user_input = user_input.strip()
                    if not user_input:
                        return "Please share the start date in YYYY-MM-DD format (or say skip)."
                    setattr(self.state.context, field, user_input)
                elif user_input.lower() in {"skip", "none", "n/a"} and not info["required"]:
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


ACTIVITY_KEYWORDS = {
    "hiking": ["hike", "hiking", "trail"],
    "beach": ["beach", "swim", "snorkel"],
    "museum": ["museum", "gallery", "art"]
}

TIME_OF_DAY_KEYWORDS = {
    "day": ["day", "morning", "afternoon"],
    "night": ["night", "evening"],
}

def _prefill_from_text(context: PackingContext, text: str) -> None:
    lower = text.lower()

    def _clean(proposed: str) -> str:
        return re.sub(r"[^A-Za-z\s-]", "", proposed).strip().title()

    # Origin extraction
    if not context.origin_city:
        match = re.search(r"from\s+([A-Za-z\s-]+?)(?:\s+to|\s+for|\.|,|$)", text, re.IGNORECASE)
        if match:
            context.origin_city = _clean(match.group(1))

    # Destination extraction (support "go to" etc.)
    if not context.destination:
        match = re.search(r"(?:go(?:ing)?|travel(?:ing)?|head(?:ing)?|trip)\s+to\s+([A-Za-z\s-]+?)(?:\s+for|\s+in|\s+with|\.|,|$)", text, re.IGNORECASE)
        if match:
            context.destination = _clean(match.group(1))
    if not context.destination and "philippines" in lower:
        context.destination = "Philippines"

    if not context.destination_country:
        match = re.search(r"(?:country|region)\s+([A-Za-z\s-]+)", text, re.IGNORECASE)
        if match:
            context.destination_country = _clean(match.group(1))
        elif context.destination:
            context.destination_country = context.destination

    if not context.nationality:
        match = re.search(r"(?:i\s+am|i'm|passport(?:\s+is)?|nationality(?:\s+is)?)\s+([A-Za-z]+)", text, re.IGNORECASE)
        if match:
            context.nationality = _clean(match.group(1))
    if not context.nationality and "polish" in lower:
        context.nationality = "Polish"

    # detect partner nationalities (use first mentioned for primary context)
    if "girlfriend" in lower and "ukrain" in lower and context.traveling_adults in (None, 0):
        context.traveling_adults = 2

    # Start date parsing (YYYY-MM-DD or "October 27")
    if not context.start_date:
        iso_match = re.search(r"(\d{4}-\d{2}-\d{2})", text)
        if iso_match:
            context.start_date = iso_match.group(1)
        else:
            month_names = {
                "january": 1,
                "february": 2,
                "march": 3,
                "april": 4,
                "may": 5,
                "june": 6,
                "july": 7,
                "august": 8,
                "september": 9,
                "october": 10,
                "november": 11,
                "december": 12,
            }
            month_match = re.search(
                r"(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2})(?:st|nd|rd|th)?",
                lower,
            )
            if month_match:
                month = month_names[month_match.group(1)]
                day = int(month_match.group(2))
                year = datetime.now().year
                context.start_date = f"{year:04d}-{month:02d}-{day:02d}"
            else:
                alt_match = re.search(
                    r"(\d{1,2})(?:st|nd|rd|th)?\s+(?:of\s+)?(january|february|march|april|may|june|july|august|september|october|november|december)",
                    lower,
                )
                if alt_match:
                    day = int(alt_match.group(1))
                    month = month_names[alt_match.group(2)]
                    year = datetime.now().year
                    context.start_date = f"{year:04d}-{month:02d}-{day:02d}"

    if context.trip_length_days in (None, 0):
        match = re.search(r"(\d+)\s+(?:day|days)", lower)
        if match:
            context.trip_length_days = int(match.group(1))
        else:
            week_match = re.search(r"(\d+)\s+(?:week|weeks)", lower)
            if week_match:
                context.trip_length_days = int(week_match.group(1)) * 7

    for label, keywords in TIME_OF_DAY_KEYWORDS.items():
        if any(word in lower for word in keywords):
            if label not in context.time_of_day_usage:
                context.time_of_day_usage.append(label)
    if not context.time_of_day_usage and "both" in lower:
        context.time_of_day_usage.extend(["day", "night"])

    for label, keywords in ACTIVITY_KEYWORDS.items():
        if any(word in lower for word in keywords):
            if label not in context.activities:
                context.activities.append(label)
    if "island" in lower and "jump" in lower:
        if "beach" not in context.activities:
            context.activities.append("beach")

    if context.traveling_adults in (None, 0):
        match = re.search(r"(\d+)\s+(?:adult|adults)", lower)
        if match:
            context.traveling_adults = int(match.group(1))
        elif "solo" in lower:
            context.traveling_adults = 1
        elif any(term in lower for term in ["girlfriend", "boyfriend", "partner", "spouse", "husband", "wife"]):
            context.traveling_adults = 2

    if context.carrying_children in (None, 0):
        match = re.search(r"(\d+)\s+(?:child|children)\b", lower)
        if match:
            context.carrying_children = int(match.group(1))

    if context.carrying_infants in (None, 0):
        match = re.search(r"(\d+)\s+(?:infant|infants|baby|babies)", lower)
        if match:
            context.carrying_infants = int(match.group(1))

    if context.traveling_pets in (None, 0):
        match = re.search(r"(\d+)\s+(?:pet|pets)", lower)
        if match:
            context.traveling_pets = int(match.group(1))


