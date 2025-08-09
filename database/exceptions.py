"""
Custom Exceptions for MotoGP Analytics
======================================
Specific exception classes for better error handling and debugging.
"""

from typing import Optional, Any, Dict


class MotoGPAnalyticsError(Exception):
    """Base exception for MotoGP Analytics application."""
    
    def __init__(
        self, 
        message: str, 
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses."""
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details
        }


# Database Exceptions
class DatabaseError(MotoGPAnalyticsError):
    """Base exception for database-related errors."""
    pass


class DatabaseConnectionError(DatabaseError):
    """Exception raised when database connection fails."""
    
    def __init__(self, message: str = "Failed to connect to database", **kwargs):
        super().__init__(message, error_code="DB_CONNECTION_FAILED", **kwargs)


class DatabaseQueryError(DatabaseError):
    """Exception raised when database query fails."""
    
    def __init__(
        self, 
        message: str, 
        query: Optional[str] = None, 
        params: Optional[tuple] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if query:
            details['query'] = query
        if params:
            details['params'] = params
        kwargs['details'] = details
        
        super().__init__(message, error_code="DB_QUERY_FAILED", **kwargs)


class DatabasePoolExhaustedError(DatabaseError):
    """Exception raised when database connection pool is exhausted."""
    
    def __init__(self, message: str = "Database connection pool exhausted", **kwargs):
        super().__init__(message, error_code="DB_POOL_EXHAUSTED", **kwargs)


class DatabaseTransactionError(DatabaseError):
    """Exception raised when database transaction fails."""
    
    def __init__(self, message: str = "Database transaction failed", **kwargs):
        super().__init__(message, error_code="DB_TRANSACTION_FAILED", **kwargs)


# API Exceptions
class APIError(MotoGPAnalyticsError):
    """Base exception for API-related errors."""
    
    def __init__(self, message: str, status_code: int = 500, **kwargs):
        super().__init__(message, **kwargs)
        self.status_code = status_code


class ValidationError(APIError):
    """Exception raised when input validation fails."""
    
    def __init__(self, message: str, field: Optional[str] = None, **kwargs):
        details = kwargs.get('details', {})
        if field:
            details['field'] = field
        kwargs['details'] = details
        
        super().__init__(
            message, 
            status_code=400, 
            error_code="VALIDATION_FAILED",
            **kwargs
        )


class AuthenticationError(APIError):
    """Exception raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(
            message, 
            status_code=401, 
            error_code="AUTHENTICATION_FAILED",
            **kwargs
        )


class AuthorizationError(APIError):
    """Exception raised when authorization fails."""
    
    def __init__(self, message: str = "Access forbidden", **kwargs):
        super().__init__(
            message, 
            status_code=403, 
            error_code="AUTHORIZATION_FAILED",
            **kwargs
        )


class ResourceNotFoundError(APIError):
    """Exception raised when requested resource is not found."""
    
    def __init__(
        self, 
        message: str = "Resource not found", 
        resource_type: Optional[str] = None,
        resource_id: Optional[Any] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if resource_type:
            details['resource_type'] = resource_type
        if resource_id:
            details['resource_id'] = resource_id
        kwargs['details'] = details
        
        super().__init__(
            message, 
            status_code=404, 
            error_code="RESOURCE_NOT_FOUND",
            **kwargs
        )


class RateLimitExceededError(APIError):
    """Exception raised when rate limit is exceeded."""
    
    def __init__(
        self, 
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if retry_after:
            details['retry_after'] = retry_after
        kwargs['details'] = details
        
        super().__init__(
            message, 
            status_code=429, 
            error_code="RATE_LIMIT_EXCEEDED",
            **kwargs
        )


# Data Processing Exceptions
class DataProcessingError(MotoGPAnalyticsError):
    """Base exception for data processing errors."""
    pass


class DataValidationError(DataProcessingError):
    """Exception raised when data validation fails."""
    
    def __init__(
        self, 
        message: str, 
        dataset: Optional[str] = None,
        row: Optional[int] = None,
        column: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if dataset:
            details['dataset'] = dataset
        if row:
            details['row'] = row
        if column:
            details['column'] = column
        kwargs['details'] = details
        
        super().__init__(message, error_code="DATA_VALIDATION_FAILED", **kwargs)


class DataIntegrityError(DataProcessingError):
    """Exception raised when data integrity constraints are violated."""
    
    def __init__(self, message: str, constraint: Optional[str] = None, **kwargs):
        details = kwargs.get('details', {})
        if constraint:
            details['constraint'] = constraint
        kwargs['details'] = details
        
        super().__init__(message, error_code="DATA_INTEGRITY_FAILED", **kwargs)


class DataTransformationError(DataProcessingError):
    """Exception raised when data transformation fails."""
    
    def __init__(
        self, 
        message: str, 
        transformation: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if transformation:
            details['transformation'] = transformation
        kwargs['details'] = details
        
        super().__init__(message, error_code="DATA_TRANSFORMATION_FAILED", **kwargs)


# Configuration Exceptions
class ConfigurationError(MotoGPAnalyticsError):
    """Exception raised when configuration is invalid."""
    
    def __init__(
        self, 
        message: str, 
        setting: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if setting:
            details['setting'] = setting
        kwargs['details'] = details
        
        super().__init__(message, error_code="CONFIGURATION_ERROR", **kwargs)


class EnvironmentError(ConfigurationError):
    """Exception raised when environment configuration is invalid."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, error_code="ENVIRONMENT_ERROR", **kwargs)


# External Service Exceptions  
class ExternalServiceError(MotoGPAnalyticsError):
    """Exception raised when external service call fails."""
    
    def __init__(
        self, 
        message: str, 
        service: Optional[str] = None,
        status_code: Optional[int] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if service:
            details['service'] = service
        if status_code:
            details['status_code'] = status_code
        kwargs['details'] = details
        
        super().__init__(message, error_code="EXTERNAL_SERVICE_ERROR", **kwargs)


# Convenience functions for common error patterns
def raise_if_none(value: Any, message: str, exception_class=ResourceNotFoundError):
    """Raise exception if value is None."""
    if value is None:
        raise exception_class(message)
    return value


def raise_if_empty(collection, message: str, exception_class=ResourceNotFoundError):
    """Raise exception if collection is empty."""
    if not collection:
        raise exception_class(message)
    return collection