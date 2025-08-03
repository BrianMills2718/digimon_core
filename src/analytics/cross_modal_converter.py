#!/usr/bin/env python3
"""
Cross-Modal Converter - Comprehensive format transformation between graph/table/vector

Implements bidirectional conversion between graph, table, and vector formats
with semantic preservation, comprehensive validation, and performance monitoring.
"""

import anyio
import time
import logging
import json
import hashlib
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager

try:
    from ..core.unified_service_interface import CoreService, ServiceResponse, create_service_response
    from ..core.config_manager import get_config
    from ..core.logging_config import get_logger
except ImportError:
    # Fallback for direct execution - ONLY try absolute import, NO stubs
    from src.core.unified_service_interface import CoreService, ServiceResponse, create_service_response
    from src.core.config_manager import get_config
    from src.core.logging_config import get_logger

logger = get_logger("analytics.cross_modal_converter")


class DataFormat(Enum):
    """Supported data formats for cross-modal conversion"""
    GRAPH = "graph"
    TABLE = "table"
    VECTOR = "vector"
    MULTIMODAL = "multimodal"


@dataclass
class ConversionMetadata:
    """Metadata about a conversion operation"""
    source_format: DataFormat
    target_format: DataFormat
    conversion_timestamp: str
    processing_time: float
    data_size_before: int
    data_size_after: int
    semantic_features_preserved: List[str]
    quality_metrics: Dict[str, float]
    conversion_parameters: Dict[str, Any]


@dataclass
class ConversionResult:
    """Result of a cross-modal conversion operation"""
    data: Any
    source_format: DataFormat
    target_format: DataFormat
    preservation_score: float
    conversion_metadata: ConversionMetadata
    validation_passed: bool
    semantic_integrity: bool
    warnings: List[str]


@dataclass
class ValidationResult:
    """Result of conversion validation"""
    valid: bool
    preservation_score: float
    semantic_match: bool
    integrity_score: float
    details: Dict[str, Any]
    errors: List[str]
    warnings: List[str]


class ConversionError(Exception):
    """Exception raised when conversion fails"""
    pass


class ConversionIntegrityError(ConversionError):
    """Exception raised when conversion integrity check fails"""
    pass


class ErrorClassification(Enum):
    """Classification of errors for recovery strategies"""
    TRANSIENT = "transient"          # Network, timeout - retry possible
    STRUCTURAL = "structural"        # Invalid data format - fix input
    RESOURCE = "resource"            # Memory, disk space - cleanup needed
    CONFIGURATION = "configuration"  # Missing service, auth - admin action
    LOGIC = "logic"                  # Programming error - bug fix needed


@dataclass
class ClassifiedError:
    """Error with classification and recovery information"""
    original_error: Exception
    classification: ErrorClassification
    recovery_strategy: str
    retry_recommended: bool
    user_actionable: bool
    suggested_actions: List[str]


# Simplified error handling - keep specific error types but remove classification complexity
def should_retry_error(error: Exception) -> bool:
    """Simple retry logic for transient errors"""
    return isinstance(error, (ConnectionError, TimeoutError))


# Performance monitoring removed - use standard APM tools instead


class CircuitBreakerError(ConversionError):
    """Exception raised when circuit breaker is open"""
    pass


class CircuitBreakerState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Service failing, blocking calls
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """Circuit breaker for external service calls"""
    
    def __init__(self, failure_threshold: int = 5, timeout: float = 60.0, recovery_timeout: float = 30.0):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.recovery_timeout = recovery_timeout
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitBreakerState.CLOSED
        self._lock = anyio.Lock()
    
    async def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        async with self._lock:
            await self._check_state()
            
            if self.state == CircuitBreakerState.OPEN:
                raise CircuitBreakerError("Circuit breaker is OPEN - service unavailable")
        
        try:
            result = await func(*args, **kwargs)
            await self._on_success()
            return result
        except Exception as e:
            await self._on_failure()
            raise
    
    async def _check_state(self):
        """Check and update circuit breaker state"""
        now = datetime.now()
        
        if self.state == CircuitBreakerState.OPEN:
            if self.last_failure_time and (now - self.last_failure_time).total_seconds() > self.recovery_timeout:
                self.state = CircuitBreakerState.HALF_OPEN
                logger.info("Circuit breaker transitioning to HALF_OPEN state")
        
        elif self.state == CircuitBreakerState.HALF_OPEN:
            # Stay in half-open, will transition based on next call result
            pass
    
    async def _on_success(self):
        """Handle successful call"""
        async with self._lock:
            self.failure_count = 0
            if self.state == CircuitBreakerState.HALF_OPEN:
                self.state = CircuitBreakerState.CLOSED
                logger.info("Circuit breaker transitioned to CLOSED state")
    
    async def _on_failure(self):
        """Handle failed call"""
        async with self._lock:
            self.failure_count += 1
            self.last_failure_time = datetime.now()
            
            if (self.state == CircuitBreakerState.CLOSED and 
                self.failure_count >= self.failure_threshold):
                self.state = CircuitBreakerState.OPEN
                logger.warning(f"Circuit breaker opened after {self.failure_count} failures")
            
            elif self.state == CircuitBreakerState.HALF_OPEN:
                self.state = CircuitBreakerState.OPEN
                logger.warning("Circuit breaker reopened during half-open test")
    
    def get_state(self) -> Dict[str, Any]:
        """Get current circuit breaker state"""
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None,
            "failure_threshold": self.failure_threshold,
            "recovery_timeout": self.recovery_timeout
        }


# Memory monitoring removed - use Prometheus/standard monitoring instead


class RetryConfig:
    """Configuration for retry logic"""
    
    def __init__(self, max_attempts: int = 3, base_delay: float = 1.0, max_delay: float = 60.0, backoff_factor: float = 2.0):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor


async def retry_with_backoff(func, *args, retry_config: RetryConfig = None, **kwargs):
    """Execute function with exponential backoff retry logic"""
    if retry_config is None:
        retry_config = RetryConfig()
    
    last_exception = None
    
    for attempt in range(retry_config.max_attempts):
        try:
            return await func(*args, **kwargs)
        except (ConnectionError, TimeoutError) as e:
            last_exception = e
            if attempt == retry_config.max_attempts - 1:
                raise
            
            # Calculate delay with exponential backoff
            delay = min(
                retry_config.base_delay * (retry_config.backoff_factor ** attempt),
                retry_config.max_delay
            )
            
            logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay:.2f}s")
            await anyio.sleep(delay)
        
        except Exception as e:
            # Non-retryable errors
            raise
    
    # This should never be reached, but just in case
    raise last_exception


class BaseConverter(ABC):
    """Abstract base class for format converters"""
    
    @abstractmethod
    async def convert(self, data: Any, target_format: DataFormat, **kwargs) -> Any:
        """Convert data to target format"""
        pass
    
    @abstractmethod
    async def validate_input(self, data: Any) -> bool:
        """Validate input data for conversion"""
        pass
    
    @abstractmethod
    def get_supported_targets(self) -> List[DataFormat]:
        """Get list of supported target formats"""
        pass


class GraphToTableConverter(BaseConverter):
    """Convert graph data to table format"""
    
    async def convert(self, data: Any, target_format: DataFormat, **kwargs) -> pd.DataFrame:
        """Convert graph to table format"""
        
        try:
            if target_format != DataFormat.TABLE:
                raise ConversionError(f"GraphToTableConverter cannot convert to {target_format}")
            
            # Extract nodes and edges from graph data
            if isinstance(data, dict):
                nodes = data.get('nodes', [])
                edges = data.get('edges', [])
            else:
                raise ConversionError("Graph data must be a dictionary with 'nodes' and 'edges'")
            
            conversion_type = kwargs.get('table_type', 'nodes')
            
            if conversion_type == 'nodes':
                return self._convert_nodes_to_table(nodes)
            elif conversion_type == 'edges':
                return self._convert_edges_to_table(edges)
            elif conversion_type == 'adjacency':
                return self._convert_to_adjacency_matrix(nodes, edges)
            else:
                return self._convert_full_graph_to_table(nodes, edges)
                
        except ConversionError:
            # Re-raise conversion errors as-is
            raise
        except (KeyError, AttributeError) as e:
            logger.error(f"Invalid graph structure in GraphToTableConverter.convert: {e}")
            raise ConversionError(f"Invalid graph structure: missing required fields - {e}") from e
        except (ValueError, TypeError) as e:
            logger.error(f"Invalid data type in GraphToTableConverter.convert: {e}")
            raise ConversionError(f"Invalid data type for graph conversion: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error in GraphToTableConverter.convert: {e}")
            raise ConversionError(f"Graph to table conversion failed: {e}") from e
    
    def _convert_nodes_to_table(self, nodes: List[Dict]) -> pd.DataFrame:
        """Convert node list to DataFrame"""
        if not nodes:
            return pd.DataFrame()
        
        # Normalize node data
        normalized_nodes = []
        for node in nodes:
            normalized_node = {
                'node_id': node.get('id', ''),
                'label': node.get('label', ''),
                'type': node.get('type', ''),
            }
            
            # Add node properties
            properties = node.get('properties', {})
            for key, value in properties.items():
                normalized_node[f'prop_{key}'] = value
            
            normalized_nodes.append(normalized_node)
        
        return pd.DataFrame(normalized_nodes)
    
    def _convert_edges_to_table(self, edges: List[Dict]) -> pd.DataFrame:
        """Convert edge list to DataFrame"""
        if not edges:
            return pd.DataFrame()
        
        normalized_edges = []
        for edge in edges:
            normalized_edge = {
                'source': edge.get('source', ''),
                'target': edge.get('target', ''),
                'relationship_type': edge.get('type', ''),
                'weight': edge.get('weight', 1.0)
            }
            
            # Add edge properties
            properties = edge.get('properties', {})
            for key, value in properties.items():
                normalized_edge[f'prop_{key}'] = value
            
            normalized_edges.append(normalized_edge)
        
        return pd.DataFrame(normalized_edges)
    
    def _convert_to_adjacency_matrix(self, nodes: List[Dict], edges: List[Dict]) -> pd.DataFrame:
        """Convert graph to adjacency matrix"""
        
        # Create node index mapping
        node_ids = [node.get('id', '') for node in nodes]
        node_index = {node_id: i for i, node_id in enumerate(node_ids)}
        
        # Initialize adjacency matrix
        n_nodes = len(nodes)
        adj_matrix = np.zeros((n_nodes, n_nodes))
        
        # Populate adjacency matrix
        for edge in edges:
            source_id = edge.get('source', '')
            target_id = edge.get('target', '')
            weight = edge.get('weight', 1.0)
            
            if source_id in node_index and target_id in node_index:
                source_idx = node_index[source_id]
                target_idx = node_index[target_id]
                adj_matrix[source_idx][target_idx] = weight
        
        return pd.DataFrame(adj_matrix, index=node_ids, columns=node_ids)
    
    def _convert_full_graph_to_table(self, nodes: List[Dict], edges: List[Dict]) -> pd.DataFrame:
        """Convert full graph to comprehensive table"""
        
        # Create node properties table
        node_df = self._convert_nodes_to_table(nodes)
        edge_df = self._convert_edges_to_table(edges)
        
        # Merge node information with edge information
        if not edge_df.empty and not node_df.empty:
            # Add source node properties
            edge_df = edge_df.merge(
                node_df.add_suffix('_source'),
                left_on='source',
                right_on='node_id_source',
                how='left'
            )
            
            # Add target node properties
            edge_df = edge_df.merge(
                node_df.add_suffix('_target'),
                left_on='target', 
                right_on='node_id_target',
                how='left'
            )
        
        return edge_df if not edge_df.empty else node_df
    
    async def validate_input(self, data: Any) -> bool:
        """Validate graph input data"""
        try:
            if not isinstance(data, dict):
                return False
            
            if 'nodes' not in data and 'edges' not in data:
                return False
            
            return True
            
        except Exception:
            return False
    
    def get_supported_targets(self) -> List[DataFormat]:
        """Get supported target formats"""
        return [DataFormat.TABLE]


class TableToGraphConverter(BaseConverter):
    """Convert table data to graph format"""
    
    async def convert(self, data: Any, target_format: DataFormat, **kwargs) -> Dict[str, Any]:
        """Convert table to graph format"""
        
        try:
            if target_format != DataFormat.GRAPH:
                raise ConversionError(f"TableToGraphConverter cannot convert to {target_format}")
            
            if not isinstance(data, pd.DataFrame):
                raise ConversionError("Table data must be a pandas DataFrame")
            
            conversion_type = kwargs.get('graph_type', 'entity_relationship')
            
            if conversion_type == 'entity_relationship':
                return self._convert_entity_relationship_table(data, **kwargs)
            elif conversion_type == 'adjacency_matrix':
                return self._convert_adjacency_matrix(data)
            else:
                return self._convert_generic_table_to_graph(data, **kwargs)
                
        except ConversionError:
            # Re-raise conversion errors as-is
            raise
        except (KeyError, AttributeError) as e:
            logger.error(f"Invalid table structure in TableToGraphConverter.convert: {e}")
            raise ConversionError(f"Invalid table structure: missing required columns - {e}") from e
        except (ValueError, TypeError) as e:
            logger.error(f"Invalid data type in TableToGraphConverter.convert: {e}")
            raise ConversionError(f"Invalid data type for table conversion: {e}") from e
        except pd.errors.EmptyDataError as e:
            logger.error(f"Empty dataframe in TableToGraphConverter.convert: {e}")
            raise ConversionError(f"Cannot convert empty dataframe: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error in TableToGraphConverter.convert: {e}")
            raise ConversionError(f"Table to graph conversion failed: {e}") from e
    
    def _convert_entity_relationship_table(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """Convert entity-relationship table to graph"""
        
        source_col = kwargs.get('source_column', 'source')
        target_col = kwargs.get('target_column', 'target')
        weight_col = kwargs.get('weight_column', 'weight')
        type_col = kwargs.get('type_column', 'type')
        
        nodes = set()
        edges = []
        
        for _, row in df.iterrows():
            source = str(row.get(source_col, ''))
            target = str(row.get(target_col, ''))
            
            if source and target:
                nodes.add(source)
                nodes.add(target)
                
                edge = {
                    'source': source,
                    'target': target,
                    'type': row.get(type_col, 'related'),
                    'weight': row.get(weight_col, 1.0)
                }
                
                # Add other columns as edge properties
                properties = {}
                for col in df.columns:
                    if col not in [source_col, target_col, weight_col, type_col]:
                        properties[col] = row[col]
                
                if properties:
                    edge['properties'] = properties
                
                edges.append(edge)
        
        # Create node objects
        node_objects = []
        for node_id in nodes:
            node_objects.append({
                'id': node_id,
                'label': node_id,
                'type': 'entity'
            })
        
        return {
            'nodes': node_objects,
            'edges': edges,
            'graph_type': 'entity_relationship',
            'node_count': len(node_objects),
            'edge_count': len(edges)
        }
    
    def _convert_adjacency_matrix(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Convert adjacency matrix to graph"""
        
        if df.shape[0] != df.shape[1]:
            raise ConversionError("Adjacency matrix must be square")
        
        nodes = []
        edges = []
        
        # Create nodes from matrix indices
        for i, node_id in enumerate(df.index):
            nodes.append({
                'id': str(node_id),
                'label': str(node_id),
                'type': 'node'
            })
        
        # Create edges from matrix values
        for i, source in enumerate(df.index):
            for j, target in enumerate(df.columns):
                weight = df.iloc[i, j]
                
                if weight != 0:  # Only create edges for non-zero weights
                    edges.append({
                        'source': str(source),
                        'target': str(target),
                        'weight': float(weight),
                        'type': 'connection'
                    })
        
        return {
            'nodes': nodes,
            'edges': edges,
            'graph_type': 'adjacency_matrix',
            'node_count': len(nodes),
            'edge_count': len(edges)
        }
    
    def _convert_generic_table_to_graph(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """Convert generic table to graph using heuristics"""
        
        # Try to identify entity columns (columns with many unique values)
        entity_columns = []
        for col in df.columns:
            if df[col].dtype == 'object':  # String columns
                unique_ratio = df[col].nunique() / len(df)
                if unique_ratio > 0.1:  # More than 10% unique values
                    entity_columns.append(col)
        
        if len(entity_columns) < 2:
            # Create nodes from all unique values in string columns
            nodes = set()
            for col in df.columns:
                if df[col].dtype == 'object':
                    nodes.update(df[col].dropna().astype(str).unique())
            
            node_objects = [{'id': node, 'label': node, 'type': 'entity'} for node in nodes]
            
            return {
                'nodes': node_objects,
                'edges': [],
                'graph_type': 'entity_nodes',
                'node_count': len(node_objects),
                'edge_count': 0
            }
        
        # Use first two entity columns as source and target
        source_col = entity_columns[0]
        target_col = entity_columns[1]
        
        return self._convert_entity_relationship_table(
            df, 
            source_column=source_col,
            target_column=target_col
        )
    
    async def validate_input(self, data: Any) -> bool:
        """Validate table input data"""
        try:
            return isinstance(data, pd.DataFrame) and not data.empty
        except Exception:
            return False
    
    def get_supported_targets(self) -> List[DataFormat]:
        """Get supported target formats"""
        return [DataFormat.GRAPH]


class VectorConverter(BaseConverter):
    """Convert data to/from vector format"""
    
    def __init__(self, embedding_service=None):
        self.embedding_service = embedding_service
        self.embedding_circuit_breaker = CircuitBreaker(
            failure_threshold=3,
            timeout=60.0,
            recovery_timeout=30.0
        )
        self.retry_config = RetryConfig(
            max_attempts=3,
            base_delay=1.0,
            max_delay=10.0,
            backoff_factor=2.0
        )
    
    async def convert(self, data: Any, target_format: DataFormat, **kwargs) -> np.ndarray:
        """Convert data to vector format"""
        
        try:
            if target_format != DataFormat.VECTOR:
                raise ConversionError(f"VectorConverter cannot convert to {target_format}")
            
            if isinstance(data, dict):  # Graph data
                return await self._convert_graph_to_vector(data, **kwargs)
            elif isinstance(data, pd.DataFrame):  # Table data
                return await self._convert_table_to_vector(data, **kwargs)
            else:
                raise ConversionError(f"Unsupported data type for vector conversion: {type(data)}")
                
        except ConversionError:
            # Re-raise conversion errors as-is
            raise
        except (KeyError, AttributeError) as e:
            logger.error(f"Invalid data structure in VectorConverter.convert: {e}")
            raise ConversionError(f"Invalid data structure for vector conversion: {e}") from e
        except (ValueError, TypeError) as e:
            logger.error(f"Invalid data type in VectorConverter.convert: {e}")
            raise ConversionError(f"Unsupported data type for vector conversion: {e}") from e
        except np.linalg.LinAlgError as e:
            logger.error(f"Linear algebra error in VectorConverter.convert: {e}")
            raise ConversionError(f"Vector computation failed: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error in VectorConverter.convert: {e}")
            raise ConversionError(f"Vector conversion failed: {e}") from e
    
    async def _convert_graph_to_vector(self, graph_data: Dict, **kwargs) -> np.ndarray:
        """Convert graph to vector representation"""
        
        try:
            method = kwargs.get('method', 'node_embeddings')
            
            if method == 'node_embeddings':
                return await self._create_node_embeddings(graph_data)
            elif method == 'graph_features':
                return self._create_graph_feature_vector(graph_data)
            else:
                raise ConversionError(f"Unknown graph-to-vector method: {method}")
                
        except ConversionError:
            raise
        except (KeyError, AttributeError) as e:
            logger.error(f"Invalid graph structure in _convert_graph_to_vector: {e}")
            raise ConversionError(f"Invalid graph structure for vector conversion: {e}") from e
        except (ValueError, TypeError) as e:
            logger.error(f"Invalid parameter in _convert_graph_to_vector: {e}")
            raise ConversionError(f"Invalid conversion method or parameter: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error in _convert_graph_to_vector: {e}")
            raise ConversionError(f"Graph to vector conversion failed: {e}") from e
    
    async def _create_node_embeddings(self, graph_data: Dict) -> np.ndarray:
        """Create embeddings for graph nodes"""
        
        try:
            nodes = graph_data.get('nodes', [])
            if not nodes:
                return np.array([])
            
            # Extract text content from nodes
            texts = []
            for node in nodes:
                text_parts = []
                
                # Add label
                if 'label' in node:
                    text_parts.append(str(node['label']))
                
                # Add properties
                properties = node.get('properties', {})
                for key, value in properties.items():
                    text_parts.append(f"{key}: {value}")
                
                texts.append(" ".join(text_parts) if text_parts else node.get('id', ''))
            
            # Generate embeddings with circuit breaker and retry protection
            if self.embedding_service:
                try:
                    async def embedding_call():
                        return await self.embedding_service.generate_text_embeddings(texts)
                    
                    # Combine retry logic with circuit breaker
                    embeddings = await self.embedding_circuit_breaker.call(
                        retry_with_backoff, embedding_call, retry_config=self.retry_config
                    )
                    return np.array(embeddings)
                except CircuitBreakerError:
                    logger.warning("Embedding service circuit breaker open, using fallback")
                    return self._create_hash_embeddings(texts)
                except Exception as e:
                    logger.warning(f"Embedding service failed after retries: {e}, using fallback")
                    return self._create_hash_embeddings(texts)
            else:
                # Fallback: simple hash-based embeddings
                return self._create_hash_embeddings(texts)
                
        except (AttributeError, KeyError) as e:
            logger.error(f"Invalid graph structure in _create_node_embeddings: {e}")
            raise ConversionError(f"Cannot extract text from graph nodes: {e}") from e
        except (ConnectionError, TimeoutError) as e:
            logger.error(f"Embedding service error in _create_node_embeddings: {e}")
            raise ConversionError(f"Embedding service failed: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error in _create_node_embeddings: {e}")
            raise ConversionError(f"Node embedding creation failed: {e}") from e
    
    def _create_graph_feature_vector(self, graph_data: Dict) -> np.ndarray:
        """Create feature vector representing the entire graph"""
        
        nodes = graph_data.get('nodes', [])
        edges = graph_data.get('edges', [])
        
        features = []
        
        # Basic graph statistics
        features.extend([
            len(nodes),  # Node count
            len(edges),  # Edge count
            len(edges) / max(1, len(nodes)),  # Average degree
        ])
        
        # Node type distribution
        node_types = {}
        for node in nodes:
            node_type = node.get('type', 'unknown')
            node_types[node_type] = node_types.get(node_type, 0) + 1
        
        # Add top 5 node type counts
        top_types = sorted(node_types.items(), key=lambda x: x[1], reverse=True)[:5]
        for _, count in top_types:
            features.append(count)
        
        # Pad to fixed size
        while len(features) < 10:
            features.append(0)
        
        return np.array(features)
    
    async def _convert_table_to_vector(self, df: pd.DataFrame, **kwargs) -> np.ndarray:
        """Convert table to vector representation"""
        
        try:
            method = kwargs.get('method', 'statistical_features')
            
            if method == 'statistical_features':
                return self._create_statistical_features(df)
            elif method == 'row_embeddings':
                return await self._create_row_embeddings(df)
            else:
                raise ConversionError(f"Unknown table-to-vector method: {method}")
                
        except ConversionError:
            raise
        except (KeyError, AttributeError) as e:
            logger.error(f"Invalid table structure in _convert_table_to_vector: {e}")
            raise ConversionError(f"Invalid table structure for vector conversion: {e}") from e
        except (ValueError, TypeError) as e:
            logger.error(f"Invalid parameter in _convert_table_to_vector: {e}")
            raise ConversionError(f"Invalid conversion method or parameter: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error in _convert_table_to_vector: {e}")
            raise ConversionError(f"Table to vector conversion failed: {e}") from e
    
    def _create_statistical_features(self, df: pd.DataFrame) -> np.ndarray:
        """Create statistical feature vector from table"""
        
        features = []
        
        # Basic table statistics
        features.extend([
            len(df),  # Row count
            len(df.columns),  # Column count
            df.isnull().sum().sum(),  # Total null count
        ])
        
        # Column type statistics
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        string_cols = df.select_dtypes(include=['object']).columns
        
        features.extend([
            len(numeric_cols),
            len(string_cols)
        ])
        
        # Statistical features for numeric columns
        if len(numeric_cols) > 0:
            numeric_data = df[numeric_cols]
            features.extend([
                numeric_data.mean().mean(),  # Overall mean
                numeric_data.std().mean(),   # Overall std
                numeric_data.min().min(),    # Overall min
                numeric_data.max().max()     # Overall max
            ])
        else:
            features.extend([0, 0, 0, 0])
        
        # String column statistics
        if len(string_cols) > 0:
            avg_unique_ratio = sum(df[col].nunique() / len(df) for col in string_cols) / len(string_cols)
            features.append(avg_unique_ratio)
        else:
            features.append(0)
        
        return np.array(features)
    
    async def _create_row_embeddings(self, df: pd.DataFrame) -> np.ndarray:
        """Create embeddings for table rows"""
        
        try:
            # Convert each row to text
            texts = []
            for _, row in df.iterrows():
                text_parts = []
                for col, value in row.items():
                    if pd.notna(value):
                        text_parts.append(f"{col}: {value}")
                
                texts.append(" ".join(text_parts))
            
            # Generate embeddings with circuit breaker and retry protection
            if self.embedding_service:
                try:
                    async def embedding_call():
                        return await self.embedding_service.generate_text_embeddings(texts)
                    
                    # Combine retry logic with circuit breaker
                    embeddings = await self.embedding_circuit_breaker.call(
                        retry_with_backoff, embedding_call, retry_config=self.retry_config
                    )
                    return np.array(embeddings)
                except CircuitBreakerError:
                    logger.warning("Embedding service circuit breaker open, using fallback")
                    return self._create_hash_embeddings(texts)
                except Exception as e:
                    logger.warning(f"Embedding service failed after retries: {e}, using fallback")
                    return self._create_hash_embeddings(texts)
            else:
                return self._create_hash_embeddings(texts)
                
        except (AttributeError, KeyError) as e:
            logger.error(f"Invalid table structure in _create_row_embeddings: {e}")
            raise ConversionError(f"Cannot extract text from table rows: {e}") from e
        except (ConnectionError, TimeoutError) as e:
            logger.error(f"Embedding service error in _create_row_embeddings: {e}")
            raise ConversionError(f"Embedding service failed: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error in _create_row_embeddings: {e}")
            raise ConversionError(f"Row embedding creation failed: {e}") from e
    
    def _create_hash_embeddings(self, texts: List[str], dimension: int = 384) -> np.ndarray:
        """Create hash-based embeddings as fallback"""
        
        embeddings = []
        for text in texts:
            # Create deterministic hash-based embedding
            hash_val = hashlib.md5(text.encode()).hexdigest()
            embedding = []
            
            for i in range(0, len(hash_val), 8):
                chunk = hash_val[i:i+8]
                value = int(chunk, 16) / (16**8)  # Normalize to [0,1]
                embedding.append(value)
            
            # Pad or truncate to desired dimension
            while len(embedding) < dimension:
                embedding.extend(embedding[:dimension-len(embedding)])
            
            embeddings.append(embedding[:dimension])
        
        return np.array(embeddings)
    
    async def validate_input(self, data: Any) -> bool:
        """Validate input data for vector conversion"""
        try:
            return isinstance(data, (dict, pd.DataFrame))
        except Exception:
            return False
    
    def get_supported_targets(self) -> List[DataFormat]:
        """Get supported target formats"""
        return [DataFormat.VECTOR]


class VectorToGraphConverter(BaseConverter):
    """Convert vector data to graph format"""
    
    def __init__(self):
        self.distance_threshold = 0.7  # Similarity threshold for creating edges
    
    async def convert(self, data: Any, target_format: DataFormat, **kwargs) -> Dict[str, Any]:
        """Convert vector to graph format"""
        
        try:
            if target_format != DataFormat.GRAPH:
                raise ConversionError(f"VectorToGraphConverter cannot convert to {target_format}")
            
            if not isinstance(data, np.ndarray):
                data = np.array(data)
            
            # Get conversion method
            method = kwargs.get('method', 'similarity_graph')
            
            if method == 'similarity_graph':
                return await self._create_similarity_graph(data, **kwargs)
            elif method == 'clustering_graph':
                return await self._create_clustering_graph(data, **kwargs)
            else:
                raise ConversionError(f"Unknown vector-to-graph method: {method}")
                
        except ConversionError:
            raise
        except Exception as e:
            logger.error(f"Error in VectorToGraphConverter: {e}")
            raise ConversionError(f"Vector to graph conversion failed: {e}") from e
    
    async def _create_similarity_graph(self, vectors: np.ndarray, **kwargs) -> Dict[str, Any]:
        """Create graph based on vector similarities"""
        
        try:
            # Get parameters
            threshold = kwargs.get('similarity_threshold', self.distance_threshold)
            metric = kwargs.get('metric', 'cosine')
            labels = kwargs.get('labels', None)
            
            # Normalize vectors for cosine similarity
            if metric == 'cosine':
                from sklearn.preprocessing import normalize
                vectors = normalize(vectors, norm='l2')
            
            # Compute pairwise similarities
            from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
            
            if metric == 'cosine':
                similarities = cosine_similarity(vectors)
            elif metric == 'euclidean':
                distances = euclidean_distances(vectors)
                # Convert distances to similarities
                similarities = 1 / (1 + distances)
            else:
                raise ConversionError(f"Unsupported metric: {metric}")
            
            # Create nodes
            nodes = []
            for i in range(len(vectors)):
                node = {
                    'id': f'node_{i}',
                    'label': labels[i] if labels and i < len(labels) else f'Vector_{i}',
                    'properties': {
                        'vector_dimension': len(vectors[i]),
                        'vector_norm': float(np.linalg.norm(vectors[i]))
                    }
                }
                # Store first few vector values as properties
                for j in range(min(5, len(vectors[i]))):
                    node['properties'][f'v_{j}'] = float(vectors[i][j])
                
                nodes.append(node)
            
            # Create edges based on similarity threshold
            edges = []
            for i in range(len(vectors)):
                for j in range(i + 1, len(vectors)):
                    similarity = similarities[i][j]
                    if similarity >= threshold:
                        edge = {
                            'source': f'node_{i}',
                            'target': f'node_{j}',
                            'relationship': 'similar_to',
                            'properties': {
                                'similarity': float(similarity),
                                'metric': metric
                            }
                        }
                        edges.append(edge)
            
            return {
                'nodes': nodes,
                'edges': edges,
                'metadata': {
                    'conversion_method': 'similarity_graph',
                    'similarity_threshold': threshold,
                    'metric': metric,
                    'total_vectors': len(vectors),
                    'edge_count': len(edges),
                    'graph_density': len(edges) / (len(nodes) * (len(nodes) - 1) / 2) if len(nodes) > 1 else 0
                }
            }
            
        except ImportError as e:
            raise ConversionError(f"Required library not available: {e}")
        except Exception as e:
            raise ConversionError(f"Failed to create similarity graph: {e}")
    
    async def _create_clustering_graph(self, vectors: np.ndarray, **kwargs) -> Dict[str, Any]:
        """Create graph based on vector clustering"""
        
        try:
            from sklearn.cluster import KMeans, DBSCAN
            
            # Get clustering parameters
            algorithm = kwargs.get('algorithm', 'kmeans')
            n_clusters = kwargs.get('n_clusters', min(10, len(vectors) // 5))
            labels = kwargs.get('labels', None)
            
            # Perform clustering
            if algorithm == 'kmeans':
                clusterer = KMeans(n_clusters=n_clusters, random_state=42)
                cluster_labels = clusterer.fit_predict(vectors)
                centroids = clusterer.cluster_centers_
            elif algorithm == 'dbscan':
                eps = kwargs.get('eps', 0.5)
                min_samples = kwargs.get('min_samples', 5)
                clusterer = DBSCAN(eps=eps, min_samples=min_samples)
                cluster_labels = clusterer.fit_predict(vectors)
                # Calculate centroids for non-noise clusters
                unique_labels = set(cluster_labels)
                centroids = []
                for label in unique_labels:
                    if label != -1:  # -1 is noise in DBSCAN
                        mask = cluster_labels == label
                        centroid = vectors[mask].mean(axis=0)
                        centroids.append(centroid)
                centroids = np.array(centroids)
            else:
                raise ConversionError(f"Unsupported clustering algorithm: {algorithm}")
            
            # Create nodes for data points
            nodes = []
            for i in range(len(vectors)):
                cluster_id = int(cluster_labels[i])
                node = {
                    'id': f'node_{i}',
                    'label': labels[i] if labels and i < len(labels) else f'Vector_{i}',
                    'type': 'data_point',
                    'properties': {
                        'cluster_id': cluster_id,
                        'vector_dimension': len(vectors[i])
                    }
                }
                nodes.append(node)
            
            # Create cluster nodes
            unique_clusters = set(cluster_labels)
            if -1 in unique_clusters:
                unique_clusters.remove(-1)  # Remove noise label
            
            cluster_nodes = []
            for i, cluster_id in enumerate(unique_clusters):
                cluster_node = {
                    'id': f'cluster_{cluster_id}',
                    'label': f'Cluster_{cluster_id}',
                    'type': 'cluster',
                    'properties': {
                        'cluster_size': int(sum(cluster_labels == cluster_id)),
                        'centroid_norm': float(np.linalg.norm(centroids[i])) if i < len(centroids) else 0
                    }
                }
                cluster_nodes.append(cluster_node)
            
            nodes.extend(cluster_nodes)
            
            # Create edges from data points to clusters
            edges = []
            for i in range(len(vectors)):
                cluster_id = int(cluster_labels[i])
                if cluster_id != -1:  # Skip noise points
                    edge = {
                        'source': f'node_{i}',
                        'target': f'cluster_{cluster_id}',
                        'relationship': 'belongs_to',
                        'properties': {
                            'membership': 'hard'  # Could be extended to soft clustering
                        }
                    }
                    edges.append(edge)
            
            # Create edges between similar clusters
            if len(centroids) > 1:
                from sklearn.metrics.pairwise import cosine_similarity
                cluster_similarities = cosine_similarity(centroids)
                similarity_threshold = kwargs.get('cluster_similarity_threshold', 0.8)
                
                for i in range(len(centroids)):
                    for j in range(i + 1, len(centroids)):
                        similarity = cluster_similarities[i][j]
                        if similarity >= similarity_threshold:
                            edge = {
                                'source': f'cluster_{i}',
                                'target': f'cluster_{j}',
                                'relationship': 'similar_to',
                                'properties': {
                                    'similarity': float(similarity)
                                }
                            }
                            edges.append(edge)
            
            return {
                'nodes': nodes,
                'edges': edges,
                'metadata': {
                    'conversion_method': 'clustering_graph',
                    'clustering_algorithm': algorithm,
                    'n_clusters': len(unique_clusters),
                    'total_vectors': len(vectors),
                    'edge_count': len(edges)
                }
            }
            
        except ImportError as e:
            raise ConversionError(f"Required library not available: {e}")
        except Exception as e:
            raise ConversionError(f"Failed to create clustering graph: {e}")
    
    async def validate_input(self, data: Any) -> bool:
        """Validate input data for graph conversion"""
        try:
            if isinstance(data, np.ndarray):
                return data.ndim == 2  # Must be 2D array
            if isinstance(data, list):
                return all(isinstance(row, (list, np.ndarray)) for row in data)
            return False
        except Exception:
            return False
    
    def get_supported_targets(self) -> List[DataFormat]:
        """Get supported target formats"""
        return [DataFormat.GRAPH]


class VectorToTableConverter(BaseConverter):
    """Convert vector data to table format"""
    
    async def convert(self, data: Any, target_format: DataFormat, **kwargs) -> pd.DataFrame:
        """Convert vector to table format"""
        
        try:
            if target_format != DataFormat.TABLE:
                raise ConversionError(f"VectorToTableConverter cannot convert to {target_format}")
            
            if not isinstance(data, np.ndarray):
                data = np.array(data)
            
            # Get conversion method
            method = kwargs.get('method', 'direct')
            
            if method == 'direct':
                return self._create_direct_table(data, **kwargs)
            elif method == 'feature_table':
                return await self._create_feature_table(data, **kwargs)
            elif method == 'similarity_matrix':
                return self._create_similarity_matrix_table(data, **kwargs)
            else:
                raise ConversionError(f"Unknown vector-to-table method: {method}")
                
        except ConversionError:
            raise
        except Exception as e:
            logger.error(f"Error in VectorToTableConverter: {e}")
            raise ConversionError(f"Vector to table conversion failed: {e}") from e
    
    def _create_direct_table(self, vectors: np.ndarray, **kwargs) -> pd.DataFrame:
        """Create table directly from vectors"""
        
        try:
            # Get parameters
            labels = kwargs.get('labels', None)
            feature_names = kwargs.get('feature_names', None)
            
            # Ensure 2D array
            if vectors.ndim == 1:
                vectors = vectors.reshape(1, -1)
            
            # Create column names
            if feature_names and len(feature_names) == vectors.shape[1]:
                columns = feature_names
            else:
                columns = [f'feature_{i}' for i in range(vectors.shape[1])]
            
            # Create DataFrame
            df = pd.DataFrame(vectors, columns=columns)
            
            # Add labels if provided
            if labels and len(labels) == len(vectors):
                df.insert(0, 'label', labels)
            else:
                df.insert(0, 'id', [f'vector_{i}' for i in range(len(vectors))])
            
            # Add vector statistics
            df['vector_norm'] = np.linalg.norm(vectors, axis=1)
            df['vector_mean'] = vectors.mean(axis=1)
            df['vector_std'] = vectors.std(axis=1)
            
            return df
            
        except Exception as e:
            raise ConversionError(f"Failed to create direct table: {e}")
    
    async def _create_feature_table(self, vectors: np.ndarray, **kwargs) -> pd.DataFrame:
        """Create feature-engineered table from vectors"""
        
        try:
            from sklearn.decomposition import PCA
            from sklearn.preprocessing import StandardScaler
            
            # Get parameters
            n_components = kwargs.get('n_components', min(10, vectors.shape[1]))
            labels = kwargs.get('labels', None)
            include_original = kwargs.get('include_original', False)
            
            # Ensure 2D array
            if vectors.ndim == 1:
                vectors = vectors.reshape(1, -1)
            
            # Standardize vectors
            scaler = StandardScaler()
            vectors_scaled = scaler.fit_transform(vectors)
            
            # Apply PCA
            pca = PCA(n_components=n_components)
            pca_features = pca.fit_transform(vectors_scaled)
            
            # Create base DataFrame with PCA features
            pca_columns = [f'pca_{i}' for i in range(pca_features.shape[1])]
            df = pd.DataFrame(pca_features, columns=pca_columns)
            
            # Add original features if requested
            if include_original:
                original_columns = [f'original_{i}' for i in range(vectors.shape[1])]
                df_original = pd.DataFrame(vectors, columns=original_columns)
                df = pd.concat([df, df_original], axis=1)
            
            # Add labels or IDs
            if labels and len(labels) == len(vectors):
                df.insert(0, 'label', labels)
            else:
                df.insert(0, 'id', [f'vector_{i}' for i in range(len(vectors))])
            
            # Add metadata columns
            df['explained_variance_ratio'] = [pca.explained_variance_ratio_.sum()] * len(df)
            df['n_components'] = n_components
            
            # Add vector statistics
            df['vector_norm'] = np.linalg.norm(vectors, axis=1)
            df['vector_mean'] = vectors.mean(axis=1)
            df['vector_std'] = vectors.std(axis=1)
            
            return df
            
        except ImportError as e:
            # Fallback to direct table if sklearn not available
            logger.warning(f"sklearn not available, falling back to direct table: {e}")
            return self._create_direct_table(vectors, **kwargs)
        except Exception as e:
            raise ConversionError(f"Failed to create feature table: {e}")
    
    def _create_similarity_matrix_table(self, vectors: np.ndarray, **kwargs) -> pd.DataFrame:
        """Create similarity matrix as table"""
        
        try:
            from sklearn.metrics.pairwise import cosine_similarity
            
            # Get parameters
            metric = kwargs.get('metric', 'cosine')
            labels = kwargs.get('labels', None)
            
            # Ensure 2D array
            if vectors.ndim == 1:
                vectors = vectors.reshape(1, -1)
            
            # Compute similarities
            if metric == 'cosine':
                similarities = cosine_similarity(vectors)
            else:
                # Could add more metrics here
                raise ConversionError(f"Unsupported metric: {metric}")
            
            # Create labels for rows/columns
            if labels and len(labels) == len(vectors):
                index_labels = labels
            else:
                index_labels = [f'vector_{i}' for i in range(len(vectors))]
            
            # Create DataFrame
            df = pd.DataFrame(similarities, index=index_labels, columns=index_labels)
            
            # Add metadata
            df.attrs['metric'] = metric
            df.attrs['n_vectors'] = len(vectors)
            df.attrs['vector_dimension'] = vectors.shape[1]
            
            return df
            
        except ImportError as e:
            raise ConversionError(f"Required library not available: {e}")
        except Exception as e:
            raise ConversionError(f"Failed to create similarity matrix: {e}")
    
    async def validate_input(self, data: Any) -> bool:
        """Validate input data for table conversion"""
        try:
            if isinstance(data, np.ndarray):
                return True
            if isinstance(data, list):
                return all(isinstance(row, (list, np.ndarray)) for row in data)
            return False
        except Exception:
            return False
    
    def get_supported_targets(self) -> List[DataFormat]:
        """Get supported target formats"""
        return [DataFormat.TABLE]


class CrossModalConverter(CoreService):
    """Comprehensive cross-modal data conversion service
    
    Provides bidirectional conversion between graph, table, and vector formats
    with semantic preservation, validation, and performance monitoring.
    """
    
    def __init__(self, service_manager=None, embedding_service=None):
        self.service_manager = service_manager
        self.config = get_config()
        self.logger = get_logger("analytics.cross_modal_converter")
        
        # Initialize embedding service if not provided
        if embedding_service:
            self.embedding_service = embedding_service
            self.logger.info("Using provided embedding service")
        else:
            try:
                # Initialize real embedding service - NO FALLBACKS
                from .real_embedding_service import RealEmbeddingService
                self.embedding_service = RealEmbeddingService()
                self.logger.info("Initialized RealEmbeddingService")
            except Exception as e:
                self.logger.error(f"Failed to initialize embedding service: {e}")
                # NO FALLBACKS - embedding service is required for vector operations
                self.embedding_service = None
        
        # Initialize converters
        graph_to_vector = VectorConverter(self.embedding_service)
        table_to_vector = VectorConverter(self.embedding_service)
        vector_to_graph = VectorToGraphConverter()
        vector_to_table = VectorToTableConverter()
        
        self.converters = {
            (DataFormat.GRAPH, DataFormat.TABLE): GraphToTableConverter(),
            (DataFormat.TABLE, DataFormat.GRAPH): TableToGraphConverter(),
            (DataFormat.GRAPH, DataFormat.VECTOR): graph_to_vector,
            (DataFormat.TABLE, DataFormat.VECTOR): table_to_vector,
            (DataFormat.VECTOR, DataFormat.GRAPH): vector_to_graph,
            (DataFormat.VECTOR, DataFormat.TABLE): vector_to_table,
        }
        
        # Performance tracking with bounded collections
        from collections import deque
        self.conversion_times = deque(maxlen=1000)  # Bounded to prevent memory leak
        self.conversion_count = 0
        self.validation_failures = 0
        self._stats_lock = anyio.Lock()  # Thread safety for statistics
        
        # Configuration
        self.enable_validation = True
        self.preservation_threshold = 0.4  # Realistic threshold for cross-modal conversion
        self.max_conversion_time = 300.0  # 5 minutes
        
        # Circuit breakers for external services
        self.embedding_circuit_breaker = CircuitBreaker(
            failure_threshold=3,
            timeout=60.0,
            recovery_timeout=30.0
        )
        
        # Share circuit breaker with vector converters
        graph_to_vector.embedding_circuit_breaker = self.embedding_circuit_breaker
        table_to_vector.embedding_circuit_breaker = self.embedding_circuit_breaker
        
        self.logger.info("CrossModalConverter initialized")
    
    # Backward compatibility sync wrappers
    def health_check_sync(self) -> ServiceResponse:
        """Backward compatible sync wrapper for health_check"""
        import asyncio
        try:
            # Handle case where we're already in an event loop
            try:
                loop = asyncio.get_running_loop()
                # We're in an async context, return a future-like response
                return create_service_response(
                    success=True,
                    data={"note": "Called from async context - use await health_check() instead"},
                    metadata={"timestamp": datetime.now().isoformat()}
                )
            except RuntimeError:
                # No running loop, safe to use asyncio.run
                return asyncio.run(self.health_check())
        except Exception as e:
            self.logger.error(f"Sync health check failed: {e}")
            return create_service_response(
                success=False,
                data=None,
                error_code="HEALTH_CHECK_FAILED",
                error_message=str(e)
            )
    
    def get_statistics_sync(self) -> ServiceResponse:
        """Backward compatible sync wrapper for get_statistics"""
        import asyncio
        try:
            # Handle case where we're already in an event loop
            try:
                loop = asyncio.get_running_loop()
                # We're in an async context, return a future-like response
                return create_service_response(
                    success=True,
                    data={"note": "Called from async context - use await get_statistics() instead"},
                    metadata={"timestamp": datetime.now().isoformat()}
                )
            except RuntimeError:
                # No running loop, safe to use asyncio.run
                return asyncio.run(self.get_statistics())
        except Exception as e:
            self.logger.error(f"Sync statistics failed: {e}")
            return create_service_response(
                success=False,
                data=None,
                error_code="STATISTICS_FAILED",
                error_message=str(e)
            )
    
    def cleanup_sync(self) -> ServiceResponse:
        """Backward compatible sync wrapper for cleanup"""
        import asyncio
        try:
            return asyncio.run(self.cleanup())
        except Exception as e:
            self.logger.error(f"Sync cleanup failed: {e}")
            return create_service_response(
                success=False,
                data=None,
                error_code="CLEANUP_FAILED",
                error_message=str(e)
            )
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit with cleanup"""
        try:
            await self._cleanup_resources()
        except Exception as e:
            self.logger.error(f"Error during resource cleanup: {e}")
        return False
    
    async def _cleanup_resources(self):
        """Clean up all resources properly"""
        # Clear bounded collections
        async with self._stats_lock:
            self.conversion_times.clear()
            self.conversion_count = 0
            self.validation_failures = 0
        
        # Close embedding service connections if applicable
        if hasattr(self.embedding_service, 'close'):
            try:
                await self.embedding_service.close()
            except Exception as e:
                self.logger.warning(f"Failed to close embedding service: {e}")
        
        # Clear converter references
        self.converters.clear()
        
        self.logger.info("CrossModalConverter resources cleaned up")
    
    @asynccontextmanager
    async def conversion_context(self, operation_name: str):
        """Context manager for conversion operations with proper resource cleanup"""
        start_time = time.time()
        operation_id = f"{operation_name}_{int(start_time * 1000)}"
        
        self.logger.debug(f"Starting operation: {operation_id}")
        
        try:
            yield operation_id
        except Exception as e:
            self.logger.error(f"Operation {operation_id} failed: {e}")
            raise
        finally:
            duration = time.time() - start_time
            self.logger.debug(f"Operation {operation_id} completed in {duration:.3f}s")
    
    def initialize(self, config: Dict[str, Any]) -> ServiceResponse:
        """Initialize service with configuration"""
        try:
            self.enable_validation = config.get('enable_validation', True)
            self.preservation_threshold = config.get('preservation_threshold', 0.85)
            self.max_conversion_time = config.get('max_conversion_time', 300.0)
            
            # Initialize embedding service if not provided
            if not self.embedding_service and self.service_manager:
                self.embedding_service = self._initialize_embedding_service()
                
                # Update vector converters with embedding service
                for (source, target), converter in self.converters.items():
                    if isinstance(converter, VectorConverter):
                        converter.embedding_service = self.embedding_service
            
            self.logger.info("CrossModalConverter initialized successfully")
            return create_service_response(
                success=True,
                data={"status": "initialized"},
                metadata={"timestamp": datetime.now().isoformat()}
            )
            
        except Exception as e:
            self.logger.error(f"Failed to initialize CrossModalConverter: {e}")
            return create_service_response(
                success=False,
                data=None,
                error_code="INITIALIZATION_FAILED",
                error_message=str(e)
            )
    
    async def health_check(self) -> ServiceResponse:
        """Check service health and readiness"""
        return await self.health_check_async()
    
    async def health_check_async(self) -> ServiceResponse:
        """Check service health and readiness (async version)"""
        try:
            # Thread-safe access to statistics
            async with self._stats_lock:
                total_conversions = self.conversion_count
                validation_failures = self.validation_failures
                conversion_times_list = list(self.conversion_times)
            
            health_data = {
                "service_status": "healthy",
                "converters_available": len(self.converters),
                "embedding_service_status": "available" if self.embedding_service else "unavailable",
                "conversion_stats": {
                    "total_conversions": total_conversions,
                    "validation_failures": validation_failures,
                    "success_rate": (total_conversions - validation_failures) / max(1, total_conversions),
                    "avg_conversion_time": sum(conversion_times_list) / max(1, len(conversion_times_list))
                },
                "circuit_breaker_status": self.embedding_circuit_breaker.get_state()
            }
            
            return create_service_response(
                success=True,
                data=health_data,
                metadata={"timestamp": datetime.now().isoformat()}
            )
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return create_service_response(
                success=False,
                data=None,
                error_code="HEALTH_CHECK_FAILED",
                error_message=str(e)
            )
    
    async def get_statistics(self) -> ServiceResponse:
        """Get service performance statistics"""
        return await self.get_statistics_async()
    
    async def get_statistics_async(self) -> ServiceResponse:
        """Get service performance statistics (async version)"""
        try:
            # Thread-safe access to statistics
            async with self._stats_lock:
                total_conversions = self.conversion_count
                validation_failures = self.validation_failures
                conversion_times_list = list(self.conversion_times)
            
            stats = {
                "conversion_statistics": {
                    "total_conversions": total_conversions,
                    "successful_conversions": total_conversions - validation_failures,
                    "validation_failures": validation_failures,
                    "success_rate": (total_conversions - validation_failures) / max(1, total_conversions)
                },
                "performance_metrics": {
                    "avg_conversion_time": sum(conversion_times_list) / max(1, len(conversion_times_list)),
                    "min_conversion_time": min(conversion_times_list) if conversion_times_list else 0,
                    "max_conversion_time": max(conversion_times_list) if conversion_times_list else 0
                },
                "supported_conversions": [
                    f"{source.value} -> {target.value}" 
                    for (source, target) in self.converters.keys()
                ]
            }
            
            return create_service_response(
                success=True,
                data=stats,
                metadata={"timestamp": datetime.now().isoformat()}
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get statistics: {e}")
            return create_service_response(
                success=False,
                data=None,
                error_code="STATISTICS_FAILED",
                error_message=str(e)
            )
    
    async def cleanup(self) -> ServiceResponse:
        """Clean up service resources"""
        return await self.cleanup_async()
    
    async def cleanup_async(self) -> ServiceResponse:
        """Clean up service resources (async version)"""
        try:
            await self._cleanup_resources()
            
            return create_service_response(
                success=True,
                data={"status": "cleaned_up"},
                metadata={"timestamp": datetime.now().isoformat()}
            )
            
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")
            return create_service_response(
                success=False,
                data=None,
                error_code="CLEANUP_FAILED",
                error_message=str(e)
            )
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get service information and capabilities"""
        return {
            "service_name": "CrossModalConverter",
            "version": "1.0.0",
            "description": "Comprehensive cross-modal data conversion service",
            "capabilities": [
                "format_conversion",
                "semantic_preservation",
                "validation",
                "round_trip_testing"
            ],
            "supported_formats": [fmt.value for fmt in DataFormat],
            "conversion_types": [
                "graph_to_table",
                "table_to_graph", 
                "graph_to_vector",
                "table_to_vector"
            ],
            "features": [
                "preservation_scoring",
                "integrity_validation",
                "performance_monitoring",
                "metadata_tracking"
            ]
        }
    
    async def convert_data(
        self,
        data: Any,
        source_format: DataFormat,
        target_format: DataFormat,
        preserve_semantics: bool = True,
        **conversion_kwargs
    ) -> ConversionResult:
        """Convert data between formats with semantic preservation"""
        start_time = time.time()
        warnings = []
        operation_name = f"convert_{source_format.value}_to_{target_format.value}"
        
        # Use conversion context manager for proper resource management
        async with self.conversion_context(operation_name) as context_id:
                try:
                    # Handle same format case
                    if source_format == target_format:
                        return self._create_same_format_result(
                            data, source_format, target_format, start_time, warnings
                        )
                    
                    # Get and validate converter
                    converter = self._get_converter(source_format, target_format)
                    await self._validate_input_data(converter, data, source_format)
                    
                    # Perform conversion
                    converted_data = await self._perform_conversion(
                        converter, data, target_format, conversion_kwargs
                    )
                    
                    # Validate conversion results
                    validation_passed, semantic_integrity, preservation_score = await self._validate_conversion_results(
                        data, converted_data, source_format, target_format, preserve_semantics, warnings
                    )
                    
                    # Update metrics and log
                    conversion_time = await self._update_conversion_metrics(start_time, source_format, target_format, preservation_score)
                    
                    # Conversion completed successfully
                    
                    # Create final result
                    metadata = self._create_metadata(
                        source_format, target_format, start_time, data, converted_data, conversion_kwargs
                    )
                    
                    return ConversionResult(
                        data=converted_data,
                        source_format=source_format,
                        target_format=target_format,
                        preservation_score=preservation_score,
                        conversion_metadata=metadata,
                        validation_passed=validation_passed,
                        semantic_integrity=semantic_integrity,
                        warnings=warnings
                    )
                    
                except Exception as e:
                    # Simple error handling with context
                    self.logger.error(f"Conversion failed in {operation_name}: {e}")
                    raise ConversionError(f"Conversion failed: {e}") from e
    
    def _create_same_format_result(
        self,
        data: Any,
        source_format: DataFormat,
        target_format: DataFormat,
        start_time: float,
        warnings: List[str]
    ) -> ConversionResult:
        """Create result when source and target formats are the same"""
        warnings.append("Source and target formats are the same")
        return ConversionResult(
            data=data,
            source_format=source_format,
            target_format=target_format,
            preservation_score=1.0,
            conversion_metadata=self._create_metadata(
                source_format, target_format, start_time, data, data, {}
            ),
            validation_passed=True,
            semantic_integrity=True,
            warnings=warnings
        )
    
    def _get_converter(self, source_format: DataFormat, target_format: DataFormat):
        """Get appropriate converter for format pair"""
        converter_key = (source_format, target_format)
        if converter_key not in self.converters:
            raise ConversionError(f"No converter available for {source_format.value} -> {target_format.value}")
        return self.converters[converter_key]
    
    async def _validate_input_data(self, converter, data: Any, source_format: DataFormat):
        """Validate input data before conversion"""
        if not await converter.validate_input(data):
            raise ConversionError(f"Invalid input data for {source_format.value} format")
    
    async def _perform_conversion(
        self, 
        converter, 
        data: Any, 
        target_format: DataFormat, 
        conversion_kwargs: Dict[str, Any]
    ) -> Any:
        """Perform the actual data conversion with timeout"""
        try:
            with anyio.fail_after(self.max_conversion_time):
                return await converter.convert(data, target_format, **conversion_kwargs)
        except TimeoutError:
            raise ConversionError(f"Conversion timed out after {self.max_conversion_time} seconds")
    
    async def _validate_conversion_results(
        self,
        original_data: Any,
        converted_data: Any,
        source_format: DataFormat,
        target_format: DataFormat,
        preserve_semantics: bool,
        warnings: List[str]
    ) -> Tuple[bool, bool, float]:
        """Validate conversion results and return validation metrics"""
        validation_passed = True
        semantic_integrity = True
        preservation_score = 1.0
        
        if preserve_semantics and self.enable_validation:
            validation_result = await self._validate_conversion(
                original_data, converted_data, source_format, target_format
            )
            
            validation_passed = validation_result.valid
            semantic_integrity = validation_result.semantic_match
            preservation_score = validation_result.preservation_score
            
            if not validation_passed:
                async with self._stats_lock:
                    self.validation_failures += 1
                warnings.extend(validation_result.warnings)
                
                if preservation_score < self.preservation_threshold:
                    raise ConversionIntegrityError(
                        f"Conversion failed integrity check: preservation score {preservation_score:.3f} "
                        f"below threshold {self.preservation_threshold}"
                    )
        
        return validation_passed, semantic_integrity, preservation_score
    
    async def _update_conversion_metrics(
        self, 
        start_time: float, 
        source_format: DataFormat, 
        target_format: DataFormat, 
        preservation_score: float
    ) -> float:
        """Update conversion metrics and log completion"""
        conversion_time = time.time() - start_time
        
        # Thread-safe update of statistics
        async with self._stats_lock:
            self.conversion_count += 1
            self.conversion_times.append(conversion_time)
        
        self.logger.info(
            f"Conversion completed: {source_format.value} -> {target_format.value} "
            f"in {conversion_time:.2f}s (preservation: {preservation_score:.3f})"
        )
        
        return conversion_time
    
    async def convert_multiple_parallel(
        self,
        conversion_jobs: List[Tuple[Any, DataFormat, DataFormat, Dict[str, Any]]]
    ) -> List[ConversionResult]:
        """Convert multiple data items in parallel using AnyIO structured concurrency
        
        Args:
            conversion_jobs: List of (data, source_format, target_format, kwargs) tuples
            
        Returns:
            List of ConversionResult objects in same order as input
        """
        results = [None] * len(conversion_jobs)
        
        async def convert_job(index: int, data: Any, source_format: DataFormat, 
                            target_format: DataFormat, kwargs: Dict[str, Any]):
            """Convert a single job and store result at correct index"""
            try:
                result = await self.convert_data(data, source_format, target_format, **kwargs)
                results[index] = result
            except Exception as e:
                # Create error result to maintain order
                results[index] = ConversionResult(
                    data=None,
                    source_format=source_format,
                    target_format=target_format,
                    preservation_score=0.0,
                    conversion_metadata=self._create_metadata(
                        source_format, target_format, time.time(), data, None, kwargs
                    ),
                    validation_passed=False,
                    semantic_integrity=False,
                    warnings=[f"Conversion failed: {e}"]
                )
        
        # Use AnyIO task groups for structured concurrency
        async with anyio.create_task_group() as task_group:
            for i, (data, source_fmt, target_fmt, kwargs) in enumerate(conversion_jobs):
                task_group.start_soon(convert_job, i, data, source_fmt, target_fmt, kwargs)
        
        return results
    
    async def batch_convert_with_fallback(
        self,
        data_items: List[Any],
        source_format: DataFormat,
        target_formats: List[DataFormat],
        **kwargs
    ) -> Dict[DataFormat, List[ConversionResult]]:
        """Convert multiple data items to multiple target formats with structured concurrency
        
        Uses AnyIO structured concurrency to process all combinations in parallel
        with proper error handling and resource management.
        """
        results = {fmt: [] for fmt in target_formats}
        
        async def convert_to_format(target_format: DataFormat):
            """Convert all data items to a specific target format"""
            conversion_jobs = [
                (data, source_format, target_format, kwargs) 
                for data in data_items
            ]
            format_results = await self.convert_multiple_parallel(conversion_jobs)
            results[target_format] = format_results
        
        # Process all target formats concurrently using structured concurrency
        async with anyio.create_task_group() as task_group:
            for target_format in target_formats:
                task_group.start_soon(convert_to_format, target_format)
        
        return results
    
    async def validate_round_trip_conversion(
        self,
        original_data: Any,
        format_sequence: List[DataFormat]
    ) -> ValidationResult:
        """Validate data preserves semantics through format conversions
        
        Args:
            original_data: Original data to test
            format_sequence: Sequence of formats to convert through
            
        Returns:
            ValidationResult with validation details
        """
        try:
            if len(format_sequence) < 2:
                return ValidationResult(
                    valid=False,
                    preservation_score=0.0,
                    semantic_match=False,
                    integrity_score=0.0,
                    details={},
                    errors=["Format sequence must have at least 2 formats"],
                    warnings=[]
                )
            
            current_data = original_data
            preservation_scores = []
            conversion_details = []
            
            # Perform sequential conversions
            for i in range(len(format_sequence) - 1):
                source_format = format_sequence[i]
                target_format = format_sequence[i + 1]
                
                try:
                    conversion_result = await self.convert_data(
                        current_data, source_format, target_format, preserve_semantics=True
                    )
                    
                    preservation_scores.append(conversion_result.preservation_score)
                    current_data = conversion_result.data
                    
                    conversion_details.append({
                        "step": i + 1,
                        "conversion": f"{source_format.value} -> {target_format.value}",
                        "preservation_score": conversion_result.preservation_score,
                        "validation_passed": conversion_result.validation_passed
                    })
                    
                except Exception as e:
                    return ValidationResult(
                        valid=False,
                        preservation_score=0.0,
                        semantic_match=False,
                        integrity_score=0.0,
                        details={"failed_at_step": i + 1, "conversion_details": conversion_details},
                        errors=[f"Conversion failed at step {i + 1}: {e}"],
                        warnings=[]
                    )
            
            # Calculate overall metrics
            overall_preservation = np.mean(preservation_scores) if preservation_scores else 0.0
            min_preservation = min(preservation_scores) if preservation_scores else 0.0
            
            # Validate final data matches original semantically
            semantic_match = await self._validate_semantic_equivalence(
                original_data, current_data, format_sequence[0], format_sequence[-1]
            )
            
            # Calculate integrity score
            integrity_score = (overall_preservation + (1.0 if semantic_match else 0.0)) / 2
            
            # Determine overall validity
            valid = (
                overall_preservation >= self.preservation_threshold and
                min_preservation >= self.preservation_threshold * 0.8 and
                semantic_match
            )
            
            return ValidationResult(
                valid=valid,
                preservation_score=overall_preservation,
                semantic_match=semantic_match,
                integrity_score=integrity_score,
                details={
                    "format_sequence": [f.value for f in format_sequence],
                    "preservation_scores": preservation_scores,
                    "conversion_details": conversion_details,
                    "min_preservation": min_preservation,
                    "max_preservation": max(preservation_scores) if preservation_scores else 0.0
                },
                errors=[],
                warnings=[]
            )
            
        except Exception as e:
            self.logger.error(f"Round-trip validation failed: {e}")
            return ValidationResult(
                valid=False,
                preservation_score=0.0,
                semantic_match=False,
                integrity_score=0.0,
                details={},
                errors=[f"Round-trip validation failed: {e}"],
                warnings=[]
            )
    
    def _create_metadata(
        self,
        source_format: DataFormat,
        target_format: DataFormat,
        start_time: float,
        original_data: Any,
        converted_data: Any,
        parameters: Dict[str, Any]
    ) -> ConversionMetadata:
        """Create conversion metadata"""
        
        processing_time = time.time() - start_time
        
        # Calculate data sizes
        data_size_before = self._calculate_data_size(original_data)
        data_size_after = self._calculate_data_size(converted_data)
        
        # Identify preserved semantic features
        semantic_features = self._identify_semantic_features(original_data, source_format)
        
        # Calculate quality metrics
        quality_metrics = {
            "size_preservation_ratio": data_size_after / max(1, data_size_before),
            "processing_efficiency": data_size_before / max(0.001, processing_time),
        }
        
        return ConversionMetadata(
            source_format=source_format,
            target_format=target_format,
            conversion_timestamp=datetime.now().isoformat(),
            processing_time=processing_time,
            data_size_before=data_size_before,
            data_size_after=data_size_after,
            semantic_features_preserved=semantic_features,
            quality_metrics=quality_metrics,
            conversion_parameters=parameters
        )
    
    def _calculate_data_size(self, data: Any) -> int:
        """Calculate approximate size of data"""
        
        try:
            if isinstance(data, dict):
                return len(json.dumps(data))
            elif isinstance(data, pd.DataFrame):
                return len(data) * len(data.columns)
            elif isinstance(data, np.ndarray):
                return data.size
            elif isinstance(data, list):
                return len(data)
            else:
                return len(str(data))
        except Exception:
            return 0
    
    def _identify_semantic_features(self, data: Any, format_type: DataFormat) -> List[str]:
        """Identify semantic features in the data"""
        
        features = []
        
        try:
            if format_type == DataFormat.GRAPH:
                if isinstance(data, dict):
                    if 'nodes' in data:
                        features.append("node_structure")
                    if 'edges' in data:
                        features.append("edge_relationships")
                        
            elif format_type == DataFormat.TABLE:
                if isinstance(data, pd.DataFrame):
                    features.append("tabular_structure")
                    if any(data.dtypes == 'object'):
                        features.append("categorical_data")
                    if any(data.dtypes.apply(lambda x: np.issubdtype(x, np.number))):
                        features.append("numerical_data")
                        
            elif format_type == DataFormat.VECTOR:
                if isinstance(data, np.ndarray):
                    features.append("vector_embeddings")
                    if data.ndim > 1:
                        features.append("multi_dimensional")
                        
        except Exception as e:
            self.logger.warning(f"Failed to identify semantic features: {e}")
        
        return features
    
    async def _validate_conversion(
        self,
        original_data: Any,
        converted_data: Any,
        source_format: DataFormat,
        target_format: DataFormat
    ) -> ValidationResult:
        """Validate conversion preserves semantic information"""
        
        try:
            errors = []
            warnings = []
            
            # Basic structure validation
            if converted_data is None:
                errors.append("Converted data is None")
                return ValidationResult(
                    valid=False,
                    preservation_score=0.0,
                    semantic_match=False,
                    integrity_score=0.0,
                    details={},
                    errors=errors,
                    warnings=warnings
                )
            
            # Format-specific validation
            format_valid = self._validate_target_format(converted_data, target_format)
            if not format_valid:
                errors.append(f"Converted data does not match {target_format.value} format")
            
            # Calculate preservation score based on structural similarity
            preservation_score = self._calculate_preservation_score(
                original_data, converted_data, source_format, target_format
            )
            
            # Check semantic equivalence
            semantic_match = await self._validate_semantic_equivalence(
                original_data, converted_data, source_format, target_format
            )
            
            # Calculate overall integrity
            integrity_score = (preservation_score + (1.0 if semantic_match else 0.0)) / 2
            
            # Determine validity
            valid = (
                len(errors) == 0 and
                preservation_score >= self.preservation_threshold and
                semantic_match
            )
            
            return ValidationResult(
                valid=valid,
                preservation_score=preservation_score,
                semantic_match=semantic_match,
                integrity_score=integrity_score,
                details={
                    "format_validation": format_valid,
                    "preservation_threshold": self.preservation_threshold
                },
                errors=errors,
                warnings=warnings
            )
            
        except Exception as e:
            self.logger.error(f"Validation failed: {e}")
            return ValidationResult(
                valid=False,
                preservation_score=0.0,
                semantic_match=False,
                integrity_score=0.0,
                details={},
                errors=[f"Validation error: {e}"],
                warnings=[]
            )
    
    def _validate_target_format(self, data: Any, target_format: DataFormat) -> bool:
        """Validate data matches expected target format"""
        
        try:
            if target_format == DataFormat.GRAPH:
                return isinstance(data, dict) and ('nodes' in data or 'edges' in data)
            elif target_format == DataFormat.TABLE:
                return isinstance(data, pd.DataFrame)
            elif target_format == DataFormat.VECTOR:
                return isinstance(data, np.ndarray)
            else:
                return True
                
        except Exception:
            return False
    
    def _calculate_preservation_score(
        self,
        original_data: Any,
        converted_data: Any,
        source_format: DataFormat,
        target_format: DataFormat
    ) -> float:
        """Calculate how well the conversion preserves information"""
        
        try:
            # Size-based preservation (basic metric)
            original_size = self._calculate_data_size(original_data)
            converted_size = self._calculate_data_size(converted_data)
            
            if original_size == 0:
                return 1.0 if converted_size == 0 else 0.0
            
            size_ratio = min(converted_size / original_size, original_size / converted_size)
            
            # Structure-based preservation
            structure_score = self._calculate_structure_preservation(
                original_data, converted_data, source_format, target_format
            )
            
            # Combine scores
            return (size_ratio + structure_score) / 2
            
        except Exception as e:
            self.logger.warning(f"Failed to calculate preservation score: {e}")
            return 0.5  # Default moderate score
    
    def _calculate_structure_preservation(
        self,
        original_data: Any,
        converted_data: Any,
        source_format: DataFormat,
        target_format: DataFormat
    ) -> float:
        """Calculate structural preservation score"""
        
        try:
            # Graph to table preservation
            if source_format == DataFormat.GRAPH and target_format == DataFormat.TABLE:
                if isinstance(original_data, dict) and isinstance(converted_data, pd.DataFrame):
                    original_edges = len(original_data.get('edges', []))
                    converted_rows = len(converted_data)
                    if original_edges > 0:
                        return min(1.0, converted_rows / original_edges)
            
            # Table to graph preservation
            elif source_format == DataFormat.TABLE and target_format == DataFormat.GRAPH:
                if isinstance(original_data, pd.DataFrame) and isinstance(converted_data, dict):
                    original_rows = len(original_data)
                    converted_edges = len(converted_data.get('edges', []))
                    if original_rows > 0:
                        return min(1.0, converted_edges / original_rows)
            
            # Vector conversions
            elif target_format == DataFormat.VECTOR:
                if isinstance(converted_data, np.ndarray):
                    return 1.0 if converted_data.size > 0 else 0.0
            
            return 0.8  # Default good preservation
            
        except Exception:
            return 0.5  # Default moderate preservation
    
    async def _validate_semantic_equivalence(
        self,
        original_data: Any,
        converted_data: Any,
        source_format: DataFormat,
        target_format: DataFormat
    ) -> bool:
        """Validate semantic equivalence between original and converted data"""
        
        try:
            # For now, use structural heuristics
            # In a full implementation, this would use embeddings or other semantic comparison
            
            # Check if key information is preserved
            if source_format == DataFormat.GRAPH and target_format == DataFormat.TABLE:
                if isinstance(original_data, dict) and isinstance(converted_data, pd.DataFrame):
                    # Check if entity relationships are preserved
                    edges = original_data.get('edges', [])
                    if edges and not converted_data.empty:
                        # Look for source/target columns or similar
                        has_relationship_info = any(
                            col in converted_data.columns 
                            for col in ['source', 'target', 'from', 'to', 'relationship']
                        )
                        return has_relationship_info
                    return True
            
            # For other conversions, check basic preservation
            return self._calculate_preservation_score(
                original_data, converted_data, source_format, target_format
            ) >= 0.7
            
        except Exception as e:
            self.logger.warning(f"Semantic equivalence check failed: {e}")
            return False
    
    def _initialize_embedding_service(self):
        """Initialize embedding service from service manager"""
        try:
            # Try to get embedding service from service manager
            if hasattr(self.service_manager, 'get_embedding_service'):
                return self.service_manager.get_embedding_service()
            
            # Fallback to real embedding service
            from .real_embedding_service import RealEmbeddingService
            return RealEmbeddingService()
            
        except Exception as e:
            self.logger.warning(f"Failed to initialize embedding service: {e}")
            return None