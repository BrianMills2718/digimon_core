"""Theory knowledge base for identifying and applying relevant theories"""

import logging
from typing import List, Dict, Any, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import asyncio

logger = logging.getLogger(__name__)


class TheoryKnowledgeBase:
    """Real theory identification using knowledge base and semantic search"""
    
    def __init__(self, neo4j_manager):
        """Initialize with Neo4j manager for database access.
        
        Args:
            neo4j_manager: Neo4j manager instance
        """
        self.neo4j_manager = neo4j_manager
        self.theory_embeddings = {}
        self.theory_model = SentenceTransformer('all-MiniLM-L6-v2')
        self._theories_cached = False
        
    async def identify_applicable_theories(self, evidence_base: Dict) -> List[Dict[str, Any]]:
        """Identify theories from knowledge base that apply to evidence.
        
        Args:
            evidence_base: Dictionary containing evidence entities and relationships
            
        Returns:
            List of applicable theories with scores
        """
        try:
            # Extract key concepts from evidence
            concepts = await self._extract_concepts(evidence_base)
            
            # First try: Query theory database
            theories = await self._query_theory_database(concepts)
            
            # If no theories found, try semantic search
            if not theories:
                theories = await self._search_theories_by_similarity(evidence_base)
            
            # If still no theories, use domain-specific fallbacks
            if not theories:
                theories = await self._get_domain_specific_theories(evidence_base)
            
            # Score applicability of each theory
            scored_theories = []
            for theory in theories:
                score = await self._score_theory_applicability(theory, evidence_base)
                theory_dict = {
                    'name': theory.get('name', 'Unknown Theory'),
                    'applicability': score,
                    'description': theory.get('description', ''),
                    'domain': theory.get('domain', 'general'),
                    'conditions': theory.get('conditions', []),
                    'key_concepts': theory.get('keywords', [])
                }
                scored_theories.append(theory_dict)
            
            # Sort by applicability score
            scored_theories.sort(key=lambda x: x['applicability'], reverse=True)
            
            # Return top theories
            return scored_theories[:5]
            
        except Exception as e:
            logger.error(f"Failed to identify applicable theories: {e}")
            return await self._get_default_theories()
    
    async def _extract_concepts(self, evidence_base: Dict) -> List[str]:
        """Extract key concepts from evidence base.
        
        Args:
            evidence_base: Evidence dictionary
            
        Returns:
            List of key concepts
        """
        concepts = set()
        
        # Extract from entities
        for entity in evidence_base.get('entities', []):
            # Entity labels
            if 'labels' in entity:
                concepts.update(entity['labels'])
            
            # Entity properties that might contain concepts
            for key in ['type', 'category', 'field', 'domain', 'topic']:
                if key in entity and entity[key]:
                    concepts.add(str(entity[key]))
        
        # Extract from relationships
        for rel in evidence_base.get('relationships', []):
            if 'type' in rel:
                # Convert relationship type to concept
                rel_type = rel['type'].replace('_', ' ').lower()
                concepts.add(rel_type)
        
        # Extract from modalities if present
        if 'modalities' in evidence_base:
            concepts.update(evidence_base['modalities'])
        
        return list(concepts)
    
    async def _query_theory_database(self, concepts: List[str]) -> List[Dict]:
        """Query theory database for matching theories.
        
        Args:
            concepts: List of concepts to match
            
        Returns:
            List of matching theories
        """
        try:
            # Query for theories matching concepts
            query = """
            MATCH (t:Theory)
            WHERE any(concept IN $concepts WHERE 
                toLower(t.name) CONTAINS toLower(concept) OR
                any(keyword IN t.keywords WHERE toLower(keyword) CONTAINS toLower(concept)) OR
                toLower(t.domain) CONTAINS toLower(concept) OR
                toLower(t.description) CONTAINS toLower(concept)
            )
            RETURN t.name as name, 
                   t.description as description,
                   t.keywords as keywords, 
                   t.domain as domain,
                   t.applicability_conditions as conditions,
                   t.confidence_score as base_score
            ORDER BY t.citation_count DESC
            LIMIT 20
            """
            
            result = await self.neo4j_manager.execute_read_query(
                query, {'concepts': concepts}
            )
            
            if result:
                return result
            
            # Try broader search without concept filtering
            fallback_query = """
            MATCH (t:Theory)
            WHERE t.domain IN ['knowledge synthesis', 'cross-modal analysis', 
                              'network science', 'information theory', 'systems theory']
            RETURN t.name as name, 
                   t.description as description,
                   t.keywords as keywords, 
                   t.domain as domain,
                   t.applicability_conditions as conditions,
                   t.confidence_score as base_score
            ORDER BY t.citation_count DESC
            LIMIT 10
            """
            
            return await self.neo4j_manager.execute_read_query(fallback_query)
            
        except Exception as e:
            logger.warning(f"Theory database query failed: {e}")
            return []
    
    async def _search_theories_by_similarity(self, evidence_base: Dict) -> List[Dict]:
        """Search for theories using semantic similarity.
        
        Args:
            evidence_base: Evidence to match against
            
        Returns:
            List of similar theories
        """
        try:
            # Create evidence description
            evidence_desc = await self._create_evidence_description(evidence_base)
            
            if not evidence_desc:
                return []
            
            # Get all theories with embeddings
            if not self._theories_cached:
                await self._cache_theory_embeddings()
            
            if not self.theory_embeddings:
                return []
            
            # Compute similarity
            evidence_embedding = self.theory_model.encode([evidence_desc])
            
            similarities = []
            for theory_id, theory_data in self.theory_embeddings.items():
                similarity = cosine_similarity(
                    evidence_embedding,
                    theory_data['embedding'].reshape(1, -1)
                )[0][0]
                
                similarities.append({
                    'theory': theory_data['theory'],
                    'similarity': similarity
                })
            
            # Sort by similarity
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            
            # Return top matches
            return [item['theory'] for item in similarities[:10]]
            
        except Exception as e:
            logger.error(f"Semantic theory search failed: {e}")
            return []
    
    async def _cache_theory_embeddings(self):
        """Cache embeddings for all theories in database."""
        try:
            query = """
            MATCH (t:Theory)
            RETURN t.id as id, 
                   t.name as name,
                   t.description as description,
                   t.keywords as keywords,
                   t.domain as domain
            """
            
            theories = await self.neo4j_manager.execute_read_query(query)
            
            for theory in theories:
                # Create theory text representation
                theory_text = f"{theory['name']} {theory.get('description', '')} {' '.join(theory.get('keywords', []))}"
                
                # Generate embedding
                embedding = self.theory_model.encode(theory_text)
                
                self.theory_embeddings[theory['id']] = {
                    'embedding': embedding,
                    'theory': theory
                }
            
            self._theories_cached = True
            logger.info(f"Cached embeddings for {len(self.theory_embeddings)} theories")
            
        except Exception as e:
            logger.error(f"Failed to cache theory embeddings: {e}")
    
    async def _create_evidence_description(self, evidence_base: Dict) -> str:
        """Create textual description of evidence for similarity matching.
        
        Args:
            evidence_base: Evidence dictionary
            
        Returns:
            Text description
        """
        parts = []
        
        # Describe entities
        entity_types = set()
        for entity in evidence_base.get('entities', [])[:10]:  # Limit to prevent too long descriptions
            if 'type' in entity:
                entity_types.add(entity['type'])
        
        if entity_types:
            parts.append(f"Entities of types: {', '.join(entity_types)}")
        
        # Describe relationships
        rel_types = set()
        for rel in evidence_base.get('relationships', [])[:10]:
            if 'type' in rel:
                rel_types.add(rel['type'].replace('_', ' '))
        
        if rel_types:
            parts.append(f"Relationships: {', '.join(rel_types)}")
        
        # Add modalities
        if 'modalities' in evidence_base:
            parts.append(f"Modalities: {', '.join(evidence_base['modalities'])}")
        
        # Add any patterns or anomalies
        if 'patterns' in evidence_base:
            parts.append(f"Patterns observed: {len(evidence_base['patterns'])}")
        
        return ' '.join(parts)
    
    async def _score_theory_applicability(self, theory: Dict, evidence_base: Dict) -> float:
        """Score how applicable a theory is to the evidence.
        
        Args:
            theory: Theory dictionary
            evidence_base: Evidence dictionary
            
        Returns:
            Applicability score (0-1)
        """
        score = 0.0
        
        # Base score from theory confidence
        base_score = theory.get('base_score', 0.5)
        score += base_score * 0.3
        
        # Check domain match
        theory_domain = theory.get('domain', '').lower()
        evidence_concepts = await self._extract_concepts(evidence_base)
        
        domain_match = any(concept.lower() in theory_domain for concept in evidence_concepts)
        if domain_match:
            score += 0.2
        
        # Check keyword overlap
        theory_keywords = [kw.lower() for kw in theory.get('keywords', [])]
        keyword_overlap = sum(1 for concept in evidence_concepts 
                            if any(kw in concept.lower() or concept.lower() in kw 
                                  for kw in theory_keywords))
        
        keyword_score = min(keyword_overlap / max(len(theory_keywords), 1), 1.0) * 0.3
        score += keyword_score
        
        # Check applicability conditions
        conditions = theory.get('conditions', [])
        if conditions:
            # Simple check - in practice, would evaluate conditions
            condition_score = 0.2  # Default partial match
            score += condition_score
        else:
            score += 0.2  # No conditions = generally applicable
        
        return min(score, 1.0)
    
    async def _get_domain_specific_theories(self, evidence_base: Dict) -> List[Dict]:
        """Get domain-specific theories based on evidence characteristics.
        
        Args:
            evidence_base: Evidence dictionary
            
        Returns:
            List of domain-specific theories
        """
        theories = []
        
        # Analyze evidence characteristics
        has_network = len(evidence_base.get('relationships', [])) > 0
        has_multi_modal = len(evidence_base.get('modalities', [])) > 1
        has_temporal = any('timestamp' in e or 'date' in e 
                          for e in evidence_base.get('entities', []))
        
        # Add relevant theories based on characteristics
        if has_network:
            theories.append({
                'name': 'Network Theory',
                'description': 'Analyzes patterns and dynamics in networked systems',
                'domain': 'network science',
                'keywords': ['network', 'graph', 'connectivity', 'centrality', 'clustering'],
                'conditions': ['presence of relational data'],
                'base_score': 0.8
            })
            
            theories.append({
                'name': 'Small World Theory',
                'description': 'Studies networks with high clustering and short path lengths',
                'domain': 'network science',
                'keywords': ['small world', 'six degrees', 'clustering coefficient'],
                'conditions': ['network with clustering patterns'],
                'base_score': 0.6
            })
        
        if has_multi_modal:
            theories.append({
                'name': 'Information Integration Theory',
                'description': 'Explains how information from multiple sources is combined',
                'domain': 'cognitive science',
                'keywords': ['integration', 'multi-modal', 'fusion', 'synthesis'],
                'conditions': ['multiple data modalities'],
                'base_score': 0.7
            })
            
            theories.append({
                'name': 'Multimodal Learning Theory',
                'description': 'Framework for learning from heterogeneous data sources',
                'domain': 'machine learning',
                'keywords': ['multimodal', 'cross-modal', 'heterogeneous', 'fusion'],
                'conditions': ['diverse data types'],
                'base_score': 0.65
            })
        
        if has_temporal:
            theories.append({
                'name': 'Temporal Network Theory',
                'description': 'Analyzes time-varying networks and dynamic processes',
                'domain': 'temporal networks',
                'keywords': ['temporal', 'dynamic', 'evolution', 'time-series'],
                'conditions': ['temporal data available'],
                'base_score': 0.7
            })
        
        # Always include general theories
        theories.extend([
            {
                'name': 'Systems Theory',
                'description': 'Holistic approach to analyzing complex interconnected systems',
                'domain': 'systems science',
                'keywords': ['system', 'emergence', 'complexity', 'holistic'],
                'conditions': [],
                'base_score': 0.5
            },
            {
                'name': 'Knowledge Graph Theory',
                'description': 'Framework for representing and reasoning with structured knowledge',
                'domain': 'knowledge representation',
                'keywords': ['knowledge graph', 'ontology', 'semantic', 'reasoning'],
                'conditions': ['structured entity data'],
                'base_score': 0.6
            }
        ])
        
        return theories
    
    async def _get_default_theories(self) -> List[Dict[str, Any]]:
        """Get default theories when other methods fail.
        
        Returns:
            List of basic applicable theories
        """
        return [
            {
                'name': 'General Systems Theory',
                'applicability': 0.6,
                'description': 'Provides a framework for analyzing complex systems',
                'domain': 'systems science',
                'conditions': [],
                'key_concepts': ['system', 'interaction', 'emergence']
            },
            {
                'name': 'Information Theory',
                'applicability': 0.5,
                'description': 'Mathematical framework for information processing and transmission',
                'domain': 'information science',
                'conditions': [],
                'key_concepts': ['information', 'entropy', 'communication']
            }
        ]