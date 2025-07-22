#!/usr/bin/env python3
"""
Simple script to get Gemini review of architecture documentation
"""
import os
import google.generativeai as genai
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def collect_architecture_docs():
    """Collect key architecture documentation files"""
    base_path = Path("docs/architecture")
    
    key_files = [
        "ARCHITECTURE_OVERVIEW.md",
        "concepts/master-concept-library.md", 
        "concepts/cross-modal-philosophy.md",
        "concepts/uncertainty-architecture.md",
        "concepts/conceptual-to-implementation-mapping.md",
        "systems/mcp-integration-architecture.md",
        "systems/external-mcp-orchestration.md",
        "adrs/ADR-001-Phase-Interface-Design.md",
        "adrs/ADR-003-Vector-Store-Consolidation.md", 
        "adrs/ADR-005-buy-vs-build-strategy.md"
    ]
    
    docs_content = []
    
    for file_path in key_files:
        full_path = base_path / file_path
        if full_path.exists():
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                docs_content.append(f"## File: {file_path}\n\n{content}\n\n" + "="*80 + "\n")
                print(f"✅ Included: {file_path}")
        else:
            print(f"⚠️  Missing: {file_path}")
    
    return "\n".join(docs_content)

def main():
    # Configure Gemini
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY environment variable not set")
        return
    
    genai.configure(api_key=api_key)
    
    # Collect documentation
    print("📋 Collecting architecture documentation...")
    docs = collect_architecture_docs()
    
    # Prepare review prompt
    prompt = f"""
Please provide a critical, independent review of the KGAS architecture documentation below. 

Focus on these key areas:

1. **Technical Depth and Completeness**: Are the specifications sufficient for implementation? What critical details are missing?

2. **Implementation Feasibility**: Can developers actually build this system from the documentation provided? What gaps would prevent implementation?

3. **Architectural Consistency**: Are all components and patterns properly aligned? Do the different documents contradict each other?

4. **Documentation Quality and Clarity**: Is the documentation well-organized, clear, and easy to follow? Are there confusing or unclear sections?

5. **Missing Critical Elements**: What essential documentation, specifications, or architectural decisions are missing?

6. **Academic Research Suitability**: Does this architecture effectively serve academic research needs? Are there gaps in research-specific requirements?

Be critical and identify specific issues that could impact implementation or research utility. Provide actionable recommendations for improvement.

Focus particularly on any inconsistencies, missing implementation details, unclear specifications, or gaps that would prevent successful system implementation.

---

ARCHITECTURE DOCUMENTATION:

{docs}

---

Please provide a structured critical analysis with specific recommendations for improvement.
"""
    
    # Get Gemini review
    print("🤖 Requesting Gemini review...")
    try:
        model = genai.GenerativeModel('gemini-1.5-pro')
        response = model.generate_content(prompt)
        
        # Save results
        with open('architecture_review_results.md', 'w') as f:
            f.write("# KGAS Architecture Documentation - Critical Review\n\n")
            f.write("**Date**: 2025-07-22\n")
            f.write("**Reviewer**: Google Gemini 1.5 Pro\n\n")
            f.write(response.text)
        
        print("✅ Review completed!")
        print("📁 Results saved to: architecture_review_results.md")
        print("\n" + "="*60)
        print("CRITICAL REVIEW SUMMARY:")
        print("="*60)
        print(response.text[:1000] + "..." if len(response.text) > 1000 else response.text)
        
    except Exception as e:
        print(f"❌ Error during Gemini review: {e}")

if __name__ == "__main__":
    main()