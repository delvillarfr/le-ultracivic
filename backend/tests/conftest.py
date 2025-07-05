"""Test configuration and fixtures."""

import os
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

# Set test environment before importing app
os.environ.update(
    {
        "DATABASE_URL": "postgresql+asyncpg://test:test@localhost:5432/test",
        "DEBUG": "true",
        "ALCHEMY_API_KEY": "test_key",
        "ALCHEMY_SEPOLIA_URL": "https://eth-sepolia.g.alchemy.com/v2/test_key",
        "THIRDWEB_SECRET_KEY": "test_key",
        "TREASURY_WALLET_ADDRESS": "0x742d35cc6634c0532925a3b8d11d2d7d2ae30b2b",
        "PR_TOKEN_CONTRACT_ADDRESS": "0x742d35cc6634c0532925a3b8d11d2d7d2ae30b2b",
        "RESEND_API_KEY": "test_key",
        "ALERT_EMAIL": "test@example.com",
        "FRONTEND_URL": "http://localhost:3000",
        "RATE_LIMIT_REQUESTS": "100",
    }
)

from app.database import get_session
from app.main import app


# Mock database session for testing
@pytest.fixture
def mock_session():
    """Mock database session."""
    session = AsyncMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    return session


# Override database dependency
def get_mock_session():
    """Override database session dependency."""
    session = AsyncMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    return session


@pytest.fixture
def client(mock_session):
    """FastAPI test client with mocked dependencies."""
    app.dependency_overrides[get_session] = lambda: mock_session

    # Disable rate limiting for tests
    from app.middleware.rate_limit import limiter

    app.state.limiter = None

    with TestClient(app) as test_client:
        yield test_client

    # Cleanup
    app.dependency_overrides.clear()
    app.state.limiter = limiter


@pytest.fixture
def sample_retirement_request():
    """Sample retirement request data."""
    return {
        "num_allowances": 5,
        "message": "Test retirement message",
        "wallet": "0x742d35cc6634c0532925a3b8d11d2d7d2ae30b2b",
    }


@pytest.fixture
def sample_confirm_request():
    """Sample payment confirmation request data."""
    return {
        "order_id": "550e8400-e29b-41d4-a716-446655440000",
        "tx_hash": "0x1234567890123456789012345678901234567890123456789012345678901234",
    }
