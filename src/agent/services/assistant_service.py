"""High-level orchestration for DeepseekTravels (mock Phase 1)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from ..models.packing_models import PackingContext
from ..packing.engine import DeepseekTravelsEngine
from .mcp_clients import build_mock_clients


@dataclass
class PackingAssistantService:
    """Facade for coordinating engine and mock MCP clients."""

    engine: DeepseekTravelsEngine
    clients: Dict[str, Any]
    history: List[str] = field(default_factory=list)

    @classmethod
    def create(cls) -> "PackingAssistantService":
        clients = build_mock_clients()
        engine = DeepseekTravelsEngine()
        return cls(engine=engine, clients=clients)

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

