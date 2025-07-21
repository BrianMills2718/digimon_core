#!/usr/bin/env python3

import os
import sys
import json
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure Gemini
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print("❌ GEMINI_API_KEY not found in environment")
    sys.exit(1)
    
genai.configure(api_key=api_key)

# Read the documentation bundle
with open('manual-docs-bundle.xml', 'r') as f:
    bundle_content = f.read()

# Comprehensive documentation assessment prompt
prompt = """You are conducting a comprehensive documentation audit for the KGAS (Knowledge Graph AI System) project to identify ALL inconsistencies, conflicts, and structural problems across the entire documentation set.

## CRITICAL FOCUS AREAS

### 1. PROJECT STATUS CONSISTENCY
- **Phase status conflicts**: Compare claims across CLAUDE.md, README.md, roadmap.md, and phase implementation plans
- **Completion claims**: Verify any "complete" or "implemented" claims against actual documented evidence
- **Timeline inconsistencies**: Check for conflicting dates, milestones, and progress reports
- **Implementation vs documentation gaps**: Identify where documentation claims don't match described reality

### 2. ARCHITECTURAL ALIGNMENT
- **System description consistency**: Do all docs describe the same system architecture?
- **Component naming**: Are components consistently named across all documentation?
- **Technology stack alignment**: Are technology choices consistently described?
- **Data flow consistency**: Do architecture docs align with implementation guides?

### 3. DOCUMENTATION ORGANIZATION PROBLEMS
- **Redundant content**: Identify duplicate information that should be consolidated
- **Broken cross-references**: Find references to missing or moved files
- **Outdated file references**: Check for references to old versions or deprecated docs
- **Authority conflicts**: Multiple docs claiming to be "authoritative" or "single source of truth"

### 4. CONTENT QUALITY ISSUES
- **Accuracy problems**: Technical claims that appear incorrect or unverifiable
- **Completeness gaps**: Missing critical information for users or developers
- **Clarity issues**: Confusing or contradictory instructions
- **Actionability problems**: Guidance that cannot be followed as written

### 5. SPECIFIC INCONSISTENCY PATTERNS TO CHECK
- **Phase 4 status**: Is Phase 4 consistently described as complete/incomplete across all docs?
- **Production readiness**: Are production capabilities consistently described?
- **Tool counts**: Are tool implementation numbers consistent across documents?
- **Validation claims**: Do validation reports match claimed implementation status?
- **Roadmap alignment**: Do phase plans match the master roadmap?

## ANALYSIS REQUIREMENTS

### For EVERY inconsistency found:
1. **Cite specific files and line numbers** where conflicts occur
2. **Quote the conflicting statements** directly
3. **Assess the impact** - does this create confusion or block progress?
4. **Recommend resolution** - which version is correct or how to reconcile

### Priority classification:
- **CRITICAL**: Blocks project understanding or creates false claims
- **HIGH**: Creates confusion for developers or users  
- **MEDIUM**: Minor inconsistencies that should be cleaned up
- **LOW**: Style or formatting issues

## DELIVERABLES REQUIRED

1. **Executive Summary**: Top 5 most critical documentation problems
2. **Detailed Inconsistency Report**: All conflicts found with specific citations
3. **Structural Problems Analysis**: Organization and navigation issues
4. **Authority Conflicts**: Documents claiming conflicting authority
5. **Missing Documentation Gaps**: Critical missing information
6. **Prioritized Action Plan**: What to fix first, second, third
7. **Truth Reconciliation Plan**: How to establish single source of truth for each topic

Be thorough, specific, and actionable. The goal is to restore complete documentation integrity across the entire project.

Here is the documentation bundle to analyze:

""" + bundle_content

# Create Gemini model
model = genai.GenerativeModel('gemini-2.5-flash')

print("🤖 Analyzing comprehensive documentation bundle with Gemini...")

# Generate analysis
try:
    response = model.generate_content(prompt)
    analysis_result = response.text
    
    # Create output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"outputs/{timestamp}/analysis"
    os.makedirs(output_dir, exist_ok=True)
    
    # Save results
    output_file = f"{output_dir}/comprehensive-docs-analysis-direct.md"
    with open(output_file, 'w') as f:
        f.write(f"# Comprehensive KGAS Documentation Analysis\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n")
        f.write(f"Model: gemini-2.5-flash\n")
        f.write(f"Method: Direct Documentation Bundle Analysis\n\n")
        f.write(analysis_result)
    
    print(f"✅ Analysis complete! Results saved to: {output_file}")
    print(f"📄 Analysis length: {len(analysis_result)} characters")
    
except Exception as e:
    print(f"❌ Error during analysis: {e}")
    sys.exit(1)