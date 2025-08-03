"""
Unit tests for security validation system

Tests the comprehensive security validation framework including
credential scanning, vulnerability detection, and security scoring.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, mock_open

from src.core.security_validation import (
    SecurityValidator,
    SecurityIssue
)


@pytest.fixture
def temp_project_dir(tmp_path):
    """Create temporary project directory with test files"""
    # Create directory structure
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    
    # Create test files with various security issues
    test_file1 = src_dir / "test_service.py"
    test_file1.write_text("""
import os

class TestService:
    def __init__(self):
        # Hardcoded credentials
        self.api_key = "sk-1234567890abcdef"
        self.password = "testpassword123"
        self.secret = "my-secret-key"
        
    def connect_database(self):
        # Potential SQL injection
        query = f"SELECT * FROM users WHERE id = {user_id}"
        return execute_query(query)
""")
    
    return tmp_path


@pytest.fixture
def security_validator():
    """Create security validator instance"""
    return SecurityValidator()


class TestSecurityIssue:
    """Test SecurityIssue data structure"""
    
    def test_security_issue_creation(self):
        """Test creating SecurityIssue"""
        issue = SecurityIssue(
            file_path="test.py",
            line_number=10,
            issue_type="hardcoded_password",
            severity="high",
            description="Hardcoded password found",
            recommendation="Use environment variables"
        )
        
        assert issue.file_path == "test.py"
        assert issue.line_number == 10
        assert issue.issue_type == "hardcoded_password"
        assert issue.severity == "high"
        assert issue.description == "Hardcoded password found"
        assert issue.recommendation == "Use environment variables"


class TestSecurityValidator:
    """Test SecurityValidator functionality"""
    
    def test_validator_initialization(self, security_validator):
        """Test validator initializes correctly"""
        assert security_validator.credential_patterns is not None
        assert len(security_validator.credential_patterns) > 0
        assert "password" in security_validator.credential_patterns
        assert "api_key" in security_validator.credential_patterns
        
    def test_scan_file_for_credentials(self, security_validator, tmp_path):
        """Test scanning file for hardcoded credentials"""
        test_file = tmp_path / "test.py"
        test_file.write_text("""
api_key = "sk-1234567890abcdef"
password = "secret123"
token = "my-secret-token"
""")
        
        issues = security_validator.scan_file(str(test_file))
        
        # Should find credential issues
        assert len(issues) >= 1
        
        # Check issue properties
        for issue in issues:
            assert isinstance(issue, SecurityIssue)
            assert issue.file_path == str(test_file)
            assert issue.line_number > 0
            assert issue.severity in ["critical", "high", "medium", "low"]
            
    def test_scan_nonexistent_file(self, security_validator):
        """Test scanning non-existent file"""
        issues = security_validator.scan_file("nonexistent.py")
        assert issues == []
        
    def test_scan_empty_file(self, security_validator, tmp_path):
        """Test scanning empty file"""
        empty_file = tmp_path / "empty.py"
        empty_file.write_text("")
        
        issues = security_validator.scan_file(str(empty_file))
        assert issues == []
        
    def test_validate_environment_config(self, security_validator):
        """Test environment configuration validation"""
        # Test with good environment config
        good_config = {
            "database": {
                "password": "${DATABASE_PASSWORD}",
                "api_key": "${API_KEY}"
            }
        }
        
        issues = security_validator.validate_environment_config(good_config)
        assert len(issues) == 0
        
        # Test with bad environment config (hardcoded values)
        bad_config = {
            "database": {
                "password": "hardcoded123",
                "api_key": "sk-hardcoded-key"
            }
        }
        
        issues = security_validator.validate_environment_config(bad_config)
        assert len(issues) > 0
        
    def test_security_score_calculation(self, security_validator):
        """Test security score calculation"""
        # Create some test issues
        issues = [
            SecurityIssue("test.py", 1, "password", "critical", "Critical issue", "Fix it"),
            SecurityIssue("test.py", 2, "api_key", "high", "High issue", "Fix it"),
            SecurityIssue("test.py", 3, "token", "medium", "Medium issue", "Fix it")
        ]
        
        score = security_validator.calculate_security_score(issues, total_files=3)
        
        # Score should be between 0 and 100
        assert 0 <= score <= 100
        
        # With critical and high issues, score should be lower
        assert score < 90
        
    def test_get_security_recommendations(self, security_validator):
        """Test getting security recommendations"""
        issues = [
            SecurityIssue("test.py", 1, "password", "critical", "Hardcoded password", "Use env vars"),
            SecurityIssue("test.py", 2, "api_key", "high", "Hardcoded API key", "Use env vars")
        ]
        
        recommendations = security_validator.get_security_recommendations(issues)
        
        assert len(recommendations) > 0
        assert any("environment" in rec.lower() for rec in recommendations)
        
    def test_concurrent_file_scanning(self, security_validator, temp_project_dir):
        """Test concurrent file scanning"""
        import threading
        
        results = []
        
        def scan_files():
            issues = security_validator.scan_directory(str(temp_project_dir))
            results.append(len(issues))
            
        # Run multiple concurrent scans
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=scan_files)
            threads.append(thread)
            thread.start()
            
        for thread in threads:
            thread.join()
            
        # All scans should return same number of issues
        assert len(results) == 3
        assert all(r > 0 for r in results)  # Should find issues
        
        # Results should be consistent
        first_result = results[0]
        for result in results[1:]:
            assert abs(result - first_result) <= 1  # Allow small variance
            
    def test_file_extension_filtering(self, security_validator, tmp_path):
        """Test filtering by file extensions"""
        # Create files with different extensions
        py_file = tmp_path / "test.py"
        py_file.write_text('password = "secret123"')
        
        js_file = tmp_path / "test.js"
        js_file.write_text('const password = "secret123"')
        
        txt_file = tmp_path / "test.txt"
        txt_file.write_text('password = "secret123"')
        
        # Scan with Python extension filter
        issues = security_validator.scan_directory(str(tmp_path), file_extensions=['.py'])
        
        # Should only find issues in Python files
        python_files = [issue.file_path for issue in issues if issue.file_path.endswith('.py')]
        non_python_files = [issue.file_path for issue in issues if not issue.file_path.endswith('.py')]
        
        assert len(python_files) > 0
        assert len(non_python_files) == 0


class TestSecurityValidationIntegration:
    """Test integration scenarios for security validation"""
    
    def test_complete_directory_scan(self, security_validator, temp_project_dir):
        """Test complete directory scanning"""
        issues = security_validator.scan_directory(str(temp_project_dir))
        
        # Should find issues
        assert len(issues) > 0
        
        # All issues should be valid
        for issue in issues:
            assert isinstance(issue, SecurityIssue)
            assert Path(issue.file_path).exists()
            assert issue.line_number > 0
            assert issue.severity in ["critical", "high", "medium", "low"]
            assert issue.description
            assert issue.recommendation
            
    def test_security_report_generation(self, security_validator, temp_project_dir):
        """Test generating comprehensive security report"""
        report = security_validator.generate_security_report(str(temp_project_dir))
        
        # Report should contain necessary information
        assert "total_files" in report
        assert "total_issues" in report
        assert "security_score" in report
        assert "issues_by_severity" in report
        assert "recommendations" in report
        
        # Values should be reasonable
        assert report["total_files"] > 0
        assert report["total_issues"] > 0
        assert 0 <= report["security_score"] <= 100
        assert len(report["recommendations"]) > 0
        
    def test_security_validation_performance(self, security_validator, temp_project_dir):
        """Test security validation performance"""
        import time
        
        # Measure scan time
        start_time = time.time()
        issues = security_validator.scan_directory(str(temp_project_dir))
        end_time = time.time()
        
        scan_time = end_time - start_time
        
        # Should complete quickly for small projects
        assert scan_time < 2.0
        
        # Should still find issues
        assert len(issues) > 0