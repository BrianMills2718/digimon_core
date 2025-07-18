#!/usr/bin/env python3
"""
Demonstration of OpenAI text-embedding-3-small for semantic search and entity matching.
IMPORTANT: Using text-embedding-3-small (NOT ada-002 or any other model)
"""

import os
import numpy as np
from typing import List, Dict, Tuple
from openai import OpenAI
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

class EmbeddingDemo:
    """Demonstrates OpenAI embeddings for entity resolution and semantic search"""
    
    def __init__(self):
        """Initialize OpenAI client"""
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "text-embedding-3-small"  # IMPORTANT: Using 3-small as specified
        
    def get_embedding(self, text: str) -> List[float]:
        """Get embedding for a single text"""
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error getting embedding: {e}")
            return []
    
    def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for multiple texts in a batch"""
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=texts
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            print(f"Error getting batch embeddings: {e}")
            return []
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def find_similar_entities(self, query: str, entity_list: List[Dict[str, str]], threshold: float = 0.8) -> List[Tuple[str, float]]:
        """Find entities similar to query using embeddings"""
        
        # Get query embedding
        query_embedding = self.get_embedding(query)
        if not query_embedding:
            return []
        
        # Get embeddings for all entities
        entity_texts = [f"{e['name']} ({e['type']})" for e in entity_list]
        entity_embeddings = self.get_embeddings_batch(entity_texts)
        
        # Calculate similarities
        similar_entities = []
        for i, (entity, embedding) in enumerate(zip(entity_list, entity_embeddings)):
            if embedding:
                similarity = self.cosine_similarity(query_embedding, embedding)
                if similarity >= threshold:
                    similar_entities.append((entity['name'], similarity))
        
        # Sort by similarity
        similar_entities.sort(key=lambda x: x[1], reverse=True)
        return similar_entities
    
    def resolve_entity_aliases(self, entities: List[str]) -> Dict[str, List[str]]:
        """Group entities that likely refer to the same thing"""
        
        if not entities:
            return {}
        
        # Get embeddings for all entities
        embeddings = self.get_embeddings_batch(entities)
        if not embeddings:
            return {}
        
        # Group similar entities
        groups = {}
        used = set()
        
        for i, entity1 in enumerate(entities):
            if entity1 in used:
                continue
                
            # Start new group
            group = [entity1]
            used.add(entity1)
            
            # Find similar entities
            for j, entity2 in enumerate(entities):
                if i != j and entity2 not in used:
                    similarity = self.cosine_similarity(embeddings[i], embeddings[j])
                    if similarity >= 0.85:  # High threshold for entity resolution
                        group.append(entity2)
                        used.add(entity2)
            
            # Use shortest name as canonical
            canonical = min(group, key=len)
            groups[canonical] = group
        
        return groups

def demonstrate_embeddings():
    """Demonstrate various embedding use cases"""
    
    demo = EmbeddingDemo()
    
    print("🚀 Testing OpenAI text-embedding-3-small\n")
    
    # Test 1: Basic embedding
    print("📊 Test 1: Basic Embedding")
    test_text = "Massachusetts Institute of Technology"
    embedding = demo.get_embedding(test_text)
    print(f"Text: '{test_text}'")
    print(f"Embedding dimensions: {len(embedding)}")
    print(f"First 10 values: {embedding[:10]}")
    
    # Test 2: Entity resolution
    print("\n🔍 Test 2: Entity Resolution")
    entities_to_resolve = [
        "MIT",
        "Massachusetts Institute of Technology",
        "M.I.T.",
        "Mass. Inst. of Tech.",
        "Stanford University",
        "Stanford",
        "Stanford U.",
        "IBM",
        "International Business Machines",
        "I.B.M."
    ]
    
    print("Entities to resolve:")
    for e in entities_to_resolve:
        print(f"  - {e}")
    
    groups = demo.resolve_entity_aliases(entities_to_resolve)
    
    print("\nResolved entity groups:")
    for canonical, aliases in groups.items():
        print(f"\n✅ Canonical: {canonical}")
        print(f"   Aliases: {', '.join(aliases)}")
    
    # Test 3: Semantic search
    print("\n🔎 Test 3: Semantic Search for Entities")
    
    # Sample entity database
    entity_database = [
        {"name": "SolarTech Industries", "type": "ORG"},
        {"name": "WindPower Global", "type": "ORG"},
        {"name": "Dr. Sarah Johnson", "type": "PERSON"},
        {"name": "Phoenix, Arizona", "type": "GPE"},
        {"name": "renewable energy company", "type": "ORG"},
        {"name": "solar panel manufacturer", "type": "ORG"},
        {"name": "National Science Foundation", "type": "ORG"},
        {"name": "$2 billion", "type": "MONEY"},
        {"name": "March 2023", "type": "DATE"}
    ]
    
    queries = [
        "companies working on solar energy",
        "organizations in renewable sector",
        "scientists and researchers",
        "funding amounts"
    ]
    
    for query in queries:
        print(f"\n🔍 Query: '{query}'")
        similar = demo.find_similar_entities(query, entity_database, threshold=0.7)
        if similar:
            for entity, score in similar[:3]:  # Top 3
                print(f"   - {entity} (similarity: {score:.3f})")
        else:
            print("   No similar entities found")
    
    # Test 4: Relationship extraction assistance
    print("\n🔗 Test 4: Relationship Context Matching")
    
    relationship_patterns = [
        "founded by",
        "located in",
        "works for",
        "invested in",
        "collaborated with",
        "subsidiary of"
    ]
    
    test_sentence = "The company is based in Phoenix and has received funding from investors"
    
    print(f"\nSentence: '{test_sentence}'")
    print("Checking for relationship patterns...")
    
    sentence_embedding = demo.get_embedding(test_sentence)
    pattern_embeddings = demo.get_embeddings_batch(relationship_patterns)
    
    for pattern, pattern_embedding in zip(relationship_patterns, pattern_embeddings):
        if pattern_embedding:
            similarity = demo.cosine_similarity(sentence_embedding, pattern_embedding)
            if similarity > 0.5:
                print(f"   ✓ '{pattern}' relevance: {similarity:.3f}")

if __name__ == "__main__":
    # Verify API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found in environment variables")
        print("Please ensure .env file exists with OPENAI_API_KEY=your_key")
        exit(1)
    
    # Run demonstration
    demonstrate_embeddings()
    
    print("\n✨ OpenAI text-embedding-3-small demonstration complete!")
    print("Model used: text-embedding-3-small (NOT ada-002 or older models)")
    print(f"Embedding dimensions: 1536 (standard for this model)")