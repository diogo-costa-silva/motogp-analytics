"""
Unit tests for custom exceptions.
"""

import pytest

from database.exceptions import (
    MotoGPAnalyticsError,
    DatabaseError,
    DatabaseConnectionError,
    DatabaseQueryError,
    ValidationError,
    ResourceNotFoundError,
    raise_if_none,
    raise_if_empty
)


class TestMotoGPAnalyticsError:
    """Test base MotoGPAnalyticsError class."""
    
    def test_basic_exception(self):
        """Test basic exception creation."""
        error = MotoGPAnalyticsError("Test error")
        
        assert str(error) == "Test error"
        assert error.message == "Test error"
        assert error.error_code is None
        assert error.details == {}
    
    def test_exception_with_details(self):
        """Test exception with error code and details."""
        details = {"field": "value", "count": 42}
        error = MotoGPAnalyticsError(
            "Detailed error",
            error_code="TEST_ERROR",
            details=details
        )
        
        assert error.error_code == "TEST_ERROR"
        assert error.details == details
    
    def test_to_dict_conversion(self):
        """Test exception conversion to dictionary."""
        error = MotoGPAnalyticsError(
            "Test message",
            error_code="TEST_CODE",
            details={"key": "value"}
        )
        
        result = error.to_dict()
        expected = {
            "error": "MotoGPAnalyticsError",
            "message": "Test message", 
            "error_code": "TEST_CODE",
            "details": {"key": "value"}
        }
        
        assert result == expected


class TestDatabaseErrors:
    """Test database-specific exceptions."""
    
    def test_database_connection_error(self):
        """Test DatabaseConnectionError."""
        error = DatabaseConnectionError()
        
        assert isinstance(error, DatabaseError)
        assert error.error_code == "DB_CONNECTION_FAILED"
        assert "Failed to connect to database" in error.message
    
    def test_database_query_error_with_context(self):
        """Test DatabaseQueryError with query context."""
        query = "SELECT * FROM riders WHERE id = %s"
        params = (1,)
        
        error = DatabaseQueryError(
            "Query failed",
            query=query,
            params=params
        )
        
        assert error.error_code == "DB_QUERY_FAILED"
        assert error.details["query"] == query
        assert error.details["params"] == params


class TestAPIErrors:
    """Test API-specific exceptions."""
    
    def test_validation_error(self):
        """Test ValidationError with field context."""
        error = ValidationError("Invalid email", field="email")
        
        assert error.status_code == 400
        assert error.error_code == "VALIDATION_FAILED"
        assert error.details["field"] == "email"
    
    def test_resource_not_found_error(self):
        """Test ResourceNotFoundError with resource context."""
        error = ResourceNotFoundError(
            "Rider not found",
            resource_type="rider",
            resource_id=123
        )
        
        assert error.status_code == 404
        assert error.error_code == "RESOURCE_NOT_FOUND"
        assert error.details["resource_type"] == "rider"
        assert error.details["resource_id"] == 123


class TestUtilityFunctions:
    """Test utility functions for error handling."""
    
    def test_raise_if_none_with_none(self):
        """Test raise_if_none raises when value is None."""
        with pytest.raises(ResourceNotFoundError, match="Value not found"):
            raise_if_none(None, "Value not found")
    
    def test_raise_if_none_with_value(self):
        """Test raise_if_none returns value when not None."""
        result = raise_if_none("test_value", "Should not raise")
        assert result == "test_value"
    
    def test_raise_if_empty_with_empty_list(self):
        """Test raise_if_empty raises when collection is empty."""
        with pytest.raises(ResourceNotFoundError, match="No items found"):
            raise_if_empty([], "No items found")
    
    def test_raise_if_empty_with_items(self):
        """Test raise_if_empty returns collection when not empty."""
        items = ["item1", "item2"]
        result = raise_if_empty(items, "Should not raise")
        assert result == items
    
    def test_custom_exception_class(self):
        """Test utility functions with custom exception class."""
        with pytest.raises(ValidationError):
            raise_if_none(None, "Invalid input", ValidationError)


class TestExceptionInheritance:
    """Test exception class inheritance hierarchy."""
    
    def test_database_error_inheritance(self):
        """Test database errors inherit from base classes."""
        error = DatabaseConnectionError()
        
        assert isinstance(error, DatabaseConnectionError)
        assert isinstance(error, DatabaseError)
        assert isinstance(error, MotoGPAnalyticsError)
        assert isinstance(error, Exception)
    
    def test_api_error_inheritance(self):
        """Test API errors inherit from base classes."""
        error = ValidationError("Test validation error")
        
        assert isinstance(error, ValidationError)
        assert isinstance(error, MotoGPAnalyticsError)
        assert isinstance(error, Exception)
        assert hasattr(error, 'status_code')


class TestExceptionChaining:
    """Test exception chaining and context preservation."""
    
    def test_exception_chaining(self):
        """Test exceptions can be chained properly."""
        try:
            try:
                raise ValueError("Original error")
            except ValueError as e:
                raise DatabaseQueryError("Query failed") from e
        except DatabaseQueryError as final_error:
            assert final_error.__cause__ is not None
            assert isinstance(final_error.__cause__, ValueError)
            assert str(final_error.__cause__) == "Original error"