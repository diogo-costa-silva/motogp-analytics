"""
Global test configuration and fixtures for MotoGP Analytics.
"""

import pytest
from typing import Generator, Dict, Any
from unittest.mock import Mock, patch
import tempfile
import os
from pathlib import Path

from database.config.settings import Settings, Environment
from database.api.database import DatabaseManager
from database.exceptions import DatabaseConnectionError


# =============================================================================
# CONFIGURATION FIXTURES
# =============================================================================

@pytest.fixture(scope="session")
def test_settings() -> Settings:
    """Provide test-specific settings."""
    # Override settings for testing
    test_env_vars = {
        "ENVIRONMENT": "testing",
        "DB_HOST": "localhost",
        "DB_PORT": "5432", 
        "DB_NAME": "motogp_test",
        "DB_USER": "test_user",
        "DB_PASSWORD": "test_password",
        "SECURITY_SECRET_KEY": "test_secret_key_with_minimum_32_characters_for_security",
        "API_ALLOWED_ORIGINS": "http://localhost:3000,http://localhost:8501",
        "LOG_LEVEL": "DEBUG",
    }
    
    with patch.dict(os.environ, test_env_vars):
        return Settings()


@pytest.fixture(scope="session") 
def temp_data_dir() -> Generator[Path, None, None]:
    """Provide temporary directory for test data."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


# =============================================================================
# DATABASE FIXTURES
# =============================================================================

@pytest.fixture
def mock_db_connection():
    """Mock database connection for unit tests."""
    mock_conn = Mock()
    mock_cursor = Mock()
    mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
    mock_conn.cursor.return_value.__exit__ = Mock(return_value=None)
    return mock_conn


@pytest.fixture
def mock_database_manager(mock_db_connection):
    """Mock DatabaseManager for testing."""
    with patch('database.api.database.DatabaseManager') as mock_manager:
        instance = mock_manager.return_value
        instance.get_connection.return_value.__enter__ = Mock(return_value=mock_db_connection)
        instance.get_connection.return_value.__exit__ = Mock(return_value=None)
        instance.test_connection.return_value = True
        yield instance


@pytest.fixture
def database_manager_with_real_connection(test_settings):
    """Database manager with real connection (for integration tests)."""
    # Only create real connections in integration tests
    if pytest.current_pytest_config.getoption("--integration", default=False):
        db_manager = DatabaseManager(
            min_connections=1,
            max_connections=2
        )
        try:
            if db_manager.connect():
                yield db_manager
            else:
                pytest.skip("Database not available for integration tests")
        finally:
            db_manager.disconnect()
    else:
        pytest.skip("Integration test fixture requires --integration flag")


# =============================================================================
# API FIXTURES
# =============================================================================

@pytest.fixture
def mock_api_client():
    """Mock API client for testing."""
    with patch('apps.streamlit_demo.utils.api_client.MotoGPAPIClient') as mock_client:
        instance = mock_client.return_value
        instance.health_check.return_value = True
        instance.get_executive_dashboard.return_value = {
            'total_active_riders': 100,
            'total_active_circuits': 20,
            'countries_represented': 30,
            'most_wins_rider': 'Test Rider'
        }
        yield instance


# =============================================================================
# DATA FIXTURES
# =============================================================================

@pytest.fixture
def sample_rider_data() -> Dict[str, Any]:
    """Sample rider data for testing."""
    return {
        'rider_id': 1,
        'rider_name': 'Test Rider',
        'rider_name_clean': 'Test Rider',
        'country_name': 'Test Country',
        'country_code': 'TC',
        'total_races': 100,
        'total_wins': 25,
        'total_podiums': 50,
        'win_percentage': 25.0,
        'career_status': 'Active'
    }


@pytest.fixture
def sample_circuit_data() -> Dict[str, Any]:
    """Sample circuit data for testing."""
    return {
        'circuit_id': 1,
        'circuit_name': 'Test Circuit',
        'circuit_name_clean': 'Test Circuit',
        'country_name': 'Test Country',
        'country_code': 'TC',
        'total_events_hosted': 20,
        'unique_winners': 10,
        'home_win_percentage': 15.0
    }


@pytest.fixture
def sample_dashboard_data() -> Dict[str, Any]:
    """Sample dashboard data for testing."""
    return {
        'total_active_riders': 180,
        'total_active_circuits': 23,
        'countries_represented': 35,
        'total_race_results': 12500,
        'most_wins_rider': 'Valentino Rossi',
        'most_wins_count': 89,
        'most_successful_constructor': 'Honda',
        'most_championships_count': 25
    }


# =============================================================================
# ERROR SIMULATION FIXTURES
# =============================================================================

@pytest.fixture
def database_connection_error():
    """Simulate database connection error."""
    def _raise_error(*args, **kwargs):
        raise DatabaseConnectionError("Test database connection failed")
    return _raise_error


@pytest.fixture
def mock_failing_database():
    """Mock database that fails connections."""
    with patch('database.api.database.DatabaseManager') as mock_manager:
        instance = mock_manager.return_value
        instance.connect.return_value = False
        instance.test_connection.return_value = False
        yield instance


# =============================================================================
# PYTEST CONFIGURATION
# =============================================================================

def pytest_addoption(parser):
    """Add custom pytest command line options."""
    parser.addoption(
        "--integration",
        action="store_true", 
        default=False,
        help="Run integration tests that require database connection"
    )
    parser.addoption(
        "--slow",
        action="store_true",
        default=False, 
        help="Run slow tests that may take several seconds"
    )


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "unit: mark test as unit test")
    config.addinivalue_line("markers", "smoke: mark test as smoke test")


def pytest_collection_modifyitems(config, items):
    """Modify test collection based on command line options."""
    # Skip integration tests unless --integration flag is provided
    if not config.getoption("--integration"):
        skip_integration = pytest.mark.skip(reason="need --integration option to run")
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip_integration)
    
    # Skip slow tests unless --slow flag is provided
    if not config.getoption("--slow"):
        skip_slow = pytest.mark.skip(reason="need --slow option to run")  
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)


# Store pytest config globally for fixtures that need it
@pytest.fixture(scope="session", autouse=True)
def store_pytest_config(request):
    """Store pytest config globally."""
    pytest.current_pytest_config = request.config