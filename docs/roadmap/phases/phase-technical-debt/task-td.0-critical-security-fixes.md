# Task TD.0: Critical Security Fixes (IMMEDIATE)

## Overview
Fix critical security vulnerabilities by removing all hardcoded credentials from the codebase.

**Duration**: Day 1 (IMMEDIATE)  
**Priority**: 🚨 CRITICAL SECURITY RISK  
**Prerequisites**: None - Must be done FIRST  

## 🔍 VERIFIED SECURITY VULNERABILITIES

### Hardcoded Password Locations (Confirmed 2025-07-25)
1. **src/tools/phase1/t68_pagerank_calculator_unified.py:78**
   ```python
   neo4j_password = "testpassword"  # ✅ VERIFIED LINE 78
   ```

2. **src/tools/phase1/t49_multihop_query_unified.py:73**
   ```python
   neo4j_password = "testpassword"  # ✅ VERIFIED LINE 73
   ```

3. **config/default.yaml:10**
   ```yaml
   password: 'testpassword'  # ✅ VERIFIED LINE 10 - IN VERSION CONTROL
   ```

## 🧪 TDD APPROACH

### Step 1: Write Security Tests (Red Phase)
```python
# tests/security/test_no_hardcoded_credentials.py
import os
import re
from pathlib import Path

def test_no_hardcoded_passwords_in_python_files():
    """Test that no Python files contain hardcoded passwords"""
    
    # Patterns that indicate hardcoded credentials
    password_patterns = [
        r'password\s*=\s*[\'\"]\w+[\'\"]]',
        r'testpassword',
        r'password.*=.*[\'\"]\w+[\'\"]]'
    ]
    
    python_files = Path('src').glob('**/*.py')
    violations = []
    
    for file_path in python_files:
        with open(file_path, 'r') as f:
            content = f.read()
            
        for line_num, line in enumerate(content.split('\n'), 1):
            for pattern in password_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    violations.append(f"{file_path}:{line_num}: {line.strip()}")
    
    # This test should FAIL initially with 2 violations
    assert len(violations) == 0, f"Found hardcoded passwords: {violations}"

def test_no_hardcoded_passwords_in_config_files():
    """Test that config files don't contain hardcoded passwords"""
    
    config_files = list(Path('config').glob('**/*.yaml')) + list(Path('config').glob('**/*.yml'))
    violations = []
    
    for file_path in config_files:
        with open(file_path, 'r') as f:
            content = f.read()
            
        if 'testpassword' in content.lower():
            violations.append(f"{file_path}: Contains 'testpassword'")
    
    # This test should FAIL initially with 1 violation
    assert len(violations) == 0, f"Found hardcoded passwords in config: {violations}"
```

### Step 2: Fix Security Issues (Green Phase)

**Fix 1: t68_pagerank_calculator_unified.py**
```python
# BEFORE (Line 78):
neo4j_password = "testpassword"

# AFTER:
neo4j_password = os.getenv('NEO4J_PASSWORD') or self.neo4j_config.get('password', '')
if not neo4j_password:
    raise ValueError("Neo4j password must be provided via NEO4J_PASSWORD env var or config")
```

**Fix 2: t49_multihop_query_unified.py**  
```python
# BEFORE (Line 73):
neo4j_password = "testpassword"

# AFTER:
neo4j_password = os.getenv('NEO4J_PASSWORD') or self.neo4j_config.get('password', '')
if not neo4j_password:
    raise ValueError("Neo4j password must be provided via NEO4J_PASSWORD env var or config")
```

**Fix 3: config/default.yaml**
```yaml
# BEFORE (Line 10):
password: 'testpassword'

# AFTER:
password: '${NEO4J_PASSWORD:-}'  # Environment variable with empty default
```

### Step 3: Add Environment Configuration (Refactor Phase)

**Create .env.example**:
```bash
# .env.example - Safe to commit
NEO4J_PASSWORD=your_secure_password_here
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
```

**Update config_loader.py to handle environment variables**:
```python
# config/config_loader.py
import os
from typing import Any, Dict

def resolve_env_vars(config: Dict[str, Any]) -> Dict[str, Any]:
    """Resolve ${VAR_NAME:-default} patterns in config"""
    
    def resolve_value(value):
        if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
            # Parse ${VAR_NAME:-default} format
            env_spec = value[2:-1]  # Remove ${ and }
            if ':-' in env_spec:
                var_name, default = env_spec.split(':-', 1)
                return os.getenv(var_name, default)
            else:
                return os.getenv(env_spec, '')
        elif isinstance(value, dict):
            return {k: resolve_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [resolve_value(item) for item in value]
        return value
    
    return resolve_value(config)
```

## 🎯 SUCCESS CRITERIA

### Security Tests Must Pass
- [ ] `test_no_hardcoded_passwords_in_python_files()` passes (0 violations)
- [ ] `test_no_hardcoded_passwords_in_config_files()` passes (0 violations)
- [ ] All existing functionality still works with environment variables

### Verification Commands
```bash
# Verify no hardcoded passwords remain
grep -r "testpassword" src/ config/ || echo "✅ No hardcoded passwords found"

# Verify config resolution works
python -c "from config.config_loader import get_config; print('✅ Config loads successfully')"

# Verify tools still work with proper env vars
export NEO4J_PASSWORD="secure_password"
python -c "from src.tools.phase1.t68_pagerank_calculator_unified import PageRankCalculator; print('✅ Tools work with env vars')"
```

### Documentation Updates
- [ ] Update README.md with environment variable requirements
- [ ] Create setup instructions for secure password management
- [ ] Add security best practices documentation

## 🚨 IMMEDIATE ACTION REQUIRED

This task must be completed IMMEDIATELY before any other work:

1. **Day 1 Morning**: Write and run security tests (should fail)
2. **Day 1 Afternoon**: Fix all hardcoded passwords 
3. **Day 1 Evening**: Verify tests pass and functionality works

**Risk**: Every day these hardcoded passwords remain is a security vulnerability that could compromise production systems.

## Evidence Required

Create `Evidence_Security_Fixes.md` with:
- Screenshots of failing security tests
- Git diff showing removed hardcoded passwords
- Verification that all security tests pass
- Confirmation that functionality works with environment variables

**No other technical debt work should begin until this critical security issue is resolved.**