"""Configuration management"""

import os
import json
import logging
from typing import List
from pydantic_settings import BaseSettings
from .models import SwitchConfig

logger = logging.getLogger(__name__)


class AppConfig(BaseSettings):
    """Application configuration loaded from environment variables"""
    
    jwt_secret: str = os.getenv("JWT_SECRET", "")
    port: int = int(os.getenv("PORT", "8099"))
    log_level: str = os.getenv("LOG_LEVEL", "info").upper()
    supervisor_token: str = os.getenv("SUPERVISOR_TOKEN", "")
    ha_url: str = os.getenv("HA_URL", "http://supervisor/core")
    
    @property
    def switches(self) -> List[SwitchConfig]:
        """Parse switches configuration from JSON environment variable"""
        switches_json = os.getenv("SWITCHES", "[]")
        try:
            switches_data = json.loads(switches_json)
            return [SwitchConfig(**switch) for switch in switches_data]
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse switches configuration: {e}")
            return []
    
    def get_switch_by_id(self, switch_id: str) -> SwitchConfig | None:
        """Get switch configuration by ID"""
        for switch in self.switches:
            if switch.id == switch_id:
                return switch
        return None
    
    def validate_config(self) -> bool:
        """Validate configuration"""
        if not self.jwt_secret or len(self.jwt_secret) < 32:
            logger.error("JWT secret must be at least 32 characters long")
            return False
        
        if not self.switches:
            logger.warning("No switches configured")
            return False
        
        # Check for duplicate switch IDs
        switch_ids = [s.id for s in self.switches]
        if len(switch_ids) != len(set(switch_ids)):
            logger.error("Duplicate switch IDs found in configuration")
            return False
        
        return True


# Global config instance
config = AppConfig()
