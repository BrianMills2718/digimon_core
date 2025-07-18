#!/usr/bin/env python3
"""
Script to concatenate all evergreen documentation into one comprehensive file.
This creates a single source of truth for examining the complete evergreen documentation.
"""

import os
import glob
from pathlib import Path

def get_file_content(file_path):
    """Read file content with error handling."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"ERROR READING FILE: {e}\n"

def concatenate_evergreen_files():
    """Concatenate all evergreen documentation files."""
    
    # Define the evergreen files in order of importance
    evergreen_files = [
        # Core theoretical foundation
        "docs/current/THEORY_META_SCHEMA.md",
        "docs/current/MASTER_CONCEPT_LIBRARY.md",
        "docs/current/THEORETICAL_FRAMEWORK.md",
        "docs/current/ORM_METHODOLOGY.md",
        
        # Core architecture and design
        "docs/current/ARCHITECTURE.md",
        "docs/current/VISION_ALIGNMENT_PROPOSAL.md",
        "docs/current/CONTRACT_SYSTEM.md",
        
        # Core operational documentation
        "docs/current/QUICK_START.md",
        "docs/current/VERIFICATION_COMMANDS.md",
        "docs/current/UI_README.md",
        
        # Core compliance and standards
        "docs/current/ETHICS.md",
        "docs/current/SECURITY.md",
        "docs/current/REPRODUCIBILITY.md",
        "docs/current/LIMITATIONS.md",
        "docs/current/HARDWARE.md",
        "docs/current/EVALUATION.md",
        "docs/current/OPERATIONS.md",
        "docs/current/CONTRIBUTING.md",
        "docs/current/LICENSES_THIRD_PARTY.md",
        
        # Core ADRs (Architecture Decision Records)
        "docs/current/ADRs/ADR-001-Pipeline-Orchestrator-Architecture.md",
        
        # Core guides
        "docs/guides/USAGE_GUIDE.md",
        "docs/guides/NEO4J_BROWSER_GUIDE.md",
        "docs/guides/EXTRACTION_EXPLAINED.md",
        
        # Core API documentation
        "docs/api/README.md",
        
        # Core project structure
        "docs/PROJECT_STRUCTURE.md",
        "docs/README.md",
    ]
    
    # Create the concatenated content
    concatenated_content = []
    concatenated_content.append("# COMPREHENSIVE EVERGREEN DOCUMENTATION")
    concatenated_content.append("")
    concatenated_content.append("This document combines all evergreen documentation from across the project.")
    concatenated_content.append("Generated programmatically to provide a single source of truth for evergreen documentation examination.")
    concatenated_content.append("")
    concatenated_content.append("**Evergreen Documentation Definition:**")
    concatenated_content.append("- Core theoretical foundations and concepts")
    concatenated_content.append("- Architecture and design principles")
    concatenated_content.append("- Operational procedures and standards")
    concatenated_content.append("- Compliance and regulatory requirements")
    concatenated_content.append("- User guides and reference materials")
    concatenated_content.append("- Project structure and organization")
    concatenated_content.append("")
    concatenated_content.append("---")
    concatenated_content.append("")
    
    # Process each file
    for file_path in evergreen_files:
        if os.path.exists(file_path):
            print(f"Processing: {file_path}")
            
            # Add file header
            concatenated_content.append(f"## {os.path.basename(file_path)}")
            concatenated_content.append(f"**Source:** `{file_path}`")
            concatenated_content.append("")
            
            # Add file content
            content = get_file_content(file_path)
            concatenated_content.append(content)
            
            # Add separator
            concatenated_content.append("")
            concatenated_content.append("---")
            concatenated_content.append("")
        else:
            print(f"WARNING: File not found: {file_path}")
    
    # Write the concatenated file
    output_file = "docs/current/COMPREHENSIVE_EVERGREEN.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(concatenated_content))
    
    print(f"\nConcatenated evergreen documentation written to: {output_file}")
    print(f"Total files processed: {len([f for f in evergreen_files if os.path.exists(f)])}")
    
    return output_file

if __name__ == "__main__":
    concatenate_evergreen_files() 