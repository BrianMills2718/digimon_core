#!/usr/bin/env python3
"""
Direct validation script for Phase 2.1 implementation claims
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from gemini_review import send_to_gemini

def run_phase2_validation():
    """Run direct validation of Phase 2.1 implementation claims"""
    
    # Read the manually created XML bundle
    xml_file = "validation-manual.xml"
    if not os.path.exists(xml_file):
        print(f"❌ Error: {xml_file} not found")
        return
    
    with open(xml_file, 'r', encoding='utf-8') as f:
        xml_content = f.read()
    
    # Custom validation prompt
    prompt = """
VALIDATION OBJECTIVE: Verify implementation claims for Phase 2.1 Graph Analytics Tools (T50 Community Detection and T51 Centrality Analysis)

VALIDATION CRITERIA FOR EACH CLAIM:
1. **Implementation Present**: Does the method/feature exist where claimed?
2. **Functionality Complete**: Is it fully implemented (not stub/placeholder)?
3. **Requirements Met**: Does it satisfy the specific requirements mentioned?

For each claim below, provide a verdict of FULLY RESOLVED, PARTIALLY RESOLVED, or NOT RESOLVED with specific line number references.

CLAIMS TO VALIDATE:

T50 Community Detection:
- T50 Community Detection implements real Louvain algorithm using NetworkX
- T50 supports multiple community detection algorithms: Louvain, Leiden, Label Propagation, Greedy Modularity, Fluid Communities
- T50 calculates modularity scores and comprehensive community statistics
- T50 loads graph data from multiple sources: Neo4j, NetworkX, edge lists, adjacency matrices
- T50 provides academic-quality confidence scoring based on modularity and algorithm reliability
- T50 achieves 71% test coverage through real functionality testing (22 tests passing)

T51 Centrality Analysis:
- T51 Centrality Analysis implements 12 real centrality metrics including degree, betweenness, closeness, eigenvector, PageRank
- T51 includes advanced metrics: Katz, harmonic, load, information, current flow betweenness/closeness, subgraph centrality
- T51 calculates correlation matrix between different centrality metrics using numpy
- T51 provides PageRank fallback implementations for scipy compatibility issues
- T51 supports comprehensive graph statistics calculation including connectivity and path length analysis
- T51 achieves 65% test coverage through real functionality testing (22 tests passing)

General Claims:
- Both tools follow BaseTool interface with standardized ToolRequest/ToolResult patterns
- Both tools implement academic-quality output formatting with publication-ready statistics
- Both tools include comprehensive error handling with specific error codes and fallback mechanisms

FOCUS AREAS:
- Real algorithm implementations (no mocking in core functionality)
- Academic-quality statistical analysis and confidence scoring
- Comprehensive test coverage with real graph data
- BaseTool interface compliance and standardized patterns
- Error handling and fallback mechanisms for compatibility

Please examine the actual implementation code provided and give specific verdicts with line number evidence.
"""
    
    try:
        print("🤖 Sending validation to Gemini...")
        response = send_to_gemini(xml_content, prompt)
        
        # Save results
        output_file = f"phase2_validation_results_{len(xml_content)//1000}k.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# Phase 2.1 Implementation Validation Results\n\n")
            f.write(f"Generated: {os.popen('date').read().strip()}\n\n")
            f.write(f"Files analyzed: 4 files (T50, T51 implementation + tests)\n")
            f.write(f"Content size: {len(xml_content):,} characters\n\n")
            f.write("---\n\n")
            f.write(response)
        
        print(f"✅ Validation complete! Results saved to: {output_file}")
        print(f"📊 Content analyzed: {len(xml_content):,} characters")
        
        return response
        
    except Exception as e:
        print(f"❌ Error during validation: {e}")
        return None

if __name__ == "__main__":
    run_phase2_validation()