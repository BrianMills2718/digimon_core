#!/usr/bin/env python
"""Test embeddings generation."""

print("Testing embeddings...")

# Test sentence transformers
print("1. Loading sentence transformer model...")
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")
print("✓ Model loaded")

# Test embedding
print("2. Generating test embedding...")
test_text = ["This is a test sentence."]
embedding = model.encode(test_text)
print(f"✓ Generated embedding with shape: {embedding.shape}")

print("\n✅ Embedding test completed!")