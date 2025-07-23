# Documentation Standards - Implementation Status

## Status Headers Required

All architecture and implementation documents MUST include clear status headers:

### For Architecture Documents
```markdown
# Component Name Architecture

*Status: ✅ IMPLEMENTED AND TESTED*  
*Implementation*: `path/to/implementation.py`  
*Tests*: `path/to/tests.py`  
*Last Verified*: 2025-07-19

## OR

*Status: 🔄 PARTIALLY IMPLEMENTED*  
*Implementation*: `path/to/implementation.py` (missing X, Y, Z features)  
*Tests*: `path/to/tests.py`  
*Missing Features*: [list specific missing features]  
*Last Verified*: 2025-07-19

## OR

*Status: 📋 PLANNED*  
*Target Implementation*: `path/to/planned/implementation.py`  
*Dependencies*: [list dependencies needed first]  
*Last Verified*: 2025-07-19
```

### For Roadmap Documents
```markdown
# Feature Name

**Status**: ✅ COMPLETED | 🔄 IN PROGRESS | 📋 PLANNED  
**Implementation**: Specific file paths  
**Evidence**: Link to validation/test results  
**Last Updated**: 2025-07-19  
```

## Tool Count Standards

### Tool Inventory Requirements
1. **Automated Count**: Use `find src/tools -name "t[0-9]*_*.py" | wc -l` 
2. **Manual Verification**: List all T-numbered tools with functionality status
3. **Update Frequency**: Verify count monthly and after any tool additions
4. **Documentation Updates**: Update all docs when tool count changes

### Tool Status Categories
- **Implemented**: Tool code exists and basic functionality works
- **Tested**: Tool has both unit tests AND functional tests
- **Integrated**: Tool works in end-to-end workflows
- **Production-Ready**: Tool meets all quality and performance standards

## Functional Testing Standards

### Test Type Definitions
- **Unit Tests**: Test individual functions with mocks/stubs
- **Integration Tests**: Test tool interactions without mocks
- **Functional Tests**: Test complete workflows with real data
- **End-to-End Tests**: Test user scenarios from UI to results

### Implementation Requirements
Each tool MUST have:
1. **Unit Tests**: With and without mocks
2. **Functional Tests**: Real execution with sample data  
3. **Integration Tests**: Tool works with other tools
4. **Performance Tests**: Timing and resource usage validation

## Search and Discovery Standards

### File Naming for Discoverability
- Implementation files: Clear descriptive names matching documentation
- Test files: `test_[component]_functional.py` for functional tests
- Documentation: Include implementation file paths in headers

### Cross-Reference Requirements
- All architecture docs MUST link to implementation files
- All implementation files MUST link to documentation
- All tests MUST reference the components they test
- Use absolute paths from repo root for consistency

## Review and Validation Standards

### Monthly Documentation Review
1. Verify all status headers are current
2. Check implementation file links work
3. Validate tool counts match reality
4. Ensure test coverage is documented accurately

### Implementation Verification Commands
```bash
# Tool count verification
find src/tools -name "t[0-9]*_*.py" | wc -l

# Implementation status check
python -c "
from src.agents.workflow_agent import WorkflowAgent
print('✅ Multi-layer agent: IMPLEMENTED')
"

# Functional testing verification  
python -c "
from src.tools.phase1.t23a_spacy_ner import SpacyNER
ner = SpacyNER()
result = ner.extract_entities_working('Test text with John Smith.')
print(f'✅ SpaCy functional: {len(result)} entities extracted')
"
```

These standards prevent confusion by requiring explicit, verifiable status information in all documentation.

## Code Documentation Standards - "Why" Not Just "What"

### Academic Research Code Documentation Philosophy

Academic research code must be self-explanatory to domain experts who may not be the original developers. Documentation must explain **rationale, decisions, and context** rather than just describing what the code does.

#### **Documentation Hierarchy of Value**
1. **Why decisions were made** (highest value - often missing)
2. **What constraints influenced the implementation** 
3. **How the code works** (medium value)
4. **What the code does** (lowest value - often obvious from reading)

#### **Required Documentation Types**

##### **1. Architectural Decision Comments**
Every non-obvious design decision must be documented with rationale:

```python
# WHY: Using degradation factors instead of Bayesian updates because:
# 1. Academic research requires conservative confidence estimates
# 2. Bayesian updates require calibration data we don't have
# 3. Simple degradation model meets research transparency needs
# See ADR-010 for full analysis of alternatives considered
class QualityService:
    def __init__(self):
        self.quality_rules = {
            "pdf_loader": QualityRule(degradation_factor=0.95),
            # WHY 0.95: Empirical analysis shows PDF extraction introduces
            # ~5% uncertainty due to OCR errors and formatting issues
```

##### **2. Academic Domain Context Comments**
Code that implements academic concepts must explain the research context:

```python
def calculate_stakeholder_salience(legitimacy: float, urgency: float, power: float) -> float:
    """Calculate stakeholder salience using Mitchell, Agle, & Wood (1997) model.
    
    WHY geometric mean: Mitchell et al. specify that stakeholder salience
    is the geometric mean of three attributes because:
    - Multiplicative relationship: Zero in any dimension = zero salience
    - Equal weighting: No single attribute should dominate
    - Academic validation: Extensively validated in management literature
    
    WHY not arithmetic mean: Would allow high scores in one dimension
    to compensate for zero scores in others, contradicting theory
    """
    return (legitimacy * urgency * power) ** (1/3)
```

##### **3. Error Handling Rationale Comments**
Error handling decisions must explain why specific approaches were chosen:

```python
try:
    result = self.neo4j_driver.run(query)
except Neo4jConnectionError as e:
    # WHY fail-fast instead of graceful degradation:
    # Academic research cannot proceed with unknown data state
    # Silent failures corrupt research validity and reproducibility
    # Researchers need immediate feedback to resolve infrastructure issues
    # See ADR-014 for full error handling strategy rationale
    raise ProcessingError(
        f"Database connection failed: {e}",
        recovery_guidance=[
            "Check Neo4j service is running: docker ps | grep neo4j",
            "Verify connection settings in config/database.yaml",
            "Check database logs: docker logs neo4j"
        ]
    )
```

##### **4. Performance Trade-off Comments**
Code that makes performance vs. other trade-offs must explain the rationale:

```python
def process_documents_sequentially(self, documents: List[Document]) -> List[ProcessedDocument]:
    """Process documents one at a time instead of parallel processing.
    
    WHY sequential processing:
    - Academic research prioritizes correctness over speed (ADR-011)
    - Memory constraints: Typical researcher hardware (8-16GB RAM)
    - Error isolation: Easier to debug processing issues
    - Progress tracking: Researchers can monitor long-running analyses
    
    REJECTED parallel processing because:
    - Memory exhaustion on typical academic hardware
    - Complex error handling across worker processes
    - Difficult progress reporting for multi-hour analyses
    - Academic datasets (10-1000 docs) don't require high throughput
    """
```

##### **5. Academic Integrity Comments**
Code that affects research integrity must explain the safeguards:

```python
def log_extraction_provenance(self, claim: str, source_document: str, confidence: float):
    """Log extraction with complete provenance for academic integrity.
    
    WHY granular provenance logging:
    - Academic integrity requires every claim traceable to specific source
    - Research misconduct prevention: Cannot fabricate citations
    - Reproducibility: Other researchers must verify extraction accuracy
    - Publication requirements: Journals require source attribution
    
    WHY not just tool-level provenance:
    - Tool-level ("extracted by T27") insufficient for academic citation
    - Need document, page, paragraph for proper academic attribution
    - Prevents citation fabrication risk identified in architectural review
    """
```

#### **Forbidden Documentation Patterns**

##### **❌ What Without Why**
```python
# BAD: Only describes what, not why
def apply_degradation_factor(confidence, factor):
    """Multiply confidence by degradation factor."""
    return confidence * factor
```

##### **❌ Implementation Details Without Context**
```python
# BAD: Describes how, but not why this approach
def wait_for_neo4j_ready_async(self):
    """Check Neo4j connection every 2 seconds with exponential backoff."""
    # Missing: Why this specific sequence? What edge cases does it handle?
```

##### **❌ Obvious Comments**
```python
# BAD: States the obvious
def calculate_confidence(self, base_confidence: float) -> float:
    # Calculate confidence
    return base_confidence * 0.95
```

#### **Required Documentation Elements**

##### **Function/Method Documentation Template**
```python
def academic_research_function(param1: Type, param2: Type) -> ReturnType:
    """Brief description of function purpose in research context.
    
    Academic Context:
        Why this function exists in the research workflow.
        What research requirements it satisfies.
        
    Design Rationale:
        Why this specific implementation approach was chosen.
        What alternatives were considered and rejected.
        
    Academic Integrity Notes:
        How this function affects research validity/reproducibility.
        What safeguards are implemented.
        
    Args:
        param1: Description including academic research context
        param2: Description including expected ranges/constraints
        
    Returns:
        Description including research interpretation of results
        
    Raises:
        SpecificError: When this happens and why it's critical for research
        
    Example:
        >>> # Show realistic academic research usage
        >>> result = academic_research_function(research_data, 0.8)
        >>> assert result.confidence > 0.7  # Research quality threshold
        
    See Also:
        - ADR-XXX: Related architectural decision
        - Theory documentation: Link to relevant academic theory
    """
```

##### **Class Documentation Template**
```python
class AcademicResearchClass:
    """Brief description of class role in research system.
    
    Academic Purpose:
        What specific research need this class addresses.
        How it fits into academic workflow.
        
    Design Philosophy:
        Why this design approach supports research goals.
        What research principles influenced the design.
        
    Key Research Features:
        - Feature 1: Why this is important for research integrity
        - Feature 2: How this supports academic transparency
        
    Usage in Research Context:
        Typical academic research usage patterns.
        Integration with other research components.
        
    Academic Integrity Considerations:
        How this class protects research validity.
        What audit trails and safeguards are provided.
    """
```

#### **Domain-Specific Documentation Requirements**

##### **Social Science Theory Implementation**
Code implementing social science theories must reference academic literature:

```python
class StakeholderTheoryProcessor:
    """Implement Mitchell, Agle, & Wood (1997) stakeholder identification model.
    
    Academic Foundation:
        Based on "Toward a Theory of Stakeholder Identification and Salience"
        Academy of Management Review, 22(4), 853-886.
        
    Theory Implementation:
        - Legitimacy: Stakeholder's legitimate claim on organization
        - Power: Stakeholder's ability to influence organization
        - Urgency: Time-critical nature of stakeholder's claim
        - Salience: f(legitimacy, power, urgency) using geometric mean
        
    WHY geometric mean implementation:
        Theory specifies multiplicative relationship where zero
        in any dimension results in zero salience (non-stakeholder).
        Arithmetic mean would incorrectly allow compensation across dimensions.
    """
```

##### **Graph Algorithm Implementation**
Graph algorithms must explain academic research context:

```python
def calculate_research_influence_centrality(self, graph: ResearchGraph) -> Dict[str, float]:
    """Calculate researcher influence using PageRank adapted for academic networks.
    
    Academic Rationale:
        PageRank adapted for academic citation networks where:
        - Nodes: Researchers, theories, concepts
        - Edges: Citations, influences, references
        - Weights: Citation strength, co-authorship frequency
        
    WHY PageRank over other centrality measures:
        - Handles directed citation relationships appropriately
        - Accounts for quality of citations (influential sources matter more)
        - Established precedent in bibliometric research (Chen et al. 2007)
        
    Research Validity Considerations:
        - Self-citation filtering to prevent influence inflation
        - Temporal weighting to account for recency bias
        - Confidence scoring based on citation network completeness
    """
```

### **Documentation Quality Assurance**

#### **Documentation Review Checklist**
- [ ] Every non-obvious design decision explained with "WHY"
- [ ] Academic research context provided for domain-specific code
- [ ] Error handling rationale documented
- [ ] Performance trade-offs explained
- [ ] Academic integrity considerations addressed
- [ ] Alternative approaches mentioned and rejection reasons given
- [ ] Relevant ADRs and academic literature referenced

#### **Documentation Metrics**
- **"Why" ratio**: Proportion of comments explaining rationale vs. describing actions
- **Academic context coverage**: Percentage of domain-specific code with research context
- **Decision documentation**: Percentage of design decisions with documented rationale
- **Knowledge transfer readiness**: Can new researcher understand code without original developer?

#### **Documentation Maintenance Process**
1. **Pre-commit hook**: Check for documentation standards compliance
2. **Code review requirement**: Reviewers must verify documentation quality
3. **Architecture decision updates**: Update code comments when ADRs change
4. **Knowledge transfer testing**: New team members review code documentation quality

These enhanced documentation standards ensure that critical architectural knowledge and research context are preserved in the codebase, preventing the expert knowledge extraction failure identified in the architectural review.