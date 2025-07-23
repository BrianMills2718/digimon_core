#!/usr/bin/env python3
"""
Direct T52 Validation Script
"""

import google.generativeai as genai
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def load_gemini_api_key():
    """Load Gemini API key from environment"""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        api_key = os.getenv('GOOGLE_API_KEY')
    return api_key

def load_bundle(file_path):
    """Load the repomix bundle content"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def create_t52_validation_prompt():
    """Create focused validation prompt for T52"""
    return """
CRITICAL VALIDATION: T52 Graph Clustering Implementation

**CONTEXT**: Verify that T52 Graph Clustering tool is fully implemented with real algorithms and comprehensive functionality as claimed.

**SPECIFIC VALIDATION REQUIRED**:
1. T52 implements real spectral clustering with graph Laplacian computation (check for _compute_graph_laplacian and spectral clustering methods)
2. T52 supports 6 clustering algorithms: Spectral, K-means, Hierarchical, DBSCAN, Louvain, Leiden (check ClusteringAlgorithm enum and algorithm implementations)
3. T52 calculates academic-quality confidence scoring with modularity and silhouette metrics (check _calculate_academic_confidence method)
4. T52 loads graph data from 4 sources: Neo4j, NetworkX, edge lists, adjacency matrices (check _load_graph_data and specific loading methods)
5. T52 implements BaseTool interface with get_contract() method and proper execution flow (check class inheritance and required methods)

**EVIDENCE REQUIRED**:
- ✅ FULLY RESOLVED / ⚠️ PARTIALLY RESOLVED / ❌ NOT RESOLVED for each claim
- Specific code examples with line references where implementations exist
- Assessment of algorithm completeness (real vs stub implementations)
- Verification of academic-quality output with confidence scoring
- Score 1-10 for overall implementation completeness

**FOCUS**: Only T52 implementation - analyze actual method implementations and algorithm completeness.

**VERDICT FORMAT**:
For each claim: ✅ FULLY RESOLVED / ⚠️ PARTIALLY RESOLVED / ❌ NOT RESOLVED
Include specific line numbers as evidence.

Analyze the provided T52 code and validate these claims with specific evidence.
"""

def main():
    """Run T52 validation"""
    try:
        # Load API key and configure Gemini
        api_key = load_gemini_api_key()
        if not api_key:
            print("❌ No Gemini API key found. Set GEMINI_API_KEY or GOOGLE_API_KEY environment variable.")
            return
            
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        # Load the T52 bundle
        bundle_path = "/home/brian/projects/Digimons/gemini-review-tool/t52-validation-focused.xml"
        if not Path(bundle_path).exists():
            print(f"❌ Bundle not found: {bundle_path}")
            return
            
        bundle_content = load_bundle(bundle_path)
        print(f"📦 Loaded T52 bundle: {len(bundle_content)} characters")
        
        # Create validation prompt
        prompt = create_t52_validation_prompt()
        
        # Combine prompt and code
        full_prompt = f"{prompt}\n\n**CODE TO ANALYZE:**\n{bundle_content}"
        
        print("🔍 Running T52 implementation validation...")
        
        # Generate response
        response = model.generate_content(full_prompt)
        
        # Save results
        timestamp = "20250723_000200"
        output_dir = f"/home/brian/projects/Digimons/gemini-review-tool/outputs/{timestamp}"
        os.makedirs(f"{output_dir}/reviews", exist_ok=True)
        
        results_file = f"{output_dir}/reviews/t52-implementation-validation-results.md"
        with open(results_file, 'w') as f:
            f.write(f"# T52 Graph Clustering Implementation Validation Results\n")
            f.write(f"Generated: {timestamp}\n\n")
            f.write(response.text)
            
        print(f"✅ T52 validation completed!")
        print(f"📁 Results saved to: {results_file}")
        print("\n" + "="*80)
        print(response.text)
        print("="*80)
        
    except Exception as e:
        print(f"❌ Error running T52 validation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()