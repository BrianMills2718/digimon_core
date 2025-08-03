# Two-Layer Theory Architecture: Design Specification

**Related**: carter-analysis-lessons-learned.md, uncertainty-framework-selection-integration.md

## Executive Summary

This document defines the architectural design for theoretical analysis in KGAS, specifying a two-layer architecture that separates:

1. **Layer 1**: Comprehensive theoretical structure extraction (what's in the text)
2. **Layer 2**: Question-driven analysis using that structure (what we want to know)

This separation addresses fundamental problems in theory application and enables more flexible, accurate theoretical applications.

## Table of Contents

1. [Problem Analysis](#problem-analysis)
2. [Core Architectural Insight](#core-architectural-insight)
3. [Design Decisions](#design-decisions)
4. [Meta-Schema Architecture](#meta-schema-architecture)
5. [Extraction Method Specification](#extraction-method-specification)
6. [Future Architecture Evolution](#future-architecture-evolution)

## Problem Analysis

### Fundamental Issue in Single-Stage Theory Application

Traditional approaches to computational theory application attempt to:
1. Load theory definitions
2. Apply theory directly to analysis questions
3. Generate analysis results

This approach creates several architectural problems:

**Problem 1: Theory-Question Coupling**
- Analysis questions drive what gets extracted from theories
- Missing theoretical components not relevant to immediate questions
- Inability to reuse theoretical structure for different questions

**Problem 2: Context Loss**
- Theory application loses original theoretical context
- Difficult to trace analysis back to specific theoretical claims
- Theory modifications require complete re-analysis

**Problem 3: Limited Reusability**
- Each analysis question requires separate theory processing
- No accumulation of theoretical understanding over time
- Inefficient for multiple analyses using the same theory

## Core Architectural Insight

### Two-Layer Separation of Concerns

**Layer 1: Theory Structure Extraction**
- **Purpose**: Extract complete theoretical structure independent of analysis questions
- **Scope**: Capture all theoretical components comprehensively
- **Output**: Structured representation of theory suitable for multiple analytical purposes
- **Reusability**: One extraction serves multiple analytical questions

**Layer 2: Question-Driven Analysis**
- **Purpose**: Apply extracted theoretical structure to specific research questions
- **Input**: Pre-extracted theoretical structure from Layer 1
- **Process**: Select relevant theory components based on analytical requirements
- **Output**: Question-specific analysis using appropriate theoretical elements

### Architectural Benefits

**Flexibility**: Same theoretical extraction supports diverse analytical approaches
**Efficiency**: Theory processing occurs once, analysis questions multiple times
**Traceability**: Clear lineage from analysis results back to specific theoretical components
**Reusability**: Theoretical structures accumulate and can be shared across projects
**Quality**: Comprehensive extraction not biased by immediate analytical needs

## Design Decisions

### Decision 1: Complete vs Selective Extraction

**Decision**: Extract complete theoretical structure regardless of immediate analytical needs

**Rationale**:
- Theories contain interrelated components that may become relevant in future analyses
- Selective extraction risks losing important theoretical nuances
- Complete extraction enables serendipitous discovery of relevant theoretical elements
- Storage and processing costs are manageable for academic-scale theory libraries

**Trade-offs**:
- Future-proofing: Theories ready for unanticipated analytical questions
- Theoretical integrity: Preserves complete theoretical context
- Initial processing time: Longer extraction time for complete coverage
- Storage requirements: Larger theoretical representations

### Decision 2: LLM-Based vs Rule-Based Extraction

**Decision**: Use LLM-based extraction with structured V13 meta-schema guidance

**Rationale**:
- Theories use natural language that requires semantic understanding
- Rule-based systems cannot handle theoretical diversity and nuance
- LLMs can interpret theoretical context and relationships
- Structured guidance ensures consistent extraction across theories

**Trade-offs**:
- Semantic understanding: Handles complex theoretical language
- Adaptability: Works across diverse theoretical approaches
- Consistency: May interpret theories differently across runs
- Determinism: Results may vary with model updates

### Decision 3: Single vs Multiple Meta-Schema Approaches

**Decision**: Use single meta-schema (V13) with operational component categories

**Rationale**:
- Enables consistent comparison across different theories
- Simplifies tooling and analysis infrastructure
- Provides standardized interface for Layer 2 applications
- Reduces complexity while maintaining theoretical coverage

**Trade-offs**:
- Consistency: Uniform structure across all theories
- Tooling simplicity: Single interface for all theoretical applications
- Theoretical diversity: May not capture domain-specific theoretical elements
- Flexibility: Cannot optimize extraction for specific theory types

## Meta-Schema Architecture

### V13 Meta-Schema: Six-Category Operational Framework

**Design Principle**: Capture theoretical components that can be operationalized for computational analysis

#### Category 1: Entities
**Definition**: Core concepts, constructs, variables, and theoretical objects
**Purpose**: Identify the fundamental building blocks of theoretical understanding
**Examples**: 
- Social identity, group membership, intergroup bias (Social Identity Theory)
- Perceived behavioral control, attitude, intention (Theory of Reasoned Action)
- Loss aversion, reference point, value function (Prospect Theory)

#### Category 2: Relations
**Definition**: Relationships between entities, causal links, dependencies, and interactions
**Purpose**: Capture theoretical claims about how concepts relate to each other
**Examples**:
- Group membership → in-group favoritism (Social Identity Theory)
- Attitude + subjective norms → behavioral intention (Theory of Reasoned Action)
- Loss framing → risk-seeking behavior (Prospect Theory)

#### Category 3: Assumptions
**Definition**: Foundational assumptions, scope conditions, and theoretical boundaries
**Purpose**: Define when and where the theory applies
**Examples**:
- People categorize themselves into social groups (Social Identity Theory)
- Behavior is rational and under volitional control (Theory of Reasoned Action)
- People evaluate outcomes relative to reference points (Prospect Theory)

#### Category 4: Processes
**Definition**: Mechanisms, procedures, algorithms, and operational sequences
**Purpose**: Specify how theoretical relationships operate in practice
**Examples**:
- Social categorization → social comparison → in-group bias (Social Identity Theory)
- Belief formation → attitude formation → intention formation (Theory of Reasoned Action)
- Reference point establishment → outcome evaluation → choice (Prospect Theory)

#### Category 5: Measurement
**Definition**: Operationalization approaches, indicators, metrics, and assessment methods
**Purpose**: Connect theoretical concepts to empirical measurement
**Examples**:
- In-group identification scales, implicit association tests (Social Identity Theory)
- Semantic differential scales, behavioral intention measures (Theory of Reasoned Action)
- Choice tasks, certainty equivalents, utility assessments (Prospect Theory)

#### Category 6: Context
**Definition**: Boundary conditions, applicability scope, and environmental factors
**Purpose**: Define the theoretical scope and applicability limits
**Examples**:
- Relevant for intergroup contexts with salient group boundaries (Social Identity Theory)
- Applies to deliberate, planned behaviors (Theory of Reasoned Action)
- Relevant for decision-making under risk and uncertainty (Prospect Theory)

### Meta-Schema Design Principles

**Operational Focus**: Categories emphasize actionable, computable theoretical elements
**Cross-Domain Compatibility**: Framework works across mathematical, taxonomic, causal, and procedural theories
**LLM Optimization**: Categories align with natural language model capabilities
**Complete Coverage**: Six categories capture all essential theoretical components
**Standardization**: Consistent structure enables cross-theory comparison and analysis

## Extraction Method Specification

### Core Extraction Architecture

**Input Processing**:
- Accept theoretical documents in natural language format
- Parse document structure and identify theoretical content sections
- Prepare content for systematic component extraction

**Component Extraction Process**:
1. **Entity Identification**: Extract theoretical concepts and constructs
2. **Relationship Mapping**: Identify connections and causal claims between entities
3. **Assumption Extraction**: Capture foundational assumptions and scope conditions
4. **Process Specification**: Define mechanisms and operational sequences
5. **Measurement Integration**: Extract operationalization and assessment approaches
6. **Context Definition**: Identify boundary conditions and applicability scope

**Output Structure**:
- Structured theoretical representation using V13 meta-schema
- JSON/YAML format suitable for computational processing
- Preserved links to original theoretical text for traceability
- Metadata including extraction method, quality assessment, and provenance

### Quality Assurance Architecture

**Extraction Quality Criteria**:
- **Completeness**: All relevant theoretical components captured
- **Accuracy**: Extracted components correctly represent theoretical claims
- **Operational Clarity**: Components defined sufficiently for computational use
- **Relationship Fidelity**: Inter-component relationships properly specified

**Quality Assessment Methods**:
- **Automated Assessment**: LLM-based evaluation of extraction completeness and accuracy
- **Cross-Validation**: Multiple extraction attempts for consistency verification
- **Expert Review**: Domain expert validation for critical theoretical extractions
- **Template Matching**: Consistency checks against established theoretical templates

### Alternative Extraction Approaches

**Standard Single-Pass Method**:
- **Architecture**: Direct extraction using V13 meta-schema with component-specific prompts
- **Process**: Single comprehensive processing pass through theoretical content
- **Optimization**: Speed-optimized while maintaining extraction quality
- **Use Cases**: Large-scale theory processing, batch extraction operations

**Context-Aware Refinement Method**:
- **Architecture**: Multi-pass extraction with iterative improvement
- **Process Flow**:
  1. Initial extraction pass using enhanced V13 prompts
  2. Context-aware refinement passes using previous extraction as context
  3. Automatic termination when extraction quality criteria met
- **Optimization**: Quality-optimized for maximum theoretical component capture
- **Use Cases**: Critical theoretical extractions, high-stakes analytical applications

## Future Architecture Evolution

### Immediate Architectural Enhancements
1. **Multi-Schema Support**: Enable domain-specific meta-schema variants while maintaining V13 core
2. **Quality Metrics**: Develop objective theoretical extraction quality measures
3. **Theory Integration**: Architecture for combining multiple theoretical frameworks
4. **Cross-Theory Analysis**: Tools for systematic theoretical comparison and synthesis

### Medium-Term Architectural Development
1. **Theory Composition Engine**: Systematic combination of multiple theoretical frameworks
2. **Dynamic Schema Evolution**: Meta-schema adaptation based on theoretical domain characteristics
3. **Natural Language Query Interface**: Architecture for natural language theory questions
4. **Expert Validation Framework**: Integration of domain expert feedback into extraction quality

### Long-Term Vision
1. **Theoretical Knowledge Graph**: Interconnected representation of theoretical relationships across domains
2. **Predictive Theory Selection**: Intelligent recommendation of theories for analytical questions
3. **Theory Evolution Tracking**: Architecture for tracking theoretical development over time
4. **Automated Theory Discovery**: Identification of emergent theoretical patterns across literature

## Architecture Constraints and Limitations

### Current Architectural Constraints
- **Single Meta-Schema**: V13 framework may not capture all domain-specific theoretical elements
- **LLM Dependency**: Extraction quality limited by language model capabilities
- **English Language**: Current architecture optimized for English-language theories
- **Text-Based**: Limited support for mathematical or formal logical theoretical representations

### Scalability Considerations
- **Theory Library Size**: Architecture scales to thousands of theories per domain
- **Extraction Performance**: Processing time scales linearly with theoretical complexity
- **Storage Requirements**: Structured theoretical representations require moderate storage
- **Query Performance**: Layer 2 analysis performance depends on theoretical library size

### Quality Limitations
- **Interpretation Variability**: Different LLMs may extract different theoretical elements
- **Context Dependency**: Extraction quality depends on theoretical presentation quality
- **Expert Validation**: No automated substitute for domain expert theoretical assessment
- **Cross-Cultural Validity**: Theories may lose meaning when extracted from cultural context

This architecture provides the foundation for systematic theoretical analysis while maintaining flexibility for diverse analytical applications and future evolution.