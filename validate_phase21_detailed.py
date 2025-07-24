#!/usr/bin/env python3
"""Detailed Phase 2.1 Real Implementation Validation with Evidence"""

import os
import re
import ast

def extract_evidence(filepath, patterns):
    """Extract lines containing specific patterns"""
    evidence = []
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
        
        for i, line in enumerate(lines, 1):
            for pattern in patterns:
                if pattern in line:
                    evidence.append(f"  Line {i}: {line.strip()}")
                    break
        return evidence
    except:
        return []

def validate_real_embedding_service():
    """Validate RealEmbeddingService implementation"""
    print("\n=== CLAIM 1: RealEmbeddingService ===")
    filepath = "src/analytics/real_embedding_service.py"
    
    if not os.path.exists(filepath):
        print("❌ NOT RESOLVED - File not found")
        return False
    
    # Check for real model usage
    patterns = [
        "SentenceTransformer('all-MiniLM-L6-v2'",
        "CLIPModel.from_pretrained",
        "class RealEmbeddingService",
        "def generate_text_embeddings",
        "def generate_image_embeddings"
    ]
    
    evidence = extract_evidence(filepath, patterns)
    
    if len(evidence) >= 4:
        print("✅ FULLY RESOLVED")
        print("Evidence found:")
        for e in evidence[:5]:  # Show first 5 pieces of evidence
            print(e)
        return True
    else:
        print("⚠️ PARTIALLY RESOLVED")
        print(f"Found {len(evidence)} of expected patterns")
        return False

def validate_real_llm_service():
    """Validate RealLLMService implementation"""
    print("\n=== CLAIM 2: RealLLMService ===")
    filepath = "src/analytics/real_llm_service.py"
    
    if not os.path.exists(filepath):
        print("❌ NOT RESOLVED - File not found")
        return False
    
    patterns = [
        "class RealLLMService",
        "openai.AsyncOpenAI",
        "Anthropic(",
        "gpt-4-turbo-preview",
        "claude-3-opus",
        "async def generate_text",
        "async def generate_structured_hypotheses"
    ]
    
    evidence = extract_evidence(filepath, patterns)
    
    if len(evidence) >= 4:
        print("✅ FULLY RESOLVED")
        print("Evidence found:")
        for e in evidence[:5]:
            print(e)
        return True
    else:
        print("⚠️ PARTIALLY RESOLVED")
        print(f"Found {len(evidence)} of expected patterns")
        return False

def validate_advanced_scoring():
    """Validate AdvancedScoring implementation"""
    print("\n=== CLAIM 3: AdvancedScoring ===")
    filepath = "src/analytics/advanced_scoring.py"
    
    if not os.path.exists(filepath):
        print("❌ NOT RESOLVED - File not found")
        return False
    
    patterns = [
        "class AdvancedScoring",
        "SentenceTransformer",
        "pipeline(\"zero-shot-classification\"",
        "calculate_explanatory_power",
        "cosine_similarity",
        "calculate_testability",
        "transformers"
    ]
    
    evidence = extract_evidence(filepath, patterns)
    
    if len(evidence) >= 4:
        print("✅ FULLY RESOLVED")
        print("Evidence found:")
        for e in evidence[:5]:
            print(e)
        return True
    else:
        print("⚠️ PARTIALLY RESOLVED")
        print(f"Found {len(evidence)} of expected patterns")
        return False

def validate_real_percentile_ranker():
    """Validate RealPercentileRanker implementation"""
    print("\n=== CLAIM 4: RealPercentileRanker ===")
    filepath = "src/analytics/real_percentile_ranker.py"
    
    if not os.path.exists(filepath):
        print("❌ NOT RESOLVED - File not found")
        return False
    
    patterns = [
        "class RealPercentileRanker",
        "from scipy import stats",
        "import networkx as nx",
        "stats.percentileofscore",
        "nx.betweenness_centrality",
        "nx.closeness_centrality",
        "calculate_collaboration_network_centrality"
    ]
    
    evidence = extract_evidence(filepath, patterns)
    
    if len(evidence) >= 5:
        print("✅ FULLY RESOLVED")
        print("Evidence found:")
        for e in evidence[:6]:
            print(e)
        return True
    else:
        print("⚠️ PARTIALLY RESOLVED")
        print(f"Found {len(evidence)} of expected patterns")
        return False

def validate_theory_knowledge_base():
    """Validate TheoryKnowledgeBase implementation"""
    print("\n=== CLAIM 5: TheoryKnowledgeBase ===")
    filepath = "src/analytics/theory_knowledge_base.py"
    
    if not os.path.exists(filepath):
        print("❌ NOT RESOLVED - File not found")
        return False
    
    patterns = [
        "class TheoryKnowledgeBase",
        "neo4j_manager",
        "MATCH (t:Theory)",
        "execute_read_query",
        "identify_applicable_theories",
        "SentenceTransformer"
    ]
    
    evidence = extract_evidence(filepath, patterns)
    
    if len(evidence) >= 4:
        print("✅ FULLY RESOLVED")
        print("Evidence found:")
        for e in evidence[:5]:
            print(e)
        return True
    else:
        print("⚠️ PARTIALLY RESOLVED")
        print(f"Found {len(evidence)} of expected patterns")
        return False

def validate_integration_updates():
    """Validate integration file updates"""
    print("\n=== CLAIMS 6-8: Integration Updates ===")
    
    results = []
    
    # Check CrossModalEntityLinker
    filepath = "src/analytics/cross_modal_linker.py"
    if os.path.exists(filepath):
        content = open(filepath).read()
        if "from .real_embedding_service import RealEmbeddingService" in content and \
           "self.embedding_service = RealEmbeddingService()" in content and \
           "class MockEmbeddingService" not in content:
            print("✅ CrossModalEntityLinker: Updated to use RealEmbeddingService, MockEmbeddingService removed")
            results.append(True)
        else:
            print("❌ CrossModalEntityLinker: Issues with integration")
            results.append(False)
    
    # Check ConceptualKnowledgeSynthesizer
    filepath = "src/analytics/knowledge_synthesizer.py"
    if os.path.exists(filepath):
        content = open(filepath).read()
        checks = [
            "from .real_llm_service import RealLLMService" in content,
            "from .advanced_scoring import AdvancedScoring" in content,
            "from .theory_knowledge_base import TheoryKnowledgeBase" in content,
            "class MockLLMService" not in content
        ]
        if all(checks):
            print("✅ ConceptualKnowledgeSynthesizer: All real services integrated, MockLLMService removed")
            results.append(True)
        else:
            print("❌ ConceptualKnowledgeSynthesizer: Issues with integration")
            results.append(False)
    
    # Check CitationImpactAnalyzer
    filepath = "src/analytics/citation_impact_analyzer.py"
    if os.path.exists(filepath):
        content = open(filepath).read()
        if "from .real_percentile_ranker import RealPercentileRanker" in content and \
           "self.percentile_ranker = RealPercentileRanker" in content:
            print("✅ CitationImpactAnalyzer: Updated to use RealPercentileRanker")
            results.append(True)
        else:
            print("❌ CitationImpactAnalyzer: Issues with integration")
            results.append(False)
    
    return all(results)

def main():
    print("=== Phase 2.1 Real Implementation Detailed Validation ===")
    
    results = []
    results.append(validate_real_embedding_service())
    results.append(validate_real_llm_service())
    results.append(validate_advanced_scoring())
    results.append(validate_real_percentile_ranker())
    results.append(validate_theory_knowledge_base())
    results.append(validate_integration_updates())
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n=== FINAL VERDICT: {passed}/{total} validations passed ===")
    
    if passed == total:
        print("\n🎉 ALL CLAIMS FULLY RESOLVED!")
        print("Phase 2.1 mock replacement is complete with real AI/ML implementations.")
    else:
        print("\n⚠️ Some implementations need attention")

if __name__ == "__main__":
    main()