#!/usr/bin/env python3

"""
Documentation Drift Checker
Checks for broken links and schema version inconsistencies
"""

import os
import re
import sys
from pathlib import Path

def check_schema_version_consistency():
    """Check that all schema references use v9"""
    print("🔍 Checking schema version consistency...")
    
    docs_dir = Path("docs/current")
    schema_pattern = re.compile(r'compatability_code/contracts/schemas/')
    v9_pattern = re.compile(r'_schemas/theory_meta_schema_v9\.json')
    
    issues = []
    
    for md_file in docs_dir.rglob("*.md"):
        content = md_file.read_text()
        
        # Check for old schema paths
        if schema_pattern.search(content):
            issues.append(f"❌ {md_file}: Uses old schema path")
        
        # Check for v9 references
        if not v9_pattern.search(content) and "schema" in content.lower():
            issues.append(f"⚠️  {md_file}: May need v9 schema reference")
    
    if issues:
        print("\n".join(issues))
        return False
    
    print("✅ Schema version consistency verified")
    return True

def check_cross_references():
    """Check that all docs have roadmap cross-references"""
    print("🔍 Checking cross-references...")
    
    docs_dir = Path("docs/current")
    roadmap_ref = "ROADMAP_v2.1.md"
    
    issues = []
    
    for md_file in docs_dir.rglob("*.md"):
        if md_file.name in ["TABLE_OF_CONTENTS.md", "ROADMAP_v2.1.md"]:
            continue
            
        content = md_file.read_text()
        
        if roadmap_ref not in content:
            issues.append(f"❌ {md_file}: Missing roadmap cross-reference")
    
    if issues:
        print("\n".join(issues))
        return False
    
    print("✅ Cross-references verified")
    return True

def check_v2_1_integration():
    """Check that v2.1 changes are properly integrated"""
    print("🔍 Checking v2.1 integration...")
    
    issues = []
    
    # Check for Service Compatibility Layer
    try:
        with open("docs/current/ARCHITECTURE.md") as f:
            content = f.read()
            if "Service Compatibility Layer" not in content:
                issues.append("❌ ARCHITECTURE.md: Missing Service Compatibility Layer")
    except FileNotFoundError:
        issues.append("❌ ARCHITECTURE.md: File not found")
    
    # Check for Contract Validator
    try:
        with open("docs/current/CONTRACT_SYSTEM.md") as f:
            content = f.read()
            if "Contract Validator" not in content:
                issues.append("❌ CONTRACT_SYSTEM.md: Missing Contract Validator")
    except FileNotFoundError:
        issues.append("❌ CONTRACT_SYSTEM.md: File not found")
    
    # Check for ontology_alignment_strategy
    try:
        with open("docs/current/THEORY_META_SCHEMA.md") as f:
            content = f.read()
            if "ontology_alignment_strategy" not in content:
                issues.append("❌ THEORY_META_SCHEMA.md: Missing ontology_alignment_strategy")
    except FileNotFoundError:
        issues.append("❌ THEORY_META_SCHEMA.md: File not found")
    
    if issues:
        print("\n".join(issues))
        return False
    
    print("✅ v2.1 integration verified")
    return True

def main():
    """Main drift check function"""
    print("🔍 Running documentation drift check...")
    
    success = True
    
    if not check_schema_version_consistency():
        success = False
    
    if not check_cross_references():
        success = False
    
    if not check_v2_1_integration():
        success = False
    
    if success:
        print("✅ All documentation checks passed")
        sys.exit(0)
    else:
        print("❌ Documentation drift detected")
        sys.exit(1)

if __name__ == "__main__":
    main() 