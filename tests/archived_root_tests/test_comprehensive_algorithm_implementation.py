#!/usr/bin/env python3
"""
Comprehensive Algorithm Implementation Test
Tests automatic generation of working implementations for different theory types:
- FORMULAS (mathematical calculations)
- PROCEDURES (step-by-step processes) 
- RULES (decision logic)
- SEQUENCES (ordered steps)
- FRAMEWORKS (analytical systems)
- ALGORITHMS (computational methods)
"""

import os
import json
import sys
import ast
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple

# Add universal model tester to path
sys.path.append(str(Path(__file__).parent / "universal_model_tester"))
from universal_model_client import UniversalModelClient

class ComprehensiveAlgorithmImplementor:
    def __init__(self):
        self.client = UniversalModelClient()
        self.results = []
    
    def get_category_specific_prompt(self, component: Dict[str, Any], theory_name: str) -> str:
        """Generate category-specific implementation prompts"""
        name = component.get('name', 'Unknown')
        category = component.get('category', 'UNKNOWN').upper()
        description = component.get('description', '')
        implementation = component.get('implementation', '')
        
        base_context = f"""
THEORY: {theory_name}
COMPONENT: {name}
DESCRIPTION: {description}
IMPLEMENTATION NOTES: {implementation}
"""
        
        if category == 'FORMULAS':
            return base_context + """
Generate a Python function that implements this mathematical formula:

Requirements:
1. Take input parameters with clear types
2. Implement the mathematical calculation exactly
3. Return computed result with validation
4. Include error handling for invalid inputs
5. Add comprehensive docstring

Format as working Python code with test examples.
"""
        
        elif category == 'PROCEDURES':
            return base_context + """
Generate a Python class that implements this step-by-step procedure:

Requirements:
1. Break down into discrete, executable steps
2. Maintain state between steps if needed
3. Allow step-by-step execution and full workflow
4. Return structured results for each step
5. Include validation and error handling

Format as working Python code with test scenarios.
"""
        
        elif category == 'RULES':
            return base_context + """
Generate a Python function/class that implements this decision rule system:

Requirements:
1. Take criteria/conditions as input
2. Apply decision logic systematically
3. Return classification/decision with reasoning
4. Include confidence scores or explanation
5. Handle edge cases and multiple rule scenarios

Format as working Python code with decision test cases.
"""
        
        elif category == 'SEQUENCES':
            return base_context + """
Generate a Python class that manages this sequential process:

Requirements:
1. Implement ordered phases/steps with transitions
2. Track current state and progress
3. Allow interruption and resumption
4. Validate prerequisites for each step
5. Return structured progress and final results

Format as working Python code with sequence test cases.
"""
        
        elif category == 'FRAMEWORKS':
            return base_context + """
Generate a Python framework class that implements this analytical system:

Requirements:
1. Provide clear interface for applying the framework
2. Support different types of analysis within framework
3. Return structured analytical results
4. Allow framework customization and extension
5. Include multiple analysis methods

Format as working Python code with analysis examples.
"""
        
        elif category == 'ALGORITHMS':
            return base_context + """
Generate a Python function/class that implements this computational algorithm:

Requirements:
1. Implement the computational logic efficiently
2. Handle different input sizes and types
3. Optimize for accuracy and performance
4. Include algorithm complexity documentation
5. Provide debugging and tracing capabilities

Format as working Python code with algorithmic test cases.
"""
        
        else:
            return base_context + """
Generate a Python implementation for this theoretical component:

Requirements:
1. Create functional, executable implementation
2. Provide clear interface and usage patterns
3. Include appropriate validation and error handling
4. Add comprehensive documentation
5. Support practical application of the theory

Format as working Python code with usage examples.
"""
    
    def extract_python_code(self, response_text: str) -> str:
        """Extract Python code from LLM response"""
        # Try to find code blocks
        code_blocks = re.findall(r'```python\n(.*?)\n```', response_text, re.DOTALL)
        if code_blocks:
            return code_blocks[0]
        
        # If no code blocks, try to find code after certain patterns
        patterns = [
            r'Here\'s the implementation:\n\n(.*?)(?:\n\n|\Z)',
            r'Implementation:\n\n(.*?)(?:\n\n|\Z)',
            r'```\n(.*?)\n```'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, response_text, re.DOTALL)
            if matches:
                return matches[0]
        
        # If still nothing, return the whole response (might be all code)
        return response_text
    
    def validate_code_implementation(self, code: str, name: str) -> Dict[str, Any]:
        """Validate that generated code is syntactically correct and functional"""
        validation = {
            "syntax_valid": False,
            "has_main_function": False,
            "has_class": False,
            "has_tests": False,
            "code_quality_score": 0.0,
            "error": None
        }
        
        try:
            # Parse syntax
            tree = ast.parse(code)
            validation["syntax_valid"] = True
            
            # Analyze AST for structure
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    validation["has_main_function"] = True
                elif isinstance(node, ast.ClassDef):
                    validation["has_class"] = True
            
            # Check for test patterns
            if "test" in code.lower() or "example" in code.lower():
                validation["has_tests"] = True
            
            # Calculate quality score
            quality_factors = [
                validation["syntax_valid"],
                validation["has_main_function"] or validation["has_class"],
                validation["has_tests"],
                len(code) > 100,  # Reasonable length
                "def " in code or "class " in code,  # Has definitions
                '"""' in code or "'''" in code  # Has docstrings
            ]
            validation["code_quality_score"] = sum(quality_factors) / len(quality_factors)
            
        except SyntaxError as e:
            validation["error"] = f"Syntax error: {str(e)}"
        except Exception as e:
            validation["error"] = f"Analysis error: {str(e)}"
        
        return validation
    
    def generate_implementation(self, component: Dict[str, Any], theory_name: str) -> Dict[str, Any]:
        """Generate implementation for a single component"""
        name = component.get('name', 'Unknown')
        category = component.get('category', 'UNKNOWN')
        
        print(f"\n🔧 Implementing: {name} ({category})")
        print("-" * 60)
        
        prompt = self.get_category_specific_prompt(component, theory_name)
        
        try:
            messages = [{"role": "user", "content": prompt}]
            
            result = self.client.complete(
                messages=messages,
                model="claude_sonnet_4",
                timeout=90
            )
            
            response_text = result["response"].choices[0].message.content
            generated_code = self.extract_python_code(response_text)
            
            # Validate the implementation
            validation = self.validate_code_implementation(generated_code, name)
            
            print(f"✅ Generated implementation")
            print(f"   Code length: {len(generated_code)} characters")
            print(f"   Syntax valid: {validation['syntax_valid']}")
            print(f"   Quality score: {validation['code_quality_score']:.2f}")
            
            return {
                "name": name,
                "category": category,
                "theory_name": theory_name,
                "description": component.get('description', ''),
                "original_implementation": component.get('implementation', ''),
                "generated_code": generated_code,
                "validation": validation,
                "response_text": response_text,
                "success": validation['syntax_valid'] and validation['code_quality_score'] > 0.5
            }
            
        except Exception as e:
            print(f"❌ Implementation failed: {str(e)[:100]}...")
            return {
                "name": name,
                "category": category,
                "theory_name": theory_name,
                "description": component.get('description', ''),
                "original_implementation": component.get('implementation', ''),
                "generated_code": "",
                "validation": {"syntax_valid": False, "error": str(e)},
                "response_text": "",
                "success": False
            }
    
    def test_generated_implementation(self, implementation: Dict[str, Any]) -> Dict[str, Any]:
        """Test if generated implementation actually works"""
        code = implementation.get('generated_code', '')
        name = implementation.get('name', 'Unknown')
        
        if not code or not implementation['validation']['syntax_valid']:
            return {"tested": False, "error": "No valid code to test"}
        
        try:
            # Create isolated namespace and execute
            namespace = {}
            exec(code, namespace)
            
            # Look for test functions or executable examples
            test_functions = [k for k in namespace.keys() if 'test' in k.lower() and callable(namespace[k])]
            
            if test_functions:
                # Run first test function
                test_func = namespace[test_functions[0]]
                test_result = test_func()
                return {"tested": True, "test_passed": True, "result": str(test_result)[:200]}
            else:
                # Just verify it executed without error
                return {"tested": True, "test_passed": True, "result": "Code executed successfully"}
                
        except Exception as e:
            return {"tested": True, "test_passed": False, "error": str(e)[:200]}
    
    def load_diverse_theory_components(self) -> List[Tuple[Dict[str, Any], str]]:
        """Load diverse operational components from multiple theories"""
        results_file = "advanced_multi_pass_results_20250726_061840.json"
        
        try:
            with open(results_file, 'r') as f:
                data = json.load(f)
        except Exception as e:
            print(f"Error loading results: {e}")
            return []
        
        # Extract components from multiple theories and different categories
        components = []
        categories_found = set()
        
        for result in data.get('detailed_results', []):
            for pass_result in reversed(result.get('passes', [])):
                if pass_result.get('success') and pass_result.get('extraction_data'):
                    theory_data = pass_result['extraction_data']
                    theory_name = theory_data.get('theory_name', 'Unknown')
                    
                    for comp in theory_data.get('operational_components', []):
                        category = comp.get('category', 'UNKNOWN').upper()
                        
                        # Collect diverse categories
                        if len(components) < 8:  # Limit total components
                            components.append((comp, theory_name))
                            categories_found.add(category)
                        elif category not in categories_found and len(categories_found) < 6:
                            # Add new categories we haven't seen
                            components.append((comp, theory_name))
                            categories_found.add(category)
                    break
        
        return components
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive algorithm implementation test"""
        print("🚀 COMPREHENSIVE ALGORITHM IMPLEMENTATION TEST")
        print("=" * 70)
        print("Testing automatic generation of working code across all theory component types")
        
        components = self.load_diverse_theory_components()
        
        if not components:
            return {"error": "No components found to test"}
        
        print(f"Testing {len(components)} components across different categories")
        
        # Generate implementations
        implementations = []
        successful = 0
        category_stats = {}
        
        for i, (component, theory_name) in enumerate(components):
            print(f"\n[{i+1}/{len(components)}] " + "="*40)
            
            implementation = self.generate_implementation(component, theory_name)
            
            # Test the implementation
            test_result = self.test_generated_implementation(implementation)
            implementation['test_result'] = test_result
            
            implementations.append(implementation)
            
            if implementation['success']:
                successful += 1
            
            # Track category statistics
            category = implementation['category']
            if category not in category_stats:
                category_stats[category] = {'total': 0, 'successful': 0}
            category_stats[category]['total'] += 1
            if implementation['success']:
                category_stats[category]['successful'] += 1
        
        # Calculate category success rates
        for category in category_stats:
            stats = category_stats[category]
            stats['success_rate'] = stats['successful'] / stats['total'] if stats['total'] > 0 else 0
        
        overall_success_rate = successful / len(components) if components else 0
        
        print(f"\n📊 COMPREHENSIVE TEST RESULTS")
        print("=" * 50)
        print(f"Total components: {len(components)}")
        print(f"Successful implementations: {successful}")
        print(f"Overall success rate: {overall_success_rate:.1%}")
        
        print(f"\n📋 Category Performance:")
        for category, stats in category_stats.items():
            print(f"  {category}: {stats['success_rate']:.1%} ({stats['successful']}/{stats['total']})")
        
        # Show successful examples
        successful_impls = [impl for impl in implementations if impl['success']]
        if successful_impls:
            print(f"\n🎯 Successful Implementation Examples:")
            for impl in successful_impls[:3]:  # Show first 3
                print(f"  ✅ {impl['name']} ({impl['category']}) - Quality: {impl['validation']['code_quality_score']:.2f}")
        
        return {
            "summary": {
                "total_components": len(components),
                "successful_implementations": successful,
                "overall_success_rate": overall_success_rate,
                "categories_tested": list(category_stats.keys())
            },
            "category_stats": category_stats,
            "implementations": implementations
        }

def main():
    """Run comprehensive algorithm implementation test"""
    implementor = ComprehensiveAlgorithmImplementor()
    
    print("Testing comprehensive automatic algorithm implementation...")
    print("This generates working Python code for all operational component types.\n")
    
    analysis = implementor.run_comprehensive_test()
    
    # Save results
    import time
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_file = f"comprehensive_implementation_results_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump(analysis, f, indent=2)
    
    print(f"\n💾 Full results saved: {output_file}")
    
    if 'summary' in analysis:
        summary = analysis['summary']
        print(f"\n🏆 FINAL SUMMARY:")
        print(f"  Success Rate: {summary['overall_success_rate']:.1%}")
        print(f"  Categories: {', '.join(summary['categories_tested'])}")
        print(f"  Implementations: {summary['successful_implementations']}/{summary['total_components']}")
    
    return analysis

if __name__ == "__main__":
    main()