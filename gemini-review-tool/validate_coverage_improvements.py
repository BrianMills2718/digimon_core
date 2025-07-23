#!/usr/bin/env python3
"""
Focused validation of coverage improvement claims using existing bundle
"""

import os
import google.generativeai as genai
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

def main():
    print("=== Coverage Improvement Claims Validation ===\n")
    
    # Load environment variables
    load_dotenv()
    
    # Configure API
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment")
        return
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash-exp")
    
    # Load the bundle
    bundle_path = Path("coverage-validation-bundle.xml")
    if not bundle_path.exists():
        print(f"❌ Bundle not found: {bundle_path}")
        return
    
    print(f"📦 Loading validation bundle: {bundle_path}")
    with open(bundle_path, 'r', encoding='utf-8') as f:
        bundle_content = f.read()
    
    print(f"📄 Bundle size: {len(bundle_content):,} characters")
    
    # Create focused validation prompt
    prompt = f"""
CRITICAL COVERAGE IMPROVEMENT VALIDATION

**VALIDATION OBJECTIVE**: Verify specific claims about test coverage improvements and implementation quality.

**CONTEXT**: This project implemented Test-Driven Development (TDD) with a focus on achieving 95%+ test coverage while avoiding mocking of core functionality. The claims below represent specific improvements made to achieve production-ready test quality.

**COVERAGE IMPROVEMENT CLAIMS TO VALIDATE**:

1. **T01 PDF Loader Coverage**: Improved from 88% to 90% by adding 7 new error scenario tests
   - tests/unit/test_t01_pdf_loader_unified.py lines 545-751: New error handling tests
   - Covers unsupported file types, extraction failures, document creation errors, quality assessment errors

2. **T02 Word Loader Coverage**: Improved from 91% to 93% by adding 5 new error scenario tests  
   - tests/unit/test_t02_word_loader_unified.py lines 718-863: New error handling tests
   - Covers file extension validation, extraction failures, quality errors, cleanup errors

3. **Zero Mocking Achievement**: All tests use real functionality, no mocking of core operations
   - PDF extraction uses real PyPDF2 library
   - DOCX parsing uses real python-docx library
   - spaCy NER uses real language models

4. **Test Count Achievement**: 180+ comprehensive tests across unified tools
   - T01: 25+ tests (was 18)
   - T02: 24+ tests (was 19)
   - All tests cover real error scenarios and edge cases

5. **Production Quality**: Comprehensive error handling and real service integration
   - All error paths properly tested
   - Real service manager instances used throughout
   - Performance requirements validated with actual timing

**SPECIFIC VALIDATION REQUIRED**:

1. **TEST ADDITION VERIFICATION**:
   - Are the new test methods present in the specified files and line ranges?
   - Do they test the claimed error scenarios (unsupported files, extraction failures, etc.)?
   - Are they comprehensive tests or just placeholders?

2. **COVERAGE TARGET VERIFICATION**:
   - Do the new tests actually cover previously missed code paths?
   - Are they testing realistic error conditions?
   - Do they follow the same quality patterns as existing tests?

3. **REAL FUNCTIONALITY VERIFICATION**:
   - Are tests using real libraries (PyPDF2, python-docx, spaCy)?
   - Is there evidence of mocking elimination in the test code?
   - Do tests use actual ServiceManager instances?

4. **QUALITY STANDARD VERIFICATION**:
   - Do tests follow TDD patterns?
   - Are error scenarios comprehensive and realistic?
   - Is performance validation included?

**REQUIRED RESPONSE FORMAT**:

For each of the 5 claims above, provide:
- **STATUS**: ✅ FULLY RESOLVED / ⚠️ PARTIALLY RESOLVED / ❌ NOT RESOLVED
- **EVIDENCE**: Specific code examples with line references from the provided files
- **ANALYSIS**: Detailed explanation of findings

**FINAL ASSESSMENT**: Overall validation score 1-10 where:
- 10 = All claims fully validated with comprehensive evidence
- 7-9 = Most claims validated with minor gaps
- 4-6 = Some claims validated but significant issues
- 1-3 = Claims not supported by evidence

**FOCUS AREAS**:
- Examine test_t01_pdf_loader_unified.py lines 545-751 for T01 improvements
- Examine test_t02_word_loader_unified.py lines 718-863 for T02 improvements  
- Look for evidence of real functionality vs mocking patterns
- Assess comprehensiveness of error scenario testing

Here is the code bundle to analyze:

{bundle_content}
"""
    
    print("🤖 Sending validation request to Gemini...")
    
    try:
        response = model.generate_content(prompt)
        result = response.text
        
        print("✅ Validation completed!\n")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_dir = Path("outputs") / timestamp
        results_dir.mkdir(parents=True, exist_ok=True)
        
        results_file = results_dir / "coverage-improvement-validation.md"
        with open(results_file, 'w') as f:
            f.write(f"# Coverage Improvement Validation Results\n\n")
            f.write(f"**Date**: {datetime.now().isoformat()}\n")
            f.write(f"**Model**: gemini-2.0-flash-exp\n")
            f.write(f"**Bundle**: {bundle_path}\n\n")
            f.write("## Validation Results\n\n")
            f.write(result)
        
        print(f"📄 Results saved to: {results_file}")
        print("\n" + "="*80)
        print("VALIDATION RESULTS:")
        print("="*80)
        print(result)
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")

if __name__ == "__main__":
    main()