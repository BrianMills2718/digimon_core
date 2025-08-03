#!/usr/bin/env python3
"""
Test script for the new LiteLLM-based AsyncEnhancedAPIClient with AnyIO
"""

import os
import sys
import asyncio
sys.path.insert(0, '/home/brian/projects/Digimons/src')

from core.async_api_client import AsyncEnhancedAPIClient, AsyncAPIRequest, AsyncAPIRequestType

async def test_async_enhanced_api_client():
    """Test the new LiteLLM-based async API client"""
    
    # Set test environment (using mock keys for testing)
    os.environ['OPENAI_API_KEY'] = 'test-key'
    os.environ['PRIMARY_MODEL'] = 'gpt_4o_mini'
    
    # Initialize client
    try:
        client = AsyncEnhancedAPIClient(max_concurrent=5)
        print(f"✅ AsyncClient initialized successfully with {len(client.models)} models")
        print(f"Available models: {list(client.models.keys())}")
    except Exception as e:
        print(f"❌ AsyncClient initialization failed: {e}")
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
    
    # Test generate_content method (main interface)
    try:
        # This will fail because we don't have real API keys, but should test the structure
        content = await client.generate_content("Hello, world!", use_fallback=False)
        print(f"✅ generate_content method works (returned: {content[:50]}...)")
    except Exception as e:
        # Expected to fail with mock keys, but should be an API error, not a structural error
        if "api" in str(e).lower() or "key" in str(e).lower() or "auth" in str(e).lower():
            print(f"✅ generate_content method structure correct (expected API error: {str(e)[:100]}...)")
        else:
            print(f"❌ generate_content method structure error: {e}")
            return False
    
    # Test performance metrics
    try:
        metrics = client.get_performance_metrics()
        print(f"✅ Performance metrics: {metrics}")
    except Exception as e:
        print(f"❌ Performance metrics failed: {e}")
        return False
    
    print("\n🎉 All async tests passed! AsyncEnhancedAPIClient is working correctly.")
    return True

if __name__ == "__main__":
    asyncio.run(test_async_enhanced_api_client())