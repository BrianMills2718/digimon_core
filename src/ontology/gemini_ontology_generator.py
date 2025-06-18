"""
Gemini 2.5 Flash Ontology Generator with structured output.
Uses Google's Generative AI for domain-specific ontology generation.
"""

import os
import json
import re
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
        # IMPORTANT: DO NOT CHANGE THIS MODEL - gemini-2.5-flash has 1000 RPM limit
        # Other models have much lower limits (e.g., 10 RPM) and will cause quota errors
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
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
            
            # Validate response before parsing
            response_text = self._extract_response_text(response)
            
            # Parse structured output
            ontology_data = self._parse_response(response_text)
            
            # Convert to DomainOntology
            return self._build_ontology(ontology_data, conversation_text)
            
        except Exception as e:
            logger.error(f"Error generating ontology: {e}")
            raise
    
    def _extract_response_text(self, response) -> str:
        """
        Extract text from Gemini response with proper error handling.
        
        Args:
            response: Gemini GenerateContentResponse object
            
        Returns:
            Extracted response text
            
        Raises:
            ValueError: If response is blocked, empty, or invalid
        """
        # Check if response has candidates
        if not response.candidates:
            raise ValueError("No response candidates returned from Gemini")
        
        candidate = response.candidates[0]
        
        # Check finish reason
        finish_reason = candidate.finish_reason
        if finish_reason == 2:  # SAFETY
            safety_ratings = getattr(candidate, 'safety_ratings', [])
            safety_issues = [
                f"{rating.category.name}: {rating.probability.name}" 
                for rating in safety_ratings 
                if rating.probability.name in ['HIGH', 'MEDIUM']
            ]
            raise ValueError(f"Response blocked by safety filters: {safety_issues}")
        elif finish_reason == 3:  # RECITATION
            raise ValueError("Response blocked due to recitation concerns")
        elif finish_reason == 4:  # OTHER
            raise ValueError("Response generation stopped for unknown reasons")
        elif finish_reason != 1:  # Not STOP (successful completion)
            raise ValueError(f"Response generation incomplete (finish_reason: {finish_reason})")
        
        # Try to extract text content
        try:
            if hasattr(response, 'text') and response.text:
                return response.text
            elif candidate.content and candidate.content.parts:
                # Extract from parts if direct text access fails
                text_parts = []
                for part in candidate.content.parts:
                    if hasattr(part, 'text') and part.text:
                        text_parts.append(part.text)
                if text_parts:
                    return ''.join(text_parts)
        except Exception as e:
            logger.warning(f"Error accessing response.text: {e}")
        
        raise ValueError("No valid text content found in response")

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
        """Parse JSON response from Gemini with robust error handling."""
        if not response_text or not response_text.strip():
            raise ValueError("Empty response text from Gemini")
        
        # Clean response text
        cleaned = self._clean_json_response(response_text)
        
        # Attempt to parse JSON with multiple strategies
        parse_errors = []
        
        # Strategy 1: Direct parsing
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            parse_errors.append(f"Direct parsing: {e}")
        
        # Strategy 2: Extract JSON from text (handle cases where there's extra text)
        try:
            json_start = cleaned.find('{')
            json_end = cleaned.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_only = cleaned[json_start:json_end]
                return json.loads(json_only)
        except json.JSONDecodeError as e:
            parse_errors.append(f"JSON extraction: {e}")
        
        # Strategy 3: Fix common JSON issues
        try:
            fixed_json = self._fix_common_json_issues(cleaned)
            return json.loads(fixed_json)
        except json.JSONDecodeError as e:
            parse_errors.append(f"JSON fixing: {e}")
        
        # All strategies failed
        logger.error(f"Failed to parse JSON response with all strategies:")
        for i, error in enumerate(parse_errors, 1):
            logger.error(f"  Strategy {i}: {error}")
        logger.error(f"Original response text: {response_text[:500]}...")
        logger.error(f"Cleaned response text: {cleaned[:500]}...")
        
        raise ValueError(f"Invalid JSON response from Gemini. Tried {len(parse_errors)} parsing strategies. Last error: {parse_errors[-1]}")
    
    def _clean_json_response(self, response_text: str) -> str:
        """Clean response text to extract JSON content."""
        cleaned = response_text.strip()
        
        # Remove markdown code blocks
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        
        # Remove common prefixes/suffixes
        prefixes_to_remove = [
            "Here's the ontology:",
            "Here is the ontology:",
            "The ontology is:",
            "JSON:",
            "Response:",
        ]
        
        for prefix in prefixes_to_remove:
            if cleaned.lower().startswith(prefix.lower()):
                cleaned = cleaned[len(prefix):].strip()
        
        # Clean up whitespace and control characters
        cleaned = cleaned.strip()
        
        return cleaned
    
    def _fix_common_json_issues(self, json_text: str) -> str:
        """Fix common JSON formatting issues."""
        fixed = json_text
        
        # Fix trailing commas before closing brackets/braces
        fixed = re.sub(r',(\s*[}\]])', r'\1', fixed)
        
        # Fix single quotes (replace with double quotes, but be careful with apostrophes)
        # This is a basic approach and might need refinement
        fixed = re.sub(r"'([^']*)'(\s*:)", r'"\1"\2', fixed)  # Keys
        fixed = re.sub(r":\s*'([^']*)'", r': "\1"', fixed)    # Values
        
        # Fix common escape issues
        fixed = fixed.replace('\n', '\\n')
        fixed = fixed.replace('\t', '\\t')
        fixed = fixed.replace('\r', '\\r')
        
        return fixed
    
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
            
            # Validate response before parsing
            response_text = self._extract_response_text(response)
            return self._parse_response(response_text)
            
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
            
            # Validate response before parsing
            response_text = self._extract_response_text(response)
            refined_data = self._parse_response(response_text)
            return self._build_ontology(refined_data, 
                                      ontology.created_by_conversation + f"\n\nRefinement: {refinement_request}")
            
        except Exception as e:
            logger.error(f"Error refining ontology: {e}")
            raise