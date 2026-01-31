"""Pydantic models for request/response validation"""

from typing import Optional, Literal
from pydantic import BaseModel, Field


class SwitchConfig(BaseModel):
    """Configuration for a single virtual switch"""
    id: str = Field(..., description="Unique identifier for the switch")
    name: str = Field(..., description="Friendly name displayed in Home Assistant")
    icon: str = Field(default="mdi:light-switch", description="Material Design Icon")


class WebhookRequest(BaseModel):
    """Incoming webhook request model"""
    switch_id: str = Field(..., description="ID of the switch to control")
    action: Literal["on", "off", "toggle", "status"] = Field(
        ..., 
        description="Action to perform: on, off, toggle, or status"
    )
    attributes: Optional[dict] = Field(
        default=None,
        description="Optional custom attributes to set on the switch"
    )


class WebhookResponse(BaseModel):
    """Webhook response model"""
    status: Literal["success", "error"]
    switch_id: Optional[str] = None
    action: Optional[str] = None
    state: Optional[str] = None
    attributes: Optional[dict] = None
    error: Optional[str] = None
    details: Optional[str] = None


class ErrorResponse(BaseModel):
    """Error response model"""
    status: Literal["error"] = "error"
    error: str
    details: Optional[str] = None
