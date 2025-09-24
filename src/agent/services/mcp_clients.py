"""Mock MCP clients used in Phase 1 of DeepseekTravels."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict

from .mock_fixtures import (
    BOOKING_FIXTURES,
    BUDGET_FIXTURES,
    SECURITY_FIXTURES,
    VISA_FIXTURES,
    WEATHER_FIXTURES,
)


@dataclass
class WeatherClient:
    """Returns canned weather data keyed by destination."""

    fixtures: Dict[str, Dict[str, Any]]

    def get_current(self, location: str) -> Dict[str, Any]:
        key = location.lower()
        return self.fixtures.get(key, self.fixtures["default"])


@dataclass
class RequirementsClient:
    """Provides security and visa guidance from fixtures."""

    security_fixtures: Dict[str, Dict[str, Any]]
    visa_fixtures: Dict[str, Dict[str, Any]]

    def get_security_rules(self, airport_code: str | None = None) -> Dict[str, Any]:
        return self.security_fixtures.get("default", {})

    def get_visa_requirements(
        self, nationality: str, destination_country: str
    ) -> Dict[str, Any]:
        key = f"{nationality.lower()}-{destination_country.lower()}"
        return self.visa_fixtures.get(key, self.visa_fixtures["default"])


@dataclass
class BookingClient:
    """Returns mocked booking data (flights, hotels)."""

    fixtures: Dict[str, Dict[str, Any]]

    def search_flights(self, destination: str) -> Dict[str, Any]:
        return self.fixtures.get(destination.lower(), self.fixtures["default"])

    def search_hotels(self, destination: str) -> Dict[str, Any]:
        return self.fixtures.get(destination.lower(), self.fixtures["default"])


@dataclass
class BudgetingClient:
    fixtures: Dict[str, Dict[str, Any]]

    def get_defaults(self) -> Dict[str, Any]:
        return self.fixtures.get("default", {})


def build_mock_clients() -> dict[str, Any]:
    """Factory that honors Phase 1 offline requirements."""

    if os.getenv("DEEPSEEKTRAVELS_USE_MOCKS", "true").lower() != "true":
        raise RuntimeError("Phase 1 requires mock mode enabled.")

    return {
        "weather": WeatherClient(WEATHER_FIXTURES),
        "requirements": RequirementsClient(SECURITY_FIXTURES, VISA_FIXTURES),
        "booking": BookingClient(BOOKING_FIXTURES),
        "budgeting": BudgetingClient(BUDGET_FIXTURES),
    }


__all__ = [
    "WeatherClient",
    "RequirementsClient",
    "BookingClient",
    "BudgetingClient",
    "build_mock_clients",
]

