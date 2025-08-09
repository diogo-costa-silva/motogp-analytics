"""
Application Settings and Configuration
======================================
Centralized configuration management with environment-specific overrides.
"""

import os
from functools import lru_cache
from typing import Optional, List
from pydantic import BaseSettings, validator, Field
from enum import Enum


class Environment(str, Enum):
    """Application environment types."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""
    
    host: str = Field(default="localhost", description="Database host")
    port: int = Field(default=5432, description="Database port")
    name: str = Field(default="motogp_analytics", description="Database name")
    user: str = Field(default="postgres", description="Database user")
    password: str = Field(description="Database password")
    
    min_connections: int = Field(default=1, ge=1, description="Minimum pool connections")
    max_connections: int = Field(default=20, ge=1, le=100, description="Maximum pool connections")
    
    connection_timeout: int = Field(default=30, ge=1, description="Connection timeout seconds")
    query_timeout: int = Field(default=300, ge=1, description="Query timeout seconds")
    
    @validator('max_connections')
    def validate_max_connections(cls, v, values):
        if 'min_connections' in values and v < values['min_connections']:
            raise ValueError('max_connections must be >= min_connections')
        return v
    
    class Config:
        env_prefix = "DB_"


class APISettings(BaseSettings):
    """API configuration settings."""
    
    host: str = Field(default="0.0.0.0", description="API host")
    port: int = Field(default=8000, ge=1, le=65535, description="API port")
    workers: int = Field(default=1, ge=1, le=32, description="Number of workers")
    
    allowed_origins: List[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://localhost:8501"], 
        description="CORS allowed origins"
    )
    
    enable_docs: bool = Field(default=True, description="Enable API documentation")
    enable_metrics: bool = Field(default=True, description="Enable metrics endpoint")
    
    # Rate limiting
    rate_limit_enabled: bool = Field(default=True, description="Enable rate limiting")
    rate_limit_requests: int = Field(default=100, ge=1, description="Requests per window")
    rate_limit_window: int = Field(default=60, ge=1, description="Rate limit window seconds")
    
    class Config:
        env_prefix = "API_"


class SecuritySettings(BaseSettings):
    """Security configuration settings."""
    
    secret_key: str = Field(description="Application secret key")
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    jwt_expire_minutes: int = Field(default=30, ge=1, description="JWT expiration minutes")
    
    # Password requirements
    min_password_length: int = Field(default=12, ge=8, description="Minimum password length")
    require_special_chars: bool = Field(default=True, description="Require special characters")
    
    # Session settings
    session_timeout: int = Field(default=3600, ge=300, description="Session timeout seconds")
    
    @validator('secret_key')
    def validate_secret_key(cls, v):
        if len(v) < 32:
            raise ValueError('secret_key must be at least 32 characters long')
        return v
    
    class Config:
        env_prefix = "SECURITY_"


class LoggingSettings(BaseSettings):
    """Logging configuration settings."""
    
    level: str = Field(default="INFO", description="Log level")
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format"
    )
    
    # File logging
    file_enabled: bool = Field(default=True, description="Enable file logging")
    file_path: str = Field(default="logs/motogp.log", description="Log file path")
    max_file_size: int = Field(default=10485760, ge=1048576, description="Max log file size (bytes)")
    backup_count: int = Field(default=5, ge=1, description="Number of backup log files")
    
    # Structured logging
    structured: bool = Field(default=True, description="Use structured logging")
    include_request_id: bool = Field(default=True, description="Include request ID in logs")
    
    @validator('level')
    def validate_log_level(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'level must be one of {valid_levels}')
        return v.upper()
    
    class Config:
        env_prefix = "LOG_"


class Settings(BaseSettings):
    """Main application settings."""
    
    # Application metadata
    name: str = Field(default="MotoGP Analytics", description="Application name")
    version: str = Field(default="1.0.0", description="Application version")
    description: str = Field(
        default="MotoGP Analytics API and Dashboard",
        description="Application description"
    )
    
    # Environment
    environment: Environment = Field(default=Environment.DEVELOPMENT, description="Application environment")
    debug: bool = Field(default=False, description="Debug mode")
    
    # Component settings
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    api: APISettings = Field(default_factory=APISettings)  
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    
    # Data paths
    data_raw_path: str = Field(default="data/raw", description="Raw data directory")
    data_interim_path: str = Field(default="data/interim", description="Interim data directory")
    data_processed_path: str = Field(default="data/processed", description="Processed data directory")
    
    @validator('environment')
    def set_production_defaults(cls, v, values):
        """Set production-safe defaults for production environment."""
        if v == Environment.PRODUCTION:
            # Override development defaults for production
            values['debug'] = False
            if 'api' in values:
                values['api'].enable_docs = False
        return v
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == Environment.DEVELOPMENT
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == Environment.PRODUCTION
    
    @property
    def database_url(self) -> str:
        """Get database connection URL."""
        return (
            f"postgresql://{self.database.user}:{self.database.password}"
            f"@{self.database.host}:{self.database.port}/{self.database.name}"
        )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()


# Convenience functions for common settings
def get_database_settings() -> DatabaseSettings:
    """Get database settings."""
    return get_settings().database


def get_api_settings() -> APISettings:
    """Get API settings."""
    return get_settings().api


def get_security_settings() -> SecuritySettings:
    """Get security settings."""
    return get_settings().security


def get_logging_settings() -> LoggingSettings:
    """Get logging settings."""
    return get_settings().logging