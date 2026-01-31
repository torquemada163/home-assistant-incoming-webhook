"""JWT authentication module"""

import jwt
import logging
from datetime import datetime
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .config import config

logger = logging.getLogger(__name__)
security = HTTPBearer()


def verify_jwt_token(token: str) -> dict:
    """
    Verify JWT token and return payload
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            config.jwt_secret,
            algorithms=["HS256"]
        )
        
        # Check expiration if present
        if "exp" in payload:
            exp_timestamp = payload["exp"]
            if datetime.utcnow().timestamp() > exp_timestamp:
                logger.warning("JWT token expired")
                raise HTTPException(
                    status_code=401,
                    detail="Token expired"
                )
        
        logger.debug(f"JWT token verified successfully for issuer: {payload.get('iss', 'unknown')}")
        return payload
        
    except jwt.ExpiredSignatureError:
        logger.warning("JWT token expired")
        raise HTTPException(
            status_code=401,
            detail="Token expired"
        )
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid JWT token: {e}")
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token"
        )
    except Exception as e:
        logger.error(f"Unexpected error during JWT verification: {e}")
        raise HTTPException(
            status_code=401,
            detail="Authentication failed"
        )


async def verify_authentication(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> dict:
    """
    FastAPI dependency for JWT authentication
    
    Args:
        credentials: HTTP authorization credentials from request
        
    Returns:
        Decoded JWT payload
    """
    token = credentials.credentials
    return verify_jwt_token(token)
