"""
Suggestion Engine for Ontology Validation

Provides intelligent suggestions for entity types, relationship types,
and concept mappings based on text analysis and ontology knowledge.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict

from src.ontology_library.ontology_service import OntologyService

logger = logging.getLogger(__name__)


class TypeSuggestionEngine:
    """Suggests entity and relationship types based on text content"""
    
    def __init__(self, ontology_service: OntologyService):
        """Initialize with ontology service"""
        self.ontology = ontology_service
        self.logger = logging.getLogger("core.ontology_validation.type_suggestions")

    def suggest_entity_type(self, text: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Suggest entity types based on text content.
        
        Uses indigenous terms to find matching concepts.
        """
        suggestions = []
        
        try:
            # Search for concepts matching terms in the text
            words = text.lower().split()
            concept_matches = defaultdict(list)
            
            for word in words:
                concepts = self.ontology.search_by_indigenous_term(word)
                for concept in concepts:
                    if hasattr(concept, 'object_type') and concept.object_type == "Entity":
                        concept_matches[concept.name].append(word)
            
            # Score suggestions based on number of matching terms
            for concept_name, matching_words in concept_matches.items():
                score = len(matching_words) / len(words)  # Proportion of words that matched
                
                suggestions.append({
                    "entity_type": concept_name,
                    "score": score,
                    "matching_terms": matching_words,
                    "total_terms": len(words),
                    "confidence": min(score * 2, 1.0)  # Boost score but cap at 1.0
                })
            
            # Sort by score (highest first) and limit results
            suggestions.sort(key=lambda x: x["score"], reverse=True)
            
            # Add additional metadata
            for suggestion in suggestions[:limit]:
                suggestion["description"] = self._get_entity_type_description(suggestion["entity_type"])
                suggestion["typical_attributes"] = self._get_entity_typical_attributes(suggestion["entity_type"])
        
        except Exception as e:
            self.logger.error(f"Failed to suggest entity types for text '{text}': {e}")
        
        return suggestions[:limit]

    def suggest_relationship_type(self, text: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Suggest relationship types based on text content.
        
        Uses indigenous terms to find matching concepts.
        """
        suggestions = []
        
        try:
            # Search for concepts matching terms in the text
            words = text.lower().split()
            concept_matches = defaultdict(list)
            
            for word in words:
                concepts = self.ontology.search_by_indigenous_term(word)
                for concept in concepts:
                    if hasattr(concept, 'object_type') and concept.object_type == "Connection":
                        concept_matches[concept.name].append(word)
            
            # Score suggestions based on number of matching terms
            for concept_name, matching_words in concept_matches.items():
                score = len(matching_words) / len(words)
                
                suggestions.append({
                    "relationship_type": concept_name,
                    "score": score,
                    "matching_terms": matching_words,
                    "total_terms": len(words),
                    "confidence": min(score * 2, 1.0)
                })
            
            # Sort by score and limit results
            suggestions.sort(key=lambda x: x["score"], reverse=True)
            
            # Add additional metadata
            for suggestion in suggestions[:limit]:
                suggestion["description"] = self._get_relationship_type_description(suggestion["relationship_type"])
                suggestion["domain_range"] = self._get_relationship_domain_range(suggestion["relationship_type"])
        
        except Exception as e:
            self.logger.error(f"Failed to suggest relationship types for text '{text}': {e}")
        
        return suggestions[:limit]

    def suggest_entity_type_contextual(self, text: str, context: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Suggest entity types based on text content and additional context"""
        try:
            # Get base suggestions from text
            base_suggestions = self.suggest_entity_type(text, limit * 2)
            
            # Analyze context for additional clues
            context_words = context.lower().split()
            context_clues = self._extract_context_clues(context_words)
            
            # Re-score suggestions based on context
            for suggestion in base_suggestions:
                context_boost = self._calculate_context_boost(suggestion["entity_type"], context_clues)
                suggestion["original_score"] = suggestion["score"]
                suggestion["context_boost"] = context_boost
                suggestion["final_score"] = suggestion["score"] + context_boost
                suggestion["context_clues_matched"] = context_clues
            
            # Sort by final score and return top suggestions
            base_suggestions.sort(key=lambda x: x["final_score"], reverse=True)
            return base_suggestions[:limit]
            
        except Exception as e:
            self.logger.error(f"Failed to suggest contextual entity types: {e}")
            return self.suggest_entity_type(text, limit)

    def _extract_context_clues(self, context_words: List[str]) -> Dict[str, List[str]]:
        """Extract context clues from context words"""
        clues = {
            "people_indicators": [],
            "organization_indicators": [],
            "location_indicators": [],
            "event_indicators": [],
            "concept_indicators": []
        }
        
        # Define indicator words for different entity categories
        indicators = {
            "people_indicators": ["person", "individual", "human", "doctor", "professor", "ceo", "manager", "employee"],
            "organization_indicators": ["company", "corporation", "organization", "institution", "business", "firm"],
            "location_indicators": ["city", "country", "building", "office", "place", "location", "region"],
            "event_indicators": ["meeting", "conference", "event", "activity", "process", "action"],
            "concept_indicators": ["concept", "idea", "principle", "theory", "abstract", "notion"]
        }
        
        for category, words in indicators.items():
            for word in context_words:
                if word in words:
                    clues[category].append(word)
        
        return clues

    def _calculate_context_boost(self, entity_type: str, context_clues: Dict[str, List[str]]) -> float:
        """Calculate boost score based on context clues"""
        boost = 0.0
        entity_type_lower = entity_type.lower()
        
        # Check for entity type category matches with context clues
        if any(indicator in entity_type_lower for indicator in ["person", "individual", "human"]):
            boost += len(context_clues["people_indicators"]) * 0.1
        
        if any(indicator in entity_type_lower for indicator in ["organization", "company", "business"]):
            boost += len(context_clues["organization_indicators"]) * 0.1
        
        if any(indicator in entity_type_lower for indicator in ["location", "place", "region"]):
            boost += len(context_clues["location_indicators"]) * 0.1
        
        if any(indicator in entity_type_lower for indicator in ["event", "activity", "process"]):
            boost += len(context_clues["event_indicators"]) * 0.1
        
        if any(indicator in entity_type_lower for indicator in ["concept", "abstract", "principle"]):
            boost += len(context_clues["concept_indicators"]) * 0.1
        
        return min(boost, 0.5)  # Cap boost at 0.5

    def _get_entity_type_description(self, entity_type: str) -> str:
        """Get description for an entity type"""
        try:
            concept = self.ontology.get_concept(entity_type)
            return concept.description if concept and hasattr(concept, 'description') else ""
        except:
            return ""

    def _get_entity_typical_attributes(self, entity_type: str) -> List[str]:
        """Get typical attributes for an entity type"""
        try:
            return self.ontology.get_entity_attributes(entity_type)
        except:
            return []

    def _get_relationship_type_description(self, relationship_type: str) -> str:
        """Get description for a relationship type"""
        try:
            concept = self.ontology.get_concept(relationship_type)
            return concept.description if concept and hasattr(concept, 'description') else ""
        except:
            return ""

    def _get_relationship_domain_range(self, relationship_type: str) -> Dict[str, List[str]]:
        """Get domain and range for a relationship type"""
        try:
            concept = self.ontology.registry.connections.get(relationship_type)
            if concept:
                return {
                    "domain": concept.domain,
                    "range": concept.range
                }
        except:
            pass
        return {"domain": [], "range": []}

    def get_suggestion_statistics(self) -> Dict[str, Any]:
        """Get statistics about suggestion capabilities"""
        try:
            total_entities = len(self.ontology.registry.entities)
            total_connections = len(self.ontology.registry.connections)
            
            # Count entities with indigenous terms
            entities_with_terms = 0
            for entity_name, entity_concept in self.ontology.registry.entities.items():
                if hasattr(entity_concept, 'indigenous_terms') and entity_concept.indigenous_terms:
                    entities_with_terms += 1
            
            # Count connections with indigenous terms
            connections_with_terms = 0
            for conn_name, conn_concept in self.ontology.registry.connections.items():
                if hasattr(conn_concept, 'indigenous_terms') and conn_concept.indigenous_terms:
                    connections_with_terms += 1
            
            return {
                "total_entity_types": total_entities,
                "total_relationship_types": total_connections,
                "entities_with_indigenous_terms": entities_with_terms,
                "connections_with_indigenous_terms": connections_with_terms,
                "entity_term_coverage": entities_with_terms / total_entities if total_entities > 0 else 0,
                "connection_term_coverage": connections_with_terms / total_connections if total_connections > 0 else 0
            }
        except Exception as e:
            self.logger.error(f"Failed to get suggestion statistics: {e}")
            return {}


class ConceptMappingEngine:
    """Manages concept mappings between different ontology systems"""
    
    def __init__(self, ontology_service: OntologyService, dolce_service):
        """Initialize with ontology services"""
        self.ontology = ontology_service
        self.dolce = dolce_service
        self.logger = logging.getLogger("core.ontology_validation.concept_mapping")

    def get_dolce_mapping(self, graphrag_concept: str) -> Optional[str]:
        """Get DOLCE mapping for a GraphRAG concept
        
        Args:
            graphrag_concept: GraphRAG concept name
            
        Returns:
            DOLCE category or None if not found
        """
        try:
            return self.dolce.map_to_dolce(graphrag_concept)
        except Exception as e:
            self.logger.error(f"Failed to get DOLCE mapping for {graphrag_concept}: {e}")
            return None

    def suggest_dolce_mappings(self, graphrag_concept: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Suggest possible DOLCE mappings for a GraphRAG concept"""
        suggestions = []
        
        try:
            # Get direct mapping if available
            direct_mapping = self.get_dolce_mapping(graphrag_concept)
            if direct_mapping:
                suggestions.append({
                    "dolce_concept": direct_mapping,
                    "mapping_type": "direct",
                    "confidence": 1.0,
                    "description": self._get_dolce_concept_description(direct_mapping)
                })
            
            # Get similar concepts based on name similarity
            similar_mappings = self._find_similar_dolce_concepts(graphrag_concept)
            for mapping in similar_mappings[:limit-1]:  # Leave room for direct mapping
                if mapping["dolce_concept"] != direct_mapping:  # Avoid duplicates
                    suggestions.append(mapping)
            
        except Exception as e:
            self.logger.error(f"Failed to suggest DOLCE mappings for {graphrag_concept}: {e}")
        
        return suggestions

    def _find_similar_dolce_concepts(self, concept: str) -> List[Dict[str, Any]]:
        """Find DOLCE concepts similar to the given concept"""
        similar_concepts = []
        
        try:
            # Simple similarity based on string matching
            concept_lower = concept.lower()
            
            # Get all DOLCE concepts (this would need to be implemented in dolce service)
            if hasattr(self.dolce, 'get_all_concepts'):
                all_dolce_concepts = self.dolce.get_all_concepts()
                
                for dolce_concept in all_dolce_concepts:
                    dolce_name_lower = dolce_concept.lower()
                    
                    # Calculate simple similarity score
                    similarity = self._calculate_string_similarity(concept_lower, dolce_name_lower)
                    
                    if similarity > 0.3:  # Threshold for similarity
                        similar_concepts.append({
                            "dolce_concept": dolce_concept,
                            "mapping_type": "similar",
                            "confidence": similarity,
                            "description": self._get_dolce_concept_description(dolce_concept)
                        })
                
                # Sort by confidence
                similar_concepts.sort(key=lambda x: x["confidence"], reverse=True)
        
        except Exception as e:
            self.logger.error(f"Failed to find similar DOLCE concepts: {e}")
        
        return similar_concepts

    def _calculate_string_similarity(self, str1: str, str2: str) -> float:
        """Calculate simple string similarity between two strings"""
        # Simple Jaccard similarity based on character n-grams
        def get_ngrams(s: str, n: int = 2) -> set:
            return set(s[i:i+n] for i in range(len(s) - n + 1))
        
        ngrams1 = get_ngrams(str1)
        ngrams2 = get_ngrams(str2)
        
        if not ngrams1 and not ngrams2:
            return 1.0
        if not ngrams1 or not ngrams2:
            return 0.0
        
        intersection = len(ngrams1 & ngrams2)
        union = len(ngrams1 | ngrams2)
        
        return intersection / union if union > 0 else 0.0

    def _get_dolce_concept_description(self, dolce_concept: str) -> str:
        """Get description for a DOLCE concept"""
        try:
            concept_info = self.dolce.get_dolce_concept(dolce_concept)
            return concept_info.description if concept_info and hasattr(concept_info, 'description') else ""
        except:
            return ""

    def validate_concept_mapping(self, graphrag_concept: str, dolce_concept: str) -> Dict[str, Any]:
        """Validate a concept mapping between GraphRAG and DOLCE"""
        validation_result = {
            "valid": False,
            "confidence": 0.0,
            "issues": [],
            "recommendations": []
        }
        
        try:
            # Check if GraphRAG concept exists
            if not self.ontology.get_concept(graphrag_concept):
                validation_result["issues"].append(f"GraphRAG concept '{graphrag_concept}' not found")
            
            # Check if DOLCE concept exists
            if not self.dolce.get_dolce_concept(dolce_concept):
                validation_result["issues"].append(f"DOLCE concept '{dolce_concept}' not found")
            
            # Check existing mapping
            existing_mapping = self.get_dolce_mapping(graphrag_concept)
            if existing_mapping and existing_mapping != dolce_concept:
                validation_result["issues"].append(
                    f"Conflict: {graphrag_concept} already mapped to {existing_mapping}"
                )
                validation_result["recommendations"].append(
                    f"Consider updating existing mapping or using different GraphRAG concept"
                )
            
            # Calculate semantic compatibility (simplified)
            compatibility = self._calculate_semantic_compatibility(graphrag_concept, dolce_concept)
            validation_result["confidence"] = compatibility
            
            if compatibility > 0.7:
                validation_result["valid"] = True
            elif compatibility > 0.5:
                validation_result["recommendations"].append("Mapping has moderate compatibility, review carefully")
            else:
                validation_result["recommendations"].append("Low semantic compatibility, consider alternative mapping")
            
        except Exception as e:
            validation_result["issues"].append(f"Validation error: {str(e)}")
        
        return validation_result

    def _calculate_semantic_compatibility(self, graphrag_concept: str, dolce_concept: str) -> float:
        """Calculate semantic compatibility between concepts"""
        # Simplified compatibility based on string similarity and category matching
        string_sim = self._calculate_string_similarity(graphrag_concept.lower(), dolce_concept.lower())
        
        # Add category-based compatibility (this would be enhanced with actual semantic analysis)
        category_boost = 0.0
        
        # Simple category matching heuristics
        if "person" in graphrag_concept.lower() and "agent" in dolce_concept.lower():
            category_boost = 0.3
        elif "organization" in graphrag_concept.lower() and "collective" in dolce_concept.lower():
            category_boost = 0.3
        elif "location" in graphrag_concept.lower() and "spatial" in dolce_concept.lower():
            category_boost = 0.3
        
        return min(string_sim + category_boost, 1.0)

    def get_mapping_statistics(self) -> Dict[str, Any]:
        """Get statistics about concept mappings"""
        try:
            total_graphrag_concepts = len(self.ontology.registry.entities) + len(self.ontology.registry.connections)
            
            # Count mapped concepts (this would require checking all mappings)
            mapped_concepts = 0
            unmapped_concepts = []
            
            # Check entity mappings
            for entity_name in self.ontology.registry.entities.keys():
                mapping = self.get_dolce_mapping(entity_name)
                if mapping:
                    mapped_concepts += 1
                else:
                    unmapped_concepts.append(entity_name)
            
            # Check connection mappings
            for conn_name in self.ontology.registry.connections.keys():
                mapping = self.get_dolce_mapping(conn_name)
                if mapping:
                    mapped_concepts += 1
                else:
                    unmapped_concepts.append(conn_name)
            
            return {
                "total_graphrag_concepts": total_graphrag_concepts,
                "mapped_concepts": mapped_concepts,
                "unmapped_concepts": len(unmapped_concepts),
                "mapping_coverage": mapped_concepts / total_graphrag_concepts if total_graphrag_concepts > 0 else 0,
                "sample_unmapped": unmapped_concepts[:10]  # Show first 10 unmapped
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get mapping statistics: {e}")
            return {}