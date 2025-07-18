#!/usr/bin/env python3
"""Simple verification script to test core functionality"""

import sys
import os
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_evidence_logging():
    """Test evidence logging functionality"""
    print("Testing evidence logging...")
    
    try:
        from core.evidence_logger import EvidenceLogger
        
        evidence_logger = EvidenceLogger()
        
        # Test logging with verification
        test_data = {
            "test_name": "simple_verification",
            "timestamp": datetime.now().isoformat(),
            "verification_type": "cryptographic_hash"
        }
        
        verification_hash = evidence_logger.log_with_verification("SIMPLE_VERIFICATION_TEST", test_data)
        
        print(f"✅ Evidence logging works - Hash: {verification_hash[:16]}...")
        return True
        
    except Exception as e:
        print(f"❌ Evidence logging failed: {e}")
        return False

def test_production_validator():
    """Test production validator functionality"""
    print("Testing production validator...")
    
    try:
        from core.config_manager import ConfigManager
        from core.production_validator import ProductionValidator
        
        config_manager = ConfigManager()
        validator = ProductionValidator(config_manager)
        
        # Test validation
        results = validator.validate_production_readiness()
        
        print(f"✅ Production validator works - Readiness: {results['readiness_percentage']:.1f}%")
        return True
        
    except Exception as e:
        print(f"❌ Production validator failed: {e}")
        return False

def test_quality_service():
    """Test quality service functionality"""
    print("Testing quality service...")
    
    try:
        from core.quality_service import QualityService
        
        quality_service = QualityService()
        
        # Test quality check
        check_result = quality_service.run_comprehensive_quality_check()
        
        print(f"✅ Quality service works - Status: {check_result['service_status']}")
        return True
        
    except Exception as e:
        print(f"❌ Quality service failed: {e}")
        return False

def test_file_structure():
    """Test that all required files exist"""
    print("Testing file structure...")
    
    required_files = [
        "src/core/evidence_logger.py",
        "src/core/tool_factory.py", 
        "src/core/production_validator.py",
        "src/core/quality_service.py",
        "src/core/ontology_validator.py",
        "src/core/contract_validator.py",
        "tests/test_tool_success_rate.py",
        "tests/test_evidence_verification.py",
        "tests/test_production_readiness_comprehensive.py",
        "tests/integration/test_complete_pipeline.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    else:
        print("✅ All required files exist")
        return True

def main():
    """Main verification function"""
    print("=== CLAUDE.md IMPLEMENTATION VERIFICATION ===")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    tests = [
        test_file_structure,
        test_evidence_logging,
        test_quality_service,
        test_production_validator
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            failed += 1
    
    print(f"\n=== SUMMARY ===")
    print(f"Tests passed: {passed}")
    print(f"Tests failed: {failed}")
    print(f"Success rate: {(passed/(passed+failed)*100):.1f}%")
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED - CLAUDE.md IMPLEMENTATION COMPLETE!")
        return 0
    else:
        print("⚠️  Some tests failed - Implementation needs work")
        return 1

if __name__ == "__main__":
    sys.exit(main())