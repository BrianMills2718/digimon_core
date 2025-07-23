#!/usr/bin/env python3

import os
import sys
import json
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from gemini_review import GeminiCodeReviewer

def main():
    """Run direct validation on the mock elimination work"""
    
    # Initialize the reviewer
    reviewer = GeminiCodeReviewer()
    
    # Load the repomix file
    repomix_file = Path(__file__).parent / "mock-validation.xml"
    if not repomix_file.exists():
        print(f"Error: {repomix_file} not found")
        return 1
    
    # Define the validation prompt
    claims = """FOCUSED MOCK ELIMINATION VALIDATION:

**PRIMARY CLAIM**: Complete elimination of all mocking from T01 and T02 unified tool tests.

**SPECIFIC EVIDENCE TO VALIDATE**:
1. Test files contain zero mock/patch/Mock imports
2. Tests use real libraries (PyPDF2 for T01, python-docx for T02) directly  
3. Real file generation and processing in test methods
4. Evidence files document the transformation with execution logs"""

    custom_prompt = """FOCUSED MOCK ELIMINATION VALIDATION

**OBJECTIVE**: Verify complete elimination of mocking from T01 and T02 test files.

**VALIDATION STEPS**:

1. **Scan Test Files for Mocking**:
   - Search tests/unit/test_t01_pdf_loader_unified.py for any "mock", "patch", or "Mock" imports
   - Search tests/unit/test_t02_word_loader_unified.py for any "mock", "patch", or "Mock" imports  
   - Verify tests use real libraries directly (import PyPDF2, import docx)

2. **Verify Real Functionality**:
   - Confirm test methods create actual PDF/DOCX files for testing
   - Verify tests call real library methods (not mocked versions)
   - Check that ServiceManager instances are real, not mocked

3. **Evidence Validation**:
   - Review evidence files for before/after comparisons
   - Confirm execution logs show real functionality

**SCORING**:
- 10/10: Zero mocking found, all tests use real functionality
- 0/10: Mocking still present or false claims

**REQUIRED RESPONSE**:
- ✅ FULLY RESOLVED: No mocking found, complete real functionality
- ❌ NOT RESOLVED: Mocking still present or inadequate evidence

Focus exclusively on detecting any remaining mock usage patterns."""

    # Read the repomix content
    with open(repomix_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🤖 Running direct validation on mock elimination...")
    print(f"📊 File size: {len(content)/1024:.1f} KB")
    print(f"📝 Token count: ~{len(content)//4:,} tokens")
    
    # Run the validation
    try:
        response = reviewer.analyze_code(
            codebase_content=content,
            claims_of_success=claims,
            custom_prompt=custom_prompt,
            documentation=""
        )
        
        # Save the result
        output_dir = Path(__file__).parent / "outputs" / "direct_validation"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        from datetime import datetime
        
        result_file = output_dir / "mock_elimination_validation.md"
        with open(result_file, 'w', encoding='utf-8') as f:
            f.write(f"# Direct Mock Elimination Validation\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n\n")
            f.write("---\n\n")
            f.write(response)
        
        print(f"✅ Validation complete! Results saved to: {result_file}")
        print("\n" + "="*50)
        print("VALIDATION RESULT:")
        print("="*50)
        print(response)
        
        return 0
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())