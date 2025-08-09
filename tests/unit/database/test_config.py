"""
Unit tests for configuration management.
"""

import pytest
import os
from unittest.mock import patch

from database.config.settings import Settings, Environment, get_settings
from database.exceptions import ConfigurationError


class TestSettings:
    """Test Settings configuration class."""
    
    def test_default_settings(self):
        """Test default settings are reasonable."""
        settings = Settings()
        
        assert settings.name == "MotoGP Analytics"
        assert settings.version == "1.0.0"
        assert settings.environment == Environment.DEVELOPMENT
        assert settings.database.host == "localhost"
        assert settings.database.port == 5432
        assert settings.api.port == 8000
    
    def test_environment_from_env_var(self):
        """Test environment is set from environment variable."""
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}):
            settings = Settings()
            assert settings.environment == Environment.PRODUCTION
            assert not settings.debug  # Should be False in production
    
    def test_database_url_construction(self):
        """Test database URL is constructed correctly."""
        with patch.dict(os.environ, {
            "DB_HOST": "test-host",
            "DB_PORT": "5433", 
            "DB_NAME": "test_db",
            "DB_USER": "test_user",
            "DB_PASSWORD": "test_pass"
        }):
            settings = Settings()
            expected = "postgresql://test_user:test_pass@test-host:5433/test_db"
            assert settings.database_url == expected
    
    def test_production_security_defaults(self):
        """Test production environment sets secure defaults."""
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}):
            settings = Settings()
            
            assert settings.environment == Environment.PRODUCTION
            assert not settings.is_development
            assert settings.is_production
            assert not settings.api.enable_docs  # Docs disabled in production
    
    def test_validation_errors(self):
        """Test validation errors are raised for invalid config."""
        with patch.dict(os.environ, {"SECURITY_SECRET_KEY": "too_short"}):
            with pytest.raises(ValueError, match="secret_key must be at least 32 characters"):
                Settings()
    
    def test_get_settings_caching(self):
        """Test get_settings returns cached instance."""
        # Clear any existing cache
        get_settings.cache_clear()
        
        settings1 = get_settings()
        settings2 = get_settings() 
        
        assert settings1 is settings2  # Same instance due to caching


class TestDatabaseSettings:
    """Test DatabaseSettings configuration."""
    
    def test_connection_pool_validation(self):
        """Test connection pool settings validation."""
        with patch.dict(os.environ, {
            "DB_MIN_CONNECTIONS": "10",
            "DB_MAX_CONNECTIONS": "5"  # Invalid: less than min
        }):
            with pytest.raises(ValueError, match="max_connections must be >= min_connections"):
                Settings()
    
    def test_default_pool_settings(self):
        """Test default connection pool settings."""
        settings = Settings()
        
        assert settings.database.min_connections == 1
        assert settings.database.max_connections == 20
        assert settings.database.connection_timeout == 30


class TestAPISettings:
    """Test APISettings configuration."""
    
    def test_cors_origins_parsing(self):
        """Test CORS origins are parsed correctly."""
        with patch.dict(os.environ, {
            "API_ALLOWED_ORIGINS": "http://localhost:3000,https://example.com"
        }):
            settings = Settings()
            expected = ["http://localhost:3000", "https://example.com"]
            assert settings.api.allowed_origins == expected
    
    def test_rate_limiting_settings(self):
        """Test rate limiting configuration."""
        settings = Settings()
        
        assert settings.api.rate_limit_enabled is True
        assert settings.api.rate_limit_requests == 100
        assert settings.api.rate_limit_window == 60


class TestSecuritySettings:
    """Test SecuritySettings configuration."""
    
    def test_secret_key_validation(self):
        """Test secret key length validation."""
        with patch.dict(os.environ, {"SECURITY_SECRET_KEY": "x" * 31}):  # Too short
            with pytest.raises(ValueError):
                Settings()
        
        # Valid length should work
        with patch.dict(os.environ, {"SECURITY_SECRET_KEY": "x" * 32}):
            settings = Settings()
            assert len(settings.security.secret_key) == 32
    
    def test_jwt_settings(self):
        """Test JWT configuration defaults."""
        with patch.dict(os.environ, {"SECURITY_SECRET_KEY": "x" * 32}):
            settings = Settings()
            
            assert settings.security.jwt_algorithm == "HS256"
            assert settings.security.jwt_expire_minutes == 30


class TestLoggingSettings:
    """Test LoggingSettings configuration."""
    
    def test_log_level_validation(self):
        """Test log level validation."""
        with patch.dict(os.environ, {"LOG_LEVEL": "INVALID"}):
            with pytest.raises(ValueError, match="level must be one of"):
                Settings()
    
    def test_valid_log_levels(self):
        """Test all valid log levels are accepted."""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        
        for level in valid_levels:
            with patch.dict(os.environ, {"LOG_LEVEL": level.lower()}):
                settings = Settings()
                assert settings.logging.level == level.upper()
    
    def test_structured_logging_defaults(self):
        """Test structured logging is enabled by default."""
        settings = Settings()
        
        assert settings.logging.structured is True
        assert settings.logging.include_request_id is True


@pytest.mark.integration 
class TestSettingsIntegration:
    """Integration tests for settings with real environment."""
    
    def test_settings_from_env_file(self, temp_data_dir):
        """Test settings can be loaded from .env file."""
        env_file = temp_data_dir / ".env"
        env_file.write_text(
            "DB_HOST=env-host\n"
            "DB_PORT=5434\n"
            "SECURITY_SECRET_KEY=test_secret_key_with_minimum_32_characters\n"
        )
        
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings(_env_file=str(env_file))
            
            assert settings.database.host == "env-host"
            assert settings.database.port == 5434