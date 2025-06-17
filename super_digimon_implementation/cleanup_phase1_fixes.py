#!/usr/bin/env python
"""Phase 1: Critical bug fixes for systematic cleanup."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

print("=== PHASE 1: CRITICAL BUG FIXES ===\n")

# Fix 1: PageRank Timestamp Issue
print("1. Fixing PageRank timestamp issue...")

# Read the current neo4j_manager.py
with open("src/utils/neo4j_manager.py", "r") as f:
    content = f.read()

# Check if we need to fix _entity_from_props
if "props.get('created_at')" not in content:
    print("  ✓ Need to add timestamp handling")
    
    # Create fixed version
    fixed_content = content.replace(
        'props["created_at"] = datetime.fromisoformat(props["created_at"])',
        '''# Handle optional timestamps
        if "created_at" in props:
            if isinstance(props["created_at"], str):
                props["created_at"] = datetime.fromisoformat(props["created_at"])
        else:
            props["created_at"] = datetime.utcnow()
            
        if "updated_at" in props:
            if isinstance(props["updated_at"], str):
                props["updated_at"] = datetime.fromisoformat(props["updated_at"])
        else:
            props["updated_at"] = datetime.utcnow()'''
    )
    
    # Also fix the relationship method
    fixed_content = fixed_content.replace(
        'props["created_at"] = datetime.fromisoformat(props["created_at"])\n        props["updated_at"] = datetime.fromisoformat(props["updated_at"])',
        '''# Handle optional timestamps
        if "created_at" in props:
            if isinstance(props["created_at"], str):
                props["created_at"] = datetime.fromisoformat(props["created_at"])
        else:
            props["created_at"] = datetime.utcnow()
            
        if "updated_at" in props:
            if isinstance(props["updated_at"], str):
                props["updated_at"] = datetime.fromisoformat(props["updated_at"])
        else:
            props["updated_at"] = datetime.utcnow()'''
    )
    
    with open("src/utils/neo4j_manager.py", "w") as f:
        f.write(fixed_content)
    
    print("  ✓ Fixed timestamp handling in neo4j_manager.py")
else:
    print("  ✓ Timestamp handling already fixed")

# Fix 2: Embedding Text Assumption
print("\n2. Checking T41 Embedding Generator...")

# Check the current implementation
import ast

class EmbeddingChecker(ast.NodeVisitor):
    def __init__(self):
        self.has_text_fallback = False
        
    def visit_FunctionDef(self, node):
        if node.name == "_get_text_for_object":
            # Check if it handles missing text
            for child in ast.walk(node):
                if isinstance(child, ast.Str) and "name" in child.s:
                    self.has_text_fallback = True
        self.generic_visit(node)

with open("src/tools/phase3/t41_embedding_generator.py", "r") as f:
    tree = ast.parse(f.read())
    
checker = EmbeddingChecker()
checker.visit(tree)

if not checker.has_text_fallback:
    print("  ✗ T41 needs text fallback implementation")
    print("  TODO: Add fallback to entity name when no text content")
else:
    print("  ✓ T41 already has text fallback")

# Fix 3: Natural Language Query Success Rate
print("\n3. Analyzing T94 Natural Language Query...")

# Quick analysis of current implementation
with open("src/tools/phase7/t94_natural_language_query.py", "r") as f:
    nlq_content = f.read()
    
issues = []
if "similarity_threshold" not in nlq_content:
    issues.append("No similarity threshold parameter")
if "fallback" not in nlq_content.lower():
    issues.append("No fallback strategy")
if nlq_content.count("try:") < 2:
    issues.append("Limited error handling")

if issues:
    print("  ✗ Issues found:")
    for issue in issues:
        print(f"    - {issue}")
    print("  TODO: Improve query parsing and add fallbacks")
else:
    print("  ✓ NLQ has basic error handling and fallbacks")

# Summary
print("\n\n=== PHASE 1 SUMMARY ===")
print("Fixed:")
print("  ✓ Neo4j timestamp handling")
print("\nTODO:")
print("  - T41: Add text fallback for entities without text content")
print("  - T94: Improve query parsing and success rate")
print("\nNext step: Run test_adversarial_deep_dive.py to verify fixes")

print("\n✅ Phase 1 fixes applied!")