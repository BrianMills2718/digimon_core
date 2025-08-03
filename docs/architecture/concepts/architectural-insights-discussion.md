# KGAS Architectural Insights & Design Philosophy

**Status**: Living Document - Synthesis of Critical Design Discussions  
**Purpose**: Capture key insights, critiques, and decisions from architectural review  
**Last Updated**: 2025-07-21

## Table of Contents
1. [Core Insights](#core-insights)
2. [Architecture Philosophy](#architecture-philosophy)
3. [Critical Critiques & Responses](#critical-critiques--responses)
4. [Cross-Modal Analysis Design](#cross-modal-analysis-design)
5. [Uncertainty Architecture](#uncertainty-architecture)
6. [Theory Integration Strategy](#theory-integration-strategy)
7. [Implementation Philosophy](#implementation-philosophy)
8. [Key Tradeoffs & Mitigations](#key-tradeoffs--mitigations)

---

## Core Insights

### The Fundamental Vision
KGAS represents an ambitious attempt to create a **theory-aware, cross-modal knowledge graph analysis system** for academic social science research. The key insight is that different research questions require different data representations, and the system should fluidly support movement between these representations while maintaining theoretical grounding.

### Key Architectural Principles

1. **Synchronized Multi-Modal Views, Not Lossy Conversions**
   - Each representation (graph, table, vector) is a first-class citizen
   - Enrichment rather than reduction when moving between modes
   - All views linked by common provenance

2. **Hidden Complexity Through LLM Mediation**
   - Sophisticated capabilities (ontologies, uncertainty, theory) hidden behind natural language interface
   - LLM assesses analytic goals and configures appropriate tools
   - Users never see formal logic or complex ontologies

3. **Vertical Slice Development Philosophy**
   - Build thin but complete implementation touching all layers
   - Validate architectural decisions early
   - Expand horizontally after vertical validation

4. **Theory as Configuration, Not Hardcoding**
   - Theories encoded as schemas that configure analysis
   - Master Concept Library provides reusable mappings
   - Cross-theory analysis through common vocabulary

---

## Architecture Philosophy

### Bi-Store Justification

The bi-store architecture (Neo4j + SQLite) is **not arbitrary** but serves specific analytical needs:

- **Neo4j**: Optimized for graph traversal, network analysis, vector similarity
- **SQLite**: Optimized for statistical analysis, structured equation modeling, relational operations

**Key Insight**: Different analytical methods have natural data representations. Rather than forcing all analysis through one store, use the optimal store for each analysis type.

### Cross-Modal Philosophy

**Traditional Approach** (Information Loss):
```
Graph → Flatten → Table (loses network structure)
Table → Aggregate → Statistics (loses individual records)
```

**KGAS Approach** (Synchronized Views):
```
Source Data → Parallel Extraction → Graph View (full network)
                                  ↘ Table View (with graph metrics as columns)
                                  ↘ Vector View (semantic embeddings)
                                  
All views maintain entity IDs and provenance links
```

### Example: Graph Metrics as Table Columns
```sql
CREATE TABLE entities (
    entity_id TEXT PRIMARY KEY,
    -- Original attributes
    name TEXT,
    type TEXT,
    -- Graph-computed metrics
    pagerank_score FLOAT,
    betweenness_centrality FLOAT,
    community_id INTEGER,
    -- Provenance
    computation_algorithm TEXT,
    computation_timestamp DATETIME
);
```

This enables statistical analysis (regression, SEM) on graph-computed features while maintaining full traceability.

---

## Critical Critiques & Responses

### Critique 1: Scope Overextension

**Issue**: Project attempts to solve 8-10 independent research problems simultaneously:
- Theory extraction
- Cross-modal analysis  
- Uncertainty quantification
- LLM integration
- Ontology management
- MCP protocol
- Temporal reasoning
- PII management

**Response & Mitigation**:
- Adopt vertical slice approach: minimal implementation of all features first
- Use LLM as orchestration layer (Claude via MCP) rather than building custom agent
- Defer complex features (4-layer uncertainty, full DOLCE integration) to later phases
- Focus on demonstrable value in each phase

### Critique 2: Implementation-Documentation Misalignment

**Issue**: Architecture documents describe sophisticated target system while implementation is basic.

**Response & Mitigation**:
- Clear separation established:
  - `/docs/architecture/` = target design (stable)
  - `/ROADMAP_OVERVIEW.md` = current status (living)
- Documentation now explicitly distinguishes aspirational architecture from current state
- Vertical slice approach provides path from current to target

### Critique 3: Ontology Complexity

**Initial Concern**: Multiple overlapping ontological frameworks (DOLCE, FOAF/SIOC, CERQual, custom typology)

**Revised Understanding**:
- Ontologies hidden behind LLM configuration layer
- User never interacts with formal ontologies directly
- LLM determines when formal reasoning adds value

**Key Decision**: Start without formal ontologies, add only when specific use cases demonstrate need

---

## Cross-Modal Analysis Design

### Core Concept: Analytical Appropriateness

Different research questions naturally fit different representations:

| Research Question | Optimal Mode | Why |
|------------------|--------------|-----|
| "Who influences whom?" | Graph | Natural for relationship traversal |
| "Is influence correlated with expertise?" | Table | Statistical operations native to SQL |
| "Find similar discourse patterns" | Vector | Semantic similarity in embedding space |

### Implementation Strategy

```python
class CrossModalOrchestrator:
    async def analyze(self, question: str, data: Any) -> Results:
        # LLM determines optimal analysis path
        strategy = await self.llm.determine_strategy(question)
        
        if strategy.primary_mode == "graph":
            graph_results = await self.graph_analysis(data)
            # Enrich with other modes as needed
            if strategy.needs_statistics:
                table_view = self.graph_to_table_enrichment(graph_results)
                stats = await self.statistical_analysis(table_view)
                
        return self.integrate_results(all_results)
```

### Synchronization Pattern

```python
@dataclass
class SynchronizedEntity:
    # Core identity (same across all modes)
    entity_id: str
    source_document: str
    
    # Mode-specific representations
    graph_node: Neo4jNode
    table_row: SQLiteRow
    embedding: NumpyVector
    
    # Shared provenance
    extraction_timestamp: datetime
    extraction_confidence: float
```

---

## Uncertainty Architecture

### Philosophical Shift: Everything is a Claim

Rather than treating system outputs as facts, KGAS treats everything as claims with associated uncertainty:
- Factual claims: "Tim Cook is CEO of Apple" (confidence: 0.95)
- Theoretical claims: "This community exhibits bridging capital" (confidence: 0.73)
- Synthetic detection: "This text appears AI-generated" (confidence: 0.61)

### Implementation Pragmatism

**Initial 4-Layer Architecture** (Overly Complex):
1. Contextual Entity Resolution (BERT embeddings)
2. Temporal Knowledge Graph (interval confidence)
3. Bayesian Network Pipeline (learned CPTs)
4. Distribution-Preserving Aggregation (mixture models)

**Revised Approach** (Practical):
- Start with simple confidence scores (0-1)
- Use CERQual dimensions for structured assessment
- Add complexity only when demonstrated need
- Let LLM explain uncertainty in natural language

### CERQual Integration

All uncertainty assessed on four dimensions:
1. **Methodological Limitations**: Quality of extraction/analysis method
2. **Relevance**: Applicability to research context
3. **Coherence**: Internal consistency of evidence
4. **Adequacy**: Sufficiency of supporting data

---

## Theory Integration Strategy

### Theory Meta-Schema Capabilities

The existing theory meta-schema is **more capable than initially assessed**. It can handle complex theories through operationalization:

```json
{
  "theory_name": "Bourdieu's Theory of Practice",
  "ontology": {
    "entities": [
      {
        "name": "Agent",
        "properties": [
          {"name": "habitus", "type": "disposition_matrix"},
          {"name": "capital_portfolio", "type": "multi_type_resource"}
        ]
      }
    ],
    "relationships": [
      {
        "name": "generates_practice",
        "source_role": "habitus",
        "target_role": "practice",
        "properties": [
          {"name": "unconscious", "type": "boolean"},
          {"name": "field_appropriate", "type": "float"}
        ]
      }
    ]
  }
}
```

**Key Insight**: The schema doesn't need to capture ALL philosophical complexity - just **operationalizable components** that LLMs can identify in text.

### Handling Dynamic and Emergent Processes

**Dynamic Processes** (e.g., Spiral of Silence):
```json
{
  "process": {
    "type": "iterative_adaptive",
    "steps": [
      {
        "measure": "minority_opinion_visibility",
        "threshold_check": "visibility < previous_visibility * 0.8",
        "adaptation": "increase_spiral_strength"
      }
    ],
    "measurement_interval": "1 week"
  }
}
```

**Emergent Properties** (e.g., Collective Intelligence):
```json
{
  "emergence_checks": [
    {
      "name": "collective_intelligence",
      "condition": "group_solution_quality > max(individual_solutions) * 1.2",
      "measurement": "problem_solving_performance"
    }
  ]
}
```

Human analysts use heuristics that can be codified into process specifications.

### Theory Operationalization Philosophy

**Core Principle**: If a theory has value, it must have at least heuristics (if not quantitative rules) for application. Theories that cannot be operationalized have limited empirical value.

**Simplification Strategy**:
```json
"simplifications": [
  "Habitus reduced to measurable dispositions",
  "Pre-reflexive coded as unconscious patterns",
  "Doxa operationalized as unquestioned beliefs"
]
```

### Theory Schema → MCL Mapping

The key architectural insight is mapping theory-specific terms to common concepts:

```yaml
# Master Concept Library (universal concepts)
CohesiveGroup:
  properties: [high_internal_connectivity, shared_identity]

# Theory A calls it "in-group"
# Theory B calls it "cluster"  
# Theory C calls it "bonded community"
# All map to MCL: "CohesiveGroup"
```

This enables cross-theory analysis and comparison.

### Validation Through Primitive Concepts

**Mechanical Turk Strategy** (Revised Understanding):
- Workers code **primitive concepts**, not full theory application
- Example: "Does this text express in-group identification? YES/NO"
- Multiple coders provide inter-rater reliability
- LLM performance compared against human baseline on primitives
- Theory application happens in aggregation layer

```python
# What MTurk workers do:
text = "As a doctor, I naturally understand medical journals"
concepts_to_code = {
    "habitus": "embodied dispositions from past experience",
    "field": "social domain with specific rules",
    "capital": "resources valued in the field"
}
# Workers identify: habitus=YES, field=YES, capital=YES
```

### Addressing LLM Consistency Through Layered Ontology

**The MCL/FOAF/DOLCE Layering Solution**:
```python
# Text: "The doctor community rallied together"

# Level 1 (Instance): Specific extraction - may vary
community_instance = "doctors_who_rallied"  # Monday
community_instance = "medical_professionals_group"  # Tuesday

# Level 2 (Domain concept): MCL mapping - stable
mcl_concept = "ProfessionalCommunity"  # Consistent

# Level 3 (Upper ontology): DOLCE - always consistent
dolce_category = "SocialObject"  

# Result: Instance variation doesn't affect conceptual consistency
```

This layered approach provides stability at the conceptual level while allowing natural variation at the instance level.

### Theory Complexity Tiers

**Tier 1: Direct Operationalization**
- Social Network Theory (clear metrics: centrality, clustering)
- Diffusion of Innovations (defined stages: awareness → adoption)

**Tier 2: Heuristic Operationalization**  
- Social Identity Theory (in-group/out-group dynamics)
- Framing Theory (frame identification and effects)

**Tier 3: Simplified Operationalization**
- Bourdieu's Practice Theory (habitus as dispositions)
- Giddens' Structuration (agency-structure duality)
- Critical Theory (power structures as identifiable patterns)
- Interpretivist approaches (meaning-making as codifiable heuristics)

### Lightweight Constraint System

Rather than full Description Logic reasoning:

```python
class TheoryConstraints:
    def validate(self, entity: Entity, theory: Theory) -> List[Violation]:
        violations = []
        
        # Simple Python logic for most constraints
        if entity.type == "IsolatedCommunity" and "BridgingCapital" in entity.properties:
            violations.append(Violation(
                rule="isolated_excludes_bridging",
                explanation="Isolated communities cannot have bridging capital"
            ))
            
        return violations
```

### Theory as Analysis Configuration

```python
@dataclass
class TheoryConfiguration:
    extraction_focus: List[str]  # What entities/relations to prioritize
    analysis_methods: List[str]  # What algorithms to run
    constraint_rules: List[Rule]  # What to validate
    output_mappings: Dict[str, str]  # Theory terms → MCL concepts
    operationalization_notes: List[str]  # Document simplifications
```

### Operationalizing Vague Theoretical Concepts

**Challenge**: Theory says "Strong ties influence more than weak ties" but doesn't specify the function

**Solution**: Document operationalization decisions explicitly
```json
{
  "tie_strength_operationalization": {
    "strong_tie": {
      "definition": "Interaction frequency > 3x per week AND emotional_closeness > 0.7",
      "influence_weight": 0.8
    },
    "weak_tie": {
      "definition": "Interaction frequency < 1x per week OR emotional_closeness < 0.3",
      "influence_weight": 0.3
    },
    "assumptions_made": [
      "Linear influence model",
      "Frequency and emotional closeness as key indicators",
      "Specific thresholds chosen based on distribution analysis"
    ]
  }
}
```

**Value**: Making implicit theoretical assumptions explicit advances the theory itself by forcing precision.

---

## Validation Strategy

### Multi-Level Validation Approach

**Level 1: Primitive Concept Validation**
- Mechanical Turk workers identify theory primitives in text
- Inter-rater reliability establishes human baseline
- LLM performance compared against human coding
- Focus on concept identification, not theory application

**Level 2: Theory Application Validation**
- Compare full theory application against expert analyses
- Use published papers as ground truth
- Temporal validation: train on 2020-2023, predict 2024

**Level 3: Cross-Theory Robustness**
- Apply multiple theories to same dataset
- Identify convergent vs divergent findings
- Document where theories agree/disagree
- Robustness across theories indicates reliable findings

### Handling Theory Conflicts

**Philosophy**: Don't force resolution - present all perspectives
```python
# When theories disagree
results = {
    "social_contagion": "Influence spreads through network exposure",
    "cognitive_dissonance": "Influence requires resolving internal conflict",
    "social_identity": "Influence depends on group membership"
}
# Present all three explanations with confidence scores
```

**Value Proposition**: Understanding where theories converge/diverge is itself a major contribution

### Explanation vs Causation

**Important Distinction**:
- System provides **explanations** in context of theories
- Not claiming rigorous **causal inference**
- Interventions are **theory-grounded suggestions**, not causal prescriptions
- Appropriate for exploratory research and hypothesis generation

### Four-Tier Analysis Framework

**Policy-Oriented Analysis Progression**:
1. **Descriptive**: "What patterns exist in the discourse?"
2. **Explanatory**: "Why do these patterns exist (according to theory X)?"
3. **Predictive**: "What patterns will likely emerge next?"
4. **Interventionary**: "What actions might change these patterns?"

This framework provides clear value progression while avoiding contentious causal claims. Each tier builds on the previous, enabling comprehensive policy analysis without requiring causal certainty.

## Implementation Philosophy

### Build vs Buy Decisions

**MCP for Agent Layer**: Buy (use Claude via MCP)
- Avoids building custom orchestration
- Leverages state-of-the-art LLM
- Standard protocol with tool versioning

**Formal Ontologies**: Don't Buy (build lightweight)
- Existing tools (OWL/Protégé) too heavyweight
- Social science constraints simpler than medical/legal
- Python implementation more maintainable

**Cross-Modal Conversion**: Build (custom implementation)
- No existing tools handle provenance preservation
- Need domain-specific enrichment logic
- Core differentiator for system

**Theory Schema Extraction**: Already Built (automated)
- Automated extraction from academic papers implemented
- Located in `/home/brian/projects/Digimons/lit_review`
- Multi-phase extraction preserves theoretical nuance
- Eliminates manual schema creation bottleneck

### Vertical Slice Components

**Phase 1 Minimal Implementations**:
```python
# Graph (minimal)
graph.add_entity("Apple", type="Organization")
graph.add_relationship("Tim Cook", "LEADS", "Apple")

# Table (minimal)  
table = graph_to_table(graph)  # Entities with basic properties

# Cross-modal (minimal)
stats_df = compute_basic_stats(table)
update_graph_properties(graph, stats_df)

# Uncertainty (minimal)
result = extract_entities(text)
confidence = assess_confidence(result)  # Single 0-1 score

# Theory (minimal)
constraints = load_theory_constraints("Social Capital Theory")
violations = check_constraints(entities, constraints)
```

### Development Principles

1. **Demonstrable Progress**: Working system at each phase
2. **Early Validation**: Test architectural decisions quickly
3. **Incremental Complexity**: Add sophistication based on need
4. **User-Driven Features**: Build what researchers actually use

---

## Key Tradeoffs & Mitigations

### Tradeoff 1: Flexibility vs Performance

**Choice**: Prioritize flexibility (multiple representations, theory configurations)

**Mitigation**:
- Single-node design reduces distributed system complexity
- Async operations where possible
- Caching of expensive computations
- Performance optimization deferred to Phase 4

### Tradeoff 2: Sophistication vs Usability

**Choice**: Hide complexity behind LLM interface

**Mitigation**:
- Natural language interaction for all operations
- LLM explains complex concepts in user terms
- Progressive disclosure of advanced features
- Default configurations for common use cases

### Tradeoff 3: Rigor vs Practicality

**Choice**: Practical implementation over formal rigor

**Mitigation**:
- Document limitations clearly
- Provide confidence scores for all outputs
- Enable export to formal tools when needed
- Focus on research utility over theoretical purity

### Tradeoff 4: Completeness vs Time-to-Value

**Choice**: Vertical slice over complete components

**Mitigation**:
- Each phase provides usable functionality
- Architecture supports future expansion
- Core abstractions enable component evolution
- Clear roadmap from minimal to complete

---

## Risk Mitigations

### Technical Risks

1. **Cross-Modal Complexity**
   - Mitigation: Start with simple property copying
   - Expand to sophisticated transformations gradually
   - Maintain clear transformation audit trail

2. **Theory Integration Challenges**
   - Mitigation: Begin with 2-3 well-understood theories
   - Collaborate with domain experts
   - Build theory schemas iteratively

3. **Performance at Scale**
   - Mitigation: Design for optimization from start
   - Profile early and often
   - Clear boundaries for refactoring

### Research Risks

1. **Validation Difficulty**
   - Mitigation: Partner with active researchers
   - Define clear evaluation metrics
   - Publish methodology papers

2. **Theory-Reality Mismatch**
   - Mitigation: Flexible schema evolution
   - Empirical validation cycles
   - Theory modification workflows

---

## Success Criteria

### Phase 1 (Vertical Slice)
- Can load documents and extract entities
- Can query across graph and table representations
- Can assess basic confidence in results
- Can apply simple theory constraints

### Phase 2 (Research Useful)
- Researchers can complete real analyses
- Cross-modal conversions preserve analytical value
- Theory schemas guide meaningful extraction
- Results traceable to sources

### Phase 3 (Full Vision)
- Sophisticated uncertainty quantification
- Multiple theories integrated
- Performance suitable for large corpora
- Active research community

---

## Key Decisions Summary

1. **Use bi-store architecture** for optimal analytical capabilities
2. **Hide complexity behind LLM** for usability
3. **Build vertical slice first** for early validation
4. **Defer formal ontologies** until demonstrated need
5. **Use theory schemas** for domain logic, not general ontologies
6. **Leverage MCP/Claude** for orchestration layer
7. **Prioritize research utility** over theoretical completeness

---

## Future Considerations

### When to Add Complexity

Add formal ontologies when:
- Cross-dataset integration requires schema matching
- Logical inference becomes bottleneck
- Publication requires formal semantics

Add sophisticated uncertainty when:
- Simple confidence insufficient for decisions
- Temporal dynamics require decay models
- Distribution preservation critical for analysis

Add performance optimization when:
- Analysis time impacts research iteration
- Dataset size exceeds single node capacity
- Real-time analysis requirements emerge

### Architecture Evolution Path

1. **Current**: Basic GraphRAG with Neo4j
2. **Phase 1**: Minimal cross-modal with simple confidence
3. **Phase 2**: Theory-guided extraction with MCL mapping
4. **Phase 3**: Full cross-modal orchestration
5. **Future**: Formal reasoning and advanced uncertainty as needed

The architecture is designed to evolve based on empirical research needs rather than theoretical completeness.

---

## Comprehensive Research Workflow Example

### Research Question
**"How do environmental advocacy groups influence corporate climate policy through social media networks?"**

### Multi-Theory Application Workflow

**Step 1: Theory Configuration**
```python
theories = [
    load_theory("Social Network Theory"),     # For influence paths
    load_theory("Framing Theory"),           # For message construction
    load_theory("Stakeholder Theory")        # For corporate response
]
```

**Step 2: Theory-Guided Extraction**
Each theory extracts different aspects:
- **Social Network**: Nodes (NGOs, corporations, media) and influence paths
- **Framing**: Environmental frames, economic frames, moral frames
- **Stakeholder**: Stakeholder salience, legitimacy, urgency

**Step 3: Cross-Modal Analysis**
```python
# Graph mode: Find influence paths
influence_paths = neo4j.query("""
MATCH path = (ngo:NGO)-[:MENTIONS|AMPLIFIES*1..3]->(corp:Corporation)
WHERE exists((corp)-[:ANNOUNCES]->(policy:ClimatePolicy))
RETURN path
""")

# Table mode: Statistical correlation
influence_df = graph_to_table_with_metrics(influence_paths)
correlation = stats.correlate(
    influence_df['betweenness_centrality'],
    influence_df['policy_change_likelihood']
)
# Result: r=0.73, p<0.001
```

**Step 4: Multi-Theory Synthesis**
```python
synthesis = {
    "network_theory": "Bridge actors (journalists) critical for influence",
    "framing_theory": "Moral frames most effective for policy change",
    "stakeholder_theory": "NGO legitimacy increases with media coverage"
}
```

**Step 5: Uncertainty Quantification**
- Network path confidence: 0.82 (strong evidence)
- Frame classification confidence: 0.71 (moderate evidence)
- Stakeholder salience: 0.64 (limited evidence)

### Key Insights from Walkthrough

1. **Value emerges from synthesis**: No single theory explains everything
2. **Cross-modal essential**: Network analysis + statistics reveal patterns
3. **Uncertainty varies by component**: Not uniform across analysis
4. **Theory guides focus**: Each theory highlights different aspects

---

## Critical Success Factors

### Technical Requirements
1. **Consistent entity IDs** across all representations and theories
2. **Provenance tracking** from source text through all transformations
3. **Confidence propagation** through analytical pipeline
4. **Theory-aware extraction** that respects each theory's focus

### Research Requirements
1. **Theory fidelity** through documented operationalization
2. **Transparent limitations** in uncertainty reporting
3. **Reproducible workflows** via YAML serialization
4. **Academic rigor** in validation methodology

### Practical Requirements
1. **Computational efficiency** for reasonable dataset sizes
2. **User-friendly interface** hiding complexity
3. **Flexible configuration** for diverse research needs
4. **Incremental results** enabling iterative research

---

## Final Assessment

### Where This System Adds Unique Value

1. **Scaling Qualitative Analysis**: Apply multiple theories to large corpora impossible to analyze manually
2. **Theory Comparison**: Systematic comparison of theoretical explanations on same data
3. **Mixed Methods Integration**: Combine network, statistical, and semantic analysis fluidly
4. **Uncertainty Transparency**: Know confidence in each analytical component

### Honest Limitations

1. **Theory Simplification**: Complex theories reduced to operationalizable components
   - **Mitigation**: Document all simplifications explicitly
2. **LLM Consistency**: Instance-level variation in extractions
   - **Mitigation**: MCL/DOLCE layering provides conceptual stability
3. **Validation Challenges**: No ground truth for many social phenomena
   - **Mitigation**: Multi-level validation and cross-theory robustness checks
4. **Academic Acceptance**: Computational operationalization may face resistance
   - **Mitigation**: Frame as augmentation, include theory experts as collaborators

### Path to Success

1. **Start with well-understood theories** (Social Network, Diffusion)
2. **Partner with domain experts** for theory validation
3. **Build incrementally** with vertical slice approach
4. **Embrace uncertainty** as feature not bug
5. **Focus on augmentation** not automation of research

The system's value lies not in perfect theory implementation but in **systematic, scalable, transparent application** of theoretical frameworks to empirical data at unprecedented scale.

---

## Updated Assessment After Deep Dive

### No Longer Concerns

1. **Theory Schema Creation Bottleneck** - Already automated via lit_review extraction
2. **Critical Theory Operationalization** - Shown to be feasible through heuristic encoding
3. **Scale Requirements** - Moderate scale sufficient for demonstrating value
4. **Post-hoc vs Synchronized** - Synchronized approach correctly maintains traceability
5. **Theory × Mode × Uncertainty Explosion** - Manageable with proper abstraction
6. **Operationalizing Vague Concepts** - Documentation of decisions advances theory

### Remaining Considerations (All Addressed)

1. **LLM Consistency** - SOLVED through entity resolution post-processing
   ```python
   # Standard knowledge graph approach
   clusters = semantic_clustering(["Bill Gates", "Mr. Gates", "Former Microsoft CEO"])
   canonical_entity = merge_to_canonical(clusters)  # → "Bill Gates"
   ```

2. **Theory Operationalization Disagreements** - FEATURE not bug
   - Multiple operationalizations can be tested and compared
   - Best performing operationalization emerges empirically
   - Advances theory by making implicit assumptions explicit

3. **Validation Approaches** - MULTIPLE solutions available
   - Predictive validation (which operationalization predicts best)
   - Statistical validation (relational DB enables rigorous testing)
   - Qualitative validation (LLMs with research capabilities)
   - Cross-theory robustness (convergent findings across theories)

### Key Innovations Recognized

1. **Four-Tier Analysis Framework** - Clear value progression without causal claims
2. **Automated Theory Extraction** - Game-changing for feasibility
3. **Layered Ontology for Consistency** - Elegant solution to LLM variation
4. **Explicit Operationalization** - Advances theory through forced precision
5. **Multi-Theory Comparison** - Novel contribution to computational social science
6. **Theory Extensibility** - Three ways to handle novel phenomena:
   - Automated paper ingestion → theory schema
   - User-defined custom theories
   - Grounded theory emergence from data
7. **Full Traceability** - Every analytical decision documented and traceable

### Clear Value Proposition: The RAND Use Case

**Current State**: Million-dollar analyses taking months with teams of experts
**KGAS Solution**: Automated, faster, more rigorous, fully traceable, fraction of cost

Target users are **not** grad students with keyword search but **organizations paying millions** for policy analyses that can be automated better.

### Final Verdict

The system is **not just feasible but necessary**. All major critiques have been addressed:
- Entity resolution handles consistency
- Multiple validation approaches available  
- Theory extensibility handles coverage
- Clear use case with demonstrated value

The remaining challenges are **engineering execution** rather than conceptual barriers. The key insight: **This isn't competing with simple tools - it's automating expensive expert analysis.**

---

## Implementation Priorities Based on RAND Use Case

### Immediate Value Demonstration

1. **Pick 2-3 RAND-relevant theories** (e.g., Stakeholder Theory, Diffusion of Innovations)
2. **Select a recent RAND analysis** as benchmark comparison
3. **Show speed improvement** (weeks → hours)
4. **Demonstrate depth** (more theories applied systematically)
5. **Highlight traceability** (every finding linked to source)

### MVP for Policy Analysis

```python
# Minimum viable system for RAND-style analysis
class PolicyAnalysisMVP:
    theories = ["stakeholder_theory", "diffusion_theory", "framing_theory"]
    
    def analyze_policy_discourse(self, documents):
        # 1. Extract entities across theories
        entities = self.multi_theory_extraction(documents)
        
        # 2. Build knowledge graph
        graph = self.construct_graph(entities)
        
        # 3. Run cross-modal analysis
        findings = {
            "network": self.analyze_influence_networks(graph),
            "statistical": self.analyze_correlations(graph.to_table()),
            "temporal": self.analyze_evolution(graph.temporal_view())
        }
        
        # 4. Generate traceable report
        return self.generate_policy_report(findings)
```

### Scaling Strategy

1. **Start with single policy domain** (e.g., climate policy)
2. **Prove value on real RAND projects**
3. **Expand theory library based on demand**
4. **Build custom theories for specific analyses**
5. **Eventually: RAND theory repository**

### Key Differentiators for RAND

- **Multi-theory application**: Apply 10+ theories systematically (vs 1-2 manually)
- **Speed**: Days not months
- **Completeness**: Analyze entire corpora, not samples
- **Consistency**: Same methodology across projects
- **Traceability**: Every claim linked to evidence
- **Cost**: Fraction of current manual analysis

The path to success is demonstrating clear value on actual RAND analyses, not abstract academic examples.

---

## Stress Testing Insights from Stakeholder Theory v10.0

### Schema Validation and Edge Case Discovery

During comprehensive stress testing of the stakeholder theory v10.0 implementation, several critical issues emerged that inform future schema development and validation approaches:

#### **Issue 1: Mathematical Formula Ambiguity**
**Problem**: The Mitchell-Agle-Wood geometric mean formula `(legitimacy * urgency * power) ^ (1/3)` is undefined when any input is zero, but this boundary case wasn't addressed in the test cases.

**Discovery**: 
```json
{
  "inputs": {"legitimacy": 1.0, "urgency": 0.0, "power": 0.8},
  "mathematical_result": "0.0",
  "theoretical_meaning": "Should a stakeholder with zero urgency have zero salience even with high legitimacy and power?"
}
```

**Schema Improvement Required**:
- Add boundary case handling to custom script specifications
- Include zero-value test cases explicitly
- Document mathematical vs theoretical interpretation of edge cases
- Consider modified geometric mean that handles zeros gracefully

#### **Issue 2: Prompt Consistency Across LLM Models**
**Problem**: Theory schemas include specific prompts, but different LLM models may interpret these prompts differently, leading to inconsistent operationalization.

**Discovery**: The legitimacy assessment prompt assumes certain legal/moral frameworks that may vary across cultural contexts or model training.

**Schema Enhancement Needed**:
```json
"llm_prompts": {
  "extraction_prompt": "...",
  "model_specific_variations": {
    "gpt-4": "Emphasize precise legal definitions",
    "claude": "Focus on nuanced moral reasoning",
    "llama": "Use concrete examples for clarity"
  },
  "consistency_validation": {
    "test_examples": [...],
    "acceptable_variance": 0.15
  }
}
```

#### **Issue 3: Dynamic Relationship Modeling Gaps**
**Problem**: Current schema handles static stakeholder attributes well but struggles with evolving relationships and legitimacy changes over time.

**Discovery**: A stakeholder's legitimacy can shift rapidly (e.g., activist group gains legitimacy through media coverage), but the schema doesn't capture this temporal dimension.

**Required Schema Extensions**:
- Temporal versioning for entity properties
- Event-triggered property updates
- Dynamic relationship strength modeling
- Time-decay functions for urgency

#### **Issue 4: Cross-Modal Semantic Preservation**
**Problem**: When converting from graph to table representation, stakeholder relationship semantics may be lost or oversimplified.

**Specific Example**: The relationship "INFLUENCES" becomes a simple numeric score in table format, losing context about influence mechanism and conditionality.

**Solution Framework**:
```json
"cross_modal_mappings": {
  "semantic_preservation_rules": [
    {
      "relationship": "INFLUENCES",
      "table_columns": ["influence_strength", "influence_mechanism", "conditionality"],
      "semantic_validation": "Ensure mechanism and conditionality preserved in table view"
    }
  ]
}
```

#### **Issue 5: Boundary Case Documentation Insufficient**
**Problem**: The validation section includes boundary cases but doesn't specify expected system behavior for each case with sufficient precision.

**Enhanced Boundary Case Specification Needed**:
```json
"boundary_cases": [
  {
    "case_description": "Stakeholder with negative legitimacy (actively harmful claims)",
    "input_example": "Terrorist group demanding policy changes",
    "expected_legitimacy_score": 0.0,
    "expected_salience_impact": "Zero salience regardless of power/urgency",
    "system_behavior": "Flag as negative stakeholder, exclude from priority calculations",
    "validation_criteria": "legitimacy < 0.1 AND salience = 0.0 AND flagged = true"
  }
]
```

### Key Insights for Schema v11.0 Development

#### **1. Comprehensive Edge Case Coverage**
Future theory schemas must include:
- Mathematical boundary cases (zeros, negatives, extremes)
- Cultural/contextual variations in interpretation
- Temporal dynamics and change scenarios
- Cross-modal conversion edge cases

#### **2. Multi-Model Prompt Engineering**
```json
"prompt_engineering": {
  "base_prompt": "Core prompt applicable to all models",
  "model_adaptations": {
    "risk_assessment": "Identify which models need specific guidance",
    "validation_strategy": "Cross-model consistency testing required"
  },
  "fallback_mechanisms": "Simple prompts for model-agnostic behavior"
}
```

#### **3. Temporal Modeling Requirements**
Social science theories often involve dynamic processes that current schema handles inadequately:
- Stakeholder legitimacy evolution
- Urgency decay over time
- Power relationship changes
- Coalition formation and dissolution

#### **4. Semantic Preservation Architecture**
Cross-modal analysis must preserve theoretical meaning:
- Relationship semantics maintained in all representations
- Context-dependent properties properly encoded
- Theoretical constraints enforced across modes

#### **5. Validation Automation Framework**
```python
class TheorySchemaValidator:
    def stress_test_schema(self, schema):
        edge_cases = self.generate_edge_cases(schema)
        model_consistency = self.test_cross_model_prompts(schema)
        temporal_validity = self.test_dynamic_scenarios(schema)
        semantic_preservation = self.test_cross_modal_conversion(schema)
        
        return ValidationReport({
            "edge_case_coverage": edge_cases,
            "model_consistency": model_consistency,
            "temporal_handling": temporal_validity,
            "semantic_integrity": semantic_preservation
        })
```

### Immediate Actions Required

1. **Update Theory Meta-Schema v10.0** to include enhanced boundary case specifications
2. **Develop validation automation** for systematic schema testing
3. **Create model-specific prompt guidelines** for cross-LLM consistency
4. **Design temporal modeling extensions** for dynamic theories
5. **Implement semantic preservation validation** for cross-modal operations

### Strategic Implications

**For Theory Schema Authors**: Must think more systematically about edge cases and model variations when encoding theories.

**For System Implementation**: Need robust validation framework that catches mathematical and semantic inconsistencies before deployment.

**For Research Users**: Enhanced transparency about limitations and edge case handling builds trust in automated theory application.

**For KGAS Architecture**: Validates the importance of the validation framework as a core system component, not an afterthought.

### Stress Testing as Standard Practice

This stress testing revealed that **theoretical soundness** and **implementation robustness** are distinct concerns requiring different validation approaches. Future theory development should include:

1. **Theoretical Validation**: Does the schema capture the theory accurately?
2. **Mathematical Validation**: Are formulas and calculations robust to edge cases?
3. **Implementation Validation**: Do prompts and tools work consistently across contexts?
4. **Semantic Validation**: Is meaning preserved across representational transformations?

The stakeholder theory stress test demonstrates both the **power and necessity** of systematic schema validation in theory-aware systems.

---

## Contract System Analysis & Data Type Architecture Evolution

### Existing Contract System Assessment

After comprehensive analysis of the existing KGAS contract and compatibility system, several key insights emerged:

#### **Strengths of Current System**
- **121 Tool Contracts**: Comprehensive YAML-based contracts for all tools
- **Contract Validator**: Sophisticated validation engine with schema enforcement
- **MCP Integration**: All tools accessible via Model Context Protocol
- **Data Model Standardization**: BaseObject foundation with quality tracking
- **Cross-Modal Support**: Built-in graph/table/vector conversion capabilities
- **Provenance Tracking**: Complete audit trail through entire pipeline
- **Theory Integration Framework**: Theory-aware contracts and validation

#### **Critical Gaps Identified**
1. **Theory Meta-Schema v10.0 Integration**: Existing contracts don't fully support custom script validation, multi-model prompt consistency, or systematic edge case testing
2. **Theory-Tool Mapping Ambiguity**: Current approach requires tools to declare theory support, creating N×M complexity
3. **Cross-Modal Semantic Preservation**: No systematic validation that meaning is preserved during format conversions
4. **Custom Algorithm Validation**: No automated testing of custom implementations against theory-specified test cases

### **Architectural Evolution: From Concepts to Data Types**

#### **Original Hierarchy Problems**
```
Theories → Tools (Direct coupling, N×M explosion)
```

#### **First Refinement: MCL-Mediated**
```
Theories → MCL Concepts → Tools (Better, but still concept-focused)
```

#### **Superior Architecture: Data Type Foundation**
```
Theories → MCL Concepts → Operationalizations → Data Types (Pydantic Schemas)
```

### **Data Type Architecture Benefits**

#### **1. Universal Composability via Pydantic Schemas**
```python
# Tools declare data shapes, not domain concepts
class LegitimacyScore(BaseModel):
    value: float = Field(ge=0.0, le=1.0)
    evidence_type: Literal["legal", "moral", "contractual"]
    confidence: float = Field(ge=0.0, le=1.0)
    source_mentions: List[str]

class StakeholderEntity(BaseModel):
    canonical_name: str
    entity_type: Literal["individual", "organization", "group"]
    legitimacy: LegitimacyScore
    urgency: UrgencyScore
    power: PowerScore
```

#### **2. Schema-Based Tool Contracts**
```yaml
tool_id: "T23A_SPACY_NER"
data_contracts:
  produces:
    - schema: "EntityMention" 
      fields: ["surface_text", "position", "entity_type", "confidence"]
  consumes:
    - schema: "TextChunk"
      fields: ["text", "document_ref", "position"]
```

#### **3. Theory as Data Requirements**
```json
{
  "theory_id": "stakeholder_theory",
  "data_requirements": {
    "input_schemas": ["EntityMention", "TextChunk"],
    "output_schemas": ["StakeholderEntity", "SalienceScore"],
    "transformations": [
      {
        "from": "EntityMention",
        "to": "StakeholderEntity", 
        "algorithm": "stakeholder_classification",
        "validation_schema": "StakeholderValidation"
      }
    ]
  }
}
```

### **Cross-Modal Architecture: N-ary Relations & Reification**

#### **Graph Representation (Reified N-ary Relations)**
```cypher
// Reified relationship node supports complex n-ary relations
CREATE (r:STAKEHOLDER_INFLUENCE {
  id: "rel_001",
  influence_strength: 0.7,
  mechanism: "media_pressure", 
  conditionality: "crisis_only",
  temporal_scope: "2024-Q1"
})

// Connect to all participants
CREATE (stakeholder)-[:INFLUENCES_VIA]->(r)
CREATE (r)-[:TARGETS]->(organization)
CREATE (r)-[:THROUGH_MECHANISM]->(media_outlet)
```

#### **Table Representation (N-ary Relation as Row)**
```python
class InfluenceRelation(BaseModel):
    stakeholder_id: str
    target_id: str
    mechanism_id: str  # Third party participant
    influence_strength: float
    mechanism: str
    conditionality: str
    temporal_scope: str
    
# Each table row = complete n-ary relation with all participants
```

#### **Schema-Guaranteed Semantic Preservation**
```python
class NaryRelationSchema(BaseModel):
    """Ensures n-ary relations preserve semantics across modes"""
    participants: List[str]  # All entity participants
    relation_type: str
    properties: Dict[str, Any]  # All relation properties
    
    def to_graph_nodes(self) -> List[CypherNode]:
        # Convert to reified relationship nodes
    
    def to_table_row(self) -> Dict[str, Any]:
        # Convert to flat table row
    
    def validate_semantic_equivalence(self, other: 'NaryRelationSchema') -> bool:
        # Ensure conversions preserve meaning
```

### **Implementation Benefits of Data Type Architecture**

#### **1. Automatic Pipeline Generation**
```python
def find_compatible_pipeline(input_schema, output_schema):
    # Graph search through data transformations
    return shortest_path(input_schema, output_schema, tool_graph)
```

#### **2. Type Safety Throughout System**
```python
def validate_tool_chain(tools: List[Tool]) -> bool:
    for i in range(len(tools) - 1):
        output_schema = tools[i].produces
        input_schema = tools[i+1].consumes
        if not schema_compatible(output_schema, input_schema):
            return False
    return True
```

#### **3. Automatic Test Generation**
```python
def generate_test_data(schema: BaseModel) -> Dict:
    return schema.schema()["example"]

def test_tool_contract(tool: Tool):
    for input_schema in tool.consumes:
        test_data = generate_test_data(input_schema)
        result = tool.execute(test_data)
        validate_against_schema(result, tool.produces)
```

### **Contract System Enhancement Strategy**

#### **Phase 1: Data Type Foundation**
1. **Define Core Pydantic Schemas** - Entity, Relationship, Mention, etc.
2. **Update Tool Contracts** - Tools declare data shapes they produce/consume
3. **Schema-Based Validation** - Automatic validation at every tool boundary

#### **Phase 2: Cross-Modal Schema Preservation**
4. **N-ary Relation Schema** - Base schema for complex relationships
5. **Cross-Modal Converters** - Schema-preserving graph ↔ table conversion
6. **Semantic Validation Tests** - Ensure conversions preserve meaning

#### **Phase 3: Automatic Pipeline Generation**
7. **Pipeline Planning** - Automatic tool chain discovery via schema compatibility
8. **Theory-Data Mapping** - Theories declare required data schemas
9. **End-to-End Validation** - Complete pipeline validation via schema checking

### **Key Architectural Insights**

#### **1. Data Types as Universal Language**
- Tools speak in data types, not domain concepts
- Theories translate to data requirements  
- System automatically builds valid transformations
- Type safety guarantees correctness
- Cross-modal conversion preserves semantics through schema contracts

#### **2. Eliminates Architectural Tensions**
- **No N×M Theory-Tool Explosion**: Tools declare data shapes, system determines compatibility
- **Universal Composability**: Any tool producing schema X can feed any tool consuming schema X
- **Automatic Validation**: Pydantic schemas enable automatic test generation and validation
- **Semantic Preservation**: Schema contracts ensure meaning preservation across conversions

#### **3. Leverages Existing Infrastructure**
- Current contract system provides excellent foundation
- Shift from "capability declarations" to "data shape contracts"
- Pydantic as universal schema language
- Existing validation framework extends naturally to schema validation

### **Strategic Decision: Deprioritize LLM Consistency**

**Rationale**: Multi-model prompt consistency testing determined to be lower priority because:
- Expert humans show similar variation in entity classification tasks
- Inter-rater reliability is a known challenge in qualitative coding
- System can build in reliability metrics later in implementation roadmap
- Core data type architecture provides more fundamental value

**Focus Instead On**: Data shape contracts, schema-based validation, and cross-modal semantic preservation through type-safe transformations.

---

## Refined Implementation Considerations

### Performance Optimization Through MCL

**Challenge**: Avoid redundant LLM calls when applying multiple theories to same documents

**Solution**: MCL-based extraction strategy
```python
class MCLBasedExtraction:
    def extract_comprehensive_entities(self, document):
        # Phase 1: Theory-agnostic extraction (single LLM call)
        raw_extraction = extract_all_possible_entities(document)
        
        # Map to MCL universal concepts
        mcl_mapped = map_to_mcl_concepts(raw_extraction)
        
        return mcl_mapped
    
    def apply_theory_lens(self, mcl_entities, theory):
        # Phase 2: Theory-specific interpretation (no additional LLM calls)
        # Reinterpret MCL concepts through theory lens
        
        if theory == "stakeholder_theory":
            return reinterpret_as_stakeholders(mcl_entities)
        elif theory == "institutional_theory":
            return reinterpret_as_institutional_actors(mcl_entities)
```

**Key Insight**: MCL provides "universal language" that theories interpret without re-extraction

### Edge Case Handling Strategy

**Development Mode**: Fail fast for debugging
```python
if self.mode == "development":
    raise EdgeCaseException(f"Unhandled case: {case_type}")
```

**Production Mode**: Uncertainty metrics + LLM intelligence
```python
uncertainty = self.compute_edge_case_uncertainty(case_type)
if uncertainty > threshold:
    response = self.llm.handle_novel_situation(context)
    return {
        "result": response,
        "uncertainty": uncertainty,
        "handling": "llm_intelligent_response"
    }
```

**Rationale**: Better to fail explicitly during development than provide degraded quality. In production, use LLM general intelligence rather than hardcoded fallbacks.

### Pipeline Stage Storage for Interactivity

**Design Principle**: Store every intermediate stage for maximum traceability and control

```python
class PipelineStateManager:
    def save_stage(self, stage_name, stage_data, inputs, outputs):
        # Enable resumption from any point
        stage_id = f"{stage_name}_{timestamp()}"
        self.stages[stage_id] = {
            "data": stage_data,
            "inputs": inputs,
            "outputs": outputs,
            "can_resume_from": True
        }
    
    def resume_from_stage(self, stage_id):
        # Interactive capability
        return PipelineResumption(starting_point=stage)
    
    def modify_and_rerun(self, stage_id, modifications):
        # Change parameters mid-analysis
        return self.resume_from_modified_stage(stage_id, modifications)
```

**Enables**:
- Add documents → Resume from entity extraction stage
- Change theories → Resume from theory application stage
- Adjust parameters → Resume from analysis stage
- Full traceability → Every stage inspectable

### Theory Validation Protocol

**Challenge**: Ensure automated theory extraction accurately captures theory

**Solution**: LLM-based validation rather than human SME
```python
class TheoryValidationProtocol:
    def validate_extracted_schema(self, paper_pdf, extracted_schema):
        # Generate synthetic examples using schema
        examples = self.generate_from_schema(extracted_schema)
        
        # LLM expert validation
        validation_prompt = f"""
        Given this theory paper: {paper_pdf}
        Do these examples correctly apply the theory?
        {examples}
        Rate accuracy and explain discrepancies.
        """
        
        return self.expert_llm.validate(validation_prompt)
```

### Tiered LLM Strategy (Configurable)

**Cost Optimization**: Use appropriate model for each task
- **Screening**: Fast, cheap model for initial filtering
- **Extraction**: Accurate model for entity extraction  
- **Reasoning**: Powerful model for complex analysis
- **Validation**: Simple model for binary checks

**Configuration**: Users can adjust model selection based on budget/accuracy tradeoffs

### Key Design Decisions Clarified

1. **Feedback Loops**: Out of scope for initial system
2. **Edge Cases**: Uncertainty metrics + explicit failures preferred over graceful degradation
3. **Theory Application**: MCL enables efficient multi-theory analysis
4. **User Control**: Pipeline storage enables interactive analysis without loss of traceability
5. **Validation**: LLM-based theory validation more scalable than human experts

These refinements maintain the system's analytical sophistication while addressing practical implementation concerns.

---

## Practical Implementation Deep Dive

### Theory Meta-Schema Extensions for Real-World Execution

**Core Challenge**: Bridging the gap between abstract theory schemas and concrete implementation

**Solution**: Extended schema structure with embedded execution details

```json
{
  "theory_id": "stakeholder_theory",
  "process": {
    "steps": [
      {
        "step_id": "identify_stakeholders",
        "method": "llm_extraction",
        "prompts": {
          "extraction_prompt": "Identify all entities that have a stake in the organization's decisions. Look for: employees, customers, shareholders, regulators, communities...",
          "validation_prompt": "Does this entity have legitimate interest, power, or urgency regarding the organization?"
        },
        "outputs": ["stakeholder_entities"],
        "tool_mapping": "entity_extractor_mcp"
      },
      {
        "step_id": "custom_salience_calculation",
        "method": "custom_script",
        "script_requirements": {
          "inputs": {"legitimacy": "float", "urgency": "float", "power": "float"},
          "outputs": {"salience_score": "float"},
          "business_logic": "salience = (legitimacy * urgency * power) ^ (1/3)",
          "implementation_hint": "Geometric mean of three dimensions",
          "test_cases": [
            {"inputs": {"legitimacy": 1.0, "urgency": 1.0, "power": 1.0}, "expected_output": 1.0},
            {"inputs": {"legitimacy": 0.8, "urgency": 0.6, "power": 0.4}, "expected_output": 0.573}
          ]
        },
        "tool_contracts": ["input_validator", "output_formatter"]
      }
    ]
  }
}
```

### Key Schema Extensions Required

#### 1. Embedded Prompts for LLM Steps
**Rationale**: Solves the "how do we translate theory concepts to LLM prompts" problem
- Store extraction prompts directly in theory schema
- Include validation prompts for quality control
- Enable theory-specific prompt engineering

#### 2. Custom Script Specifications
**Structure**: Define inputs, outputs, business logic, and validation
- **Inputs/Outputs**: Strict typing for Claude Code implementation
- **Business Logic**: Plain language description of algorithm
- **Implementation Hints**: Pseudo-code or mathematical formulas
- **Test Cases**: Validation examples to verify correctness
- **Tool Contracts**: Interface requirements for system integration

#### 3. Tool Mapping Strategy
**Approach**: LLM intelligence for dynamic mapping
```python
class ToolMapper:
    def map_theory_to_tools(self, theory_step, available_tools):
        mapping_prompt = f"""
        Theory step: {theory_step}
        Available tools: {available_tools}
        
        Which tool best implements this theoretical concept?
        Consider: purpose, inputs/outputs, parameters
        If no perfect match, suggest custom script requirements.
        """
        return self.llm.determine_mapping(mapping_prompt)
```

#### 4. Parameter Adaptation Logic
**For tool parameter mismatches**:
```json
"parameter_adaptation": {
  "method": "wrapper_script", 
  "wrapper_logic": "Transform stakeholder_salience to tool's weight parameter",
  "implementation": "weight = normalize(salience_score, min=0.1, max=1.0)"
}
```

### Decision Authority Framework

**Primary Decision Maker**: LLM Agent (Claude Code as orchestrating brain)
- **Theory Selection**: Agent analyzes query and selects appropriate theories
- **Operationalization Choices**: Agent makes reasonable interpretations of vague concepts
- **Tool Mapping**: Agent determines best tool for each theoretical requirement
- **Parameter Setting**: Agent sets reasonable defaults with user override capability

**Human Override**: Available at all decision points for expert users
**Traceability**: All decisions logged with rationale

### Custom Algorithm Implementation Strategy

**Process**:
1. Theory schema defines algorithm requirements (inputs, outputs, logic)
2. Claude Code writes implementation based on specification
3. System validates against test cases
4. Tool contracts ensure compatibility with rest of system

**Validation Approach**:
- Include test cases in schema for automatic validation
- Business logic description guides implementation
- Tool contracts enforce interface compatibility

**Example Algorithm Specification**:
```json
"custom_algorithm": {
  "algorithm_name": "stakeholder_salience",
  "description": "Calculate stakeholder salience using Mitchell-Agle-Wood model",
  "inputs": {
    "legitimacy": {"type": "float", "range": [0,1], "description": "Stakeholder's legitimate claim"},
    "urgency": {"type": "float", "range": [0,1], "description": "Time-critical nature of claim"},
    "power": {"type": "float", "range": [0,1], "description": "Ability to influence organization"}
  },
  "outputs": {
    "salience_score": {"type": "float", "range": [0,1], "description": "Overall stakeholder importance"}
  },
  "business_logic": "Geometric mean of three dimensions provides balanced weighting",
  "implementation_hint": "salience = (legitimacy * urgency * power) ^ (1/3)",
  "validation_rules": ["all_inputs_required", "output_bounds_check"],
  "tool_contracts": ["stakeholder_data_interface", "influence_score_interface"],
  "test_cases": [
    {"inputs": {"legitimacy": 1.0, "urgency": 1.0, "power": 1.0}, "expected_output": 1.0},
    {"inputs": {"legitimacy": 0.8, "urgency": 0.6, "power": 0.4}, "expected_output": 0.573}
  ]
}
```

### Uncertainty and Traceability: Configurable Approach

**Assessment**: Storage overhead is not a real problem
- Modern systems handle millions of log entries routinely
- Insights are more valuable than storage efficiency
- Configurable verbosity addresses user preferences

**Tracing Configuration**:
```python
class TracingConfig:
    levels = {
        "minimal": ["major_decisions", "final_outputs"],
        "standard": ["theory_selection", "tool_mapping", "parameter_choices"],
        "verbose": ["every_llm_call", "every_threshold", "every_validation"],
        "debug": ["everything"]
    }
```

**Design Principle**: Everything configurable, no hardcoded values
- User controls tracing verbosity
- Expert users can access full decision history
- Casual users see simplified summaries

### Tool Contract System

**Purpose**: Ensure compatibility between custom scripts and system tools

**Contract Structure**:
```python
class ToolContract:
    def __init__(self, contract_name):
        self.input_schema = {}
        self.output_schema = {}
        self.validation_rules = []
        self.interface_requirements = []
    
    def validate_implementation(self, custom_script):
        # Ensure custom script meets contract requirements
        return validation_result
```

**Benefits**:
- Custom algorithms integrate seamlessly with predefined tools
- Type safety across theory implementations
- Consistent interfaces enable tool interoperability

### Implementation Feasibility Assessment

**VERDICT: FEASIBLE** with extended schema approach

**Combination of capabilities that makes it work**:
1. **Structured schema** for standard operations
2. **LLM intelligence** for mapping and adaptation
3. **Claude Code** for custom implementation
4. **Configurable tracing** for transparency
5. **Tool contracts** for system integration

**Critical Success Factors**:
- Theory schemas must include execution details (prompts, algorithms, tests)
- LLM agent handles dynamic decision-making
- Custom script specifications enable flexible algorithm implementation
- Tool contracts ensure system-wide compatibility

**Recommended Validation Approach**: Prototype with stakeholder theory to test extended schema approach before broader implementation.