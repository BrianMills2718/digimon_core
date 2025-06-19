#!/usr/bin/env python3
"""
TEST FILE FOR CAPABILITY 017
Capability: TextChunker._validate_chunk_parameters()
Description: Validate chunking parameters
File: src/tools/phase1/t15a_text_chunker.py
Class: TextChunker
Method: _validate_chunk_parameters
Test Type: private_method

EXPECTED RESULT: PASS or FAIL with specific evidence
"""

import sys
import traceback
import json
import time
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

def test_capability_017():
    """Test Capability 017: TextChunker._validate_chunk_parameters()"""
    
    test_start_time = time.time()
    result = {
        "capability_id": 17,
        "capability_name": "TextChunker._validate_chunk_parameters()",
        "test_type": "private_method",
        "description": "Validate chunking parameters",
        "file_path": "src/tools/phase1/t15a_text_chunker.py",
        "class_name": "TextChunker",
        "method_name": "_validate_chunk_parameters",
        "test_start_time": test_start_time,
        "status": "UNKNOWN",
        "evidence": "",
        "error": "",
        "execution_time": 0
    }
    
    try:
        print(f"🧪 TESTING CAPABILITY 017: TextChunker._validate_chunk_parameters()")
        print(f"📁 File: src/tools/phase1/t15a_text_chunker.py")
        print(f"🏗️  Class: TextChunker")
        print(f"⚙️  Method: _validate_chunk_parameters")
        print(f"📝 Description: Validate chunking parameters")
        print("-" * 80)
        
        # Test based on capability type
        if "private_method" == "constructor":
            evidence = test_constructor_capability(
                "src/tools/phase1/t15a_text_chunker.py", 
                "TextChunker"
            )
        elif "private_method" == "method":
            evidence = test_method_capability(
                "src/tools/phase1/t15a_text_chunker.py", 
                "TextChunker", 
                "_validate_chunk_parameters"
            )
        elif "private_method" == "private_method":
            evidence = test_private_method_capability(
                "src/tools/phase1/t15a_text_chunker.py", 
                "TextChunker", 
                "_validate_chunk_parameters"
            )
        elif "private_method" == "function":
            evidence = test_function_capability(
                "src/tools/phase1/t15a_text_chunker.py", 
                "_validate_chunk_parameters"
            )
        else:
            evidence = test_generic_capability(
                "src/tools/phase1/t15a_text_chunker.py", 
                "TextChunker", 
                "_validate_chunk_parameters"
            )
            
        result["status"] = "PASS"
        result["evidence"] = evidence
        print(f"✅ PASS: {evidence}")
        
    except Exception as e:
        result["status"] = "FAIL"
        result["error"] = str(e)
        result["evidence"] = f"Failed to test capability: {str(e)}"
        print(f"❌ FAIL: {str(e)}")
        print(f"🔍 Traceback: {traceback.format_exc()}")
        
    finally:
        result["execution_time"] = time.time() - test_start_time
        result["test_end_time"] = time.time()
        
    return result

def test_constructor_capability(file_path, class_name):
    """Test a constructor capability"""
    try:
        # Import the module
        module_path = file_path.replace('/', '.').replace('.py', '')
        module = __import__(module_path, fromlist=[class_name])
        
        # Get the class
        cls = getattr(module, class_name)
        
        # Check if constructor exists and get signature
        import inspect
        signature = inspect.signature(cls.__init__)
        params = list(signature.parameters.keys())[1:]  # Skip 'self'
        
        return f"Constructor exists with parameters: {params}"
        
    except ImportError as e:
        raise Exception(f"Cannot import {module_path}: {e}")
    except AttributeError as e:
        raise Exception(f"Class {class_name} not found in {file_path}: {e}")

def test_method_capability(file_path, class_name, method_name):
    """Test a public method capability"""
    try:
        # Import the module
        module_path = file_path.replace('/', '.').replace('.py', '')
        module = __import__(module_path, fromlist=[class_name])
        
        # Get the class
        cls = getattr(module, class_name)
        
        # Check if method exists and get signature
        if hasattr(cls, method_name):
            method = getattr(cls, method_name)
            import inspect
            signature = inspect.signature(method)
            return f"Method {method_name} exists with signature: {signature}"
        else:
            raise Exception(f"Method {method_name} not found in class {class_name}")
            
    except ImportError as e:
        raise Exception(f"Cannot import {module_path}: {e}")
    except AttributeError as e:
        raise Exception(f"Class {class_name} not found in {file_path}: {e}")

def test_private_method_capability(file_path, class_name, method_name):
    """Test a private method capability"""
    try:
        # Import the module
        module_path = file_path.replace('/', '.').replace('.py', '')
        module = __import__(module_path, fromlist=[class_name])
        
        # Get the class
        cls = getattr(module, class_name)
        
        # Check if private method exists
        if hasattr(cls, method_name):
            method = getattr(cls, method_name)
            import inspect
            signature = inspect.signature(method)
            return f"Private method {method_name} exists with signature: {signature}"
        else:
            raise Exception(f"Private method {method_name} not found in class {class_name}")
            
    except ImportError as e:
        raise Exception(f"Cannot import {module_path}: {e}")
    except AttributeError as e:
        raise Exception(f"Class {class_name} not found in {file_path}: {e}")

def test_function_capability(file_path, function_name):
    """Test a standalone function capability"""
    try:
        # Import the module
        module_path = file_path.replace('/', '.').replace('.py', '')
        module = __import__(module_path, fromlist=[function_name])
        
        # Check if function exists
        if hasattr(module, function_name):
            func = getattr(module, function_name)
            import inspect
            signature = inspect.signature(func)
            return f"Function {function_name} exists with signature: {signature}"
        else:
            raise Exception(f"Function {function_name} not found in {file_path}")
            
    except ImportError as e:
        raise Exception(f"Cannot import {module_path}: {e}")

def test_generic_capability(file_path, class_name, method_name):
    """Generic capability test"""
    try:
        # Check if file exists
        if not Path(file_path).exists():
            raise Exception(f"File {file_path} does not exist")
            
        # Try to import
        module_path = file_path.replace('/', '.').replace('.py', '')
        module = __import__(module_path)
        
        return f"File {file_path} exists and can be imported"
        
    except Exception as e:
        raise Exception(f"Generic test failed: {e}")

def main():
    """Run the capability test and save results"""
    result = test_capability_017()
    
    # Save result to log file
    log_file = f"capability_017_test_log.txt"
    
    with open(log_file, 'w') as f:
        f.write(f"CAPABILITY 017 TEST LOG\n")
        f.write("=" * 50 + "\n")
        f.write(f"Capability: TextChunker._validate_chunk_parameters()\n")
        f.write(f"Description: Validate chunking parameters\n")
        f.write(f"File: src/tools/phase1/t15a_text_chunker.py\n")
        f.write(f"Class: TextChunker\n")
        f.write(f"Method: _validate_chunk_parameters\n")
        f.write(f"Test Type: private_method\n")
        f.write("=" * 50 + "\n")
        f.write(f"STATUS: {result['status']}\n")
        f.write(f"EVIDENCE: {result['evidence']}\n")
        if result['error']:
            f.write(f"ERROR: {result['error']}\n")
        f.write(f"EXECUTION TIME: {result['execution_time']:.4f} seconds\n")
        f.write(f"TIMESTAMP: {time.ctime(result['test_start_time'])}\n")
    
    # Print result summary
    print(f"\n📊 CAPABILITY 017 TEST COMPLETE")
    print(f"Status: {result['status']}")
    print(f"Evidence: {result['evidence']}")
    print(f"Log file: {log_file}")
    
    return result

if __name__ == "__main__":
    result = main()
    sys.exit(0 if result["status"] == "PASS" else 1)
