---
status: living
---

# Theoretical Framework: Three-Dimensional Typology for KGAS

## Overview

KGAS organizes social-behavioral theories using a three-dimensional framework, enabling both human analysts and machines to reason about influence and persuasion in a structured, computable way.

## Analytical Purpose and Scope

### Primary Analytical Goal: **World Analysis**
KGAS uses discourse (text) as evidence to analyze real-world phenomena, following a hierarchical approach:

1. **Text Analysis** → Analyze properties of linguistic artifacts (foundation)
2. **World Analysis** → Use text evidence to understand real-world phenomena (primary goal) 
3. **Effect Analysis** → Predict how discourse affects readers/audiences (application)

### Input Scope: Discourse Analysis
**Supported inputs**:
- Excel sheets of tweets, social media posts
- Books, academic papers, reports
- Blog posts, news articles, editorials  
- Any form of written discourse or communication

**Theory Boundaries** (out of scope):
- Biological/physiological theories requiring lab data (hormone levels, brain scans)
- Economic theories needing market/financial data beyond discourse
- Environmental/physical theories requiring sensor/measurement data  
- Pure mathematical theories without empirical text manifestations

### Human-Guided Analysis
Analysis is driven by **human analytical questions** that specify the analysis tier:

**Question Types**:
- **Descriptive**: "What does this discourse describe?" (text properties)
- **Explanatory**: "What does this tell us about the world?" (world analysis)
- **Predictive**: "What effects might this discourse have?" (effect analysis)
- **Prescriptive**: "How should we intervene based on this understanding?" (design guidance)

**LLM Agent Guidance**: Frontier LLMs automatically select optimal analysis approaches based on:
- Human analytical question intent
- Theory requirements and specifications
- Cross-modal analysis tradeoffs and automation

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

### Theory Classification Process

**Hybrid Validation Approach**: The three-dimensional classification combines automated LLM processing with expert validation to ensure academic credibility:

1. **Validation Set Creation**: Domain experts manually classify a representative sample of theories (50-100 theories) to establish quality standards and calibrate confidence thresholds

2. **Automated Classification**: LLM processes theories using patterns learned from the expert validation set, applying the three-dimensional framework automatically

3. **Confidence-Based Review**: System flags low-confidence classifications for potential expert review, while high-confidence classifications proceed automatically

4. **Continuous Calibration**: Expert feedback from flagged cases improves the automated classification accuracy over time

**Classification Usage**:
- Theories are classified along these axes in the Theory Meta-Schema
- Classifications guide tool selection, LLM prompting, and analysis workflows
- Three-dimensional positioning enables systematic theory comparison and selection

## Analytical Tiers

KGAS supports four distinct analytical tiers, each serving different research purposes:

### 1. Descriptive Analysis (Text Properties)
**Focus**: What linguistic and structural patterns exist in the discourse?
- Identifies entities, relationships, and themes present in text
- Maps theoretical concepts to textual elements
- Quantifies linguistic features and patterns
- **Example**: "This political speech contains 47 fear-based appeals and 23 hope-based appeals"

### 2. Explanatory Analysis (World Understanding)  
**Focus**: What does this discourse reveal about real-world phenomena?
- Uses text as evidence for understanding external reality
- Explains why certain patterns appear in discourse
- Connects textual features to contextual factors
- **Example**: "The prevalence of security rhetoric reveals heightened threat perception in policy circles"

### 3. Predictive Analysis (Effect Forecasting)
**Focus**: How will this discourse affect audiences and outcomes?
- Forecasts behavioral responses to messages
- Predicts attitude changes from exposure
- Estimates persuasive impact of different frames
- **Example**: "This loss-framed message will increase opposition to the policy by 15-20%"

### 4. Prescriptive Analysis (Design Guidance)
**Focus**: How should discourse be crafted for desired outcomes?
- Recommends optimal message strategies
- Designs effective communication approaches
- Suggests improvements to existing content
- **Example**: "To increase support, reframe using gain language and concrete examples"

### Tier Selection Through Questions
The analytical tier is determined by the researcher's question:
- **"What patterns exist?"** → Descriptive
- **"What does this reveal?"** → Explanatory  
- **"What will happen?"** → Predictive
- **"What should we do?"** → Prescriptive

This explicit tier selection ensures focused analysis aligned with research goals.

## References

- Lasswell (1948), Druckman (2022), Eyster et al. (2022)
- [ADR-027: Analytical Purpose Clarification](../adrs/ADR-027-Analytical-Purpose-Clarification.md)

<br><sup>See `docs/roadmap/ROADMAP_OVERVIEW.md` for master plan.</sup>
