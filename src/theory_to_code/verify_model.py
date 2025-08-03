#!/usr/bin/env python3
"""
Model Verification Script

Ensures that all theory-to-code components are using gemini-2.5-flash consistently.
Run this script to verify the model configuration is locked in correctly.
"""

import os
import yaml
from typing import Dict, Any

def check_config_file():
    """Check the main config file for model settings"""
    config_path = "/home/brian/projects/Digimons/config/default.yaml"
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        llm_config = config.get('llm', {})
        default_model = llm_config.get('default_model', 'NOT FOUND')
        gemini_model = config.get('api', {}).get('gemini_model', 'NOT FOUND')
        
        print(f"✓ Config file: {config_path}")
        print(f"  default_model: {default_model}")
        print(f"  gemini_model: {gemini_model}")
        
        # Check if both are gemini-2.5-flash
        is_correct = (default_model == 'gemini-2.5-flash' and 
                     gemini_model == 'gemini-2.5-flash')
        
        if is_correct:
            print("  ✅ Both models set to gemini-2.5-flash")
        else:
            print("  ❌ Models not correctly set to gemini-2.5-flash")
        
        return is_correct
        
    except Exception as e:
        print(f"❌ Error reading config: {e}")
        return False

def check_environment_variables():
    """Check environment variables that might override settings"""
    env_vars = ['LLM_MODEL', 'DEFAULT_MODEL', 'OPENAI_MODEL', 'GEMINI_MODEL']
    
    print("\n✓ Environment Variables:")
    for var in env_vars:
        value = os.getenv(var, 'not set')
        print(f"  {var}: {value}")
    
    # Check if any are overriding to wrong model
    problematic = []
    for var in env_vars:
        value = os.getenv(var)
        if value and value != 'gemini-2.5-flash' and 'gemini' in value:
            problematic.append(f"{var}={value}")
    
    if problematic:
        print(f"  ⚠️  Potentially conflicting: {', '.join(problematic)}")
        return False
    else:
        print("  ✅ No conflicting environment variables")
        return True

def check_theory_to_code_modules():
    """Check that theory-to-code modules are configured correctly"""
    modules_to_check = [
        'algorithm_generator.py',
        'llm_code_generator.py', 
        'llm_parameter_extractor.py',
        'structured_extractor.py'
    ]
    
    print("\n✓ Theory-to-Code Module Defaults:")
    
    all_correct = True
    for module in modules_to_check:
        module_path = f"/home/brian/projects/Digimons/src/theory_to_code/{module}"
        
        try:
            with open(module_path, 'r') as f:
                content = f.read()
            
            # Check for gemini-2.5-flash in default parameters
            if 'gemini-2.5-flash' in content:
                print(f"  ✅ {module}: Uses gemini-2.5-flash")
            elif 'gpt-4' in content or 'gpt-4o' in content:
                print(f"  ❌ {module}: Still has GPT-4 defaults")
                all_correct = False
            else:
                print(f"  ⚠️  {module}: No explicit model default found")
                
        except Exception as e:
            print(f"  ❌ {module}: Error reading - {e}")
            all_correct = False
    
    return all_correct

def test_actual_model_usage():
    """Test that the model is actually being used in practice"""
    print("\n✓ Testing Actual Model Usage:")
    
    try:
        # Test algorithm generator
        from .algorithm_generator import AlgorithmGenerator
        generator = AlgorithmGenerator()
        print(f"  Algorithm Generator model: {generator.model}")
        
        # Test procedure generator  
        from .procedure_generator import ProcedureGenerator
        proc_generator = ProcedureGenerator()
        print(f"  Procedure Generator model: {proc_generator.model}")
        
        # Check if both are using gemini-2.5-flash
        if (generator.model == 'gemini-2.5-flash' and 
            proc_generator.model == 'gemini-2.5-flash'):
            print("  ✅ All generators using gemini-2.5-flash")
            return True
        else:
            print("  ❌ Generators not using gemini-2.5-flash")
            return False
            
    except Exception as e:
        print(f"  ❌ Error testing model usage: {e}")
        return False

def main():
    """Run all verification checks"""
    print("=" * 60)
    print("GEMINI-2.5-FLASH MODEL VERIFICATION")
    print("=" * 60)
    
    checks = [
        ("Config File", check_config_file),
        ("Environment Variables", check_environment_variables), 
        ("Module Defaults", check_theory_to_code_modules),
        ("Actual Usage", test_actual_model_usage)
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append(result)
        except Exception as e:
            print(f"❌ {check_name} check failed: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    all_passed = all(results)
    status = "✅ PASSED" if all_passed else "❌ FAILED"
    print(f"Overall Status: {status}")
    
    if all_passed:
        print("\n🎉 gemini-2.5-flash is properly locked in across all components!")
        print("The model should be consistently used during development.")
    else:
        print("\n⚠️  Some components may still use other models.")
        print("Review the issues above and update the affected files.")
    
    return all_passed

if __name__ == "__main__":
    main()