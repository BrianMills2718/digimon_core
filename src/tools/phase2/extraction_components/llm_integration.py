"""LLM Integration Component (<300 lines)

Handles integration with Large Language Models (OpenAI and Gemini) for entity extraction.
Provides mock APIs for testing and fallback mechanisms.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class LLMExtractionClient:
    """Client for LLM-based entity extraction."""
    
    def __init__(self, api_client=None, auth_manager=None):
        """Initialize LLM extraction client."""
        self.api_client = api_client
        self.auth_manager = auth_manager
        
        # Check API availability
        self.openai_available = False
        self.google_available = False
        
        if auth_manager:
            self.openai_available = auth_manager.is_service_available("openai")
            self.google_available = auth_manager.is_service_available("google")
        
        logger.info(f"LLM services available - OpenAI: {self.openai_available}, Google: {self.google_available}")
    
    def extract_entities_openai(self, text: str, ontology: 'DomainOntology') -> Dict[str, Any]:
        """Extract entities using OpenAI GPT."""
        if not self.openai_available or not self.api_client:
            logger.warning("OpenAI not available, using fallback")
            return self._fallback_extraction(text, ontology)
        
        try:
            # Prepare extraction prompt
            prompt = self._build_openai_prompt(text, ontology)
            
            # Make API request
            response = self._make_openai_request(prompt)
            
            # Parse and validate response
            extraction_result = self._parse_openai_response(response, ontology)
            
            logger.info(f"OpenAI extraction completed: {len(extraction_result.get('entities', []))} entities")
            return extraction_result
            
        except Exception as e:
            logger.error(f"OpenAI extraction failed: {e}")
            return self._fallback_extraction(text, ontology)
    
    def extract_entities_gemini(self, text: str, ontology: 'DomainOntology') -> Dict[str, Any]:
        """Extract entities using Google Gemini."""
        if not self.google_available or not self.api_client:
            logger.warning("Gemini not available, using fallback")
            return self._fallback_extraction(text, ontology)
        
        try:
            # Prepare extraction prompt
            prompt = self._build_gemini_prompt(text, ontology)
            
            # Make API request
            response = self._make_gemini_request(prompt)
            
            # Parse and validate response
            extraction_result = self._parse_gemini_response(response, ontology)
            
            logger.info(f"Gemini extraction completed: {len(extraction_result.get('entities', []))} entities")
            return extraction_result
            
        except Exception as e:
            logger.error(f"Gemini extraction failed: {e}")
            return self._fallback_extraction(text, ontology)
    
    def _build_openai_prompt(self, text: str, ontology: 'DomainOntology') -> str:
        """Build structured prompt for OpenAI."""
        entity_types = [et.name for et in ontology.entity_types]
        relationship_types = [rt.name for rt in ontology.relationship_types]
        
        prompt = f"""
Extract entities and relationships from the following text using the provided ontology.

Domain: {ontology.domain_name}
Description: {ontology.domain_description}

Entity Types: {', '.join(entity_types)}
Relationship Types: {', '.join(relationship_types)}

Text to analyze:
{text}

Return the result as JSON with the following structure:
{{
    "entities": [
        {{
            "text": "entity mention",
            "type": "ENTITY_TYPE",
            "confidence": 0.0-1.0,
            "context": "surrounding context"
        }}
    ],
    "relationships": [
        {{
            "source": "source entity text",
            "target": "target entity text", 
            "relation": "RELATIONSHIP_TYPE",
            "confidence": 0.0-1.0,
            "context": "relationship context"
        }}
    ]
}}

Focus on entities that clearly belong to the specified types and relationships that are explicitly stated or strongly implied.
"""
        return prompt
    
    def _build_gemini_prompt(self, text: str, ontology: 'DomainOntology') -> str:
        """Build structured prompt for Gemini."""
        # Similar to OpenAI but with Gemini-specific formatting
        entity_examples = []
        for et in ontology.entity_types[:3]:  # Limit examples
            entity_examples.extend(et.examples[:2])
        
        relationship_examples = []
        for rt in ontology.relationship_types[:3]:
            relationship_examples.extend(rt.examples[:2])
        
        prompt = f"""
Analyze the following text and extract entities and relationships based on the ontology.

Domain: {ontology.domain_name}

Entity Types with Examples:
"""
        
        for et in ontology.entity_types:
            prompt += f"- {et.name}: {et.description} (e.g., {', '.join(et.examples[:2])})\n"
        
        prompt += f"\nRelationship Types with Examples:\n"
        for rt in ontology.relationship_types:
            prompt += f"- {rt.name}: {rt.description} (e.g., {', '.join(rt.examples[:1])})\n"
        
        prompt += f"""
Text: {text}

Extract entities and relationships in JSON format:
{{
    "entities": [
        {{"text": "entity", "type": "TYPE", "confidence": 0.9, "context": "context"}}
    ],
    "relationships": [
        {{"source": "entity1", "target": "entity2", "relation": "TYPE", "confidence": 0.8}}
    ]
}}
"""
        return prompt
    
    def _make_openai_request(self, prompt: str) -> str:
        """Make request to OpenAI API using LiteLLM universal client."""
        if not self.api_client:
            raise Exception("API client not available")
        
        try:
            # Use new LiteLLM-based API client interface
            response = self.api_client.make_request(
                service="openai",
                request_type="chat_completion", 
                prompt=prompt,
                max_tokens=2000,
                temperature=0.1,
                model="gpt_4o_mini"  # Use configured default model
            )
            
            if response.success:
                return response.response_data  # Updated field name
            else:
                raise Exception(f"OpenAI request failed: {response.error}")
                
        except Exception as e:
            logger.error(f"OpenAI API request failed: {e}")
            raise
    
    def _make_gemini_request(self, prompt: str) -> str:
        """Make request to Gemini API using LiteLLM universal client."""
        if not self.api_client:
            raise Exception("API client not available")
        
        try:
            # Use new LiteLLM-based API client interface
            response = self.api_client.make_request(
                service="gemini",
                request_type="chat_completion",
                prompt=prompt,
                max_tokens=2000,
                temperature=0.1,
                model="gemini_flash"  # Use configured default model
            )
            
            if response.success:
                return response.response_data  # Updated field name
            else:
                raise Exception(f"Gemini request failed: {response.error}")
                
        except Exception as e:
            logger.error(f"Gemini API request failed: {e}")
            raise
    
    def _parse_openai_response(self, response: str, ontology: 'DomainOntology') -> Dict[str, Any]:
        """Parse and validate OpenAI response."""
        try:
            # Extract JSON from response
            json_str = self._extract_json_from_response(response)
            result = json.loads(json_str)
            
            # Validate and clean result
            return self._validate_extraction_result(result, ontology)
            
        except Exception as e:
            logger.error(f"Failed to parse OpenAI response: {e}")
            return {"entities": [], "relationships": []}
    
    def _parse_gemini_response(self, response: str, ontology: 'DomainOntology') -> Dict[str, Any]:
        """Parse and validate Gemini response."""
        try:
            # Extract JSON from response
            json_str = self._extract_json_from_response(response)
            result = json.loads(json_str)
            
            # Validate and clean result
            return self._validate_extraction_result(result, ontology)
            
        except Exception as e:
            logger.error(f"Failed to parse Gemini response: {e}")
            return {"entities": [], "relationships": []}
    
    def _extract_json_from_response(self, response: str) -> str:
        """Extract JSON content from LLM response."""
        # Find JSON block in response
        start_markers = ['{', '```json', '```']
        end_markers = ['}', '```']
        
        # Find start of JSON
        start_idx = -1
        for marker in start_markers:
            idx = response.find(marker)
            if idx != -1:
                start_idx = idx if marker == '{' else response.find('{', idx)
                break
        
        if start_idx == -1:
            raise ValueError("No JSON found in response")
        
        # Find end of JSON by matching braces
        brace_count = 0
        end_idx = start_idx
        
        for i, char in enumerate(response[start_idx:], start_idx):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_idx = i + 1
                    break
        
        return response[start_idx:end_idx]
    
    def _validate_extraction_result(self, result: Dict[str, Any], 
                                  ontology: 'DomainOntology') -> Dict[str, Any]:
        """Validate and clean extraction result."""
        valid_entity_types = {et.name for et in ontology.entity_types}
        valid_relationship_types = {rt.name for rt in ontology.relationship_types}
        
        # Validate entities
        valid_entities = []
        for entity in result.get('entities', []):
            if (isinstance(entity, dict) and 
                'text' in entity and 
                'type' in entity and
                entity['type'] in valid_entity_types):
                
                # Ensure required fields
                entity.setdefault('confidence', 0.8)
                entity.setdefault('context', '')
                
                # Validate confidence
                if not isinstance(entity['confidence'], (int, float)):
                    entity['confidence'] = 0.8
                entity['confidence'] = max(0.0, min(1.0, float(entity['confidence'])))
                
                valid_entities.append(entity)
        
        # Validate relationships
        valid_relationships = []
        entity_texts = {e['text'] for e in valid_entities}
        
        for rel in result.get('relationships', []):
            if (isinstance(rel, dict) and
                'source' in rel and
                'target' in rel and
                'relation' in rel and
                rel['relation'] in valid_relationship_types and
                rel['source'] in entity_texts and
                rel['target'] in entity_texts):
                
                # Ensure required fields
                rel.setdefault('confidence', 0.7)
                rel.setdefault('context', '')
                
                # Validate confidence
                if not isinstance(rel['confidence'], (int, float)):
                    rel['confidence'] = 0.7
                rel['confidence'] = max(0.0, min(1.0, float(rel['confidence'])))
                
                valid_relationships.append(rel)
        
        return {
            'entities': valid_entities,
            'relationships': valid_relationships
        }
    
    def _fallback_extraction(self, text: str, ontology: 'DomainOntology') -> Dict[str, Any]:
        """Fallback extraction when LLMs are not available."""
        logger.info("Using fallback extraction (pattern-based)")
        
        # Simple pattern-based extraction
        entities = []
        relationships = []
        
        # Basic patterns for common entity types
        import re
        
        # Person names (Dr. Title + Name, Name + credentials)
        person_patterns = [
            r'\b(?:Dr\.?|Prof\.?|Mr\.?|Ms\.?|Mrs\.?)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'\b([A-Z][a-z]+\s+[A-Z][a-z]+)(?:\s+(?:PhD|MD|Prof))?'
        ]
        
        # Organizations (Inc., Corp., University, Institute)
        org_patterns = [
            r'\b([A-Z][a-zA-Z\s]+(?:Inc\.?|Corp\.?|Company|LLC))',
            r'\b([A-Z][a-zA-Z\s]*(?:University|Institute|College))',
            r'\b([A-Z][a-zA-Z\s]+(?:Research|Lab|Laboratory))'
        ]
        
        # Locations (states, countries, cities)
        location_patterns = [
            r'\b(California|New York|Texas|Florida|Washington)\b',
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:,\s+[A-Z]{2}))\b'  # City, State
        ]
        
        # Extract entities based on patterns
        if any(et.name == 'PERSON' for et in ontology.entity_types):
            for pattern in person_patterns:
                for match in re.finditer(pattern, text):
                    entities.append({
                        'text': match.group(1),
                        'type': 'PERSON',
                        'confidence': 0.7,
                        'context': text[max(0, match.start()-20):match.end()+20]
                    })
        
        if any(et.name == 'ORGANIZATION' for et in ontology.entity_types):
            for pattern in org_patterns:
                for match in re.finditer(pattern, text):
                    entities.append({
                        'text': match.group(1),
                        'type': 'ORGANIZATION',
                        'confidence': 0.6,
                        'context': text[max(0, match.start()-20):match.end()+20]
                    })
        
        if any(et.name == 'LOCATION' for et in ontology.entity_types):
            for pattern in location_patterns:
                for match in re.finditer(pattern, text):
                    entities.append({
                        'text': match.group(1),
                        'type': 'LOCATION',
                        'confidence': 0.6,
                        'context': text[max(0, match.start()-20):match.end()+20]
                    })
        
        # Remove duplicates
        seen_entities = set()
        unique_entities = []
        for entity in entities:
            key = (entity['text'], entity['type'])
            if key not in seen_entities:
                seen_entities.add(key)
                unique_entities.append(entity)
        
        return {
            'entities': unique_entities,
            'relationships': relationships  # No relationship extraction in fallback
        }


class MockAPIProvider:
    """Provides mock LLM responses for testing."""
    
    def __init__(self):
        self.call_count = 0
        
    def mock_extract(self, text: str, ontology: 'DomainOntology') -> Dict[str, Any]:
        """Generate mock extraction results."""
        self.call_count += 1
        
        # Generate mock entities based on ontology types
        mock_entities = []
        mock_relationships = []
        
        # Simple text analysis for mock data
        words = text.lower().split()
        
        # Mock entity generation
        for i, entity_type in enumerate(ontology.entity_types[:3]):  # Limit to 3 types
            if i < len(entity_type.examples):
                mock_entities.append({
                    'text': entity_type.examples[i],
                    'type': entity_type.name,
                    'confidence': 0.8 + (i * 0.05),
                    'context': f"Mock context for {entity_type.examples[i]}"
                })
        
        # Mock relationship generation
        if len(mock_entities) >= 2 and ontology.relationship_types:
            rel_type = ontology.relationship_types[0]
            mock_relationships.append({
                'source': mock_entities[0]['text'],
                'target': mock_entities[1]['text'],
                'relation': rel_type.name,
                'confidence': 0.75,
                'context': f"Mock relationship between entities"
            })
        
        logger.info(f"Mock extraction #{self.call_count}: {len(mock_entities)} entities, {len(mock_relationships)} relationships")
        
        return {
            'entities': mock_entities,
            'relationships': mock_relationships,
            'metadata': {
                'extraction_method': 'mock',
                'call_count': self.call_count,
                'timestamp': datetime.now().isoformat()
            }
        }