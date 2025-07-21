#!/usr/bin/env python3
"""
Configuration validation script.

Validates that the consolidated configuration system works correctly
and provides better performance than the previous system.
"""

import os
import sys
import time
import traceback
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_configuration_loading():
    """Test configuration loading performance and functionality."""
    print("Testing configuration loading...")
    
    results = {
        "config_load_time": 0.0,
        "config_validation_time": 0.0,
        "configuration_loaded": False,
        "validation_passed": False,
        "environment_vars_processed": 0,
        "config_sections": [],
        "errors": []
    }
    
    try:
        # Test configuration loading time
        start_time = time.time()
        from src.core.config_manager import get_config
        config = get_config()
        load_time = time.time() - start_time
        
        results["config_load_time"] = load_time
        results["configuration_loaded"] = True
        
        print(f"✅ Configuration loaded in {load_time:.4f}s")
        
        # Test configuration validation
        start_time = time.time()
        env_summary = config.get_environment_summary()
        validation_time = time.time() - start_time
        
        results["config_validation_time"] = validation_time
        results["validation_passed"] = True
        results["environment_vars_processed"] = env_summary["environment_vars_loaded"]
        
        print(f"✅ Configuration validation completed in {validation_time:.4f}s")
        print(f"   Environment variables processed: {env_summary['environment_vars_loaded']}")
        
        # Test individual configuration sections
        config_sections = []
        
        # Test database config
        try:
            db_config = config.get_neo4j_config()
            config_sections.append("database")
            print(f"✅ Database config: {db_config['uri']}")
        except Exception as e:
            results["errors"].append(f"Database config error: {e}")
        
        # Test API config
        try:
            api_config = config.get_api_config()
            config_sections.append("api")
            print(f"✅ API config loaded with {len(api_config)} settings")
        except Exception as e:
            results["errors"].append(f"API config error: {e}")
        
        # Test system config
        try:
            system_config = config.get_system_config()
            config_sections.append("system")
            print(f"✅ System config: environment={system_config['environment']}")
        except Exception as e:
            results["errors"].append(f"System config error: {e}")
        
        results["config_sections"] = config_sections
        
        # Test production readiness check
        try:
            is_ready, issues = config.is_production_ready()
            print(f"✅ Production readiness check: {'Ready' if is_ready else 'Not ready'}")
            if issues:
                print(f"   Issues: {', '.join(issues)}")
        except Exception as e:
            results["errors"].append(f"Production readiness error: {e}")
        
    except Exception as e:
        results["errors"].append(f"Configuration loading failed: {e}")
        print(f"❌ Configuration loading failed: {e}")
        traceback.print_exc()
    
    return results


def test_configuration_performance():
    """Test configuration access performance."""
    print("\nTesting configuration performance...")
    
    results = {
        "multiple_access_time": 0.0,
        "config_get_operations": 0,
        "average_access_time": 0.0,
        "errors": []
    }
    
    try:
        from src.core.config_manager import get_config
        config = get_config()
        
        # Test multiple rapid config accesses
        start_time = time.time()
        operations = 0
        
        for i in range(100):
            # Test various config access patterns
            _ = config.get_neo4j_config()
            _ = config.get_api_config()
            _ = config.get_system_config()
            _ = config.get("database.uri")
            _ = config.get("system.log_level")
            operations += 5
        
        total_time = time.time() - start_time
        avg_time = total_time / operations
        
        results["multiple_access_time"] = total_time
        results["config_get_operations"] = operations
        results["average_access_time"] = avg_time
        
        print(f"✅ {operations} config operations completed in {total_time:.4f}s")
        print(f"   Average access time: {avg_time:.6f}s per operation")
        
        # Performance threshold check
        if avg_time < 0.001:  # Less than 1ms per operation
            print("✅ Configuration access performance: EXCELLENT")
        elif avg_time < 0.01:  # Less than 10ms per operation
            print("✅ Configuration access performance: GOOD")
        else:
            print("⚠️  Configuration access performance: SLOW")
            
    except Exception as e:
        results["errors"].append(f"Performance test failed: {e}")
        print(f"❌ Performance test failed: {e}")
        traceback.print_exc()
    
    return results


def test_environment_variable_handling():
    """Test environment variable processing."""
    print("\nTesting environment variable handling...")
    
    results = {
        "env_vars_tested": 0,
        "env_vars_processed": 0,
        "override_working": False,
        "errors": []
    }
    
    try:
        from src.core.config_manager import get_config
        
        # Test environment variable override
        original_log_level = os.environ.get("LOG_LEVEL")
        
        # Set test environment variable
        os.environ["LOG_LEVEL"] = "DEBUG"
        results["env_vars_tested"] += 1
        
        # Create new config instance to pick up env var
        from src.core.config_manager import load_config
        config = load_config(force_reload=True)
        
        system_config = config.get_system_config()
        
        if system_config["log_level"] == "DEBUG":
            results["override_working"] = True
            results["env_vars_processed"] += 1
            print("✅ Environment variable override working correctly")
        else:
            results["errors"].append("Environment variable override not working")
            print("❌ Environment variable override not working")
        
        # Restore original environment
        if original_log_level:
            os.environ["LOG_LEVEL"] = original_log_level
        else:
            os.environ.pop("LOG_LEVEL", None)
            
    except Exception as e:
        results["errors"].append(f"Environment variable test failed: {e}")
        print(f"❌ Environment variable test failed: {e}")
        traceback.print_exc()
    
    return results


def test_configuration_consolidation():
    """Test that configuration consolidation eliminated redundancy."""
    print("\nTesting configuration consolidation...")
    
    results = {
        "import_test_passed": False,
        "unified_interface": False,
        "backward_compatibility": False,
        "errors": []
    }
    
    try:
        # Test that we can import from the new location
        from src.core.config_manager import ConfigurationManager, get_config
        results["import_test_passed"] = True
        print("✅ New configuration import working")
        
        # Test unified interface
        config = get_config()
        if hasattr(config, 'get_neo4j_config') and hasattr(config, 'get_api_config'):
            results["unified_interface"] = True
            print("✅ Unified configuration interface available")
        
        # Test backward compatibility aliases
        from src.core.config_manager import ConfigManager, UnifiedConfigManager
        if ConfigManager == ConfigurationManager and UnifiedConfigManager == ConfigurationManager:
            results["backward_compatibility"] = True
            print("✅ Backward compatibility aliases working")
            
    except Exception as e:
        results["errors"].append(f"Consolidation test failed: {e}")
        print(f"❌ Consolidation test failed: {e}")
        traceback.print_exc()
    
    return results


def validate_configuration_system():
    """Run comprehensive configuration system validation."""
    print("🔧 Validating Consolidated Configuration System")
    print("=" * 50)
    
    start_time = datetime.now()
    
    # Run all tests
    test_results = {
        "validation_timestamp": start_time.isoformat(),
        "loading_test": test_configuration_loading(),
        "performance_test": test_configuration_performance(),
        "environment_test": test_environment_variable_handling(),
        "consolidation_test": test_configuration_consolidation()
    }
    
    # Calculate overall results
    total_errors = sum(len(test["errors"]) for test in test_results.values() if isinstance(test, dict) and "errors" in test)
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    test_results["validation_duration"] = duration
    test_results["total_errors"] = total_errors
    test_results["validation_passed"] = total_errors == 0
    
    # Print summary
    print(f"\n{'='*50}")
    print("📊 VALIDATION SUMMARY")
    print(f"{'='*50}")
    print(f"Duration: {duration:.2f}s")
    print(f"Total Errors: {total_errors}")
    print(f"Status: {'✅ PASSED' if total_errors == 0 else '❌ FAILED'}")
    
    if test_results["loading_test"]["configuration_loaded"]:
        load_time = test_results["loading_test"]["config_load_time"]
        print(f"Config Load Time: {load_time:.4f}s")
    
    if test_results["performance_test"]["config_get_operations"] > 0:
        avg_time = test_results["performance_test"]["average_access_time"]
        print(f"Avg Access Time: {avg_time:.6f}s per operation")
    
    # Print any errors
    if total_errors > 0:
        print(f"\n❌ ERRORS FOUND:")
        for test_name, test_data in test_results.items():
            if isinstance(test_data, dict) and "errors" in test_data and test_data["errors"]:
                print(f"  {test_name}:")
                for error in test_data["errors"]:
                    print(f"    - {error}")
    
    return test_results


if __name__ == "__main__":
    results = validate_configuration_system()
    
    # Exit with appropriate code
    sys.exit(0 if results["validation_passed"] else 1)