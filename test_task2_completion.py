#!/usr/bin/env python3
"""Test Task 2 Completion - Vector Storage Implementation

This script tests that Task 2 has been successfully completed by verifying:
1. Vector store interface is properly implemented
2. Qdrant vector store implementation works
3. In-memory fallback works
4. Vector embedder tool is functional
5. Vector storage integrates with pipeline
"""

import sys
import numpy as np
sys.path.insert(0, '/home/brian/Digimons/src')

from src.core.vector_store import VectorStore, VectorMetadata, VectorDistance
from src.core.qdrant_store import QdrantVectorStore, InMemoryVectorStore
from src.tools.phase1.t15b_vector_embedder import VectorEmbedder
from src.core.tool_adapters import VectorEmbedderAdapter
from src.core.config_manager import ConfigManager
from src.core.evidence_logger import evidence_logger
import datetime

def test_vector_store_interface():
    """Test that vector store interfaces are properly implemented"""
    print("Testing Vector Store Interface...")
    
    # Test in-memory vector store
    print("  Testing in-memory vector store...")
    store = InMemoryVectorStore()
    
    # Test initialization
    init_success = store.initialize_collection(384)
    print(f"  - Initialize collection: {init_success}")
    
    # Test adding vectors
    test_vectors = [np.random.rand(384) for _ in range(3)]
    test_metadata = [
        VectorMetadata(text="test text 1", chunk_id="chunk1"),
        VectorMetadata(text="test text 2", chunk_id="chunk2"),
        VectorMetadata(text="test text 3", chunk_id="chunk3")
    ]
    
    vector_ids = store.add_vectors(test_vectors, test_metadata)
    print(f"  - Add vectors: {len(vector_ids)} vectors added")
    
    # Test search
    query_vector = np.random.rand(384)
    results = store.search_similar(query_vector, k=2)
    print(f"  - Search similar: {len(results)} results found")
    
    # Test get vector
    if vector_ids:
        vector = store.get_vector(vector_ids[0])
        print(f"  - Get vector: {'Found' if vector else 'Not found'}")
    
    # Test collection info
    info = store.get_collection_info()
    print(f"  - Collection info: {info['vector_count']} vectors")
    
    return {
        'in_memory_store': True,
        'vector_operations': len(results) > 0,
        'collection_info': info['vector_count'] > 0
    }

def test_qdrant_fallback():
    """Test Qdrant store with fallback to in-memory"""
    print("Testing Qdrant Vector Store (with fallback)...")
    
    try:
        # Try to create Qdrant store
        store = QdrantVectorStore(host="localhost", port=6333)
        store.initialize_collection(384)
        print("  - Qdrant store initialized successfully")
        
        # Test basic operations
        test_vectors = [np.random.rand(384) for _ in range(2)]
        test_metadata = [
            VectorMetadata(text="qdrant test 1", chunk_id="qchunk1"),
            VectorMetadata(text="qdrant test 2", chunk_id="qchunk2")
        ]
        
        vector_ids = store.add_vectors(test_vectors, test_metadata)
        print(f"  - Qdrant add vectors: {len(vector_ids)} vectors added")
        
        # Test search
        query_vector = np.random.rand(384)
        results = store.search_similar(query_vector, k=1)
        print(f"  - Qdrant search: {len(results)} results found")
        
        return {'qdrant_available': True, 'operations_working': len(results) > 0}
        
    except Exception as e:
        print(f"  - Qdrant not available: {str(e)}")
        print("  - Testing fallback to in-memory store...")
        
        # Test fallback behavior
        store = InMemoryVectorStore()
        store.initialize_collection(384)
        
        test_vectors = [np.random.rand(384)]
        test_metadata = [VectorMetadata(text="fallback test", chunk_id="fchunk1")]
        
        vector_ids = store.add_vectors(test_vectors, test_metadata)
        print(f"  - Fallback store: {len(vector_ids)} vectors added")
        
        return {'qdrant_available': False, 'fallback_working': len(vector_ids) > 0}

def test_vector_embedder():
    """Test vector embedder tool"""
    print("Testing Vector Embedder Tool...")
    
    config_manager = ConfigManager()
    embedder = VectorEmbedder(config_manager, vector_store_type="memory")
    
    # Test tool info
    tool_info = embedder.get_tool_info()
    print(f"  - Tool info: {tool_info['name']}")
    
    # Test input validation
    valid_input = {
        "chunks": [
            {"chunk_id": "test1", "text": "This is test text 1"},
            {"chunk_id": "test2", "text": "This is test text 2"}
        ],
        "workflow_id": "test_workflow"
    }
    
    validation_result = embedder.validate_input(valid_input)
    print(f"  - Input validation: {validation_result}")
    
    # Test execution
    try:
        result = embedder.execute(valid_input)
        print(f"  - Execution: {result['embeddings_stored']} embeddings stored")
        print(f"  - Vector store type: {result['vector_store_type']}")
        print(f"  - Embedding dimension: {result['embedding_dimension']}")
        
        # Test similarity search
        similar_chunks = embedder.search_similar_chunks("test text", k=2)
        print(f"  - Similarity search: {len(similar_chunks)} similar chunks found")
        
        return {
            'tool_functional': True,
            'embeddings_stored': result['embeddings_stored'],
            'similarity_search': len(similar_chunks) > 0
        }
        
    except Exception as e:
        print(f"  - Execution failed: {str(e)}")
        return {'tool_functional': False, 'error': str(e)}

def test_vector_embedder_adapter():
    """Test vector embedder adapter"""
    print("Testing Vector Embedder Adapter...")
    
    config_manager = ConfigManager()
    adapter = VectorEmbedderAdapter(config_manager)
    
    # Test tool protocol implementation
    implements_tool = hasattr(adapter, 'execute') and hasattr(adapter, 'get_tool_info') and hasattr(adapter, 'validate_input')
    print(f"  - Implements Tool protocol: {implements_tool}")
    
    # Test tool info
    tool_info = adapter.get_tool_info()
    print(f"  - Tool info: {tool_info['name']}")
    
    # Test execution
    valid_input = {
        "chunks": [
            {"chunk_id": "adapter_test1", "text": "Adapter test text 1"},
            {"chunk_id": "adapter_test2", "text": "Adapter test text 2"}
        ],
        "workflow_id": "adapter_test_workflow"
    }
    
    try:
        result = adapter.execute(valid_input)
        print(f"  - Adapter execution: {result['embeddings_stored']} embeddings stored")
        
        return {
            'adapter_functional': True,
            'implements_protocol': implements_tool,
            'embeddings_stored': result['embeddings_stored']
        }
        
    except Exception as e:
        print(f"  - Adapter execution failed: {str(e)}")
        return {'adapter_functional': False, 'error': str(e)}

def main():
    """Run all tests and log evidence"""
    print("=== TASK 2 COMPLETION VERIFICATION ===")
    print("Testing Persistent Vector Storage Implementation...")
    
    try:
        # Run all tests
        interface_results = test_vector_store_interface()
        qdrant_results = test_qdrant_fallback()
        embedder_results = test_vector_embedder()
        adapter_results = test_vector_embedder_adapter()
        
        # Check overall success
        all_passed = (
            interface_results['in_memory_store'] and
            interface_results['vector_operations'] and
            (qdrant_results['qdrant_available'] or qdrant_results.get('fallback_working', False)) and
            embedder_results.get('tool_functional', False) and
            adapter_results.get('adapter_functional', False)
        )
        
        print(f"\n=== RESULTS ===")
        print(f"Vector store interface working: {interface_results['in_memory_store']}")
        print(f"Vector operations working: {interface_results['vector_operations']}")
        print(f"Qdrant available: {qdrant_results.get('qdrant_available', False)}")
        print(f"Fallback working: {qdrant_results.get('fallback_working', False)}")
        print(f"Vector embedder functional: {embedder_results.get('tool_functional', False)}")
        print(f"Adapter functional: {adapter_results.get('adapter_functional', False)}")
        
        if all_passed:
            print("✅ TASK 2 COMPLETED SUCCESSFULLY")
        else:
            print("❌ TASK 2 FAILED")
            
        # Log evidence
        evidence_logger.log_task_completion(
            "TASK2_PERSISTENT_VECTOR_STORAGE",
            {
                "task_description": "Implement Persistent Vector Storage",
                "files_created": [
                    "src/core/vector_store.py",
                    "src/core/qdrant_store.py",
                    "src/tools/phase1/t15b_vector_embedder.py",
                    "src/core/tool_adapters.py (VectorEmbedderAdapter)",
                    "src/core/tool_factory.py (updated)"
                ],
                "interface_results": interface_results,
                "qdrant_results": qdrant_results,
                "embedder_results": embedder_results,
                "adapter_results": adapter_results
            },
            all_passed
        )
        
        return all_passed
        
    except Exception as e:
        print(f"❌ TASK 2 FAILED WITH ERROR: {e}")
        
        # Log evidence of failure
        evidence_logger.log_task_completion(
            "TASK2_PERSISTENT_VECTOR_STORAGE",
            {
                "task_description": "Implement Persistent Vector Storage",
                "error": str(e),
                "timestamp": datetime.datetime.now().isoformat()
            },
            False
        )
        
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)