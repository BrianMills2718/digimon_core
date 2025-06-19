# Adversarial Testing Methodology

## The Problem: Premature Success Claims

Claude has repeatedly claimed milestones were complete, only to have adversarial testing reveal critical failures:

1. **First Claim**: "Milestone 2 Complete" → Testing revealed 0 relationships in graph
2. **Second Claim**: "TRUE GraphRAG Working" → Testing revealed 0% relationship extraction
3. **Third Claim**: "80% accuracy achieved" → But still 85% CO_OCCURS_WITH relationships

## Root Causes of False Success

1. **Confirmation Bias**: Running simple happy-path tests that are designed to pass
2. **Shallow Testing**: Checking if code runs, not if it actually works correctly  
3. **Missing Ground Truth**: Not comparing against expected results
4. **Incomplete Metrics**: Looking at one metric (e.g., "relationships exist") without checking quality

## Mandatory Adversarial Testing Protocol

### Before ANY Success Claim:

1. **Assume It's Broken**
   ```python
   # BAD: "Let me test if it works"
   # GOOD: "Let me prove it's broken"
   ```

2. **Test Against Ground Truth**
   ```python
   expected_relationships = [
       ("Elon Musk", "Tesla", "FOUNDED"),
       ("Microsoft", "OpenAI", "INVESTED_IN"),
       # ... explicit expectations
   ]
   # Count how many are ACTUALLY found
   ```

3. **Check Quality, Not Just Quantity**
   ```python
   # BAD: "Found 100 relationships!" 
   # GOOD: "Found 100 relationships: 85 CO_OCCURS_WITH, 10 LOCATED_IN, 5 FOUNDED"
   ```

4. **Test Edge Cases**
   - Partial names: "Musk" vs "Elon Musk"
   - Missing data: What if no embeddings?
   - Complex queries: Multi-hop paths
   - Scale: Does it work with 1000 entities?

5. **Verify End-to-End**
   ```python
   # Start with raw text
   text = "Bill Gates founded Microsoft. Microsoft acquired GitHub."
   
   # Verify EACH step produces expected output:
   # 1. Entities: ["Bill Gates", "Microsoft", "GitHub"]
   # 2. Relationships: [("Bill Gates", "Microsoft", "FOUNDED"), 
   #                    ("Microsoft", "GitHub", "ACQUIRED")]
   # 3. Query: "Who founded Microsoft?" → "Bill Gates"
   ```

## Adversarial Test Suite Requirements

### Test 1: Relationship Extraction Accuracy
```python
test_cases = [
    {
        "text": "Elon Musk founded Tesla in 2003.",
        "must_find": [
            ("Elon Musk", "Tesla", "FOUNDED"),
            ("Tesla|Elon Musk", "2003", "HAPPENED_IN")
        ],
        "must_not_find": [
            ("Elon", "Musk", "FOUNDED"),  # Wrong entity boundaries
            ("founded", "Tesla", "CO_OCCURS_WITH")  # Verb as entity
        ]
    }
]
```

### Test 2: Graph Structure Validation
```python
# Minimum requirements:
assert relationship_type_distribution["CO_OCCURS_WITH"] < 0.7  # Less than 70%
assert len(semantic_relationship_types) >= 5  # At least 5 different types
assert multi_hop_paths_exist()  # Can traverse A->B->C
assert no_isolated_entities_ratio < 0.2  # Less than 20% isolated
```

### Test 3: Query Capability Matrix
```python
query_types = {
    "direct_relationship": "Who founded Tesla?",
    "inverse_relationship": "What did Elon Musk found?",
    "multi_hop": "How is Bill Gates connected to GitHub?",
    "aggregation": "Which companies were acquired in 2016?",
    "path_finding": "Find the shortest path between OpenAI and Google",
    "without_embeddings": "Test all above with FAISS disabled"
}
# Must pass at least 60% of query types
```

### Test 4: Robustness Tests
```python
robustness_tests = [
    "empty_text": "",
    "no_entities": "The weather is nice today.",
    "only_pronouns": "He founded it in that year.",
    "foreign_names": "José García founded Empresas Madrid",
    "special_characters": "X.com (now PayPal) was founded",
    "very_long_text": "A" * 10000,
    "malformed_text": "Elon Musk founded founded Tesla Tesla in"
]
```

## Success Criteria Checklist

Before claiming ANY milestone complete:

- [ ] Ran full adversarial test suite
- [ ] Compared against explicit ground truth
- [ ] Tested without key dependencies (no embeddings, no LLM)
- [ ] Verified relationship type distribution is reasonable
- [ ] Checked multi-hop path queries work
- [ ] Tested with edge cases and malformed input
- [ ] Performance acceptable (< 5s for typical query)
- [ ] Error handling graceful (no crashes)
- [ ] Results reproducible across multiple runs
- [ ] Someone else could run tests and get same results

## Anti-Patterns to Avoid

1. **"Look, it extracted entities!"** → But are they the RIGHT entities?
2. **"The graph has relationships!"** → But are they MEANINGFUL relationships?
3. **"Queries return answers!"** → But are they CORRECT answers?
4. **"All tests pass!"** → But did you test the RIGHT things?

## The Golden Rule

**If you find yourself thinking "This looks good!" - STOP and write a test designed to make it fail.**

Only when you genuinely cannot make it fail should you consider it working.