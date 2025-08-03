# Configuration Management Guide

**Status**: Production-Ready  
**Version**: 1.0  
**Last Updated**: 2025-07-26  

This guide covers the comprehensive configuration management system for KGAS, including environment-based configuration, secure credential management, and production deployment.

## Overview

The KGAS configuration management system provides:

- **Environment-based configuration** (development, testing, production)
- **Secure credential management** with AES-GCM encryption
- **Configuration validation** and health monitoring
- **Runtime configuration updates** without restarts
- **Production-ready deployment** scenarios

## Quick Start

### 1. Basic Setup

```python
from src.core.configuration_service import ConfigurationService

# Initialize configuration service
config_service = ConfigurationService()

# Get database configuration
neo4j_config = config_service.get_database_config('neo4j')

# Get API key (automatically decrypted)
openai_key = config_service.get_api_key('openai')
```

### 2. Environment Variables

Copy `.env.template` to `.env` and configure:

```bash
# Copy template
cp .env.template .env

# Edit with your values
KGAS_ENV=development
KGAS_NEO4J_PASSWORD=your_password
KGAS_OPENAI_API_KEY=sk-your-api-key
```

## Configuration Architecture

### Core Components

```
┌─────────────────────────────────────────┐
│        Configuration Service            │
├─────────────────────────────────────────┤
│  ┌─────────────────┐ ┌─────────────────┐ │
│  │ Production      │ │ Secure          │ │
│  │ Config Manager  │ │ Credential Mgr  │ │
│  └─────────────────┘ └─────────────────┘ │
├─────────────────────────────────────────┤
│  ┌─────────────────────────────────────┐ │
│  │     Configuration Files             │ │
│  │  base.yaml + {env}.yaml + .env      │ │
│  └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

### Configuration Layers

1. **Base Configuration** (`config/base.yaml`)
   - Default settings for all environments
   - Common database and service configurations

2. **Environment-Specific** (`config/{environment}.yaml`)
   - Overrides for development, testing, production
   - Environment-specific security and performance settings

3. **Environment Variables** (`.env` or system environment)
   - Sensitive data like API keys and passwords
   - Runtime configuration overrides

## Environment Configuration

### Development Environment

```yaml
# config/development.yaml
database:
  neo4j:
    password: "development"
    max_connections: 10

security:
  encrypt_credentials: false
  audit_logging: false

logging:
  level: "DEBUG"
  debug: true

error_handling:
  circuit_breaker_enabled: false
  max_retries: 1
```

### Production Environment

```yaml
# config/production.yaml
database:
  neo4j:
    password: "${NEO4J_PASSWORD}"
    max_connections: 100
    connection_timeout: 60

security:
  encrypt_credentials: true
  audit_logging: true

logging:
  level: "INFO"
  debug: false

error_handling:
  circuit_breaker_enabled: true
  circuit_breaker_threshold: 10
  max_retries: 5
```

## Secure Credential Management

### Storing Credentials

```python
from src.core.configuration_service import ConfigurationService

config_service = ConfigurationService()

# Store encrypted API key
config_service.set_api_key(
    provider='openai',
    api_key='sk-your-api-key',
    expires_days=90
)
```

### Retrieving Credentials

```python
# Get API key (automatically decrypted)
api_key = config_service.get_api_key('openai')

# Get full LLM configuration
llm_config = config_service.get_llm_config('openai')
```

### Credential Rotation

```python
# Rotate credential
config_service.rotate_credential(
    provider='openai',
    new_credential='sk-new-api-key',
    expires_days=90
)
```

### Credential Status

```python
# Check credential status
status = config_service.credential_manager.get_credential_status('openai')
print(f"Expires in {status['days_until_expiry']} days")

# List all credentials
credentials = config_service.credential_manager.list_credentials()
for cred in credentials:
    print(f"{cred['provider']}: expires {cred['expires_at']}")
```

## Configuration Validation

### Health Checking

```python
# Check configuration health
health = config_service.check_health()

print(f"Status: {health.overall_status}")
if health.issues:
    for issue in health.issues:
        print(f"Issue: {issue}")
```

### Validation Results

The system validates:
- ✅ Database connectivity settings
- ✅ API key availability and format
- ✅ Schema framework configuration
- ✅ Error handling parameters
- ✅ Security settings consistency

## Schema Framework Configuration

### Schema Settings

```python
# Get schema configuration
schema_config = config_service.get_schema_config()

print(f"Enabled paradigms: {schema_config.enabled_paradigms}")
print(f"Default paradigm: {schema_config.default_paradigm}")
print(f"Cross-paradigm validation: {schema_config.cross_paradigm_validation}")
```

### Available Schema Paradigms

- **UML**: Object-oriented class diagrams
- **RDF/OWL**: Semantic web ontologies
- **ORM**: Fact-based relationship modeling
- **TypeDB**: Enhanced entity-relationship
- **N-ary**: Complex multi-party relationships

## Error Handling Configuration

### Error Handling Settings

```python
# Get error handling configuration
error_config = config_service.get_error_config()

print(f"Circuit breaker enabled: {error_config.circuit_breaker_enabled}")
print(f"Max retries: {error_config.max_retries}")
print(f"Health check interval: {error_config.health_check_interval}")
```

### Circuit Breaker Configuration

- **Threshold**: Number of failures before opening circuit
- **Timeout**: Time before attempting reset
- **Health Monitoring**: Regular status checks

## Runtime Configuration Updates

### Hot Reloading

```python
# Reload configuration without restart
config_service.reload_configuration()

# Update credential at runtime
config_service.set_api_key('new_provider', 'api-key')

# Check updated status
summary = config_service.get_configuration_summary()
```

## Production Deployment

### Deployment Checklist

1. **Environment Setup**
   ```bash
   export KGAS_ENV=production
   export KGAS_NEO4J_PASSWORD=secure_password
   export KGAS_OPENAI_API_KEY=sk-production-key
   ```

2. **Configuration Validation**
   ```python
   config_service = ConfigurationService(environment='production')
   health = config_service.check_health()
   assert health.is_healthy(), f"Configuration issues: {health.issues}"
   ```

3. **Security Verification**
   ```python
   security_config = config_service.get_security_config()
   assert security_config.encrypt_credentials, "Credentials must be encrypted in production"
   assert security_config.audit_logging, "Audit logging must be enabled"
   ```

### Production Security

- ✅ **Encrypted credentials** with AES-GCM
- ✅ **Secure file permissions** (600 for credential files)
- ✅ **Audit logging** for all credential access
- ✅ **Environment variable** fallbacks
- ✅ **Configuration validation** on startup

## Configuration Files Reference

### Directory Structure

```
config/
├── base.yaml           # Base configuration
├── development.yaml    # Development overrides
├── testing.yaml        # Testing environment
├── production.yaml     # Production settings
└── credentials/        # Encrypted credential storage
    ├── credentials.json
    ├── metadata.json
    └── encryption.key
```

### Base Configuration Schema

```yaml
database:
  neo4j:
    host: string
    port: integer
    username: string
    password: string
    database: string
    max_connections: integer
    connection_timeout: integer
    read_timeout: integer

llm:
  {provider}:
    provider: string
    model: string
    max_tokens: integer
    temperature: float
    timeout: integer
    max_retries: integer
    rate_limit_per_minute: integer

schema:
  enabled_paradigms: [string]
  default_paradigm: string
  cross_paradigm_validation: boolean
  auto_transform: boolean
  validation_timeout: integer

error_handling:
  circuit_breaker_enabled: boolean
  circuit_breaker_threshold: integer
  circuit_breaker_timeout: integer
  max_retries: integer
  retry_delay: float
  exponential_backoff: boolean
  health_check_interval: integer
  metrics_enabled: boolean

security:
  encrypt_credentials: boolean
  pii_encryption: boolean
  api_key_rotation_days: integer
  audit_logging: boolean
```

## API Reference

### ConfigurationService

```python
class ConfigurationService:
    def __init__(self, config_dir: Optional[str] = None, environment: Optional[str] = None)
    
    # Database configuration
    def get_database_config(self, database: str = "neo4j") -> DatabaseConfig
    
    # LLM configuration
    def get_llm_config(self, provider: str) -> LLMConfig
    def get_api_key(self, provider: str) -> str
    def set_api_key(self, provider: str, api_key: str, expires_days: int = 90) -> None
    
    # Framework configuration
    def get_schema_config(self) -> SchemaConfig
    def get_error_config(self) -> ErrorHandlingConfig
    def get_security_config(self) -> SecurityConfig
    
    # Environment information
    def is_development(self) -> bool
    def is_production(self) -> bool
    def get_environment(self) -> str
    
    # Health and validation
    def check_health(self, force_check: bool = False) -> ConfigurationHealth
    def validate_api_key(self, provider: str) -> bool
    def get_active_llm_providers(self) -> List[str]
    
    # Runtime updates
    def reload_configuration(self) -> None
    def rotate_credential(self, provider: str, new_credential: str, expires_days: int = 90) -> None
    
    # Information and export
    def get_configuration_summary(self) -> Dict[str, Any]
    def export_configuration(self, include_credentials: bool = False) -> Dict[str, Any]
```

## Troubleshooting

### Common Issues

1. **Credential Not Found**
   ```
   ValueError: No credential found for openai
   ```
   **Solution**: Set API key or check environment variables
   ```python
   config_service.set_api_key('openai', 'sk-your-key')
   ```

2. **Configuration Validation Failed**
   ```
   Configuration validation found 3 issues
   ```
   **Solution**: Check health and fix reported issues
   ```python
   health = config_service.check_health()
   for issue in health.issues:
       print(f"Fix: {issue}")
   ```

3. **Environment Variable Not Loaded**
   ```
   Database configuration error: Missing host
   ```
   **Solution**: Check environment variable names
   ```bash
   export KGAS_NEO4J_HOST=localhost
   ```

### Debugging

1. **Enable Debug Logging**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **Check Configuration Summary**
   ```python
   summary = config_service.get_configuration_summary()
   print(json.dumps(summary, indent=2, default=str))
   ```

3. **Validate All Settings**
   ```python
   issues = config_service.config_manager.validate_configuration()
   for issue in issues:
       print(f"Issue: {issue}")
   ```

## Performance

### Benchmark Results

- **Credential retrieval**: 0.27ms average
- **Health check**: 0.02ms
- **Configuration summary**: 0.03ms
- **Configuration reload**: ~5ms

### Optimization Tips

1. **Use configuration caching** (enabled by default)
2. **Minimize health check frequency** in production
3. **Batch credential operations** when possible
4. **Use environment variables** for frequently accessed values

## Migration Guide

### From Legacy Configuration

1. **Backup existing configuration**
2. **Create new configuration structure**
3. **Migrate credentials to encrypted storage**
4. **Update application code to use ConfigurationService**
5. **Test configuration validation**
6. **Deploy with health monitoring**

### Version Compatibility

- **v1.0**: Initial production-ready release
- **Backward compatibility**: Environment variables still supported
- **Migration path**: Automatic credential import from environment

---

## Summary

The KGAS configuration management system provides a production-ready foundation for:

✅ **Environment-based configuration** with validation  
✅ **Secure credential management** with encryption  
✅ **Runtime configuration updates** without restarts  
✅ **Comprehensive health monitoring** and validation  
✅ **Production deployment** scenarios  

The system is **fully validated** and ready for production use.