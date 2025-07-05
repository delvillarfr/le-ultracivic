"""Simple smoke tests for hackathon."""

from fastapi.testclient import TestClient

# Import app after setting environment
from tests.conftest import app


def test_health_endpoint_simple():
    """Test health endpoint works."""
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


def test_retirement_endpoint_validation():
    """Test retirement endpoint validates input."""
    with TestClient(app) as client:
        # Test invalid wallet
        response = client.post(
            "/api/retirements/",
            json={"num_allowances": 5, "message": "test", "wallet": "invalid"},
        )
        assert response.status_code == 422


def test_retirement_endpoint_missing_fields():
    """Test retirement endpoint requires fields."""
    with TestClient(app) as client:
        response = client.post("/api/retirements/", json={})
        assert response.status_code == 422


def test_order_status_endpoint_format():
    """Test order status endpoint validates UUID format."""
    with TestClient(app) as client:
        response = client.get("/api/retirements/status/invalid-uuid")
        assert response.status_code == 422


def test_api_endpoints_exist():
    """Test all expected endpoints are available."""
    with TestClient(app) as client:
        # Health endpoint
        response = client.get("/health")
        assert response.status_code == 200

        # Retirement endpoints return validation errors (not 404)
        response = client.post("/api/retirements/", json={})
        assert response.status_code == 422  # Not 404

        response = client.post("/api/retirements/confirm", json={})
        assert response.status_code == 422  # Not 404
