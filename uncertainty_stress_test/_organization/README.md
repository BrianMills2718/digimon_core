# File Organization Summary

This directory organizes all files in `/uncertainty_stress_test` into 4 categories using symbolic links.

## 📁 Directory Structure

### `/useful_scripts/` (25+ files)
**Active, production-ready code that should be maintained:**
- Core LLM personality prediction system
- Alternative prediction methods (BERT, Bayesian, Traditional ML, etc.)
- Evaluation and comparison frameworks  
- **Uncertainty analysis and confidence scoring engines**
- Essential datasets (100 users, 500 tweets each)
- Configuration files

**Key Files:**
- `working_llm_personality_system.py` - Main LLM system
- `quick_test_personality_system.py` - Simplified test system
- `real_bert_predictor.py` - BERT implementation
- `run_complete_comparison.py` - Comprehensive evaluation
- `100_users_500tweets_dataset.json` - Core dataset
- `core_services/` - **Advanced uncertainty quantification engines**
  - `uncertainty_engine.py` - Main uncertainty orchestrator
  - `bayesian_aggregation_service.py` - LLM-powered Bayesian inference
  - `formal_bayesian_llm_engine.py` - Rigorous Bayesian mathematics
  - `cerqual_assessor.py` - Research quality assessment

### `/nonuseful_scripts/` (~70 files)
**Experimental, legacy, or superseded code:**
- Draft implementations replaced by "real" versions
- One-off test and demo scripts
- Historical archive directories
- Kunst-specific validation scripts
- Mock/fallback implementations

### `/useful_documentation/` (12 files)
**Current, actionable documentation:**
- Implementation guides and handoffs
- Final honest assessments and critical evaluations
- Success documentation showing what works
- Historical methodology (for context)
- BERT and Bayesian tool documentation

**Key Files:**
- `FINAL_BRUTAL_HONEST_ASSESSMENT.md` - Honest evaluation of methods
- `HANDOFF_DETAILED.md` - Technical implementation details
- `IMPLEMENTATION_COMPLETE.md` - Current implementation status

### `/nonuseful_documentation/` (~55 files)
**Outdated, draft, or superseded documentation:**
- Early draft assessments replaced by final versions
- Incomplete systematic summaries
- Historical analysis documents
- Experimental validation reports

## 🎯 Current Focus Areas

Based on the file organization, the **useful scripts** show that you have:

1. **Working LLM Personality Prediction System** with 4 strategies:
   - Direct Survey Mapping (works: r=0.75-0.81 for political)
   - Behavioral Pattern Analysis
   - Comparative Assessment  
   - Multi-Perspective Analysis

2. **Alternative Prediction Methods** ready for comparison:
   - BERT predictor
   - Traditional ML (Random Forest/XGBoost)
   - Bayesian predictor
   - Transformer models
   - Linguistic/temporal/network analysis

3. **Advanced Uncertainty Analysis Infrastructure**:
   - LLM-powered Bayesian evidence aggregation
   - CERQual research quality assessment framework
   - Formal Bayesian mathematics with LLM parameters
   - Confidence scoring and uncertainty quantification engines

4. **Missing Piece**: Comprehensive evaluation comparing ALL methods across ALL 4 personality scales, potentially enhanced with uncertainty quantification

## 🚀 Next Steps

The useful scripts contain everything needed to:

1. **Generate comprehensive correlation table** showing r values for each method on each personality dimension (Political, Narcissism, Conspiracy, Denialism)

2. **Enhance with uncertainty quantification** using the core_services engines to provide confidence intervals and evidence quality assessments for predictions

3. **Integrate personality prediction with broader uncertainty analysis framework** - personality prediction appears to be one component of a larger knowledge analysis system

## 📊 File Counts
- Total files analyzed: ~200
- Useful scripts: 25+ (core functionality + uncertainty engines)
- Non-useful scripts: ~65 (experimental/legacy)
- Useful documentation: 15 (current guides)
- Non-useful documentation: ~55 (outdated/draft)

All files remain in their original locations - this organization uses symbolic links for easy navigation without disrupting the existing structure.