#!/usr/bin/env python3
"""
Run Gemini Review for NEW Improvements Only
Focus on documents created/updated after last review
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


def collect_improvement_files() -> Dict[str, str]:
    """Collect only NEW/UPDATED documents since last review"""
    files = {}
    
    # New documents created
    new_files = [
        "docs/roadmap/initiatives/standardized-success-metrics.md",
        "docs/roadmap/initiatives/risk-management-framework.md",
        # Updated with significant changes
        "docs/roadmap/initiatives/tooling/tool-rollout-timeline.md",
        "docs/development/testing/integration-testing-strategy.md",
        "docs/roadmap/initiatives/uncertainty-implementation-plan.md",
        "docs/architecture/specifications/compatibility-matrix.md"
    ]
    
    # Reference files for context
    context_files = [
        "docs/roadmap/ROADMAP_OVERVIEW.md",
        "docs/architecture/ARCHITECTURE_OVERVIEW.md"
    ]
    
    all_files = new_files + context_files
    
    for file_name in all_files:
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
    
    return files


def create_improvements_prompt(files: Dict[str, str]) -> str:
    """Create focused prompt for reviewing improvements"""
    prompt = """You are a senior software architect reviewing IMPROVEMENTS made to the KGAS roadmap based on your previous feedback.

**CONTEXT**: You previously reviewed the KGAS roadmap and gave it a score of 7.8/10, with these main areas for improvement:
1. Inconsistent Success Metrics Across Phases (affecting score by -1.0)
2. Risk Management Needs Refinement in Later Phases (affecting score by -0.7)
3. Tool Rollout Timeline needs more granular breakdowns (affecting score by -0.3)
4. Testing Acceptance Criteria need specific thresholds (affecting score by -0.2)
5. Uncertainty Implementation needs concrete metrics (affecting score by -0.2)
6. Schema Review for consistency and redundancy (affecting score by -0.1)

**YOUR TASK**: Review the NEW/UPDATED documents provided and assess whether they adequately address your previous concerns.

# Documents Provided

## NEW Documents Created:
- standardized-success-metrics.md
- risk-management-framework.md

## SIGNIFICANTLY Updated Documents:
- tool-rollout-timeline.md (added weekly breakdowns)
- integration-testing-strategy.md (added acceptance criteria)
- uncertainty-implementation-plan.md (added concrete metrics)
- compatibility-matrix.md (enhanced schema validation)

## Context Documents:
- ROADMAP_OVERVIEW.md
- ARCHITECTURE_OVERVIEW.md

# Review Focus Areas

## 1. Success Metrics Framework
**Previous Issue**: Inconsistent success metrics, lack of SMART goals
**Expected Improvement**: Standardized metrics with clear thresholds
**Files to Check**: standardized-success-metrics.md

## 2. Risk Management Framework
**Previous Issue**: Insufficient risk detail for Phases 7-8
**Expected Improvement**: Detailed risk matrices, mitigation plans
**Files to Check**: risk-management-framework.md

## 3. Tool Rollout Granularity
**Previous Issue**: Lack of weekly task breakdowns
**Expected Improvement**: Day-by-day implementation plan
**Files to Check**: tool-rollout-timeline.md

## 4. Testing Acceptance Criteria
**Previous Issue**: No specific pass/fail thresholds
**Expected Improvement**: Concrete acceptance criteria
**Files to Check**: integration-testing-strategy.md

## 5. Uncertainty Layer Metrics
**Previous Issue**: Vague success criteria for layers
**Expected Improvement**: Specific performance targets
**Files to Check**: uncertainty-implementation-plan.md

## 6. Schema Consistency
**Previous Issue**: Potential redundancy in schemas
**Expected Improvement**: Clear schema definitions
**Files to Check**: compatibility-matrix.md

# Files Content

"""
    
    # Add file contents
    for file_path, content in files.items():
        prompt += f"\n\n## File: {file_path}\n```markdown\n{content}\n```\n"
    
    prompt += """

# Review Output Format

## Executive Summary
[Assess whether the improvements adequately address the previous concerns]

## Improvement Assessment

### 1. Success Metrics Framework
- **Addressed**: [Yes/Partially/No]
- **Quality**: [Excellent/Good/Adequate/Poor]
- **Specific Improvements**: [What was added]
- **Remaining Gaps**: [If any]

### 2. Risk Management Framework
- **Addressed**: [Yes/Partially/No]
- **Quality**: [Excellent/Good/Adequate/Poor]
- **Specific Improvements**: [What was added]
- **Remaining Gaps**: [If any]

### 3. Tool Rollout Granularity
- **Addressed**: [Yes/Partially/No]
- **Quality**: [Excellent/Good/Adequate/Poor]
- **Specific Improvements**: [What was added]
- **Remaining Gaps**: [If any]

### 4. Testing Acceptance Criteria
- **Addressed**: [Yes/Partially/No]
- **Quality**: [Excellent/Good/Adequate/Poor]
- **Specific Improvements**: [What was added]
- **Remaining Gaps**: [If any]

### 5. Uncertainty Layer Metrics
- **Addressed**: [Yes/Partially/No]
- **Quality**: [Excellent/Good/Adequate/Poor]
- **Specific Improvements**: [What was added]
- **Remaining Gaps**: [If any]

### 6. Schema Consistency
- **Addressed**: [Yes/Partially/No]
- **Quality**: [Excellent/Good/Adequate/Poor]
- **Specific Improvements**: [What was added]
- **Remaining Gaps**: [If any]

## Updated Roadmap Quality Score
Based on the improvements:
- Architecture Alignment: [X/10] (was 9/10)
- Implementation Feasibility: [X/10] (was 7/10)
- Completeness: [X/10] (was 8/10)
- Risk Management: [X/10] (was 7/10)
- Success Metrics: [X/10] (was 6/10)
- Documentation Quality: [X/10] (was 9/10)
- **Overall: [X/10]** (was 7.8/10)

## Final Recommendations
[Any remaining improvements needed to achieve 8.5+/10]
"""
    
    return prompt


def run_improvements_review():
    """Run focused review of improvements"""
    print("KGAS Roadmap Improvements Review")
    print("=" * 60)
    print(f"Start time: {datetime.now().isoformat()}")
    print("\nFocus: Review of improvements made based on previous feedback\n")
    
    # Collect files
    print("Collecting improvement documents...")
    files = collect_improvement_files()
    
    if not files:
        print("ERROR: No files found for review")
        return
    
    print(f"\nCollected {len(files)} files for review")
    
    # Create prompt
    print("\nGenerating focused review prompt...")
    prompt = create_improvements_prompt(files)
    
    # Calculate token estimate
    prompt_length = len(prompt)
    print(f"Prompt length: {prompt_length:,} characters (manageable size)")
    
    # Run review
    print("\nSending to Gemini for improvements review...")
    
    try:
        start_time = time.time()
        response = model.generate_content(prompt)
        end_time = time.time()
        
        print(f"\nReview completed in {end_time - start_time:.1f} seconds")
        
        # Save results
        output_file = "gemini-review-tool/roadmap-improvements-results.md"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w') as f:
            f.write(f"# KGAS Roadmap Improvements Review\n\n")
            f.write(f"**Review Date**: {datetime.now().isoformat()}\n")
            f.write(f"**Review Focus**: Assessment of improvements since 7.8/10 review\n")
            f.write(f"**Files Reviewed**: {len(files)}\n")
            f.write(f"**Review Tool**: Gemini 1.5 Flash\n\n")
            f.write("---\n\n")
            f.write(response.text)
        
        print(f"\nReview saved to: {output_file}")
        
        # Also save a summary
        summary_file = "gemini-review-tool/roadmap-improvements-summary.json"
        summary = {
            "review_date": datetime.now().isoformat(),
            "review_type": "improvements_assessment",
            "files_reviewed": len(files),
            "file_list": sorted(files.keys()),
            "review_time_seconds": end_time - start_time,
            "output_file": output_file,
            "previous_score": 7.8,
            "focus": "improvements_only"
        }
        
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"Summary saved to: {summary_file}")
        
    except Exception as e:
        print(f"\nERROR during review: {e}")
        return
    
    print("\n" + "=" * 60)
    print("Improvements review completed!")


if __name__ == "__main__":
    # Change to project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    run_improvements_review()