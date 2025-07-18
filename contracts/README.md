# 🚀 Current Workstream: Theory Schema & Contract System Integration (A1/A2)

The contract system is now the focus of active development, with the following goals:
- Enforce version checking and theory schema validation for all core services
- Define and maintain immutable, theory-aware interfaces for all phases in the `contracts/` directory
- Document and enforce contract-based phase interfaces (`GraphRAGPhase`, `ProcessingRequest`, `ProcessingResult`)
- Integrate contract validation and theory schema compliance into CI and verification workflows

See `docs/planning/roadmap.md` and `docs/architecture/ARCHITECTURE.md` for progress and architectural context.

# Tool Contract System

This directory contains the structured contract definitions for all tools and adapters in the GraphRAG system. The contract system enables programmatic verification of tool compatibility and automated testing of the 121-tool ecosystem.

## Overview

The contract system consists of three core components:

1. **Structured Data Models** (`src/core/data_models.py`) - Pydantic models defining standardized data types
2. **Tool Contracts** (`contracts/tools/`, `contracts/adapters/`) - YAML files declaring tool input/output requirements
3. **Contract Validator** (`src/core/contract_validator.py`) - Programmatic verification engine

## Directory Structure

```
contracts/
├── README.md                          # This file
├── schemas/
│   └── tool_contract_schema.yaml      # JSON Schema for contract validation
├── tools/
│   ├── T01_PDF_Loader.yaml           # PDF loading tool contract
│   ├── T15A_Text_Chunker.yaml        # Text chunking tool contract
│   └── ...                           # Additional tool contracts
└── adapters/
    ├── Phase1ToPhase2Adapter.yaml    # Phase adapter contract
    └── ...                           # Additional adapter contracts
```

## Contract Format

Each contract is a YAML file following this structure:

```yaml
tool_id: T01_PDF_LOADER
description: Loads PDF files and extracts raw text content
category: Ingestion
version: 1.0.0

input_contract:
  required_data_types: []  # Data types tool requires
  required_state: {}       # Workflow states tool requires
  parameters:              # Configuration parameters
    required:
      file_path: string
    optional:
      use_ocr: boolean

output_contract:
  produced_data_types:     # Data types tool produces
    - type: Document
      attributes: [content, original_filename, ...]
  produced_state:          # Workflow states tool sets
    document_loaded: true

error_codes:               # Structured error definitions
  - code: FILE_NOT_FOUND
    description: The specified file path does not exist
    severity: error
```

## Data Types

The system defines standardized data types in `src/core/data_models.py`:

- **BaseObject** - Foundation class with identity, quality, and provenance
- **Document** - Source documents (Phase 1 output)
- **Chunk** - Text chunks (Phase 1 processing)
- **Mention** - Entity mentions in text (Phase 2)
- **Entity** - Canonical entities (Phase 2/3)
- **Relationship** - Entity relationships (Phase 2/3)
- **Graph** - Knowledge graphs (Phase 3)
- **Table** - Structured data (Phase 3+)
- **WorkflowState** - Execution state tracking

All data types inherit from `BaseObject` and include:
- Unique ID and object type
- Confidence score and quality tier
- Provenance (created_by, created_at, workflow_id)
- Version tracking
- Reference linking capability

## Usage

### Validating Contracts

```bash
# Validate all contracts
python scripts/validate_contracts.py

# Validate with verbose output
python scripts/validate_contracts.py --verbose

# Generate compatibility matrix
python scripts/validate_contracts.py --generate-matrix

# Save detailed report
python scripts/validate_contracts.py --output validation_report.json
```

### Programmatic Validation

```python
from src.core.contract_validator import ContractValidator

# Initialize validator
validator = ContractValidator("contracts")

# Load and validate a contract
contract = validator.load_contract("T01_PDF_LOADER")

# Validate tool implementation
errors = validator.validate_tool_interface(tool_instance, contract)

# Test data flow
success, errors, output = validator.validate_data_flow(
    tool_instance, contract, test_input
)
```

### Integration Testing

```python
from src.core.contract_validator import ContractTestFramework

# Create test framework
test_framework = ContractTestFramework(validator)

# Run comprehensive tests
results = test_framework.run_contract_tests(tool_instance, "T01_PDF_LOADER")

# Create test data
test_doc = test_framework.create_test_data("Document", content="Test content")
```

## Creating New Contracts

1. **Copy template** from existing contract
2. **Update tool_id** to match your tool (e.g., "T42_NEW_TOOL")
3. **Define input requirements**:
   - Required data types and their attributes
   - Required workflow states
   - Configuration parameters
4. **Define output guarantees**:
   - Produced data types and attributes
   - Workflow states set on completion
5. **Document error codes** with descriptions and severity
6. **Add performance requirements** and dependencies
7. **Validate** using `python scripts/validate_contracts.py`

## Contract Validation Rules

### Schema Validation
- Tool ID must match pattern `^[A-Z0-9_]+$`
- Description must be at least 10 characters
- Category must be from allowed enum
- All required fields must be present

### Data Type Validation
- Input/output types must be from defined data models
- Required attributes must exist on data objects
- Minimum/maximum counts must be respected
- Quality impact must be specified

### State Validation
- State names must match pattern `^[a-zA-Z_][a-zA-Z0-9_]*$`
- Required states must be boolean
- State dependencies must be logical

### Error Code Validation
- Error codes must match pattern `^[A-Z_]+$`
- Descriptions must be meaningful
- Severity must be: error, warning, or info

## CI/CD Integration

Add to your CI pipeline:

```yaml
# GitHub Actions example
- name: Validate Tool Contracts
  run: |
    python scripts/validate_contracts.py --fail-on-invalid
    
# Generate compatibility report
- name: Generate Compatibility Matrix
  run: |
    python scripts/validate_contracts.py --generate-matrix --output compatibility_report.json
```

## Benefits

### De-risking
- **Catch integration issues early** through automated validation
- **Prevent API breaking changes** with contract enforcement
- **Ensure data compatibility** across tool boundaries
- **Validate tool chains** before deployment

### Scalability
- **Standardized interfaces** enable independent tool development
- **Automated testing** reduces manual validation overhead
- **Clear contracts** improve developer onboarding
- **Modular architecture** supports the 121-tool vision

### Quality Assurance
- **Consistent data formats** across all tools
- **Provenance tracking** for audit trails
- **Quality metrics** built into all data objects
- **Error handling** standardized across tools

## Troubleshooting

### Common Issues

1. **Contract not found**
   - Check file naming: `{TOOL_ID}.yaml`
   - Verify it's in correct directory (`tools/` or `adapters/`)

2. **Schema validation failed**
   - Check YAML syntax
   - Verify all required fields are present
   - Ensure enum values are correct

3. **Data type validation failed**
   - Confirm data type names match data_models.py
   - Check required attributes are specified
   - Verify object structure matches Pydantic models

4. **Tool interface validation failed**
   - Ensure tool has `execute` method
   - Check method signature accepts required parameters
   - Verify tool produces expected output format

### Getting Help

1. Run with `--verbose` flag for detailed error messages
2. Check the contract schema: `contracts/schemas/tool_contract_schema.yaml`
3. Review example contracts in `contracts/tools/`
4. Run integration tests: `python tests/integration/test_contract_validation.py`

## Future Enhancements

- **Automatic contract generation** from tool implementations
- **Visual compatibility matrix** showing tool connections
- **Performance benchmarking** integrated with contracts
- **Version compatibility** tracking across tool updates
- **Dynamic contract discovery** for plugin architectures