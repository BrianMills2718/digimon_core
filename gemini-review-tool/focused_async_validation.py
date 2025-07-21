#!/usr/bin/env python3
"""
Focused validation for CLAIM 1: Async Migration fixes only
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
script_dir = Path(__file__).parent
env_file = script_dir / '.env'
load_dotenv(env_file)

try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

def validate_async_migration():
    """Validate only the async migration fixes with minimal context"""
    
    if not HAS_GEMINI:
        print("❌ Google Generative AI not available")
        return False
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ No Gemini API key found")
        return False
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # Read only the two relevant files with just the async methods
    neo4j_file = Path(__file__).parent.parent / 'src/core/neo4j_manager.py'
    tool_factory_file = Path(__file__).parent.parent / 'src/core/tool_factory.py'
    
    try:
        with open(neo4j_file, 'r') as f:
            neo4j_content = f.read()
            
        with open(tool_factory_file, 'r') as f:
            tool_factory_content = f.read()
    except Exception as e:
        print(f"❌ Could not read files: {e}")
        return False
    
    # Focused prompt ONLY for async migration
    prompt = f"""
    Validate ONLY this specific claim about async migration fixes:

    **CLAIM: Fixed Async Migration - Removed all simulation code and implemented real async operations**
    
    SPECIFIC ISSUES TO CHECK:
    1. src/core/neo4j_manager.py around line 127-155: Should use AsyncGraphDatabase, not sync driver wrapped in async
    2. src/core/tool_factory.py around line 318-384: Should use asyncio.gather for concurrent execution, not sequential loop with sleep
    
    VALIDATION CRITERIA:
    - ✅ FULLY RESOLVED: Real async operations, no simulation code
    - ⚠️ PARTIALLY RESOLVED: Some improvement but still has issues  
    - ❌ NOT RESOLVED: Still using simulation or sync-wrapped-in-async
    
    FOCUS ONLY ON:
    - Look for AsyncGraphDatabase vs GraphDatabase usage
    - Look for asyncio.gather vs sequential for loops
    - Check for asyncio.sleep() used as simulation vs real async operations
    
    IGNORE: Everything else not related to async migration
    
    neo4j_manager.py content:
    ```python
    {neo4j_content}
    ```
    
    tool_factory.py content:
    ```python
    {tool_factory_content}
    ```
    
    Provide a focused verdict ONLY for the async migration claim.
    """
    
    try:
        print("🎯 Validating async migration fixes with focused context...")
        response = model.generate_content(prompt)
        
        print("\n" + "="*60)
        print("🔍 FOCUSED ASYNC MIGRATION VALIDATION")
        print("="*60)
        print(response.text)
        
        return True
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return False

if __name__ == "__main__":
    success = validate_async_migration()
    exit(0 if success else 1)