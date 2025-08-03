"""
Quality Assessment Logic

Extracted from t301_multi_document_fusion.py (ConsistencyChecker and quality methods)
Assesses quality of fused results and ensures consistency.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict, Counter
import re

logger = logging.getLogger(__name__)


@dataclass
class QualityMetrics:
    """Data class for fusion quality metrics."""
    
    entity_consistency: float = 0.0
    relationship_consistency: float = 0.0
    temporal_consistency: float = 0.0
    ontological_compliance: float = 0.0
    overall_score: float = 0.0
    inconsistencies: List[Dict[str, Any]] = field(default_factory=list)
    quality_issues: List[str] = field(default_factory=list)
    assessment_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'entity_consistency': self.entity_consistency,
            'relationship_consistency': self.relationship_consistency,
            'temporal_consistency': self.temporal_consistency,
            'ontological_compliance': self.ontological_compliance,
            'overall_score': self.overall_score,
            'inconsistencies': self.inconsistencies,
            'quality_issues': self.quality_issues,
            'assessment_timestamp': self.assessment_timestamp
        }


class QualityAssessor:
    """Assesses quality of fused results and identifies consistency issues."""
    
    def __init__(self, quality_service=None, ontology_service=None):
        """Initialize quality assessor with optional services."""
        self.quality_service = quality_service
        self.ontology_service = ontology_service
        self.logger = logging.getLogger(f"{__name__}.QualityAssessor")
        
        # Quality thresholds
        self.consistency_threshold = 0.8
        self.temporal_tolerance_days = 30
        self.confidence_threshold = 0.7
        
    def assess_fusion_quality(self, 
                            fused_entities: List[Dict[str, Any]], 
                            fused_relationships: List[Dict[str, Any]],
                            original_documents: List[Dict[str, Any]] = None) -> QualityMetrics:
        """
        Comprehensive quality assessment of fusion results.
        
        Args:
            fused_entities: List of fused entities
            fused_relationships: List of fused relationships  
            original_documents: Optional original documents for cross-reference
            
        Returns:
            QualityMetrics object with assessment results
        """
        self.logger.info(f"Assessing fusion quality for {len(fused_entities)} entities and {len(fused_relationships)} relationships")
        
        try:
            # Assess different aspects of quality
            entity_consistency = self._assess_entity_consistency(fused_entities)
            relationship_consistency = self._assess_relationship_consistency(fused_relationships, fused_entities)
            temporal_consistency = self._assess_temporal_consistency(fused_entities, fused_relationships)
            ontological_compliance = self._assess_ontological_compliance(fused_entities, fused_relationships)
            
            # Collect all inconsistencies
            all_inconsistencies = []
            all_inconsistencies.extend(entity_consistency.get('inconsistencies', []))
            all_inconsistencies.extend(relationship_consistency.get('inconsistencies', []))
            all_inconsistencies.extend(temporal_consistency.get('inconsistencies', []))
            all_inconsistencies.extend(ontological_compliance.get('inconsistencies', []))
            
            # Calculate overall score
            scores = [
                entity_consistency.get('score', 0.0),
                relationship_consistency.get('score', 0.0),
                temporal_consistency.get('score', 0.0),
                ontological_compliance.get('score', 0.0)
            ]
            overall_score = sum(scores) / len(scores) if scores else 0.0
            
            # Collect quality issues
            quality_issues = []
            if entity_consistency.get('score', 0.0) < self.consistency_threshold:
                quality_issues.append("Entity consistency below threshold")
            if relationship_consistency.get('score', 0.0) < self.consistency_threshold:
                quality_issues.append("Relationship consistency below threshold")
            if temporal_consistency.get('score', 0.0) < self.consistency_threshold:
                quality_issues.append("Temporal consistency issues detected")
            if ontological_compliance.get('score', 0.0) < self.consistency_threshold:
                quality_issues.append("Ontological compliance issues detected")
            
            metrics = QualityMetrics(
                entity_consistency=entity_consistency.get('score', 0.0),
                relationship_consistency=relationship_consistency.get('score', 0.0),
                temporal_consistency=temporal_consistency.get('score', 0.0),
                ontological_compliance=ontological_compliance.get('score', 0.0),
                overall_score=overall_score,
                inconsistencies=all_inconsistencies,
                quality_issues=quality_issues
            )
            
            self.logger.info(f"Quality assessment completed: overall score {overall_score:.3f}")
            return metrics
            
        except Exception as e:
            self.logger.error(f"Quality assessment failed: {e}", exc_info=True)
            return QualityMetrics(
                quality_issues=[f"Assessment failed: {str(e)}"]
            )
    
    def _assess_entity_consistency(self, entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess consistency within and between entities."""
        if not entities:
            return {'score': 1.0, 'inconsistencies': []}
        
        inconsistencies = []
        total_checks = 0
        passed_checks = 0
        
        for entity in entities:
            entity_name = entity.get('name', '')
            
            # Check confidence levels
            confidence = entity.get('confidence', 0.0)
            total_checks += 1
            if confidence >= self.confidence_threshold:
                passed_checks += 1
            else:
                inconsistencies.append({
                    'type': 'low_confidence',
                    'entity': entity_name,
                    'issue': f"Confidence {confidence:.3f} below threshold {self.confidence_threshold}",
                    'severity': 'medium'
                })
            
            # Check for required fields
            required_fields = ['name', 'type']
            for field in required_fields:
                total_checks += 1
                if entity.get(field):
                    passed_checks += 1
                else:
                    inconsistencies.append({
                        'type': 'missing_field',
                        'entity': entity_name,
                        'issue': f"Missing required field: {field}",
                        'severity': 'high'
                    })
            
            # Check for duplicate sources
            sources = entity.get('sources', [])
            if len(sources) != len(set(sources)):
                inconsistencies.append({
                    'type': 'duplicate_sources',
                    'entity': entity_name,
                    'issue': "Entity has duplicate source references",
                    'severity': 'low'
                })
        
        # Check for duplicate entities (potential fusion misses)
        entity_names = [e.get('name', '').lower() for e in entities]
        name_counts = Counter(entity_names)
        for name, count in name_counts.items():
            if count > 1 and name:
                inconsistencies.append({
                    'type': 'potential_duplicates', 
                    'entity': name,
                    'issue': f"Found {count} entities with similar names - potential fusion miss",
                    'severity': 'medium'
                })
        
        score = passed_checks / total_checks if total_checks > 0 else 1.0
        
        return {
            'score': score,
            'inconsistencies': inconsistencies,
            'checks_performed': total_checks,
            'checks_passed': passed_checks
        }
    
    def _assess_relationship_consistency(self, relationships: List[Dict[str, Any]], 
                                       entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess consistency of relationships."""
        if not relationships:
            return {'score': 1.0, 'inconsistencies': []}
        
        # Create entity name lookup
        entity_names = {e.get('name', '').lower() for e in entities}
        
        inconsistencies = []
        total_checks = 0
        passed_checks = 0
        
        for rel in relationships:
            source = rel.get('source', '')
            target = rel.get('target', '')
            rel_type = rel.get('type', '')
            
            # Check if source and target entities exist
            total_checks += 2
            if source.lower() in entity_names:
                passed_checks += 1
            else:
                inconsistencies.append({
                    'type': 'missing_entity',
                    'relationship': f"{source} -> {target}",
                    'issue': f"Source entity '{source}' not found in fused entities",
                    'severity': 'high'
                })
            
            if target.lower() in entity_names:
                passed_checks += 1
            else:
                inconsistencies.append({
                    'type': 'missing_entity',
                    'relationship': f"{source} -> {target}",
                    'issue': f"Target entity '{target}' not found in fused entities",
                    'severity': 'high'
                })
            
            # Check for self-references
            total_checks += 1
            if source.lower() != target.lower():
                passed_checks += 1
            else:
                inconsistencies.append({
                    'type': 'self_reference',
                    'relationship': f"{source} -> {target}",
                    'issue': "Relationship references same entity as source and target",
                    'severity': 'medium'
                })
            
            # Check confidence
            confidence = rel.get('confidence', 0.0)
            total_checks += 1
            if confidence >= self.confidence_threshold:
                passed_checks += 1
            else:
                inconsistencies.append({
                    'type': 'low_confidence',
                    'relationship': f"{source} -> {target}",
                    'issue': f"Relationship confidence {confidence:.3f} below threshold",
                    'severity': 'medium'
                })
        
        score = passed_checks / total_checks if total_checks > 0 else 1.0
        
        return {
            'score': score,
            'inconsistencies': inconsistencies,
            'checks_performed': total_checks,
            'checks_passed': passed_checks
        }
    
    def _assess_temporal_consistency(self, entities: List[Dict[str, Any]], 
                                   relationships: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess temporal consistency across entities and relationships."""
        inconsistencies = []
        total_checks = 0
        passed_checks = 0
        
        # Extract temporal information
        entity_dates = {}
        for entity in entities:
            entity_name = entity.get('name', '')
            properties = entity.get('properties', {})
            
            # Look for date-related properties
            date_fields = ['founded', 'born', 'created', 'established', 'date', 'birth_date', 'death_date']
            for field in date_fields:
                if field in properties:
                    try:
                        date_value = properties[field]
                        # Try to parse date (simplified)
                        if isinstance(date_value, str) and len(date_value) >= 4:
                            year = int(date_value[:4])
                            entity_dates[entity_name] = {field: year}
                    except (ValueError, TypeError):
                        continue
        
        # Check temporal consistency in relationships
        for rel in relationships:
            source = rel.get('source', '')
            target = rel.get('target', '')
            rel_type = rel.get('type', '').upper()
            
            # Check for temporal violations
            if rel_type in ['FOUNDED', 'CREATED', 'ESTABLISHED']:
                # Founder should be born before founding
                if source in entity_dates and target in entity_dates:
                    source_birth = entity_dates[source].get('born', entity_dates[source].get('birth_date'))
                    target_founded = entity_dates[target].get('founded', entity_dates[target].get('established'))
                    
                    if source_birth and target_founded:
                        total_checks += 1
                        if source_birth < target_founded:
                            passed_checks += 1
                        else:
                            inconsistencies.append({
                                'type': 'temporal_violation',
                                'relationship': f"{source} -> {target}",
                                'issue': f"Founder born ({source_birth}) after company founded ({target_founded})",
                                'severity': 'high'
                            })
        
        # If no temporal checks possible, assume consistency
        if total_checks == 0:
            score = 1.0
        else:
            score = passed_checks / total_checks
        
        return {
            'score': score,
            'inconsistencies': inconsistencies,
            'checks_performed': total_checks,
            'checks_passed': passed_checks
        }
    
    def _assess_ontological_compliance(self, entities: List[Dict[str, Any]], 
                                     relationships: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess compliance with ontological constraints."""
        inconsistencies = []
        total_checks = 0
        passed_checks = 0
        
        # Define basic ontological rules
        valid_entity_types = {'PERSON', 'ORG', 'ORGANIZATION', 'GPE', 'LOCATION', 'PRODUCT', 'EVENT', 'WORK_OF_ART', 'LAW', 'LANGUAGE'}
        valid_relationship_types = {'FOUNDED', 'WORKS_FOR', 'LOCATED_IN', 'PART_OF', 'PRODUCES', 'OWNS', 'MEMBER_OF', 'LEADS', 'RELATED_TO'}
        
        # Check entity type validity
        for entity in entities:
            entity_type = entity.get('type', '').upper()
            entity_name = entity.get('name', '')
            
            total_checks += 1
            if entity_type in valid_entity_types or not entity_type:  # Allow empty types
                passed_checks += 1
            else:
                inconsistencies.append({
                    'type': 'invalid_entity_type',
                    'entity': entity_name,
                    'issue': f"Unknown entity type: {entity_type}",
                    'severity': 'low'
                })
        
        # Check relationship type validity and semantic constraints
        for rel in relationships:
            rel_type = rel.get('type', '').upper()
            source = rel.get('source', '')
            target = rel.get('target', '')
            
            # Check relationship type validity
            total_checks += 1
            if rel_type in valid_relationship_types or not rel_type:
                passed_checks += 1
            else:
                inconsistencies.append({
                    'type': 'invalid_relationship_type',
                    'relationship': f"{source} -> {target}",
                    'issue': f"Unknown relationship type: {rel_type}",
                    'severity': 'low'
                })
            
            # Check semantic constraints (simplified)
            if rel_type == 'FOUNDED':
                # Typically PERSON founds ORG
                source_entity = next((e for e in entities if e.get('name', '').lower() == source.lower()), None)
                target_entity = next((e for e in entities if e.get('name', '').lower() == target.lower()), None)
                
                if source_entity and target_entity:
                    total_checks += 1
                    source_type = source_entity.get('type', '').upper()
                    target_type = target_entity.get('type', '').upper()
                    
                    if source_type == 'PERSON' and target_type in ['ORG', 'ORGANIZATION']:
                        passed_checks += 1
                    else:
                        inconsistencies.append({
                            'type': 'semantic_violation',
                            'relationship': f"{source} -> {target}",
                            'issue': f"Unusual semantic pattern: {source_type} {rel_type} {target_type}",
                            'severity': 'low'
                        })
        
        score = passed_checks / total_checks if total_checks > 0 else 1.0
        
        return {
            'score': score,
            'inconsistencies': inconsistencies,
            'checks_performed': total_checks,
            'checks_passed': passed_checks
        }
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get tool information for MCP compatibility."""
        return {
            'tool_name': 'QualityAssessor',
            'description': 'Assesses quality and consistency of fused multi-document results',
            'version': '1.0.0',
            'capabilities': [
                'entity_consistency_assessment',
                'relationship_consistency_assessment',
                'temporal_consistency_checking',
                'ontological_compliance_validation'
            ],
            'thresholds': {
                'consistency_threshold': self.consistency_threshold,
                'confidence_threshold': self.confidence_threshold,
                'temporal_tolerance_days': self.temporal_tolerance_days
            }
        }