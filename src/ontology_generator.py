#!/usr/bin/env python3
"""
Ontology Generator Module - Gemini Integration
Handles LLM-based ontology generation and refinement
CLEANED VERSION - No mock/fallback patterns
"""

import os
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import google.generativeai as genai
from pathlib import Path

# Configure Gemini
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

# Data classes matching the Streamlit app
@dataclass
class EntityType:
    name: str
    description: str
    attributes: List[str]
    examples: List[str]
    parent: Optional[str] = None

@dataclass
class RelationType:
    name: str
    description: str
    source_types: List[str]
    target_types: List[str]
    examples: List[str]
    properties: Optional[Dict[str, str]] = None

@dataclass
class RelationshipType:
    """Alias for RelationType to match Gemini generator expectations"""
    name: str
    description: str
    source_types: List[str]
    target_types: List[str]
    examples: List[str]
    properties: Optional[Dict[str, str]] = None

@dataclass
class DomainOntology:
    """Core ontology data structure for domain-specific knowledge"""
    domain_name: str
    domain_description: str
    entity_types: List[EntityType]
    relationship_types: List[RelationshipType]
    extraction_patterns: List[str]
    created_by_conversation: str = ""

@dataclass
class Ontology:
    """UI-compatible ontology structure"""
    domain: str
    description: str
    entity_types: List[EntityType]
    relation_types: List[RelationType]
    version: str = "1.0"
    created_at: Optional[str] = None
    modified_at: Optional[str] = None

class OntologyGenerator:
    """Main class for generating and refining ontologies using LLMs"""
    
    # IMPORTANT: DO NOT CHANGE DEFAULT MODEL - gemini-2.5-flash has 1000 RPM limit
    # Other models have much lower limits (e.g., 10 RPM) and will cause quota errors
    def __init__(self, model_name: Optional[str] = None):
        """Initialize the generator with specified model"""
        # Get model from standard config (single source of truth)
        if model_name is None:
            from src.core.standard_config import get_model
            self.model_name = get_model("ontology_generator")
        else:
            self.model_name = model_name
        self.model = None
        if GOOGLE_API_KEY:
            try:
                self.model = genai.GenerativeModel(model_name)
            except Exception as e:
                print(f"Warning: Could not initialize Gemini model: {e}")
        
        # Load prompts
        self.prompts = self._load_prompts()
    
    def _load_prompts(self) -> Dict[str, str]:
        """Load prompt templates"""
        prompts_dir = Path(__file__).parent / "prompts"
        prompts = {}
        
        # Default prompts if files don't exist
        prompts["generate_ontology"] = """
You are an expert ontology designer. Create a domain-specific ontology based on the user's description.

User Domain Description:
{domain_description}

Configuration:
- Maximum entity types: {max_entities}
- Maximum relation types: {max_relations}
- Include hierarchies: {include_hierarchies}
- Auto-suggest attributes: {auto_suggest_attributes}

Generate a comprehensive ontology with:
1. Entity types relevant to the domain (with clear names, descriptions, attributes, and examples)
2. Relation types that connect these entities (with source/target constraints and examples)
3. A clear domain name and description

Format your response as valid JSON matching this structure:
{{
    "domain": "Domain Name",
    "description": "Clear description of the domain",
    "entity_types": [
        {{
            "name": "ENTITY_NAME",
            "description": "What this entity represents",
            "attributes": ["attr1", "attr2"],
            "examples": ["example1", "example2"],
            "parent": null
        }}
    ],
    "relation_types": [
        {{
            "name": "RELATION_NAME",
            "description": "What this relation represents",
            "source_types": ["SOURCE_ENTITY"],
            "target_types": ["TARGET_ENTITY"],
            "examples": ["Example of this relation"],
            "properties": null
        }}
    ]
}}

Important guidelines:
- Use UPPER_CASE_SNAKE for entity and relation names
- Be specific to the domain (avoid generic entities like PERSON, ORGANIZATION)
- Include domain-specific attributes
- Provide concrete examples from the domain
- Relations should be meaningful and actionable
"""

        prompts["refine_ontology"] = """
You are refining an existing domain ontology based on user feedback.

Current Ontology:
{current_ontology}

User Refinement Request:
{refinement_request}

Modify the ontology according to the user's request. Maintain the same JSON structure and only change what's necessary.

Return the complete updated ontology in the same JSON format.
"""

        prompts["extract_entities"] = """
Extract entities from the following text using the provided ontology.

Ontology:
{ontology}

Text:
{text}

For each entity found, provide:
1. The exact text span
2. The entity type from the ontology
3. Confidence score (0-1)
4. Any extracted attributes

Format as JSON:
{{
    "entities": [
        {{
            "text": "extracted text",
            "type": "ENTITY_TYPE",
            "confidence": 0.95,
            "attributes": {{"attr": "value"}}
        }}
    ]
}}
"""
        
        # Try to load from files if they exist
        if prompts_dir.exists():
            for prompt_file in prompts_dir.glob("*.txt"):
                prompt_name = prompt_file.stem
                prompts[prompt_name] = prompt_file.read_text()
        
        return prompts
    
    def generate_ontology(self, domain_description: str, config: Dict[str, Any]) -> Ontology:
        """Generate a new ontology from domain description"""
        # TODO: enforce v9 required fields
        if not self.model:
            raise ValueError("Gemini model not available. Check GOOGLE_API_KEY environment variable.")
        
        try:
            # Prepare the prompt
            prompt = self.prompts["generate_ontology"].format(
                domain_description=domain_description,
                max_entities=config.get("max_entities", 20),
                max_relations=config.get("max_relations", 15),
                include_hierarchies=config.get("include_hierarchies", True),
                auto_suggest_attributes=config.get("auto_suggest_attributes", True)
            )
            
            # Generate with Gemini
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=config.get("temperature", 0.7),
                    response_mime_type="application/json"
                )
            )
            
            # Parse response
            ontology_data = json.loads(response.text)
            
            # Convert to Ontology object
            entity_types = [EntityType(**et) for et in ontology_data["entity_types"]]
            relation_types = [RelationType(**rt) for rt in ontology_data["relation_types"]]
            
            return Ontology(
                domain=ontology_data["domain"],
                description=ontology_data["description"],
                entity_types=entity_types,
                relation_types=relation_types,
                created_at=datetime.now().isoformat()
            )
            
        except Exception as e:
            raise RuntimeError(f"Failed to generate ontology with Gemini: {e}") from e
    
    def refine_ontology(self, current_ontology: Ontology, refinement_request: str) -> Ontology:
        """Refine an existing ontology based on user feedback"""
        if not self.model:
            raise ValueError("Gemini model not available. Check GOOGLE_API_KEY environment variable.")
        
        try:
            # Convert ontology to dict for prompt
            ontology_dict = asdict(current_ontology)
            
            # Prepare the prompt
            prompt = self.prompts["refine_ontology"].format(
                current_ontology=json.dumps(ontology_dict, indent=2),
                refinement_request=refinement_request
            )
            
            # Generate with Gemini
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.3,  # Lower temperature for refinement
                    response_mime_type="application/json"
                )
            )
            
            # Parse response
            ontology_data = json.loads(response.text)
            
            # Convert to Ontology object
            entity_types = [EntityType(**et) for et in ontology_data["entity_types"]]
            relation_types = [RelationType(**rt) for rt in ontology_data["relation_types"]]
            
            return Ontology(
                domain=ontology_data["domain"],
                description=ontology_data["description"],
                entity_types=entity_types,
                relation_types=relation_types,
                version=current_ontology.version,
                created_at=current_ontology.created_at,
                modified_at=datetime.now().isoformat()
            )
            
        except Exception as e:
            raise RuntimeError(f"Failed to refine ontology with Gemini: {e}") from e
    
    def extract_entities(self, text: str, ontology: Ontology) -> List[Dict[str, Any]]:
        """Extract entities from text using the ontology"""
        if not self.model:
            raise ValueError("Gemini model not available. Check GOOGLE_API_KEY environment variable.")
        
        try:
            # Prepare prompt
            ontology_summary = {
                "entity_types": [
                    {"name": et.name, "description": et.description}
                    for et in ontology.entity_types
                ]
            }
            
            prompt = self.prompts["extract_entities"].format(
                ontology=json.dumps(ontology_summary, indent=2),
                text=text
            )
            
            # Generate with Gemini
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.1,  # Low temperature for extraction
                    response_mime_type="application/json"
                )
            )
            
            # Parse response
            result = json.loads(response.text)
            return result.get("entities", [])
            
        except Exception as e:
            raise RuntimeError(f"Failed to extract entities with Gemini: {e}") from e
    
    def validate_with_text(self, ontology: Ontology, sample_text: str) -> Dict[str, Any]:
        """Validate ontology completeness using sample text"""
        # Extract entities
        entities = self.extract_entities(sample_text, ontology)
        
        # Calculate coverage metrics
        entity_types_found = set(entity["type"] for entity in entities)
        total_entity_types = len(ontology.entity_types)
        coverage = len(entity_types_found) / total_entity_types if total_entity_types > 0 else 0
        
        # Generate suggestions for improvement
        unused_types = [et.name for et in ontology.entity_types if et.name not in entity_types_found]
        suggestions = [f"Consider adding examples for {et}" for et in unused_types[:3]]
        
        # Look for patterns in unmatched text (simplified analysis)
        text_words = set(sample_text.lower().split())
        ontology_words = set()
        for et in ontology.entity_types:
            ontology_words.update(ex.lower() for ex in et.examples)
        
        unmatched_words = text_words - ontology_words
        if len(unmatched_words) > 5:
            suggestions.append("Consider adding entity types for domain-specific terms found in text")
        
        return {
            "entities_found": len(entities),
            "relations_found": len(entities) // 2,  # Estimate relation count
            "coverage": coverage,
            "entity_types_used": list(entity_types_found),
            "suggestions": suggestions[:3]  # Limit suggestions
        }


# Convenience functions for external use
def generate_domain_ontology(
    domain_description: str,
    config: Optional[Dict[str, Any]] = None
) -> Ontology:
    """Generate an ontology for a domain"""
    if config is None:
        config = {}
    
    generator = OntologyGenerator()
    return generator.generate_ontology(domain_description, config)

def refine_existing_ontology(
    current_ontology: Ontology,
    refinement_request: str
) -> Ontology:
    """Refine an existing ontology based on feedback"""
    generator = OntologyGenerator()
    return generator.refine_ontology(current_ontology, refinement_request)

def validate_ontology_coverage(
    ontology: Ontology,
    sample_text: str
) -> Dict[str, Any]:
    """Validate how well an ontology covers a sample text"""
    generator = OntologyGenerator()
    return generator.validate_with_text(ontology, sample_text)