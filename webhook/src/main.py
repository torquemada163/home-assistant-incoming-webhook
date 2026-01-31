"""Main FastAPI application"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from .models import WebhookRequest, WebhookResponse, ErrorResponse
from .config import config
from .auth import verify_authentication
from .ha_integration import ha_client

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.log_level),
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("=" * 50)
    logger.info("Starting Incoming Webhook Addon")
    logger.info("=" * 50)
    
    # Validate configuration
    if not config.validate_config():
        logger.error("Configuration validation failed!")
        raise RuntimeError("Invalid configuration")
    
    logger.info(f"Configuration validated successfully")
    logger.info(f"Configured switches: {len(config.switches)}")
    
    # Initialize Home Assistant switches
    try:
        await ha_client.initialize_switches()
    except Exception as e:
        logger.error(f"Failed to initialize switches: {e}")
        # Don't raise - allow addon to start even if HA is temporarily unavailable
    
    logger.info("Webhook addon is ready to receive requests")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Incoming Webhook Addon")


# Create FastAPI app
app = FastAPI(
    title="Home Assistant Incoming Webhook",
    description="Secure webhook API for controlling virtual switches",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {
        "name": "Home Assistant Incoming Webhook",
        "version": "1.0.0",
        "status": "running",
        "switches_configured": len(config.switches)
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.post("/webhook", response_model=WebhookResponse)
async def webhook(
    request: WebhookRequest,
    jwt_payload: dict = Depends(verify_authentication)
):
    """
    Main webhook endpoint for controlling switches
    
    Args:
        request: Webhook request with switch_id, action, and optional attributes
        jwt_payload: Verified JWT payload (injected by auth dependency)
        
    Returns:
        WebhookResponse with operation result
    """
    switch_id = request.switch_id
    action = request.action
    custom_attributes = request.attributes or {}
    
    logger.info(f"Webhook called: switch_id={switch_id}, action={action}")
    
    # Validate switch exists in configuration
    switch_config = config.get_switch_by_id(switch_id)
    if not switch_config:
        logger.warning(f"Switch '{switch_id}' not found in configuration")
        raise HTTPException(
            status_code=404,
            detail=f"Switch '{switch_id}' is not configured"
        )
    
    try:
        # Perform the requested action
        if action == "on":
            await ha_client.turn_on(switch_id)
            
        elif action == "off":
            await ha_client.turn_off(switch_id)
            
        elif action == "toggle":
            await ha_client.toggle(switch_id)
        
        # Set custom attributes (for all actions including status)
        if custom_attributes:
            await ha_client.set_attributes(switch_id, custom_attributes)
        
        # Get current state
        state_info = await ha_client.get_state(switch_id)
        
        # Build response
        response = WebhookResponse(
            status="success",
            switch_id=switch_id,
            action=action,
            state=state_info["state"],
            attributes=state_info["attributes"]
        )
        
        logger.info(
            f"Successfully processed {action} for {switch_id}, "
            f"state={state_info['state']}"
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing webhook request: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Custom HTTP exception handler"""
    error_response = ErrorResponse(
        error=exc.detail if isinstance(exc.detail, str) else "Error occurred",
        details=str(exc.detail) if not isinstance(exc.detail, str) else None
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """General exception handler for unexpected errors"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    error_response = ErrorResponse(
        error="Internal server error",
        details="An unexpected error occurred"
    )
    
    return JSONResponse(
        status_code=500,
        content=error_response.model_dump()
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=config.port,
        log_level=config.log_level.lower()
    )
