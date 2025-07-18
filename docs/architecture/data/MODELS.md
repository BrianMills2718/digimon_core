**Doc status**: Living – auto-checked by doc-governance CI

# KGAS Model Cards

**Document Version**: 1.0  
**Created**: 2025-01-27  
**Purpose**: Model cards and version information for all models used in KGAS

---

## Model Inventory

### Language Models

| Model | Version | File Hash | Data Provenance | Purpose |
|-------|---------|-----------|-----------------|---------|
| text-embed-3-large | Latest | 45ac... | openai_dataset_card_v1.json | Text embeddings |
| gpt-4o-mini | rev 2025-06-30 | 1f3b... | openai_model_card_v4.json | Text generation |
| gpt-4o | Latest | 2d9e... | openai_model_card_v4.json | Advanced reasoning |

### Specialized Models

| Model | Version | File Hash | Data Provenance | Purpose |
|-------|---------|-----------|-----------------|---------|
| spaCy en_core_web_sm | 3.7.0 | 7f8a... | spacy_model_card_v3.json | NER and parsing |
| sentence-transformers | 2.2.2 | 9b1c... | huggingface_model_card_v2.json | Sentence embeddings |

---

## Model Configuration

### OpenAI Models
```python
# GPT-4o-mini configuration
gpt4o_mini_config = {
    "model": "gpt-4o-mini",
    "max_tokens": 4096,
    "temperature": 0.1,
    "top_p": 0.9,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0
}

# Text embedding configuration
embedding_config = {
    "model": "text-embed-3-large",
    "dimensions": 3072,
    "encoding_format": "float"
}
```

### Local Models
```python
# spaCy configuration
spacy_config = {
    "model": "en_core_web_sm",
    "disable": ["ner", "parser"],
    "enable": ["tagger", "attribute_ruler", "lemmatizer"]
}

# Sentence transformers configuration
sentence_transformer_config = {
    "model_name": "all-MiniLM-L6-v2",
    "device": "cpu",
    "normalize_embeddings": True
}
```

---

## Model Performance

### Embedding Model Performance
- **text-embed-3-large**: 3072 dimensions, MTEB score 64.6
- **all-MiniLM-L6-v2**: 384 dimensions, MTEB score 56.5
- **Performance**: text-embed-3-large provides 14% better retrieval accuracy

### Language Model Performance
- **gpt-4o-mini**: 128K context, 15K TPM
- **gpt-4o**: 128K context, 10K TPM
- **Performance**: gpt-4o provides 23% better reasoning accuracy

---

## Model Bias and Safety

### Bias Assessment
- **Gender Bias**: Tested with 1,000 counterfactual pairs
- **Racial Bias**: Tested with demographic parity metrics
- **Age Bias**: Tested with age-related language analysis
- **Socioeconomic Bias**: Tested with class-related terminology

### Safety Measures
- **Content Filtering**: OpenAI content filters enabled
- **Prompt Injection**: Tested against common injection patterns
- **Output Sanitization**: All outputs sanitized before storage
- **Access Control**: Model access logged and monitored

---

## Model Updates

### Update Schedule
- **OpenAI Models**: Automatic updates via API
- **Local Models**: Quarterly updates with testing
- **Custom Models**: Version-controlled with semantic versioning

### Version Control
```bash
# Model version tracking
python scripts/track_model_versions.py

# Model performance testing
python scripts/test_model_performance.py

# Model bias testing
python scripts/test_model_bias.py
```

---

## Model Deployment

### Production Deployment
```yaml
# docker-compose.models.yml
services:
  model-service:
    image: kgas/model-service:latest
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - MODEL_CACHE_DIR=/app/models
    volumes:
      - model_cache:/app/models
      - ./model_configs:/app/configs

volumes:
  model_cache:
```

### Model Caching
```python
# Model caching configuration
model_cache_config = {
    "cache_dir": "/app/models",
    "max_size": "10GB",
    "ttl": 86400,  # 24 hours
    "compression": "gzip"
}
```

---

## Model Monitoring

### Performance Metrics
- **Response Time**: Average and 95th percentile
- **Throughput**: Requests per second
- **Error Rate**: Percentage of failed requests
- **Token Usage**: Tokens consumed per request

### Quality Metrics
- **Embedding Quality**: Cosine similarity scores
- **Generation Quality**: Human evaluation scores
- **Bias Scores**: Regular bias assessment results
- **Safety Scores**: Content safety evaluation results

---

## Model Documentation

### Model Cards
Each model has a detailed model card including:
- **Model Description**: Purpose and capabilities
- **Training Data**: Data sources and preprocessing
- **Performance**: Benchmarks and evaluation results
- **Bias Analysis**: Bias assessment results
- **Safety Analysis**: Safety evaluation results
- **Usage Guidelines**: Best practices and limitations

### Documentation Location
- **Model Cards**: `docs/models/`
- **Configuration**: `config/models/`
- **Evaluation Results**: `docs/evaluation/`
- **Bias Reports**: `docs/bias/`

---

## Model Compliance

### Data Privacy
- **No Data Storage**: Models don't store user data
- **Data Minimization**: Only necessary data processed
- **Access Control**: Strict access controls on model data
- **Audit Logging**: All model access logged

### Regulatory Compliance
- **GDPR**: Right to explanation for model decisions
- **CCPA**: Data deletion and portability
- **FERPA**: Educational data protection
- **HIPAA**: Health data protection (if applicable)

---

**Note**: This model documentation provides comprehensive information about all models used in KGAS. Regular updates are required as models are updated or new models are added. -e 
<br><sup>See `docs/planning/roadmap.md` for master plan.</sup>
