"""Simple Aggregator (<150 lines)

Basic aggregation for sequential pipeline results.
Consolidates results from multiple tools into unified format.
"""

from typing import Dict, Any, List
from ...logging_config import get_logger

logger = get_logger("core.orchestration.simple_aggregator")


class SimpleAggregator:
    """Simple aggregator for basic result consolidation"""
    
    def __init__(self):
        self.logger = get_logger("core.orchestration.simple_aggregator")
        
    def aggregate(self, execution_results: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate execution results into unified format
        
        Args:
            execution_results: Results from pipeline execution
            
        Returns:
            Aggregated results in unified format
        """
        if not execution_results:
            return self._create_empty_result()
            
        try:
            # Extract final data from execution results
            final_data = execution_results.get("final_data", {})
            execution_result_list = execution_results.get("execution_results", [])
            
            # Aggregate core data types
            aggregated_data = {
                "documents": self._aggregate_documents(final_data),
                "chunks": self._aggregate_chunks(final_data),
                "entities": self._aggregate_entities(final_data),
                "relationships": self._aggregate_relationships(final_data),
                "graph_data": self._aggregate_graph_data(final_data),
                "query_results": self._aggregate_query_results(final_data)
            }
            
            # Calculate summary statistics
            summary_stats = self._calculate_summary_stats(aggregated_data, execution_result_list)
            
            # Create unified result
            unified_result = {
                "status": execution_results.get("status", "unknown"),
                "data": aggregated_data,
                "summary": summary_stats,
                "execution_metadata": execution_results.get("execution_metadata", {}),
                "tool_results": self._summarize_tool_results(execution_result_list)
            }
            
            self.logger.info(f"Aggregated results: {summary_stats['total_entities']} entities, {summary_stats['total_relationships']} relationships")
            
            return unified_result
            
        except Exception as e:
            self.logger.error(f"Error aggregating results: {e}")
            return self._create_error_result(str(e))
            
    def _aggregate_documents(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Aggregate document data"""
        documents = data.get("documents", [])
        
        if not isinstance(documents, list):
            return []
            
        # Normalize document format
        normalized_docs = []
        for doc in documents:
            if isinstance(doc, dict):
                normalized_doc = {
                    "document_id": doc.get("document_id"),
                    "file_path": doc.get("file_path"),
                    "text": doc.get("text", ""),
                    "metadata": doc.get("metadata", {}),
                    "confidence": doc.get("confidence", 0.0),
                    "processing_status": "processed" if doc.get("text") else "failed"
                }
                normalized_docs.append(normalized_doc)
                
        return normalized_docs
        
    def _aggregate_chunks(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Aggregate text chunk data"""
        chunks = data.get("chunks", [])
        
        if not isinstance(chunks, list):
            return []
            
        # Normalize chunk format
        normalized_chunks = []
        for chunk in chunks:
            if isinstance(chunk, dict):
                normalized_chunk = {
                    "chunk_id": chunk.get("chunk_id"),
                    "text": chunk.get("text", ""),
                    "source_document": chunk.get("source_document"),
                    "source_file_path": chunk.get("source_file_path"),
                    "start_position": chunk.get("start_position", 0),
                    "end_position": chunk.get("end_position", 0),
                    "confidence": chunk.get("confidence", 0.0)
                }
                normalized_chunks.append(normalized_chunk)
                
        return normalized_chunks
        
    def _aggregate_entities(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Aggregate entity data"""
        entities = data.get("entities", [])
        
        if not isinstance(entities, list):
            return []
            
        # Deduplicate and normalize entities
        entity_map = {}
        for entity in entities:
            if isinstance(entity, dict):
                entity_id = entity.get("entity_id")
                if entity_id:
                    if entity_id not in entity_map:
                        entity_map[entity_id] = {
                            "entity_id": entity_id,
                            "surface_form": entity.get("surface_form", ""),
                            "canonical_name": entity.get("canonical_name", ""),
                            "entity_type": entity.get("entity_type", "UNKNOWN"),
                            "confidence": entity.get("confidence", 0.0),
                            "mentions": [],
                            "source_chunks": set(),
                            "source_documents": set()
                        }
                    
                    # Merge mentions and sources
                    current_entity = entity_map[entity_id]
                    if entity.get("source_chunk"):
                        current_entity["source_chunks"].add(entity["source_chunk"])
                    if entity.get("source_document"):
                        current_entity["source_documents"].add(entity["source_document"])
                        
        # Convert sets to lists for JSON serialization
        for entity in entity_map.values():
            entity["source_chunks"] = list(entity["source_chunks"])
            entity["source_documents"] = list(entity["source_documents"])
            
        return list(entity_map.values())
        
    def _aggregate_relationships(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Aggregate relationship data"""
        relationships = data.get("relationships", [])
        
        if not isinstance(relationships, list):
            return []
            
        # Normalize relationship format
        normalized_rels = []
        for rel in relationships:
            if isinstance(rel, dict):
                normalized_rel = {
                    "relationship_id": rel.get("relationship_id"),
                    "subject_entity_id": rel.get("subject_entity_id"),
                    "object_entity_id": rel.get("object_entity_id"),
                    "relationship_type": rel.get("relationship_type", "UNKNOWN"),
                    "confidence": rel.get("confidence", 0.0),
                    "source_chunk": rel.get("source_chunk"),
                    "source_document": rel.get("source_document")
                }
                normalized_rels.append(normalized_rel)
                
        return normalized_rels
        
    def _aggregate_graph_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate graph construction data"""
        return {
            "neo4j_entities": data.get("neo4j_entities", []),
            "neo4j_relationships": data.get("neo4j_relationships", []),
            "entity_build_result": data.get("entity_build_result", {}),
            "edge_build_result": data.get("edge_build_result", {}),
            "pagerank_scores": data.get("pagerank_scores", [])
        }
        
    def _aggregate_query_results(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Aggregate query execution results"""
        return data.get("query_results", [])
        
    def _calculate_summary_stats(self, aggregated_data: Dict[str, Any], 
                                execution_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate summary statistics"""
        return {
            "total_documents": len(aggregated_data.get("documents", [])),
            "total_chunks": len(aggregated_data.get("chunks", [])),
            "total_entities": len(aggregated_data.get("entities", [])),
            "total_relationships": len(aggregated_data.get("relationships", [])),
            "total_neo4j_entities": len(aggregated_data.get("graph_data", {}).get("neo4j_entities", [])),
            "total_neo4j_relationships": len(aggregated_data.get("graph_data", {}).get("neo4j_relationships", [])),
            "total_query_results": len(aggregated_data.get("query_results", [])),
            "tools_executed": len(execution_results),
            "successful_tools": len([r for r in execution_results if r.get("status") == "success"]),
            "failed_tools": len([r for r in execution_results if r.get("status") == "error"])
        }
        
    def _summarize_tool_results(self, execution_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Summarize individual tool results"""
        tool_summary = {}
        
        for result in execution_results:
            tool_name = result.get("tool_name", "unknown")
            tool_summary[tool_name] = {
                "status": result.get("status", "unknown"),
                "execution_time": result.get("execution_time", 0.0),
                "error": result.get("error") if result.get("status") == "error" else None
            }
            
        return tool_summary
        
    def _create_empty_result(self) -> Dict[str, Any]:
        """Create empty result structure"""
        return {
            "status": "empty",
            "data": {
                "documents": [],
                "chunks": [],
                "entities": [],
                "relationships": [],
                "graph_data": {},
                "query_results": []
            },
            "summary": {
                "total_documents": 0,
                "total_chunks": 0,
                "total_entities": 0,
                "total_relationships": 0,
                "tools_executed": 0,
                "successful_tools": 0,
                "failed_tools": 0
            },
            "execution_metadata": {},
            "tool_results": {}
        }
        
    def _create_error_result(self, error_message: str) -> Dict[str, Any]:
        """Create error result structure"""
        result = self._create_empty_result()
        result["status"] = "error"
        result["error"] = error_message
        return result