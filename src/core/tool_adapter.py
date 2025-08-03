"""Tool Adapter - Convert existing tools to KGASTool interface

Provides adapters to make existing MVRT tools compatible with the new
KGASTool interface without requiring complete rewrites.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime

from .tool_contract import (
    KGASTool, ToolRequest, ToolResult, ToolValidationResult,
    tool_execution_wrapper
)
from .confidence_score import ConfidenceScore
from .service_manager import get_service_manager


class LegacyToolAdapter(KGASTool):
    """Adapter to wrap existing tools in KGASTool interface."""
    
    def __init__(self, legacy_tool: Any, tool_id: str, tool_name: str):
        """Initialize adapter with legacy tool instance.
        
        Args:
            legacy_tool: Existing tool instance
            tool_id: Tool identifier
            tool_name: Human-readable tool name
        """
        super().__init__(tool_id, tool_name)
        self.legacy_tool = legacy_tool
        self.description = getattr(legacy_tool, 'description', '')
        self.category = getattr(legacy_tool, 'category', 'legacy')
        self.version = getattr(legacy_tool, 'version', '1.0.0')
    
    @tool_execution_wrapper
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute legacy tool with new interface."""
        start_time = datetime.now()
        
        try:
            # Convert ToolRequest to legacy format
            legacy_input = self._convert_request_to_legacy(request)
            
            # Execute legacy tool
            if hasattr(self.legacy_tool, 'execute'):
                # Tool has execute method
                legacy_result = self.legacy_tool.execute(legacy_input)
            elif hasattr(self.legacy_tool, 'load_pdf') and 'T01' in self.tool_id:
                # PDF Loader tool
                file_path = legacy_input.get('file_path') or legacy_input
                workflow_id = legacy_input.get('workflow_id') if isinstance(legacy_input, dict) else request.workflow_id
                legacy_result = self.legacy_tool.load_pdf(file_path, workflow_id)
            elif hasattr(self.legacy_tool, 'chunk_text') and 'T15A' in self.tool_id:
                # Text Chunker tool
                document_ref = legacy_input.get('document_ref', '')
                text_content = legacy_input.get('text_content', '')
                confidence = legacy_input.get('confidence', 0.8)
                legacy_result = self.legacy_tool.chunk_text(document_ref, text_content, confidence)
            elif hasattr(self.legacy_tool, 'extract_entities') and 'T23' in self.tool_id:
                # Entity extraction tools
                source_ref = legacy_input.get('source_ref', '')
                text_content = legacy_input.get('text_content', '')
                source_confidence = legacy_input.get('source_confidence', 0.8)
                legacy_result = self.legacy_tool.extract_entities(source_ref, text_content, source_confidence)
            elif hasattr(self.legacy_tool, 'extract_relationships') and 'T27' in self.tool_id:
                # Relationship extractor
                source_ref = legacy_input.get('source_ref', '')
                text_content = legacy_input.get('text_content', '')
                entities = legacy_input.get('entities', [])
                source_confidence = legacy_input.get('source_confidence', 0.8)
                legacy_result = self.legacy_tool.extract_relationships(source_ref, text_content, entities, source_confidence)
            elif hasattr(self.legacy_tool, 'build_entities') and 'T31' in self.tool_id:
                # Entity builder
                mentions = legacy_input.get('mentions', [])
                source_refs = legacy_input.get('source_refs', [])
                legacy_result = self.legacy_tool.build_entities(mentions, source_refs)
            elif hasattr(self.legacy_tool, 'build_edges') and 'T34' in self.tool_id:
                # Edge builder
                relationships = legacy_input.get('relationships', [])
                source_refs = legacy_input.get('source_refs', [])
                legacy_result = self.legacy_tool.build_edges(relationships, source_refs)
            elif hasattr(self.legacy_tool, 'calculate_pagerank') and 'T68' in self.tool_id:
                # PageRank calculator
                graph_ref = legacy_input.get('graph_ref', "neo4j://graph/main")
                legacy_result = self.legacy_tool.calculate_pagerank(graph_ref)
            elif hasattr(self.legacy_tool, 'query_graph') and 'T49' in self.tool_id:
                # Multi-hop query
                query = legacy_input.get('query', legacy_input)
                legacy_result = self.legacy_tool.query_graph(query)
            else:
                # Generic execute attempt
                if hasattr(self.legacy_tool, '__call__'):
                    legacy_result = self.legacy_tool(legacy_input)
                else:
                    raise ValueError(f"Cannot execute legacy tool {self.tool_id} - no compatible method found")
            
            # Convert legacy result to ToolResult
            return self._convert_legacy_result(legacy_result, request, start_time)
            
        except Exception as e:
            return self.create_error_result(
                request,
                f"Legacy tool execution failed: {str(e)}",
                str(e)
            )
    
    def get_theory_compatibility(self) -> List[str]:
        """Get theory compatibility from legacy tool."""
        if hasattr(self.legacy_tool, 'get_theory_compatibility'):
            return self.legacy_tool.get_theory_compatibility()
        elif hasattr(self.legacy_tool, 'supported_theories'):
            return self.legacy_tool.supported_theories
        elif 'T23C' in self.tool_id or 'ONTOLOGY' in self.tool_id.upper():
            # Theory-aware tools
            return ['general', 'academic', 'business']
        else:
            return []
    
    def get_input_schema(self) -> Dict[str, Any]:
        """Get input schema from legacy tool."""
        if hasattr(self.legacy_tool, 'get_input_schema'):
            return self.legacy_tool.get_input_schema()
        else:
            # Generate basic schema based on tool type
            return self._generate_basic_input_schema()
    
    def get_output_schema(self) -> Dict[str, Any]:
        """Get output schema from legacy tool."""
        if hasattr(self.legacy_tool, 'get_output_schema'):
            return self.legacy_tool.get_output_schema()
        else:
            # Generate basic schema based on tool type
            return self._generate_basic_output_schema()
    
    def validate_input(self, input_data: Any) -> ToolValidationResult:
        """Validate input for legacy tool."""
        result = ToolValidationResult(True)
        
        # Basic validation
        if input_data is None:
            result.add_error("Input data cannot be None")
            return result
        
        # Tool-specific validation
        if 'T01' in self.tool_id:
            # PDF Loader validation
            if isinstance(input_data, dict):
                file_path = input_data.get('file_path')
            else:
                file_path = input_data
            
            if not file_path or not isinstance(file_path, str):
                result.add_error("file_path is required and must be a string")
        
        elif 'T15A' in self.tool_id:
            # Text Chunker validation
            if not isinstance(input_data, dict):
                result.add_error("Input must be a dictionary")
            else:
                if 'text_content' not in input_data:
                    result.add_error("text_content is required")
        
        elif 'T23' in self.tool_id:
            # Entity extraction validation
            if not isinstance(input_data, dict):
                result.add_error("Input must be a dictionary")
            else:
                if 'text_content' not in input_data:
                    result.add_error("text_content is required")
        
        elif 'T49' in self.tool_id:
            # Query validation
            if isinstance(input_data, dict):
                query = input_data.get('query')
            else:
                query = input_data
            
            if not query or not isinstance(query, str):
                result.add_error("query is required and must be a string")
        
        return result
    
    def _convert_request_to_legacy(self, request: ToolRequest) -> Any:
        """Convert ToolRequest to legacy tool input format."""
        input_data = request.input_data
        
        # Add context from request to input_data if it's a dict
        if isinstance(input_data, dict):
            legacy_input = dict(input_data)
            legacy_input['workflow_id'] = request.workflow_id
            
            # Add theory context if tool supports it
            if request.theory_schema and self.supports_theory(request.theory_schema.theory_id):
                legacy_input['theory_schema'] = request.theory_schema
                legacy_input['ontology_context'] = request.theory_schema.ontology_definitions
            
            # Add concept library if available
            if request.concept_library:
                legacy_input['concept_library'] = request.concept_library
            
            return legacy_input
        else:
            return input_data
    
    def _convert_legacy_result(self, legacy_result: Any, request: ToolRequest, start_time: datetime) -> ToolResult:
        """Convert legacy tool result to ToolResult."""
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # Get service manager for provenance
        service_manager = get_service_manager()
        provenance_service = service_manager.provenance_service
        
        # Handle different legacy result formats
        if isinstance(legacy_result, dict):
            status = legacy_result.get('status', 'success')
            data = legacy_result.get('data', legacy_result)
            
            # Extract confidence
            confidence_value = legacy_result.get('confidence', 0.8)
            if isinstance(confidence_value, dict):
                confidence = ConfidenceScore(**confidence_value)
            elif isinstance(confidence_value, (int, float)):
                confidence = ConfidenceScore.create_medium_confidence(value=float(confidence_value))
            else:
                confidence = ConfidenceScore.create_medium_confidence()
            
            # Handle error cases
            if status == 'error':
                error_msg = legacy_result.get('error', 'Unknown error')
                return self.create_error_result(request, error_msg)
            
            # Create provenance record
            provenance_record = provenance_service.create_tool_execution_record(
                tool_id=self.tool_id,
                workflow_id=request.workflow_id,
                input_summary=str(type(request.input_data).__name__),
                success=(status == 'success'),
                metadata={
                    'legacy_tool': True,
                    'execution_time': execution_time,
                    'status': status
                }
            )
            
            return ToolResult(
                status=status,
                data=data,
                confidence=confidence,
                metadata={
                    'tool_id': self.tool_id,
                    'legacy_tool': True,
                    'execution_time': execution_time,
                    **legacy_result.get('metadata', {})
                },
                provenance=provenance_record,
                request_id=request.request_id,
                execution_time=execution_time,
                warnings=legacy_result.get('warnings', [])
            )
        else:
            # Non-dict result - wrap it
            confidence = ConfidenceScore.create_medium_confidence()
            
            provenance_record = provenance_service.create_tool_execution_record(
                tool_id=self.tool_id,
                workflow_id=request.workflow_id,
                input_summary=str(type(request.input_data).__name__),
                success=True,
                metadata={
                    'legacy_tool': True,
                    'execution_time': execution_time
                }
            )
            
            return ToolResult(
                status='success',
                data=legacy_result,
                confidence=confidence,
                metadata={
                    'tool_id': self.tool_id,
                    'legacy_tool': True,
                    'execution_time': execution_time
                },
                provenance=provenance_record,
                request_id=request.request_id,
                execution_time=execution_time
            )
    
    def _generate_basic_input_schema(self) -> Dict[str, Any]:
        """Generate basic input schema based on tool type."""
        if 'T01' in self.tool_id:
            return {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Path to PDF file"}
                },
                "required": ["file_path"]
            }
        elif 'T15A' in self.tool_id:
            return {
                "type": "object",
                "properties": {
                    "document_ref": {"type": "string"},
                    "text_content": {"type": "string"},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1}
                },
                "required": ["text_content"]
            }
        elif 'T23' in self.tool_id:
            return {
                "type": "object",
                "properties": {
                    "source_ref": {"type": "string"},
                    "text_content": {"type": "string"},
                    "source_confidence": {"type": "number", "minimum": 0, "maximum": 1}
                },
                "required": ["text_content"]
            }
        elif 'T49' in self.tool_id:
            return {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Natural language query"}
                },
                "required": ["query"]
            }
        else:
            return {
                "type": "object",
                "properties": {
                    "data": {"type": "object"}
                },
                "required": ["data"]
            }
    
    def _generate_basic_output_schema(self) -> Dict[str, Any]:
        """Generate basic output schema based on tool type."""
        return {
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": ["success", "error"]},
                "data": {"type": "object"},
                "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                "metadata": {"type": "object"}
            },
            "required": ["status", "data"]
        }


def adapt_legacy_tool(legacy_tool: Any, tool_id: str, tool_name: str) -> LegacyToolAdapter:
    """Create adapter for legacy tool."""
    return LegacyToolAdapter(legacy_tool, tool_id, tool_name)


def create_mvrt_tool_adapters() -> Dict[str, LegacyToolAdapter]:
    """Create adapters for all MVRT tools."""
    adapters = {}
    
    try:
        # T01: PDF Loader
        from src.tools.phase1.t01_pdf_loader import PDFLoader
        pdf_loader = PDFLoader()
        adapters['T01_PDF_LOADER'] = adapt_legacy_tool(pdf_loader, 'T01_PDF_LOADER', 'PDF Document Loader')
    except Exception as e:
        print(f"Failed to load T01_PDF_LOADER: {e}")
        pass
    
    try:
        # T15A: Text Chunker
        from src.tools.phase1.t15a_text_chunker import TextChunker
        text_chunker = TextChunker()
        adapters['T15A_TEXT_CHUNKER'] = adapt_legacy_tool(text_chunker, 'T15A_TEXT_CHUNKER', 'Text Chunker')
    except Exception as e:
        print(f"Failed to load T15A_TEXT_CHUNKER: {e}")
        pass
    
    try:
        # T15B: Vector Embedder
        from src.tools.phase1.t15b_vector_embedder import VectorEmbedder
        vector_embedder = VectorEmbedder()
        adapters['T15B_VECTOR_EMBEDDER'] = adapt_legacy_tool(vector_embedder, 'T15B_VECTOR_EMBEDDER', 'Vector Embedder')
    except Exception as e:
        print(f"Failed to load T15B_VECTOR_EMBEDDER: {e}")
        pass
    
    try:
        # T23A: SpaCy NER
        from src.tools.phase1.t23a_spacy_ner import SpacyNER
        spacy_ner = SpacyNER()
        adapters['T23A_SPACY_NER'] = adapt_legacy_tool(spacy_ner, 'T23A_SPACY_NER', 'SpaCy Named Entity Recognition')
    except Exception as e:
        print(f"Failed to load T23A_SPACY_NER: {e}")
        pass
    
    try:
        # T23C: Ontology-Aware Extractor
        from src.tools.phase2.t23c_ontology_aware_extractor import OntologyAwareExtractor
        ontology_extractor = OntologyAwareExtractor()
        adapters['T23C_ONTOLOGY_AWARE_EXTRACTOR'] = adapt_legacy_tool(ontology_extractor, 'T23C_ONTOLOGY_AWARE_EXTRACTOR', 'Ontology-Aware Entity Extractor')
    except Exception as e:
        print(f"Failed to load T23C_ONTOLOGY_AWARE_EXTRACTOR: {e}")
        pass
    
    try:
        # T27: Relationship Extractor
        from src.tools.phase1.t27_relationship_extractor import RelationshipExtractor
        rel_extractor = RelationshipExtractor()
        adapters['T27_RELATIONSHIP_EXTRACTOR'] = adapt_legacy_tool(rel_extractor, 'T27_RELATIONSHIP_EXTRACTOR', 'Relationship Extractor')
    except Exception as e:
        print(f"Failed to load T27_RELATIONSHIP_EXTRACTOR: {e}")
        pass
    
    try:
        # T31: Entity Builder (skip due to Neo4j config issues)
        print("Skipping T31_ENTITY_BUILDER due to Neo4j configuration requirements")
        pass
    except Exception as e:
        print(f"Failed to load T31_ENTITY_BUILDER: {e}")
        pass
    
    try:
        # T34: Edge Builder (skip due to Neo4j config issues)
        print("Skipping T34_EDGE_BUILDER due to Neo4j configuration requirements")
        pass
    except Exception as e:
        print(f"Failed to load T34_EDGE_BUILDER: {e}")
        pass
    
    try:
        # T49: Multi-hop Query
        from src.tools.phase1.t49_multihop_query import MultiHopQuery
        multihop_query = MultiHopQuery()
        adapters['T49_MULTIHOP_QUERY'] = adapt_legacy_tool(multihop_query, 'T49_MULTIHOP_QUERY', 'Multi-hop Query Engine')
    except Exception as e:
        print(f"Failed to load T49_MULTIHOP_QUERY: {e}")
        pass
    
    try:
        # T68: PageRank (skip due to Neo4j config issues)
        print("Skipping T68_PAGERANK due to Neo4j configuration requirements")
        pass
    except Exception as e:
        print(f"Failed to load T68_PAGERANK: {e}")
        pass
    
    try:
        # T301: Multi-Document Fusion
        from src.tools.phase3.t301_multi_document_fusion import MultiDocumentFusion
        multidoc_fusion = MultiDocumentFusion()
        adapters['T301_MULTI_DOCUMENT_FUSION'] = adapt_legacy_tool(multidoc_fusion, 'T301_MULTI_DOCUMENT_FUSION', 'Multi-Document Fusion')
    except Exception as e:
        print(f"Failed to load T301_MULTI_DOCUMENT_FUSION: {e}")
        pass
    
    return adapters


def register_all_mvrt_tools():
    """Register all MVRT tools in the global registry using auto-registration."""
    from .tool_contract import register_tool
    from .tool_registry_auto import ToolAutoRegistry
    
    # Use auto-registration to discover and register all tools
    registry = ToolAutoRegistry()
    results = registry.auto_register_all_tools()
    
    # Register discovered tools in the global registry
    registered_count = 0
    for tool_id in results.registered_tools:
        tool = registry.get_tool(tool_id)
        if tool:
            register_tool(tool)
            registered_count += 1
    
    print(f"Registered {registered_count} tools from auto-discovery")
    
    # Also try the legacy adapters for any tools not in auto-registry
    try:
        adapters = create_mvrt_tool_adapters()
        for tool_id, adapter in adapters.items():
            if tool_id not in results.registered_tools:
                register_tool(adapter)
                registered_count += 1
                print(f"Registered legacy adapter for {tool_id}")
    except Exception as e:
        print(f"Error loading legacy adapters: {e}")
    
    return results.registered_tools