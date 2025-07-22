---
status: living
---

# Provenance & Lineage in KGAS

## Overview
Provenance (lineage) tracking is implemented throughout KGAS to ensure every node and edge in the knowledge graph can be traced back to its generating activity, supporting full auditability and reproducibility.

## Provenance Object
Each theory instance and graph element includes a `provenance` object:
```json
{
  "source_chunk_id": "str",
  "prompt_hash": "str",
  "model_id": "str",
  "timestamp": "datetime"
}
```
- **source_chunk_id**: Unique ID of the input chunk or document
- **prompt_hash**: SHA-256 hash of the prompt or input
- **model_id**: Identifier for the LLM or tool used
- **timestamp**: ISO 8601 UTC timestamp of generation

## Hashing Rule
- All prompts/inputs are hashed using SHA-256.
- Hashes are stored alongside provenance metadata in the database.

## Storage
- Provenance objects are stored as part of each node/edge in the graph database.
- The `generated_by_activity_id` field links to the activity/process that created the element.

## CI Validation
- CI checks ensure every node/edge contract includes `generated_by_activity_id`.
- Provenance fields are validated for presence and correct format.
- See `scripts/verify_all_documentation_claims.sh` for automated checks.

## W3C PROV Compliance
- KGAS uses the W3C PROV model: `(Entity)-[GENERATED_BY]->(Activity)`.
- Enables full lineage queries and audit trails.

---
For more, see `ARCHITECTURE.md` and `CONTRACT_SYSTEM.md`. 