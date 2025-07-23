# Step 1: Document Processing and Initial Extraction

## Document Processing Flow

### Document 1: Conference Proceedings (1995)
```python
# Tool: T01_PDFLoader
pdf_content = pdf_loader.load("acl_1995_proceedings.pdf")
# Degradation: 0.95 (5% for PDF processing)

# Tool: T15a_TextChunker
chunks = text_chunker.chunk(pdf_content, chunk_size=512)
# No additional degradation

# Tool: T23a_SpacyNER
entities = spacy_ner.extract_entities(relevant_chunk)
# Output: 
# - "Johnson" (PERSON, confidence: 0.92)
# - "Smith" (PERSON, confidence: 0.94)
# - "1990" (DATE, confidence: 0.98)
# Degradation: 0.90 (10% for NER)

# Tool: T27_RelationshipExtractor (with LLM)
extraction_with_uncertainty = llm.extract_with_uncertainty(
    prompt="""Extract relationships and assess uncertainty from this text:
    "Johnson's work on semantic parsing builds directly on Smith's foundational grammar formalism (Smith, 1990)."
    
    For each relationship found:
    1. Identify the claim
    2. Assess your confidence in the extraction (0.0-1.0)
    3. Note any caveats or ambiguities
    
    Return structured output with relationship and uncertainty assessment.""",
    
    response_format=RelationshipExtractionOutput
)

# LLM Response:
{
    "relationship": {
        "subject": "Johnson",
        "predicate": "influenced_by",
        "object": "Smith",
        "temporal_context": "1990-1995"
    },
    "extraction_confidence": 0.88,
    "reasoning": "Clear statement of building on work, 'directly' indicates strong influence",
    "caveats": "Academic writing convention might overstate influence"
}

# Combined confidence after degradation chain:
# 0.88 × 0.95 × 0.90 × 0.85 = 0.64
```

### Key Observations from Document 1 Processing

1. **Degradation Cascade**: Initial extraction confidence of 0.88 degraded to 0.64
2. **LLM Uncertainty Assessment**: LLM noted potential overstatement in academic writing
3. **Temporal Context**: Relationship tagged with time period

---

## Document 2: Academic Biography (2005)
```python
# Tool: T03_TextLoader
text_content = text_loader.load("pioneers_book_chapter.txt")
# Degradation: 0.98 (2% for text processing)

# Similar NER and extraction process...

# LLM Extraction:
{
    "relationship": {
        "subject": "Bob Johnson",
        "predicate": "influenced_by", 
        "object": "Alice Smith",
        "temporal_context": "1990-ongoing"
    },
    "extraction_confidence": 0.82,
    "reasoning": "Direct credit given, but retrospective account may be romanticized",
    "caveats": "10-year gap between event and account; potential narrative construction"
}

# Note: LLM recognizes "Bob Johnson" and "Johnson" as same entity
# This will be important for claim matching
```

---

## Document 3: Citation Analysis (2010)
```python
# Quantitative data extraction
{
    "relationship": {
        "subject": "Johnson",
        "predicate": "cited",
        "object": "Smith",
        "temporal_context": "1991-1999",
        "quantity": 47,
        "percentage": 0.23
    },
    "extraction_confidence": 0.95,
    "reasoning": "Quantitative data is reliable, but citation doesn't prove influence",
    "caveats": "High citation count could indicate disagreement or obligatory citation"
}

# Note: Different predicate "cited" vs "influenced_by"
# System must reason about relationship between these predicates
```

---

## Document 4: Interview Transcript (1998)
```python
# Direct quote extraction
{
    "relationship": {
        "subject": "Johnson",
        "predicate": "influenced_by",
        "object": "Smith",
        "temporal_context": "acknowledged 1998"
    },
    "extraction_confidence": 0.78,
    "reasoning": "Direct acknowledgment but qualified with disagreement",
    "caveats": "Mixed signal - acknowledges influence but notes disagreement"
}
```

---

## Document 5: Grant Proposal (1992)
```python
# Grant proposal extraction
{
    "relationship": {
        "subject": "Johnson",
        "predicate": "extends_work_of",
        "object": "Smith",
        "temporal_context": "1992"
    },
    "extraction_confidence": 0.85,
    "reasoning": "Grant proposals tend to overclaim connections for fundability",
    "caveats": "Strategic document, may exaggerate intellectual lineage"
}
```

---

## Summary of Initial Extractions

| Document | Claim | Initial Confidence | Post-Degradation | Key Caveats |
|----------|-------|-------------------|------------------|-------------|
| Doc 1 (1995) | Johnson influenced_by Smith | 0.88 | 0.64 | Academic convention |
| Doc 2 (2005) | Johnson influenced_by Smith | 0.82 | 0.63 | Retrospective bias |
| Doc 3 (2010) | Johnson cited Smith 47x | 0.95 | 0.73 | Citation ≠ influence |
| Doc 4 (1998) | Johnson influenced_by Smith | 0.78 | 0.58 | Mixed acknowledgment |
| Doc 5 (1992) | Johnson extends Smith | 0.85 | 0.66 | Grant strategy |

## Critical Observations

1. **Multiple Predicate Types**: "influenced_by", "cited", "extends_work_of"
2. **Temporal Spread**: Evidence from 1992-2010 about 1990 influence
3. **Confidence Range**: Post-degradation 0.58-0.73
4. **LLM Awareness**: Each extraction includes domain-aware caveats
5. **Entity Resolution Needed**: "Johnson" vs "Bob Johnson"

## Next Step
These extractions now need to be processed by the claim matching system to identify which are about the same underlying claim.