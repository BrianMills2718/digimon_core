"""
T23c: Ontology-Aware Entity Extractor
Replaces generic spaCy NER with domain-specific extraction using LLMs and ontologies.
"""

import os
import json
import logging
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import numpy as np
from datetime import datetime

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import openai

from src.core.base_types import Entity, Relationship, Mention
from src.core.enhanced_identity_service import EnhancedIdentityService
from src.ontology_generator import DomainOntology, EntityType, RelationshipType

logger = logging.getLogger(__name__)


@dataclass
class ExtractionResult:
    """Result of ontology-aware extraction."""
    entities: List[Entity]
    relationships: List[Relationship]
    mentions: List[Mention]
    extraction_metadata: Dict[str, Any]


class OntologyAwareExtractor:
    """
    Extract entities and relationships using domain-specific ontologies.
    Uses Gemini for extraction and OpenAI for embeddings.
    """
    
    def __init__(self, 
                 identity_service: EnhancedIdentityService,
                 google_api_key: Optional[str] = None,
                 openai_api_key: Optional[str] = None):
        """
        Initialize the extractor.
        
        Args:
            identity_service: Service for entity resolution and identity management
            google_api_key: Google API key for Gemini
            openai_api_key: OpenAI API key for embeddings
        """
        self.identity_service = identity_service
        
        # Initialize Gemini
        self.google_api_key = google_api_key or os.getenv("GOOGLE_API_KEY")
        if not self.google_api_key:
            raise ValueError("Google API key required")
        
        genai.configure(api_key=self.google_api_key)
        self.gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Safety settings for academic content
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }
        
        # Initialize OpenAI for embeddings
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
            self.openai_client = openai.OpenAI()
        else:
            logger.warning("OpenAI API key not provided. Embeddings will use mock values.")
            self.openai_client = None
    
    def extract_entities(self, 
                        text: str, 
                        ontology: DomainOntology,
                        source_ref: str,
                        confidence_threshold: float = 0.7) -> ExtractionResult:
        """
        Extract entities and relationships from text using domain ontology.
        
        Args:
            text: Text to extract from
            ontology: Domain-specific ontology
            source_ref: Reference to source document
            confidence_threshold: Minimum confidence for extraction
            
        Returns:
            ExtractionResult with entities, relationships, and mentions
        """
        start_time = datetime.now()
        
        # Step 1: Use Gemini to extract based on ontology
        raw_extraction = self._gemini_extract(text, ontology)
        
        # Step 2: Create mentions and entities
        entities = []
        mentions = []
        entity_map = {}  # Track text -> entity mapping
        
        for raw_entity in raw_extraction.get("entities", []):
            if raw_entity.get("confidence", 0) < confidence_threshold:
                continue
            
            # Create mention
            mention = self._create_mention(
                surface_text=raw_entity["text"],
                entity_type=raw_entity["type"],
                source_ref=source_ref,
                confidence=raw_entity.get("confidence", 0.8),
                context=raw_entity.get("context", "")
            )
            mentions.append(mention)
            
            # Create or resolve entity
            entity = self._resolve_or_create_entity(
                surface_text=raw_entity["text"],
                entity_type=raw_entity["type"],
                ontology=ontology,
                confidence=raw_entity.get("confidence", 0.8)
            )
            entities.append(entity)
            entity_map[raw_entity["text"]] = entity
            
            # Link mention to entity
            self.identity_service.link_mention_to_entity(mention.id, entity.id)
        
        # Step 3: Create relationships
        relationships = []
        for raw_rel in raw_extraction.get("relationships", []):
            if raw_rel.get("confidence", 0) < confidence_threshold:
                continue
            
            source_entity = entity_map.get(raw_rel["source"])
            target_entity = entity_map.get(raw_rel["target"])
            
            if source_entity and target_entity:
                relationship = Relationship(
                    id=f"rel_{len(relationships)}_{source_ref}",
                    source_id=source_entity.id,
                    target_id=target_entity.id,
                    relationship_type=raw_rel["relation"],
                    confidence=raw_rel.get("confidence", 0.8),
                    attributes={
                        "extracted_from": source_ref,
                        "context": raw_rel.get("context", ""),
                        "ontology_domain": ontology.domain_name
                    }
                )
                relationships.append(relationship)
        
        # Step 4: Generate embeddings for entities
        if self.openai_client:
            self._generate_embeddings(entities, ontology)
        
        extraction_time = (datetime.now() - start_time).total_seconds()
        
        return ExtractionResult(
            entities=entities,
            relationships=relationships,
            mentions=mentions,
            extraction_metadata={
                "ontology_domain": ontology.domain_name,
                "extraction_time_seconds": extraction_time,
                "source_ref": source_ref,
                "total_entities": len(entities),
                "total_relationships": len(relationships),
                "confidence_threshold": confidence_threshold
            }
        )
    
    def _gemini_extract(self, text: str, ontology: DomainOntology) -> Dict[str, Any]:
        """Use Gemini to extract entities and relationships based on ontology."""
        # Build entity and relationship descriptions
        entity_desc = []
        for et in ontology.entity_types:
            examples = ", ".join(et.examples[:3]) if et.examples else "no examples"
            entity_desc.append(f"- {et.name}: {et.description} (examples: {examples})")
        
        rel_desc = []
        for rt in ontology.relationship_types:
            rel_desc.append(f"- {rt.name}: {rt.description} (connects {rt.source_types} to {rt.target_types})")
        
        guidelines = "\n".join(f"- {g}" for g in ontology.extraction_patterns)
        
        prompt = f"""Extract domain-specific entities and relationships from the following text using the provided ontology.

DOMAIN: {ontology.domain_name}
{ontology.domain_description}

ENTITY TYPES:
{chr(10).join(entity_desc)}

RELATIONSHIP TYPES:
{chr(10).join(rel_desc)}

EXTRACTION GUIDELINES:
{guidelines}

TEXT TO ANALYZE:
{text}

Extract entities and relationships in this JSON format:
{{
    "entities": [
        {{
            "text": "exact text from source",
            "type": "ENTITY_TYPE_NAME",
            "confidence": 0.95,
            "context": "surrounding context"
        }}
    ],
    "relationships": [
        {{
            "source": "source entity text",
            "relation": "RELATIONSHIP_TYPE",
            "target": "target entity text",
            "confidence": 0.90,
            "context": "relationship context"
        }}
    ]
}}

Important:
1. Only extract entities that match the defined types
2. Use exact text from the source
3. Include confidence scores (0-1)
4. Provide context for disambiguation
5. Only extract relationships between identified entities

Respond ONLY with the JSON."""
        
        try:
            response = self.gemini_model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,  # Low temperature for consistent extraction
                    candidate_count=1,
                    max_output_tokens=4000,
                ),
                safety_settings=self.safety_settings
            )
            
            # Parse response
            cleaned = response.text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            
            return json.loads(cleaned)
            
        except Exception as e:
            logger.error(f"Gemini extraction failed: {e}")
            return {"entities": [], "relationships": []}
    
    def _create_mention(self, surface_text: str, entity_type: str, 
                       source_ref: str, confidence: float, context: str) -> Mention:
        """Create a mention for the extracted text."""
        mention_data = self.identity_service.create_mention(
            surface_form=surface_text,
            start_pos=0,  # Would need proper position tracking in production
            end_pos=len(surface_text),
            source_ref=source_ref,
            entity_type=entity_type,
            confidence=confidence
        )
        
        return Mention(
            id=mention_data["mention_id"],
            surface_form=surface_text,
            start_pos=0,
            end_pos=len(surface_text),
            source_ref=source_ref,
            entity_type=entity_type,
            confidence=confidence,
            context=context
        )
    
    def _resolve_or_create_entity(self, surface_text: str, entity_type: str,
                                 ontology: DomainOntology, confidence: float) -> Entity:
        """Resolve to existing entity or create new one."""
        # Try to find similar existing entities
        similar = self.identity_service.find_similar_entities(surface_text, threshold=0.85)
        
        if similar:
            # Use the most similar existing entity
            return Entity(
                id=similar[0]["entity_id"],
                canonical_name=similar[0]["canonical_name"],
                entity_type=entity_type,
                confidence=max(confidence, similar[0]["confidence"]),
                attributes={
                    "ontology_domain": ontology.domain_name,
                    "resolved": True,
                    "similarity_score": similar[0]["similarity"]
                }
            )
        else:
            # Create new entity
            entity_data = self.identity_service.create_entity(
                canonical_name=surface_text,
                entity_type=entity_type,
                confidence=confidence
            )
            
            return Entity(
                id=entity_data["entity_id"],
                canonical_name=surface_text,
                entity_type=entity_type,
                confidence=confidence,
                attributes={
                    "ontology_domain": ontology.domain_name,
                    "resolved": False
                }
            )
    
    def _generate_embeddings(self, entities: List[Entity], ontology: DomainOntology):
        """Generate contextual embeddings for entities using OpenAI."""
        for entity in entities:
            # Create context-rich description
            entity_type_info = next((et for et in ontology.entity_types 
                                   if et.name == entity.entity_type), None)
            
            if entity_type_info:
                context = f"{entity.entity_type}: {entity.canonical_name} - {entity_type_info.description}"
            else:
                context = f"{entity.entity_type}: {entity.canonical_name}"
            
            try:
                # Generate embedding
                response = self.openai_client.embeddings.create(
                    model="text-embedding-3-small",
                    input=context
                )
                
                embedding = response.data[0].embedding
                
                # Store embedding (would go to Qdrant in production)
                entity.attributes["embedding"] = embedding
                entity.attributes["embedding_model"] = "text-embedding-3-small"
                entity.attributes["embedding_context"] = context
                
            except Exception as e:
                logger.error(f"Failed to generate embedding for {entity.canonical_name}: {e}")
                # Use mock embedding
                entity.attributes["embedding"] = np.random.randn(1536).tolist()
                entity.attributes["embedding_model"] = "mock"
    
    def batch_extract(self, 
                     texts: List[Tuple[str, str]],  # (text, source_ref) pairs
                     ontology: DomainOntology,
                     confidence_threshold: float = 0.7) -> List[ExtractionResult]:
        """
        Extract from multiple texts efficiently.
        
        Args:
            texts: List of (text, source_ref) tuples
            ontology: Domain ontology to use
            confidence_threshold: Minimum confidence
            
        Returns:
            List of ExtractionResult objects
        """
        results = []
        
        for text, source_ref in texts:
            try:
                result = self.extract_entities(
                    text=text,
                    ontology=ontology,
                    source_ref=source_ref,
                    confidence_threshold=confidence_threshold
                )
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to extract from {source_ref}: {e}")
                # Return empty result on failure
                results.append(ExtractionResult(
                    entities=[],
                    relationships=[],
                    mentions=[],
                    extraction_metadata={
                        "error": str(e),
                        "source_ref": source_ref
                    }
                ))
        
        return results