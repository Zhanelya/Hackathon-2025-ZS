"""Configuration for booking MCP server."""

import os
from typing import Optional


class Config:
    """Configuration settings for booking service."""
    
    # Phase 1: All external HTTP is disabled
    OFFLINE_MODE: bool = True
    USE_MOCKS: bool = True
    DEMO_ONLY: bool = True
    
    # Future: External API endpoints (disabled in Phase 1)
    FLIGHTS_API_URL: Optional[str] = None
    HOTELS_API_URL: Optional[str] = None
    ACTIVITIES_API_URL: Optional[str] = None
    
    # Hold booking settings
    DEFAULT_HOLD_DURATION_MINUTES: int = 15
    MAX_HOLD_DURATION_MINUTES: int = 60
    
    # Demo disclaimers
    DEMO_DISCLAIMER: str = "DEMO ONLY - No real bookings are made"
    
    @classmethod
    def from_env(cls) -> "Config":
        """Create config from environment variables."""
        config = cls()
        
        # Force offline/demo mode in Phase 1
        config.OFFLINE_MODE = os.getenv("DEEPSEEKTRAVELS_OFFLINE", "true").lower() == "true"
        config.USE_MOCKS = os.getenv("DEEPSEEKTRAVELS_USE_MOCKS", "true").lower() == "true"
        config.DEMO_ONLY = True  # Always true in Phase 1
        
        if not config.OFFLINE_MODE:
            raise RuntimeError("Phase 1: Only offline mode is supported. Set DEEPSEEKTRAVELS_OFFLINE=true")
        
        return config


# Global config instance
config = Config.from_env()