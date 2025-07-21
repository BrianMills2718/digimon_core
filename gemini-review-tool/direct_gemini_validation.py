#!/usr/bin/env python3
"""
Direct Gemini Validation Script

Validates CLAUDE.md implementation claims by reading files directly
and sending them to Gemini for analysis, bypassing repomix issues.
"""

import os
import yaml
from pathlib import Path

def read_validation_files():
    """Read all files specified in the validation config."""
    
    include_patterns = [
        "docs/architecture/architecture_overview.md",
        "docs/architecture/concurrency-strategy.md", 
        "docs/architecture/agent-interface.md",
        "docs/architecture/llm-ontology-integration.md",
        "docs/architecture/cross-modal-analysis.md",
        "docs/planning/roadmap_overview.md",
        "src/core/tool_registry.py",
        "validate_tool_inventory.py",
        "resolve_tool_conflicts.py"
    ]
    
    file_contents = {}
    
    for pattern in include_patterns:
        file_path = Path(pattern)
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_contents[str(file_path)] = f.read()
                print(f"✅ Read: {file_path}")
            except Exception as e:
                print(f"❌ Error reading {file_path}: {e}")
        else:
            print(f"⚠️  File not found: {file_path}")
    
    return file_contents

def generate_validation_bundle(file_contents):
    """Generate a validation bundle for Gemini analysis."""
    
    # Load the validation config
    with open('gemini-review-tool/validation-20250719-claude-implementation.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    bundle = f"""# CLAUDE.md Implementation Validation Bundle

## Validation Request
{config['custom_prompt']}

## Claims to Validate
{config['claims_of_success']}

## Implementation Files

"""
    
    for file_path, content in file_contents.items():
        bundle += f"""
### File: {file_path}

```
{content}
```

"""
    
    return bundle

def main():
    """Generate validation bundle for manual Gemini review."""
    
    print("📋 CLAUDE.md Implementation Validation")
    print("=" * 50)
    
    # Read all validation files
    file_contents = read_validation_files()
    
    if not file_contents:
        print("❌ No files read successfully")
        return
    
    print(f"\n📊 Summary: Read {len(file_contents)} files")
    
    # Generate validation bundle
    bundle = generate_validation_bundle(file_contents)
    
    # Write bundle to file
    bundle_file = "claude-implementation-validation-bundle.md"
    with open(bundle_file, 'w', encoding='utf-8') as f:
        f.write(bundle)
    
    print(f"✅ Validation bundle written to: {bundle_file}")
    print(f"📄 Bundle size: {len(bundle):,} characters")
    
    print(f"\n🔍 VALIDATION INSTRUCTIONS:")
    print(f"1. Review the generated bundle: {bundle_file}")
    print(f"2. Copy the contents and paste into Gemini for analysis")
    print(f"3. Ask Gemini to validate each claim against the provided implementations")
    print(f"4. Focus on: Implementation completeness, evidence quality, claim accuracy")

if __name__ == "__main__":
    main()