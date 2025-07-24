#!/usr/bin/env python3

import os
import sys
import json
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from gemini_review import GeminiCodeReviewer

def main():
    """Run direct validation on Phase 2.1 implementation"""
    
    # Initialize the reviewer
    reviewer = GeminiCodeReviewer()
    
    # Load the repomix file
    repomix_file = Path(__file__).parent / "repomix-output.xml"
    if not repomix_file.exists():
        print(f"Error: {repomix_file} not found")
        return 1
    
    # Define the validation prompt
    custom_prompt = """PHASE 2.1 ADVANCED GRAPH ANALYTICS VALIDATION

**OBJECTIVE**: Validate all Phase 2.1 components are fully implemented and meet requirements.

**VALIDATION CRITERIA**:

1. **GraphCentralityAnalyzer** (src/analytics/graph_centrality_analyzer.py):
   - ✓ Class exists with __init__(self, neo4j_manager, distributed_tx_manager)
   - ✓ calculate_pagerank_centrality() method with entity_type filtering
   - ✓ calculate_betweenness_centrality() method with sampling for large graphs
   - ✓ calculate_closeness_centrality() method implemented
   - ✓ Uses AnalyticsError for error handling
   - ✓ Integrates with DTM using begin/commit/rollback transaction pattern

2. **CommunityDetector** (src/analytics/community_detector.py):
   - ✓ Class exists with community_algorithms dictionary
   - ✓ _louvain_clustering() method implemented
   - ✓ _label_propagation_clustering() method implemented
   - ✓ _greedy_modularity_clustering() method with fallback
   - ✓ _analyze_communities() for community characteristics
   - ✓ Uses AnalyticsError for error handling

3. **CrossModalEntityLinker** (src/analytics/cross_modal_linker.py):
   - ✓ Main class and EntityResolver helper class exist
   - ✓ link_cross_modal_entities() main method
   - ✓ _generate_modal_embeddings() for text/image/structured
   - ✓ _calculate_cross_modal_similarities() method
   - ✓ _build_cross_modal_graph() method
   - ✓ MockEmbeddingService for testing

4. **ConceptualKnowledgeSynthesizer** (src/analytics/knowledge_synthesizer.py):
   - ✓ Class with synthesis_strategies dictionary
   - ✓ _abductive_synthesis() method for anomaly-based reasoning
   - ✓ _inductive_synthesis() method for pattern extraction
   - ✓ _deductive_synthesis() method for theory application
   - ✓ HypothesisGenerator helper class
   - ✓ _detect_knowledge_anomalies() method

5. **CitationImpactAnalyzer** (src/analytics/citation_impact_analyzer.py):
   - ✓ Class with impact_metrics list containing all 8 metrics
   - ✓ _calculate_h_index() method implementation
   - ✓ _calculate_citation_velocity() method
   - ✓ _calculate_cross_disciplinary_impact() method
   - ✓ _analyze_temporal_impact() method
   - ✓ _generate_impact_report() method

**REPORT FORMAT**: For each component, state:
- FULLY IMPLEMENTED: If all criteria are met with specific evidence
- PARTIALLY IMPLEMENTED: If some criteria are missing (list what's missing)
- NOT IMPLEMENTED: If the component is missing entirely

Provide specific evidence (method names, line numbers) for your assessment."""

    # Read the repomix content
    with open(repomix_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🤖 Running direct validation on Phase 2.1 implementation...")
    print(f"📊 File size: {len(content)/1024:.1f} KB")
    print(f"📝 Token count: ~{len(content)//4:,} tokens")
    
    # Run the review
    result = reviewer.analyze_code(
        codebase_content=content,
        claims_of_success="Phase 2.1 Advanced Graph Analytics fully implemented",
        custom_prompt=custom_prompt,
        documentation=""
    )
    
    # Print the result
    print("\n" + "="*60)
    print("PHASE 2.1 VALIDATION RESULTS")
    print("="*60)
    print(result)
    
    # Save the result
    output_file = Path(__file__).parent / "phase21_validation_results.md"
    with open(output_file, 'w') as f:
        f.write(f"# Phase 2.1 Advanced Graph Analytics Validation Results\n\n")
        f.write(f"Generated: {Path(__file__).stat().st_mtime}\n\n")
        f.write(result)
    
    print(f"\nResults saved to: {output_file}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())