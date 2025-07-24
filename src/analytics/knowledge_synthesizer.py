#!/usr/bin/env python3
"""
Conceptual Knowledge Synthesizer - Synthesize knowledge across modalities to generate research insights

Implements abductive, inductive, and deductive reasoning to synthesize cross-modal knowledge
and generate novel research hypotheses with comprehensive error handling.
"""

import asyncio
import time
import logging
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime
from collections import defaultdict, Counter
import json

from .graph_centrality_analyzer import AnalyticsError

logger = logging.getLogger(__name__)


class HypothesisGenerator:
    """Generate research hypotheses using various reasoning strategies"""
    
    def __init__(self, llm_service=None):
        if llm_service is None:
            from .real_llm_service import RealLLMService
            self.llm_service = RealLLMService()
        else:
            self.llm_service = llm_service
        
    async def generate_hypotheses(self, prompt: str, max_hypotheses: int = 5, 
                                creativity_level: float = 0.7) -> List[Dict[str, Any]]:
        """Generate research hypotheses using LLM"""
        
        # Use structured hypothesis generation if available
        if hasattr(self.llm_service, 'generate_structured_hypotheses'):
            return await self.llm_service.generate_structured_hypotheses(
                prompt, max_hypotheses, creativity_level
            )
        
        # Fallback to text generation and parsing
        raw_hypotheses = await self.llm_service.generate_text(
            prompt, max_length=500, temperature=creativity_level
        )
        
        # Parse and structure hypotheses
        hypotheses = await self._parse_hypotheses(raw_hypotheses, max_hypotheses)
        
        return hypotheses
    
    async def _parse_hypotheses(self, raw_text: str, max_count: int) -> List[Dict[str, Any]]:
        """Parse raw hypothesis text into structured format"""
        
        # Simple parsing - split by numbers or bullet points
        lines = raw_text.strip().split('\n')
        hypotheses = []
        
        current_hypothesis = ""
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if it's a new hypothesis (starts with number or bullet)
            if (line.startswith(('1.', '2.', '3.', '4.', '5.', '•', '-', '*')) or
                len(hypotheses) == 0):
                
                if current_hypothesis:
                    # Save previous hypothesis
                    hypothesis = await self._structure_hypothesis(current_hypothesis, len(hypotheses))
                    hypotheses.append(hypothesis)
                    
                    if len(hypotheses) >= max_count:
                        break
                
                # Start new hypothesis
                current_hypothesis = line.lstrip('123456789.•-* ')
            else:
                # Continue current hypothesis
                current_hypothesis += " " + line
        
        # Add final hypothesis
        if current_hypothesis and len(hypotheses) < max_count:
            hypothesis = await self._structure_hypothesis(current_hypothesis, len(hypotheses))
            hypotheses.append(hypothesis)
        
        return hypotheses[:max_count]
    
    async def _structure_hypothesis(self, text: str, index: int) -> Dict[str, Any]:
        """Structure hypothesis text into formal format"""
        
        return {
            'id': f'hypothesis_{index}',
            'text': text.strip(),
            'confidence_score': 0.7,  # Default confidence
            'novelty_score': 0.6,     # Default novelty
            'testability_score': 0.8, # Default testability
            'evidence_support': [],
            'reasoning_type': 'abductive'
        }



class ConceptualKnowledgeSynthesizer:
    """Synthesize knowledge across modalities to generate research insights"""
    
    def __init__(self, neo4j_manager, distributed_tx_manager, llm_service=None):
        self.neo4j_manager = neo4j_manager
        self.dtm = distributed_tx_manager
        
        # Use real LLM service if none provided
        if llm_service is None:
            from .real_llm_service import RealLLMService
            self.llm_service = RealLLMService()
        else:
            self.llm_service = llm_service
            
        self.hypothesis_generator = HypothesisGenerator(self.llm_service)
        
        # Initialize advanced scoring
        from .advanced_scoring import AdvancedScoring
        self.scorer = AdvancedScoring()
        
        # Initialize theory knowledge base
        from .theory_knowledge_base import TheoryKnowledgeBase
        self.theory_kb = TheoryKnowledgeBase(neo4j_manager)
        
        # Synthesis strategies
        self.synthesis_strategies = {
            'inductive': self._inductive_synthesis,
            'deductive': self._deductive_synthesis,
            'abductive': self._abductive_synthesis
        }
        
        # Configuration
        self.max_evidence_items = 100
        self.anomaly_threshold = 2.0  # Standard deviations
        self.confidence_threshold = 0.7
        
        logger.info("ConceptualKnowledgeSynthesizer initialized")
    
    async def synthesize_research_insights(self, domain: str, 
                                         synthesis_strategy: str = 'abductive',
                                         confidence_threshold: float = 0.7,
                                         max_hypotheses: int = 5) -> Dict[str, Any]:
        """Synthesize cross-modal knowledge to generate research insights"""
        
        tx_id = f"knowledge_synthesis_{domain}_{int(time.time())}"
        logger.info(f"Starting knowledge synthesis - domain: {domain}, strategy: {synthesis_strategy}, tx_id: {tx_id}")
        
        try:
            await self.dtm.begin_distributed_transaction(tx_id)
            
            # Gather cross-modal evidence for domain
            evidence_base = await self._gather_cross_modal_evidence(domain)
            
            if not evidence_base or not evidence_base.get('entities'):
                logger.warning(f"No evidence found for domain: {domain}")
                await self.dtm.commit_distributed_transaction(tx_id)
                return {
                    'domain': domain,
                    'synthesis_strategy': synthesis_strategy,
                    'evidence_base': {'entities': [], 'relationships': []},
                    'synthesis_results': {},
                    'generated_hypotheses': [],
                    'confidence_metrics': {'overall_confidence': 0.0}
                }
            
            # Apply synthesis strategy
            start_time = time.time()
            synthesis_results = await self.synthesis_strategies[synthesis_strategy](
                evidence_base, confidence_threshold
            )
            execution_time = time.time() - start_time
            
            # Generate research hypotheses
            hypotheses = await self._generate_research_hypotheses(
                synthesis_results, max_hypotheses
            )
            
            # Validate hypotheses against existing knowledge
            validated_hypotheses = await self._validate_hypotheses(hypotheses, evidence_base)
            
            # Store synthesis results with full provenance
            await self._store_synthesis_results(tx_id, synthesis_results, validated_hypotheses)
            
            await self.dtm.commit_distributed_transaction(tx_id)
            
            result = {
                'domain': domain,
                'synthesis_strategy': synthesis_strategy,
                'evidence_base': evidence_base,
                'synthesis_results': synthesis_results,
                'generated_hypotheses': validated_hypotheses,
                'confidence_metrics': await self._calculate_synthesis_confidence(synthesis_results),
                'metadata': {
                    'execution_time': execution_time,
                    'evidence_count': len(evidence_base.get('entities', [])),
                    'hypothesis_count': len(validated_hypotheses),
                    'confidence_threshold': confidence_threshold
                }
            }
            
            logger.info(f"Knowledge synthesis completed in {execution_time:.2f}s - generated {len(validated_hypotheses)} hypotheses")
            return result
            
        except Exception as e:
            logger.error(f"Knowledge synthesis failed: {e}", exc_info=True)
            await self.dtm.rollback_distributed_transaction(tx_id)
            raise AnalyticsError(f"Knowledge synthesis failed: {e}")
    
    async def _gather_cross_modal_evidence(self, domain: str) -> Dict[str, Any]:
        """Gather cross-modal evidence for the specified domain"""
        
        logger.info(f"Gathering cross-modal evidence for domain: {domain}")
        
        # Query for entities and relationships in the domain
        entity_query = """
        MATCH (e)
        WHERE any(label IN labels(e) WHERE toLower(label) CONTAINS toLower($domain))
           OR any(prop IN keys(e) WHERE toLower(toString(e[prop])) CONTAINS toLower($domain))
        RETURN id(e) as entity_id, labels(e) as labels, properties(e) as props
        LIMIT $max_entities
        """
        
        relationship_query = """
        MATCH (a)-[r]->(b)
        WHERE any(label IN labels(a) WHERE toLower(label) CONTAINS toLower($domain))
           OR any(label IN labels(b) WHERE toLower(label) CONTAINS toLower($domain))
        RETURN id(a) as source_id, id(b) as target_id, type(r) as rel_type,
               properties(r) as rel_props, labels(a) as source_labels, 
               labels(b) as target_labels
        LIMIT $max_relationships
        """
        
        params = {
            'domain': domain,
            'max_entities': self.max_evidence_items,
            'max_relationships': self.max_evidence_items * 2
        }
        
        # Execute queries
        await self.dtm.add_operation(self.dtm.current_tx_id, 'read', 'neo4j', 'evidence_entities', {
            'query': entity_query,
            'params': params,
            'operation_type': 'synthesis_evidence_fetch'
        })
        
        await self.dtm.add_operation(self.dtm.current_tx_id, 'read', 'neo4j', 'evidence_relationships', {
            'query': relationship_query,
            'params': params,
            'operation_type': 'synthesis_evidence_fetch'
        })
        
        entities_data = await self.neo4j_manager.execute_read_query(entity_query, params)
        relationships_data = await self.neo4j_manager.execute_read_query(relationship_query, params)
        
        # Process evidence
        entities = []
        for record in entities_data:
            entity = {
                'id': record['entity_id'],
                'labels': record['labels'],
                'properties': record['props'],
                'modality': self._determine_modality(record['labels'], record['props'])
            }
            entities.append(entity)
        
        relationships = []
        for record in relationships_data:
            relationship = {
                'source_id': record['source_id'],
                'target_id': record['target_id'],
                'type': record['rel_type'],
                'properties': record['rel_props'],
                'source_labels': record['source_labels'],
                'target_labels': record['target_labels']
            }
            relationships.append(relationship)
        
        logger.info(f"Gathered {len(entities)} entities and {len(relationships)} relationships")
        
        return {
            'domain': domain,
            'entities': entities,
            'relationships': relationships,
            'modality_distribution': self._analyze_modality_distribution(entities)
        }
    
    def _determine_modality(self, labels: List[str], properties: Dict[str, Any]) -> str:
        """Determine the modality of an entity based on labels and properties"""
        
        # Check labels for modality indicators
        text_indicators = ['Text', 'Document', 'Paper', 'Article', 'Content']
        image_indicators = ['Image', 'Figure', 'Photo', 'Visual', 'Diagram']
        structured_indicators = ['Data', 'Table', 'Schema', 'Metadata', 'Structure']
        
        for label in labels:
            if any(indicator in label for indicator in text_indicators):
                return 'text'
            elif any(indicator in label for indicator in image_indicators):
                return 'image'
            elif any(indicator in label for indicator in structured_indicators):
                return 'structured'
        
        # Check properties for modality indicators
        if properties:
            if any(prop in ['text', 'content', 'title', 'abstract'] for prop in properties.keys()):
                return 'text'
            elif any(prop in ['image_path', 'image_url', 'visual_data'] for prop in properties.keys()):
                return 'image'
            elif any(prop in ['data', 'metadata', 'schema'] for prop in properties.keys()):
                return 'structured'
        
        return 'unknown'
    
    def _analyze_modality_distribution(self, entities: List[Dict]) -> Dict[str, int]:
        """Analyze the distribution of entities across modalities"""
        
        modality_counts = Counter()
        for entity in entities:
            modality_counts[entity['modality']] += 1
        
        return dict(modality_counts)
    
    async def _abductive_synthesis(self, evidence_base: Dict, 
                                 confidence_threshold: float) -> Dict[str, Any]:
        """Abductive reasoning to generate best explanatory hypotheses"""
        
        logger.info("Applying abductive synthesis strategy")
        
        # Extract surprising patterns and anomalies
        anomalies = await self._detect_knowledge_anomalies(evidence_base)
        
        # Generate explanatory hypotheses for anomalies
        explanatory_hypotheses = []
        
        for anomaly in anomalies:
            # Create hypothesis prompt
            hypothesis_prompt = await self._create_hypothesis_prompt(anomaly, evidence_base)
            
            # Generate hypotheses using LLM
            generated_hypotheses = await self.hypothesis_generator.generate_hypotheses(
                prompt=hypothesis_prompt,
                max_hypotheses=3,
                creativity_level=0.7
            )
            
            # Score hypotheses based on explanatory power and simplicity
            scored_hypotheses = await self._score_explanatory_hypotheses(
                generated_hypotheses, anomaly, evidence_base
            )
            
            # Filter by confidence threshold
            high_confidence_hypotheses = [
                h for h in scored_hypotheses 
                if h['confidence_score'] >= confidence_threshold
            ]
            
            explanatory_hypotheses.extend(high_confidence_hypotheses)
        
        # Calculate overall synthesis confidence
        synthesis_confidence = np.mean([h['confidence_score'] for h in explanatory_hypotheses]) if explanatory_hypotheses else 0.0
        
        return {
            'strategy': 'abductive',
            'anomalies_detected': len(anomalies),
            'hypotheses_generated': len(explanatory_hypotheses),
            'hypotheses': explanatory_hypotheses,
            'synthesis_confidence': synthesis_confidence,
            'anomalies': anomalies
        }
    
    async def _inductive_synthesis(self, evidence_base: Dict, 
                                 confidence_threshold: float) -> Dict[str, Any]:
        """Inductive reasoning to generate patterns from evidence"""
        
        logger.info("Applying inductive synthesis strategy")
        
        # Extract patterns from evidence
        patterns = await self._extract_inductive_patterns(evidence_base)
        
        # Generate generalizations from patterns
        generalizations = await self._generate_generalizations(patterns, evidence_base)
        
        # Score generalizations
        scored_generalizations = await self._score_generalizations(
            generalizations, evidence_base, confidence_threshold
        )
        
        synthesis_confidence = np.mean([g['confidence_score'] for g in scored_generalizations]) if scored_generalizations else 0.0
        
        return {
            'strategy': 'inductive',
            'patterns_found': len(patterns),
            'generalizations_generated': len(scored_generalizations),
            'hypotheses': scored_generalizations,
            'synthesis_confidence': synthesis_confidence,
            'patterns': patterns
        }
    
    async def _deductive_synthesis(self, evidence_base: Dict, 
                                 confidence_threshold: float) -> Dict[str, Any]:
        """Deductive reasoning to apply known theories to evidence"""
        
        logger.info("Applying deductive synthesis strategy")
        
        # Identify applicable theories
        applicable_theories = await self._identify_applicable_theories(evidence_base)
        
        # Apply theories to generate predictions
        predictions = await self._apply_theories_to_evidence(applicable_theories, evidence_base)
        
        # Score predictions
        scored_predictions = await self._score_predictions(
            predictions, evidence_base, confidence_threshold
        )
        
        synthesis_confidence = np.mean([p['confidence_score'] for p in scored_predictions]) if scored_predictions else 0.0
        
        return {
            'strategy': 'deductive',
            'theories_applied': len(applicable_theories),
            'predictions_generated': len(scored_predictions),
            'hypotheses': scored_predictions,
            'synthesis_confidence': synthesis_confidence,
            'applicable_theories': applicable_theories
        }
    
    async def _detect_knowledge_anomalies(self, evidence_base: Dict) -> List[Dict[str, Any]]:
        """Detect surprising patterns and anomalies in the evidence"""
        
        anomalies = []
        entities = evidence_base['entities']
        relationships = evidence_base['relationships']
        
        # Detect entity degree anomalies
        entity_degrees = Counter()
        for rel in relationships:
            entity_degrees[rel['source_id']] += 1
            entity_degrees[rel['target_id']] += 1
        
        degrees = list(entity_degrees.values())
        if degrees:
            mean_degree = np.mean(degrees)
            std_degree = np.std(degrees)
            
            # Find entities with unusually high or low degrees
            for entity_id, degree in entity_degrees.items():
                z_score = abs(degree - mean_degree) / std_degree if std_degree > 0 else 0
                if z_score > self.anomaly_threshold:
                    anomalies.append({
                        'type': 'degree_anomaly',
                        'entity_id': entity_id,
                        'degree': degree,
                        'z_score': z_score,
                        'description': f'Entity has unusually {"high" if degree > mean_degree else "low"} connectivity'
                    })
        
        # Detect cross-modal relationship anomalies
        cross_modal_rels = []
        for rel in relationships:
            source_entity = next((e for e in entities if e['id'] == rel['source_id']), None)
            target_entity = next((e for e in entities if e['id'] == rel['target_id']), None)
            
            if source_entity and target_entity:
                source_modality = source_entity['modality']
                target_modality = target_entity['modality']
                
                if source_modality != target_modality and source_modality != 'unknown' and target_modality != 'unknown':
                    cross_modal_rels.append(rel)
        
        if cross_modal_rels:
            # High number of cross-modal relationships might be anomalous
            cross_modal_ratio = len(cross_modal_rels) / len(relationships)
            if cross_modal_ratio > 0.3:  # More than 30% cross-modal
                anomalies.append({
                    'type': 'cross_modal_anomaly',
                    'cross_modal_count': len(cross_modal_rels),
                    'total_relationships': len(relationships),
                    'ratio': cross_modal_ratio,
                    'description': 'Unusually high proportion of cross-modal relationships'
                })
        
        # Detect isolated entity clusters
        # Simple clustering based on connectivity
        entity_clusters = await self._find_entity_clusters(entities, relationships)
        isolated_clusters = [cluster for cluster in entity_clusters if len(cluster) < 3]
        
        if len(isolated_clusters) > len(entity_clusters) * 0.2:  # More than 20% isolated
            anomalies.append({
                'type': 'fragmentation_anomaly',
                'isolated_clusters': len(isolated_clusters),
                'total_clusters': len(entity_clusters),
                'description': 'High degree of knowledge fragmentation detected'
            })
        
        logger.info(f"Detected {len(anomalies)} knowledge anomalies")
        return anomalies
    
    async def _find_entity_clusters(self, entities: List[Dict], 
                                  relationships: List[Dict]) -> List[List[int]]:
        """Find connected components in the entity graph"""
        
        # Build adjacency list
        adjacency = defaultdict(set)
        for rel in relationships:
            adjacency[rel['source_id']].add(rel['target_id'])
            adjacency[rel['target_id']].add(rel['source_id'])
        
        # Find connected components using DFS
        visited = set()
        clusters = []
        
        for entity in entities:
            entity_id = entity['id']
            if entity_id not in visited:
                cluster = []
                stack = [entity_id]
                
                while stack:
                    current = stack.pop()
                    if current not in visited:
                        visited.add(current)
                        cluster.append(current)
                        
                        # Add connected entities
                        for neighbor in adjacency[current]:
                            if neighbor not in visited:
                                stack.append(neighbor)
                
                if cluster:
                    clusters.append(cluster)
        
        return clusters
    
    async def _create_hypothesis_prompt(self, anomaly: Dict, evidence_base: Dict) -> str:
        """Create a prompt for hypothesis generation based on anomaly"""
        
        domain = evidence_base['domain']
        modality_dist = evidence_base['modality_distribution']
        
        prompt = f"""
        Research Domain: {domain}
        
        Anomaly Detected: {anomaly['description']}
        Anomaly Type: {anomaly['type']}
        
        Evidence Context:
        - Total entities: {len(evidence_base['entities'])}
        - Total relationships: {len(evidence_base['relationships'])}
        - Modality distribution: {modality_dist}
        
        Generate research hypotheses that could explain this anomaly. Consider:
        1. What underlying mechanisms could cause this pattern?
        2. How might this relate to known research phenomena?
        3. What implications does this have for the field?
        
        Provide testable hypotheses that explain the observed anomaly.
        """
        
        return prompt.strip()
    
    async def _score_explanatory_hypotheses(self, hypotheses: List[Dict], 
                                          anomaly: Dict, evidence_base: Dict) -> List[Dict]:
        """Score hypotheses based on explanatory power and simplicity"""
        
        scored_hypotheses = []
        
        for hypothesis in hypotheses:
            # Calculate explanatory power (how well it explains the anomaly)
            explanatory_power = await self._calculate_explanatory_power(hypothesis, anomaly)
            
            # Calculate simplicity (Occam's razor)
            simplicity = await self._calculate_simplicity(hypothesis)
            
            # Calculate testability
            testability = await self._calculate_testability(hypothesis, evidence_base)
            
            # Combined confidence score
            confidence_score = (explanatory_power * 0.4 + simplicity * 0.3 + testability * 0.3)
            
            scored_hypothesis = hypothesis.copy()
            scored_hypothesis.update({
                'explanatory_power': explanatory_power,
                'simplicity': simplicity,
                'testability': testability,
                'confidence_score': confidence_score,
                'anomaly_explained': anomaly['type']
            })
            
            scored_hypotheses.append(scored_hypothesis)
        
        # Sort by confidence score
        scored_hypotheses.sort(key=lambda x: x['confidence_score'], reverse=True)
        
        return scored_hypotheses
    
    async def _calculate_explanatory_power(self, hypothesis: Dict, anomaly: Dict) -> float:
        """Calculate how well the hypothesis explains the anomaly"""
        # Use advanced NLP-based scoring
        return await self.scorer.calculate_explanatory_power(hypothesis, anomaly)
    
    async def _calculate_simplicity(self, hypothesis: Dict) -> float:
        """Calculate hypothesis simplicity (fewer assumptions = higher score)"""
        # Use advanced linguistic analysis
        return await self.scorer.calculate_simplicity(hypothesis)
    
    async def _calculate_testability(self, hypothesis: Dict, evidence_base: Dict) -> float:
        """Calculate how testable the hypothesis is given available evidence"""
        # Use advanced NLP-based testability analysis
        return await self.scorer.calculate_testability(hypothesis, evidence_base)
    
    async def _extract_inductive_patterns(self, evidence_base: Dict) -> List[Dict[str, Any]]:
        """Extract patterns from evidence for inductive reasoning"""
        
        patterns = []
        entities = evidence_base['entities']
        relationships = evidence_base['relationships']
        
        # Pattern 1: Label co-occurrence patterns
        label_pairs = Counter()
        for rel in relationships:
            source_entity = next((e for e in entities if e['id'] == rel['source_id']), None)
            target_entity = next((e for e in entities if e['id'] == rel['target_id']), None)
            
            if source_entity and target_entity:
                for source_label in source_entity['labels']:
                    for target_label in target_entity['labels']:
                        if source_label != target_label:
                            pair = tuple(sorted([source_label, target_label]))
                            label_pairs[pair] += 1
        
        # Find frequent label pairs
        total_relationships = len(relationships)
        for pair, count in label_pairs.most_common(10):
            frequency = count / total_relationships
            if frequency > 0.1:  # Appears in more than 10% of relationships
                patterns.append({
                    'type': 'label_co_occurrence',
                    'pattern': f'{pair[0]} often connects to {pair[1]}',
                    'frequency': frequency,
                    'support_count': count
                })
        
        # Pattern 2: Modality interaction patterns
        modality_pairs = Counter()
        for rel in relationships:
            source_entity = next((e for e in entities if e['id'] == rel['source_id']), None)
            target_entity = next((e for e in entities if e['id'] == rel['target_id']), None)
            
            if source_entity and target_entity:
                source_modality = source_entity['modality']
                target_modality = target_entity['modality']
                
                if source_modality != 'unknown' and target_modality != 'unknown':
                    pair = tuple(sorted([source_modality, target_modality]))
                    modality_pairs[pair] += 1
        
        for pair, count in modality_pairs.most_common(5):
            frequency = count / total_relationships
            patterns.append({
                'type': 'modality_interaction',
                'pattern': f'{pair[0]} and {pair[1]} modalities frequently interact',
                'frequency': frequency,
                'support_count': count
            })
        
        return patterns
    
    async def _generate_generalizations(self, patterns: List[Dict], 
                                      evidence_base: Dict) -> List[Dict[str, Any]]:
        """Generate generalizations from detected patterns"""
        
        generalizations = []
        
        for pattern in patterns:
            if pattern['type'] == 'label_co_occurrence':
                generalization = {
                    'text': f"In {evidence_base['domain']} research, {pattern['pattern']} occurs in {pattern['frequency']:.1%} of cases, suggesting a systematic relationship between these concepts.",
                    'pattern_type': pattern['type'],
                    'evidence_strength': pattern['frequency'],
                    'reasoning_type': 'inductive'
                }
                generalizations.append(generalization)
            
            elif pattern['type'] == 'modality_interaction':
                generalization = {
                    'text': f"Cross-modal analysis reveals that {pattern['pattern']}, indicating integrated knowledge representation across data types.",
                    'pattern_type': pattern['type'],
                    'evidence_strength': pattern['frequency'],
                    'reasoning_type': 'inductive'
                }
                generalizations.append(generalization)
        
        return generalizations
    
    async def _score_generalizations(self, generalizations: List[Dict], 
                                   evidence_base: Dict, threshold: float) -> List[Dict]:
        """Score inductive generalizations"""
        
        scored = []
        
        for gen in generalizations:
            # Score based on evidence strength and generalizability
            evidence_strength = gen.get('evidence_strength', 0)
            
            # Higher evidence strength = higher confidence
            confidence_score = min(evidence_strength * 2, 1.0)  # Cap at 1.0
            
            if confidence_score >= threshold:
                scored_gen = gen.copy()
                scored_gen['confidence_score'] = confidence_score
                scored_gen['novelty_score'] = 0.6  # Default novelty
                scored_gen['testability_score'] = 0.8  # Inductive patterns are generally testable
                scored.append(scored_gen)
        
        return scored
    
    async def _identify_applicable_theories(self, evidence_base: Dict) -> List[Dict[str, Any]]:
        """Identify theories applicable to the evidence"""
        # Use real theory knowledge base
        return await self.theory_kb.identify_applicable_theories(evidence_base)
    
    async def _apply_theories_to_evidence(self, theories: List[Dict], 
                                        evidence_base: Dict) -> List[Dict[str, Any]]:
        """Apply theories to generate predictions"""
        
        predictions = []
        
        for theory in theories:
            prediction = {
                'text': f"Based on {theory['name']}, we predict that {evidence_base['domain']} entities will exhibit {theory['description']} with measurable outcomes.",
                'theory_applied': theory['name'],
                'applicability_score': theory['applicability'],
                'reasoning_type': 'deductive'
            }
            predictions.append(prediction)
        
        return predictions
    
    async def _score_predictions(self, predictions: List[Dict], 
                               evidence_base: Dict, threshold: float) -> List[Dict]:
        """Score deductive predictions"""
        
        scored = []
        
        for pred in predictions:
            # Score based on theory applicability
            applicability = pred.get('applicability_score', 0)
            confidence_score = applicability  # Direct mapping for simplicity
            
            if confidence_score >= threshold:
                scored_pred = pred.copy()
                scored_pred['confidence_score'] = confidence_score
                scored_pred['novelty_score'] = 0.5  # Deductive reasoning is less novel
                scored_pred['testability_score'] = 0.9  # Theory-based predictions are highly testable
                scored.append(scored_pred)
        
        return scored
    
    async def _generate_research_hypotheses(self, synthesis_results: Dict, 
                                          max_hypotheses: int) -> List[Dict[str, Any]]:
        """Generate research hypotheses from synthesis results"""
        
        # Return hypotheses from synthesis results
        hypotheses = synthesis_results.get('hypotheses', [])
        
        # Limit to max_hypotheses
        return hypotheses[:max_hypotheses]
    
    async def _validate_hypotheses(self, hypotheses: List[Dict], 
                                 evidence_base: Dict) -> List[Dict[str, Any]]:
        """Validate hypotheses against existing knowledge"""
        
        validated = []
        
        for hypothesis in hypotheses:
            # Simple validation - check if hypothesis is supported by evidence
            validation_score = await self._calculate_evidence_support(hypothesis, evidence_base)
            
            validated_hypothesis = hypothesis.copy()
            validated_hypothesis['validation_score'] = validation_score
            validated_hypothesis['evidence_support'] = validation_score > 0.5
            
            validated.append(validated_hypothesis)
        
        # Sort by validation score
        validated.sort(key=lambda x: x.get('validation_score', 0), reverse=True)
        
        return validated
    
    async def _calculate_evidence_support(self, hypothesis: Dict, 
                                        evidence_base: Dict) -> float:
        """Calculate how well the evidence supports the hypothesis"""
        
        # Simple heuristic based on keyword matching
        hypothesis_text = hypothesis.get('text', '').lower()
        
        # Count entities and relationships that might support the hypothesis
        support_count = 0
        total_items = len(evidence_base['entities']) + len(evidence_base['relationships'])
        
        # Check entity labels and properties
        for entity in evidence_base['entities']:
            for label in entity['labels']:
                if label.lower() in hypothesis_text:
                    support_count += 1
                    break
        
        # Check relationship types
        for rel in evidence_base['relationships']:
            if rel['type'].lower().replace('_', ' ') in hypothesis_text:
                support_count += 1
        
        return min(support_count / max(total_items, 1), 1.0)
    
    async def _calculate_synthesis_confidence(self, synthesis_results: Dict) -> Dict[str, float]:
        """Calculate overall confidence metrics for synthesis"""
        
        hypotheses = synthesis_results.get('hypotheses', [])
        
        if not hypotheses:
            return {'overall_confidence': 0.0}
        
        # Calculate various confidence metrics
        confidence_scores = [h.get('confidence_score', 0) for h in hypotheses]
        novelty_scores = [h.get('novelty_score', 0) for h in hypotheses]
        testability_scores = [h.get('testability_score', 0) for h in hypotheses]
        
        return {
            'overall_confidence': np.mean(confidence_scores),
            'average_novelty': np.mean(novelty_scores),
            'average_testability': np.mean(testability_scores),
            'confidence_std': np.std(confidence_scores),
            'high_confidence_count': sum(1 for score in confidence_scores if score > 0.8)
        }
    
    async def _store_synthesis_results(self, tx_id: str, synthesis_results: Dict, 
                                     hypotheses: List[Dict]) -> None:
        """Store synthesis results with provenance"""
        
        await self.dtm.add_operation(tx_id, 'write', 'neo4j', 'synthesis_results', {
            'synthesis_results': synthesis_results,
            'hypotheses': hypotheses,
            'operation_type': 'knowledge_synthesis_storage',
            'timestamp': datetime.now().isoformat()
        })
        
        logger.info(f"Knowledge synthesis results prepared for storage - {len(hypotheses)} hypotheses")