#!/usr/bin/env python3
"""
Run Gemini Review for Roadmap Critique with COMPLETE Context

This script reviews the ROADMAP_OVERVIEW.md against the architecture documentation
INCLUDING all detailed phase documentation AND the newly created documents.
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


def collect_review_files() -> Dict[str, str]:
    """Collect architecture files, roadmap, detailed phases, AND new documents"""
    files = {}
    
    # Core roadmap files
    core_files = [
        "docs/roadmap/ROADMAP_OVERVIEW.md",
        "docs/roadmap/phases/phase-7/phase-7-service-architecture-completion.md",
        "docs/roadmap/phases/phase-8/phase-8-strategic-external-integrations.md",
        "docs/roadmap/analysis/dependencies.md",
        "docs/roadmap/initiatives/tooling/tool-implementation-status.md",
        "docs/roadmap/initiatives/tooling/tool-count-methodology.md",
        # NEW DOCUMENTS
        "docs/roadmap/initiatives/tooling/tool-rollout-timeline.md",
        "docs/roadmap/initiatives/uncertainty-implementation-plan.md",
        "docs/development/testing/integration-testing-strategy.md"
    ]
    
    # Collect roadmap and new documents
    for file_name in core_files:
        file_path = Path(file_name)
        if file_path.exists():
            try:
                content = file_path.read_text(encoding='utf-8')
                files[str(file_path)] = content
                print(f"Collected: {file_path}")
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
        else:
            print(f"WARNING: File not found: {file_path}")
    
    # Key architecture files for context
    arch_files = [
        "docs/architecture/ARCHITECTURE_OVERVIEW.md",
        "docs/architecture/ARCHITECTURE_PHASES.md",
        "docs/architecture/TOOL_GOVERNANCE.md",
        "docs/architecture/SCALABILITY_STRATEGY.md",
        "docs/architecture/concepts/uncertainty-architecture.md",
        "docs/architecture/specifications/compatibility-matrix.md",  # This has tool dependencies!
        "docs/architecture/systems/COMPONENT_ARCHITECTURE_DETAILED.md",
        "docs/architecture/adrs/ADR-001-Phase-Interface-Design.md",
        "docs/architecture/adrs/ADR-003-Vector-Store-Consolidation.md",
        "docs/architecture/adrs/ADR-004-Normative-Confidence-Score-Ontology.md",
        "docs/architecture/adrs/ADR-005-buy-vs-build-strategy.md"
    ]
    
    # Collect architecture files
    for file_name in arch_files:
        file_path = Path(file_name)
        if file_path.exists():
            try:
                content = file_path.read_text(encoding='utf-8')
                files[str(file_path)] = content
                print(f"Collected: {file_path}")
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
    
    return files


def create_roadmap_critique_prompt(files: Dict[str, str]) -> str:
    """Create the prompt for roadmap critique with complete context"""
    prompt = """You are a senior software architect and project manager reviewing the ROADMAP_OVERVIEW.md against the target architecture documentation for the Knowledge Graph Analysis System (KGAS).

**CRITICAL INSTRUCTION**: Your task is to critique the ROADMAP document's quality, alignment with architecture, feasibility, and completeness. Focus on whether the roadmap effectively translates the architectural vision into an actionable implementation plan.

**IMPORTANT CONTEXT**: 
- The architecture documentation describes the full aspirational system design
- The roadmap should show how to incrementally build toward that vision
- KGAS uses a phased approach with vertical slices (implementing subsets of features fully rather than all features partially)

**NEW DOCUMENTS PROVIDED**: Please specifically acknowledge these new documents:
1. **tool-rollout-timeline.md** - Detailed 121-tool implementation timeline with dependencies
2. **integration-testing-strategy.md** - Comprehensive testing strategy with TDD emphasis
3. **uncertainty-implementation-plan.md** - Layer-by-layer uncertainty implementation details
4. **compatibility-matrix.md** - Complete tool input/output dependencies and chains

# Review Criteria for Roadmap Critique

## 1. Architecture Alignment (25%)
- Does the roadmap accurately reflect the architecture's goals and principles?
- Are all major architectural components addressed in the roadmap?
- Is the phasing consistent with architectural dependencies?
- Are architectural trade-offs properly considered in implementation order?

## 2. Implementation Feasibility (20%)
- Are the phases realistically scoped?
- Do timelines seem achievable given the complexity?
- Are dependencies between phases properly managed?
- Is the vertical slice approach effectively applied?

## 3. Completeness & Coverage (20%)
- Does the roadmap cover all aspects of the architecture?
- Are there missing components or features?
- Is the path from current state to target architecture clear?
- Are all 121 tools accounted for in the phases?

## 4. Risk Management (15%)
- Are technical risks identified and addressed?
- Is there appropriate de-risking in early phases?
- Are there contingency plans for major uncertainties?
- Is the most risky/complex work appropriately scheduled?

## 5. Success Metrics (10%)
- Are completion criteria clear and measurable?
- Can progress be objectively tracked?
- Are there appropriate milestones and checkpoints?
- Is there a definition of "done" for each phase?

## 6. Documentation Quality (10%)
- Is the roadmap clear and well-structured?
- Are decisions and rationales explained?
- Is it usable as a project management tool?
- Can new team members understand the plan?

# Files to Review

"""
    
    # Add file contents
    for file_path, content in files.items():
        prompt += f"\n\n## File: {file_path}\n```markdown\n{content}\n```\n"
    
    prompt += """

# Review Output Format

## Executive Summary
[2-3 paragraphs evaluating how well the roadmap translates the architecture into an implementation plan]

## Documents Reviewed
[List ALL key documents you found, especially the NEW ones: tool-rollout-timeline.md, integration-testing-strategy.md, uncertainty-implementation-plan.md, compatibility-matrix.md]

## Strengths of the Roadmap

### Strength 1: [Title]
- **Description**: [What's good about this aspect]
- **Evidence**: [Specific examples from the roadmap and detailed documents]
- **Impact**: [Why this matters for project success]

## Improvements Since Last Review
[What new documents or changes have addressed previous concerns?]

## Remaining Issues (if any)

### Issue 1: [Title] 
- **Severity**: [High/Medium/Low]
- **Description**: [What's wrong or missing]
- **Architecture Impact**: [How this affects achieving the target architecture]
- **Recommendation**: [Specific improvement suggestion]

## Tool Implementation Assessment
- **121 Tool Rollout**: [Assessment of tool-rollout-timeline.md]
- **Tool Dependencies**: [Assessment of compatibility-matrix.md]
- **Integration Testing**: [Assessment of integration-testing-strategy.md]

## Uncertainty Implementation Assessment
- **4-Layer Plan**: [Assessment of uncertainty-implementation-plan.md]
- **Implementation Timeline**: [Are the timelines realistic?]
- **TDD Approach**: [Is the test-driven approach well integrated?]

## Roadmap Quality Score (Final)
- Architecture Alignment: [X/10]
- Implementation Feasibility: [X/10]
- Completeness: [X/10]
- Risk Management: [X/10]
- Success Metrics: [X/10]
- Documentation Quality: [X/10]
- **Overall: [X/10]**

## Final Recommendations
[Any remaining suggestions to perfect the roadmap]

Remember: Acknowledge ALL the new documents that have been provided and update your assessment based on their content.
"""
    
    return prompt


def run_roadmap_critique():
    """Run the complete roadmap critique review"""
    print("KGAS Roadmap Critique - COMPLETE DOCUMENTATION")
    print("=" * 60)
    print(f"Start time: {datetime.now().isoformat()}")
    print("\nFocus: Final evaluation with ALL documentation")
    print("Including: New rollout timeline, testing strategy, uncertainty plan\n")
    
    # Collect files
    print("Collecting all documentation files...")
    files = collect_review_files()
    
    if not files:
        print("ERROR: No files found for review")
        return
    
    print(f"\nCollected {len(files)} files for review")
    print("\nFiles included:")
    for file_path in sorted(files.keys()):
        print(f"  - {file_path}")
    
    # Create prompt
    print("\nGenerating comprehensive critique prompt...")
    prompt = create_roadmap_critique_prompt(files)
    
    # Calculate token estimate
    prompt_length = len(prompt)
    print(f"Prompt length: {prompt_length:,} characters")
    
    if prompt_length > 900000:  # Roughly 225k tokens
        print("\nWARNING: Prompt is very large. Splitting review...")
        # Could implement splitting logic here if needed
    
    # Run review
    print("\nSending to Gemini for final roadmap critique...")
    print("This may take a few minutes due to the comprehensive documentation...")
    
    try:
        start_time = time.time()
        response = model.generate_content(prompt)
        end_time = time.time()
        
        print(f"\nCritique completed in {end_time - start_time:.1f} seconds")
        
        # Save results
        output_file = "gemini-review-tool/roadmap-critique-complete-results.md"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w') as f:
            f.write(f"# KGAS Roadmap Critique - Complete Documentation\n\n")
            f.write(f"**Review Date**: {datetime.now().isoformat()}\n")
            f.write(f"**Review Focus**: Final roadmap evaluation with all documentation\n")
            f.write(f"**Files Reviewed**: {len(files)}\n")
            f.write(f"**Review Tool**: Gemini 1.5 Flash\n\n")
            f.write("---\n\n")
            f.write(response.text)
        
        print(f"\nCritique saved to: {output_file}")
        
        # Also save a summary
        summary_file = "gemini-review-tool/roadmap-critique-complete-summary.json"
        summary = {
            "review_date": datetime.now().isoformat(),
            "review_type": "roadmap_critique_complete",
            "files_reviewed": len(files),
            "file_list": sorted(files.keys()),
            "review_time_seconds": end_time - start_time,
            "output_file": output_file,
            "includes_new_documents": True
        }
        
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"Summary saved to: {summary_file}")
        
    except Exception as e:
        print(f"\nERROR during critique: {e}")
        print("\nTroubleshooting:")
        print("1. Check that GEMINI_API_KEY is set in .env")
        print("2. Verify API key is valid")
        print("3. Check internet connection")
        print("4. File size may be too large - consider splitting the review")
        return
    
    print("\n" + "=" * 60)
    print("Complete roadmap critique finished!")
    print(f"End time: {datetime.now().isoformat()}")


if __name__ == "__main__":
    # Change to project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    run_roadmap_critique()