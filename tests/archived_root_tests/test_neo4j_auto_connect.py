#!/usr/bin/env python3
"""
Test automatic Neo4j connection discovery
"""

import os
from src.core.neo4j_config import get_neo4j_config, ensure_neo4j_connection

def test_auto_connection():
    """Test the automatic Neo4j connection"""
    print("🔍 TESTING AUTOMATIC NEO4J CONNECTION")
    print("=" * 60)
    
    # Clear any existing environment variables to test discovery
    for key in ["NEO4J_URI", "NEO4J_USER", "NEO4J_PASSWORD"]:
        if key in os.environ:
            del os.environ[key]
    
    # Get the Neo4j configuration
    print("1️⃣ Attempting automatic Neo4j discovery...")
    config = get_neo4j_config()
    
    # Check status
    status = config.get_status()
    
    if status["connected"]:
        print("\n✅ AUTOMATIC CONNECTION SUCCESSFUL!")
        print(f"   • Source: {status['source']}")
        print(f"   • URI: {status['uri']}")
        print(f"   • User: {status['user']}")
        print(f"   • Nodes in database: {status['node_count']}")
        
        if status.get('container'):
            print(f"   • Docker container: {status['container']}")
        
        # Now test with KGAS tools
        print("\n2️⃣ Testing KGAS tools with auto-connected Neo4j...")
        
        from src.core.service_manager import get_service_manager
        from src.tools.phase1.t31_entity_builder import EntityBuilder
        from src.tools.base_tool import ToolRequest
        
        service_manager = get_service_manager()
        entity_builder = EntityBuilder(service_manager)
        
        # Quick test
        test_mention = [{
            'mention_id': 'auto_test_001',
            'entity_id': 'entity_auto_test',
            'surface_form': 'Auto Test Entity',
            'entity_type': 'TEST',
            'confidence': 0.99,
            'source_ref': 'auto_test',
            'text': 'Auto Test Entity',
            'label': 'TEST'
        }]
        
        request = ToolRequest(
            tool_id="T31",
            operation="build_entities",
            input_data={
                "mentions": test_mention,
                "source_refs": ["auto_test"]
            },
            parameters={}
        )
        
        result = entity_builder.execute(request)
        if result.status == "success":
            print("   ✅ T31 Entity Builder works with auto-connection!")
        else:
            print(f"   ❌ T31 failed: {result.error_message}")
        
        # Show connection info for Neo4j tool
        neo4j_status = entity_builder.get_neo4j_status()
        print(f"\n3️⃣ Neo4j tool status:")
        print(f"   • Connected: {neo4j_status.get('connected', False)}")
        print(f"   • Node count: {neo4j_status.get('node_count', 0)}")
        print(f"   • Driver owned by tool: {neo4j_status.get('driver_owned', 'unknown')}")
        
        print("\n✅ AUTOMATIC NEO4J CONNECTION IS WORKING!")
        print("\nFrom now on, KGAS will automatically:")
        print("• Check environment variables")
        print("• Check .env file")
        print("• Find running Docker containers")
        print("• Try common passwords")
        print("• Connect without manual configuration!")
        
    else:
        print("\n❌ Automatic connection failed")
        print("\nThe system tried:")
        print("• Environment variables")
        print("• .env file")
        print("• Docker containers")
        print("• Common passwords on localhost")
        print("\nPlease follow the setup instructions provided above.")

def test_ensure_connection():
    """Test the ensure_neo4j_connection helper"""
    print("\n\n🔗 TESTING ENSURE CONNECTION HELPER")
    print("=" * 60)
    
    if ensure_neo4j_connection():
        print("✅ ensure_neo4j_connection() returned True")
        print("   Neo4j is ready for use!")
    else:
        print("❌ ensure_neo4j_connection() returned False")
        print("   Neo4j setup required")

if __name__ == "__main__":
    test_auto_connection()
    test_ensure_connection()