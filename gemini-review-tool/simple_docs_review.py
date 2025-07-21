#!/usr/bin/env python3
"""
Simple docs-only review using Gemini API directly
"""

import os
import google.generativeai as genai
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def collect_documentation():
    """Collect all documentation files"""
    docs = []
    
    # Main documentation
    files_to_include = [
        "CLAUDE.md",
        "docs/planning/roadmap_overview_planning.md",
        "docs/architecture/adrs/ADR-001-Phase-Interface-Design.md",
        "docs/architecture/adrs/ADR-002-Pipeline-Orchestrator-Architecture.md", 
        "docs/architecture/adrs/ADR-003-Vector-Store-Consolidation.md",
        "docs/architecture/adrs/ADR-004-Normative-Confidence-Score-Ontology.md",
        "docs/architecture/architecture_overview.md",
        "docs/architecture/cross-modal-analysis.md",
        "docs/architecture/project-structure.md",
        "docs/architecture/LIMITATIONS.md",
        "README.md"
    ]
    
    for file_path in files_to_include:
        full_path = Path(file_path)
        if full_path.exists():
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                docs.append(f"=== {file_path} ===\n{content}\n\n")
    
    return "".join(docs)

def main():
    # Configure Gemini
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY environment variable not set")
        return
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # Collect documentation
    print("📚 Collecting documentation...")
    docs_content = collect_documentation()
    
    # Review prompt
    prompt = f"""
You are conducting an expert architectural and roadmap review for KGAS (Knowledge Graph Analysis System), an academic research tool. You have been provided with ONLY the documentation - no source code.

Based solely on the documentation provided, please provide a comprehensive critique focusing on:

## ARCHITECTURE REVIEW
1. **System Coherence**: Does the overall architecture make sense as a unified system?
2. **Academic Appropriateness**: Is this architecture suitable for academic research workflows?
3. **Cross-Modal Vision**: Can the architecture realistically support graph↔table↔vector analysis?
4. **Technical Soundness**: Are there obvious architectural flaws or bottlenecks?
5. **Theory Integration**: How well does the LLM-ontology system fit with the overall design?

## ROADMAP ANALYSIS
1. **Timeline Realism**: Is the 2-week MVRT (Minimum Viable Research Tool) timeline achievable?
2. **Decision Quality**: Are the 5 roadmap decisions (LLM-ontology, tool strategy, testing, cross-modal UI, academic focus) well-reasoned?
3. **Priority Logic**: Do the tool priorities and implementation phases make sense?
4. **Risk Assessment**: Are the identified risks adequate and are mitigations realistic?
5. **Academic Value**: Does the roadmap appropriately prioritize research value?

## INTEGRATION CONSISTENCY
1. **ADR Alignment**: Do the Architecture Decision Records align with roadmap decisions?
2. **Documentation Philosophy**: Is the separation between architecture (target) and planning (current state) appropriate?
3. **Implementation Gaps**: Are there gaps between architectural vision and implementation planning?

## SPECIFIC CONCERNS
Please pay special attention to:
- The multi-layer agent interface (Layer 1: Agent, Layer 2: Simple UI, Layer 3: Advanced UI)
- The LLM-ontology integration using Gemini 2.5 Flash
- The cross-modal orchestration complexity
- The 2-week timeline given the architectural complexity
- The risk-based testing strategy

## DELIVERABLES REQUIRED
1. **Executive Summary** (2-3 paragraphs highlighting key findings)
2. **Architectural Strengths and Weaknesses**
3. **Roadmap Feasibility Assessment**
4. **Critical Issues** (must-address problems)
5. **Specific Recommendations** for improvements

Be constructively critical. This is an academic project with real constraints, but architectural soundness and roadmap realism are crucial for success.

=== DOCUMENTATION CONTENT ===
{docs_content}
"""
    
    # Generate review
    print("🤖 Generating Gemini review...")
    try:
        response = model.generate_content(prompt)
        
        # Save to file
        with open('gemini-review.md', 'w', encoding='utf-8') as f:
            f.write("# Gemini Architecture & Roadmap Review\n\n")
            f.write(response.text)
        
        print("✅ Review completed and saved to gemini-review.md")
        print("\n" + "="*50)
        print(response.text)
        
    except Exception as e:
        print(f"❌ Error generating review: {e}")

if __name__ == "__main__":
    main()