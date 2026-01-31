"""Home Assistant integration module"""

import logging
from datetime import datetime
from typing import Optional
import aiohttp
from .config import config
from .models import SwitchConfig

logger = logging.getLogger(__name__)


class HomeAssistantClient:
    """Client for interacting with Home Assistant REST API"""
    
    def __init__(self):
        self.base_url = config.ha_url
        self.token = config.supervisor_token
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def _get_entity_id(self, switch_id: str) -> str:
        """Get Home Assistant entity ID for a switch"""
        return f"input_boolean.webhook_{switch_id}"
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[dict] = None
    ) -> dict:
        """Make HTTP request to Home Assistant API"""
        url = f"{self.base_url}/api/{endpoint}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method,
                    url,
                    headers=self.headers,
                    json=json_data,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    response.raise_for_status()
                    return await response.json()
        except aiohttp.ClientError as e:
            logger.error(f"Home Assistant API error: {e}")
            raise Exception(f"Failed to communicate with Home Assistant: {e}")
        except Exception as e:
            logger.error(f"Unexpected error calling Home Assistant: {e}")
            raise
    
    async def ensure_switch_exists(self, switch: SwitchConfig) -> bool:
        """
        Ensure input_boolean helper exists for the switch
        
        Args:
            switch: Switch configuration
            
        Returns:
            True if switch exists or was created
        """
        entity_id = self._get_entity_id(switch.id)
        
        try:
            # Check if entity exists
            await self._make_request("GET", f"states/{entity_id}")
            logger.debug(f"Switch {entity_id} already exists")
            return True
        except Exception:
            # Entity doesn't exist, create it
            logger.info(f"Creating input_boolean for switch {switch.id}")
            
            try:
                # Create input_boolean via service call
                await self._make_request(
                    "POST",
                    "services/input_boolean/create",
                    json_data={
                        "name": switch.name,
                        "icon": switch.icon,
                        "initial": False
                    }
                )
                
                # Update entity ID to match our naming convention
                # Note: This is a simplified approach. In production, you might
                # need to use Home Assistant's entity registry API
                logger.info(f"Successfully created switch {entity_id}")
                return True
            except Exception as e:
                logger.error(f"Failed to create switch {switch.id}: {e}")
                return False
    
    async def get_state(self, switch_id: str) -> dict:
        """
        Get current state of a switch
        
        Args:
            switch_id: Switch ID
            
        Returns:
            State dictionary with 'state' and 'attributes'
        """
        entity_id = self._get_entity_id(switch_id)
        
        try:
            response = await self._make_request("GET", f"states/{entity_id}")
            return {
                "state": response.get("state", "unknown"),
                "attributes": response.get("attributes", {})
            }
        except Exception as e:
            logger.error(f"Failed to get state for {switch_id}: {e}")
            raise
    
    async def turn_on(self, switch_id: str) -> None:
        """Turn on a switch"""
        entity_id = self._get_entity_id(switch_id)
        
        await self._make_request(
            "POST",
            f"services/input_boolean/turn_on",
            json_data={"entity_id": entity_id}
        )
        logger.info(f"Switch {switch_id} turned on")
    
    async def turn_off(self, switch_id: str) -> None:
        """Turn off a switch"""
        entity_id = self._get_entity_id(switch_id)
        
        await self._make_request(
            "POST",
            f"services/input_boolean/turn_off",
            json_data={"entity_id": entity_id}
        )
        logger.info(f"Switch {switch_id} turned off")
    
    async def toggle(self, switch_id: str) -> None:
        """Toggle a switch"""
        entity_id = self._get_entity_id(switch_id)
        
        await self._make_request(
            "POST",
            f"services/input_boolean/toggle",
            json_data={"entity_id": entity_id}
        )
        logger.info(f"Switch {switch_id} toggled")
    
    async def set_attributes(
        self,
        switch_id: str,
        attributes: dict
    ) -> None:
        """
        Set custom attributes on a switch
        
        Note: This uses state update to set attributes
        """
        entity_id = self._get_entity_id(switch_id)
        current_state = await self.get_state(switch_id)
        
        # Merge new attributes with existing ones
        updated_attributes = current_state.get("attributes", {}).copy()
        updated_attributes.update(attributes)
        updated_attributes["last_triggered_at"] = datetime.now().isoformat()
        
        # Update state with new attributes
        try:
            await self._make_request(
                "POST",
                f"states/{entity_id}",
                json_data={
                    "state": current_state["state"],
                    "attributes": updated_attributes
                }
            )
            logger.debug(f"Updated attributes for {switch_id}")
        except Exception as e:
            logger.warning(f"Failed to set attributes for {switch_id}: {e}")
    
    async def initialize_switches(self) -> None:
        """Initialize all configured switches"""
        logger.info(f"Initializing {len(config.switches)} switches...")
        
        for switch in config.switches:
            try:
                await self.ensure_switch_exists(switch)
            except Exception as e:
                logger.error(f"Failed to initialize switch {switch.id}: {e}")
        
        logger.info("Switch initialization complete")


# Global Home Assistant client instance
ha_client = HomeAssistantClient()
