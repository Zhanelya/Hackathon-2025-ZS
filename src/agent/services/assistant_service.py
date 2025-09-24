from __future__ import annotations

import os
from typing import Optional

from src.agent.models.packing_models import GeneratePackingListRequest, PackingListResponse
from src.agent.packing.engine import generate_packing_list


class PackingAssistantService:
    """High-level orchestrator for packing flows.

    Iteration 0: delegates to engine only.
    Future: will consult weather and requirements MCPs before/after engine.
    """

    def __init__(self, offline: Optional[bool] = None, use_mocks: Optional[bool] = None):
        self.offline = (
            True if offline is None else bool(offline)
        ) if os.getenv("DEEPSEEKTRAVELS_OFFLINE", "true").lower() == "true" else False
        self.use_mocks = (
            True if use_mocks is None else bool(use_mocks)
        ) if os.getenv("DEEPSEEKTRAVELS_USE_MOCKS", "true").lower() == "true" else False

    def generate(self, req: GeneratePackingListRequest) -> PackingListResponse:
        # Iteration 1+: fetch weather, requirements, etc.
        return generate_packing_list(req)
