"""Pytest configuration and fixtures."""

import pytest
import asyncio
from unittest.mock import MagicMock


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client for testing."""
    mock_client = MagicMock()
    mock_client.table.return_value.insert.return_value.execute.return_value = MagicMock(
        data=[{"id": "test_id", "created_at": "2023-01-01T00:00:00"}]
    )
    mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
        data=[{"id": "test_id", "status": "completed"}]
    )
    mock_client.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock(
        data=[{"id": "test_id", "status": "updated"}]
    )
    return mock_client


@pytest.fixture
def mock_groq_client():
    """Mock Groq client for testing."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Test response"
    mock_client.chat.completions.create.return_value = mock_response
    return mock_client
