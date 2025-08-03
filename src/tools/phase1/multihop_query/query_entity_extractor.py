"""
Query Entity Extractor for Multi-hop Query Tool

Extracts entities from natural language queries using pattern matching
and Neo4j database lookups.
"""

import re
import logging
from typing import Dict, Any, List
from .connection_manager import Neo4jConnectionManager

logger = logging.getLogger(__name__)


class QueryEntityExtractor:
    """Extracts entities from natural language queries"""
    
    def __init__(self, connection_manager: Neo4jConnectionManager):
        self.connection_manager = connection_manager
        self.logger = logging.getLogger("multihop_query.entity_extractor")
        
        # Statistics tracking
        self.extraction_stats = {
            "queries_processed": 0,
            "entities_extracted": 0,
            "patterns_matched": 0,
            "neo4j_lookups": 0
        }
    
    def extract_query_entities(self, query_text: str) -> List[Dict[str, Any]]:
        """Extract entities from query text using patterns and Neo4j lookup"""
        if not self.connection_manager.driver:
            self.logger.warning("No Neo4j connection available for entity extraction")
            return []
        
        self.extraction_stats["queries_processed"] += 1
        
        try:
            # Extract potential entity names using multiple patterns
            potential_entities = self._extract_potential_entities(query_text)
            
            if not potential_entities:
                return []
            
            # Look up entities in Neo4j database
            found_entities = self._lookup_entities_in_database(potential_entities)
            
            self.extraction_stats["entities_extracted"] = len(found_entities)
            
            return found_entities
            
        except Exception as e:
            self.logger.error(f"Entity extraction failed: {e}")
            return []
    
    def _extract_potential_entities(self, query_text: str) -> List[str]:
        """Extract potential entity names using pattern matching"""
        potential_entities = []
        
        # Pattern 1: Capitalized words/phrases (proper nouns)
        capitalized_patterns = re.findall(r'\b[A-Z][a-zA-Z\s]{1,30}(?=\s|$)', query_text)
        potential_entities.extend([p.strip() for p in capitalized_patterns if len(p.strip()) > 2])
        self.extraction_stats["patterns_matched"] += len(capitalized_patterns)
        
        # Pattern 2: Quoted entities
        quoted_patterns = re.findall(r'"([^"]+)"', query_text)
        potential_entities.extend(quoted_patterns)
        self.extraction_stats["patterns_matched"] += len(quoted_patterns)
        
        # Pattern 3: Common entity indicators
        entity_indicators = [
            r'(?:company|corporation|inc|corp|ltd)\s+([A-Z][a-zA-Z\s]+)',
            r'(?:person|people|individual)\s+([A-Z][a-zA-Z\s]+)',
            r'(?:city|country|state)\s+([A-Z][a-zA-Z\s]+)',
            r'([A-Z][a-zA-Z\s]+)\s+(?:company|corporation|inc|corp|ltd)',
            r'(?:Dr|Mr|Ms|Mrs|Professor)\s+([A-Z][a-zA-Z\s]+)',
            r'([A-Z][a-zA-Z\s]+)\s+(?:University|Institute|Foundation)'
        ]
        
        for pattern in entity_indicators:
            matches = re.findall(pattern, query_text, re.IGNORECASE)
            potential_entities.extend([m.strip() for m in matches])
            self.extraction_stats["patterns_matched"] += len(matches)
        
        # Pattern 4: Multi-word capitalized phrases
        multiword_patterns = re.findall(r'\b[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)+\b', query_text)
        potential_entities.extend([p.strip() for p in multiword_patterns if len(p.strip()) > 4])
        self.extraction_stats["patterns_matched"] += len(multiword_patterns)
        
        # Remove duplicates and clean up
        unique_entities = list(set([e.strip() for e in potential_entities if len(e.strip()) > 2]))
        
        # Filter out common words that aren't entities
        filtered_entities = self._filter_common_words(unique_entities)
        
        return filtered_entities
    
    def _filter_common_words(self, entities: List[str]) -> List[str]:
        """Filter out common words that aren't likely to be entities"""
        # Common words that are often false positives
        common_words = {
            'The', 'This', 'That', 'These', 'Those', 'What', 'When', 'Where', 'Who', 'Why', 'How',
            'Are', 'Were', 'Was', 'Is', 'Am', 'Have', 'Has', 'Had', 'Do', 'Does', 'Did',
            'Can', 'Could', 'Should', 'Would', 'Will', 'Shall', 'May', 'Might', 'Must',
            'And', 'Or', 'But', 'So', 'Yet', 'For', 'Nor', 'Because', 'Since', 'Although',
            'All', 'Any', 'Some', 'Many', 'Much', 'Most', 'Few', 'Several', 'Each', 'Every',
            'Before', 'After', 'During', 'While', 'Until', 'Since', 'From', 'To', 'In', 'On', 'At',
            'About', 'Above', 'Below', 'Under', 'Over', 'Through', 'Between', 'Among', 'With', 'Without'
        }
        
        return [entity for entity in entities if entity not in common_words]
    
    def _lookup_entities_in_database(self, potential_entities: List[str]) -> List[Dict[str, Any]]:
        """Look up potential entities in Neo4j database"""
        found_entities = []
        
        for entity_name in potential_entities:
            try:
                self.extraction_stats["neo4j_lookups"] += 1
                
                # Search for entities with similar names
                entities = self.connection_manager.find_entities_by_name(entity_name, limit=3)
                
                for entity_record in entities:
                    found_entities.append({
                        "query_name": entity_name,
                        "entity_id": entity_record["entity_id"],
                        "canonical_name": entity_record["canonical_name"],
                        "entity_type": entity_record["entity_type"],
                        "confidence": entity_record["confidence"] or 0.5,
                        "pagerank_score": entity_record["pagerank_score"] or 0.0001,
                        "match_type": self._determine_match_type(entity_name, entity_record["canonical_name"])
                    })
                
            except Exception as e:
                self.logger.error(f"Database lookup failed for entity '{entity_name}': {e}")
                continue
        
        return found_entities
    
    def _determine_match_type(self, query_name: str, canonical_name: str) -> str:
        """Determine the type of match between query name and canonical name"""
        query_lower = query_name.lower().strip()
        canonical_lower = canonical_name.lower().strip()
        
        if query_lower == canonical_lower:
            return "exact"
        elif query_lower in canonical_lower or canonical_lower in query_lower:
            return "partial"
        else:
            return "fuzzy"
    
    def get_extraction_patterns(self) -> List[str]:
        """Get list of entity extraction patterns used"""
        return [
            "Capitalized words/phrases (proper nouns)",
            "Quoted text (\"entity name\")",
            "Company indicators (Microsoft Corporation, Apple Inc)",
            "Person titles (Dr. Smith, Professor Johnson)",
            "Organization suffixes (Harvard University, Red Cross Foundation)",
            "Multi-word capitalized phrases"
        ]
    
    def get_supported_entity_types(self) -> List[str]:
        """Get list of entity types that can be extracted"""
        # This could be dynamically loaded from the database
        return [
            "PERSON", "ORGANIZATION", "LOCATION", "PRODUCT", "EVENT",
            "WORK_OF_ART", "LAW", "LANGUAGE", "FACILITY", "MONEY",
            "DATE", "TIME", "PERCENT", "ORDINAL", "CARDINAL"
        ]
    
    def validate_query_entities(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate and enrich extracted entities"""
        validated_entities = []
        
        for entity in entities:
            # Basic validation
            if not entity.get("entity_id") or not entity.get("canonical_name"):
                continue
            
            # Confidence validation
            confidence = entity.get("confidence", 0.5)
            if confidence < 0.1:  # Too low confidence
                continue
            
            # PageRank validation (entities with some importance)
            pagerank_score = entity.get("pagerank_score", 0.0001)
            if pagerank_score <= 0.0:
                pagerank_score = 0.0001  # Set minimum value
            
            # Enrich entity data
            enriched_entity = {
                **entity,
                "confidence": max(0.1, min(1.0, confidence)),
                "pagerank_score": pagerank_score,
                "extraction_method": "pattern_matching_with_db_lookup",
                "validated": True
            }
            
            validated_entities.append(enriched_entity)
        
        return validated_entities
    
    def get_extraction_stats(self) -> Dict[str, Any]:
        """Get entity extraction statistics"""
        return {
            **self.extraction_stats,
            "extraction_patterns": len(self.get_extraction_patterns()),
            "supported_entity_types": len(self.get_supported_entity_types())
        }
    
    def analyze_query_complexity(self, query_text: str, entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze complexity of the query based on extracted entities"""
        return {
            "query_length": len(query_text),
            "word_count": len(query_text.split()),
            "entity_count": len(entities),
            "unique_entity_types": len(set(e.get("entity_type", "UNKNOWN") for e in entities)),
            "has_multiple_entities": len(entities) > 1,
            "complexity_score": self._calculate_complexity_score(query_text, entities),
            "entity_types_found": list(set(e.get("entity_type", "UNKNOWN") for e in entities))
        }
    
    def _calculate_complexity_score(self, query_text: str, entities: List[Dict[str, Any]]) -> float:
        """Calculate a complexity score for the query"""
        # Base complexity from entity count
        entity_complexity = min(len(entities) / 5.0, 1.0)
        
        # Query length factor
        length_factor = min(len(query_text) / 100.0, 1.0)
        
        # Entity type diversity factor
        type_diversity = len(set(e.get("entity_type", "UNKNOWN") for e in entities)) / max(len(entities), 1)
        
        # Combined complexity score
        complexity = (entity_complexity * 0.5) + (length_factor * 0.3) + (type_diversity * 0.2)
        
        return max(0.0, min(1.0, complexity))