#!/usr/bin/env python3
"""
Test the new dynamic parallel execution system
Should work for ANY independent tools, not just hardcoded pairs
"""
import asyncio
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Enable debug for dependency analyzer and dynamic executor
logging.getLogger('src.execution.dependency_analyzer').setLevel(logging.DEBUG)
logging.getLogger('src.execution.dynamic_executor').setLevel(logging.INFO)

# Reduce noise
logging.getLogger('src.core.resource_manager').setLevel(logging.WARNING)
logging.getLogger('src.orchestration.memory').setLevel(logging.WARNING)
logging.getLogger('src.core.identity_management').setLevel(logging.WARNING)
logging.getLogger('src.tools').setLevel(logging.WARNING)

async def test_dynamic_parallel_execution():
    """Test that dynamic parallel execution works for any independent tools"""
    
    print("\n" + "="*80)
    print("TESTING DYNAMIC PARALLEL EXECUTION")
    print("="*80 + "\n")
    
    # Initialize services
    from src.core.service_manager import ServiceManager
    from src.nlp.natural_language_interface import NaturalLanguageInterface
    
    print("1. Initializing services...")
    service_manager = ServiceManager()
    interface = NaturalLanguageInterface(service_manager)
    await interface.initialize()
    
    # Create document with rich content to trigger multiple tools
    print("\n2. Creating document to test various parallel scenarios...")
    doc_path = Path("doc_dynamic_parallel_test.txt")
    doc_path.write_text("""
    Complex Multi-Domain Analysis Document
    
    Technology Companies:
    Microsoft, Google, Amazon, Apple, Facebook (Meta), and Tesla represent major tech companies.
    Microsoft competes with Google in cloud computing through Azure vs Google Cloud.
    Amazon's AWS dominates cloud infrastructure while Apple focuses on premium hardware.
    Facebook's Meta pivots to virtual reality and metaverse technologies.
    Tesla leads electric vehicle innovation with autonomous driving capabilities.
    
    Academic Research Context:
    Published in 2023, this analysis covers technological evolution from 2020-2024.
    Research methodology follows grounded theory approaches established in 2022.
    Data collection occurred throughout 2023 with validation in early 2024.
    
    Network Relationships:
    Microsoft partners with OpenAI while competing with Google's AI initiatives.
    Amazon collaborates with multiple car manufacturers including Tesla competitors.
    Apple maintains closed ecosystem while Google promotes open-source Android.
    Meta's social platforms connect billions while facing regulatory challenges.
    
    Performance Metrics:
    Revenue growth: Microsoft +15%, Google +12%, Amazon +9% (2023 data)
    Market cap changes: Apple -5%, Meta +18%, Tesla +25% (2023 performance)
    Employee count: Microsoft 220k, Google 180k, Amazon 1.5M workers (2023 figures)
    """)
    
    interface.current_document_path = str(doc_path)
    
    # Test Case 1: Network analysis (should trigger multiple parallel opportunities)
    print("\n" + "="*70)
    print("TEST 1: Complex network analysis - Multiple parallel opportunities")
    print("="*70)
    
    question = "Build a comprehensive knowledge graph showing all companies, their relationships, analyze network centrality, and provide multi-hop query capabilities"
    print(f"Question: {question}")
    
    result = await interface.ask_question(question)
    print(f"\nResult length: {len(result)} characters")
    
    # Test Case 2: Temporal analysis (should trigger temporal filtering + parallel execution)
    print("\n" + "="*70)
    print("TEST 2: Temporal analysis - Should filter and parallelize")
    print("="*70)
    
    question = "What technological developments happened in 2023 and how do they form a network?"
    print(f"Question: {question}")
    
    result = await interface.ask_question(question)
    print(f"\nResult length: {len(result)} characters")
    
    # Test Case 3: Multi-modal analysis (should trigger maximum parallelization)
    print("\n" + "="*70)
    print("TEST 3: Multi-modal analysis - Maximum parallelization test")
    print("="*70)
    
    question = "Extract all entities, build relationships, create knowledge graph, calculate centrality measures, and enable semantic search across all data"
    print(f"Question: {question}")
    
    result = await interface.ask_question(question)
    print(f"\nResult length: {len(result)} characters")
    
    # Cleanup
    doc_path.unlink(missing_ok=True)
    
    print("\n" + "="*80)
    print("DYNAMIC PARALLEL EXECUTION TEST COMPLETE")
    print("="*80 + "\n")
    
    print("Expected Results:")
    print("- Multiple parallel groups should be detected and executed")
    print("- Any independent tools should run in parallel, not just T27/T31")
    print("- Dependency analysis should find all possible parallel opportunities")
    print("- Performance should improve with true parallelization")

if __name__ == "__main__":
    asyncio.run(test_dynamic_parallel_execution())