# KGAS Configuration Guide

Easy configuration setup for KGAS system with secure defaults and simple management.

## Quick Start (30 seconds)

```bash
# 1. Run quick setup
python setup_kgas.py

# 2. Verify configuration
python scripts/verify_config.py

# 3. Start using KGAS
python src/mcp_server.py
```

## Configuration Files

### `.env` - Environment Variables (Required)
Contains sensitive configuration like passwords and API keys.
**Never commit this file to version control.**

```bash
# Example .env file
KGAS_ENV=development
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-secure-password

# Optional LLM API keys
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
```

### `config/default.yaml` - Main Configuration
Contains structured configuration that references environment variables.

```yaml
database:
  password: '${NEO4J_PASSWORD}'    # References .env variable
  username: '${NEO4J_USER:-neo4j}' # With default fallback

system:
  log_level: '${KGAS_LOG_LEVEL:-INFO}'
  max_workers: 4
```

## Setup Options

### Option 1: Quick Setup (Recommended)
```bash
python setup_kgas.py
```
- Interactive setup with secure password generation
- Creates all required files
- Tests configuration

### Option 2: Advanced Setup
```bash
python scripts/setup_config.py
```
- Full wizard with environment selection
- Advanced security options
- Production deployment support

### Option 3: Manual Setup
1. Copy `.env.template` to `.env`
2. Edit `.env` with your settings
3. Run `python scripts/verify_config.py`

## Required Configuration

### Minimum Required Settings
```bash
# .env file
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password
```

### Neo4j Database Setup
```bash
# Using Docker (recommended)
docker run -d \
  --name neo4j-kgas \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/your-password \
  neo4j:latest
```

## Optional Configuration

### LLM API Keys (for AI features)
```bash
# Add to .env file
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
```

### System Settings
```bash
# Add to .env file
KGAS_LOG_LEVEL=DEBUG          # DEBUG, INFO, WARNING, ERROR
KGAS_MAX_WORKERS=8            # Number of worker threads
KGAS_DEBUG=true               # Enable debug mode
KGAS_METRICS_ENABLED=true     # Enable metrics collection
```

### Custom Paths
```bash
# Add to .env file
KGAS_DATA_DIR=./data          # Data storage directory
KGAS_LOGS_DIR=./logs          # Log files directory
KGAS_CONFIG_DIR=./config      # Configuration directory
```

## Environment Types

### Development (default)
- Debug mode enabled
- Detailed logging
- Metrics collection
- No encryption required

### Testing
- Minimal logging
- Fast execution
- Temporary data
- No external APIs required

### Production
- Security features enabled
- Backup system active
- Encrypted storage
- Performance optimized

## Configuration Validation

### Check Configuration
```bash
# Verify all settings
python scripts/verify_config.py

# Test specific components
python -c "from src.core.enhanced_config_manager import get_config; print(get_config())"
```

### Common Issues & Fixes

#### "NEO4J_PASSWORD not set"
```bash
# Check .env file exists and has password
cat .env | grep NEO4J_PASSWORD

# Re-run setup if missing
python setup_kgas.py
```

#### "Neo4j connection failed"
```bash
# Check Neo4j is running
docker ps | grep neo4j

# Test connection manually
python scripts/test_neo4j_connection.py
```

#### "Configuration file not found"
```bash
# Create default configuration
python setup_kgas.py

# Or copy from template
cp config/default.yaml.template config/default.yaml
```

## Security Best Practices

### File Permissions
```bash
# Secure .env file
chmod 600 .env

# Verify permissions
ls -la .env
```

### Password Security
- Use generated passwords (16+ characters)
- Include special characters
- Don't reuse passwords
- Rotate regularly in production

### Version Control
```bash
# Ensure .env is ignored
echo ".env" >> .gitignore
echo ".env.*" >> .gitignore

# Check what's tracked
git status --ignored
```

## Updating Configuration

### Change Database Password
1. Update `.env` file with new password
2. Update Neo4j database with new password
3. Restart KGAS services
4. Verify: `python scripts/verify_config.py`

### Add API Keys
1. Add key to `.env` file: `OPENAI_API_KEY=sk-...`
2. Restart KGAS services
3. Verify: `python scripts/verify_config.py`

### Switch Environments
```bash
# Change environment in .env
KGAS_ENV=production

# Or set temporarily
KGAS_ENV=testing python src/mcp_server.py
```

## Migration Between Environments

### Development → Production
1. Run production setup: `python scripts/setup_config.py`
2. Enable security features in `.env`
3. Update deployment configuration
4. Test thoroughly before deployment

### Backup Configuration
```bash
# Backup current configuration
cp .env .env.backup.$(date +%Y%m%d)
cp config/default.yaml config/default.yaml.backup.$(date +%Y%m%d)
```

## Getting Help

### Diagnostic Tools
```bash
# Full system check
python scripts/verify_config.py

# Configuration debugging
python scripts/diagnose_config.py

# Connection testing
python scripts/test_connections.py
```

### Common Commands
```bash
# Reset configuration
rm .env && python setup_kgas.py

# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('config/default.yaml'))"

# Check environment variables
env | grep KGAS
env | grep NEO4J
```

### Log Files
- Application logs: `logs/kgas.log`
- Configuration logs: `logs/config.log`
- Error logs: `logs/error.log`

## Configuration Templates

### Development Template
```bash
KGAS_ENV=development
KGAS_LOG_LEVEL=DEBUG
KGAS_DEBUG=true
KGAS_METRICS_ENABLED=true
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=dev-password-123
```

### Production Template
```bash
KGAS_ENV=production
KGAS_LOG_LEVEL=INFO
KGAS_BACKUP_ENABLED=true
KGAS_ENCRYPTION_ENABLED=true
NEO4J_URI=${NEO4J_PRODUCTION_URL}
NEO4J_USER=${NEO4J_PRODUCTION_USER}
NEO4J_PASSWORD=${NEO4J_PRODUCTION_PASSWORD}
```

---

**Need help?** Run `python setup_kgas.py` or check the full documentation in `docs/`.