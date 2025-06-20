"""
Enhanced Vertical Slice Workflow - Phase 2
Replaces spaCy NER with ontology-aware extraction for real GraphRAG capabilities.

Enhanced Workflow Steps:
1. T01: Load PDF document
2. T15a: Chunk text into segments
3. T120: Generate domain ontology (or use existing)
4. T23c: Ontology-aware entity extraction
5. T31: Enhanced graph building with semantic validation
6. T68: Calculate PageRank scores
7. T49: Enhanced multi-hop queries with ontological reasoning
8. Interactive visualization and analysis

This demonstrates the complete ontology-driven pipeline.
"""

import os
import json
import time
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from datetime import datetime
import traceback
from dotenv import load_dotenv

# Load environment variables for API keys
load_dotenv()

# Import Phase 1 tools (reusable)
from ..phase1.t01_pdf_loader import PDFLoader
from ..phase1.t15a_text_chunker import TextChunker
from ..phase1.t68_pagerank import PageRankCalculator
from ..phase1.t49_multihop_query import MultiHopQuery

# Import Phase 2 tools
from .t23c_ontology_aware_extractor import OntologyAwareExtractor, ExtractionResult
from .t31_ontology_graph_builder import OntologyAwareGraphBuilder, GraphBuildResult
from .interactive_graph_visualizer import InteractiveGraphVisualizer, GraphVisualizationConfig

# Import ontology components
from src.ontology_generator import DomainOntology
from src.ontology.gemini_ontology_generator import GeminiOntologyGenerator
from src.core.ontology_storage_service import OntologyStorageService, OntologySession

# Import core services
from src.core.enhanced_identity_service import EnhancedIdentityService
from src.core.quality_service import QualityService
from src.core.workflow_state_service import WorkflowStateService

import logging
logger = logging.getLogger(__name__)


class EnhancedVerticalSliceWorkflow:
    """
    Complete ontology-driven PDF → GraphRAG → Answer workflow.
    Demonstrates real GraphRAG capabilities with domain-specific entities.
    """
    
    def __init__(self,
                 neo4j_uri: str = "bolt://localhost:7687",
                 neo4j_user: str = "neo4j", 
                 neo4j_password: str = "password",
                 workflow_storage_dir: str = "./data/workflows",
                 confidence_threshold: float = 0.7):
        """Initialize the enhanced workflow."""
        self.confidence_threshold = confidence_threshold
        
        # Initialize services
        self.identity_service = EnhancedIdentityService()
        self.quality_service = QualityService()
        self.workflow_service = WorkflowStateService(storage_dir=workflow_storage_dir)
        self.ontology_storage = OntologyStorageService()
        
        # Initialize legacy identity service for Phase 1 tools compatibility
        from src.core.identity_service import IdentityService
        from src.core.provenance_service import ProvenanceService
        legacy_identity_service = IdentityService()
        provenance_service = ProvenanceService()
        
        # Initialize Phase 1 tools (reusable) with required services
        self.pdf_loader = PDFLoader(legacy_identity_service, provenance_service, self.quality_service)
        self.text_chunker = TextChunker(legacy_identity_service, provenance_service, self.quality_service)
        self.pagerank_calculator = PageRankCalculator(legacy_identity_service, provenance_service, self.quality_service, neo4j_uri, neo4j_user, neo4j_password)
        self.query_engine = MultiHopQuery(neo4j_uri, neo4j_user, neo4j_password)
        
        # Initialize Phase 2 tools
        self.ontology_extractor = OntologyAwareExtractor(self.identity_service)
        self.graph_builder = OntologyAwareGraphBuilder(neo4j_uri, neo4j_user, neo4j_password, confidence_threshold)
        self.visualizer = InteractiveGraphVisualizer(neo4j_uri, neo4j_user, neo4j_password)
        
        # Initialize ontology generator
        try:
            self.ontology_generator = GeminiOntologyGenerator()
            self.use_real_ontology = True
        except Exception as e:
            logger.warning(f"Could not initialize Gemini ontology generator: {e}")
            self.use_real_ontology = False
        
        # Current ontology
        self.current_ontology = None
        
        logger.info("✅ Enhanced Vertical Slice Workflow initialized")
    
    def execute_enhanced_workflow(self, 
                                 pdf_path: str,
                                 domain_description: str,
                                 queries: List[str],
                                 workflow_name: str = "enhanced_workflow",
                                 use_existing_ontology: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute the complete enhanced workflow.
        
        Args:
            pdf_path: Path to PDF document
            domain_description: Description of domain for ontology generation
            queries: List of questions to answer
            workflow_name: Name for workflow tracking
            use_existing_ontology: Optional ontology session ID to reuse
            
        Returns:
            Complete workflow results with enhanced analysis
        """
        start_time = time.time()
        
        # Start workflow tracking
        workflow_id = self.workflow_service.start_workflow(
            name=workflow_name,
            total_steps=9,  # Enhanced workflow has 9 steps
            initial_state={
                "pdf_path": pdf_path,
                "domain_description": domain_description,
                "queries": queries,
                "status": "started",
                "use_existing_ontology": use_existing_ontology
            }
        )
        
        try:
            results = {
                "workflow_id": workflow_id,
                "workflow_name": workflow_name,
                "execution_time": 0,
                "input": {
                    "pdf_path": pdf_path,
                    "domain_description": domain_description,
                    "queries": queries
                },
                "steps": {},
                "ontology_info": {},
                "graph_metrics": {},
                "query_results": {},
                "visualizations": {},
                "quality_assessment": {},
                "status": "running"
            }
            
            # Step 1: Load PDF
            print("Step 1: Loading PDF...")
            results["steps"]["pdf_loading"] = self._execute_pdf_loading(workflow_id, pdf_path)
            if results["steps"]["pdf_loading"]["status"] != "success":
                return self._complete_workflow_with_error(workflow_id, results, "PDF loading failed")
            
            # Step 2: Chunk text
            print("Step 2: Chunking text...")
            results["steps"]["text_chunking"] = self._execute_text_chunking(
                workflow_id, 
                results["steps"]["pdf_loading"]["document"]
            )
            if results["steps"]["text_chunking"]["status"] != "success":
                return self._complete_workflow_with_error(workflow_id, results, "Text chunking failed")
            
            # Step 3: Generate or load domain ontology
            print("Step 3: Creating domain ontology...")
            results["steps"]["ontology_generation"] = self._execute_ontology_generation(
                workflow_id, domain_description, use_existing_ontology
            )
            if results["steps"]["ontology_generation"]["status"] != "success":
                return self._complete_workflow_with_error(workflow_id, results, "Ontology generation failed")
            
            # Step 4: Ontology-aware entity extraction
            print("Step 4: Extracting entities with ontology...")
            results["steps"]["entity_extraction"] = self._execute_ontology_aware_extraction(
                workflow_id,
                results["steps"]["text_chunking"]["chunks"],
                results["steps"]["pdf_loading"]["document"]["document_ref"]
            )
            if results["steps"]["entity_extraction"]["status"] != "success":
                return self._complete_workflow_with_error(workflow_id, results, "Entity extraction failed")
            
            # Step 5: Enhanced graph building
            print("Step 5: Building knowledge graph...")
            results["steps"]["graph_building"] = self._execute_enhanced_graph_building(
                workflow_id,
                results["steps"]["entity_extraction"]["extraction_result"],
                results["steps"]["pdf_loading"]["document"]["document_ref"]
            )
            if results["steps"]["graph_building"]["status"] != "success":
                return self._complete_workflow_with_error(workflow_id, results, "Graph building failed")
            
            # Step 6: Calculate PageRank scores
            print("Step 6: Calculating PageRank scores...")
            results["steps"]["pagerank"] = self._execute_pagerank_calculation(workflow_id)
            if results["steps"]["pagerank"]["status"] == "error":
                return self._complete_workflow_with_error(workflow_id, results, "PageRank calculation failed")
            elif results["steps"]["pagerank"]["status"] == "warning":
                print(f"⚠️  PageRank calculation warning: {results['steps']['pagerank'].get('message', 'Unknown warning')}")
            
            # Step 7: Execute enhanced queries
            print("Step 7: Executing queries...")
            results["steps"]["query_execution"] = self._execute_enhanced_queries(workflow_id, queries)
            results["query_results"] = results["steps"]["query_execution"].get("results", {})
            
            # Step 8: Create visualizations
            print("Step 8: Creating visualizations...")
            results["steps"]["visualization"] = self._execute_visualization_creation(
                workflow_id,
                results["steps"]["pdf_loading"]["document"]["document_ref"]
            )
            results["visualizations"] = results["steps"]["visualization"].get("visualizations", {})
            
            # Step 9: Quality assessment and analysis
            print("Step 9: Analyzing quality metrics...")
            results["steps"]["quality_analysis"] = self._execute_quality_analysis(workflow_id, results)
            results["quality_assessment"] = results["steps"]["quality_analysis"].get("assessment", {})
            
            # Complete workflow
            execution_time = time.time() - start_time
            results["execution_time"] = execution_time
            results["status"] = "success"
            
            # Update workflow progress to completion
            self.workflow_service.update_workflow_progress(
                workflow_id,
                step_number=9,
                status="completed"
            )
            
            return results
            
        except Exception as e:
            error_msg = f"Enhanced workflow failed: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            return self._complete_workflow_with_error(workflow_id, results, error_msg)
    
    def _execute_pdf_loading(self, workflow_id: str, pdf_path: str) -> Dict[str, Any]:
        """Execute PDF loading step."""
        self.workflow_service.create_checkpoint(workflow_id, "load_pdf", 1, {"step": "loading_pdf"})
        
        pdf_result = self.pdf_loader.load_pdf(pdf_path)
        if pdf_result["status"] != "success":
            return {"status": "error", "error": pdf_result.get("error")}
        
        return {
            "status": "success",
            "document": pdf_result["document"],
            "confidence": pdf_result["document"]["confidence"],
            "text_length": len(pdf_result["document"]["text"])
        }
    
    def _execute_text_chunking(self, workflow_id: str, document: Dict[str, Any]) -> Dict[str, Any]:
        """Execute text chunking step."""
        self.workflow_service.create_checkpoint(workflow_id, "chunk_text", 2, {"step": "chunking_text"})
        
        chunk_result = self.text_chunker.chunk_text(
            document_ref=document["document_ref"],
            text=document["text"],
            document_confidence=document["confidence"]
        )
        
        if chunk_result["status"] != "success":
            return {"status": "error", "error": chunk_result.get("error")}
        
        return {
            "status": "success",
            "chunks": chunk_result["chunks"],
            "chunk_count": len(chunk_result["chunks"]),
            "total_tokens": chunk_result["total_tokens"]
        }
    
    def _execute_ontology_generation(self, workflow_id: str, domain_description: str, 
                                   existing_session_id: Optional[str] = None) -> Dict[str, Any]:
        """Execute ontology generation or loading step."""
        self.workflow_service.create_checkpoint(workflow_id, "generate_ontology", 3, {"step": "creating_ontology"})
        
        try:
            # Try to use existing ontology first
            if existing_session_id:
                session = self.ontology_storage.load_session(existing_session_id)
                if session:
                    self.current_ontology = session.final_ontology
                    self.graph_builder.set_ontology(self.current_ontology)
                    return {
                        "status": "success",
                        "method": "loaded_existing",
                        "session_id": existing_session_id,
                        "entity_types": len(self.current_ontology.entity_types),
                        "relationship_types": len(self.current_ontology.relationship_types)
                    }
            
            # Generate new ontology
            if self.use_real_ontology:
                try:
                    # Use real Gemini generation
                    messages = [{"role": "user", "content": domain_description}]
                    self.current_ontology = self.ontology_generator.generate_from_conversation(
                        messages=messages,
                        temperature=0.7,
                        constraints={"max_entities": 8, "max_relations": 6}
                    )
                    
                    # Save session
                    session = OntologySession(
                        session_id=f"enhanced_workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        created_at=datetime.now(),
                        conversation_history=messages,
                        initial_ontology=self.current_ontology,
                        refinements=[],
                        final_ontology=self.current_ontology,
                        generation_parameters={"temperature": 0.7, "method": "enhanced_workflow"}
                    )
                    session_id = self.ontology_storage.save_session(session)
                    
                    method = "generated_with_gemini"
                    
                except Exception as gemini_error:
                    # Fallback to mock ontology if Gemini fails
                    logger.warning(f"Gemini ontology generation failed: {gemini_error}, falling back to mock ontology")
                    self.current_ontology = self._create_mock_climate_ontology()
                    session_id = None
                    method = "fallback_to_mock"
                    
            else:
                # Use mock ontology for testing
                self.current_ontology = self._create_mock_climate_ontology()
                session_id = None
                method = "mock_generated"
            
            # Set ontology for graph builder
            self.graph_builder.set_ontology(self.current_ontology)
            
            return {
                "status": "success",
                "method": method,
                "session_id": session_id,
                "entity_types": len(self.current_ontology.entity_types),
                "relationship_types": len(self.current_ontology.relationship_types)
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _execute_ontology_aware_extraction(self, workflow_id: str, chunks: List[Dict], 
                                         document_ref: str) -> Dict[str, Any]:
        """Execute ontology-aware entity extraction."""
        self.workflow_service.create_checkpoint(workflow_id, "extract_entities", 4, {"step": "ontology_extraction"})
        
        try:
            all_entities = []
            all_relationships = []
            all_mentions = []
            
            for i, chunk in enumerate(chunks):
                extraction_result = self.ontology_extractor.extract_entities(
                    text=chunk["text"],
                    ontology=self.current_ontology,
                    source_ref=f"{document_ref}_chunk_{i}",
                    confidence_threshold=self.confidence_threshold
                )
                
                all_entities.extend(extraction_result.entities)
                all_relationships.extend(extraction_result.relationships)
                all_mentions.extend(extraction_result.mentions)
            
            # Create consolidated extraction result
            consolidated_result = ExtractionResult(
                entities=all_entities,
                relationships=all_relationships,
                mentions=all_mentions,
                extraction_metadata={
                    "ontology_domain": self.current_ontology.domain_name,
                    "total_chunks": len(chunks),
                    "confidence_threshold": self.confidence_threshold
                }
            )
            
            # Count entity types
            entity_type_counts = {}
            for entity in all_entities:
                entity_type_counts[entity.entity_type] = entity_type_counts.get(entity.entity_type, 0) + 1
            
            return {
                "status": "success",
                "extraction_result": consolidated_result,
                "total_entities": len(all_entities),
                "total_relationships": len(all_relationships),
                "total_mentions": len(all_mentions),
                "entity_type_distribution": entity_type_counts,
                "avg_confidence": sum(e.confidence for e in all_entities) / len(all_entities) if all_entities else 0
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _execute_enhanced_graph_building(self, workflow_id: str, extraction_result: ExtractionResult,
                                       document_ref: str) -> Dict[str, Any]:
        """Execute enhanced graph building with semantic validation."""
        self.workflow_service.create_checkpoint(workflow_id, "build_graph", 5, {"step": "building_graph"})
        
        try:
            build_result = self.graph_builder.build_graph_from_extraction(
                extraction_result=extraction_result,
                source_document=document_ref
            )
            
            return {
                "status": "success",
                "build_result": build_result,
                "entities_created": build_result.entities_created,
                "relationships_created": build_result.relationships_created,
                "ontology_coverage": build_result.metrics.ontology_coverage,
                "semantic_density": build_result.metrics.semantic_density,
                "warnings": build_result.warnings,
                "errors": build_result.errors
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _execute_pagerank_calculation(self, workflow_id: str) -> Dict[str, Any]:
        """Execute PageRank calculation with Phase 2 compatibility."""
        self.workflow_service.create_checkpoint(workflow_id, "calculate_pagerank", 6, {"step": "calculating_pagerank"})
        
        try:
            pagerank_result = self.pagerank_calculator.calculate_pagerank()
            if pagerank_result["status"] == "success":
                return {
                    "status": "success",
                    "entities_updated": pagerank_result.get("entities_updated", 0),
                    "average_score": pagerank_result.get("average_score", 0.0),
                    "top_entities": pagerank_result.get("ranked_entities", [])[:10],  # Get top 10
                    "total_entities": pagerank_result.get("total_entities", 0),
                    "graph_stats": pagerank_result.get("graph_stats", {})
                }
            else:
                # If PageRank fails, continue with warning but don't fail the whole workflow
                logger.warning(f"PageRank calculation failed: {pagerank_result.get('error', 'Unknown error')}")
                return {
                    "status": "warning",
                    "error": pagerank_result.get("error", "PageRank failed"),
                    "entities_updated": 0,
                    "average_score": 0.0,
                    "top_entities": [],
                    "message": "PageRank failed but workflow continued"
                }
                
        except Exception as e:
            # If PageRank fails completely, continue with warning
            logger.warning(f"PageRank calculation exception: {str(e)}")
            return {
                "status": "warning",
                "error": str(e),
                "entities_updated": 0,
                "average_score": 0.0,
                "top_entities": [],
                "message": "PageRank failed but workflow continued"
            }
    
    def _execute_enhanced_queries(self, workflow_id: str, queries: List[str]) -> Dict[str, Any]:
        """Execute enhanced multi-hop queries."""
        self.workflow_service.create_checkpoint(workflow_id, "execute_queries", 7, {"step": "executing_queries"})
        
        try:
            query_results = {}
            for i, query in enumerate(queries):
                result = self.query_engine.execute_query(query)
                query_results[f"query_{i+1}"] = {
                    "question": query,
                    "result": result,
                    "status": result.get("status", "unknown")
                }
            
            successful_queries = sum(1 for r in query_results.values() if r["status"] == "success")
            
            return {
                "status": "success",
                "results": query_results,
                "total_queries": len(queries),
                "successful_queries": successful_queries,
                "success_rate": successful_queries / len(queries) if queries else 0
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _execute_visualization_creation(self, workflow_id: str, document_ref: str) -> Dict[str, Any]:
        """Execute visualization creation."""
        self.workflow_service.create_checkpoint(workflow_id, "create_visualizations", 8, {"step": "creating_visualizations"})
        
        try:
            config = GraphVisualizationConfig(
                max_nodes=100,
                max_edges=200,
                color_by="entity_type",
                confidence_threshold=self.confidence_threshold
            )
            
            # Fetch graph data
            vis_data = self.visualizer.fetch_graph_data(
                source_document=document_ref,
                ontology_domain=self.current_ontology.domain_name if self.current_ontology else None,
                config=config
            )
            
            # Create different visualizations
            visualizations = {}
            
            try:
                main_plot = self.visualizer.create_interactive_plot(vis_data, config)
                visualizations["main_graph"] = "Interactive graph created successfully"
            except Exception as e:
                visualizations["main_graph"] = f"Failed: {str(e)}"
            
            try:
                structure_plot = self.visualizer.create_ontology_structure_plot(vis_data.ontology_info)
                visualizations["ontology_structure"] = "Ontology structure plot created successfully"
            except Exception as e:
                visualizations["ontology_structure"] = f"Failed: {str(e)}"
            
            try:
                similarity_plot = self.visualizer.create_semantic_similarity_heatmap(vis_data)
                visualizations["similarity_heatmap"] = "Semantic similarity heatmap created successfully"
            except Exception as e:
                visualizations["similarity_heatmap"] = f"Failed: {str(e)}"
            
            return {
                "status": "success",
                "visualizations": visualizations,
                "graph_data": {
                    "nodes": len(vis_data.nodes),
                    "edges": len(vis_data.edges),
                    "metrics": vis_data.metrics
                }
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _execute_quality_analysis(self, workflow_id: str, results: Dict[str, Any]) -> Dict[str, Any]:
        """Execute comprehensive quality analysis."""
        self.workflow_service.create_checkpoint(workflow_id, "analyze_quality", 9, {"step": "analyzing_quality"})
        
        try:
            assessment = {
                "overall_score": 0.0,
                "component_scores": {},
                "recommendations": [],
                "metrics": {}
            }
            
            # Ontology quality
            if "ontology_generation" in results["steps"]:
                ontology_step = results["steps"]["ontology_generation"]
                ontology_score = 1.0 if ontology_step["status"] == "success" else 0.0
                assessment["component_scores"]["ontology_generation"] = ontology_score
                assessment["metrics"]["entity_types"] = ontology_step.get("entity_types", 0)
                assessment["metrics"]["relationship_types"] = ontology_step.get("relationship_types", 0)
            
            # Extraction quality
            if "entity_extraction" in results["steps"]:
                extraction_step = results["steps"]["entity_extraction"]
                if extraction_step["status"] == "success":
                    entity_count = extraction_step.get("total_entities", 0)
                    avg_confidence = extraction_step.get("avg_confidence", 0)
                    extraction_score = min(1.0, (entity_count / 10) * 0.5 + avg_confidence * 0.5)
                else:
                    extraction_score = 0.0
                assessment["component_scores"]["entity_extraction"] = extraction_score
                assessment["metrics"]["entities_extracted"] = extraction_step.get("total_entities", 0)
                assessment["metrics"]["avg_extraction_confidence"] = extraction_step.get("avg_confidence", 0)
            
            # Graph building quality
            if "graph_building" in results["steps"]:
                graph_step = results["steps"]["graph_building"]
                if graph_step["status"] == "success":
                    coverage = graph_step.get("ontology_coverage", 0)
                    density = graph_step.get("semantic_density", 0)
                    graph_score = coverage * 0.6 + min(1.0, density) * 0.4
                else:
                    graph_score = 0.0
                assessment["component_scores"]["graph_building"] = graph_score
                assessment["metrics"]["ontology_coverage"] = graph_step.get("ontology_coverage", 0)
                assessment["metrics"]["semantic_density"] = graph_step.get("semantic_density", 0)
            
            # Query performance
            if "query_execution" in results["steps"]:
                query_step = results["steps"]["query_execution"]
                query_score = query_step.get("success_rate", 0)
                assessment["component_scores"]["query_performance"] = query_score
                assessment["metrics"]["query_success_rate"] = query_step.get("success_rate", 0)
            
            # Calculate overall score
            scores = list(assessment["component_scores"].values())
            assessment["overall_score"] = sum(scores) / len(scores) if scores else 0.0
            
            # Generate recommendations
            if assessment["overall_score"] < 0.7:
                assessment["recommendations"].append("Consider improving ontology specificity for better extraction")
            if assessment["component_scores"].get("query_performance", 0) < 0.5:
                assessment["recommendations"].append("Query engine may need enhancement for better question answering")
            if assessment["metrics"].get("ontology_coverage", 0) < 0.8:
                assessment["recommendations"].append("Ontology may be missing important entity or relationship types")
            
            return {
                "status": "success",
                "assessment": assessment
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _create_mock_climate_ontology(self) -> DomainOntology:
        """Create mock climate ontology for testing when Gemini is not available."""
        from src.ontology_generator import EntityType, RelationshipType
        
        return DomainOntology(
            domain_name="Climate Change Analysis",
            domain_description="Domain ontology for climate change research and policy analysis",
            entity_types=[
                EntityType(name="CLIMATE_POLICY", description="Climate policies and agreements", 
                          examples=["Paris Agreement", "Carbon Tax"], attributes=["scope", "target"]),
                EntityType(name="CLIMATE_ORGANIZATION", description="Organizations working on climate", 
                          examples=["IPCC", "IEA"], attributes=["type", "focus"]),
                EntityType(name="ENVIRONMENTAL_IMPACT", description="Environmental effects", 
                          examples=["Sea Level Rise", "Warming"], attributes=["severity", "region"]),
                EntityType(name="RENEWABLE_TECHNOLOGY", description="Clean energy technologies", 
                          examples=["Solar", "Wind"], attributes=["efficiency", "cost"])
            ],
            relationship_types=[
                RelationshipType(name="ADDRESSES", description="Policy addresses impact", 
                               source_types=["CLIMATE_POLICY"], target_types=["ENVIRONMENTAL_IMPACT"], examples=[]),
                RelationshipType(name="IMPLEMENTS", description="Organization implements policy", 
                               source_types=["CLIMATE_ORGANIZATION"], target_types=["CLIMATE_POLICY"], examples=[]),
                RelationshipType(name="DEVELOPS", description="Organization develops technology", 
                               source_types=["CLIMATE_ORGANIZATION"], target_types=["RENEWABLE_TECHNOLOGY"], examples=[])
            ],
            extraction_patterns=["Look for climate policies", "Identify organizations", "Find environmental impacts"],
            created_by_conversation="Mock ontology for enhanced workflow testing"
        )
    
    def _complete_workflow_with_error(self, workflow_id: str, results: Dict[str, Any], error_msg: str) -> Dict[str, Any]:
        """Complete workflow with error state."""
        results["status"] = "error"
        results["error"] = error_msg
        results["execution_time"] = time.time() - results.get("start_time", time.time())
        
        # Update workflow progress to error state
        self.workflow_service.update_workflow_progress(
            workflow_id,
            step_number=0,
            status="error",
            error_message=error_msg
        )
        
        return results
    
    def _count_types(self, items: List[Dict], type_field: str) -> Dict[str, int]:
        """Count occurrences of types in a list of items."""
        counts = {}
        for item in items:
            item_type = item.get(type_field, "unknown")
            counts[item_type] = counts.get(item_type, 0) + 1
        return counts
    
    def cleanup(self):
        """Clean up resources."""
        try:
            if hasattr(self.graph_builder, 'close'):
                self.graph_builder.close()
            if hasattr(self.visualizer, 'close'):
                self.visualizer.close()
            logger.info("✅ Enhanced workflow resources cleaned up")
        except Exception as e:
            logger.warning(f"Cleanup warning: {e}")


def demonstrate_enhanced_workflow():
    """Demonstrate the enhanced workflow with a sample document."""
    print("🚀 Demonstrating Enhanced Vertical Slice Workflow")
    
    # Create sample climate policy document
    test_pdf_path = "./data/test_docs/climate_policy_analysis.pdf"
    os.makedirs(os.path.dirname(test_pdf_path), exist_ok=True)
    
    # Use existing test document if available
    if not os.path.exists(test_pdf_path):
        print("⚠️  Test PDF not found, using text-based analysis")
        test_pdf_path = None
    
    # Initialize workflow
    workflow = EnhancedVerticalSliceWorkflow()
    
    try:
        # Define analysis parameters
        domain_description = """
        I need to analyze climate change policy documents to understand:
        - Climate policies and international agreements
        - Organizations involved in climate action
        - Environmental impacts being addressed
        - Renewable energy technologies mentioned
        - Geographic regions affected by climate change
        """
        
        queries = [
            "What climate policies are mentioned in this document?",
            "Which organizations are working on climate solutions?",
            "What environmental impacts are discussed?",
            "What renewable energy technologies are mentioned?"
        ]
        
        # Execute workflow
        if test_pdf_path and os.path.exists(test_pdf_path):
            results = workflow.execute_enhanced_workflow(
                pdf_path=test_pdf_path,
                domain_description=domain_description,
                queries=queries,
                workflow_name="demo_enhanced_workflow"
            )
        else:
            print("Using mock execution for demonstration...")
            # Would normally execute with real PDF
            results = {"status": "demo", "message": "Enhanced workflow demonstration complete"}
        
        print(f"✅ Enhanced workflow completed: {results.get('status')}")
        return results
        
    except Exception as e:
        print(f"❌ Enhanced workflow demonstration failed: {e}")
        return {"status": "error", "error": str(e)}
    
    finally:
        workflow.cleanup()


if __name__ == "__main__":
    demonstrate_enhanced_workflow()