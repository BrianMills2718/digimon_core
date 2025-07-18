# KGAS Configuration Directory

This directory contains all configuration files for the KGAS (Knowledge Graph Analysis System) organized in a structured manner.

## Directory Structure

```
config/
├── config.yaml                    # Main configuration file
├── config_loader.py               # Configuration loader utility
├── README.md                      # This file
├── environments/                  # Environment-specific configurations
│   ├── docker-compose.yml         # Development Docker Compose
│   └── docker-compose.prod.yml    # Production Docker Compose
├── monitoring/                    # Monitoring and observability configs
│   ├── docker-compose.monitoring.yml
│   ├── prometheus.yml
│   └── grafana-datasources.yml
├── schemas/                       # JSON/YAML schema definitions
│   └── tool_contract_schema.yaml
├── contracts/                     # Contract definitions
│   └── Phase1ToPhase2Adapter.yaml
└── examples/                      # Example configurations
    ├── gemini-review.yaml
    ├── docs-review.yaml
    └── verification-review.yaml
```

## Configuration Files

### Main Configuration (`config.yaml`)
The central configuration file that defines:
- Environment-specific settings (development, production)
- Monitoring configuration
- Contract system settings
- Core system parameters
- Security settings
- Performance tuning

### Configuration Loader (`config_loader.py`)
Python utility that provides:
- Environment-specific configuration loading
- Environment variable resolution
- Path resolution relative to config directory
- Type-safe configuration objects

## Environment Variables

The system supports the following environment variables:

- `KGAS_ENV`: Environment name (development, production) - defaults to 'development'
- `NEO4J_URL`: Neo4j database URL for production
- `LLM_PROVIDER`: LLM provider name for production
- `BACKUP_ENCRYPTION_PASSWORD`: Password for backup encryption

## Usage

### In Python Code
```python
from config.config_loader import get_settings

# Get settings for current environment
settings = get_settings()

# Get settings for specific environment
prod_settings = get_settings('production')

# Access configuration values
database_url = settings.database_url
max_concurrent = settings.max_concurrent_documents
```

### Environment-Specific Usage
```bash
# Use development environment (default)
export KGAS_ENV=development
python main.py

# Use production environment
export KGAS_ENV=production
export NEO4J_URL=bolt://prod-neo4j:7687
export LLM_PROVIDER=azure
python main.py
```

## Docker Compose Files

### Development (`environments/docker-compose.yml`)
- Neo4j database
- Basic monitoring
- Development-friendly settings

### Production (`environments/docker-compose.prod.yml`)
- Production-optimized Neo4j
- Enhanced security
- Performance tuning
- Load balancing ready

### Monitoring (`monitoring/docker-compose.monitoring.yml`)
- Prometheus for metrics collection
- Grafana for visualization
- Alert manager for notifications

## Schema Files

### Tool Contract Schema (`schemas/tool_contract_schema.yaml`)
Defines the structure and validation rules for tool contracts in the KGAS system.

### Phase1ToPhase2Adapter (`contracts/Phase1ToPhase2Adapter.yaml`)
Contract definition for the adapter between Phase 1 and Phase 2 processing.

## Example Configurations

The `examples/` directory contains sample configurations for:
- Gemini review setup
- Documentation review
- Verification and validation

## Configuration Best Practices

1. **Environment Isolation**: Use different configuration files for different environments
2. **Security**: Store sensitive values in environment variables, not in config files
3. **Validation**: Use the configuration loader to ensure type safety
4. **Documentation**: Keep this README updated when adding new configuration options
5. **Version Control**: Never commit sensitive configuration values to version control

## Adding New Configuration Options

1. Add the option to the appropriate section in `config.yaml`
2. Update the `ConfigurationSettings` dataclass in `config_loader.py`
3. Update the `_build_settings` method to handle the new option
4. Update this README with documentation for the new option