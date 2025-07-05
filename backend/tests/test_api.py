"""Basic API endpoint smoke tests."""

from unittest.mock import MagicMock

import pytest


@pytest.mark.smoke
def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "Ultra Civic API is running"}


@pytest.mark.api
def test_create_retirement_success(client, mock_session, sample_retirement_request):
    """Test successful retirement creation."""
    # Mock successful database response
    mock_result = MagicMock()
    mock_allowances = [MagicMock() for _ in range(5)]
    for allowance in mock_allowances:
        allowance.status = "available"
    mock_result.scalars.return_value.all.return_value = mock_allowances
    mock_session.execute.return_value = mock_result

    response = client.post("/api/retirements/", json=sample_retirement_request)

    assert response.status_code == 200
    data = response.json()
    assert "order_id" in data
    assert data["message"] == "Allowances reserved successfully"


@pytest.mark.api
def test_create_retirement_insufficient_allowances(
    client, mock_session, sample_retirement_request
):
    """Test retirement creation with insufficient allowances."""
    # Mock insufficient allowances
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [
        MagicMock(),
        MagicMock(),
    ]  # Only 2 allowances
    mock_session.execute.return_value = mock_result

    response = client.post("/api/retirements/", json=sample_retirement_request)

    assert response.status_code == 400
    assert "Only 2 allowances available" in response.json()["detail"]


@pytest.mark.api
def test_create_retirement_invalid_wallet(client, sample_retirement_request):
    """Test retirement creation with invalid wallet address."""
    sample_retirement_request["wallet"] = "invalid_wallet"

    response = client.post("/api/retirements/", json=sample_retirement_request)

    assert response.status_code == 422  # Validation error


@pytest.mark.api
def test_confirm_payment_success(client, mock_session, sample_confirm_request):
    """Test successful payment confirmation."""
    # Mock order exists
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [MagicMock()]
    mock_session.execute.return_value = mock_result

    response = client.post("/api/retirements/confirm", json=sample_confirm_request)

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Payment confirmation received"
    assert data["status"] == "processing"


@pytest.mark.api
def test_confirm_payment_order_not_found(client, mock_session, sample_confirm_request):
    """Test payment confirmation for non-existent order."""
    # Mock order doesn't exist
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_session.execute.return_value = mock_result

    response = client.post("/api/retirements/confirm", json=sample_confirm_request)

    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"


@pytest.mark.api
def test_get_order_status_success(client, mock_session):
    """Test successful order status retrieval."""
    order_id = "550e8400-e29b-41d4-a716-446655440000"

    # Mock order exists
    mock_allowance = MagicMock()
    mock_allowance.status = "reserved"
    mock_allowance.message = "Test message"
    mock_allowance.serial_number = "ABC123"

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_allowance]
    mock_session.execute.return_value = mock_result

    response = client.get(f"/api/retirements/status/{order_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["order_id"] == order_id
    assert data["status"] == "pending"
    assert data["message"] == "Test message"


@pytest.mark.api
def test_get_order_status_not_found(client, mock_session):
    """Test order status for non-existent order."""
    order_id = "550e8400-e29b-41d4-a716-446655440000"

    # Mock order doesn't exist
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_session.execute.return_value = mock_result

    response = client.get(f"/api/retirements/status/{order_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"
