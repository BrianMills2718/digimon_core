#!/usr/bin/env python3
"""
Direct validation using the existing gemini review infrastructure
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from gemini_review import GeminiReviewer
from gemini_review_config import ReviewConfig

def main():
    # Create a custom config for validation
    config = ReviewConfig(
        project_name="Development Standards Documentation Validation",
        custom_prompt="""
**VALIDATION OBJECTIVE**: Verify the implementation claims for the comprehensive development standards documentation suite.

**VALIDATION CRITERIA**: For each claim below, verify:
1. **Implementation Present**: Does the documentation file exist with the claimed content?
2. **Comprehensive Coverage**: Does it cover all the claimed areas and use cases?  
3. **Academic Research Focus**: Does it specifically address academic research requirements?
4. **Integration Consistency**: Does it integrate properly with the overall system architecture?
5. **Practical Completeness**: Is it actionable and complete rather than just theoretical?

**CLAIMS TO VALIDATE**:

1. **Code Documentation Standards**: Complete comprehensive code documentation framework with academic research requirements
2. **System Behavior Recording Protocols**: Complete operational knowledge capture framework for knowledge transfer  
3. **Knowledge Transfer Protocols**: Complete systematic developer transition processes with academic domain knowledge preservation
4. **Comprehensive Configuration Documentation**: Complete centralized configuration management with academic optimization
5. **Development Workflow Documentation**: Complete systematic development processes with academic integration
6. **Testing Strategy Documentation**: Complete mock-free testing methodology with academic validation frameworks
7. **Deployment Procedures Documentation**: Complete safe deployment processes with academic data protection
8. **Monitoring and Observability Documentation**: Complete academic research-focused monitoring frameworks

**SUCCESS CRITERIA**:
Each claim should be rated as:
- ✅ FULLY RESOLVED: Complete implementation with all claimed features and academic focus
- ⚠️ PARTIALLY RESOLVED: Implementation present but missing some claimed elements  
- ❌ NOT RESOLVED: Implementation incomplete, missing, or not meeting claims

**VALIDATION INSTRUCTIONS**:
1. Examine each documentation file for completeness and practical applicability
2. Verify academic research focus is maintained throughout
3. Check integration between different standards documents
4. Assess whether implementations address the specific architectural issues they claim to solve
5. Determine if the documentation provides actionable guidance rather than just theoretical frameworks

Please analyze the provided documentation files and provide a verdict for each claim with specific evidence from the content.
""",
        claims_of_success={
            "Code Documentation Standards": "Complete comprehensive code documentation framework with academic research requirements implemented in docs/development/standards/code-documentation-standards.md",
            "System Behavior Recording Protocols": "Complete operational knowledge capture framework for knowledge transfer implemented in docs/development/standards/system-behavior-recording-protocols.md", 
            "Knowledge Transfer Protocols": "Complete systematic developer transition processes with academic domain knowledge preservation implemented in docs/development/standards/knowledge-transfer-protocols.md",
            "Comprehensive Configuration Documentation": "Complete centralized configuration management with academic optimization implemented in docs/development/standards/comprehensive-configuration-documentation.md",
            "Development Workflow Documentation": "Complete systematic development processes with academic integration implemented in docs/development/standards/development-workflow-documentation.md",
            "Testing Strategy Documentation": "Complete mock-free testing methodology with academic validation frameworks implemented in docs/development/standards/testing-strategy-documentation.md",
            "Deployment Procedures Documentation": "Complete safe deployment processes with academic data protection implemented in docs/development/standards/deployment-procedures-documentation.md",
            "Monitoring and Observability Documentation": "Complete academic research-focused monitoring frameworks implemented in docs/development/standards/monitoring-observability-documentation.md"
        }
    )
    
    # Initialize reviewer
    reviewer = GeminiReviewer()
    
    # Read the repomix output
    repomix_path = "repomix-output.xml"
    if not os.path.exists(repomix_path):
        print(f"❌ {repomix_path} not found")
        return
    
    with open(repomix_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🤖 Sending validation request to Gemini...")
    
    try:
        # Run the review
        result = reviewer.review_content(content, config)
        
        # Save results
        output_file = "development-standards-validation-results.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result)
        
        print(f"✅ Validation complete! Results saved to: {output_file}")
        
        # Print key findings
        print("\n" + "="*60)
        print("📊 VALIDATION RESULTS SUMMARY")
        print("="*60)
        
        lines = result.split('\n')
        for line in lines:
            if '✅' in line or '⚠️' in line or '❌' in line:
                print(line)
        
        print("="*60)
        print(f"📄 Full results: {output_file}")
        
    except Exception as e:
        print(f"❌ Error during validation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()