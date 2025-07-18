#!/usr/bin/env python3
"""
Minimal Working Example - Super-Digimon GraphRAG System
Uses the new PipelineOrchestrator architecture
"""

import tempfile
import os
from pathlib import Path

# Proper package imports (no sys.path manipulation)
from src.core.pipeline_orchestrator import PipelineOrchestrator
from src.core.tool_factory import create_unified_workflow_config, Phase, OptimizationLevel
from src.core.config_manager import ConfigManager
from typing import Dict, Any

def get_entity_name(entity: Dict[str, Any]) -> str:
    """Get entity name using standardized schema"""
    # With schema enforcement, canonical_name is guaranteed to exist
    canonical_name = entity.get('canonical_name')
    if canonical_name:
        return canonical_name
    else:
        # This should never happen with schema enforcement
        raise ValueError(f"Entity missing required canonical_name field: {entity}")

def minimal_working_example():
    """Minimal end-to-end example using PipelineOrchestrator."""
    print("🚀 Super-Digimon GraphRAG - Minimal Working Example")
    print("=" * 60)
    
    # Create test PDF content (using embedded text for simplicity)
    test_content = """
    Elon Musk is the CEO of Tesla Inc., an electric vehicle company based in Austin, Texas.
    He also founded SpaceX in 2002. Tesla and SpaceX are both innovative technology companies.
    Apple Inc. was founded by Steve Jobs in 1976 and is headquartered in Cupertino, California.
    Tim Cook currently serves as Apple's CEO.
    """
    
    # Create temporary text file (simulating PDF processing)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(test_content)
        test_file = f.name
    
    try:
        # Initialize workflow with PipelineOrchestrator
        print("📋 Step 1: Initialize PipelineOrchestrator...")
        config_manager = ConfigManager()
        config = create_unified_workflow_config(
            phase=Phase.PHASE1,
            optimization_level=OptimizationLevel.STANDARD
        )
        orchestrator = PipelineOrchestrator(config, config_manager)
        print("✅ PipelineOrchestrator initialized successfully")
        
        # Execute workflow
        print("⚙️  Step 2: Process document...")
        result = orchestrator.execute(
            document_paths=[test_file],
            queries=["What companies are mentioned?", "Who founded Tesla?"]
        )
        
        # Display results
        print("📊 Step 3: Results")
        print(f"Status: {result.get('status', 'unknown')}")
        
        # Extract entities and relationships from the result
        final_result = result.get('final_result', {})
        entities = final_result.get('entities', [])
        relationships = final_result.get('relationships', [])
        
        print(f"\n📊 Summary:")
        print(f"  • Entities extracted: {len(entities)}")
        print(f"  • Relationships found: {len(relationships)}")
        
        # Show sample entities
        if entities:
            print(f"\n🏷️  Sample entities:")
            for i, entity in enumerate(entities[:5]):
                try:
                    name = get_entity_name(entity)
                    entity_type = entity.get('entity_type', 'UNKNOWN')
                    print(f"  {i+1}. {name} ({entity_type})")
                except ValueError as e:
                    print(f"  {i+1}. ERROR: {e}")
        
        # Show sample relationships
        if relationships:
            print(f"\n🔗 Sample relationships:")
            for i, rel in enumerate(relationships[:5]):
                rel_type = rel.get('type', rel.get('relationship_type', 'Unknown'))
                source = rel.get('source', rel.get('source_id', 'Unknown'))
                target = rel.get('target', rel.get('target_id', 'Unknown'))
                print(f"  {i+1}. {source} --{rel_type}--> {target}")
        
        # Show query results if available
        query_results = result.get('query_results', [])
        if query_results:
            print(f"\n❓ Query results: {len(query_results)} answers")
            for i, answer in enumerate(query_results[:3]):
                print(f"  {i+1}. {answer.get('answer', answer)}")
        
        print("\n✅ Minimal example completed successfully!")
        return True
        
    except ImportError as e:
        print(f"\n❌ Import Error: {str(e)}")
        print("💡 Solution: Run 'pip install -e .' from the project root directory")
        return False
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup
        if os.path.exists(test_file):
            os.unlink(test_file)

if __name__ == "__main__":
    success = minimal_working_example()
    exit(0 if success else 1)