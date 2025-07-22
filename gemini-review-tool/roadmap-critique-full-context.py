#!/usr/bin/env python3
"""
Run Gemini Review for Roadmap Critique with FULL Context

This script reviews the ROADMAP_OVERVIEW.md against the architecture documentation
INCLUDING all detailed phase documentation to provide complete context.
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
    """Collect architecture files, roadmap, AND detailed phase documentation"""
    files = {}
    
    # First, collect the roadmap overview
    roadmap_path = Path("docs/roadmap/ROADMAP_OVERVIEW.md")
    if roadmap_path.exists():
        try:
            content = roadmap_path.read_text(encoding='utf-8')
            files[str(roadmap_path)] = content
            print(f"Collected: {roadmap_path}")
        except Exception as e:
            print(f"Error reading {roadmap_path}: {e}")
    else:
        print(f"ERROR: Roadmap file not found: {roadmap_path}")
        return files
    
    # Collect detailed phase documentation
    phase_files = [
        "docs/roadmap/phases/phase-7/phase-7-service-architecture-completion.md",
        "docs/roadmap/phases/phase-8/phase-8-strategic-external-integrations.md",
        "docs/roadmap/analysis/dependencies.md",
        "docs/roadmap/initiatives/tooling/tool-implementation-status.md",
        "docs/roadmap/initiatives/tooling/tool-count-methodology.md"
    ]
    
    for file_name in phase_files:
        file_path = Path(file_name)
        if file_path.exists():
            try:
                content = file_path.read_text(encoding='utf-8')
                files[str(file_path)] = content
                print(f"Collected: {file_path}")
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
    
    # Then collect key architecture files for context
    base_path = Path("docs/architecture")
    
    if not base_path.exists():
        print(f"ERROR: Architecture directory not found: {base_path}")
        return files
    
    # Key architecture files needed for roadmap critique
    key_files = [
        "ARCHITECTURE_OVERVIEW.md",
        "ARCHITECTURE_PHASES.md",
        "TOOL_GOVERNANCE.md",
        "SCALABILITY_STRATEGY.md",
        "concepts/uncertainty-architecture.md",
        "concepts/cross-modal-philosophy.md",
        "systems/COMPONENT_ARCHITECTURE_DETAILED.md",
        "adrs/ADR-001-Phase-Interface-Design.md",
        "adrs/ADR-003-Vector-Store-Consolidation.md",
        "adrs/ADR-005-buy-vs-build-strategy.md"
    ]
    
    # Collect architecture files
    for file_name in key_files:
        file_path = base_path / file_name
        if file_path.exists():
            try:
                content = file_path.read_text(encoding='utf-8')
                relative_path = file_path.relative_to(Path("."))
                files[str(relative_path)] = content
                print(f"Collected: {relative_path}")
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
    
    return files


def create_roadmap_critique_prompt(files: Dict[str, str]) -> str:
    """Create the prompt for roadmap critique with full context"""
    prompt = """You are a senior software architect and project manager reviewing the ROADMAP_OVERVIEW.md against the target architecture documentation for the Knowledge Graph Analysis System (KGAS).

**CRITICAL INSTRUCTION**: Your task is to critique the ROADMAP document's quality, alignment with architecture, feasibility, and completeness. Focus on whether the roadmap effectively translates the architectural vision into an actionable implementation plan.

**IMPORTANT CONTEXT**: 
- The architecture documentation describes the full aspirational system design
- The roadmap should show how to incrementally build toward that vision
- KGAS uses a phased approach with vertical slices (implementing subsets of features fully rather than all features partially)
- DETAILED PHASE DOCUMENTATION IS PROVIDED - Please read the full Phase 7 and Phase 8 detailed plans

**SPECIFIC NOTE**: The ROADMAP_OVERVIEW.md now includes references to detailed phase documentation. The detailed plans for Phase 7 and Phase 8 are included in this review. Please acknowledge that you have seen these detailed documents.

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

Provide your critique in the following format:

## Executive Summary
[2-3 paragraphs evaluating how well the roadmap translates the architecture into an implementation plan]

## Documents Reviewed
[List the key documents you found in this review, especially Phase 7 and Phase 8 detailed plans]

## Strengths of the Roadmap

### Strength 1: [Title]
- **Description**: [What's good about this aspect]
- **Evidence**: [Specific examples from the roadmap and detailed phase documents]
- **Impact**: [Why this matters for project success]

## Critical Issues (if any remain)

### Issue 1: [Title] 
- **Severity**: [High/Medium/Low]
- **Description**: [What's wrong or missing]
- **Architecture Impact**: [How this affects achieving the target architecture]
- **Recommendation**: [Specific improvement suggestion]

## Alignment Analysis

### Well-Aligned Areas
[List aspects where roadmap and architecture align well]

### Areas Needing Attention
[List any remaining areas where roadmap could be improved]

## Implementation Assessment

### Phase 7 Analysis
- **Documentation Quality**: [Assessment of the detailed Phase 7 plan]
- **Sub-phase Breakdown**: [Quality of the 4 sub-phases]
- **Timeline Realism**: [Are the 6-8 weeks realistic?]
- **Dependencies**: [Are they clearly defined?]

### Phase 8 Analysis
- **Documentation Quality**: [Assessment of the detailed Phase 8 plan]
- **Sub-phase Breakdown**: [Quality of the 5 sub-phases]
- **Timeline Realism**: [Are the 12-16 weeks realistic?]
- **ROI Analysis**: [Is the 163-520% ROI justified?]

### Tool Rollout Strategy
- **121 Tool Plan**: [Assessment of how tools are distributed across phases]
- **Tool Dependencies**: [Are tool dependencies well documented?]

### Uncertainty Model Implementation
- **4-Layer Plan**: [Assessment of the phased uncertainty implementation]
- **Layer Distribution**: [Is the layer-by-layer approach clear?]

## Roadmap Quality Score (Updated)
- Architecture Alignment: [X/10]
- Implementation Feasibility: [X/10]
- Completeness: [X/10]
- Risk Management: [X/10]
- Success Metrics: [X/10]
- Documentation Quality: [X/10]
- **Overall: [X/10]**

## Recommendations for Further Improvement
[Any remaining suggestions to make the roadmap even better]

Remember: Acknowledge the detailed phase documentation that has been provided and update your assessment accordingly.
"""
    
    return prompt


def run_roadmap_critique():
    """Run the roadmap critique review with full context"""
    print("KGAS Roadmap Critique - FULL CONTEXT VERSION")
    print("=" * 60)
    print(f"Start time: {datetime.now().isoformat()}")
    print("\nFocus: Evaluating roadmap with ALL detailed phase documentation")
    print("Including: Phase 7/8 detailed plans, tool rollout, dependencies\n")
    
    # Collect files
    print("Collecting roadmap, architecture, and detailed phase files...")
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
    
    if prompt_length > 800000:  # Roughly 200k tokens
        print("\nWARNING: Prompt may be too large. Consider reducing file count.")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return
    
    # Run review
    print("\nSending to Gemini for comprehensive roadmap critique...")
    print("This may take a few minutes due to the comprehensive nature of the review...")
    
    try:
        start_time = time.time()
        response = model.generate_content(prompt)
        end_time = time.time()
        
        print(f"\nCritique completed in {end_time - start_time:.1f} seconds")
        
        # Save results
        output_file = "gemini-review-tool/roadmap-critique-full-context-results.md"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w') as f:
            f.write(f"# KGAS Roadmap Critique - Full Context\n\n")
            f.write(f"**Review Date**: {datetime.now().isoformat()}\n")
            f.write(f"**Review Focus**: Roadmap vs Architecture Alignment (with detailed phase docs)\n")
            f.write(f"**Files Reviewed**: {len(files)}\n")
            f.write(f"**Review Tool**: Gemini 1.5 Flash\n\n")
            f.write("---\n\n")
            f.write(response.text)
        
        print(f"\nCritique saved to: {output_file}")
        
        # Also save a summary
        summary_file = "gemini-review-tool/roadmap-critique-full-context-summary.json"
        summary = {
            "review_date": datetime.now().isoformat(),
            "review_type": "roadmap_critique_full_context",
            "files_reviewed": len(files),
            "file_list": sorted(files.keys()),
            "review_time_seconds": end_time - start_time,
            "output_file": output_file,
            "includes_detailed_phases": True
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
    print("Comprehensive roadmap critique complete!")
    print(f"End time: {datetime.now().isoformat()}")


if __name__ == "__main__":
    # Change to project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    run_roadmap_critique()