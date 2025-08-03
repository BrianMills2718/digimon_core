"""
Phase 3 Tool Adapters

Extracted from tool_adapters.py - Adapters for Phase 3 advanced analysis tools.
These adapters bridge the unified Tool protocol to Phase 3 multi-document and visualization tools.
"""

from typing import Any, Dict, List, Optional
from ..logging_config import get_logger
from ..config_manager import ConfigurationManager
from ..tool_protocol import ToolExecutionError, ToolValidationError, ToolValidationResult
from .base_adapters import BaseToolAdapter

logger = get_logger("core.adapters.phase3")


class MultiDocumentFusionAdapter(BaseToolAdapter):
    """Adapter for Multi-Document Fusion"""
    
    def __init__(self, config_manager: ConfigurationManager = None):
        super().__init__(config_manager)
        
        try:
            from ...tools.phase3.t301_multi_document_fusion_unified import T301MultiDocumentFusionUnified as _MultiDocumentFusion
            self._tool = _MultiDocumentFusion(
                identity_service=self.identity_service,
                quality_service=self.quality_service
            )
        except ImportError as e:
            logger.error(f"Failed to import T301MultiDocumentFusionUnified: {e}")
            self._tool = None
            
        self.tool_name = "MultiDocumentFusionAdapter"
    
    def execute(self, input_data: Any, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Convert Tool protocol to MultiDocumentFusion interface"""
        if self._tool is None:
            raise ToolExecutionError("MultiDocumentFusionAdapter", "T301MultiDocumentFusionUnified not available")
            
        validation_result = self.validate_input(input_data)
        if not validation_result.is_valid:
            raise ToolValidationError("MultiDocumentFusionAdapter", validation_result.validation_errors)
        
        try:
            documents = input_data.get("documents", [])
            document_refs = input_data.get("document_refs", [])
            fusion_strategy = input_data.get("fusion_strategy", "evidence_based")
            
            # Execute multi-document fusion
            if documents:
                result = self._tool.fuse_documents(documents=documents, fusion_strategy=fusion_strategy)
            elif document_refs:
                result = self._tool.fuse_documents(document_refs=document_refs, fusion_strategy=fusion_strategy)
            else:
                result = self._tool.fuse_documents(documents=[], fusion_strategy=fusion_strategy)
            
            return {
                "fusion_results": result.to_dict() if hasattr(result, 'to_dict') else result,
                "fusion_metadata": {
                    "strategy_used": fusion_strategy,
                    "documents_processed": len(documents) if documents else len(document_refs),
                    "fusion_method": "multi_document_fusion"
                },
                **input_data  # Pass through other data
            }
            
        except Exception as e:
            raise ToolExecutionError("MultiDocumentFusionAdapter", str(e), e)
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get MultiDocumentFusion tool information"""
        return {
            "name": "Multi-Document Fusion Engine",
            "version": "1.0",
            "description": "Fuses knowledge from multiple documents with conflict resolution",
            "contract_id": "T301_MultiDocumentFusion",
            "capabilities": ["multi_document_fusion", "conflict_resolution", "knowledge_integration"]
        }

    def validate_input(self, input_data: Dict[str, Any]) -> ToolValidationResult:
        """Validate MultiDocumentFusion input"""
        errors = []
        
        if not isinstance(input_data, dict):
            errors.append("Input data must be a dictionary")
        
        # Check for documents or document_refs (at least one required)
        has_documents = False
        if "documents" in input_data and isinstance(input_data["documents"], list):
            has_documents = True
        elif "document_refs" in input_data and isinstance(input_data["document_refs"], list):
            has_documents = True
        
        if not has_documents:
            errors.append("Must provide either 'documents' or 'document_refs'")
        
        # Validate fusion_strategy if present
        if "fusion_strategy" in input_data:
            strategy = input_data["fusion_strategy"]
            valid_strategies = ["evidence_based", "confidence_weighted", "time_based", "llm_based"]
            if strategy not in valid_strategies:
                errors.append(f"fusion_strategy must be one of: {', '.join(valid_strategies)}")
        
        return ToolValidationResult(
            is_valid=len(errors) == 0,
            validation_errors=errors,
            method_signatures={},
            execution_test_results={},
            input_schema_validation={"valid": len(errors) == 0, "errors": errors},
            security_validation={"valid": True, "errors": []},
            performance_validation={"valid": True, "errors": []}
        )


class InteractiveGraphVisualizerAdapter(BaseToolAdapter):
    """Adapter for Interactive Graph Visualizer"""
    
    def __init__(self, config_manager: ConfigurationManager = None):
        super().__init__(config_manager)
        
        try:
            # Try to import the visualizer tool
            from ...tools.phase3.interactive_graph_visualizer import InteractiveGraphVisualizer as _GraphVisualizer
            self._tool = _GraphVisualizer()
        except ImportError as e:
            logger.error(f"Failed to import InteractiveGraphVisualizer: {e}")
            self._tool = None
            
        self.tool_name = "InteractiveGraphVisualizerAdapter"
    
    def execute(self, input_data: Any, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Convert Tool protocol to InteractiveGraphVisualizer interface"""
        if self._tool is None:
            # Provide basic visualization functionality even without the tool
            return self._basic_visualization(input_data)
            
        validation_result = self.validate_input(input_data)
        if not validation_result.is_valid:
            raise ToolValidationError("InteractiveGraphVisualizerAdapter", validation_result.validation_errors)
        
        try:
            graph_data = input_data.get("graph_data", {})
            visualization_config = input_data.get("visualization_config", {})
            
            # Execute graph visualization
            result = self._tool.create_visualization(graph_data, visualization_config)
            
            return {
                "visualization_results": result,
                "visualization_metadata": {
                    "visualization_type": visualization_config.get("type", "interactive"),
                    "node_count": len(graph_data.get("nodes", graph_data.get("entities", []))),
                    "edge_count": len(graph_data.get("edges", graph_data.get("relationships", []))),
                    "visualization_method": "interactive_graph_visualizer"
                },
                **input_data  # Pass through other data
            }
            
        except Exception as e:
            raise ToolExecutionError("InteractiveGraphVisualizerAdapter", str(e), e)
    
    def _basic_visualization(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Basic visualization when tool is not available"""
        graph_data = input_data.get("graph_data", {})
        
        # Generate basic visualization data
        nodes = graph_data.get("nodes", graph_data.get("entities", []))
        edges = graph_data.get("edges", graph_data.get("relationships", []))
        
        # Create basic visualization structure
        viz_data = {
            "nodes": [
                {
                    "id": node.get("id", node.get("entity_id", f"node_{i}")),
                    "label": node.get("name", node.get("label", f"Node {i}")),
                    "type": node.get("type", "unknown"),
                    "size": 10
                }
                for i, node in enumerate(nodes)
            ],
            "edges": [
                {
                    "source": edge.get("source", edge.get("from")),
                    "target": edge.get("target", edge.get("to")),
                    "label": edge.get("type", edge.get("label", "connected")),
                    "weight": edge.get("weight", 1)
                }
                for edge in edges
            ]
        }
        
        return {
            "visualization_results": {
                "data": viz_data,
                "format": "basic_json",
                "status": "generated_basic"
            },
            "visualization_metadata": {
                "visualization_type": "basic",
                "node_count": len(nodes),
                "edge_count": len(edges),
                "visualization_method": "basic_adapter_fallback"
            },
            **input_data
        }
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get InteractiveGraphVisualizer tool information"""
        return {
            "name": "Interactive Graph Visualizer",
            "version": "1.0",
            "description": "Creates interactive visualizations of knowledge graphs",
            "contract_id": "InteractiveGraphVisualizer",
            "capabilities": ["graph_visualization", "interactive_exploration", "visual_analytics"]
        }

    def validate_input(self, input_data: Dict[str, Any]) -> ToolValidationResult:
        """Validate InteractiveGraphVisualizer input"""
        errors = []
        
        if not isinstance(input_data, dict):
            errors.append("Input data must be a dictionary")
        elif "graph_data" not in input_data:
            errors.append("Missing required field: graph_data")
        elif not isinstance(input_data["graph_data"], dict):
            errors.append("graph_data must be a dictionary")
        else:
            graph_data = input_data["graph_data"]
            
            # Check for nodes/entities
            has_nodes = False
            if "nodes" in graph_data and isinstance(graph_data["nodes"], list):
                has_nodes = True
            elif "entities" in graph_data and isinstance(graph_data["entities"], list):
                has_nodes = True
            
            if not has_nodes:
                errors.append("graph_data must contain 'nodes' or 'entities'")
            
            # Check for edges/relationships
            has_edges = False
            if "edges" in graph_data and isinstance(graph_data["edges"], list):
                has_edges = True
            elif "relationships" in graph_data and isinstance(graph_data["relationships"], list):
                has_edges = True
            
            if not has_edges:
                errors.append("graph_data must contain 'edges' or 'relationships'")
        
        # Validate visualization_config if present
        if "visualization_config" in input_data:
            viz_config = input_data["visualization_config"]
            if not isinstance(viz_config, dict):
                errors.append("visualization_config must be a dictionary")
        
        return ToolValidationResult(
            is_valid=len(errors) == 0,
            validation_errors=errors,
            method_signatures={},
            execution_test_results={},
            input_schema_validation={"valid": len(errors) == 0, "errors": errors},
            security_validation={"valid": True, "errors": []},
            performance_validation={"valid": True, "errors": []}
        )


class DocumentComparisonAdapter(BaseToolAdapter):
    """Adapter for Document Comparison and Analysis"""
    
    def __init__(self, config_manager: ConfigurationManager = None):
        super().__init__(config_manager)
        self.tool_name = "DocumentComparisonAdapter"
    
    def execute(self, input_data: Any, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute document comparison"""
        validation_result = self.validate_input(input_data)
        if not validation_result.is_valid:
            raise ToolValidationError("DocumentComparisonAdapter", validation_result.validation_errors)
        
        try:
            documents = input_data.get("documents", [])
            comparison_method = input_data.get("comparison_method", "similarity")
            
            # Perform document comparison
            comparison_results = self._compare_documents(documents, comparison_method)
            
            return {
                "comparison_results": comparison_results,
                "comparison_metadata": {
                    "method": comparison_method,
                    "documents_compared": len(documents),
                    "comparison_type": "document_analysis"
                },
                **input_data  # Pass through other data
            }
            
        except Exception as e:
            raise ToolExecutionError("DocumentComparisonAdapter", str(e), e)
    
    def _compare_documents(self, documents: List[Dict], method: str) -> Dict[str, Any]:
        """Compare documents using specified method"""
        if method == "similarity":
            return self._similarity_comparison(documents)
        elif method == "entity_overlap":
            return self._entity_overlap_comparison(documents)
        elif method == "topic_analysis":
            return self._topic_analysis_comparison(documents)
        else:
            return {"error": f"Unknown comparison method: {method}"}
    
    def _similarity_comparison(self, documents: List[Dict]) -> Dict[str, Any]:
        """Basic similarity comparison"""
        # Placeholder for similarity analysis
        return {
            "similarity_matrix": [],
            "most_similar_pair": None,
            "average_similarity": 0.0,
            "method": "text_similarity"
        }
    
    def _entity_overlap_comparison(self, documents: List[Dict]) -> Dict[str, Any]:
        """Entity overlap analysis"""
        # Extract entities from each document
        doc_entities = []
        for doc in documents:
            entities = set()
            for entity in doc.get("entities", []):
                entities.add(entity.get("name", ""))
            doc_entities.append(entities)
        
        # Calculate overlap
        overlaps = {}
        for i in range(len(doc_entities)):
            for j in range(i + 1, len(doc_entities)):
                overlap = len(doc_entities[i].intersection(doc_entities[j]))
                union = len(doc_entities[i].union(doc_entities[j]))
                jaccard = overlap / union if union > 0 else 0
                overlaps[f"doc_{i}_doc_{j}"] = {
                    "overlap_count": overlap,
                    "jaccard_similarity": jaccard
                }
        
        return {
            "entity_overlaps": overlaps,
            "method": "entity_overlap_analysis"
        }
    
    def _topic_analysis_comparison(self, documents: List[Dict]) -> Dict[str, Any]:
        """Topic analysis comparison"""
        # Placeholder for topic analysis
        return {
            "topic_distribution": {},
            "topic_similarity": {},
            "dominant_topics": [],
            "method": "topic_analysis"
        }
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get DocumentComparison tool information"""
        return {
            "name": "Document Comparison Adapter",
            "version": "1.0",
            "description": "Compares and analyzes multiple documents",
            "contract_id": "DocumentComparison",
            "capabilities": ["document_comparison", "similarity_analysis", "entity_overlap_analysis"]
        }

    def validate_input(self, input_data: Dict[str, Any]) -> ToolValidationResult:
        """Validate DocumentComparison input"""
        errors = []
        
        if not isinstance(input_data, dict):
            errors.append("Input data must be a dictionary")
        elif "documents" not in input_data:
            errors.append("Missing required field: documents")
        elif not isinstance(input_data["documents"], list):
            errors.append("documents must be a list")
        elif len(input_data["documents"]) < 2:
            errors.append("Need at least 2 documents for comparison")
        
        # Validate comparison_method if present
        if "comparison_method" in input_data:
            method = input_data["comparison_method"]
            valid_methods = ["similarity", "entity_overlap", "topic_analysis"]
            if method not in valid_methods:
                errors.append(f"comparison_method must be one of: {', '.join(valid_methods)}")
        
        return ToolValidationResult(
            is_valid=len(errors) == 0,
            validation_errors=errors,
            method_signatures={},
            execution_test_results={},
            input_schema_validation={"valid": len(errors) == 0, "errors": errors},
            security_validation={"valid": True, "errors": []},
            performance_validation={"valid": True, "errors": []}
        )