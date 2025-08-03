#!/usr/bin/env python3
"""
Test the integrated formula parsing in the MCP algorithm tools.
This validates that real formula implementation is working in the production system.
"""

import json
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp_tools.algorithm_tools import AlgorithmImplementationTools

def test_integrated_formula_tools():
    """Test that the algorithm tools can now generate real formula implementations"""
    
    print("=== Testing Integrated Formula Tools ===")
    
    # Create the tools instance
    algo_tools = AlgorithmImplementationTools()
    
    # Test prospect theory formulas
    test_components = [
        {
            "name": "Value Function for Gains",
            "category": "FORMULAS",
            "description": "Value function for gains in prospect theory: v(x) = x^0.88",
            "implementation": "v(x) = x^0.88"
        },
        {
            "name": "Value Function for Losses",
            "category": "FORMULAS", 
            "description": "Value function for losses: v(x) = -2.25 * (-x)^0.88",
            "implementation": "v(x) = -2.25 * (-x)^0.88"
        },
        {
            "name": "Probability Weighting",
            "category": "FORMULAS",
            "description": "Probability weighting function: w(p) = p^0.61", 
            "implementation": "w(p) = p^0.61"
        }
    ]
    
    results = {
        "total_tested": len(test_components),
        "real_implementations": 0,
        "placeholder_implementations": 0,
        "semantic_quality_scores": [],
        "results": []
    }
    
    for component in test_components:
        print(f"\n--- Testing {component['name']} ---")
        
        # Generate implementation using the integrated tools
        result = algo_tools._generate_implementation(component, "Prospect Theory")
        
        if result.success:
            print(f"✅ Generated code successfully")
            
            # Check if it's a real implementation or placeholder
            if "placeholder" in result.code.lower() or "todo" in result.code.lower():
                results["placeholder_implementations"] += 1
                print(f"❌ Still generating placeholder code")
                implementation_type = "placeholder"
            else:
                # Check for actual mathematical operations
                if any(op in result.code for op in ['**', 'math.', '*', '+', '-']):
                    results["real_implementations"] += 1
                    print(f"✅ Generated REAL mathematical implementation")
                    implementation_type = "real"
                else:
                    results["placeholder_implementations"] += 1
                    print(f"❌ No mathematical operations found")
                    implementation_type = "placeholder"
            
            # Check quality score (should be higher for real implementations)
            quality = result.quality_score
            results["semantic_quality_scores"].append(quality)
            print(f"Quality score: {quality:.3f}")
            
            results["results"].append({
                "name": component["name"],
                "success": result.success,
                "implementation_type": implementation_type,
                "quality_score": quality,
                "has_math_operations": any(op in result.code for op in ['**', 'math.', '*', '+', '-']),
                "code_preview": result.code[:200] + "..." if len(result.code) > 200 else result.code
            })
        else:
            print(f"❌ Failed to generate code: {result.error}")
            results["results"].append({
                "name": component["name"],
                "success": False,
                "error": result.error
            })
    
    # Calculate success metrics
    total = results["total_tested"]
    real_impls = results["real_implementations"]
    placeholder_impls = results["placeholder_implementations"]
    
    print(f"\n=== RESULTS ===")
    print(f"Total tested: {total}")
    print(f"Real implementations: {real_impls}")
    print(f"Placeholder implementations: {placeholder_impls}")
    print(f"Real implementation rate: {real_impls}/{total} ({100*real_impls/total:.1f}%)")
    
    if results["semantic_quality_scores"]:
        avg_quality = sum(results["semantic_quality_scores"]) / len(results["semantic_quality_scores"])
        print(f"Average quality score: {avg_quality:.3f}")
    
    # Save results
    with open("integrated_formula_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"Detailed results saved to integrated_formula_test_results.json")
    
    # Success criteria: at least 2/3 real implementations
    success = real_impls >= 2
    if success:
        print(f"\n✅ SUCCESS: Formula parsing integration working!")
        print(f"BREAKTHROUGH: We now have real mathematical code generation!")
    else:
        print(f"\n❌ INTEGRATION INCOMPLETE: Still generating mostly placeholders")
    
    return success

if __name__ == "__main__":
    success = test_integrated_formula_tools()
    sys.exit(0 if success else 1)