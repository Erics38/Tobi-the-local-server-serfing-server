"""
Pytest configuration and shared fixtures.
"""

import pytest
import os
import sys
from pathlib import Path

# Add parent directory to path so tests can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set env vars before any app module is imported so settings pick them up
os.environ.setdefault("ENVIRONMENT", "testing")
os.environ.setdefault("USE_LOCAL_AI", "false")
os.environ.setdefault("LOG_LEVEL", "ERROR")

# Ensure DB tables exist before any test runs
from app.database import init_db  # noqa: E402
init_db()


@pytest.fixture(scope="session")
def test_env():
    """Set up test environment variables."""
    yield


@pytest.fixture
def mock_session_id():
    """Provide a mock session ID for testing."""
    return "test-session-12345"


@pytest.fixture
def sample_order_items():
    """Provide sample order items for testing."""
    return [
        {"name": "House Smash Burger", "price": 16.00, "quantity": 2},
        {"name": "Truffle Fries", "price": 12.00, "quantity": 1},
    ]


@pytest.fixture
def sample_chat_messages():
    """Provide sample chat messages for testing."""
    return ["hello", "what burgers do you have?", "what do you recommend?", "how much does it cost?"]
