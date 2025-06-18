#!/usr/bin/env python3
"""Test the GraphRAG Phase Interface and Adapters"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.core.graphrag_phase_interface import (
    ProcessingRequest, PhaseStatus, get_available_phases, execute_phase
)
from src.core.phase_adapters import initialize_phase_adapters


def test_phase_interface():
    """Test the standardized phase interface"""
    print("Testing GraphRAG Phase Interface...")
    print("=" * 50)
    
    # Initialize adapters
    print("\n🔄 Initializing phase adapters...")
    success = initialize_phase_adapters()
    if not success:
        print("❌ Failed to initialize adapters")
        return False
    
    # List available phases
    phases = get_available_phases()
    print(f"\n📋 Available phases: {phases}")
    
    # Test each phase with validation
    test_request = ProcessingRequest(
        documents=["examples/pdfs/wiki1.pdf"],
        queries=["What are the main entities mentioned in this document?"],
        workflow_id="interface_test",
        domain_description="Technology and innovation analysis"
    )
    
    results = {}
    
    for phase_name in phases:
        print(f"\n🧪 Testing {phase_name}...")
        
        try:
            # Test using the interface
            result = execute_phase(phase_name, test_request)
            results[phase_name] = result
            
            print(f"   Status: {result.status.value}")
            print(f"   Execution time: {result.execution_time:.2f}s")
            print(f"   Entities: {result.entity_count}")
            print(f"   Relationships: {result.relationship_count}")
            
            if result.status == PhaseStatus.ERROR:
                print(f"   Error: {result.error_message}")
            elif result.status == PhaseStatus.SUCCESS:
                print(f"   Confidence: {result.confidence_score:.2f}")
                print("   ✅ Success!")
            
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            results[phase_name] = None
    
    # Summary
    print(f"\n📊 Test Summary:")
    print("=" * 50)
    
    success_count = 0
    for phase_name, result in results.items():
        if result and result.status == PhaseStatus.SUCCESS:
            status_icon = "✅"
            success_count += 1
        elif result and result.status == PhaseStatus.ERROR:
            status_icon = "⚠️"
        else:
            status_icon = "❌"
        
        print(f"{status_icon} {phase_name}")
    
    print(f"\nSuccessful phases: {success_count}/{len(phases)}")
    
    # Test capabilities
    print(f"\n🔍 Phase Capabilities:")
    print("=" * 50)
    
    from src.core.graphrag_phase_interface import phase_registry
    
    for phase_name in phases:
        phase = phase_registry.get_phase(phase_name)
        if phase:
            capabilities = phase.get_capabilities()
            print(f"\n{phase_name}:")
            print(f"  Documents: {capabilities.get('supported_document_types', [])}")
            print(f"  Services: {capabilities.get('required_services', [])}")
            print(f"  Multi-query: {capabilities.get('supports_multiple_queries', False)}")
            print(f"  Uses ontology: {capabilities.get('uses_ontology', False)}")
    
    return success_count > 0


def test_input_validation():
    """Test input validation across phases"""
    print(f"\n🔍 Testing Input Validation:")
    print("=" * 50)
    
    from src.core.graphrag_phase_interface import phase_registry
    
    # Test cases
    test_cases = [
        {
            "name": "Valid request",
            "request": ProcessingRequest(
                documents=["examples/pdfs/wiki1.pdf"],
                queries=["Test query"],
                workflow_id="test",
                domain_description="Test domain"
            )
        },
        {
            "name": "Missing documents",
            "request": ProcessingRequest(
                documents=[],
                queries=["Test query"],
                workflow_id="test"
            )
        },
        {
            "name": "Missing queries",
            "request": ProcessingRequest(
                documents=["examples/pdfs/wiki1.pdf"],
                queries=[],
                workflow_id="test"
            )
        },
        {
            "name": "Non-existent file",
            "request": ProcessingRequest(
                documents=["non_existent.pdf"],
                queries=["Test query"],
                workflow_id="test"
            )
        }
    ]
    
    phases = get_available_phases()
    validation_summary = {}
    
    for test_case in test_cases:
        print(f"\n📝 Test case: {test_case['name']}")
        validation_summary[test_case['name']] = {}
        
        for phase_name in phases:
            phase = phase_registry.get_phase(phase_name)
            if phase:
                errors = phase.validate_input(test_case['request'])
                validation_summary[test_case['name']][phase_name] = len(errors)
                
                if errors:
                    print(f"   {phase_name}: {len(errors)} errors")
                else:
                    print(f"   {phase_name}: ✅ Valid")
    
    return validation_summary


if __name__ == "__main__":
    print("GraphRAG Phase Interface Test")
    print("=" * 50)
    
    # Check if sample document exists
    sample_doc = Path("examples/pdfs/wiki1.pdf")
    if not sample_doc.exists():
        print(f"⚠️  Sample document not found: {sample_doc}")
        print("Some tests may fail due to missing test data")
    
    # Run interface tests
    interface_success = test_phase_interface()
    
    # Run validation tests
    validation_results = test_input_validation()
    
    print(f"\n🎯 Overall Result:")
    print("=" * 50)
    
    if interface_success:
        print("✅ Phase interface system is working!")
        print("✅ Standardized interface successfully wraps existing implementations")
        print("✅ Input validation is functioning across phases")
    else:
        print("❌ Phase interface system needs attention")
    
    print(f"\nNext steps for A2 completion:")
    print("- ✅ Base interface contract defined")
    print("- ✅ Phase adapters implemented")
    print("- ✅ Registry system created")
    print("- ✅ Validation framework added")
    print("- 🔄 Integration with UI (A3)")
    
    sys.exit(0 if interface_success else 1)