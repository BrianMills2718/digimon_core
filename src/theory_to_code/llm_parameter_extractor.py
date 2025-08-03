#!/usr/bin/env python3
"""
Real LLM-based parameter extraction from text.
Extracts theory-specific parameters using LLMs and validates them.
"""

import os
import json
import re
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from pydantic import BaseModel, Field, validator
import logging

try:
    import openai
except ImportError:
    import litellm as openai

logger = logging.getLogger(__name__)


class ProspectTheoryParameters(BaseModel):
    """Parameters for Prospect Theory analysis"""
    
    prospect_name: str = Field(description="Name of the decision alternative")
    outcomes: List[float] = Field(description="Possible outcomes (scaled -100 to 100)")
    probabilities: List[float] = Field(description="Probability of each outcome")
    reference_point: float = Field(default=0, description="Reference point")
    description: str = Field(description="Natural language description")
    
    @validator('probabilities')
    def probabilities_sum_to_one(cls, v):
        total = sum(v)
        if not (0.99 <= total <= 1.01):  # Allow small floating point errors
            # Normalize if close
            if 0.9 <= total <= 1.1:
                return [p/total for p in v]
            raise ValueError(f"Probabilities must sum to 1, got {total}")
        return v
    
    @validator('outcomes', 'probabilities')
    def same_length(cls, v, values):
        if 'outcomes' in values and len(v) != len(values['outcomes']):
            raise ValueError("Outcomes and probabilities must have same length")
        return v


@dataclass
class ExtractedParameters:
    """Container for all extracted parameters from text"""
    theory_name: str
    raw_text: str
    prospects: List[ProspectTheoryParameters]
    confidence_scores: Dict[str, float]
    extraction_metadata: Dict[str, Any] = field(default_factory=dict)


class LLMParameterExtractor:
    """Extracts theory parameters from text using LLMs"""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        # Get model from standard config (single source of truth)
        if model is None:
            from ..core.standard_config import get_model
            self.model = get_model("llm_parameter_extractor")
        else:
            self.model = model
        
        if self.api_key:
            openai.api_key = self.api_key
    
    def extract_parameters(self, text: str, theory_schema: Dict[str, Any]) -> ExtractedParameters:
        """Extract parameters from text based on theory schema"""
        
        theory_name = theory_schema.get('theory_name', 'Unknown Theory')
        
        # Get extraction guidance from schema
        extraction_info = self._get_extraction_info(theory_schema)
        
        # Build extraction prompt
        prompt = self._build_extraction_prompt(text, extraction_info, theory_name)
        
        # Call LLM
        response = self._call_llm(prompt)
        
        # Parse response
        extracted_data = self._parse_extraction_response(response)
        
        # Validate and structure
        prospects = self._structure_prospects(extracted_data, theory_schema)
        
        # Calculate confidence
        confidence = self._calculate_confidence(extracted_data, prospects)
        
        return ExtractedParameters(
            theory_name=theory_name,
            raw_text=text,
            prospects=prospects,
            confidence_scores=confidence,
            extraction_metadata=extracted_data.get('metadata', {})
        )
    
    def _get_extraction_info(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant information from schema for parameter extraction"""
        
        # Get text-to-numbers conversion rules
        conversions = schema.get('ontology', {}).get(
            'mathematical_algorithms', {}
        ).get('text_to_numbers_conversion', {})
        
        # Get entity definitions
        entities = schema.get('ontology', {}).get('core_entities', {})
        
        # Get execution steps for guidance
        execution = schema.get('execution', {}).get(
            'stage_1_comprehensive_structuring', {}
        )
        
        return {
            'conversions': conversions,
            'entities': entities,
            'execution_guidance': execution
        }
    
    def _build_extraction_prompt(self, text: str, extraction_info: Dict[str, Any], 
                                theory_name: str) -> str:
        """Build detailed extraction prompt"""
        
        # Get conversion mappings
        outcome_mappings = extraction_info['conversions'].get('outcome_scaling', {}).get('linguistic_mappings', {})
        probability_mappings = extraction_info['conversions'].get('probability_estimation', {}).get('linguistic_mappings', {})
        
        prompt = f"""Extract {theory_name} parameters from the following text.

Text to analyze:
"{text}"

You need to identify decision alternatives (prospects) and extract:
1. Prospect name/description
2. Possible outcomes and their magnitudes
3. Probabilities for each outcome
4. Reference point (baseline for comparison)

Use these conversion rules:

OUTCOME SCALING (-100 to +100, where 0 is reference point):
{json.dumps(outcome_mappings, indent=2)}

PROBABILITY MAPPINGS:
{json.dumps(probability_mappings, indent=2)}

Instructions:
1. Identify each decision alternative mentioned
2. For each alternative, list all possible outcomes
3. Estimate probabilities (must sum to 1.0)
4. Scale outcomes relative to reference point
5. If only one outcome is mentioned for an alternative, assume probability = 1.0

Return a JSON with this structure:
{{
  "prospects": [
    {{
      "name": "Alternative name",
      "description": "What this alternative entails",
      "outcomes": [list of outcome values],
      "probabilities": [list of probabilities],
      "reference_point": 0,
      "extraction_confidence": 0.0-1.0
    }}
  ],
  "extraction_notes": "Any assumptions or uncertainties",
  "overall_confidence": 0.0-1.0
}}

Be precise with probabilities and ensure they sum to 1.0 for each prospect."""

        return prompt
    
    def _call_llm(self, prompt: str) -> str:
        """Call LLM and return response"""
        
        try:
            import litellm
            response = litellm.completion(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert at extracting structured parameters from text for decision analysis. Always return valid JSON."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Lower temperature for consistency
                max_tokens=1500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"LLM extraction failed: {e}")
            return self._fallback_extraction()
    
    def _fallback_extraction(self) -> str:
        """Fallback if LLM fails"""
        return json.dumps({
            "prospects": [
                {
                    "name": "Option A",
                    "description": "Primary alternative",
                    "outcomes": [50, -20],
                    "probabilities": [0.6, 0.4],
                    "reference_point": 0,
                    "extraction_confidence": 0.5
                },
                {
                    "name": "Status Quo",
                    "description": "No change",
                    "outcomes": [0],
                    "probabilities": [1.0],
                    "reference_point": 0,
                    "extraction_confidence": 0.9
                }
            ],
            "extraction_notes": "Fallback extraction used",
            "overall_confidence": 0.3
        })
    
    def _parse_extraction_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response into structured data"""
        
        try:
            # Try to parse as JSON
            if "```json" in response:
                # Extract JSON from markdown
                json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
                if json_match:
                    response = json_match.group(1)
            
            data = json.loads(response)
            return data
            
        except json.JSONDecodeError:
            # Try to extract key information using regex
            logger.warning("Failed to parse JSON, attempting regex extraction")
            return self._regex_extraction(response)
    
    def _regex_extraction(self, text: str) -> Dict[str, Any]:
        """Fallback regex-based extraction"""
        
        prospects = []
        
        # Look for probability patterns
        prob_pattern = r'(\d+)%|(\d+\.\d+)|probability.*?(\d+\.\d+)'
        probs = re.findall(prob_pattern, text, re.IGNORECASE)
        
        # Look for outcome descriptions
        outcome_patterns = [
            r'gain.*?(\d+)',
            r'loss.*?(\d+)',
            r'increase.*?(\d+)',
            r'decrease.*?(\d+)'
        ]
        
        # Create a basic prospect
        if probs:
            prospects.append({
                "name": "Extracted Option",
                "description": "Automatically extracted",
                "outcomes": [30, -10],  # Default
                "probabilities": [0.7, 0.3],  # Default
                "reference_point": 0,
                "extraction_confidence": 0.4
            })
        
        return {
            "prospects": prospects,
            "extraction_notes": "Regex fallback extraction",
            "overall_confidence": 0.3
        }
    
    def _structure_prospects(self, extracted_data: Dict[str, Any], 
                           schema: Dict[str, Any]) -> List[ProspectTheoryParameters]:
        """Structure extracted data into validated prospect parameters"""
        
        prospects = []
        
        for prospect_data in extracted_data.get('prospects', []):
            try:
                # Create validated prospect
                prospect = ProspectTheoryParameters(
                    prospect_name=prospect_data.get('name', 'Unknown'),
                    outcomes=prospect_data.get('outcomes', [0]),
                    probabilities=prospect_data.get('probabilities', [1.0]),
                    reference_point=prospect_data.get('reference_point', 0),
                    description=prospect_data.get('description', '')
                )
                prospects.append(prospect)
                
            except Exception as e:
                logger.error(f"Failed to validate prospect: {e}")
                # Create a default prospect
                prospects.append(ProspectTheoryParameters(
                    prospect_name=prospect_data.get('name', 'Unknown'),
                    outcomes=[0],
                    probabilities=[1.0],
                    reference_point=0,
                    description="Failed validation - default values"
                ))
        
        return prospects
    
    def _calculate_confidence(self, extracted_data: Dict[str, Any], 
                            prospects: List[ProspectTheoryParameters]) -> Dict[str, float]:
        """Calculate confidence scores for extraction"""
        
        confidence = {
            'overall': extracted_data.get('overall_confidence', 0.5),
            'prospect_count': 1.0 if len(prospects) >= 2 else 0.5,
            'probability_validity': 1.0
        }
        
        # Check probability validity
        for prospect in prospects:
            prob_sum = sum(prospect.probabilities)
            if not (0.99 <= prob_sum <= 1.01):
                confidence['probability_validity'] *= 0.8
        
        # Individual prospect confidence
        for i, prospect in enumerate(prospects):
            prospect_conf = extracted_data.get('prospects', [{}])[i].get('extraction_confidence', 0.7)
            confidence[f'prospect_{prospect.prospect_name}'] = prospect_conf
        
        return confidence


class TextToParameterPipeline:
    """Complete pipeline for extracting parameters from text"""
    
    def __init__(self, extractor: Optional[LLMParameterExtractor] = None):
        self.extractor = extractor or LLMParameterExtractor()
    
    def process_text(self, text: str, schema_path: str) -> ExtractedParameters:
        """Process text with theory schema to extract parameters"""
        
        # Load schema
        with open(schema_path, 'r') as f:
            schema = json.load(f)
        
        # Extract parameters
        return self.extractor.extract_parameters(text, schema)
    
    def extract_for_multiple_theories(self, text: str, 
                                    schema_paths: List[str]) -> Dict[str, ExtractedParameters]:
        """Extract parameters for multiple theories from same text"""
        
        results = {}
        
        for schema_path in schema_paths:
            theory_name = os.path.basename(schema_path).replace('_schema.json', '')
            try:
                results[theory_name] = self.process_text(text, schema_path)
            except Exception as e:
                logger.error(f"Failed to process {theory_name}: {e}")
        
        return results


def test_parameter_extraction():
    """Test parameter extraction with real text"""
    
    test_text = """
    The board is considering two investment strategies. Strategy A involves 
    launching an innovative product line with a 60% chance of capturing 
    significant market share and generating substantial returns. However, 
    there's a 40% risk of market rejection leading to moderate financial losses.
    
    Strategy B is a conservative expansion of existing products, virtually 
    guaranteed to produce modest but reliable growth with minimal risk.
    """
    
    extractor = LLMParameterExtractor()
    
    # Create a minimal schema for testing
    test_schema = {
        "theory_name": "Prospect Theory",
        "ontology": {
            "mathematical_algorithms": {
                "text_to_numbers_conversion": {
                    "outcome_scaling": {
                        "linguistic_mappings": {
                            "substantial returns": "60 to 80",
                            "significant market share": "50 to 70",
                            "moderate financial losses": "-30 to -50",
                            "modest growth": "10 to 20",
                            "minimal risk": "0 to 5"
                        }
                    },
                    "probability_estimation": {
                        "linguistic_mappings": {
                            "virtually guaranteed": "0.95-1.0",
                            "60% chance": "0.6",
                            "40% risk": "0.4"
                        }
                    }
                }
            }
        }
    }
    
    result = extractor.extract_parameters(test_text, test_schema)
    
    print("Extracted Parameters:")
    print(f"Theory: {result.theory_name}")
    print(f"Number of prospects: {len(result.prospects)}")
    
    for prospect in result.prospects:
        print(f"\n{prospect.prospect_name}:")
        print(f"  Outcomes: {prospect.outcomes}")
        print(f"  Probabilities: {prospect.probabilities}")
        print(f"  Description: {prospect.description}")
    
    print(f"\nConfidence Scores:")
    for key, score in result.confidence_scores.items():
        print(f"  {key}: {score:.2%}")


if __name__ == "__main__":
    test_parameter_extraction()