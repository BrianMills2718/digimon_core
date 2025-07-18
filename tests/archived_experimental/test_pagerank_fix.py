#!/usr/bin/env python3
"""Test script to isolate and verify the PageRank error fix."""

import sys
import os

def test_pagerank_initialization():
    """Test that PageRank calculator initializes correctly with service objects."""
    try:
        # Import required services
        from src.core.identity_service import IdentityService
        from src.core.provenance_service import ProvenanceService
        from src.core.quality_service import QualityService
        from src.tools.phase1.t68_pagerank import PageRankCalculator
        
        print("✅ Successfully imported all required services and PageRankCalculator")
        
        # Initialize services
        identity_service = IdentityService()
        provenance_service = ProvenanceService()
        quality_service = QualityService()
        
        print("✅ Successfully initialized all services")
        print(f"  - Identity Service: {type(identity_service)}")
        print(f"  - Provenance Service: {type(provenance_service)}")
        print(f"  - Quality Service: {type(quality_service)}")
        
        # Test PageRank initialization with correct parameters
        pagerank_calculator = PageRankCalculator(
            identity_service=identity_service,
            provenance_service=provenance_service,
            quality_service=quality_service,
            neo4j_uri="bolt://localhost:7687",
            neo4j_user="neo4j",
            neo4j_password="password"
        )
        
        print("✅ Successfully initialized PageRankCalculator with service objects")
        print(f"  - PageRank Calculator: {type(pagerank_calculator)}")
        print(f"  - Has provenance_service: {hasattr(pagerank_calculator, 'provenance_service')}")
        print(f"  - Provenance service type: {type(pagerank_calculator.provenance_service)}")
        
        # Test calling calculate_pagerank (should not get 'str' object error)
        try:
            result = pagerank_calculator.calculate_pagerank()
            print("✅ Successfully called calculate_pagerank()")
            print(f"  - Result status: {result.get('status', 'unknown')}")
            if result.get('status') == 'error':
                print(f"  - Error (expected): {result.get('error', 'unknown')}")
            return True
            
        except AttributeError as e:
            if "'str' object has no attribute 'start_operation'" in str(e):
                print(f"❌ STILL GETTING 'str' object error: {e}")
                return False
            else:
                print(f"❌ Different AttributeError: {e}")
                return False
        except Exception as e:
            print(f"⚠️ Other error (may be expected): {e}")
            return True  # Other errors are expected if Neo4j isn't connected
            
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return False

def test_enhanced_workflow_pagerank_initialization():
    """Test that Enhanced Workflow initializes PageRank correctly."""
    try:
        from src.core.tool_factory import create_unified_workflow_config, Phase, OptimizationLevel
        
        print("\n✅ Successfully imported EnhancedVerticalSliceWorkflow")
        
        # Initialize workflow
        workflow = EnhancedVerticalSliceWorkflow()
        
        print("✅ Successfully initialized Enhanced Workflow")
        print(f"  - Workflow type: {type(workflow)}")
        print(f"  - Has pagerank_calculator: {hasattr(workflow, 'pagerank_calculator')}")
        
        if hasattr(workflow, 'pagerank_calculator'):
            pagerank_calc = workflow.pagerank_calculator
            print(f"  - PageRank Calculator type: {type(pagerank_calc)}")
            print(f"  - Has provenance_service: {hasattr(pagerank_calc, 'provenance_service')}")
            
            if hasattr(pagerank_calc, 'provenance_service'):
                print(f"  - Provenance service type: {type(pagerank_calc.provenance_service)}")
                
                # Check if it's a string (the bug) or a service object (fixed)
                if isinstance(pagerank_calc.provenance_service, str):
                    print("❌ BUG: provenance_service is a string!")
                    return False
                else:
                    print("✅ FIXED: provenance_service is a proper service object")
                    return True
            else:
                print("❌ PageRank calculator missing provenance_service")
                return False
        else:
            print("❌ Workflow missing pagerank_calculator")
            return False
            
    except Exception as e:
        print(f"❌ Failed to test Enhanced Workflow: {e}")
        return False

if __name__ == "__main__":
    print("🔍 TESTING PAGERANK INITIALIZATION FIX")
    print("=" * 50)
    
    # Test 1: Direct PageRank initialization
    print("\n📋 Test 1: Direct PageRank Initialization")
    test1_result = test_pagerank_initialization()
    
    # Test 2: Enhanced Workflow PageRank initialization  
    print("\n📋 Test 2: Enhanced Workflow PageRank Initialization")
    test2_result = test_enhanced_workflow_pagerank_initialization()
    
    # Summary
    print("\n" + "=" * 50)
    print("🎯 SUMMARY:")
    print(f"  - Direct PageRank test: {'✅ PASS' if test1_result else '❌ FAIL'}")
    print(f"  - Enhanced Workflow test: {'✅ PASS' if test2_result else '❌ FAIL'}")
    
    if test1_result and test2_result:
        print("🎉 ALL TESTS PASSED - PageRank initialization is FIXED!")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED - PageRank initialization still has issues")
        sys.exit(1)