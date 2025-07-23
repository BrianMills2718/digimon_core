#!/usr/bin/env python3
"""
Run Data Model Analysis using Gemini (Fixed version)
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

import google.generativeai as genai
from dotenv import load_dotenv
import yaml

# Load environment variables
load_dotenv()

def read_validation_config():
    """Read the data model validation config"""
    config_path = Path(__file__).parent / "data-model-analysis.yaml"
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def read_bundle():
    """Read the repomix bundle"""
    bundle_path = Path(__file__).parent / "bundles" / "data-model-analysis-fixed.xml"
    if not bundle_path.exists():
        raise FileNotFoundError(f"Bundle not found: {bundle_path}")
    
    with open(bundle_path, 'r', encoding='utf-8') as f:
        return f.read()

def run_gemini_analysis(bundle_content, prompt):
    """Run Gemini analysis on the bundle"""
    # Configure Gemini
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
    
    genai.configure(api_key=api_key)
    
    # Create the model
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    # Combine bundle and prompt
    full_prompt = f"""
{prompt}

Here are the data model and schema documents to analyze:

{bundle_content}
"""
    
    print("🤖 Sending to Gemini for data model analysis...")
    print(f"   Bundle size: {len(bundle_content):,} characters")
    
    try:
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        print(f"❌ Error from Gemini: {e}")
        return None

def save_results(analysis, config):
    """Save the analysis results"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = Path(__file__).parent / "results" / timestamp
    results_dir.mkdir(parents=True, exist_ok=True)
    
    # Save the analysis
    analysis_file = results_dir / "data-model-analysis-complete.md"
    with open(analysis_file, 'w', encoding='utf-8') as f:
        f.write(f"# Data Model and Schema Analysis\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"## Analysis Type\n{config['validation_type']}\n\n")
        f.write(f"## Claim\n{config['claim']}\n\n")
        f.write("## Analysis Results\n\n")
        f.write(analysis)
    
    print(f"✅ Results saved to: {analysis_file}")
    return analysis_file

def main():
    """Run the data model analysis"""
    print("🗄️  Running Data Model and Schema Analysis")
    print("=" * 50)
    
    try:
        # Read config
        config = read_validation_config()
        
        # Read bundle
        bundle_content = read_bundle()
        
        # Run analysis
        analysis = run_gemini_analysis(bundle_content, config['prompt'])
        
        if analysis:
            # Save results
            results_file = save_results(analysis, config)
            
            # Print summary
            print("\n📊 Analysis Summary:")
            lines = analysis.split('\n')
            for line in lines[:10]:  # First 10 lines
                if line.strip():
                    print(f"   {line}")
            print("   ...")
            
            print(f"\n✅ Full analysis available at: {results_file}")
        else:
            print("❌ Analysis failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()