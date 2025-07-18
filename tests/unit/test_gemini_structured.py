#!/usr/bin/env python3
"""
Demonstration of Gemini 2.5 Flash with structured output for graph extraction.
IMPORTANT: Using gemini-2.5-flash (NOT gemini-1.5-flash or any other version)
"""

import os
from typing import List, Optional
from pydantic import BaseModel, Field
from google import genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Entity and Relationship models for structured output
class Entity(BaseModel):
    """Represents an entity extracted from text"""
    name: str = Field(description="The entity name as it appears in text")
    canonical_name: str = Field(description="Normalized/canonical form of the name")
    entity_type: str = Field(description="Type: PERSON, ORG, GPE, DATE, MONEY, etc.")
    confidence: float = Field(description="Confidence score 0.0-1.0", ge=0.0, le=1.0)
    surface_forms: List[str] = Field(description="All variations of this entity found")
    context: str = Field(description="Brief context where entity was found")

class Relationship(BaseModel):
    """Represents a relationship between entities"""
    subject_name: str = Field(description="Subject entity name")
    subject_type: str = Field(description="Subject entity type")
    predicate: str = Field(description="Relationship type (e.g., FOUNDED, LOCATED_IN, WORKS_FOR)")
    object_name: str = Field(description="Object entity name")
    object_type: str = Field(description="Object entity type")
    confidence: float = Field(description="Confidence score 0.0-1.0", ge=0.0, le=1.0)
    evidence: str = Field(description="Text snippet supporting this relationship")

class GraphExtraction(BaseModel):
    """Complete graph extraction from text"""
    entities: List[Entity]
    relationships: List[Relationship]
    summary: str = Field(description="Brief summary of extracted graph")

def extract_graph_with_gemini(text: str) -> GraphExtraction:
    """Extract entities and relationships using Gemini 2.5 Flash with structured output"""
    
    # Initialize Gemini client
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    
    # Create prompt for graph extraction
    prompt = f"""Extract all entities and relationships from the following text to build a knowledge graph.

Instructions:
1. Identify ALL named entities (people, organizations, locations, dates, money amounts, etc.)
2. For each entity, provide all surface forms found in the text
3. Extract relationships between entities with evidence from the text
4. Normalize entity names (e.g., "MIT" and "Massachusetts Institute of Technology" should have same canonical_name)
5. Use standard relationship types: FOUNDED, LOCATED_IN, WORKS_FOR, AFFILIATED_WITH, CREATED, OWNS, etc.

Text to analyze:
{text}

Extract entities and relationships following the schema."""

    try:
        # Generate with structured output
        response = client.models.generate_content(
            model="gemini-2.5-flash",  # IMPORTANT: Using 2.5 Flash as specified
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": GraphExtraction,
                "temperature": 0.1,  # Low temperature for consistency
                "max_output_tokens": 8192
            }
        )
        
        # Parse the structured response
        graph_data = response.parsed
        
        return graph_data
        
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return GraphExtraction(entities=[], relationships=[], summary="Extraction failed")

def demonstrate_extraction():
    """Demonstrate graph extraction with sample text"""
    
    # Sample text for testing
    test_text = """
    Dr. Sarah Johnson from MIT announced a breakthrough in quantum computing. 
    The Massachusetts Institute of Technology research team, led by Johnson, 
    has developed a new algorithm that could revolutionize cryptography.
    
    SolarTech Industries, based in Phoenix, Arizona, announced a $2 billion 
    investment in solar panel manufacturing. The company's CEO, Maria Rodriguez, 
    stated that they plan to double production capacity by 2025.
    
    MIT collaborated with Stanford University on this project, which was 
    funded by the National Science Foundation with a grant of $5 million.
    """
    
    print("🚀 Testing Gemini 2.5 Flash Structured Output for Graph Extraction\n")
    print(f"Input text ({len(test_text)} chars):")
    print("-" * 50)
    print(test_text.strip())
    print("-" * 50)
    
    # Extract graph
    print("\n📊 Extracting knowledge graph...")
    graph = extract_graph_with_gemini(test_text)
    
    # Display results
    print(f"\n✅ Extraction complete!")
    print(f"\n📌 Summary: {graph.summary}")
    
    print(f"\n🔵 Entities ({len(graph.entities)}):")
    for i, entity in enumerate(graph.entities, 1):
        print(f"\n{i}. {entity.name}")
        print(f"   - Canonical: {entity.canonical_name}")
        print(f"   - Type: {entity.entity_type}")
        print(f"   - Confidence: {entity.confidence:.2f}")
        print(f"   - Surface forms: {entity.surface_forms}")
        print(f"   - Context: {entity.context}")
    
    print(f"\n🔗 Relationships ({len(graph.relationships)}):")
    for i, rel in enumerate(graph.relationships, 1):
        print(f"\n{i}. {rel.subject_name} --[{rel.predicate}]--> {rel.object_name}")
        print(f"   - Subject type: {rel.subject_type}")
        print(f"   - Object type: {rel.object_type}")
        print(f"   - Confidence: {rel.confidence:.2f}")
        print(f"   - Evidence: {rel.evidence}")
    
    # Test entity resolution
    print("\n🔍 Testing Entity Resolution:")
    print("Checking if MIT and Massachusetts Institute of Technology are resolved...")
    mit_entities = [e for e in graph.entities if 'mit' in e.canonical_name.lower()]
    if len(mit_entities) == 1:
        print("✅ Successfully resolved to single entity!")
        print(f"   Canonical: {mit_entities[0].canonical_name}")
        print(f"   Surface forms: {mit_entities[0].surface_forms}")
    else:
        print(f"⚠️  Found {len(mit_entities)} MIT-related entities")

if __name__ == "__main__":
    # Verify API key is set
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ Error: GOOGLE_API_KEY not found in environment variables")
        print("Please ensure .env file exists with GOOGLE_API_KEY=your_key")
        exit(1)
    
    # Run demonstration
    demonstrate_extraction()
    
    print("\n✨ Gemini 2.5 Flash structured output demonstration complete!")
    print("Model used: gemini-2.5-flash (NOT 1.5 or any other version)")