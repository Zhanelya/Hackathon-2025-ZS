"""MCP client builders for DeepseekTravels."""

from __future__ import annotations

import os
from typing import Any, Dict

from langchain_mcp_adapters.client import MultiServerMCPClient


def build_mock_clients() -> dict[str, Any]:
    """Return MCP tool clients backed by the local mock MCP servers."""

    base_config = {}

    attractions_url = os.getenv("ATTRACTIONS_MCP_URL")
    if attractions_url:
        base_config["attractions"] = {
            "transport": "streamable_http",
            "url": attractions_url,
        }

    base_config["weather"] = {
        "transport": "streamable_http",
        "url": os.getenv("WEATHER_MCP_URL", "http://localhost:8009"),
    }
    base_config["requirements"] = {
        "transport": "streamable_http",
        "url": os.getenv("REQUIREMENTS_MCP_URL", "http://localhost:8010"),
    }
    base_config["booking"] = {
        "transport": "streamable_http",
        "url": os.getenv("BOOKING_MCP_URL", "http://localhost:8011"),
    }

    # Phase 1 still enforces mock mode, but the clients themselves connect over MCP.
    if os.getenv("DEEPSEEKTRAVELS_USE_MOCKS", "true").lower() != "true":
        raise RuntimeError("Phase 1 requires mock mode enabled.")

    # Existing deterministic budgeting helper remains in-process until a dedicated MCP is built.
    mcp_client = MultiServerMCPClient(base_config)

    return {
        "mcp_client": mcp_client,
    }


__all__ = ["build_mock_clients"]

