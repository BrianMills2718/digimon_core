#!/usr/bin/env python3
"""
Test Provenance Persistence
Tests the new persistent provenance storage capability
"""
import sys
import os
sys.path.append('/home/brian/projects/Digimons')

from src.core.provenance_service import ProvenanceService
from datetime import datetime
import json

def test_provenance_persistence():
    """Test provenance persistence functionality"""
    
    print("🔍 TESTING PROVENANCE PERSISTENCE")
    print("=" * 60)
    
    # Test 1: Create service with persistence enabled
    print("\n1. Creating ProvenanceService with persistence enabled...")
    provenance = ProvenanceService(persistence_enabled=True, persistence_path="data/test_provenance.db")
    
    # Test 2: Create some operations
    print("\n2. Creating test operations...")
    
    # Operation 1: PDF loading
    op1_id = provenance.start_operation(
        operation_type="load_document",
        used={"file": "test.pdf"},
        agent_details={"tool_id": "T01", "name": "PDF Loader", "version": "1.0"},
        parameters={"format": "pdf", "extract_metadata": True}
    )
    print(f"   Created operation: {op1_id}")
    
    # Complete operation 1
    provenance.complete_operation(
        op1_id,
        outputs=["storage://document/doc123"],
        success=True,
        metadata={"pages": 10, "size_bytes": 1024000}
    )
    print(f"   Completed operation: {op1_id}")
    
    # Operation 2: Text chunking
    op2_id = provenance.start_operation(
        operation_type="chunk_text",
        used={"document": "storage://document/doc123"},
        agent_details={"tool_id": "T15A", "name": "Text Chunker"},
        parameters={"chunk_size": 512, "overlap": 50}
    )
    print(f"   Created operation: {op2_id}")
    
    # Complete operation 2
    provenance.complete_operation(
        op2_id,
        outputs=["storage://chunks/chunk1", "storage://chunks/chunk2", "storage://chunks/chunk3"],
        success=True,
        metadata={"chunk_count": 3}
    )
    print(f"   Completed operation: {op2_id}")
    
    # Test 3: Export data
    print("\n3. Exporting provenance data...")
    export_success = provenance.export_provenance_data("data/test_provenance_export.json")
    print(f"   Export successful: {export_success}")
    
    # Test 4: Create new service instance and verify persistence
    print("\n4. Creating new ProvenanceService instance to test persistence...")
    provenance2 = ProvenanceService(persistence_enabled=True, persistence_path="data/test_provenance.db")
    
    # Check if data was loaded
    print(f"   Operations loaded: {len(provenance2.operations)}")
    print(f"   Objects tracked: {len(provenance2.object_to_operations)}")
    
    # Verify specific operations
    print("\n5. Verifying persisted operations...")
    for op_id, operation in provenance2.operations.items():
        print(f"   Operation {op_id}:")
        print(f"     - Type: {operation.operation_type}")
        print(f"     - Agent: {operation.agent}")
        print(f"     - Status: {operation.status}")
        print(f"     - Generated: {operation.generated}")
    
    # Test 5: Query operations
    print("\n6. Testing operation queries...")
    
    # Get lineage for an object
    lineage = provenance2.get_lineage("storage://chunks/chunk1")
    print(f"   Lineage for 'storage://chunks/chunk1':")
    print(f"     - Status: {lineage['status']}")
    print(f"     - Depth: {lineage.get('depth', 0)}")
    print(f"     - Operations: {len(lineage.get('lineage', []))}")
    
    # Get tool statistics
    stats = provenance2.get_tool_statistics()
    print(f"\n   Tool statistics:")
    for tool_id, tool_stats in stats.get('tool_statistics', {}).items():
        print(f"     {tool_id}: {tool_stats}")
    
    # Test 6: Direct persistence queries
    print("\n7. Testing direct persistence queries...")
    if provenance2.persistence:
        # Query operations by tool
        pdf_ops = provenance2.persistence.query_operations(tool_id='T01')
        print(f"   PDF Loader operations: {len(pdf_ops)}")
        
        # Get object lineage from persistence
        chunk_lineage = provenance2.persistence.get_object_lineage("storage://chunks/chunk1")
        print(f"   Lineage operations for chunk1: {len(chunk_lineage)}")
        
        # Get tool statistics from persistence
        db_stats = provenance2.persistence.get_tool_statistics()
        print(f"   Tools in database: {list(db_stats.keys())}")
    
    print("\n✅ Provenance persistence test complete!")
    
    # Show export file contents
    print("\n8. Exported data preview:")
    try:
        with open("data/test_provenance_export.json", 'r') as f:
            export_data = json.load(f)
            print(f"   - Operations: {len(export_data['operations'])}")
            print(f"   - Lineage chains: {len(export_data['lineage_chains'])}")
            print(f"   - Tool stats: {len(export_data['tool_stats'])}")
            print(f"   - Export timestamp: {export_data['export_timestamp']}")
    except Exception as e:
        print(f"   Failed to read export file: {e}")
    
    return True

if __name__ == "__main__":
    success = test_provenance_persistence()
    sys.exit(0 if success else 1)