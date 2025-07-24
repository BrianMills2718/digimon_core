#!/usr/bin/env python3
"""
Direct validation using Gemini API
"""
import os
import google.generativeai as genai
from datetime import datetime

def main():
    """Run direct validation"""
    
    # Configure Gemini
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment")
        return 1
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # Read validation bundle
    with open('validation-resolved-files.xml', 'r') as f:
        codebase = f.read()
    
    prompt = f"""
CODEBASE ANALYSIS REQUEST

Please critically evaluate this codebase to validate that specific integration issues have been resolved.

CODEBASE:
{codebase}

VALIDATION REQUEST:

Validate that the 4 specific issues identified by previous Gemini analysis have been resolved:

**ISSUE 1: Claude Tool Calls Parsing**
BEFORE: Line 90 showed "tool_calls=[], # Tool calls would need separate parsing"
REQUIREMENT: Should have real _parse_tool_calls() method with regex parsing of function calls

**ISSUE 2: Claude Workflow Extraction**  
BEFORE: Line 231 showed "Simple extraction - in real implementation, would parse structured formats"
REQUIREMENT: Should have robust _extract_workflow_specification() with YAML/JSON parsing

**ISSUE 3: KGAS Phase 2 Tool Implementations**
BEFORE: Lines 166, 185, 214 showed "Placeholder implementation - would need real KGAS ... analysis"
REQUIREMENT: Should have real implementations using NLTK, NetworkX, SciPy instead of hardcoded returns

**ISSUE 4: Mock Fallbacks Removed**
BEFORE: Line 243 showed generic mock with status: "mock_execution"
REQUIREMENT: Should raise NotImplementedError for unimplemented tools

ANALYSIS FORMAT:

For each issue, provide:
1. ✅ RESOLVED or ❌ STILL PRESENT
2. Evidence: Specific line numbers and code excerpts
3. Assessment: Brief explanation of the implementation

Be specific and cite actual code from the files provided.
"""
    
    print("🚀 Sending validation request to Gemini...")
    print(f"📊 Bundle size: {len(codebase):,} characters")
    
    try:
        response = model.generate_content(prompt)
        result = response.text
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"final_validation_results_{timestamp}.md"
        
        with open(output_file, 'w') as f:
            f.write("# Final Integration Issues Validation Results\n\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n\n")
            f.write("---\n\n")
            f.write(result)
        
        print(f"✅ Validation complete! Results saved to {output_file}")
        print("\n" + "="*60)
        print("VALIDATION SUMMARY:")
        print("="*60)
        print(result)
        
        return 0
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())