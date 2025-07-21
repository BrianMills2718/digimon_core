#!/usr/bin/env python3
"""
Manual Phase 5.3 validation for critical implementation fixes
"""

import os
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from the tool directory
script_dir = Path(__file__).parent
env_file = script_dir / '.env'
load_dotenv(env_file)

# Try to import Gemini API
try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

def validate_phase53_fixes():
    """Validate Phase 5.3 implementation fixes using Gemini API"""
    
    if not HAS_GEMINI:
        print("❌ Google Generative AI not available")
        return False
    
    # Get API key
    api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ No Gemini API key found")
        return False
    
    # Configure Gemini
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # Read the repomix output with the actual code content
    repomix_file = Path(__file__).parent.parent / 'final-phase53-validation.xml'
    if not repomix_file.exists():
        print("❌ Repomix file not found. Please run: npx repomix@latest --style xml --include 'src/core/neo4j_manager.py,src/core/tool_factory.py,src/core/confidence_score.py,tests/unit/test_async_multi_document_processor.py' --output direct-test.xml .")
        return False
    
    with open(repomix_file, 'r') as f:
        codebase_content = f.read()
    
    # Validation prompt focused on Phase 5.3 critical tasks
    prompt = f"""
    Please validate that Phase 5.3 implementation issues have been fully resolved.
    
    **VALIDATION OBJECTIVE**: Verify all 4 critical issues identified in previous Gemini review are fixed.
    
    **CRITICAL REQUIREMENTS**: Each claim must demonstrate:
    1. **No Simulation Code**: Async methods use real operations, not asyncio.sleep() placeholders
    2. **No Placeholder Logic**: Tools implement real functionality, not dummy returns
    3. **Minimal Mocking**: Tests use real functionality, minimal external dependency mocking
    4. **End-to-End Integration**: Pipeline chains real data flow, no isolated component tests
    
    **CLAIMS TO VALIDATE**:
    
    **CLAIM 1: Fixed Async Migration - Removed all simulation code and implemented real async operations**
    - LOCATION: src/core/neo4j_manager.py (real async Neo4j connection), src/core/tool_factory.py (real concurrent tool auditing)
    - EXPECTED: No asyncio.sleep() simulation, real async operations using proper APIs
    - VALIDATION: Performance improvement from real async operations, not simulation timing
    
    **CLAIM 2: Fixed ConfidenceScore Integration - Replaced all placeholder tools with real implementations**
    - LOCATION: src/tools/phase1/t27_relationship_extractor.py, t31_entity_builder.py, t68_pagerank_optimized.py, src/tools/phase2/t23c_ontology_aware_extractor.py
    - EXPECTED: Real entity/relationship/aggregation logic with evidence weights and metadata
    - VALIDATION: No placeholder or dummy logic, full ConfidenceScore usage with add_evidence()
    
    **CLAIM 3: Fixed Unit Testing - Replaced heavy mocking with real functionality testing**
    - LOCATION: tests/unit/test_async_multi_document_processor.py, test_security_manager.py
    - EXPECTED: Real async processing, memory management, and security validation with minimal external mocking
    - VALIDATION: Tests measure actual performance, memory usage, and cryptographic operations
    
    **CLAIM 4: Fixed Academic Pipeline - Implemented true end-to-end workflow integration**
    - LOCATION: tests/integration/test_academic_pipeline_simple.py
    - EXPECTED: Chained data flow from PDF→Text→Entities→Export with real data passing between steps
    - VALIDATION: 15+ entities extracted, LaTeX/BibTeX contain real data, complete workflow under 60s
    
    For each claim, verify:
    - ✅ FULLY RESOLVED: Issue completely fixed with real implementation
    - ⚠️ PARTIALLY RESOLVED: Some improvement but still has issues
    - ❌ NOT RESOLVED: Issue remains unaddressed
    
    **CRITICAL VALIDATION CRITERIA**:
    
    **CLAIM 1 - Async Migration**: Look for:
    - src/core/neo4j_manager.py: NO asyncio.sleep() simulation around lines 94+
    - src/core/tool_factory.py: NO asyncio.sleep() simulation around lines 239+
    - Real async operations using neo4j.AsyncGraphDatabase or proper async APIs
    - Real concurrent tool auditing with asyncio.gather
    
    **CLAIM 2 - ConfidenceScore Integration**: Look for:
    - Any tool files in the codebase: Real functionality with add_evidence()
    - ConfidenceScore usage with meaningful weights and metadata
    - NO "placeholder", "dummy", or "simulation" logic in tool implementations
    
    **CLAIM 3 - Unit Testing**: Look for:
    - test_async_multi_document_processor.py: Real async processing, minimal mocking
    - Tests that measure actual performance, memory usage, timing
    - NO heavy mocking of core business logic (excessive use of MagicMock, patch)
    
    **CLAIM 4 - Academic Pipeline**: (May not be fully visible in this subset)
    - Any integration test files: True end-to-end workflow chains
    - NO hardcoded or dummy test data in workflow tests
    
    **VALIDATION METHODOLOGY**:
    1. Code inspection for simulation/placeholder removal
    2. Implementation verification for real functionality
    3. Evidence checking for actual data processing
    4. Integration verification for end-to-end workflows
    
    Provide specific line numbers and code evidence for each assessment.
    Be thorough and skeptical - look for any remaining simulation, placeholder, or mock code.
    
    CODEBASE CONTENT:
    {codebase_content}
    """
    
    try:
        print("🤖 Sending Phase 5.3 validation request to Gemini...")
        response = model.generate_content(prompt)
        
        print("\n" + "="*80)
        print("🔍 GEMINI PHASE 5.3 VALIDATION RESULTS")
        print("="*80)
        print(response.text)
        
        # Save results
        results = {
            "validation_timestamp": datetime.now().isoformat(),
            "model": "gemini-2.5-flash",
            "prompt_length": len(prompt),
            "response": response.text,
            "claims_validated": [
                "CLAIM 1: Fixed Async Migration",
                "CLAIM 2: Fixed ConfidenceScore Integration", 
                "CLAIM 3: Fixed Unit Testing",
                "CLAIM 4: Fixed Academic Pipeline"
            ]
        }
        
        output_file = f'phase53_validation_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Also save as markdown
        md_file = f'phase53_validation_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
        with open(md_file, 'w') as f:
            f.write(f"# Phase 5.3 Implementation Fixes Validation\n\n")
            f.write(f"**Generated**: {datetime.now().isoformat()}\n")
            f.write(f"**Model**: gemini-2.5-flash\n")
            f.write(f"**Validation Objective**: Verify 4 critical Phase 5.3 implementation fixes\n\n")
            f.write("---\n\n")
            f.write(response.text)
        
        print(f"\n💾 Validation results saved to:")
        print(f"   📄 {output_file}")
        print(f"   📝 {md_file}")
        return True
        
    except Exception as e:
        print(f"❌ Gemini validation failed: {e}")
        return False

def main():
    """Main validation execution"""
    print("🧪 Manual Phase 5.3 Critical Fixes Validation")
    print("📋 Validating 4 critical implementation fixes for Phase 5.3")
    print("=" * 80)
    
    success = validate_phase53_fixes()
    
    if success:
        print("\n✅ Phase 5.3 validation completed successfully")
        print("📊 Review results above for FULLY RESOLVED, PARTIALLY RESOLVED, or NOT RESOLVED verdicts")
    else:
        print("\n❌ Phase 5.3 validation failed")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)