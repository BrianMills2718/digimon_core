#!/usr/bin/env python3
"""
Run Gemini Review for Aspirational Architecture Documentation

This script reviews the target architecture documentation focusing on the design vision,
architectural decisions, and conceptual clarity - NOT implementation status.
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print("ERROR: GEMINI_API_KEY not found in environment variables")
    sys.exit(1)

genai.configure(api_key=api_key)

# Initialize model
model = genai.GenerativeModel('gemini-1.5-flash')


def collect_architecture_files() -> Dict[str, str]:
    """Collect architecture documentation files, excluding current implementation docs"""
    architecture_files = {}
    
    # First, collect the roadmap overview to provide phasing context
    roadmap_path = Path("docs/roadmap/ROADMAP_OVERVIEW.md")
    if roadmap_path.exists():
        try:
            content = roadmap_path.read_text(encoding='utf-8')
            architecture_files[str(roadmap_path)] = content
            print(f"Collected: {roadmap_path}")
        except Exception as e:
            print(f"Error reading {roadmap_path}: {e}")
    
    # Then collect architecture files
    base_path = Path("docs/architecture")
    
    if not base_path.exists():
        print(f"ERROR: Architecture directory not found: {base_path}")
        return architecture_files
    
    # Files to explicitly exclude (implementation-focused)
    exclude_files = {
        "CURRENT_ARCHITECTURE.md",
        "ARCHITECTURE_REVIEW_ACTION_PLAN.md",
        "ASPIRATIONAL_ARCHITECTURE_IMPROVEMENTS.md"
    }
    
    # Define file patterns to include - reduced set for token limits
    patterns = [
        "ARCHITECTURE_OVERVIEW.md",
        "ARCHITECTURE_PHASES.md",
        "GLOSSARY.md",
        "TOOL_GOVERNANCE.md",
        "data/CORE_SCHEMAS.md",
        "systems/COMPONENT_ARCHITECTURE_DETAILED.md",
        "concepts/uncertainty-architecture.md",
        "concepts/cross-modal-philosophy.md",
        "concepts/kgas-theoretical-foundation.md",
        "adrs/ADR-*.md"
    ]
    
    # Collect files
    for pattern in patterns:
        for file_path in base_path.glob(pattern):
            if file_path.is_file() and file_path.name not in exclude_files:
                relative_path = file_path.relative_to(Path("."))
                try:
                    content = file_path.read_text(encoding='utf-8')
                    architecture_files[str(relative_path)] = content
                    print(f"Collected: {relative_path}")
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
    
    return architecture_files


def create_review_prompt(files: Dict[str, str]) -> str:
    """Create the review prompt focused on aspirational architecture"""
    prompt = """You are a senior software architect reviewing the TARGET ARCHITECTURE documentation for the Knowledge Graph Analysis System (KGAS).

**CRITICAL INSTRUCTION**: This review should focus ONLY on evaluating the quality of the architectural vision, design decisions, and conceptual documentation. DO NOT evaluate implementation status, completion percentages, or whether features are built. Treat this as a pure architecture design review.

**IMPORTANT CONTEXT**: The ROADMAP_OVERVIEW.md file shows the PHASED IMPLEMENTATION approach. The architecture describes the full aspirational design, while the roadmap shows how it will be built incrementally with vertical slices (e.g., starting with 2 layers of uncertainty before expanding to all 4 layers). Please consider this phased approach when evaluating whether the architecture is achievable.

**SPECIFIC VERIFICATION REQUEST**: Please specifically check if the following items are present in the documentation:
1. GLOSSARY.md - A comprehensive glossary of technical terms
2. COMPONENT_ARCHITECTURE_DETAILED.md - Detailed component specifications with pseudo-code and algorithms
3. CORE_SCHEMAS.md - Concrete Pydantic schema examples for data types
4. Trade-off analyses in architecture documentation
5. Tool governance framework in TOOL_GOVERNANCE.md

If you find these items, please acknowledge their presence. If you cannot find them despite them being in the file list, please indicate this clearly.

# Review Criteria for Aspirational Architecture

## 1. Architectural Vision & Coherence (25%)
- Is the overall system vision clear and compelling?
- Do all components work together toward a unified goal?
- Are the architectural principles well-defined?
- Is there a clear value proposition?

## 2. Design Quality & Patterns (20%)
- Are established architectural patterns used appropriately?
- Is the system design modular and extensible?
- Are component boundaries well-defined?
- Does the design support the stated goals?

## 3. Technical Soundness (20%)
- Are the technical choices appropriate for the problem domain?
- Is the architecture feasible with current technology?
- Are performance and scalability considered in the design?
- Are there any fundamental technical flaws?

## 4. Conceptual Clarity (15%)
- Are complex concepts explained clearly?
- Is technical terminology used consistently?
- Are diagrams and examples helpful?
- Can a new team member understand the vision?

## 5. Decision Documentation (10%)
- Are architectural decisions well-justified?
- Are trade-offs clearly explained?
- Are alternatives considered?
- Is the rationale for choices clear?

## 6. Innovation & Research Value (10%)
- Does the architecture advance the field?
- Are novel approaches justified?
- Is the research contribution clear?
- Are theoretical foundations sound?

# Files to Review

"""
    
    # Add file contents
    for file_path, content in files.items():
        prompt += f"\n\n## File: {file_path}\n```markdown\n{content}\n```\n"
    
    prompt += """

# Review Output Format

Provide your review in the following format:

## Executive Summary
[2-3 paragraphs evaluating the overall architectural vision and documentation quality]

## Strengths of the Architecture
[What aspects of the target architecture are well-designed and clearly documented?]

### Strength 1: [Title]
- **Description**: [What's good about this]
- **Evidence**: [Where this is demonstrated]
- **Impact**: [Why this matters]

## Areas for Improvement
[What aspects of the architectural design or documentation need work?]

### Issue 1: [Title]
- **Location**: [Specific file and section]
- **Problem**: [What needs improvement]
- **Recommendation**: [Specific suggestion]
- **Priority**: [High/Medium/Low]

## Architectural Risks
[What risks exist in the proposed architecture?]

### Risk 1: [Title]
- **Description**: [Nature of the risk]
- **Likelihood**: [High/Medium/Low]
- **Impact**: [High/Medium/Low]
- **Mitigation**: [Suggested approach]

## Innovation Assessment
[How innovative is the proposed architecture?]

- **Novel Aspects**: [What's new or innovative]
- **Research Contribution**: [Academic/industry value]
- **Practical Viability**: [Can this be built?]

## Documentation Quality Score
- Vision Clarity: [X/10]
- Design Quality: [X/10]
- Technical Soundness: [X/10]
- Conceptual Clarity: [X/10]
- Decision Documentation: [X/10]
- Innovation Value: [X/10]
- **Overall: [X/10]**

## Specific Architectural Questions

1. **Cross-Modal Analysis**: Is the approach to cross-modal analysis (graph/table/vector) architecturally sound? Are the conversion mechanisms well-designed?

2. **Theory-Aware Design**: How well does the architecture integrate theoretical frameworks? Is the ontology integration practical?

3. **Uncertainty Architecture**: Is the 4-layer uncertainty model architecturally sound? Could it be simplified without losing value?

4. **Tool Ecosystem**: Is the 121-tool ecosystem a good architectural choice? What governance is proposed?

5. **Scalability Design**: How well does the architecture address scaling to millions of entities and relationships?

## Recommendations for Architecture Documentation

[Specific suggestions to improve the documentation of the aspirational architecture]

Remember: Focus on the DESIGN QUALITY, not implementation status. Evaluate this as if reviewing architecture documentation for a system that will be built in the future.
"""
    
    return prompt


def run_architecture_review():
    """Run the aspirational architecture review"""
    print("KGAS Aspirational Architecture Review")
    print("=" * 60)
    print(f"Start time: {datetime.now().isoformat()}")
    print("\nFocus: Target architecture design and documentation quality")
    print("NOT evaluating: Implementation status or completion\n")
    
    # Collect files
    print("Collecting architecture documentation files...")
    files = collect_architecture_files()
    
    if not files:
        print("ERROR: No architecture files found")
        return
    
    print(f"\nCollected {len(files)} files for review")
    print("\nFiles included:")
    for file_path in sorted(files.keys()):
        print(f"  - {file_path}")
    
    # Create prompt
    print("\nGenerating review prompt...")
    prompt = create_review_prompt(files)
    
    # Calculate token estimate
    prompt_length = len(prompt)
    print(f"Prompt length: {prompt_length:,} characters")
    
    # Run review
    print("\nSending to Gemini for architecture design review...")
    print("This may take a few minutes due to the comprehensive nature of the review...")
    
    try:
        start_time = time.time()
        response = model.generate_content(prompt)
        end_time = time.time()
        
        print(f"\nReview completed in {end_time - start_time:.1f} seconds")
        
        # Save results
        output_file = "gemini-review-tool/aspirational-architecture-review-results.md"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w') as f:
            f.write(f"# KGAS Aspirational Architecture Review\n\n")
            f.write(f"**Review Date**: {datetime.now().isoformat()}\n")
            f.write(f"**Review Focus**: Target Architecture Design Quality\n")
            f.write(f"**Files Reviewed**: {len(files)}\n")
            f.write(f"**Review Tool**: Gemini 1.5 Flash\n\n")
            f.write("---\n\n")
            f.write(response.text)
        
        print(f"\nReview saved to: {output_file}")
        
        # Also save a summary
        summary_file = "gemini-review-tool/aspirational-architecture-review-summary.json"
        summary = {
            "review_date": datetime.now().isoformat(),
            "review_type": "aspirational_architecture",
            "files_reviewed": len(files),
            "file_list": sorted(files.keys()),
            "review_time_seconds": end_time - start_time,
            "output_file": output_file
        }
        
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"Summary saved to: {summary_file}")
        
    except Exception as e:
        print(f"\nERROR during review: {e}")
        print("\nTroubleshooting:")
        print("1. Check that GEMINI_API_KEY is set in .env")
        print("2. Verify API key is valid")
        print("3. Check internet connection")
        print("4. Try reducing the number of files if hitting token limits")
        return
    
    print("\n" + "=" * 60)
    print("Aspirational architecture review complete!")
    print(f"End time: {datetime.now().isoformat()}")


if __name__ == "__main__":
    # Change to project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    run_architecture_review()