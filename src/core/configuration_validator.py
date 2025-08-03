from src.core.standard_config import get_database_uri
"""Configuration Validator

Validates configuration settings and ensures secure configuration
across all services and components.
"""

import os
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from .logging_config import get_logger
from .config_manager import get_config

logger = get_logger("core.configuration_validator")


@dataclass
class ConfigValidationResult:
    """Result of configuration validation"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    security_score: float
    recommendations: List[str]


class ConfigurationValidator:
    """Validates configuration for security and completeness"""
    
    def __init__(self):
        self.logger = get_logger("core.configuration_validator")
        
        # Required environment variables for production
        self.required_env_vars = {
            'NEO4J_URI': 'Neo4j database connection URI',
            'NEO4J_USER': 'Neo4j username', 
            'NEO4J_PASSWORD': 'Neo4j password',
            'OPENAI_API_KEY': 'OpenAI API key for embeddings',
            'KGAS_ENVIRONMENT': 'Application environment (development/production)'
        }
        
        # Optional but recommended environment variables
        self.recommended_env_vars = {
            'GOOGLE_API_KEY': 'Google API key for Gemini models',
            'ANTHROPIC_API_KEY': 'Anthropic API key for Claude models',
            'KGAS_PII_PASSWORD': 'PII encryption password',
            'KGAS_PII_SALT': 'PII encryption salt',
            'KGAS_LOG_LEVEL': 'Logging level',
            'KGAS_MAX_WORKERS': 'Maximum worker threads',
            'KGAS_ENCRYPTION_KEY': 'Application encryption key'
        }
        
        # Insecure default values that should be changed
        self.insecure_defaults = {
            'password', 'admin', 'test', 'default', '123456',
            'changeme', 'secret', 'password123', 'testpassword'
        }
        
    def validate_configuration(self) -> ConfigValidationResult:
        """Validate current configuration
        
        Returns:
            Configuration validation result
        """
        errors = []
        warnings = []
        recommendations = []
        
        # Validate environment variables
        env_errors, env_warnings = self._validate_environment_variables()
        errors.extend(env_errors)
        warnings.extend(env_warnings)
        
        # Validate configuration manager settings
        config_errors, config_warnings = self._validate_config_manager()
        errors.extend(config_errors)
        warnings.extend(config_warnings)
        
        # Validate security settings
        security_errors, security_warnings = self._validate_security_settings()
        errors.extend(security_errors)
        warnings.extend(security_warnings)
        
        # Validate database connections
        db_errors, db_warnings = self._validate_database_configuration()
        errors.extend(db_errors)
        warnings.extend(db_warnings)
        
        # Validate API configurations
        api_errors, api_warnings = self._validate_api_configuration()
        errors.extend(api_errors)
        warnings.extend(api_warnings)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(errors, warnings)
        
        # Calculate security score
        security_score = self._calculate_security_score(errors, warnings)
        
        is_valid = len(errors) == 0
        
        return ConfigValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            security_score=security_score,
            recommendations=recommendations
        )
        
    def _validate_environment_variables(self) -> Tuple[List[str], List[str]]:
        """Validate environment variables"""
        errors = []
        warnings = []
        
        # Check required variables
        for var, description in self.required_env_vars.items():
            value = os.getenv(var)
            if not value:
                errors.append(f"Missing required environment variable: {var} ({description})")
            elif self._is_insecure_value(value):
                errors.append(f"Insecure value for {var}: appears to be a default/test value")
                
        # Check recommended variables
        for var, description in self.recommended_env_vars.items():
            value = os.getenv(var)
            if not value:
                warnings.append(f"Missing recommended environment variable: {var} ({description})")
            elif self._is_insecure_value(value):
                warnings.append(f"Insecure value for {var}: appears to be a default/test value")
                
        return errors, warnings
        
    def _validate_config_manager(self) -> Tuple[List[str], List[str]]:
        """Validate configuration manager settings"""
        errors = []
        warnings = []
        
        try:
            config = get_config()
            
            # Validate Neo4j configuration
            neo4j_config = config.neo4j
            if neo4j_config.password in self.insecure_defaults:
                errors.append("Neo4j password appears to be a default/test value")
                
            if neo4j_config.uri == get_database_uri() and os.getenv('KGAS_ENVIRONMENT') == 'production':
                warnings.append("Using localhost Neo4j URI in production environment")
                
            # Validate API configuration
            api_config = config.api
            if not api_config.openai_api_key and not os.getenv('OPENAI_API_KEY'):
                errors.append("OpenAI API key not configured")
                
            if api_config.timeout < 10:
                warnings.append("API timeout is very low, may cause failures")
                
            # Validate system configuration
            system_config = config.system
            if system_config.environment == 'development' and os.getenv('KGAS_ENVIRONMENT') == 'production':
                warnings.append("System environment mismatch with KGAS_ENVIRONMENT")
                
        except Exception as e:
            errors.append(f"Error validating configuration manager: {e}")
            
        return errors, warnings
        
    def _validate_security_settings(self) -> Tuple[List[str], List[str]]:
        """Validate security-related settings"""
        errors = []
        warnings = []
        
        # Check for encryption configuration
        encryption_key = os.getenv('KGAS_ENCRYPTION_KEY')
        if not encryption_key:
            warnings.append("No encryption key configured (KGAS_ENCRYPTION_KEY)")
        elif len(encryption_key) < 32:
            errors.append("Encryption key is too short (minimum 32 characters)")
            
        # Check JWT secret
        jwt_secret = os.getenv('KGAS_JWT_SECRET')
        if not jwt_secret:
            warnings.append("No JWT secret configured (KGAS_JWT_SECRET)")
        elif len(jwt_secret) < 32:
            warnings.append("JWT secret is too short (recommended minimum 32 characters)")
            
        # Check environment setting
        environment = os.getenv('KGAS_ENVIRONMENT', 'development')
        if environment == 'production':
            # More strict validation for production
            debug_mode = os.getenv('KGAS_DEBUG', 'false').lower()
            if debug_mode == 'true':
                errors.append("Debug mode is enabled in production environment")
                
            log_level = os.getenv('KGAS_LOG_LEVEL', 'INFO')
            if log_level.upper() == 'DEBUG':
                warnings.append("Debug logging enabled in production environment")
                
        return errors, warnings
        
    def _validate_database_configuration(self) -> Tuple[List[str], List[str]]:
        """Validate database configuration"""
        errors = []
        warnings = []
        
        try:
            config = get_config()
            neo4j_config = config.neo4j
            
            # Check connection settings
            if neo4j_config.max_connection_pool_size < 5:
                warnings.append("Neo4j connection pool size is very small")
            elif neo4j_config.max_connection_pool_size > 100:
                warnings.append("Neo4j connection pool size is very large")
                
            if neo4j_config.connection_acquisition_timeout < 5:
                warnings.append("Neo4j connection timeout is very short")
                
            # Validate URI format
            if not neo4j_config.uri.startswith(('bolt://', 'neo4j://', 'bolt+s://', 'neo4j+s://')):
                errors.append("Invalid Neo4j URI format")
                
        except Exception as e:
            errors.append(f"Error validating database configuration: {e}")
            
        return errors, warnings
        
    def _validate_api_configuration(self) -> Tuple[List[str], List[str]]:
        """Validate API configuration"""
        errors = []
        warnings = []
        
        try:
            config = get_config()
            api_config = config.api
            
            # Validate API keys
            api_keys = {
                'OpenAI': api_config.openai_api_key or os.getenv('OPENAI_API_KEY'),
                'Google': api_config.google_api_key or os.getenv('GOOGLE_API_KEY'),
                'Anthropic': api_config.anthropic_api_key or os.getenv('ANTHROPIC_API_KEY')
            }
            
            active_keys = sum(1 for key in api_keys.values() if key)
            if active_keys == 0:
                errors.append("No API keys configured - at least one is required")
            elif active_keys == 1:
                warnings.append("Only one API key configured - consider configuring backup APIs")
                
            # Validate API key formats
            for api_name, key in api_keys.items():
                if key:
                    if not self._validate_api_key_format(api_name, key):
                        warnings.append(f"{api_name} API key format appears invalid")
                        
            # Validate timeout and retry settings
            if api_config.timeout > 60:
                warnings.append("API timeout is very high")
            elif api_config.timeout < 5:
                warnings.append("API timeout is very low")
                
            if api_config.max_retries > 5:
                warnings.append("Maximum retries is very high")
            elif api_config.max_retries < 1:
                warnings.append("Maximum retries is too low")
                
        except Exception as e:
            errors.append(f"Error validating API configuration: {e}")
            
        return errors, warnings
        
    def _is_insecure_value(self, value: str) -> bool:
        """Check if a value appears to be insecure/default"""
        if not value:
            return True
            
        value_lower = value.lower()
        return any(default in value_lower for default in self.insecure_defaults)
        
    def _validate_api_key_format(self, api_name: str, key: str) -> bool:
        """Validate API key format"""
        if api_name == 'OpenAI':
            return key.startswith('sk-') and len(key) > 20
        elif api_name == 'Google':
            return len(key) > 30 and re.match(r'^[A-Za-z0-9_-]+$', key)
        elif api_name == 'Anthropic':
            return key.startswith('sk-ant-') and len(key) > 20
        return len(key) > 10  # Basic length check for unknown APIs
        
    def _generate_recommendations(self, errors: List[str], warnings: List[str]) -> List[str]:
        """Generate configuration recommendations"""
        recommendations = []
        
        if errors:
            recommendations.append("Fix all configuration errors before deploying to production")
            
        if any("environment variable" in error.lower() for error in errors):
            recommendations.append("Create .env file from .env.template and set all required variables")
            
        if any("api key" in error.lower() for error in errors):
            recommendations.append("Obtain and configure API keys for external services")
            
        if any("password" in error.lower() for error in errors):
            recommendations.append("Use strong, unique passwords for all services")
            
        if any("encryption" in warning.lower() for warning in warnings):
            recommendations.append("Configure encryption keys for data protection")
            
        if any("production" in warning.lower() for warning in warnings):
            recommendations.append("Review production-specific configuration settings")
            
        return recommendations
        
    def _calculate_security_score(self, errors: List[str], warnings: List[str]) -> float:
        """Calculate security score based on configuration issues"""
        total_issues = len(errors) + len(warnings)
        
        if total_issues == 0:
            return 100.0
            
        # Weight errors more heavily than warnings
        error_weight = 10
        warning_weight = 3
        
        total_weight = len(errors) * error_weight + len(warnings) * warning_weight
        max_weight = total_issues * error_weight  # If all were errors
        
        score = max(0, 100 - (total_weight / max_weight * 100))
        return round(score, 2)
        
    def generate_secure_config(self) -> str:
        """Generate a secure configuration template
        
        Returns:
            String containing secure configuration template
        """
        import secrets
        import base64
        
        # Generate secure random values
        encryption_key = base64.b64encode(secrets.token_bytes(32)).decode()
        jwt_secret = secrets.token_urlsafe(32)
        pii_salt = secrets.token_hex(16)
        
        template = f"""# Secure KGAS Configuration
# Generated on {__import__('datetime').datetime.now().isoformat()}

# Database Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=CHANGE_THIS_SECURE_PASSWORD

# API Keys (obtain from respective providers)
OPENAI_API_KEY=sk-your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
ANTHROPIC_API_KEY=sk-ant-your_anthropic_api_key_here

# Security Configuration
KGAS_ENCRYPTION_KEY={encryption_key}
KGAS_JWT_SECRET={jwt_secret}
KGAS_PII_SALT={pii_salt}

# Application Configuration
KGAS_ENVIRONMENT=production
KGAS_LOG_LEVEL=INFO
KGAS_DEBUG=false
KGAS_MAX_WORKERS=4

# Monitoring
KGAS_METRICS_ENABLED=true
KGAS_HEALTH_CHECK_INTERVAL=60
KGAS_BACKUP_ENABLED=true
"""
        
        return template
        
    def validate_and_report(self) -> Dict[str, Any]:
        """Validate configuration and return comprehensive report
        
        Returns:
            Dictionary with validation results and recommendations
        """
        result = self.validate_configuration()
        
        report = {
            'validation_status': 'PASS' if result.is_valid else 'FAIL',
            'security_score': result.security_score,
            'total_errors': len(result.errors),
            'total_warnings': len(result.warnings),
            'errors': result.errors,
            'warnings': result.warnings,
            'recommendations': result.recommendations,
            'next_steps': self._get_next_steps(result)
        }
        
        return report
        
    def _get_next_steps(self, result: ConfigValidationResult) -> List[str]:
        """Get next steps based on validation results"""
        next_steps = []
        
        if not result.is_valid:
            next_steps.append("1. Fix all configuration errors listed above")
            
        if result.security_score < 80:
            next_steps.append("2. Address security warnings to improve security score")
            
        if any("environment variable" in error for error in result.errors):
            next_steps.append("3. Set up environment variables using .env.template")
            
        if any("api key" in error.lower() for error in result.errors):
            next_steps.append("4. Obtain and configure API keys for external services")
            
        next_steps.append("5. Run configuration validation again to verify fixes")
        
        return next_steps


def validate_current_configuration() -> Dict[str, Any]:
    """Validate current configuration and return report
    
    Returns:
        Configuration validation report
    """
    validator = ConfigurationValidator()
    return validator.validate_and_report()