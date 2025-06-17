"""Vertical Slice Workflow Integration

Orchestrates the complete PDF → PageRank → Answer workflow.
Demonstrates end-to-end functionality of the Phase 1 implementation.

Workflow Steps:
1. T01: Load PDF document
2. T15a: Chunk text into segments  
3. T23a: Extract entities from chunks
4. T27: Extract relationships between entities
5. T31: Build entity nodes in Neo4j
6. T34: Build relationship edges in Neo4j
7. T68: Calculate PageRank scores
8. T49: Execute multi-hop queries

This integration proves the vertical slice architecture works.
"""

from typing import Dict, List, Optional, Any
import os
from pathlib import Path

# Import Phase 1 tools
from .t01_pdf_loader import PDFLoader
from .t15a_text_chunker import TextChunker
from .t23a_spacy_ner import SpacyNER
from .t27_relationship_extractor import RelationshipExtractor
from .t31_entity_builder import EntityBuilder
from .t34_edge_builder import EdgeBuilder
from .t68_pagerank import PageRankCalculator
from .t49_multihop_query import MultiHopQuery

# Import core services
from src.core.identity_service import IdentityService
from src.core.provenance_service import ProvenanceService
from src.core.quality_service import QualityService
from src.core.workflow_state_service import WorkflowStateService


class VerticalSliceWorkflow:
    """Complete PDF → PageRank → Answer workflow."""
    
    def __init__(
        self,
        neo4j_uri: str = "bolt://localhost:7687",
        neo4j_user: str = "neo4j", 
        neo4j_password: str = "password",
        workflow_storage_dir: str = "./data/workflows"
    ):
        # Initialize core services
        self.identity_service = IdentityService()
        self.provenance_service = ProvenanceService()
        self.quality_service = QualityService()
        self.workflow_service = WorkflowStateService(workflow_storage_dir)
        
        # Initialize Phase 1 tools
        self.pdf_loader = PDFLoader(
            self.identity_service, self.provenance_service, self.quality_service
        )
        self.text_chunker = TextChunker(
            self.identity_service, self.provenance_service, self.quality_service
        )
        self.entity_extractor = SpacyNER(
            self.identity_service, self.provenance_service, self.quality_service
        )
        self.relationship_extractor = RelationshipExtractor(
            self.identity_service, self.provenance_service, self.quality_service
        )
        self.entity_builder = EntityBuilder(
            self.identity_service, self.provenance_service, self.quality_service,
            neo4j_uri, neo4j_user, neo4j_password
        )
        self.edge_builder = EdgeBuilder(
            self.identity_service, self.provenance_service, self.quality_service,
            neo4j_uri, neo4j_user, neo4j_password
        )
        self.pagerank_calculator = PageRankCalculator(
            self.identity_service, self.provenance_service, self.quality_service,
            neo4j_uri, neo4j_user, neo4j_password
        )
        self.query_engine = MultiHopQuery(
            self.identity_service, self.provenance_service, self.quality_service,
            neo4j_uri, neo4j_user, neo4j_password
        )
    
    def execute_workflow(
        self,
        pdf_path: str,
        query: str,
        workflow_name: str = "PDF_to_Answer_Workflow"
    ) -> Dict[str, Any]:
        """Execute the complete vertical slice workflow.
        
        Args:
            pdf_path: Path to PDF file to process
            query: Question to answer using the graph
            workflow_name: Name for workflow tracking
            
        Returns:
            Complete workflow results with answers
        """
        # Start workflow tracking
        workflow_id = self.workflow_service.start_workflow(
            name=workflow_name,
            total_steps=8,
            initial_state={
                "pdf_path": pdf_path,
                "query": query,
                "status": "started"
            }
        )
        
        try:
            results = {
                "workflow_id": workflow_id,
                "workflow_name": workflow_name,
                "input": {
                    "pdf_path": pdf_path,
                    "query": query
                },
                "steps": {},
                "final_answer": None,
                "status": "running"
            }
            
            # Step 1: Load PDF
            print("Step 1: Loading PDF...")
            self.workflow_service.create_checkpoint(
                workflow_id, "load_pdf", 1, {"step": "loading_pdf"}
            )
            
            pdf_result = self.pdf_loader.load_pdf(pdf_path)
            if pdf_result["status"] != "success":
                return self._complete_workflow_with_error(
                    workflow_id, results, f"PDF loading failed: {pdf_result.get('error')}"
                )
            
            results["steps"]["pdf_loading"] = {
                "status": "success",
                "document": pdf_result["document"],
                "confidence": pdf_result["document"]["confidence"]
            }
            
            # Step 2: Chunk text
            print("Step 2: Chunking text...")
            self.workflow_service.create_checkpoint(
                workflow_id, "chunk_text", 2, {"step": "chunking_text"}
            )
            
            chunk_result = self.text_chunker.chunk_text(
                document_ref=pdf_result["document"]["document_ref"],
                text=pdf_result["document"]["text"],
                document_confidence=pdf_result["document"]["confidence"]
            )
            if chunk_result["status"] != "success":
                return self._complete_workflow_with_error(
                    workflow_id, results, f"Text chunking failed: {chunk_result.get('error')}"
                )
            
            results["steps"]["text_chunking"] = {
                "status": "success",
                "chunks": len(chunk_result["chunks"]),
                "total_tokens": chunk_result["total_tokens"]
            }
            
            # Step 3: Extract entities from chunks
            print("Step 3: Extracting entities...")
            self.workflow_service.create_checkpoint(
                workflow_id, "extract_entities", 3, {"step": "extracting_entities"}
            )
            
            all_entities = []
            for chunk in chunk_result["chunks"]:
                entity_result = self.entity_extractor.extract_entities(
                    chunk_ref=chunk["chunk_ref"],
                    text=chunk["text"],
                    chunk_confidence=chunk["confidence"]
                )
                if entity_result["status"] == "success":
                    all_entities.extend(entity_result["entities"])
            
            results["steps"]["entity_extraction"] = {
                "status": "success",
                "total_entities": len(all_entities),
                "entity_types": self._count_types(all_entities, "entity_type")
            }
            
            # Step 4: Extract relationships
            print("Step 4: Extracting relationships...")
            self.workflow_service.create_checkpoint(
                workflow_id, "extract_relationships", 4, {"step": "extracting_relationships"}
            )
            
            all_relationships = []
            for chunk in chunk_result["chunks"]:
                # Get entities for this chunk
                chunk_entities = [e for e in all_entities if e["source_chunk"] == chunk["chunk_ref"]]
                
                if len(chunk_entities) >= 2:
                    rel_result = self.relationship_extractor.extract_relationships(
                        chunk_ref=chunk["chunk_ref"],
                        text=chunk["text"],
                        entities=chunk_entities,
                        chunk_confidence=chunk["confidence"]
                    )
                    if rel_result["status"] == "success":
                        all_relationships.extend(rel_result["relationships"])
            
            results["steps"]["relationship_extraction"] = {
                "status": "success",
                "total_relationships": len(all_relationships),
                "relationship_types": self._count_types(all_relationships, "relationship_type")
            }
            
            # Step 5: Build entity nodes in Neo4j
            print("Step 5: Building entity nodes...")
            self.workflow_service.create_checkpoint(
                workflow_id, "build_entities", 5, {"step": "building_entities"}
            )
            
            entity_build_result = self.entity_builder.build_entities(
                mentions=all_entities,
                source_refs=[pdf_result["document"]["document_ref"]]
            )
            if entity_build_result["status"] != "success":
                return self._complete_workflow_with_error(
                    workflow_id, results, f"Entity building failed: {entity_build_result.get('error')}"
                )
            
            results["steps"]["entity_building"] = {
                "status": "success",
                "entities_created": entity_build_result["total_entities"],
                "entity_types": entity_build_result["entity_types"]
            }
            
            # Step 6: Build relationship edges in Neo4j
            print("Step 6: Building relationship edges...")
            self.workflow_service.create_checkpoint(
                workflow_id, "build_edges", 6, {"step": "building_edges"}
            )
            
            edge_build_result = self.edge_builder.build_edges(
                relationships=all_relationships,
                source_refs=[pdf_result["document"]["document_ref"]]
            )
            if edge_build_result["status"] != "success":
                return self._complete_workflow_with_error(
                    workflow_id, results, f"Edge building failed: {edge_build_result.get('error')}"
                )
            
            results["steps"]["edge_building"] = {
                "status": "success",
                "edges_created": edge_build_result["total_edges"],
                "relationship_types": edge_build_result["relationship_types"]
            }
            
            # Step 7: Calculate PageRank
            print("Step 7: Calculating PageRank...")
            self.workflow_service.create_checkpoint(
                workflow_id, "calculate_pagerank", 7, {"step": "calculating_pagerank"}
            )
            
            pagerank_result = self.pagerank_calculator.calculate_pagerank()
            if pagerank_result["status"] != "success":
                return self._complete_workflow_with_error(
                    workflow_id, results, f"PageRank calculation failed: {pagerank_result.get('error')}"
                )
            
            results["steps"]["pagerank_calculation"] = {
                "status": "success",
                "entities_ranked": pagerank_result["total_entities"],
                "graph_stats": pagerank_result["graph_stats"],
                "top_entities": pagerank_result["ranked_entities"][:5] if pagerank_result["ranked_entities"] else []
            }
            
            # Step 8: Execute query
            print("Step 8: Executing query...")
            self.workflow_service.create_checkpoint(
                workflow_id, "execute_query", 8, {"step": "executing_query"}
            )
            
            query_result = self.query_engine.query_graph(
                query_text=query,
                max_hops=2,
                result_limit=10
            )
            if query_result["status"] != "success":
                return self._complete_workflow_with_error(
                    workflow_id, results, f"Query execution failed: {query_result.get('error')}"
                )
            
            results["steps"]["query_execution"] = {
                "status": "success",
                "results_found": query_result["total_results"],
                "search_stats": query_result["search_stats"]
            }
            
            # Format final answer
            if query_result["results"]:
                best_result = query_result["results"][0]
                results["final_answer"] = {
                    "answer": best_result["answer_entity"],
                    "confidence": best_result["confidence"],
                    "explanation": best_result["explanation"],
                    "full_path": best_result["full_path"],
                    "supporting_evidence": query_result["results"][:3]  # Top 3 results
                }
            else:
                results["final_answer"] = {
                    "answer": "No answer found",
                    "confidence": 0.0,
                    "explanation": "No relevant entities found in the graph for this query"
                }
            
            # Complete workflow
            results["status"] = "completed"
            self.workflow_service.update_workflow_progress(
                workflow_id, 8, "completed"
            )
            
            print("Workflow completed successfully!")
            return results
            
        except Exception as e:
            return self._complete_workflow_with_error(
                workflow_id, results, f"Unexpected workflow error: {str(e)}"
            )
    
    def _complete_workflow_with_error(
        self, 
        workflow_id: str, 
        results: Dict[str, Any], 
        error_message: str
    ) -> Dict[str, Any]:
        """Complete workflow with error."""
        results["status"] = "failed"
        results["error"] = error_message
        
        self.workflow_service.update_workflow_progress(
            workflow_id, -1, "failed", error_message
        )
        
        return results
    
    def _count_types(self, items: List[Dict[str, Any]], type_field: str) -> Dict[str, int]:
        """Count items by type."""
        counts = {}
        for item in items:
            item_type = item.get(type_field, "UNKNOWN")
            counts[item_type] = counts.get(item_type, 0) + 1
        return counts
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow status."""
        return self.workflow_service.get_workflow_status(workflow_id)
    
    def close(self):
        """Close all connections."""
        self.entity_builder.close()
        self.edge_builder.close()
        self.pagerank_calculator.close()
        self.query_engine.close()
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get workflow information."""
        return {
            "workflow_name": "PDF to Answer Vertical Slice",
            "version": "1.0.0",
            "description": "Complete workflow from PDF document to graph-based answers",
            "steps": [
                "T01: PDF Loading",
                "T15a: Text Chunking", 
                "T23a: Entity Extraction",
                "T27: Relationship Extraction",
                "T31: Entity Building",
                "T34: Edge Building",
                "T68: PageRank Calculation",
                "T49: Multi-hop Query"
            ],
            "input_types": ["pdf_file", "natural_language_query"],
            "output_type": "ranked_answers_with_provenance",
            "requires_neo4j": True
        }