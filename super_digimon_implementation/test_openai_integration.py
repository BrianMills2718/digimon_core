#!/usr/bin/env python
"""Test OpenAI integration specifically."""

import os
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI

# Test OpenAI connection
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("❌ OPENAI_API_KEY not found in environment")
    exit(1)

print(f"✓ API Key found: {api_key[:20]}...")

try:
    client = OpenAI(api_key=api_key)
    
    # Test with a simple query
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What company created GPT-4? Answer in one sentence."}
        ],
        max_tokens=50
    )
    
    answer = response.choices[0].message.content
    print(f"\n✓ OpenAI Response: {answer}")
    
    # Test with graph context
    context = """
    Entities found in the knowledge graph:
    - OpenAI (ORG)
    - GPT-4 (PRODUCT)
    - Anthropic (ORG)
    - Claude (PRODUCT)
    
    Text excerpts:
    - "OpenAI created GPT-4, their most advanced language model."
    - "Anthropic built Claude as an AI assistant."
    """
    
    response2 = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a GraphRAG assistant analyzing knowledge graph data."},
            {"role": "user", "content": f"Based on this context:\n{context}\n\nQuestion: What company created GPT-4?"}
        ],
        max_tokens=100
    )
    
    print(f"\n✓ GraphRAG Response: {response2.choices[0].message.content}")
    
except Exception as e:
    print(f"\n❌ OpenAI Error: {e}")
    print("\nPossible issues:")
    print("- Invalid API key")
    print("- Network connection")
    print("- Rate limiting")
    print("- Account issues")