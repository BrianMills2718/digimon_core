#!/usr/bin/env python3
"""
TEST MCP SERVICES WITH CORRECT METHOD SIGNATURES
Fixed version that uses the actual method signatures from the code
"""

import sys
import json
import time
import os
from pathlib import Path

# Add src to path

def test_mcp_services_fixed():
    """Test the underlying services with correct method signatures"""
    
    print("🔥 TESTING MCP SERVICES (FIXED METHOD SIGNATURES)")
    print("=" * 80)
    
    results = {
        "test_summary": {
            "total_services": 6,
            "services_tested": 0,
            "services_passed": 0,
            "services_failed": 0,
            "start_time": time.time()
        },
        "service_results": []
    }
    
    # Test each service category
    services = [
        {"name": "Identity Service", "test_func": test_identity_service_fixed},
        {"name": "Provenance Service", "test_func": test_provenance_service_fixed},
        {"name": "Quality Service", "test_func": test_quality_service_fixed},
        {"name": "Workflow State Service", "test_func": test_workflow_service_fixed},
        {"name": "Vertical Slice Workflow", "test_func": test_vertical_slice_fixed},
        {"name": "Phase 1 MCP Tools", "test_func": test_phase1_mcp_tools_fixed},
    ]
    
    # Test each service
    for service in services:
        print(f"\n🧪 TESTING: {service['name']}")
        print("-" * 60)
        
        service_start = time.time()
        try:
            result = service['test_func']()
            service_result = {
                "service_name": service['name'],
                "status": "PASS",
                "result": result,
                "execution_time": time.time() - service_start,
                "error": None
            }
            results["test_summary"]["services_passed"] += 1
            print(f"✅ PASS: {result}")
            
        except Exception as e:
            service_result = {
                "service_name": service['name'],
                "status": "FAIL",
                "result": None,
                "execution_time": time.time() - service_start,
                "error": str(e)
            }
            results["test_summary"]["services_failed"] += 1
            print(f"❌ FAIL: {str(e)}")
        
        results["service_results"].append(service_result)
        results["test_summary"]["services_tested"] += 1
    
    # Generate summary
    results["test_summary"]["end_time"] = time.time()
    results["test_summary"]["total_execution_time"] = results["test_summary"]["end_time"] - results["test_summary"]["start_time"]
    
    print("\n" + "=" * 80)
    print("📊 MCP SERVICES TEST SUMMARY (FIXED)")
    print("=" * 80)
    print(f"Total Services: {results['test_summary']['total_services']}")
    print(f"✅ Passed: {results['test_summary']['services_passed']}")
    print(f"❌ Failed: {results['test_summary']['services_failed']}")
    print(f"📈 Pass Rate: {(results['test_summary']['services_passed']/results['test_summary']['total_services'])*100:.1f}%")
    print(f"⏱️  Total Time: {results['test_summary']['total_execution_time']:.2f}s")
    
    # Save results
    with open("mcp_services_fixed_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: mcp_services_fixed_test_results.json")
    
    return results

def test_identity_service_fixed():
    """Test Identity Service with correct signatures"""
    try:
        from src.core.identity_service import IdentityService
        
        service = IdentityService()
        
        # Test create mention with correct signature
        result = service.create_mention(
            surface_form="Test Entity",
            start_pos=0,
            end_pos=11,
            source_ref="test_doc",
            entity_type="TEST",
            confidence=0.8
        )
        
        mention_id = result.get('mention_id')
        if not mention_id:
            raise Exception("No mention_id returned")
        
        # Test get entity by mention
        entity = service.get_entity_by_mention(mention_id)
        if not entity:
            raise Exception("Could not retrieve entity by mention")
        
        entity_id = entity.get('entity_id')
        
        # Test get mentions for entity
        mentions = service.get_mentions_for_entity(entity_id)
        if not isinstance(mentions, list):
            raise Exception("get_mentions_for_entity did not return list")
        
        # Test get stats
        stats = service.get_stats()
        if not isinstance(stats, dict):
            raise Exception("get_stats did not return dict")
        
        return f"Identity Service working: {stats.get('entity_count', 0)} entities, {stats.get('mention_count', 0)} mentions"
        
    except Exception as e:
        raise Exception(f"Identity Service test failed: {str(e)}")

def test_provenance_service_fixed():
    """Test Provenance Service with correct signatures"""
    try:
        from src.core.provenance_service import ProvenanceService
        
        service = ProvenanceService()
        
        # Test start operation with correct signature
        operation_id = service.start_operation(
            tool_id="test_tool",
            operation_type="test",
            inputs=["test_input"],
            parameters={"test": "data"}
        )
        
        if not operation_id:
            raise Exception("No operation_id returned")
        
        # Test complete operation
        completion = service.complete_operation(
            operation_id=operation_id,
            outputs=["test_output"],
            success=True
        )
        
        if not completion:
            raise Exception("Operation completion failed")
        
        # Test get operation
        op_details = service.get_operation(operation_id)
        if not op_details:
            raise Exception("Could not retrieve operation details")
        
        # Test get tool statistics
        stats = service.get_tool_statistics()
        if not isinstance(stats, dict):
            raise Exception("get_tool_statistics did not return dict")
        
        return f"Provenance Service working: operation {operation_id[:8]}... tracked"
        
    except Exception as e:
        raise Exception(f"Provenance Service test failed: {str(e)}")

def test_quality_service_fixed():
    """Test Quality Service with correct signatures"""
    try:
        from src.core.quality_service import QualityService
        
        service = QualityService()
        
        # Test assess confidence with correct signature
        assessment = service.assess_confidence(
            source_tool="test_tool",
            object_ref="test_object",
            base_confidence=0.8,
            context={"source": "test"}
        )
        
        confidence = assessment.get('confidence')
        if confidence is None:
            raise Exception("No confidence returned")
        
        # Test get quality statistics
        stats = service.get_quality_statistics()
        if not isinstance(stats, dict):
            raise Exception("get_quality_statistics did not return dict")
        
        return f"Quality Service working: confidence {confidence:.2f}, {stats.get('total_assessments', 0)} assessments"
        
    except Exception as e:
        raise Exception(f"Quality Service test failed: {str(e)}")

def test_workflow_service_fixed():
    """Test Workflow State Service with correct signatures"""
    try:
        from src.core.workflow_state_service import WorkflowStateService
        import tempfile
        
        # Create temp directory for test
        with tempfile.TemporaryDirectory() as temp_dir:
            service = WorkflowStateService(temp_dir)
            
            # Test start workflow with correct signature
            workflow_id = service.start_workflow(
                name="test_workflow",
                description="Test workflow"
            )
            
            if not workflow_id:
                raise Exception("No workflow_id returned")
            
            # Test create checkpoint
            checkpoint_id = service.create_checkpoint(
                workflow_id=workflow_id,
                stage="test_stage",
                data={"test": "data"}
            )
            
            if not checkpoint_id:
                raise Exception("No checkpoint_id returned")
            
            # Test get workflow status
            status = service.get_workflow_status(workflow_id)
            if not status:
                raise Exception("Could not get workflow status")
            
            # Test get service statistics
            stats = service.get_service_statistics()
            if not isinstance(stats, dict):
                raise Exception("get_service_statistics did not return dict")
            
            return f"Workflow Service working: {stats.get('total_workflows', 0)} workflows"
        
    except Exception as e:
        raise Exception(f"Workflow Service test failed: {str(e)}")

def test_vertical_slice_fixed():
    """Test Vertical Slice Workflow"""
    try:
        from src.core.pipeline_orchestrator import PipelineOrchestrator
        import tempfile
        
        with tempfile.TemporaryDirectory() as temp_dir:
            workflow = VerticalSliceWorkflow(workflow_storage_dir=temp_dir)
            
            # Test get tool info
            info = workflow.get_tool_info()
            if not isinstance(info, dict):
                raise Exception("get_tool_info did not return dict")
            
            # Test workflow can be created and has expected methods
            expected_methods = ['execute_workflow', 'get_workflow_status', 'close']
            for method in expected_methods:
                if not hasattr(workflow, method):
                    raise Exception(f"Missing method: {method}")
            
            workflow.close()
            
            return f"Vertical Slice Workflow working: {info.get('name', 'unknown')} with {len(expected_methods)} methods"
        
    except Exception as e:
        raise Exception(f"Vertical Slice Workflow test failed: {str(e)}")

def test_phase1_mcp_tools_fixed():
    """Test Phase 1 MCP Tools creation with correct signature"""
    try:
        from src.tools.phase1.phase1_mcp_tools import create_phase1_mcp_tools
        
        # Test tool creation without parameters first
        tools = create_phase1_mcp_tools()
        
        if not tools:
            raise Exception("No tools created")
        
        if not hasattr(tools, 'load_pdf'):
            raise Exception("Missing load_pdf method")
        
        # Test get tool registry
        registry = tools.get_phase1_tool_registry()
        if not isinstance(registry, dict):
            raise Exception("get_phase1_tool_registry did not return dict")
        
        tool_count = len(registry.get('tools', []))
        
        return f"Phase 1 MCP Tools working: {tool_count} tools available"
        
    except Exception as e:
        raise Exception(f"Phase 1 MCP Tools test failed: {str(e)}")

if __name__ == "__main__":
    results = test_mcp_services_fixed()
    
    # Exit with error code if any tests failed
    if results["test_summary"]["services_failed"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)