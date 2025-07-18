#!/usr/bin/env python3
"""
Script to concatenate all roadmap documentation into one comprehensive file.
This creates a single source of truth for examining the full roadmap vision.
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

def concatenate_roadmap_files():
    """Concatenate all roadmap-related documentation files."""
    
    # Define the roadmap files in order of importance
    roadmap_files = [
        # Main roadmap files
        "docs/current/ROADMAP_v2.md",
        "docs/current/COMPATIBILITY_MATRIX.md",
        "docs/planned/PLANNED_FEATURES.md",
        
        # Phase-specific documentation
        "docs/PHASE2_ACADEMIC_COMPLIANCE.md",
        "docs/phase3/HORIZONTAL_FIRST_STRATEGY.md",
        "docs/phase3/MULTI_DOCUMENT_ARCHITECTURE.md",
        
        # Planning and strategy documents
        "docs/planning/2025.06172110_planning_needs_to_be_integrated.md",
        "docs/current/PAGERANK_OPTIMIZATION_PLAN.md",
        "docs/current/IDENTITY_SERVICE_MIGRATION_PLAN.md",
        
        # Status and progress tracking
        "docs/current/STATUS.md",
        "docs/current/CONSOLIDATION_PROGRESS.md",
        "docs/current/PHASE2_API_STATUS_UPDATE.md",
        
        # Implementation and technical details
        "docs/current/API_STANDARDIZATION_FRAMEWORK.md",
        "docs/current/REORGANIZATION_PLAN.md",
        "docs/current/TOOL_ROADMAP_RECONCILIATION.md",
        
        # Analysis and audit documents
        "docs/current/CURRENT_REALITY_AUDIT.md",
        "docs/current/TECHNICAL_DEBT_AUDIT.md",
        "docs/current/IMPLEMENTATION_DIVERGENCE_ANALYSIS.md",
        "docs/current/PERFORMANCE_CLAIMS_VERIFICATION.md",
        
        # Integration and testing
        "docs/current/INTEGRATION_TESTING_GAP_ANALYSIS.md",
        "docs/current/ERROR_HANDLING_BEST_PRACTICES.md",
        "docs/current/CONSISTENCY_FRAMEWORK.md",
        
        # Capability and tool documentation
        "docs/current/CAPABILITY_REGISTRY.md",
        "docs/current/TOOL_IMPLEMENTATION_STATUS.md",
        "docs/current/CAPABILITY_AUDIT_FINAL_RESULTS.md",
        
        # Verification and evidence
        "docs/current/VERIFICATION.md",
        "docs/current/FINAL_SYSTEM_VERIFICATION_REPORT.md",
        "docs/current/MCP_TOOLS_HONEST_EVIDENCE_REPORT.md",
        
        # Future planning
        "docs/current/future_possible_performance_optimizations.md",
        "docs/current/NEXT_STEPS.md",
    ]
    
    # Create the concatenated content
    concatenated_content = []
    concatenated_content.append("# COMPREHENSIVE ROADMAP DOCUMENTATION")
    concatenated_content.append("")
    concatenated_content.append("This document combines all roadmap-related documentation from across the project.")
    concatenated_content.append("Generated programmatically to provide a single source of truth for roadmap examination.")
    concatenated_content.append("")
    concatenated_content.append("---")
    concatenated_content.append("")
    
    # Process each file
    for file_path in roadmap_files:
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
    output_file = "docs/current/COMPREHENSIVE_ROADMAP.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(concatenated_content))
    
    print(f"\nConcatenated roadmap written to: {output_file}")
    print(f"Total files processed: {len([f for f in roadmap_files if os.path.exists(f)])}")
    
    return output_file

if __name__ == "__main__":
    concatenate_roadmap_files() 