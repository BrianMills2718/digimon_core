"""
Gemini 2.5 Flash Ontology Generator with structured output.
Uses Google's Generative AI for domain-specific ontology generation.
"""

import os
import json
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import logging

from src.ontology_generator import DomainOntology, EntityType, RelationshipType

logger = logging.getLogger(__name__)


class GeminiOntologyGenerator:
    """Generate domain ontologies using Gemini 2.5 Flash with structured output."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini generator.
        
        Args:
            api_key: Google API key. If None, uses GOOGLE_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google API key required. Set GOOGLE_API_KEY env var or pass api_key.")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Safety settings to allow academic content
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }
    
    def generate_from_conversation(self, messages: List[Dict[str, str]], 
                                 temperature: float = 0.7,
                                 constraints: Optional[Dict[str, Any]] = None) -> DomainOntology:
        """
        Generate ontology from conversation history.
        
        Args:
            messages: List of conversation messages with 'role' and 'content'
            temperature: Generation temperature (0-1)
            constraints: Optional constraints (max entities, complexity, etc.)
            
        Returns:
            Generated DomainOntology
        """
        # Build conversation context
        conversation_text = self._format_conversation(messages)
        
        # Create structured prompt
        prompt = self._create_ontology_prompt(conversation_text, constraints)
        
        try:
            # Generate with Gemini
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    candidate_count=1,
                    max_output_tokens=4000,
                ),
                safety_settings=self.safety_settings
            )
            
            # Parse structured output
            ontology_data = self._parse_response(response.text)
            
            # Convert to DomainOntology
            return self._build_ontology(ontology_data, conversation_text)
            
        except Exception as e:
            logger.error(f"Error generating ontology: {e}")
            raise
    
    def _format_conversation(self, messages: List[Dict[str, str]]) -> str:
        """Format conversation messages into text."""
        formatted = []
        for msg in messages:
            role = "User" if msg["role"] == "user" else "Assistant"
            formatted.append(f"{role}: {msg['content']}")
        return "\n".join(formatted)
    
    def _create_ontology_prompt(self, conversation: str, 
                               constraints: Optional[Dict[str, Any]] = None) -> str:
        """Create structured prompt for ontology generation."""
        constraint_text = ""
        if constraints:
            if "max_entities" in constraints:
                constraint_text += f"{chr(10)}- Maximum entity types: {constraints['max_entities']}"
            if "max_relations" in constraints:
                constraint_text += f"{chr(10)}- Maximum relationship types: {constraints['max_relations']}"
            if "complexity" in constraints:
                constraint_text += f"{chr(10)}- Complexity level: {constraints['complexity']}"
        
        prompt = f"""Based on the following conversation about a domain, generate a formal ontology specification.

CONVERSATION:
{conversation}

CONSTRAINTS:{constraint_text if constraint_text else chr(10) + "None"}

Generate a domain ontology in the following JSON format:
{{
    "domain_name": "Short domain name",
    "domain_description": "One paragraph description of the domain",
    "entity_types": [
        {{
            "name": "ENTITY_TYPE_NAME",
            "description": "What this entity represents",
            "examples": ["example1", "example2", "example3"],
            "attributes": ["key_attribute1", "key_attribute2"]
        }}
    ],
    "relationship_types": [
        {{
            "name": "RELATIONSHIP_NAME",
            "description": "What this relationship represents",
            "source_types": ["ENTITY_TYPE1"],
            "target_types": ["ENTITY_TYPE2"],
            "examples": ["Entity1 RELATIONSHIP Entity2"]
        }}
    ],
    "extraction_guidelines": [
        "Guideline 1 for identifying entities in text",
        "Guideline 2 for identifying relationships",
        "Guideline 3 for handling ambiguity"
    ]
}}

Important requirements:
1. Entity type names should be UPPERCASE_WITH_UNDERSCORES
2. Relationship names should be UPPERCASE_WITH_UNDERSCORES
3. Include 3-5 concrete examples for each type
4. Focus on domain-specific types, not generic ones
5. Relationships should connect specific entity types
6. Extraction guidelines should be actionable

Respond ONLY with the JSON, no additional text."""
        
        return prompt
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse JSON response from Gemini."""
        try:
            # Clean response if needed
            cleaned = response_text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response text: {response_text}")
            raise ValueError(f"Invalid JSON response from Gemini: {e}")
    
    def _build_ontology(self, data: Dict[str, Any], conversation: str) -> DomainOntology:
        """Build DomainOntology from parsed data."""
        # Convert entity types
        entity_types = []
        for et in data.get("entity_types", []):
            entity_types.append(EntityType(
                name=et["name"],
                description=et["description"],
                examples=et.get("examples", []),
                attributes=et.get("attributes", [])
            ))
        
        # Convert relationship types
        relationship_types = []
        for rt in data.get("relationship_types", []):
            relationship_types.append(RelationshipType(
                name=rt["name"],
                description=rt["description"],
                source_types=rt.get("source_types", []),
                target_types=rt.get("target_types", []),
                examples=rt.get("examples", [])
            ))
        
        return DomainOntology(
            domain_name=data["domain_name"],
            domain_description=data["domain_description"],
            entity_types=entity_types,
            relationship_types=relationship_types,
            extraction_patterns=data.get("extraction_guidelines", []),
            created_by_conversation=conversation
        )
    
    def validate_ontology(self, ontology: DomainOntology, sample_text: str) -> Dict[str, Any]:
        """
        Validate ontology by testing extraction on sample text.
        
        Args:
            ontology: The ontology to validate
            sample_text: Sample text to test extraction
            
        Returns:
            Validation report with extracted entities and issues
        """
        prompt = f"""Using the following ontology, extract entities and relationships from the sample text.

ONTOLOGY:
Domain: {ontology.domain_name}
Entity Types: {[e.name for e in ontology.entity_types]}
Relationship Types: {[r.name for r in ontology.relationship_types]}

SAMPLE TEXT:
{sample_text}

Extract entities and relationships in this JSON format:
{{
    "entities": [
        {{
            "text": "extracted text",
            "type": "ENTITY_TYPE",
            "confidence": 0.95
        }}
    ],
    "relationships": [
        {{
            "source": "source entity text",
            "relation": "RELATIONSHIP_TYPE",
            "target": "target entity text",
            "confidence": 0.90
        }}
    ],
    "issues": [
        "Any ambiguities or difficulties encountered"
    ]
}}

Respond ONLY with the JSON."""
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,  # Lower temperature for extraction
                    candidate_count=1,
                    max_output_tokens=2000,
                ),
                safety_settings=self.safety_settings
            )
            
            return self._parse_response(response.text)
            
        except Exception as e:
            logger.error(f"Error validating ontology: {e}")
            return {
                "entities": [],
                "relationships": [],
                "issues": [f"Validation error: {str(e)}"]
            }
    
    def refine_ontology(self, ontology: DomainOntology, 
                       refinement_request: str) -> DomainOntology:
        """
        Refine an existing ontology based on user feedback.
        
        Args:
            ontology: Current ontology
            refinement_request: User's refinement request
            
        Returns:
            Refined DomainOntology
        """
        current_json = {
            "domain_name": ontology.domain_name,
            "domain_description": ontology.domain_description,
            "entity_types": [asdict(e) for e in ontology.entity_types],
            "relationship_types": [asdict(r) for r in ontology.relationship_types],
            "extraction_guidelines": ontology.extraction_patterns
        }
        
        prompt = f"""Refine the following ontology based on the user's request.

CURRENT ONTOLOGY:
{json.dumps(current_json, indent=2)}

USER REQUEST:
{refinement_request}

Generate the refined ontology in the same JSON format. Make only the requested changes while preserving the overall structure.

Respond ONLY with the JSON."""
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.5,
                    candidate_count=1,
                    max_output_tokens=4000,
                ),
                safety_settings=self.safety_settings
            )
            
            refined_data = self._parse_response(response.text)
            return self._build_ontology(refined_data, 
                                      ontology.created_by_conversation + f"\n\nRefinement: {refinement_request}")
            
        except Exception as e:
            logger.error(f"Error refining ontology: {e}")
            raise