# MCL Concept Mediation System - Operational Specification

## Proven Capabilities (2025-07-21 Validation)

### Performance Metrics
- **Resolution Success Rate**: High-confidence mappings capability
- **Domain Coverage**: Political, stakeholder, resource domain terms
- **DOLCE Integration**: Upper-level ontology categories functional
- **Confidence Scoring**: Configurable thresholds per domain

### Validated Examples
- "President" → POLITICAL_LEADER (0.95 confidence)
- "Soviet Union" → NATION_STATE (0.98 confidence)
- "Government" → POLITICAL_ENTITY (0.89 confidence)
- "Relations" → RELATIONSHIP (0.91 confidence)

## Technical Implementation

### Core Components
- **Concept Mapping Database**: String to canonical concept mappings with confidence scores
- **Fallback Resolution**: Graceful handling of unknown terms with default categorization
- **Identity Integration**: Uses IdentityService for entity resolution and deduplication
- **Confidence Thresholds**: Configurable per domain and use case

### Integration Points
- **DOLCE Ontology**: Upper-level categories for general classification
- **IdentityService**: Entity resolution and mention management
- **Theory Schemas**: Domain-specific vocabulary integration
- **Tool Contracts**: Automatic concept validation in tool chains

## Validation Evidence

### Testing Results (2025-07-21)
- **Test Scope**: 13 terms from Carter speech analysis
- **Resolution Success**: 100% (all terms successfully mapped)
- **High Confidence**: Above 0.8 confidence threshold achievement
- **Implementation**: stress_test_2025.07211755/deep_integration_scenario.py lines 127-237

### Academic Application
- **Context**: 1977 Carter Charleston speech on Soviet-American relations
- **Theory**: Stakeholder theory with political entity mapping
- **Domain**: Political science and international relations terminology
- **Success**: Complete term resolution enabling theory operationalization