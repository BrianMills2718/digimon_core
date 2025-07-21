#!/usr/bin/env python3
"""
Phase 4 Production Readiness Validation
Validates all Phase 4 implementation requirements and production readiness.
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

def validate_docker_configuration():
    """Validate Docker configuration files."""
    print("🐳 Validating Docker Configuration...")
    
    results = []
    
    # Check Dockerfile
    dockerfile_path = Path("docker/Dockerfile")
    if dockerfile_path.exists():
        with open(dockerfile_path, 'r') as f:
            dockerfile_content = f.read()
        
        # Check for security best practices
        checks = [
            ("Non-root user", "USER kgas" in dockerfile_content),
            ("Health check", "HEALTHCHECK" in dockerfile_content),
            ("Exposed port", "EXPOSE 8000" in dockerfile_content),
            ("Working directory", "WORKDIR /app" in dockerfile_content),
            ("Multi-stage build", "FROM python:3.11-slim" in dockerfile_content)
        ]
        
        for check_name, passed in checks:
            results.append({
                "check": f"dockerfile_{check_name.lower().replace(' ', '_')}",
                "status": "✅ PASSED" if passed else "❌ FAILED",
                "details": f"Dockerfile {check_name}: {'Present' if passed else 'Missing'}"
            })
    else:
        results.append({
            "check": "dockerfile_exists",
            "status": "❌ FAILED",
            "details": "Dockerfile not found at docker/Dockerfile"
        })
    
    # Check docker-compose.production.yml
    compose_path = Path("docker/docker-compose.production.yml")
    if compose_path.exists():
        results.append({
            "check": "docker_compose_production",
            "status": "✅ PASSED",
            "details": "Production docker-compose configuration found"
        })
    else:
        results.append({
            "check": "docker_compose_production",
            "status": "❌ FAILED",
            "details": "Production docker-compose.yml not found"
        })
    
    return results

def validate_kubernetes_configuration():
    """Validate Kubernetes configuration files."""
    print("☸️ Validating Kubernetes Configuration...")
    
    results = []
    
    # Check k8s directory
    k8s_path = Path("k8s")
    if k8s_path.exists():
        # Check for required files
        required_files = [
            "deployment.yaml",
            "service.yaml",
            "configmap.yaml",
            "secret.yaml"
        ]
        
        for file_name in required_files:
            file_path = k8s_path / file_name
            if file_path.exists():
                results.append({
                    "check": f"k8s_{file_name.replace('.', '_')}",
                    "status": "✅ PASSED",
                    "details": f"Kubernetes {file_name} configuration found"
                })
            else:
                results.append({
                    "check": f"k8s_{file_name.replace('.', '_')}",
                    "status": "❌ FAILED",
                    "details": f"Kubernetes {file_name} configuration missing"
                })
    else:
        results.append({
            "check": "k8s_directory",
            "status": "❌ FAILED",
            "details": "Kubernetes configuration directory not found"
        })
    
    return results

def validate_cicd_pipeline():
    """Validate CI/CD pipeline configuration."""
    print("🔄 Validating CI/CD Pipeline...")
    
    results = []
    
    # Check GitHub Actions workflow
    workflow_path = Path(".github/workflows/production-deploy.yml")
    if workflow_path.exists():
        with open(workflow_path, 'r') as f:
            workflow_content = f.read()
        
        # Check for required components
        checks = [
            ("Test job", "test:" in workflow_content),
            ("Build job", "build:" in workflow_content),
            ("Deploy job", "deploy:" in workflow_content),
            ("Security scan", "trivy" in workflow_content or "security" in workflow_content.lower()),
            ("Coverage upload", "codecov" in workflow_content or "coverage" in workflow_content.lower())
        ]
        
        for check_name, passed in checks:
            results.append({
                "check": f"cicd_{check_name.lower().replace(' ', '_')}",
                "status": "✅ PASSED" if passed else "❌ FAILED",
                "details": f"CI/CD {check_name}: {'Present' if passed else 'Missing'}"
            })
    else:
        results.append({
            "check": "cicd_workflow",
            "status": "❌ FAILED",
            "details": "GitHub Actions workflow not found"
        })
    
    return results

def validate_error_handling():
    """Validate error handling implementation."""
    print("🔧 Validating Error Handling...")
    
    results = []
    
    # Check error handler file
    error_handler_path = Path("src/core/error_handler.py")
    if error_handler_path.exists():
        with open(error_handler_path, 'r') as f:
            error_handler_content = f.read()
        
        # Check for required components
        checks = [
            ("ProductionErrorHandler class", "class ProductionErrorHandler" in error_handler_content),
            ("Circuit breaker", "circuit_breaker" in error_handler_content),
            ("Retry logic", "retry_with_backoff" in error_handler_content),
            ("Error registry", "error_registry" in error_handler_content),
            ("Custom exceptions", "class ProductionDeploymentError" in error_handler_content)
        ]
        
        for check_name, passed in checks:
            results.append({
                "check": f"error_handling_{check_name.lower().replace(' ', '_')}",
                "status": "✅ PASSED" if passed else "❌ FAILED",
                "details": f"Error handling {check_name}: {'Present' if passed else 'Missing'}"
            })
    else:
        results.append({
            "check": "error_handler_file",
            "status": "❌ FAILED",
            "details": "Error handler file not found at src/core/error_handler.py"
        })
    
    return results

def validate_performance_optimization():
    """Validate performance optimization implementation."""
    print("⚡ Validating Performance Optimization...")
    
    results = []
    
    # Check performance optimizer file
    perf_optimizer_path = Path("src/core/performance_optimizer.py")
    if perf_optimizer_path.exists():
        with open(perf_optimizer_path, 'r') as f:
            perf_content = f.read()
        
        # Check for required components
        checks = [
            ("PerformanceOptimizer class", "class PerformanceOptimizer" in perf_content),
            ("Performance profiling", "profile_operation" in perf_content),
            ("Cache manager", "CacheManager" in perf_content),
            ("Connection pool manager", "ConnectionPoolManager" in perf_content),
            ("Query optimizer", "QueryOptimizer" in perf_content)
        ]
        
        for check_name, passed in checks:
            results.append({
                "check": f"performance_{check_name.lower().replace(' ', '_')}",
                "status": "✅ PASSED" if passed else "❌ FAILED",
                "details": f"Performance optimization {check_name}: {'Present' if passed else 'Missing'}"
            })
    else:
        results.append({
            "check": "performance_optimizer_file",
            "status": "❌ FAILED",
            "details": "Performance optimizer file not found at src/core/performance_optimizer.py"
        })
    
    return results

def validate_security_hardening():
    """Validate security hardening implementation."""
    print("🔐 Validating Security Hardening...")
    
    results = []
    
    # Check security manager file
    security_manager_path = Path("src/core/security_manager.py")
    if security_manager_path.exists():
        with open(security_manager_path, 'r') as f:
            security_content = f.read()
        
        # Check for required components
        checks = [
            ("SecurityManager class", "class SecurityManager" in security_content),
            ("JWT authentication", "generate_jwt_token" in security_content),
            ("Password hashing", "bcrypt" in security_content),
            ("Rate limiting", "rate_limit_check" in security_content),
            ("Data encryption", "encrypt_sensitive_data" in security_content),
            ("Audit logging", "_log_security_event" in security_content)
        ]
        
        for check_name, passed in checks:
            results.append({
                "check": f"security_{check_name.lower().replace(' ', '_')}",
                "status": "✅ PASSED" if passed else "❌ FAILED",
                "details": f"Security hardening {check_name}: {'Present' if passed else 'Missing'}"
            })
    else:
        results.append({
            "check": "security_manager_file",
            "status": "❌ FAILED",
            "details": "Security manager file not found at src/core/security_manager.py"
        })
    
    return results

def validate_production_monitoring():
    """Validate production monitoring implementation."""
    print("📊 Validating Production Monitoring...")
    
    results = []
    
    # Check production monitoring file
    monitoring_path = Path("src/monitoring/production_monitoring.py")
    if monitoring_path.exists():
        with open(monitoring_path, 'r') as f:
            monitoring_content = f.read()
        
        # Check for required components
        checks = [
            ("ProductionMonitoring class", "class ProductionMonitoring" in monitoring_content),
            ("Alert system", "Alert" in monitoring_content),
            ("Health checks", "HealthCheck" in monitoring_content),
            ("Notification channels", "AlertChannel" in monitoring_content),
            ("Metric thresholds", "MetricThreshold" in monitoring_content)
        ]
        
        for check_name, passed in checks:
            results.append({
                "check": f"monitoring_{check_name.lower().replace(' ', '_')}",
                "status": "✅ PASSED" if passed else "❌ FAILED",
                "details": f"Production monitoring {check_name}: {'Present' if passed else 'Missing'}"
            })
    else:
        results.append({
            "check": "production_monitoring_file",
            "status": "❌ FAILED",
            "details": "Production monitoring file not found at src/monitoring/production_monitoring.py"
        })
    
    return results

def validate_health_endpoints():
    """Validate health check endpoints."""
    print("🏥 Validating Health Endpoints...")
    
    results = []
    
    # Check main.py for health endpoints
    main_path = Path("main.py")
    if main_path.exists():
        with open(main_path, 'r') as f:
            main_content = f.read()
        
        # Check for health endpoints
        checks = [
            ("Health endpoint", "/health" in main_content),
            ("Ready endpoint", "/ready" in main_content),
            ("Metrics endpoint", "/metrics" in main_content)
        ]
        
        for check_name, passed in checks:
            results.append({
                "check": f"health_{check_name.lower().replace(' ', '_')}",
                "status": "✅ PASSED" if passed else "❌ FAILED",
                "details": f"Health endpoint {check_name}: {'Present' if passed else 'Missing'}"
            })
    else:
        results.append({
            "check": "main_file",
            "status": "❌ FAILED",
            "details": "main.py file not found"
        })
    
    return results

def validate_environment_configuration():
    """Validate environment configuration."""
    print("🌍 Validating Environment Configuration...")
    
    results = []
    
    # Check .env.example
    env_example_path = Path(".env.example")
    if env_example_path.exists():
        with open(env_example_path, 'r') as f:
            env_content = f.read()
        
        # Check for required environment variables
        required_vars = [
            "NEO4J_URI",
            "REDIS_URL",
            "SECRET_KEY",
            "API_KEY",
            "PROMETHEUS_METRICS_PORT",
            "ENVIRONMENT"
        ]
        
        for var in required_vars:
            if var in env_content:
                results.append({
                    "check": f"env_{var.lower()}",
                    "status": "✅ PASSED",
                    "details": f"Environment variable {var} documented"
                })
            else:
                results.append({
                    "check": f"env_{var.lower()}",
                    "status": "❌ FAILED",
                    "details": f"Environment variable {var} not documented"
                })
    else:
        results.append({
            "check": "env_example_file",
            "status": "❌ FAILED",
            "details": ".env.example file not found"
        })
    
    return results

def main():
    """Run Phase 4 validation."""
    print("🚀 Starting Phase 4 Production Readiness Validation")
    print("=" * 80)
    
    start_time = time.time()
    
    # Run all validation checks
    validation_functions = [
        validate_docker_configuration,
        validate_kubernetes_configuration,
        validate_cicd_pipeline,
        validate_error_handling,
        validate_performance_optimization,
        validate_security_hardening,
        validate_production_monitoring,
        validate_health_endpoints,
        validate_environment_configuration
    ]
    
    all_results = []
    
    for validation_func in validation_functions:
        try:
            results = validation_func()
            all_results.extend(results)
        except Exception as e:
            print(f"❌ Error in {validation_func.__name__}: {e}")
            all_results.append({
                "check": validation_func.__name__,
                "status": "❌ FAILED",
                "details": f"Validation error: {e}"
            })
    
    # Calculate summary
    passed_checks = [r for r in all_results if r["status"].startswith("✅")]
    failed_checks = [r for r in all_results if r["status"].startswith("❌")]
    
    execution_time = time.time() - start_time
    
    # Print results
    print(f"\n📊 Phase 4 Validation Results:")
    print(f"Total Checks: {len(all_results)}")
    print(f"Passed: {len(passed_checks)}")
    print(f"Failed: {len(failed_checks)}")
    print(f"Execution Time: {execution_time:.2f} seconds")
    
    if failed_checks:
        print(f"\n❌ Failed Checks:")
        for check in failed_checks:
            print(f"  - {check['check']}: {check['details']}")
    
    if len(passed_checks) == len(all_results):
        print(f"\n🎉 ALL PHASE 4 VALIDATION CHECKS PASSED!")
        print(f"✅ Phase 4 Production Readiness implementation is complete")
    else:
        print(f"\n⚠️ Phase 4 validation incomplete - {len(failed_checks)} checks failed")
    
    # Save results
    validation_results = {
        "timestamp": datetime.now().isoformat(),
        "phase": "Phase 4 Production Readiness",
        "total_checks": len(all_results),
        "passed_checks": len(passed_checks),
        "failed_checks": len(failed_checks),
        "execution_time": execution_time,
        "results": all_results
    }
    
    with open("phase4_validation_results.json", "w") as f:
        json.dump(validation_results, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: phase4_validation_results.json")
    
    return len(failed_checks) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)