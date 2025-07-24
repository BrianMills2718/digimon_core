# Improved Agent Instructions for Paul Davis Document Analysis

## Project Context for Agents

### 🎯 **Our Uncertainty/Confidence Framework**
We've developed a dual-approach uncertainty quantification system:

1. **LLM-Native Contextual Intelligence Engine**
   - AI contextually determines what matters for each assessment
   - No hardcoded parameters - adapts to domain, claim type, evidence characteristics
   - 100% accuracy (7/7 test cases) vs 71% rule-based

2. **Formal Bayesian LLM Engine** 
   - LLM determines Bayesian parameters → rigorous mathematical updates
   - Addresses "mathematical hand-waving" critique
   - Combines AI intelligence with formal Bayes' theorem

### 🔍 **What We Need from Paul Davis Documents**

#### **Primary Extraction Targets**:
1. **Uncertainty representation methods** - How does Davis handle different types of uncertainty?
2. **Multi-method approaches** - Does Davis use multiple techniques? How does he choose?
3. **Evidence quality assessment** - How does Davis evaluate evidence strength/credibility?
4. **Validation under uncertainty** - What validation approaches work when ground truth is unclear?
5. **Contextual adaptation** - How does Davis adapt methods to different domains/situations?
6. **Soft information handling** - How does Davis deal with qualitative, ambiguous, conflicting evidence?

#### **Secondary Extraction Targets**:
7. **Bayesian methods** - Any Bayesian approaches, parameter selection, inference techniques
8. **Meta-uncertainty** - Uncertainty about uncertainty, confidence bounds
9. **Academic/research applications** - Applications to academic research, literature review, evidence synthesis
10. **Practical implementation** - Concrete tools, algorithms, workflows that could be applied

### 📋 **Agent Task Template**

Each agent should create a file: `/analysis/agent_extractions/[filename]_chunk_[XXX]_notes.md`

## Agent Instructions Template

```
AGENT MISSION: Extract insights from Paul Davis text relevant to uncertainty quantification methodology

PROJECT CONTEXT:
- We've built an uncertainty framework combining LLM contextual intelligence + formal Bayesian math
- We need validation, extensions, and practical implementation guidance from Davis's work
- Focus on methodological approaches that could improve or validate our framework

YOUR CHUNK: [filename] characters [start]-[end] (~X pages)

EXTRACTION REQUIREMENTS:

1. **Create detailed notes file**: Save comprehensive extraction to `/analysis/agent_extractions/[filename]_chunk_[XXX]_notes.md`

2. **Target-specific extraction**:
   - Uncertainty representation methods
   - Multi-method approaches and method selection
   - Evidence quality assessment techniques
   - Validation approaches under uncertainty
   - Contextual adaptation strategies
   - Handling of qualitative/ambiguous evidence
   - Bayesian methods and parameter selection
   - Meta-uncertainty and confidence bounds
   - Academic/research applications
   - Practical implementation details

3. **For each insight found**:
   - Direct quote with page/section reference
   - Explanation of the method/approach
   - Relevance to our uncertainty framework (high/medium/low)
   - Potential application or extension for our work
   - Implementation feasibility assessment

4. **Summary section**:
   - Top 5 most relevant insights from your chunk
   - Overall assessment of chunk's value for our project
   - Connections to insights from other chunks (if applicable)
   - Recommended follow-up analysis needed

READ THOROUGHLY: This is methodological research. Read every paragraph carefully looking for specific techniques, not just concept mentions.

OUTPUT: Comprehensive markdown notes file with detailed extraction and analysis.
```