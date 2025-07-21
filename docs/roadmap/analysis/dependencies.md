# Dependency Documentation and Setup Automation

## Comprehensive Dependency Matrix

### Database Dependencies
| Dependency | Version     | Configured In                    | Used In                           | Health Check | Backup/Restore |
|------------|-------------|----------------------------------|-----------------------------------|--------------|----------------|
| Neo4j      | >=5.0.0     | docker-compose.yml, .env         | t31_entity_builder, t34_edge_builder, t68_pagerank, t49_multihop_query, t31_ontology_graph_builder, interactive_graph_visualizer | Docker healthcheck | Manual |
| Redis      | >=5.0.1     | docker-compose.yml, .env         | Optional caching/job queue        | Docker healthcheck | Manual |
| SQLAlchemy | >=2.0.23    | requirements.txt                 | Metadata storage                  | None | Manual |

### AI/ML API Dependencies
| Dependency         | Version  | Configured In        | Used In                              | Health Check | Rate Limiting |
|-------------------|----------|----------------------|--------------------------------------|--------------|---------------|
| OpenAI            | >=1.0.0  | .env, pyproject.toml | t41_text_embedder, t49_enhanced_query, identity_service | None | Manual |
| Google Gemini     | >=0.3.0  | .env, pyproject.toml | ontology_generator, gemini_ontology_generator | None | Manual |
| Anthropic         | Not listed | .env only          | API auth manager                     | None | Manual |
| HuggingFace       | Not listed | .env only          | API auth manager                     | None | Manual |
| Cohere            | Not listed | .env only          | API auth manager                     | None | Manual |
| Azure OpenAI      | Not listed | .env only          | API auth manager                     | None | Manual |

### NLP/ML Processing Dependencies
| Dependency           | Version   | Configured In        | Used In                    | Health Check | Notes |
|---------------------|-----------|----------------------|----------------------------|--------------|-------|
| spaCy               | >=3.4.0   | pyproject.toml       | t23a_spacy_ner             | None | Requires model download |
| sentence-transformers| >=2.2.0  | pyproject.toml       | Vector embeddings          | None | Model download required |
| scikit-learn        | >=1.1.0   | pyproject.toml       | ML processing              | None | |
| networkx            | >=2.8.0   | pyproject.toml       | Graph analysis             | None | |
| numpy               | >=1.21.0  | pyproject.toml       | Numerical processing       | None | |
| pandas              | >=1.5.0   | pyproject.toml       | Data processing            | None | |

### Framework Dependencies
| Dependency    | Version   | Configured In        | Used In                    | Health Check | Notes |
|--------------|-----------|----------------------|----------------------------|--------------|-------|
| FastMCP      | >=0.9.0   | requirements.txt     | MCP server                 | None | |
| MCP          | >=0.9.0   | requirements.txt     | MCP protocol               | None | |
| Streamlit    | >=1.28.0  | pyproject.toml       | Web UI                     | None | |
| Pydantic     | >=1.10.0  | pyproject.toml       | Data validation            | None | |
| PyPDF2       | >=3.0.0   | pyproject.toml       | PDF processing             | None | |

### Development Dependencies
| Dependency    | Version   | Configured In        | Used In                    | Health Check | Notes |
|--------------|-----------|----------------------|----------------------------|--------------|-------|
| pytest       | >=7.4.0   | requirements.txt     | Testing                    | None | |
| pytest-cov   | >=4.1.0   | requirements.txt     | Coverage                   | None | |
| black        | >=23.10.0 | requirements.txt     | Code formatting            | None | |
| mypy         | >=1.6.0   | requirements.txt     | Type checking              | None | |
| flake8       | >=6.1.0   | requirements.txt     | Linting                    | None | |

## Health Check & Diagnostic Status

### Current Health Checks
- **Neo4j**: Docker healthcheck via HTTP endpoint (localhost:7474/browser/)
- **Redis**: Docker healthcheck via redis-cli ping
- **Application**: Basic HTTP check in production Docker Compose

### Missing Health Checks
- **Qdrant**: No health check configured
- **API Services**: No connectivity checks for OpenAI, Google, etc.
- **Application Services**: No health endpoints for core services
- **Database Connections**: No connection pool health monitoring

## Backup/Restore Status

### Current Backup/Restore
- **Neo4j**: Manual backup via Docker volumes
- **Redis**: Manual backup via Docker volumes
- **Qdrant**: No automated backup configured

### Missing Backup/Restore
- **Automated scheduling**: No cron jobs or automated backup scripts
- **Cloud backup**: No offsite backup configured
- **Recovery procedures**: No documented restore procedures
- **Data export**: No regular data export scripts

## Configuration Fragmentation

### Environment Variables Used
- NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
- OPENAI_API_KEY, GOOGLE_API_KEY, ANTHROPIC_API_KEY, HUGGINGFACE_API_KEY, COHERE_API_KEY, AZURE_OPENAI_API_KEY
- REDIS_URL, QDRANT_URL
- GRAPHRAG_MODE, ENVIRONMENT, DEBUG, LOG_LEVEL

### Configuration Files
- `pyproject.toml`: Core dependencies
- `requirements.txt`: Additional dependencies
- `docker-compose.yml`: Development services
- `docker/production/docker-compose.prod.yml`: Production services
- `config/default.yaml`: Application configuration 