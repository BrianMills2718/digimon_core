#!/usr/bin/env python3
"""
Script to fix all tool adapters with comprehensive validation
"""

import re
import os

# Read the current tool_adapters.py file
with open('/home/brian/Digimons/src/core/tool_adapters.py', 'r') as f:
    content = f.read()

# Define the adapter validation patterns
adapter_validations = {
    'SpacyNERAdapter': {
        'required_fields': ['chunks'],
        'input_schema_checks': [
            'if not isinstance(input_data, dict):',
            '    errors.append("Input data must be a dictionary")',
            '    return {"valid": False, "errors": errors}',
            '',
            'if "chunks" not in input_data:',
            '    errors.append("Missing required field: chunks")',
            'else:',
            '    chunks = input_data["chunks"]',
            '    if not isinstance(chunks, list):',
            '        errors.append("chunks must be a list")',
            '    elif len(chunks) == 0:',
            '        errors.append("chunks list cannot be empty")',
            '    else:',
            '        for i, chunk in enumerate(chunks):',
            '            if not isinstance(chunk, dict):',
            '                errors.append(f"chunks[{i}] must be a dictionary")',
            '            elif "text" not in chunk:',
            '                errors.append(f"chunks[{i}] missing required field: text")'
        ],
        'security_checks': [
            'if "chunks" in input_data:',
            '    chunks = input_data["chunks"]',
            '    if isinstance(chunks, list):',
            '        for i, chunk in enumerate(chunks):',
            '            if isinstance(chunk, dict) and "text" in chunk:',
            '                text = chunk["text"]',
            '                if isinstance(text, str) and len(text) > 1_000_000:',
            '                    errors.append(f"chunks[{i}].text too large (>1MB)")'
        ],
        'performance_checks': [
            'if "chunks" in input_data:',
            '    chunks = input_data["chunks"]',
            '    if isinstance(chunks, list):',
            '        if len(chunks) > 10000:',
            '            errors.append("Too many chunks (>10000) may cause performance issues")',
            '        elif len(chunks) > 5000:',
            '            warnings.append("Large number of chunks (>5000) may slow processing")'
        ]
    },
    'RelationshipExtractorAdapter': {
        'required_fields': ['entities'],
        'input_schema_checks': [
            'if not isinstance(input_data, dict):',
            '    errors.append("Input data must be a dictionary")',
            '    return {"valid": False, "errors": errors}',
            '',
            'if "entities" not in input_data:',
            '    errors.append("Missing required field: entities")',
            'else:',
            '    entities = input_data["entities"]',
            '    if not isinstance(entities, list):',
            '        errors.append("entities must be a list")',
            '    elif len(entities) == 0:',
            '        errors.append("entities list cannot be empty")'
        ],
        'security_checks': [
            'if "entities" in input_data:',
            '    entities = input_data["entities"]',
            '    if isinstance(entities, list) and len(entities) > 50000:',
            '        errors.append("Too many entities (>50000) may cause DoS")'
        ],
        'performance_checks': [
            'if "entities" in input_data:',
            '    entities = input_data["entities"]',
            '    if isinstance(entities, list):',
            '        if len(entities) > 10000:',
            '            errors.append("Too many entities (>10000) may cause performance issues")',
            '        elif len(entities) > 5000:',
            '            warnings.append("Large number of entities (>5000) may slow processing")'
        ]
    },
    'EntityBuilderAdapter': {
        'required_fields': ['entities'],
        'input_schema_checks': [
            'if not isinstance(input_data, dict):',
            '    errors.append("Input data must be a dictionary")',
            '    return {"valid": False, "errors": errors}',
            '',
            'if "entities" not in input_data:',
            '    errors.append("Missing required field: entities")',
            'else:',
            '    entities = input_data["entities"]',
            '    if not isinstance(entities, list):',
            '        errors.append("entities must be a list")'
        ],
        'security_checks': [
            'if "entities" in input_data:',
            '    entities = input_data["entities"]',
            '    if isinstance(entities, list) and len(entities) > 50000:',
            '        errors.append("Too many entities (>50000) may cause DoS")'
        ],
        'performance_checks': [
            'if "entities" in input_data:',
            '    entities = input_data["entities"]',
            '    if isinstance(entities, list):',
            '        if len(entities) > 10000:',
            '            errors.append("Too many entities (>10000) may cause performance issues")'
        ]
    },
    'EdgeBuilderAdapter': {
        'required_fields': ['relationships'],
        'input_schema_checks': [
            'if not isinstance(input_data, dict):',
            '    errors.append("Input data must be a dictionary")',
            '    return {"valid": False, "errors": errors}',
            '',
            'if "relationships" not in input_data:',
            '    errors.append("Missing required field: relationships")',
            'else:',
            '    relationships = input_data["relationships"]',
            '    if not isinstance(relationships, list):',
            '        errors.append("relationships must be a list")'
        ],
        'security_checks': [
            'if "relationships" in input_data:',
            '    relationships = input_data["relationships"]',
            '    if isinstance(relationships, list) and len(relationships) > 100000:',
            '        errors.append("Too many relationships (>100000) may cause DoS")'
        ],
        'performance_checks': [
            'if "relationships" in input_data:',
            '    relationships = input_data["relationships"]',
            '    if isinstance(relationships, list):',
            '        if len(relationships) > 20000:',
            '            errors.append("Too many relationships (>20000) may cause performance issues")'
        ]
    },
    'PageRankAdapter': {
        'required_fields': ['workflow_id'],
        'input_schema_checks': [
            'if not isinstance(input_data, dict):',
            '    errors.append("Input data must be a dictionary")',
            '    return {"valid": False, "errors": errors}',
            '',
            'if "workflow_id" not in input_data:',
            '    errors.append("Missing required field: workflow_id")',
            'else:',
            '    workflow_id = input_data["workflow_id"]',
            '    if not isinstance(workflow_id, str):',
            '        errors.append("workflow_id must be a string")'
        ],
        'security_checks': [
            'if "workflow_id" in input_data:',
            '    workflow_id = input_data["workflow_id"]',
            '    if isinstance(workflow_id, str) and len(workflow_id) > 1000:',
            '        errors.append("workflow_id too long (>1000 chars)")'
        ],
        'performance_checks': [
            'return {"valid": True, "errors": [], "warnings": []}'
        ]
    },
    'MultiHopQueryAdapter': {
        'required_fields': ['query'],
        'input_schema_checks': [
            'if not isinstance(input_data, dict):',
            '    errors.append("Input data must be a dictionary")',
            '    return {"valid": False, "errors": errors}',
            '',
            'if "query" not in input_data:',
            '    errors.append("Missing required field: query")',
            'else:',
            '    query = input_data["query"]',
            '    if not isinstance(query, str):',
            '        errors.append("query must be a string")'
        ],
        'security_checks': [
            'if "query" in input_data:',
            '    query = input_data["query"]',
            '    if isinstance(query, str):',
            '        if len(query) > 10000:',
            '            errors.append("query too long (>10000 chars)")',
            '        if "DROP" in query.upper() or "DELETE" in query.upper():',
            '            errors.append("query contains dangerous SQL keywords")'
        ],
        'performance_checks': [
            'if "query" in input_data:',
            '    query = input_data["query"]',
            '    if isinstance(query, str) and len(query) > 5000:',
            '        warnings.append("Long query (>5000 chars) may slow processing")'
        ]
    },
    'VectorEmbedderAdapter': {
        'required_fields': ['texts'],
        'input_schema_checks': [
            'if not isinstance(input_data, dict):',
            '    errors.append("Input data must be a dictionary")',
            '    return {"valid": False, "errors": errors}',
            '',
            'if "texts" not in input_data:',
            '    errors.append("Missing required field: texts")',
            'else:',
            '    texts = input_data["texts"]',
            '    if not isinstance(texts, list):',
            '        errors.append("texts must be a list")'
        ],
        'security_checks': [
            'if "texts" in input_data:',
            '    texts = input_data["texts"]',
            '    if isinstance(texts, list):',
            '        for i, text in enumerate(texts):',
            '            if isinstance(text, str) and len(text) > 1_000_000:',
            '                errors.append(f"texts[{i}] too large (>1MB)")'
        ],
        'performance_checks': [
            'if "texts" in input_data:',
            '    texts = input_data["texts"]',
            '    if isinstance(texts, list):',
            '        if len(texts) > 10000:',
            '            errors.append("Too many texts (>10000) may cause performance issues")'
        ]
    }
}

def generate_validation_methods(adapter_name, config):
    """Generate validation methods for an adapter"""
    methods = []
    
    # Schema validation
    methods.append(f"""    def _validate_input_schema(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"Validate input schema for {adapter_name}\"\"\"
        errors = []
        
        {chr(10).join("        " + line for line in config['input_schema_checks'])}
        
        return {{"valid": len(errors) == 0, "errors": errors}}""")
    
    # Security validation
    methods.append(f"""    def _validate_input_security(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"Validate input security for {adapter_name}\"\"\"
        errors = []
        
        {chr(10).join("        " + line for line in config['security_checks'])}
        
        return {{"valid": len(errors) == 0, "errors": errors}}""")
    
    # Performance validation
    methods.append(f"""    def _validate_input_performance(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"Validate input performance for {adapter_name}\"\"\"
        errors = []
        warnings = []
        
        {chr(10).join("        " + line for line in config['performance_checks'])}
        
        return {{"valid": len(errors) == 0, "errors": errors, "warnings": warnings}}""")
    
    # Get required fields
    methods.append(f"""    def _get_required_fields(self) -> List[str]:
        \"\"\"Get required fields for {adapter_name}\"\"\"
        return {config['required_fields']}""")
    
    return "\n\n".join(methods)

# Find and replace validation methods for each adapter
for adapter_name, config in adapter_validations.items():
    # Find the current validate_input method
    pattern = rf'(class {adapter_name}.*?)\n(.*?)def validate_input\(self, input_data: Dict\[str, Any\]\) -> ToolValidationResult:\s*\n(.*?)(?=\n\n    def|\nclass|\Z)'
    
    match = re.search(pattern, content, re.DOTALL)
    if match:
        class_def = match.group(1)
        before_validate = match.group(2)
        
        # Generate new validation method
        new_validate_method = f"""    def validate_input(self, input_data: Dict[str, Any]) -> ToolValidationResult:
        \"\"\"Validate {adapter_name} input with comprehensive validation\"\"\"
        return self.validate_input_comprehensive(input_data)"""
        
        # Generate validation helper methods
        validation_methods = generate_validation_methods(adapter_name, config)
        
        # Replace the old method with new methods
        replacement = f"""{class_def}
{before_validate}{new_validate_method}
    
{validation_methods}"""
        
        content = content[:match.start()] + replacement + content[match.end():]
        print(f"Fixed {adapter_name}")
    else:
        print(f"Could not find {adapter_name} validate_input method")

# Write the updated content
with open('/home/brian/Digimons/src/core/tool_adapters.py', 'w') as f:
    f.write(content)

print("All adapters have been updated with comprehensive validation")