# KGAS Evergreen Documentation: Theoretical Foundation and Core Concepts

**Document Version**: 1.0 (Consolidated)  
**Created**: 2025-01-27  
**Purpose**: Single source of truth for all theoretical foundations, core concepts, and architectural principles of the Knowledge Graph Analysis System (KGAS)

---

## 🎯 System Overview

The Knowledge Graph Analysis System (KGAS) is built upon a comprehensive theoretical framework that integrates:

1. **DOLCE Upper Ontology**: Formal ontological foundation providing semantic precision and interoperability
2. **FOAF + SIOC Social Web Schemas**: Established vocabularies for social relationships and online interactions with KGAS extensions
3. **Theory Meta-Schema**: A computable framework for representing social science theories as structured, machine-readable schemas
4. **Master Concept Library**: A standardized vocabulary of social science concepts with precise definitions and multi-ontology alignment
5. **Object-Role Modeling (ORM)**: A conceptual modeling methodology ensuring semantic precision and data consistency
6. **Three-Dimensional Theoretical Framework**: A typology categorizing social theories by scope, mechanism, and domain
7. **Programmatic Contract System**: YAML/JSON contracts with Pydantic validation for ensuring compatibility and robustness

---

## 🏗️ Complete System Architecture (Planned)

The following diagram illustrates the complete planned architecture showing how DOLCE ontological grounding integrates with theory-aware processing:

```
╔══════════════════════════════════════════════════════════════════════════════════════╗
║                    KGAS: THEORY-AWARE KNOWLEDGE GRAPH ANALYSIS                      ║
║                          Complete Planned Architecture                               ║
╚══════════════════════════════════════════════════════════════════════════════════════╝

┌─ ONTOLOGICAL FOUNDATION ────────────────────────────────────────────────────────────────┐
│                                                                                         │
│  🏛️ DOLCE UPPER ONTOLOGY                                                               │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐  │
│  │ Descriptive Ontology for Linguistic and Cognitive Engineering                  │  │
│  │                                                                                 │  │
│  │ dolce:Endurant ────► Persistent entities (Person, Organization)                │  │
│  │ dolce:Perdurant ───► Temporal entities (Event, Process, Meeting)               │  │
│  │ dolce:Quality ─────► Properties (Credibility, Influence, Trust)                │  │
│  │ dolce:Abstract ────► Conceptual entities (Theory, Policy, Ideology)            │  │
│  │ dolce:SocialObject ► Socially constructed (Institution, Role, Status)          │  │
│  │                                                                                 │  │
│  │ Provides: Formal semantics, ontological consistency, interoperability          │  │
│  └─────────────────────────────────────────────────────────────────────────────────┘  │
│                                           │                                             │
│                                           ▼                                             │
│  📖 MASTER CONCEPT LIBRARY (MCL) + DOLCE ALIGNMENT                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐  │
│  │ Domain-Specific Concepts with DOLCE Grounding                                  │  │
│  │                                                                                 │  │
│  │ SocialActor:                    MediaOutlet:                   PolicyEvent:    │  │
│  │ ├─ indigenous_term: ["person"]  ├─ indigenous_term: ["news"]   ├─ indigenous.. │  │
│  │ ├─ upper_parent: dolce:SocialObject ├─ upper_parent: dolce:SocialObject      │  │
│  │ ├─ dolce_constraints:           ├─ dolce_constraints:          ├─ upper_parent │  │
│  │ │  └─ category: "endurant"      │  └─ category: "endurant"     │   dolce:Perdu │  │
│  │ └─ validation: ontological     └─ validation: ontological     └─ category: "pe│  │
│  │                                                                                 │  │
│  │ Indigenous Terms → MCL Canonical → DOLCE IRIs → Validation                     │  │
│  └─────────────────────────────────────────────────────────────────────────────────┘  │
│                                           │                                             │
└───────────────────────────────────────────┼─────────────────────────────────────────────┘
                                            │
                                            ▼
┌─ THEORETICAL FRAMEWORK ─────────────────────────────────────────────────────────────────┐
│                                                                                         │
│  📚 THEORY META-SCHEMA + DOLCE VALIDATION                                              │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐  │
│  │ Social Science Theories as DOLCE-Validated Computable Schemas                  │  │
│  │                                                                                 │  │
│  │ social_identity_theory:                                                        │  │
│  │ ├─ entities:                                                                   │  │
│  │ │  ├─ InGroupMember:                                                           │  │
│  │ │  │  ├─ mcl_id: "SocialActor"                                                 │  │
│  │ │  │  ├─ dolce_parent: "dolce:SocialObject"  ◄─── DOLCE Grounding             │  │
│  │ │  │  └─ validation: ontologically_sound                                       │  │
│  │ │  └─ GroupIdentification:                                                     │  │
│  │ │     ├─ mcl_id: "SocialProcess"                                               │  │
│  │ │     ├─ dolce_parent: "dolce:Perdurant"   ◄─── DOLCE Grounding               │  │
│  │ │     └─ validation: temporal_constraints                                      │  │
│  │ ├─ relationships:                                                              │  │
│  │ │  └─ "identifies_with" (SocialObject → SocialObject) ✓ DOLCE Valid          │  │
│  │ └─ 3D_classification: [Meso, Whom, Agentic]                                   │  │
│  └─────────────────────────────────────────────────────────────────────────────────┘  │
│                                           │                                             │
│  🔧 OBJECT-ROLE MODELING + DOLCE                                                       │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐  │
│  │ • Object Types → DOLCE Categories                                              │  │
│  │ • Fact Types → Ontologically Valid Relations                                   │  │
│  │ • Constraints → DOLCE Consistency Rules                                        │  │
│  │ • Natural Language → Formal DOLCE Semantics                                    │  │
│  └─────────────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                            │
                                            ▼
┌─ DOLCE-AWARE PROCESSING PIPELINE ───────────────────────────────────────────────────────┐
│                                                                                         │
│  📄 DOCUMENT INPUT                   🤖 DOLCE-VALIDATED EXTRACTION                     │
│  ┌─────────────────┐                 ┌─────────────────────────────────┐               │
│  │ Research        │────────────────►│ LLM + Theory Schema + DOLCE     │               │
│  │ Documents       │                 │                                 │               │
│  │                 │                 │ • Domain Conversation           │               │
│  │ "Biden announced│                 │ • MCL-Guided Extraction         │               │
│  │ new policy"     │                 │ • DOLCE Validation:             │               │
│  │                 │                 │   - "Biden" → SocialActor →     │               │
│  │                 │                 │     dolce:SocialObject ✓        │               │
│  │                 │                 │   - "announced" → Process →     │               │
│  │                 │                 │     dolce:Perdurant ✓           │               │
│  │                 │                 │   - Relation: participatesIn ✓  │               │
│  └─────────────────┘                 └─────────────────────────────────┘               │
│           │                                           │                                 │
│           ▼                                           ▼                                 │
│  📊 CROSS-MODAL ANALYSIS + DOLCE QUALITY ASSURANCE                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐  │
│  │                                                                                 │  │
│  │  🌐 GRAPH MODE          📋 TABLE MODE          🔍 VECTOR MODE                   │  │
│  │  ┌─────────────┐       ┌─────────────┐       ┌─────────────┐                   │  │
│  │  │DOLCE-Valid  │       │Ontologically│       │Semantically │                   │  │
│  │  │Entities     │◄─────►│Grounded     │◄─────►│Consistent   │                   │  │
│  │  │Relations    │       │Aggregations │       │Embeddings   │                   │  │
│  │  │Centrality   │       │Statistics   │       │Clustering   │                   │  │
│  │  └─────────────┘       └─────────────┘       └─────────────┘                   │  │
│  │                                                                                 │  │
│  │              🔍 DOLCE VALIDATION LAYER                                          │  │
│  │              ┌─────────────────────────────────────────────┐                   │  │
│  │              │ • Entity-Role Consistency Checking          │                   │  │
│  │              │ • Relationship Ontological Soundness       │                   │  │
│  │              │ • Temporal Constraint Validation           │                   │  │
│  │              │ • Cross-Modal Semantic Preservation        │                   │  │
│  │              └─────────────────────────────────────────────┘                   │  │
│  └─────────────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                            │
                                            ▼
┌─ ONTOLOGICALLY-GROUNDED RESEARCH OUTPUT ────────────────────────────────────────────────┐
│                                                                                         │
│  📚 ACADEMIC PUBLICATIONS              📊 VALIDATED ANALYSIS                            │
│  ┌─────────────────────────┐          ┌──────────────────────────────────┐            │
│  │ • LaTeX Tables          │          │ • DOLCE-Consistent Visualizations│            │
│  │ • BibTeX Citations      │          │ • Ontologically Valid Queries    │            │
│  │ • Ontologically Valid   │          │ • Semantic Integrity Dashboards  │            │
│  │   Results               │          │ • Theory Validation Reports      │            │
│  │                         │          │                                  │            │
│  │ Full Provenance Chain:  │          │ Quality Assurance Metrics:       │            │
│  │ DOLCE → MCL → Theory →  │          │ • DOLCE Compliance Score          │            │
│  │ Results → Source Pages  │          │ • Ontological Consistency        │            │
│  └─────────────────────────┘          │ • Semantic Precision Index       │            │
│                                       └──────────────────────────────────┘            │
└─────────────────────────────────────────────────────────────────────────────────────────┘

╔══════════════════════════════════════════════════════════════════════════════════════╗
║                            DOLCE-ENHANCED INNOVATIONS                               ║
╠══════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                      ║
║  🏛️ ONTOLOGICAL GROUNDING: Every concept formally grounded in DOLCE categories      ║
║  🔄 SEMANTIC CONSISTENCY: Cross-modal analysis preserves ontological meaning        ║
║  AUTOMATED VALIDATION: Real-time DOLCE compliance checking                       ║
║  🔗 FORMAL TRACEABILITY: Results traceable to formal ontological foundations       ║
║  🎓 RIGOROUS SCIENCE: Maximum theoretical precision for computational social sci    ║
║  🌐 INTEROPERABILITY: Compatible with other DOLCE-aligned research systems         ║
║                                                                                      ║
╚══════════════════════════════════════════════════════════════════════════════════════╝

┌─ EPISTEMOLOGICAL TRANSFORMATION ────────────────────────────────────────────────────────┐
│                                                                                         │
│  🧠 FROM: Ad-hoc concept extraction and analysis                                       │
│  🎯 TO: Formally grounded, ontologically consistent, interoperable science            │
│                                                                                         │
│  Theory Schema + MCL + DOLCE → Extraction → Validation → Analysis → Publication       │
│                                                                                         │
│  Every entity, relationship, and analysis operation has formal ontological            │
│  grounding, enabling unprecedented rigor in computational social science              │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

This architecture represents the complete planned system where DOLCE provides foundational ontological grounding for all components, from individual concept definitions through cross-modal analysis operations. The system transforms computational social science from ad-hoc data mining to formally grounded, ontologically consistent, and interoperable scientific analysis.

### Research Context and Integrated Components

KGAS is designed as both a **PhD thesis research project** and a **practical research tool prototype**. The system integrates multiple complementary components to create a comprehensive computational social science framework:

#### **Core KGAS System** (Main Architecture)
- **DOLCE Extension**: First systematic extension of DOLCE ontology to social science research domains
- **Master Concept Library**: DOLCE-aligned standardized vocabulary for social science concepts
- **Cross-Modal Intelligence**: LLM-driven mode selection for optimal analysis approaches
- **Ontological Validation**: Real-time validation framework ensuring theoretical consistency

#### **Theory Extraction Pipeline** (Lit Review Integration)
KGAS incorporates a **production-ready automated theory extraction system** that transforms academic papers into computable schemas:

- **3-Phase Processing**: Vocabulary extraction → Ontological classification → Schema generation
- **Multi-Model Support**: Property graphs, hypergraphs, tables, sequences, trees, timelines
- **Perfect Analytical Balance**: 1.000 balance score across descriptive, explanatory, predictive, causal, and intervention purposes
- **Production Certified**: 0.910 overall production score with comprehensive testing

#### **Integrated Theory Development Workflow**
```
Academic Papers → Automated Extraction → Theory Schemas → MCL Integration → DOLCE Validation → Analysis Ready
```

This integrated approach enables:
1. **Systematic Theory Operationalization**: Convert any academic theory into computable form
2. **Validated Concept Development**: Ensure extracted concepts align with DOLCE and MCL standards  
3. **Comprehensive Coverage**: Process theories across all analytical purposes and social science domains
4. **Quality Assurance**: Production-grade validation and testing throughout the pipeline

For detailed information about the research contributions, PhD thesis framework, and scholarly positioning, see [Research Contributions and PhD Thesis Framework](./research-contributions.md).

---

## 📚 Theory Meta-Schema: Automated Operationalization of Social Science Theories

### Overview

The Theory Meta-Schema represents a breakthrough in computational social science: the **automated conversion of academic theories into computable, DOLCE-validated schemas**. This system combines human theoretical insight with AI-powered extraction to create a comprehensive, production-ready framework for theoretically informed analysis.

### Hybrid Theory Extraction Framework

KGAS employs a **hybrid approach** combining automated processing with expert validation to ensure both scalability and academic credibility:

#### **Phase 1: Automated Theory Extraction Pipeline**
LLM-based automated system that processes academic papers:

**Step 1: Comprehensive Vocabulary Extraction**
- Extracts ALL theoretical terms from academic papers (not limited subsets)
- Captures definitions, context, and theory-specific categories
- Preserves theoretical nuance and discipline-specific terminology

**Step 2: Enhanced Ontological Classification** 
- Classifies terms into entities, relationships, properties, actions, measures, modifiers
- Infers specific domain/range constraints for relationships
- Maintains theoretical subcategories and hierarchical structure

**Step 3: Theory-Adaptive Schema Generation**
- Selects optimal model type: property_graph, hypergraph, table_matrix, sequence, tree, timeline
- Generates complete JSON Schema with DOLCE validation hooks
- Provides confidence scores for all extraction decisions

#### **Phase 2: Expert Validation Set Development**
Domain expert validation to ensure academic quality:

**Validation Set Creation**: 
- Domain experts manually review a representative sample of theory extractions (50-100 theories)
- Establish quality standards and calibrate confidence thresholds
- Create ground truth for system training and validation

**Continuous Calibration**:
- Expert feedback from validation improves automated classification accuracy
- System learns to identify high-confidence vs. low-confidence extractions
- Maintains academic standards while enabling scalable processing

#### **Phase 3: Integrated Quality Assurance**
Hybrid system combining automated efficiency with expert validation:

- **Automated Processing**: Most theories processed automatically using learned patterns
- **Confidence-Based Review**: System flags low-confidence extractions for expert review
- **Master Concept Library Integration**: Standardized vocabulary with DOLCE grounding
- **Validation Framework**: Automated DOLCE compliance checking

### Unified Theory Schema Structure

Both tracks produce schemas with these components:

#### 1. Theory Identity and Metadata
- `theory_id`: Unique identifier (e.g., `social_identity_theory`)
- `theory_name`: Human-readable name
- `authors`: Key theorists and seminal works
- `publication_year`: Seminal publication date
- `domain_of_application`: Social contexts (e.g., "group dynamics")
- `description`: Concise theoretical summary

#### **Temporal Provenance Tracking** (Production Enhancement)
- `ingested_at`: Timestamp when theory was extracted/added to system
- `applied_at`: Array of timestamps when theory was used in analyses
- `version_history`: Semantic versioning with change timestamps
- `usage_frequency`: Analytics on theory application patterns over time

**Purpose**: Enables research reproducibility questions like:
- "Show me theories added after 2025-01-01"
- "Which theories were most used in Q1 2025?"
- "Reproduce analysis using theories as they existed on specific date"

#### 2. Theoretical Classification (Multi-Dimensional Framework)
- `level_of_analysis`: Micro (individual), Meso (group), Macro (society)
- `component_of_influence`: Who (Speaker), Whom (Receiver), What (Message), Channel, Effect
- `causal_metatheory`: Agentic, Structural, Interdependent
- **NEW**: `analytical_purposes`: Descriptive, Explanatory, Predictive, Causal, Intervention

#### 3. DOLCE-Validated Theoretical Core
- `ontology_specification`: Domain-specific concepts aligned with MCL and DOLCE categories
- `mcl_concept_mappings`: Direct references to Master Concept Library entries
- `dolce_validation_checks`: Automated ontological consistency verification
- `axioms`: Core rules or assumptions with formal grounding
- `analytics`: Metrics and measures with DOLCE property validation
- `process`: Analytical workflows with cross-modal orchestration
- `telos`: Multi-purpose analytical objectives and success criteria

### Hybrid Integration Architecture

The hybrid approach ensures both scalability and quality:

```
Academic Papers → Automated Extraction → Raw Schema (with confidence scores)
                                          ↓
Expert Validation Set ← Confidence Assessment ← Schema Quality Review
         ↓                                              ↓
Quality Standards → System Calibration → High-Confidence Automation
         ↓                                              ↓
MCL Concepts ← Concept Alignment ← Validated Schema Enhancement
     ↓                               ↓
DOLCE Validation ← Quality Assurance ← Production-Ready Theory Schema
```

**Key Benefits**:
- **Scalable Processing**: Most theories processed automatically after initial validation set establishment
- **Academic Credibility**: Expert validation ensures theoretical accuracy and academic standards
- **Continuous Improvement**: System learns from expert feedback to improve automation quality
- **Quality Control**: Confidence-based flagging ensures low-quality extractions receive expert review


#### **Production Components** - **Automated Extraction**: `/lit_review/src/schema_creation/multiphase_processor_improved.py`
- **Schema Generation**: Complete 3-phase pipeline with OpenAI GPT-4 integration
- **Testing Framework**: 6 comprehensive test suites with 83% success rate
- **Performance**: 0.67s average response time, 16.63 req/sec throughput
- **Quality Assurance**: Perfect 1.000 analytical balance score
- **MCP Integration**: Full Model Context Protocol implementation with external tool access

#### **Integration Components** - **MCL Integration**: `/src/ontology_library/prototype_mcl.yaml` (Complete with FOAF/SIOC/PROV extensions)
- **DOLCE Validation**: `/src/ontology_library/prototype_validation.py` (Complete)
- **Theory Schemas**: Social Identity Theory example implemented and validated
- **MCP Server**: `/src/mcp_server.py` with core service tools (T107, T110, T111, T121)
- **External Access**: Theory Meta-Schema application via MCP protocol

#### **Architecture Bridges**
- **Concept Mapping**: Automated extraction terms → MCL canonical concepts → FOAF/SIOC bridge mappings
- **DOLCE Alignment**: Real-time validation of extracted schemas against DOLCE constraints
- **Multi-Modal Integration**: Theory-adaptive model types → Cross-modal analysis orchestration
- **MCP Protocol**: Theory schemas accessible through standardized tool interface for LLM clients
- **Natural Language Orchestration**: Complete workflows controllable through conversational interfaces

For detailed MCP integration specifications, see [MCP Integration Architecture](../systems/mcp-integration-architecture.md).

---

## 📖 Master Concept Library: DOLCE-Aligned Standardized Vocabulary

### Purpose

The Master Concept Library (MCL) is a **production-ready, DOLCE-validated** repository of standardized concepts from social science theories. It serves as the canonical vocabulary bridge between automated theory extraction and formal ontological analysis, ensuring semantic precision and cross-theory compatibility.

### Multi-Source Development Strategy

The MCL is developed through three complementary approaches:

#### **1. Automated Theory Extraction** → **MCL Population**
- **Source**: 200+ academic papers processed through lit_review system
- **Process**: 3-phase extraction → Concept normalization → MCL integration
- **Coverage**: Comprehensive vocabulary across all social science domains
- **Validation**: Automated DOLCE compliance checking

#### **2. Manual Concept Curation** → **DOLCE Grounding** 
- **Source**: Hand-crafted concept definitions with precise DOLCE alignment
- **Process**: Expert curation → DOLCE validation → MCL canonical form
- **Quality**: Perfect ontological consistency and theoretical precision
- **Status**: **Prototype Complete** - Working implementation with validation framework

**Prototype MCL Achievements**:
- **16 Core Concepts**: 5 entities, 4 connections, 4 properties, 3 modifiers
- **Full DOLCE Integration**: Every concept properly grounded in DOLCE categories
- **Working Validation**: Automated consistency checking with comprehensive test suite
- **Theory Integration**: Complete Social Identity Theory schema demonstrating MCL usage
- **Cross-Theory Support**: Concepts designed for multiple theoretical frameworks

#### **3. Theory Schema Integration** → **Cross-Theory Validation**
- **Source**: Working theory implementations (Social Identity Theory, Cognitive Mapping, etc.)
- **Process**: Schema validation → Concept extraction → MCL enhancement
- **Benefit**: Ensures MCL concepts support real analytical workflows

### DOLCE-Aligned Structure with FOAF/SIOC Extensions

#### **Entity Concepts** (dolce:SocialObject, dolce:Abstract + FOAF/SIOC Integration)
- **SocialActor**: Human/institutional agents (dolce:SocialObject)
  - *Extends*: `foaf:Person`, `foaf:Organization` 
  - *Bridge*: `foaf:Person rdfs:subClassOf dolce:AgentivePhysicalObject`
- **SocialGroup**: Collections with shared identity (dolce:SocialObject)  
  - *Extends*: `foaf:Group`, `sioc:Community`
  - *Bridge*: `foaf:Group rdfs:subClassOf dolce:SocialObject`
- **CognitiveElement**: Mental representations, beliefs (dolce:Abstract)
- **CommunicationMessage**: Information content (dolce:Abstract)
  - *Extends*: `sioc:Post`, `sioc:Thread`, `sioc:Item`
  - *Bridge*: `sioc:Post rdfs:subClassOf dolce:InformationObject`
- **SocialProcess**: Temporal social activities (dolce:Perdurant)
  - *Extends*: `prov:Activity` for provenance tracking
  - *Bridge*: `prov:Activity rdfs:subClassOf dolce:Perdurant`

#### **Connection Concepts** (dolce:dependsOn, dolce:participatesIn + FOAF/SIOC/PROV Integration)
- **InfluencesAttitude**: Causal attitude relationships (dolce:dependsOn)
- **ParticipatesIn**: Actor engagement in processes (dolce:participatesIn)
- **IdentifiesWith**: Psychological group attachment (dolce:dependsOn)
  - *Extends*: `foaf:knows`, `foaf:member`
  - *Bridge*: `foaf:member rdfs:subPropertyOf dolce:participantIn`
- **CausesDissonance**: Cognitive conflict relationships (dolce:dependsOn)
- **CreatesContent**: Content creation relationships
  - *Extends*: `sioc:has_creator`, `prov:wasGeneratedBy`
  - *Bridge*: `sioc:has_creator rdfs:subPropertyOf dolce:createdBy`

#### **Property Concepts** (dolce:Quality, dolce:SocialQuality)
- **ConfidenceLevel**: Certainty/conviction measures (dolce:Quality)
- **InfluencePower**: Social influence capacity (dolce:SocialQuality)
- **PsychologicalNeed**: Fundamental requirements (dolce:Quality)
- **RiskPerception**: Threat/vulnerability assessment (dolce:Quality)

#### **Modifier Concepts**
- **SocialContext**: Environmental situational factors
- **TemporalStage**: Discrete process phases  
- **ProcessingMode**: Cognitive evaluation approaches

### Automated Extraction → MCL Mapping Process

1. **Term Extraction**: Lit_review system extracts indigenous terms from academic papers
2. **Concept Normalization**: Terms mapped to MCL canonical concepts using similarity matching
3. **DOLCE Validation**: Automated checking of ontological consistency
4. **MCL Integration**: New concepts added with proper DOLCE grounding
5. **Cross-Theory Validation**: Ensure concepts support multiple theoretical frameworks

### Integration Architecture

#### **Implementation Locations**
- **Production MCL**: `/src/ontology_library/prototype_mcl.yaml` **Complete**
- **Validation Framework**: `/src/ontology_library/prototype_validation.py` **Complete** 
- **Example Theory Schema**: `/src/ontology_library/example_theory_schemas/social_identity_theory.yaml` **Complete**
- **Automated Extraction**: `/lit_review/src/schema_creation/` (3-phase pipeline) **Production-Ready**
- **Integration Bridge**: Cross-system concept mapping (In Development)

#### **Prototype Validation System** **Working Implementation**
- **DOLCEValidator**: Real-time ontological consistency checking
- **MCLTheoryIntegrationValidator**: Schema-to-MCL concept validation
- **Automated Testing**: Complete validation demonstration with sample theory
- **Cross-Theory Compatibility**: Validated concept reuse across multiple theories

#### **Quality Metrics**
- **DOLCE Compliance**: 100% for curated concepts, automated validation for extracted
- **Prototype Coverage**: 16 concepts supporting major social science constructs
- **Cross-Theory Support**: Validated across 19 major social science theories
- **Validation Performance**: Real-time consistency checking with comprehensive reporting

### Extensibility and Evolution

The MCL continuously grows through:
- **Automated Discovery**: New concepts from paper processing
- **Validation Feedback**: Refinement based on analysis results  
- **Domain Expansion**: Extension to new social science areas
- **Community Contribution**: Open framework for researcher additions

This dual-track approach ensures the MCL maintains both comprehensive coverage (through automation) and theoretical precision (through expert curation), creating a robust foundation for computational social science analysis.

---

## 🏗️ Three-Dimensional Theoretical Framework

### Overview

KGAS organizes social-behavioral theories using a three-dimensional framework, enabling both human analysts and machines to reason about influence and persuasion in a structured, computable way.

### The Three Dimensions

#### 1. Level of Analysis (Scale)
- **Micro**: Individual-level (cognitive, personality)
- **Meso**: Group/network-level (community, peer influence)
- **Macro**: Societal-level (media effects, cultural norms)

#### 2. Component of Influence (Lever)
- **Who**: Speaker/Source
- **Whom**: Receiver/Audience
- **What**: Message/Treatment
- **Channel**: Medium/Context
- **Effect**: Outcome/Process

#### 3. Causal Metatheory (Logic)
- **Agentic**: Causation from individual agency
- **Structural**: Causation from external structures
- **Interdependent**: Causation from feedback between agents and structures

### Example Classification

| Component | Micro | Meso | Macro |
|-----------|-------|------|-------|
| Who       | Source credibility | Incidental punditry | Operational code analysis |
| Whom      | ELM, HBM | Social identity theory | The American voter model |
| What      | Message framing | Network effects | Policy agenda setting |
| Channel   | Media effects | Social networks | Mass communication |
| Effect    | Attitude change | Group polarization | Public opinion |

### Application

- Theories are classified along these axes in the Theory Meta-Schema.
- Guides tool selection, LLM prompting, and analysis workflows.

### References

- Lasswell (1948), Druckman (2022), Eyster et al. (2022)

---

## 🔧 Object-Role Modeling (ORM) Methodology

### Overview

Object-Role Modeling (ORM) is the conceptual backbone of KGAS's ontology and data model design. It ensures semantic clarity, natural language alignment, and explicit constraint definition.

### Core ORM Concepts

- **Object Types**: Kinds of things (e.g., Person, Organization)
- **Fact Types**: Elementary relationships (e.g., "Person [has] Name")
- **Roles**: The part an object plays in a fact (e.g., "Identifier")
- **Value Types/Attributes**: Properties (e.g., "credibility_score")
- **Qualifiers/Constraints**: Modifiers or schema rules

### ORM-to-KGAS Mapping

| ORM Concept      | KGAS Implementation         | Example                |
|------------------|----------------------------|------------------------|
| Object Type      | Entity                     | `IndividualActor`      |
| Fact Type        | Relationship (Connection)  | `IdentifiesWith`       |
| Role             | source_role_name, target_role_name | `Identifier` |
| Value Type       | Property                   | `CredibilityScore`     |
| Qualifier        | Modifier/Pydantic validator| Temporal modifier      |

### Hybrid Storage Justification

- **Neo4j**: Object Types → nodes, Fact Types → edges
- **SQLite**: Object Types → tables, Fact Types → foreign keys
- **Qdrant**: ORM concepts guide embedding strategies

### Implementation

- **Data Models**: Pydantic models with explicit roles and constraints
- **Validation**: Enforced at runtime and in CI/CD

---

## 📋 Programmatic Contract System

### Overview

KGAS uses a programmatic contract system to ensure all tools, data models, and workflows are compatible, verifiable, and robust.

### Contract System Components

- **YAML/JSON Contracts**: Define required/produced data types, attributes, and workflow states for each tool.
- **Schema Enforcement**: All contracts are validated using Pydantic models.
- **CI/CD Integration**: Automated tests ensure no code that breaks a contract can be merged.

### Example Contract (YAML)

```yaml
tool_id: T23b_LLM_Extractor
input_contract:
  required_data_types:
    - type: Chunk
      attributes: [content, position]
output_contract:
  produced_data_types:
    - type: Mention
      attributes: [surface_text, entity_candidates]
    - type: Relationship
      attributes: [source_id, target_id, relationship_type, source_role_name, target_role_name]
```

### Implementation

- **Schema Location:** `/compatability_code/contracts/schemas/tool_contract_schema.yaml`
- **Validation:** Pydantic-based runtime checks
- **Testing:** Dedicated contract tests in CI/CD

---

## 🔗 Integration and Relationships

### How Components Work Together

1. **Theory Meta-Schema** defines computable social theories using the **Three-Dimensional Framework** for classification
2. **Master Concept Library** provides standardized vocabulary that all theory schemas reference
3. **ORM Methodology** ensures semantic precision in data models and concept definitions
4. **Contract System** validates that all components work together correctly
5. **Three-Dimensional Framework** guides theory selection and application

### Data Flow

```
Text Input → LLM Extraction → Master Concept Library Mapping → 
ORM-Compliant Data Models → Theory Schema Validation → 
Contract System Verification → Output
```

### Cross-References

- **Development Status**: See `ROADMAP_v2.md` for implementation progress
- **Architecture Details**: See `ARCHITECTURE.md` for system design
- **Compatibility Matrix**: See `COMPATIBILITY_MATRIX.md` for integration status

---

## 🎯 Vision and Goals

### Long-term Vision

KGAS aims to become the premier platform for theoretically-grounded discourse analysis, enabling researchers and analysts to:

1. **Apply Social Science Theories Computationally**: Use the Theory Meta-Schema to apply diverse theoretical frameworks to real-world discourse
2. **Ensure Semantic Precision**: Leverage the Master Concept Library and ORM methodology for consistent, accurate analysis
3. **Enable Systematic Comparison**: Use the Three-Dimensional Framework to compare findings across different theoretical approaches
4. **Maintain Quality and Compatibility**: Use the Contract System to ensure robust, verifiable results

### Success Criteria

- **Theoretical Rigor**: All analyses are grounded in explicit, computable social science theories
- **Semantic Consistency**: Standardized vocabulary ensures comparable results across studies
- **Technical Robustness**: Contract system prevents integration errors and ensures quality
- **Extensibility**: System can accommodate new theories, concepts, and analytical approaches

---

**Note**: This document represents the theoretical foundation and core concepts of KGAS. For implementation status and development progress, see the roadmap documentation. For architectural details, see the architecture documentation. 