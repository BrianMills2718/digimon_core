# Task 1.1: KGASTool Interface Contract Compliance

**Duration**: Days 1-3 (Week 1)  
**Owner**: Lead Developer  
**Priority**: BLOCKING - Prevents all tool integration

## Objective

Fix critical interface violations across all 14 tools by implementing proper KGASTool contracts, enabling tool chaining, service integration, and eliminating validation theater.

## Problem Analysis

### **Root Cause**
All tools implement legacy interface pattern instead of required KGASTool contracts:

```python
# CURRENT (WRONG) - Legacy Tool Interface
def execute(self, input_data: Any = None, context: Optional[Dict] = None) -> Dict[str, Any]:

# REQUIRED (CORRECT) - KGASTool Interface  
def execute(self, request: ToolRequest) -> ToolResult:
```

### **Impact Assessment**
- **Tool Chaining**: BROKEN - Cannot pass ToolResult → ToolRequest
- **Service Integration**: BROKEN - No standardized service access
- **Provenance Tracking**: BROKEN - Missing ToolResult metadata
- **Confidence Propagation**: BROKEN - No confidence score handling
- **Theory Awareness**: BROKEN - No TheorySchema integration

## Implementation Plan

### **Day 1: Critical Tool Fixes**

#### **Priority 1: T301 Multi-Document Fusion (IMMEDIATE)**
**Issue**: File contains wrong class entirely

**Current State**:
```python
# File: src/tools/phase3/t301_multi_document_fusion.py
class T301MultiDocumentFusionTool:  # Wrong class name pattern
    def execute(self, input_data: Any = None, context: Optional[Dict] = None):
        # Wrong signature
```

**Required Fix**:
```python
from src.core.tool_contract import KGASTool, ToolRequest, ToolResult
from typing import Dict, Any, List

class T301MultiDocumentFusion(KGASTool):
    """Multi-document entity fusion and resolution with cross-document analysis"""
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute multi-document fusion with proper contract compliance"""
        try:
            # Extract documents from request
            documents = request.input_data.get("documents", [])
            entities = request.input_data.get("entities", [])
            
            # Fusion logic
            fused_entities = self._perform_entity_fusion(entities)
            cross_doc_relationships = self._analyze_cross_document_patterns(documents)
            
            return ToolResult(
                status="success",
                data={
                    "fused_entities": fused_entities,
                    "cross_document_relationships": cross_doc_relationships,
                    "fusion_statistics": self._get_fusion_stats(entities, fused_entities)
                },
                confidence=self._calculate_fusion_confidence(fused_entities),
                metadata={
                    "tool_id": "T301",
                    "documents_processed": len(documents),
                    "entities_input": len(entities),
                    "entities_output": len(fused_entities)
                },
                provenance=self._create_fusion_provenance(request),
                request_id=request.request_id
            )
            
        except Exception as e:
            return ToolResult(
                status="error",
                data={},
                confidence=0.0,
                error_details=str(e),
                request_id=request.request_id
            )
    
    def get_theory_compatibility(self) -> List[str]:
        return ["document_fusion", "entity_resolution", "cross_modal_analysis"]
    
    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "documents": {"type": "array", "items": {"type": "string"}},
                "entities": {"type": "array", "items": {"type": "object"}}
            },
            "required": ["documents", "entities"]
        }
    
    def get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object", 
            "properties": {
                "fused_entities": {"type": "array"},
                "cross_document_relationships": {"type": "array"},
                "fusion_statistics": {"type": "object"}
            }
        }
    
    def validate_input(self, input_data: Any) -> ToolValidationResult:
        # Implement proper validation logic
        pass
```

#### **Priority 2: Core MVRT Tools Contract Updates**

**Tools to Fix**:
- T01 PDF Loader
- T15a Text Chunker  
- T15b Vector Embedder
- T23a SpaCy NER
- T23c Ontology-Aware Extractor

**Template for Each Tool**:
```python
from src.core.tool_contract import KGASTool, ToolRequest, ToolResult, ToolValidationResult
from src.core.confidence_score import ConfidenceScore

class T01PDFLoader(KGASTool):
    """Load and extract text from PDF documents with full contract compliance"""
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute PDF loading with proper error handling and provenance"""
        try:
            # Extract file path from request
            file_path = request.input_data.get("file_path")
            if not file_path:
                return self._create_error_result("Missing file_path", request.request_id)
            
            # Perform PDF loading
            extracted_text = self._load_pdf(file_path)
            metadata = self._extract_pdf_metadata(file_path)
            
            # Calculate confidence based on extraction quality
            confidence = self._calculate_extraction_confidence(extracted_text)
            
            return ToolResult(
                status="success",
                data={
                    "extracted_text": extracted_text,
                    "metadata": metadata,
                    "page_count": len(extracted_text.split('\n\n'))
                },
                confidence=confidence,
                metadata={
                    "tool_id": "T01",
                    "file_path": file_path,
                    "file_size": self._get_file_size(file_path)
                },
                provenance=self._create_pdf_provenance(request, file_path),
                request_id=request.request_id
            )
            
        except Exception as e:
            return self._create_error_result(str(e), request.request_id)
    
    def get_theory_compatibility(self) -> List[str]:
        return ["document_processing", "text_extraction"]
    
    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Path to PDF file"}
            },
            "required": ["file_path"]
        }
    
    def get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "extracted_text": {"type": "string"},
                "metadata": {"type": "object"},
                "page_count": {"type": "integer"}
            }
        }
    
    def validate_input(self, input_data: Any) -> ToolValidationResult:
        if not isinstance(input_data, dict):
            return ToolValidationResult(valid=False, error="Input must be dictionary")
        
        file_path = input_data.get("file_path")
        if not file_path:
            return ToolValidationResult(valid=False, error="Missing required field: file_path")
        
        if not file_path.endswith('.pdf'):
            return ToolValidationResult(valid=False, error="File must be PDF format")
        
        return ToolValidationResult(valid=True)
    
    def _create_error_result(self, error_msg: str, request_id: str) -> ToolResult:
        return ToolResult(
            status="error",
            data={},
            confidence=0.0,
            error_details=error_msg,
            request_id=request_id
        )
```

### **Day 2: Cross-Modal Tools Integration**

#### **Graph→Table Exporter Contract Update**
```python
class GraphTableExporter(KGASTool):
    """Export graph data to table formats with academic publication quality"""
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Convert graph to table with statistical analysis"""
        try:
            graph_data = request.input_data.get("graph")
            format_type = request.input_data.get("format", "csv")
            
            # Generate table with statistics
            table_data = self._convert_graph_to_table(graph_data)
            statistics = self._calculate_graph_statistics(graph_data)
            
            return ToolResult(
                status="success",
                data={
                    "table_data": table_data,
                    "statistics": statistics,
                    "format": format_type
                },
                confidence=self._calculate_conversion_confidence(graph_data, table_data),
                metadata={
                    "tool_id": "GraphTableExporter",
                    "nodes_processed": len(graph_data.get("nodes", [])),
                    "edges_processed": len(graph_data.get("edges", []))
                },
                provenance=self._create_conversion_provenance(request),
                request_id=request.request_id
            )
            
        except Exception as e:
            return self._create_error_result(str(e), request.request_id)
```

#### **Multi-Format Exporter Contract Update**
```python
class MultiFormatExporter(KGASTool):
    """Export data to multiple academic formats (LaTeX, BibTeX, etc.)"""
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Generate publication-ready academic outputs"""
        try:
            data = request.input_data.get("data")
            formats = request.input_data.get("formats", ["latex", "bibtex"])
            
            # Generate exports for each format
            exports = {}
            for format_type in formats:
                exports[format_type] = self._generate_export(data, format_type)
            
            return ToolResult(
                status="success",
                data={
                    "exports": exports,
                    "formats_generated": list(exports.keys())
                },
                confidence=self._calculate_export_quality(exports),
                metadata={
                    "tool_id": "MultiFormatExporter",
                    "formats_requested": len(formats),
                    "exports_generated": len(exports)
                },
                provenance=self._create_export_provenance(request),
                request_id=request.request_id
            )
            
        except Exception as e:
            return self._create_error_result(str(e), request.request_id)
```

### **Day 3: Specialized Tools and Validation**

#### **Remaining Tools to Update**
- T27 Relationship Extractor
- T31 Entity Builder
- T34 Edge Builder  
- T41 Async Text Embedder
- T49 Multi-Hop Query
- T68 PageRank Optimized

#### **Tool Chain Integration Testing**
```python
# File: tests/integration/test_tool_chain_integration.py

def test_complete_tool_chain():
    """Test tools can be chained together with new contracts"""
    
    # Create test request
    pdf_request = ToolRequest(
        input_data={"file_path": "test_data/sample.pdf"},
        request_id="test_001"
    )
    
    # Step 1: PDF Loading
    pdf_loader = T01PDFLoader()
    pdf_result = pdf_loader.execute(pdf_request)
    assert pdf_result.status == "success"
    
    # Step 2: Text Chunking (chained from PDF result)
    chunk_request = ToolRequest(
        input_data={"text": pdf_result.data["extracted_text"]},
        request_id="test_002"
    )
    
    chunker = T15aTextChunker()
    chunk_result = chunker.execute(chunk_request)
    assert chunk_result.status == "success"
    
    # Step 3: Entity Extraction (chained from chunk result)
    entity_request = ToolRequest(
        input_data={"chunks": chunk_result.data["chunks"]},
        request_id="test_003"
    )
    
    extractor = T23cOntologyAwareExtractor()
    entity_result = extractor.execute(entity_request)
    assert entity_result.status == "success"
    
    # Verify provenance chain
    assert pdf_result.request_id == "test_001"
    assert chunk_result.request_id == "test_002"
    assert entity_result.request_id == "test_003"
    
    # Verify data compatibility
    assert chunk_result.data["chunks"]
    assert entity_result.data["entities"]
```

## Success Criteria

### **Functional Requirements**
- [ ] All 14 tools implement KGASTool interface
- [ ] All tools pass contract compliance validation
- [ ] Tools can be chained in workflows without parameter mismatches
- [ ] ToolResult → ToolRequest conversion works properly

### **Quality Requirements**
- [ ] No validation theater - all testing uses real data
- [ ] Proper error handling with detailed error messages
- [ ] Confidence scores calculated and propagated
- [ ] Provenance tracking through tool chains

### **Integration Requirements**
- [ ] Service integration works through ToolRequest context
- [ ] Theory-aware tools access ontology through request
- [ ] Cross-modal data flows properly between tools
- [ ] Academic output quality maintained

## Validation Plan

### **Contract Compliance Testing**
```bash
# Test all tools implement required interface
python -c "
from src.core.tool_contract import KGASTool
from src.tools.phase1.t01_pdf_loader import T01PDFLoader
assert issubclass(T01PDFLoader, KGASTool)
print('✅ T01 implements KGASTool')
"

# Test method signatures
python -c "
import inspect
from src.tools.phase1.t01_pdf_loader import T01PDFLoader
tool = T01PDFLoader()
sig = inspect.signature(tool.execute)
assert 'request' in sig.parameters
print('✅ T01 has correct execute signature')
"
```

### **Real Data Integration Testing**
```bash
# Test with actual academic paper
python -c "
from src.core.tool_contract import ToolRequest
from src.tools.phase1.t01_pdf_loader import T01PDFLoader

request = ToolRequest(
    input_data={'file_path': 'test_data/real_paper.pdf'},
    request_id='real_test_001'
)

tool = T01PDFLoader()
result = tool.execute(request)
assert result.status == 'success'
assert len(result.data['extracted_text']) > 100
print('✅ T01 processes real PDF successfully')
"
```

## Risk Mitigation

### **Breaking Changes**
- **Risk**: Tool interface changes break existing code
- **Mitigation**: Gradual migration with backward compatibility wrappers

### **Integration Failures**
- **Risk**: Tools still can't chain together after updates
- **Mitigation**: Comprehensive integration testing at each step

### **Performance Regression**
- **Risk**: New interface adds overhead
- **Mitigation**: Performance benchmarking before/after changes

## Deliverables

1. **14 Updated Tool Files** with KGASTool contract compliance
2. **Integration Test Suite** verifying tool chaining works
3. **Migration Documentation** for any dependent code
4. **Performance Benchmarks** showing no regression
5. **Real Data Validation** proving tools work with academic papers

---

**Next Action**: Begin with T301 fix (wrong class) then proceed through core MVRT tools systematically.