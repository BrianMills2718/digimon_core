# KGAS Theoretical Framework and Data Architecture

**Description**: Theory integration, meta-schemas, concepts, and data structures
**Generated**: Split from comprehensive architecture document
**Files Included**: 7

---

## Table of Contents

1. [kgas-theoretical-foundation.md](#1-kgastheoreticalfoundationmd)
2. [theory-meta-schema-v10.md](#2-theorymetaschemav10md)
3. [theory-meta-schema.md](#3-theorymetaschemamd)
4. [theory_meta_schema_v10.json](#4-theorymetaschemav10json)
5. [master-concept-library.md](#5-masterconceptlibrarymd)
6. [bi-store-justification.md](#6-bistorejustificationmd)
7. [DATABASE_SCHEMAS.md](#7-databaseschemasmd)

---

## 1. kgas-theoretical-foundation.md {#1-kgastheoreticalfoundationmd}

**Source**: `docs/architecture/concepts/kgas-theoretical-foundation.md`

---

---

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
║  ✅ AUTOMATED VALIDATION: Real-time DOLCE compliance checking                       ║
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
KGAS incorporates a **validated automated theory extraction system** that transforms academic papers into computable schemas:

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

The Theory Meta-Schema represents a breakthrough in computational social science: the **automated conversion of academic theories into computable, DOLCE-validated schemas**. This system combines human theoretical insight with AI-powered extraction to create a comprehensive, validated framework for theoretically informed analysis.

### Dual-Track Theory Development

KGAS employs two complementary approaches for theory schema development:

#### **Track 1: Automated Theory Extraction** (Validated)
A fully operational 3-phase system that processes academic papers:

**Phase 1: Comprehensive Vocabulary Extraction**
- Extracts ALL theoretical terms from academic papers (not limited subsets)
- Captures definitions, context, and theory-specific categories
- Preserves theoretical nuance and discipline-specific terminology

**Phase 2: Enhanced Ontological Classification** 
- Classifies terms into entities, relationships, properties, actions, measures, modifiers
- Infers specific domain/range constraints for relationships
- Maintains theoretical subcategories and hierarchical structure

**Phase 3: Theory-Adaptive Schema Generation**
- Selects optimal model type: property_graph, hypergraph, table_matrix, sequence, tree, timeline
- Generates complete JSON Schema with DOLCE validation hooks
- Achieves perfect analytical balance across all 5 purposes

#### **Track 2: Manual Concept Library Development** (MCL Integration)
Hand-crafted DOLCE-aligned concept definitions:

- **Master Concept Library**: Standardized vocabulary with DOLCE grounding
- **Example Theory Schemas**: Detailed implementations like Social Identity Theory
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

### Integration Architecture

The two tracks work synergistically:

```
Academic Papers → Automated Extraction → Raw Schema
                                          ↓
MCL Concepts ← Concept Alignment ← Schema Enhancement
     ↓                               ↓
DOLCE Validation ← Quality Assurance ← Final Schema
     ↓
Validated Theory Schema
```

### Implementation Status and Integration

#### **Production Components** ✅
- **Automated Extraction**: `/lit_review/src/schema_creation/multiphase_processor_improved.py`
- **Schema Generation**: Complete 3-phase pipeline with OpenAI GPT-4 integration
- **Testing Framework**: 6 comprehensive test suites with 83% success rate
- **Performance**: 0.67s average response time, 16.63 req/sec throughput
- **Quality Assurance**: Perfect 1.000 analytical balance score
- **MCP Integration**: Full Model Context Protocol implementation with external tool access

#### **Integration Components** ✅
- **MCL Integration**: `/src/ontology_library/prototype_mcl.yaml` (Complete with FOAF/SIOC/PROV extensions)
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

The Master Concept Library (MCL) is a **validated, DOLCE-integrated** repository of standardized concepts from social science theories. It serves as the canonical vocabulary bridge between automated theory extraction and formal ontological analysis, ensuring semantic precision and cross-theory compatibility.

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
- **Status**: **Prototype Complete** ✅ - Working implementation with validation framework

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
- **Production MCL**: `/src/ontology_library/prototype_mcl.yaml` ✅ **Complete**
- **Validation Framework**: `/src/ontology_library/prototype_validation.py` ✅ **Complete** 
- **Example Theory Schema**: `/src/ontology_library/example_theory_schemas/social_identity_theory.yaml` ✅ **Complete**
- **Automated Extraction**: `/lit_review/src/schema_creation/` (3-phase pipeline) ✅ **Validated**
- **Integration Bridge**: Cross-system concept mapping (In Development)

#### **Prototype Validation System** ✅ **Working Implementation**
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

================================================================================

## 2. theory-meta-schema-v10.md {#2-theorymetaschemav10md}

**Source**: `docs/architecture/data/theory-meta-schema-v10.md`

---

---

# Theory Meta-Schema v10.0: Executable Implementation Framework

**Purpose**: Comprehensive framework for representing executable social science theories

## Overview

Theory Meta-Schema v10.0 represents a major evolution from v9.0, incorporating practical implementation insights to bridge the gap between abstract theory and concrete execution. This version enables direct translation from theory schemas to executable workflows.

## Key Enhancements in v10.0

### 1. Execution Framework
- **Renamed `process` to `execution`** for clarity
- **Added implementation methods**: `llm_extraction`, `predefined_tool`, `custom_script`, `hybrid`
- **Embedded LLM prompts** directly in schema
- **Tool mapping strategy** with parameter adaptation
- **Custom script specifications** with test cases

### 2. Practical Implementation Support
- **Operationalization details** for concept boundaries
- **Cross-modal mappings** for graph/table/vector representations
- **Dynamic adaptation** for theories with changing processes
- **Uncertainty handling** at step level

### 3. Validation and Testing
- **Theory validation framework** with test cases
- **Operationalization documentation** for transparency
- **Boundary case specifications** for edge handling

### 4. Configuration Management
- **Configurable tracing levels** (minimal to debug)
- **LLM model selection** per task type
- **Performance optimization** flags
- **Fallback strategies** for error handling

## Schema Structure

### Core Required Fields
```json
{
  "theory_id": "stakeholder_theory",
  "theory_name": "Stakeholder Theory", 
  "version": "1.0.0",
  "classification": {...},
  "ontology": {...},
  "execution": {...},
  "telos": {...}
}
```

### Execution Framework Detail

#### Analysis Steps with Multiple Implementation Methods

**LLM Extraction Method**:
```json
{
  "step_id": "identify_stakeholders",
  "method": "llm_extraction",
  "llm_prompts": {
    "extraction_prompt": "Identify all entities that have a stake in the organization's decisions...",
    "validation_prompt": "Does this entity have legitimate interest, power, or urgency?"
  }
}
```

**Predefined Tool Method**:
```json
{
  "step_id": "calculate_centrality",
  "method": "predefined_tool",
  "tool_mapping": {
    "preferred_tool": "graph_centrality_mcp",
    "tool_parameters": {
      "centrality_type": "pagerank",
      "normalize": true
    },
    "parameter_adaptation": {
      "method": "wrapper_script",
      "adaptation_logic": "Convert stakeholder_salience to centrality weights"
    }
  }
}
```

**Custom Script Method**:
```json
{
  "step_id": "stakeholder_salience",
  "method": "custom_script",
  "custom_script": {
    "algorithm_name": "mitchell_agle_wood_salience",
    "business_logic": "Calculate geometric mean of legitimacy, urgency, and power",
    "implementation_hint": "salience = (legitimacy * urgency * power) ^ (1/3)",
    "inputs": {
      "legitimacy": {"type": "float", "range": [0,1]},
      "urgency": {"type": "float", "range": [0,1]}, 
      "power": {"type": "float", "range": [0,1]}
    },
    "outputs": {
      "salience_score": {"type": "float", "range": [0,1]}
    },
    "test_cases": [
      {
        "inputs": {"legitimacy": 1.0, "urgency": 1.0, "power": 1.0},
        "expected_output": 1.0,
        "description": "Maximum salience case"
      }
    ],
    "tool_contracts": ["stakeholder_interface", "salience_calculator"]
  }
}
```

### Cross-Modal Mappings

Specify how theory concepts map across different analysis modes:

```json
"cross_modal_mappings": {
  "graph_representation": {
    "nodes": "stakeholder_entities",
    "edges": "influence_relationships", 
    "node_properties": ["salience_score", "legitimacy", "urgency", "power"]
  },
  "table_representation": {
    "primary_table": "stakeholders",
    "key_columns": ["entity_id", "salience_score", "influence_rank"],
    "calculated_metrics": ["centrality_scores", "cluster_membership"]
  },
  "vector_representation": {
    "embedding_features": ["behavioral_patterns", "communication_style"],
    "similarity_metrics": ["stakeholder_type_similarity"]
  }
}
```

### Dynamic Adaptation (New Feature)

For theories like Spiral of Silence that change behavior based on state:

```json
"dynamic_adaptation": {
  "adaptation_triggers": [
    {"condition": "minority_visibility < 0.3", "action": "increase_spiral_strength"}
  ],
  "state_variables": {
    "minority_visibility": {"type": "float", "initial": 0.5},
    "spiral_strength": {"type": "float", "initial": 1.0}
  },
  "adaptation_rules": [
    "spiral_strength *= 1.2 when minority_visibility decreases"
  ]
}
```

### Validation Framework

```json
"validation": {
  "operationalization_notes": [
    "Legitimacy operationalized as stakeholder claim validity (0-1 scale)",
    "Power operationalized as ability to influence organizational decisions",
    "Urgency operationalized as time-critical nature of stakeholder claim"
  ],
  "theory_tests": [
    {
      "test_name": "high_salience_stakeholder_identification",
      "input_scenario": "CEO announces layoffs affecting employees and shareholders",
      "expected_theory_application": "Both employees and shareholders identified as high-salience stakeholders",
      "validation_criteria": "Salience scores > 0.7 for both groups"
    }
  ],
  "boundary_cases": [
    {
      "case_description": "Potential future stakeholder with no current relationship",
      "theory_applicability": "Mitchell model may not apply",
      "expected_behavior": "Flag as edge case, use alternative identification method"
    }
  ]
}
```

### Configuration Options

```json
"configuration": {
  "tracing_level": "standard",
  "llm_models": {
    "extraction": "gpt-4-turbo",
    "reasoning": "claude-3-opus", 
    "validation": "gpt-3.5-turbo"
  },
  "performance_optimization": {
    "enable_caching": true,
    "batch_processing": true,
    "parallel_execution": false
  },
  "fallback_strategies": {
    "missing_tools": "llm_implementation",
    "low_confidence": "human_review",
    "edge_cases": "uncertainty_flagging"
  }
}
```

## Migration from v9.0 to v10.0

### Breaking Changes
- `process` renamed to `execution`
- `steps` array structure enhanced with implementation methods
- New required fields: `method` in each step

### Migration Strategy
1. Rename `process` to `execution`
2. Add `method` field to each step 
3. Move prompts from separate files into `llm_prompts` objects
4. Add `custom_script` specifications for algorithms
5. Include `tool_mapping` for predefined tools

### Backward Compatibility
A migration tool will convert v9.0 schemas to v10.0 format:
- Default `method` to "llm_extraction" for existing steps
- Generate placeholder prompts from step descriptions
- Create basic tool mappings based on step naming

## Implementation Requirements

### For Theory Schema Authors
1. **Specify implementation method** for each analysis step
2. **Include LLM prompts** for extraction steps
3. **Define custom algorithms** with test cases for novel procedures
4. **Document operationalization decisions** in validation section

### For System Implementation
1. **Execution engine** that can dispatch to different implementation methods
2. **Custom script compiler** using Claude Code for algorithm implementation
3. **Tool mapper** using LLM intelligence for tool selection
4. **Validation framework** that runs theory tests automatically

### For Researchers
1. **Transparent operationalization** - all theory simplifications documented
2. **Configurable complexity** - adjust tracing and validation levels
3. **Extensible framework** - can add custom theories and algorithms
4. **Cross-modal capability** - theory works across graph, table, vector modes

## Next Steps

1. **Create example theory** using v10.0 schema (stakeholder theory)
2. **Implement execution engine** that can interpret v10.0 schemas
3. **Build validation framework** for theory testing
4. **Test stress cases** with complex multi-step theories

The v10.0 schema provides the comprehensive framework needed to bridge theory and implementation while maintaining flexibility and configurability.

## Security Architecture Requirements

### Rule Execution Security and Flexibility
- **Implementation**: DebuggableEvaluator with controlled eval() usage
- **Rationale**: Maintains maximum flexibility for academic research while enabling debugging
- **Approach**: 
  ```python
  class DebuggableEvaluator:
      def evaluate(self, expression, context, debug=False):
          if debug:
              wrapped_expr = f"import pdb; result = ({expression}); pdb.set_trace(); result"
          else:
              wrapped_expr = expression
          return eval(wrapped_expr, {"__builtins__": {}}, context)
  ```
- **Benefits**: 
  - Full Python flexibility for complex academic expressions
  - Real-time debugging with breakpoints and print statements
  - Support for custom research logic and numpy operations
- **Validation**: All rule execution must be sandboxed and validated

================================================================================

## 3. theory-meta-schema.md {#3-theorymetaschemamd}

**Source**: `docs/architecture/data/theory-meta-schema.md`

---

---

---
status: living
---

# Theory Meta-Schema: Operationalizing Social Science Theories in KGAS

![Meta-Schema v9.1 (JSON Schema draft-07)](https://img.shields.io/badge/Meta--Schema-v9.1-blue)

## Overview

The Theory Meta-Schema is the foundational innovation of the Knowledge Graph Analysis System (KGAS). It provides a standardized, computable framework for representing and applying diverse social science theories to discourse analysis. The goal is to move beyond data description to *theoretically informed, computable analysis*.

## Structure of the Theory Meta-Schema

Each Theory Meta-Schema instance is a structured document with the following components:

### 1. Theory Identity and Metadata
- `theory_id`: Unique identifier (e.g., `social_identity_theory`)
- `theory_name`: Human-readable name
- `authors`: Key theorists
- `publication_year`: Seminal publication date
- `domain_of_application`: Social contexts (e.g., “group dynamics”)
- `description`: Concise summary

**New in v9.1**  
• `mcl_id` – cross-link to Master Concept Library  
• `dolce_parent` – IRI of the DOLCE superclass for every entity  
• `ontology_alignment_strategy` – strategy for aligning with DOLCE ontology
• Tags now sit in `classification.domain` (`level`, `component`, `metatheory`)

### 2. Theoretical Classification (Three-Dimensional Framework)
- `level_of_analysis`: Micro (individual), Meso (group), Macro (society)
- `component_of_influence`: Who (Speaker), Whom (Receiver), What (Message), Channel, Effect
- `causal_metatheory`: Agentic, Structural, Interdependent

### 3. Computable Theoretical Core
- `ontology_specification`: Domain-specific concepts (entities, relationships, properties, modifiers) aligned with the Master Concept Library
- `axioms`: Core rules or assumptions (optional)
- `analytics`: Metrics or focal concepts (optional)
- `process`: Sequence of steps (sequential, iterative, workflow)
- `telos`: Analytical purpose, output format, and success criteria

### 4. Provenance
- `provenance`: {source_chunk_id: str, prompt_hash: str, model_id: str, timestamp: datetime}
  - Captures the lineage of each theory instance for audit and reproducibility.

## Implementation

- **Schema Location:** `/_schemas/theory_meta_schema_v10.json`
- **Validation:** Pydantic models with runtime verification
- **Integration:** CI/CD enforced contract compliance
- **Codegen**: dataclasses auto-generated into /src/contracts/generated/

## Example

See `docs/architecture/THEORETICAL_FRAMEWORK.md` for a worked example using Social Identity Theory.

## Changelog

### v9.0 → v9.1
- Added `ontology_alignment_strategy` field for DOLCE alignment
- Enhanced codegen support with auto-generated dataclasses
- Updated schema location to v9.1
- Improved validation and integration documentation
<br><sup>See `docs/roadmap/ROADMAP_OVERVIEW.md` for master plan.</sup>

================================================================================

## 4. theory_meta_schema_v10.json {#4-theorymetaschemav10json}

**Source**: `docs/architecture/data/-schemas/theory_meta_schema_v10.json`

---

---

{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Theory Meta-Schema v10.0",
  "description": "Comprehensive framework for representing executable social science theories with practical implementation details",
  "version": "10.0",
  "type": "object",
  "required": ["theory_id", "theory_name", "version", "classification", "ontology", "execution", "telos"],
  "properties": {
    "theory_id": {
      "type": "string",
      "pattern": "^[a-z_][a-z0-9_]*$",
      "description": "Unique identifier for the theory"
    },
    "theory_name": {
      "type": "string",
      "description": "Human-readable name of the theory"
    },
    "version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+(\\.\\d+)?$",
      "description": "Semantic version of this theory schema"
    },
    "authors": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Key theorists and contributors"
    },
    "publication_year": {
      "type": "integer",
      "minimum": 1900,
      "maximum": 2030,
      "description": "Year of seminal publication"
    },
    "description": {
      "type": "string",
      "description": "Concise summary of the theory"
    },
    "classification": {
      "type": "object",
      "required": ["domain"],
      "properties": {
        "domain": {
          "type": "object",
          "required": ["level", "component", "metatheory"],
          "properties": {
            "level": {
              "type": "string",
              "enum": ["Micro", "Meso", "Macro"],
              "description": "Level of analysis"
            },
            "component": {
              "type": "string", 
              "enum": ["Who", "Whom", "What", "Channel", "Effect"],
              "description": "Component of influence"
            },
            "metatheory": {
              "type": "string",
              "enum": ["Agentic", "Structural", "Interdependent"],
              "description": "Causal metatheory"
            }
          }
        },
        "complexity_tier": {
          "type": "string",
          "enum": ["direct", "heuristic", "simplified"],
          "description": "Operationalization complexity level"
        }
      }
    },
    "ontology": {
      "type": "object",
      "required": ["entities", "relationships"],
      "properties": {
        "entities": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["name", "mcl_id"],
            "properties": {
              "name": {"type": "string"},
              "description": {"type": "string"},
              "mcl_id": {
                "type": "string",
                "description": "Master Concept Library primary key"
              },
              "dolce_parent": {
                "type": "string",
                "format": "uri",
                "description": "IRI of closest DOLCE class"
              },
              "properties": {
                "type": "array",
                "items": {
                  "type": "object",
                  "required": ["name", "type"],
                  "properties": {
                    "name": {"type": "string"},
                    "type": {"type": "string"},
                    "description": {"type": "string"},
                    "constraints": {"type": "object"},
                    "operationalization": {
                      "type": "object",
                      "properties": {
                        "measurement_approach": {"type": "string"},
                        "boundary_rules": {"type": "array"},
                        "fuzzy_boundaries": {"type": "boolean"},
                        "validation_examples": {"type": "array"}
                      }
                    }
                  }
                }
              }
            }
          }
        },
        "relationships": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["name", "source_role", "target_role"],
            "properties": {
              "name": {"type": "string"},
              "description": {"type": "string"},
              "source_role": {"type": "string"},
              "target_role": {"type": "string"},
              "dolce_parent": {
                "type": "string",
                "format": "uri",
                "description": "IRI of closest DOLCE relation"
              },
              "properties": {
                "type": "array",
                "items": {
                  "type": "object",
                  "required": ["name", "type"],
                  "properties": {
                    "name": {"type": "string"},
                    "type": {"type": "string"},
                    "description": {"type": "string"},
                    "constraints": {"type": "object"}
                  }
                }
              }
            }
          }
        }
      }
    },
    "execution": {
      "type": "object",
      "required": ["process_type", "analysis_steps"],
      "properties": {
        "process_type": {
          "type": "string",
          "enum": ["sequential", "iterative", "workflow", "adaptive"],
          "description": "Process flow type"
        },
        "analysis_steps": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["step_id", "method", "description"],
            "properties": {
              "step_id": {"type": "string"},
              "description": {"type": "string"},
              "method": {
                "type": "string",
                "enum": ["llm_extraction", "predefined_tool", "custom_script", "hybrid"],
                "description": "Implementation method"
              },
              "inputs": {"type": "array", "items": {"type": "string"}},
              "outputs": {"type": "array", "items": {"type": "string"}},
              "conditions": {"type": "object"},
              
              "llm_prompts": {
                "type": "object",
                "description": "Prompts for LLM-based steps",
                "properties": {
                  "extraction_prompt": {"type": "string"},
                  "validation_prompt": {"type": "string"},
                  "classification_prompt": {"type": "string"},
                  "context_instructions": {"type": "string"}
                }
              },
              
              "tool_mapping": {
                "type": "object",
                "description": "Tool selection and configuration",
                "properties": {
                  "preferred_tool": {"type": "string"},
                  "alternative_tools": {"type": "array", "items": {"type": "string"}},
                  "tool_parameters": {"type": "object"},
                  "parameter_adaptation": {
                    "type": "object",
                    "properties": {
                      "method": {"type": "string"},
                      "adaptation_logic": {"type": "string"},
                      "wrapper_script": {"type": "string"}
                    }
                  }
                }
              },
              
              "custom_script": {
                "type": "object",
                "description": "Custom algorithm specification",
                "properties": {
                  "algorithm_name": {"type": "string"},
                  "description": {"type": "string"},
                  "business_logic": {"type": "string"},
                  "implementation_hint": {"type": "string"},
                  "inputs": {
                    "type": "object",
                    "patternProperties": {
                      ".*": {
                        "type": "object",
                        "properties": {
                          "type": {"type": "string"},
                          "range": {"type": "array"},
                          "description": {"type": "string"},
                          "constraints": {"type": "object"}
                        }
                      }
                    }
                  },
                  "outputs": {
                    "type": "object",
                    "patternProperties": {
                      ".*": {
                        "type": "object",
                        "properties": {
                          "type": {"type": "string"},
                          "range": {"type": "array"},
                          "description": {"type": "string"}
                        }
                      }
                    }
                  },
                  "test_cases": {
                    "type": "array",
                    "items": {
                      "type": "object",
                      "properties": {
                        "inputs": {"type": "object"},
                        "expected_output": {},
                        "description": {"type": "string"}
                      }
                    }
                  },
                  "validation_rules": {"type": "array", "items": {"type": "string"}},
                  "tool_contracts": {"type": "array", "items": {"type": "string"}}
                }
              },
              
              "uncertainty_handling": {
                "type": "object",
                "properties": {
                  "confidence_thresholds": {"type": "object"},
                  "fallback_strategy": {"type": "string"},
                  "uncertainty_propagation": {"type": "string"}
                }
              }
            }
          }
        },
        
        "cross_modal_mappings": {
          "type": "object",
          "description": "How theory maps across graph/table/vector modes",
          "properties": {
            "graph_representation": {"type": "object"},
            "table_representation": {"type": "object"},
            "vector_representation": {"type": "object"},
            "mode_conversions": {"type": "array"}
          }
        },
        
        "dynamic_adaptation": {
          "type": "object",
          "description": "For adaptive processes like Spiral of Silence",
          "properties": {
            "adaptation_triggers": {"type": "array"},
            "state_variables": {"type": "object"},
            "adaptation_rules": {"type": "array"}
          }
        }
      }
    },
    "telos": {
      "type": "object",
      "required": ["purpose", "output_format", "success_criteria"],
      "properties": {
        "purpose": {"type": "string"},
        "output_format": {"type": "string"},
        "success_criteria": {
          "type": "array",
          "items": {"type": "string"}
        },
        "analysis_tiers": {
          "type": "array",
          "items": {
            "type": "string",
            "enum": ["descriptive", "explanatory", "predictive", "interventionary"]
          }
        }
      }
    },
    "validation": {
      "type": "object",
      "description": "Theory validation and testing framework",
      "properties": {
        "operationalization_notes": {
          "type": "array",
          "items": {"type": "string"},
          "description": "Documented simplifications and assumptions"
        },
        "theory_tests": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "test_name": {"type": "string"},
              "input_scenario": {"type": "string"},
              "expected_theory_application": {"type": "string"},
              "validation_criteria": {"type": "string"}
            }
          }
        },
        "boundary_cases": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "case_description": {"type": "string"},
              "theory_applicability": {"type": "string"},
              "expected_behavior": {"type": "string"}
            }
          }
        }
      }
    },
    "configuration": {
      "type": "object",
      "description": "Configurable aspects of theory application",
      "properties": {
        "tracing_level": {
          "type": "string",
          "enum": ["minimal", "standard", "verbose", "debug"],
          "default": "standard"
        },
        "llm_models": {
          "type": "object",
          "properties": {
            "extraction": {"type": "string"},
            "reasoning": {"type": "string"},
            "validation": {"type": "string"}
          }
        },
        "performance_optimization": {
          "type": "object",
          "properties": {
            "enable_caching": {"type": "boolean"},
            "batch_processing": {"type": "boolean"},
            "parallel_execution": {"type": "boolean"}
          }
        },
        "fallback_strategies": {
          "type": "object",
          "properties": {
            "missing_tools": {"type": "string"},
            "low_confidence": {"type": "string"},
            "edge_cases": {"type": "string"}
          }
        }
      }
    },
    "metadata": {
      "type": "object",
      "properties": {
        "mcl_id": {
          "type": "string",
          "description": "Master Concept Library primary key"
        },
        "created": {"type": "string", "format": "date-time"},
        "modified": {"type": "string", "format": "date-time"},
        "contributors": {"type": "array", "items": {"type": "string"}},
        "validation_status": {"type": "string"},
        "implementation_status": {"type": "string"},
        "test_coverage": {"type": "number"}
      }
    }
  }
}

================================================================================

## 5. master-concept-library.md {#5-masterconceptlibrarymd}

**Source**: `docs/architecture/concepts/master-concept-library.md`

---

---

---
status: living
---

# Master Concept Library: Standardized Vocabulary for KGAS

## Purpose

The Master Concept Library (MCL) is a machine-readable, extensible repository of standardized concepts (entities, connections, properties, modifiers) from social, behavioral, and communication science. It ensures semantic precision and cross-theory comparability in all KGAS analyses.

## Structure

- **EntityConcept**: Actors, groups, organizations, etc.
- **ConnectionConcept**: Relationships between entities (e.g., “identifies_with”)
- **PropertyConcept**: Attributes of entities or connections (e.g., “credibility_score”)
- **ModifierConcept**: Qualifiers or contextualizers (e.g., “temporal”, “certainty”)

## Mapping Process

1. **LLM Extraction**: Indigenous terms are extracted from text.
2. **Standardization**: Terms are mapped to canonical names in the MCL.
3. **Human-in-the-Loop**: Novel terms are reviewed and added as needed.

## Schema Specification

### EntityConcept Schema
```json
{
  "type": "EntityConcept",
  "canonical_name": "string",
  "description": "string",
  "upper_parent": "dolce:IRI",
  "subtypes": ["string"],
  "properties": ["PropertyConcept"],
  "connections": ["ConnectionConcept"],
  "bridge_links": ["external:IRI"],
  "version": "semver",
  "created_at": "timestamp",
  "validated_by": "string"
}
```

### ConnectionConcept Schema
```json
{
  "type": "ConnectionConcept", 
  "canonical_name": "string",
  "description": "string",
  "upper_parent": "dolce:Relation",
  "domain": "EntityConcept",
  "range": "EntityConcept",
  "properties": ["PropertyConcept"],
  "directional": "boolean",
  "validation_rules": ["rule"]
}
```

### PropertyConcept Schema
```json
{
  "type": "PropertyConcept",
  "canonical_name": "string", 
  "description": "string",
  "value_type": "numeric|categorical|boolean|text",
  "scale": "nominal|ordinal|interval|ratio",
  "valid_values": ["value"],
  "measurement_unit": "string",
  "uncertainty_type": "stochastic|epistemic|systematic"
}
```

## Implementation Details

### Storage and Access
- **Code Location:** `/src/ontology_library/mcl/__init__.py`
- **Schema Enforcement:** Pydantic models with JSON Schema validation
- **Database Storage:** Neo4j graph with concept relationships
- **API Endpoints:** RESTful API for concept CRUD operations
- **Integration:** Used in all theory schemas and extraction pipelines

### Validation Pipeline
```python
class MCLValidator:
    """Validates concepts against MCL standards"""
    
    def validate_concept(self, concept: ConceptDict) -> ValidationResult:
        # 1. Schema validation
        # 2. DOLCE alignment check
        # 3. Duplicate detection
        # 4. Cross-reference validation
        # 5. Semantic consistency check
```

### API Operations
```python
# Core MCL operations
mcl.add_concept(concept_data, validate=True)
mcl.get_concept(canonical_name)
mcl.search_concepts(query, filters={})
mcl.map_term_to_concept(indigenous_term)
mcl.validate_theory_schema(schema)
```

## Detailed Examples

### Production Theory Integration Example
**See**: [MCL Theory Schemas - Implementation Examples](../data/mcl-theory-schemas-examples.md) for complete production theory integrations including Cognitive Dissonance Theory, Prospect Theory, and Social Identity Theory.

### Entity Concept Example
**Indigenous term:** "grassroots organizer"
```json
{
  "type": "EntityConcept",
  "canonical_name": "CommunityOrganizer",
  "description": "Individual who mobilizes community members for collective action",
  "upper_parent": "dolce:SocialAgent",
  "subtypes": ["GrassrootsOrganizer", "PolicyOrganizer"],
  "properties": ["influence_level", "network_size", "expertise_domain"],
  "connections": ["mobilizes", "coordinates_with", "represents"],
  "indigenous_terms": ["grassroots organizer", "community leader", "activist"],
  "theory_sources": ["Social Identity Theory", "Social Cognitive Theory"],
  "validation_status": "production_ready"
}
```

### Connection Concept Example  
**Indigenous term:** "influences public opinion"
```json
{
  "type": "ConnectionConcept",
  "canonical_name": "influences_opinion",
  "description": "Causal relationship where entity affects public perception",
  "domain": "SocialAgent",
  "range": "PublicOpinion", 
  "properties": ["influence_strength", "temporal_duration"],
  "directional": true,
  "validation_rules": ["requires_evidence_source", "measurable_outcome"]
}
```

### Property Concept Example
**Indigenous term:** "credibility"
```json
{
  "type": "PropertyConcept",
  "canonical_name": "credibility_score",
  "description": "Perceived trustworthiness and reliability measure",
  "value_type": "numeric",
  "scale": "interval", 
  "valid_values": [0.0, 10.0],
  "measurement_unit": "likert_scale",
  "uncertainty_type": "stochastic"
}
```

## DOLCE Alignment Procedures

### Automated Alignment Process
```python
class DOLCEAligner:
    """Automatically aligns new concepts with DOLCE upper ontology"""
    
    def align_concept(self, concept: NewConcept) -> DOLCEAlignment:
        # 1. Semantic similarity analysis
        # 2. Definition matching against DOLCE taxonomy
        # 3. Structural constraint checking
        # 4. Expert review recommendation
        # 5. Alignment confidence score
```

### DOLCE Classification Rules
| Concept Type | DOLCE Parent | Validation Rules |
|--------------|--------------|------------------|
| **Physical Entity** | `dolce:PhysicalObject` | Must have spatial location |
| **Social Entity** | `dolce:SocialObject` | Must involve multiple agents |
| **Abstract Entity** | `dolce:AbstractObject` | Must be non-spatial |
| **Relationship** | `dolce:Relation` | Must connect two entities |
| **Property** | `dolce:Quality` | Must be measurable attribute |

### Quality Assurance Framework
```python
class ConceptQualityValidator:
    """Ensures MCL concept quality and consistency"""
    
    quality_checks = [
        "semantic_precision",      # Clear, unambiguous definition
        "dolce_consistency",       # Proper upper ontology alignment  
        "cross_reference_validity", # Valid concept connections
        "measurement_clarity",     # Clear measurement procedures
        "research_utility"         # Useful for social science research
    ]
```

## Extension Guidelines

### Adding New Concepts
1. **Research Validation**: Concept must appear in peer-reviewed literature
2. **Semantic Gap Analysis**: Must fill genuine gap in existing MCL
3. **DOLCE Alignment**: Must align with appropriate DOLCE parent class
4. **Community Review**: Subject to expert panel review process
5. **Integration Testing**: Must integrate cleanly with existing concepts

### Concept Evolution Procedures
```python
# Concept modification workflow
def evolve_concept(concept_name: str, changes: dict) -> EvolutionResult:
    # 1. Impact analysis on dependent concepts
    # 2. Backward compatibility assessment
    # 3. Migration path generation
    # 4. Validation test suite update
    # 5. Documentation synchronization
```

### Version Control and Migration
- **Semantic Versioning**: Major.Minor.Patch versioning for concept changes
- **Migration Scripts**: Automated concept evolution with data preservation
- **Rollback Procedures**: Safe rollback mechanisms for problematic changes
- **Change Documentation**: Complete audit trail for all concept modifications

## Extensibility Framework

The MCL grows systematically through:

### Research-Driven Expansion
- **Literature Integration**: New concepts from emerging research domains
- **Cross-Domain Synthesis**: Concepts spanning multiple social science fields
- **Methodological Innovation**: Concepts supporting novel analysis techniques

### Community Contribution Process
```markdown
1. **Concept Proposal**: Submit via GitHub issue with research justification
2. **Expert Review**: Panel evaluation for research merit and semantic precision
3. **Prototype Integration**: Test integration with existing concept ecosystem
4. **Community Validation**: Broader community review and feedback
5. **Production Integration**: Full integration with versioning and documentation
```

### Quality Metrics and Monitoring
- **Usage Analytics**: Track concept utilization across research projects
- **Semantic Drift Detection**: Monitor concept meaning stability over time  
- **Research Impact Assessment**: Evaluate contribution to research outcomes
- **Community Satisfaction**: Regular feedback collection from users

## Versioning Rules

| Change Type | Version Bump | Review Required | Documentation |
|-------------|--------------|-----------------|---------------|
| **Concept Addition** | Patch (x.y.z+1) | No | Update concept list |
| **Concept Modification** | Minor (x.y+1.0) | Yes | Update examples |
| **Schema Change** | Major (x+1.0.0) | Yes | Migration guide |
| **DOLCE Alignment** | Minor (x.y+1.0) | Yes | Alignment report |

### Concept Merge Policy
New concepts are merged via `scripts/mcl_merge.py` which:
- Validates against existing concepts
- Checks DOLCE alignment
- Updates cross-references
- Generates migration guide

## DOLCE and Bridge Links

### Upper Ontology Alignment
Every concept in the MCL is aligned with the DOLCE (Descriptive Ontology for Linguistic and Cognitive Engineering) upper ontology:

- **`upper_parent`**: IRI of the closest DOLCE superclass (e.g., `dolce:PhysicalObject`, `dolce:SocialObject`)
- **Semantic Precision**: Ensures ontological consistency across all concepts
- **Interoperability**: Enables integration with other DOLCE-aligned systems

### Bridge Links (Optional)
For enhanced interoperability, concepts may include:

- **`bridge_links`**: Array of IRIs linking to related concepts in external ontologies
- **Cross-Domain Mapping**: Connects social science concepts to domain-specific ontologies
- **Research Integration**: Enables collaboration with other research platforms -e 
<br><sup>See `docs/roadmap/ROADMAP_OVERVIEW.md` for master plan.</sup>

================================================================================

## 6. bi-store-justification.md {#6-bistorejustificationmd}

**Source**: `docs/architecture/data/bi-store-justification.md`

---

---

# Bi-Store Architecture Justification

## Overview

KGAS employs a bi-store architecture with Neo4j and SQLite, each optimized for different analytical modalities required in academic social science research.

## ⚠️ CRITICAL RELIABILITY ISSUE

**IDENTIFIED**: Bi-store operations lack distributed transaction consistency, creating risk of data corruption where Neo4j entities are created but SQLite identity tracking fails, leaving orphaned graph nodes.

**STATUS**: Phase RELIABILITY Issue C2 - requires distributed transaction implementation across both stores.

**IMPACT**: Current implementation unsuitable for production use until transaction consistency is implemented.

## Architectural Decision

### Neo4j (Graph + Vector Store)
**Purpose**: Graph-native operations and vector similarity search

**Optimized for**:
- Network analysis (centrality, community detection, pathfinding)
- Relationship traversal and pattern matching
- Vector similarity search (using native HNSW index)
- Graph-based machine learning features

**Example Operations**:
```cypher
-- Find influential entities
MATCH (n:Entity)
RETURN n.name, n.pagerank_score
ORDER BY n.pagerank_score DESC

-- Vector similarity search
MATCH (n:Entity)
WHERE n.embedding IS NOT NULL
WITH n, vector.similarity.cosine(n.embedding, $query_vector) AS similarity
RETURN n, similarity
ORDER BY similarity DESC
```

### SQLite (Relational Store)
**Purpose**: Statistical analysis and structured data operations

**Optimized for**:
- Statistical analysis (regression, correlation, hypothesis testing)
- Structured Equation Modeling (SEM)
- Time series analysis
- Tabular data export for R/SPSS/Stata
- Complex aggregations and pivot operations
- Workflow metadata and provenance tracking

**Example Operations**:
```sql
-- Correlation analysis preparation
SELECT 
    e1.pagerank_score,
    e1.betweenness_centrality,
    COUNT(r.id) as relationship_count,
    AVG(r.weight) as avg_relationship_strength
FROM entities e1
LEFT JOIN relationships r ON e1.id = r.source_id
GROUP BY e1.id;

-- SEM data preparation
CREATE VIEW sem_data AS
SELECT 
    e.id,
    e.community_id,
    e.pagerank_score as influence,
    e.clustering_coefficient as cohesion,
    COUNT(DISTINCT r.target_id) as out_degree
FROM entities e
LEFT JOIN relationships r ON e.id = r.source_id
GROUP BY e.id;
```

## Why Not Single Store?

### Graph Databases (Neo4j alone)
- **Limitation**: Not optimized for statistical operations
- **Challenge**: Difficult to export to statistical software
- **Missing**: Native support for complex aggregations needed in social science

### Relational Databases (PostgreSQL/SQLite alone)
- **Limitation**: Recursive queries for graph algorithms are inefficient
- **Challenge**: No native vector similarity search
- **Missing**: Natural graph traversal operations

### Document Stores (MongoDB alone)
- **Limitation**: Neither graph-native nor optimized for statistics
- **Challenge**: Complex joins for relationship analysis
- **Missing**: ACID guarantees for research reproducibility

## Cross-Modal Synchronization

The bi-store architecture enables synchronized views:

```python
class CrossModalSync:
    def sync_graph_to_table(self, graph_metrics: Dict):
        """Sync graph analysis results to relational tables"""
        # Store graph metrics in SQLite for statistical analysis
        self.sqlite.execute("""
            INSERT INTO entity_metrics 
            (entity_id, pagerank, betweenness, community_id, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, graph_metrics)
    
    def sync_table_to_graph(self, statistical_results: Dict):
        """Sync statistical results back to graph"""
        # Update graph with statistical findings
        self.neo4j.query("""
            MATCH (n:Entity {id: $entity_id})
            SET n.regression_coefficient = $coefficient,
                n.significance = $p_value
        """, statistical_results)
```

## Research Workflow Integration

### Example: Mixed Methods Analysis
1. **Graph Analysis** (Neo4j): Identify influential actors and communities
2. **Export to Table** (SQLite): Prepare data for statistical analysis
3. **Statistical Analysis** (SQLite/R): Run regression, SEM, or other tests
4. **Integrate Results** (Both): Update graph with statistical findings
5. **Vector Search** (Neo4j): Find similar patterns in other datasets

This bi-store approach provides the **best tool for each job** while maintaining **data coherence** and **analytical flexibility** required for sophisticated social science research.

================================================================================

## 7. DATABASE_SCHEMAS.md {#7-databaseschemasmd}

**Source**: `docs/architecture/data/DATABASE_SCHEMAS.md`

---

---

### Neo4j Schema
```cypher
// Core Node Type with Embedding Property
(:Entity {
    id: string,
    canonical_name: string,
    entity_type: string,
    confidence: float,
    quality_tier: string,
    created_by: string,
    embedding: vector[384] // Native vector type
})

// Vector Index for Fast Similarity Search
CREATE VECTOR INDEX entity_embedding_index IF NOT EXISTS
FOR (e:Entity) ON (e.embedding)
OPTIONS {
  indexConfig: {
    `vector.dimensions`: 384,
    `vector.similarity_function`: 'cosine'
  }
}
```

### SQLite Schemas
```sql
-- Workflow Management
CREATE TABLE workflow_states (
    workflow_id TEXT PRIMARY KEY,
    state_data JSON,
    checkpoint_time TIMESTAMP,
    current_step INTEGER
);

-- Object Provenance
CREATE TABLE provenance (
    object_id TEXT,
    tool_id TEXT,
    operation TEXT,
    inputs JSON,
    outputs JSON,
    execution_time REAL,
    created_at TIMESTAMP
);

-- PII Vault
CREATE TABLE pii_vault (
    pii_id TEXT PRIMARY KEY,
    ciphertext_b64 TEXT NOT NULL,
    nonce_b64 TEXT NOT NULL,
    created_at TIMESTAMP
);
```

================================================================================

