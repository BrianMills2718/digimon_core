#!/usr/bin/env python3
"""
Genuine system verification script - NO DECEPTIVE PRACTICES
"""
import sys
import subprocess
from pathlib import Path
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def verify_database_connection():
    """Test actual Neo4j connection"""
    try:
        from src.core.neo4j_manager import Neo4jManager
        manager = Neo4jManager()
        health = manager.get_health_status()  # Must be real health check
        if health and health.get('status') == 'healthy':
            return True, "Database connection verified"
        else:
            return False, f"Database unhealthy: {health}"
    except Exception as e:
        return False, f"Database connection failed: {str(e)}"

def verify_contracts():
    """Test actual contract validation"""
    try:
        # Check if contract validator exists and can be imported
        from src.core.contract_validator import ContractValidator
        validator = ContractValidator("contracts")
        
        # Test all contracts - no fake success
        contract_files = list(Path("contracts/tools").glob("*.yaml"))
        if not contract_files:
            return False, "No contract files found"
            
        valid_count = 0
        total_count = len(contract_files)
        
        for contract_file in contract_files:
            try:
                contract = validator.load_contract(contract_file.stem)
                if contract:
                    errors = validator.validate_contract_schema(contract)
                    if not errors:
                        valid_count += 1
            except Exception:
                pass  # Count as invalid
        
        success = valid_count == total_count
        return success, f"Contracts: {valid_count}/{total_count} valid"
    except ImportError:
        return False, "Contract validator not available"
    except Exception as e:
        return False, f"Contract validation failed: {str(e)}"

def verify_core_tools():
    """Test core tool functionality with real data"""
    try:
        # Test PDF loader with actual file
        from src.tools.phase1.t01_pdf_loader import PDFLoader
        loader = PDFLoader()
        
        # Use actual test file, not mock
        test_file = "examples/pdfs/test_document.pdf"
        if not Path(test_file).exists():
            return False, f"Test file missing: {test_file}"
        
        result = loader.load_pdf(test_file, "verification_test")
        success = (result.get('status') == 'success' and 
                  'standardized_document' in result and
                  hasattr(result['standardized_document'], 'content') and
                  len(result['standardized_document'].content) > 0)
        
        return success, f"PDF loader test: {'PASS' if success else 'FAIL'}"
    except ImportError:
        return False, "PDF loader not available"
    except Exception as e:
        return False, f"Core tool test failed: {str(e)}"

def verify_basic_imports():
    """Verify basic system imports work"""
    try:
        # Test core system imports
        from src.core.pipeline_orchestrator import PipelineOrchestrator
        from src.core.service_manager import ServiceManager
        from src.core.config_manager import Config
        
        return True, "Basic imports successful"
    except ImportError as e:
        return False, f"Import failed: {str(e)}"
    except Exception as e:
        return False, f"Import error: {str(e)}"

def main():
    """Run comprehensive verification with NO fake results"""
    print("🔍 Starting GENUINE system verification...")
    
    checks = [
        ("Basic System Imports", verify_basic_imports),
        ("Database Connection", verify_database_connection),
        ("Contract Validation", verify_contracts),
        ("Core Tool Functionality", verify_core_tools),
    ]
    
    all_passed = True
    results = []
    
    for check_name, check_func in checks:
        try:
            passed, message = check_func()
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status} {check_name}: {message}")
            results.append((check_name, passed, message))
            all_passed = all_passed and passed
        except Exception as e:
            print(f"❌ FAIL {check_name}: Exception - {str(e)}")
            results.append((check_name, False, f"Exception: {str(e)}"))
            all_passed = False
    
    # Record genuine results in Evidence.md
    with open("Evidence.md", "a") as f:
        timestamp = datetime.now().isoformat()
        f.write(f"\n--- GENUINE VERIFICATION RUN {timestamp} ---\n")
        f.write(f"Overall Status: {'PASS' if all_passed else 'FAIL'}\n")
        for check_name, passed, message in results:
            f.write(f"{check_name}: {'PASS' if passed else 'FAIL'} - {message}\n")
        f.write(f"Total: {sum(1 for _, passed, _ in results if passed)}/{len(results)} checks passed\n")
    
    if all_passed:
        print("\n✅ SYSTEM VERIFICATION PASSED")
        return 0
    else:
        print("\n❌ SYSTEM VERIFICATION FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())