"""Advanced scoring using NLP models for hypothesis evaluation"""

import logging
from typing import Dict, List, Any, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import asyncio

logger = logging.getLogger(__name__)

# Try to import transformers for zero-shot classification
try:
    from transformers import pipeline
    HAS_TRANSFORMERS = True
except ImportError:
    logger.warning("transformers library not available, some advanced scoring features will be limited")
    HAS_TRANSFORMERS = False


class AdvancedScoring:
    """Advanced scoring using NLP models for hypothesis and synthesis evaluation"""
    
    def __init__(self):
        """Initialize NLP models for scoring"""
        # Initialize sentence similarity model
        self.similarity_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize classification pipelines if available
        if HAS_TRANSFORMERS:
            try:
                self.classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
                self.qa_model = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")
                logger.info("Initialized advanced NLP pipelines for scoring")
            except Exception as e:
                logger.warning(f"Failed to initialize NLP pipelines: {e}")
                self.classifier = None
                self.qa_model = None
        else:
            self.classifier = None
            self.qa_model = None
    
    async def calculate_explanatory_power(self, hypothesis: Dict, anomaly: Dict) -> float:
        """Calculate explanatory power using semantic similarity and classification.
        
        Args:
            hypothesis: Hypothesis dictionary with 'text' field
            anomaly: Anomaly dictionary with 'description' and 'type' fields
            
        Returns:
            Score between 0 and 1 indicating explanatory power
        """
        try:
            # Get embeddings for hypothesis and anomaly
            hypothesis_text = hypothesis.get('text', '')
            anomaly_text = anomaly.get('description', '')
            
            if not hypothesis_text or not anomaly_text:
                return 0.5  # Default score if missing text
            
            # Calculate semantic similarity
            embeddings = self.similarity_model.encode([hypothesis_text, anomaly_text])
            similarity = cosine_similarity(embeddings[0:1], embeddings[1:2])[0][0]
            
            # Use zero-shot classification if available
            if self.classifier:
                try:
                    # Check if hypothesis explains anomaly
                    result = await self._run_classifier(
                        hypothesis_text,
                        candidate_labels=['explains anomaly', 'unrelated to anomaly', 'partially explains anomaly'],
                        hypothesis_template="This hypothesis {} the observed pattern."
                    )
                    
                    # Map classification scores
                    explanation_scores = {
                        'explains anomaly': 1.0,
                        'partially explains anomaly': 0.7,
                        'unrelated to anomaly': 0.3
                    }
                    
                    top_label = result['labels'][0]
                    classification_score = explanation_scores.get(top_label, 0.5) * result['scores'][0]
                    
                    # Combine semantic similarity and classification
                    return (similarity + classification_score) / 2
                    
                except Exception as e:
                    logger.warning(f"Classification failed: {e}")
                    return similarity
            else:
                # Enhanced similarity score based on key concepts
                key_concepts = anomaly.get('type', '').replace('_', ' ').split()
                concept_matches = sum(1 for concept in key_concepts if concept.lower() in hypothesis_text.lower())
                concept_bonus = min(concept_matches / max(len(key_concepts), 1), 0.3)
                
                return min(similarity + concept_bonus, 1.0)
                
        except Exception as e:
            logger.error(f"Failed to calculate explanatory power: {e}")
            return 0.5
    
    async def calculate_testability(self, hypothesis: Dict, evidence_base: Dict) -> float:
        """Calculate testability using NLP analysis.
        
        Args:
            hypothesis: Hypothesis dictionary
            evidence_base: Available evidence
            
        Returns:
            Score between 0 and 1 indicating testability
        """
        try:
            hypothesis_text = hypothesis.get('text', '')
            
            if not hypothesis_text:
                return 0.5
            
            # Base testability score from language patterns
            testability_score = await self._analyze_testability_language(hypothesis_text)
            
            # Check if we have evidence to test it
            evidence_texts = []
            for entity in evidence_base.get('entities', []):
                if 'text' in entity:
                    evidence_texts.append(entity['text'])
                elif 'description' in entity:
                    evidence_texts.append(entity['description'])
            
            if evidence_texts and self.qa_model:
                # Try to answer questions about the hypothesis using evidence
                sample_question = f"What evidence supports this claim: {hypothesis_text[:200]}?"
                
                try:
                    # Combine evidence texts
                    context = ' '.join(evidence_texts[:10])  # Limit context size
                    
                    answer = await self._run_qa(sample_question, context)
                    
                    # Higher confidence in answer = more testable with current evidence
                    evidence_score = answer.get('score', 0) if answer else 0
                    testability_score = (testability_score + evidence_score) / 2
                    
                except Exception as e:
                    logger.warning(f"QA model failed: {e}")
            
            return min(testability_score, 1.0)
            
        except Exception as e:
            logger.error(f"Failed to calculate testability: {e}")
            return 0.5
    
    async def calculate_simplicity(self, hypothesis: Dict) -> float:
        """Calculate hypothesis simplicity using advanced linguistic analysis.
        
        Args:
            hypothesis: Hypothesis dictionary
            
        Returns:
            Score between 0 and 1 (higher = simpler)
        """
        try:
            text = hypothesis.get('text', '')
            
            if not text:
                return 0.5
            
            # Analyze linguistic complexity
            words = text.split()
            sentence_count = text.count('.') + text.count('!') + text.count('?')
            sentence_count = max(sentence_count, 1)
            
            # Average words per sentence (lower is simpler)
            avg_words_per_sentence = len(words) / sentence_count
            sentence_complexity = 1 - min(avg_words_per_sentence / 30, 1.0)
            
            # Complex word ratio (approximate using word length)
            complex_words = sum(1 for word in words if len(word) > 8)
            complex_ratio = complex_words / max(len(words), 1)
            word_simplicity = 1 - min(complex_ratio, 1.0)
            
            # Check for jargon and technical terms
            technical_indicators = [
                'mechanism', 'framework', 'paradigm', 'methodology', 'architecture',
                'infrastructure', 'implementation', 'optimization', 'algorithm'
            ]
            
            technical_count = sum(1 for term in technical_indicators if term in text.lower())
            technical_simplicity = 1 - min(technical_count / 5, 1.0)
            
            # Combine scores
            simplicity_score = (sentence_complexity + word_simplicity + technical_simplicity) / 3
            
            return simplicity_score
            
        except Exception as e:
            logger.error(f"Failed to calculate simplicity: {e}")
            return 0.5
    
    async def calculate_novelty(self, hypothesis: Dict, existing_knowledge: List[Dict]) -> float:
        """Calculate novelty by comparing to existing knowledge.
        
        Args:
            hypothesis: Hypothesis to evaluate
            existing_knowledge: List of existing hypotheses/theories
            
        Returns:
            Score between 0 and 1 (higher = more novel)
        """
        try:
            hypothesis_text = hypothesis.get('text', '')
            
            if not hypothesis_text or not existing_knowledge:
                return 0.7  # Default moderate novelty
            
            # Get embeddings for hypothesis and existing knowledge
            texts = [hypothesis_text] + [k.get('text', '') for k in existing_knowledge if k.get('text')]
            
            if len(texts) == 1:
                return 0.8  # High novelty if no existing knowledge
            
            embeddings = self.similarity_model.encode(texts)
            
            # Calculate similarity to each existing piece of knowledge
            hypothesis_embedding = embeddings[0:1]
            existing_embeddings = embeddings[1:]
            
            similarities = cosine_similarity(hypothesis_embedding, existing_embeddings)[0]
            
            # Novelty is inverse of maximum similarity
            max_similarity = np.max(similarities) if len(similarities) > 0 else 0
            novelty = 1 - max_similarity
            
            # Adjust based on conceptual uniqueness
            if self.classifier:
                try:
                    # Check if hypothesis introduces new concepts
                    result = await self._run_classifier(
                        hypothesis_text,
                        candidate_labels=['conventional idea', 'novel approach', 'revolutionary concept'],
                        hypothesis_template="This hypothesis represents a {}."
                    )
                    
                    novelty_scores = {
                        'revolutionary concept': 0.9,
                        'novel approach': 0.7,
                        'conventional idea': 0.3
                    }
                    
                    top_label = result['labels'][0]
                    classification_novelty = novelty_scores.get(top_label, 0.5)
                    
                    # Combine embedding and classification novelty
                    novelty = (novelty + classification_novelty) / 2
                    
                except Exception as e:
                    logger.warning(f"Novelty classification failed: {e}")
            
            return novelty
            
        except Exception as e:
            logger.error(f"Failed to calculate novelty: {e}")
            return 0.5
    
    async def _analyze_testability_language(self, text: str) -> float:
        """Analyze language patterns to determine testability.
        
        Args:
            text: Hypothesis text
            
        Returns:
            Base testability score
        """
        # Testable language patterns
        testable_patterns = [
            'if', 'then', 'when', 'causes', 'results in', 'leads to',
            'predicts', 'correlates', 'increases', 'decreases', 'affects'
        ]
        
        # Untestable language patterns
        untestable_patterns = [
            'might', 'possibly', 'perhaps', 'sometimes', 'occasionally',
            'in theory', 'conceptually', 'philosophically', 'arguably'
        ]
        
        text_lower = text.lower()
        
        # Count pattern matches
        testable_count = sum(1 for pattern in testable_patterns if pattern in text_lower)
        untestable_count = sum(1 for pattern in untestable_patterns if pattern in text_lower)
        
        # Calculate base score
        testability = 0.5  # Start neutral
        testability += min(testable_count * 0.1, 0.4)  # Up to +0.4 for testable patterns
        testability -= min(untestable_count * 0.1, 0.3)  # Up to -0.3 for untestable patterns
        
        # Use classification if available
        if self.classifier:
            try:
                result = await self._run_classifier(
                    text,
                    candidate_labels=['testable hypothesis', 'theoretical speculation', 'philosophical idea'],
                    hypothesis_template="This is a {}."
                )
                
                if result['labels'][0] == 'testable hypothesis':
                    testability += 0.2 * result['scores'][0]
                elif result['labels'][0] == 'philosophical idea':
                    testability -= 0.2 * result['scores'][0]
                    
            except Exception as e:
                logger.warning(f"Testability classification failed: {e}")
        
        return max(0, min(testability, 1.0))
    
    async def _run_classifier(self, text: str, candidate_labels: List[str], 
                            hypothesis_template: str = None) -> Dict:
        """Run zero-shot classification in thread pool to avoid blocking.
        
        Args:
            text: Text to classify
            candidate_labels: Possible labels
            hypothesis_template: Template for hypothesis
            
        Returns:
            Classification results
        """
        if not self.classifier:
            return {'labels': candidate_labels, 'scores': [1.0/len(candidate_labels)] * len(candidate_labels)}
        
        loop = asyncio.get_event_loop()
        
        if hypothesis_template:
            result = await loop.run_in_executor(
                None,
                lambda: self.classifier(text, candidate_labels, hypothesis_template=hypothesis_template)
            )
        else:
            result = await loop.run_in_executor(
                None,
                lambda: self.classifier(text, candidate_labels)
            )
        
        return result
    
    async def _run_qa(self, question: str, context: str) -> Dict:
        """Run question answering in thread pool to avoid blocking.
        
        Args:
            question: Question to answer
            context: Context to search for answer
            
        Returns:
            Answer dictionary with 'answer' and 'score' fields
        """
        if not self.qa_model:
            return None
        
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: self.qa_model(question=question, context=context)
        )
        
        return result