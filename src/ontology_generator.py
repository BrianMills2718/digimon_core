"""
Ontology Generator Module - Gemini Integration
Handles LLM-based ontology generation and refinement
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
    
    def __init__(self, model_name: str = "gemini-2.0-flash-thinking-exp"):
        """Initialize the generator with specified model"""
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
        if not self.model:
            # Return mock data if no model
            return self._generate_mock_ontology(domain_description)
        
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
            print(f"Error generating ontology: {e}")
            return self._generate_mock_ontology(domain_description)
    
    def refine_ontology(self, current_ontology: Ontology, refinement_request: str) -> Ontology:
        """Refine an existing ontology based on user feedback"""
        if not self.model:
            # Return slightly modified mock
            current_ontology.modified_at = datetime.now().isoformat()
            return current_ontology
        
        try:
            # Convert ontology to dict for prompt
            ontology_dict = asdict(current_ontology)
            
            # Prepare prompt
            prompt = self.prompts["refine_ontology"].format(
                current_ontology=json.dumps(ontology_dict, indent=2),
                refinement_request=refinement_request
            )
            
            # Generate with Gemini
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.7,
                    response_mime_type="application/json"
                )
            )
            
            # Parse response
            refined_data = json.loads(response.text)
            
            # Convert to Ontology object
            entity_types = [EntityType(**et) for et in refined_data["entity_types"]]
            relation_types = [RelationType(**rt) for rt in refined_data["relation_types"]]
            
            return Ontology(
                domain=refined_data["domain"],
                description=refined_data["description"],
                entity_types=entity_types,
                relation_types=relation_types,
                version=current_ontology.version,
                created_at=current_ontology.created_at,
                modified_at=datetime.now().isoformat()
            )
            
        except Exception as e:
            print(f"Error refining ontology: {e}")
            current_ontology.modified_at = datetime.now().isoformat()
            return current_ontology
    
    def extract_entities(self, text: str, ontology: Ontology) -> List[Dict[str, Any]]:
        """Extract entities from text using the ontology"""
        if not self.model:
            # Return mock extractions
            return self._mock_entity_extraction()
        
        try:
            # Prepare prompt
            ontology_summary = {
                "entity_types": [
                    {"name": et.name, "description": et.description, "attributes": et.attributes}
                    for et in ontology.entity_types
                ]
            }
            
            prompt = self.prompts["extract_entities"].format(
                ontology=json.dumps(ontology_summary, indent=2),
                text=text[:2000]  # Limit text length
            )
            
            # Generate with Gemini
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.3,
                    response_mime_type="application/json"
                )
            )
            
            # Parse response
            result = json.loads(response.text)
            return result.get("entities", [])
            
        except Exception as e:
            print(f"Error extracting entities: {e}")
            return self._mock_entity_extraction()
    
    def validate_with_text(self, ontology: Ontology, sample_text: str) -> Dict[str, Any]:
        """Validate ontology completeness using sample text"""
        # Extract entities
        entities = self.extract_entities(sample_text, ontology)
        
        # Analyze coverage
        entity_types_found = set(e["type"] for e in entities)
        coverage = len(entity_types_found) / len(ontology.entity_types) if ontology.entity_types else 0
        
        # Generate suggestions
        suggestions = []
        if coverage < 0.5:
            suggestions.append("Low coverage - consider adding more specific entity types")
        
        # Look for patterns in unmatched text (mock for now)
        suggestions.extend([
            "Consider adding temporal entities for date/time references",
            "Relationship types could be expanded for better connectivity"
        ])
        
        return {
            "entities_found": len(entities),
            "relations_found": len(entities) // 2,  # Mock relation count
            "coverage": coverage,
            "entity_types_used": list(entity_types_found),
            "suggestions": suggestions[:3]  # Limit suggestions
        }
    
    def _generate_mock_ontology(self, domain_description: str) -> Ontology:
        """Generate a mock ontology for testing without API"""
        # Detect domain from description
        domain_lower = domain_description.lower()
        
        if "climate" in domain_lower:
            return self._mock_climate_ontology()
        elif "medical" in domain_lower or "health" in domain_lower:
            return self._mock_medical_ontology()
        else:
            return self._mock_generic_ontology(domain_description)
    
    def _mock_climate_ontology(self) -> Ontology:
        """Mock climate policy ontology"""
        return Ontology(
            domain="Climate Policy Analysis",
            description="Ontology for analyzing climate change policies and their impacts",
            entity_types=[
                EntityType(
                    name="CLIMATE_POLICY",
                    description="Government or organizational policies addressing climate change",
                    attributes=["policy_name", "jurisdiction", "implementation_date", "target_year"],
                    examples=["Paris Agreement", "EU Green Deal", "Carbon Tax Policy"]
                ),
                EntityType(
                    name="EMISSION_TARGET",
                    description="Specific emission reduction targets",
                    attributes=["target_value", "baseline_year", "target_year", "measurement_unit"],
                    examples=["Net-zero by 2050", "50% reduction by 2030", "Carbon neutral by 2040"]
                ),
                EntityType(
                    name="POLICY_INSTRUMENT",
                    description="Specific tools or mechanisms used to implement climate policies",
                    attributes=["instrument_type", "scope", "enforcement_mechanism"],
                    examples=["Carbon pricing", "Renewable energy subsidies", "Emission trading system"]
                ),
                EntityType(
                    name="STAKEHOLDER",
                    description="Organizations or groups involved in climate policy",
                    attributes=["name", "type", "role", "influence_level"],
                    examples=["Environmental Protection Agency", "Greenpeace", "Oil Industry Association"]
                )
            ],
            relation_types=[
                RelationType(
                    name="IMPLEMENTS",
                    description="Stakeholder implements or enforces a climate policy",
                    source_types=["STAKEHOLDER"],
                    target_types=["CLIMATE_POLICY"],
                    examples=["EPA implements Clean Air Act", "EU Commission implements Green Deal"]
                ),
                RelationType(
                    name="TARGETS",
                    description="Policy aims to achieve specific emission targets",
                    source_types=["CLIMATE_POLICY"],
                    target_types=["EMISSION_TARGET"],
                    examples=["Paris Agreement targets 1.5°C warming limit"]
                ),
                RelationType(
                    name="USES_INSTRUMENT",
                    description="Policy employs specific policy instruments",
                    source_types=["CLIMATE_POLICY"],
                    target_types=["POLICY_INSTRUMENT"],
                    examples=["EU ETS uses carbon trading", "Carbon tax policy uses pricing mechanism"]
                )
            ],
            created_at=datetime.now().isoformat()
        )
    
    def _mock_medical_ontology(self) -> Ontology:
        """Mock medical/healthcare ontology"""
        return Ontology(
            domain="Clinical Research",
            description="Ontology for clinical trials and medical research",
            entity_types=[
                EntityType(
                    name="CLINICAL_TRIAL",
                    description="Formal study of medical interventions",
                    attributes=["trial_id", "phase", "status", "start_date", "end_date"],
                    examples=["NCT04280705", "RECOVERY Trial", "Phase III Vaccine Study"]
                ),
                EntityType(
                    name="MEDICAL_CONDITION",
                    description="Disease or health condition being studied",
                    attributes=["condition_name", "icd_code", "severity", "prevalence"],
                    examples=["COVID-19", "Type 2 Diabetes", "Alzheimer's Disease"]
                ),
                EntityType(
                    name="INTERVENTION",
                    description="Treatment or procedure being tested",
                    attributes=["intervention_type", "dosage", "administration_route", "duration"],
                    examples=["Remdesivir 200mg IV", "mRNA Vaccine", "Behavioral Therapy"]
                ),
                EntityType(
                    name="RESEARCH_SITE",
                    description="Location where research is conducted",
                    attributes=["site_name", "location", "principal_investigator", "capacity"],
                    examples=["Johns Hopkins Hospital", "Mayo Clinic", "UCLA Medical Center"]
                )
            ],
            relation_types=[
                RelationType(
                    name="STUDIES",
                    description="Clinical trial studies a medical condition",
                    source_types=["CLINICAL_TRIAL"],
                    target_types=["MEDICAL_CONDITION"],
                    examples=["RECOVERY Trial studies COVID-19"]
                ),
                RelationType(
                    name="TESTS",
                    description="Clinical trial tests an intervention",
                    source_types=["CLINICAL_TRIAL"],
                    target_types=["INTERVENTION"],
                    examples=["NCT04280705 tests Remdesivir"]
                ),
                RelationType(
                    name="CONDUCTED_AT",
                    description="Clinical trial is conducted at research site",
                    source_types=["CLINICAL_TRIAL"],
                    target_types=["RESEARCH_SITE"],
                    examples=["Phase III trial conducted at Mayo Clinic"]
                )
            ],
            created_at=datetime.now().isoformat()
        )
    
    def _mock_generic_ontology(self, domain_description: str) -> Ontology:
        """Generic ontology for any domain"""
        domain_name = domain_description.split('.')[0][:50]  # First sentence, max 50 chars
        
        return Ontology(
            domain=domain_name,
            description=domain_description[:200],
            entity_types=[
                EntityType(
                    name="PRIMARY_ENTITY",
                    description="Main entity type in this domain",
                    attributes=["identifier", "name", "description", "status"],
                    examples=["Example 1", "Example 2", "Example 3"]
                ),
                EntityType(
                    name="SECONDARY_ENTITY",
                    description="Supporting entity type",
                    attributes=["identifier", "type", "properties"],
                    examples=["Support 1", "Support 2"]
                )
            ],
            relation_types=[
                RelationType(
                    name="RELATES_TO",
                    description="Generic relationship between entities",
                    source_types=["PRIMARY_ENTITY"],
                    target_types=["SECONDARY_ENTITY"],
                    examples=["Entity A relates to Entity B"]
                )
            ],
            created_at=datetime.now().isoformat()
        )
    
    def _mock_entity_extraction(self) -> List[Dict[str, Any]]:
        """Mock entity extraction results"""
        return [
            {
                "text": "Paris Agreement",
                "type": "CLIMATE_POLICY",
                "confidence": 0.95,
                "attributes": {"policy_name": "Paris Agreement", "jurisdiction": "International"}
            },
            {
                "text": "net-zero by 2050",
                "type": "EMISSION_TARGET",
                "confidence": 0.88,
                "attributes": {"target_value": "net-zero", "target_year": "2050"}
            },
            {
                "text": "carbon pricing",
                "type": "POLICY_INSTRUMENT",
                "confidence": 0.82,
                "attributes": {"instrument_type": "economic"}
            }
        ]

# Convenience functions for direct use
def generate_ontology_from_description(
    domain_description: str,
    config: Optional[Dict[str, Any]] = None
) -> Ontology:
    """Generate an ontology from a domain description"""
    if config is None:
        config = {
            "temperature": 0.7,
            "max_entities": 20,
            "max_relations": 15,
            "include_hierarchies": True,
            "auto_suggest_attributes": True
        }
    
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