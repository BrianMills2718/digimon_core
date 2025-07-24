"""
Integration Exceptions

Custom exceptions for integration modules.
"""


class IntegrationError(Exception):
    """Base class for integration errors"""
    pass


class MCPError(IntegrationError):
    """Base class for MCP-related errors"""
    pass


class APIError(IntegrationError):
    """Base class for API integration errors"""
    pass


class RateLimitError(APIError):
    """Rate limit exceeded error"""
    pass


class AuthenticationError(APIError):
    """Authentication failure error"""
    pass


class ServiceUnavailableError(IntegrationError):
    """Service temporarily unavailable"""
    pass


class InvalidFormatError(IntegrationError):
    """Invalid document or data format"""
    pass


class TimeoutError(IntegrationError):
    """Operation timeout error"""
    pass