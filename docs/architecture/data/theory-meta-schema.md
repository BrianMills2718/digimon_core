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
