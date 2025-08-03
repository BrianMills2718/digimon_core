#!/usr/bin/env python3
"""
Graph format converters for cross-modal conversion.

Handles conversion from graph format to other formats (table, vector).
"""

import logging
import numpy as np
import pandas as pd
from typing import Any, Dict, List

from .base_converter import BaseConverter
from .models import DataFormat, ConversionError

logger = logging.getLogger("analytics.conversion.graph_converters")


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