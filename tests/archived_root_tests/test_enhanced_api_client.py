#!/usr/bin/env python3
"""
Test script for the new LiteLLM-based EnhancedAPIClient
"""

import os
import sys
sys.path.insert(0, '/home/brian/projects/Digimons/src')

from core.enhanced_api_client import EnhancedAPIClient, APIRequest, APIRequestType

def test_enhanced_api_client():
    """Test the new LiteLLM-based API client"""
    
    # Set test environment (using mock keys for testing)
    os.environ['OPENAI_API_KEY'] = 'test-key'
    os.environ['PRIMARY_MODEL'] = 'gpt_4o_mini'
    
    # Initialize client
    try:
        client = EnhancedAPIClient()
        print(f"✅ Client initialized successfully with {len(client.models)} models")
        print(f"Available models: {list(client.models.keys())}")
    except Exception as e:
        print(f"❌ Client initialization failed: {e}")
        return False
    
    # Test configuration loading
    try:
        primary_model = client.fallback_config['primary_model']
        fallback_models = client.fallback_config['fallback_models']
        print(f"✅ Configuration loaded - Primary: {primary_model}, Fallbacks: {fallback_models}")
    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        return False
    
    # Test model config lookup
    try:
        model_config = client._get_model_config('gpt_4o_mini')
        if model_config:
            print(f"✅ Model config found: {model_config.litellm_name}")
        else:
            print("❌ Model config not found")
            return False
    except Exception as e:
        print(f"❌ Model config lookup failed: {e}")
        return False
    
    # Test request type mapping
    try:
        req_type = client._map_request_type('chat_completion')
        print(f"✅ Request type mapping works: {req_type}")
    except Exception as e:
        print(f"❌ Request type mapping failed: {e}")
        return False
    
    print("\n🎉 All tests passed! EnhancedAPIClient is working correctly.")
    return True

if __name__ == "__main__":
    test_enhanced_api_client()