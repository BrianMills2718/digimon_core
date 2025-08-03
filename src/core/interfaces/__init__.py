"""
Service interfaces package for dependency injection.

Defines abstract interfaces that services must implement,
enabling loose coupling and easy testing through dependency injection.
"""

from .service_interfaces import (
    IdentityServiceInterface,
    ProvenanceServiceInterface, 
    QualityServiceInterface,
    Neo4jServiceInterface
)

__all__ = [
    "IdentityServiceInterface",
    "ProvenanceServiceInterface",
    "QualityServiceInterface", 
    "Neo4jServiceInterface"
]