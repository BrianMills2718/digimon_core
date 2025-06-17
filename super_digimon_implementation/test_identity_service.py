#!/usr/bin/env python
"""Test identity service initialization."""

import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

print("=== TESTING IDENTITY SERVICE ===\n")

# Initialize database
from src.utils.database import DatabaseManager
db = DatabaseManager()
db.faiss.dimension = 384
db.initialize()

# Clear
with db.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")

# Test getting identity service
print("Getting identity service...")
start = time.time()
try:
    identity = db.get_identity_service()
    elapsed = time.time() - start
    print(f"✓ Got identity service ({elapsed:.2f}s)")
except Exception as e:
    elapsed = time.time() - start
    print(f"✗ Failed to get identity service after {elapsed:.2f}s: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test creating an entity
print("\nTesting entity creation...")
start = time.time()
try:
    result = identity.create_or_link_entity(
        surface_form="Microsoft",
        entity_type="ORG",
        attributes={"test": True}
    )
    elapsed = time.time() - start
    print(f"✓ Created entity ({elapsed:.2f}s)")
    print(f"  Entity ID: {result['entity'].id}")
    print(f"  Action: {result['action']}")
except Exception as e:
    elapsed = time.time() - start
    print(f"✗ Failed to create entity after {elapsed:.2f}s: {e}")
    import traceback
    traceback.print_exc()

# Cleanup
with db.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")
db.close()

print("\n✅ Test complete!")