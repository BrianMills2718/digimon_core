#!/usr/bin/env python3
"""
Test KGAS graph tools after Neo4j configuration fix
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.tools.phase1.t68_pagerank_calculator_unified import T68PageRankCalculatorUnified
from src.tools.phase1.t49_multihop_query_unified import T49MultiHopQueryUnified
from src.core.service_manager import get_service_manager
from src.tools.base_tool import ToolRequest
from neo4j import GraphDatabase

def add_test_data():
    """Add test data to Neo4j"""
    print("📝 Adding test data to Neo4j...")
    
    try:
        driver = GraphDatabase.driver(
            "bolt://localhost:7687",
            auth=("neo4j", "testpassword")
        )
        
        with driver.session() as session:
            # Clear existing data
            session.run("MATCH (n) DETACH DELETE n")
            
            # Add test entities and relationships from the academic paper
            session.run("""
                CREATE (alex:Person {name: 'Alex Mintz', affiliation: 'Texas A&M University'})
                CREATE (theory:Theory {name: 'Poliheuristic Theory', type: 'Decision Making'})
                CREATE (carter:Person {name: 'Jimmy Carter', role: 'President'})
                CREATE (clinton:Person {name: 'Bill Clinton', role: 'President'})
                CREATE (texas:Organization {name: 'Texas A&M University', type: 'University'})
                CREATE (yale:Organization {name: 'Yale University', type: 'University'})
                CREATE (decision:Concept {name: 'Two-Stage Decision Process', type: 'Process'})
                CREATE (heuristic:Concept {name: 'Non-Compensatory Principle', type: 'Heuristic'})
                
                CREATE (alex)-[:DEVELOPED]->(theory)
                CREATE (alex)-[:AFFILIATED_WITH]->(texas)
                CREATE (alex)-[:AFFILIATED_WITH]->(yale)
                CREATE (theory)-[:APPLIED_TO]->(carter)
                CREATE (theory)-[:APPLIED_TO]->(clinton)
                CREATE (theory)-[:USES]->(decision)
                CREATE (theory)-[:INCORPORATES]->(heuristic)
                CREATE (decision)-[:INCLUDES]->(heuristic)
            """)
            
            # Verify data was added
            count_result = session.run("MATCH (n) RETURN count(n) as node_count")
            node_count = count_result.single()["node_count"]
            print(f"✅ Added test data: {node_count} nodes created")
            
            rel_result = session.run("MATCH ()-[r]->() RETURN count(r) as rel_count")
            rel_count = rel_result.single()["rel_count"]
            print(f"✅ Added test data: {rel_count} relationships created")
            
        driver.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to add test data: {e}")
        return False

def test_pagerank():
    """Test PageRank calculation"""
    print("\n🧮 Testing PageRank calculation...")
    
    try:
        service_manager = get_service_manager()
        pagerank_tool = T68PageRankCalculatorUnified(service_manager)
        
        request = ToolRequest(
            tool_id="T68",
            operation="calculate_pagerank",
            input_data={},
            parameters={}
        )
        
        print("🔄 Executing PageRank calculation...")
        result = pagerank_tool.execute(request)
        
        if result.status == "success":
            print("✅ PageRank calculation successful!")
            print(f"📊 Results summary: {len(result.data.get('pagerank_scores', {}))} nodes ranked")
            
            # Show top-ranked entities
            scores = result.data.get('pagerank_scores', {})
            if scores:
                sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
                print("🏆 Top-ranked entities:")
                for entity, score in sorted_scores[:5]:
                    print(f"   • {entity}: {score:.4f}")
            
            print(f"⏱️ Execution time: {result.execution_time:.3f}s")
            return True
        else:
            print(f"❌ PageRank failed: {result.error_code} - {result.error_message}")
            return False
            
    except Exception as e:
        print(f"❌ PageRank test failed: {e}")
        return False

def test_graph_query():
    """Test graph query"""
    print("\n🔍 Testing graph query...")
    
    try:
        service_manager = get_service_manager()
        query_tool = T49MultiHopQueryUnified(service_manager)
        
        request = ToolRequest(
            tool_id="T49",
            operation="query_graph",
            input_data={"query_text": "What theories did Alex Mintz develop?"},
            parameters={}
        )
        
        print("🔄 Executing graph query...")
        result = query_tool.execute(request)
        
        if result.status == "success":
            print("✅ Graph query successful!")
            print(f"📊 Query results: {result.data}")
            print(f"⏱️ Execution time: {result.execution_time:.3f}s")
            return True
        else:
            print(f"❌ Graph query failed: {result.error_code} - {result.error_message}")
            return False
            
    except Exception as e:
        print(f"❌ Graph query test failed: {e}")
        return False

def main():
    print("🧪 Testing KGAS Graph Tools After Configuration Fix")
    print("=" * 60)
    
    # Add test data
    if not add_test_data():
        print("❌ Could not add test data. Exiting.")
        return False
    
    # Test PageRank
    pagerank_success = test_pagerank()
    
    # Test graph query
    query_success = test_graph_query()
    
    # Final summary
    print("\n" + "=" * 60)
    print("🏁 FINAL TEST RESULTS:")
    print(f"   PageRank Tool: {'✅ Working' if pagerank_success else '❌ Failed'}")
    print(f"   Graph Query Tool: {'✅ Working' if query_success else '❌ Failed'}")
    
    if pagerank_success and query_success:
        print("\n🎉 SUCCESS: All graph tools are now working with Neo4j!")
        print("📊 KGAS comprehensive testing is now COMPLETE!")
        return True
    else:
        print("\n⚠️ Some tools still need fixes.")
        return False

if __name__ == "__main__":
    main()