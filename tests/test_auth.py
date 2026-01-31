"""Tests for JWT authentication"""

import pytest
import jwt
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from webhook.src.auth import verify_jwt_token


def test_valid_jwt_token():
    """Test JWT token verification with valid token"""
    secret = "test-secret-key-at-least-32-chars-long"
    
    payload = {
        "iss": "test-service",
        "exp": datetime.now(timezone.utc) + timedelta(hours=1)
    }
    
    token = jwt.encode(payload, secret, algorithm="HS256")
    
    # Mock config
    import webhook.src.config as config_module
    config_module.config.jwt_secret = secret
    
    result = verify_jwt_token(token)
    
    assert result["iss"] == "test-service"
    assert "exp" in result


def test_expired_jwt_token():
    """Test JWT token verification with expired token"""
    secret = "test-secret-key-at-least-32-chars-long"
    
    payload = {
        "iss": "test-service",
        "exp": datetime.now(timezone.utc) - timedelta(hours=1)  # Expired 1 hour ago
    }
    
    token = jwt.encode(payload, secret, algorithm="HS256")
    
    # Mock config
    import webhook.src.config as config_module
    config_module.config.jwt_secret = secret
    
    with pytest.raises(HTTPException) as exc_info:
        verify_jwt_token(token)
    
    assert exc_info.value.status_code == 401
    assert "expired" in exc_info.value.detail.lower()


def test_invalid_signature():
    """Test JWT token verification with invalid signature"""
    secret = "test-secret-key-at-least-32-chars-long"
    wrong_secret = "wrong-secret-key-different-32-chars"
    
    payload = {
        "iss": "test-service",
        "exp": datetime.now(timezone.utc) + timedelta(hours=1)
    }
    
    # Create token with one secret
    token = jwt.encode(payload, secret, algorithm="HS256")
    
    # Try to verify with different secret
    import webhook.src.config as config_module
    config_module.config.jwt_secret = wrong_secret
    
    with pytest.raises(HTTPException) as exc_info:
        verify_jwt_token(token)
    
    assert exc_info.value.status_code == 401


def test_malformed_token():
    """Test JWT token verification with malformed token"""
    import webhook.src.config as config_module
    config_module.config.jwt_secret = "test-secret-key-at-least-32-chars-long"
    
    with pytest.raises(HTTPException) as exc_info:
        verify_jwt_token("not.a.valid.jwt.token")
    
    assert exc_info.value.status_code == 401


def test_token_without_expiration():
    """Test JWT token without expiration claim"""
    secret = "test-secret-key-at-least-32-chars-long"
    
    payload = {
        "iss": "test-service"
        # No exp claim
    }
    
    token = jwt.encode(payload, secret, algorithm="HS256")
    
    import webhook.src.config as config_module
    config_module.config.jwt_secret = secret
    
    # Should succeed - expiration is optional
    result = verify_jwt_token(token)
    assert result["iss"] == "test-service"
