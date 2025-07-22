# Automated Schema Validation Tools

## Overview

This document describes the automated tools and processes for ensuring schema compliance across all 121 KGAS tools. These tools enforce data consistency, catch compatibility issues early, and maintain the integrity of our cross-modal data architecture.

## Core Validation Tools

### 1. Schema Registry CLI

```bash
# Install the KGAS schema tools
pip install kgas-schema-tools

# Basic usage
kgas-schema validate <file>
kgas-schema check-compatibility <tool_id>
kgas-schema generate-model <schema_name>
kgas-schema migrate <from_version> <to_version>
```

### 2. Pydantic Model Generator

```python
# scripts/generate_pydantic_models.py
"""
Automatically generate Pydantic models from JSON schemas
"""

import json
from pathlib import Path
from typing import Dict, Any
from datamodel_code_generator import generate

def generate_models_from_schemas():
    """Generate Python models from all schema definitions"""
    schema_dir = Path("docs/architecture/data/-schemas")
    output_dir = Path("src/models/generated")
    
    for schema_file in schema_dir.glob("*.json"):
        with open(schema_file) as f:
            schema = json.load(f)
        
        # Generate Pydantic model
        model_code = generate(
            schema,
            input_file_type="jsonschema",
            output_model_type="pydantic.BaseModel",
            field_constraints=True,
            use_default=True,
            reuse_model=True,
            enum_field_as_literal="all"
        )
        
        # Write to file
        output_file = output_dir / f"{schema_file.stem}_model.py"
        output_file.write_text(model_code)
        
        print(f"Generated {output_file}")

if __name__ == "__main__":
    generate_models_from_schemas()
```

### 3. Runtime Validation Middleware

```python
# src/core/validation/schema_validator.py
"""
Runtime schema validation for all tool inputs/outputs
"""

from typing import Dict, Any, Type
from pydantic import BaseModel, ValidationError
from functools import wraps
import logging

logger = logging.getLogger(__name__)

class SchemaValidator:
    """Central schema validation service"""
    
    def __init__(self, registry: 'SchemaRegistry'):
        self.registry = registry
        self._cache = {}
    
    def validate_input(self, tool_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate tool input against registered schema"""
        schema = self._get_schema(tool_id, "input")
        try:
            validated = schema(**data)
            return validated.dict()
        except ValidationError as e:
            logger.error(f"Input validation failed for {tool_id}: {e}")
            raise ValueError(f"Invalid input for {tool_id}: {e.errors()}")
    
    def validate_output(self, tool_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate tool output against registered schema"""
        schema = self._get_schema(tool_id, "output")
        try:
            validated = schema(**data)
            return validated.dict()
        except ValidationError as e:
            logger.error(f"Output validation failed for {tool_id}: {e}")
            raise ValueError(f"Invalid output from {tool_id}: {e.errors()}")
    
    def _get_schema(self, tool_id: str, schema_type: str) -> Type[BaseModel]:
        """Get cached schema or load from registry"""
        cache_key = f"{tool_id}:{schema_type}"
        if cache_key not in self._cache:
            self._cache[cache_key] = self.registry.get_schema(tool_id, schema_type)
        return self._cache[cache_key]

def validate_schema(input_schema=None, output_schema=None):
    """Decorator for automatic schema validation"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Validate input
            if input_schema and len(args) > 1:
                validator = SchemaValidator.get_instance()
                validated_input = validator.validate_against_schema(
                    args[1], input_schema
                )
                args = (args[0], validated_input) + args[2:]
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Validate output
            if output_schema:
                validator = SchemaValidator.get_instance()
                result = validator.validate_against_schema(
                    result, output_schema
                )
            
            return result
        return wrapper
    return decorator
```

### 4. Contract Testing Framework

```python
# src/testing/contract_test_generator.py
"""
Generate contract tests from tool specifications
"""

import pytest
from typing import Dict, Any, List
from pathlib import Path

class ContractTestGenerator:
    """Generate contract tests for tools"""
    
    def generate_contract_tests(self, tool_spec: Dict[str, Any]) -> str:
        """Generate pytest contract tests from tool specification"""
        tool_id = tool_spec['tool_id']
        
        test_code = f'''
import pytest
from src.tools.{tool_id} import {tool_id.title()}Tool
from src.testing.contract_validator import ContractValidator

class TestContract_{tool_id.title()}:
    """Auto-generated contract tests for {tool_id}"""
    
    def setup_method(self):
        self.tool = {tool_id.title()}Tool()
        self.validator = ContractValidator()
    
    def test_input_contract(self):
        """Test tool accepts valid inputs per contract"""
        valid_inputs = {self._generate_valid_inputs(tool_spec)}
        
        result = self.tool.process(valid_inputs)
        assert result is not None
        assert self.validator.validate_output_contract(result, "{tool_id}")
    
    def test_invalid_input_rejection(self):
        """Test tool rejects invalid inputs"""
        invalid_inputs = {self._generate_invalid_inputs(tool_spec)}
        
        with pytest.raises(ValidationError):
            self.tool.process(invalid_inputs)
    
    def test_output_contract_compliance(self):
        """Test tool output matches contract"""
        valid_inputs = {self._generate_valid_inputs(tool_spec)}
        
        result = self.tool.process(valid_inputs)
        
        # Verify all required fields present
        assert all(field in result for field in {tool_spec['output']['required']})
        
        # Verify types match contract
        for field, expected_type in {tool_spec['output']['properties']}.items():
            if field in result:
                assert isinstance(result[field], expected_type)
    
    def test_state_transitions(self):
        """Test workflow state transitions match contract"""
        initial_state = {tool_spec['required_state']}
        valid_inputs = {self._generate_valid_inputs(tool_spec)}
        
        result = self.tool.process(valid_inputs, workflow_state=initial_state)
        
        # Verify produced state
        for state_key, state_value in {tool_spec['produced_state']}.items():
            assert result['workflow_state'][state_key] == state_value
'''
        return test_code
    
    def _generate_valid_inputs(self, spec: Dict) -> Dict[str, Any]:
        """Generate valid test inputs from specification"""
        # Implementation generates valid test data based on schema
        pass
    
    def _generate_invalid_inputs(self, spec: Dict) -> List[Dict[str, Any]]:
        """Generate invalid test inputs for boundary testing"""
        # Implementation generates invalid test cases
        pass
```

### 5. CI/CD Integration

```yaml
# .github/workflows/schema-validation.yml
name: Schema Validation

on:
  push:
    paths:
      - 'src/**/*.py'
      - 'docs/architecture/data/-schemas/**'
      - 'docs/architecture/specifications/compatibility-matrix.md'
  pull_request:

jobs:
  validate-schemas:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -e .
          pip install kgas-schema-tools
      
      - name: Validate JSON schemas
        run: |
          python scripts/validate_all_schemas.py
      
      - name: Check schema consistency
        run: |
          kgas-schema check-consistency \
            --matrix docs/architecture/specifications/compatibility-matrix.md \
            --schemas docs/architecture/data/-schemas/
      
      - name: Generate Pydantic models
        run: |
          python scripts/generate_pydantic_models.py
      
      - name: Run contract tests
        run: |
          pytest tests/contracts/ -v
      
      - name: Check breaking changes
        if: github.event_name == 'pull_request'
        run: |
          kgas-schema check-breaking-changes \
            --base origin/main \
            --head HEAD
```

### 6. Schema Evolution Validator

```python
# scripts/validate_schema_evolution.py
"""
Ensure schema changes maintain backward compatibility
"""

import json
from typing import Dict, Any, List, Tuple
from deepdiff import DeepDiff

class SchemaEvolutionValidator:
    """Validate schema changes for compatibility"""
    
    def check_backward_compatibility(
        self, 
        old_schema: Dict[str, Any], 
        new_schema: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """Check if new schema is backward compatible"""
        issues = []
        
        # Check removed required fields
        old_required = set(old_schema.get('required', []))
        new_required = set(new_schema.get('required', []))
        removed_required = old_required - new_required
        
        if removed_required:
            issues.append(f"Removed required fields: {removed_required}")
        
        # Check type changes
        old_props = old_schema.get('properties', {})
        new_props = new_schema.get('properties', {})
        
        for field, old_type in old_props.items():
            if field in new_props:
                new_type = new_props[field]
                if not self._types_compatible(old_type, new_type):
                    issues.append(
                        f"Incompatible type change for '{field}': "
                        f"{old_type['type']} -> {new_type['type']}"
                    )
        
        # Check removed fields
        removed_fields = set(old_props.keys()) - set(new_props.keys())
        if removed_fields:
            issues.append(f"Removed fields: {removed_fields}")
        
        return len(issues) == 0, issues
    
    def generate_migration(
        self, 
        old_schema: Dict[str, Any], 
        new_schema: Dict[str, Any]
    ) -> str:
        """Generate migration code for schema changes"""
        diff = DeepDiff(old_schema, new_schema)
        
        migration_code = f'''
def migrate_v{old_schema.get("version", "1.0.0")}_to_v{new_schema.get("version", "2.0.0")}(data: Dict[str, Any]) -> Dict[str, Any]:
    """Auto-generated migration function"""
    migrated = data.copy()
    
'''
        
        # Add field migrations
        for change_type, changes in diff.items():
            if change_type == 'dictionary_item_added':
                for path in changes:
                    field = self._extract_field_name(path)
                    default = self._get_default_value(new_schema, field)
                    migration_code += f'    migrated["{field}"] = {default}\n'
            
            elif change_type == 'dictionary_item_removed':
                for path in changes:
                    field = self._extract_field_name(path)
                    migration_code += f'    migrated.pop("{field}", None)\n'
        
        migration_code += '\n    return migrated\n'
        return migration_code
```

### 7. Real-time Validation Dashboard

```python
# src/monitoring/schema_validation_metrics.py
"""
Real-time metrics for schema validation
"""

from prometheus_client import Counter, Histogram, Gauge
import time

# Metrics
validation_success = Counter(
    'schema_validation_success_total',
    'Total successful schema validations',
    ['tool_id', 'schema_type']
)

validation_failure = Counter(
    'schema_validation_failure_total',
    'Total failed schema validations',
    ['tool_id', 'schema_type', 'error_type']
)

validation_duration = Histogram(
    'schema_validation_duration_seconds',
    'Time spent validating schemas',
    ['tool_id', 'schema_type']
)

schema_version_gauge = Gauge(
    'schema_version_info',
    'Current schema versions in use',
    ['schema_name', 'version']
)

class ValidationMetricsCollector:
    """Collect and report validation metrics"""
    
    def record_validation(self, tool_id: str, schema_type: str, success: bool, duration: float, error_type: str = None):
        """Record validation metrics"""
        if success:
            validation_success.labels(tool_id=tool_id, schema_type=schema_type).inc()
        else:
            validation_failure.labels(
                tool_id=tool_id, 
                schema_type=schema_type,
                error_type=error_type or "unknown"
            ).inc()
        
        validation_duration.labels(
            tool_id=tool_id,
            schema_type=schema_type
        ).observe(duration)
    
    def update_schema_version(self, schema_name: str, version: str):
        """Update current schema version metric"""
        schema_version_gauge.labels(
            schema_name=schema_name,
            version=version
        ).set(1)
```

## Command-Line Tools

### Schema Validation CLI

```bash
# Validate a single file
kgas-schema validate data.json --schema entity.schema.json

# Validate all tool outputs in a directory
kgas-schema validate-dir output/ --recursive

# Check tool compatibility
kgas-schema check-tool T23a --matrix compatibility-matrix.md

# Generate contract tests
kgas-schema generate-tests --tool T31 --output tests/contracts/

# Run compatibility check between versions
kgas-schema diff v1.0.0 v2.0.0 --check-breaking

# Generate migration script
kgas-schema generate-migration entity.v1.json entity.v2.json
```

### Integration with IDEs

```json
// .vscode/settings.json
{
  "json.schemas": [
    {
      "fileMatch": ["**/entity_*.json"],
      "url": "./docs/architecture/data/-schemas/entity.schema.json"
    },
    {
      "fileMatch": ["**/mention_*.json"],
      "url": "./docs/architecture/data/-schemas/mention.schema.json"
    }
  ],
  "python.linting.mypyArgs": [
    "--strict",
    "--plugins", "pydantic.mypy"
  ]
}
```

## Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: validate-schemas
        name: Validate JSON schemas
        entry: kgas-schema validate-all
        language: system
        files: '\.(json|yaml)$'
        
      - id: check-contracts
        name: Check tool contracts
        entry: python scripts/check_tool_contracts.py
        language: system
        files: '^src/tools/.*\.py$'
        
      - id: pydantic-models
        name: Generate Pydantic models
        entry: python scripts/generate_pydantic_models.py
        language: system
        files: '^docs/architecture/data/-schemas/.*\.json$'
```

## Validation Reports

### Daily Validation Report
```
Schema Validation Report - 2025-07-22
====================================

Total Validations: 15,234
Success Rate: 99.87%
Average Validation Time: 2.3ms

Failures by Type:
- Missing Required Field: 12 (0.08%)
- Type Mismatch: 6 (0.04%)
- Invalid Reference: 2 (0.01%)

Top Failing Tools:
1. T23a_SpacyNER: 8 failures (confidence field)
2. T31_EntityBuilder: 4 failures (mcl_mapping)
3. T115_GraphToTable: 2 failures (conversion_metadata)

Schema Version Status:
- Up to date: 117 tools (96.7%)
- Needs update: 4 tools (3.3%)

Recommendations:
1. Update T23a to include confidence in all outputs
2. Ensure MCL mappings are complete for T31
3. Review schema migration for T115
```

## Best Practices

1. **Always validate at boundaries**: Input validation, output validation, storage validation
2. **Use strong typing**: Leverage Pydantic's type system fully
3. **Version everything**: Track schema versions in data and code
4. **Test migrations**: Always test schema migrations with real data
5. **Monitor in production**: Track validation metrics and failures
6. **Document changes**: Update compatibility matrix with schema changes
7. **Automate updates**: Use code generation to keep models in sync

This comprehensive schema validation tooling ensures data consistency and compatibility across all KGAS components.