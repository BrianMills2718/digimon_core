# KGAS Uncertainty System Stress Test Scenario

## Scenario: Academic Influence Network Analysis

We're analyzing the influence of "Dr. Alice Smith" on "Dr. Bob Johnson" in the field of computational linguistics during the 1990s. This is a complex scenario that will test all aspects of our uncertainty system.

## Data Sources

### Document Set 1: Conference Proceedings (1995)
- **Source**: ACL 1995 Conference Proceedings
- **Content**: "Johnson's work on semantic parsing builds directly on Smith's foundational grammar formalism (Smith, 1990)."
- **Initial Confidence**: 0.85
- **Context**: Peer-reviewed academic paper

### Document Set 2: Academic Biography (2005)
- **Source**: "Pioneers of Computational Linguistics" book
- **Content**: "Bob Johnson credits Alice Smith as a major influence, noting her 1990 paper changed his research direction."
- **Initial Confidence**: 0.80
- **Context**: Retrospective biography, potentially romanticized

### Document Set 3: Citation Analysis (2010)
- **Source**: Academic citation database analysis
- **Content**: "Johnson cited Smith's work 47 times between 1991-1999, representing 23% of his citations."
- **Initial Confidence**: 0.90
- **Context**: Quantitative analysis, but doesn't prove influence vs. obligatory citation

### Document Set 4: Interview Transcript (1998)
- **Source**: Oral History Project interview with Johnson
- **Content**: "I have to acknowledge Smith's influence, though we later disagreed on implementation details."
- **Initial Confidence**: 0.75
- **Context**: Direct statement but includes caveat

### Document Set 5: Grant Proposal (1992)
- **Source**: NSF grant archive
- **Content**: "This project extends Smith (1990) framework to handle pragmatic inference."
- **Initial Confidence**: 0.82
- **Context**: Early in timeline, shows direct building on work

## Complicating Factors

1. **Citation Network Dependencies**: 
   - The biography (Doc 2) cites the conference paper (Doc 1)
   - The citation analysis (Doc 3) includes the conference paper in its count
   
2. **Temporal Dependencies**:
   - Later documents may be influenced by earlier published claims
   - Retrospective accounts may be colored by established narrative

3. **Mixed Evidence Types**:
   - Direct statements (interview, biography)
   - Behavioral evidence (citations, grant proposal)
   - Third-party assessments (conference paper)

4. **Theory Context**:
   - Theory of "Academic Influence Networks" requires actual influence, not just citation
   - Must distinguish between genuine intellectual influence vs. social obligation

5. **Domain-Specific Factors**:
   - Computational linguistics in 1990s was small field (everyone knew everyone)
   - Citation practices included "courtesy citations" to senior researchers
   - Grant proposals often overclaim connections to established work

## Expected Challenges

1. **Dependency Modeling**: Sources are clearly not independent
2. **Prior Estimation**: What's the base rate of one researcher influencing another?
3. **Likelihood Estimation**: How likely are these observations given true vs. false influence?
4. **Theory Requirements**: Does our theory need "actual influence" or "perceived influence"?
5. **Confidence Degradation**: How do dependencies affect our confidence?

## Success Criteria

Our uncertainty system should:
1. Recognize the dependencies between sources
2. Appropriately adjust confidence based on dependency structure
3. Provide transparent reasoning about its Bayesian parameter estimates
4. Handle the mixed evidence types appropriately
5. Consider domain-specific factors in its analysis
6. Produce a final confidence that reflects the complexity of the evidence

## Next Steps

We'll walk through how each component of the KGAS system would handle this scenario:
1. Initial document processing and extraction
2. Claim identification and matching
3. Uncertainty assessment and Bayesian aggregation
4. Theory context integration
5. Final knowledge graph construction