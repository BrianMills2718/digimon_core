#!/usr/bin/env python3
"""
Structured parameter extraction using OpenAI's response_format with JSON Schema.
This properly implements the text-schema concept.
"""

import json
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field
import logging
import litellm

logger = logging.getLogger(__name__)


# Text-Schema Models (what we extract from text)
class TextOutcome(BaseModel):
    """An outcome as described in text"""
    description: str = Field(description="Natural language description")
    linguistic_category: str = Field(description="Category from theory mappings")
    mapped_range: str = Field(description="Range from linguistic mappings")
    
    class Config:
        extra = "forbid"  # This sets additionalProperties: false
    
class TextProbability(BaseModel):
    """A probability as expressed in text"""
    description: str = Field(description="How probability is expressed")
    value: float = Field(ge=0, le=1, description="Numerical probability")
    
    class Config:
        extra = "forbid"

class TextProspect(BaseModel):
    """A decision alternative as described in text"""
    name: str = Field(description="Name of the alternative")
    full_description: str = Field(description="Complete text description")
    text_outcomes: List[TextOutcome] = Field(description="Outcomes mentioned")
    text_probabilities: List[TextProbability] = Field(description="Probabilities mentioned")
    reference_point_description: str = Field(description="How reference point is described")
    
    class Config:
        extra = "forbid"

class TextSchema(BaseModel):
    """Complete text-schema extraction"""
    theory_name: str
    extracted_prospects: List[TextProspect]
    extraction_notes: str = Field(description="Notes about extraction process")
    confidence: float = Field(ge=0, le=1, description="Extraction confidence")
    
    class Config:
        extra = "forbid"


# Parameter Models (resolved from text-schema)
class ResolvedParameters(BaseModel):
    """Final parameters ready for computation"""
    prospect_name: str
    outcomes: List[float]
    probabilities: List[float]
    reference_point: float
    
    class Config:
        extra = "forbid"


class StructuredParameterExtractor:
    """Extracts parameters using structured outputs"""
    
    def __init__(self, model: Optional[str] = None):
        # Get model from config
        if model is None:
            try:
                # Try to use standard config if available
                import sys
                import os
                parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                if parent_dir not in sys.path:
                    sys.path.insert(0, parent_dir)
                from core.standard_config import get_model
                self.model = get_model("structured_extractor")
            except ImportError:
                # Fallback to config file
                try:
                    config_path = os.path.join(os.path.dirname(__file__), '../../config/default.yaml')
                    with open(config_path, 'r') as f:
                        import yaml
                        config = yaml.safe_load(f)
                    self.model = config.get('llm', {}).get('default_model', 'gemini/gemini-2.0-flash-exp')
                except (FileNotFoundError, KeyError):
                    self.model = "gemini/gemini-2.0-flash-exp"
        else:
            self.model = model
    
    def extract_text_schema(self, text: str, theory_schema: Dict[str, Any]) -> TextSchema:
        """Extract text-schema using structured output"""
        
        # Get linguistic mappings from theory schema
        mappings = self._get_theory_mappings(theory_schema)
        
        # Build the extraction prompt
        prompt = f"""Extract decision alternatives and their attributes from this text:

{text}

Use these linguistic mappings from the theory:
Outcome Mappings: {json.dumps(mappings['outcomes'], indent=2)}
Probability Mappings: {json.dumps(mappings['probabilities'], indent=2)}

For each alternative:
1. Identify the name and full description
2. List all outcomes with their linguistic categories
3. Extract exact probabilities
4. Note how the reference point is described (use "current situation" if not explicitly mentioned)"""
        
        # Use structured output with JSON Schema
        response = litellm.completion(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You extract structured information about decision alternatives from text."
                },
                {"role": "user", "content": prompt}
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "text_schema_extraction",
                    "strict": True,
                    "schema": TextSchema.model_json_schema()
                }
            },
            temperature=0.2
        )
        
        # Parse the structured response
        extracted_json = json.loads(response.choices[0].message.content)
        return TextSchema(**extracted_json)
    
    def resolve_parameters(self, text_schema: TextSchema, 
                          resolution_strategy: str = "midpoint") -> List[ResolvedParameters]:
        """Resolve text-schema to computational parameters"""
        
        resolved = []
        
        for prospect in text_schema.extracted_prospects:
            # Resolve outcomes from ranges to values
            outcomes = []
            for outcome in prospect.text_outcomes:
                value = self._resolve_range(outcome.mapped_range, resolution_strategy)
                outcomes.append(value)
            
            # Probabilities are already resolved
            probabilities = [p.value for p in prospect.text_probabilities]
            
            # Validate probabilities sum to ~1
            prob_sum = sum(probabilities)
            if abs(prob_sum - 1.0) > 0.01:
                # Normalize if close
                if 0.9 <= prob_sum <= 1.1:
                    probabilities = [p/prob_sum for p in probabilities]
                else:
                    logger.warning(f"Probabilities sum to {prob_sum}, not 1.0")
            
            resolved.append(ResolvedParameters(
                prospect_name=prospect.name,
                outcomes=outcomes,
                probabilities=probabilities,
                reference_point=0  # Default, could be extracted
            ))
        
        return resolved
    
    def _get_theory_mappings(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Extract linguistic mappings from theory schema"""
        
        conversions = schema.get('ontology', {}).get(
            'mathematical_algorithms', {}
        ).get('text_to_numbers_conversion', {})
        
        return {
            'outcomes': conversions.get('outcome_scaling', {}).get('linguistic_mappings', {}),
            'probabilities': conversions.get('probability_estimation', {}).get('linguistic_mappings', {})
        }
    
    def _resolve_range(self, range_str: str, strategy: str = "midpoint") -> float:
        """Resolve a range string to a single value"""
        
        # Handle single numbers
        try:
            return float(range_str)
        except ValueError:
            pass
        
        # Parse range "X to Y"
        if " to " in range_str:
            parts = range_str.split(" to ")
            try:
                low = float(parts[0])
                high = float(parts[1])
                
                if strategy == "midpoint":
                    return (low + high) / 2
                elif strategy == "conservative":
                    return low if low > 0 else high  # Smaller gain, larger loss
                elif strategy == "optimistic":
                    return high if high > 0 else low  # Larger gain, smaller loss
                else:
                    return (low + high) / 2
                    
            except (ValueError, IndexError):
                logger.error(f"Could not parse range: {range_str}")
                return 0.0
        
        return 0.0


def demonstrate_structured_extraction():
    """Show the complete extraction pipeline"""
    
    # Example text
    text = """
    The company faces a strategic decision about market expansion.
    
    Option A: Launch aggressively with a 65% chance of capturing 
    significant market share and achieving major revenue growth. 
    However, there's a 35% risk of regulatory challenges leading 
    to substantial financial losses.
    
    Option B: Partner with local firms, which is virtually certain 
    (95% probability) to yield moderate returns, with only a 5% 
    chance of minor setbacks due to partnership disputes.
    """
    
    # Minimal theory schema for demo
    theory_schema = {
        "theory_name": "Prospect Theory",
        "ontology": {
            "mathematical_algorithms": {
                "text_to_numbers_conversion": {
                    "outcome_scaling": {
                        "linguistic_mappings": {
                            "major revenue growth": "60 to 80",
                            "significant market share": "50 to 70",
                            "substantial financial losses": "-60 to -80",
                            "moderate returns": "20 to 40",
                            "minor setbacks": "-5 to -15"
                        }
                    },
                    "probability_estimation": {
                        "linguistic_mappings": {
                            "virtually certain": "0.95",
                            "65% chance": "0.65",
                            "35% risk": "0.35",
                            "95% probability": "0.95",
                            "5% chance": "0.05"
                        }
                    }
                }
            }
        }
    }
    
    # Extract
    extractor = StructuredParameterExtractor()
    
    print("1. EXTRACTING TEXT-SCHEMA")
    print("=" * 60)
    
    try:
        # Step 1: Extract text-schema
        text_schema = extractor.extract_text_schema(text, theory_schema)
        
        print(f"Theory: {text_schema.theory_name}")
        print(f"Confidence: {text_schema.confidence:.0%}")
        print(f"\nExtracted Prospects:")
        
        for prospect in text_schema.extracted_prospects:
            print(f"\n{prospect.name}:")
            print(f"  Description: {prospect.full_description[:60]}...")
            print(f"  Outcomes:")
            for outcome in prospect.text_outcomes:
                print(f"    - {outcome.description}")
                print(f"      Category: {outcome.linguistic_category}")
                print(f"      Range: {outcome.mapped_range}")
            print(f"  Probabilities:")
            for prob in prospect.text_probabilities:
                print(f"    - {prob.description}: {prob.value}")
        
        # Step 2: Resolve to parameters
        print("\n2. RESOLVING TO PARAMETERS")
        print("=" * 60)
        
        resolved = extractor.resolve_parameters(text_schema)
        
        for params in resolved:
            print(f"\n{params.prospect_name}:")
            print(f"  Outcomes: {params.outcomes}")
            print(f"  Probabilities: {params.probabilities}")
            print(f"  Reference Point: {params.reference_point}")
        
        print("\n✅ Complete extraction pipeline demonstrated!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    demonstrate_structured_extraction()