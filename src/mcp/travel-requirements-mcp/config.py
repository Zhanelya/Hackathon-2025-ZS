"""Configuration for travel requirements MCP server."""

import os
from typing import Optional


class Config:
    """Configuration settings for travel requirements service."""
    
    # Phase 1: All external HTTP is disabled
    OFFLINE_MODE: bool = True
    USE_MOCKS: bool = True
    
    # Future: External API endpoints (disabled in Phase 1)
    SECURITY_API_URL: Optional[str] = None
    BAGGAGE_API_URL: Optional[str] = None
    VISA_API_URL: Optional[str] = None
    DOCUMENTS_API_URL: Optional[str] = None
    
    # Rate limiting
    MAX_REQUESTS_PER_MINUTE: int = 60
    
    @classmethod
    def from_env(cls) -> "Config":
        """Create config from environment variables."""
        config = cls()
        
        # Force offline mode in Phase 1
        config.OFFLINE_MODE = os.getenv("DEEPSEEKTRAVELS_OFFLINE", "true").lower() == "true"
        config.USE_MOCKS = os.getenv("DEEPSEEKTRAVELS_USE_MOCKS", "true").lower() == "true"
        
        if not config.OFFLINE_MODE:
            raise RuntimeError("Phase 1: Only offline mode is supported. Set DEEPSEEKTRAVELS_OFFLINE=true")
        
        return config


# Global config instance
config = Config.from_env()