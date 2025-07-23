"""
Pytest configuration and fixtures for Anki-AI backend tests.
"""

import pytest
import asyncio
from typing import Generator, AsyncGenerator
from fastapi.testclient import TestClient
from httpx import AsyncClient
from unittest.mock import Mock, patch

from app.main import app
from app.core.config import settings
from app.models.database import UserCreate, CardCreate, ReviewCreate
from app.core.auth import create_access_token


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client() -> Generator:
    """Create a test client for the FastAPI application."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client for the FastAPI application."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def test_user_data():
    """Test user data for authentication tests."""
    return {
        "email": "test@example.com",
        "password": "testpassword123",
        "username": "testuser"
    }


@pytest.fixture
def test_user_create(test_user_data):
    """Test user creation model."""
    return UserCreate(**test_user_data)


@pytest.fixture
def test_card_data():
    """Test card data for card tests."""
    return {
        "front": "What is the capital of France?",
        "back": "Paris is the capital and largest city of France.",
        "tags": ["geography", "europe"]
    }


@pytest.fixture
def test_card_create(test_card_data):
    """Test card creation model."""
    return CardCreate(**test_card_data)


@pytest.fixture
def test_review_data():
    """Test review data for review tests."""
    return {
        "rating": 4,
        "card_id": "123e4567-e89b-12d3-a456-426614174000"
    }


@pytest.fixture
def test_review_create(test_review_data):
    """Test review creation model."""
    return ReviewCreate(**test_review_data)


@pytest.fixture
def mock_user():
    """Mock user object for testing."""
    user = Mock()
    user.id = "123e4567-e89b-12d3-a456-426614174000"
    user.email = "test@example.com"
    user.username = "testuser"
    return user


@pytest.fixture
def auth_headers(mock_user):
    """Generate authentication headers with a valid JWT token."""
    token = create_access_token(data={"sub": str(mock_user.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def mock_supabase():
    """Mock Supabase client for testing."""
    with patch("app.core.supabase.supabase") as mock_supabase:
        # Mock successful responses
        mock_response = Mock()
        mock_response.data = []
        mock_response.error = None
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
        mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_response
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = mock_response
        mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value = mock_response
        
        yield mock_supabase


@pytest.fixture
def mock_cache():
    """Mock cache for testing."""
    with patch("app.core.cache.cache") as mock_cache:
        mock_cache.get.return_value = None
        mock_cache.set.return_value = True
        mock_cache.delete.return_value = True
        mock_cache.delete_pattern.return_value = True
        mock_cache.get_stats.return_value = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "total_requests": 0,
            "hit_rate": 0.0,
            "size": 0
        }
        yield mock_cache


@pytest.fixture
def mock_rate_limiter():
    """Mock rate limiter for testing."""
    with patch("app.core.rate_limiter.rate_limiter") as mock_limiter:
        mock_limiter.check_rate_limit.return_value = (True, {
            "X-RateLimit-Limit": 100,
            "X-RateLimit-Remaining": 99,
            "X-RateLimit-Reset": 1234567890
        })
        yield mock_limiter


@pytest.fixture
def test_settings():
    """Test settings configuration."""
    with patch("app.core.config.settings") as mock_settings:
        mock_settings.app_name = "Anki-AI Test"
        mock_settings.app_version = "1.0.0"
        mock_settings.debug = True
        mock_settings.log_level = "DEBUG"
        mock_settings.allowed_origins = "http://localhost:3000"
        mock_settings.supabase_url = "https://test.supabase.co"
        mock_settings.supabase_key = "test-key"
        yield mock_settings 