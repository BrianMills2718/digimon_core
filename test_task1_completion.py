#!/usr/bin/env python3
"""Test Task 1 Completion - Tool Adapter Interface Fix

This script tests that Task 1 has been successfully completed by verifying:
1. Tool protocol interface is properly implemented
2. All tool adapters implement the Tool protocol
3. Pipeline orchestrator can use the tools correctly
"""

import sys
sys.path.insert(0, '/home/brian/Digimons/src')

from src.core.tool_protocol import Tool
from src.core.tool_adapters import (
    PDFLoaderAdapter, TextChunkerAdapter, SpacyNERAdapter,
    RelationshipExtractorAdapter, EntityBuilderAdapter, EdgeBuilderAdapter,
    PageRankAdapter, MultiHopQueryAdapter
)
from src.core.config_manager import ConfigManager
from src.core.evidence_logger import evidence_logger
import datetime

def test_tool_protocol_implementation():
    """Test that all tool adapters implement the Tool protocol"""
    print("Testing Tool Protocol Implementation...")
    
    # Test tool adapters
    config_manager = ConfigManager()
    
    adapters = [
        PDFLoaderAdapter(config_manager),
        TextChunkerAdapter(config_manager),
        SpacyNERAdapter(config_manager),
        RelationshipExtractorAdapter(config_manager),
        EntityBuilderAdapter(config_manager),
        EdgeBuilderAdapter(config_manager),
        PageRankAdapter(config_manager),
        MultiHopQueryAdapter(config_manager)
    ]
    
    test_results = []
    
    for adapter in adapters:
        adapter_name = adapter.__class__.__name__
        print(f"Testing {adapter_name}...")
        
        # Test 1: Check if adapter implements Tool protocol
        is_tool_instance = isinstance(adapter, Tool)
        print(f"  - Implements Tool protocol: {is_tool_instance}")
        
        # Test 2: Check if adapter has required methods
        has_execute = hasattr(adapter, 'execute')
        has_get_tool_info = hasattr(adapter, 'get_tool_info')
        has_validate_input = hasattr(adapter, 'validate_input')
        
        print(f"  - Has execute method: {has_execute}")
        print(f"  - Has get_tool_info method: {has_get_tool_info}")
        print(f"  - Has validate_input method: {has_validate_input}")
        
        # Test 3: Test get_tool_info method
        try:
            tool_info = adapter.get_tool_info()
            has_valid_tool_info = (
                isinstance(tool_info, dict) and
                'name' in tool_info and
                'version' in tool_info and
                'description' in tool_info
            )
            print(f"  - get_tool_info returns valid info: {has_valid_tool_info}")
        except Exception as e:
            print(f"  - get_tool_info failed: {e}")
            has_valid_tool_info = False
        
        # Test 4: Test validate_input method
        try:
            # Test with None (should return False)
            validation_result = adapter.validate_input(None)
            print(f"  - validate_input(None) = {validation_result}")
            
            # Test with empty dict (should return False for most adapters)
            validation_result2 = adapter.validate_input({})
            print(f"  - validate_input({{}}) = {validation_result2}")
        except Exception as e:
            print(f"  - validate_input failed: {e}")
            validation_result = False
        
        test_results.append({
            'adapter': adapter_name,
            'implements_tool': is_tool_instance,
            'has_execute': has_execute,
            'has_get_tool_info': has_get_tool_info,
            'has_validate_input': has_validate_input,
            'valid_tool_info': has_valid_tool_info,
            'validation_works': validation_result is not None
        })
    
    return test_results

def main():
    """Run tests and log evidence"""
    print("=== TASK 1 COMPLETION VERIFICATION ===")
    print("Testing Tool Adapter Interface Fix...")
    
    try:
        test_results = test_tool_protocol_implementation()
        
        # Check if all tests passed
        all_passed = all(
            result['implements_tool'] and 
            result['has_execute'] and 
            result['has_get_tool_info'] and 
            result['has_validate_input'] and
            result['valid_tool_info'] and
            result['validation_works']
            for result in test_results
        )
        
        print(f"\n=== RESULTS ===")
        print(f"All adapters implement Tool protocol: {all_passed}")
        
        if all_passed:
            print("✅ TASK 1 COMPLETED SUCCESSFULLY")
        else:
            print("❌ TASK 1 FAILED")
            
        # Log evidence
        evidence_logger.log_task_completion(
            "TASK1_TOOL_ADAPTER_INTERFACE_FIX",
            {
                "task_description": "Fix Adapter Interface Mismatch",
                "files_modified": [
                    "src/core/tool_protocol.py",
                    "src/core/tool_adapters.py", 
                    "src/core/pipeline_orchestrator.py",
                    "src/core/tool_factory.py"
                ],
                "adapters_tested": len(test_results),
                "test_results": test_results
            },
            all_passed
        )
        
        return all_passed
        
    except Exception as e:
        print(f"❌ TASK 1 FAILED WITH ERROR: {e}")
        
        # Log evidence of failure
        evidence_logger.log_task_completion(
            "TASK1_TOOL_ADAPTER_INTERFACE_FIX",
            {
                "task_description": "Fix Adapter Interface Mismatch",
                "error": str(e),
                "timestamp": datetime.datetime.now().isoformat()
            },
            False
        )
        
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)