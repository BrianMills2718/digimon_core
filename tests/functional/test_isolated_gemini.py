#!/usr/bin/env python3
"""Isolated test of Gemini ontology generation"""

import sys
import os

def test_gemini_direct():
    """Test Gemini directly with the modified prompt"""
    try:
        import google.generativeai as genai
        from dotenv import load_dotenv
        load_dotenv()
        
        # Initialize Gemini
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Use the exact modified prompt from the generator
        prompt = """Based on the following conversation about a domain, please help create a structured knowledge framework.

CONVERSATION:
User: Simple document analysis for testing

CONSTRAINTS:
- Maximum entity types: 8
- Maximum relationship types: 6

Please provide a structured knowledge framework in the following JSON format:
{
    "domain_name": "Short domain name",
    "domain_description": "One paragraph description of the domain",
    "entity_types": [
        {
            "name": "ENTITY_TYPE_NAME",
            "description": "What this entity represents",
            "examples": ["example1", "example2", "example3"],
            "attributes": ["key_attribute1", "key_attribute2"]
        }
    ],
    "relationship_types": [
        {
            "name": "RELATIONSHIP_NAME",
            "description": "What this relationship represents",
            "source_types": ["ENTITY_TYPE1"],
            "target_types": ["ENTITY_TYPE2"],
            "examples": ["Entity1 RELATIONSHIP Entity2"]
        }
    ],
    "identification_guidelines": [
        "Guideline 1 for identifying entities in text",
        "Guideline 2 for identifying relationships", 
        "Guideline 3 for handling ambiguity"
    ]
}

Important requirements:
1. Entity type names should be UPPERCASE_WITH_UNDERSCORES
2. Relationship names should be UPPERCASE_WITH_UNDERSCORES
3. Include 3-5 concrete examples for each type
4. Focus on domain-specific types, not generic ones
5. Relationships should connect specific entity types
6. Guidelines should be helpful for academic research

Please respond with the JSON format only."""
        
        print("🔍 Testing modified Gemini prompt directly...")
        
        # Safety settings
        safety_settings = {
            genai.types.HarmCategory.HARM_CATEGORY_HARASSMENT: genai.types.HarmBlockThreshold.BLOCK_NONE,
            genai.types.HarmCategory.HARM_CATEGORY_HATE_SPEECH: genai.types.HarmBlockThreshold.BLOCK_NONE,
            genai.types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: genai.types.HarmBlockThreshold.BLOCK_NONE,
            genai.types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: genai.types.HarmBlockThreshold.BLOCK_NONE,
        }
        
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                candidate_count=1,
                max_output_tokens=4000,
            ),
            safety_settings=safety_settings
        )
        
        print(f"✅ Response received!")
        print(f"   Has candidates: {bool(response.candidates)}")
        if response.candidates:
            candidate = response.candidates[0]
            print(f"   Finish reason: {candidate.finish_reason}")
            if candidate.finish_reason == 1:
                print("🎉 SUCCESS: Gemini generated response without safety filter block!")
                print(f"   Response length: {len(response.text)} characters")
                return True
            elif candidate.finish_reason == 2:
                print("❌ SAFETY FILTER STILL TRIGGERED")
                return False
            else:
                print(f"⚠️ Other finish reason: {candidate.finish_reason}")
                return False
        else:
            print("❌ No candidates returned")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🎯 ISOLATED GEMINI SAFETY FILTER TEST")
    print("=" * 50)
    
    success = test_gemini_direct()
    
    if success:
        print("\n✅ GEMINI SAFETY FILTER ISSUE IS RESOLVED!")
    else:
        print("\n❌ Gemini safety filter issue persists")
    
    sys.exit(0 if success else 1)