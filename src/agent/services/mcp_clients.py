from __future__ import annotations

import os


class OfflineNetworkGuard(Exception):
    pass


def ensure_offline() -> None:
    if os.getenv("DEEPSEEKTRAVELS_OFFLINE", "true").lower() == "true":
        # In Phase 1, forbid any live HTTP/network calls
        raise OfflineNetworkGuard(
            "Live network calls are disabled in Phase 1 (offline/mock mode)."
        )


class WeatherClient:
    def forecast(self, lat: float, lon: float, date: str):  # pragma: no cover (stub)
        ensure_offline()


class TravelRequirementsClient:
    def get_security_rules(self, airport_code: str, country_code: str, airline: str, cabin_class: str):  # pragma: no cover (stub)
        ensure_offline()
