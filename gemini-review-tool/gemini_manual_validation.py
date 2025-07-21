#!/usr/bin/env python3
"""
Manual Gemini validation for Task 4 claims
"""

import os
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from the tool directory
script_dir = Path(__file__).parent
env_file = script_dir / '.env'
load_dotenv(env_file)

# Try to import Gemini API
try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

def validate_task4_claims():
    """Validate Task 4 claims using Gemini API"""
    
    if not HAS_GEMINI:
        print("❌ Google Generative AI not available")
        return False
    
    # Get API key
    api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ No Gemini API key found")
        return False
    
    # Configure Gemini
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # Read the async client code
    with open('src/core/async_api_client.py', 'r') as f:
        code_content = f.read()
    
    # Validation prompt
    prompt = f"""
    Validate the Task 4 Async API Client Enhancement implementation claims by examining this Python code.
    
    TASK 4: ASYNC API CLIENT ENHANCEMENT CLAIMS TO VALIDATE:
    
    CLAIM 1: Enhanced Connection Pooling Implementation
    - Expected: aiohttp.TCPConnector with limit=100, limit_per_host=30, DNS cache, keep-alive
    - Look for: initialize_clients method around lines 296-303
    
    CLAIM 2: Increased Concurrency Limits  
    - Expected: OpenAI semaphore increased from 10 to 25, Gemini from 5 to 15
    - Look for: __init__ method around lines 261-264
    
    CLAIM 3: Response Caching System
    - Expected: TTL cache (300s), size limit (1000), automatic cleanup, cache hit tracking
    - Look for: cache methods around lines 397-421, cache_ttl=300, response_cache dict
    
    CLAIM 4: Batch Processing Optimization
    - Expected: Background batch processor, async queue, optimal batch sizes (50 OpenAI, 20 Gemini)
    - Look for: batch methods around lines 331-372, _create_embeddings_batch with batch_size=50
    
    CLAIM 5: Performance Monitoring
    - Expected: Performance metrics tracking, get_performance_metrics method, benchmark_performance method
    - Look for: performance_metrics dict around lines 275-283, get_performance_metrics around lines 599-611
    
    For each claim, verify:
    1. IMPLEMENTATION PRESENT: Does the feature exist in the code?
    2. FUNCTIONALITY COMPLETE: Is it fully implemented (not a stub)?
    3. REQUIREMENTS MET: Does it meet the specific technical requirements?
    
    Provide verdict for each claim:
    - ✅ FULLY RESOLVED: Implementation present, complete, and meets requirements
    - ⚠️ PARTIALLY RESOLVED: Implementation present but incomplete
    - ❌ NOT RESOLVED: Implementation missing or broken
    
    Reference specific line numbers and code examples when making assessments.
    
    CODE TO ANALYZE:
    {code_content}
    """
    
    try:
        print("🤖 Sending validation request to Gemini...")
        response = model.generate_content(prompt)
        
        print("\n" + "="*60)
        print("🔍 GEMINI VALIDATION RESULTS")
        print("="*60)
        print(response.text)
        
        # Save results
        results = {
            "validation_timestamp": datetime.now().isoformat(),
            "model": "gemini-2.5-flash",
            "prompt_length": len(prompt),
            "response": response.text
        }
        
        with open('gemini_task4_validation_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Validation results saved to: gemini_task4_validation_results.json")
        return True
        
    except Exception as e:
        print(f"❌ Gemini validation failed: {e}")
        return False

def main():
    """Main validation execution"""
    print("🧪 Manual Gemini Validation for Task 4 Claims")
    print("📋 Validating Async API Client Enhancement implementation")
    print("=" * 60)
    
    success = validate_task4_claims()
    
    if success:
        print("\n✅ Gemini validation completed successfully")
    else:
        print("\n❌ Gemini validation failed")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)