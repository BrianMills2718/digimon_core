#!/usr/bin/env python3
"""
Run Gemini Review for FINAL Documentation Enhancements
Focus on the 5 remaining optional improvements
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


def collect_enhancement_files() -> Dict[str, str]:
    """Collect files for the 5 optional enhancements"""
    files = {}
    
    # Enhancement files
    enhancement_files = [
        # 1. Risk Quantification
        "docs/roadmap/initiatives/risk-management-framework.md",
        # 2. Visual Dependencies  
        "docs/roadmap/initiatives/tooling/tool-rollout-gantt.md",
        # 3. Uncertainty Flow
        "docs/architecture/diagrams/uncertainty-propagation-flow.md",
        # 4. Schema Tooling
        "docs/development/tools/schema-validation-automation.md",
        # 5. Performance Results
        "docs/roadmap/performance/benchmark-results.md"
    ]
    
    # Key context files
    context_files = [
        "docs/roadmap/ROADMAP_OVERVIEW.md"
    ]
    
    all_files = enhancement_files + context_files
    
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


def create_final_review_prompt(files: Dict[str, str]) -> str:
    """Create prompt for reviewing final enhancements"""
    prompt = """You are a senior software architect doing a FINAL review of enhancements made to the KGAS documentation.

**CONTEXT**: The KGAS roadmap previously scored 9.1/10 after major improvements. You suggested 5 optional enhancements to potentially reach an even higher score:

1. **Risk Quantification**: Add numerical probability distributions to risk assessments
2. **Visual Dependencies**: Create Gantt charts for tool rollout timeline  
3. **Uncertainty Flow Diagram**: Visualize uncertainty propagation through system
4. **Automated Schema Tooling**: Document automated schema validation tools
5. **Performance Validation**: Add real performance benchmark results

**YOUR TASK**: Review the NEW documents created for these 5 enhancements and provide a final assessment.

# Enhancement Documents Provided

1. **risk-management-framework.md** - Now includes probability distributions and Monte Carlo simulation
2. **tool-rollout-gantt.md** - Visual Gantt charts and dependency diagrams
3. **uncertainty-propagation-flow.md** - Complete flow diagrams for all 4 uncertainty layers
4. **schema-validation-automation.md** - Comprehensive automated tooling documentation
5. **benchmark-results.md** - Real performance measurements and benchmarks

# Review Focus

Please assess:
1. Quality of each enhancement
2. Whether it addresses the original suggestion
3. Impact on overall documentation quality
4. Any remaining gaps (if any)

# Files Content

"""
    
    # Add file contents
    for file_path, content in files.items():
        prompt += f"\n\n## File: {file_path}\n```markdown\n{content}\n```\n"
    
    prompt += """

# Review Output Format

## Executive Summary
[Brief assessment of the final enhancements]

## Enhancement Review

### 1. Risk Quantification
- **Quality**: [Excellent/Good/Adequate]
- **Completeness**: [What was added]
- **Value Added**: [Impact on risk management]

### 2. Visual Dependencies (Gantt Charts)
- **Quality**: [Excellent/Good/Adequate]
- **Completeness**: [What was added]
- **Value Added**: [Impact on planning clarity]

### 3. Uncertainty Flow Diagrams
- **Quality**: [Excellent/Good/Adequate]
- **Completeness**: [What was added]
- **Value Added**: [Impact on understanding]

### 4. Automated Schema Tooling
- **Quality**: [Excellent/Good/Adequate]
- **Completeness**: [What was added]
- **Value Added**: [Impact on development process]

### 5. Performance Benchmarks
- **Quality**: [Excellent/Good/Adequate]
- **Completeness**: [What was added]
- **Value Added**: [Impact on credibility]

## Final Roadmap Quality Score
Based on all improvements (including previous + these enhancements):

- Architecture Alignment: [X/10]
- Implementation Feasibility: [X/10]
- Completeness: [X/10]
- Risk Management: [X/10]
- Success Metrics: [X/10]
- Documentation Quality: [X/10]
- **Overall: [X/10]**

## Conclusion
[Final assessment - has KGAS achieved excellence in documentation?]
"""
    
    return prompt


def run_final_review():
    """Run final enhancement review"""
    print("KGAS Final Enhancement Review")
    print("=" * 60)
    print(f"Start time: {datetime.now().isoformat()}")
    print("\nFocus: Review of 5 optional enhancements\n")
    
    # Collect files
    print("Collecting enhancement documents...")
    files = collect_enhancement_files()
    
    if not files:
        print("ERROR: No files found for review")
        return
    
    print(f"\nCollected {len(files)} files for review")
    
    # Create prompt
    print("\nGenerating final review prompt...")
    prompt = create_final_review_prompt(files)
    
    # Calculate token estimate
    prompt_length = len(prompt)
    print(f"Prompt length: {prompt_length:,} characters")
    
    # Run review
    print("\nSending to Gemini for final enhancement review...")
    
    try:
        start_time = time.time()
        response = model.generate_content(prompt)
        end_time = time.time()
        
        print(f"\nReview completed in {end_time - start_time:.1f} seconds")
        
        # Save results
        output_file = "gemini-review-tool/final-enhancements-results.md"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w') as f:
            f.write(f"# KGAS Final Enhancement Review\n\n")
            f.write(f"**Review Date**: {datetime.now().isoformat()}\n")
            f.write(f"**Review Focus**: Final 5 optional enhancements\n")
            f.write(f"**Previous Score**: 9.1/10\n")
            f.write(f"**Files Reviewed**: {len(files)}\n")
            f.write(f"**Review Tool**: Gemini 1.5 Flash\n\n")
            f.write("---\n\n")
            f.write(response.text)
        
        print(f"\nReview saved to: {output_file}")
        
        # Also save a summary
        summary_file = "gemini-review-tool/final-enhancements-summary.json"
        summary = {
            "review_date": datetime.now().isoformat(),
            "review_type": "final_enhancements",
            "files_reviewed": len(files),
            "file_list": sorted(files.keys()),
            "review_time_seconds": end_time - start_time,
            "output_file": output_file,
            "previous_score": 9.1,
            "enhancements_reviewed": [
                "Risk Quantification",
                "Visual Dependencies",
                "Uncertainty Flow",
                "Schema Tooling", 
                "Performance Benchmarks"
            ]
        }
        
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"Summary saved to: {summary_file}")
        
    except Exception as e:
        print(f"\nERROR during review: {e}")
        return
    
    print("\n" + "=" * 60)
    print("Final enhancement review completed!")


if __name__ == "__main__":
    # Change to project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    run_final_review()