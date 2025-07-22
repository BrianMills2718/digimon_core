---
status: living
---

# Theoretical Framework: Three-Dimensional Typology for KGAS

## Overview

KGAS organizes social-behavioral theories using a three-dimensional framework, enabling both human analysts and machines to reason about influence and persuasion in a structured, computable way.

## The Three Dimensions

Each theory includes a formal classification object:

```json
{
  "classification": {
    "domain": {
      "level": "Meso",
      "component": "Who", 
      "metatheory": "Interdependent"
    }
  }
}
```

1. **Level of Analysis (Scale)**
   - Micro: Individual-level (cognitive, personality)
   - Meso: Group/network-level (community, peer influence)
   - Macro: Societal-level (media effects, cultural norms)

2. **Component of Influence (Lever)**
   - Who: Speaker/Source
   - Whom: Receiver/Audience
   - What: Message/Treatment
   - Channel: Medium/Context
   - Effect: Outcome/Process

3. **Causal Metatheory (Logic)**
   - Agentic: Causation from individual agency
   - Structural: Causation from external structures
   - Interdependent: Causation from feedback between agents and structures

!INCLUDE "tables/theory_examples.md"

## Application

- Theories are classified along these axes in the Theory Meta-Schema.
- Guides tool selection, LLM prompting, and analysis workflows.

## References

- Lasswell (1948), Druckman (2022), Eyster et al. (2022)

<br><sup>See `docs/roadmap/ROADMAP_OVERVIEW.md` for master plan.</sup>
