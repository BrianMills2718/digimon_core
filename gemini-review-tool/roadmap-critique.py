#!/usr/bin/env python3
"""
Run Gemini Review for Roadmap Critique

This script reviews the ROADMAP_OVERVIEW.md against the architecture documentation
to assess alignment, feasibility, and completeness of the implementation plan.
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
    """Collect architecture files and roadmap for review"""
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
        "adrs/ADR-003-Vector-Store-Consolidation.md"
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
    """Create the prompt for roadmap critique"""
    prompt = """You are a senior software architect and project manager reviewing the ROADMAP_OVERVIEW.md against the target architecture documentation for the Knowledge Graph Analysis System (KGAS).

**CRITICAL INSTRUCTION**: Your task is to critique the ROADMAP document's quality, alignment with architecture, feasibility, and completeness. Focus on whether the roadmap effectively translates the architectural vision into an actionable implementation plan.

**CONTEXT**: 
- The architecture documentation describes the full aspirational system design
- The roadmap should show how to incrementally build toward that vision
- KGAS uses a phased approach with vertical slices (implementing subsets of features fully rather than all features partially)

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

## Strengths of the Roadmap

### Strength 1: [Title]
- **Description**: [What's good about this aspect]
- **Evidence**: [Specific examples from the roadmap]
- **Impact**: [Why this matters for project success]

## Critical Issues

### Issue 1: [Title]
- **Severity**: [High/Medium/Low]
- **Description**: [What's wrong or missing]
- **Architecture Impact**: [How this affects achieving the target architecture]
- **Recommendation**: [Specific improvement suggestion]

## Alignment Analysis

### Well-Aligned Areas
[List aspects where roadmap and architecture align well]

### Misalignment Concerns
[List areas where roadmap diverges from or inadequately addresses architecture]

## Implementation Risks

### Risk 1: [Title]
- **Description**: [Nature of the risk]
- **Probability**: [High/Medium/Low]
- **Impact**: [High/Medium/Low]
- **Mitigation**: [Suggested approach]

## Missing Elements
[What architectural components or features are not adequately addressed in the roadmap?]

## Phase-Specific Critique

### Phase 1 (MVP) Assessment
- **Scope appropriateness**: [Is it truly an MVP?]
- **Foundation quality**: [Does it set up future phases well?]
- **Risk level**: [Are the highest risks addressed early?]

### Phase 2 (Enhanced Analysis) Assessment
- **Building on Phase 1**: [Logical progression?]
- **Value delivery**: [Clear user value?]
- **Technical dependencies**: [Properly sequenced?]

### Phase 3 (Theory Integration) Assessment
- **Complexity management**: [Is this achievable?]
- **Prerequisites**: [Are foundations in place?]
- **Integration approach**: [Well-planned?]

### Phase 4 (Scale & Production) Assessment
- **Readiness**: [Will previous phases prepare for this?]
- **Scope creep**: [Is this phase overloaded?]
- **Production readiness**: [Adequate preparation?]

## Recommendations for Roadmap Improvement

1. **Immediate fixes**: [What should be changed right away]
2. **Structural improvements**: [How to better organize the roadmap]
3. **Additional details needed**: [What information is missing]
4. **Risk mitigation strategies**: [How to address identified risks]

## Roadmap Quality Score
- Architecture Alignment: [X/10]
- Implementation Feasibility: [X/10]
- Completeness: [X/10]
- Risk Management: [X/10]
- Success Metrics: [X/10]
- Documentation Quality: [X/10]
- **Overall: [X/10]**

## Critical Questions

1. **Tool Rollout Strategy**: How does the phased rollout of 121 tools ensure each phase has the tools it needs? Is the distribution logical?

2. **Uncertainty Model Implementation**: How does the 4-layer uncertainty model get implemented across phases? Is the progression clear?

3. **Cross-Modal Features**: When and how do the three modes (graph/table/vector) become available? Is this sequencing optimal?

4. **Theory Integration Timing**: Is Phase 3 the right time for theory integration, or should some aspects come earlier?

5. **Scalability Preparation**: Does the roadmap adequately prepare for the scalability requirements outlined in the architecture?

Remember: Focus on the ROADMAP's effectiveness as an implementation plan, not on the architecture itself.
"""
    
    return prompt


def run_roadmap_critique():
    """Run the roadmap critique review"""
    print("KGAS Roadmap Critique")
    print("=" * 60)
    print(f"Start time: {datetime.now().isoformat()}")
    print("\nFocus: Evaluating roadmap against target architecture")
    print("Assessing: Alignment, feasibility, completeness\n")
    
    # Collect files
    print("Collecting roadmap and architecture files...")
    files = collect_review_files()
    
    if not files:
        print("ERROR: No files found for review")
        return
    
    print(f"\nCollected {len(files)} files for review")
    print("\nFiles included:")
    for file_path in sorted(files.keys()):
        print(f"  - {file_path}")
    
    # Create prompt
    print("\nGenerating critique prompt...")
    prompt = create_roadmap_critique_prompt(files)
    
    # Calculate token estimate
    prompt_length = len(prompt)
    print(f"Prompt length: {prompt_length:,} characters")
    
    # Run review
    print("\nSending to Gemini for roadmap critique...")
    print("This may take a few minutes due to the comprehensive nature of the review...")
    
    try:
        start_time = time.time()
        response = model.generate_content(prompt)
        end_time = time.time()
        
        print(f"\nCritique completed in {end_time - start_time:.1f} seconds")
        
        # Save results
        output_file = "gemini-review-tool/roadmap-critique-results.md"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w') as f:
            f.write(f"# KGAS Roadmap Critique\n\n")
            f.write(f"**Review Date**: {datetime.now().isoformat()}\n")
            f.write(f"**Review Focus**: Roadmap vs Architecture Alignment\n")
            f.write(f"**Files Reviewed**: {len(files)}\n")
            f.write(f"**Review Tool**: Gemini 1.5 Flash\n\n")
            f.write("---\n\n")
            f.write(response.text)
        
        print(f"\nCritique saved to: {output_file}")
        
        # Also save a summary
        summary_file = "gemini-review-tool/roadmap-critique-summary.json"
        summary = {
            "review_date": datetime.now().isoformat(),
            "review_type": "roadmap_critique",
            "files_reviewed": len(files),
            "file_list": sorted(files.keys()),
            "review_time_seconds": end_time - start_time,
            "output_file": output_file
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
        print("4. Try reducing the number of files if hitting token limits")
        return
    
    print("\n" + "=" * 60)
    print("Roadmap critique complete!")
    print(f"End time: {datetime.now().isoformat()}")


if __name__ == "__main__":
    # Change to project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    run_roadmap_critique()