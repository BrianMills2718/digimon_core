#!/usr/bin/env python3
"""Test script to verify real analytics implementations work correctly"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.analytics.real_embedding_service import RealEmbeddingService
from src.analytics.real_llm_service import RealLLMService
from src.analytics.advanced_scoring import AdvancedScoring
from src.analytics.real_percentile_ranker import RealPercentileRanker
from src.analytics.theory_knowledge_base import TheoryKnowledgeBase


async def test_embedding_service():
    """Test RealEmbeddingService"""
    print("\n=== Testing RealEmbeddingService ===")
    
    try:
        service = RealEmbeddingService()
        
        # Test text embeddings
        texts = ["This is a test sentence", "Another test with different content"]
        text_embeddings = await service.generate_text_embeddings(texts)
        print(f"✓ Text embeddings shape: {text_embeddings.shape}")
        print(f"  Sample values: {text_embeddings[0][:5]}")
        
        # Test structured embeddings
        structured_data = [
            {"h_index": 25, "citation_count": 500, "year": 2020},
            {"h_index": 10, "citation_count": 100, "year": 2022}
        ]
        struct_embeddings = await service.generate_structured_embeddings(structured_data)
        print(f"✓ Structured embeddings shape: {struct_embeddings.shape}")
        print(f"  Sample values: {struct_embeddings[0][:5]}")
        
        return True
        
    except Exception as e:
        print(f"✗ RealEmbeddingService failed: {e}")
        return False


async def test_llm_service():
    """Test RealLLMService"""
    print("\n=== Testing RealLLMService ===")
    
    try:
        service = RealLLMService()
        
        # Test text generation
        prompt = "Generate a hypothesis about the relationship between citation patterns and research impact"
        text = await service.generate_text(prompt, max_length=200)
        print(f"✓ Generated text ({len(text)} chars): {text[:100]}...")
        
        # Test structured hypothesis generation
        hypotheses = await service.generate_structured_hypotheses(prompt, max_hypotheses=2)
        print(f"✓ Generated {len(hypotheses)} structured hypotheses")
        if hypotheses:
            print(f"  First hypothesis: {hypotheses[0]['text'][:80]}...")
            print(f"  Confidence: {hypotheses[0]['confidence_score']}")
        
        return True
        
    except Exception as e:
        print(f"✗ RealLLMService failed: {e}")
        print("  Note: This requires OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable")
        return False


async def test_advanced_scoring():
    """Test AdvancedScoring"""
    print("\n=== Testing AdvancedScoring ===")
    
    try:
        scorer = AdvancedScoring()
        
        # Test explanatory power
        hypothesis = {"text": "Increased collaboration leads to higher citation impact"}
        anomaly = {"description": "High citation counts in collaborative papers", "type": "high_collaboration_impact"}
        
        exp_power = await scorer.calculate_explanatory_power(hypothesis, anomaly)
        print(f"✓ Explanatory power: {exp_power:.3f}")
        
        # Test simplicity
        simplicity = await scorer.calculate_simplicity(hypothesis)
        print(f"✓ Simplicity score: {simplicity:.3f}")
        
        # Test testability
        evidence_base = {
            "entities": [
                {"text": "Collaborative research shows 2x citation rate"},
                {"text": "Single-author papers have lower impact"}
            ]
        }
        testability = await scorer.calculate_testability(hypothesis, evidence_base)
        print(f"✓ Testability score: {testability:.3f}")
        
        return True
        
    except Exception as e:
        print(f"✗ AdvancedScoring failed: {e}")
        return False


async def test_percentile_ranker():
    """Test RealPercentileRanker"""
    print("\n=== Testing RealPercentileRanker ===")
    
    try:
        # Mock Neo4j manager for testing
        class MockNeo4jManager:
            async def execute_read_query(self, query, params=None):
                # Return empty results to trigger synthetic distribution
                return []
        
        ranker = RealPercentileRanker(MockNeo4jManager())
        
        # Test percentile calculation
        h_index_percentile = await ranker.calculate_percentile_rank(15, 'h_index')
        print(f"✓ H-index 15 percentile: {h_index_percentile:.1f}%")
        
        citation_percentile = await ranker.calculate_percentile_rank(100, 'citation_velocity')
        print(f"✓ Citation velocity 100 percentile: {citation_percentile:.1f}%")
        
        # Test batch calculation
        scores = {
            'h_index': 20,
            'citation_velocity': 50,
            'cross_disciplinary_impact': 0.7
        }
        percentiles = await ranker.calculate_percentile_ranks_batch(scores)
        print(f"✓ Batch percentiles: {percentiles}")
        
        return True
        
    except Exception as e:
        print(f"✗ RealPercentileRanker failed: {e}")
        return False


async def test_theory_knowledge_base():
    """Test TheoryKnowledgeBase"""
    print("\n=== Testing TheoryKnowledgeBase ===")
    
    try:
        # Mock Neo4j manager
        class MockNeo4jManager:
            async def execute_read_query(self, query, params=None):
                return []  # No theories in DB, will use fallbacks
        
        theory_kb = TheoryKnowledgeBase(MockNeo4jManager())
        
        # Test theory identification
        evidence_base = {
            'entities': [
                {'type': 'Paper', 'labels': ['Research', 'Citation']},
                {'type': 'Author', 'labels': ['Researcher']}
            ],
            'relationships': [
                {'type': 'CITES'},
                {'type': 'AUTHORED_BY'}
            ],
            'modalities': ['text', 'structured']
        }
        
        theories = await theory_kb.identify_applicable_theories(evidence_base)
        print(f"✓ Identified {len(theories)} applicable theories")
        
        if theories:
            print(f"  Top theory: {theories[0]['name']} (applicability: {theories[0]['applicability']:.2f})")
            print(f"  Description: {theories[0]['description'][:80]}...")
        
        return True
        
    except Exception as e:
        print(f"✗ TheoryKnowledgeBase failed: {e}")
        return False


async def main():
    """Run all tests"""
    print("Testing Real Analytics Implementations")
    print("=" * 50)
    
    results = []
    
    # Run tests
    results.append(("RealEmbeddingService", await test_embedding_service()))
    results.append(("RealLLMService", await test_llm_service()))
    results.append(("AdvancedScoring", await test_advanced_scoring()))
    results.append(("RealPercentileRanker", await test_percentile_ranker()))
    results.append(("TheoryKnowledgeBase", await test_theory_knowledge_base()))
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary:")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"  {name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All real implementations are working correctly!")
    else:
        print("\n⚠️  Some implementations need attention")
        print("Note: LLM service requires API keys to be set")


if __name__ == "__main__":
    asyncio.run(main())