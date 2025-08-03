"""
Comprehensive Security Test Suite for Production Configuration System
===================================================================

Tests all critical security aspects identified in the security assessment:
- Encryption security and key management
- File permission security
- Configuration validation security
- Error handling security
- Resource management security

NO SECURITY COMPROMISES ALLOWED - ALL TESTS MUST PASS
"""

import os
import sys
import pytest
import tempfile
import json
import time
import subprocess
from pathlib import Path
from unittest.mock import patch, mock_open

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.core.secure_credential_manager_fixed import (
    ProductionCredentialManager,
    SecureCredentialEncryption,
    AtomicFileOperations,
    CredentialSecurityError,
    CredentialNotFoundError,
    generate_master_key
)
from src.core.production_config_manager_fixed import (
    ProductionConfigManager,
    ConfigurationError,
    ConfigurationValidationError,
    Environment
)


class TestEncryptionSecurity:
    """Test encryption implementation security."""
    
    def test_master_key_required(self):
        """Test that master key is required - NO fallbacks allowed."""
        # Remove any existing master key
        if 'KGAS_MASTER_KEY' in os.environ:
            del os.environ['KGAS_MASTER_KEY']
        
        with pytest.raises(CredentialSecurityError, match="KGAS_MASTER_KEY environment variable is required"):
            SecureCredentialEncryption()
    
    def test_invalid_master_key_format(self):
        """Test that invalid master key format is rejected."""
        os.environ['KGAS_MASTER_KEY'] = 'invalid-key'
        
        with pytest.raises(CredentialSecurityError, match="Invalid KGAS_MASTER_KEY format"):
            SecureCredentialEncryption()
    
    def test_master_key_length_validation(self):
        """Test that master key must be exactly 32 bytes."""
        # Too short
        short_key = b'short'
        with pytest.raises(CredentialSecurityError, match="Master key must be exactly 32 bytes"):
            SecureCredentialEncryption(master_key=short_key)
        
        # Too long
        long_key = b'x' * 64
        with pytest.raises(CredentialSecurityError, match="Master key must be exactly 32 bytes"):
            SecureCredentialEncryption(master_key=long_key)
    
    def test_encryption_no_empty_values(self):
        """Test that empty values cannot be encrypted."""
        master_key = os.urandom(32)
        encryption = SecureCredentialEncryption(master_key=master_key)
        
        with pytest.raises(CredentialSecurityError, match="Cannot encrypt empty credential"):
            encryption.encrypt("")
        
        with pytest.raises(CredentialSecurityError, match="Cannot encrypt empty credential"):
            encryption.encrypt(None)
    
    def test_decryption_no_empty_values(self):
        """Test that empty values cannot be decrypted."""
        master_key = os.urandom(32)
        encryption = SecureCredentialEncryption(master_key=master_key)
        
        with pytest.raises(CredentialSecurityError, match="Cannot decrypt empty ciphertext"):
            encryption.decrypt("")
        
        with pytest.raises(CredentialSecurityError, match="Cannot decrypt empty ciphertext"):
            encryption.decrypt(None)
    
    def test_no_plaintext_fallback(self):
        """Test that there is NO fallback to plaintext on decryption failure."""
        master_key = os.urandom(32)
        encryption = SecureCredentialEncryption(master_key=master_key)
        
        # Try to decrypt plaintext - should fail with security error
        with pytest.raises(CredentialSecurityError, match="Decryption failed"):
            encryption.decrypt("plaintext-api-key")
    
    def test_encryption_roundtrip(self):
        """Test that encryption/decryption works correctly."""
        master_key = os.urandom(32)
        encryption = SecureCredentialEncryption(master_key=master_key)
        
        original = "sk-test123456789abcdef"
        encrypted = encryption.encrypt(original)
        decrypted = encryption.decrypt(encrypted)
        
        assert decrypted == original
        assert encrypted != original  # Must be actually encrypted
        assert encryption.is_encrypted(encrypted)
        assert not encryption.is_encrypted(original)


class TestFilePermissionSecurity:
    """Test file permission security."""
    
    def test_credential_directory_permissions(self):
        """Test that credential directory has secure permissions."""
        master_key = generate_master_key()
        os.environ['KGAS_MASTER_KEY'] = master_key
        
        with tempfile.TemporaryDirectory() as temp_dir:
            cred_manager = ProductionCredentialManager(credentials_dir=temp_dir)
            
            # Check directory permissions
            dir_mode = Path(temp_dir).stat().st_mode & 0o777
            assert dir_mode == 0o700, f"Directory permissions should be 700, got {oct(dir_mode)}"
    
    def test_credential_file_permissions(self):
        """Test that credential files have secure permissions."""
        master_key = generate_master_key()
        os.environ['KGAS_MASTER_KEY'] = master_key
        
        with tempfile.TemporaryDirectory() as temp_dir:
            cred_manager = ProductionCredentialManager(credentials_dir=temp_dir)
            cred_manager.store_credential('test', 'sk-test123', expires_days=30)
            
            # Check file permissions
            creds_file = Path(temp_dir) / "credentials.json"
            metadata_file = Path(temp_dir) / "metadata.json"
            
            for file_path in [creds_file, metadata_file]:
                file_mode = file_path.stat().st_mode & 0o777
                assert file_mode == 0o600, f"File {file_path} permissions should be 600, got {oct(file_mode)}"
    
    def test_insecure_directory_permissions_rejected(self):
        """Test that insecure directory permissions are rejected."""
        master_key = generate_master_key()
        os.environ['KGAS_MASTER_KEY'] = master_key
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Make directory world-readable
            os.chmod(temp_dir, 0o755)
            
            with pytest.raises(CredentialSecurityError, match="Credentials directory has insecure permissions"):
                ProductionCredentialManager(credentials_dir=temp_dir)
    
    def test_atomic_file_operations(self):
        """Test that file operations are atomic."""
        test_dir = Path(tempfile.mkdtemp())
        test_file = test_dir / "test.json"
        
        try:
            # Test atomic write
            content = '{"test": "value"}'
            AtomicFileOperations.write_secure_file(test_file, content)
            
            # File should exist and be readable
            assert test_file.exists()
            read_content = AtomicFileOperations.read_secure_file(test_file)
            assert read_content == content
            
            # Check permissions
            file_mode = test_file.stat().st_mode & 0o777
            assert file_mode == 0o600
            
        finally:
            # Cleanup
            if test_file.exists():
                test_file.unlink()
            test_dir.rmdir()


class TestCredentialValidationSecurity:
    """Test credential validation security."""
    
    def test_provider_name_validation(self):
        """Test that provider names are validated."""
        master_key = generate_master_key()
        os.environ['KGAS_MASTER_KEY'] = master_key
        
        with tempfile.TemporaryDirectory() as temp_dir:
            cred_manager = ProductionCredentialManager(credentials_dir=temp_dir)
            
            # Empty provider name
            with pytest.raises(ValueError, match="Provider name cannot be empty"):
                cred_manager.store_credential("", "sk-test123", expires_days=30)
            
            # Whitespace-only provider name
            with pytest.raises(ValueError, match="Provider name cannot be empty"):
                cred_manager.store_credential("   ", "sk-test123", expires_days=30)
    
    def test_credential_content_validation(self):
        """Test that credential content is validated."""
        master_key = generate_master_key()
        os.environ['KGAS_MASTER_KEY'] = master_key
        
        with tempfile.TemporaryDirectory() as temp_dir:
            cred_manager = ProductionCredentialManager(credentials_dir=temp_dir)
            
            # Empty credential
            with pytest.raises(ValueError, match="Credential must be at least 8 characters"):
                cred_manager.store_credential("test", "", expires_days=30)
            
            # Too short credential
            with pytest.raises(ValueError, match="Credential must be at least 8 characters"):
                cred_manager.store_credential("test", "short", expires_days=30)
    
    def test_expiry_validation(self):
        """Test that expiry is validated."""
        master_key = generate_master_key()
        os.environ['KGAS_MASTER_KEY'] = master_key
        
        with tempfile.TemporaryDirectory() as temp_dir:
            cred_manager = ProductionCredentialManager(credentials_dir=temp_dir)
            
            # Zero expiry
            with pytest.raises(ValueError, match="Expiry must be between 1 and 365 days"):
                cred_manager.store_credential("test", "sk-test123", expires_days=0)
            
            # Negative expiry
            with pytest.raises(ValueError, match="Expiry must be between 1 and 365 days"):
                cred_manager.store_credential("test", "sk-test123", expires_days=-1)
            
            # Too long expiry
            with pytest.raises(ValueError, match="Expiry must be between 1 and 365 days"):
                cred_manager.store_credential("test", "sk-test123", expires_days=400)
    
    def test_expired_credential_access_denied(self):
        """Test that expired credentials cannot be accessed."""
        master_key = generate_master_key()
        os.environ['KGAS_MASTER_KEY'] = master_key
        
        with tempfile.TemporaryDirectory() as temp_dir:
            cred_manager = ProductionCredentialManager(credentials_dir=temp_dir)
            
            # Store credential with 1 day expiry
            cred_manager.store_credential("test", "sk-test123", expires_days=1)
            
            # Manually expire the credential
            cred_manager.metadata["test"].expires_at = cred_manager.metadata["test"].created_at
            
            # Access should be denied
            with pytest.raises(CredentialSecurityError, match="Credential for test has expired"):
                cred_manager.get_credential("test")


class TestConfigurationValidationSecurity:
    """Test configuration validation security."""
    
    def test_missing_config_directory_fails(self):
        """Test that missing config directory causes failure."""
        with pytest.raises(ConfigurationError, match="Configuration directory does not exist"):
            ProductionConfigManager(config_dir="/nonexistent/path")
    
    def test_invalid_environment_fails(self):
        """Test that invalid environment values are rejected."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create minimal config
            base_config = Path(temp_dir) / "base.yaml"
            base_config.write_text("database:\n  neo4j:\n    host: localhost\n    port: 7687\n    username: neo4j\n    database: neo4j")
            
            with pytest.raises(ConfigurationError, match="Invalid environment 'invalid'"):
                ProductionConfigManager(config_dir=temp_dir, environment="invalid")
    
    def test_missing_base_config_fails(self):
        """Test that missing base configuration causes failure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with pytest.raises(ConfigurationError, match="Base configuration file not found"):
                ProductionConfigManager(config_dir=temp_dir)
    
    def test_invalid_yaml_fails(self):
        """Test that invalid YAML causes failure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create invalid YAML
            base_config = Path(temp_dir) / "base.yaml"
            base_config.write_text("invalid: yaml: content: [unclosed")
            
            with pytest.raises(ConfigurationError, match="Invalid YAML in base configuration"):
                ProductionConfigManager(config_dir=temp_dir)
    
    def test_schema_validation_fails_on_invalid_config(self):
        """Test that schema validation rejects invalid configurations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create config with invalid values
            base_config = Path(temp_dir) / "base.yaml"
            base_config.write_text("""
database:
  neo4j:
    host: ""  # Invalid empty host
    port: 99999  # Invalid port
    username: neo4j
    database: neo4j
""")
            
            with pytest.raises(ConfigurationError, match="Configuration validation failed"):
                ProductionConfigManager(config_dir=temp_dir)
    
    def test_production_security_requirements(self):
        """Test that production environment enforces security requirements."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create config without production security
            base_config = Path(temp_dir) / "base.yaml"
            base_config.write_text("""
database:
  neo4j:
    host: localhost
    port: 7687
    username: neo4j
    database: neo4j
    password: ""  # No password for production
security:
  encrypt_credentials: false
  audit_logging: false
""")
            
            with pytest.raises(ConfigurationError, match="Database password required for production"):
                ProductionConfigManager(config_dir=temp_dir, environment="production")


class TestErrorHandlingSecurity:
    """Test that error handling doesn't leak sensitive information."""
    
    def test_no_credential_leakage_in_errors(self):
        """Test that credentials are not leaked in error messages."""
        master_key = generate_master_key()
        os.environ['KGAS_MASTER_KEY'] = master_key
        
        with tempfile.TemporaryDirectory() as temp_dir:
            cred_manager = ProductionCredentialManager(credentials_dir=temp_dir)
            
            # Store a credential
            secret_credential = "sk-very-secret-api-key-12345"
            cred_manager.store_credential("test", secret_credential, expires_days=30)
            
            # Corrupt the encryption to trigger error
            cred_manager.credentials["test"] = "corrupted-ciphertext"
            
            # Error message should not contain the secret
            try:
                cred_manager.get_credential("test")
                assert False, "Should have raised an error"
            except CredentialSecurityError as e:
                error_msg = str(e)
                assert secret_credential not in error_msg
                assert "very-secret" not in error_msg
    
    def test_file_operation_errors_dont_leak_content(self):
        """Test that file operation errors don't leak file content."""
        test_content = "secret-api-key-content"
        
        # Create a temporary file that exists but mock the open to fail
        with tempfile.NamedTemporaryFile() as temp_file:
            temp_path = Path(temp_file.name)
            
            # Mock file open to raise exception after the exists check
            with patch('builtins.open', side_effect=PermissionError("Permission denied")):
                with pytest.raises(CredentialSecurityError) as exc_info:
                    AtomicFileOperations.read_secure_file(temp_path)
                
                # Error message should not contain file content
                error_msg = str(exc_info.value)
                assert test_content not in error_msg


class TestResourceManagementSecurity:
    """Test proper resource management and cleanup."""
    
    def test_credential_memory_cleanup(self):
        """Test that credentials are properly cleared from memory."""
        master_key = generate_master_key()
        os.environ['KGAS_MASTER_KEY'] = master_key
        
        with tempfile.TemporaryDirectory() as temp_dir:
            cred_manager = ProductionCredentialManager(credentials_dir=temp_dir)
            
            # Store credential
            cred_manager.store_credential("test", "sk-test123", expires_days=30)
            
            # Remove credential
            cred_manager.remove_credential("test")
            
            # Credential should not be accessible
            with pytest.raises(CredentialNotFoundError):
                cred_manager.get_credential("test")
    
    def test_temporary_file_cleanup(self):
        """Test that temporary files are cleaned up on failure."""
        test_dir = Path(tempfile.mkdtemp())
        test_file = test_dir / "test.json"
        
        try:
            # Simulate write failure by making directory read-only
            os.chmod(test_dir, 0o400)
            
            with pytest.raises(CredentialSecurityError):
                AtomicFileOperations.write_secure_file(test_file, "content")
            
            # No temporary files should remain
            temp_files = list(test_dir.glob(".*tmp*"))
            assert len(temp_files) == 0, f"Temporary files not cleaned up: {temp_files}"
            
        finally:
            # Cleanup
            os.chmod(test_dir, 0o700)
            if test_file.exists():
                test_file.unlink()
            test_dir.rmdir()


class TestSecurityValidation:
    """Test comprehensive security validation."""
    
    def test_security_validation_detects_issues(self):
        """Test that security validation detects various issues."""
        master_key = generate_master_key()
        os.environ['KGAS_MASTER_KEY'] = master_key
        
        with tempfile.TemporaryDirectory() as temp_dir:
            cred_manager = ProductionCredentialManager(credentials_dir=temp_dir)
            
            # Store valid credential
            cred_manager.store_credential("test", "sk-test123", expires_days=30)
            
            # Check that no issues are found initially
            issues = cred_manager.validate_credential_security()
            assert len(issues) == 0, f"Unexpected security issues: {issues}"
            
            # Manually create security issue by changing file permissions
            creds_file = Path(temp_dir) / "credentials.json"
            os.chmod(creds_file, 0o644)  # World-readable
            
            # Validation should detect the issue
            issues = cred_manager.validate_credential_security()
            assert len(issues) > 0
            assert any("Insecure file permissions" in issue for issue in issues)


if __name__ == "__main__":
    # Run security tests
    pytest.main([__file__, "-v", "--tb=short"])