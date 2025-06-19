#!/usr/bin/env python
"""Test LLM extractor initialization."""

import os
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

print("=== TESTING LLM INITIALIZATION ===\n")

# Check API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("ERROR: OPENAI_API_KEY not found")
    sys.exit(1)
else:
    print(f"✓ API key found: {api_key[:10]}...")

# Try to import and initialize
print("\nImporting LLM extractor...")
start = time.time()
try:
    from src.tools.phase2.t23b_llm_extractor import LLMExtractor
    print(f"✓ Import successful ({time.time() - start:.2f}s)")
except Exception as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)

# Initialize database
print("\nInitializing database...")
start = time.time()
from src.utils.database import DatabaseManager
db = DatabaseManager()
db.faiss.dimension = 384
db.initialize()
print(f"✓ Database initialized ({time.time() - start:.2f}s)")

# Create LLM extractor
print("\nCreating LLM extractor...")
start = time.time()
try:
    llm_extractor = LLMExtractor(db)
    print(f"✓ LLM extractor created ({time.time() - start:.2f}s)")
except Exception as e:
    print(f"✗ Failed to create LLM extractor: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test OpenAI client directly
print("\nTesting OpenAI client...")
start = time.time()
try:
    response = llm_extractor.client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Say 'test successful'"}],
        max_tokens=10
    )
    elapsed = time.time() - start
    print(f"✓ OpenAI API call successful ({elapsed:.2f}s)")
    print(f"  Response: {response.choices[0].message.content}")
except Exception as e:
    elapsed = time.time() - start
    print(f"✗ OpenAI API call failed after {elapsed:.2f}s: {e}")

db.close()
print("\n✅ Test complete!")