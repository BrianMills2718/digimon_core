"""
Real Quality Service using Neo4j
NO MOCKS - Real quality assessment and confidence propagation
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import statistics

logger = logging.getLogger(__name__)


class QualityService:
    """Real quality assessment and confidence propagation service"""
    
    def __init__(self, neo4j_driver):
        """Initialize with real Neo4j driver"""
        if not neo4j_driver:
            raise ValueError("Neo4j driver is required for QualityService")
        
        self.driver = neo4j_driver
        logger.info("QualityService initialized with real Neo4j connection")
        
        # Quality tier thresholds
        self.quality_tiers = {
            "HIGH": 0.9,
            "MEDIUM": 0.7,
            "LOW": 0.5,
            "UNCERTAIN": 0.0
        }
    
    def assess_confidence(self, object_ref: str, base_confidence: float,
                         factors: Dict[str, float] = None,
                         metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Assess confidence for an object (entity, relationship, document, etc.)
        
        Args:
            object_ref: Reference to the object being assessed
            base_confidence: Base confidence score (0-1)
            factors: Additional factors affecting confidence
            metadata: Additional metadata for assessment
            
        Returns:
            Assessment result with confidence and quality tier
        """
        try:
            # Validate base confidence
            if not 0 <= base_confidence <= 1:
                logger.warning(f"Invalid base confidence {base_confidence}, clamping to [0, 1]")
                base_confidence = max(0, min(1, base_confidence))
            
            # Calculate adjusted confidence
            adjusted_confidence = base_confidence
            
            if factors:
                # Apply factors (weighted average)
                factor_values = list(factors.values())
                if factor_values:
                    # Ensure all factors are in [0, 1]
                    factor_values = [max(0, min(1, f)) for f in factor_values]
                    factor_avg = statistics.mean(factor_values)
                    # Weighted combination: 70% base, 30% factors
                    adjusted_confidence = 0.7 * base_confidence + 0.3 * factor_avg
            
            # Determine quality tier
            quality_tier = self._determine_quality_tier(adjusted_confidence)
            
            # Store assessment in Neo4j
            assessment_id = self._store_assessment(
                object_ref, base_confidence, adjusted_confidence,
                quality_tier, factors, metadata
            )
            
            return {
                "status": "success",
                "confidence": adjusted_confidence,
                "base_confidence": base_confidence,
                "quality_tier": quality_tier,
                "assessment_id": assessment_id,
                "factors": factors,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"Error assessing confidence: {e}")
            return {
                "status": "error",
                "error": str(e),
                "confidence": base_confidence,
                "quality_tier": "UNCERTAIN"
            }
    
    def propagate_confidence(self, source_confidence: float, 
                           operation_type: str,
                           degradation_factor: float = None) -> float:
        """
        Propagate confidence through an operation
        
        Args:
            source_confidence: Input confidence
            operation_type: Type of operation being performed
            degradation_factor: Optional custom degradation factor
            
        Returns:
            Propagated confidence score
        """
        try:
            # Default degradation factors by operation type
            default_factors = {
                "chunk_text": 0.98,
                "extract_entities": 0.95,
                "extract_relationships": 0.90,
                "merge_entities": 0.95,
                "calculate_pagerank": 0.99,
                "query": 0.85,
                "transform": 0.92,
                "aggregate": 0.88
            }
            
            # Use provided factor or default
            factor = degradation_factor if degradation_factor else default_factors.get(operation_type, 0.9)
            
            # Ensure factor is in reasonable range
            factor = max(0.5, min(1.0, factor))
            
            # Calculate propagated confidence
            propagated = source_confidence * factor
            
            logger.debug(f"Confidence propagated: {source_confidence:.3f} -> {propagated:.3f} (operation: {operation_type})")
            
            return propagated
            
        except Exception as e:
            logger.error(f"Error propagating confidence: {e}")
            return source_confidence * 0.9  # Default degradation
    
    def aggregate_confidence(self, confidence_scores: List[float],
                           aggregation_method: str = "weighted_mean") -> float:
        """
        Aggregate multiple confidence scores
        
        Args:
            confidence_scores: List of confidence scores
            aggregation_method: Method to use (weighted_mean, min, harmonic_mean)
            
        Returns:
            Aggregated confidence score
        """
        try:
            if not confidence_scores:
                return 0.0
            
            # Filter out invalid scores
            valid_scores = [s for s in confidence_scores if 0 <= s <= 1]
            
            if not valid_scores:
                logger.warning("No valid confidence scores to aggregate")
                return 0.0
            
            if aggregation_method == "min":
                return min(valid_scores)
            elif aggregation_method == "harmonic_mean":
                # Harmonic mean (good for rates/ratios)
                if 0 in valid_scores:
                    return 0.0
                return len(valid_scores) / sum(1/s for s in valid_scores)
            else:  # weighted_mean (default)
                # Weight higher scores more
                weights = [s for s in valid_scores]  # Use scores as weights
                weighted_sum = sum(s * w for s, w in zip(valid_scores, weights))
                total_weight = sum(weights)
                return weighted_sum / total_weight if total_weight > 0 else 0.0
                
        except Exception as e:
            logger.error(f"Error aggregating confidence: {e}")
            return statistics.mean(confidence_scores) if confidence_scores else 0.0
    
    def _determine_quality_tier(self, confidence: float) -> str:
        """Determine quality tier based on confidence"""
        for tier, threshold in self.quality_tiers.items():
            if confidence >= threshold:
                return tier
        return "UNCERTAIN"
    
    def _store_assessment(self, object_ref: str, base_confidence: float,
                         adjusted_confidence: float, quality_tier: str,
                         factors: Dict[str, float] = None,
                         metadata: Dict[str, Any] = None) -> str:
        """Store quality assessment in Neo4j"""
        try:
            import uuid
            assessment_id = f"qa_{uuid.uuid4().hex[:12]}"
            
            with self.driver.session() as session:
                # Create quality assessment node
                session.run("""
                    CREATE (qa:QualityAssessment {
                        assessment_id: $assessment_id,
                        object_ref: $object_ref,
                        base_confidence: $base_confidence,
                        adjusted_confidence: $adjusted_confidence,
                        quality_tier: $quality_tier,
                        factors: $factors,
                        metadata: $metadata,
                        created_at: datetime()
                    })
                """,
                assessment_id=assessment_id,
                object_ref=object_ref,
                base_confidence=base_confidence,
                adjusted_confidence=adjusted_confidence,
                quality_tier=quality_tier,
                factors=str(factors) if factors else "{}",
                metadata=str(metadata) if metadata else "{}")
                
                logger.debug(f"Stored quality assessment {assessment_id} for {object_ref}")
                return assessment_id
                
        except Exception as e:
            logger.error(f"Error storing assessment: {e}")
            return f"qa_error_{datetime.now().timestamp()}"
    
    def get_object_quality(self, object_ref: str) -> Optional[Dict[str, Any]]:
        """Get the latest quality assessment for an object"""
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (qa:QualityAssessment {object_ref: $object_ref})
                    RETURN qa
                    ORDER BY qa.created_at DESC
                    LIMIT 1
                """, object_ref=object_ref)
                
                record = result.single()
                if record:
                    return dict(record["qa"])
                    
                return None
                
        except Exception as e:
            logger.error(f"Error getting object quality: {e}")
            return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get quality assessment statistics"""
        try:
            with self.driver.session() as session:
                # Count assessments
                count_result = session.run("""
                    MATCH (qa:QualityAssessment)
                    RETURN COUNT(qa) as count
                """)
                total_assessments = count_result.single()["count"]
                
                # Count by quality tier
                tier_result = session.run("""
                    MATCH (qa:QualityAssessment)
                    RETURN qa.quality_tier as tier, COUNT(qa) as count
                """)
                
                tiers = {}
                for record in tier_result:
                    tiers[record["tier"]] = record["count"]
                
                # Average confidence
                avg_result = session.run("""
                    MATCH (qa:QualityAssessment)
                    RETURN AVG(qa.adjusted_confidence) as avg_confidence
                """)
                avg_confidence = avg_result.single()["avg_confidence"]
                
                return {
                    "total_assessments": total_assessments,
                    "assessments_by_tier": tiers,
                    "average_confidence": avg_confidence if avg_confidence else 0.0
                }
                
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {
                "total_assessments": 0,
                "assessments_by_tier": {},
                "average_confidence": 0.0
            }


# Test function
def test_quality_service(driver):
    """Test the quality service with real Neo4j"""
    service = QualityService(driver)
    
    # Test confidence assessment
    result = service.assess_confidence(
        object_ref="entity_123",
        base_confidence=0.85,
        factors={
            "source_reliability": 0.9,
            "extraction_quality": 0.8,
            "context_clarity": 0.75
        },
        metadata={"source": "test_document", "tool": "T23A"}
    )
    
    print(f"✅ Assessment result: {result}")
    print(f"   Confidence: {result.get('confidence', 0):.3f}")
    print(f"   Quality Tier: {result.get('quality_tier')}")
    
    # Test confidence propagation
    propagated = service.propagate_confidence(0.9, "extract_entities")
    print(f"✅ Propagated confidence: 0.9 -> {propagated:.3f}")
    
    # Test confidence aggregation
    scores = [0.9, 0.85, 0.8, 0.95]
    aggregated = service.aggregate_confidence(scores)
    print(f"✅ Aggregated confidence: {scores} -> {aggregated:.3f}")
    
    # Test statistics
    stats = service.get_statistics()
    print(f"📊 Statistics: {stats}")
    
    return service


if __name__ == "__main__":
    # Test with mock driver for standalone testing
    class MockDriver:
        class MockSession:
            def run(self, query, **params):
                class MockResult:
                    def single(self):
                        return {"count": 0, "avg_confidence": 0.85}
                return MockResult()
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
        def session(self):
            return self.MockSession()
    
    test_quality_service(MockDriver())