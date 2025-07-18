#!/usr/bin/env python3
"""
Gemini AI Validation Script - CLAUDE.md Implementation Claims Verification
==========================================================================

This script performs a comprehensive verification of all claims made regarding
the implementation of Priority 0 and Priority 1 tasks from CLAUDE.md.

Claims to Validate:
1. ✅ C-1: Fixed systemic project structure flaw - created proper Python package structure
2. ✅ C-5: Fixed hardcoded secrets in Docker
3. ✅ M-2: Implemented dependency locking
4. ✅ C-3: Enforced ServiceManager & ConfigurationManager usage
5. ✅ C-4: Completed broken implementations

Each claim will be thoroughly tested with evidence collection.
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import traceback

class ClaimValidator:
    """Validates implementation claims with detailed evidence collection."""
    
    def __init__(self):
        self.results = {
            "validation_timestamp": None,
            "claims_validated": {},
            "overall_status": "UNKNOWN",
            "evidence": {},
            "failures": [],
            "warnings": []
        }
        
    def validate_all_claims(self) -> Dict[str, Any]:
        """Validate all Priority 0 and Priority 1 implementation claims."""
        
        from datetime import datetime
        self.results["validation_timestamp"] = datetime.now().isoformat()
        
        print("🔍 GEMINI VALIDATION: CLAUDE.md Implementation Claims")
        print("=" * 60)
        
        # Priority 0 Claims
        self._validate_c1_package_structure()
        self._validate_c5_docker_secrets()
        self._validate_m2_dependency_locking()
        
        # Priority 1 Claims
        self._validate_c3_service_manager_usage()
        self._validate_c4_broken_implementations()
        
        # Overall assessment
        self._calculate_overall_status()
        
        return self.results
    
    def _validate_c1_package_structure(self):
        """Validate C-1: Fixed systemic project structure flaw."""
        
        print("\n🧪 VALIDATING C-1: Package Structure Fix")
        claim_key = "c1_package_structure"
        evidence = {}
        
        try:
            # Check 1: pyproject.toml exists and is properly configured
            pyproject_path = Path("pyproject.toml")
            if pyproject_path.exists():
                evidence["pyproject_exists"] = True
                with open(pyproject_path) as f:
                    content = f.read()
                    evidence["pyproject_has_build_system"] = "[build-system]" in content
                    evidence["pyproject_has_package_config"] = "name = \"super-digimon-graphrag\"" in content
                    evidence["pyproject_has_dependencies"] = "dependencies = [" in content
            else:
                evidence["pyproject_exists"] = False
            
            # Check 2: Package is installed as editable
            result = subprocess.run([sys.executable, "-c", "import pkg_resources; print([p.key for p in pkg_resources.working_set if 'super-digimon' in p.key])"], 
                                  capture_output=True, text=True)
            evidence["package_installed"] = "super-digimon-graphrag" in result.stdout
            
            # Check 3: No sys.path manipulation in src/
            result = subprocess.run(["grep", "-r", "sys.path", "src/"], capture_output=True, text=True)
            evidence["no_syspath_in_src"] = result.returncode != 0  # grep returns 0 if found
            
            # Check 4: Key files properly import without sys.path
            try:
                from src.core.service_manager import get_service_manager
                from src.core.config import ConfigurationManager
                evidence["imports_work_without_syspath"] = True
            except ImportError as e:
                evidence["imports_work_without_syspath"] = False
                evidence["import_error"] = str(e)
            
            # Check 5: UI files cleaned up
            ui_files_checked = []
            for ui_file in ["ui/graphrag_ui.py", "streamlit_app.py"]:
                if Path(ui_file).exists():
                    with open(ui_file) as f:
                        content = f.read()
                        has_syspath = "sys.path.insert" in content
                        ui_files_checked.append({"file": ui_file, "has_syspath": has_syspath})
            evidence["ui_files_cleaned"] = ui_files_checked
            
            # Determine claim status
            critical_checks = [
                evidence.get("pyproject_exists", False),
                evidence.get("package_installed", False),
                evidence.get("no_syspath_in_src", False),
                evidence.get("imports_work_without_syspath", False)
            ]
            
            self.results["claims_validated"][claim_key] = all(critical_checks)
            self.results["evidence"][claim_key] = evidence
            
            if all(critical_checks):
                print("   ✅ C-1 VALIDATED: Package structure properly fixed")
            else:
                print("   ❌ C-1 FAILED: Package structure issues detected")
                self.results["failures"].append("C-1: Package structure validation failed")
                
        except Exception as e:
            print(f"   ⚠️  C-1 ERROR: {str(e)}")
            self.results["claims_validated"][claim_key] = False
            self.results["failures"].append(f"C-1: Validation error - {str(e)}")
    
    def _validate_c5_docker_secrets(self):
        """Validate C-5: Fixed hardcoded secrets in Docker."""
        
        print("\n🧪 VALIDATING C-5: Docker Secrets Fix")
        claim_key = "c5_docker_secrets"
        evidence = {}
        
        try:
            # Check 1: .env.example exists
            env_example_path = Path(".env.example")
            evidence["env_example_exists"] = env_example_path.exists()
            if env_example_path.exists():
                with open(env_example_path) as f:
                    content = f.read()
                    evidence["env_example_has_neo4j"] = "NEO4J_PASSWORD" in content
                    evidence["env_example_has_api_keys"] = "OPENAI_API_KEY" in content
            
            # Check 2: docker-compose.yml uses environment variables
            docker_compose_path = Path("docker-compose.yml")
            evidence["docker_compose_exists"] = docker_compose_path.exists()
            if docker_compose_path.exists():
                with open(docker_compose_path) as f:
                    content = f.read()
                    evidence["docker_uses_env_vars"] = "${NEO4J_PASSWORD}" in content
                    evidence["no_hardcoded_password"] = "neo4j/password" not in content
            
            # Check 3: .gitignore properly configured
            gitignore_path = Path(".gitignore")
            evidence["gitignore_exists"] = gitignore_path.exists()
            if gitignore_path.exists():
                with open(gitignore_path) as f:
                    content = f.read()
                    evidence["gitignore_excludes_env"] = ".env" in content and "!.env.example" in content
            
            # Determine claim status
            critical_checks = [
                evidence.get("env_example_exists", False),
                evidence.get("docker_uses_env_vars", False),
                evidence.get("no_hardcoded_password", False)
            ]
            
            self.results["claims_validated"][claim_key] = all(critical_checks)
            self.results["evidence"][claim_key] = evidence
            
            if all(critical_checks):
                print("   ✅ C-5 VALIDATED: Docker secrets properly secured")
            else:
                print("   ❌ C-5 FAILED: Docker secrets issues detected")
                self.results["failures"].append("C-5: Docker secrets validation failed")
                
        except Exception as e:
            print(f"   ⚠️  C-5 ERROR: {str(e)}")
            self.results["claims_validated"][claim_key] = False
            self.results["failures"].append(f"C-5: Validation error - {str(e)}")
    
    def _validate_m2_dependency_locking(self):
        """Validate M-2: Implemented dependency locking."""
        
        print("\n🧪 VALIDATING M-2: Dependency Locking")
        claim_key = "m2_dependency_locking"
        evidence = {}
        
        try:
            # Check 1: requirements.in exists
            req_in_path = Path("requirements.in")
            evidence["requirements_in_exists"] = req_in_path.exists()
            if req_in_path.exists():
                with open(req_in_path) as f:
                    content = f.read()
                    evidence["requirements_in_has_deps"] = "fastmcp" in content and "neo4j" in content
            
            # Check 2: requirements-dev.in exists
            req_dev_path = Path("requirements-dev.in")
            evidence["requirements_dev_in_exists"] = req_dev_path.exists()
            if req_dev_path.exists():
                with open(req_dev_path) as f:
                    content = f.read()
                    evidence["requirements_dev_has_tools"] = "pytest" in content and "pip-tools" in content
            
            # Check 3: Update script exists and is executable
            update_script_path = Path("scripts/update_dependencies.sh")
            evidence["update_script_exists"] = update_script_path.exists()
            if update_script_path.exists():
                evidence["update_script_executable"] = os.access(update_script_path, os.X_OK)
                with open(update_script_path) as f:
                    content = f.read()
                    evidence["update_script_has_pip_compile"] = "pip-compile" in content
            
            # Check 4: pip-tools is available
            result = subprocess.run([sys.executable, "-c", "import piptools"], capture_output=True, text=True)
            evidence["pip_tools_available"] = result.returncode == 0
            
            # Determine claim status
            critical_checks = [
                evidence.get("requirements_in_exists", False),
                evidence.get("requirements_dev_in_exists", False),
                evidence.get("update_script_exists", False),
                evidence.get("pip_tools_available", False)
            ]
            
            self.results["claims_validated"][claim_key] = all(critical_checks)
            self.results["evidence"][claim_key] = evidence
            
            if all(critical_checks):
                print("   ✅ M-2 VALIDATED: Dependency locking infrastructure ready")
            else:
                print("   ❌ M-2 FAILED: Dependency locking issues detected")
                self.results["failures"].append("M-2: Dependency locking validation failed")
                
        except Exception as e:
            print(f"   ⚠️  M-2 ERROR: {str(e)}")
            self.results["claims_validated"][claim_key] = False
            self.results["failures"].append(f"M-2: Validation error - {str(e)}")
    
    def _validate_c3_service_manager_usage(self):
        """Validate C-3: Enforced ServiceManager & ConfigurationManager usage."""
        
        print("\n🧪 VALIDATING C-3: ServiceManager Usage")
        claim_key = "c3_service_manager"
        evidence = {}
        
        try:
            # Check 1: No direct service instantiation in key files
            key_files = [
                "src/mcp_server.py",
                "src/tools/phase1/phase1_mcp_tools.py", 
                "src/tools/phase2/enhanced_vertical_slice_workflow.py",
                "ui/web_ui.py",
                "streamlit_app.py"
            ]
            
            direct_instantiation_found = []
            service_manager_usage = []
            
            for file_path in key_files:
                if Path(file_path).exists():
                    with open(file_path) as f:
                        content = f.read()
                        # Check for direct instantiation
                        has_direct = any(pattern in content for pattern in [
                            "IdentityService()", 
                            "ProvenanceService()", 
                            "QualityService()"
                        ])
                        # Check for ServiceManager usage
                        has_service_manager = "get_service_manager" in content
                        
                        direct_instantiation_found.append({
                            "file": file_path,
                            "has_direct_instantiation": has_direct
                        })
                        service_manager_usage.append({
                            "file": file_path,
                            "uses_service_manager": has_service_manager
                        })
            
            evidence["direct_instantiation_check"] = direct_instantiation_found
            evidence["service_manager_usage"] = service_manager_usage
            
            # Check 2: ServiceManager works correctly
            try:
                from src.core.service_manager import get_service_manager
                sm = get_service_manager()
                stats = sm.get_service_stats()
                evidence["service_manager_functional"] = True
                evidence["service_manager_stats"] = stats
            except Exception as e:
                evidence["service_manager_functional"] = False
                evidence["service_manager_error"] = str(e)
            
            # Check 3: Configuration manager works
            try:
                from src.core.config import ConfigurationManager
                config = ConfigurationManager().get_config()
                evidence["config_manager_functional"] = True
                evidence["config_has_neo4j"] = hasattr(config, 'neo4j')
                evidence["config_has_workflow"] = hasattr(config, 'workflow')
            except Exception as e:
                evidence["config_manager_functional"] = False
                evidence["config_manager_error"] = str(e)
            
            # Determine claim status
            no_direct_instantiation = all(not item["has_direct_instantiation"] for item in direct_instantiation_found)
            has_service_manager_usage = any(item["uses_service_manager"] for item in service_manager_usage)
            
            critical_checks = [
                no_direct_instantiation,
                has_service_manager_usage,
                evidence.get("service_manager_functional", False),
                evidence.get("config_manager_functional", False)
            ]
            
            self.results["claims_validated"][claim_key] = all(critical_checks)
            self.results["evidence"][claim_key] = evidence
            
            if all(critical_checks):
                print("   ✅ C-3 VALIDATED: ServiceManager pattern properly enforced")
            else:
                print("   ❌ C-3 FAILED: ServiceManager enforcement issues detected")
                self.results["failures"].append("C-3: ServiceManager validation failed")
                
        except Exception as e:
            print(f"   ⚠️  C-3 ERROR: {str(e)}")
            self.results["claims_validated"][claim_key] = False
            self.results["failures"].append(f"C-3: Validation error - {str(e)}")
    
    def _validate_c4_broken_implementations(self):
        """Validate C-4: Completed broken implementations."""
        
        print("\n🧪 VALIDATING C-4: Broken Implementations Fixed")
        claim_key = "c4_broken_implementations"
        evidence = {}
        
        try:
            # Check 1: ServiceManager has all required methods
            from src.core.service_manager import get_service_manager
            sm = get_service_manager()
            
            required_methods = ["configure_identity_service", "get_neo4j_driver"]
            missing_methods = []
            for method in required_methods:
                if not hasattr(sm, method):
                    missing_methods.append(method)
            
            evidence["service_manager_methods"] = {
                "required": required_methods,
                "missing": missing_methods,
                "all_present": len(missing_methods) == 0
            }
            
            # Check 2: EntityBuilder constructor works
            try:
                from src.tools.phase1.t31_entity_builder import EntityBuilder
                eb = EntityBuilder(sm.identity_service, sm.provenance_service, sm.quality_service)
                evidence["entity_builder_constructor"] = True
            except Exception as e:
                evidence["entity_builder_constructor"] = False
                evidence["entity_builder_error"] = str(e)
            
            # Check 3: Thread safety enhancements
            from src.core.service_manager import ServiceManager
            has_init_lock = hasattr(ServiceManager, '_init_lock')
            evidence["thread_safety_enhanced"] = has_init_lock
            
            # Check 4: Configuration completeness
            from src.core.config import ConfigurationManager, WorkflowConfig, APIConfig
            config = ConfigurationManager().get_config()
            evidence["config_completeness"] = {
                "has_workflow_config": hasattr(config, 'workflow'),
                "has_api_keys": hasattr(config.api, 'openai_api_key') if hasattr(config, 'api') else False,
                "workflow_config_type": type(config.workflow).__name__ if hasattr(config, 'workflow') else None
            }
            
            # Determine claim status
            critical_checks = [
                evidence["service_manager_methods"]["all_present"],
                evidence.get("entity_builder_constructor", False),
                evidence.get("thread_safety_enhanced", False),
                evidence["config_completeness"]["has_workflow_config"]
            ]
            
            self.results["claims_validated"][claim_key] = all(critical_checks)
            self.results["evidence"][claim_key] = evidence
            
            if all(critical_checks):
                print("   ✅ C-4 VALIDATED: Broken implementations properly fixed")
            else:
                print("   ❌ C-4 FAILED: Broken implementation issues detected")
                self.results["failures"].append("C-4: Broken implementations validation failed")
                
        except Exception as e:
            print(f"   ⚠️  C-4 ERROR: {str(e)}")
            self.results["claims_validated"][claim_key] = False
            self.results["failures"].append(f"C-4: Validation error - {str(e)}")
    
    def _calculate_overall_status(self):
        """Calculate overall validation status."""
        
        validated_claims = self.results["claims_validated"]
        total_claims = len(validated_claims)
        passed_claims = sum(1 for status in validated_claims.values() if status)
        
        if passed_claims == total_claims:
            self.results["overall_status"] = "ALL_CLAIMS_VALIDATED"
        elif passed_claims >= total_claims * 0.8:  # 80% threshold
            self.results["overall_status"] = "MOSTLY_VALIDATED"
        elif passed_claims > 0:
            self.results["overall_status"] = "PARTIALLY_VALIDATED"
        else:
            self.results["overall_status"] = "VALIDATION_FAILED"
        
        print(f"\n📊 OVERALL VALIDATION STATUS: {self.results['overall_status']}")
        print(f"   Claims Validated: {passed_claims}/{total_claims}")
        
        if self.results["failures"]:
            print("\n❌ FAILURES DETECTED:")
            for failure in self.results["failures"]:
                print(f"   • {failure}")
        
        if self.results["warnings"]:
            print("\n⚠️  WARNINGS:")
            for warning in self.results["warnings"]:
                print(f"   • {warning}")

def main():
    """Run the comprehensive validation."""
    
    # Change to project directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    validator = ClaimValidator()
    results = validator.validate_all_claims()
    
    # Save detailed results
    results_file = "gemini_validation_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📋 DETAILED RESULTS SAVED TO: {results_file}")
    print("\n🎯 VALIDATION COMPLETE")
    
    return results

if __name__ == "__main__":
    main()