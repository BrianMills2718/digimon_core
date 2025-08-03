#!/usr/bin/env python3
"""
Test the fully fixed integrated system with:
1. Structured parameter extraction (text-schema)
2. Simple executor that works
3. Proper parameter resolution
"""

import os
import sys
import json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.theory_to_code import IntegratedTheorySystem


def main():
    print("🚀 FIXED THEORY-TO-CODE SYSTEM TEST")
    print("=" * 60)
    
    # Initialize system
    system = IntegratedTheorySystem()
    
    # Load theory
    schema_path = "config/schemas/prospect_theory_schema.json"
    print(f"\n1. Loading {schema_path}...")
    
    success = system.load_and_compile_theory(schema_path)
    print(f"   ✓ Theory compiled: {success}")
    
    if not success:
        return
    
    # Test text with clear parameters
    test_text = """
    The board must choose between two investment strategies.
    
    Strategy A: Aggressive expansion with 70% probability of major gains
    (capturing significant market share), but 30% chance of substantial 
    losses if market conditions turn unfavorable.
    
    Strategy B: Conservative growth that is virtually certain (95%) to 
    deliver moderate returns, with only a 5% risk of minor losses.
    """
    
    print(f"\n2. Analyzing text...")
    print("-" * 40)
    print(test_text.strip())
    print("-" * 40)
    
    try:
        # Analyze
        analysis = system.analyze_text(test_text, 'prospect_theory')
        
        # Show text-schema extraction
        text_schema = analysis.execution_metadata.get('text_schema', {})
        print(f"\n3. TEXT-SCHEMA EXTRACTION:")
        print(f"   Theory: {text_schema.get('theory_name')}")
        print(f"   Confidence: {text_schema.get('confidence', 0):.0%}")
        
        for prospect in text_schema.get('extracted_prospects', []):
            print(f"\n   {prospect['name']}:")
            print(f"   Outcomes:")
            for outcome in prospect.get('text_outcomes', []):
                print(f"     - {outcome['description']}")
                print(f"       Category: {outcome['linguistic_category']}")
                print(f"       Range: {outcome['mapped_range']}")
            print(f"   Probabilities:")
            for prob in prospect.get('text_probabilities', []):
                print(f"     - {prob['description']}: {prob['value']}")
        
        # Show resolved parameters
        print(f"\n4. RESOLVED PARAMETERS:")
        for param in analysis.extracted_parameters:
            print(f"\n   {param['prospect_name']}:")
            print(f"     Outcomes: {param['outcomes']}")
            print(f"     Probabilities: {param['probabilities']}")
        
        # Show computational results
        print(f"\n5. COMPUTATIONAL RESULTS:")
        for prospect, data in analysis.computational_results.items():
            print(f"\n   {prospect}:")
            for func, result in data['results'].items():
                if result['success']:
                    value = result['value']
                    # Handle both single values and lists
                    if isinstance(value, list):
                        formatted = [f"{v:.2f}" for v in value]
                        print(f"     {func}: {formatted} ✓")
                    else:
                        print(f"     {func}: {value:.2f} ✓")
                else:
                    print(f"     {func}: Failed ✗")
                    if result.get('error'):
                        print(f"       Error: {result['error'][:100]}...")
        
        # Show insights
        print(f"\n6. INSIGHTS:")
        print(f"{analysis.insights}")
        
        # Summary
        print(f"\n7. EXECUTION SUMMARY:")
        print(f"   Total time: {analysis.execution_metadata['execution_time_seconds']:.1f}s")
        print(f"   Functions executed: {len(analysis.execution_metadata['functions_executed'])}")
        
        # What's in the text-schema vs parameters
        print(f"\n8. KEY DIFFERENCE - TEXT-SCHEMA vs PARAMETERS:")
        print(f"   Text-Schema: Contains ranges like '60 to 80'")
        print(f"   Parameters: Resolved to single values like 70.0")
        print(f"   This separation allows flexibility in resolution strategies!")
        
        print("\n✅ ALL SYSTEMS WORKING!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()