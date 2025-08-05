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
    
    async def extract_entities(self, text: str, ontology: 'DomainOntology', model: Optional[str] = None, schema=None) -> Dict[str, Any]:
        """Extract entities using structured output with automatic fallbacks and schema support."""
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
                return await self._extract_entities_structured(text, ontology, model, schema)
            else:
                logger.info("Using legacy extraction method")
                return await self._extract_entities_legacy(text, ontology, model, schema)
                
        except Exception as e:
            logger.error(f"LLM extraction error: {e}")
            raise RuntimeError(f"LLM extraction failed: {e}. System will fail fast without working LLM services.")
    
    async def _extract_entities_structured(self, text: str, ontology: 'DomainOntology', model: Optional[str] = None, schema=None) -> Dict[str, Any]:
        """Extract entities using structured output with Pydantic validation and schema support."""
        try:
            from ...core.structured_llm_service import get_structured_llm_service
            from ...orchestration.reasoning_schema import LLMExtractionResponse
            
            # Get structured LLM service
            structured_llm = get_structured_llm_service()
            
            # Build extraction prompt based on schema mode or ontology
            if schema:
                prompt = self._build_schema_aware_prompt(text, schema, ontology)
            else:
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
                "ontology_domain": ontology.domain_name if ontology else "unknown",
                "schema_mode": schema.mode.value if schema and hasattr(schema, 'mode') else None
            }
            
            logger.info(f"Structured extraction completed: {len(extraction_result.get('entities', []))} entities")
            return extraction_result
            
        except Exception as e:
            logger.error(f"Structured extraction failed: {e}")
            # Fail fast as per coding philosophy - no fallback to manual parsing
            raise Exception(f"Structured entity extraction failed: {e}")
    
    async def _extract_entities_legacy(self, text: str, ontology: 'DomainOntology', model: Optional[str] = None, schema=None) -> Dict[str, Any]:
        """Legacy entity extraction method (will be deprecated after migration) with schema support."""
        # Build extraction prompt based on schema mode or ontology
        if schema:
            prompt = self._build_schema_aware_prompt(text, schema, ontology)
        else:
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
            logger.debug(f"Raw LLM response: {response.response_data[:500]}...")
            # Parse response based on schema mode
            if schema:
                extraction_result = self._parse_schema_aware_response(response.response_data, schema, ontology)
            else:
                extraction_result = self._parse_llm_response(response.response_data, ontology)
            
            # Add metadata from EnhancedAPIClient
            extraction_result["llm_metadata"] = {
                "model_used": response.service_used,
                "execution_time": response.response_time,
                "fallback_used": response.fallback_used,
                "task_type": "extraction",
                "schema_mode": schema.mode.value if schema and hasattr(schema, 'mode') else None
            }
            
            logger.info(f"LLM extraction completed: {len(extraction_result.get('entities', []))} entities using {response.service_used}")
            logger.debug(f"Extraction result: {extraction_result}")
            return extraction_result
        else:
            logger.error(f"LLM extraction failed: {response.error}")
            raise RuntimeError(f"LLM extraction failed: {response.error}. System will fail fast without working LLM services.")
    
    # Backward compatibility methods - delegate to unified method
    def extract_entities_openai(self, text: str, ontology: 'DomainOntology', schema=None) -> Dict[str, Any]:
        """Legacy method for OpenAI extraction - delegates to unified method."""
        logger.warning("extract_entities_openai is deprecated. Use extract_entities() instead.")
        
        # Use synchronous version to avoid asyncio conflicts
        return self._extract_entities_sync(text, ontology, model=self._get_default_model(), schema=schema)
    
    def extract_entities_gemini(self, text: str, ontology: 'DomainOntology', schema=None) -> Dict[str, Any]:
        """Legacy method for Gemini extraction - delegates to unified method."""
        logger.warning("extract_entities_gemini is deprecated. Use extract_entities() instead.")
        
        # Use synchronous version to avoid asyncio conflicts
        return self._extract_entities_sync(text, ontology, model=self._get_default_model(), schema=schema)
    
    def _extract_entities_sync(self, text: str, ontology: 'DomainOntology', model: Optional[str] = None, schema=None) -> Dict[str, Any]:
        """Synchronous wrapper for entity extraction to avoid asyncio conflicts."""
        try:
            # Try to get the current event loop
            try:
                loop = asyncio.get_running_loop()
                # We're already in an async context, use sync version
                # This is the synchronous path that doesn't use asyncio
                return self._extract_entities_sync_impl(text, ontology, model, schema)
            except RuntimeError:
                # No event loop running, safe to use asyncio.run
                return asyncio.run(self.extract_entities(text, ontology, model, schema))
        except Exception as e:
            logger.error(f"Entity extraction error: {e}")
            raise RuntimeError(f"Entity extraction failed: {e}. System will fail fast without working LLM services.")
    
    def _extract_entities_sync_impl(self, text: str, ontology: 'DomainOntology', model: Optional[str] = None, schema=None) -> Dict[str, Any]:
        """Synchronous implementation of entity extraction with schema support."""
        try:
            # Check if structured output is enabled
            try:
                from ...core.feature_flags import is_structured_output_enabled
                use_structured = is_structured_output_enabled("entity_extraction")
            except ImportError:
                logger.warning("Feature flags not available, using legacy extraction")
                use_structured = False
            
            if use_structured:
                logger.info("Using structured output for entity extraction (sync)")
                # For now, skip structured in sync mode as it requires async
                logger.info("Falling back to legacy extraction in sync mode")
                use_structured = False
            
            # Build prompt based on schema mode or ontology
            if schema:
                prompt = self._build_schema_aware_prompt(text, schema, ontology)
            else:
                prompt = self._build_extraction_prompt(text, ontology)
            
            # Use EnhancedAPIClient for LLM request (synchronous)
            response = self.api_client.make_request(
                prompt=prompt,
                model=model or self._get_default_model(),
                temperature=0.1,
                max_tokens=2048,
                request_type="chat_completion",
                use_fallback=True
            )
            
            if response.success:
                # Parse response based on schema mode
                if schema:
                    extraction_result = self._parse_schema_aware_response(response.response_data, schema, ontology)
                else:
                    extraction_result = self._parse_llm_response(response.response_data, ontology)
                
                # Add metadata
                extraction_result["llm_metadata"] = {
                    "model_used": response.service_used,
                    "execution_time": response.response_time if hasattr(response, 'response_time') else 0,
                    "fallback_used": response.fallback_used if hasattr(response, 'fallback_used') else False,
                    "task_type": "extraction",
                    "schema_mode": schema.mode.value if schema and hasattr(schema, 'mode') else None
                }
                
                logger.info(f"LLM extraction completed (sync): {len(extraction_result.get('entities', []))} entities")
                return extraction_result
            else:
                logger.error(f"LLM extraction failed: {response.error}")
                raise RuntimeError(f"LLM extraction failed: {response.error}. System will fail fast without working LLM services.")
                
        except Exception as e:
            logger.error(f"Sync extraction error: {e}")
            raise RuntimeError(f"LLM extraction failed: {e}. System will fail fast without working LLM services.")
    
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
            "error": response.error
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
            "error": response.error
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
            raise RuntimeError(f"LLM response parsing failed: {e}. System will fail fast without valid LLM responses.")
        except Exception as e:
            logger.error(f"Error processing LLM response: {e}")
            raise RuntimeError(f"LLM response processing failed: {e}. System will fail fast without working LLM services.")
    
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
        """Fallback extraction is not allowed - system must fail fast when LLMs unavailable."""
        raise RuntimeError("LLM extraction fallback is not allowed. Configure OpenAI or Google API keys. System will fail fast without LLM services.")
    
    def _build_schema_aware_prompt(self, text: str, schema, ontology: Optional['DomainOntology'] = None) -> str:
        """Build extraction prompt based on schema mode (open, closed, or hybrid)."""
        from src.core.extraction_schemas import SchemaMode
        
        # Use schema's prompt generation method if available
        if hasattr(schema, 'get_extraction_prompt'):
            base_prompt = schema.get_extraction_prompt()
            
            # Add the text to analyze
            prompt = f"{base_prompt}\n\nTEXT TO ANALYZE:\n{text}"
            
            logger.info(f"Using schema mode {schema.mode.value} for extraction")
            return prompt
        
        # Fallback to building prompt based on schema mode
        if hasattr(schema, 'mode'):
            if schema.mode == SchemaMode.OPEN:
                return self._build_open_extraction_prompt(text)
            elif schema.mode == SchemaMode.CLOSED:
                # Use ontology if provided, otherwise use schema's entity/relation types
                if ontology:
                    return self._build_extraction_prompt(text, ontology)
                else:
                    # Build from schema's types
                    entity_types = list(schema.entity_types.keys()) if hasattr(schema, 'entity_types') else []
                    relation_types = list(schema.relation_types.keys()) if hasattr(schema, 'relation_types') else []
                    return self._build_closed_extraction_prompt(text, entity_types, relation_types)
            elif schema.mode == SchemaMode.HYBRID:
                # Hybrid mode - use predefined types but allow discovery
                if ontology:
                    entity_types = [et.name for et in ontology.entity_types]
                    relation_types = [rt.name for rt in ontology.relationship_types]
                else:
                    entity_types = list(schema.entity_types.keys()) if hasattr(schema, 'entity_types') else []
                    relation_types = list(schema.relation_types.keys()) if hasattr(schema, 'relation_types') else []
                return self._build_hybrid_extraction_prompt(text, entity_types, relation_types)
        
        # Default to ontology-based extraction
        if ontology:
            return self._build_extraction_prompt(text, ontology)
        else:
            raise ValueError("No schema mode or ontology provided for extraction")
    
    def _build_open_extraction_prompt(self, text: str) -> str:
        """Build prompt for open schema extraction - discover all entities and relationships."""
        prompt = f"""Extract ALL entities and relationships from the following text.
Do not limit yourself to predefined types - discover and categorize all entities and relationships dynamically.

TEXT TO ANALYZE:
{text}

INSTRUCTIONS:
1. Identify ALL entities (people, organizations, places, concepts, technologies, etc.)
2. Assign appropriate types to each entity based on their nature
3. Extract ALL relationships between entities
4. Assign meaningful relationship types based on the context
5. Provide confidence scores (0.0-1.0) for each extraction
6. Include character positions when possible

Return the result as valid JSON with this structure:
{{
    "discovered_types": {{
        "entity_types": ["list of discovered entity types"],
        "relation_types": ["list of discovered relationship types"]
    }},
    "entities": [
        {{
            "text": "exact text span",
            "type": "DISCOVERED_TYPE",
            "confidence": 0.0-1.0,
            "context": "surrounding context",
            "start_pos": 0,
            "end_pos": 0
        }}
    ],
    "relationships": [
        {{
            "source": "source entity text",
            "target": "target entity text",
            "relation": "DISCOVERED_RELATION_TYPE",
            "confidence": 0.0-1.0,
            "context": "relationship context"
        }}
    ]
}}

Be comprehensive - extract ALL entities and relationships you can identify."""
        return prompt
    
    def _build_closed_extraction_prompt(self, text: str, entity_types: List[str], relation_types: List[str]) -> str:
        """Build prompt for closed schema extraction - only predefined types."""
        prompt = f"""Extract entities and relationships from the following text using ONLY the predefined types.

ALLOWED ENTITY TYPES:
{chr(10).join(f"- {et}" for et in entity_types)}

ALLOWED RELATIONSHIP TYPES:
{chr(10).join(f"- {rt}" for rt in relation_types)}

TEXT TO ANALYZE:
{text}

INSTRUCTIONS:
1. Extract ONLY entities that match the allowed entity types
2. Extract ONLY relationships that match the allowed relationship types
3. Do NOT extract entities or relationships of other types
4. Provide confidence scores (0.0-1.0) for each extraction
5. Use exact text spans from the original text

Return the result as valid JSON with this structure:
{{
    "entities": [
        {{
            "text": "exact text span",
            "type": "ALLOWED_ENTITY_TYPE",
            "confidence": 0.0-1.0,
            "context": "surrounding context"
        }}
    ],
    "relationships": [
        {{
            "source": "source entity text",
            "target": "target entity text",
            "relation": "ALLOWED_RELATIONSHIP_TYPE",
            "confidence": 0.0-1.0,
            "context": "relationship context"
        }}
    ]
}}

Only extract entities and relationships that clearly match the allowed types."""
        return prompt
    
    def _build_hybrid_extraction_prompt(self, text: str, entity_types: List[str], relation_types: List[str]) -> str:
        """Build prompt for hybrid schema extraction - predefined types + discovery."""
        prompt = f"""Extract entities and relationships from the following text.
Use the predefined types when applicable, but also discover new types when needed.

PREDEFINED ENTITY TYPES (use these when applicable):
{chr(10).join(f"- {et}" for et in entity_types)}

PREDEFINED RELATIONSHIP TYPES (use these when applicable):
{chr(10).join(f"- {rt}" for rt in relation_types)}

TEXT TO ANALYZE:
{text}

INSTRUCTIONS:
1. Use predefined entity types when entities clearly match them
2. Discover and create new entity types for entities that don't fit predefined types
3. Use predefined relationship types when applicable
4. Discover new relationship types when needed
5. Provide confidence scores (0.0-1.0) for each extraction
6. Mark discovered types clearly

Return the result as valid JSON with this structure:
{{
    "discovered_types": {{
        "entity_types": ["list of newly discovered entity types"],
        "relation_types": ["list of newly discovered relationship types"]
    }},
    "entities": [
        {{
            "text": "exact text span",
            "type": "ENTITY_TYPE",
            "is_discovered": true/false,
            "confidence": 0.0-1.0,
            "context": "surrounding context"
        }}
    ],
    "relationships": [
        {{
            "source": "source entity text",
            "target": "target entity text",
            "relation": "RELATIONSHIP_TYPE",
            "is_discovered": true/false,
            "confidence": 0.0-1.0,
            "context": "relationship context"
        }}
    ]
}}

Prefer predefined types when they clearly apply, but don't force entities into inappropriate types."""
        return prompt
    
    def _parse_schema_aware_response(self, response_content: str, schema, ontology: Optional['DomainOntology'] = None) -> Dict[str, Any]:
        """Parse LLM response based on schema mode."""
        from src.core.extraction_schemas import SchemaMode
        
        try:
            # Parse JSON response
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
            
            # Process based on schema mode
            if hasattr(schema, 'mode'):
                if schema.mode == SchemaMode.OPEN:
                    return self._process_open_schema_response(extraction_data, schema)
                elif schema.mode == SchemaMode.CLOSED:
                    return self._process_closed_schema_response(extraction_data, schema, ontology)
                elif schema.mode == SchemaMode.HYBRID:
                    return self._process_hybrid_schema_response(extraction_data, schema, ontology)
            
            # Default processing
            return self._parse_llm_response(response_content, ontology)
            
        except Exception as e:
            logger.error(f"Failed to parse schema-aware response: {e}")
            raise RuntimeError(f"Schema-aware response parsing failed: {e}")
    
    def _process_open_schema_response(self, data: Dict[str, Any], schema) -> Dict[str, Any]:
        """Process response from open schema extraction."""
        processed_entities = []
        processed_relationships = []
        
        # Track discovered types
        discovered_entity_types = set(data.get('discovered_types', {}).get('entity_types', []))
        discovered_relation_types = set(data.get('discovered_types', {}).get('relation_types', []))
        
        # Handle both response formats - direct or nested under extracted_data
        extracted_data = data.get('extracted_data', data)
        entities = extracted_data.get('entities', [])
        relationships = extracted_data.get('relationships', extracted_data.get('relations', []))
        
        # Process entities - no validation against predefined types
        for entity in entities:
            # Handle both formats: simple with 'text' or complex with 'properties'
            if 'properties' in entity:
                # Complex format from LLM
                entity_text = entity.get('properties', {}).get('name', '') or entity.get('properties', {}).get('title', '')
                entity_type = entity.get('type', 'UNKNOWN')
            else:
                # Simple format
                entity_text = entity.get('text', '')
                entity_type = entity.get('type', 'UNKNOWN')
            
            processed_entities.append({
                'text': entity_text,
                'type': entity_type,
                'confidence': float(entity.get('confidence', 0.8)),
                'context': entity.get('context', ''),
                'start_pos': entity.get('start_pos'),
                'end_pos': entity.get('end_pos'),
                'extraction_method': 'llm_open_schema',
                'timestamp': datetime.now().isoformat()
            })
            discovered_entity_types.add(entity_type)
        
        # Process relationships - no validation against predefined types
        for relationship in relationships:
            # Handle ID-based references
            source = relationship.get('source', '')
            target = relationship.get('target', '')
            
            # Check if source/target are IDs that need resolution
            if isinstance(source, str) and (source.startswith(('person_', 'org_', 'job_', 'tech_', 'company_', 'entity_')) or '_' in source):
                # Need to resolve IDs to text
                source_text = self._resolve_entity_id(source, entities)
                target_text = self._resolve_entity_id(target, entities)
            else:
                source_text = source
                target_text = target
            
            processed_relationships.append({
                'source': source_text,
                'target': target_text,
                'relation': relationship.get('type', relationship.get('relation', 'RELATED_TO')),
                'confidence': float(relationship.get('confidence', 0.8)),
                'context': relationship.get('context', ''),
                'extraction_method': 'llm_open_schema',
                'timestamp': datetime.now().isoformat()
            })
            discovered_relation_types.add(relationship.get('type', relationship.get('relation', 'RELATED_TO')))
        
        return {
            'entities': processed_entities,
            'relationships': processed_relationships,
            'discovered_types': {
                'entity_types': list(discovered_entity_types),
                'relation_types': list(discovered_relation_types)
            },
            'extraction_stats': {
                'entities_extracted': len(processed_entities),
                'relationships_extracted': len(processed_relationships),
                'entity_types_discovered': len(discovered_entity_types),
                'relation_types_discovered': len(discovered_relation_types),
                'extraction_timestamp': datetime.now().isoformat(),
                'schema_mode': 'open'
            }
        }
    
    def _process_closed_schema_response(self, data: Dict[str, Any], schema, ontology: Optional['DomainOntology'] = None) -> Dict[str, Any]:
        """Process response from closed schema extraction - validate against allowed types."""
        processed_entities = []
        processed_relationships = []
        
        # Get valid types from schema or ontology
        if ontology:
            valid_entity_types = {et.name for et in ontology.entity_types}
            valid_relation_types = {rt.name for rt in ontology.relationship_types}
        else:
            valid_entity_types = set(schema.entity_types.keys()) if hasattr(schema, 'entity_types') else set()
            valid_relation_types = set(schema.relation_types.keys()) if hasattr(schema, 'relation_types') else set()
        
        # Process entities - only keep valid types
        for entity in data.get('entities', []):
            entity_type = entity.get('type', '')
            if entity_type in valid_entity_types:
                processed_entities.append({
                    'text': entity.get('text', ''),
                    'type': entity_type,
                    'confidence': float(entity.get('confidence', 0.8)),
                    'context': entity.get('context', ''),
                    'extraction_method': 'llm_closed_schema',
                    'timestamp': datetime.now().isoformat()
                })
            else:
                logger.debug(f"Skipping entity with invalid type: {entity_type}")
        
        # Process relationships - only keep valid types
        for relationship in data.get('relationships', []):
            relation_type = relationship.get('relation', '')
            if relation_type in valid_relation_types:
                processed_relationships.append({
                    'source': relationship.get('source', ''),
                    'target': relationship.get('target', ''),
                    'relation': relation_type,
                    'confidence': float(relationship.get('confidence', 0.8)),
                    'context': relationship.get('context', ''),
                    'extraction_method': 'llm_closed_schema',
                    'timestamp': datetime.now().isoformat()
                })
            else:
                logger.debug(f"Skipping relationship with invalid type: {relation_type}")
        
        return {
            'entities': processed_entities,
            'relationships': processed_relationships,
            'extraction_stats': {
                'entities_extracted': len(processed_entities),
                'relationships_extracted': len(processed_relationships),
                'extraction_timestamp': datetime.now().isoformat(),
                'schema_mode': 'closed'
            }
        }
    
    def _process_hybrid_schema_response(self, data: Dict[str, Any], schema, ontology: Optional['DomainOntology'] = None) -> Dict[str, Any]:
        """Process response from hybrid schema extraction - allow both predefined and discovered types."""
        processed_entities = []
        processed_relationships = []
        
        # Get predefined types
        if ontology:
            predefined_entity_types = {et.name for et in ontology.entity_types}
            predefined_relation_types = {rt.name for rt in ontology.relationship_types}
        else:
            predefined_entity_types = set(schema.entity_types.keys()) if hasattr(schema, 'entity_types') else set()
            predefined_relation_types = set(schema.relation_types.keys()) if hasattr(schema, 'relation_types') else set()
        
        # Track discovered types
        discovered_entity_types = set(data.get('discovered_types', {}).get('entity_types', []))
        discovered_relation_types = set(data.get('discovered_types', {}).get('relation_types', []))
        
        # Process entities - accept both predefined and discovered
        for entity in data.get('entities', []):
            entity_type = entity.get('type', 'UNKNOWN')
            is_discovered = entity.get('is_discovered', entity_type not in predefined_entity_types)
            
            processed_entities.append({
                'text': entity.get('text', ''),
                'type': entity_type,
                'confidence': float(entity.get('confidence', 0.8)),
                'context': entity.get('context', ''),
                'is_discovered': is_discovered,
                'extraction_method': 'llm_hybrid_schema',
                'timestamp': datetime.now().isoformat()
            })
            
            if is_discovered:
                discovered_entity_types.add(entity_type)
        
        # Process relationships - accept both predefined and discovered
        for relationship in data.get('relationships', []):
            relation_type = relationship.get('relation', 'RELATED_TO')
            is_discovered = relationship.get('is_discovered', relation_type not in predefined_relation_types)
            
            processed_relationships.append({
                'source': relationship.get('source', ''),
                'target': relationship.get('target', ''),
                'relation': relation_type,
                'confidence': float(relationship.get('confidence', 0.8)),
                'context': relationship.get('context', ''),
                'is_discovered': is_discovered,
                'extraction_method': 'llm_hybrid_schema',
                'timestamp': datetime.now().isoformat()
            })
            
            if is_discovered:
                discovered_relation_types.add(relation_type)
        
        return {
            'entities': processed_entities,
            'relationships': processed_relationships,
            'discovered_types': {
                'entity_types': list(discovered_entity_types),
                'relation_types': list(discovered_relation_types)
            },
            'extraction_stats': {
                'entities_extracted': len(processed_entities),
                'relationships_extracted': len(processed_relationships),
                'predefined_entities': len([e for e in processed_entities if not e.get('is_discovered', False)]),
                'discovered_entities': len([e for e in processed_entities if e.get('is_discovered', False)]),
                'entity_types_discovered': len(discovered_entity_types),
                'relation_types_discovered': len(discovered_relation_types),
                'extraction_timestamp': datetime.now().isoformat(),
                'schema_mode': 'hybrid'
            }
        }
    
    def _resolve_entity_id(self, entity_id: str, entities: List[Dict[str, Any]]) -> str:
        """Resolve entity ID to its text representation."""
        # First try exact ID match
        for entity in entities:
            if entity.get('id') == entity_id:
                # Handle both formats
                if 'properties' in entity:
                    return entity.get('properties', {}).get('name', '') or entity.get('properties', {}).get('title', entity_id)
                else:
                    return entity.get('text', entity_id)
        
        # If no exact match, try partial matching (e.g., "company_1" might match entity with ID "1" and type "company")
        id_parts = entity_id.split('_')
        if len(id_parts) >= 2:
            entity_type = id_parts[0]
            entity_num = id_parts[-1]
            
            # Try to match by type and number/position
            entities_of_type = [e for e in entities if e.get('type', '').lower() == entity_type.lower()]
            if entity_num.isdigit() and int(entity_num) <= len(entities_of_type):
                # Use position-based matching (1-indexed)
                entity = entities_of_type[int(entity_num) - 1]
                if 'properties' in entity:
                    return entity.get('properties', {}).get('name', '') or entity.get('properties', {}).get('title', entity_id)
                else:
                    return entity.get('text', entity_id)
        
        return entity_id  # Return ID if not found

