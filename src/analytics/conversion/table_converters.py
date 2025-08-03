#!/usr/bin/env python3
"""
Table format converters for cross-modal conversion.

Handles conversion from table format to other formats (graph, vector).
"""

import logging
import pandas as pd
from typing import Any, Dict, List

from .base_converter import BaseConverter
from .models import DataFormat, ConversionError

logger = logging.getLogger("analytics.conversion.table_converters")


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