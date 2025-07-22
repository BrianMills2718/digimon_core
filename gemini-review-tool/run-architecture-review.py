#!/usr/bin/env python3
"""
Run Gemini Review specifically for Architecture Documentation

This script performs a focused critical review of all architecture documentation
in the KGAS project.
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
    """Collect all architecture documentation files"""
    architecture_files = {}
    base_path = Path("docs/architecture")
    
    if not base_path.exists():
        print(f"ERROR: Architecture directory not found: {base_path}")
        return architecture_files
    
    # Define file patterns to include
    patterns = [
        "ARCHITECTURE_OVERVIEW.md",
        "concepts/*.md",
        "data/*.md",
        "specifications/*.md", 
        "systems/*.md",
        "adrs/ADR-*.md"
    ]
    
    # Collect files
    for pattern in patterns:
        for file_path in base_path.glob(pattern):
            if file_path.is_file():
                relative_path = file_path.relative_to(Path("."))
                try:
                    content = file_path.read_text(encoding='utf-8')
                    architecture_files[str(relative_path)] = content
                    print(f"Collected: {relative_path}")
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
    
    return architecture_files


def create_review_prompt(files: Dict[str, str]) -> str:
    """Create the comprehensive review prompt"""
    prompt = """You are a senior software architect conducting a CRITICAL review of the Knowledge Graph Analysis System (KGAS) architecture documentation.

Your review must be thorough, specific, and actionable. Focus on identifying real issues that could impact system quality, maintainability, or scalability.

# Review Criteria

## 1. Architectural Clarity (Weight: 25%)
- Are architectural decisions clearly explained with rationale?
- Is the system structure easy to understand?
- Are component responsibilities well-defined?
- Are diagrams accurate and helpful?

## 2. Completeness (Weight: 20%)
- Are all major components documented?
- Are integration points fully specified?
- Are cross-cutting concerns addressed?
- Are failure modes and error handling documented?

## 3. Consistency (Weight: 20%)
- Do all documents align with each other?
- Are naming conventions consistent?
- Do ADRs match the actual architecture?
- Are there conflicting design decisions?

## 4. Technical Quality (Weight: 15%)
- Are technology choices well-justified?
- Are best practices followed?
- Are performance considerations addressed?
- Is the architecture testable?

## 5. Risks and Debt (Weight: 10%)
- What architectural risks are present?
- Is technical debt acknowledged?
- Are mitigation strategies defined?
- Are upgrade paths considered?

## 6. Security and Privacy (Weight: 10%)
- Are security boundaries clear?
- Is data protection addressed?
- Are authentication/authorization patterns defined?
- Are compliance requirements met?

# Files to Review

"""
    
    # Add file contents
    for file_path, content in files.items():
        prompt += f"\n\n## File: {file_path}\n```markdown\n{content}\n```\n"
    
    prompt += """

# Review Output Format

Provide your review in the following format:

## Executive Summary
[2-3 paragraph overview of the architecture quality and major findings]

## Critical Issues (Must Fix)
[Issues that block production readiness or create significant risk]

### Issue 1: [Title]
- **Location**: [Specific file and section]
- **Problem**: [Clear description]
- **Impact**: [Why this matters]
- **Recommendation**: [Specific fix]

## High Priority Issues
[Important issues that should be addressed soon]

## Medium Priority Issues
[Issues that impact quality but aren't blocking]

## Low Priority Issues
[Nice-to-have improvements]

## Positive Observations
[What's done well - be specific]

## Architecture Score
- Clarity: [X/10]
- Completeness: [X/10]
- Consistency: [X/10]
- Technical Quality: [X/10]
- Risk Management: [X/10]
- Security: [X/10]
- **Overall: [X/10]**

## Specific Questions

1. **Bi-directional Store Architecture**: The system uses Neo4j + SQLite. Is this complexity justified? Are the sync mechanisms robust?

2. **Tool Proliferation**: 121 tools planned. Is this manageable? What's the governance model?

3. **Identity Resolution**: How does the identity service handle conflicts at scale?

4. **Performance**: No clear performance requirements or benchmarks. What are the targets?

5. **Error Recovery**: How does the system recover from partial failures in the pipeline?

Be critical but constructive. Every issue should have an actionable recommendation.
"""
    
    return prompt


def run_architecture_review():
    """Run the architecture review"""
    print("Knowledge Graph Analysis System - Architecture Review")
    print("=" * 60)
    print(f"Start time: {datetime.now().isoformat()}")
    print()
    
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
    print("\nSending to Gemini for review...")
    print("This may take a few minutes due to the comprehensive nature of the review...")
    
    try:
        start_time = time.time()
        response = model.generate_content(prompt)
        end_time = time.time()
        
        print(f"\nReview completed in {end_time - start_time:.1f} seconds")
        
        # Save results
        output_file = "gemini-review-tool/architecture-review-results.md"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w') as f:
            f.write(f"# KGAS Architecture Documentation Review\n\n")
            f.write(f"**Review Date**: {datetime.now().isoformat()}\n")
            f.write(f"**Files Reviewed**: {len(files)}\n")
            f.write(f"**Review Tool**: Gemini 1.5 Flash\n\n")
            f.write("---\n\n")
            f.write(response.text)
        
        print(f"\nReview saved to: {output_file}")
        
        # Also save a summary
        summary_file = "gemini-review-tool/architecture-review-summary.json"
        summary = {
            "review_date": datetime.now().isoformat(),
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
    print("Architecture review complete!")
    print(f"End time: {datetime.now().isoformat()}")


if __name__ == "__main__":
    # Change to project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    run_architecture_review()