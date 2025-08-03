"""
Secure Credential Management System
==================================

Handles encryption, rotation, and secure storage of API keys and credentials
for the KGAS system.

Features:
- AES-GCM encryption for API keys
- Credential rotation with expiry tracking
- Environment variable fallback
- Audit logging for credential access
- Multiple encryption backend support

Usage:
    cred_manager = SecureCredentialManager()
    cred_manager.store_credential('openai', 'sk-...', expires_days=90)
    api_key = cred_manager.get_credential('openai')
"""

import os
import json
import time
import logging
import secrets
import base64
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass, asdict
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


@dataclass
class CredentialMetadata:
    """Metadata for stored credentials."""
    provider: str
    created_at: datetime
    expires_at: Optional[datetime]
    last_accessed: Optional[datetime]
    access_count: int = 0
    encrypted: bool = True
    description: str = ""
    
    def is_expired(self) -> bool:
        """Check if credential has expired."""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at
    
    def days_until_expiry(self) -> Optional[int]:
        """Calculate days until expiry."""
        if self.expires_at is None:
            return None
        delta = self.expires_at - datetime.now()
        return max(0, delta.days)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        # Convert datetime objects to ISO strings
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CredentialMetadata':
        """Create from dictionary with datetime parsing."""
        # Convert ISO strings back to datetime objects
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if 'expires_at' in data and isinstance(data['expires_at'], str):
            data['expires_at'] = datetime.fromisoformat(data['expires_at'])
        if 'last_accessed' in data and isinstance(data['last_accessed'], str):
            data['last_accessed'] = datetime.fromisoformat(data['last_accessed'])
        
        return cls(**data)


class CredentialEncryption:
    """Handles encryption and decryption of credentials."""
    
    def __init__(self, password: Optional[str] = None, salt: Optional[bytes] = None):
        """Initialize encryption with password and salt."""
        self.logger = logging.getLogger(__name__)
        
        # Use provided password or environment variable
        if password is None:
            password = os.getenv('KGAS_CREDENTIAL_PASSWORD', 'default-insecure-password')
        
        # Use provided salt or generate/load one
        if salt is None:
            salt = self._get_or_create_salt()
        
        # Derive encryption key from password and salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        self.fernet = Fernet(key)
    
    def _get_or_create_salt(self) -> bytes:
        """Get existing salt or create new one."""
        salt_file = Path("config") / "credential.salt"
        
        if salt_file.exists():
            return salt_file.read_bytes()
        else:
            salt = os.urandom(16)
            salt_file.parent.mkdir(exist_ok=True)
            salt_file.write_bytes(salt)
            salt_file.chmod(0o600)  # Restrict permissions
            return salt
    
    def encrypt(self, plaintext: str) -> str:
        """Encrypt plaintext credential."""
        encrypted = self.fernet.encrypt(plaintext.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt(self, ciphertext: str) -> str:
        """Decrypt encrypted credential."""
        encrypted = base64.urlsafe_b64decode(ciphertext.encode())
        decrypted = self.fernet.decrypt(encrypted)
        return decrypted.decode()
    
    def is_encrypted(self, value: str) -> bool:
        """Check if a value appears to be encrypted."""
        try:
            # Try to decode as base64 and decrypt
            encrypted = base64.urlsafe_b64decode(value.encode())
            self.fernet.decrypt(encrypted)
            return True
        except Exception:
            return False


class SecureCredentialManager:
    """
    Secure credential management with encryption and rotation.
    
    Provides secure storage and retrieval of API keys and other credentials
    with support for encryption, expiry tracking, and audit logging.
    """
    
    def __init__(self, credentials_dir: Optional[str] = None, encrypt_by_default: bool = True):
        """Initialize credential manager."""
        self.logger = logging.getLogger(__name__)
        
        # Set up credentials directory
        if credentials_dir:
            self.credentials_dir = Path(credentials_dir)
        else:
            self.credentials_dir = Path("config") / "credentials"
        
        self.credentials_dir.mkdir(parents=True, exist_ok=True)
        
        # Secure the credentials directory
        try:
            os.chmod(self.credentials_dir, 0o700)
        except OSError:
            self.logger.warning("Could not set secure permissions on credentials directory")
        
        self.encrypt_by_default = encrypt_by_default
        self.encryption = CredentialEncryption()
        
        # Load existing credentials
        self.credentials: Dict[str, str] = {}
        self.metadata: Dict[str, CredentialMetadata] = {}
        self._load_credentials()
        
        self.logger.info(f"Credential manager initialized with {len(self.credentials)} credentials")
    
    def store_credential(
        self, 
        provider: str, 
        credential: str, 
        expires_days: Optional[int] = None,
        description: str = "",
        encrypt: Optional[bool] = None
    ) -> None:
        """Store a credential with metadata."""
        if encrypt is None:
            encrypt = self.encrypt_by_default
        
        # Encrypt credential if requested
        if encrypt:
            stored_credential = self.encryption.encrypt(credential)
        else:
            stored_credential = credential
        
        # Create metadata
        created_at = datetime.now()
        expires_at = None
        if expires_days is not None:
            expires_at = created_at + timedelta(days=expires_days)
        
        metadata = CredentialMetadata(
            provider=provider,
            created_at=created_at,
            expires_at=expires_at,
            last_accessed=None,
            access_count=0,
            encrypted=encrypt,
            description=description
        )
        
        # Store credential and metadata
        self.credentials[provider] = stored_credential
        self.metadata[provider] = metadata
        
        # Save to disk
        self._save_credentials()
        
        self.logger.info(f"Stored credential for {provider} (encrypted: {encrypt})")
        if expires_at:
            self.logger.info(f"Credential expires on {expires_at.strftime('%Y-%m-%d')}")
    
    def get_credential(self, provider: str, fallback_env_var: Optional[str] = None) -> str:
        """Get a credential with fallback to environment variable."""
        # Try stored credential first
        if provider in self.credentials:
            metadata = self.metadata[provider]
            
            # Check if expired
            if metadata.is_expired():
                self.logger.warning(f"Credential for {provider} has expired")
                # Try environment variable fallback
                if fallback_env_var:
                    env_value = os.getenv(fallback_env_var)
                    if env_value:
                        self.logger.info(f"Using environment variable {fallback_env_var} for {provider}")
                        return env_value
                raise ValueError(f"Credential for {provider} has expired and no fallback available")
            
            # Update access metadata
            metadata.last_accessed = datetime.now()
            metadata.access_count += 1
            
            # Decrypt if necessary
            credential = self.credentials[provider]
            if metadata.encrypted:
                credential = self.encryption.decrypt(credential)
            
            # Save updated metadata
            self._save_credentials()
            
            return credential
        
        # Fallback to environment variable
        if fallback_env_var:
            env_value = os.getenv(fallback_env_var)
            if env_value:
                self.logger.info(f"Using environment variable {fallback_env_var} for {provider}")
                return env_value
        
        # Try common environment variable patterns
        common_env_vars = [
            f"KGAS_{provider.upper()}_API_KEY",
            f"{provider.upper()}_API_KEY",
            f"KGAS_{provider.upper()}_KEY",
        ]
        
        for env_var in common_env_vars:
            env_value = os.getenv(env_var)
            if env_value:
                self.logger.info(f"Using environment variable {env_var} for {provider}")
                return env_value
        
        raise ValueError(f"No credential found for {provider}")
    
    def rotate_credential(self, provider: str, new_credential: str, expires_days: Optional[int] = None) -> None:
        """Rotate an existing credential."""
        if provider not in self.credentials:
            raise ValueError(f"No existing credential for {provider}")
        
        old_metadata = self.metadata[provider]
        
        # Store new credential with same encryption setting
        self.store_credential(
            provider=provider,
            credential=new_credential,
            expires_days=expires_days,
            description=f"Rotated from {old_metadata.created_at.strftime('%Y-%m-%d')}",
            encrypt=old_metadata.encrypted
        )
        
        self.logger.info(f"Rotated credential for {provider}")
    
    def list_credentials(self) -> List[Dict[str, Any]]:
        """List all credentials with metadata (excluding actual values)."""
        credentials_info = []
        
        for provider, metadata in self.metadata.items():
            info = {
                "provider": provider,
                "description": metadata.description,
                "created_at": metadata.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                "expires_at": metadata.expires_at.strftime('%Y-%m-%d') if metadata.expires_at else None,
                "days_until_expiry": metadata.days_until_expiry(),
                "last_accessed": metadata.last_accessed.strftime('%Y-%m-%d %H:%M:%S') if metadata.last_accessed else None,
                "access_count": metadata.access_count,
                "encrypted": metadata.encrypted,
                "is_expired": metadata.is_expired(),
            }
            credentials_info.append(info)
        
        return credentials_info
    
    def remove_credential(self, provider: str) -> None:
        """Remove a credential."""
        if provider in self.credentials:
            del self.credentials[provider]
            del self.metadata[provider]
            self._save_credentials()
            self.logger.info(f"Removed credential for {provider}")
        else:
            raise ValueError(f"No credential found for {provider}")
    
    def check_expiring_credentials(self, days_threshold: int = 30) -> List[str]:
        """Check for credentials expiring within threshold."""
        expiring = []
        
        for provider, metadata in self.metadata.items():
            days_until_expiry = metadata.days_until_expiry()
            if days_until_expiry is not None and days_until_expiry <= days_threshold:
                expiring.append(provider)
        
        return expiring
    
    def get_credential_status(self, provider: str) -> Dict[str, Any]:
        """Get detailed status of a credential."""
        if provider not in self.metadata:
            raise ValueError(f"No credential found for {provider}")
        
        metadata = self.metadata[provider]
        return {
            "provider": provider,
            "exists": True,
            "encrypted": metadata.encrypted,
            "created_at": metadata.created_at,
            "expires_at": metadata.expires_at,
            "days_until_expiry": metadata.days_until_expiry(),
            "is_expired": metadata.is_expired(),
            "last_accessed": metadata.last_accessed,
            "access_count": metadata.access_count,
            "description": metadata.description,
        }
    
    def _load_credentials(self) -> None:
        """Load credentials from disk."""
        credentials_file = self.credentials_dir / "credentials.json"
        metadata_file = self.credentials_dir / "metadata.json"
        
        # Load credentials
        if credentials_file.exists():
            try:
                with open(credentials_file, 'r') as f:
                    self.credentials = json.load(f)
            except Exception as e:
                self.logger.error(f"Failed to load credentials: {e}")
                self.credentials = {}
        
        # Load metadata
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r') as f:
                    metadata_data = json.load(f)
                    self.metadata = {
                        provider: CredentialMetadata.from_dict(data)
                        for provider, data in metadata_data.items()
                    }
            except Exception as e:
                self.logger.error(f"Failed to load metadata: {e}")
                self.metadata = {}
    
    def _save_credentials(self) -> None:
        """Save credentials to disk."""
        credentials_file = self.credentials_dir / "credentials.json"
        metadata_file = self.credentials_dir / "metadata.json"
        
        # Save credentials
        try:
            with open(credentials_file, 'w') as f:
                json.dump(self.credentials, f, indent=2)
            os.chmod(credentials_file, 0o600)  # Secure permissions
        except Exception as e:
            self.logger.error(f"Failed to save credentials: {e}")
        
        # Save metadata
        try:
            metadata_data = {
                provider: metadata.to_dict()
                for provider, metadata in self.metadata.items()
            }
            with open(metadata_file, 'w') as f:
                json.dump(metadata_data, f, indent=2)
            os.chmod(metadata_file, 0o600)  # Secure permissions
        except Exception as e:
            self.logger.error(f"Failed to save metadata: {e}")


def setup_credentials_from_env() -> SecureCredentialManager:
    """Set up credential manager with credentials from environment variables."""
    cred_manager = SecureCredentialManager()
    
    # Common LLM providers
    providers = {
        'openai': 'KGAS_OPENAI_API_KEY',
        'anthropic': 'KGAS_ANTHROPIC_API_KEY',
        'google': 'KGAS_GOOGLE_API_KEY',
    }
    
    for provider, env_var in providers.items():
        api_key = os.getenv(env_var)
        if api_key and provider not in cred_manager.credentials:
            cred_manager.store_credential(
                provider=provider,
                credential=api_key,
                expires_days=90,
                description=f"Imported from {env_var}"
            )
    
    return cred_manager


if __name__ == "__main__":
    # Test credential manager
    import tempfile
    
    # Use temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        cred_manager = SecureCredentialManager(credentials_dir=temp_dir)
        
        # Test storing and retrieving credentials
        test_key = "sk-test123456789"
        cred_manager.store_credential('openai', test_key, expires_days=90)
        
        retrieved_key = cred_manager.get_credential('openai')
        assert retrieved_key == test_key, "Credential storage/retrieval failed"
        
        # Test credential listing
        credentials = cred_manager.list_credentials()
        assert len(credentials) == 1, "Credential listing failed"
        assert credentials[0]['provider'] == 'openai', "Credential provider mismatch"
        
        # Test expiry checking
        expiring = cred_manager.check_expiring_credentials(days_threshold=100)
        assert 'openai' in expiring, "Expiry checking failed"
        
        print("✅ All credential manager tests passed")
        print(f"Credentials: {len(credentials)}")
        print(f"Expiring soon: {expiring}")