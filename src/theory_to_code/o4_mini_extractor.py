#!/usr/bin/env python3
"""
Parameter extractor optimized for o4-mini
"""

import json
from typing import Dict, Any, List
from pydantic import BaseModel, Field
import logging
import litellm

from .structured_extractor import (
    TextOutcome, TextProbability, TextProspect, TextSchema, 
    ResolvedParameters, StructuredParameterExtractor
)

logger = logging.getLogger(__name__)


class O4MiniExtractor(StructuredParameterExtractor):
    """Parameter extractor optimized for o4-mini model"""
    
    def __init__(self, model: str = "o4-mini"):
        # O4-mini requires temperature=1
        self.model = model
    
    def extract_text_schema(self, text: str, theory_schema: Dict[str, Any]) -> TextSchema:
        """Extract text-schema using o4-mini with proper parameters"""
        
        # Get linguistic mappings from theory schema
        mappings = self._get_theory_mappings(theory_schema)
        
        # Build the extraction prompt
        prompt = f"""Extract decision alternatives and their attributes from this text:

    def _get_default_model(self) -> str:
        """Get default model from standard config"""
        return get_model()

{text}

Use these linguistic mappings from the theory:
Outcome Mappings: {json.dumps(mappings['outcomes'], indent=2)}
Probability Mappings: {json.dumps(mappings['probabilities'], indent=2)}

For each alternative:
1. Identify the name and full description
2. List all outcomes with their linguistic categories
3. Extract exact probabilities
4. Note how the reference point is described (use "current situation" if not explicitly mentioned)"""
        
        # Use structured output with JSON Schema - o4-mini requires temperature=1
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
            temperature=1  # Required for o4-mini
        )
        
        # Parse the structured response
        extracted_json = json.loads(response.choices[0].message.content)
        return TextSchema(**extracted_json)


def test_o4_mini_extractor():
    """Test the o4-mini specific extractor"""
    
    print("TESTING O4-MINI EXTRACTOR")
    print("=" * 50)
    
    # Test text
    test_text = """
    The board must decide between two strategies:
    
    Strategy Alpha: High-risk approach with 65% chance of major returns
    but 35% probability of significant losses.
    
    Strategy Beta: Low-risk method that's almost certain (90%) to yield
    moderate profits with only 10% chance of minor losses.
    """
    
    # Load theory schema
    from ..core.standard_config import get_file_path
    schema_path = f"{get_file_path('config_dir')}/schemas/prospect_theory_schema.json"
    with open(schema_path, "r") as f:
        theory_schema = json.load(f)
    
    try:
        # Create o4-mini extractor
        extractor = O4MiniExtractor()
        
        print("Extracting with o4-mini...")
        text_schema = extractor.extract_text_schema(test_text, theory_schema)
        
        print(f"✓ SUCCESS")
        print(f"  Theory: {text_schema.theory_name}")
        print(f"  Confidence: {text_schema.confidence:.0%}")
        print(f"  Prospects: {len(text_schema.extracted_prospects)}")
        
        # Resolve parameters
        resolved_params = extractor.resolve_parameters(text_schema)
        
        print(f"\nResolved Parameters:")
        for params in resolved_params:
            print(f"  {params.prospect_name}:")
            print(f"    Outcomes: {params.outcomes}")
            print(f"    Probabilities: {params.probabilities}")
        
        # Compare with baseline
        print(f"\nComparing with GPT-4o baseline...")
        baseline_extractor = StructuredParameterExtractor(model = self._get_default_model())
        baseline_schema = baseline_extractor.extract_text_schema(test_text, theory_schema)
        
        print(f"  Baseline confidence: {baseline_schema.confidence:.0%}")
        print(f"  O4-mini confidence: {text_schema.confidence:.0%}")
        
        confidence_diff = text_schema.confidence - baseline_schema.confidence
        if confidence_diff > 0:
            print(f"  O4-mini is {confidence_diff:.0%} more confident")
        else:
            print(f"  Baseline is {abs(confidence_diff):.0%} more confident")
            
    except Exception as e:
        print(f"✗ FAILED: {e}")


if __name__ == "__main__":
    test_o4_mini_extractor()