"""
Phase 1 tools load theory YAML and map MCL IDs before extraction.
"""

"""Phase 1 Tools - Vertical Slice Implementation

Implements the critical path for PDF → PageRank → Answer workflow:
- T01: PDF Loader
- T15a: Text Chunker  
- T23a: spaCy NER
- T27: Relationship Extractor
- T31: Entity Builder
- T34: Edge Builder
- T68: PageRank
- T49: Multi-hop Query
"""