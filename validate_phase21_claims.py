#!/usr/bin/env python3
"""Validate Phase 2.1 Real Implementation Claims"""

import os
import ast
import sys

def check_file_exists(filepath):
    """Check if a file exists"""
    return os.path.exists(filepath)

def check_class_in_file(filepath, classname):
    """Check if a class exists in a file"""
    try:
        with open(filepath, 'r') as f:
            tree = ast.parse(f.read())
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == classname:
                return True
        return False
    except:
        return False

def check_imports_in_file(filepath, imports):
    """Check if specific imports exist in a file"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        found = []
        for imp in imports:
            if imp in content:
                found.append(imp)
        return found
    except:
        return []

def main():
    results = []
    
    # Claim 1: RealEmbeddingService
    filepath = "src/analytics/real_embedding_service.py"
    if check_file_exists(filepath):
        has_class = check_class_in_file(filepath, "RealEmbeddingService")
        imports = check_imports_in_file(filepath, ["SentenceTransformer", "CLIPModel"])
        if has_class and len(imports) == 2:
            results.append("✅ CLAIM 1: RealEmbeddingService - FULLY RESOLVED")
        else:
            results.append(f"⚠️ CLAIM 1: RealEmbeddingService - PARTIALLY RESOLVED (class: {has_class}, imports: {imports})")
    else:
        results.append("❌ CLAIM 1: RealEmbeddingService - NOT RESOLVED (file missing)")
    
    # Claim 2: RealLLMService
    filepath = "src/analytics/real_llm_service.py"
    if check_file_exists(filepath):
        has_class = check_class_in_file(filepath, "RealLLMService")
        imports = check_imports_in_file(filepath, ["openai", "anthropic"])
        if has_class and len(imports) >= 1:
            results.append("✅ CLAIM 2: RealLLMService - FULLY RESOLVED")
        else:
            results.append(f"⚠️ CLAIM 2: RealLLMService - PARTIALLY RESOLVED (class: {has_class}, imports: {imports})")
    else:
        results.append("❌ CLAIM 2: RealLLMService - NOT RESOLVED (file missing)")
    
    # Claim 3: AdvancedScoring
    filepath = "src/analytics/advanced_scoring.py"
    if check_file_exists(filepath):
        has_class = check_class_in_file(filepath, "AdvancedScoring")
        imports = check_imports_in_file(filepath, ["SentenceTransformer", "transformers"])
        if has_class and len(imports) >= 1:
            results.append("✅ CLAIM 3: AdvancedScoring - FULLY RESOLVED")
        else:
            results.append(f"⚠️ CLAIM 3: AdvancedScoring - PARTIALLY RESOLVED (class: {has_class}, imports: {imports})")
    else:
        results.append("❌ CLAIM 3: AdvancedScoring - NOT RESOLVED (file missing)")
    
    # Claim 4: RealPercentileRanker
    filepath = "src/analytics/real_percentile_ranker.py"
    if check_file_exists(filepath):
        has_class = check_class_in_file(filepath, "RealPercentileRanker")
        imports = check_imports_in_file(filepath, ["scipy", "networkx"])
        if has_class and len(imports) == 2:
            results.append("✅ CLAIM 4: RealPercentileRanker - FULLY RESOLVED")
        else:
            results.append(f"⚠️ CLAIM 4: RealPercentileRanker - PARTIALLY RESOLVED (class: {has_class}, imports: {imports})")
    else:
        results.append("❌ CLAIM 4: RealPercentileRanker - NOT RESOLVED (file missing)")
    
    # Claim 5: TheoryKnowledgeBase
    filepath = "src/analytics/theory_knowledge_base.py"
    if check_file_exists(filepath):
        has_class = check_class_in_file(filepath, "TheoryKnowledgeBase")
        has_neo4j = "neo4j_manager" in open(filepath).read()
        if has_class and has_neo4j:
            results.append("✅ CLAIM 5: TheoryKnowledgeBase - FULLY RESOLVED")
        else:
            results.append(f"⚠️ CLAIM 5: TheoryKnowledgeBase - PARTIALLY RESOLVED (class: {has_class}, neo4j: {has_neo4j})")
    else:
        results.append("❌ CLAIM 5: TheoryKnowledgeBase - NOT RESOLVED (file missing)")
    
    # Claim 6: CrossModalEntityLinker updated
    filepath = "src/analytics/cross_modal_linker.py"
    if check_file_exists(filepath):
        content = open(filepath).read()
        uses_real = "RealEmbeddingService" in content
        no_mock = "MockEmbeddingService" not in content or "class MockEmbeddingService" not in content
        if uses_real and no_mock:
            results.append("✅ CLAIM 6: CrossModalEntityLinker - FULLY RESOLVED")
        else:
            results.append(f"⚠️ CLAIM 6: CrossModalEntityLinker - PARTIALLY RESOLVED (uses_real: {uses_real}, no_mock: {no_mock})")
    else:
        results.append("❌ CLAIM 6: CrossModalEntityLinker - NOT RESOLVED (file missing)")
    
    # Claim 7: ConceptualKnowledgeSynthesizer updated
    filepath = "src/analytics/knowledge_synthesizer.py"
    if check_file_exists(filepath):
        content = open(filepath).read()
        uses_real_llm = "RealLLMService" in content
        uses_scoring = "AdvancedScoring" in content
        uses_theory = "TheoryKnowledgeBase" in content
        no_mock = "MockLLMService" not in content or "class MockLLMService" not in content
        if uses_real_llm and uses_scoring and uses_theory and no_mock:
            results.append("✅ CLAIM 7: ConceptualKnowledgeSynthesizer - FULLY RESOLVED")
        else:
            results.append(f"⚠️ CLAIM 7: ConceptualKnowledgeSynthesizer - PARTIALLY RESOLVED (llm: {uses_real_llm}, scoring: {uses_scoring}, theory: {uses_theory}, no_mock: {no_mock})")
    else:
        results.append("❌ CLAIM 7: ConceptualKnowledgeSynthesizer - NOT RESOLVED (file missing)")
    
    # Claim 8: CitationImpactAnalyzer updated
    filepath = "src/analytics/citation_impact_analyzer.py"
    if check_file_exists(filepath):
        content = open(filepath).read()
        uses_real = "RealPercentileRanker" in content
        if uses_real:
            results.append("✅ CLAIM 8: CitationImpactAnalyzer - FULLY RESOLVED")
        else:
            results.append("❌ CLAIM 8: CitationImpactAnalyzer - NOT RESOLVED (not using RealPercentileRanker)")
    else:
        results.append("❌ CLAIM 8: CitationImpactAnalyzer - NOT RESOLVED (file missing)")
    
    # Print results
    print("=== Phase 2.1 Real Implementation Validation ===\n")
    for result in results:
        print(result)
    
    # Summary
    fully_resolved = sum(1 for r in results if "FULLY RESOLVED" in r)
    total = len(results)
    print(f"\n=== Summary: {fully_resolved}/{total} claims fully resolved ===")
    
    if fully_resolved == total:
        print("\n🎉 All Phase 2.1 real implementations are verified!")
        return 0
    else:
        print("\n⚠️ Some implementations need attention")
        return 1

if __name__ == "__main__":
    sys.exit(main())