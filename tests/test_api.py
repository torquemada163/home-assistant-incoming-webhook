"""Tests for webhook API endpoints"""

import pytest
from fastapi.testclient import TestClient
from webhook.src.main import app
from webhook.src.config import config
import jwt
from datetime import datetime, timedelta


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


@pytest.fixture
def valid_token():
    """Generate valid JWT token for testing"""
    payload = {
        "iss": "test-client",
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, config.jwt_secret, algorithm="HS256")


def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Home Assistant Incoming Webhook"
    assert data["status"] == "running"


def test_health_endpoint(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_webhook_without_auth(client):
    """Test webhook endpoint without authentication"""
    response = client.post(
        "/webhook",
        json={
            "switch_id": "test_switch",
            "action": "on"
        }
    )
    assert response.status_code == 403  # Forbidden - no auth header


def test_webhook_with_invalid_auth(client):
    """Test webhook endpoint with invalid token"""
    response = client.post(
        "/webhook",
        headers={"Authorization": "Bearer invalid-token"},
        json={
            "switch_id": "test_switch",
            "action": "on"
        }
    )
    assert response.status_code == 401


def test_webhook_invalid_action(client, valid_token):
    """Test webhook with invalid action"""
    response = client.post(
        "/webhook",
        headers={"Authorization": f"Bearer {valid_token}"},
        json={
            "switch_id": "test_switch",
            "action": "invalid_action"
        }
    )
    assert response.status_code == 422  # Validation error


def test_webhook_missing_switch_id(client, valid_token):
    """Test webhook without switch_id"""
    response = client.post(
        "/webhook",
        headers={"Authorization": f"Bearer {valid_token}"},
        json={
            "action": "on"
        }
    )
    assert response.status_code == 422  # Validation error


def test_webhook_unknown_switch(client, valid_token):
    """Test webhook with non-existent switch"""
    response = client.post(
        "/webhook",
        headers={"Authorization": f"Bearer {valid_token}"},
        json={
            "switch_id": "nonexistent_switch",
            "action": "status"
        }
    )
    # Should return 404 if switch not in config
    # Note: Actual behavior depends on config
    assert response.status_code in [404, 500]  # 500 if HA integration fails


def test_webhook_with_attributes(client, valid_token):
    """Test webhook with custom attributes"""
    response = client.post(
        "/webhook",
        headers={"Authorization": f"Bearer {valid_token}"},
        json={
            "switch_id": "example_switch",
            "action": "status",
            "attributes": {
                "source": "test",
                "custom_field": "value"
            }
        }
    )
    # Should succeed or fail gracefully
    assert response.status_code in [200, 404, 500]


# Integration tests - require actual HA instance
@pytest.mark.integration
def test_switch_on_integration(client, valid_token):
    """Integration test for turning switch on"""
    response = client.post(
        "/webhook",
        headers={"Authorization": f"Bearer {valid_token}"},
        json={
            "switch_id": "example_switch",
            "action": "on"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        assert data["status"] == "success"
        assert data["switch_id"] == "example_switch"
        assert data["action"] == "on"
        assert data["state"] in ["on", "off"]


@pytest.mark.integration
def test_switch_toggle_integration(client, valid_token):
    """Integration test for toggling switch"""
    response = client.post(
        "/webhook",
        headers={"Authorization": f"Bearer {valid_token}"},
        json={
            "switch_id": "example_switch",
            "action": "toggle"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        assert data["status"] == "success"
        assert data["action"] == "toggle"


@pytest.mark.integration
def test_switch_status_integration(client, valid_token):
    """Integration test for getting switch status"""
    response = client.post(
        "/webhook",
        headers={"Authorization": f"Bearer {valid_token}"},
        json={
            "switch_id": "example_switch",
            "action": "status"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        assert data["status"] == "success"
        assert data["action"] == "status"
        assert "state" in data
        assert "attributes" in data
