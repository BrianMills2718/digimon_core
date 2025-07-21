# Contracts Module - CLAUDE.md

## Overview
The `contracts/` directory contains the contract system that ensures consistency and validation across all tools, phases, and theory implementations in KGAS. This is a critical architectural component that enforces interface compliance and data integrity.

## Directory Structure

### Core Components
- **`schemas/`**: JSON schemas for tool contracts and validation
- **`tools/`**: Individual tool contract YAML files (T01, T15A, T23A, etc.)
- **`validation/`**: Contract validation logic and theory validators
- **`theory_schemas/`**: Theory meta-schema contracts and instances
- **`phase_interfaces/`**: Phase interface definitions and registry
- **`adapters/`**: Phase transition adapters and compatibility layers

## Key Concepts

### Tool Contracts
Every tool in KGAS must have a corresponding YAML contract that defines:
- Input/output specifications
- Error handling requirements
- Quality metrics and confidence scoring
- Integration points with core services
- Theory compliance (if applicable)

### Contract Validation
All contracts are validated against JSON schemas to ensure:
- Structural consistency across tools
- Required fields are present
- Data types are correct
- Theory meta-schema compliance

### Theory Integration
The contract system integrates with the theory meta-schema to enable:
- Theory-aware tool contracts
- Ontology validation
- Academic compliance (TORC standards)

## Common Commands

### Validate All Contracts
```bash
# Validate all tool contracts
python contracts/validation/theory_validator.py

# Validate specific contract
python -m contracts.validation.theory_validator contracts/tools/T01_PDF_LOADER.yaml
```

### Create New Tool Contract
```bash
# Use existing contract as template
cp contracts/tools/T01_PDF_LOADER.yaml contracts/tools/T_NEW_TOOL.yaml
# Edit the new contract file
# Validate the contract
python contracts/validation/theory_validator.py contracts/tools/T_NEW_TOOL.yaml
```

### Check Contract Compliance
```bash
# Check if all tools have contracts
find src/tools -name "*.py" | grep -E "t[0-9]+" | while read tool; do
    tool_id=$(basename "$tool" .py | tr '[:lower:]' '[:upper:]')
    if [ ! -f "contracts/tools/${tool_id}.yaml" ]; then
        echo "Missing contract: $tool_id"
    fi
done
```

## Contract File Format

### Tool Contract Template
```yaml
# contracts/tools/TOOL_NAME.yaml
tool_id: "TOOL_ID"
tool_name: "Human Readable Name"
description: "What this tool does"
input_schema:
  type: object
  properties:
    # Define input parameters
output_schema:
  type: object
  properties:
    # Define output format
error_handling:
  # Error scenarios and responses
quality_metrics:
  # Confidence scoring and quality assessment
integration:
  # How this tool integrates with core services
theory_compliance:
  # Theory meta-schema alignment (if applicable)
```

### Theory Schema Template
```yaml
# contracts/theory_schemas/theory_name.yaml
theory_id: "theory_identifier"
theory_name: "Theory Name"
domain_of_application: "Domain description"
ontology_specification:
  # Domain-specific entities and relationships
analytics:
  # Theory-specific metrics
process:
  # Analytical workflow
```

## Integration Points

### Core Services Integration
- **IdentityService**: Entity resolution contracts
- **QualityService**: Confidence scoring contracts
- **PiiService**: PII handling contracts
- **ProvenanceService**: Execution tracking contracts

### Tool Development Workflow
1. **Design Tool**: Define inputs, outputs, behavior
2. **Create Contract**: Write YAML contract following schema
3. **Validate Contract**: Run validation against JSON schema
4. **Implement Tool**: Code tool to match contract specification
5. **Test Compliance**: Verify tool behavior matches contract

### Phase Interface Contracts
- **Phase Adapters**: Define how phases transition and share data
- **Phase Registry**: Central registry of available phases
- **Interface Validation**: Ensure phase compatibility

## Common Patterns

### Error Handling Contracts
```yaml
error_handling:
  validation_errors:
    - code: "INVALID_INPUT"
      message: "Input validation failed"
      recovery: "Check input format and retry"
  processing_errors:
    - code: "PROCESSING_FAILED"
      message: "Processing encountered error"
      recovery: "Review error logs and data quality"
```

### Quality Metrics Contracts
```yaml
quality_metrics:
  confidence_scoring:
    type: "float"
    range: [0.0, 1.0]
    description: "Tool confidence in results"
  quality_tier:
    type: "string"
    values: ["HIGH", "MEDIUM", "LOW"]
    description: "Result quality assessment"
```

### Theory Compliance Contracts
```yaml
theory_compliance:
  meta_schema_version: "v9.1"
  ontology_alignment: "MANUAL" # or "AUTOMATIC"
  theory_reference: "theory_id"
  extraction_strategy: "LLM_GUIDED" # or "PATTERN_BASED"
```

## Development Guidelines

### Contract Creation
- Start with existing contract as template
- Focus on clear input/output specifications
- Include comprehensive error handling
- Define quality metrics appropriately
- Add theory compliance if tool is theory-aware

### Validation Best Practices
- Run validation after every contract change
- Use continuous integration to validate contracts
- Keep JSON schemas updated with contract changes
- Test contract compliance in tool implementation

### Theory Integration
- Align with theory meta-schema when applicable
- Use consistent ontology_alignment strategies
- Reference specific theory instances
- Include theory-specific analytics when relevant

## Troubleshooting

### Common Issues
1. **Schema Validation Errors**: Check contract syntax against JSON schema
2. **Missing Required Fields**: Ensure all required contract fields are present
3. **Type Mismatches**: Verify data types match schema expectations
4. **Reference Errors**: Check theory_reference points to valid theory

### Debug Commands
```bash
# Validate contract syntax
python -c "import yaml; yaml.safe_load(open('contracts/tools/TOOL.yaml'))"

# Check schema compliance
python contracts/validation/theory_validator.py --verbose contracts/tools/TOOL.yaml

# List all contracts
find contracts/tools -name "*.yaml" | sort

# Check for contract coverage
python -c "
import os
tools = [f for f in os.listdir('src/tools/phase1') if f.startswith('t') and f.endswith('.py')]
contracts = [f for f in os.listdir('contracts/tools') if f.endswith('.yaml')]
print('Tools without contracts:')
for tool in tools:
    contract_name = tool.replace('.py', '.yaml').upper()
    if contract_name not in contracts:
        print(f'  {tool} -> {contract_name}')
"
```

## Performance Considerations

### Contract Loading
- Contracts are loaded at tool registration time
- Use caching for frequently accessed contracts
- Validate contracts at build time, not runtime
- Keep contract files concise but complete

### Validation Performance
- Schema validation is fast for small contracts
- Batch validate multiple contracts when possible
- Use contract validation in CI/CD pipeline
- Cache validation results when appropriate

## Integration with Development Workflow

### Pre-commit Hooks
Consider adding contract validation to pre-commit hooks:
```bash
# .git/hooks/pre-commit
#!/bin/bash
python contracts/validation/theory_validator.py contracts/tools/*.yaml
```

### CI/CD Integration
Include contract validation in continuous integration:
```yaml
# .github/workflows/validate-contracts.yml
- name: Validate Contracts
  run: python contracts/validation/theory_validator.py contracts/tools/*.yaml
```

The contracts system is fundamental to maintaining consistency and quality across the entire KGAS system. All tool development should start with contract definition and validation.