# Architecture Diagrams

This directory contains visual representations of KGAS architectural components and flows.

## IC-Informed Uncertainty Framework Diagrams

The current uncertainty framework is based on ADR-029 and the Comprehensive7 specification, which superseded the previous Bayesian approach.

### Core Diagrams

1. **[ic-uncertainty-framework-overview.md](ic-uncertainty-framework-overview.md)**
   - High-level architecture flow showing the complete uncertainty pipeline
   - Comparison with superseded Bayesian approach
   - Key components: IC standards, single LLM analysis, mathematical propagation

2. **[ic-uncertainty-propagation-flow.md](ic-uncertainty-propagation-flow.md)**
   - Detailed propagation pipeline from source quality to final IC bands
   - Stage-by-stage uncertainty calculation
   - Root-sum-squares (RSS) mathematical propagation
   - Mapping from total uncertainty to IC probability bands

3. **[ic-uncertainty-analysis-components.md](ic-uncertainty-analysis-components.md)**
   - Breakdown of the single integrated LLM analysis call
   - Six IC methodology components in detail
   - ICD-203 probability standards reference
   - ICD-206 source quality framework

4. **[ic-uncertainty-entity-resolution.md](ic-uncertainty-entity-resolution.md)**
   - Entity resolution with realistic confidence ranges
   - Five reference type classifications with confidence bands
   - Evidence-based resolution (not format-based)
   - Integration with IC principles

5. **[ic-uncertainty-mermaid-flow.md](ic-uncertainty-mermaid-flow.md)**
   - Mermaid diagram versions for integration with documentation tools
   - Overall system flow
   - Entity resolution flow
   - Uncertainty propagation visualization
   - IC analysis components

### Key Principles Visualized

- **Single LLM Call**: One comprehensive analysis instead of fragmented calls
- **Mathematical Rigor**: Hard-coded RSS propagation, not LLM-estimated
- **IC Standards**: ICD-203 probability bands and ICD-206 quality assessment
- **Realistic Confidence**: Evidence-based ranges for different scenarios
- **Transparent Calculation**: Clear propagation from sources to final assessment

## Other System Diagrams

- **[component-interaction-diagrams.md](component-interaction-diagrams.md)** - General system component interactions
- **[uncertainty-propagation-flow.md](uncertainty-propagation-flow.md)** - (To be reviewed for ADR-029 alignment)

## Archived Diagrams

The following diagrams were archived on 2025-01-29 as they represent the superseded Bayesian uncertainty approach:
- `bayesian_network_diagram.md` - Moved to `archive/docs-architecture/`
- `bayesian_network_mermaid.md` - Moved to `archive/docs-architecture/`

These diagrams showed stage-based Bayesian networks with probabilistic dependencies, which no longer align with the current IC-informed framework that uses mathematical propagation and IC methodologies.

## Usage Guidelines

When referencing uncertainty handling in KGAS:
1. Use the IC-informed diagrams for current architecture
2. Refer to ADR-029 for the authoritative uncertainty framework
3. The Comprehensive7 specification provides implementation details
4. Archived Bayesian diagrams are historical only

## Creating New Diagrams

When creating new architectural diagrams:
1. Ensure alignment with current ADRs
2. Use consistent notation and formatting
3. Include both ASCII-art and Mermaid versions when applicable
4. Reference relevant ADRs and specifications
5. Update this README with new diagram descriptions