#!/usr/bin/env python3
"""
Direct T57 validation using existing repomix output
"""

import os
import sys
import json
from pathlib import Path

# Add the gemini-review-tool to path to use its modules
sys.path.append(str(Path(__file__).parent))

try:
    import google.generativeai as genai
    from gemini_review_config import ReviewConfig
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please install required packages: pip install google-generativeai")
    sys.exit(1)

def run_direct_validation():
    """Run direct validation using existing repomix file"""
    
    # Check for API key
    api_key = os.getenv('GOOGLE_AI_API_KEY')
    if not api_key:
        print("❌ Error: GOOGLE_AI_API_KEY environment variable not set")
        return False
    
    # Configure Gemini
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # Load repomix output
    repomix_file = Path("repomix-output.xml")
    if not repomix_file.exists():
        print(f"❌ Error: {repomix_file} not found")
        return False
    
    print(f"📄 Loading {repomix_file} ({repomix_file.stat().st_size} bytes)")
    
    with open(repomix_file, 'r', encoding='utf-8') as f:
        code_content = f.read()
    
    # Validation prompt
    validation_prompt = """You are validating specific implementation claims for the T57 Path Analysis Tool.

For each claim below, verify:
1. **Implementation Present**: Does the method/feature exist where claimed?
2. **Functionality Complete**: Is it fully implemented (not stub/placeholder)?
3. **Requirements Met**: Does it satisfy the specific requirements mentioned?

CLAIMS TO VALIDATE:

**CLAIM 1**: "T57 implements advanced shortest path algorithms including Dijkstra, BFS, Bellman-Ford"
- Verify: _compute_dijkstra_paths method uses nx.single_source_dijkstra
- Verify: _compute_bfs_paths method uses nx.single_source_shortest_path  
- Verify: _compute_bellman_ford_paths method uses nx.single_source_bellman_ford
- Expected: Real NetworkX algorithms, no mocking

**CLAIM 2**: "T57 implements all-pairs shortest path analysis with proper API handling"
- Verify: _analyze_all_pairs_paths method exists
- Verify: Correctly handles nx.all_pairs_dijkstra vs nx.all_pairs_shortest_path differences
- Expected: Proper tuple unpacking for (lengths, paths) format

**CLAIM 3**: "T57 implements flow analysis with NetworkX flow algorithms"
- Verify: _analyze_flows method uses nx.maximum_flow and nx.minimum_cut
- Verify: Proper capacity attribute handling for flow graphs
- Expected: Real flow computation, not simulation

**CLAIM 4**: "T57 implements reachability analysis with connectivity metrics"
- Verify: _analyze_reachability method calculates reachability matrix
- Verify: Computes connectivity ratio and component analysis
- Expected: Real graph traversal algorithms

**CLAIM 5**: "T57 has comprehensive test suite with ~28 tests and zero mocking"
- Verify: Test file has approximately 28 test methods
- Verify: Tests use real NetworkX graphs, not mocked objects
- Expected: test_zero_mocking_validation method confirms no mocks

**CLAIM 6**: "T57 follows BaseTool interface with required methods"
- Verify: PathAnalysisTool inherits from BaseTool
- Verify: Implements get_contract, health_check, validate_input methods
- Expected: Complete interface compliance

**CLAIM 7**: "T57 provides academic-ready output with confidence calculation"
- Verify: _calculate_academic_confidence method exists
- Verify: Result metadata includes academic_ready and publication_ready flags
- Expected: Statistical significance scoring for research use

For each claim, provide verdict with specific evidence:
- ✅ **FULLY RESOLVED** - Implementation present, complete, meets requirements
- ⚠️ **PARTIALLY RESOLVED** - Implementation present but incomplete
- ❌ **NOT RESOLVED** - Implementation missing or inadequate

Include specific line numbers and method names in your analysis."""
    
    print("🤖 Sending validation request to Gemini...")
    
    try:
        response = model.generate_content(
            f"{validation_prompt}\n\nCODE TO VALIDATE:\n{code_content}",
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,
                max_output_tokens=4000
            )
        )
        
        print("\n" + "="*60)
        print("📊 GEMINI VALIDATION RESULTS")
        print("="*60)
        print(response.text)
        print("="*60)
        
        # Save results
        results_file = Path("t57-validation-results.md")
        with open(results_file, 'w') as f:
            f.write("# T57 Path Analysis - Gemini Validation Results\n\n")
            f.write(f"**Generated**: {Path(__file__).name}\n")
            f.write(f"**Timestamp**: {repomix_file.stat().st_mtime}\n\n")
            f.write("## Validation Results\n\n")
            f.write(response.text)
        
        print(f"📝 Results saved to {results_file}")
        return True
        
    except Exception as e:
        print(f"❌ Error during validation: {str(e)}")
        return False

if __name__ == "__main__":
    success = run_direct_validation()
    sys.exit(0 if success else 1)