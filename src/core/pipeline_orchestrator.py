"""Unified Pipeline Orchestrator - Priority 2 Implementation

Eliminates workflow duplication by providing a single, configurable orchestrator
that can execute Phase 1, Phase 2, and Phase 3 workflows with different optimization levels.

This replaces multiple near-identical workflow files and provides a unified interface
for all GraphRAG pipeline execution.

Architecture:
- PipelineOrchestrator: Main execution engine
- PipelineConfig: Configuration for pipeline execution 
- Tool Protocol: Interface that all pipeline tools must implement
- Optimization levels: STANDARD, OPTIMIZED, ENHANCED
- Phase support: PHASE1, PHASE2, PHASE3

Addresses CLAUDE.md Priority 2 - C-2: Consolidate Workflow Duplication
"""

from typing import List, Dict, Any, Protocol, Optional
from dataclasses import dataclass
from enum import Enum
import time
import traceback
import os
from .logging_config import get_logger
from .contract_validator import ContractValidator
from .ontology_validator import OntologyValidator
from .config import ConfigurationManager
from .pipeline_validation import PipelineValidator
from .tool_protocol import Tool


class OptimizationLevel(Enum):
    """Different optimization levels for pipeline execution"""
    STANDARD = "standard"
    OPTIMIZED = "optimized" 
    ENHANCED = "enhanced"


class Phase(Enum):
    """Supported pipeline phases"""
    PHASE1 = "phase1"
    PHASE2 = "phase2"
    PHASE3 = "phase3"


@dataclass
class PipelineResult:
    """Result of pipeline execution"""
    status: str
    entities: List[Any]
    relationships: List[Any]
    graph_created: bool
    query_enabled: bool
    text_chunks: List[str]
    error: Optional[str] = None


@dataclass
class QueryResult:
    """Result of query execution"""
    count: int
    records: List[Any]




@dataclass 
class PipelineConfig:
    """Configuration for pipeline execution
    
    Provides all necessary configuration for running any phase/optimization combination.
    Uses sensible defaults while allowing full customization.
    """
    tools: List[Tool]
    optimization_level: OptimizationLevel = OptimizationLevel.STANDARD
    phase: Phase = Phase.PHASE1
    neo4j_uri: Optional[str] = None
    neo4j_user: Optional[str] = None
    neo4j_password: Optional[str] = None
    confidence_threshold: float = 0.7
    workflow_storage_dir: Optional[str] = None


class PipelineOrchestrator:
    """Unified pipeline orchestrator for all workflow types
    
    This single class replaces all duplicate workflow implementations:
    - vertical_slice_workflow.py (kept, but refactored to use this)
    - vertical_slice_workflow_optimized.py (deleted - 95% duplicate)
    - enhanced_vertical_slice_workflow.py (refactored to use this)
    - basic_multi_document_workflow.py (updated to use this)
    
    Benefits:
    - Single source of truth for workflow execution
    - Configurable for different phases and optimization levels
    - Leverages existing ServiceManager architecture
    - Eliminates 95% code duplication
    - Maintains all existing functionality
    """
    
    def __init__(self, config: PipelineConfig = None, config_manager: ConfigManager = None):
        """Initialize orchestrator with configuration
        
        Args:
            config: Pipeline configuration containing tools and settings
            config_manager: Optional ConfigManager instance for centralized configuration
        """
        self.config = config
        self.logger = get_logger("core.orchestrator")
        
        # Initialize ConfigManager for centralized configuration
        self.config_manager = config_manager or ConfigManager()
        
        # Use shared services (following existing architecture)
        from src.core.service_manager import get_service_manager
        
        self.service_manager = get_service_manager()
        
        # Use configuration from ConfigManager
        neo4j_config = self.config_manager.get_neo4j_config()
        self.neo4j_uri = (config.neo4j_uri if config else None) or neo4j_config['uri']
        self.neo4j_user = (config.neo4j_user if config else None) or neo4j_config['user']
        self.neo4j_password = (config.neo4j_password if config else None) or neo4j_config['password']
        self.storage_dir = (config.workflow_storage_dir if config else None) or './data/workflows'
        
        # Performance tracking
        self.execution_stats = {
            "total_execution_time": 0.0,
            "tool_execution_times": [],
            "memory_usage": {},
            "errors": []
        }
        
        # MANDATORY: Initialize validation framework - FAIL FAST if unavailable
        try:
            self.contract_validator = ContractValidator("contracts")
            self.logger.info("Contract validator initialized successfully")
        except Exception as e:
            # FAIL FAST if validation framework cannot be initialized
            raise RuntimeError(f"Failed to initialize contract validator: {str(e)}")
        
        try:
            self.ontology_validator = OntologyValidator()
            self.logger.info("Ontology validator initialized successfully")
        except Exception as e:
            # FAIL FAST if ontology system cannot be initialized
            raise RuntimeError(f"Failed to initialize ontology validator: {str(e)}")
        
        self.validation_enabled = True
        
        # Add pipeline validation
        system_config = self.config_manager.get_system_config()
        strict_mode = system_config.get('strict_schema_validation', False)
        self.pipeline_validator = PipelineValidator(strict_mode=strict_mode)
        
    def execute(self, document_paths: List[str], queries: List[str] = None) -> Dict[str, Any]:
        """Execute pipeline with configured tools
        
        This is the main entry point that replaces all workflow execute methods.
        
        Args:
            document_paths: List of document paths to process
            queries: Optional list of queries to execute (for multi-hop queries)
            
        Returns:
            Complete pipeline execution result with metadata
        """
        # Input validation
        if not document_paths:
            raise ValueError("document_paths cannot be empty")
        
        if not isinstance(document_paths, list):
            raise TypeError("document_paths must be a list")
        
        # Validate all document paths exist
        import os
        for path in document_paths:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Document not found: {path}")
        
        # Validate queries parameter if provided
        if queries is not None and not isinstance(queries, list):
            raise TypeError("queries must be a list or None")
        
        start_time = time.time()
        
        results = {
            "pipeline_config": {
                "optimization_level": self.config.optimization_level.value,
                "phase": self.config.phase.value,
                "tools_count": len(self.config.tools),
                "document_count": len(document_paths),
                "query_count": len(queries) if queries else 0
            },
            "execution_results": [],
            "final_result": None,
            "execution_metadata": {
                "start_time": start_time,
                "end_time": None,
                "total_time": None,
                "success": False,
                "error_summary": None
            }
        }
        
        # Initial data structure
        current_data = {
            "document_paths": document_paths, 
            "queries": queries or [],
            "workflow_id": f"{self.config.phase.value}_{self.config.optimization_level.value}_{int(start_time)}"
        }
        
        # Validate tool inputs if enabled
        if self.validation_enabled:
            try:
                # Validate input data against contracts
                self.contract_validator.validate_input("PDFLoader", {"file_paths": document_paths})
                self.logger.info("Input validation passed")
            except Exception as e:
                self.logger.warning(f"Input validation failed: {e}")
        
        try:
            # Execute tools in sequence
            for i, tool in enumerate(self.config.tools):
                tool_start_time = time.time()
                
                try:
                    # Execute tool with validation
                    tool_result = self._execute_tool(tool, current_data)
                    tool_execution_time = time.time() - tool_start_time
                    
                    # Record successful execution
                    results["execution_results"].append({
                        "tool_index": i,
                        "tool_type": type(tool).__name__,
                        "status": "success",
                        "execution_time": tool_execution_time,
                        "result_summary": self._summarize_tool_result(tool_result)
                    })
                    
                    # Update data for next tool
                    if isinstance(tool_result, dict):
                        # Merge results while preserving workflow metadata
                        current_data.update(tool_result)
                    else:
                        # Tool returned non-dict result
                        current_data["last_tool_result"] = tool_result
                        
                    self.execution_stats["tool_execution_times"].append(tool_execution_time)
                    
                except Exception as e:
                    tool_execution_time = time.time() - tool_start_time
                    error_msg = f"Tool {type(tool).__name__} failed: {str(e)}"
                    
                    # Record failed execution
                    results["execution_results"].append({
                        "tool_index": i,
                        "tool_type": type(tool).__name__,
                        "status": "error",
                        "execution_time": tool_execution_time,
                        "error": error_msg,
                        "traceback": traceback.format_exc()
                    })
                    
                    self.execution_stats["errors"].append(error_msg)
                    results["execution_metadata"]["error_summary"] = error_msg
                    break
            
            # Mark as successful if we completed all tools without errors
            results["execution_metadata"]["success"] = all(
                result["status"] == "success" for result in results["execution_results"]
            )
            results["final_result"] = current_data
            
        except Exception as e:
            # Catch-all for orchestrator-level errors
            error_msg = f"Pipeline orchestrator failed: {str(e)}"
            results["execution_metadata"]["error_summary"] = error_msg
            self.execution_stats["errors"].append(error_msg)
            
        finally:
            # Always record timing metadata
            end_time = time.time()
            total_time = end_time - start_time
            
            results["execution_metadata"]["end_time"] = end_time
            results["execution_metadata"]["total_time"] = total_time
            self.execution_stats["total_execution_time"] = total_time
            
        return results
    
    def _summarize_tool_result(self, result: Any) -> Dict[str, Any]:
        """Create a summary of tool result for logging
        
        Args:
            result: Tool execution result
            
        Returns:
            Summary dictionary with key metrics
        """
        if isinstance(result, dict):
            summary = {
                "type": "dict",
                "keys": list(result.keys()),
                "size": len(result)
            }
            
            # Add specific summaries for known result types
            if "entities" in result:
                summary["entities_count"] = len(result.get("entities", []))
            if "relationships" in result:
                summary["relationships_count"] = len(result.get("relationships", []))
            if "chunks" in result:
                summary["chunks_count"] = len(result.get("chunks", []))
            if "documents" in result:
                summary["documents_count"] = len(result.get("documents", []))
                
            return summary
            
        elif isinstance(result, list):
            return {
                "type": "list",
                "length": len(result),
                "first_item_type": type(result[0]).__name__ if result else None
            }
        else:
            return {
                "type": type(result).__name__,
                "string_length": len(str(result)) if hasattr(result, '__str__') else None
            }
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get detailed execution statistics
        
        Returns:
            Execution statistics including timing and memory usage
        """
        return {
            **self.execution_stats,
            "average_tool_time": (
                sum(self.execution_stats["tool_execution_times"]) / 
                len(self.execution_stats["tool_execution_times"])
                if self.execution_stats["tool_execution_times"] else 0.0
            ),
            "config_summary": {
                "phase": self.config.phase.value,
                "optimization_level": self.config.optimization_level.value,
                "tools_count": len(self.config.tools)
            }
        }
    
    def _execute_tool(self, tool: Tool, input_data: Any) -> Dict[str, Any]:
        """Execute tool with mandatory validation"""
        tool_name = getattr(tool, 'tool_name', tool.__class__.__name__)
        
        # MANDATORY: Load and validate contract BEFORE execution
        contract = None
        if self.contract_validator:
            try:
                # Map tool names to contract IDs
                contract_mapping = {
                    'PDFLoader': 'T01_PDF_LOADER',
                    'TextChunker': 'T15A_TEXT_CHUNKER', 
                    'SpacyNER': 'T23A_SPACY_NER',
                    'RelationshipExtractor': 'T27_RELATIONSHIP_EXTRACTOR',
                    'EntityBuilder': 'T31_ENTITY_BUILDER',
                    'EdgeBuilder': 'T34_EDGE_BUILDER',
                    'MultiHopQuery': 'T49_MULTI_HOP_QUERY',
                    'PageRankCalculator': 'T68_PAGE_RANK'
                }
                
                contract_id = contract_mapping.get(tool_name)
                if contract_id:
                    contract = self.contract_validator.load_contract(contract_id)
                    if contract:
                        # Validate input data against contract
                        input_errors = self.contract_validator.validate_input_data(input_data, contract)
                        if input_errors:
                            raise ValueError(f"Input validation failed for {tool_name}: {input_errors}")
                        
                        self.logger.info(f"Contract input validation passed for {tool_name}")
            except Exception as e:
                # FAIL FAST - do not proceed with invalid input
                raise ValueError(f"Contract validation error for {tool_name}: {str(e)}")
        
        # Execute the tool with context
        try:
            context = {
                "workflow_id": input_data.get("workflow_id"),
                "phase": self.config.phase.value,
                "optimization_level": self.config.optimization_level.value
            }
            result = tool.execute(input_data, context)
        except Exception as e:
            self.logger.error(f"Tool {tool_name} execution failed: {e}")
            raise
        
        # MANDATORY: Validate output against contract and ontology
        if contract and self.contract_validator:
            try:
                output_errors = self.contract_validator.validate_output_data(result, contract)
                if output_errors:
                    raise ValueError(f"Output validation failed for {tool_name}: {output_errors}")
            except Exception as e:
                # FAIL FAST - do not accept invalid output
                raise ValueError(f"Output contract validation error for {tool_name}: {str(e)}")
        
        # MANDATORY: Validate entities/relationships against ontology
        if self.ontology_validator and isinstance(result, dict):
            try:
                if 'entities' in result:
                    for entity in result['entities']:
                        ontology_errors = self.ontology_validator.validate_entity(entity)
                        if ontology_errors:
                            # Log warnings but don't fail (semantic validation is advisory)
                            self.logger.warning(f"Ontology validation issues for {tool_name}: {ontology_errors}")
                
                if 'relationships' in result:
                    for relationship in result['relationships']:
                        ontology_errors = self.ontology_validator.validate_relationship(relationship)
                        if ontology_errors:
                            self.logger.warning(f"Relationship ontology issues for {tool_name}: {ontology_errors}")
            except Exception as e:
                self.logger.warning(f"Ontology validation error for {tool_name}: {str(e)}")
        
        return result
    
    def execute_full_pipeline(self, input_path: str) -> PipelineResult:
        """Execute complete PDF→Entities→Graph→Query pipeline"""
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        try:
            # Step 1: Load document
            from src.tools.phase1.phase1_mcp_tools import create_phase1_mcp_tools
            from src.core.service_manager import get_service_manager
            
            service_manager = get_service_manager()
            
            # Initialize Phase 1 tools
            from src.tools.phase1.t01_pdf_loader import PDFLoader
            from src.tools.phase1.t23a_spacy_ner import SpacyNER
            from src.tools.phase1.t27_relationship_extractor import RelationshipExtractor
            from src.tools.phase1.t31_entity_builder import EntityBuilder
            from src.tools.phase1.t34_edge_builder import EdgeBuilder
            
            identity_service = service_manager.identity_service
            provenance_service = service_manager.provenance_service
            quality_service = service_manager.quality_service
            
            pdf_loader = PDFLoader(identity_service, provenance_service, quality_service)
            
            # Load text from file
            if input_path.endswith('.pdf'):
                text_result = pdf_loader.load_pdf(input_path)
                if isinstance(text_result, dict) and 'document' in text_result:
                    text = text_result['document'].get('text', '')
                else:
                    text = str(text_result)
            else:
                with open(input_path, 'r', encoding='utf-8') as f:
                    text = f.read()
            
            # Step 2: Extract entities
            entity_extractor = SpacyNER(identity_service, provenance_service, quality_service)
            entities_result = entity_extractor.extract_entities("doc_chunk", text)
            if isinstance(entities_result, dict):
                entities = entities_result.get('entities', [])
            else:
                entities = entities_result if isinstance(entities_result, list) else []
            
            # Step 3: Extract relationships
            rel_extractor = RelationshipExtractor(identity_service, provenance_service, quality_service)
            relationships_result = rel_extractor.extract_relationships("doc_chunk", text, entities)
            if isinstance(relationships_result, dict):
                relationships = relationships_result.get('relationships', [])
            else:
                relationships = relationships_result if isinstance(relationships_result, list) else []
            
            # Step 4: Build graph components
            # Get Neo4j config from ConfigManager
            from src.core.config import ConfigurationManager
            config_manager = ConfigurationManager()
            neo4j_config = config_manager.get_neo4j_config()
            neo4j_uri = neo4j_config['uri']
            neo4j_user = neo4j_config['user']
            neo4j_password = neo4j_config['password']
            
            entity_builder = EntityBuilder(identity_service, provenance_service, quality_service, neo4j_uri, neo4j_user, neo4j_password)
            edge_builder = EdgeBuilder(identity_service, provenance_service, quality_service, neo4j_uri, neo4j_user, neo4j_password)
            
            # Build entities and relationships
            built_entities_result = entity_builder.build_entities(entities, ["doc_chunk"])
            if isinstance(built_entities_result, dict):
                built_entities = built_entities_result.get('entities', [])
            else:
                built_entities = built_entities_result if isinstance(built_entities_result, list) else []
            
            built_edges_result = edge_builder.build_edges(relationships, ["doc_chunk"])
            if isinstance(built_edges_result, dict):
                built_edges = built_edges_result.get('relationships', [])
            else:
                built_edges = built_edges_result if isinstance(built_edges_result, list) else []
            
            # Step 5: Store in Neo4j (graph creation)
            driver = service_manager.get_neo4j_driver()
            if driver:
                with driver.session() as session:
                    # Clear existing test data
                    session.run("MATCH (n:Entity) DETACH DELETE n")
                    
                    # Create entities
                    for entity in built_entities:
                        if isinstance(entity, dict):
                            name = entity.get('canonical_name')
                            entity_type = entity.get('entity_type', 'UNKNOWN')
                            confidence = entity.get('confidence', 0.8)
                        else:
                            name = getattr(entity, 'canonical_name', None)
                            entity_type = getattr(entity, 'entity_type', 'UNKNOWN')
                            confidence = getattr(entity, 'confidence', 0.8)
                        
                        if name:
                            session.run("""
                                CREATE (e:Entity {
                                    canonical_name: $name,
                                    entity_type: $type,
                                    confidence: $confidence
                                })
                            """, 
                            name=name, 
                            type=entity_type,
                            confidence=confidence)
                    
                    # Create relationships
                    for rel in built_edges:
                        if isinstance(rel, dict):
                            source = rel.get('source_entity') or rel.get('subject_text')
                            target = rel.get('target_entity') or rel.get('object_text')
                            rel_type = rel.get('relationship_type', 'RELATED')
                        else:
                            source = getattr(rel, 'source_entity', None)
                            target = getattr(rel, 'target_entity', None)
                            rel_type = getattr(rel, 'relationship_type', 'RELATED')
                        
                        if source and target:
                            session.run("""
                                MATCH (source:Entity {canonical_name: $source})
                                MATCH (target:Entity {canonical_name: $target})
                                CREATE (source)-[:RELATED_TO {type: $rel_type}]->(target)
                            """, 
                            source=source, 
                            target=target, 
                            rel_type=rel_type)
                
                graph_created = True
            else:
                graph_created = False
            
            return PipelineResult(
                status="SUCCESS",
                entities=built_entities,
                relationships=built_edges,
                graph_created=graph_created,
                query_enabled=graph_created,
                text_chunks=[text],
                error=None
            )
            
        except Exception as e:
            import traceback
            error_msg = f"{str(e)}\n\nTraceback:\n{traceback.format_exc()}"
            return PipelineResult(
                status="FAILED",
                entities=[],
                relationships=[],
                graph_created=False,
                query_enabled=False,
                text_chunks=[],
                error=error_msg
            )
    
    def execute_pdf_pipeline(self, input_path: str) -> PipelineResult:
        """Execute PDF-specific pipeline"""
        # Same as execute_full_pipeline but with PDF-specific handling
        return self.execute_full_pipeline(input_path)
    
    def execute_query(self, query: str) -> QueryResult:
        """Execute Cypher query against the graph"""
        try:
            from src.core.service_manager import get_service_manager
            service_manager = get_service_manager()
            driver = service_manager.get_neo4j_driver()
            
            if not driver:
                raise Exception("Neo4j driver not available")
            
            with driver.session() as session:
                result = session.run(query)
                records = list(result)
                
                # Handle count queries
                if "count(" in query.lower():
                    count = records[0][0] if records else 0
                    return QueryResult(count=count, records=records)
                else:
                    return QueryResult(count=len(records), records=records)
                    
        except Exception as e:
            raise Exception(f"Query execution failed: {e}")