---
status: living
---

# KGAS Evaluation Framework

**Document Version**: 1.0  
**Created**: 2025-01-27  
**Purpose**: Evaluation metrics and procedures for the Knowledge Graph Analysis System

![Evaluation CI](https://github.com/your-org/kgas/actions/workflows/eval.yml/badge.svg)

---

## Evaluation Metrics

### Entity Extraction Evaluation
- **Precision**: Ratio of correctly extracted entities to total extracted entities
- **Recall**: Ratio of correctly extracted entities to total actual entities
- **F1-Score**: Harmonic mean of precision and recall
- **Accuracy**: Overall extraction accuracy

### Relationship Extraction Evaluation
- **Precision**: Ratio of correctly extracted relationships to total extracted relationships
- **Recall**: Ratio of correctly extracted relationships to total actual relationships
- **F1-Score**: Harmonic mean of precision and recall
- **Accuracy**: Overall relationship accuracy

### Graph Quality Evaluation
- **Connectivity**: Measures of graph connectivity and structure
- **Centrality**: Distribution of node centrality measures
- **Clustering**: Quality of community detection
- **Density**: Graph density measures

### Explainability Metrics
- **SHAP Coverage**: Percentage of predictions explained by SHAP values
- **LIME Coverage**: Percentage of predictions explained by LIME analysis
- **Feature Importance**: Ranking of feature importance in predictions
- **Decision Paths**: Clarity of decision paths in model predictions

### Weighted Metrics Using Confidence
- **Weighted Precision**: Precision weighted by confidence scores
- **Weighted Recall**: Recall weighted by confidence scores
- **Weighted F1-Score**: Harmonic mean of weighted precision and recall

All evaluation metrics are now computed both unweighted and weighted by the confidence assigned to each relationship edge.

## Benchmark 0.1

| Metric         | Value |
|---------------|-------|
| Entity F1     | 0.85  |
| Relation F1   | 0.78  |
| Dataset Size  | 1,000 documents |

- Gold labels: See `dataset/gold_labels/`
- Evaluation script: `python scripts/run_evaluation.py`

---

## Embedding Bias Probe

### Bias Detection Methodology
- **1,000 counterfactual sentence pairs** per protected term
- **Flag if cosine-distance drift Δ ≥ 0.10**
- **Job runs monthly** via GitHub Actions (`.github/workflows/bias.yml`)

Cron job: `.github/workflows/bias.yml` runs first day of each month, 02:00 UTC.

### Protected Terms
- **Gender terms**: male/female, man/woman, he/she, etc.
- **Race terms**: white/black, asian/latino, etc.
- **Age terms**: young/old, elderly/youth, etc.
- **Socioeconomic terms**: rich/poor, wealthy/impoverished, etc.

### Bias Detection Process
```python
def detect_bias(protected_terms, embedding_model):
    for term in protected_terms:
        # Generate counterfactual pairs
        pairs = generate_counterfactual_pairs(term)
        
        # Calculate cosine distances
        distances = []
        for pair in pairs:
            emb1 = embedding_model.encode(pair[0])
            emb2 = embedding_model.encode(pair[1])
            distance = cosine_distance(emb1, emb2)
            distances.append(distance)
        
        # Check for drift
        mean_distance = np.mean(distances)
        if mean_distance >= 0.10:
            flag_bias(term, mean_distance)
```

---

## Performance Evaluation

### Processing Speed
- **Document Processing Time**: Time to process a single document
- **Batch Processing Time**: Time to process multiple documents
- **Query Response Time**: Time to respond to user queries
- **System Throughput**: Documents processed per hour

### Resource Usage
- **Memory Usage**: Peak memory consumption during processing
- **CPU Usage**: CPU utilization during processing
- **Storage Usage**: Disk space used for data storage
- **Network Usage**: Bandwidth consumption for API calls

---

## Quality Evaluation

### Content Quality
- **Entity Accuracy**: Correctness of extracted entities
- **Relationship Accuracy**: Correctness of extracted relationships
- **Context Preservation**: Preservation of contextual information
- **Semantic Consistency**: Consistency of semantic meaning

### System Quality
- **Reliability**: System uptime and error rates
- **Scalability**: Performance under increased load
- **Usability**: User experience and interface quality
- **Maintainability**: Code quality and documentation

---

## Comparative Evaluation

### Baseline Comparison
- **Traditional NLP**: Compare with standard NLP approaches
- **GraphRAG Systems**: Compare with other GraphRAG implementations
- **Theory-Aware Systems**: Compare with theory-aware approaches
- **Academic Benchmarks**: Compare with academic benchmarks

### Evaluation Datasets
- **Standard Benchmarks**: Use established evaluation datasets
- **Domain-Specific**: Use domain-specific evaluation data
- **Synthetic Data**: Generate synthetic data for testing
- **Real-World Data**: Use real-world documents for evaluation

---

## Evaluation Procedures

### Automated Evaluation
```bash
# Run automated evaluation
python scripts/run_evaluation.py

# Generate evaluation report
python scripts/generate_evaluation_report.py

# Compare with baselines
python scripts/compare_with_baselines.py
```

### Manual Evaluation
```bash
# Set up manual evaluation environment
python scripts/setup_manual_evaluation.py

# Run manual evaluation tasks
python scripts/run_manual_evaluation.py

# Collect manual evaluation results
python scripts/collect_manual_results.py
```

---

## Evaluation Reporting

### Report Structure
1. **Executive Summary**: High-level evaluation results
2. **Methodology**: Evaluation methods and procedures
3. **Results**: Detailed evaluation results
4. **Analysis**: Analysis of results and insights
5. **Conclusions**: Conclusions and recommendations

### Report Generation
```bash
# Generate comprehensive report
python scripts/generate_comprehensive_report.py

# Generate executive summary
python scripts/generate_executive_summary.py

# Generate technical report
python scripts/generate_technical_report.py
```

---

## Continuous Evaluation

### Monitoring
- **Real-time Monitoring**: Monitor system performance in real-time
- **Periodic Evaluation**: Conduct periodic comprehensive evaluations
- **User Feedback**: Collect and analyze user feedback
- **System Logs**: Analyze system logs for performance insights

### Improvement
- **Performance Optimization**: Optimize system performance based on evaluation results
- **Quality Improvement**: Improve system quality based on evaluation feedback
- **Feature Enhancement**: Enhance features based on user needs
- **Bug Fixes**: Fix bugs identified through evaluation

---

## Evaluation Standards

### Academic Standards
- **Reproducibility**: All evaluations must be reproducible
- **Transparency**: Evaluation methods must be transparent
- **Objectivity**: Evaluations must be objective and unbiased
- **Completeness**: Evaluations must be comprehensive

### Industry Standards
- **Performance Benchmarks**: Meet industry performance benchmarks
- **Quality Standards**: Meet industry quality standards
- **Security Standards**: Meet industry security standards
- **Compliance Standards**: Meet relevant compliance standards

---

**Note**: This evaluation framework provides a comprehensive approach to evaluating the KGAS system. Regular evaluations should be conducted to ensure system quality and performance. -e 
<br><sup>See `docs/planning/roadmap.md` for master plan.</sup>
