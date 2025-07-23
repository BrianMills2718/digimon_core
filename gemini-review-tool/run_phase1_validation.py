#!/usr/bin/env python3
"""
Run focused Gemini validation for Phase 1 tool completion claims
"""

import os
import sys
import google.generativeai as genai
from pathlib import Path

def run_validation():
    """Run Phase 1 implementation validation"""
    
    # Check API key
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY environment variable not set")
        return
    
    # Configure Gemini
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    # Read validation context
    context_file = Path("gemini-review-tool/phase1-validation.xml")
    if not context_file.exists():
        print(f"❌ Validation context file not found: {context_file}")
        return
    
    with open(context_file, 'r') as f:
        context = f.read()
    
    # Create focused validation prompt
    prompt = """
VALIDATION OBJECTIVE: Verify specific Phase 1 tool implementation claims for KGAS project completion.

I need you to validate these SPECIFIC CLAIMS about the implementation:

CLAIM 1: "T34 Edge Builder has comprehensive mock-free test suite"
- File: tests/unit/test_t34_edge_builder_unified.py
- Expected: Test class with 15+ test methods, explicit "NO mocks" statements, real ServiceManager usage

CLAIM 2: "T68 PageRank Calculator implements real NetworkX PageRank algorithm"
- File: src/tools/phase1/t68_pagerank_calculator_unified.py
- Expected: NetworkX PageRank integration, Neo4j graph loading, unified BaseTool interface

CLAIM 3: "T68 PageRank Calculator has comprehensive test coverage"
- File: tests/unit/test_t68_pagerank_calculator_unified.py
- Expected: 20+ test methods covering PageRank calculation, graph metrics, mock-free testing

CLAIM 4: "T49 Multi-hop Query implements real Neo4j multi-hop traversal"
- File: src/tools/phase1/t49_multihop_query_unified.py
- Expected: Neo4j multi-hop path finding, entity extraction, PageRank-weighted ranking

CLAIM 5: "T49 Multi-hop Query has comprehensive test coverage"
- File: tests/unit/test_t49_multihop_query_unified.py
- Expected: 25+ test methods covering query processing, path finding, mock-free testing

CLAIM 6: "All tools implement unified BaseTool interface"
- Files: T68 and T49 implementation files
- Expected: Inheritance from BaseTool, execute() method, get_contract() method, proper tool_id

FOR EACH CLAIM:
1. State whether FULLY RESOLVED, PARTIALLY RESOLVED, or NOT RESOLVED
2. Provide specific evidence (line numbers, method names, implementation details)
3. Explain what makes the implementation complete or incomplete

Focus ONLY on these specific files and claims. Do not analyze other aspects of the codebase.

CONTEXT:
""" + context
    
    print("🚀 Starting Phase 1 Implementation Validation...")
    print(f"📄 Context size: {len(context)} chars (~{len(context)//4} tokens)")
    print("🔍 Validating 6 specific implementation claims...")
    
    try:
        # Send to Gemini
        response = model.generate_content(prompt)
        
        # Write results
        output_file = Path("gemini-review-tool/phase1-validation-results.md")
        with open(output_file, 'w') as f:
            f.write("# Phase 1 Implementation Validation Results\n\n")
            f.write(f"**Date**: {os.popen('date').read().strip()}\n")
            f.write(f"**Model**: gemini-2.0-flash-exp\n")
            f.write(f"**Context**: 6 files, ~{len(context)//4} tokens\n\n")
            f.write("## Validation Results\n\n")
            f.write(response.text)
        
        print(f"✅ Validation completed! Results saved to: {output_file}")
        print("\n" + "="*60)
        print("VALIDATION RESULTS SUMMARY:")
        print("="*60)
        print(response.text[:1000] + "..." if len(response.text) > 1000 else response.text)
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")

if __name__ == "__main__":
    run_validation()