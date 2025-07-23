# IC-Inspired Uncertainty Features - Stress Test Suite

This directory contains comprehensive stress tests for the Intelligence Community (IC) inspired features in KGAS. These tests demonstrate how academic research can benefit from analytical techniques developed by the intelligence community.

## Features Tested

### 1. Information Value Assessment (Heuer's 4 Types)
- **File**: `test_information_value_assessment.py`
- **Purpose**: Tests the system's ability to categorize information according to Richards Heuer's framework
- **Categories**:
  - Diagnostic: Helps distinguish between hypotheses
  - Consistent: Supports multiple hypotheses equally
  - Anomalous: Contradicts all current hypotheses
  - Irrelevant: No bearing on any hypothesis
- **Scenarios**: Shakespeare authorship, Bronze Age collapse

### 2. Stopping Rules for Information Collection
- **File**: `test_stopping_rules.py`
- **Purpose**: Tests when to stop collecting additional information
- **Rules Implemented**:
  - Diminishing returns
  - Confidence threshold
  - Cost-benefit analysis
  - Time constraints
  - Convergence detection
  - Sufficient discrimination
- **Scenarios**: Climate change analysis, drug efficacy meta-analysis

### 3. ACH (Analysis of Competing Hypotheses) Theory Competition
- **File**: `test_ach_theory_competition.py`
- **Purpose**: Tests systematic evaluation of multiple competing theories
- **Features**:
  - Bayesian probability updates
  - Evidence diagnosticity calculation
  - Sensitivity analysis
  - Hypothesis ranking
- **Scenarios**: Maya civilization collapse, dark matter detection

### 4. Calibration System
- **File**: `test_calibration_system.py`
- **Purpose**: Tests confidence calibration and uncertainty estimation
- **Metrics**:
  - Brier score
  - Overconfidence/underconfidence detection
  - Resolution and reliability
  - Category-specific calibration
- **Scenarios**: Academic predictions, large-scale calibration analysis

### 5. Mental Model Auditing
- **File**: `test_mental_model_auditing.py`
- **Purpose**: Tests detection and correction of cognitive biases
- **Biases Detected**:
  - Confirmation bias
  - Availability heuristic
  - Anchoring bias
  - Representativeness
  - Hindsight bias
  - Overconfidence
  - Base rate neglect
  - Framing effects
  - Sunk cost fallacy
  - Groupthink
- **Scenarios**: Literary research, climate science

## Running the Tests

### Run All Tests
```bash
python run_all_tests.py
```

### Run Individual Tests
```bash
python test_information_value_assessment.py
python test_stopping_rules.py
python test_ach_theory_competition.py
python test_calibration_system.py
python test_mental_model_auditing.py
```

## Test Structure

Each test file contains:
1. **Implementation**: Working implementation of the IC-inspired feature
2. **Academic Scenarios**: Realistic research scenarios with synthetic data
3. **Stress Testing**: Large-scale processing tests
4. **Edge Cases**: Handling of unusual or extreme inputs
5. **Report Generation**: Comprehensive analysis of results

## Key Findings

### Information Value Assessment
- Successfully categorizes information by diagnostic value
- Handles 1000+ information pieces efficiently
- Properly identifies anomalous information requiring new hypotheses

### Stopping Rules
- Multiple rules can be combined with different strategies (any, all, majority)
- Prevents both premature stopping and over-collection
- Adapts to different research contexts

### ACH Competition
- Effectively manages 50+ competing hypotheses
- Diagnostic evidence correctly prioritized
- Sensitivity analysis identifies critical evidence

### Calibration System
- Detects systematic overconfidence/underconfidence
- Provides actionable feedback for improvement
- Tracks calibration across different categories

### Mental Model Auditing
- Detects 10 different cognitive biases
- Generates specific debiasing strategies
- Scales to analyze 100+ mental models

## Integration with KGAS

These features can be integrated into KGAS Phase 2 tools:

1. **T50-T60 (Graph Analytics)**: Use ACH for theory comparison
2. **T61-T70 (Statistical Analysis)**: Apply calibration to confidence intervals
3. **T71-T80 (Machine Learning)**: Use stopping rules for model selection
4. **T81-T90 (Research Integration)**: Apply mental model auditing to peer review

## Academic Applications

1. **Literature Reviews**: Information value assessment for source prioritization
2. **Meta-Analysis**: Stopping rules for study inclusion decisions
3. **Theory Development**: ACH for systematic theory comparison
4. **Peer Review**: Mental model auditing for bias detection
5. **Research Planning**: Calibration for project timeline estimation

## Performance Metrics

- Information Assessment: 1000 pieces in <1 second
- Stopping Rules: Real-time decision making
- ACH Competition: 50 hypotheses with 100 evidence pieces in <1 second
- Calibration: 1000+ predictions processed efficiently
- Mental Model Audit: 100 models analyzed in seconds

## Future Enhancements

1. **Machine Learning Integration**: Train models on historical decisions
2. **Visualization**: Interactive dashboards for bias detection
3. **Collaborative Features**: Multi-analyst fusion techniques
4. **Domain Adaptation**: Customize for specific research fields
5. **API Development**: RESTful endpoints for integration

## References

- Heuer, R. J. (1999). Psychology of Intelligence Analysis
- Kahneman, D. (2011). Thinking, Fast and Slow
- Tetlock, P. E. (2005). Expert Political Judgment
- Moore, D. A., & Healy, P. J. (2008). The trouble with overconfidence