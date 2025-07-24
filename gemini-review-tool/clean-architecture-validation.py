#!/usr/bin/env python3
"""
Clean Architecture Validation - Post archival analysis
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from gemini_review import GeminiCodeReviewer
from gemini_review_config import ReviewConfig

def main():
    # Create a custom config for clean architecture validation
    config = ReviewConfig(
        project_name="KGAS Clean Architecture Analysis",
        custom_prompt="""
**OBJECTIVE**: Analyze the KGAS architecture design quality now that implementation status documents have been removed.

**CONTEXT**: This is a clean analysis of PURE ARCHITECTURAL DESIGN documents. All implementation status, progress reports, and point-in-time documents have been archived. We are analyzing only:
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

4. **Technical Sophistication** (1-10):
   - Are advanced concepts (cross-modal analysis, uncertainty propagation) well-designed?
   - Do the architectural patterns demonstrate good engineering practices?
   - Is the system designed for extensibility and maintainability?

5. **Documentation Quality** (1-10):
   - Are architectural decisions well-documented with rationale?
   - Do the concepts documents provide clear guidance for implementers?
   - Is the documentation comprehensive without being overwhelming?

**KEY ARCHITECTURAL DECISIONS TO EVALUATE**:
- ADR-001: Contract-first tool interface design
- ADR-009: Bi-store database strategy (Neo4j + SQLite)
- ADR-007: CERQual-based uncertainty quantification
- ADR-014: Fail-fast error handling strategy
- ADR-011: Academic research focus over enterprise scalability
- Cross-modal analysis architecture (graph/table/vector)
- Service-oriented architecture with core services

**OUTPUT REQUIREMENTS**:
1. **Overall Architecture Score (1-10)**: Based on design quality, not implementation
2. **Detailed Analysis**: For each of the 5 criteria above
3. **Architectural Strengths**: What's well-designed and innovative
4. **Design Gaps**: Missing specifications or unclear architectural decisions
5. **Academic Research Fit**: How well the architecture serves its intended academic research domain

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
    
    print("Starting clean architecture analysis...")
    
    # Use the clean architecture bundle
    bundle_file = "clean-architecture-bundle.xml"
    
    if not os.path.exists(bundle_file):
        print(f"Error: Bundle file {bundle_file} not found")
        print("Please run: npx repomix --include 'docs/architecture/ARCHITECTURE_OVERVIEW.md,docs/architecture/adrs/ADR-*.md,docs/architecture/systems/*.md,docs/architecture/data/*.md,docs/architecture/concepts/*.md,docs/architecture/specifications/*.md,docs/architecture/diagrams/*.md' --output clean-architecture-bundle.xml .")
        return
    
    reviewer = GeminiCodeReviewer(config)
    
    try:
        result = reviewer.review_file(bundle_file)
        
        # Save results
        output_file = f"outputs/clean-architecture-analysis-{reviewer.timestamp}.md"
        os.makedirs("outputs", exist_ok=True)
        
        with open(output_file, 'w') as f:
            f.write(result)
        
        print(f"\n✅ Clean architecture analysis completed!")
        print(f"📄 Results saved to: {output_file}")
        print(f"\n📊 Analysis Summary:")
        print("=" * 60)
        
        # Extract key insights from the result
        lines = result.split('\n')
        for i, line in enumerate(lines):
            if 'Overall Architecture Score' in line or 'ARCHITECTURE SCORE' in line:
                print(f"🎯 {line}")
            elif any(keyword in line.lower() for keyword in ['score:', 'rating:', '/10']):
                if not any(skip in line.lower() for skip in ['test', 'implementation', 'progress']):
                    print(f"📈 {line}")
        
        print("=" * 60)
        print(f"📖 Full detailed analysis available in: {output_file}")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Check that the bundle file exists and is < 200KB")
        print("2. Verify Gemini API credentials are configured")
        print("3. Try reducing bundle size if getting 500 errors")

if __name__ == "__main__":
    main()