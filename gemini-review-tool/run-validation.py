#!/usr/bin/env python3

import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from gemini_review import GeminiCodeReviewer

def main():
    """Run validation using the properly packed test files"""
    
    # Initialize the reviewer
    reviewer = GeminiCodeReviewer()
    
    # Load the repomix file with test content
    repomix_file = Path(__file__).parent / "test-validation.xml"
    if not repomix_file.exists():
        print(f"Error: {repomix_file} not found")
        return 1
    
    # Define claims
    claims = """MOCK ELIMINATION IMPLEMENTATION CLAIMS:

1. **Complete Mock Import Elimination**: T01 and T02 test files contain zero unittest.mock imports
   - File: tests/unit/test_t01_pdf_loader_unified.py - No unittest.mock, Mock, patch, or MagicMock imports
   - File: tests/unit/test_t02_word_loader_unified.py - No unittest.mock, Mock, patch, or MagicMock imports

2. **Real PDF Processing Implementation**: T01 tests create and process actual PDF files
   - File: tests/unit/test_t01_pdf_loader_unified.py - Contains _create_real_test_pdf() method using reportlab/raw PDF
   - Expected: Real PDF file generation using actual PDF structure or reportlab library

3. **Real DOCX Processing Implementation**: T02 tests create and process actual DOCX files  
   - File: tests/unit/test_t02_word_loader_unified.py - Contains _create_real_test_docx() method using python-docx
   - Expected: Real DOCX file generation using python-docx Document class

4. **Real ServiceManager Integration**: Both test files use actual ServiceManager instances
   - Files: Both test files - ServiceManager() instantiation in setup_method, not mocked
   - Expected: self.service_manager = ServiceManager() calls instead of Mock() objects"""

    custom_prompt = """MOCK ELIMINATION IMPLEMENTATION VALIDATION

**OBJECTIVE**: Verify that T01 and T02 test files have completely eliminated mocking and implement real functionality.

**VALIDATION CRITERIA FOR EACH CLAIM**:

1. **Mock Import Elimination Verification**:
   - Scan import statements at top of both test files
   - Confirm NO "from unittest.mock import" statements
   - Confirm NO usage of Mock(), patch(), MagicMock() anywhere in the files
   - Look for comments indicating mock removal (e.g., "# Real imports - NO mocking imports")

2. **Real PDF Processing Implementation**:
   - Locate _create_real_test_pdf() method in test_t01_pdf_loader_unified.py
   - Verify it creates actual PDF files using reportlab or raw PDF byte structure
   - Confirm method writes real PDF content to filesystem using open() with 'wb' mode
   - Check for real file creation with proper PDF headers/structure

3. **Real DOCX Processing Implementation**:
   - Locate _create_real_test_docx() method in test_t02_word_loader_unified.py  
   - Verify it imports and uses python-docx Document class
   - Confirm method creates real DOCX with document.add_heading(), document.add_paragraph()
   - Check for document.save() calls to write actual DOCX files

4. **Real ServiceManager Integration**:
   - Find setup_method() in both test classes
   - Verify "self.service_manager = ServiceManager()" instantiation
   - Confirm NO "Mock(spec=ServiceManager)" or similar mock patterns
   - Check that tools are initialized with real service_manager instances

**REQUIRED RESPONSE FORMAT**:
For each claim, provide:
- ✅ FULLY RESOLVED: Implementation found at [specific line numbers], meets all requirements
- ⚠️ PARTIALLY RESOLVED: Implementation found but incomplete/missing elements  
- ❌ NOT RESOLVED: Implementation missing or still uses mocking patterns

**FOCUS AREAS**:
- Reference specific line numbers where implementations are found
- Quote actual code snippets that demonstrate real functionality
- Identify any remaining mock patterns if found
- Verify file creation methods use real libraries not mocks"""

    # Read the repomix content
    with open(repomix_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔍 RUNNING GEMINI VALIDATION")
    print("="*50)
    print(f"📊 File size: {len(content)/1024:.1f} KB")
    print(f"📝 Token count: ~{len(content)//4:,} tokens")
    print(f"📁 Validating files: test_t01_pdf_loader_unified.py, test_t02_word_loader_unified.py")
    
    # Run the validation
    try:
        response = reviewer.analyze_code(
            codebase_content=content,
            claims_of_success=claims,
            custom_prompt=custom_prompt,
            documentation=""
        )
        
        # Save the result
        from datetime import datetime
        output_dir = Path(__file__).parent / "outputs" / "implementation_validation"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        result_file = output_dir / f"validation_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(result_file, 'w', encoding='utf-8') as f:
            f.write(f"# Mock Elimination Implementation Validation\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n\n")
            f.write("---\n\n")
            f.write(response)
        
        print(f"✅ Validation complete! Results saved to: {result_file}")
        print("\n" + "="*50)
        print("GEMINI VALIDATION VERDICT:")
        print("="*50)
        print(response)
        
        return 0
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())