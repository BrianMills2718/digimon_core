#!/usr/bin/env python3
"""
Script to split the comprehensive KGAS architecture document into logical sections
"""

from pathlib import Path
import re

def split_comprehensive_doc():
    """Split the comprehensive document into 4 logical sections"""
    
    input_file = Path("KGAS_COMPREHENSIVE_ARCHITECTURE.md")
    
    if not input_file.exists():
        print(f"❌ Input file not found: {input_file}")
        return
    
    # Read the comprehensive document
    content = input_file.read_text(encoding='utf-8')
    
    # Define the 4 logical sections based on content analysis
    sections = {
        "01_Core_Architecture_and_Vision": {
            "title": "KGAS Core Architecture and System Vision",
            "description": "Fundamental architecture, principles, and system overview",
            "files": [
                "ARCHITECTURE_OVERVIEW.md",
                "GLOSSARY.md", 
                "project-structure.md",
                "CLAUDE.md"
            ]
        },
        
        "02_Theoretical_Framework_and_Data": {
            "title": "KGAS Theoretical Framework and Data Architecture", 
            "description": "Theory integration, meta-schemas, concepts, and data structures",
            "files": [
                "kgas-theoretical-foundation.md",
                "theory-meta-schema-v10.md",
                "theory-meta-schema.md",
                "theory_meta_schema_v10.json",
                "master-concept-library.md",
                "bi-store-justification.md",
                "DATABASE_SCHEMAS.md"
            ]
        },
        
        "03_Analysis_and_Integration_Architecture": {
            "title": "KGAS Analysis Architecture and Integration Systems",
            "description": "Cross-modal analysis, interfaces, components, and MCP integration", 
            "files": [
                "cross-modal-analysis.md",
                "agent-interface.md", 
                "COMPONENT_ARCHITECTURE_DETAILED.md",
                "SPECIFICATIONS.md",
                "mcp-integration-architecture.md"
            ]
        },
        
        "04_Architecture_Decisions_and_Extensions": {
            "title": "KGAS Architecture Decisions and Advanced Capabilities",
            "description": "ADRs, ABM integration, statistical analysis, and system limitations",
            "files": [
                "ADR-001-Phase-Interface-Design.md",
                "ADR-002-Pipeline-Orchestrator-Architecture.md", 
                "ADR-003-Vector-Store-Consolidation.md",
                "ADR-009-Bi-Store-Database-Strategy.md",
                "ADR-020-Agent-Based-Modeling-Integration.md",
                "ADR-021-Statistical-Analysis-Integration.md",
                "LIMITATIONS.md"
            ]
        }
    }
    
    # Split content by section markers
    section_pattern = r"## (\d+)\. ([^\n]+)\n\n\*\*Source\*\*: `([^`]+)`"
    matches = list(re.finditer(section_pattern, content))
    
    if not matches:
        print("❌ Could not find section markers in the document")
        return
    
    print(f"📄 Found {len(matches)} sections in the comprehensive document")
    
    # Create section content mapping
    section_contents = {}
    for i, match in enumerate(matches):
        section_num = int(match.group(1))
        section_title = match.group(2)
        source_path = match.group(3)
        
        # Extract content between this section and the next
        start_pos = match.end()
        if i + 1 < len(matches):
            end_pos = matches[i + 1].start()
            section_content = content[start_pos:end_pos]
        else:
            section_content = content[start_pos:]
        
        # Clean up content (remove separator lines)
        section_content = re.sub(r"\n={80}\n", "\n\n", section_content)
        section_content = section_content.strip()
        
        # Get filename from source path
        filename = Path(source_path).name
        section_contents[filename] = {
            'title': section_title,
            'content': section_content,
            'source': source_path
        }
    
    # Generate the 4 logical documents
    for section_key, section_info in sections.items():
        output_file = Path(f"KGAS_{section_key}.md")
        
        with open(output_file, 'w', encoding='utf-8') as out_file:
            # Write header
            out_file.write(f"# {section_info['title']}\n\n")
            out_file.write(f"**Description**: {section_info['description']}\n")
            out_file.write(f"**Generated**: Split from comprehensive architecture document\n")
            out_file.write(f"**Files Included**: {len(section_info['files'])}\n\n")
            out_file.write("---\n\n")
            
            # Write table of contents
            out_file.write("## Table of Contents\n\n")
            for i, filename in enumerate(section_info['files'], 1):
                if filename in section_contents:
                    title = section_contents[filename]['title']
                    out_file.write(f"{i}. [{title}](#{i}-{filename.lower().replace('.', '').replace('-', '').replace('_', '')})\n")
                else:
                    out_file.write(f"{i}. {filename} (not found in source)\n")
            out_file.write("\n---\n\n")
            
            # Write content for each file in this section
            files_found = 0
            for i, filename in enumerate(section_info['files'], 1):
                if filename in section_contents:
                    file_info = section_contents[filename]
                    
                    # Write section header
                    anchor = f"{i}-{filename.lower().replace('.', '').replace('-', '').replace('_', '')}"
                    out_file.write(f"## {i}. {file_info['title']} {{#{anchor}}}\n\n")
                    out_file.write(f"**Source**: `{file_info['source']}`\n\n")
                    out_file.write("---\n\n")
                    
                    # Write content
                    out_file.write(file_info['content'])
                    out_file.write("\n\n" + "="*80 + "\n\n")
                    
                    files_found += 1
                else:
                    out_file.write(f"## {i}. {filename} (NOT FOUND)\n\n")
                    out_file.write(f"This file was expected but not found in the source document.\n\n")
                    out_file.write("="*80 + "\n\n")
        
        # Report results
        size_mb = output_file.stat().st_size / (1024 * 1024)
        print(f"✅ Created: {output_file.name}")
        print(f"   📊 Files included: {files_found}/{len(section_info['files'])}")
        print(f"   📏 Size: {size_mb:.2f} MB")
        print()
    
    print("🎯 Successfully split comprehensive document into 4 logical sections!")
    
    # Create index file
    create_index_file(sections)

def create_index_file(sections):
    """Create an index file that references all sections"""
    
    index_file = Path("KGAS_Architecture_Index.md")
    
    with open(index_file, 'w', encoding='utf-8') as out_file:
        out_file.write("# KGAS Architecture Documentation Index\n\n")
        out_file.write("**Purpose**: Navigation guide for KGAS architecture documentation\n")
        out_file.write("**Organization**: 4 logical sections covering all aspects of the system\n\n")
        out_file.write("---\n\n")
        
        out_file.write("## Architecture Documentation Sections\n\n")
        
        for i, (section_key, section_info) in enumerate(sections.items(), 1):
            filename = f"KGAS_{section_key}.md"
            out_file.write(f"### {i}. [{section_info['title']}]({filename})\n\n")
            out_file.write(f"**Description**: {section_info['description']}\n\n")
            out_file.write(f"**Includes {len(section_info['files'])} documents**:\n")
            
            for file in section_info['files']:
                out_file.write(f"- {file}\n")
            out_file.write("\n")
        
        out_file.write("---\n\n")
        out_file.write("## Reading Recommendations\n\n")
        out_file.write("### For New Developers\n")
        out_file.write("1. Start with **Core Architecture and Vision** for system overview\n")
        out_file.write("2. Read **Theoretical Framework** to understand the conceptual foundation\n")
        out_file.write("3. Study **Analysis Architecture** for implementation details\n")
        out_file.write("4. Review **Architecture Decisions** for context and rationale\n\n")
        
        out_file.write("### For Researchers\n")
        out_file.write("1. Begin with **Theoretical Framework** for theory integration approach\n")
        out_file.write("2. Review **Core Architecture** for system capabilities\n")
        out_file.write("3. Examine **Analysis Architecture** for cross-modal analysis\n")
        out_file.write("4. Check **Architecture Decisions** for ABM and statistical integration\n\n")
        
        out_file.write("### For System Integrators\n")
        out_file.write("1. Focus on **Analysis Architecture** for MCP integration details\n")
        out_file.write("2. Study **Core Architecture** for system interfaces\n")
        out_file.write("3. Review **Architecture Decisions** for design rationale\n")
        out_file.write("4. Reference **Theoretical Framework** for data schemas\n\n")
    
    print(f"📋 Created navigation index: {index_file.name}")

if __name__ == "__main__":
    split_comprehensive_doc()