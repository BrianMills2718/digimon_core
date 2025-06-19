#!/usr/bin/env python3
"""Run PageRank calculation on the graph"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from tools.phase1.t68_pagerank import PageRankCalculator
from core.identity_service import IdentityService
from core.provenance_service import ProvenanceService
from core.quality_service import QualityService

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