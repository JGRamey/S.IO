"""Unit tests for utility functions."""

import pytest
import logging
from unittest.mock import patch, MagicMock
from pathlib import Path


class TestLoggingUtils:
    """Unit tests for logging utilities."""
    
    @pytest.mark.unit
    @patch('yggdrasil.utils.logging.settings')
    def test_setup_logging(self, mock_settings):
        """Test logging setup."""
        from yggdrasil.utils.logging import setup_logging
        
        # Mock settings
        mock_settings.logs_dir = Path('/tmp/test_logs')
        mock_settings.log_level = 'DEBUG'
        
        # Test setup_logging function
        logger = setup_logging()
        
        assert logger is not None
        assert isinstance(logger, logging.Logger)
    
    @pytest.mark.unit
    def test_get_logger(self):
        """Test get_logger function."""
        from yggdrasil.utils.logging import get_logger
        
        logger = get_logger('test_logger')
        
        assert logger is not None
        assert isinstance(logger, logging.Logger)
        assert logger.name == 'test_logger'


class TestExceptions:
    """Unit tests for custom exceptions."""
    
    @pytest.mark.unit
    def test_yggdrasil_exception(self):
        """Test base YggdrasilException."""
        from yggdrasil.utils.exceptions import YggdrasilException
        
        with pytest.raises(YggdrasilException):
            raise YggdrasilException("Test exception")
    
    @pytest.mark.unit
    def test_database_connection_error(self):
        """Test DatabaseConnectionError."""
        from yggdrasil.utils.exceptions import DatabaseConnectionError, YggdrasilException
        
        with pytest.raises(DatabaseConnectionError):
            raise DatabaseConnectionError("Database connection failed")
        
        # Test inheritance
        with pytest.raises(YggdrasilException):
            raise DatabaseConnectionError("Database connection failed")
    
    @pytest.mark.unit
    def test_all_custom_exceptions(self):
        """Test all custom exceptions can be instantiated."""
        from yggdrasil.utils.exceptions import (
            YggdrasilException, DatabaseConnectionError, AgentInitializationError,
            ScrapingError, ConfigurationError, MCPServerError, QdrantConnectionError,
            AIModelError, ValidationError
        )
        
        exceptions = [
            YggdrasilException, DatabaseConnectionError, AgentInitializationError,
            ScrapingError, ConfigurationError, MCPServerError, QdrantConnectionError,
            AIModelError, ValidationError
        ]
        
        for exc_class in exceptions:
            exc = exc_class("Test message")
            assert isinstance(exc, Exception)
            assert isinstance(exc, YggdrasilException)
            assert str(exc) == "Test message"
