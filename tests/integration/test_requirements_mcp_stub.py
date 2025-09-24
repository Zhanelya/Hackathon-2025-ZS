import os
import pytest

from src.agent.services.mcp_clients import TravelRequirementsClient, OfflineNetworkGuard


def test_offline_guard_blocks_network(monkeypatch):
    monkeypatch.setenv("DEEPSEEKTRAVELS_OFFLINE", "true")
    client = TravelRequirementsClient()
    with pytest.raises(OfflineNetworkGuard):
        client.get_security_rules("LHR", "GB", "BA", "economy")
