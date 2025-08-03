"""
Enterprise Security Fixes Validation Tests
==========================================

Tests that validate all critical security fixes identified in the assessment:
1. Environment variable bypass elimination
2. Enterprise-grade access controls
3. Credential rotation enforcement
4. Secure error handling without information leakage

These tests must ALL PASS for enterprise production readiness.
"""

import os
import sys
import pytest
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.core.secure_credential_manager_fixed import (
    ProductionCredentialManager,
    CredentialSecurityError,
    CredentialNotFoundError,
    generate_master_key
)
from src.core.secure_error_handler import (
    SecureErrorHandler,
    secure_error_response,
    get_secure_error_handler
)


class TestEnvironmentVariableBypassElimination:
    """Test that environment variable bypass vulnerability is completely eliminated."""
    
    def test_no_environment_variable_fallback(self):
        """Test that environment variables are NO LONGER used as fallback."""
        master_key = generate_master_key()
        os.environ['KGAS_MASTER_KEY'] = master_key
        
        # Set environment variable that would previously be used as fallback
        os.environ['KGAS_OPENAI_API_KEY'] = 'sk-env-variable-key'
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                cred_manager = ProductionCredentialManager(credentials_dir=temp_dir)
                
                # This MUST fail - no fallback to environment variables allowed
                with pytest.raises(CredentialNotFoundError) as exc_info:
                    cred_manager.get_credential('openai')
                
                # Verify error message mentions no managed credential found
                error_msg = str(exc_info.value)
                assert "No managed credential found" in error_msg
                assert "Environment variable fallbacks are disabled" in error_msg
                
        finally:
            # Clean up
            if 'KGAS_OPENAI_API_KEY' in os.environ:
                del os.environ['KGAS_OPENAI_API_KEY']
    
    def test_error_message_explains_security_policy(self):
        """Test that error message explains why environment variables are disabled."""
        master_key = generate_master_key()
        os.environ['KGAS_MASTER_KEY'] = master_key
        
        with tempfile.TemporaryDirectory() as temp_dir:
            cred_manager = ProductionCredentialManager(credentials_dir=temp_dir)
            
            with pytest.raises(CredentialNotFoundError) as exc_info:
                cred_manager.get_credential('nonexistent')
            
            error_msg = str(exc_info.value)
            assert "All credentials must be stored through the secure credential manager" in error_msg
            assert "Environment variable fallbacks are disabled for security" in error_msg


class TestEnterpriseAccessControls:
    """Test enterprise-grade access controls and policies."""
    
    def test_credential_rotation_enforcement_on_startup(self):
        """Test that rotation policies are enforced on startup."""
        master_key = generate_master_key()
        os.environ['KGAS_MASTER_KEY'] = master_key
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create credential manager and store credential
            cred_manager = ProductionCredentialManager(credentials_dir=temp_dir, enforce_rotation=False)
            cred_manager.store_credential('test', 'sk-test123456789', expires_days=30)
            
            # Manually age the credential beyond rotation limit
            cred_manager.metadata['test'].created_at = datetime.now() - timedelta(days=91)
            cred_manager._save_credentials()
            
            # Create new manager with rotation enforcement - should fail
            with pytest.raises(CredentialSecurityError) as exc_info:
                ProductionCredentialManager(credentials_dir=temp_dir, enforce_rotation=True)
            
            error_msg = str(exc_info.value)
            assert "Credential rotation REQUIRED" in error_msg
            assert "test" in error_msg
    
    def test_access_count_rotation_enforcement(self):
        """Test that high access count triggers rotation requirement."""
        master_key = generate_master_key()
        os.environ['KGAS_MASTER_KEY'] = master_key
        
        with tempfile.TemporaryDirectory() as temp_dir:
            cred_manager = ProductionCredentialManager(credentials_dir=temp_dir, enforce_rotation=True)
            cred_manager.store_credential('test', 'sk-test123456789', expires_days=30)
            
            # Simulate high access count
            cred_manager.metadata['test'].access_count = 10001  # Over limit
            
            # Access should fail due to rotation requirement
            with pytest.raises(CredentialSecurityError) as exc_info:
                cred_manager.get_credential('test')
            
            error_msg = str(exc_info.value)
            assert "MUST be rotated" in error_msg
            assert "10001 times" in error_msg
    
    def test_age_based_rotation_enforcement(self):
        """Test that old credentials require rotation."""
        master_key = generate_master_key()
        os.environ['KGAS_MASTER_KEY'] = master_key
        
        with tempfile.TemporaryDirectory() as temp_dir:
            cred_manager = ProductionCredentialManager(credentials_dir=temp_dir, enforce_rotation=True)
            cred_manager.store_credential('test', 'sk-test123456789', expires_days=30)
            
            # Age the credential beyond rotation limit
            cred_manager.metadata['test'].created_at = datetime.now() - timedelta(days=91)
            
            # Access should fail due to age
            with pytest.raises(CredentialSecurityError) as exc_info:
                cred_manager.get_credential('test')
            
            error_msg = str(exc_info.value)
            assert "91 days old and MUST be rotated" in error_msg
    
    def test_rotation_warnings_at_threshold(self):
        """Test that warnings are issued when approaching rotation limits."""
        master_key = generate_master_key()
        os.environ['KGAS_MASTER_KEY'] = master_key
        
        with tempfile.TemporaryDirectory() as temp_dir:
            cred_manager = ProductionCredentialManager(credentials_dir=temp_dir, enforce_rotation=True)
            cred_manager.store_credential('test', 'sk-test123456789', expires_days=30)
            
            # Set credential to 80% of age limit (72 days)
            cred_manager.metadata['test'].created_at = datetime.now() - timedelta(days=72)
            
            # Should succeed but generate warning
            with patch.object(cred_manager.logger, 'warning') as mock_warning:
                credential = cred_manager.get_credential('test')
                assert credential == 'sk-test123456789'
                
                # Check that warning was logged
                mock_warning.assert_called()
                warning_calls = [call.args[0] for call in mock_warning.call_args_list]
                assert any("approaching age limit" in call for call in warning_calls)
    
    def test_audit_trail_logging(self):
        """Test that comprehensive audit trail is logged."""
        master_key = generate_master_key()
        os.environ['KGAS_MASTER_KEY'] = master_key
        
        with tempfile.TemporaryDirectory() as temp_dir:
            cred_manager = ProductionCredentialManager(credentials_dir=temp_dir, enforce_rotation=True)
            cred_manager.store_credential('test', 'sk-test123456789', expires_days=30)
            
            # Access credential and verify audit logging
            with patch.object(cred_manager.logger, 'info') as mock_info:
                credential = cred_manager.get_credential('test')
                
                # Check that access was logged with proper details
                info_calls = [call.args[0] for call in mock_info.call_args_list]
                access_log = next((call for call in info_calls if "Credential accessed" in call), None)
                
                assert access_log is not None
                assert "provider=test" in access_log
                assert "access_count=" in access_log
                assert "days_since_creation=" in access_log


class TestSecureErrorHandling:
    """Test that error handling doesn't leak sensitive information."""
    
    def test_error_message_sanitization(self):
        """Test that sensitive information is removed from error messages."""
        handler = SecureErrorHandler()
        
        # Test various sensitive patterns
        test_cases = [
            ("File '/home/user/secret/api_key.txt' not found", "Required file not found"),
            ("Connection failed with sk-1234567890abcdef", "[API_KEY_REDACTED]"),
            ("Permission denied for /etc/password", "Access denied"),
            ("Invalid token: Bearer abc123xyz789", "[AUTH_TOKEN_REDACTED]"),
            ("Database error at localhost:5432", "Network connection failed"),
        ]
        
        for original, expected_pattern in test_cases:
            sanitized = handler.sanitize_error_message(original)
            
            # Check that sensitive information is not present
            assert "secret" not in sanitized.lower()
            assert "sk-" not in sanitized
            assert "/home/" not in sanitized
            assert "/etc/" not in sanitized
            assert "localhost" not in sanitized
    
    def test_safe_error_response_creation(self):
        """Test that safe error responses don't leak information."""
        handler = SecureErrorHandler()
        
        # Create error with sensitive information
        try:
            raise FileNotFoundError("/sensitive/path/credentials.json: Permission denied")
        except Exception as e:
            response = handler.create_safe_error_response("test_operation", e)
            
            # Verify response structure
            assert response['success'] is False
            assert response['operation'] == 'test_operation'
            assert 'error_code' in response
            assert 'error_message' in response
            assert 'timestamp' in response
            
            # Verify no sensitive information leaked
            error_msg = response['error_message']
            assert "/sensitive/" not in error_msg
            assert "credentials.json" not in error_msg
            assert "Permission denied" not in error_msg or error_msg == "Access denied"
    
    def test_timing_safe_error_responses(self):
        """Test that error responses don't reveal timing information."""
        handler = SecureErrorHandler()
        
        # Create error response
        try:
            raise ValueError("Test error")
        except Exception as e:
            error_response = handler.create_safe_error_response("test_op", e)
        
        # Test timing normalization
        expected_time = 1.0  # 1 second
        start_time = time.time()
        
        normalized_response = handler.timing_safe_error_response(expected_time, error_response)
        
        elapsed_time = time.time() - start_time
        
        # Should have taken at least the expected time
        assert elapsed_time >= expected_time
        assert normalized_response['timestamp'] >= error_response['timestamp']
    
    def test_is_error_message_safe(self):
        """Test error message safety validation."""
        handler = SecureErrorHandler()
        
        safe_messages = [
            "Invalid input value",
            "Operation failed",
            "Network connection timeout",
            "Access denied"
        ]
        
        unsafe_messages = [
            "File /home/user/secret.txt not found",
            "API key sk-1234567890 is invalid",
            "Password authentication failed for admin",
            "Internal server error at localhost:8080"
        ]
        
        for msg in safe_messages:
            assert handler.is_error_message_safe(msg), f"Message should be safe: {msg}"
        
        for msg in unsafe_messages:
            assert not handler.is_error_message_safe(msg), f"Message should be unsafe: {msg}"
    
    def test_security_event_logging(self):
        """Test that security events are logged with sanitization."""
        handler = SecureErrorHandler()
        
        with patch.object(handler.logger, 'warning') as mock_warning:
            handler.log_security_event("credential_access_failed", {
                "user": "admin",
                "file": "/sensitive/path/creds.json",
                "api_key": "sk-secret123456789",
                "timestamp": time.time()
            })
            
            # Verify logging occurred
            mock_warning.assert_called_once()
            log_message = mock_warning.call_args[0][0]
            
            # Verify sensitive information was redacted
            assert "sk-secret123456789" not in log_message
            assert "/sensitive/path/creds.json" not in log_message
            assert "[API_KEY_REDACTED]" in log_message or "[PATH_REDACTED]" in log_message


class TestConvenienceFunctionSecurity:
    """Test convenience functions maintain security."""
    
    def test_secure_error_response_function(self):
        """Test that convenience function creates secure responses."""
        try:
            raise FileNotFoundError("/secret/file.txt")
        except Exception as e:
            response = secure_error_response("test_op", e, "FILE_ERROR", include_details=True)
            
            assert response['success'] is False
            assert response['operation'] == 'test_op'
            assert response['error_code'] == 'FILE_ERROR'
            
            # Verify no path information leaked
            assert "/secret/" not in str(response)
    
    def test_global_error_handler_singleton(self):
        """Test that global error handler is properly managed."""
        handler1 = get_secure_error_handler()
        handler2 = get_secure_error_handler()
        
        # Should be the same instance
        assert handler1 is handler2


class TestEnterpriseComplianceValidation:
    """Test that the system meets enterprise compliance requirements."""
    
    def test_no_unmanaged_credential_access_paths(self):
        """Test that ALL credential access goes through secure manager."""
        master_key = generate_master_key()
        os.environ['KGAS_MASTER_KEY'] = master_key
        
        # Set various environment variables that might be used as fallbacks
        env_vars = {
            'KGAS_OPENAI_API_KEY': 'sk-env-openai',
            'OPENAI_API_KEY': 'sk-fallback-openai',
            'KGAS_ANTHROPIC_API_KEY': 'ant-env-anthropic',
            'ANTHROPIC_API_KEY': 'ant-fallback-anthropic'
        }
        
        for var, value in env_vars.items():
            os.environ[var] = value
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                cred_manager = ProductionCredentialManager(credentials_dir=temp_dir)
                
                # Try to access credentials - all should fail
                providers = ['openai', 'anthropic', 'google']
                for provider in providers:
                    with pytest.raises(CredentialNotFoundError):
                        cred_manager.get_credential(provider)
        
        finally:
            # Clean up environment variables
            for var in env_vars:
                if var in os.environ:
                    del os.environ[var]
    
    def test_comprehensive_security_validation(self):
        """Test comprehensive security validation detects all issues."""
        master_key = generate_master_key()
        os.environ['KGAS_MASTER_KEY'] = master_key
        
        with tempfile.TemporaryDirectory() as temp_dir:
            cred_manager = ProductionCredentialManager(credentials_dir=temp_dir)
            
            # Store valid credential
            cred_manager.store_credential('test', 'sk-test123456789', expires_days=30)
            
            # Initially should have no issues
            issues = cred_manager.validate_credential_security()
            assert len(issues) == 0
            
            # Create security issue by manually expiring credential
            cred_manager.metadata['test'].expires_at = datetime.now() - timedelta(days=1)
            
            # Should detect the expired credential
            issues = cred_manager.validate_credential_security()
            assert len(issues) > 0
            assert any("Expired credentials" in issue for issue in issues)


if __name__ == "__main__":
    # Run all enterprise security tests
    pytest.main([__file__, "-v", "--tb=short"])