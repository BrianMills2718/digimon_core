#!/usr/bin/env python3
"""
Direct T57 validation script using Google Gemini API
"""

import os
import google.generativeai as genai
from pathlib import Path

def validate_t57_implementation():
    """Run direct validation of T57 implementation with Gemini"""
    
    # Configure Gemini API
    api_key = os.getenv('GOOGLE_AI_API_KEY')
    if not api_key:
        print("❌ Error: GOOGLE_AI_API_KEY environment variable not set")
        return
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # Read repomix file
    repomix_file = Path("repomix-t57.xml")
    if not repomix_file.exists():
        print("❌ Error: repomix-t57.xml not found")
        return
    
    print(f"📄 Reading {repomix_file} ({repomix_file.stat().st_size} bytes)")
    
    with open(repomix_file, 'r', encoding='utf-8') as f:
        code_content = f.read()
    
    validation_prompt = """
You are validating specific implementation claims for the T57 Path Analysis Tool. 

For each claim, verify:
1. Implementation Present: Does the method/feature exist where claimed?
2. Functionality Complete: Is it fully implemented (not stub/placeholder)?  
3. Requirements Met: Does it satisfy the specific requirements mentioned?

Focus ONLY on the T57 tool implementation and its comprehensive test suite.

CLAIMS TO VALIDATE:

1. "T57 Path Analysis Tool implements advanced shortest path algorithms including Dijkstra, BFS, Bellman-Ford with real NetworkX integration"
   - Verify _compute_dijkstra_paths, _compute_bfs_paths, _compute_bellman_ford_paths methods exist and use real NetworkX algorithms

2. "T57 implements comprehensive all-pairs shortest path analysis with proper NetworkX API handling"
   - Verify _analyze_all_pairs_paths method exists and correctly handles nx.all_pairs_dijkstra vs nx.all_pairs_shortest_path API differences

3. "T57 implements flow analysis with maximum flow and minimum cut algorithms using real NetworkX flow functions" 
   - Verify _analyze_flows method exists and correctly uses nx.maximum_flow and nx.minimum_cut with proper capacity attribute handling

4. "T57 implements reachability analysis for connectivity metrics with component analysis"
   - Verify _analyze_reachability method exists and calculates reachability matrix, connectivity ratio, and component analysis

5. "T57 has comprehensive test suite with 28 tests, 80% coverage, zero mocking approach"
   - Verify test file exists with ~28 test methods, uses real NetworkX graphs, no mock objects, comprehensive test scenarios

6. "T57 follows unified BaseTool interface with proper contract definition, health check, and validation methods"
   - Verify PathAnalysisTool class inherits from BaseTool, implements get_contract, health_check, validate_input methods

7. "T57 provides academic-ready output with statistical significance calculation and publication-ready formatting"
   - Verify _calculate_academic_confidence method exists and result metadata includes academic_ready, publication_ready flags

For each claim, provide verdict:
- ✅ FULLY RESOLVED - Implementation present, complete, meets requirements
- ⚠️ PARTIALLY RESOLVED - Implementation present but incomplete or doesn't fully meet requirements  
- ❌ NOT RESOLVED - Implementation missing or doesn't address the claimed issue

Provide specific line references and code examples to support your assessment.
"""
    
    print("🤖 Sending validation request to Gemini...")
    
    try:
        response = model.generate_content(
            f"{validation_prompt}\n\nCODE TO VALIDATE:\n{code_content}",
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,
                max_output_tokens=4000
            )
        )
        
        print("📊 GEMINI VALIDATION RESULTS:")
        print("=" * 60)
        print(response.text)
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error during validation: {str(e)}")

if __name__ == "__main__":
    validate_t57_implementation()