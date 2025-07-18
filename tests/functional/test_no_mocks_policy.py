#!/usr/bin/env python3
"""
Test NO MOCKS Policy Compliance

Verifies that all Phase 1 tools properly fail when Neo4j is unavailable,
following the NO MOCKS policy from CLAUDE.md.

This test ensures:
1. No mock data is returned when dependencies fail
2. Clear error messages with recovery suggestions are provided
3. Tools fail honestly instead of pretending to work
"""

import os
from pathlib import Path

# Add src to path for imports

from core.identity_service import IdentityService
from core.provenance_service import ProvenanceService
from core.quality_service import QualityService
from tools.phase1.t31_entity_builder import EntityBuilder
from tools.phase1.t34_edge_builder import EdgeBuilder
from tools.phase1.t49_multihop_query import MultiHopQuery
from tools.phase1.t68_pagerank import PageRankCalculator


def test_no_mocks_policy_compliance():
    """Test that all tools fail properly when Neo4j is unavailable."""
    print("=" * 80)
    print("🧪 NO MOCKS POLICY COMPLIANCE TEST")
    print("=" * 80)
    print("Testing: Tools fail clearly when Neo4j is unavailable")
    print("Policy: When Neo4j is down, fail clearly - don't pretend to work")
    print()
    
    # Initialize services
    identity_service = IdentityService()
    provenance_service = ProvenanceService()
    quality_service = QualityService()
    
    # Use invalid Neo4j connection to simulate unavailability
    invalid_uri = "bolt://localhost:9999"  # Non-existent port
    
    results = {
        "tools_tested": 0,
        "compliant": 0,
        "violations": [],
        "details": {}
    }
    
    # Test T31: EntityBuilder
    print("🔍 Testing T31: EntityBuilder...")
    try:
        entity_builder = EntityBuilder(
            identity_service, provenance_service, quality_service,
            neo4j_uri=invalid_uri
        )
        
        # Try to build entities - should fail with proper error
        result = entity_builder.build_entities(
            mentions=[{"mention_text": "test", "entity_type": "TEST"}],
            source_refs=["test_ref"]
        )
        
        results["tools_tested"] += 1
        if validate_error_response(result, "T31_EntityBuilder"):
            results["compliant"] += 1
            print("✅ T31: EntityBuilder - COMPLIANT")
        else:
            results["violations"].append("T31_EntityBuilder")
            print("❌ T31: EntityBuilder - VIOLATION")
        
        results["details"]["T31_EntityBuilder"] = result
        
    except Exception as e:
        print(f"❌ T31: EntityBuilder - EXCEPTION: {e}")
        results["violations"].append("T31_EntityBuilder")
    
    # Test T34: EdgeBuilder
    print("\n🔍 Testing T34: EdgeBuilder...")
    try:
        edge_builder = EdgeBuilder(
            identity_service, provenance_service, quality_service,
            neo4j_uri=invalid_uri
        )
        
        # Try to build edges - should fail with proper error
        result = edge_builder.build_edges(
            relationships=[{
                "relationship_id": "test_rel",
                "subject_entity_id": "e1",
                "object_entity_id": "e2",
                "relationship_type": "RELATED_TO",
                "confidence": 0.8
            }],
            source_refs=["test_ref"]
        )
        
        results["tools_tested"] += 1
        if validate_error_response(result, "T34_EdgeBuilder"):
            results["compliant"] += 1
            print("✅ T34: EdgeBuilder - COMPLIANT")
        else:
            results["violations"].append("T34_EdgeBuilder")
            print("❌ T34: EdgeBuilder - VIOLATION")
        
        results["details"]["T34_EdgeBuilder"] = result
        
    except Exception as e:
        print(f"❌ T34: EdgeBuilder - EXCEPTION: {e}")
        results["violations"].append("T34_EdgeBuilder")
    
    # Test T49: MultiHopQuery
    print("\n🔍 Testing T49: MultiHopQuery...")
    try:
        query_engine = MultiHopQuery(
            identity_service, provenance_service, quality_service,
            neo4j_uri=invalid_uri
        )
        
        # Try to query - should fail with proper error
        result = query_engine.query_graph("What is the test?")
        
        results["tools_tested"] += 1
        if validate_error_response(result, "T49_MultiHopQuery"):
            results["compliant"] += 1
            print("✅ T49: MultiHopQuery - COMPLIANT")
        else:
            results["violations"].append("T49_MultiHopQuery")
            print("❌ T49: MultiHopQuery - VIOLATION")
        
        results["details"]["T49_MultiHopQuery"] = result
        
    except Exception as e:
        print(f"❌ T49: MultiHopQuery - EXCEPTION: {e}")
        results["violations"].append("T49_MultiHopQuery")
    
    # Test T68: PageRankCalculator
    print("\n🔍 Testing T68: PageRankCalculator...")
    try:
        pagerank_calc = PageRankCalculator(
            identity_service, provenance_service, quality_service,
            neo4j_uri=invalid_uri
        )
        
        # Try to calculate PageRank - should fail with proper error
        result = pagerank_calc.calculate_pagerank()
        
        results["tools_tested"] += 1
        if validate_error_response(result, "T68_PageRankCalculator"):
            results["compliant"] += 1
            print("✅ T68: PageRankCalculator - COMPLIANT")
        else:
            results["violations"].append("T68_PageRankCalculator")
            print("❌ T68: PageRankCalculator - VIOLATION")
        
        results["details"]["T68_PageRankCalculator"] = result
        
    except Exception as e:
        print(f"❌ T68: PageRankCalculator - EXCEPTION: {e}")
        results["violations"].append("T68_PageRankCalculator")
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 NO MOCKS POLICY COMPLIANCE SUMMARY")
    print("=" * 80)
    print(f"Tools tested: {results['tools_tested']}")
    print(f"Compliant: {results['compliant']}")
    print(f"Violations: {len(results['violations'])}")
    
    if results['violations']:
        print("\n⚠️  VIOLATIONS FOUND:")
        for tool in results['violations']:
            print(f"  - {tool}")
            if tool in results['details']:
                print(f"    Response: {results['details'][tool]}")
    
    # Final verdict
    print("\n" + "=" * 80)
    if len(results['violations']) == 0:
        print("✅ SUCCESS: All tools comply with NO MOCKS policy")
        print("   Tools fail clearly when Neo4j is unavailable")
        return True
    else:
        print("❌ FAILURE: Some tools violate NO MOCKS policy")
        print("   Tools are returning mock data or not failing properly")
        return False


def validate_error_response(response: dict, tool_name: str) -> bool:
    """Validate that the response is a proper error following NO MOCKS policy."""
    
    # Check status is error
    if response.get("status") != "error":
        print(f"  ⚠️  {tool_name}: Status is '{response.get('status')}' not 'error'")
        return False
    
    # Check for clear error message
    if not response.get("error"):
        print(f"  ⚠️  {tool_name}: No error message provided")
        return False
    
    # Check for recovery suggestions
    if not response.get("recovery_suggestions"):
        print(f"  ⚠️  {tool_name}: No recovery suggestions provided")
        return False
    
    # Check that no mock data is included
    mock_indicators = ["mock", "fake", "placeholder", "dummy"]
    response_str = str(response).lower()
    for indicator in mock_indicators:
        if indicator in response_str and "no mocks" not in response_str:
            print(f"  ⚠️  {tool_name}: Response contains mock indicator '{indicator}'")
            return False
    
    # Check that it's not returning success with empty data
    if "results" in response or "edges" in response or "entities" in response:
        print(f"  ⚠️  {tool_name}: Response contains data fields despite error status")
        return False
    
    return True


def main():
    """Run the NO MOCKS policy compliance test."""
    print("Starting NO MOCKS Policy Compliance Test...")
    print("This test verifies tools fail properly when Neo4j is unavailable")
    print()
    
    success = test_no_mocks_policy_compliance()
    
    if success:
        print("\n✅ NO MOCKS policy is properly implemented")
        return 0
    else:
        print("\n❌ NO MOCKS policy violations detected")
        print("Tools must fail clearly when dependencies are unavailable")
        return 1


if __name__ == "__main__":
    exit(main())