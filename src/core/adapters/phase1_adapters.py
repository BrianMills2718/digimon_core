"""
Phase 1 Tool Adapters

Extracted from tool_adapters.py - Adapters for Phase 1 document processing tools.
These adapters bridge the unified Tool protocol to specific Phase 1 tool interfaces.
"""

from typing import Any, Dict, List, Optional
from ..logging_config import get_logger
from ..config_manager import ConfigurationManager
from ..tool_protocol import ToolExecutionError, ToolValidationError, ToolValidationResult
from .base_adapters import BaseToolAdapter

logger = get_logger("core.adapters.phase1")


class PDFLoaderAdapter(BaseToolAdapter):
    """Adapter for PDFLoader to implement Tool protocol
    
    Converts PipelineOrchestrator Tool protocol to PDFLoader.load_pdf interface.
    Handles document path iteration and result aggregation.
    """
    
    def __init__(self, config_manager: ConfigurationManager = None):
        super().__init__(config_manager)
        
        # Import and initialize tool with error handling
        try:
            from ...tools.phase1.t01_pdf_loader_unified import PDFLoaderUnified as _PDFLoader
            self._tool = _PDFLoader(self.identity_service, self.provenance_service, self.quality_service)
        except ImportError as e:
            logger.error(f"Failed to import PDFLoaderUnified: {e}")
            self._tool = None
            
        self.tool_name = "PDFLoaderAdapter"
    
    def execute(self, input_data: Any, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Convert Tool protocol to PDFLoader interface"""
        if self._tool is None:
            raise ToolExecutionError("PDFLoaderAdapter", "PDFLoaderUnified not available")
            
        validation_result = self.validate_input(input_data)
        if not validation_result.is_valid:
            raise ToolValidationError("PDFLoaderAdapter", validation_result.validation_errors)
        
        try:
            return self._execute_original(input_data)
        except Exception as e:
            raise ToolExecutionError("PDFLoaderAdapter", str(e), e)
    
    def _execute_original(self, input_data: Any) -> Dict[str, Any]:
        """Original execution logic"""
        document_paths = input_data["document_paths"]
        documents = []
        
        for path in document_paths:
            try:
                # Call actual tool method
                result = self._tool.load_pdf(path)
                
                if result.get("status") == "success":
                    # Extract document data from tool result
                    if "document" in result:
                        doc_info = result["document"]
                        doc_data = {
                            "document_id": doc_info.get("document_id"),
                            "file_path": path,
                            "text": doc_info.get("text", ""),
                            "metadata": doc_info.get("metadata", {}),
                            "confidence": doc_info.get("confidence", 0.0),
                            "operation_id": result.get("operation_id")
                        }
                    else:
                        # Fallback to old format
                        doc_data = {
                            "document_id": result.get("document_id"),
                            "file_path": path,
                            "text": result.get("text", ""),
                            "metadata": result.get("metadata", {}),
                            "confidence": result.get("confidence", 0.0),
                            "operation_id": result.get("operation_id")
                        }
                    documents.append(doc_data)
                else:
                    logger.warning("PDF loading failed for %s: %s", path, result.get("error"))
                    documents.append({
                        "document_id": None,
                        "file_path": path,
                        "text": "",
                        "metadata": {"error": result.get("error")},
                        "confidence": 0.0
                    })
                    
            except Exception as e:
                logger.error("Exception loading PDF %s: %s", path, str(e))
                documents.append({
                    "document_id": None,
                    "file_path": path,
                    "text": "",
                    "metadata": {"exception": str(e)},
                    "confidence": 0.0
                })
        
        return {
            "documents": documents,
            **input_data  # Pass through other data
        }

    def get_tool_info(self) -> Dict[str, Any]:
        """Get PDFLoader tool information"""
        return {
            "name": "PDF Loader",
            "version": "1.0",
            "description": "Loads PDF documents and extracts text content",
            "contract_id": "T01_PDFLoader",
            "capabilities": ["pdf_loading", "text_extraction", "document_processing"]
        }

    def validate_input(self, input_data: Dict[str, Any]) -> ToolValidationResult:
        """Validate PDFLoader input"""
        errors = []
        
        if not isinstance(input_data, dict):
            errors.append("Input data must be a dictionary")
        elif "document_paths" not in input_data:
            errors.append("Missing required field: document_paths")
        elif not isinstance(input_data["document_paths"], list):
            errors.append("document_paths must be a list")
        elif len(input_data["document_paths"]) == 0:
            errors.append("document_paths list cannot be empty")
        else:
            for i, path in enumerate(input_data["document_paths"]):
                if not isinstance(path, str):
                    errors.append(f"document_paths[{i}] must be a string")
                elif "../" in path:
                    errors.append(f"Path traversal detected in document_paths[{i}]")
        
        return ToolValidationResult(
            is_valid=len(errors) == 0,
            validation_errors=errors,
            method_signatures={},
            execution_test_results={},
            input_schema_validation={"valid": len(errors) == 0, "errors": errors},
            security_validation={"valid": True, "errors": []},
            performance_validation={"valid": True, "errors": []}
        )


class TextChunkerAdapter(BaseToolAdapter):
    """Adapter for TextChunker to implement Tool protocol"""
    
    def __init__(self, config_manager: ConfigurationManager = None):
        super().__init__(config_manager)
        
        try:
            from ...tools.phase1.t15a_text_chunker_unified import TextChunkerUnified as _TextChunker
            self._tool = _TextChunker(self.identity_service, self.provenance_service, self.quality_service)
        except ImportError as e:
            logger.error(f"Failed to import TextChunkerUnified: {e}")
            self._tool = None
            
        self.tool_name = "TextChunkerAdapter"
    
    def execute(self, input_data: Any, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Convert Tool protocol to TextChunker interface"""
        if self._tool is None:
            raise ToolExecutionError("TextChunkerAdapter", "TextChunkerUnified not available")
            
        validation_result = self.validate_input(input_data)
        if not validation_result.is_valid:
            raise ToolValidationError("TextChunkerAdapter", validation_result.validation_errors)
        
        try:
            documents = input_data["documents"]
            chunks = []
            
            for doc in documents:
                if doc.get("text"):
                    result = self._tool.chunk_text(doc["text"], doc.get("document_id"))
                    if result.get("status") == "success":
                        chunks.extend(result.get("chunks", []))
            
            return {
                "chunks": chunks,
                **input_data  # Pass through other data
            }
        except Exception as e:
            raise ToolExecutionError("TextChunkerAdapter", str(e), e)
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get TextChunker tool information"""
        return {
            "name": "Text Chunker",
            "version": "1.0",
            "description": "Chunks text documents into manageable pieces",
            "contract_id": "T15A_TextChunker",
            "capabilities": ["text_chunking", "document_segmentation"]
        }

    def validate_input(self, input_data: Dict[str, Any]) -> ToolValidationResult:
        """Validate TextChunker input"""
        errors = []
        
        if not isinstance(input_data, dict):
            errors.append("Input data must be a dictionary")
        elif "documents" not in input_data:
            errors.append("Missing required field: documents")
        elif not isinstance(input_data["documents"], list):
            errors.append("documents must be a list")
        
        return ToolValidationResult(
            is_valid=len(errors) == 0,
            validation_errors=errors,
            method_signatures={},
            execution_test_results={},
            input_schema_validation={"valid": len(errors) == 0, "errors": errors},
            security_validation={"valid": True, "errors": []},
            performance_validation={"valid": True, "errors": []}
        )


class SpacyNERAdapter(BaseToolAdapter):
    """Adapter for SpaCy Named Entity Recognition"""
    
    def __init__(self, config_manager: ConfigurationManager = None):
        super().__init__(config_manager)
        
        try:
            from ...tools.phase1.t23a_spacy_ner_unified import SpacyNERUnified as _SpacyNER
            self._tool = _SpacyNER(self.identity_service, self.provenance_service, self.quality_service)
        except ImportError as e:
            logger.error(f"Failed to import SpacyNERUnified: {e}")
            self._tool = None
            
        self.tool_name = "SpacyNERAdapter"
    
    def execute(self, input_data: Any, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Convert Tool protocol to SpacyNER interface"""
        if self._tool is None:
            raise ToolExecutionError("SpacyNERAdapter", "SpacyNERUnified not available")
            
        validation_result = self.validate_input(input_data)
        if not validation_result.is_valid:
            raise ToolValidationError("SpacyNERAdapter", validation_result.validation_errors)
        
        try:
            chunks = input_data["chunks"]
            entities = []
            
            for chunk in chunks:
                if chunk.get("text"):
                    result = self._tool.extract_entities(chunk["text"], chunk.get("chunk_id"))
                    if result.get("status") == "success":
                        entities.extend(result.get("entities", []))
            
            return {
                "entities": entities,
                **input_data  # Pass through other data
            }
        except Exception as e:
            raise ToolExecutionError("SpacyNERAdapter", str(e), e)
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get SpacyNER tool information"""
        return {
            "name": "SpaCy Named Entity Recognition",
            "version": "1.0",
            "description": "Extracts named entities using SpaCy NLP models",
            "contract_id": "T23A_SpacyNER",
            "capabilities": ["named_entity_recognition", "nlp_processing"]
        }

    def validate_input(self, input_data: Dict[str, Any]) -> ToolValidationResult:
        """Validate SpacyNER input"""
        errors = []
        
        if not isinstance(input_data, dict):
            errors.append("Input data must be a dictionary")
        elif "chunks" not in input_data:
            errors.append("Missing required field: chunks")
        elif not isinstance(input_data["chunks"], list):
            errors.append("chunks must be a list")
        
        return ToolValidationResult(
            is_valid=len(errors) == 0,
            validation_errors=errors,
            method_signatures={},
            execution_test_results={},
            input_schema_validation={"valid": len(errors) == 0, "errors": errors},
            security_validation={"valid": True, "errors": []},
            performance_validation={"valid": True, "errors": []}
        )


class RelationshipExtractorAdapter(BaseToolAdapter):
    """Adapter for Relationship Extraction"""
    
    def __init__(self, config_manager: ConfigurationManager = None):
        super().__init__(config_manager)
        
        try:
            from ...tools.phase1.t27_relationship_extractor_unified import RelationshipExtractorUnified as _RelationshipExtractor
            self._tool = _RelationshipExtractor(self.identity_service, self.provenance_service, self.quality_service)
        except ImportError as e:
            logger.error(f"Failed to import RelationshipExtractorUnified: {e}")
            self._tool = None
            
        self.tool_name = "RelationshipExtractorAdapter"
    
    def execute(self, input_data: Any, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Convert Tool protocol to RelationshipExtractor interface"""
        if self._tool is None:
            raise ToolExecutionError("RelationshipExtractorAdapter", "RelationshipExtractorUnified not available")
            
        validation_result = self.validate_input(input_data)
        if not validation_result.is_valid:
            raise ToolValidationError("RelationshipExtractorAdapter", validation_result.validation_errors)
        
        try:
            entities = input_data["entities"]
            relationships = []
            
            # Group entities by chunk/document for relationship extraction
            entity_groups = {}
            for entity in entities:
                chunk_id = entity.get("chunk_id", "default")
                if chunk_id not in entity_groups:
                    entity_groups[chunk_id] = []
                entity_groups[chunk_id].append(entity)
            
            # Extract relationships for each group
            for chunk_id, chunk_entities in entity_groups.items():
                if len(chunk_entities) > 1:
                    result = self._tool.extract_relationships(chunk_entities)
                    if result.get("status") == "success":
                        relationships.extend(result.get("relationships", []))
            
            return {
                "relationships": relationships,
                **input_data  # Pass through other data
            }
        except Exception as e:
            raise ToolExecutionError("RelationshipExtractorAdapter", str(e), e)
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get RelationshipExtractor tool information"""
        return {
            "name": "Relationship Extractor",
            "version": "1.0",
            "description": "Extracts relationships between named entities",
            "contract_id": "T27_RelationshipExtractor",
            "capabilities": ["relationship_extraction", "entity_linking"]
        }

    def validate_input(self, input_data: Dict[str, Any]) -> ToolValidationResult:
        """Validate RelationshipExtractor input"""
        errors = []
        
        if not isinstance(input_data, dict):
            errors.append("Input data must be a dictionary")
        elif "entities" not in input_data:
            errors.append("Missing required field: entities")
        elif not isinstance(input_data["entities"], list):
            errors.append("entities must be a list")
        
        return ToolValidationResult(
            is_valid=len(errors) == 0,
            validation_errors=errors,
            method_signatures={},
            execution_test_results={},
            input_schema_validation={"valid": len(errors) == 0, "errors": errors},
            security_validation={"valid": True, "errors": []},
            performance_validation={"valid": True, "errors": []}
        )


class EntityBuilderAdapter(BaseToolAdapter):
    """Adapter for Entity Builder"""
    
    def __init__(self, config_manager: ConfigurationManager = None):
        super().__init__(config_manager)
        
        try:
            from ...tools.phase1.t31_entity_builder_unified import EntityBuilderUnified as _EntityBuilder
            self._tool = _EntityBuilder(self.identity_service, self.provenance_service, self.quality_service)
        except ImportError as e:
            logger.error(f"Failed to import EntityBuilderUnified: {e}")
            self._tool = None
            
        self.tool_name = "EntityBuilderAdapter"
    
    def execute(self, input_data: Any, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Convert Tool protocol to EntityBuilder interface"""
        if self._tool is None:
            raise ToolExecutionError("EntityBuilderAdapter", "EntityBuilderUnified not available")
            
        validation_result = self.validate_input(input_data)
        if not validation_result.is_valid:
            raise ToolValidationError("EntityBuilderAdapter", validation_result.validation_errors)
        
        try:
            entities = input_data["entities"]
            result = self._tool.build_entities(entities)
            
            return {
                "entity_results": result.get("entities", []) if result.get("status") == "success" else [],
                **input_data  # Pass through other data
            }
        except Exception as e:
            raise ToolExecutionError("EntityBuilderAdapter", str(e), e)
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get EntityBuilder tool information"""
        return {
            "name": "Entity Builder",
            "version": "1.0",
            "description": "Builds and stores entities in graph database",
            "contract_id": "T31_EntityBuilder",
            "capabilities": ["entity_building", "graph_storage"]
        }

    def validate_input(self, input_data: Dict[str, Any]) -> ToolValidationResult:
        """Validate EntityBuilder input"""
        errors = []
        
        if not isinstance(input_data, dict):
            errors.append("Input data must be a dictionary")
        elif "entities" not in input_data:
            errors.append("Missing required field: entities")
        elif not isinstance(input_data["entities"], list):
            errors.append("entities must be a list")
        
        return ToolValidationResult(
            is_valid=len(errors) == 0,
            validation_errors=errors,
            method_signatures={},
            execution_test_results={},
            input_schema_validation={"valid": len(errors) == 0, "errors": errors},
            security_validation={"valid": True, "errors": []},
            performance_validation={"valid": True, "errors": []}
        )


class EdgeBuilderAdapter(BaseToolAdapter):
    """Adapter for Edge Builder"""
    
    def __init__(self, config_manager: ConfigurationManager = None):
        super().__init__(config_manager)
        
        try:
            from ...tools.phase1.t34_edge_builder_unified import EdgeBuilderUnified as _EdgeBuilder
            self._tool = _EdgeBuilder(self.identity_service, self.provenance_service, self.quality_service)
        except ImportError as e:
            logger.error(f"Failed to import EdgeBuilderUnified: {e}")
            self._tool = None
            
        self.tool_name = "EdgeBuilderAdapter"
    
    def execute(self, input_data: Any, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Convert Tool protocol to EdgeBuilder interface"""
        if self._tool is None:
            raise ToolExecutionError("EdgeBuilderAdapter", "EdgeBuilderUnified not available")
            
        validation_result = self.validate_input(input_data)
        if not validation_result.is_valid:
            raise ToolValidationError("EdgeBuilderAdapter", validation_result.validation_errors)
        
        try:
            relationships = input_data["relationships"]
            result = self._tool.build_edges(relationships)
            
            return {
                "edge_results": result.get("edges", []) if result.get("status") == "success" else [],
                **input_data  # Pass through other data
            }
        except Exception as e:
            raise ToolExecutionError("EdgeBuilderAdapter", str(e), e)
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get EdgeBuilder tool information"""
        return {
            "name": "Edge Builder",
            "version": "1.0",
            "description": "Builds and stores relationship edges in graph database",
            "contract_id": "T34_EdgeBuilder",
            "capabilities": ["edge_building", "relationship_storage"]
        }

    def validate_input(self, input_data: Dict[str, Any]) -> ToolValidationResult:
        """Validate EdgeBuilder input"""
        errors = []
        
        if not isinstance(input_data, dict):
            errors.append("Input data must be a dictionary")
        elif "relationships" not in input_data:
            errors.append("Missing required field: relationships")
        elif not isinstance(input_data["relationships"], list):
            errors.append("relationships must be a list")
        
        return ToolValidationResult(
            is_valid=len(errors) == 0,
            validation_errors=errors,
            method_signatures={},
            execution_test_results={},
            input_schema_validation={"valid": len(errors) == 0, "errors": errors},
            security_validation={"valid": True, "errors": []},
            performance_validation={"valid": True, "errors": []}
        )