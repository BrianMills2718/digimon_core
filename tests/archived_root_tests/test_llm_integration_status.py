#!/usr/bin/env python3
"""Test LLM Integration Status

This script tests the current LLM integration to identify specific issues.
"""

import os
import sys
sys.path.append('/home/brian/projects/Digimons')

from src.core.enhanced_api_client import EnhancedAPIClient
from src.core.api_auth_manager import APIAuthManager
from src.tools.phase2.extraction_components.llm_integration import LLMExtractionClient

def test_environment_setup():
    """Test environment and API key setup"""
    print("=== TESTING ENVIRONMENT SETUP ===")
    
    # Check for API keys in environment
    api_keys = {
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY'), 
        'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY')
    }
    
    print("\nAPI Key Status:")
    for key_name, key_value in api_keys.items():
        if key_value:
            print(f"✅ {key_name}: Available ({key_value[:8]}...)")
        else:
            print(f"❌ {key_name}: Not found")
    
    return any(api_keys.values())

def test_auth_manager():
    """Test API authentication manager"""
    print("\n=== TESTING API AUTH MANAGER ===")
    
    try:
        auth_manager = APIAuthManager()
        available_services = auth_manager.get_available_services()
        
        print(f"\nAvailable services: {available_services}")
        
        # Test each service
        for service in available_services:
            service_info = auth_manager.get_service_info(service)
            print(f"\n{service}:")
            print(f"  Available: {service_info.get('available', False)}")
            print(f"  Has API Key: {service_info.get('has_api_key', False)}")
            print(f"  Base URL: {service_info.get('base_url', 'Not set')}")
            print(f"  Model: {service_info.get('model_name', 'Not set')}")
        
        # Test actual API connections
        print("\n=== TESTING REAL API CONNECTIONS ===")
        connection_results = auth_manager.test_all_api_connections()
        
        for service, result in connection_results.items():
            status = "✅ WORKING" if result['connection_valid'] else "❌ FAILED"
            duration = result['test_duration_seconds']
            error = result.get('error', 'None')
            
            print(f"{service}: {status} ({duration:.2f}s)")
            if error != 'None':
                print(f"  Error: {error}")
        
        return len(connection_results) > 0 and any(r['connection_valid'] for r in connection_results.values())
        
    except Exception as e:
        print(f"❌ Auth Manager Error: {e}")
        return False

def test_enhanced_api_client():
    """Test enhanced API client"""
    print("\n=== TESTING ENHANCED API CLIENT ===")
    
    try:
        auth_manager = APIAuthManager()
        client = EnhancedAPIClient(auth_manager)
        
        print(f"Available models: {client.available_models}")
        
        # Test simple API call
        test_prompt = "Hello, this is a test message. Please respond with just 'Test successful'."
        
        print("\nTesting API call...")
        response = client.make_request(
            prompt=test_prompt,
            max_tokens=50,
            temperature=0.1
        )
        
        if response.success:
            print(f"✅ API Call Success!")
            print(f"Service used: {response.service_used}")
            print(f"Response time: {response.response_time:.2f}s")
            print(f"Response: {response.response_data}")
            print(f"Fallback used: {response.fallback_used}")
            return True
        else:
            print(f"❌ API Call Failed: {response.error}")
            return False
            
    except Exception as e:
        print(f"❌ Enhanced API Client Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_llm_extraction_client():
    """Test LLM extraction client"""
    print("\n=== TESTING LLM EXTRACTION CLIENT ===")
    
    try:
        # Create auth manager and API client
        auth_manager = APIAuthManager()
        api_client = EnhancedAPIClient(auth_manager)
        
        # Create LLM extraction client
        llm_client = LLMExtractionClient(api_client, auth_manager)
        
        # Create simple test ontology
        class MockOntology:
            def __init__(self):
                self.domain_name = "Test Domain"
                self.domain_description = "Test domain for LLM integration"
                self.entity_types = [MockEntityType("PERSON"), MockEntityType("LOCATION")]
                self.relationship_types = [MockRelationType("LOCATED_IN")]
        
        class MockEntityType:
            def __init__(self, name):
                self.name = name
                self.description = f"Test {name} entity type"
                self.examples = [f"Example {name}"]
        
        class MockRelationType:
            def __init__(self, name):
                self.name = name
                self.description = f"Test {name} relationship type"
                self.examples = [f"Example {name}"]
        
        ontology = MockOntology()
        test_text = "John Smith lives in New York City."
        
        # Test OpenAI extraction
        if auth_manager.is_service_available("openai"):
            print("\nTesting OpenAI extraction...")
            try:
                result = llm_client.extract_entities_openai(test_text, ontology)
                print(f"✅ OpenAI extraction successful!")
                print(f"Entities found: {len(result.get('entities', []))}")
                for entity in result.get('entities', []):
                    print(f"  - {entity.get('text', 'N/A')} ({entity.get('type', 'N/A')})")
            except Exception as e:
                print(f"❌ OpenAI extraction failed: {e}")
        
        # Test Gemini extraction
        if auth_manager.is_service_available("google"):
            print("\nTesting Gemini extraction...")
            try:
                result = llm_client.extract_entities_gemini(test_text, ontology)
                print(f"✅ Gemini extraction successful!")
                print(f"Entities found: {len(result.get('entities', []))}")
                for entity in result.get('entities', []):
                    print(f"  - {entity.get('text', 'N/A')} ({entity.get('type', 'N/A')})")
            except Exception as e:
                print(f"❌ Gemini extraction failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ LLM Extraction Client Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dependencies():
    """Test required dependencies"""
    print("\n=== TESTING DEPENDENCIES ===")
    
    dependencies = [
        "litellm",
        "openai", 
        "google-generativeai",
        "anthropic",
        "python-dotenv"
    ]
    
    all_good = True
    for dep in dependencies:
        try:
            __import__(dep.replace('-', '_'))
            print(f"✅ {dep}: Available")
        except ImportError:
            print(f"❌ {dep}: Missing")
            all_good = False
    
    return all_good

def main():
    """Main test function"""
    print("🔍 TESTING LLM INTEGRATION STATUS")
    print("=" * 50)
    
    # Run all tests
    tests = [
        ("Environment Setup", test_environment_setup),
        ("Dependencies", test_dependencies), 
        ("Auth Manager", test_auth_manager),
        ("Enhanced API Client", test_enhanced_api_client),
        ("LLM Extraction Client", test_llm_extraction_client)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("🔍 TEST SUMMARY")
    print("=" * 50)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    overall_status = all(results.values())
    print(f"\nOverall Status: {'✅ ALL TESTS PASSED' if overall_status else '❌ SOME TESTS FAILED'}")
    
    if not overall_status:
        print("\n🔧 NEXT STEPS:")
        if not results.get("Environment Setup", True):
            print("1. Set up API keys in environment variables")
        if not results.get("Dependencies", True):
            print("2. Install missing dependencies: pip install litellm openai google-generativeai anthropic")
        if not results.get("Auth Manager", True):
            print("3. Check API key validity and network connectivity")
        if not results.get("Enhanced API Client", True):
            print("4. Debug Enhanced API Client integration")
        if not results.get("LLM Extraction Client", True):
            print("5. Fix LLM Extraction Client implementation")

if __name__ == "__main__":
    main()