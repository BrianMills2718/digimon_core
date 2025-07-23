# Step 2: Claim Identification and Matching

## Entity Resolution Phase

```python
# Tool: EntityResolutionService
entity_resolution = EntityResolutionService()

# Resolve entity variations
resolved_entities = entity_resolution.resolve([
    "Johnson",
    "Bob Johnson", 
    "Smith",
    "Alice Smith"
])

# Result:
{
    "entity_clusters": [
        {
            "canonical": "Bob Johnson",
            "variations": ["Johnson", "Bob Johnson", "B. Johnson"],
            "confidence": 0.94
        },
        {
            "canonical": "Alice Smith", 
            "variations": ["Smith", "Alice Smith", "A. Smith"],
            "confidence": 0.92
        }
    ]
}
```

## Predicate Relationship Analysis

```python
# LLM analyzes relationship between different predicates
predicate_analysis = llm.analyze_predicate_relationships(
    prompt="""Analyze the semantic relationships between these predicates:
    1. "influenced_by"
    2. "cited" 
    3. "extends_work_of"
    
    In the context of academic influence, how do these relate?
    Which could be evidence for which others?""",
    
    predicates=["influenced_by", "cited", "extends_work_of"]
)

# LLM Response:
{
    "analysis": {
        "influenced_by": {
            "type": "high_level_claim",
            "evidence_predicates": ["cited", "extends_work_of"],
            "strength": "requires_multiple_evidence"
        },
        "cited": {
            "type": "behavioral_evidence",
            "supports": ["influenced_by"],
            "caveat": "necessary_not_sufficient"
        },
        "extends_work_of": {
            "type": "direct_evidence",
            "supports": ["influenced_by"],
            "strength": "strong_indicator"
        }
    },
    "reasoning": "Citation is weak evidence for influence (could be criticism). Extending work is stronger evidence. Multiple evidence types strengthen influence claim."
}
```

## Claim Clustering

```python
# System identifies related claims
claim_clusters = ClaimMatcher.cluster_claims([
    {"subject": "Bob Johnson", "predicate": "influenced_by", "object": "Alice Smith", "doc": 1},
    {"subject": "Bob Johnson", "predicate": "influenced_by", "object": "Alice Smith", "doc": 2},
    {"subject": "Bob Johnson", "predicate": "cited", "object": "Alice Smith", "doc": 3},
    {"subject": "Bob Johnson", "predicate": "influenced_by", "object": "Alice Smith", "doc": 4},
    {"subject": "Bob Johnson", "predicate": "extends_work_of", "object": "Alice Smith", "doc": 5}
])

# Result: One main claim cluster with supporting evidence
primary_claim_cluster = {
    "core_claim": {
        "subject": "Bob Johnson",
        "predicate": "influenced_by", 
        "object": "Alice Smith",
        "temporal_context": "1990-1999"
    },
    "evidence_instances": [
        {
            "doc_id": 1,
            "type": "direct_claim",
            "predicate": "influenced_by",
            "confidence": 0.64,
            "year": 1995
        },
        {
            "doc_id": 2,
            "type": "direct_claim",
            "predicate": "influenced_by", 
            "confidence": 0.63,
            "year": 2005
        },
        {
            "doc_id": 3,
            "type": "supporting_evidence",
            "predicate": "cited",
            "confidence": 0.73,
            "year": 2010,
            "quantitative": {"count": 47, "percentage": 0.23}
        },
        {
            "doc_id": 4,
            "type": "direct_claim",
            "predicate": "influenced_by",
            "confidence": 0.58,
            "year": 1998,
            "qualified": True
        },
        {
            "doc_id": 5,
            "type": "supporting_evidence",
            "predicate": "extends_work_of",
            "confidence": 0.66,
            "year": 1992
        }
    ]
}
```

## Source Dependency Analysis

```python
# LLM analyzes dependencies between sources
dependency_analysis = llm.analyze_source_dependencies(
    prompt="""Analyze potential dependencies between these sources about Johnson being influenced by Smith:
    
    1. Conference paper (1995) - Academic claim
    2. Biography (2005) - Credits Smith, retrospective
    3. Citation analysis (2010) - 47 citations, 23% of total
    4. Interview (1998) - Johnson acknowledges but notes disagreement
    5. Grant proposal (1992) - Extends Smith's framework
    
    Consider temporal order, citation relationships, and how narratives build.""",
    
    response_format=DependencyAnalysisOutput
)

# LLM Response:
{
    "dependency_structure": {
        "likely_dependencies": [
            {
                "source": "Biography (2005)",
                "depends_on": ["Conference paper (1995)", "Interview (1998)"],
                "reasoning": "Retrospective account likely influenced by established narrative"
            },
            {
                "source": "Citation analysis (2010)", 
                "depends_on": ["Conference paper (1995)"],
                "reasoning": "Includes the conference paper in its citation count"
            }
        ],
        "independent_sources": [
            {
                "source": "Grant proposal (1992)",
                "reasoning": "Earliest source, predates others"
            },
            {
                "source": "Interview (1998)",
                "reasoning": "Direct testimony, though may be influenced by 1995 paper"
            }
        ],
        "correlation_factors": {
            "temporal_cascade": 0.7,
            "narrative_reinforcement": 0.6,
            "citation_overlap": 0.4
        }
    },
    "overall_independence": 0.4,
    "reasoning": "Clear temporal dependencies and narrative building. Later sources likely influenced by earlier published claims. Not fully independent evidence."
}
```

## Prepared for Bayesian Analysis

The system has now:
1. **Resolved entities** to canonical forms
2. **Clustered claims** into one primary claim with supporting evidence
3. **Analyzed predicate relationships** (cited and extends support influenced_by)
4. **Identified source dependencies** (overall independence = 0.4)

## Key Insights for Next Step

1. **Not Independent Sources**: Biography and citation analysis show clear dependencies
2. **Mixed Evidence Types**: Direct claims vs behavioral evidence
3. **Temporal Ordering Matters**: 1992 grant is most independent
4. **Qualified Evidence**: Interview acknowledges influence but with caveats

This complex dependency structure will be crucial for the Bayesian aggregation step.