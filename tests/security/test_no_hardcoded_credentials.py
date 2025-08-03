"""
Security tests to detect hardcoded credentials in the codebase.
These tests should FAIL initially, exposing the security vulnerabilities.
"""
import os
import re
from pathlib import Path
import pytest


def test_no_hardcoded_passwords_in_python_files():
    """Test that no Python files contain hardcoded passwords"""
    
    # Patterns that indicate hardcoded credentials
    password_patterns = [
        r'password\s*=\s*[\'\"]\w+[\'\"]]',
        r'testpassword',
        r'neo4j_password\s*=\s*[\'\"]\w+[\'\"]]'
    ]
    
    python_files = list(Path('src').glob('**/*.py'))
    violations = []
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            for line_num, line in enumerate(content.split('\n'), 1):
                for pattern in password_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        violations.append(f"{file_path}:{line_num}: {line.strip()}")
        except Exception as e:
            # Skip files that can't be read
            continue
    
    # This test should FAIL initially with 2 violations from verified analysis
    assert len(violations) == 0, f"Found hardcoded passwords in Python files: {violations}"


def test_no_hardcoded_passwords_in_config_files():
    """Test that config files don't contain hardcoded passwords"""
    
    config_paths = ['config']
    violations = []
    
    for config_dir in config_paths:
        if not Path(config_dir).exists():
            continue
            
        config_files = list(Path(config_dir).glob('**/*.yaml')) + list(Path(config_dir).glob('**/*.yml'))
        
        for file_path in config_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                if 'testpassword' in content.lower():
                    violations.append(f"{file_path}: Contains 'testpassword'")
            except Exception as e:
                continue
    
    # This test should FAIL initially with 1 violation from verified analysis
    assert len(violations) == 0, f"Found hardcoded passwords in config files: {violations}"


def test_specific_verified_vulnerabilities():
    """Test the 3 specific vulnerabilities identified in the analysis"""
    
    vulnerabilities = [
        ('src/tools/phase1/t68_pagerank_calculator_unified.py', 78, 'testpassword'),
        ('src/tools/phase1/t49_multihop_query_unified.py', 73, 'testpassword'),
        ('config/default.yaml', 10, 'testpassword')
    ]
    
    found_vulnerabilities = []
    
    for file_path, expected_line, expected_content in vulnerabilities:
        if not Path(file_path).exists():
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            # Check if the vulnerability still exists
            if len(lines) >= expected_line:
                line_content = lines[expected_line - 1].strip()
                if expected_content.lower() in line_content.lower():
                    found_vulnerabilities.append(f"{file_path}:{expected_line}: {line_content}")
        except Exception as e:
            continue
    
    # This test should FAIL initially with the 3 verified vulnerabilities
    assert len(found_vulnerabilities) == 0, f"Found verified hardcoded credentials: {found_vulnerabilities}"


def test_environment_variables_configured():
    """Test that environment variable configuration is properly set up"""
    
    # Check if .env.example exists (should be created during fix)
    env_example_path = Path('.env.example')
    assert env_example_path.exists(), ".env.example file should exist for secure configuration"
    
    # Check that .env.example contains required variables
    with open(env_example_path, 'r') as f:
        env_content = f.read()
    
    required_vars = ['NEO4J_PASSWORD', 'NEO4J_URI', 'NEO4J_USER']
    for var in required_vars:
        assert var in env_content, f"Required environment variable {var} not found in .env.example"


if __name__ == "__main__":
    # Run tests to see current failures
    print("🧪 Running security tests to expose vulnerabilities...")
    
    try:
        test_no_hardcoded_passwords_in_python_files()
        print("✅ No hardcoded passwords in Python files")
    except AssertionError as e:
        print(f"❌ SECURITY ISSUE: {e}")
    
    try:
        test_no_hardcoded_passwords_in_config_files()
        print("✅ No hardcoded passwords in config files")
    except AssertionError as e:
        print(f"❌ SECURITY ISSUE: {e}")
        
    try:
        test_specific_verified_vulnerabilities()
        print("✅ No verified vulnerabilities found")
    except AssertionError as e:
        print(f"❌ SECURITY ISSUE: {e}")
        
    try:
        test_environment_variables_configured()
        print("✅ Environment variables properly configured")
    except AssertionError as e:
        print(f"❌ CONFIGURATION ISSUE: {e}")