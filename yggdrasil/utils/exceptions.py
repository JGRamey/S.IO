"""Custom exceptions for the Yggdrasil project."""


class YggdrasilException(Exception):
    """Base exception for Yggdrasil application."""
    pass


class DatabaseConnectionError(YggdrasilException):
    """Database connection failed."""
    pass


class AgentInitializationError(YggdrasilException):
    """Agent failed to initialize."""
    pass


class ScrapingError(YggdrasilException):
    """Scraping operation failed."""
    pass


class ConfigurationError(YggdrasilException):
    """Configuration error."""
    pass


class MCPServerError(YggdrasilException):
    """MCP server operation failed."""
    pass


class QdrantConnectionError(YggdrasilException):
    """Qdrant vector database connection failed."""
    pass


class AIModelError(YggdrasilException):
    """AI model operation failed."""
    pass


class ValidationError(YggdrasilException):
    """Data validation failed."""
    pass
