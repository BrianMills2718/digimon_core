"""Theory-Driven Validation Component (<400 lines)

Provides theory-driven validation of entities against ontological frameworks.
Implements concept hierarchy building and comprehensive validation logic.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class TheoryValidationResult:
    """Result of theory-driven validation."""
    entity_id: str
    is_valid: bool
    validation_score: float
    theory_alignment: Dict[str, float]
    concept_hierarchy_path: List[str]
    validation_reasons: List[str]


@dataclass
class ConceptHierarchy:
    """Hierarchical concept structure."""
    concept_id: str
    concept_name: str
    parent_concepts: List[str]
    child_concepts: List[str]
    properties: Dict[str, Any]
    validation_rules: List[str]


class TheoryDrivenValidator:
    """Validates entities against theoretical frameworks."""
    
    def __init__(self, domain_ontology: 'DomainOntology'):
        self.domain_ontology = domain_ontology
        self.concept_hierarchy = self._build_concept_hierarchy()
        
    def _build_concept_hierarchy(self) -> Dict[str, ConceptHierarchy]:
        """Build hierarchical concept structure from ontology."""
        hierarchy = {}
        
        # Extract concepts from ontology
        for concept_data in self.domain_ontology.entity_types:
            concept = ConceptHierarchy(
                concept_id=concept_data.name,
                concept_name=concept_data.name,
                parent_concepts=[],  # Would be populated from ontology structure
                child_concepts=[],   # Would be populated from ontology structure
                properties={"description": concept_data.description, "attributes": concept_data.attributes},
                validation_rules=[f"required_attributes:{','.join(concept_data.attributes)}"]
            )
            hierarchy[concept.concept_id] = concept
        
        return hierarchy
    
    def validate_entity_against_theory(self, entity: Dict[str, Any]) -> TheoryValidationResult:
        """Validate entity against theoretical framework."""
        entity_id = entity.get('id', '')
        entity_type = entity.get('type', '')
        entity_text = entity.get('text', '')
        entity_properties = entity.get('properties', {})
        
        # Find matching concept in hierarchy
        matching_concept = self._find_matching_concept(entity_type, entity_text, entity_properties)
        
        if not matching_concept:
            return TheoryValidationResult(
                entity_id=entity_id,
                is_valid=False,
                validation_score=0.0,
                theory_alignment={},
                concept_hierarchy_path=[],
                validation_reasons=["No matching concept found in hierarchy"]
            )
        
        # Validate against concept rules
        validation_score = self._calculate_validation_score(entity, matching_concept)
        is_valid = validation_score >= 0.7  # Threshold for validity
        
        # Calculate theory alignment
        theory_alignment = self._calculate_theory_alignment(entity, matching_concept)
        
        # Build concept hierarchy path
        hierarchy_path = self._build_hierarchy_path(matching_concept)
        
        # Generate validation reasons
        validation_reasons = self._generate_validation_reasons(entity, matching_concept, validation_score)
        
        return TheoryValidationResult(
            entity_id=entity_id,
            is_valid=is_valid,
            validation_score=validation_score,
            theory_alignment=theory_alignment,
            concept_hierarchy_path=hierarchy_path,
            validation_reasons=validation_reasons
        )
    
    def _find_matching_concept(self, entity_type: str, entity_text: str, 
                              entity_properties: Dict[str, Any]) -> Optional[ConceptHierarchy]:
        """Find matching concept in hierarchy."""
        # Direct type match
        if entity_type in self.concept_hierarchy:
            return self.concept_hierarchy[entity_type]
        
        # Fuzzy matching based on text and properties
        best_match = None
        best_score = 0.0
        
        for concept in self.concept_hierarchy.values():
            score = self._calculate_concept_match_score(
                entity_type, entity_text, entity_properties, concept
            )
            if score > best_score:
                best_score = score
                best_match = concept
        
        return best_match if best_score > 0.5 else None
    
    def _calculate_concept_match_score(self, entity_type: str, entity_text: str,
                                     entity_properties: Dict[str, Any],
                                     concept: ConceptHierarchy) -> float:
        """Calculate how well an entity matches a concept."""
        score = 0.0
        
        # Type similarity
        if entity_type.upper() == concept.concept_name.upper():
            score += 0.5
        elif entity_type.lower() in concept.concept_name.lower():
            score += 0.3
        
        # Text similarity with concept examples
        concept_examples = concept.properties.get('examples', [])
        for example in concept_examples:
            if entity_text.lower() in example.lower() or example.lower() in entity_text.lower():
                score += 0.2
                break
        
        # Property alignment
        concept_attrs = set(concept.properties.get('attributes', []))
        entity_attrs = set(entity_properties.keys())
        if concept_attrs:
            attr_overlap = len(concept_attrs.intersection(entity_attrs)) / len(concept_attrs)
            score += attr_overlap * 0.3
        
        return min(score, 1.0)
    
    def _calculate_validation_score(self, entity: Dict[str, Any], 
                                  concept: ConceptHierarchy) -> float:
        """Calculate validation score based on concept rules."""
        total_score = 0.0
        rules = concept.validation_rules
        
        if not rules:
            return 0.8  # Default score if no rules
        
        passed_rules = 0
        
        for rule in rules:
            if self._check_rule(entity, rule):
                passed_rules += 1
        
        return passed_rules / len(rules)
    
    def _check_rule(self, entity: Dict[str, Any], rule: str) -> bool:
        """Check if entity satisfies a validation rule."""
        if "required_attributes" in rule:
            attrs = rule.split(":")[1].split(",")
            return all(attr in entity.get('properties', {}) for attr in attrs)
        
        if "min_confidence" in rule:
            min_confidence = float(rule.split(":")[1].strip())
            return entity.get('confidence', 0.0) >= min_confidence
        
        return True
    
    def _calculate_theory_alignment(self, entity: Dict[str, Any], 
                                  concept: ConceptHierarchy) -> Dict[str, float]:
        """Calculate alignment with different theoretical aspects."""
        return {
            'structural_alignment': self._calculate_structural_alignment(entity, concept),
            'contextual_alignment': self._calculate_contextual_alignment(entity, concept),
            'domain_alignment': self._calculate_domain_alignment(entity, concept)
        }
    
    def _calculate_structural_alignment(self, entity: Dict[str, Any], 
                                      concept: ConceptHierarchy) -> float:
        """Calculate structural alignment score."""
        entity_props = set(entity.get('properties', {}).keys())
        concept_attrs = set(concept.properties.get('attributes', []))
        
        if not concept_attrs:
            return 1.0
        
        intersection = entity_props & concept_attrs
        return len(intersection) / len(concept_attrs)
    
    def _calculate_contextual_alignment(self, entity: Dict[str, Any], 
                                      concept: ConceptHierarchy) -> float:
        """Calculate contextual alignment score."""
        entity_context = entity.get('context', '')
        concept_desc = concept.properties.get('description', '')
        
        if not entity_context or not concept_desc:
            return 0.5  # Neutral score
        
        # Simple keyword overlap
        entity_words = set(entity_context.lower().split())
        concept_words = set(concept_desc.lower().split())
        
        if not concept_words:
            return 0.5
        
        overlap = len(entity_words.intersection(concept_words))
        return min(overlap / len(concept_words), 1.0)
    
    def _calculate_domain_alignment(self, entity: Dict[str, Any], 
                                  concept: ConceptHierarchy) -> float:
        """Calculate domain-specific alignment."""
        # Extract domain indicators
        entity_type = entity.get('type', '').lower()
        concept_type = concept.properties.get('type', '').lower()
        
        # Type alignment
        type_alignment = 1.0 if entity_type == concept_type else 0.0
        
        # Confidence alignment
        entity_confidence = entity.get('confidence', 0.0)
        min_confidence = concept.properties.get('min_confidence', 0.0)
        confidence_alignment = 1.0 if entity_confidence >= min_confidence else entity_confidence / min_confidence
        
        # Attribute alignment
        entity_attrs = set(entity.get('properties', {}).keys())
        required_attrs = set(concept.properties.get('required_attributes', []))
        
        if required_attrs:
            attr_alignment = len(entity_attrs & required_attrs) / len(required_attrs)
        else:
            attr_alignment = 1.0
        
        # Combine alignments
        return (type_alignment * 0.4) + (confidence_alignment * 0.3) + (attr_alignment * 0.3)
    
    def _build_hierarchy_path(self, concept: ConceptHierarchy) -> List[str]:
        """Build hierarchy path for concept."""
        path = [concept.concept_name]
        
        # Add parent concepts (if available)
        for parent in concept.parent_concepts:
            if parent in self.concept_hierarchy:
                path.insert(0, parent)
        
        return path
    
    def _generate_validation_reasons(self, entity: Dict[str, Any], 
                                   concept: ConceptHierarchy, 
                                   validation_score: float) -> List[str]:
        """Generate human-readable validation reasons."""
        reasons = []
        
        # Score-based reasons
        if validation_score >= 0.9:
            reasons.append("Entity strongly aligns with concept requirements")
        elif validation_score >= 0.7:
            reasons.append("Entity meets concept requirements")
        elif validation_score >= 0.5:
            reasons.append("Entity partially meets concept requirements")
        else:
            reasons.append("Entity does not meet concept requirements")
        
        # Specific validation reasons
        for rule in concept.validation_rules:
            if self._check_rule(entity, rule):
                reasons.append(f"Passes validation rule: {rule}")
            else:
                reasons.append(f"Fails validation rule: {rule}")
        
        # Alignment reasons
        theory_alignment = self._calculate_theory_alignment(entity, concept)
        
        if theory_alignment['structural_alignment'] > 0.8:
            reasons.append("Strong structural alignment with concept")
        elif theory_alignment['structural_alignment'] < 0.3:
            reasons.append("Weak structural alignment with concept")
        
        if theory_alignment['contextual_alignment'] > 0.8:
            reasons.append("Strong contextual alignment with concept")
        elif theory_alignment['contextual_alignment'] < 0.3:
            reasons.append("Weak contextual alignment with concept")
        
        return reasons


class ValidationResultAnalyzer:
    """Analyzes and aggregates validation results."""
    
    def __init__(self):
        self.validation_history = []
    
    def analyze_validation_batch(self, results: List[TheoryValidationResult]) -> Dict[str, Any]:
        """Analyze a batch of validation results."""
        if not results:
            return {"total_entities": 0, "valid_entities": 0, "validation_rate": 0.0}
        
        valid_count = sum(1 for r in results if r.is_valid)
        total_count = len(results)
        
        # Calculate average scores
        avg_validation_score = sum(r.validation_score for r in results) / total_count
        
        # Analyze theory alignments
        alignment_types = ['structural_alignment', 'contextual_alignment', 'domain_alignment']
        avg_alignments = {}
        
        for alignment_type in alignment_types:
            scores = []
            for result in results:
                if alignment_type in result.theory_alignment:
                    scores.append(result.theory_alignment[alignment_type])
            
            avg_alignments[alignment_type] = sum(scores) / len(scores) if scores else 0.0
        
        # Common validation reasons
        reason_counts = {}
        for result in results:
            for reason in result.validation_reasons:
                reason_counts[reason] = reason_counts.get(reason, 0) + 1
        
        return {
            "total_entities": total_count,
            "valid_entities": valid_count,
            "validation_rate": valid_count / total_count,
            "average_validation_score": avg_validation_score,
            "average_alignments": avg_alignments,
            "common_validation_reasons": sorted(reason_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        }
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get summary of all validation history."""
        if not self.validation_history:
            return {"message": "No validation history available"}
        
        return self.analyze_validation_batch(self.validation_history)
    
    def record_validation(self, result: TheoryValidationResult):
        """Record a validation result for analysis."""
        self.validation_history.append(result)
        
        # Keep only recent history (last 1000 validations)
        if len(self.validation_history) > 1000:
            self.validation_history = self.validation_history[-1000:]