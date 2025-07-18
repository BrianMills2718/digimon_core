# ⚠️ EXPERIMENTAL - Tool Contract & Ontology Validation System

## ⚠️ Development Status

**NOT PRODUCTION READY**

This is an experimental validation framework that:
- Demonstrates contract-based validation concepts
- Provides semantic validation via ontology
- Has NOT been integrated with the main pipeline
- Requires extensive testing before production use

## Overview

This experimental implementation demonstrates concepts for structured compatibility and programmatic verification of tool contracts.

## 📏 Scope & Limitations

This validation framework:
- Validates 8 specific tools from the main pipeline
- Demonstrates contract and ontology concepts  
- Has NOT been integrated with the main project
- Would need significant work to scale to more tools
- Performance impact not measured with real data
- Requires extensive testing before any production use

## ✅ Core Components Implemented

### 1. Structured Data Models (`src/core/data_models.py`)
- **BaseObject** foundation class with identity, quality, and provenance tracking
- **Standardized data types**: Document, Chunk, Entity, Relationship, WorkflowState
- **Universal reference system** for object linking (`neo4j://type/id`)
- **Pydantic validation** with proper optional field handling
- **Quality and confidence tracking** built into every object
- **Ontology integration** with properties and modifiers fields

### 2. Tool Contract Schema (`contracts/schemas/tool_contract_schema.yaml`)
- **JSON Schema definition** for contract validation
- **Structured format** for input/output requirements
- **State management** for workflow tracking
- **Error code standardization** with severity levels
- **Automatic validation** against schema
- **Ontology constraint specifications** for semantic validation

### 3. Contract Validator (`src/core/contract_validator.py`)
- **Contract loading and validation** against schema
- **Tool interface verification** (method signatures, etc.)
- **Data flow validation** with test input/output
- **Batch validation** for entire contract directories
- **Comprehensive reporting** with detailed error messages
- **Ontology validation** for entities and relationships

### 4. Master Concept Library (`src/ontology_library/`)
- **Pre-constructed ontology** from social/behavioral science theories
- **88 standardized concepts**: 16 entities, 23 connections, 29 properties, 20 modifiers
- **Academic grounding** with references to source theories
- **Domain/range constraints** for relationship validation
- **Singleton service** for consistent access across tools
- **YAML-based definitions** for easy extension

## 📁 Directory Structure

```
compatability_code/
├── src/
│   ├── core/
│   │   ├── data_models.py          # Pydantic data models
│   │   ├── contract_validator.py   # Validation engine
│   │   └── ontology_validator.py   # Ontology validation
│   └── ontology_library/
│       ├── master_concepts.py      # Concept models
│       ├── ontology_service.py     # Singleton service
│       └── concepts/
│           ├── entities.yaml       # Entity definitions
│           ├── connections.yaml    # Relationship definitions
│           ├── properties.yaml     # Property definitions
│           └── modifiers.yaml      # Modifier definitions
├── contracts/
│   ├── schemas/
│   │   └── tool_contract_schema.yaml  # Contract schema
│   ├── tools/                        # 8 tool contracts
│   │   ├── T01_PDFLoader.yaml
│   │   ├── T15A_TextChunker.yaml
│   │   ├── T23A_SpacyNER.yaml
│   │   ├── T27_RelationshipExtractor.yaml
│   │   ├── T31_EntityBuilder.yaml
│   │   ├── T34_EdgeBuilder.yaml
│   │   ├── T49_MultiHopQuery.yaml
│   │   └── T68_PageRank.yaml
│   └── adapters/
│       └── Phase1ToPhase2Adapter.yaml # Phase adapter
├── scripts/
│   └── validate_contracts.py   # CI/CD integration script
├── tests/
│   ├── test_contract_validation.py  # Contract tests
│   └── test_ontology_integration.py # Ontology tests
├── docs/
│   └── MASTER_CONCEPT_LIBRARY.md    # Ontology documentation
├── demo_contract_system.py     # Contract demo
├── demo_ontology_integration.py # Ontology demo
└── README.md                   # This file
```

## 🚀 Quick Start

### Run the Contract System Demo
```bash
python demo_contract_system.py
```

### Run the Ontology Integration Demo
```bash
python demo_ontology_integration.py
```

### Validate All Contracts
```bash
python scripts/validate_contracts.py --verbose
```

### Run All Tests
```bash
# Contract validation tests
python tests/test_contract_validation.py

# Ontology integration tests
python tests/test_ontology_integration.py
```

## 📋 Example Contract (T01_PDF_Loader.yaml)

```yaml
tool_id: T01_PDF_LOADER
description: Loads PDF files and extracts raw text content using OCR when necessary
category: Ingestion

input_contract:
  required_data_types: []  # No input data types, it's a source tool
  required_state: {}       # No specific state needed, it's an entry point

output_contract:
  produced_data_types:
    - type: Document
      attributes: 
        - content
        - original_filename
        - id
        - object_type
        - confidence
        - quality_tier
        - created_by
        - created_at
        - workflow_id
        - version
  produced_state:
    document_loaded: true

error_codes:
  - code: FILE_NOT_FOUND
    description: The specified file path does not exist
    severity: error
  - code: OCR_FAILED
    description: Optical Character Recognition failed on the PDF
    severity: warning
```

## 🔧 Usage Examples

### Programmatic Contract Validation

```python
from core.contract_validator import ContractValidator

# Initialize validator
validator = ContractValidator("contracts")

# Load and validate a contract
contract = validator.load_contract("T01_PDF_Loader")
schema_errors = validator.validate_contract_schema(contract)

# Validate tool implementation
errors = validator.validate_tool_interface(tool_instance, contract)

# Test data flow
success, errors, output = validator.validate_data_flow(
    tool_instance, contract, test_input
)
```

### Creating Test Data

```python
from core.contract_validator import ContractTestFramework

test_framework = ContractTestFramework(validator)

# Create test objects
test_doc = test_framework.create_test_data(
    "Document", 
    content="Test content",
    original_filename="test.pdf"
)

test_chunk = test_framework.create_test_data(
    "Chunk",
    content="Test chunk",
    document_ref=test_doc.to_reference(),
    position=0
)
```

### CI/CD Integration

```bash
# Basic validation (exit code 0 = success, 1 = failure)
python scripts/validate_contracts.py

# Verbose output with detailed errors
python scripts/validate_contracts.py --verbose

# Generate report for CI artifacts
python scripts/validate_contracts.py --output validation_report.json
```

## ✨ Key Benefits Achieved

### De-risking
- ✅ **Catch integration issues early** through automated validation
- ✅ **Prevent API breaking changes** with contract enforcement
- ✅ **Ensure data compatibility** across tool boundaries
- ✅ **Validate tool chains** before deployment

### Scalability
- ✅ **Standardized interfaces** enable independent tool development
- ✅ **Automated testing** reduces manual validation overhead
- ✅ **Clear contracts** improve developer onboarding
- ✅ **Modular architecture** for potential tool expansion

### Quality Assurance
- ✅ **Consistent data formats** across all tools
- ✅ **Provenance tracking** for audit trails
- ✅ **Quality metrics** built into all data objects
- ✅ **Error handling** standardized across tools

## 📦 Available Contracts (8 tools)

- **T01_PDFLoader** - PDF document loading
- **T15A_TextChunker** - Text segmentation  
- **T23A_SpacyNER** - Entity extraction
- **T27_RelationshipExtractor** - Relationship extraction
- **T31_EntityBuilder** - Neo4j entity persistence
- **T34_EdgeBuilder** - Neo4j relationship persistence
- **T49_MultiHopQuery** - Graph traversal
- **T68_PageRank** - Graph centrality

## 🎯 Validation Example Output

When running validation, the system shows:

```
📊 Validation Summary:
  → Total contracts: 8
  → Valid contracts: 8 (when properly implemented)
  → Invalid contracts: 0

📝 Example Results:
  ✅ Tool: T01_PDFLoader (Ingestion)
    → Inputs: None → Outputs: Document
  ✅ Tool: T15A_TextChunker (Processing)  
    → Inputs: Document → Outputs: Chunk
  ... (and 6 more tools)
```

## 🔄 Tool Chain Compatibility

The system demonstrates successful validation of tool chains:

1. **T01_PDF_Loader** produces `Document` objects
2. **T15A_Text_Chunker** consumes `Document`, produces `Chunk` objects  
3. **Phase1ToPhase2Adapter** transforms `Chunk` to `TextForLLMProcessing`

Each tool's output contract matches the next tool's input contract, ensuring compatibility.

## 🔬 Experimental Concepts Demonstrated

This prototype explores approaches for tool validation:

### Challenges Addressed (Conceptually)
- Manual integration testing
- Inconsistent data formats
- Breaking changes detection
- Tool onboarding clarity
- Testing complexity

### Concepts Demonstrated
- Contract validation patterns
- Standardized data models with Pydantic
- CI/CD integration examples
- Contract specifications for tools
- Testing through contracts

## 📊 Current Implementation Status

This experimental system demonstrates:

- **Contract validation concepts** for tool interfaces
- **Basic CI/CD integration** examples
- **Error reporting** mechanisms
- **Extensible architecture** patterns
- **Testing framework** prototypes
- **Semantic validation** ideas through concept library

## 🌟 Master Concept Library Impact

The addition of the Master Concept Library transforms the system from syntactic to **semantic validation**:

### Before (Syntactic Only)
- ✓ Entity has required fields
- ✓ Relationship connects two IDs
- ✗ No meaning validation
- ✗ Any string accepted as type

### After (Semantic + Syntactic)
- ✓ Entity type exists in ontology
- ✓ Properties match entity type
- ✓ Relationship respects domain/range
- ✓ Modifiers have valid values
- ✓ Theory-grounded extractions

This creates a **knowledge-aware** compatibility system that ensures not just structural correctness but **semantic meaningfulness** aligned with social science theories.

This experimental foundation demonstrates concepts that could potentially be applied to larger tool ecosystems, but requires significant development and testing before any production use.

## ⚠️ Known Limitations

1. **Not Integrated** - This code has NOT been integrated with the main GraphRAG pipeline
2. **Limited Testing** - Only tested with synthetic data, not real-world documents
3. **Performance Unknown** - No performance benchmarks with realistic data volumes
4. **Incomplete Validation** - `data_models.py` only logs warnings, doesn't enforce validation
5. **Error Handling** - Missing error handling for ontology concept mismatches
6. **Scale Limitations** - Only 8 tools validated, scaling to 100+ tools untested
7. **Ontology Rigidity** - Fixed ontology may be too restrictive for diverse data
8. **No Integration Tests** - Lacks tests simulating main pipeline integration