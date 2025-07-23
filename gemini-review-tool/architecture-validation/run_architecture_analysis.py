#!/usr/bin/env python3
"""
Architecture Deep Analysis Runner
Executes focused validations on different architectural aspects
"""

import os
import sys
import subprocess
import time
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Validation configurations in order of priority
VALIDATIONS = [
    {
        "name": "Core Architecture",
        "config": "core-architecture.yaml",
        "description": "Analyzing core architectural design and coherence"
    },
    {
        "name": "Architecture Decision Records",
        "config": "adr-analysis.yaml", 
        "description": "Evaluating design decisions and rationale"
    },
    {
        "name": "Data Models and Schemas",
        "config": "data-model-analysis.yaml",
        "description": "Assessing data architecture and modeling"
    },
    {
        "name": "System Contracts and Integration",
        "config": "system-contracts-analysis.yaml",
        "description": "Reviewing component contracts and interfaces"
    },
    {
        "name": "Uncertainty and Quality Systems",
        "config": "uncertainty-quality-analysis.yaml",
        "description": "Examining academic rigor of quality metrics"
    }
]

def create_repomix_bundle(config_file):
    """Create focused repomix bundle based on configuration"""
    import yaml
    
    config_path = Path(__file__).parent / config_file
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Get target files
    files = config.get('target_files', [])
    if not files:
        print(f"❌ No target files specified in {config_file}")
        return None
    
    # Create include pattern
    include_pattern = ','.join([f"**/{Path(f).name}" for f in files])
    
    # Create output filename
    output_name = config_file.replace('.yaml', '.xml')
    output_path = Path(__file__).parent / 'bundles' / output_name
    output_path.parent.mkdir(exist_ok=True)
    
    # Run repomix
    project_root = Path(__file__).parent.parent.parent
    cmd = [
        'npx', 'repomix',
        '--include', include_pattern,
        '--output', str(output_path),
        str(project_root)
    ]
    
    print(f"📦 Creating bundle for {config_file}...")
    print(f"   Including: {include_pattern}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Repomix failed: {result.stderr}")
            return None
        
        # Check file size
        size_mb = output_path.stat().st_size / (1024 * 1024)
        print(f"✅ Bundle created: {output_path.name} ({size_mb:.1f} MB)")
        
        if size_mb > 0.15:  # 150KB limit
            print(f"⚠️  Warning: Bundle may be too large for optimal analysis")
        
        return str(output_path)
        
    except Exception as e:
        print(f"❌ Error creating bundle: {e}")
        return None

def run_validation(validation):
    """Run a single validation using gemini_review.py"""
    config_file = validation['config']
    bundle_path = create_repomix_bundle(config_file)
    
    if not bundle_path:
        return None
    
    # Run gemini review
    config_path = Path(__file__).parent / config_file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(__file__).parent / 'results' / timestamp
    
    cmd = [
        sys.executable,
        str(Path(__file__).parent.parent / 'gemini_review.py'),
        '--bundle', bundle_path,
        '--config', str(config_path),
        '--output-dir', str(output_dir)
    ]
    
    print(f"\n🔍 Running {validation['name']} analysis...")
    print(f"   {validation['description']}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Analysis complete! Results in: {output_dir}")
            return output_dir
        else:
            print(f"❌ Analysis failed: {result.stderr}")
            return None
    except Exception as e:
        print(f"❌ Error running validation: {e}")
        return None

def synthesize_results(result_dirs):
    """Create a synthesis report from all validation results"""
    synthesis_path = Path(__file__).parent / 'results' / 'architecture_synthesis.md'
    
    with open(synthesis_path, 'w') as f:
        f.write("# KGAS Architecture Deep Analysis - Synthesis Report\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("## Executive Summary\n\n")
        f.write("This report synthesizes findings from a comprehensive architectural analysis of the KGAS system.\n\n")
        
        for i, (validation, result_dir) in enumerate(zip(VALIDATIONS, result_dirs)):
            if result_dir:
                f.write(f"### {i+1}. {validation['name']}\n\n")
                # Try to read the actual results
                result_files = list(Path(result_dir).rglob("*.md"))
                if result_files:
                    with open(result_files[0], 'r') as rf:
                        content = rf.read()
                        # Extract key findings (customize based on actual format)
                        f.write("Key findings:\n")
                        f.write(content[:500] + "...\n\n")
                else:
                    f.write("Results pending analysis...\n\n")
        
        f.write("## Overall Architectural Assessment\n\n")
        f.write("Based on the comprehensive analysis across all architectural dimensions:\n\n")
        f.write("1. **Strengths**: [To be filled based on results]\n")
        f.write("2. **Weaknesses**: [To be filled based on results]\n")
        f.write("3. **Critical Improvements Needed**: [To be filled based on results]\n")
        f.write("4. **Risk Assessment**: [To be filled based on results]\n")
        f.write("5. **Recommendations**: [To be filled based on results]\n")
    
    print(f"\n📄 Synthesis report created: {synthesis_path}")
    return synthesis_path

def main():
    """Run all architecture validations"""
    print("🏗️  KGAS Architecture Deep Analysis")
    print("=" * 50)
    
    # Create necessary directories
    Path(__file__).parent.joinpath('bundles').mkdir(exist_ok=True)
    Path(__file__).parent.joinpath('results').mkdir(exist_ok=True)
    
    result_dirs = []
    
    for validation in VALIDATIONS:
        result_dir = run_validation(validation)
        result_dirs.append(result_dir)
        
        # Add delay to avoid rate limiting
        if result_dir:
            print("⏳ Waiting 30 seconds before next validation...")
            time.sleep(30)
    
    # Create synthesis report
    synthesis_path = synthesize_results(result_dirs)
    
    print("\n✅ Architecture analysis complete!")
    print(f"📊 Synthesis report: {synthesis_path}")
    
    # Summary
    successful = sum(1 for r in result_dirs if r is not None)
    print(f"\n📈 Summary: {successful}/{len(VALIDATIONS)} validations completed successfully")

if __name__ == "__main__":
    main()