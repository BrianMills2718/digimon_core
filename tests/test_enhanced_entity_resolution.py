#!/usr/bin/env python3
"""
Test Enhanced Entity Resolution - Phase D.2

Tests for LLM-based entity resolution to achieve >60% F1 score.
"""

import pytest
import asyncio
from typing import List, Tuple
from datetime import datetime

from src.services.enhanced_entity_resolution import EnhancedEntityResolver, CrossDocumentEntityResolver
from src.core.evidence_logger import EvidenceLogger


class TestEnhancedEntityResolution:
    """Test suite for enhanced entity resolution with F1 score validation"""
    
    @pytest.fixture
    def resolver(self):
        """Create enhanced entity resolver instance"""
        return EnhancedEntityResolver()
    
    @pytest.fixture
    def evidence_logger(self):
        """Create evidence logger for test results"""
        return EvidenceLogger("Phase_D2_Entity_Resolution")
    
    @pytest.fixture
    def test_corpus(self):
        """Test corpus with ground truth entities"""
        return [
            (
                "Apple Inc. was founded by Steve Jobs in Cupertino, California in 1976.",
                [
                    ("Apple Inc.", "ORG"),
                    ("Steve Jobs", "PERSON"),
                    ("Cupertino", "GPE"),
                    ("California", "GPE"),
                    ("1976", "DATE")
                ]
            ),
            (
                "The Federal Reserve raised interest rates by 0.25% on March 15, 2023.",
                [
                    ("Federal Reserve", "ORG"),
                    ("0.25%", "PERCENT"),
                    ("March 15, 2023", "DATE")
                ]
            ),
            (
                "Microsoft CEO Satya Nadella announced a $10 billion investment in OpenAI.",
                [
                    ("Microsoft", "ORG"),
                    ("Satya Nadella", "PERSON"),
                    ("$10 billion", "MONEY"),
                    ("OpenAI", "ORG")
                ]
            ),
            (
                "Tesla's Gigafactory in Austin, Texas produces over 5,000 vehicles per week.",
                [
                    ("Tesla", "ORG"),
                    ("Gigafactory", "FACILITY"),
                    ("Austin", "GPE"),
                    ("Texas", "GPE"),
                    ("5,000", "CARDINAL")
                ]
            ),
            (
                "The United Nations Climate Summit will be held in Dubai from November 30 to December 12.",
                [
                    ("United Nations", "ORG"),
                    ("Climate Summit", "EVENT"),
                    ("Dubai", "GPE"),
                    ("November 30", "DATE"),
                    ("December 12", "DATE")
                ]
            )
        ]
    
    @pytest.mark.asyncio
    async def test_entity_resolution_f1_score(self, resolver, evidence_logger, test_corpus):
        """Test that LLM entity resolution achieves >60% F1 score"""
        total_precision = 0
        total_recall = 0
        total_f1 = 0
        
        evidence_logger.log_test_start("test_entity_resolution_f1_score")
        
        for text, expected_entities in test_corpus:
            # Extract entities
            start_time = datetime.now()
            predicted_entities = await resolver.resolve_entities(text)
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Calculate metrics
            true_positives = 0
            false_positives = 0
            false_negatives = 0
            
            # Check each predicted entity
            for pred_entity in predicted_entities:
                found = False
                for exp_name, exp_type in expected_entities:
                    if (self._entities_match(pred_entity.name, exp_name) and 
                        pred_entity.entity_type == exp_type):
                        true_positives += 1
                        found = True
                        break
                
                if not found:
                    false_positives += 1
            
            # Check for missed entities
            for exp_name, exp_type in expected_entities:
                found = False
                for pred_entity in predicted_entities:
                    if (self._entities_match(pred_entity.name, exp_name) and 
                        pred_entity.entity_type == exp_type):
                        found = True
                        break
                
                if not found:
                    false_negatives += 1
            
            # Calculate metrics
            precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
            recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            
            total_precision += precision
            total_recall += recall
            total_f1 += f1
            
            # Log evidence
            evidence_logger.log_test_execution(
                "ENTITY_EXTRACTION",
                {
                    "status": "success",
                    "text": text[:100] + "...",
                    "text_length": len(text),
                    "expected_entities": len(expected_entities),
                    "predicted_entities": len(predicted_entities),
                    "true_positives": true_positives,
                    "false_positives": false_positives,
                    "false_negatives": false_negatives,
                    "precision": precision,
                    "recall": recall,
                    "f1_score": f1,
                    "execution_time": execution_time,
                    "entities_found": [
                        {
                            "name": e.name,
                            "type": e.entity_type,
                            "confidence": e.confidence,
                            "canonical_form": e.canonical_form
                        } for e in predicted_entities
                    ]
                }
            )
        
        # Calculate average metrics
        num_tests = len(test_corpus)
        avg_precision = total_precision / num_tests
        avg_recall = total_recall / num_tests
        avg_f1 = total_f1 / num_tests
        
        # Log overall performance
        evidence_logger.log_test_execution(
            "OVERALL_F1_PERFORMANCE",
            {
                "status": "success",
                "test_cases": num_tests,
                "average_precision": avg_precision,
                "average_recall": avg_recall,
                "average_f1_score": avg_f1,
                "target_f1_score": 0.6,
                "performance_vs_target": avg_f1 - 0.6,
                "improvement_vs_baseline": avg_f1 - 0.24  # vs current 24%
            }
        )
        
        # Assert F1 score meets target
        assert avg_f1 > 0.6, f"Average F1 score {avg_f1:.3f} below target 0.6"
        
        evidence_logger.log_test_end(
            "test_entity_resolution_f1_score",
            success=True,
            metrics={"avg_f1": avg_f1}
        )
    
    @pytest.mark.asyncio
    async def test_confidence_threshold_filtering(self, resolver, evidence_logger):
        """Test that confidence threshold filtering works correctly"""
        text = "John Smith works at Apple Inc. in California."
        
        # Test with default threshold (0.6)
        entities = await resolver.resolve_entities(text)
        high_conf_count = len(entities)
        
        # Lower threshold should return same or more entities
        resolver.confidence_threshold = 0.3
        entities_low = await resolver.resolve_entities(text)
        low_conf_count = len(entities_low)
        
        assert low_conf_count >= high_conf_count, "Lower threshold should return more entities"
        
        evidence_logger.log_test_execution(
            "CONFIDENCE_FILTERING",
            {
                "status": "success",
                "high_threshold_count": high_conf_count,
                "low_threshold_count": low_conf_count,
                "entities_at_0.6": [e.name for e in entities],
                "entities_at_0.3": [e.name for e in entities_low]
            }
        )
    
    @pytest.mark.asyncio
    async def test_entity_canonicalization(self, resolver, evidence_logger):
        """Test entity canonicalization and alias extraction"""
        text = "Microsoft Corp. announced that MSFT stock rose. Microsoft Corporation continues to grow."
        
        entities = await resolver.resolve_entities(text)
        
        # Find Microsoft entities
        microsoft_entities = [e for e in entities if "Microsoft" in e.name or "MSFT" in e.name]
        
        assert len(microsoft_entities) > 0, "Should find Microsoft entities"
        
        # Check canonicalization
        for entity in microsoft_entities:
            assert entity.canonical_form in ["Microsoft Corporation", "Microsoft Corp", "Microsoft"]
            assert len(entity.aliases) > 0, "Should have aliases"
        
        evidence_logger.log_test_execution(
            "CANONICALIZATION",
            {
                "status": "success",
                "entities_found": len(microsoft_entities),
                "canonical_forms": list(set(e.canonical_form for e in microsoft_entities)),
                "all_aliases": list(set(alias for e in microsoft_entities for alias in e.aliases))
            }
        )
    
    @pytest.mark.asyncio
    async def test_cross_document_resolution(self, evidence_logger):
        """Test cross-document entity resolution"""
        resolver = CrossDocumentEntityResolver()
        
        documents = [
            {
                "id": "doc1",
                "text": "Apple Inc. CEO Tim Cook announced new products."
            },
            {
                "id": "doc2",
                "text": "Tim Cook, the CEO of Apple, spoke at the conference."
            },
            {
                "id": "doc3",
                "text": "Apple's chief executive Cook revealed the iPhone 15."
            }
        ]
        
        clusters = await resolver.resolve_entity_clusters(documents)
        
        # Should find clusters for Apple and Tim Cook
        apple_clusters = [c for c in clusters if "Apple" in c["canonical_name"]]
        cook_clusters = [c for c in clusters if "Cook" in c["canonical_name"] or "Tim" in c["canonical_name"]]
        
        assert len(apple_clusters) >= 1, "Should find Apple cluster"
        assert len(cook_clusters) >= 1, "Should find Tim Cook cluster"
        
        # Check cluster quality
        for cluster in clusters:
            assert len(cluster["entities"]) >= 1, "Cluster should have entities"
            assert cluster["confidence"] >= 0.6, "Cluster confidence should be high"
        
        evidence_logger.log_test_execution(
            "CROSS_DOCUMENT_RESOLUTION",
            {
                "status": "success",
                "total_clusters": len(clusters),
                "apple_clusters": len(apple_clusters),
                "cook_clusters": len(cook_clusters),
                "cluster_sizes": [len(c["entities"]) for c in clusters],
                "cluster_details": [
                    {
                        "canonical_name": c["canonical_name"],
                        "entity_count": len(c["entities"]),
                        "confidence": c["confidence"]
                    } for c in clusters[:5]  # Log first 5 clusters
                ]
            }
        )
    
    @pytest.mark.asyncio
    async def test_complex_entity_types(self, resolver, evidence_logger):
        """Test extraction of complex entity types"""
        text = """
        The $2.5 billion merger between TechCorp and DataSystems was announced on January 15th, 2024.
        The deal, representing a 45% premium, will create the third-largest technology company.
        CEO Maria Rodriguez said "This positions us for 20% annual growth through 2025."
        """
        
        entities = await resolver.resolve_entities(text)
        
        # Check for various entity types
        entity_types = {e.entity_type for e in entities}
        
        expected_types = {"MONEY", "ORG", "DATE", "PERCENT", "PERSON"}
        found_types = entity_types & expected_types
        
        assert len(found_types) >= 4, f"Should find at least 4 entity types, found {found_types}"
        
        # Check specific entities
        money_entities = [e for e in entities if e.entity_type == "MONEY"]
        assert len(money_entities) >= 1, "Should find money entities"
        
        percent_entities = [e for e in entities if e.entity_type == "PERCENT"]
        assert len(percent_entities) >= 2, "Should find percentage entities"
        
        evidence_logger.log_test_execution(
            "COMPLEX_ENTITY_TYPES",
            {
                "status": "success",
                "entity_types_found": list(entity_types),
                "expected_types_coverage": len(found_types) / len(expected_types),
                "money_entities": [e.name for e in money_entities],
                "percent_entities": [e.name for e in percent_entities],
                "total_entities": len(entities)
            }
        )
    
    @pytest.mark.asyncio
    async def test_performance_metrics(self, resolver, evidence_logger):
        """Test performance metrics collection"""
        texts = [
            "Short text with Apple and Google.",
            "Medium length text discussing Microsoft, Amazon, and other tech companies in Silicon Valley.",
            "A longer text that mentions many entities including the United States, European Union, "
            "World Bank, International Monetary Fund, and various other organizations across multiple sentences."
        ]
        
        for i, text in enumerate(texts):
            await resolver.resolve_entities(text)
        
        stats = resolver.get_stats()
        
        assert stats["total_documents"] == len(texts)
        assert stats["api_calls"] == len(texts)
        assert stats["success_rate"] > 0
        assert stats["avg_entities_per_doc"] > 0
        
        evidence_logger.log_test_execution(
            "PERFORMANCE_METRICS",
            {
                "status": "success",
                "stats": stats,
                "texts_processed": len(texts)
            }
        )
    
    def _entities_match(self, name1: str, name2: str) -> bool:
        """Check if two entity names match (fuzzy matching)"""
        # Exact match
        if name1.lower() == name2.lower():
            return True
        
        # Substring match
        if name1.lower() in name2.lower() or name2.lower() in name1.lower():
            return True
        
        # Token overlap (for multi-word entities)
        tokens1 = set(name1.lower().split())
        tokens2 = set(name2.lower().split())
        overlap = len(tokens1 & tokens2)
        
        if overlap > 0 and overlap >= min(len(tokens1), len(tokens2)) * 0.5:
            return True
        
        return False


if __name__ == "__main__":
    # Run tests with evidence collection
    pytest.main([__file__, "-v", "--tb=short"])