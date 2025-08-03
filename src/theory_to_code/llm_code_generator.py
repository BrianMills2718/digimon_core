#!/usr/bin/env python3
"""
Real LLM-based code generation for theory formulas.
Uses OpenAI API (or compatible) to generate executable code.
"""

import os
import json
import ast
import subprocess
import tempfile
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import logging

# For LLM integration
try:
    import openai
except ImportError:
    # Fallback to litellm which supports multiple providers
    import litellm as openai

logger = logging.getLogger(__name__)

@dataclass
class GeneratedFunction:
    """Represents an LLM-generated function"""
    name: str
    source_code: str
    parameters: List[str]
    return_type: str
    imports: List[str]
    docstring: str
    
class LLMCodeGenerator:
    """Generates executable code from theory schemas using LLMs"""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        # Get model from config
        if model is None:
            try:
                # Try to use standard config if available
                import sys
                import os
                parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                if parent_dir not in sys.path:
                    sys.path.insert(0, parent_dir)
                from core.standard_config import get_model
                self.model = get_model("llm_code_generator")
            except ImportError:
                # Fallback to config file
                try:
                    config_path = os.path.join(os.path.dirname(__file__), '../../config/default.yaml')
                    with open(config_path, 'r') as f:
                        import yaml
                        config = yaml.safe_load(f)
                    self.model = config.get('llm', {}).get('default_model', 'gemini/gemini-2.0-flash-exp')
                except (FileNotFoundError, KeyError):
                    self.model = "gemini/gemini-2.0-flash-exp"
        else:
            self.model = model
        
        if self.api_key:
            openai.api_key = self.api_key
    
    def generate_formula_code(self, formula_spec: Dict[str, Any], 
                            theory_name: str) -> GeneratedFunction:
        """Generate Python code from a formula specification"""
        
        # Build the prompt
        prompt = self._build_code_generation_prompt(formula_spec, theory_name)
        
        # Call LLM
        response = self._call_llm(prompt)
        
        # Parse the generated code
        return self._parse_generated_code(response, formula_spec)
    
    def _build_code_generation_prompt(self, formula_spec: Dict[str, Any], 
                                    theory_name: str) -> str:
        """Build a detailed prompt for code generation"""
        
        prompt = f"""Generate Python code for this {theory_name} formula.

Formula Name: {formula_spec.get('name', 'formula')}
Mathematical Formula: {formula_spec.get('formula', '')}
Parameters: {json.dumps(formula_spec.get('parameters', {}), indent=2)}
Input Requirements: {formula_spec.get('input_requirements', [])}
Output Description: {formula_spec.get('output', '')}

Requirements:
1. Create a pure Python function (no class needed)
2. Use descriptive parameter names based on the formula
3. Include comprehensive type hints
4. Add a detailed docstring explaining:
   - What the formula calculates
   - Parameter meanings and ranges
   - Return value interpretation
5. Handle edge cases (division by zero, negative values where inappropriate, etc.)
6. Use numpy only if dealing with arrays/matrices
7. Include any necessary imports at the top

Format your response as:
```python
# Imports
import math
from typing import ...

def function_name(param1: type1, param2: type2, ...) -> return_type:
    \"\"\"
    Detailed docstring
    \"\"\"
    # Implementation
    return result
```

Only return the Python code, no explanations."""

        return prompt
    
    def _call_llm(self, prompt: str) -> str:
        """Call the LLM API and return response"""
        
        try:
            # Use litellm for compatibility with multiple providers
            import litellm
            response = litellm.completion(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert Python programmer specializing in mathematical and scientific computing."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,  # Lower temperature for more consistent code
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"LLM API call failed: {e}")
            # Fallback to a more detailed prompt-based approach
            return self._fallback_generation(prompt)
    
    def _fallback_generation(self, prompt: str) -> str:
        """Fallback generation if LLM API fails"""
        # Extract key information from prompt
        if "value_function" in prompt.lower():
            return '''import math
from typing import Union

def calculate_value(x: float, reference_point: float = 0, 
                   alpha: float = 0.88, beta: float = 0.88, 
                   lambda_: float = 2.25) -> float:
    """
    Calculate subjective value using Prospect Theory value function.
    
    Implements the value function v(x) where:
    - For gains (x ≥ reference_point): v(x) = (x - reference_point)^α
    - For losses (x < reference_point): v(x) = -λ * |x - reference_point|^β
    
    Args:
        x: Outcome value
        reference_point: Reference point for determining gains/losses
        alpha: Risk aversion parameter for gains (typically 0.88)
        beta: Risk seeking parameter for losses (typically 0.88)
        lambda_: Loss aversion coefficient (typically 2.25)
    
    Returns:
        Subjective value of the outcome
    """
    relative_outcome = x - reference_point
    
    if relative_outcome >= 0:
        # Gain domain
        return relative_outcome ** alpha
    else:
        # Loss domain
        return -lambda_ * (abs(relative_outcome) ** beta)
'''
        
        # Generic fallback
        return '''def generated_function(*args, **kwargs):
    """Generated function - implementation needed"""
    raise NotImplementedError("LLM generation failed - manual implementation required")
'''
    
    def _parse_generated_code(self, code: str, formula_spec: Dict[str, Any]) -> GeneratedFunction:
        """Parse the generated code to extract components"""
        
        # Clean the code (remove markdown if present)
        code = code.strip()
        if code.startswith("```python"):
            code = code[9:]
        if code.startswith("```"):
            code = code[3:]
        if code.endswith("```"):
            code = code[:-3]
        code = code.strip()
        
        # Parse imports
        imports = []
        lines = code.split('\n')
        code_lines = []
        
        for line in lines:
            if line.strip().startswith(('import ', 'from ')):
                imports.append(line.strip())
            else:
                code_lines.append(line)
        
        clean_code = '\n'.join(code_lines).strip()
        
        # Parse the function
        try:
            tree = ast.parse(clean_code)
            
            # Find the function definition
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_name = node.name
                    
                    # Extract parameters
                    params = [arg.arg for arg in node.args.args]
                    
                    # Extract return type if annotated
                    return_type = "float"  # default
                    if node.returns:
                        return_type = ast.unparse(node.returns)
                    
                    # Extract docstring
                    docstring = ast.get_docstring(node) or "Generated function"
                    
                    return GeneratedFunction(
                        name=func_name,
                        source_code=code,
                        parameters=params,
                        return_type=return_type,
                        imports=imports,
                        docstring=docstring
                    )
            
            # If no function found, create a wrapper
            func_name = formula_spec.get('name', 'formula').replace(' ', '_')
            return GeneratedFunction(
                name=func_name,
                source_code=code,
                parameters=[],
                return_type="float",
                imports=imports,
                docstring="Generated formula implementation"
            )
            
        except Exception as e:
            logger.error(f"Failed to parse generated code: {e}")
            # Return a basic structure
            return GeneratedFunction(
                name="generated_function",
                source_code=code,
                parameters=[],
                return_type="Any",
                imports=imports,
                docstring="Generated function"
            )
    
    def validate_generated_code(self, func: GeneratedFunction) -> Tuple[bool, Optional[str]]:
        """Validate that generated code is safe and executable"""
        
        # Security checks
        forbidden_imports = ['os', 'subprocess', 'eval', 'exec', '__import__']
        for imp in func.imports:
            for forbidden in forbidden_imports:
                if forbidden in imp:
                    return False, f"Forbidden import: {forbidden}"
        
        # Check for dangerous constructs in code
        dangerous_patterns = ['eval(', 'exec(', '__import__(', 'compile(', 'open(']
        for pattern in dangerous_patterns:
            if pattern in func.source_code:
                return False, f"Dangerous pattern detected: {pattern}"
        
        # Try to compile the code
        try:
            compile(func.source_code, '<generated>', 'exec')
            return True, None
        except SyntaxError as e:
            return False, f"Syntax error: {e}"
        except Exception as e:
            return False, f"Compilation error: {e}"
    
    def execute_in_sandbox(self, func: GeneratedFunction, 
                          test_inputs: Dict[str, Any]) -> Tuple[bool, Any]:
        """Execute generated code in a sandboxed environment"""
        
        # Create a restricted namespace
        safe_builtins = {
            'abs': abs, 'min': min, 'max': max, 'sum': sum,
            'len': len, 'range': range, 'enumerate': enumerate,
            'int': int, 'float': float, 'str': str, 'bool': bool,
            'list': list, 'dict': dict, 'tuple': tuple, 'set': set
        }
        
        namespace = {
            '__builtins__': safe_builtins,
            'math': __import__('math'),
            'Union': type(int | float),  # For type hints
        }
        
        # Add numpy if needed
        if any('numpy' in imp or 'np' in imp for imp in func.imports):
            namespace['np'] = __import__('numpy')
            namespace['numpy'] = namespace['np']
        
        try:
            # Execute the code to define the function
            exec(func.source_code, namespace)
            
            # Find and call the function
            if func.name in namespace:
                result = namespace[func.name](**test_inputs)
                return True, result
            else:
                return False, "Function not found in namespace"
                
        except Exception as e:
            return False, f"Execution error: {e}"


class SchemaToCodeBridge:
    """Bridges theory schemas to executable code"""
    
    def __init__(self, llm_generator: Optional[LLMCodeGenerator] = None):
        self.generator = llm_generator or LLMCodeGenerator()
        self.generated_functions = {}
    
    def process_theory_schema(self, schema_path: str) -> Dict[str, GeneratedFunction]:
        """Process a complete theory schema and generate all formula code"""
        
        # Load schema
        with open(schema_path, 'r') as f:
            schema = json.load(f)
        
        theory_name = schema.get('theory_name', 'Unknown Theory')
        
        # Extract mathematical algorithms
        math_algos = schema.get('ontology', {}).get('mathematical_algorithms', {})
        
        generated = {}
        
        for algo_name, algo_spec in math_algos.items():
            if isinstance(algo_spec, dict) and 'formula' in algo_spec:
                logger.info(f"Generating code for {algo_name}")
                
                # Add name to spec
                algo_spec['name'] = algo_name
                
                # Generate code
                func = self.generator.generate_formula_code(algo_spec, theory_name)
                
                # Validate
                is_valid, error = self.generator.validate_generated_code(func)
                if is_valid:
                    generated[algo_name] = func
                    logger.info(f"Successfully generated {algo_name}")
                else:
                    logger.error(f"Validation failed for {algo_name}: {error}")
        
        self.generated_functions = generated
        return generated
    
    def create_theory_module(self, module_name: str = "generated_theory") -> str:
        """Create a complete Python module from generated functions"""
        
        if not self.generated_functions:
            raise ValueError("No functions generated yet")
        
        # Collect all imports
        all_imports = set()
        for func in self.generated_functions.values():
            all_imports.update(func.imports)
        
        # Build module
        module_lines = [
            f'"""Auto-generated theory implementation module"""',
            '',
            '# Imports'
        ]
        module_lines.extend(sorted(all_imports))
        module_lines.append('')
        
        # Add each function
        for name, func in self.generated_functions.items():
            module_lines.append(f'# {name}')
            module_lines.append(func.source_code)
            module_lines.append('')
        
        return '\n'.join(module_lines)
    
    def save_module(self, filepath: str) -> None:
        """Save the generated module to a file"""
        module_code = self.create_theory_module()
        with open(filepath, 'w') as f:
            f.write(module_code)
        logger.info(f"Saved generated module to {filepath}")


def test_code_generation():
    """Test the code generation with a real formula"""
    
    # Example formula specification
    formula_spec = {
        'name': 'prospect_value',
        'formula': 'V = Σ w(p_i) * v(x_i) for all outcomes',
        'parameters': {
            'outcomes': 'List of possible outcomes',
            'probabilities': 'Probabilities for each outcome',
            'reference_point': 'Reference point for gains/losses'
        },
        'input_requirements': ['outcomes', 'probabilities', 'reference_point'],
        'output': 'Overall prospect value'
    }
    
    generator = LLMCodeGenerator()
    func = generator.generate_formula_code(formula_spec, "Prospect Theory")
    
    print("Generated Function:")
    print(func.source_code)
    
    # Validate
    is_valid, error = generator.validate_generated_code(func)
    print(f"\nValidation: {'✓ Passed' if is_valid else f'✗ Failed: {error}'}")
    
    # Test execution
    if is_valid:
        test_inputs = {
            'outcomes': [100, -50],
            'probabilities': [0.7, 0.3],
            'reference_point': 0
        }
        
        success, result = generator.execute_in_sandbox(func, test_inputs)
        print(f"\nExecution: {'✓ Success' if success else '✗ Failed'}")
        if success:
            print(f"Result: {result}")


if __name__ == "__main__":
    test_code_generation()