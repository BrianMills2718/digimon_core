"""Real LLM service using OpenAI or Anthropic APIs"""

import asyncio
import os
import json
import logging
from typing import List, Dict, Any, Optional
import openai
from anthropic import Anthropic

logger = logging.getLogger(__name__)


class RealLLMService:
    """Real LLM service using OpenAI or Anthropic APIs"""
    
    def __init__(self, provider: str = 'openai'):
        """Initialize LLM service with specified provider.
        
        Args:
            provider: LLM provider to use ('openai' or 'anthropic')
        """
        self.provider = provider
        
        if provider == 'openai':
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                logger.warning("OPENAI_API_KEY not found, LLM features will be limited")
                self.client = None
            else:
                self.client = openai.AsyncOpenAI(api_key=api_key)
                self.model = 'gpt-4-turbo-preview'
                
        elif provider == 'anthropic':
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                logger.warning("ANTHROPIC_API_KEY not found, LLM features will be limited")
                self.client = None
            else:
                self.client = Anthropic(api_key=api_key)
                self.model = 'claude-3-opus-20240229'
        else:
            raise ValueError(f"Unsupported provider: {provider}")
            
        logger.info(f"Initialized RealLLMService with provider: {provider}")
    
    async def generate_text(self, prompt: str, max_length: int = 500, 
                          temperature: float = 0.7) -> str:
        """Generate text using real LLM.
        
        Args:
            prompt: Input prompt for generation
            max_length: Maximum tokens to generate
            temperature: Sampling temperature (0-1)
            
        Returns:
            Generated text
        """
        if not self.client:
            logger.warning("LLM client not initialized, using fallback generation")
            return await self._fallback_generation(prompt, max_length)
            
        try:
            if self.provider == 'openai':
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a research hypothesis generator specializing in cross-modal analysis and knowledge synthesis."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=max_length,
                    temperature=temperature
                )
                return response.choices[0].message.content
                
            elif self.provider == 'anthropic':
                # Use synchronous call wrapped in executor
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: self.client.messages.create(
                        model=self.model,
                        messages=[
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=max_length,
                        temperature=temperature
                    )
                )
                return response.content[0].text
                
        except Exception as e:
            logger.error(f"Failed to generate text with {self.provider}: {e}")
            return await self._fallback_generation(prompt, max_length)
    
    async def generate_structured_hypotheses(self, prompt: str, max_hypotheses: int = 5,
                                           creativity_level: float = 0.7) -> List[Dict[str, Any]]:
        """Generate research hypotheses with structured output.
        
        Args:
            prompt: Context and requirements for hypothesis generation
            max_hypotheses: Maximum number of hypotheses to generate
            creativity_level: Temperature for generation (0-1)
            
        Returns:
            List of structured hypothesis dictionaries
        """
        # Enhance prompt to request structured output
        structured_prompt = f"""
{prompt}

Generate {max_hypotheses} research hypotheses in the following JSON format:
[
    {{
        "hypothesis": "The hypothesis statement",
        "confidence": 0.0-1.0,
        "novelty": 0.0-1.0,
        "testability": 0.0-1.0,
        "reasoning": "Brief explanation of the reasoning",
        "key_concepts": ["concept1", "concept2"],
        "evidence_requirements": ["required evidence type 1", "required evidence type 2"]
    }}
]

Ensure the output is valid JSON that can be parsed. Focus on novel, testable hypotheses that connect different modalities or reveal hidden patterns.
"""
        
        # Generate hypotheses
        raw_response = await self.generate_text(
            structured_prompt, 
            max_length=1500,  # More tokens for structured output
            temperature=creativity_level
        )
        
        # Parse structured response
        try:
            # Extract JSON from response
            json_start = raw_response.find('[')
            json_end = raw_response.rfind(']') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = raw_response[json_start:json_end]
                hypotheses_data = json.loads(json_str)
            else:
                # Try to parse the entire response
                hypotheses_data = json.loads(raw_response)
            
            # Structure hypotheses with IDs
            hypotheses = []
            for i, h_data in enumerate(hypotheses_data[:max_hypotheses]):
                hypothesis = {
                    'id': f'hypothesis_{i}',
                    'text': h_data.get('hypothesis', ''),
                    'confidence_score': float(h_data.get('confidence', 0.5)),
                    'novelty_score': float(h_data.get('novelty', 0.5)),
                    'testability_score': float(h_data.get('testability', 0.5)),
                    'evidence_support': [],
                    'reasoning_type': 'llm_generated',
                    'reasoning': h_data.get('reasoning', ''),
                    'key_concepts': h_data.get('key_concepts', []),
                    'evidence_requirements': h_data.get('evidence_requirements', [])
                }
                hypotheses.append(hypothesis)
                
            logger.info(f"Successfully generated {len(hypotheses)} structured hypotheses")
            return hypotheses
            
        except (json.JSONDecodeError, KeyError) as e:
            # Fallback to simple parsing if structured output fails
            logger.warning(f"Failed to parse structured LLM output: {e}")
            return await self._parse_unstructured_hypotheses(raw_response, max_hypotheses)
    
    async def _parse_unstructured_hypotheses(self, text: str, max_hypotheses: int) -> List[Dict[str, Any]]:
        """Parse hypotheses from unstructured text.
        
        Args:
            text: Unstructured text containing hypotheses
            max_hypotheses: Maximum number to extract
            
        Returns:
            List of structured hypothesis dictionaries
        """
        hypotheses = []
        
        # Split by common patterns
        lines = text.split('\n')
        hypothesis_lines = []
        
        for line in lines:
            line = line.strip()
            # Look for numbered lists or bullet points
            if (line and (
                line[0].isdigit() or 
                line.startswith('-') or 
                line.startswith('*') or
                line.startswith('•') or
                'hypothesis' in line.lower()
            )):
                # Clean up the line
                cleaned = line.lstrip('0123456789.-*•) ').strip()
                if cleaned and len(cleaned) > 20:  # Minimum length for valid hypothesis
                    hypothesis_lines.append(cleaned)
        
        # Create structured hypotheses from extracted lines
        for i, hyp_text in enumerate(hypothesis_lines[:max_hypotheses]):
            hypothesis = {
                'id': f'hypothesis_{i}',
                'text': hyp_text,
                'confidence_score': 0.7,  # Default scores
                'novelty_score': 0.6,
                'testability_score': 0.8,
                'evidence_support': [],
                'reasoning_type': 'llm_generated',
                'reasoning': 'Extracted from unstructured LLM output',
                'key_concepts': self._extract_concepts(hyp_text),
                'evidence_requirements': []
            }
            hypotheses.append(hypothesis)
        
        logger.info(f"Extracted {len(hypotheses)} hypotheses from unstructured text")
        return hypotheses
    
    def _extract_concepts(self, text: str) -> List[str]:
        """Extract key concepts from hypothesis text.
        
        Args:
            text: Hypothesis text
            
        Returns:
            List of key concepts
        """
        # Simple concept extraction based on capitalized words and domain terms
        concepts = []
        
        # Domain-specific terms
        domain_terms = {
            'cross-modal', 'entity', 'pattern', 'relationship', 'correlation',
            'analysis', 'synthesis', 'integration', 'network', 'cluster',
            'embedding', 'similarity', 'linkage', 'evidence', 'hypothesis'
        }
        
        words = text.lower().split()
        
        # Extract domain terms
        for word in words:
            cleaned = word.strip('.,;:!?()[]{}')
            if cleaned in domain_terms:
                concepts.append(cleaned)
        
        # Extract capitalized terms (potential entities)
        words = text.split()
        for word in words:
            if word[0].isupper() and len(word) > 3:
                cleaned = word.strip('.,;:!?()[]{}')
                if cleaned.lower() not in domain_terms:
                    concepts.append(cleaned)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_concepts = []
        for concept in concepts:
            if concept.lower() not in seen:
                seen.add(concept.lower())
                unique_concepts.append(concept)
        
        return unique_concepts[:10]  # Limit to 10 concepts
    
    async def _fallback_generation(self, prompt: str, max_length: int) -> str:
        """Fallback text generation when LLM is not available.
        
        Args:
            prompt: Input prompt
            max_length: Maximum length (ignored in fallback)
            
        Returns:
            Basic generated text
        """
        # Extract key information from prompt
        key_terms = []
        for word in prompt.lower().split():
            if len(word) > 5 and word not in ['research', 'hypothesis', 'generate', 'create']:
                key_terms.append(word)
        
        # Generate basic hypotheses
        templates = [
            f"Cross-modal analysis suggests a relationship between {key_terms[0] if key_terms else 'entities'} across different modalities.",
            f"The integration of multi-modal data reveals patterns in {key_terms[1] if len(key_terms) > 1 else 'knowledge networks'}.",
            f"Novel connections emerge when analyzing {key_terms[2] if len(key_terms) > 2 else 'cross-disciplinary relationships'}."
        ]
        
        return '\n'.join(f"{i+1}. {template}" for i, template in enumerate(templates[:3]))