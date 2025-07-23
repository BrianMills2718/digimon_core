#!/usr/bin/env python3
"""
Direct Gemini validation script for development standards documentation
"""

import os
import google.generativeai as genai
from datetime import datetime

def main():
    # Configure Gemini API - try different ways to get the key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        # Try to read from common locations
        key_files = ["~/.config/gemini/api_key", "~/.gemini_api_key", ".gemini_api_key"]
        for key_file in key_files:
            expanded_path = os.path.expanduser(key_file)
            if os.path.exists(expanded_path):
                try:
                    with open(expanded_path, 'r') as f:
                        api_key = f.read().strip()
                    break
                except:
                    continue
    
    if not api_key:
        print("❌ Could not find GEMINI_API_KEY. Please set environment variable or create ~/.gemini_api_key file")
        return
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # Read the repomix output
    try:
        with open('validation-docs.xml', 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ validation-docs.xml not found. Run repomix first.")
        return
    
    # Validation prompt
    prompt = """
**VALIDATION OBJECTIVE**: Verify the implementation claims for the comprehensive development standards documentation suite.

**VALIDATION CRITERIA**: For each claim below, verify:
1. **Implementation Present**: Does the documentation file exist with the claimed content?
2. **Comprehensive Coverage**: Does it cover all the claimed areas and use cases?
3. **Academic Research Focus**: Does it specifically address academic research requirements?
4. **Integration Consistency**: Does it integrate properly with the overall system architecture?
5. **Practical Completeness**: Is it actionable and complete rather than just theoretical?

**CLAIMS TO VALIDATE**:

1. **Code Documentation Standards**: Complete comprehensive code documentation framework with academic research requirements implemented in docs/development/standards/code-documentation-standards.md
2. **System Behavior Recording Protocols**: Complete operational knowledge capture framework for knowledge transfer implemented in docs/development/standards/system-behavior-recording-protocols.md
3. **Knowledge Transfer Protocols**: Complete systematic developer transition processes with academic domain knowledge preservation implemented in docs/development/standards/knowledge-transfer-protocols.md
4. **Comprehensive Configuration Documentation**: Complete centralized configuration management with academic optimization implemented in docs/development/standards/comprehensive-configuration-documentation.md
5. **Development Workflow Documentation**: Complete systematic development processes with academic integration implemented in docs/development/standards/development-workflow-documentation.md
6. **Testing Strategy Documentation**: Complete mock-free testing methodology with academic validation frameworks implemented in docs/development/standards/testing-strategy-documentation.md
7. **Deployment Procedures Documentation**: Complete safe deployment processes with academic data protection implemented in docs/development/standards/deployment-procedures-documentation.md
8. **Monitoring and Observability Documentation**: Complete academic research-focused monitoring frameworks implemented in docs/development/standards/monitoring-observability-documentation.md

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

CODEBASE CONTENT:
""" + content

    print("🤖 Sending validation request to Gemini...")
    
    try:
        response = model.generate_content(prompt)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"development-standards-validation-results-{timestamp}.md"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# Development Standards Documentation Validation Results\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write(f"Model: gemini-2.5-flash\n\n")
            f.write("---\n\n")
            f.write(response.text)
        
        print(f"✅ Validation complete! Results saved to: {output_file}")
        
        # Print summary to console
        print("\n" + "="*60)
        print("📊 VALIDATION RESULTS SUMMARY")
        print("="*60)
        
        # Extract key findings from response
        lines = response.text.split('\n')
        for line in lines:
            if '✅' in line or '⚠️' in line or '❌' in line:
                print(line)
        
        print("="*60)
        print(f"📄 Full results: {output_file}")
        
    except Exception as e:
        print(f"❌ Error during validation: {e}")

if __name__ == "__main__":
    main()