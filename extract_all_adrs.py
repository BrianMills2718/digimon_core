#!/usr/bin/env python3
"""
Script to extract all ADRs (Architecture Decision Records) into a single document
"""

from pathlib import Path
import re

def extract_all_adrs():
    """Extract all ADR files and compile into comprehensive ADR document"""
    
    # Find all ADR files
    adrs_dir = Path("docs/architecture/adrs")
    
    if not adrs_dir.exists():
        print(f"❌ ADRs directory not found: {adrs_dir}")
        return
    
    # Get all ADR files (including ADR-021 which might not be in the original list)
    adr_files = list(adrs_dir.glob("ADR-*.md"))
    adr_files.sort(key=lambda x: int(re.search(r'ADR-(\d+)', x.name).group(1)))
    
    print(f"📋 Found {len(adr_files)} ADR files:")
    for adr_file in adr_files:
        print(f"   - {adr_file.name}")
    
    # Create comprehensive ADR document
    output_file = Path("KGAS_All_Architecture_Decision_Records.md")
    
    with open(output_file, 'w', encoding='utf-8') as out_file:
        # Write header
        out_file.write("# KGAS Architecture Decision Records (ADRs)\n\n")
        out_file.write("**Purpose**: Complete collection of all Architecture Decision Records for KGAS\n")
        out_file.write("**Generated**: Programmatically extracted from architecture/adrs/ directory\n")
        out_file.write(f"**Total ADRs**: {len(adr_files)}\n\n")
        out_file.write("---\n\n")
        
        # Create table of contents
        out_file.write("## Table of Contents\n\n")
        for i, adr_file in enumerate(adr_files, 1):
            adr_number = re.search(r'ADR-(\d+)', adr_file.name).group(1)
            adr_title = adr_file.name.replace(f"ADR-{adr_number}-", "").replace(".md", "").replace("-", " ").title()
            anchor = f"adr-{adr_number}"
            out_file.write(f"{i}. [ADR-{adr_number}: {adr_title}](#{anchor})\n")
        
        out_file.write("\n---\n\n")
        
        # Process each ADR file
        for i, adr_file in enumerate(adr_files, 1):
            try:
                # Extract ADR number for anchor
                adr_number = re.search(r'ADR-(\d+)', adr_file.name).group(1)
                anchor = f"adr-{adr_number}"
                
                # Read ADR content
                content = adr_file.read_text(encoding='utf-8')
                
                # Write section header with anchor
                out_file.write(f"## ADR-{adr_number} {{#{anchor}}}\n\n")
                out_file.write(f"**Source File**: `{adr_file.relative_to(Path('.'))}`\n\n")
                out_file.write("---\n\n")
                
                # Write content
                out_file.write(content)
                
                # Add separator between ADRs
                out_file.write("\n\n" + "="*100 + "\n\n")
                
                print(f"✅ Added: {adr_file.name}")
                
            except Exception as e:
                print(f"❌ Error processing {adr_file.name}: {e}")
                out_file.write(f"## ADR-{adr_number} (ERROR)\n\n")
                out_file.write(f"**Error reading file**: {e}\n\n")
                out_file.write("="*100 + "\n\n")
        
        # Add footer
        out_file.write("---\n\n")
        out_file.write("## ADR Summary\n\n")
        out_file.write(f"This document contains {len(adr_files)} Architecture Decision Records that document the key architectural decisions made during KGAS development.\n\n")
        out_file.write("### Key Decision Areas Covered:\n\n")
        out_file.write("- **Tool Architecture**: Contract-first design, tool interfaces, and orchestration\n")
        out_file.write("- **Data Architecture**: Database strategies, vector storage, and data consistency\n")
        out_file.write("- **Analysis Architecture**: Cross-modal analysis, uncertainty metrics, quality systems\n")
        out_file.write("- **Integration Architecture**: MCP protocol, agent-based modeling, statistical analysis\n")
        out_file.write("- **Research Architecture**: Academic focus, buy vs build decisions, research workflows\n\n")
        out_file.write("Each ADR documents the context, decision, rationale, and consequences of major architectural choices.\n")
    
    # Show results
    size_mb = output_file.stat().st_size / (1024 * 1024)
    print(f"\n✅ Successfully created comprehensive ADR document: {output_file}")
    print(f"📊 Total ADRs processed: {len(adr_files)}")
    print(f"📏 Output file size: {size_mb:.2f} MB")
    
    # Create ADR index for quick reference
    create_adr_index(adr_files, output_file)
    
    return output_file

def create_adr_index(adr_files, main_file):
    """Create a quick reference index of ADRs"""
    
    index_file = Path("KGAS_ADR_Index.md")
    
    with open(index_file, 'w', encoding='utf-8') as out_file:
        out_file.write("# KGAS ADR Quick Reference Index\n\n")
        out_file.write("**Purpose**: Quick reference guide to all Architecture Decision Records\n")
        out_file.write(f"**Complete Document**: [{main_file.name}]({main_file.name})\n\n")
        out_file.write("---\n\n")
        
        # Group ADRs by category
        categories = {
            "Tool & Interface Architecture": [],
            "Data & Storage Architecture": [],
            "Analysis & Processing Architecture": [],
            "Integration & Protocol Architecture": [],
            "Research & Quality Architecture": []
        }
        
        # Categorize ADRs based on their content/title
        for adr_file in adr_files:
            adr_number = re.search(r'ADR-(\d+)', adr_file.name).group(1)
            adr_title = adr_file.name.replace(f"ADR-{adr_number}-", "").replace(".md", "").replace("-", " ").title()
            adr_entry = f"**ADR-{adr_number}**: {adr_title}"
            
            # Simple categorization based on keywords in title
            title_lower = adr_title.lower()
            if any(keyword in title_lower for keyword in ['interface', 'tool', 'contract', 'phase']):
                categories["Tool & Interface Architecture"].append(adr_entry)
            elif any(keyword in title_lower for keyword in ['database', 'store', 'vector', 'bi-store']):
                categories["Data & Storage Architecture"].append(adr_entry)
            elif any(keyword in title_lower for keyword in ['analysis', 'uncertainty', 'quality', 'cross-modal', 'statistical']):
                categories["Analysis & Processing Architecture"].append(adr_entry)
            elif any(keyword in title_lower for keyword in ['mcp', 'protocol', 'integration', 'modeling']):
                categories["Integration & Protocol Architecture"].append(adr_entry)
            else:
                categories["Research & Quality Architecture"].append(adr_entry)
        
        # Write categorized index
        for category, adrs in categories.items():
            if adrs:  # Only show categories that have ADRs
                out_file.write(f"## {category}\n\n")
                for adr in adrs:
                    out_file.write(f"- {adr}\n")
                out_file.write("\n")
        
        out_file.write("---\n\n")
        out_file.write("## Decision Impact Map\n\n")
        out_file.write("### Foundation Decisions (Impact: System-Wide)\n")
        out_file.write("- ADR-001: Tool Interface Design (affects all tools)\n")
        out_file.write("- ADR-003: Vector Store Strategy (affects data architecture)\n")
        out_file.write("- ADR-009: Bi-Store Database Strategy (affects all data operations)\n\n")
        
        out_file.write("### Core Architecture Decisions (Impact: Major Components)\n")
        out_file.write("- ADR-008: Core Service Architecture\n")
        out_file.write("- ADR-010: Quality System Design\n")
        out_file.write("- ADR-015: Cross-Modal Orchestration\n\n")
        
        out_file.write("### Enhancement Decisions (Impact: Specific Capabilities)\n")
        out_file.write("- ADR-013: MCP Protocol Integration\n")
        out_file.write("- ADR-020: Agent-Based Modeling Integration\n")
        out_file.write("- ADR-021: Statistical Analysis Integration\n\n")
        
        out_file.write("### Research & Quality Decisions (Impact: Research Workflows)\n")
        out_file.write("- ADR-011: Academic Research Focus\n")
        out_file.write("- ADR-016: Bayesian Uncertainty Aggregation\n")
        out_file.write("- ADR-017: IC Analytical Techniques Integration\n")
        out_file.write("- ADR-018: Analysis Version Control\n")
        out_file.write("- ADR-019: Research Assistant Personas\n")
    
    print(f"📋 Created ADR index: {index_file.name}")

if __name__ == "__main__":
    extract_all_adrs()