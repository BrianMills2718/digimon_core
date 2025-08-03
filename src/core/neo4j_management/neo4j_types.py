"""
Neo4j Types and Configuration

Core types, enums, and configuration for Neo4j management components.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime


class ConnectionStatus(Enum):
    """Connection status enumeration."""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    ERROR = "error"
    RETRY = "retry"


class ContainerStatus(Enum):
    """Docker container status enumeration."""
    RUNNING = "running"
    STOPPED = "stopped"
    STARTING = "starting"
    ERROR = "error"
    NOT_FOUND = "not_found"


@dataclass
class Neo4jConfig:
    """Neo4j configuration settings."""
    host: str
    port: int
    username: str
    password: str
    bolt_uri: str
    container_name: str = "neo4j-graphrag"
    max_retries: int = 3
    retry_delay: float = 1.0
    connection_timeout: int = 30
    max_connection_lifetime: int = 3600
    max_connection_pool_size: int = 10
    connection_acquisition_timeout: int = 60
    keep_alive: bool = True


@dataclass
class PerformanceMetrics:
    """Performance metrics for Neo4j operations."""
    operation: str
    execution_time: float
    node_count: Optional[int] = None
    relationship_count: Optional[int] = None
    index_count: Optional[int] = None
    memory_usage: Optional[int] = None
    query_complexity: Optional[str] = None
    timestamp: Optional[datetime] = None


@dataclass
class ConnectionInfo:
    """Connection information and status."""
    status: ConnectionStatus
    connected_at: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    connection_count: int = 0
    error_message: Optional[str] = None
    performance_stats: Optional[Dict[str, Any]] = None


@dataclass
class ContainerInfo:
    """Docker container information."""
    status: ContainerStatus
    container_id: Optional[str] = None
    created_at: Optional[datetime] = None
    port_mapping: Optional[Dict[str, int]] = None
    error_message: Optional[str] = None


class Neo4jError(Exception):
    """Base exception for Neo4j operations."""
    pass


class ConnectionError(Neo4jError):
    """Connection-related errors."""
    pass


class ContainerError(Neo4jError):
    """Container-related errors."""
    pass


class QueryError(Neo4jError):
    """Query execution errors."""
    pass


class ValidationError(Neo4jError):
    """Input validation errors."""
    pass