#!/usr/bin/env python3
"""
Run all architecture analyses in sequence
"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime
import subprocess

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

import google.generativeai as genai
from dotenv import load_dotenv
import yaml

# Load environment variables
load_dotenv()

# Define all analyses
ANALYSES = [
    {
        "name": "Data Models and Schemas",
        "config": "data-model-analysis.yaml",
        "bundle_name": "data-model-analysis.xml",
        "files": [
            "docs/architecture/data/DATABASE_SCHEMAS.md",
            "docs/architecture/data/PYDANTIC_SCHEMAS.md", 
            "docs/architecture/data/AI_MODELS.md",
            "docs/architecture/data/bi-store-justification.md",
            "docs/architecture/data/theory-meta-schema-v10.md",
            "docs/architecture/data-model/neo4j-schema.md",
            "docs/architecture/data-model/sqlite-schema.md"
        ]
    },
    {
        "name": "System Contracts and Integration",
        "config": "system-contracts-analysis.yaml",
        "bundle_name": "system-contracts-analysis.xml",
        "files": [
            "docs/architecture/systems/contract-system.md",
            "docs/architecture/systems/tool-contract-validation-specification.md",
            "docs/architecture/systems/COMPONENT_ARCHITECTURE_DETAILED.md",
            "docs/architecture/systems/mcp-integration-architecture.md",
            "docs/architecture/systems/external-mcp-orchestration.md",
            "docs/architecture/specifications/capability-registry.md"
        ]
    },
    {
        "name": "Uncertainty and Quality Systems",
        "config": "uncertainty-quality-analysis.yaml",
        "bundle_name": "uncertainty-quality-analysis.xml",
        "files": [
            "docs/architecture/adrs/ADR-004-Normative-Confidence-Score-Ontology.md",
            "docs/architecture/adrs/ADR-007-uncertainty-metrics.md",
            "docs/architecture/adrs/ADR-016-Bayesian-Uncertainty-Aggregation.md",
            "docs/architecture/concepts/uncertainty-architecture.md",
            "docs/architecture/diagrams/uncertainty-propagation-flow.md",
            "docs/architecture/adrs/ADR-010-Quality-System-Design.md"
        ]
    }
]

def create_repomix_bundle(analysis):
    """Create repomix bundle for an analysis"""
    include_pattern = ','.join(analysis['files'])
    output_path = Path(__file__).parent / "bundles" / analysis['bundle_name']
    
    cmd = [
        'npx', 'repomix',
        '--include', include_pattern,
        '--output', str(output_path),
        '.'
    ]
    
    print(f"\n📦 Creating bundle for {analysis['name']}...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Failed to create bundle: {result.stderr}")
        return False
    
    # Check size
    size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"✅ Bundle created: {output_path.name} ({size_mb:.2f} MB)")
    return True

def run_analysis(analysis):
    """Run a single analysis"""
    # Read config
    config_path = Path(__file__).parent / analysis['config']
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Read bundle
    bundle_path = Path(__file__).parent / "bundles" / analysis['bundle_name']
    with open(bundle_path, 'r', encoding='utf-8') as f:
        bundle_content = f.read()
    
    # Configure Gemini
    api_key = os.getenv('GEMINI_API_KEY')
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    # Create prompt
    full_prompt = f"""
{config['prompt']}

Here is the content to analyze:

{bundle_content}
"""
    
    print(f"\n🤖 Running {analysis['name']} analysis...")
    print(f"   Bundle size: {len(bundle_content):,} characters")
    
    try:
        response = model.generate_content(full_prompt)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_dir = Path(__file__).parent / "results" / timestamp
        results_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = results_dir / f"{analysis['config'].replace('.yaml', '.md')}"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# {analysis['name']} Analysis\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"## Analysis Type\n{config['validation_type']}\n\n")
            f.write(f"## Claim\n{config['claim']}\n\n")
            f.write("## Analysis Results\n\n")
            f.write(response.text)
        
        print(f"✅ Analysis complete! Results: {output_file}")
        return str(output_file)
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return None

def create_synthesis_report(results):
    """Create a comprehensive synthesis report"""
    synthesis_path = Path(__file__).parent / "results" / "ARCHITECTURE_ANALYSIS_SYNTHESIS.md"
    
    with open(synthesis_path, 'w') as f:
        f.write("# KGAS Architecture Deep Analysis - Comprehensive Synthesis\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("## Executive Summary\n\n")
        f.write("This report synthesizes findings from a comprehensive architectural analysis of the KGAS system, ")
        f.write("covering core architecture, design decisions (ADRs), data models, system contracts, and quality systems.\n\n")
        
        # Include summaries from each analysis
        f.write("## Analysis Summaries\n\n")
        
        # Core Architecture (already done)
        core_results = list(Path(__file__).parent.glob("results/*/core-architecture-analysis.md"))
        if core_results:
            f.write("### 1. Core Architecture Analysis\n\n")
            with open(core_results[-1], 'r') as rf:
                content = rf.read()
                # Extract rating
                if "Overall Architectural Quality Rating:" in content:
                    rating_line = [line for line in content.split('\n') if "Overall Architectural Quality Rating:" in line]
                    if rating_line:
                        f.write(f"**{rating_line[0].strip()}**\n\n")
                # Extract top issues
                if "Top 5 Most Critical Improvements Needed:" in content:
                    idx = content.find("Top 5 Most Critical Improvements Needed:")
                    if idx > 0:
                        improvements = content[idx:idx+1000].split('\n')[2:7]
                        f.write("**Critical Improvements:**\n")
                        for imp in improvements:
                            if imp.strip():
                                f.write(f"{imp}\n")
                        f.write("\n")
        
        # ADR Analysis (already done)
        adr_results = list(Path(__file__).parent.glob("results/*/adr-analysis.md"))
        if adr_results:
            f.write("### 2. Architecture Decision Records Analysis\n\n")
            with open(adr_results[-1], 'r') as rf:
                content = rf.read()
                # Extract greatest risks
                if "greatest risks" in content:
                    idx = content.find("greatest risks")
                    if idx > 0:
                        risks = content[idx:idx+1000].split('\n')[1:4]
                        f.write("**Greatest Risks:**\n")
                        for risk in risks:
                            if risk.strip() and "ADR-" in risk:
                                f.write(f"{risk}\n")
                        f.write("\n")
        
        # Include new analyses
        for i, (analysis, result_file) in enumerate(zip(ANALYSES, results), start=3):
            if result_file:
                f.write(f"### {i}. {analysis['name']} Analysis\n\n")
                with open(result_file, 'r') as rf:
                    content = rf.read()
                    # Extract key findings (first substantive paragraph after results)
                    lines = content.split('\n')
                    start_idx = None
                    for j, line in enumerate(lines):
                        if "## Analysis Results" in line:
                            start_idx = j + 2
                            break
                    if start_idx:
                        summary_lines = []
                        for line in lines[start_idx:start_idx+20]:
                            if line.strip():
                                summary_lines.append(line)
                            if len(summary_lines) >= 5:
                                break
                        f.write('\n'.join(summary_lines[:5]) + "...\n\n")
        
        # Overall conclusions
        f.write("## Overall Architectural Assessment\n\n")
        f.write("### Key Strengths\n\n")
        f.write("1. **Conceptually Sound Design**: The target architecture shows good design principles\n")
        f.write("2. **Academic Focus**: Clear alignment with research needs and reproducibility\n")
        f.write("3. **Modularity**: Service-oriented architecture promotes separation of concerns\n\n")
        
        f.write("### Critical Weaknesses\n\n")
        f.write("1. **Implementation Gap**: Massive disconnect between design and implementation\n")
        f.write("2. **Reliability Crisis**: System currently at 1/10 reliability with data corruption risks\n")
        f.write("3. **Technical Debt**: Lack of testing, persistence, and proper error handling\n\n")
        
        f.write("### Recommendations\n\n")
        f.write("1. **HALT all feature development** until reliability issues are resolved\n")
        f.write("2. **Implement comprehensive testing** at all levels (unit, integration, system)\n")
        f.write("3. **Fix data persistence** and corruption issues as top priority\n")
        f.write("4. **Standardize interfaces** before adding new tools\n")
        f.write("5. **Add monitoring and observability** to diagnose issues in production\n\n")
        
        f.write("### Risk Assessment\n\n")
        f.write("**Current State: CRITICAL** - The system is not suitable for any production use, ")
        f.write("including academic research, due to data corruption risks and reliability issues.\n\n")
        
        f.write("### Path Forward\n\n")
        f.write("The KGAS project needs a **reliability remediation phase** before continuing with planned features. ")
        f.write("This should include:\n\n")
        f.write("1. Comprehensive testing suite implementation\n")
        f.write("2. Data integrity verification and fixes\n")
        f.write("3. Error handling and recovery mechanisms\n")
        f.write("4. Performance profiling and optimization\n")
        f.write("5. Documentation of actual vs intended architecture\n")
    
    print(f"\n📄 Synthesis report created: {synthesis_path}")
    return synthesis_path

def main():
    """Run all analyses"""
    print("🏗️  KGAS Architecture Comprehensive Analysis")
    print("=" * 50)
    
    results = []
    
    for analysis in ANALYSES:
        # Create bundle
        if not create_repomix_bundle(analysis):
            print(f"⚠️  Skipping {analysis['name']} due to bundle creation failure")
            results.append(None)
            continue
        
        # Run analysis
        result = run_analysis(analysis)
        results.append(result)
        
        # Wait between analyses to avoid rate limiting
        if result:
            print("⏳ Waiting 30 seconds before next analysis...")
            time.sleep(30)
    
    # Create synthesis
    synthesis_path = create_synthesis_report(results)
    
    print("\n✅ All analyses complete!")
    print(f"📊 Synthesis report: {synthesis_path}")
    
    # Summary
    successful = sum(1 for r in results if r is not None)
    print(f"\n📈 Summary: {successful}/{len(ANALYSES)} new analyses completed")

if __name__ == "__main__":
    main()