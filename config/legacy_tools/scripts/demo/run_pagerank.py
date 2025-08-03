#!/usr/bin/env python3
"""Run PageRank calculation on the graph"""

from src.tools.phase1.t68_pagerank import PageRankCalculator
from src.core.identity_service import IdentityService
from src.core.provenance_service import ProvenanceService
from src.core.quality_service import QualityService

# Initialize services
identity = IdentityService()
provenance = ProvenanceService()
quality = QualityService()

# Initialize PageRank calculator
pagerank = PageRankCalculator(identity, provenance, quality)

# Calculate PageRank
print("Calculating PageRank scores...")
result = pagerank.calculate_pagerank()

if result["status"] == "success":
    print(f"✅ PageRank calculated for {result['total_entities']} entities")
    print("\nTop 10 entities by PageRank:")
    for i, entity in enumerate(result["ranked_entities"][:10], 1):
        print(f"{i}. {entity['name']} ({entity['type']}) - Score: {entity['pagerank_score']:.4f}")
else:
    print(f"❌ PageRank failed: {result.get('error')}")