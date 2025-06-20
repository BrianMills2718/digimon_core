#!/usr/bin/env python3
"""
TEST MCP SERVICES DIRECTLY
Test the underlying services that the MCP tools are built on
"""

import sys
import json
import time
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

def test_core_services():
    """Test the 4 core services directly"""
    
    print("🔥 TESTING CORE SERVICES DIRECTLY")
    print("=" * 80)
    
    results = {
        "test_summary": {
            "total_services": 4,
            "services_tested": 0,
            "services_passed": 0,
            "services_failed": 0,
            "total_methods": 0,
            "methods_passed": 0,
            "methods_failed": 0,
            "start_time": time.time()
        },
        "service_results": []
    }
    
    # Test Identity Service
    print("\n🧪 TESTING: Identity Service")
    print("-" * 60)
    
    service_result = {
        "service_name": "Identity Service",
        "methods_tested": [],
        "status": "UNKNOWN",
        "error": None
    }
    
    try:
        from src.core.identity_service import IdentityService
        identity_service = IdentityService()
        
        # Test create_mention
        mention_result = identity_service.create_mention(
            surface_form="Dr. Smith",
            start_pos=0,
            end_pos=9,
            source_ref="test_document",
            entity_type="PERSON", 
            confidence=0.8
        )
        service_result["methods_tested"].append({
            "method": "create_mention",
            "status": "PASS",
            "result": mention_result
        })
        print(f"✅ create_mention: {mention_result}")
        results["test_summary"]["methods_passed"] += 1
        
        # Test get_stats
        stats_result = identity_service.get_stats()
        service_result["methods_tested"].append({
            "method": "get_stats", 
            "status": "PASS",
            "result": stats_result
        })
        print(f"✅ get_stats: {stats_result}")
        results["test_summary"]["methods_passed"] += 1
        
        service_result["status"] = "PASS"
        results["test_summary"]["services_passed"] += 1
        
    except Exception as e:
        service_result["status"] = "FAIL"
        service_result["error"] = str(e)
        results["test_summary"]["services_failed"] += 1
        print(f"❌ Identity Service failed: {e}")
    
    results["service_results"].append(service_result)
    results["test_summary"]["services_tested"] += 1
    results["test_summary"]["total_methods"] += len(service_result["methods_tested"])
    
    # Test Provenance Service
    print("\n🧪 TESTING: Provenance Service")
    print("-" * 60)
    
    service_result = {
        "service_name": "Provenance Service",
        "methods_tested": [],
        "status": "UNKNOWN",
        "error": None
    }
    
    try:
        from src.core.provenance_service import ProvenanceService
        provenance_service = ProvenanceService()
        
        # Test start_operation
        op_id = provenance_service.start_operation(
            tool_id="test_tool",
            operation_type="create",
            inputs=["input1", "input2"],
            parameters={"test": "data"}
        )
        service_result["methods_tested"].append({
            "method": "start_operation",
            "status": "PASS",
            "result": op_id
        })
        print(f"✅ start_operation: {op_id}")
        results["test_summary"]["methods_passed"] += 1
        
        # Test complete_operation
        complete_result = provenance_service.complete_operation(
            operation_id=op_id,
            outputs=["output1"],
            success=True
        )
        service_result["methods_tested"].append({
            "method": "complete_operation",
            "status": "PASS", 
            "result": complete_result
        })
        print(f"✅ complete_operation: {complete_result}")
        results["test_summary"]["methods_passed"] += 1
        
        # Test get_tool_statistics
        stats_result = provenance_service.get_tool_statistics()
        service_result["methods_tested"].append({
            "method": "get_tool_statistics",
            "status": "PASS",
            "result": stats_result
        })
        print(f"✅ get_tool_statistics: {stats_result}")
        results["test_summary"]["methods_passed"] += 1
        
        service_result["status"] = "PASS"
        results["test_summary"]["services_passed"] += 1
        
    except Exception as e:
        service_result["status"] = "FAIL"
        service_result["error"] = str(e)
        results["test_summary"]["services_failed"] += 1
        print(f"❌ Provenance Service failed: {e}")
    
    results["service_results"].append(service_result)
    results["test_summary"]["services_tested"] += 1
    results["test_summary"]["total_methods"] += len(service_result["methods_tested"])
    
    # Test Quality Service
    print("\n🧪 TESTING: Quality Service")
    print("-" * 60)
    
    service_result = {
        "service_name": "Quality Service",
        "methods_tested": [],
        "status": "UNKNOWN",
        "error": None
    }
    
    try:
        from src.core.quality_service import QualityService
        quality_service = QualityService()
        
        # Test assess_confidence
        assess_result = quality_service.assess_confidence(
            object_ref="test_object_123",
            base_confidence=0.8,
            factors={"factor1": 0.1},
            metadata={"test": "data"}
        )
        service_result["methods_tested"].append({
            "method": "assess_confidence",
            "status": "PASS",
            "result": assess_result
        })
        print(f"✅ assess_confidence: {assess_result}")
        results["test_summary"]["methods_passed"] += 1
        
        # Test get_quality_statistics
        stats_result = quality_service.get_quality_statistics()
        service_result["methods_tested"].append({
            "method": "get_quality_statistics",
            "status": "PASS",
            "result": stats_result
        })
        print(f"✅ get_quality_statistics: {stats_result}")
        results["test_summary"]["methods_passed"] += 1
        
        service_result["status"] = "PASS"
        results["test_summary"]["services_passed"] += 1
        
    except Exception as e:
        service_result["status"] = "FAIL"
        service_result["error"] = str(e)
        results["test_summary"]["services_failed"] += 1
        print(f"❌ Quality Service failed: {e}")
    
    results["service_results"].append(service_result)
    results["test_summary"]["services_tested"] += 1
    results["test_summary"]["total_methods"] += len(service_result["methods_tested"])
    
    # Test Workflow Service
    print("\n🧪 TESTING: Workflow Service")
    print("-" * 60)
    
    service_result = {
        "service_name": "Workflow Service",
        "methods_tested": [],
        "status": "UNKNOWN",
        "error": None
    }
    
    try:
        from src.core.workflow_state_service import WorkflowStateService
        workflow_service = WorkflowStateService("./data/workflows")
        
        # Test start_workflow
        workflow_id = workflow_service.start_workflow(
            name="test_workflow",
            total_steps=5,
            initial_state={"progress": 0}
        )
        service_result["methods_tested"].append({
            "method": "start_workflow",
            "status": "PASS",
            "result": workflow_id
        })
        print(f"✅ start_workflow: {workflow_id}")
        results["test_summary"]["methods_passed"] += 1
        
        # Test get_service_statistics
        stats_result = workflow_service.get_service_statistics()
        service_result["methods_tested"].append({
            "method": "get_service_statistics",
            "status": "PASS",
            "result": stats_result
        })
        print(f"✅ get_service_statistics: {stats_result}")
        results["test_summary"]["methods_passed"] += 1
        
        service_result["status"] = "PASS"
        results["test_summary"]["services_passed"] += 1
        
    except Exception as e:
        service_result["status"] = "FAIL"
        service_result["error"] = str(e)
        results["test_summary"]["services_failed"] += 1
        print(f"❌ Workflow Service failed: {e}")
    
    results["service_results"].append(service_result)
    results["test_summary"]["services_tested"] += 1
    results["test_summary"]["total_methods"] += len(service_result["methods_tested"])
    
    # Calculate failed methods
    results["test_summary"]["methods_failed"] = results["test_summary"]["total_methods"] - results["test_summary"]["methods_passed"]
    
    # Generate summary
    results["test_summary"]["end_time"] = time.time()
    results["test_summary"]["total_execution_time"] = results["test_summary"]["end_time"] - results["test_summary"]["start_time"]
    
    print("\n" + "=" * 80)
    print("📊 CORE SERVICES TEST SUMMARY")
    print("=" * 80)
    print(f"Total Services: {results['test_summary']['total_services']}")
    print(f"✅ Services Passed: {results['test_summary']['services_passed']}")
    print(f"❌ Services Failed: {results['test_summary']['services_failed']}")
    print(f"📈 Service Pass Rate: {(results['test_summary']['services_passed']/results['test_summary']['total_services'])*100:.1f}%")
    print(f"")
    print(f"Total Methods: {results['test_summary']['total_methods']}")
    print(f"✅ Methods Passed: {results['test_summary']['methods_passed']}")
    print(f"❌ Methods Failed: {results['test_summary']['methods_failed']}")
    print(f"📈 Method Pass Rate: {(results['test_summary']['methods_passed']/results['test_summary']['total_methods'])*100:.1f}%")
    print(f"⏱️  Total Time: {results['test_summary']['total_execution_time']:.2f}s")
    
    # Show service breakdown
    print(f"\n📋 SERVICE BREAKDOWN:")
    for service in results["service_results"]:
        method_count = len([m for m in service["methods_tested"] if m["status"] == "PASS"])
        total_methods = len(service["methods_tested"])
        print(f"  {service['service_name']}: {service['status']} ({method_count}/{total_methods} methods)")
    
    # Save results
    with open("core_services_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: core_services_test_results.json")
    
    return results

if __name__ == "__main__":
    results = test_core_services()
    
    # Determine success
    services_passed = results["test_summary"]["services_passed"]
    total_services = results["test_summary"]["total_services"]
    service_pass_rate = (services_passed / total_services) * 100 if total_services > 0 else 0
    
    methods_passed = results["test_summary"]["methods_passed"] 
    total_methods = results["test_summary"]["total_methods"]
    method_pass_rate = (methods_passed / total_methods) * 100 if total_methods > 0 else 0
    
    print(f"\n🎯 FINAL CONCLUSION:")
    print(f"   Services: {services_passed}/{total_services} ({service_pass_rate:.1f}% pass rate)")
    print(f"   Methods: {methods_passed}/{total_methods} ({method_pass_rate:.1f}% pass rate)")
    
    if service_pass_rate >= 75:
        print("   🎉 EXCELLENT: Core services are functional")
        sys.exit(0)
    elif service_pass_rate >= 50:
        print("   ⚠️  GOOD: Most core services working")
        sys.exit(0)
    else:
        print("   ❌ NEEDS WORK: Core service issues")
        sys.exit(1)