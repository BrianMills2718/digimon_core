# ADR-004: Normative Confidence Score Ontology

*Status: **SUPERSEDED by ADR-007** - 2025-01-18 (original), 2025-07-20 (superseded)*

## Supersession Notice

This ADR has been superseded by [ADR-007: CERQual-Based Uncertainty Architecture](./ADR-007-uncertainty-metrics.md). The simple confidence score approach described here was found insufficient for academic social science research requirements. ADR-007 introduces a more sophisticated CERQual-based uncertainty quantification framework.

## Context

KGAS currently allows each extraction or analysis tool to output its own notion of *confidence* or *uncertainty*. This flexibility has led to incompatible semantics across tools (e.g., some use logits, others probabilities, others custom scales). The external architectural review identified this as a critical source of "capability sprawl" and potential integration breakage.

## Decision

1. A single, mandatory Pydantic model named `ConfidenceScore` becomes part of the canonical contract system.
2. All tool contracts **MUST** express confidence and related uncertainty using this model—no bespoke fields.
3. The model fields are:
   ```python
   class ConfidenceScore(BaseModel):
       value: confloat(ge=0.0, le=1.0)  # Normalised probability-like confidence
       evidence_weight: PositiveInt      # Number of independent evidence items supporting the value
       propagation_method: Literal[
           "bayesian_evidence_power",
           "dempster_shafer",
           "min_max",
       ]
   ```
4. The `propagation_method` **must** be recorded in provenance metadata for every derived result, enabling reproducible downstream comparisons.
5. A tool that cannot currently compute a valid confidence must set `value=None` and `propagation_method="unknown"`, and raise a contract warning.

## Consequences

* Contract System: The `contract-system.md` documentation is updated to reference this ontology.
* Quality Service: Must be refactored to select an aggregation algorithm based on `propagation_method`.
* Migration: Existing tools will undergo a one-time update to conform to the new model.
* Future Work: Support for additional propagation methods will be added via enumeration expansion, requiring no schema change.

## Alternatives Considered

* **Leave-as-is:** Rejected—does not solve integration problems.
* **Free-text confidence fields:** Rejected—unverifiable and non-interoperable.

## Related Documents

* External Review (2024-07-18)
* `docs/architecture/systems/contract-system.md` (to be updated)

--- 