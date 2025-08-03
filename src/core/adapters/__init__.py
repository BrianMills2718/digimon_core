"""
Service Adapters for Dependency Injection

Adapters that wrap existing services to work with the new dependency injection
framework while maintaining backward compatibility.
"""

from .identity_service_adapter import IdentityServiceAdapter

__all__ = [
    "IdentityServiceAdapter"
]