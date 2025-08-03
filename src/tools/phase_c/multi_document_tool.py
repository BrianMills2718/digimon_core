"""
Multi-Document Processing Tool Wrapper

Wraps the MultiDocumentEngine with BaseTool interface for DAG integration.
"""

from typing import Dict, Any, List, Optional
from src.tools.base_tool_fixed import BaseTool, ToolRequest, ToolResult, ToolContract
from src.processing.multi_document_engine import MultiDocumentEngine
import asyncio
import json


class MultiDocumentTool(BaseTool):
    """Tool wrapper for multi-document processing capabilities."""
    
    def __init__(self, service_manager=None):
        """Initialize the multi-document processing tool."""
        super().__init__(service_manager)
        self.tool_id = "MULTI_DOCUMENT_PROCESSOR"
        self.engine = MultiDocumentEngine(max_workers=4)
    
    def get_contract(self) -> ToolContract:
        """Return tool contract specification."""
        from src.tools.base_tool_fixed import ToolContract
        return ToolContract(
            tool_id=self.tool_id,
            name="Multi-Document Processor",
            description="Process multiple documents simultaneously with dependency tracking",
            category="document_processing",
            input_schema={
                "type": "object",
                "properties": {
                    "documents": {"type": "array", "items": {"type": "string"}},
                    "operation": {"type": "string", "enum": [
                        "load_batch", "chunk_parallel", "detect_duplicates",
                        "assess_quality", "cluster_by_topic"
                    ]}
                },
                "required": ["documents"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "processed_documents": {"type": "array"},
                    "total_documents": {"type": "integer"},
                    "successful": {"type": "integer"}
                }
            },
            dependencies=[],
            performance_requirements={
                "max_execution_time": 60.0,
                "max_memory_mb": 2000
            },
            error_conditions=["INVALID_DOCUMENTS", "PROCESSING_FAILED"]
        )
        
    def execute(self, request: ToolRequest) -> ToolResult:
        """
        Execute multi-document processing.
        
        Args:
            request: Tool request with document paths and processing parameters
            
        Returns:
            ToolResult with processed documents and metadata
        """
        try:
            # Extract parameters
            documents = request.input_data.get("documents", [])
            operation = request.input_data.get("operation", "load_batch")
            
            # Run async operations in sync context
            loop = asyncio.get_event_loop()
            
            if operation == "load_batch":
                # Load multiple documents
                results = loop.run_until_complete(
                    self.engine.load_documents_batch(documents)
                )
                
                # Convert results to serializable format
                processed_results = []
                for result in results:
                    processed_results.append({
                        "document_id": result.document_id,
                        "document_path": result.document_path,
                        "success": result.success,
                        "content_length": len(result.content) if result.content else 0,
                        "status": result.status.value,
                        "processing_time": result.processing_time
                    })
                
                return self._create_success_result(
                    data={
                        "processed_documents": processed_results,
                        "total_documents": len(documents),
                        "successful": sum(1 for r in processed_results if r["success"])
                    },
                    metadata={
                        "operation": operation,
                        "engine": "MultiDocumentEngine"
                    }
                )
                
            elif operation == "chunk_parallel":
                # Chunk documents in parallel
                load_results = loop.run_until_complete(
                    self.engine.load_documents_batch(documents)
                )
                chunk_results = loop.run_until_complete(
                    self.engine.chunk_documents_parallel(load_results)
                )
                
                chunked_docs = []
                for result in chunk_results:
                    if result.success and result.chunks:
                        chunked_docs.append({
                            "document_id": result.document_id,
                            "num_chunks": len(result.chunks),
                            "chunks": result.chunks[:3]  # First 3 chunks as preview
                        })
                
                return self._create_success_result(
                    data={
                        "chunked_documents": chunked_docs,
                        "total_chunks": sum(d["num_chunks"] for d in chunked_docs)
                    }
                )
                
            elif operation == "detect_duplicates":
                # Detect duplicate content
                load_results = loop.run_until_complete(
                    self.engine.load_documents_batch(documents)
                )
                duplicates = loop.run_until_complete(
                    self.engine.detect_duplicate_content(load_results)
                )
                
                duplicate_groups = []
                for dup_group in duplicates:
                    duplicate_groups.append({
                        "documents": dup_group.documents,
                        "similarity_score": dup_group.similarity_score,
                        "representative": dup_group.representative_document
                    })
                
                return self._create_success_result(
                    data={
                        "duplicate_groups": duplicate_groups,
                        "num_duplicates": len(duplicate_groups)
                    }
                )
                
            elif operation == "assess_quality":
                # Assess document quality
                load_results = loop.run_until_complete(
                    self.engine.load_documents_batch(documents)
                )
                quality_scores = loop.run_until_complete(
                    self.engine.assess_document_quality(load_results)
                )
                
                quality_data = []
                for score in quality_scores:
                    quality_data.append({
                        "document": score.document_path,
                        "overall_score": score.overall_score,
                        "completeness": score.completeness_score,
                        "structure": score.structure_score,
                        "readability": score.readability_score
                    })
                
                return self._create_success_result(
                    data={
                        "quality_assessments": quality_data,
                        "average_quality": sum(q["overall_score"] for q in quality_data) / len(quality_data) if quality_data else 0
                    }
                )
                
            elif operation == "cluster_by_topic":
                # Cluster documents by topic
                load_results = loop.run_until_complete(
                    self.engine.load_documents_batch(documents)
                )
                clusters = loop.run_until_complete(
                    self.engine.cluster_documents_by_topic(load_results)
                )
                
                cluster_data = []
                for cluster in clusters:
                    cluster_data.append({
                        "cluster_id": cluster.cluster_id,
                        "documents": cluster.documents,
                        "keywords": cluster.topic_keywords,
                        "score": cluster.cluster_score
                    })
                
                return self._create_success_result(
                    data={
                        "topic_clusters": cluster_data,
                        "num_clusters": len(cluster_data)
                    }
                )
                
            else:
                return self._create_error_result(
                    error_code="UNKNOWN_OPERATION",
                    error_message=f"Unknown operation: {operation}"
                )
                
        except Exception as e:
            return self._create_error_result(
                error_code="PROCESSING_FAILED",
                error_message=f"Multi-document processing failed: {str(e)}"
            )
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        Validate input data for multi-document processing.
        
        Args:
            input_data: Input data to validate
            
        Returns:
            True if valid, False otherwise
        """
        if "documents" not in input_data:
            return False
            
        documents = input_data.get("documents", [])
        if not isinstance(documents, list) or len(documents) == 0:
            return False
            
        # Verify all documents are strings (paths)
        for doc in documents:
            if not isinstance(doc, str):
                return False
                
        return True
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get tool capabilities."""
        return {
            "tool_id": self.tool_id,
            "operations": [
                "load_batch",
                "chunk_parallel",
                "detect_duplicates",
                "assess_quality",
                "cluster_by_topic"
            ],
            "max_documents": 100,
            "parallel_processing": True,
            "memory_efficient": True
        }