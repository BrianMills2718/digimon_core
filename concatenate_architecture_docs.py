#!/usr/bin/env python3
"""
Script to concatenate KGAS architecture documents in logical reading order
"""

from pathlib import Path

# Define the files in logical reading order (HIGH PRIORITY first)
architecture_files = [
    # HIGH PRIORITY - Essential Foundation
    "docs/architecture/ARCHITECTURE_OVERVIEW.md",
    "docs/architecture/GLOSSARY.md", 
    "docs/architecture/project-structure.md",
    "docs/architecture/CLAUDE.md",
    "docs/architecture/concepts/kgas-theoretical-foundation.md",
    "docs/architecture/cross-modal-analysis.md",
    "docs/architecture/agent-interface.md",
    "docs/architecture/systems/COMPONENT_ARCHITECTURE_DETAILED.md",
    "docs/architecture/data/bi-store-justification.md",
    "docs/architecture/specifications/SPECIFICATIONS.md",
    
    # MEDIUM PRIORITY - Key ADRs
    "docs/architecture/adrs/ADR-001-Phase-Interface-Design.md",
    "docs/architecture/adrs/ADR-002-Pipeline-Orchestrator-Architecture.md",
    "docs/architecture/adrs/ADR-003-Vector-Store-Consolidation.md",
    "docs/architecture/adrs/ADR-009-Bi-Store-Database-Strategy.md",
    "docs/architecture/adrs/ADR-020-Agent-Based-Modeling-Integration.md",
    "docs/architecture/adrs/ADR-021-Statistical-Analysis-Integration.md",
    
    # MEDIUM PRIORITY - Supporting concepts and systems
    "docs/architecture/concepts/master-concept-library.md",
    "docs/architecture/data/theory-meta-schema-v10.md",
    "docs/architecture/data/theory-meta-schema.md", 
    "docs/architecture/data/-schemas/theory_meta_schema_v10.json",
    "docs/architecture/data/DATABASE_SCHEMAS.md",
    "docs/architecture/systems/mcp-integration-architecture.md",
    
    # LOWER PRIORITY - Supporting documentation
    "docs/architecture/LIMITATIONS.md",
]

def concatenate_docs():
    """Concatenate architecture documents into single comprehensive document"""
    
    # Create output file
    output_path = Path("KGAS_COMPREHENSIVE_ARCHITECTURE.md")
    
    with open(output_path, 'w', encoding='utf-8') as out_file:
        # Write header
        out_file.write("# KGAS (Knowledge Graph Analysis System) - Comprehensive Architecture Documentation\n\n")
        out_file.write("**Generated**: Programmatically concatenated from architecture documents\n")
        out_file.write("**Purpose**: Single comprehensive reference for planned KGAS architecture\n")
        out_file.write("**Status**: Target Architecture (intended design)\n\n")
        out_file.write("---\n\n")
        
        # Process each file
        for i, file_path in enumerate(architecture_files, 1):
            file_path_obj = Path(file_path)
            
            # Check if file exists
            if not file_path_obj.exists():
                print(f"WARNING: File not found - {file_path}")
                out_file.write(f"## {i}. {file_path_obj.name} (FILE NOT FOUND)\n\n")
                continue
            
            # Read and write file content
            try:
                content = file_path_obj.read_text(encoding='utf-8')
                
                # Write section header
                out_file.write(f"## {i}. {file_path_obj.name}\n\n")
                out_file.write(f"**Source**: `{file_path}`\n\n")
                out_file.write("---\n\n")
                
                # Write content
                out_file.write(content)
                out_file.write("\n\n" + "="*80 + "\n\n")
                
                print(f"✓ Added: {file_path}")
                
            except Exception as e:
                print(f"ERROR reading {file_path}: {e}")
                out_file.write(f"## {i}. {file_path_obj.name} (ERROR READING FILE)\n\n")
                out_file.write(f"Error: {e}\n\n")
    
    print(f"\n✅ Successfully created comprehensive architecture document: {output_path}")
    print(f"📊 Total files processed: {len(architecture_files)}")
    
    # Show file size
    size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"📏 Output file size: {size_mb:.2f} MB")
    
    return output_path

if __name__ == "__main__":
    output_file = concatenate_docs()
    print(f"\n🎯 Output available at: {output_file.absolute()}")