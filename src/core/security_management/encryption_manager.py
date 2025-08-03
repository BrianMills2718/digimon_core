"""
Encryption Manager

Handles data encryption, decryption, and key management.
"""

import logging
from typing import Dict, Any, Optional, List
from cryptography.fernet import Fernet

from .security_types import SecurityConfig, SecurityKeyManager, SecurityValidationError


class EncryptionManager:
    """Manages data encryption and decryption operations."""
    
    def __init__(self, config: SecurityConfig, key_manager: SecurityKeyManager):
        self.config = config
        self.key_manager = key_manager
        self.logger = logging.getLogger(__name__)
        
        # Generate encryption key for sensitive data
        self.encryption_key = self._generate_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
    
    def _generate_encryption_key(self) -> bytes:
        """Generate encryption key for sensitive data."""
        # In production, this should be derived from a master key
        # and stored securely (e.g., in a key management service)
        return Fernet.generate_key()
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """
        Encrypt sensitive data.
        
        Args:
            data: Plain text data to encrypt
            
        Returns:
            Encrypted data as string
            
        Raises:
            SecurityValidationError: If encryption fails
        """
        try:
            if not isinstance(data, str):
                raise SecurityValidationError("Data must be a string")
            
            if not data:
                raise SecurityValidationError("Cannot encrypt empty data")
            
            encrypted_data = self.cipher_suite.encrypt(data.encode('utf-8'))
            return encrypted_data.decode('latin-1')  # Use latin-1 for byte safety
            
        except Exception as e:
            self.logger.error(f"Encryption failed: {e}")
            raise SecurityValidationError(f"Encryption failed: {e}")
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """
        Decrypt sensitive data.
        
        Args:
            encrypted_data: Encrypted data as string
            
        Returns:
            Decrypted plain text data
            
        Raises:
            SecurityValidationError: If decryption fails
        """
        try:
            if not isinstance(encrypted_data, str):
                raise SecurityValidationError("Encrypted data must be a string")
            
            if not encrypted_data:
                raise SecurityValidationError("Cannot decrypt empty data")
            
            # Convert back to bytes
            encrypted_bytes = encrypted_data.encode('latin-1')
            decrypted_data = self.cipher_suite.decrypt(encrypted_bytes)
            return decrypted_data.decode('utf-8')
            
        except Exception as e:
            self.logger.error(f"Decryption failed: {e}")
            raise SecurityValidationError(f"Decryption failed: {e}")
    
    def encrypt_dict(self, data_dict: Dict[str, Any], 
                    sensitive_fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Encrypt sensitive fields in a dictionary.
        
        Args:
            data_dict: Dictionary containing data to encrypt
            sensitive_fields: List of field names to encrypt (if None, encrypts common sensitive fields)
            
        Returns:
            Dictionary with sensitive fields encrypted
        """
        if sensitive_fields is None:
            # Common sensitive field names
            sensitive_fields = [
                'password', 'secret', 'token', 'key', 'api_key',
                'private_key', 'access_token', 'refresh_token',
                'ssn', 'social_security_number', 'credit_card',
                'bank_account', 'phone', 'email', 'personal_info'
            ]
        
        encrypted_dict = data_dict.copy()
        
        for field_name in sensitive_fields:
            if field_name in encrypted_dict:
                field_value = encrypted_dict[field_name]
                if isinstance(field_value, str) and field_value:
                    try:
                        encrypted_dict[field_name] = self.encrypt_sensitive_data(field_value)
                        encrypted_dict[f"{field_name}_encrypted"] = True
                    except SecurityValidationError as e:
                        self.logger.warning(f"Failed to encrypt field {field_name}: {e}")
        
        return encrypted_dict
    
    def decrypt_dict(self, encrypted_dict: Dict[str, Any],
                    sensitive_fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Decrypt sensitive fields in a dictionary.
        
        Args:
            encrypted_dict: Dictionary containing encrypted data
            sensitive_fields: List of field names to decrypt
            
        Returns:
            Dictionary with sensitive fields decrypted
        """
        if sensitive_fields is None:
            # Find fields marked as encrypted
            sensitive_fields = [
                field.replace('_encrypted', '') 
                for field in encrypted_dict.keys() 
                if field.endswith('_encrypted') and encrypted_dict[field]
            ]
        
        decrypted_dict = encrypted_dict.copy()
        
        for field_name in sensitive_fields:
            encrypted_marker = f"{field_name}_encrypted"
            
            if (field_name in decrypted_dict and 
                encrypted_marker in decrypted_dict and 
                decrypted_dict[encrypted_marker]):
                
                encrypted_value = decrypted_dict[field_name]
                if isinstance(encrypted_value, str) and encrypted_value:
                    try:
                        decrypted_dict[field_name] = self.decrypt_sensitive_data(encrypted_value)
                        # Remove encryption marker
                        del decrypted_dict[encrypted_marker]
                    except SecurityValidationError as e:
                        self.logger.warning(f"Failed to decrypt field {field_name}: {e}")
        
        return decrypted_dict
    
    def hash_password(self, password: str, salt: Optional[bytes] = None) -> Dict[str, str]:
        """
        Hash password with salt.
        
        Args:
            password: Plain text password
            salt: Optional salt (if None, generates new salt)
            
        Returns:
            Dictionary with hashed password and salt
        """
        import bcrypt
        
        try:
            if not isinstance(password, str) or not password:
                raise SecurityValidationError("Password must be a non-empty string")
            
            if salt is None:
                salt = bcrypt.gensalt()
            
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            
            return {
                'hashed_password': hashed.decode('utf-8'),
                'salt': salt.decode('utf-8')
            }
            
        except Exception as e:
            self.logger.error(f"Password hashing failed: {e}")
            raise SecurityValidationError(f"Password hashing failed: {e}")
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """
        Verify password against hash.
        
        Args:
            password: Plain text password
            hashed_password: Hashed password to verify against
            
        Returns:
            True if password matches hash
        """
        import bcrypt
        
        try:
            if not isinstance(password, str) or not isinstance(hashed_password, str):
                return False
            
            return bcrypt.checkpw(
                password.encode('utf-8'), 
                hashed_password.encode('utf-8')
            )
            
        except Exception as e:
            self.logger.error(f"Password verification failed: {e}")
            return False
    
    def generate_secure_token(self, length: int = 32) -> str:
        """
        Generate cryptographically secure token.
        
        Args:
            length: Token length in bytes
            
        Returns:
            Secure token string
        """
        import secrets
        
        if length < 16:
            raise SecurityValidationError("Token length must be at least 16 bytes")
        
        return secrets.token_urlsafe(length)
    
    def encrypt_file_content(self, file_content: bytes) -> bytes:
        """
        Encrypt file content.
        
        Args:
            file_content: File content as bytes
            
        Returns:
            Encrypted file content
        """
        try:
            if not isinstance(file_content, bytes):
                raise SecurityValidationError("File content must be bytes")
            
            return self.cipher_suite.encrypt(file_content)
            
        except Exception as e:
            self.logger.error(f"File encryption failed: {e}")
            raise SecurityValidationError(f"File encryption failed: {e}")
    
    def decrypt_file_content(self, encrypted_content: bytes) -> bytes:
        """
        Decrypt file content.
        
        Args:
            encrypted_content: Encrypted file content
            
        Returns:
            Decrypted file content
        """
        try:
            if not isinstance(encrypted_content, bytes):
                raise SecurityValidationError("Encrypted content must be bytes")
            
            return self.cipher_suite.decrypt(encrypted_content)
            
        except Exception as e:
            self.logger.error(f"File decryption failed: {e}")
            raise SecurityValidationError(f"File decryption failed: {e}")
    
    def create_checksum(self, data: str) -> str:
        """
        Create SHA-256 checksum of data.
        
        Args:
            data: Data to checksum
            
        Returns:
            Hexadecimal checksum string
        """
        import hashlib
        
        if not isinstance(data, str):
            data = str(data)
        
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    
    def verify_checksum(self, data: str, expected_checksum: str) -> bool:
        """
        Verify data against expected checksum.
        
        Args:
            data: Data to verify
            expected_checksum: Expected checksum
            
        Returns:
            True if checksum matches
        """
        actual_checksum = self.create_checksum(data)
        return actual_checksum == expected_checksum
    
    def get_encryption_info(self) -> Dict[str, Any]:
        """Get encryption configuration information."""
        return {
            'encryption_algorithm': 'Fernet (AES 128)',
            'key_length_bits': 128,
            'has_encryption_key': self.encryption_key is not None,
            'cipher_suite_type': type(self.cipher_suite).__name__
        }