#!/usr/bin/env python3
"""
Simple validation script using proper environment loading
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from gemini_review import GeminiCodeReviewer
from gemini_review_config import ReviewConfig

def main():
    print("🚀 Starting focused Gemini validation...")
    
    # Check if API key is available
    api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ No GEMINI_API_KEY or GOOGLE_API_KEY found in environment")
        return
    
    print(f"✅ API key loaded: {api_key[:10]}...")
    
    # Create focused config for architecture analysis
    config = ReviewConfig(
        project_name="KGAS Architecture Clean Analysis",
        custom_prompt="""
**OBJECTIVE**: Analyze the KGAS architecture design quality after removing implementation status documents.

**CONTEXT**: This is analysis of PURE ARCHITECTURAL DESIGN documents only:
- Architecture Decision Records (ADRs)
- System design specifications
- Architectural concepts and patterns
- Data architecture designs
- Component specifications

**ANALYSIS CRITERIA**:

1. **Architectural Coherence** (1-10):
   - Do the ADRs form a coherent architectural vision?
   - Are design decisions well-reasoned with proper trade-off analysis?
   - Do components integrate logically?

2. **Design Completeness** (1-10):
   - Are interfaces and contracts well-specified?
   - Is the data architecture clearly defined?
   - Are service boundaries and interactions clear?

3. **Academic Research Alignment** (1-10):
   - Does the architecture serve academic research requirements?
   - Are uncertainty quantification and error handling appropriate for research?
   - Does the design support reproducibility and transparency?

**OUTPUT REQUIREMENTS**:
1. **Overall Architecture Score (1-10)**: Based on design quality, not implementation
2. **Detailed Analysis**: For each of the 3 criteria above
3. **Architectural Strengths**: What's well-designed and innovative
4. **Design Gaps**: Missing specifications or unclear architectural decisions

**IGNORE**:
- Implementation status or progress
- Current development phases
- Tool completion percentages
- Any timeline or milestone information

**FOCUS ON**:
- Design quality and coherence
- Architectural innovation
- Academic research appropriateness
- Technical soundness of decisions
"""
    )
    
    # Check for architecture bundle
    bundle_file = "focused-architecture-bundle.xml"
    if not os.path.exists(bundle_file):
        print(f"❌ Bundle file {bundle_file} not found")
        return
    
    # Check bundle size
    bundle_size = os.path.getsize(bundle_file)
    print(f"📊 Bundle size: {bundle_size / 1024:.1f} KB")
    
    if bundle_size > 200 * 1024:
        print("⚠️ Bundle size over 200KB - may cause API issues")
    
    try:
        # Initialize reviewer 
        reviewer = GeminiCodeReviewer(api_key=api_key)
        
        print("🤖 Sending to Gemini for analysis...")
        
        # Read the bundle content
        with open(bundle_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Run the review
        result = reviewer.analyze_code(content, custom_prompt=config.custom_prompt)
        
        # Save results
        output_file = f"outputs/clean-architecture-analysis-focused.md"
        os.makedirs("outputs", exist_ok=True)
        
        with open(output_file, 'w') as f:
            f.write(result)
        
        print(f"✅ Analysis completed! Results saved to: {output_file}")
        
        # Extract key insights
        print("\n" + "="*60)
        print("📊 KEY FINDINGS")
        print("="*60)
        
        lines = result.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ['score:', 'rating:', '/10', 'overall']):
                if not any(skip in line.lower() for skip in ['test', 'implementation']):
                    print(f"🎯 {line.strip()}")
        
        print("="*60)
        print(f"📖 Full analysis: {output_file}")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()