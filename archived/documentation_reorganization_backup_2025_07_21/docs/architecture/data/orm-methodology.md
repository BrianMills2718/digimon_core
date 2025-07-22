---
status: living
---

# Object-Role Modeling (ORM) in KGAS

## Overview

Object-Role Modeling (ORM) is the conceptual backbone of KGAS's ontology and data model design. It ensures semantic clarity, natural language alignment, and explicit constraint definition.

## Core ORM Concepts

- **Object Types**: Kinds of things (e.g., Person, Organization)
- **Fact Types**: Elementary relationships (e.g., "Person [has] Name")
- **Roles**: The part an object plays in a fact (e.g., "Identifier")
- **Value Types/Attributes**: Properties (e.g., "credibility_score")
- **Qualifiers/Constraints**: Modifiers or schema rules

## ORM-to-KGAS Mapping

| ORM Concept      | KGAS Implementation         | Example                |
|------------------|----------------------------|------------------------|
| Object Type      | Entity                     | `IndividualActor`      |
| Fact Type        | Relationship (Connection)  | `IdentifiesWith`       |
| Role             | source_role_name, target_role_name | `Identifier` |
| Value Type       | Property                   | `CredibilityScore`     |
| Value Type       | Property                   | `confidence_score: float` |
| Qualifier        | Modifier/Pydantic validator| Temporal modifier      |

## Hybrid Storage Justification

| Storage System | ORM Mapping | Justification |
|----------------|-------------|---------------|
| **Neo4j** | Object Types → nodes, Fact Types → edges | Graph traversal and relationship queries |
| **SQLite** | Object Types → tables, Fact Types → foreign keys | Transactional metadata and workflow state |
| **Neo4j Vector Index** | ORM concepts guide embedding strategies | Vector similarity and semantic search |

## DOLCE ↔ ORM Mapping Cheatsheet

| DOLCE Parent Class | ORM Object Type | KGAS Entity Type | Example |
|-------------------|-----------------|------------------|---------|
| `dolce:PhysicalObject` | Physical Entity | `PhysicalObject` | Document, Device |
| `dolce:SocialObject` | Social Entity | `SocialActor` | Person, Organization |
| `dolce:Abstract` | Abstract Entity | `Concept` | Theory, Policy |
| `dolce:Event` | Event Entity | `Event` | Meeting, Publication |
| `dolce:Quality` | Quality Entity | `Property` | Credibility, Influence |

## Implementation

- **Data Models**: Pydantic models with explicit roles and constraints
- **Validation**: Enforced at runtime and in CI/CD

## Further Reading

See `docs/architecture/ARCHITECTURE.md` for a summary and this file for full details.

<br><sup>See `docs/planning/roadmap.md` for master plan.</sup>
