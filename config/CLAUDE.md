# Configuration Module - CLAUDE.md

## Overview
The `config/` directory houses **all configuration files** for the GraphRAG system. It supports multi-environment setups (development, production, CI) and centralizes schema definitions, contracts, monitoring configs, and environment-specific Docker Compose files.

## Directory Structure
```
config/
├── config.yaml                # Main YAML configuration (multi-env)
├── config_loader.py           # Centralized configuration loader utility
├── README.md                  # Human-oriented docs (quick reference)
├── environments/              # Env-specific Docker Compose files
│   ├── docker-compose.yml
│   └── docker-compose.prod.yml
├── monitoring/                # Monitoring stack configs (Prometheus, Grafana)
│   ├── docker-compose.monitoring.yml
│   ├── prometheus.yml
│   └── grafana-datasources.yml
├── schemas/                   # JSON/YAML schema definitions
│   └── tool_contract_schema.yaml
├── contracts/                 # Contract definitions
│   └── Phase1ToPhase2Adapter.yaml
└── examples/                  # Example configs for reviews and validation
```

## Configuration Loader (`config_loader.py`)
### Key Features
- **Environment-Aware**: Reads `KGAS_ENV` (defaults to `development`).
- **Dataclass Settings**: `ConfigurationSettings` provides IDE type-safety.
- **Env-Var Resolution**: Supports `${VAR_NAME}` placeholders in YAML.
- **Path Resolution**: Resolves `./relative/path` to absolute paths inside `config/`.
- **Lazy Singleton**: `get_config_loader()` returns a global singleton.

### Usage
```python
from config.config_loader import get_settings

# Current env (KGAS_ENV or 'development')
settings = get_settings()
print(settings.database_url)

# Explicit env
prod = get_settings('production')
print(prod.llm_provider)
```

### Extending Settings
1. Add new field to `ConfigurationSettings` dataclass.
2. Update `_build_settings` to populate the field.
3. Document the option in `config/README.md`.
4. Update sample values in `config.yaml`.

## Main Configuration File (`config.yaml`)
Sections:
- `environments` – dev/prod URLs, Docker Compose overrides
- `monitoring` – Prometheus/Grafana paths
- `contracts` – Contract schema locations
- `core` – System-wide concurrency, backup, metrics
- `security` – Encryption, API rate limits
- `performance` – Memory/time limits, parallel-processing flag

### Environment Example
```yaml
environments:
  development:
    docker_compose: ./environments/docker-compose.yml
    database_url: bolt://localhost:7687
    llm_provider: openai
    log_level: DEBUG
  production:
    docker_compose: ./environments/docker-compose.prod.yml
    database_url: ${NEO4J_URL}
    llm_provider: ${LLM_PROVIDER}
    log_level: INFO
```

## Monitoring Stack Configs
- **`monitoring/docker-compose.monitoring.yml`** – Spins up Prometheus & Grafana.
- **`prometheus.yml`** – Scrape configs & alert rules.
- **`grafana-datasources.yml`** – Data source provisioning for Grafana.

## Schemas & Contracts
- **`schemas/tool_contract_schema.yaml`** – Validates tool contract YAMLs.
- **`contracts/Phase1ToPhase2Adapter.yaml`** – Defines adapter contract between phases.

## Best Practices
1. **Keep Secrets Out of Git** – Use env vars for DB URLs, API keys.
2. **Validate Configs** – Run `python -m config.config_loader` to validate YAML.
3. **Document Changes** – Update both `CLAUDE.md` and `README.md` when adding options.
4. **Use Examples** – Add example configs under `examples/` for reviewers.
5. **Schema-First** – Add JSON/YAML schemas for new contract types.

## Common Commands
```bash
# Validate YAML and print resolved settings
python - << 'PY'
from config.config_loader import get_settings
print(get_settings())
PY

# List available environments in config.yaml
python - << 'PY'
import yaml, pathlib, pprint
cfg = yaml.safe_load(open('config/config.yaml'))
print(cfg['environments'].keys())
PY
```

## Troubleshooting
| Symptom | Resolution |
|---------|------------|
| `FileNotFoundError` on config | Verify `config.yaml` exists & path correct |
| `${VAR}` not resolved | Export env var (`export VAR=value`) before running |
| Wrong environment settings | `export KGAS_ENV=development` (or prod) |
| Grafana dashboards not loading | Check `monitoring/docker-compose.monitoring.yml` running |

## Adding New Environment
1. Add new env block under `environments` in `config.yaml`.
2. Add corresponding Docker Compose file under `environments/`.
3. Export `KGAS_ENV=<new_env>` to activate.

## CI/CD Integration
- CI sets `KGAS_ENV=ci` and uses minimal services.
- Deployment pipeline overrides production secrets via GitHub Actions secrets. 