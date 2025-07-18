#!/usr/bin/env python3
"""
Create Combined Architecture Document for External Review

This script combines all relevant architecture documents into a single
comprehensive document suitable for external review.
"""

import os
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple

class ArchitectureCombiner:
    def __init__(self, docs_root: str = "docs/architecture"):
        self.docs_root = Path(docs_root)
        self.output_file = "KGAS-Combined-Architecture-External-Review.md"
        
        # Define the order and importance of documents
        self.document_order = [
            # Core Documents (Essential)
            {
                "path": "ARCHITECTURE.md",
                "title": "KGAS Architecture: Theory-Aware GraphRAG System",
                "description": "Main comprehensive architecture document",
                "priority": "essential"
            },
            {
                "path": "architecture-master.md", 
                "title": "KGAS Architecture Master Document",
                "description": "High-level overview and navigation",
                "priority": "essential"
            },
            {
                "path": "concepts/kgas-evergreen-documentation.md",
                "title": "KGAS Evergreen Documentation",
                "description": "Core theoretical principles",
                "priority": "essential"
            },
            {
                "path": "concepts/theoretical-framework.md",
                "title": "Theoretical Framework",
                "description": "Academic underpinnings for LLM-generated ontologies",
                "priority": "essential"
            },
            {
                "path": "concepts/master-concept-library.md",
                "title": "Master Concept Library",
                "description": "Central vocabulary for knowledge graph operations",
                "priority": "essential"
            },
            {
                "path": "data/MODELS.md",
                "title": "Data Models",
                "description": "Pydantic data model specifications",
                "priority": "essential"
            },
            {
                "path": "data/theory-meta-schema.md",
                "title": "Theory Meta-Schema",
                "description": "Theory integration framework",
                "priority": "essential"
            },
            {
                "path": "concepts/design-patterns.md",
                "title": "Design Patterns",
                "description": "Key software design patterns used in the codebase",
                "priority": "essential"
            },
            {
                "path": "systems/contract-system.md",
                "title": "Contract System",
                "description": "Tool and adapter contract system architecture",
                "priority": "essential"
            },
            {
                "path": "specifications/capability-registry.md",
                "title": "Capability Registry",
                "description": "Central registry of all tools and capabilities",
                "priority": "essential"
            },
            {
                "path": "adrs/ADR-001-Phase-Interface-Design.md",
                "title": "ADR-001: Phase Interface Design",
                "description": "Architecture decision record for phase interfaces",
                "priority": "essential"
            },
            {
                "path": "adrs/ADR-002-Pipeline-Orchestrator-Architecture.md",
                "title": "ADR-002: Pipeline Orchestrator Architecture",
                "description": "Architecture decision record for pipeline orchestration",
                "priority": "essential"
            },
            # Optional Documents (For Comprehensive Review)
            {
                "path": "data/database-integration.md",
                "title": "Database Integration",
                "description": "Database connection and interaction details",
                "priority": "optional"
            },
            {
                "path": "specifications/consistency-framework.md",
                "title": "Consistency Framework",
                "description": "Framework for data and process consistency",
                "priority": "optional"
            },
            {
                "path": "specifications/compatibility-matrix.md",
                "title": "Compatibility Matrix",
                "description": "Component integration requirements and compatibility",
                "priority": "optional"
            },
            {
                "path": "LIMITATIONS.md",
                "title": "System Limitations",
                "description": "Known limitations and boundaries of the system",
                "priority": "optional"
            },
            {
                "path": "project-structure.md",
                "title": "Project Structure",
                "description": "Repository layout and organization",
                "priority": "optional"
            }
        ]
        
    def clean_content(self, content: str, filename: str) -> str:
        """Clean and format content for inclusion"""
        # Remove YAML frontmatter
        content = re.sub(r'^---\n.*?\n---\n', '', content, flags=re.DOTALL)
        
        # Remove navigation sections that reference other docs
        content = re.sub(r'## 📚 Navigation.*?(?=\n##|\n$)', '', content, flags=re.DOTALL)
        
        # Remove "Related Documents" sections
        content = re.sub(r'## 📚 Related Documents.*?(?=\n##|\n$)', '', content, flags=re.DOTALL)
        
        # Remove file paths that might confuse external reviewers
        content = re.sub(r'`docs/architecture/', '`', content)
        content = re.sub(r'`\./docs/architecture/', '`', content)
        
        # Clean up any remaining internal references
        content = re.sub(r'\[.*?\]\(\./.*?\)', '', content)
        
        return content.strip()
    
    def get_file_size(self, file_path: Path) -> int:
        """Get file size in bytes"""
        try:
            return file_path.stat().st_size
        except FileNotFoundError:
            return 0
    
    def read_document(self, doc_info: Dict) -> Tuple[bool, str]:
        """Read and process a document"""
        file_path = self.docs_root / doc_info["path"]
        
        if not file_path.exists():
            return False, f"File not found: {doc_info['path']}"
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check file size (skip very large files)
            file_size = len(content)
            if file_size > 50000:  # 50KB limit
                return False, f"File too large ({file_size} bytes): {doc_info['path']}"
            
            cleaned_content = self.clean_content(content, doc_info["path"])
            return True, cleaned_content
            
        except Exception as e:
            return False, f"Error reading {doc_info['path']}: {str(e)}"
    
    def create_combined_document(self, include_optional: bool = True) -> str:
        """Create the combined architecture document"""
        combined_content = []
        
        # Header
        combined_content.append(f"""# KGAS Combined Architecture Document
**For External Review**

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Purpose**: Comprehensive architecture documentation for external review
**Total Documents**: {len([d for d in self.document_order if include_optional or d['priority'] == 'essential'])}

---

## 📋 Document Overview

This combined document contains the essential architecture documentation for the Knowledge Graph Analysis System (KGAS), a theory-aware GraphRAG platform that integrates social science theories into knowledge graph construction and analysis.

### Document Structure

The following documents are included in this combined architecture review:

""")
        
        # Add document overview
        for i, doc_info in enumerate(self.document_order, 1):
            if include_optional or doc_info['priority'] == 'essential':
                combined_content.append(f"{i}. **{doc_info['title']}** - {doc_info['description']}")
        
        combined_content.append("\n---\n")
        
        # Process each document
        included_count = 0
        skipped_count = 0
        
        for doc_info in self.document_order:
            if not include_optional and doc_info['priority'] == 'optional':
                continue
                
            print(f"Processing: {doc_info['path']}")
            
            success, content = self.read_document(doc_info)
            
            if success:
                combined_content.append(f"# {doc_info['title']}\n")
                combined_content.append(f"*{doc_info['description']}*\n")
                combined_content.append(content)
                combined_content.append("\n---\n")
                included_count += 1
            else:
                print(f"⚠️  Skipped: {content}")
                skipped_count += 1
        
        # Footer
        combined_content.append(f"""
## 📊 Summary

**Documents Included**: {included_count}
**Documents Skipped**: {skipped_count}
**Total Size**: {len(''.join(combined_content)):,} characters

---

*This document was automatically generated for external architecture review. For the most up-to-date information, please refer to the individual source documents in the KGAS repository.*
""")
        
        return '\n'.join(combined_content)
    
    def save_combined_document(self, content: str) -> None:
        """Save the combined document"""
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Combined architecture document saved: {self.output_file}")
        print(f"📊 Document size: {len(content):,} characters ({len(content)/1024:.1f} KB)")

def main():
    """Main function"""
    combiner = ArchitectureCombiner()
    
    print("🔧 Creating combined architecture document for external review...")
    print("📁 Scanning architecture documents...")
    
    # Create essential-only version
    print("\n📋 Creating essential documents version...")
    essential_content = combiner.create_combined_document(include_optional=False)
    combiner.save_combined_document(essential_content)
    
    # Create comprehensive version
    print("\n📋 Creating comprehensive version (including optional documents)...")
    comprehensive_content = combiner.create_combined_document(include_optional=True)
    
    # Save comprehensive version with different name
    comprehensive_file = "KGAS-Combined-Architecture-Comprehensive-External-Review.md"
    with open(comprehensive_file, 'w', encoding='utf-8') as f:
        f.write(comprehensive_content)
    
    print(f"✅ Comprehensive architecture document saved: {comprehensive_file}")
    print(f"📊 Comprehensive document size: {len(comprehensive_content):,} characters ({len(comprehensive_content)/1024:.1f} KB)")
    
    print("\n🎯 Recommendation:")
    print("- Use the essential version for initial review")
    print("- Use the comprehensive version for detailed technical review")

if __name__ == "__main__":
    main() 