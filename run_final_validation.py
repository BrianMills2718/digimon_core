#!/usr/bin/env python3
"""
Direct validation of resolved integration issues using Gemini
"""
import os
import sys
from pathlib import Path

# Add gemini-review-tool to path
sys.path.insert(0, str(Path(__file__).parent / "gemini-review-tool"))

from gemini_review import GeminiReviewer

def main():
    """Run final validation"""
    
    prompt = """
    Validate that the 3 specific issues identified by previous Gemini analysis have been resolved:
    
    **RESOLVED ISSUE 1: Claude Tool Calls Parsing**
    BEFORE: Line 90 showed "tool_calls=[], # Tool calls would need separate parsing"
    NOW: Should have real _parse_tool_calls() method with regex parsing of function calls
    
    **RESOLVED ISSUE 2: Claude Workflow Extraction**  
    BEFORE: Line 231 showed "Simple extraction - in real implementation, would parse structured formats"
    NOW: Should have robust _extract_workflow_specification() with YAML/JSON parsing
    
    **RESOLVED ISSUE 3: KGAS Phase 2 Tool Implementations**
    BEFORE: Lines 166, 185, 214 showed "Placeholder implementation - would need real KGAS ... analysis"
    NOW: Should have real implementations using NLTK, NetworkX, SciPy instead of hardcoded returns
    
    **RESOLVED ISSUE 4: Mock Fallbacks Removed**
    BEFORE: Line 243 showed generic mock with status: "mock_execution"
    NOW: Should raise NotImplementedError for unimplemented tools
    
    For each issue, report: ✅ RESOLVED or ❌ STILL PRESENT with evidence.
    
    Provide specific line numbers and code examples as evidence.
    """
    
    # Initialize reviewer
    reviewer = GeminiReviewer()
    
    # Read the validation bundle
    bundle_path = Path("validation-resolved-files.xml")
    if not bundle_path.exists():
        print("❌ Validation bundle not found. Run repomix first.")
        return 1
    
    with open(bundle_path, 'r') as f:
        codebase_content = f.read()
    
    print("🚀 Running final validation...")
    print(f"📊 Bundle size: {len(codebase_content)} characters")
    
    try:
        # Send to Gemini
        result = reviewer.review_code(
            codebase_content=codebase_content,
            custom_prompt=prompt
        )
        
        # Save results
        output_file = Path("final_validation_results.md")
        with open(output_file, 'w') as f:
            f.write("# Final Integration Issues Validation\n\n")
            f.write(f"Generated: {reviewer.get_timestamp()}\n\n")
            f.write("---\n\n")
            f.write(result)
        
        print(f"✅ Validation complete! Results saved to {output_file}")
        print("\n" + "="*60)
        print("VALIDATION SUMMARY:")
        print("="*60)
        print(result[:500] + "..." if len(result) > 500 else result)
        
        return 0
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())