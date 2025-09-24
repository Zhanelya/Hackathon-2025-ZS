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
        result = self.engine.generate(context, weather)
        return {
            "items": [item.__dict__ for item in result.items],
            "notes": result.notes,
            "weather": weather,
        }

    def describe(self, context: PackingContext) -> str:
        weather = self.clients["weather"].get_current(context.destination)
        result = self.engine.generate(context, weather)
        lines = [f"DeepseekTravels packing list for {context.destination}:"]
        for item in result.items:
            lines.append(f"- {item.name} x{item.quantity} ({item.category.value})")
        lines.extend(result.notes)
        lines.append(
            f"Weather reference: {weather.get('condition')} at {weather.get('temperature_c')}°C"
        )
        return "\n".join(lines)

    def chat_once(self, message: str, context: PackingContext) -> str:
        self.history.append(f"user: {message}")
        weather = self.clients["weather"].get_current(context.destination)
        result = self.engine.generate(context, weather)
        summary = ", ".join(f"{item.name} x{item.quantity}" for item in result.items[:5])
        reply = (
            f"DeepseekTravels: Based on your trip to {context.destination}, consider {summary}. "
            f"(Weather: {weather.get('condition')} at {weather.get('temperature_c')}°C)"
        )
        self.history.append(f"assistant: {reply}")
        return reply

