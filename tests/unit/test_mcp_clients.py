import importlib

import pytest

from src.agent.services import mcp_clients


def test_build_mock_clients_returns_expected(monkeypatch):
    monkeypatch.setenv("DEEPSEEKTRAVELS_USE_MOCKS", "true")

    clients = mcp_clients.build_mock_clients()

    assert "weather" in clients
    assert isinstance(clients["weather"], mcp_clients.WeatherClient)
    weather = clients["weather"].get_current("Paris")
    assert weather["location"].startswith("Paris")

    requirements = clients["requirements"].get_visa_requirements("PL", "FR")
    assert requirements["visa_required"] is False

    budgeting = clients["budgeting"].get_defaults()
    assert "laundry_per_load" in budgeting


def test_build_mock_clients_requires_mock(monkeypatch):
    monkeypatch.setenv("DEEPSEEKTRAVELS_USE_MOCKS", "false")

    with pytest.raises(RuntimeError):
        mcp_clients.build_mock_clients()

    # Reset for other tests
    monkeypatch.setenv("DEEPSEEKTRAVELS_USE_MOCKS", "true")
    importlib.reload(mcp_clients)

