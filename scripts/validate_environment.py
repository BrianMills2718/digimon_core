#!/usr/bin/env python3
"""
Environment Configuration Validation Script

Validates environment variables for KGAS production deployment.
Checks for required variables, validates formats, and provides recommendations.
"""

import os
import re
import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from urllib.parse import urlparse


class EnvironmentValidator:
    """Comprehensive environment variable validation for KGAS."""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.recommendations = []
        self.validation_results = {}
        
    def validate_all(self) -> Dict[str, Any]:
        """Run comprehensive validation of all environment variables."""
        print("🔧 KGAS Environment Configuration Validation")
        print("=" * 60)
        
        start_time = datetime.now()
        
        # Core validation categories
        self._validate_database_config()
        self._validate_api_keys()
        self._validate_system_config()
        self._validate_security_config()
        self._validate_monitoring_config()
        self._validate_production_config()
        self._validate_file_paths()
        self._validate_network_config()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Compile results
        results = {
            "validation_timestamp": start_time.isoformat(),
            "validation_duration": duration,
            "total_errors": len(self.errors),
            "total_warnings": len(self.warnings),
            "total_recommendations": len(self.recommendations),
            "validation_passed": len(self.errors) == 0,
            "production_ready": self._assess_production_readiness(),
            "errors": self.errors,
            "warnings": self.warnings,
            "recommendations": self.recommendations,
            "category_results": self.validation_results
        }
        
        self._print_summary(results)
        return results
    
    def _validate_database_config(self) -> None:
        """Validate database configuration."""
        print("\n📊 Database Configuration")
        print("-" * 30)
        
        results = {
            "neo4j_configured": False,
            "redis_configured": False,
            "vector_db_configured": False,
            "connection_pools_configured": False
        }
        
        # Neo4j validation
        neo4j_uri = os.getenv('NEO4J_URI')
        neo4j_user = os.getenv('NEO4J_USER', os.getenv('NEO4J_USERNAME'))
        neo4j_password = os.getenv('NEO4J_PASSWORD')
        
        if not neo4j_uri:
            self.errors.append("NEO4J_URI is required")
        elif not neo4j_uri.startswith(('bolt://', 'neo4j://', 'bolt+s://', 'neo4j+s://')):
            self.errors.append("NEO4J_URI must use bolt:// or neo4j:// protocol")
        else:
            results["neo4j_configured"] = True
            print(f"✅ Neo4j URI: {neo4j_uri}")
        
        if not neo4j_user:
            self.errors.append("NEO4J_USER or NEO4J_USERNAME is required")
        
        if not neo4j_password:
            self.errors.append("NEO4J_PASSWORD is required")
        elif neo4j_password == 'password':
            self.warnings.append("NEO4J_PASSWORD uses default value - change for production")
        
        # Connection pool validation
        max_pool_size = os.getenv('NEO4J_MAX_POOL_SIZE', '50')
        try:
            pool_size = int(max_pool_size)
            if pool_size < 1:
                self.warnings.append("NEO4J_MAX_POOL_SIZE should be at least 1")
            elif pool_size > 100:
                self.warnings.append("NEO4J_MAX_POOL_SIZE > 100 may cause resource issues")
            else:
                results["connection_pools_configured"] = True
        except ValueError:
            self.errors.append("NEO4J_MAX_POOL_SIZE must be a valid integer")
        
        # Redis validation (optional but recommended)
        redis_host = os.getenv('REDIS_HOST')
        if redis_host:
            redis_port = os.getenv('REDIS_PORT', '6379')
            try:
                port = int(redis_port)
                if 1 <= port <= 65535:
                    results["redis_configured"] = True
                    print(f"✅ Redis: {redis_host}:{port}")
                else:
                    self.errors.append("REDIS_PORT must be between 1 and 65535")
            except ValueError:
                self.errors.append("REDIS_PORT must be a valid integer")
        else:
            self.recommendations.append("Consider configuring Redis for caching (REDIS_HOST)")
        
        self.validation_results["database"] = results
    
    def _validate_api_keys(self) -> None:
        """Validate API keys and external service configuration."""
        print("\n🔑 API Keys & External Services")
        print("-" * 35)
        
        results = {
            "openai_configured": False,
            "anthropic_configured": False,
            "google_configured": False,
            "keys_secure": True
        }
        
        # OpenAI API
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            if openai_key.startswith('sk-') and len(openai_key) > 20:
                results["openai_configured"] = True
                print("✅ OpenAI API key configured")
            else:
                self.errors.append("OPENAI_API_KEY format appears invalid")
        else:
            self.warnings.append("OPENAI_API_KEY not configured - embedding features may not work")
        
        # Anthropic API
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        if anthropic_key:
            if anthropic_key.startswith('sk-ant-') and len(anthropic_key) > 30:
                results["anthropic_configured"] = True
                print("✅ Anthropic API key configured")
            else:
                self.errors.append("ANTHROPIC_API_KEY format appears invalid")
        else:
            self.warnings.append("ANTHROPIC_API_KEY not configured")
        
        # Google API
        google_key = os.getenv('GOOGLE_API_KEY')
        if google_key:
            if len(google_key) > 20:
                results["google_configured"] = True
                print("✅ Google API key configured")
            else:
                self.errors.append("GOOGLE_API_KEY appears too short")
        else:
            self.warnings.append("GOOGLE_API_KEY not configured")
        
        # Model configuration
        openai_model = os.getenv('OPENAI_MODEL', 'text-embedding-3-small')
        gemini_model = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash-exp')
        
        print(f"📋 OpenAI Model: {openai_model}")
        print(f"📋 Gemini Model: {gemini_model}")
        
        # API configuration
        api_timeout = os.getenv('API_TIMEOUT_SECONDS', '30')
        api_retries = os.getenv('API_RETRY_ATTEMPTS', '3')
        
        try:
            timeout = int(api_timeout)
            if timeout < 5:
                self.warnings.append("API_TIMEOUT_SECONDS < 5 may cause failures")
            elif timeout > 300:
                self.warnings.append("API_TIMEOUT_SECONDS > 300 may cause long waits")
        except ValueError:
            self.errors.append("API_TIMEOUT_SECONDS must be a valid integer")
        
        try:
            retries = int(api_retries)
            if retries < 1:
                self.warnings.append("API_RETRY_ATTEMPTS < 1 disables retries")
            elif retries > 10:
                self.warnings.append("API_RETRY_ATTEMPTS > 10 may cause long delays")
        except ValueError:
            self.errors.append("API_RETRY_ATTEMPTS must be a valid integer")
        
        self.validation_results["api_keys"] = results
    
    def _validate_system_config(self) -> None:
        """Validate system-level configuration."""
        print("\n⚙️ System Configuration")
        print("-" * 25)
        
        results = {
            "logging_configured": False,
            "performance_configured": False,
            "environment_set": False
        }
        
        # Environment
        environment = os.getenv('ENVIRONMENT', 'development')
        graphrag_mode = os.getenv('GRAPHRAG_MODE', 'development')
        debug = os.getenv('DEBUG', 'false').lower()
        
        results["environment_set"] = bool(environment)
        print(f"🏷️ Environment: {environment}")
        print(f"🏷️ GRAPHRAG Mode: {graphrag_mode}")
        print(f"🏷️ Debug Mode: {debug}")
        
        if environment == 'production' and debug == 'true':
            self.warnings.append("DEBUG=true in production environment")
        
        # Logging
        log_level = os.getenv('LOG_LEVEL', 'INFO')
        log_format = os.getenv('LOG_FORMAT', 'json')
        
        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if log_level.upper() in valid_log_levels:
            results["logging_configured"] = True
            print(f"📝 Log Level: {log_level}")
        else:
            self.errors.append(f"LOG_LEVEL must be one of: {', '.join(valid_log_levels)}")
        
        # Performance
        max_workers = os.getenv('MAX_WORKERS', '4')
        try:
            workers = int(max_workers)
            if 1 <= workers <= 32:
                results["performance_configured"] = True
                print(f"⚡ Max Workers: {workers}")
            else:
                self.warnings.append("MAX_WORKERS should be between 1 and 32")
        except ValueError:
            self.errors.append("MAX_WORKERS must be a valid integer")
        
        self.validation_results["system"] = results
    
    def _validate_security_config(self) -> None:
        """Validate security configuration."""
        print("\n🔒 Security Configuration")
        print("-" * 30)
        
        results = {
            "encryption_enabled": False,
            "jwt_configured": False,
            "passwords_secure": True,
            "ssl_configured": False
        }
        
        # Encryption
        encryption_enabled = os.getenv('ENCRYPTION_ENABLED', 'true').lower() == 'true'
        results["encryption_enabled"] = encryption_enabled
        
        if not encryption_enabled:
            self.warnings.append("ENCRYPTION_ENABLED=false - consider enabling for production")
        else:
            print("✅ Encryption enabled")
        
        # JWT Secret
        jwt_secret = os.getenv('JWT_SECRET_KEY', os.getenv('JWT_SECRET'))
        if jwt_secret:
            if len(jwt_secret) >= 32:
                results["jwt_configured"] = True
                print("✅ JWT secret configured")
            else:
                self.errors.append("JWT_SECRET_KEY should be at least 32 characters")
                results["passwords_secure"] = False
        else:
            self.warnings.append("JWT_SECRET_KEY not configured")
        
        # Secret Key
        secret_key = os.getenv('SECRET_KEY')
        if secret_key:
            if len(secret_key) >= 32:
                print("✅ Secret key configured")
            else:
                self.errors.append("SECRET_KEY should be at least 32 characters")
                results["passwords_secure"] = False
        else:
            self.warnings.append("SECRET_KEY not configured")
        
        # Password requirements
        password_min_length = os.getenv('PASSWORD_MIN_LENGTH', '12')
        try:
            min_length = int(password_min_length)
            if min_length < 8:
                self.warnings.append("PASSWORD_MIN_LENGTH < 8 is not secure")
        except ValueError:
            self.errors.append("PASSWORD_MIN_LENGTH must be a valid integer")
        
        # SSL/TLS
        ssl_enabled = os.getenv('SSL_ENABLED', 'false').lower() == 'true'
        if ssl_enabled:
            ssl_cert = os.getenv('SSL_CERT_PATH')
            ssl_key = os.getenv('SSL_KEY_PATH')
            if ssl_cert and ssl_key:
                results["ssl_configured"] = True
                print("✅ SSL/TLS configured")
            else:
                self.errors.append("SSL_ENABLED=true but SSL_CERT_PATH or SSL_KEY_PATH missing")
        else:
            self.recommendations.append("Consider enabling SSL/TLS for production (SSL_ENABLED=true)")
        
        self.validation_results["security"] = results
    
    def _validate_monitoring_config(self) -> None:
        """Validate monitoring and observability configuration."""
        print("\n📊 Monitoring Configuration")
        print("-" * 32)
        
        results = {
            "metrics_enabled": False,
            "health_checks_enabled": False,
            "alerting_configured": False,
            "tracing_configured": False
        }
        
        # Metrics
        metrics_enabled = os.getenv('METRICS_ENABLED', 'true').lower() == 'true'
        results["metrics_enabled"] = metrics_enabled
        
        if metrics_enabled:
            metrics_port = os.getenv('METRICS_PORT', '8001')
            try:
                port = int(metrics_port)
                if 1024 <= port <= 65535:
                    print(f"✅ Prometheus metrics on port {port}")
                else:
                    self.warnings.append("METRICS_PORT should be between 1024 and 65535")
            except ValueError:
                self.errors.append("METRICS_PORT must be a valid integer")
        else:
            self.warnings.append("METRICS_ENABLED=false - monitoring data will be limited")
        
        # Health checks
        health_enabled = os.getenv('HEALTH_CHECKS_ENABLED', 'true').lower() == 'true'
        results["health_checks_enabled"] = health_enabled
        
        if health_enabled:
            health_interval = os.getenv('HEALTH_CHECK_INTERVAL', '60')
            try:
                interval = int(health_interval)
                if 10 <= interval <= 300:
                    print(f"✅ Health checks every {interval}s")
                else:
                    self.warnings.append("HEALTH_CHECK_INTERVAL should be between 10 and 300 seconds")
            except ValueError:
                self.errors.append("HEALTH_CHECK_INTERVAL must be a valid integer")
        
        # Alerting
        email_server = os.getenv('EMAIL_SMTP_SERVER')
        slack_webhook = os.getenv('SLACK_WEBHOOK_URL')
        webhook_url = os.getenv('WEBHOOK_URL')
        
        if email_server or slack_webhook or webhook_url:
            results["alerting_configured"] = True
            print("✅ Alerting configured")
        else:
            self.recommendations.append("Consider configuring alerting (email, Slack, or webhook)")
        
        # Tracing
        tracing_enabled = os.getenv('TRACING_ENABLED', 'false').lower() == 'true'
        if tracing_enabled:
            jaeger_endpoint = os.getenv('JAEGER_ENDPOINT')
            if jaeger_endpoint:
                results["tracing_configured"] = True
                print("✅ Distributed tracing configured")
            else:
                self.errors.append("TRACING_ENABLED=true but JAEGER_ENDPOINT not configured")
        
        self.validation_results["monitoring"] = results
    
    def _validate_production_config(self) -> None:
        """Validate production-specific configuration."""
        print("\n🚀 Production Configuration")
        print("-" * 31)
        
        results = {
            "production_mode": False,
            "backup_configured": False,
            "scaling_configured": False,
            "security_hardened": False
        }
        
        environment = os.getenv('ENVIRONMENT', 'development')
        results["production_mode"] = environment.lower() == 'production'
        
        if results["production_mode"]:
            print("🚀 Production mode enabled")
            
            # Backup configuration
            backup_enabled = os.getenv('BACKUP_ENABLED', 'true').lower() == 'true'
            if backup_enabled:
                backup_schedule = os.getenv('BACKUP_SCHEDULE')
                backup_path = os.getenv('BACKUP_PATH', 'backups/')
                if backup_schedule and backup_path:
                    results["backup_configured"] = True
                    print("✅ Backup configured")
                else:
                    self.warnings.append("BACKUP_ENABLED=true but schedule or path not configured")
            else:
                self.warnings.append("BACKUP_ENABLED=false in production")
            
            # Security hardening checks
            hardening_enabled = os.getenv('SECURITY_HARDENING_ENABLED', 'true').lower() == 'true'
            rate_limiting = os.getenv('RATE_LIMITING_ENABLED', 'true').lower() == 'true'
            audit_logging = os.getenv('AUDIT_LOGGING_ENABLED', 'true').lower() == 'true'
            
            if hardening_enabled and rate_limiting and audit_logging:
                results["security_hardened"] = True
                print("✅ Security hardening enabled")
            else:
                self.warnings.append("Some security hardening features disabled in production")
            
            # Auto-scaling
            auto_scaling = os.getenv('AUTO_SCALING_ENABLED', 'false').lower() == 'true'
            if auto_scaling:
                min_replicas = os.getenv('MIN_REPLICAS', '1')
                max_replicas = os.getenv('MAX_REPLICAS', '10')
                try:
                    min_r = int(min_replicas)
                    max_r = int(max_replicas)
                    if min_r >= 1 and max_r > min_r:
                        results["scaling_configured"] = True
                        print(f"✅ Auto-scaling: {min_r}-{max_r} replicas")
                    else:
                        self.errors.append("Invalid auto-scaling replica configuration")
                except ValueError:
                    self.errors.append("MIN_REPLICAS and MAX_REPLICAS must be valid integers")
        else:
            print("🔧 Development mode")
        
        self.validation_results["production"] = results
    
    def _validate_file_paths(self) -> None:
        """Validate file paths and directory configuration."""
        print("\n📁 File Paths & Directories")
        print("-" * 30)
        
        results = {
            "data_dirs_exist": False,
            "log_dirs_configured": False,
            "backup_dirs_configured": False
        }
        
        # Data directories
        data_dir = Path(os.getenv('DATA_DIR', './data'))
        storage_dir = Path(os.getenv('STORAGE_DIR', './storage'))
        workflow_dir = Path(os.getenv('WORKFLOW_STORAGE_DIR', './data/workflows'))
        
        if data_dir.exists() or storage_dir.exists():
            results["data_dirs_exist"] = True
            print(f"✅ Data directories configured")
        else:
            self.warnings.append("Data directories do not exist - will be created on startup")
        
        # Log directory
        log_dir = Path(os.getenv('LOG_DIR', './logs'))
        if log_dir.exists():
            results["log_dirs_configured"] = True
            print(f"✅ Log directory: {log_dir}")
        else:
            self.recommendations.append(f"Create log directory: {log_dir}")
        
        # Backup directory
        backup_dir = Path(os.getenv('BACKUP_DIR', './backups'))
        if backup_dir.exists():
            results["backup_dirs_configured"] = True
            print(f"✅ Backup directory: {backup_dir}")
        else:
            self.recommendations.append(f"Create backup directory: {backup_dir}")
        
        self.validation_results["file_paths"] = results
    
    def _validate_network_config(self) -> None:
        """Validate network and connectivity configuration."""
        print("\n🌐 Network Configuration")
        print("-" * 26)
        
        results = {
            "host_configured": False,
            "port_configured": False,
            "load_balancer_configured": False
        }
        
        # Host and port
        host = os.getenv('HOST', '0.0.0.0')
        port = os.getenv('PORT', '8000')
        
        results["host_configured"] = bool(host)
        
        try:
            port_num = int(port)
            if 1024 <= port_num <= 65535:
                results["port_configured"] = True
                print(f"✅ Server: {host}:{port}")
            else:
                self.warnings.append("PORT should be between 1024 and 65535")
        except ValueError:
            self.errors.append("PORT must be a valid integer")
        
        # Load balancer
        lb_enabled = os.getenv('LOAD_BALANCER_ENABLED', 'false').lower() == 'true'
        if lb_enabled:
            lb_algorithm = os.getenv('LOAD_BALANCER_ALGORITHM', 'round_robin')
            results["load_balancer_configured"] = True
            print(f"✅ Load balancer: {lb_algorithm}")
        
        # Rate limiting
        rate_limit = os.getenv('RATE_LIMIT_REQUESTS', '100')
        rate_window = os.getenv('RATE_LIMIT_WINDOW', '3600')
        
        try:
            requests = int(rate_limit)
            window = int(rate_window)
            print(f"📋 Rate limit: {requests} requests per {window}s")
        except ValueError:
            self.errors.append("RATE_LIMIT_REQUESTS and RATE_LIMIT_WINDOW must be valid integers")
        
        self.validation_results["network"] = results
    
    def _assess_production_readiness(self) -> Dict[str, Any]:
        """Assess overall production readiness."""
        readiness = {
            "ready": True,
            "score": 0,
            "max_score": 0,
            "critical_issues": [],
            "missing_requirements": []
        }
        
        # Critical requirements for production
        critical_checks = [
            ("NEO4J_PASSWORD", "Database password configured"),
            ("ENCRYPTION_ENABLED", "Encryption enabled"),
            ("BACKUP_ENABLED", "Backup enabled"),
            ("METRICS_ENABLED", "Monitoring enabled"),
            ("JWT_SECRET_KEY", "JWT secret configured")
        ]
        
        for env_var, description in critical_checks:
            readiness["max_score"] += 1
            value = os.getenv(env_var)
            
            if env_var == "NEO4J_PASSWORD":
                if value and value != "password":
                    readiness["score"] += 1
                else:
                    readiness["critical_issues"].append(description)
                    readiness["ready"] = False
            elif env_var in ["ENCRYPTION_ENABLED", "BACKUP_ENABLED", "METRICS_ENABLED"]:
                if value and value.lower() == "true":
                    readiness["score"] += 1
                else:
                    readiness["missing_requirements"].append(description)
            elif env_var == "JWT_SECRET_KEY":
                if value and len(value) >= 32:
                    readiness["score"] += 1
                else:
                    readiness["critical_issues"].append(description)
                    readiness["ready"] = False
        
        readiness["percentage"] = (readiness["score"] / readiness["max_score"]) * 100
        return readiness
    
    def _print_summary(self, results: Dict[str, Any]) -> None:
        """Print validation summary."""
        print(f"\n{'='*60}")
        print("📋 VALIDATION SUMMARY")
        print(f"{'='*60}")
        
        print(f"⏱️  Duration: {results['validation_duration']:.2f}s")
        print(f"✅ Validation: {'PASSED' if results['validation_passed'] else 'FAILED'}")
        print(f"🚀 Production Ready: {'YES' if results['production_ready']['ready'] else 'NO'}")
        print(f"📊 Readiness Score: {results['production_ready']['score']}/{results['production_ready']['max_score']} ({results['production_ready']['percentage']:.1f}%)")
        
        if results["total_errors"] > 0:
            print(f"\n❌ ERRORS ({results['total_errors']}):")
            for error in results["errors"]:
                print(f"   • {error}")
        
        if results["total_warnings"] > 0:
            print(f"\n⚠️  WARNINGS ({results['total_warnings']}):")
            for warning in results["warnings"]:
                print(f"   • {warning}")
        
        if results["total_recommendations"] > 0:
            print(f"\n💡 RECOMMENDATIONS ({results['total_recommendations']}):")
            for rec in results["recommendations"]:
                print(f"   • {rec}")
        
        # Production readiness details
        if not results['production_ready']['ready']:
            if results['production_ready']['critical_issues']:
                print(f"\n🚨 CRITICAL ISSUES:")
                for issue in results['production_ready']['critical_issues']:
                    print(f"   • {issue}")
        
        print(f"\n📊 CATEGORY BREAKDOWN:")
        for category, category_results in results["category_results"].items():
            configured_count = sum(1 for v in category_results.values() if v is True)
            total_count = len(category_results)
            print(f"   {category.title()}: {configured_count}/{total_count} configured")


def main():
    """Main entry point for environment validation."""
    validator = EnvironmentValidator()
    results = validator.validate_all()
    
    # Write results to file
    results_file = Path("environment_validation_results.json")
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to: {results_file}")
    
    # Exit with appropriate code
    exit_code = 0 if results["validation_passed"] else 1
    sys.exit(exit_code)


if __name__ == "__main__":
    main()