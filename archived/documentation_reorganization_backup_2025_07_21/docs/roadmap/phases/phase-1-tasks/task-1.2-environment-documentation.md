# Task 1.2: Environment Documentation

**Duration**: Day 3 (Week 2)  
**Owner**: DevOps Lead  
**Priority**: HIGH - Critical for developer onboarding

## Objective

Create comprehensive documentation for all environment variables used in KGAS, including a complete `.env.example` file, validation scripts, and setup guides to reduce developer onboarding time to under 30 minutes.

## Current State Analysis

### Environment Variable Audit

```bash
# Script to find all environment variables
#!/bin/bash

echo "=== KGAS Environment Variable Audit ==="
echo "Searching for environment variable usage..."

# Find all os.environ and os.getenv usage
echo -e "\n1. Direct environment access (os.environ):"
grep -r "os\.environ\[" src/ --include="*.py" | grep -v "__pycache__" | cut -d: -f1 | sort | uniq -c

echo -e "\n2. Safe environment access (os.getenv):"
grep -r "os\.getenv(" src/ --include="*.py" | grep -v "__pycache__" | cut -d: -f1 | sort | uniq -c

echo -e "\n3. All unique environment variable names:"
grep -r -E "(os\.environ\[|os\.getenv\()" src/ --include="*.py" | \
    grep -v "__pycache__" | \
    grep -oE "(os\.environ\[['\"]\w+['\"]|os\.getenv\(['\"]\w+['\"])" | \
    grep -oE "['\"][A-Z_]+['\"]" | \
    tr -d "'" | tr -d '"' | sort | uniq

echo -e "\n4. Config file references:"
find . -name "*.env*" -o -name "*config*.yaml" -o -name "*config*.json" | grep -v "__pycache__" | sort
```

### Expected Environment Variables (47+)

Based on codebase analysis, these categories of variables exist:

1. **Database Configuration** (8 variables)
   - Neo4j connection settings
   - Qdrant vector store settings
   - Redis cache settings

2. **API Keys** (12 variables)
   - OpenAI, Anthropic, Google
   - Service authentication tokens

3. **Application Settings** (15 variables)
   - File paths, limits, timeouts
   - Feature flags, debug settings

4. **Infrastructure** (8 variables)
   - Monitoring, logging, metrics
   - Health check configurations

5. **Security** (4+ variables)
   - Encryption keys, salts
   - Authentication settings

## Implementation Plan

### Step 1: Create Comprehensive .env.example

```bash
# File: /home/brian/Digimons/.env.example

# ============================================================================
# KGAS Environment Configuration
# ============================================================================
# This file contains all environment variables used by KGAS.
# Copy this file to .env and fill in your values.
# Required variables are marked with [REQUIRED]
# ============================================================================

# ----------------------------------------------------------------------------
# Database Configuration
# ----------------------------------------------------------------------------

# Neo4j Graph Database [REQUIRED]
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password_here  # [REQUIRED]
NEO4J_DATABASE=neo4j  # Optional, defaults to 'neo4j'
NEO4J_MAX_RETRY=3  # Optional, max connection retries
NEO4J_TIMEOUT=30  # Optional, connection timeout in seconds
NEO4J_MAX_CONNECTION_POOL_SIZE=50  # Optional, connection pool size
NEO4J_CONNECTION_ACQUISITION_TIMEOUT=60  # Optional, timeout for acquiring connection

# Qdrant Vector Database
QDRANT_HOST=localhost  # Optional, defaults to 'localhost'
QDRANT_PORT=6333  # Optional, defaults to 6333
QDRANT_API_KEY=  # Optional, only needed for cloud deployment
QDRANT_COLLECTION=kgas_vectors  # Optional, collection name
QDRANT_TIMEOUT=30  # Optional, request timeout
QDRANT_GRPC_PORT=6334  # Optional, gRPC port

# Redis Cache (Optional)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=  # Optional
REDIS_DB=0
REDIS_MAX_CONNECTIONS=10

# ----------------------------------------------------------------------------
# API Keys and External Services
# ----------------------------------------------------------------------------

# OpenAI API [REQUIRED for LLM features]
OPENAI_API_KEY=sk-...  # [REQUIRED for LLM extraction]
OPENAI_ORGANIZATION=  # Optional, OpenAI organization ID
OPENAI_API_BASE=  # Optional, custom API endpoint
OPENAI_MODEL=gpt-4  # Optional, defaults to 'gpt-4'
OPENAI_EMBEDDING_MODEL=text-embedding-3-small  # Optional
OPENAI_MAX_TOKENS=2000  # Optional, max tokens per request
OPENAI_TEMPERATURE=0.7  # Optional, 0.0-1.0
OPENAI_REQUEST_TIMEOUT=60  # Optional, request timeout

# Anthropic API (Optional)
ANTHROPIC_API_KEY=  # Optional, for Claude integration
ANTHROPIC_MODEL=claude-3-opus-20240229  # Optional
ANTHROPIC_MAX_TOKENS=4000  # Optional

# Google AI (Optional)
GOOGLE_API_KEY=  # Optional, for Gemini integration
GOOGLE_PROJECT_ID=  # Optional, GCP project ID
GEMINI_MODEL=gemini-pro  # Optional

# ----------------------------------------------------------------------------
# Application Settings
# ----------------------------------------------------------------------------

# General Configuration
KGAS_ENV=development  # Options: development, staging, production
KGAS_DEBUG=false  # Enable debug mode
KGAS_LOG_LEVEL=INFO  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
KGAS_CONFIG_FILE=  # Optional, path to YAML/JSON config file

# File and Data Management
KGAS_DATA_DIR=/home/brian/Digimons/data  # [REQUIRED] Data storage directory
KGAS_CACHE_DIR=/home/brian/Digimons/.cache  # Optional, cache directory
KGAS_TEMP_DIR=/tmp/kgas  # Optional, temporary files
KGAS_MAX_FILE_SIZE=104857600  # Optional, max file size in bytes (100MB)
KGAS_ALLOWED_EXTENSIONS=.pdf,.txt,.md,.docx  # Optional, allowed file types

# Processing Configuration
KGAS_BATCH_SIZE=32  # Optional, batch processing size
KGAS_CHUNK_SIZE=512  # Optional, text chunk size
KGAS_CHUNK_OVERLAP=50  # Optional, chunk overlap size
KGAS_MAX_WORKERS=4  # Optional, parallel processing workers

# ----------------------------------------------------------------------------
# Feature Flags
# ----------------------------------------------------------------------------

ENABLE_CACHING=true  # Enable Redis caching
ENABLE_MONITORING=true  # Enable Prometheus metrics
ENABLE_ASYNC=true  # Enable async processing
ENABLE_PROVENANCE=true  # Enable provenance tracking
ENABLE_SECURITY_SCANNING=true  # Enable security checks
ENABLE_AUTO_BACKUP=false  # Enable automatic backups

# ----------------------------------------------------------------------------
# Infrastructure and Monitoring
# ----------------------------------------------------------------------------

# Logging Configuration
LOG_FILE_PATH=/home/brian/Digimons/logs/kgas.log  # Optional
LOG_MAX_SIZE=10485760  # Optional, max log file size (10MB)
LOG_BACKUP_COUNT=5  # Optional, number of log backups
LOG_FORMAT=json  # Options: json, text

# Metrics and Monitoring
PROMETHEUS_PORT=9090  # Optional, Prometheus metrics port
METRICS_ENABLED=true  # Optional, enable metrics collection
HEALTH_CHECK_INTERVAL=30  # Optional, health check interval in seconds
HEALTH_CHECK_TIMEOUT=5  # Optional, health check timeout

# Distributed Tracing (Optional)
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317  # Optional
OTEL_SERVICE_NAME=kgas  # Optional
OTEL_TRACES_ENABLED=false  # Optional

# ----------------------------------------------------------------------------
# Security Configuration
# ----------------------------------------------------------------------------

# Encryption and Security [REQUIRED for production]
KGAS_SECRET_KEY=  # [REQUIRED for production] Secret key for encryption
KGAS_PII_PASSWORD=  # Optional, for PII encryption
KGAS_PII_SALT=  # Optional, for PII hashing
JWT_SECRET_KEY=  # Optional, for JWT tokens
SESSION_SECRET_KEY=  # Optional, for session management

# API Security
API_RATE_LIMIT=100  # Optional, requests per minute
API_KEY_HEADER=X-API-Key  # Optional, API key header name
CORS_ORIGINS=http://localhost:3000,http://localhost:8501  # Optional

# ----------------------------------------------------------------------------
# MCP Server Configuration
# ----------------------------------------------------------------------------

MCP_SERVER_HOST=0.0.0.0  # Optional, MCP server host
MCP_SERVER_PORT=3000  # Optional, MCP server port
MCP_ENABLE_AUTH=false  # Optional, enable MCP authentication

# ----------------------------------------------------------------------------
# UI Configuration (Streamlit)
# ----------------------------------------------------------------------------

STREAMLIT_SERVER_PORT=8501  # Optional, Streamlit port
STREAMLIT_SERVER_ADDRESS=localhost  # Optional
STREAMLIT_THEME=light  # Options: light, dark
STREAMLIT_ENABLE_CORS=false  # Optional

# ============================================================================
# Quick Start Instructions:
# 1. Copy this file: cp .env.example .env
# 2. Edit .env and fill in required values (marked with [REQUIRED])
# 3. Validate configuration: python scripts/validate_env.py
# 4. Start services: docker-compose up -d
# ============================================================================
```

### Step 2: Create Environment Validation Script

```python
# File: scripts/validate_env.py

#!/usr/bin/env python3
"""
Validate environment configuration for KGAS.
Ensures all required variables are set and validates their values.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import re
from urllib.parse import urlparse

class EnvValidator:
    """Validate KGAS environment configuration"""
    
    REQUIRED_VARS = [
        'NEO4J_PASSWORD',
        'OPENAI_API_KEY',  # Required for LLM features
        'KGAS_DATA_DIR',
    ]
    
    REQUIRED_FOR_PRODUCTION = [
        'KGAS_SECRET_KEY',
        'KGAS_PII_PASSWORD',
        'KGAS_PII_SALT',
    ]
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: List[str] = []
        
    def validate(self) -> bool:
        """Run all validation checks"""
        print("🔍 Validating KGAS Environment Configuration...")
        print("=" * 60)
        
        # Check .env file exists
        if not Path('.env').exists():
            self.errors.append(".env file not found. Copy .env.example to .env")
            self._print_results()
            return False
        
        # Load environment
        self._load_dotenv()
        
        # Run validation checks
        self._check_required_variables()
        self._validate_database_config()
        self._validate_api_keys()
        self._validate_paths()
        self._validate_numeric_values()
        self._check_production_requirements()
        self._check_feature_consistency()
        
        # Print results
        self._print_results()
        
        return len(self.errors) == 0
    
    def _load_dotenv(self):
        """Load .env file if it exists"""
        try:
            from dotenv import load_dotenv
            load_dotenv()
            self.info.append("✓ Loaded .env file successfully")
        except ImportError:
            self.warnings.append("python-dotenv not installed. Using system environment only.")
    
    def _check_required_variables(self):
        """Check all required variables are set"""
        for var in self.REQUIRED_VARS:
            value = os.getenv(var)
            if not value:
                self.errors.append(f"❌ Required variable {var} is not set")
            else:
                self.info.append(f"✓ {var} is set")
    
    def _validate_database_config(self):
        """Validate database configuration"""
        # Neo4j validation
        neo4j_uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
        try:
            parsed = urlparse(neo4j_uri)
            if parsed.scheme not in ['bolt', 'neo4j']:
                self.errors.append(f"Invalid Neo4j URI scheme: {parsed.scheme}")
            else:
                self.info.append(f"✓ Neo4j URI valid: {neo4j_uri}")
        except Exception as e:
            self.errors.append(f"Invalid Neo4j URI: {e}")
        
        # Qdrant validation
        qdrant_port = os.getenv('QDRANT_PORT', '6333')
        try:
            port = int(qdrant_port)
            if not 1 <= port <= 65535:
                self.errors.append(f"Invalid Qdrant port: {port}")
            else:
                self.info.append(f"✓ Qdrant port valid: {port}")
        except ValueError:
            self.errors.append(f"Qdrant port must be numeric: {qdrant_port}")
    
    def _validate_api_keys(self):
        """Validate API key formats"""
        # OpenAI key validation
        openai_key = os.getenv('OPENAI_API_KEY', '')
        if openai_key and not openai_key.startswith('sk-'):
            self.warnings.append("OpenAI API key should start with 'sk-'")
        
        # Check if at least one LLM API is configured
        has_llm = any([
            os.getenv('OPENAI_API_KEY'),
            os.getenv('ANTHROPIC_API_KEY'),
            os.getenv('GOOGLE_API_KEY')
        ])
        
        if not has_llm:
            self.warnings.append("No LLM API keys configured. LLM features will be disabled.")
    
    def _validate_paths(self):
        """Validate file paths exist and are writable"""
        paths_to_check = [
            ('KGAS_DATA_DIR', True),  # Must exist
            ('KGAS_CACHE_DIR', False),  # Will be created
            ('LOG_FILE_PATH', False),  # Parent dir must exist
        ]
        
        for env_var, must_exist in paths_to_check:
            path_str = os.getenv(env_var)
            if not path_str:
                continue
                
            path = Path(path_str)
            
            if must_exist and not path.exists():
                self.errors.append(f"Path does not exist: {env_var}={path_str}")
            elif path.exists() and not os.access(path, os.W_OK):
                self.errors.append(f"Path is not writable: {env_var}={path_str}")
            else:
                self.info.append(f"✓ Path valid: {env_var}={path_str}")
    
    def _validate_numeric_values(self):
        """Validate numeric environment variables"""
        numeric_vars = [
            ('KGAS_MAX_FILE_SIZE', 1, 1e9),  # 1 byte to 1GB
            ('KGAS_BATCH_SIZE', 1, 1000),
            ('NEO4J_TIMEOUT', 1, 300),
            ('API_RATE_LIMIT', 1, 10000),
        ]
        
        for var, min_val, max_val in numeric_vars:
            value_str = os.getenv(var)
            if not value_str:
                continue
                
            try:
                value = int(value_str)
                if not min_val <= value <= max_val:
                    self.warnings.append(
                        f"{var}={value} outside recommended range [{min_val}, {max_val}]"
                    )
            except ValueError:
                self.errors.append(f"{var} must be numeric: {value_str}")
    
    def _check_production_requirements(self):
        """Check production-specific requirements"""
        if os.getenv('KGAS_ENV') == 'production':
            for var in self.REQUIRED_FOR_PRODUCTION:
                if not os.getenv(var):
                    self.errors.append(
                        f"❌ {var} is required for production environment"
                    )
            
            # Check debug is disabled
            if os.getenv('KGAS_DEBUG', 'false').lower() == 'true':
                self.warnings.append("Debug mode should be disabled in production")
    
    def _check_feature_consistency(self):
        """Check feature flags are consistent"""
        # If caching is enabled, Redis should be configured
        if os.getenv('ENABLE_CACHING', 'true').lower() == 'true':
            if not os.getenv('REDIS_HOST'):
                self.warnings.append(
                    "Caching enabled but Redis not configured. Using in-memory cache."
                )
        
        # If monitoring is enabled, check Prometheus port
        if os.getenv('ENABLE_MONITORING', 'true').lower() == 'true':
            if not os.getenv('PROMETHEUS_PORT'):
                self.info.append("Monitoring enabled, using default Prometheus port 9090")
    
    def _print_results(self):
        """Print validation results"""
        print("\n📋 Validation Results:")
        print("-" * 60)
        
        # Errors
        if self.errors:
            print(f"\n❌ Errors ({len(self.errors)}):")
            for error in self.errors:
                print(f"   {error}")
        
        # Warnings
        if self.warnings:
            print(f"\n⚠️  Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   {warning}")
        
        # Info
        if self.info:
            print(f"\n✅ Valid ({len(self.info)}):")
            for info in self.info[:5]:  # Show first 5
                print(f"   {info}")
            if len(self.info) > 5:
                print(f"   ... and {len(self.info) - 5} more")
        
        # Summary
        print("\n" + "=" * 60)
        if self.errors:
            print("❌ VALIDATION FAILED - Fix errors before proceeding")
        elif self.warnings:
            print("⚠️  VALIDATION PASSED WITH WARNINGS")
        else:
            print("✅ VALIDATION PASSED - Environment correctly configured")

def main():
    """Run environment validation"""
    validator = EnvValidator()
    success = validator.validate()
    
    # Generate setup report
    if success:
        print("\n📝 Next Steps:")
        print("1. Start Neo4j: docker-compose up -d neo4j")
        print("2. Start Qdrant: docker-compose up -d qdrant")
        print("3. Run setup: python scripts/setup_databases.py")
        print("4. Start KGAS: python main.py")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
```

### Step 3: Create Quick Setup Guide

```markdown
# File: docs/SETUP.md

# KGAS Quick Setup Guide

Get KGAS running in under 30 minutes with this step-by-step guide.

## Prerequisites

- Python 3.10+
- Docker and Docker Compose
- 8GB RAM minimum
- 10GB free disk space

## Step 1: Clone and Configure (5 minutes)

```bash
# Clone repository
git clone https://github.com/yourusername/kgas.git
cd kgas

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env
```

## Step 2: Configure Required Variables (5 minutes)

Edit `.env` and set these required variables:

```bash
# Minimum required configuration
NEO4J_PASSWORD=your_secure_password_here
OPENAI_API_KEY=sk-your-openai-api-key-here
KGAS_DATA_DIR=/path/to/your/data/directory
```

## Step 3: Validate Configuration (2 minutes)

```bash
# Validate your environment setup
python scripts/validate_env.py

# Expected output:
# ✅ VALIDATION PASSED - Environment correctly configured
```

## Step 4: Start Services (5 minutes)

```bash
# Start all required services
docker-compose up -d

# Verify services are running
docker-compose ps

# Expected output:
# NAME                STATUS
# kgas-neo4j          Up 7687/tcp, 7474/tcp
# kgas-qdrant         Up 6333/tcp, 6334/tcp
# kgas-redis          Up 6379/tcp
```

## Step 5: Initialize Databases (3 minutes)

```bash
# Setup database schemas and indexes
python scripts/setup_databases.py

# Expected output:
# ✅ Neo4j connected and initialized
# ✅ Qdrant collections created
# ✅ Redis cache initialized
```

## Step 6: Run Tests (5 minutes)

```bash
# Run quick validation tests
pytest tests/quick_validation.py -v

# Run full test suite (optional, 10 minutes)
pytest tests/ -v
```

## Step 7: Start KGAS (2 minutes)

```bash
# Start the MCP server
python main.py

# In a new terminal, start the UI
streamlit run streamlit_app.py
```

## Step 8: Verify Installation (3 minutes)

1. Open http://localhost:8501 in your browser
2. Upload the test PDF: `test_data/sample_paper.pdf`
3. Click "Process Document"
4. Verify you see extracted entities and graph

## Troubleshooting

### Common Issues

1. **Neo4j Connection Failed**
   ```bash
   # Check Neo4j logs
   docker-compose logs neo4j
   
   # Ensure password is set correctly
   echo $NEO4J_PASSWORD
   ```

2. **OpenAI API Errors**
   ```bash
   # Test API key
   python -c "import openai; openai.api_key='$OPENAI_API_KEY'; print(openai.Model.list())"
   ```

3. **Port Conflicts**
   ```bash
   # Check for port usage
   lsof -i :7687  # Neo4j
   lsof -i :6333  # Qdrant
   lsof -i :8501  # Streamlit
   ```

### Getting Help

- Check logs: `tail -f logs/kgas.log`
- Run diagnostics: `python scripts/diagnose.py`
- See full documentation: [docs/README.md](README.md)

## Next Steps

- Process your first document: [Tutorial](tutorials/first_document.md)
- Configure advanced features: [Configuration Guide](configuration.md)
- Explore the API: [API Documentation](api/README.md)
```

### Step 4: Create Setup Automation Script

```python
# File: scripts/quick_setup.py

#!/usr/bin/env python3
"""
Quick setup script for KGAS.
Automates the setup process to get running in <30 minutes.
"""

import subprocess
import sys
import os
import time
from pathlib import Path
import shutil

class QuickSetup:
    """Automated setup for KGAS"""
    
    def __init__(self):
        self.errors = []
        self.project_root = Path.cwd()
        
    def run(self):
        """Run complete setup process"""
        print("🚀 KGAS Quick Setup")
        print("=" * 60)
        
        steps = [
            ("Checking prerequisites", self.check_prerequisites),
            ("Setting up environment", self.setup_environment),
            ("Installing dependencies", self.install_dependencies),
            ("Configuring environment", self.configure_environment),
            ("Starting services", self.start_services),
            ("Initializing databases", self.initialize_databases),
            ("Running validation", self.run_validation),
        ]
        
        for step_name, step_func in steps:
            print(f"\n▶️  {step_name}...")
            if not step_func():
                print(f"❌ Failed at: {step_name}")
                print(f"Errors: {self.errors}")
                return False
            print(f"✅ {step_name} complete")
        
        print("\n" + "=" * 60)
        print("✅ KGAS Setup Complete!")
        print("\nStart KGAS with:")
        print("  python main.py")
        print("\nStart UI with:")
        print("  streamlit run streamlit_app.py")
        
        return True
    
    def check_prerequisites(self):
        """Check system prerequisites"""
        # Check Python version
        if sys.version_info < (3, 10):
            self.errors.append(f"Python 3.10+ required (found {sys.version})")
            return False
        
        # Check Docker
        try:
            subprocess.run(["docker", "--version"], check=True, capture_output=True)
        except:
            self.errors.append("Docker not found. Please install Docker.")
            return False
        
        # Check Docker Compose
        try:
            subprocess.run(["docker-compose", "--version"], check=True, capture_output=True)
        except:
            self.errors.append("Docker Compose not found. Please install Docker Compose.")
            return False
        
        return True
    
    def setup_environment(self):
        """Setup Python environment"""
        # Create .env if it doesn't exist
        if not Path('.env').exists():
            if Path('.env.example').exists():
                shutil.copy('.env.example', '.env')
                print("  Created .env from .env.example")
            else:
                self.errors.append(".env.example not found")
                return False
        
        # Create necessary directories
        dirs = ['data', 'logs', '.cache', 'temp']
        for dir_name in dirs:
            Path(dir_name).mkdir(exist_ok=True)
        
        return True
    
    def install_dependencies(self):
        """Install Python dependencies"""
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                check=True
            )
            
            # Install spaCy model
            subprocess.run(
                [sys.executable, "-m", "spacy", "download", "en_core_web_sm"],
                check=True
            )
            
            return True
        except subprocess.CalledProcessError as e:
            self.errors.append(f"Failed to install dependencies: {e}")
            return False
    
    def configure_environment(self):
        """Interactive environment configuration"""
        print("\n  📝 Configuring required environment variables...")
        
        # Check if already configured
        if os.getenv('KGAS_SETUP_COMPLETE'):
            print("  Environment already configured")
            return True
        
        # Get required values
        neo4j_password = input("  Enter Neo4j password (min 8 chars): ")
        if len(neo4j_password) < 8:
            self.errors.append("Neo4j password too short")
            return False
        
        openai_key = input("  Enter OpenAI API key (or press Enter to skip): ")
        
        # Update .env file
        env_path = Path('.env')
        content = env_path.read_text()
        
        # Update values
        content = content.replace('your_neo4j_password_here', neo4j_password)
        if openai_key:
            content = content.replace('sk-...', openai_key)
        
        # Add setup complete flag
        content += "\n\n# Setup completed\nKGAS_SETUP_COMPLETE=true\n"
        
        env_path.write_text(content)
        
        # Reload environment
        from dotenv import load_dotenv
        load_dotenv(override=True)
        
        return True
    
    def start_services(self):
        """Start Docker services"""
        try:
            print("  Starting Docker services...")
            subprocess.run(
                ["docker-compose", "up", "-d"],
                check=True
            )
            
            # Wait for services to be ready
            print("  Waiting for services to be ready...")
            time.sleep(10)
            
            # Check services are running
            result = subprocess.run(
                ["docker-compose", "ps"],
                capture_output=True,
                text=True
            )
            
            if "Up" not in result.stdout:
                self.errors.append("Services failed to start")
                return False
            
            return True
            
        except subprocess.CalledProcessError as e:
            self.errors.append(f"Failed to start services: {e}")
            return False
    
    def initialize_databases(self):
        """Initialize database schemas"""
        try:
            # Run database setup script
            subprocess.run(
                [sys.executable, "scripts/setup_databases.py"],
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            self.errors.append(f"Failed to initialize databases: {e}")
            return False
    
    def run_validation(self):
        """Run validation tests"""
        try:
            # Run environment validation
            subprocess.run(
                [sys.executable, "scripts/validate_env.py"],
                check=True
            )
            
            # Run quick tests
            subprocess.run(
                [sys.executable, "-m", "pytest", "tests/quick_validation.py", "-v"],
                check=True
            )
            
            return True
        except subprocess.CalledProcessError:
            self.errors.append("Validation tests failed")
            return False

if __name__ == "__main__":
    setup = QuickSetup()
    success = setup.run()
    sys.exit(0 if success else 1)
```

## Success Criteria

- [ ] All 47+ environment variables documented
- [ ] .env.example complete with descriptions
- [ ] Validation script catches common errors
- [ ] Setup guide enables <30 minute setup
- [ ] Automated setup script works reliably

## Deliverables

1. **Complete .env.example** with all 47+ variables
2. **validate_env.py** script for configuration validation  
3. **SETUP.md** quick start guide
4. **quick_setup.py** automated setup script
5. **Updated developer documentation**