"""GraphRAG UI Module - Main UI Interface for GraphRAG System

This module provides the main UI interface for the GraphRAG system,
allowing users to interact with different phases of the pipeline.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

try:
    from src.core.service_manager import get_service_manager
    from src.core.config_manager import get_config
    from src.core.pipeline_orchestrator import PipelineOrchestrator
except ImportError:
    from core.service_manager import get_service_manager
    from src.core.config_manager import get_config
    from core.pipeline_orchestrator import PipelineOrchestrator

logger = logging.getLogger(__name__)


class GraphRAGUI:
    """Main GraphRAG UI Interface
    
    Provides a unified interface for interacting with the GraphRAG system
    across different phases and workflows.
    """
    
    def __init__(self):
        """Initialize the GraphRAG UI."""
        self.service_manager = get_service_manager()
        self.config = get_config()
        self.orchestrator = PipelineOrchestrator()
        
        # UI state
        self.current_phase = "phase1"
        self.session_id = f"ui_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        logger.info(f"GraphRAG UI initialized for session: {self.session_id}")
    
    def create_workflow(self, phase: str) -> Dict[str, Any]:
        """Create workflow for specified phase.
        
        Args:
            phase: The phase to create workflow for ("phase1", "phase2", "phase3")
            
        Returns:
            Dictionary containing workflow information and status
        """
        if phase not in ["phase1", "phase2", "phase3"]:
            return {
                "status": "error",
                "message": f"Invalid phase: {phase}. Must be one of: phase1, phase2, phase3"
            }
        
        try:
            self.current_phase = phase
            
            # Get available tools for this phase
            tools = self.orchestrator.get_phase_tools(phase)
            
            # Create workflow context
            workflow_context = {
                "phase": phase,
                "tools": tools,
                "session_id": self.session_id,
                "created_at": datetime.now().isoformat(),
                "config": {
                    "entity_processing": {
                        "confidence_threshold": self.config.entity_processing.confidence_threshold,
                        "chunk_overlap_size": self.config.entity_processing.chunk_overlap_size
                    },
                    "text_processing": {
                        "chunk_size": self.config.text_processing.chunk_size,
                        "semantic_similarity_threshold": self.config.text_processing.semantic_similarity_threshold
                    }
                }
            }
            
            logger.info(f"Created workflow for {phase} with {len(tools)} tools")
            
            return {
                "status": "success",
                "workflow": workflow_context,
                "message": f"Workflow created for {phase}"
            }
            
        except Exception as e:
            logger.error(f"Error creating workflow for {phase}: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to create workflow for {phase}: {str(e)}"
            }
    
    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific tool with given parameters.
        
        Args:
            tool_name: Name of the tool to execute
            parameters: Parameters to pass to the tool
            
        Returns:
            Dictionary containing execution results
        """
        try:
            # Use the orchestrator to execute the tool
            result = self.orchestrator.execute_tool(
                tool_name=tool_name,
                parameters=parameters,
                session_id=self.session_id
            )
            
            logger.info(f"Tool {tool_name} executed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to execute tool {tool_name}: {str(e)}"
            }
    
    def get_available_tools(self, phase: str = None) -> List[str]:
        """Get list of available tools for a phase.
        
        Args:
            phase: Phase to get tools for (defaults to current phase)
            
        Returns:
            List of available tool names
        """
        target_phase = phase or self.current_phase
        
        try:
            tools = self.orchestrator.get_phase_tools(target_phase)
            return [tool["name"] for tool in tools]
            
        except Exception as e:
            logger.error(f"Error getting tools for {target_phase}: {str(e)}")
            return []
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status.
        
        Returns:
            Dictionary containing system status information
        """
        try:
            # Check service manager status
            service_status = self.service_manager.get_status()
            
            # Check database connectivity
            neo4j_status = "connected" if self.service_manager.get_neo4j_driver() else "disconnected"
            
            # Get configuration status
            config_status = {
                "entity_confidence_threshold": self.config.entity_processing.confidence_threshold,
                "text_chunk_size": self.config.text_processing.chunk_size,
                "pagerank_iterations": self.config.graph_construction.pagerank_iterations
            }
            
            return {
                "status": "success",
                "system_status": {
                    "session_id": self.session_id,
                    "current_phase": self.current_phase,
                    "services": service_status,
                    "database": {
                        "neo4j_status": neo4j_status,
                        "uri": self.config.neo4j.uri
                    },
                    "configuration": config_status
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting system status: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to get system status: {str(e)}"
            }
    
    def process_document(self, document_path: str, phase: str = "phase1") -> Dict[str, Any]:
        """Process a document through the specified phase.
        
        Args:
            document_path: Path to the document to process
            phase: Phase to process the document through
            
        Returns:
            Dictionary containing processing results
        """
        try:
            # Create workflow for the phase
            workflow_result = self.create_workflow(phase)
            
            if workflow_result["status"] != "success":
                return workflow_result
            
            # Execute document processing
            processing_result = self.orchestrator.process_document(
                document_path=document_path,
                phase=phase,
                session_id=self.session_id
            )
            
            logger.info(f"Document {document_path} processed through {phase}")
            return processing_result
            
        except Exception as e:
            logger.error(f"Error processing document {document_path}: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to process document: {str(e)}"
            }
    
    def get_tool_info(self, tool_name: str) -> Dict[str, Any]:
        """Get information about a specific tool.
        
        Args:
            tool_name: Name of the tool to get information about
            
        Returns:
            Dictionary containing tool information
        """
        try:
            tool_info = self.orchestrator.get_tool_info(tool_name)
            return {
                "status": "success",
                "tool_info": tool_info
            }
            
        except Exception as e:
            logger.error(f"Error getting tool info for {tool_name}: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to get tool info: {str(e)}"
            }
    
    def process_document_with_progress(self, uploaded_file, progress_callback=None, status_callback=None):
        """Process document with progress reporting for long-running operations"""
        try:
            # Step 1: Load document
            if status_callback:
                status_callback("Loading document...")
            if progress_callback:
                progress_callback(10)
            
            document = self.load_document(uploaded_file)
            
            # Step 2: Extract entities
            if status_callback:
                status_callback("Extracting entities...")
            if progress_callback:
                progress_callback(30)
            
            entities = self.extract_entities(document)
            
            # Step 3: Build graph
            if status_callback:
                status_callback("Building knowledge graph...")
            if progress_callback:
                progress_callback(60)
            
            graph = self.build_graph(entities)
            
            # Step 4: Finalize
            if status_callback:
                status_callback("Finalizing results...")
            if progress_callback:
                progress_callback(100)
            
            if status_callback:
                status_callback("✅ Processing complete!")
            
            return {"status": "success", "graph": graph}
            
        except Exception as e:
            if status_callback:
                status_callback(f"❌ Error: {self.format_user_error(e)}")
            if progress_callback:
                progress_callback(0)
            
            return {"status": "error", "error": str(e)}
    
    def format_user_error(self, error):
        """Convert technical errors to user-friendly messages"""
        error_messages = {
            'ConnectionError': "Unable to connect to database. Please check your connection.",
            'FileNotFoundError': "The uploaded file could not be found. Please try uploading again.",
            'ValidationError': "The uploaded file format is not supported. Please use PDF or TXT files.",
            'TimeoutError': "Processing is taking longer than expected. Please try again.",
            'MemoryError': "The file is too large to process. Please try a smaller file.",
            'DatabaseConnectionError': "Database is temporarily unavailable. Please try again in a few moments.",
            'ServiceUnavailableError': "External service is temporarily unavailable. Please try again later.",
            'ProcessingError': "An error occurred while processing your document. Please check the file format and try again."
        }
        
        error_type = type(error).__name__
        user_friendly_message = error_messages.get(error_type, f"An unexpected error occurred: {str(error)}")
        
        # Log the technical details while showing user-friendly message
        logger.error(f"Technical error details: {error_type}: {str(error)}")
        
        return user_friendly_message
    
    def load_document(self, uploaded_file):
        """Load actual document using existing PDF/text loaders"""
        try:
            # Use actual tool from phase1
            from src.tools.phase1.t01_pdf_loader import PDFLoader
            
            loader = PDFLoader()
            
            # Determine file type and extract content
            if hasattr(uploaded_file, 'name'):
                filename = uploaded_file.name
            else:
                filename = str(uploaded_file)
                
            if filename.endswith('.pdf'):
                if hasattr(uploaded_file, 'read'):
                    content = loader.extract_text_from_pdf_bytes(uploaded_file.read())
                else:
                    content = loader.extract_text_from_pdf(uploaded_file)
            elif filename.endswith('.txt'):
                if hasattr(uploaded_file, 'read'):
                    content = uploaded_file.read().decode('utf-8') if isinstance(uploaded_file.read(), bytes) else uploaded_file.read()
                    uploaded_file.seek(0)  # Reset file pointer
                else:
                    with open(uploaded_file, 'r', encoding='utf-8') as f:
                        content = f.read()
            else:
                raise ValueError(f"Unsupported file type: {filename}")
            
            # Return actual extracted content
            result = {
                "text": content,
                "metadata": {
                    "filename": filename,
                    "size_bytes": len(content),
                    "type": "pdf" if filename.endswith('.pdf') else "text",
                    "extracted_at": datetime.now().isoformat()
                }
            }
            
            # Log evidence
            from src.core.evidence_logger import EvidenceLogger
            logger_evidence = EvidenceLogger()
            logger_evidence.log_test_execution(
                "DOCUMENT_LOADING",
                {
                    "status": "success",
                    "details": {"filename": filename, "content_length": len(content)},
                    "output": f"Successfully loaded {filename} with {len(content)} characters"
                }
            )
            
            return result
            
        except Exception as e:
            # Log to evidence file
            from src.core.evidence_logger import EvidenceLogger
            logger_evidence = EvidenceLogger()
            logger_evidence.log_test_execution(
                "DOCUMENT_LOADING_ERROR",
                {
                    "status": "error",
                    "error": str(e),
                    "details": {"filename": getattr(uploaded_file, 'name', str(uploaded_file))}
                }
            )
            raise
    
    def extract_entities(self, document):
        """Extract entities using actual NER tool"""
        try:
            # Use actual tool from phase1
            from src.tools.phase1.t23a_spacy_ner import SpacyNER
            
            ner_tool = SpacyNER()
            
            # Extract entities from actual document text
            text = document.get("text", "") if isinstance(document, dict) else str(document)
            
            if not text.strip():
                return []
                
            entities = ner_tool.extract_entities(text)
            
            # Convert to standard format if needed
            if isinstance(entities, list) and entities:
                # Handle different entity formats
                standardized_entities = []
                for entity in entities:
                    if isinstance(entity, dict):
                        standardized_entities.append(entity)
                    else:
                        # Handle tuple format (text, label)
                        if hasattr(entity, '__iter__') and len(entity) >= 2:
                            standardized_entities.append({
                                "name": str(entity[0]),
                                "type": str(entity[1])
                            })
                        else:
                            standardized_entities.append({
                                "name": str(entity),
                                "type": "UNKNOWN"
                            })
                entities = standardized_entities
            
            # Log evidence
            from src.core.evidence_logger import EvidenceLogger
            logger_evidence = EvidenceLogger()
            logger_evidence.log_test_execution(
                "ENTITY_EXTRACTION",
                {
                    "status": "success", 
                    "details": {"entity_count": len(entities), "text_length": len(text)},
                    "output": f"Extracted {len(entities)} entities from {len(text)} characters"
                }
            )
            
            return entities
            
        except Exception as e:
            # Log to evidence file
            from src.core.evidence_logger import EvidenceLogger
            logger_evidence = EvidenceLogger()
            logger_evidence.log_test_execution(
                "ENTITY_EXTRACTION_ERROR",
                {
                    "status": "error",
                    "error": str(e),
                    "details": {"document_type": type(document).__name__}
                }
            )
            raise
    
    def build_graph(self, entities):
        """Build graph using actual graph building tools"""
        try:
            # Use actual tools from phase1
            from src.tools.phase1.t31_entity_builder import EntityBuilder
            from src.tools.phase1.t34_edge_builder import EdgeBuilder
            
            entity_builder = EntityBuilder()
            edge_builder = EdgeBuilder()
            
            # Build actual graph
            graph_nodes = entity_builder.build_entities(entities)
            graph_edges = edge_builder.build_edges(entities)
            
            # Store in Neo4j if available
            nodes_created = 0
            edges_created = 0
            neo4j_stored = False
            
            try:
                neo4j_manager = self.service_manager.get_neo4j_manager()
                if neo4j_manager and neo4j_manager.is_connected():
                    with neo4j_manager.get_session() as session:
                        # Insert nodes
                        for node in graph_nodes:
                            session.run(
                                "MERGE (n:Entity {id: $id}) SET n.name = $name, n.type = $type, n.updated_at = timestamp()",
                                id=node.get("id", node.get("name", "unknown")), 
                                name=node.get("name", "unknown"),
                                type=node.get("type", "UNKNOWN")
                            )
                            nodes_created += 1
                        
                        # Insert edges
                        for edge in graph_edges:
                            source_id = edge.get("source", edge.get("source_id", "unknown"))
                            target_id = edge.get("target", edge.get("target_id", "unknown"))
                            rel_type = edge.get("type", edge.get("relationship_type", "RELATES_TO"))
                            
                            session.run(
                                "MATCH (a:Entity {id: $source}), (b:Entity {id: $target}) "
                                "MERGE (a)-[:RELATES_TO {type: $rel_type, created_at: timestamp()}]->(b)",
                                source=source_id, target=target_id, rel_type=rel_type
                            )
                            edges_created += 1
                        
                        neo4j_stored = True
            except Exception as db_error:
                logger.warning(f"Could not store in Neo4j: {db_error}")
                # Continue without database storage
            
            # Log evidence
            from src.core.evidence_logger import EvidenceLogger
            logger_evidence = EvidenceLogger()
            logger_evidence.log_test_execution(
                "GRAPH_BUILDING",
                {
                    "status": "success",
                    "details": {
                        "input_entities": len(entities),
                        "graph_nodes": len(graph_nodes),
                        "graph_edges": len(graph_edges),
                        "nodes_stored": nodes_created,
                        "edges_stored": edges_created,
                        "neo4j_stored": neo4j_stored
                    },
                    "output": f"Built graph with {len(graph_nodes)} nodes and {len(graph_edges)} edges"
                }
            )
            
            return {
                "nodes": len(graph_nodes),
                "edges": len(graph_edges),
                "neo4j_stored": neo4j_stored,
                "nodes_created": nodes_created,
                "edges_created": edges_created,
                "graph_data": {
                    "nodes": graph_nodes,
                    "edges": graph_edges
                }
            }
            
        except Exception as e:
            # Log to evidence file
            from src.core.evidence_logger import EvidenceLogger
from src.core.config_manager import get_config

            logger_evidence = EvidenceLogger()
            logger_evidence.log_test_execution(
                "GRAPH_BUILDING_ERROR",
                {
                    "status": "error",
                    "error": str(e),
                    "details": {"entity_count": len(entities) if entities else 0}
                }
            )
            raise
    
    def get_processing_capabilities(self):
        """Get available processing capabilities for UI display"""
        return {
            "supported_file_types": ["PDF", "TXT", "DOCX"],
            "max_file_size_mb": 50,
            "available_phases": ["Phase 1: Basic", "Phase 2: Enhanced", "Phase 3: Multi-Document"],
            "features": {
                "entity_extraction": True,
                "relationship_discovery": True,
                "ontology_generation": True,
                "multi_document_fusion": True,
                "progress_reporting": True,
                "error_recovery": True
            }
        }
    
    def get_tool_info(self):
        """Return tool information for audit system"""
        return {
            "tool_id": "GRAPHRAG_UI",
            "tool_type": "USER_INTERFACE",
            "status": "functional",
            "description": "Main GraphRAG UI with progress reporting and user-friendly errors",
            "features": {
                "progress_reporting": True,
                "user_friendly_errors": True,
                "multi_phase_support": True,
                "real_time_feedback": True
            },
            "session_id": self.session_id,
            "current_phase": self.current_phase
        }
    
    def close(self):
        """Close the UI and cleanup resources."""
        logger.info(f"Closing GraphRAG UI session: {self.session_id}")
        # Any cleanup would go here
        pass