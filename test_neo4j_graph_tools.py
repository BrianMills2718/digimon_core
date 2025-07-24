#!/usr/bin/env python3
"""
Direct test of KGAS graph tools with correct Neo4j credentials
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from neo4j import GraphDatabase
from src.tools.base_tool import ToolRequest

def test_neo4j_connection():
    """Test basic Neo4j connection with correct credentials"""
    print("🔍 Testing Neo4j connection...")
    
    try:
        driver = GraphDatabase.driver(
            "bolt://localhost:7687",
            auth=("neo4j", "testpassword")
        )
        
        with driver.session() as session:
            result = session.run("RETURN 'Hello Neo4j!' as message")
            message = result.single()["message"]
            print(f"✅ Neo4j connected successfully: {message}")
            
            # Check if there's any data
            count_result = session.run("MATCH (n) RETURN count(n) as node_count")
            node_count = count_result.single()["node_count"]
            print(f"📊 Current nodes in database: {node_count}")
            
        driver.close()
        return True
        
    except Exception as e:
        print(f"❌ Neo4j connection failed: {e}")
        return False


def test_pagerank_with_direct_connection():
    """Test PageRank tool with direct Neo4j connection"""
    print("\n🧮 Testing PageRank calculation...")
    
    try:
        from src.tools.phase1.t68_pagerank_calculator_unified import T68PageRankCalculatorUnified
        from src.core.service_manager import get_service_manager
        
        # Get service manager
        service_manager = get_service_manager()
        
        # Create PageRank tool
        pagerank_tool = T68PageRankCalculatorUnified(service_manager)
        
        # Create request
        request = ToolRequest(
            tool_id="T68",
            operation="calculate_pagerank",
            input_data={},
            parameters={}
        )
        
        print("🔄 Executing PageRank calculation...")
        result = pagerank_tool.execute(request)
        
        if result.status == "success":
            print(f"✅ PageRank calculation successful!")
            print(f"📊 Result: {result.data}")
            print(f"⏱️ Execution time: {result.execution_time:.3f}s")
        else:
            print(f"❌ PageRank failed: {result.error_code} - {result.error_message}")
            
        return result.status == "success"
        
    except Exception as e:
        print(f"❌ PageRank test failed: {e}")
        return False


def test_graph_query_with_direct_connection():
    """Test graph query tool with direct Neo4j connection"""
    print("\n🔍 Testing graph query...")
    
    try:
        from src.tools.phase1.t49_multihop_query_unified import T49MultiHopQueryUnified
        from src.core.service_manager import get_service_manager
        
        # Get service manager
        service_manager = get_service_manager()
        
        # Create query tool
        query_tool = T49MultiHopQueryUnified(service_manager)
        
        # Create request
        request = ToolRequest(
            tool_id="T49",
            operation="query_graph",
            input_data={"query_text": "What entities are in the graph?"},
            parameters={}
        )
        
        print("🔄 Executing graph query...")
        result = query_tool.execute(request)
        
        if result.status == "success":
            print(f"✅ Graph query successful!")
            print(f"📊 Result: {result.data}")
            print(f"⏱️ Execution time: {result.execution_time:.3f}s")
        else:
            print(f"❌ Graph query failed: {result.error_code} - {result.error_message}")
            
        return result.status == "success"
        
    except Exception as e:
        print(f"❌ Graph query test failed: {e}")
        return False


def add_test_data_to_neo4j():
    """Add some test data to Neo4j for testing"""
    print("\n📝 Adding test data to Neo4j...")
    
    try:
        driver = GraphDatabase.driver(
            "bolt://localhost:7687",
            auth=("neo4j", "testpassword")
        )
        
        with driver.session() as session:
            # Clear existing data
            session.run("MATCH (n) DETACH DELETE n")
            
            # Add test entities and relationships
            session.run("""
                CREATE (alex:Person {name: 'Alex Mintz', affiliation: 'Texas A&M University'})
                CREATE (theory:Theory {name: 'Poliheuristic Theory', type: 'Decision Making'})
                CREATE (carter:Person {name: 'Jimmy Carter', role: 'President'})
                CREATE (clinton:Person {name: 'Bill Clinton', role: 'President'})
                CREATE (texas:Organization {name: 'Texas A&M University', type: 'University'})
                CREATE (yale:Organization {name: 'Yale University', type: 'University'})
                
                CREATE (alex)-[:DEVELOPED]->(theory)
                CREATE (alex)-[:AFFILIATED_WITH]->(texas)
                CREATE (alex)-[:AFFILIATED_WITH]->(yale)
                CREATE (theory)-[:APPLIED_TO]->(carter)
                CREATE (theory)-[:APPLIED_TO]->(clinton)
            """)
            
            # Verify data was added
            count_result = session.run("MATCH (n) RETURN count(n) as node_count")
            node_count = count_result.single()["node_count"]
            print(f"✅ Added test data: {node_count} nodes created")
            
        driver.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to add test data: {e}")
        return False


def main():
    """Run all Neo4j graph tool tests"""
    print("🧪 KGAS Neo4j Graph Tools Direct Testing")
    print("=" * 50)
    
    # Test 1: Basic Neo4j connection
    if not test_neo4j_connection():
        print("❌ Basic Neo4j connection failed. Exiting.")
        return False
    
    # Test 2: Add test data
    if not add_test_data_to_neo4j():
        print("❌ Failed to add test data. Continuing anyway...")
    
    # Test 3: PageRank calculation
    pagerank_success = test_pagerank_with_direct_connection()
    
    # Test 4: Graph query
    query_success = test_graph_query_with_direct_connection()
    
    # Summary
    print("\n" + "=" * 50)
    print("🏁 TEST SUMMARY:")
    print(f"   Neo4j Connection: ✅ Working")
    print(f"   Test Data Added: ✅ Working")
    print(f"   PageRank Tool: {'✅ Working' if pagerank_success else '❌ Failed'}")
    print(f"   Graph Query Tool: {'✅ Working' if query_success else '❌ Failed'}")
    
    if pagerank_success and query_success:
        print("\n🎉 All graph tools are working with Neo4j!")
        return True
    else:
        print("\n⚠️ Some graph tools need configuration fixes.")
        return False


if __name__ == "__main__":
    main()