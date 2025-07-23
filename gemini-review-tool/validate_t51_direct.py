#!/usr/bin/env python3
"""
Direct T51 Validation Script
"""

import google.generativeai as genai
import os
from pathlib import Path

def load_gemini_api_key():
    """Load Gemini API key from environment"""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        # Try alternate environment variable names
        api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY environment variable not set")
    return api_key

def load_bundle(file_path):
    """Load the repomix bundle content"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def create_validation_prompt():
    """Create focused validation prompt for T51"""
    return """
Validate ONLY T51 Centrality Analysis implementation claims:

**SPECIFIC CLAIMS TO VALIDATE:**
1. T51 implements 12 centrality metrics using NetworkX (lines 570-671)
2. T51 provides comprehensive PageRank fallback system (scipy → numpy → custom) (lines 590-635)  
3. T51 calculates correlation matrix between centrality measures (lines 673-705)
4. T51 loads graph data from 4 sources: Neo4j, NetworkX, edge lists, adjacency matrices (lines 472-510)
5. T51 provides academic-quality statistical analysis with confidence scoring (lines 707-743)

**EVIDENCE REQUIRED:**
- NetworkX centrality function calls (degree, betweenness, closeness, eigenvector, etc.)
- Three-tier PageRank fallback implementation with try/except blocks
- Real correlation calculation using numpy.corrcoef() 
- Four distinct data loading methods implemented
- Academic confidence calculation with centrality statistics

**FOCUS:** Only T51 implementation - ignore imports, tests, or other tools.

**VERDICT FORMAT:**
For each claim: ✅ FULLY RESOLVED / ⚠️ PARTIALLY RESOLVED / ❌ NOT RESOLVED
Include specific line numbers as evidence.

Analyze the provided T51 code and validate these claims with specific evidence.
"""

def main():
    """Run T51 validation"""
    try:
        # Load API key and configure Gemini
        api_key = load_gemini_api_key()
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        # Load the T51 bundle
        bundle_path = "/home/brian/projects/Digimons/gemini-review-tool/t51-validation.xml"
        if not Path(bundle_path).exists():
            print(f"❌ Bundle not found: {bundle_path}")
            return
            
        bundle_content = load_bundle(bundle_path)
        print(f"📦 Loaded T51 bundle: {len(bundle_content)} characters")
        
        # Create validation prompt
        prompt = create_validation_prompt()
        
        # Combine prompt and code
        full_prompt = f"{prompt}\n\n**CODE TO ANALYZE:**\n{bundle_content}"
        
        print("🔍 Running T51 validation...")
        
        # Generate response
        response = model.generate_content(full_prompt)
        
        # Save results
        timestamp = "20250723_001500"  # Current timestamp
        output_dir = f"/home/brian/projects/Digimons/gemini-review-tool/outputs/{timestamp}"
        os.makedirs(f"{output_dir}/reviews", exist_ok=True)
        
        results_file = f"{output_dir}/reviews/t51-validation-results.md"
        with open(results_file, 'w') as f:
            f.write(f"# T51 Centrality Analysis Validation Results\n")
            f.write(f"Generated: {timestamp}\n\n")
            f.write(response.text)
            
        print(f"✅ T51 validation completed!")
        print(f"📁 Results saved to: {results_file}")
        print("\n" + "="*80)
        print(response.text)
        print("="*80)
        
    except Exception as e:
        print(f"❌ Error running T51 validation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()