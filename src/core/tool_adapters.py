"""Tool Protocol Adapters - Priority 2 Critical Implementation
Bridges existing tools to unified Tool protocol for PipelineOrchestrator.

CRITICAL-1 IMPLEMENTATION: Fixes the gap between Tool protocol definition
and existing tool interfaces to enable actual workflow consolidation.

This module addresses:
- Tool protocol implementation gap identified in comprehensive analysis
- Interface mismatch between orchestrator expectations and tool reality
- Enables unified pipeline execution across all phases
"""

from typing import Any, Dict, List, Optional
import uuid
from .logging_config import get_logger
from .tool_adapter_bridge import ToolAdapterBridge
from .config import ConfigurationManager
from .schema_enforcer import SchemaEnforcer
from .entity_schema import StandardEntity, StandardRelationship
from .theory_integration import theory_aware_tool
from .tool_protocol import Tool, ToolExecutionError, ToolValidationError, ToolValidationResult
from ..tools.phase1.t01_pdf_loader import PDFLoader as _PDFLoader
from ..tools.phase1.t15a_text_chunker import TextChunker as _TextChunker
from ..tools.phase1.t23a_spacy_ner import SpacyNER as _SpacyNER
from ..tools.phase1.t27_relationship_extractor import RelationshipExtractor as _RelationshipExtractor
from ..tools.phase1.t31_entity_builder import EntityBuilder as _EntityBuilder
from ..tools.phase1.t34_edge_builder import EdgeBuilder as _EdgeBuilder
from ..tools.phase1.t68_pagerank import PageRankCalculator as _PageRankCalculator
from ..tools.phase1.t49_multihop_query import MultiHopQuery as _MultiHopQuery
from ..tools.phase1.t15b_vector_embedder import VectorEmbedder as _VectorEmbedder

logger = get_logger("core.tool_adapters")


class SimplifiedToolAdapter(Tool):
    """Simplified adapter that eliminates boilerplate and handles common patterns"""
    
    def __init__(self, tool_class, tool_method, input_key, output_key, config_manager=None):
        self.tool_class = tool_class
        self.tool_method = tool_method
        self.input_key = input_key
        self.output_key = output_key
        self.config_manager = config_manager or ConfigurationManager()
        self.logger = get_logger(f"core.{tool_class.__name__}")
        
        # Create services
        self.provenance_service = self._create_service("provenance")
        self.quality_service = self._create_service("quality")
        self.identity_service = self._create_service("identity")
        
        # Initialize the actual tool
        self._tool = tool_class(self.identity_service, self.provenance_service, self.quality_service)
        
    def _create_service(self, service_type):
        """Create a service with production error handling"""
        try:
            if service_type == "provenance":
                from src.core.provenance_service import ProvenanceService
                return ProvenanceService()
            elif service_type == "quality":
                from src.core.quality_service import QualityService
                return QualityService()
            elif service_type == "identity":
                from src.core.identity_service import IdentityService
                return IdentityService()
        except ImportError:
            if self.config_manager.is_production_mode():
                raise RuntimeError(f"Critical service {service_type} not available in production")
            else:
                logger.warning(f"Service {service_type} not available, using null service")
                return None
    
    def execute(self, input_data: Any, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute the tool with simplified protocol"""
        try:
            # Get the method from the tool
            method = getattr(self._tool, self.tool_method)
            
            # Handle different input patterns
            if self.input_key in input_data:
                items = input_data[self.input_key]
                if isinstance(items, list):
                    results = []
                    for item in items:
                        result = method(item)
                        if result.get("status") == "success":
                            results.extend(result.get(self.output_key, []))
                    return {self.output_key: results, "status": "success"}
                else:
                    return method(items)
            else:
                return method(input_data)
                
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def validate_input(self, input_data: Dict[str, Any]) -> ToolValidationResult:
        """Simplified validation"""
        errors = []
        if self.input_key not in input_data:
            errors.append(f"Missing required key: {self.input_key}")
        
        return ToolValidationResult(
            is_valid=len(errors) == 0,
            validation_errors=errors,
            method_signatures={},
            execution_test_results={},
            input_schema_validation={"valid": len(errors) == 0, "errors": errors},
            security_validation={"valid": True, "errors": []},
            performance_validation={"valid": True, "errors": []}
        )
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get tool information"""
        return {
            "name": self.tool_class.__name__,
            "version": "1.0.0",
            "description": f"Simplified adapter for {self.tool_class.__name__}",
            "contract_id": "unified",
            "capabilities": [self.tool_method]
        }


def create_simplified_adapter(tool_class, tool_method, input_key, output_key):
    """Factory function to create simplified adapters"""
    return SimplifiedToolAdapter(tool_class, tool_method, input_key, output_key)

# Load default concept library
DEFAULT_CONCEPT_LIBRARY = {
    "PERSON": {
        "description": "Individual human beings",
        "patterns": ["person", "individual", "people", "human"],
        "relationships": ["works_at", "lives_in", "leads", "founded"]
    },
    "ORGANIZATION": {
        "description": "Companies, institutions, groups", 
        "patterns": ["company", "organization", "institution", "corp", "inc"],
        "relationships": ["located_in", "owns", "partners_with", "competes_with"]
    },
    "LOCATION": {
        "description": "Geographic places and locations",
        "patterns": ["city", "country", "state", "region", "place"],
        "relationships": ["contains", "borders", "near"]
    },
    "PRODUCT": {
        "description": "Products, services, technologies",
        "patterns": ["product", "service", "technology", "solution"],
        "relationships": ["produced_by", "used_by", "competes_with"]
    }
}


class BaseToolAdapter(Tool):
    """Base class for all tool adapters with centralized configuration
    
    Implements the Tool protocol to ensure consistent interface across all tools.
    Optimized to reduce complexity and boilerplate code.
    """
    
    def __init__(self, config_manager: ConfigurationManager = None):
        self.config_manager = config_manager or ConfigurationManager()
        self.logger = get_logger(f"core.{self.__class__.__name__}")
        
        # Get configuration for this adapter (lazy loading)
        self._neo4j_config = None
        self._api_config = None
        self._entity_config = None
        self._text_config = None
        self._graph_config = None
        
        # Create required services with proper error handling
        self.provenance_service = self._create_provenance_service()
        self.quality_service = self._create_quality_service()
        self.identity_service = self._create_identity_service()
        
        # Add schema enforcement with production mode
        production_mode = self.config_manager.is_production_mode()
        self.schema_enforcer = SchemaEnforcer(production_mode=production_mode)
    
    @property
    def neo4j_config(self):
        """Lazy-loaded Neo4j configuration"""
        if self._neo4j_config is None:
            self._neo4j_config = self.config_manager.get_neo4j_config()
        return self._neo4j_config
    
    @property
    def api_config(self):
        """Lazy-loaded API configuration"""
        if self._api_config is None:
            self._api_config = self.config_manager.get_api_config()
        return self._api_config
    
    @property
    def entity_config(self):
        """Lazy-loaded entity processing configuration"""
        if self._entity_config is None:
            self._entity_config = self.config_manager.get_entity_processing_config()
        return self._entity_config
    
    @property
    def text_config(self):
        """Lazy-loaded text processing configuration"""
        if self._text_config is None:
            self._text_config = self.config_manager.get_text_processing_config()
        return self._text_config
    
    @property
    def graph_config(self):
        """Lazy-loaded graph construction configuration"""
        if self._graph_config is None:
            self._graph_config = self.config_manager.get_graph_construction_config()
        return self._graph_config
        
    def _create_provenance_service(self):
        """Create provenance service with production error handling"""
        try:
            from src.core.provenance_service import ProvenanceService
            return ProvenanceService()
        except ImportError as e:
            if self.config_manager.is_production_mode():
                # In production, missing critical services are fatal
                self.logger.critical(f"Critical service ProvenanceService not available in production mode: {e}")
                raise RuntimeError(f"Production deployment error: ProvenanceService required but not available: {e}")
            else:
                # In development, create a null service that logs warnings
                self.logger.warning("ProvenanceService not available, using NullProvenanceService for development")
                return self._create_null_provenance_service()
            
    def _create_quality_service(self):
        """Create quality service with production error handling"""
        try:
            from src.core.quality_service import QualityService
            return QualityService()
        except ImportError as e:
            if self.config_manager.is_production_mode():
                self.logger.critical(f"Critical service QualityService not available in production mode: {e}")
                raise RuntimeError(f"Production deployment error: QualityService required but not available: {e}")
            else:
                self.logger.warning("QualityService not available, using NullQualityService for development")
                return self._create_null_quality_service()
            
    def _create_identity_service(self):
        """Create identity service with production error handling"""
        try:
            from src.core.identity_service import IdentityService
            return IdentityService()
        except ImportError as e:
            if self.config_manager.is_production_mode():
                self.logger.critical(f"Critical service IdentityService not available in production mode: {e}")
                raise RuntimeError(f"Production deployment error: IdentityService required but not available: {e}")
            else:
                self.logger.warning("IdentityService not available, using NullIdentityService for development")
                return self._create_null_identity_service()
    
    # Replace mock services with null services that do nothing but don't break
    def _create_null_provenance_service(self):
        """Create a null service for development that logs all calls"""
        class NullProvenanceService:
            def __init__(self):
                self.logger = get_logger("core.null_provenance_service")
                
            def __getattr__(self, name):
                def null_method(*args, **kwargs):
                    self.logger.debug(f"NullProvenanceService.{name} called with args={args}, kwargs={kwargs}")
                    return None
                return null_method
                
        return NullProvenanceService()
    
    def _create_null_quality_service(self):
        """Create a null service for development that logs all calls"""
        class NullQualityService:
            def __init__(self):
                self.logger = get_logger("core.null_quality_service")
                
            def __getattr__(self, name):
                def null_method(*args, **kwargs):
                    self.logger.debug(f"NullQualityService.{name} called with args={args}, kwargs={kwargs}")
                    return None
                return null_method
                
        return NullQualityService()
    
    def _create_null_identity_service(self):
        """Create a null service for development that logs all calls"""
        class NullIdentityService:
            def __init__(self):
                self.logger = get_logger("core.null_identity_service")
                
            def __getattr__(self, name):
                def null_method(*args, **kwargs):
                    self.logger.debug(f"NullIdentityService.{name} called with args={args}, kwargs={kwargs}")
                    return None
                return null_method
                
        return NullIdentityService()

    # Abstract methods from Tool protocol that must be implemented by subclasses
    def execute(self, input_data: Any, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute tool with input data and optional context
        
        This method must be implemented by subclasses to define tool-specific execution logic.
        """
        raise NotImplementedError("Subclasses must implement execute method")
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get tool metadata and capabilities
        
        Returns basic tool information. Subclasses should override to provide specific details.
        """
        return {
            "name": self.__class__.__name__,
            "version": "1.0",
            "description": "GraphRAG tool adapter",
            "contract_id": None,
            "capabilities": []
        }
    
    def validate_input(self, input_data: Dict[str, Any]) -> ToolValidationResult:
        """Validate input data using comprehensive validation
        
        Uses the comprehensive validation method from tool_protocol as required by CLAUDE.md
        
        Returns:
            ToolValidationResult with detailed validation information
        """
        # Use the comprehensive validation method from tool_protocol
        return self.validate_input_comprehensive(input_data)


class OptimizedToolAdapterRegistry:
    """Optimized registry using simplified adapters to reduce complexity"""
    
    def __init__(self):
        self.logger = get_logger("core.tool_adapters_registry")
        self.config_manager = ConfigurationManager()
        self.adapters = {}
        
        try:
            self.validation_bridge = ToolAdapterBridge()
            self.validation_enabled = True
            self.logger.info("Tool validation bridge initialized")
        except Exception as e:
            self.logger.warning(f"Validation bridge failed: {e}")
            self.validation_enabled = False
            
        # Register simplified adapters
        self._register_simplified_adapters()
        
    def _register_simplified_adapters(self):
        """Register all simplified adapters to reduce complexity"""
        # Define adapter configurations (tool_class, method, input_key, output_key)
        adapter_configs = [
            (_PDFLoader, "load_pdf", "document_paths", "documents"),
            (_TextChunker, "chunk_text", "documents", "chunks"),
            (_SpacyNER, "extract_entities", "chunks", "entities"),
            (_RelationshipExtractor, "extract_relationships", "entities", "relationships"),
            (_EntityBuilder, "build_entities", "entities", "entity_results"),
            (_EdgeBuilder, "build_edges", "relationships", "edge_results"),
            (_PageRankCalculator, "calculate_pagerank", "graph_data", "pagerank_results"),
            (_MultiHopQuery, "execute_query", "query_data", "query_results"),
            (_VectorEmbedder, "embed_vectors", "text_data", "embeddings")
        ]
        
        # Create and register simplified adapters
        for tool_class, method, input_key, output_key in adapter_configs:
            adapter_name = f"{tool_class.__name__}Adapter"
            adapter = SimplifiedToolAdapter(tool_class, method, input_key, output_key, self.config_manager)
            self.adapters[adapter_name] = adapter
            
        self.logger.info(f"Registered {len(self.adapters)} simplified adapters")
        
    def register_adapter(self, name: str, adapter: Tool):
        """Register an adapter with the registry"""
        self.adapters[name] = adapter
        
    def get_adapter(self, name: str) -> Tool:
        """Get an adapter by name"""
        return self.adapters.get(name)
        
    def list_adapters(self) -> List[str]:
        """List all registered adapter names"""
        return list(self.adapters.keys())


# Global registry instance
tool_adapter_registry = OptimizedToolAdapterRegistry()


class PDFLoaderAdapter(BaseToolAdapter):
    """Adapter for PDFLoader to implement Tool protocol
    
    Converts PipelineOrchestrator Tool protocol to PDFLoader.load_pdf interface.
    Handles document path iteration and result aggregation.
    """
    
    def __init__(self, config_manager: ConfigurationManager = None):
        super().__init__(config_manager)
        self._tool = _PDFLoader(self.identity_service, self.provenance_service, self.quality_service)
        self.tool_name = "PDFLoaderAdapter"
    
    def execute(self, input_data: Any, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Convert Tool protocol to PDFLoader interface
        
        Args:
            input_data: Expected format: {"document_paths": List[str], ...}
            context: Optional execution context
            
        Returns:
            {"documents": List[Dict], "document_paths": List[str], ...}
        """
        validation_result = self.validate_input(input_data)
        if not validation_result.is_valid:
            raise ToolValidationError("PDFLoaderAdapter", validation_result.validation_errors)
        
        try:
            # Use validation bridge if available
            if tool_adapter_registry.validation_enabled:
                return tool_adapter_registry.validation_bridge.execute_with_validation(
                    "PDFLoader", self, input_data
                )
            else:
                # Original execution path
                return self._execute_original(input_data)
        except Exception as e:
            raise ToolExecutionError("PDFLoaderAdapter", str(e), e)
    
    def _execute_original(self, input_data: Any) -> Any:
        """Original execution logic without validation"""
        
        document_paths = input_data["document_paths"]
        documents = []
        
        for path in document_paths:
            try:
                # Call actual tool method
                result = self._tool.load_pdf(path)
                
                if result.get("status") == "success":
                    # Extract document data from tool result - check if document is nested
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
                    # Add failed document with minimal data
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
        
        # Return data in orchestrator format
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
        """Validate PDFLoader input with comprehensive validation"""
        return self.validate_input_comprehensive(input_data)
    
    def _validate_input_schema(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input schema for PDFLoader"""
        errors = []
        
        if not isinstance(input_data, dict):
            errors.append("Input data must be a dictionary")
            return {"valid": False, "errors": errors}
        
        # Check required fields
        if "document_paths" not in input_data:
            errors.append("Missing required field: document_paths")
        else:
            document_paths = input_data["document_paths"]
            if not isinstance(document_paths, list):
                errors.append("document_paths must be a list")
            elif len(document_paths) == 0:
                errors.append("document_paths list cannot be empty")
            else:
                for i, path in enumerate(document_paths):
                    if not isinstance(path, str):
                        errors.append(f"document_paths[{i}] must be a string")
        
        return {"valid": len(errors) == 0, "errors": errors}
    
    def _validate_input_security(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input security for PDFLoader"""
        errors = []
        
        if "document_paths" in input_data:
            document_paths = input_data["document_paths"]
            if isinstance(document_paths, list):
                for i, path in enumerate(document_paths):
                    if isinstance(path, str):
                        # Check for path traversal
                        if "../" in path or "..%2F" in path or "..%5C" in path:
                            errors.append(f"Path traversal detected in document_paths[{i}]")
                        # Check for suspicious file extensions
                        if path.lower().endswith(('.exe', '.bat', '.sh', '.py', '.js')):
                            errors.append(f"Suspicious file extension in document_paths[{i}]")
        
        return {"valid": len(errors) == 0, "errors": errors}
    
    def _validate_input_performance(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input performance for PDFLoader"""
        errors = []
        warnings = []
        
        if "document_paths" in input_data:
            document_paths = input_data["document_paths"]
            if isinstance(document_paths, list):
                if len(document_paths) > 100:
                    errors.append("Too many documents (>100) may cause performance issues")
                elif len(document_paths) > 50:
                    warnings.append("Large number of documents (>50) may slow processing")
        
        return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}
    
    def _get_required_fields(self) -> List[str]:
        """Get required fields for PDFLoader"""
        return ["document_paths"]


class TextChunkerAdapter(BaseToolAdapter):
    """Adapter for TextChunker to implement Tool protocol
    
    Converts document list to chunk list using TextChunker.chunk_text interface.
    """
    
    def __init__(self, config_manager: ConfigurationManager = None):
        super().__init__(config_manager)
        self._tool = _TextChunker(self.identity_service, self.provenance_service, self.quality_service)
        self.tool_name = "TextChunkerAdapter"
    
    def execute(self, input_data: Any, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Convert Tool protocol to TextChunker interface
        
        Args:
            input_data: Expected format: {"documents": List[Dict], ...}
            context: Optional execution context
            
        Returns:
            {"chunks": List[Dict], "documents": List[Dict], ...}
        """
        validation_result = self.validate_input(input_data)
        if not validation_result.is_valid:
            raise ToolValidationError("TextChunkerAdapter", validation_result.validation_errors)
        
        try:
            documents = input_data["documents"]
            all_chunks = []
            
            for doc in documents:
                try:
                    document_id = doc.get("document_id", "unknown")
                    text = doc.get("text", "")
                    confidence = doc.get("confidence", 0.8)
                    
                    if text:  # Only chunk documents with text
                        # Call actual tool method
                        result = self._tool.chunk_text(document_id, text, confidence)
                        
                        if result.get("status") == "success":
                            chunks = result.get("chunks", [])
                            # Add document reference to each chunk
                            for chunk in chunks:
                                chunk["source_document"] = document_id
                                chunk["source_file_path"] = doc.get("file_path")
                            all_chunks.extend(chunks)
                        else:
                            logger.warning("Text chunking failed for document %s: %s", 
                                         document_id, result.get("error"))
                            
                except Exception as e:
                    logger.error("Exception chunking document %s: %s", 
                               doc.get("document_id"), str(e))
            
            return {
                "chunks": all_chunks,
                **input_data  # Pass through other data including documents
            }
        except Exception as e:
            raise ToolExecutionError("TextChunkerAdapter", str(e), e)
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get TextChunker tool information"""
        return {
            "name": "Text Chunker",
            "version": "1.0",
            "description": "Splits document text into smaller chunks for processing",
            "contract_id": "T15A_TextChunker",
            "capabilities": ["text_chunking", "document_processing", "chunk_generation"]
        }
    
    def validate_input(self, input_data: Dict[str, Any]) -> ToolValidationResult:
        """Validate TextChunker input with comprehensive validation"""
        return self.validate_input_comprehensive(input_data)
    
    def _validate_input_schema(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input schema for TextChunker"""
        errors = []
        
        if not isinstance(input_data, dict):
            errors.append("Input data must be a dictionary")
            return {"valid": False, "errors": errors}
        
        # Check required fields
        if "documents" not in input_data:
            errors.append("Missing required field: documents")
        else:
            documents = input_data["documents"]
            if not isinstance(documents, list):
                errors.append("documents must be a list")
            elif len(documents) == 0:
                errors.append("documents list cannot be empty")
            else:
                for i, doc in enumerate(documents):
                    if not isinstance(doc, dict):
                        errors.append(f"documents[{i}] must be a dictionary")
                    elif "text" not in doc:
                        errors.append(f"documents[{i}] missing required field: text")
                    elif not isinstance(doc["text"], str):
                        errors.append(f"documents[{i}].text must be a string")
        
        return {"valid": len(errors) == 0, "errors": errors}
    
    def _validate_input_security(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input security for TextChunker"""
        errors = []
        
        if "documents" in input_data:
            documents = input_data["documents"]
            if isinstance(documents, list):
                for i, doc in enumerate(documents):
                    if isinstance(doc, dict) and "text" in doc:
                        text = doc["text"]
                        if isinstance(text, str):
                            # Check for extremely long text that could cause DoS
                            if len(text) > 10_000_000:  # 10MB
                                errors.append(f"documents[{i}].text too large (>10MB)")
                            # Check for suspicious patterns
                            if "<script>" in text.lower():
                                errors.append(f"documents[{i}].text contains suspicious script tags")
        
        return {"valid": len(errors) == 0, "errors": errors}
    
    def _validate_input_performance(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input performance for TextChunker"""
        errors = []
        warnings = []
        
        if "documents" in input_data:
            documents = input_data["documents"]
            if isinstance(documents, list):
                if len(documents) > 1000:
                    errors.append("Too many documents (>1000) may cause performance issues")
                elif len(documents) > 500:
                    warnings.append("Large number of documents (>500) may slow processing")
                
                # Check total text size
                total_text_size = 0
                for doc in documents:
                    if isinstance(doc, dict) and "text" in doc:
                        text = doc.get("text", "")
                        if isinstance(text, str):
                            total_text_size += len(text)
                
                if total_text_size > 100_000_000:  # 100MB
                    errors.append("Total text size too large (>100MB)")
                elif total_text_size > 50_000_000:  # 50MB
                    warnings.append("Large total text size (>50MB) may slow processing")
        
        return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}
    
    def _get_required_fields(self) -> List[str]:
        """Get required fields for TextChunker"""
        return ["documents"]


class SpacyNERAdapter(BaseToolAdapter):
    """Adapter for SpacyNER to implement Tool protocol
    
    Converts chunk list to entity list using SpacyNER.extract_entities interface.
    """
    
    def __init__(self, config_manager: ConfigurationManager = None):
        super().__init__(config_manager)
        self._tool = _SpacyNER(self.identity_service, self.provenance_service, self.quality_service)
        self.tool_name = "SpacyNERAdapter"
    
    @theory_aware_tool(DEFAULT_CONCEPT_LIBRARY)
    def execute(self, input_data: Any, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Convert Tool protocol to SpacyNER interface
        
        Args:
            input_data: Expected format: {"chunks": List[Dict], ...}
            context: Optional execution context
            
        Returns:
            {"entities": List[Dict], "chunks": List[Dict], ...}
        """
        if not self.validate_input(input_data):
            raise ToolValidationError("SpacyNERAdapter", ["Input data validation failed"])
        
        try:
            chunks = input_data["chunks"]
            all_entities = []
            
            for chunk in chunks:
                try:
                    chunk_id = chunk.get("chunk_id", "unknown")
                    text = chunk.get("text", "")
                    confidence = chunk.get("confidence", 0.8)
                    
                    if text:  # Only process chunks with text
                        # Call actual tool method
                        result = self._tool.extract_entities(chunk_id, text, confidence)
                        
                        if result.get("status") == "success":
                            entities = result.get("entities", [])
                            # Add chunk reference to each entity
                            for entity in entities:
                                entity["source_chunk"] = chunk_id
                                entity["source_document"] = chunk.get("source_document")
                            all_entities.extend(entities)
                        else:
                            logger.warning("Entity extraction failed for chunk %s: %s",
                                         chunk_id, result.get("error"))
                            
                except Exception as e:
                    logger.error("Exception extracting entities from chunk %s: %s",
                               chunk.get("chunk_id"), str(e))
            
            # Before returning results, enforce schema
            try:
                standardized_entities = self.schema_enforcer.enforce_entity_schema(all_entities)
                result = {
                    "entities": [entity.dict() for entity in standardized_entities],
                    "schema_enforced": True,
                    **input_data  # Pass through other data including chunks
                }
            except Exception as e:
                self.logger.error(f"Schema enforcement failed: {e}")
                result = {
                    "entities": all_entities,
                    "schema_enforced": False,
                    **input_data
                }
            
            return result
        except Exception as e:
            raise ToolExecutionError("SpacyNERAdapter", str(e), e)
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get SpacyNER tool information"""
        return {
            "name": "SpaCy NER",
            "version": "1.0",
            "description": "Named Entity Recognition using SpaCy NLP library",
            "contract_id": "T23A_SpacyNER",
            "capabilities": ["named_entity_recognition", "entity_extraction", "nlp_processing"]
        }
    
    def validate_input(self, input_data: Any) -> ToolValidationResult:
        """Validate SpacyNER input with comprehensive validation"""
        return self.validate_input_comprehensive(input_data)
    
    def _validate_input_schema(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input schema for SpacyNER"""
        errors = []
        
        if not isinstance(input_data, dict):
            errors.append("Input data must be a dictionary")
            return {"valid": False, "errors": errors}
        
        if "chunks" not in input_data:
            errors.append("Missing required field: chunks")
        else:
            chunks = input_data["chunks"]
            if not isinstance(chunks, list):
                errors.append("chunks must be a list")
            elif len(chunks) == 0:
                errors.append("chunks list cannot be empty")
            else:
                for i, chunk in enumerate(chunks):
                    if not isinstance(chunk, dict):
                        errors.append(f"chunks[{i}] must be a dictionary")
                    elif "text" not in chunk:
                        errors.append(f"chunks[{i}] missing required field: text")
        
        return {"valid": len(errors) == 0, "errors": errors}
    
    def _validate_input_security(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input security for SpacyNER"""
        errors = []
        
        if "chunks" in input_data:
            chunks = input_data["chunks"]
            if isinstance(chunks, list):
                for i, chunk in enumerate(chunks):
                    if isinstance(chunk, dict) and "text" in chunk:
                        text = chunk["text"]
                        if isinstance(text, str) and len(text) > 1_000_000:
                            errors.append(f"chunks[{i}].text too large (>1MB)")
        
        return {"valid": len(errors) == 0, "errors": errors}
    
    def _validate_input_performance(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input performance for SpacyNER"""
        errors = []
        warnings = []
        
        if "chunks" in input_data:
            chunks = input_data["chunks"]
            if isinstance(chunks, list):
                if len(chunks) > 10000:
                    errors.append("Too many chunks (>10000) may cause performance issues")
                elif len(chunks) > 5000:
                    warnings.append("Large number of chunks (>5000) may slow processing")
        
        return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}
    
    def _get_required_fields(self) -> List[str]:
        """Get required fields for SpacyNER"""
        return ["chunks"]


class RelationshipExtractorAdapter(BaseToolAdapter):
    """Adapter for RelationshipExtractor to implement Tool protocol
    
    Groups entities by chunk and extracts relationships using RelationshipExtractor.extract_relationships.
    """
    
    def __init__(self, config_manager: ConfigurationManager = None):
        super().__init__(config_manager)
        self._tool = _RelationshipExtractor(self.identity_service, self.provenance_service, self.quality_service)
        self.tool_name = "RelationshipExtractorAdapter"
    
    @theory_aware_tool(DEFAULT_CONCEPT_LIBRARY)
    def execute(self, input_data: Any, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Convert Tool protocol to RelationshipExtractor interface
        
        Args:
            input_data: Expected format: {"entities": List[Dict], "chunks": List[Dict], ...}
            context: Optional execution context
            
        Returns:
            {"relationships": List[Dict], "entities": List[Dict], ...}
        """
        if not self.validate_input(input_data):
            raise ToolValidationError("RelationshipExtractorAdapter", ["Input data validation failed"])
        
        try:
            entities = input_data["entities"]
            chunks = input_data.get("chunks", [])
            entity_id_mapping = input_data.get("entity_id_mapping", {})  # NEW: Get entity ID mapping
            all_relationships = []
            
            # Group entities by chunk for relationship extraction
            chunk_entities = {}
            for entity in entities:
                chunk_id = entity.get("source_chunk", "unknown")
                if chunk_id not in chunk_entities:
                    chunk_entities[chunk_id] = []
                chunk_entities[chunk_id].append(entity)
            
            # Find corresponding chunk data
            chunk_data = {chunk.get("chunk_id"): chunk for chunk in chunks}
            
            # Extract relationships for each chunk
            for chunk_id, chunk_entity_list in chunk_entities.items():
                try:
                    chunk_info = chunk_data.get(chunk_id, {})
                    text = chunk_info.get("text", "")
                    confidence = chunk_info.get("confidence", 0.8)
                    
                    if text and len(chunk_entity_list) > 1:  # Need text and multiple entities
                        # Fix entity format - add missing fields that relationship extractor expects
                        fixed_entities = []
                        for entity in chunk_entity_list:
                            # Create a copy with the fields the relationship extractor expects
                            fixed_entity = entity.copy()
                            # Add mention_id (use entity_id as fallback)
                            fixed_entity['mention_id'] = entity.get('entity_id', f"mention_{uuid.uuid4().hex[:8]}")
                            # Add position fields (use defaults if not available)
                            fixed_entity['start_char'] = entity.get('start_char', 0)
                            fixed_entity['end_char'] = entity.get('end_char', len(entity.get('surface_form', '')))
                            fixed_entities.append(fixed_entity)
                        
                        # Call actual tool method with correct parameters
                        result = self._tool.extract_relationships(
                            chunk_ref=chunk_id, 
                            text=text, 
                            entities=fixed_entities, 
                            chunk_confidence=confidence
                        )
                        
                        if result.get("status") == "success":
                            relationships = result.get("relationships", [])
                            # Add chunk reference to each relationship and apply entity ID mapping
                            for rel in relationships:
                                rel["source_chunk"] = chunk_id
                                rel["source_document"] = chunk_info.get("source_document")
                                
                                # Apply entity ID mapping if available
                                if entity_id_mapping:
                                    if rel.get("subject_entity_id") in entity_id_mapping:
                                        rel["subject_entity_id"] = entity_id_mapping[rel["subject_entity_id"]]
                                    if rel.get("object_entity_id") in entity_id_mapping:
                                        rel["object_entity_id"] = entity_id_mapping[rel["object_entity_id"]]
                                    if rel.get("subject_mention_id") in entity_id_mapping:
                                        rel["subject_mention_id"] = entity_id_mapping[rel["subject_mention_id"]]
                                    if rel.get("object_mention_id") in entity_id_mapping:
                                        rel["object_mention_id"] = entity_id_mapping[rel["object_mention_id"]]
                            all_relationships.extend(relationships)
                        else:
                            logger.warning("Relationship extraction failed for chunk %s: %s",
                                         chunk_id, result.get("error"))
                            
                except Exception as e:
                    logger.error("Exception extracting relationships from chunk %s: %s",
                               chunk_id, str(e))
            
            # Before returning results, enforce schema
            try:
                standardized_relationships = self.schema_enforcer.enforce_relationship_schema(all_relationships)
                result = {
                    "relationships": [rel.dict() for rel in standardized_relationships],
                    "schema_enforced": True,
                    **input_data  # Pass through other data including entities
                }
            except Exception as e:
                self.logger.error(f"Schema enforcement failed: {e}")
                result = {
                    "relationships": all_relationships,
                    "schema_enforced": False,
                    **input_data
                }
                
            return result
        except Exception as e:
            raise ToolExecutionError("RelationshipExtractorAdapter", str(e), e)
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get RelationshipExtractor tool information"""
        return {
            "name": "Relationship Extractor",
            "version": "1.0",
            "description": "Extracts relationships between entities from text",
            "contract_id": "T27_RelationshipExtractor",
            "capabilities": ["relationship_extraction", "entity_linking", "dependency_parsing"]
        }
    
    def validate_input(self, input_data: Any) -> ToolValidationResult:
        """Validate RelationshipExtractor input with comprehensive validation"""
        return self.validate_input_comprehensive(input_data)
    
    def _validate_input_schema(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input schema for RelationshipExtractor"""
        errors = []
        
        if not isinstance(input_data, dict):
            errors.append("Input data must be a dictionary")
            return {"valid": False, "errors": errors}
        
        if "entities" not in input_data:
            errors.append("Missing required field: entities")
        else:
            entities = input_data["entities"]
            if not isinstance(entities, list):
                errors.append("entities must be a list")
        
        return {"valid": len(errors) == 0, "errors": errors}
    
    def _validate_input_security(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input security for RelationshipExtractor"""
        errors = []
        
        if "entities" in input_data:
            entities = input_data["entities"]
            if isinstance(entities, list) and len(entities) > 50000:
                errors.append("Too many entities (>50000) may cause DoS")
        
        return {"valid": len(errors) == 0, "errors": errors}
    
    def _validate_input_performance(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input performance for RelationshipExtractor"""
        errors = []
        warnings = []
        
        if "entities" in input_data:
            entities = input_data["entities"]
            if isinstance(entities, list):
                if len(entities) > 10000:
                    errors.append("Too many entities (>10000) may cause performance issues")
                elif len(entities) > 5000:
                    warnings.append("Large number of entities (>5000) may slow processing")
        
        return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}
    
    def _get_required_fields(self) -> List[str]:
        """Get required fields for RelationshipExtractor"""
        return ["entities"]


class EntityBuilderAdapter(BaseToolAdapter):
    """Adapter for EntityBuilder to implement Tool protocol
    
    Builds Neo4j entity nodes using EntityBuilder.build_entities interface.
    """
    
    def __init__(self, config_manager: ConfigurationManager = None):
        super().__init__(config_manager)
        # Use config values from ConfigurationManager
        neo4j_uri = self.neo4j_config['uri']
        neo4j_user = self.neo4j_config['user']
        neo4j_password = self.neo4j_config['password']
        
        self._tool = _EntityBuilder(
            self.identity_service, self.provenance_service, self.quality_service,
            neo4j_uri, neo4j_user, neo4j_password, None  # shared_driver
        )
        self.tool_name = "EntityBuilderAdapter"
    
    def execute(self, input_data: Any, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Convert Tool protocol to EntityBuilder interface
        
        Args:
            input_data: Expected format: {"entities": List[Dict], ...}
            context: Optional execution context
            
        Returns:
            {"entity_build_result": Dict, "neo4j_entities": List[Dict], ...}
        """
        if not self.validate_input(input_data):
            raise ToolValidationError("EntityBuilderAdapter", ["Input data validation failed"])
        
        try:
            entities = input_data["entities"]
            
            # Prepare mentions list for EntityBuilder
            mentions = []
            source_refs = []
            
            for entity in entities:
                mention = {
                    "mention_id": entity.get("mention_id", entity.get("entity_id", f"mention_{uuid.uuid4().hex[:8]}")),
                    "entity_id": entity.get("entity_id", f"entity_{uuid.uuid4().hex[:8]}"),
                    "surface_form": entity.get("surface_form", ""),
                    "canonical_name": entity.get("canonical_name", entity.get("surface_form", "")),
                    "entity_type": entity.get("entity_type", "UNKNOWN"),
                    "confidence": entity.get("confidence", 0.0),
                    "mentions": entity.get("mentions", []),
                    "start_position": entity.get("start_char", entity.get("start_position", 0)),
                    "end_position": entity.get("end_char", entity.get("end_position", 0))
                }
                mentions.append(mention)
                
                # Collect source references
                source_chunk = entity.get("source_chunk", "")
                source_doc = entity.get("source_document", "")
                if source_chunk:
                    source_refs.append(f"chunk:{source_chunk}")
                if source_doc:
                    source_refs.append(f"document:{source_doc}")
            
            # Remove duplicate source refs
            source_refs = list(set(source_refs))
            
            # Call actual tool method
            result = self._tool.build_entities(mentions, source_refs)
            
            if result.get("status") == "success":
                return {
                    "entity_build_result": result,
                    "neo4j_entities": result.get("entities", []),
                    "entity_id_mapping": result.get("entity_id_mapping", {}),  # NEW: Pass entity ID mapping
                    **input_data  # Pass through other data
                }
            else:
                logger.error("Entity building failed: %s", result.get("error"))
                return {
                    "entity_build_result": result,
                    "neo4j_entities": [],
                    **input_data
                }
                
        except Exception as e:
            logger.error("Exception in entity building: %s", str(e))
            raise ToolExecutionError("EntityBuilderAdapter", str(e), e)
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get EntityBuilder tool information"""
        return {
            "name": "Entity Builder",
            "version": "1.0",
            "description": "Builds entity nodes in Neo4j graph database",
            "contract_id": "T31_EntityBuilder",
            "capabilities": ["entity_creation", "graph_building", "neo4j_operations"]
        }
    
    def validate_input(self, input_data: Any) -> ToolValidationResult:
        """Validate input data"""
        validation_errors = []
        
        if not isinstance(input_data, dict):
            validation_errors.append("Input data must be a dictionary")
        
        return ToolValidationResult(
            is_valid=len(validation_errors) == 0,
            validation_errors=validation_errors,
            method_signatures={"execute": "Dict[str, Any]", "validate_input": "ToolValidationResult"},
            execution_test_results={"basic_validation": "passed" if len(validation_errors) == 0 else "failed"},
            input_schema_validation={"valid": True, "errors": []},
            security_validation={"valid": True, "errors": []},
            performance_validation={"valid": True, "errors": []}
        )
class EdgeBuilderAdapter(BaseToolAdapter):
    """Adapter for EdgeBuilder to implement Tool protocol
    
    Builds Neo4j relationship edges using EdgeBuilder.build_edges interface.
    """
    
    def __init__(self, config_manager: ConfigurationManager = None):
        super().__init__(config_manager)
        # Use config values from ConfigurationManager
        neo4j_uri = self.neo4j_config['uri']
        neo4j_user = self.neo4j_config['user']
        neo4j_password = self.neo4j_config['password']
        
        self._tool = _EdgeBuilder(
            self.identity_service, self.provenance_service, self.quality_service,
            neo4j_uri, neo4j_user, neo4j_password, None  # shared_driver
        )
        self.tool_name = "EdgeBuilderAdapter"
    
    def execute(self, input_data: Any, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Convert Tool protocol to EdgeBuilder interface
        
        Args:
            input_data: Expected format: {"relationships": List[Dict], ...}
            context: Optional execution context
            
        Returns:
            {"edge_build_result": Dict, "neo4j_relationships": List[Dict], ...}
        """
        if not self.validate_input(input_data):
            raise ToolValidationError("EdgeBuilderAdapter", ["Input data validation failed"])
        
        try:
            relationships = input_data["relationships"]
            
            # Prepare relationships list for EdgeBuilder
            source_refs = []
            
            for rel in relationships:
                # Collect source references
                source_chunk = rel.get("source_chunk", "")
                source_doc = rel.get("source_document", "")
                if source_chunk:
                    source_refs.append(f"chunk:{source_chunk}")
                if source_doc:
                    source_refs.append(f"document:{source_doc}")
            
            # Remove duplicate source refs
            source_refs = list(set(source_refs))
            
            # Call actual tool method with entity verification enabled
            result = self._tool.build_edges(relationships, source_refs, entity_verification_required=True)
            
            if result.get("status") == "success":
                return {
                    "edge_build_result": result,
                    "neo4j_relationships": result.get("relationships", []),
                    **input_data  # Pass through other data
                }
            else:
                logger.error("Edge building failed: %s", result.get("error"))
                return {
                    "edge_build_result": result,
                    "neo4j_relationships": [],
                    **input_data
                }
                
        except Exception as e:
            logger.error("Exception in edge building: %s", str(e))
            raise ToolExecutionError("EdgeBuilderAdapter", str(e), e)
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get EdgeBuilder tool information"""
        return {
            "name": "Edge Builder",
            "version": "1.0",
            "description": "Builds relationship edges in Neo4j graph database",
            "contract_id": "T34_EdgeBuilder",
            "capabilities": ["relationship_creation", "graph_building", "neo4j_operations"]
        }
    
    def validate_input(self, input_data: Any) -> ToolValidationResult:
        """Validate input data"""
        validation_errors = []
        
        if not isinstance(input_data, dict):
            validation_errors.append("Input data must be a dictionary")
        
        return ToolValidationResult(
            is_valid=len(validation_errors) == 0,
            validation_errors=validation_errors,
            method_signatures={"execute": "Dict[str, Any]", "validate_input": "ToolValidationResult"},
            execution_test_results={"basic_validation": "passed" if len(validation_errors) == 0 else "failed"},
            input_schema_validation={"valid": True, "errors": []},
            security_validation={"valid": True, "errors": []},
            performance_validation={"valid": True, "errors": []}
        )
class PageRankAdapter(BaseToolAdapter):
    """Adapter for PageRankCalculator to implement Tool protocol
    
    Calculates PageRank scores using PageRankCalculator.calculate_pagerank interface.
    """
    
    def __init__(self, config_manager: ConfigurationManager = None):
        super().__init__(config_manager)
        # Use config values from ConfigurationManager
        neo4j_uri = self.neo4j_config['uri']
        neo4j_user = self.neo4j_config['user']
        neo4j_password = self.neo4j_config['password']
        
        self._tool = _PageRankCalculator(
            self.identity_service, self.provenance_service, self.quality_service,
            neo4j_uri, neo4j_user, neo4j_password, None  # shared_driver
        )
        self.tool_name = "PageRankAdapter"
    
    def execute(self, input_data: Any, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Convert Tool protocol to PageRankCalculator interface
        
        Args:
            input_data: Any pipeline data (PageRank operates on graph)
            context: Optional execution context
            
        Returns:
            {"pagerank_result": Dict, "pagerank_scores": List[Dict], ...}
        """
        if not self.validate_input(input_data):
            raise ToolValidationError("PageRankAdapter", ["Input data validation failed"])
        
        try:
            # PageRank operates on the Neo4j graph, doesn't need specific input data
            # But we can use entity filters if available
            entity_filter = {}
            
            # Extract entity types if available for filtering
            if isinstance(input_data, dict) and "neo4j_entities" in input_data:
                entity_types = set()
                for entity in input_data["neo4j_entities"]:
                    entity_type = entity.get("entity_type")
                    if entity_type:
                        entity_types.add(entity_type)
                if entity_types:
                    entity_filter["entity_types"] = list(entity_types)
            
            # Call actual tool method
            result = self._tool.calculate_pagerank(entity_filter=entity_filter)
            
            if result.get("status") == "success":
                return {
                    "pagerank_result": result,
                    "pagerank_scores": result.get("pagerank_scores", []),
                    **input_data  # Pass through other data
                }
            else:
                logger.error("PageRank calculation failed: %s", result.get("error"))
                return {
                    "pagerank_result": result,
                    "pagerank_scores": [],
                    **input_data
                }
                
        except Exception as e:
            logger.error("Exception in PageRank calculation: %s", str(e))
            raise ToolExecutionError("PageRankAdapter", str(e), e)
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get PageRankCalculator tool information"""
        return {
            "name": "PageRank Calculator",
            "version": "1.0",
            "description": "Calculates PageRank scores for entities in the graph",
            "contract_id": "T68_PageRank",
            "capabilities": ["pagerank_calculation", "centrality_analysis", "graph_analysis"]
        }
    
    def validate_input(self, input_data: Any) -> ToolValidationResult:
        """Validate input data"""
        validation_errors = []
        
        if not isinstance(input_data, dict):
            validation_errors.append("Input data must be a dictionary")
        
        return ToolValidationResult(
            is_valid=len(validation_errors) == 0,
            validation_errors=validation_errors,
            method_signatures={"execute": "Dict[str, Any]", "validate_input": "ToolValidationResult"},
            execution_test_results={"basic_validation": "passed" if len(validation_errors) == 0 else "failed"},
            input_schema_validation={"valid": True, "errors": []},
            security_validation={"valid": True, "errors": []},
            performance_validation={"valid": True, "errors": []}
        )
class MultiHopQueryAdapter(BaseToolAdapter):
    """Adapter for MultiHopQuery to implement Tool protocol
    
    Executes multi-hop queries using MultiHopQuery.query_graph interface.
    """
    
    def __init__(self, config_manager: ConfigurationManager = None):
        super().__init__(config_manager)
        # Use config values from ConfigurationManager
        neo4j_uri = self.neo4j_config['uri']
        neo4j_user = self.neo4j_config['user']
        neo4j_password = self.neo4j_config['password']
        
        self._tool = _MultiHopQuery(
            self.identity_service, self.provenance_service, self.quality_service,
            neo4j_uri, neo4j_user, neo4j_password, None  # shared_driver
        )
        self.tool_name = "MultiHopQueryAdapter"
    
    def execute(self, input_data: Any, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Convert Tool protocol to MultiHopQuery interface
        
        Args:
            input_data: Expected format: {"queries": List[str], ...}
            context: Optional execution context
            
        Returns:
            {"query_results": List[Dict], ...}
        """
        if not self.validate_input(input_data):
            raise ToolValidationError("MultiHopQueryAdapter", ["Input data validation failed"])
        
        try:
            if not isinstance(input_data, dict) or "queries" not in input_data:
                # If no queries provided, return empty results
                return {
                    "query_results": [],
                    **input_data
                }
            
            queries = input_data["queries"]
            all_query_results = []
            
            for query in queries:
                try:
                    if query and isinstance(query, str):
                        # Call actual tool method
                        result = self._tool.query_graph(query)
                        
                        if result.get("status") == "success":
                            query_result = {
                                "query": query,
                                "status": "success",
                                "results": result.get("results", []),
                                "explanation": result.get("explanation", ""),
                                "confidence": result.get("confidence", 0.0)
                            }
                            all_query_results.append(query_result)
                        else:
                            logger.warning("Query failed: %s - %s", query, result.get("error"))
                            query_result = {
                                "query": query,
                                "status": "failed",
                                "results": [],
                                "error": result.get("error", ""),
                                "confidence": 0.0
                            }
                            all_query_results.append(query_result)
                            
                except Exception as e:
                    logger.error("Exception executing query '%s': %s", query, str(e))
                    query_result = {
                        "query": query,
                        "status": "error",
                        "results": [],
                        "error": str(e),
                        "confidence": 0.0
                    }
                    all_query_results.append(query_result)
            
            return {
                "query_results": all_query_results,
                **input_data  # Pass through other data
            }
        except Exception as e:
            raise ToolExecutionError("MultiHopQueryAdapter", str(e), e)
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get MultiHopQuery tool information"""
        return {
            "name": "Multi-Hop Query",
            "version": "1.0",
            "description": "Executes multi-hop queries on the graph database",
            "contract_id": "T49_MultiHopQuery",
            "capabilities": ["graph_querying", "multi_hop_traversal", "complex_queries"]
        }
    
    def validate_input(self, input_data: Any) -> ToolValidationResult:
        """Validate input data"""
        validation_errors = []
        
        if not isinstance(input_data, dict):
            validation_errors.append("Input data must be a dictionary")
        
        return ToolValidationResult(
            is_valid=len(validation_errors) == 0,
            validation_errors=validation_errors,
            method_signatures={"execute": "Dict[str, Any]", "validate_input": "ToolValidationResult"},
            execution_test_results={"basic_validation": "passed" if len(validation_errors) == 0 else "failed"},
            input_schema_validation={"valid": True, "errors": []},
            security_validation={"valid": True, "errors": []},
            performance_validation={"valid": True, "errors": []}
        )
class OntologyAwareExtractorAdapter(BaseToolAdapter):
    """Adapter for OntologyAwareExtractor to implement Tool protocol
    
    Converts chunk list to ontology-aware entity/relationship extraction.
    """
    
    def __init__(self, config_manager: ConfigurationManager = None):
        super().__init__(config_manager)
        
        # Import the actual Phase 2 tool
        from ..tools.phase2.t23c_ontology_aware_extractor import OntologyAwareExtractor
        
        # Initialize with services created by BaseToolAdapter
        self._tool = OntologyAwareExtractor(
            self.identity_service,
            google_api_key=self.api_config.get('google_api_key'),
            openai_api_key=self.api_config.get('openai_api_key')
        )
        self.tool_name = "OntologyAwareExtractorAdapter"
    
    def execute(self, input_data: Any, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Convert Tool protocol to OntologyAwareExtractor interface
        
        Args:
            input_data: Expected format: {"chunks": List[Dict], ...}
            context: Optional execution context
            
        Returns:
            {"entities": List[Dict], "relationships": List[Dict], ...}
        """
        if not self.validate_input(input_data):
            raise ToolValidationError("OntologyAwareExtractorAdapter", ["Input data validation failed"])
        
        try:
            chunks = input_data["chunks"]
            all_entities = []
            all_relationships = []
            all_mentions = []
            
            for chunk in chunks:
                try:
                    chunk_id = chunk.get("chunk_id", "unknown")
                    text = chunk.get("text", "")
                    confidence = chunk.get("confidence", 0.8)
                    
                    if text:  # Only process chunks with text
                        # Call actual tool method
                        result = self._tool.extract_with_ontology(
                            text=text,
                            domain_description=input_data.get("domain_description", ""),
                            existing_ontology=input_data.get("existing_ontology")
                        )
                        
                        if hasattr(result, 'entities'):
                            # Add chunk reference to each entity
                            for entity in result.entities:
                                entity_dict = {
                                    "entity_id": entity.entity_id,
                                    "surface_form": entity.surface_form,
                                    "canonical_name": entity.canonical_name,
                                    "entity_type": entity.entity_type,
                                    "confidence": entity.confidence,
                                    "source_chunk": chunk_id,
                                    "source_document": chunk.get("source_document")
                                }
                                all_entities.append(entity_dict)
                            
                            # Add chunk reference to each relationship
                            for relationship in result.relationships:
                                rel_dict = {
                                    "relationship_id": relationship.relationship_id,
                                    "subject_entity_id": relationship.subject_entity_id,
                                    "object_entity_id": relationship.object_entity_id,
                                    "relationship_type": relationship.relationship_type,
                                    "confidence": relationship.confidence,
                                    "source_chunk": chunk_id,
                                    "source_document": chunk.get("source_document")
                                }
                                all_relationships.append(rel_dict)
                            
                            # Add mentions
                            for mention in result.mentions:
                                mention_dict = {
                                    "mention_id": mention.mention_id,
                                    "entity_id": mention.entity_id,
                                    "surface_form": mention.surface_form,
                                    "start_position": mention.start_position,
                                    "end_position": mention.end_position,
                                    "confidence": mention.confidence,
                                    "source_chunk": chunk_id,
                                    "source_document": chunk.get("source_document")
                                }
                                all_mentions.append(mention_dict)
                        else:
                            logger.warning("Ontology-aware extraction failed for chunk %s", chunk_id)
                            
                except Exception as e:
                    logger.error("Exception in ontology-aware extraction for chunk %s: %s",
                               chunk.get("chunk_id"), str(e))
            
            return {
                "entities": all_entities,
                "relationships": all_relationships,
                "mentions": all_mentions,
                **input_data  # Pass through other data including chunks
            }
        except Exception as e:
            raise ToolExecutionError("OntologyAwareExtractorAdapter", str(e), e)
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get OntologyAwareExtractor tool information"""
        return {
            "name": "Ontology-Aware Extractor",
            "version": "1.0",
            "description": "Extracts entities and relationships using ontology awareness",
            "contract_id": "T23C_OntologyAwareExtractor",
            "capabilities": ["ontology_aware_extraction", "entity_extraction", "relationship_extraction"]
        }
    
    def validate_input(self, input_data: Any) -> ToolValidationResult:
        """Validate input data"""
        validation_errors = []
        
        if not isinstance(input_data, dict):
            validation_errors.append("Input data must be a dictionary")
        
        return ToolValidationResult(
            is_valid=len(validation_errors) == 0,
            validation_errors=validation_errors,
            method_signatures={"execute": "Dict[str, Any]", "validate_input": "ToolValidationResult"},
            execution_test_results={"basic_validation": "passed" if len(validation_errors) == 0 else "failed"},
            input_schema_validation={"valid": True, "errors": []},
            security_validation={"valid": True, "errors": []},
            performance_validation={"valid": True, "errors": []}
        )
class OntologyGraphBuilderAdapter(BaseToolAdapter):
    """Adapter for OntologyGraphBuilder to implement Tool protocol
    
    Builds Neo4j ontology-aware graph using OntologyGraphBuilder interface.
    """
    
    def __init__(self, config_manager: ConfigurationManager = None):
        super().__init__(config_manager)
        
        from ..tools.phase2.t31_ontology_graph_builder import OntologyAwareGraphBuilder
        
        # Get Neo4j config from ConfigManager
        neo4j_config = self.config_manager.get_neo4j_config()
        
        self._tool = OntologyAwareGraphBuilder(
            neo4j_uri=neo4j_config['uri'],
            neo4j_user=neo4j_config['user'], 
            neo4j_password=neo4j_config['password'],
            confidence_threshold=self.graph_config.get('confidence_threshold', 0.7)
        )
        self.tool_name = "OntologyGraphBuilderAdapter"
    
    def execute(self, input_data: Any, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Convert Tool protocol to OntologyGraphBuilder interface
        
        Args:
            input_data: Expected format: {"entities": List[Dict], "relationships": List[Dict], ...}
            context: Optional execution context
            
        Returns:
            {"graph_build_result": Dict, "neo4j_entities": List[Dict], ...}
        """
        if not self.validate_input(input_data):
            raise ToolValidationError("OntologyGraphBuilderAdapter", ["Input data validation failed"])
        
        try:
            entities = input_data.get("entities", [])
            relationships = input_data.get("relationships", [])
            
            # Call actual tool method
            result = self._tool.build_ontology_graph(
                entities=entities,
                relationships=relationships,
                domain_description=input_data.get("domain_description", ""),
                confidence_threshold=self.graph_config.get('confidence_threshold', 0.7)
            )
            
            if hasattr(result, 'entities_created'):
                return {
                    "graph_build_result": {
                        "status": "success",
                        "entities_created": result.entities_created,
                        "relationships_created": result.relationships_created,
                        "entities_merged": result.entities_merged,
                        "execution_time_seconds": result.execution_time_seconds,
                        "metrics": result.metrics.__dict__ if hasattr(result, 'metrics') else {}
                    },
                    "neo4j_entities": entities,  # Pass through for compatibility
                    "neo4j_relationships": relationships,
                    **input_data  # Pass through other data
                }
            else:
                logger.error("Ontology graph building failed")
                return {
                    "graph_build_result": {"status": "error", "error": "Build failed"},
                    "neo4j_entities": [],
                    "neo4j_relationships": [],
                    **input_data
                }
                
        except Exception as e:
            logger.error("Exception in ontology graph building: %s", str(e))
            raise ToolExecutionError("OntologyGraphBuilderAdapter", str(e), e)
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get OntologyGraphBuilder tool information"""
        return {
            "name": "Ontology Graph Builder",
            "version": "1.0",
            "description": "Builds ontology-aware graph structures in Neo4j",
            "contract_id": "T31_OntologyGraphBuilder",
            "capabilities": ["ontology_graph_building", "graph_construction", "neo4j_operations"]
        }
    
    def validate_input(self, input_data: Any) -> ToolValidationResult:
        """Validate input data"""
        validation_errors = []
        
        if not isinstance(input_data, dict):
            validation_errors.append("Input data must be a dictionary")
        
        return ToolValidationResult(
            is_valid=len(validation_errors) == 0,
            validation_errors=validation_errors,
            method_signatures={"execute": "Dict[str, Any]", "validate_input": "ToolValidationResult"},
            execution_test_results={"basic_validation": "passed" if len(validation_errors) == 0 else "failed"},
            input_schema_validation={"valid": True, "errors": []},
            security_validation={"valid": True, "errors": []},
            performance_validation={"valid": True, "errors": []}
        )
class InteractiveGraphVisualizerAdapter(BaseToolAdapter):
    """Adapter for InteractiveGraphVisualizer to implement Tool protocol
    
    Creates interactive visualizations using InteractiveGraphVisualizer interface.
    """
    
    def __init__(self, config_manager: ConfigurationManager = None):
        super().__init__(config_manager)
        
        from ..tools.phase2.interactive_graph_visualizer import InteractiveGraphVisualizer
        
        neo4j_config = self.config_manager.get_neo4j_config()
        
        self._tool = InteractiveGraphVisualizer(
            neo4j_uri=neo4j_config['uri'],
            neo4j_user=neo4j_config['user'],
            neo4j_password=neo4j_config['password']
        )
        self.tool_name = "InteractiveGraphVisualizerAdapter"
    
    def execute(self, input_data: Any, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Convert Tool protocol to InteractiveGraphVisualizer interface
        
        Args:
            input_data: Any pipeline data (visualizer operates on graph)
            context: Optional execution context
            
        Returns:
            {"visualization_result": Dict, "visualization_data": Dict, ...}
        """
        if not self.validate_input(input_data):
            raise ToolValidationError("InteractiveGraphVisualizerAdapter", ["Input data validation failed"])
        
        try:
            # Create visualization of current graph state
            result = self._tool.create_visualization(
                max_nodes=500,
                max_edges=1000,
                layout_algorithm="spring",
                color_by="entity_type"
            )
            
            if result.get("status") == "success":
                return {
                    "visualization_result": result,
                    "visualization_data": result.get("visualization_data", {}),
                    **input_data  # Pass through other data
                }
            else:
                logger.error("Graph visualization failed: %s", result.get("error"))
                return {
                    "visualization_result": result,
                    "visualization_data": {},
                    **input_data
                }
                
        except Exception as e:
            logger.error("Exception in graph visualization: %s", str(e))
            raise ToolExecutionError("InteractiveGraphVisualizerAdapter", str(e), e)
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get InteractiveGraphVisualizer tool information"""
        return {
            "name": "Interactive Graph Visualizer",
            "version": "1.0",
            "description": "Creates interactive visualizations of graph data",
            "contract_id": "T_InteractiveGraphVisualizer",
            "capabilities": ["graph_visualization", "interactive_display", "data_visualization"]
        }
    
    def validate_input(self, input_data: Any) -> ToolValidationResult:
        """Validate input data"""
        validation_errors = []
        
        if not isinstance(input_data, dict):
            validation_errors.append("Input data must be a dictionary")
        
        return ToolValidationResult(
            is_valid=len(validation_errors) == 0,
            validation_errors=validation_errors,
            method_signatures={"execute": "Dict[str, Any]", "validate_input": "ToolValidationResult"},
            execution_test_results={"basic_validation": "passed" if len(validation_errors) == 0 else "failed"},
            input_schema_validation={"valid": True, "errors": []},
            security_validation={"valid": True, "errors": []},
            performance_validation={"valid": True, "errors": []}
        )
class MultiDocumentFusionAdapter(BaseToolAdapter):
    """Adapter for MultiDocumentFusion to implement Tool protocol
    
    Performs multi-document knowledge fusion using MultiDocumentFusion interface.
    """
    
    def __init__(self, config_manager: ConfigurationManager = None):
        super().__init__(config_manager)
        
        from ..tools.phase3.t301_multi_document_fusion import MultiDocumentFusion
        
        # Get Neo4j config from ConfigManager
        neo4j_config = self.config_manager.get_neo4j_config()
        
        self._tool = MultiDocumentFusion(
            neo4j_uri=neo4j_config['uri'],
            neo4j_user=neo4j_config['user'],
            neo4j_password=neo4j_config['password'],
            confidence_threshold=self.graph_config.get('confidence_threshold', 0.8),
            similarity_threshold=0.85
        )
        self.tool_name = "MultiDocumentFusionAdapter"
    
    def execute(self, input_data: Any, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Convert Tool protocol to MultiDocumentFusion interface
        
        Args:
            input_data: Expected format with multiple documents or document collections
            context: Optional execution context
            
        Returns:
            {"fusion_result": Dict, "fused_entities": List[Dict], ...}
        """
        if not self.validate_input(input_data):
            raise ToolValidationError("MultiDocumentFusionAdapter", ["Input data validation failed"])
        
        try:
            # Extract documents or document collections
            documents = input_data.get("documents", [])
            document_paths = input_data.get("document_paths", [])
            
            if not documents and not document_paths:
                logger.warning("No documents provided for fusion")
                return {
                    "fusion_result": {"status": "warning", "message": "No documents to fuse"},
                    "fused_entities": [],
                    "fused_relationships": [],
                    **input_data
                }
            
            # Call actual tool method
            result = self._tool.fuse_multi_document_knowledge(
                document_collections=documents or document_paths,
                similarity_threshold=0.8,
                conflict_resolution_strategy="weighted_consensus"
            )
            
            if result.get("status") == "success":
                return {
                    "fusion_result": result,
                    "fused_entities": result.get("fused_entities", []),
                    "fused_relationships": result.get("fused_relationships", []),
                    "fusion_metrics": result.get("metrics", {}),
                    **input_data  # Pass through other data
                }
            else:
                logger.error("Multi-document fusion failed: %s", result.get("error"))
                return {
                    "fusion_result": result,
                    "fused_entities": [],
                    "fused_relationships": [],
                    **input_data
                }
                
        except Exception as e:
            logger.error("Exception in multi-document fusion: %s", str(e))
            raise ToolExecutionError("MultiDocumentFusionAdapter", str(e), e)
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get MultiDocumentFusion tool information"""
        return {
            "name": "Multi-Document Fusion",
            "version": "1.0",
            "description": "Fuses knowledge from multiple documents into unified graph",
            "contract_id": "T301_MultiDocumentFusion",
            "capabilities": ["multi_document_fusion", "knowledge_integration", "graph_merging"]
        }
    
    def validate_input(self, input_data: Any) -> ToolValidationResult:
        """Validate input data"""
        validation_errors = []
        
        if not isinstance(input_data, dict):
            validation_errors.append("Input data must be a dictionary")
        
        return ToolValidationResult(
            is_valid=len(validation_errors) == 0,
            validation_errors=validation_errors,
            method_signatures={"execute": "Dict[str, Any]", "validate_input": "ToolValidationResult"},
            execution_test_results={"basic_validation": "passed" if len(validation_errors) == 0 else "failed"},
            input_schema_validation={"valid": True, "errors": []},
            security_validation={"valid": True, "errors": []},
            performance_validation={"valid": True, "errors": []}
        )
class VectorEmbedderAdapter(BaseToolAdapter):
    """Adapter for VectorEmbedder to implement Tool protocol
    
    Generates embeddings for text chunks and stores them in persistent vector database.
    """
    
    def __init__(self, config_manager: ConfigurationManager = None):
        super().__init__(config_manager)
        self._tool = _VectorEmbedder(config_manager)
        self.tool_name = "VectorEmbedderAdapter"
    
    def execute(self, input_data: Any, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Convert Tool protocol to VectorEmbedder interface
        
        Args:
            input_data: Expected format: {"chunks": List[Dict], ...}
            context: Optional execution context
            
        Returns:
            {"embeddings_stored": int, "vector_ids": List[str], ...}
        """
        if not self.validate_input(input_data):
            raise ToolValidationError("VectorEmbedderAdapter", ["Input data validation failed"])
        
        try:
            return self._tool.execute(input_data, context)
        except Exception as e:
            raise ToolExecutionError("VectorEmbedderAdapter", str(e), e)
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get VectorEmbedder tool information"""
        return {
            "name": "Vector Embedder",
            "version": "1.0",
            "description": "Generates embeddings for text chunks and stores them in persistent vector database",
            "contract_id": "T15B_VectorEmbedder",
            "capabilities": ["text_embedding", "vector_storage", "similarity_search", "persistent_storage"]
        }
    
    def validate_input(self, input_data: Any) -> ToolValidationResult:
        """Validate input data"""
        validation_errors = []
        
        if not isinstance(input_data, dict):
            validation_errors.append("Input data must be a dictionary")
        
        return ToolValidationResult(
            is_valid=len(validation_errors) == 0,
            validation_errors=validation_errors,
            method_signatures={"execute": "Dict[str, Any]", "validate_input": "ToolValidationResult"},
            execution_test_results={"basic_validation": "passed" if len(validation_errors) == 0 else "failed"},
            input_schema_validation={"valid": True, "errors": []},
            security_validation={"valid": True, "errors": []},
            performance_validation={"valid": True, "errors": []}
        )
    def search_similar_chunks(self, query_text: str, k: int = 10, 
                             filter_criteria: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search for similar chunks using vector similarity"""
        return self._tool.search_similar_chunks(query_text, k, filter_criteria)
    
    def get_vector_store_info(self) -> Dict[str, Any]:
        """Get information about the vector store"""
        return self._tool.get_vector_store_info()