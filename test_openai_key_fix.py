#!/usr/bin/env python3
"""Test that OpenAI API key is properly loaded"""

import sys
import os
sys.path.insert(0, '/home/brian/Digimons')

def test_openai_key_loading():
    """Test that the workflow loads OpenAI API key correctly"""
    
    print("🔍 TESTING OPENAI API KEY LOADING")
    print("=" * 50)
    
    # Test 1: Direct dotenv loading
    from dotenv import load_dotenv
    load_dotenv()
    
    openai_key = os.getenv("OPENAI_API_KEY")
    print(f"✅ OpenAI API Key loaded: {bool(openai_key)}")
    if openai_key:
        print(f"   Key starts with: {openai_key[:15]}...")
    
    # Test 2: Enhanced Identity Service initialization
    try:
        from src.core.enhanced_identity_service import EnhancedIdentityService
        print("✅ Enhanced Identity Service imported")
        
        service = EnhancedIdentityService()
        print("✅ Enhanced Identity Service initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ Enhanced Identity Service failed: {e}")
        return False

def test_simple_embedding():
    """Test a simple embedding call to verify the API key works"""
    
    print("\n🔍 TESTING SIMPLE EMBEDDING CALL")
    print("=" * 50)
    
    try:
        from dotenv import load_dotenv
        import os
        from openai import OpenAI
        
        load_dotenv()
        
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Test simple embedding
        response = client.embeddings.create(
            model="text-embedding-ada-002",
            input="test string"
        )
        
        print("✅ OpenAI embedding call successful")
        print(f"   Embedding dimension: {len(response.data[0].embedding)}")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI embedding call failed: {e}")
        return False

if __name__ == "__main__":
    print("🎯 OPENAI API KEY AND EMBEDDING TEST")
    print("=" * 60)
    
    # Test API key loading
    key_test = test_openai_key_loading()
    
    # Test embedding call
    embedding_test = test_simple_embedding()
    
    print("\n" + "=" * 60)
    print("🎯 SUMMARY:")
    print(f"  ✅ API Key Loading: {'PASS' if key_test else 'FAIL'}")
    print(f"  ✅ Embedding Call: {'PASS' if embedding_test else 'FAIL'}")
    
    if key_test and embedding_test:
        print("\n🎉 SUCCESS: OpenAI API key and embeddings working!")
    else:
        print("\n❌ FAILURE: OpenAI API issues detected")
    
    sys.exit(0 if (key_test and embedding_test) else 1)