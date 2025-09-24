"""High-level orchestration for DeepseekTravels (mock Phase 1)."""

from __future__ import annotations

import os
import warnings
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..models.packing_models import PackingContext
from ..packing.engine import DeepseekTravelsEngine
from .langchain_agent import build_langchain_agent
from .mcp_clients import build_mock_clients


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
class PackingAssistantService:
    """Facade for coordinating engine and mock MCP clients."""

    engine: DeepseekTravelsEngine
    clients: Dict[str, Any]
    history: List[str] = field(default_factory=list)
    agent_executor: Optional[Any] = None
    mcp_agent_client: Optional[Any] = None
    llm_enabled: bool = False

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

