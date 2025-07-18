#!/usr/bin/env python3
"""
Ensure Neo4j - Automated Neo4j Setup Script

Run this script to automatically start Neo4j if needed.
Can be called from other scripts or run standalone.
"""

from pathlib import Path

# Add src to path

from core.neo4j_manager import Neo4jDockerManager


def main():
    """Ensure Neo4j is running"""
    print("🔧 Neo4j Auto-Setup Script")
    print("=" * 40)
    
    manager = Neo4jDockerManager()
    result = manager.ensure_neo4j_available()
    
    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")
    
    if result["status"] in ["available", "started"]:
        print("\n✅ Neo4j is ready for GraphRAG operations")
        print(f"   Connection: {manager.bolt_uri}")
        print(f"   Credentials: {manager.username}/{manager.password}")
        return 0
    else:
        print("\n❌ Neo4j setup failed")
        print("   Manual setup may be required")
        return 1


if __name__ == "__main__":
    exit(main())