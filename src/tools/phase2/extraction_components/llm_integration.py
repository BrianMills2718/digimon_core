"""LLM Integration Component - Standardized on EnhancedAPIClient

Handles integration with Large Language Models using the proven EnhancedAPIClient.
Provides automatic fallbacks, rate limiting, and production-ready features.
"""

import json
import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

try:
    from ...core.enhanced_api_client import EnhancedAPIClient
    from ...core.api_auth_manager import APIAuthManager
    from ...core.standard_config import get_model
except ImportError:
    from src.core.enhanced_api_client import EnhancedAPIClient
    from src.core.api_auth_manager import APIAuthManager
    from src.core.standard_config import get_model

logger = logging.getLogger(__name__)


class LLMExtractionClient:
    """Client for LLM-based entity extraction using EnhancedAPIClient."""
    
    def __init__(self, api_client: Optional[EnhancedAPIClient] = None, auth_manager: Optional[APIAuthManager] = None):
        """Initialize LLM extraction client with EnhancedAPIClient."""
        if api_client is None:
            # Create client with auth manager
            if auth_manager is None:
                auth_manager = APIAuthManager()
            self.api_client = EnhancedAPIClient(auth_manager)
        else:
            self.api_client = api_client
        
        # Check API availability
        self.openai_available = self.api_client.auth_manager.is_service_available("openai")
        self.google_available = self.api_client.auth_manager.is_service_available("google")
        
        logger.info("LLM extraction client initialized with EnhancedAPIClient")
    
    def _get_default_model(self) -> str:
        """Get default model from standard config"""
        return get_model("llm_extraction")
    
    async def extract_entities(self, text: str, ontology: 'DomainOntology', model: Optional[str] = None) -> Dict[str, Any]:
        """Extract entities using structured output with automatic fallbacks."""
        try:
            # Check if structured output is enabled for entity extraction
            try:
                from ...core.feature_flags import is_structured_output_enabled
                use_structured = is_structured_output_enabled("entity_extraction")
            except ImportError:
                logger.warning("Feature flags not available, using legacy extraction")
                use_structured = False
            
            if use_structured:
                logger.info("Using structured output for entity extraction")
                return await self._extract_entities_structured(text, ontology, model)
            else:
                logger.info("Using legacy extraction method")
                return await self._extract_entities_legacy(text, ontology, model)
                
        except Exception as e:
            logger.error(f"LLM extraction error: {e}")
            return self._fallback_extraction(text, ontology)
    
    async def _extract_entities_structured(self, text: str, ontology: 'DomainOntology', model: Optional[str] = None) -> Dict[str, Any]:
        """Extract entities using structured output with Pydantic validation."""
        try:
            from ...core.structured_llm_service import get_structured_llm_service
            from ...orchestration.reasoning_schema import LLMExtractionResponse
            
            # Get structured LLM service
            structured_llm = get_structured_llm_service()
            
            # Build extraction prompt optimized for structured output
            prompt = self._build_structured_extraction_prompt(text, ontology)
            
            # Use structured output for entity extraction
            validated_response = structured_llm.structured_completion(
                prompt=prompt,
                schema=LLMExtractionResponse,
                model=model or "smart",  # Use Universal LLM Kit model names
                temperature=0.1,  # Low temperature for consistent extraction
                max_tokens=16000  # Sufficient for entity extraction
            )
            
            # Convert Pydantic response to legacy format for compatibility
            extraction_result = self._convert_structured_to_legacy_format(validated_response, ontology)
            
            # Add metadata
            extraction_result["llm_metadata"] = {
                "model_used": "structured_output",
                "extraction_method": "pydantic_validation",
                "task_type": "extraction",
                "ontology_domain": ontology.domain_name if ontology else "unknown"
            }
            
            logger.info(f"Structured extraction completed: {len(extraction_result.get('entities', []))} entities")
            return extraction_result
            
        except Exception as e:
            logger.error(f"Structured extraction failed: {e}")
            # Fail fast as per coding philosophy - no fallback to manual parsing
            raise Exception(f"Structured entity extraction failed: {e}")
    
    async def _extract_entities_legacy(self, text: str, ontology: 'DomainOntology', model: Optional[str] = None) -> Dict[str, Any]:
        """Legacy entity extraction method (will be deprecated after migration)."""
        # Build extraction prompt optimized for entity extraction
        prompt = self._build_extraction_prompt(text, ontology)
        
        # Use EnhancedAPIClient for LLM request
        response = self.api_client.make_request(
            prompt=prompt,
            model=model or self._get_default_model(),  # Use config model if none specified
            temperature=0.1,  # Low temperature for consistent extraction
            max_tokens=2048,
            request_type="chat_completion",
            use_fallback=True  # Enable automatic fallbacks
        )
        
        if response.success:
            # Parse and validate response
            extraction_result = self._parse_llm_response(response.response_data, ontology)
            
            # Add metadata from EnhancedAPIClient
            extraction_result["llm_metadata"] = {
                "model_used": response.service_used,
                "execution_time": response.processing_time,
                "fallback_used": response.fallback_used,
                "task_type": "extraction"
            }
            
            logger.info(f"LLM extraction completed: {len(extraction_result.get('entities', []))} entities using {response.service_used}")
            return extraction_result
        else:
            logger.error(f"LLM extraction failed: {response.error_message}")
            return self._fallback_extraction(text, ontology)
    
    # Backward compatibility methods - delegate to unified method
    def extract_entities_openai(self, text: str, ontology: 'DomainOntology') -> Dict[str, Any]:
        """Legacy method for OpenAI extraction - delegates to unified method."""
        logger.warning("extract_entities_openai is deprecated. Use extract_entities() instead.")
        return asyncio.run(self.extract_entities(text, ontology, model=self._get_default_model()))
    
    def extract_entities_gemini(self, text: str, ontology: 'DomainOntology') -> Dict[str, Any]:
        """Legacy method for Gemini extraction - delegates to unified method."""
        logger.warning("extract_entities_gemini is deprecated. Use extract_entities() instead.")
        return asyncio.run(self.extract_entities(text, ontology, model=self._get_default_model()))
    
    def _make_openai_request(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Internal method for OpenAI requests - uses EnhancedAPIClient."""
        response = self.api_client.make_request(
            prompt=prompt,
            model=self._get_default_model(),
            request_type="chat_completion",
            use_fallback=False,
            **kwargs
        )
        return {
            "success": response.success,
            "content": response.response_data,
            "model": response.service_used,
            "error": response.error_message
        }
    
    def _make_gemini_request(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Internal method for Gemini requests - uses EnhancedAPIClient."""
        response = self.api_client.make_request(
            prompt=prompt,
            model=self._get_default_model(),
            request_type="chat_completion",
            use_fallback=False,
            **kwargs
        )
        return {
            "success": response.success,
            "content": response.response_data,
            "model": response.service_used,
            "error": response.error_message
        }
    
    def _build_extraction_prompt(self, text: str, ontology: 'DomainOntology') -> str:
        """Build unified extraction prompt optimized for any LLM provider."""
        entity_types = [et.name for et in ontology.entity_types]
        relationship_types = [rt.name for rt in ontology.relationship_types]
        
        prompt = f"""Extract entities and relationships from the following text using the provided ontology.

DOMAIN: {ontology.domain_name}
DESCRIPTION: {ontology.domain_description}

ENTITY TYPES TO EXTRACT:
{chr(10).join(f"- {et}" for et in entity_types)}

RELATIONSHIP TYPES TO EXTRACT:
{chr(10).join(f"- {rt}" for rt in relationship_types)}

TEXT TO ANALYZE:
{text}

INSTRUCTIONS:
1. Extract only entities that clearly belong to the specified types
2. Extract relationships that clearly match the specified types
3. Provide confidence scores (0.0-1.0) for each extraction
4. Use exact text spans from the original text

Return the result as valid JSON with this exact structure:
{{
    "entities": [
        {{
            "text": "exact text span from original",
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
    
    def _build_structured_extraction_prompt(self, text: str, ontology: 'DomainOntology') -> str:
        """Build extraction prompt optimized for structured output with Pydantic validation."""
        entity_types = [et.name for et in ontology.entity_types]
        relationship_types = [rt.name for rt in ontology.relationship_types]
        
        prompt = f"""Extract entities and relationships from the following text using the provided ontology.

DOMAIN: {ontology.domain_name}
DESCRIPTION: {ontology.domain_description}

ENTITY TYPES TO EXTRACT:
{chr(10).join(f"- {et}" for et in entity_types)}

RELATIONSHIP TYPES TO EXTRACT:
{chr(10).join(f"- {rt}" for rt in relationship_types)}

TEXT TO ANALYZE:
{text}

INSTRUCTIONS:
1. Extract only entities that clearly belong to the specified types
2. Extract relationships that clearly match the specified types
3. Provide confidence scores (0.0-1.0) for each extraction
4. Use exact text spans from the original text
5. Include character positions when possible
6. Provide surrounding context for each entity/relationship

Focus on entities that clearly belong to the specified types and relationships that are explicitly stated or strongly implied.
Respond with structured JSON that will be validated against a Pydantic schema.
"""
        return prompt
    
    def _convert_structured_to_legacy_format(self, structured_response: 'LLMExtractionResponse', ontology: 'DomainOntology') -> Dict[str, Any]:
        """Convert structured Pydantic response to legacy format for compatibility."""
        try:
            # Convert entities to legacy format
            processed_entities = []
            for entity in structured_response.entities:
                processed_entities.append({
                    'text': entity.text,
                    'type': entity.type,
                    'confidence': entity.confidence,
                    'context': entity.context,
                    'start_pos': entity.start_pos,
                    'end_pos': entity.end_pos,
                    'extraction_method': 'structured_llm',
                    'timestamp': datetime.now().isoformat()
                })
            
            # Convert relationships to legacy format
            processed_relationships = []
            for relationship in structured_response.relationships:
                processed_relationships.append({
                    'source': relationship.source,
                    'target': relationship.target,
                    'relation': relationship.relation,
                    'confidence': relationship.confidence,
                    'context': relationship.context,
                    'extraction_method': 'structured_llm',
                    'timestamp': datetime.now().isoformat()
                })
            
            return {
                'entities': processed_entities,
                'relationships': processed_relationships,
                'extraction_stats': {
                    'entities_extracted': len(processed_entities),
                    'relationships_extracted': len(processed_relationships),
                    'extraction_timestamp': datetime.now().isoformat(),
                    'extraction_confidence': structured_response.extraction_confidence,
                    'ontology_domain': structured_response.ontology_domain
                }
            }
            
        except Exception as e:
            logger.error(f"Error converting structured response to legacy format: {e}")
            raise Exception(f"Failed to convert structured response: {e}")
    
    def _parse_llm_response(self, response_content: str, ontology: 'DomainOntology') -> Dict[str, Any]:
        """Parse LLM response into structured extraction result."""
        try:
            # Try to parse as JSON first
            if response_content.strip().startswith('{'):
                extraction_data = json.loads(response_content)
            else:
                # Handle cases where LLM returns text before JSON
                json_start = response_content.find('{')
                json_end = response_content.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_text = response_content[json_start:json_end]
                    extraction_data = json.loads(json_text)
                else:
                    raise ValueError("No valid JSON found in response")
            
            # Validate and process entities
            processed_entities = []
            for entity in extraction_data.get('entities', []):
                if self._validate_entity(entity, ontology):
                    processed_entities.append({
                        'text': entity.get('text', ''),
                        'type': entity.get('type', ''),
                        'confidence': float(entity.get('confidence', 0.0)),
                        'context': entity.get('context', ''),
                        'extraction_method': 'llm',
                        'timestamp': datetime.now().isoformat()
                    })
            
            # Validate and process relationships
            processed_relationships = []
            for relationship in extraction_data.get('relationships', []):
                if self._validate_relationship(relationship, ontology):
                    processed_relationships.append({
                        'source': relationship.get('source', ''),
                        'target': relationship.get('target', ''),
                        'relation': relationship.get('relation', ''),
                        'confidence': float(relationship.get('confidence', 0.0)),
                        'context': relationship.get('context', ''),
                        'extraction_method': 'llm',
                        'timestamp': datetime.now().isoformat()
                    })
            
            return {
                'entities': processed_entities,
                'relationships': processed_relationships,
                'extraction_stats': {
                    'entities_extracted': len(processed_entities),
                    'relationships_extracted': len(processed_relationships),
                    'extraction_timestamp': datetime.now().isoformat()
                }
            }
            
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            logger.debug(f"Response content: {response_content[:500]}...")
            return self._fallback_extraction("", ontology)
        except Exception as e:
            logger.error(f"Error processing LLM response: {e}")
            return self._fallback_extraction("", ontology)
    
    def _validate_entity(self, entity: Dict[str, Any], ontology: 'DomainOntology') -> bool:
        """Validate extracted entity against ontology."""
        try:
            # Check required fields
            if not entity.get('text') or not entity.get('type'):
                return False
            
            # Check confidence score
            confidence = entity.get('confidence', 0.0)
            if not isinstance(confidence, (int, float)) or confidence < 0.0 or confidence > 1.0:
                return False
            
            # Check if entity type exists in ontology
            valid_types = {et.name for et in ontology.entity_types}
            if entity.get('type') not in valid_types:
                return False
            
            # Check if text is not empty
            if not entity.get('text', '').strip():
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Entity validation error: {e}")
            return False
    
    def _validate_relationship(self, relationship: Dict[str, Any], ontology: 'DomainOntology') -> bool:
        """Validate extracted relationship against ontology."""
        try:
            # Check required fields
            required_fields = ['source', 'target', 'relation']
            if not all(relationship.get(field) for field in required_fields):
                return False
            
            # Check confidence score
            confidence = relationship.get('confidence', 0.0)
            if not isinstance(confidence, (int, float)) or confidence < 0.0 or confidence > 1.0:
                return False
            
            # Check if relationship type exists in ontology
            valid_relations = {rt.name for rt in ontology.relationship_types}
            if relationship.get('relation') not in valid_relations:
                return False
            
            # Check if source and target are not empty
            if not relationship.get('source', '').strip() or not relationship.get('target', '').strip():
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Relationship validation error: {e}")
            return False
    
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

