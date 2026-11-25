"""
Automated Unit Tests for TRUVEX Health Check.
Owner: Rounit / Anany
"""

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_health_check_status_code():
    """Verify that GET /api/health returns HTTP 200."""
    response = client.get("/api/health")
    assert response.status_code == 200


def test_health_check_payload_structure():
    """Verify the JSON schema of GET /api/health."""
    response = client.get("/api/health")
    data = response.json()
    assert data["status"] == "healthy"
    assert data["app"] == "TRUVEX"
    assert "version" in data
    assert "timestamp" in data
    assert "environment" in data


def test_landing_page_serves_html():
    """Verify that GET / returns the HTML landing page."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert "TRUVEX" in response.text
