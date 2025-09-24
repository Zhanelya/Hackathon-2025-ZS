"""High-level orchestration for DeepseekTravels (mock Phase 1)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from ..models.packing_models import PackingContext
from ..packing.engine import DeepseekTravelsEngine
from .mcp_clients import build_mock_clients


@dataclass
class PackingAssistantService:
    """Facade for coordinating engine and mock MCP clients."""

    engine: DeepseekTravelsEngine
    clients: Dict[str, Any]

    @classmethod
    def create(cls) -> "PackingAssistantService":
        clients = build_mock_clients()
        engine = DeepseekTravelsEngine()
        return cls(engine=engine, clients=clients)

    def generate_packing_list(self, context: PackingContext) -> dict[str, Any]:
        result = self.engine.generate(context)
        return {
            "items": [item.__dict__ for item in result.items],
            "notes": result.notes,
        }

    def describe(self, context: PackingContext) -> str:
        result = self.engine.generate(context)
        lines = [f"DeepseekTravels packing list for {context.destination}:"]
        for item in result.items:
            lines.append(f"- {item.name} x{item.quantity} ({item.category.value})")
        lines.extend(result.notes)
        return "\n".join(lines)

