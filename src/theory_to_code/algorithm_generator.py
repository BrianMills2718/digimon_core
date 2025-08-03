#!/usr/bin/env python3
"""
Level 2 (ALGORITHMS) Implementation for Theory-to-Code System

Generates computational algorithm classes from theory descriptions.
Handles iterative calculations, convergence criteria, and complex computations.
"""

import os
import json
import ast
import yaml
import logging
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass
import numpy as np

# For LLM integration
try:
    import litellm
except ImportError:
    print("Warning: litellm not available. Install with: pip install litellm")
    litellm = None

logger = logging.getLogger(__name__)

@dataclass
class GeneratedAlgorithm:
    """Represents an LLM-generated algorithm class"""
    name: str
    source_code: str
    class_name: str
    methods: List[str]
    parameters: Dict[str, Any]
    imports: List[str]
    docstring: str
    algorithm_type: str  # "iterative", "optimization", "graph", "simulation"


class AlgorithmGenerator:
    """Generates executable algorithm classes from theory descriptions"""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
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
                self.model = get_model("algorithm_generator")
            except ImportError:
                # Fallback to config file
                try:
                    config_path = os.path.join(os.path.dirname(__file__), '../../config/default.yaml')
                    with open(config_path, 'r') as f:
                        config = yaml.safe_load(f)
                    self.model = config.get('llm', {}).get('default_model', 'gemini/gemini-2.0-flash-exp')
                except (FileNotFoundError, KeyError):
                    self.model = "gemini/gemini-2.0-flash-exp"
        else:
            self.model = model
        
        self.api_key = api_key or os.getenv("OPENAI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        
        # Algorithm templates for different types
        self.algorithm_templates = {
            "iterative": self._get_iterative_template(),
            "graph": self._get_graph_template(),
            "optimization": self._get_optimization_template(),
            "simulation": self._get_simulation_template()
        }
    
    def generate_algorithm_class(self, algorithm_spec: Dict[str, Any], 
                                theory_name: str) -> GeneratedAlgorithm:
        """Generate Python algorithm class from specification"""
        
        # Determine algorithm type
        algo_type = self._classify_algorithm_type(algorithm_spec)
        
        # Build the prompt
        prompt = self._build_algorithm_prompt(algorithm_spec, theory_name, algo_type)
        
        # Call LLM or use template
        if self.api_key and litellm:
            response = self._call_llm(prompt, algorithm_spec, theory_name, algo_type)
        else:
            response = self._generate_from_template(algorithm_spec, algo_type)
        
        # Parse the generated code
        return self._parse_generated_algorithm(response, algorithm_spec, algo_type)
    
    def _classify_algorithm_type(self, spec: Dict[str, Any]) -> str:
        """Classify the algorithm type based on specification"""
        
        description = spec.get('description', '').lower()
        name = spec.get('name', '').lower()
        
        # Check for keywords to classify
        if any(keyword in description or keyword in name for keyword in 
               ['pagerank', 'influence', 'propagation', 'network', 'centrality', 'graph']):
            return "graph"
        elif any(keyword in description or keyword in name for keyword in
                ['iterate', 'converge', 'equilibrium', 'stability']):
            return "iterative"
        elif any(keyword in description or keyword in name for keyword in
                ['optimize', 'maximize', 'minimize', 'search', 'best']):
            return "optimization"
        elif any(keyword in description or keyword in name for keyword in
                ['simulate', 'monte carlo', 'random', 'agent']):
            return "simulation"
        else:
            return "iterative"  # Default
    
    def _build_algorithm_prompt(self, spec: Dict[str, Any], theory_name: str, 
                               algo_type: str) -> str:
        """Build detailed prompt for algorithm generation"""
        
        prompt = f"""Generate a Python algorithm class for this {theory_name} computational procedure.

Algorithm Name: {spec.get('name', 'algorithm')}
Type: {algo_type}
Description: {spec.get('description', '')}
Parameters: {json.dumps(spec.get('parameters', {}), indent=2)}
Steps: {spec.get('steps', [])}
Convergence Criteria: {spec.get('convergence', {})}

Requirements for {algo_type} algorithm:
1. Create a comprehensive Python class with proper __init__ method
2. Include convergence checking and iteration history tracking
3. Implement state management for intermediate results
4. Add validation for inputs and parameters
5. Include comprehensive error handling
6. Use type hints throughout
7. Add detailed docstrings for the class and all methods
8. Follow these patterns:

For iterative algorithms:
- track_history: bool parameter to save iteration states
- max_iterations: int parameter for safety
- tolerance: float parameter for convergence
- converged: bool property indicating convergence status

For graph algorithms:
- Support both adjacency matrix and edge list inputs
- Normalize inputs appropriately
- Handle disconnected components gracefully
- Return structured results with metadata

For optimization algorithms:
- Support multiple objective functions
- Include parameter bounds checking
- Track optimization progress
- Return optimization metadata

9. Use numpy for numerical computations
10. Include example usage in docstring

Format your response as:
```python
import numpy as np
from typing import Dict, List, Optional, Any, Union
import logging

class AlgorithmClassName:
    \"\"\"
    Comprehensive docstring with example usage
    \"\"\"
    
    def __init__(self, ...):
        # Initialize parameters
        pass
    
    def calculate(self, ...):
        \"\"\"Main calculation method\"\"\"
        # Implementation
        pass
    
    def _validate_inputs(self, ...):
        \"\"\"Input validation\"\"\"
        pass
    
    def _check_convergence(self, ...):
        \"\"\"Convergence checking\"\"\"
        pass
```

Only return the Python code, no explanations."""

        return prompt
    
    def _call_llm(self, prompt: str, algorithm_spec: Dict[str, Any] = None, 
                  theory_name: str = None, algo_type: str = None) -> str:
        """Call the LLM API and return response"""
        
        try:
            response = litellm.completion(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert Python programmer specializing in algorithm implementation and scientific computing."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=2000  # Longer for algorithm classes
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"LLM API call failed: {e}")
            # Fallback to template with proper spec and algorithm type
            if algorithm_spec and algo_type:
                spec_with_theory = {
                    'name': algorithm_spec.get('name', 'Algorithm'),
                    'description': algorithm_spec.get('description', 'Generated algorithm'),
                    'theory_name': theory_name or 'Theory',
                    'parameters': algorithm_spec.get('parameters', {})
                }
                return self._generate_from_template(spec_with_theory, algo_type)
            else:
                # Ultimate fallback
                return self._generate_from_template({'name': 'Algorithm', 'description': 'Generated algorithm'}, 'iterative')
    
    def _generate_from_template(self, spec: Dict[str, Any], algo_type: str) -> str:
        """Generate algorithm from template when LLM unavailable"""
        
        template = self.algorithm_templates.get(algo_type, 
                                               self.algorithm_templates["iterative"])
        
        # Customize template with specification details
        class_name = spec.get('name', 'Algorithm').replace(' ', '').title()
        description = spec.get('description', 'Generated algorithm')
        
        return template.format(
            class_name=class_name,
            description=description,
            theory_name=spec.get('theory_name', 'Theory')
        )
    
    def _get_iterative_template(self) -> str:
        """Template for iterative algorithms - Equilibrium Finding"""
        return '''import numpy as np
from typing import Dict, List, Optional, Any, Union
import logging

class {class_name}:
    """
    {description}
    
    Implements an iterative equilibrium-finding algorithm for prospect theory analysis.
    Finds stable states in decision-making dynamics.
    
    Example usage:
        algorithm = {class_name}()
        result = algorithm.calculate(data)
        print(f"Converged: {{result['converged']}}")
        print(f"Equilibrium: {{result['value']}}")
    """
    
    def __init__(self, max_iterations: int = 100, tolerance: float = 1e-6):
        self.max_iterations = max_iterations
        self.tolerance = tolerance
        self.iteration_history = []
        self.converged = False
    
    def calculate(self, data: Union[np.ndarray, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Find equilibrium state in prospect theory value dynamics
        
        Args:
            data: Dictionary containing outcomes, probabilities, and tolerance
            
        Returns:
            Dict containing equilibrium value, convergence status, and iterations
        """
        self._validate_inputs(data)
        
        # Extract data components
        outcomes = data.get('outcomes', [[0.5, -0.3], [0.2, -0.1]]) 
        probabilities = data.get('probabilities', [[0.7, 0.3], [0.8, 0.2]])
        
        # Initialize with first prospect value
        current_equilibrium = 0.5
        self.iteration_history = []
        
        for iteration in range(self.max_iterations):
            previous_equilibrium = current_equilibrium
            
            # Calculate weighted prospect values approaching equilibrium
            weighted_sum = 0.0
            total_weight = 0.0
            
            for i, (outcome_set, prob_set) in enumerate(zip(outcomes, probabilities)):
                for outcome, prob in zip(outcome_set, prob_set):
                    # Prospect theory value function: v(x) = x^0.88 for gains, -2.25*(-x)^0.88 for losses
                    if outcome >= 0:
                        value = pow(outcome, 0.88)
                    else:
                        value = -2.25 * pow(-outcome, 0.88)
                    
                    # Probability weighting: w(p) = p^0.61 / (p^0.61 + (1-p)^0.61)^(1/0.61)
                    gamma = 0.61
                    weight = pow(prob, gamma) / pow(pow(prob, gamma) + pow(1-prob, gamma), 1/gamma)
                    
                    weighted_sum += value * weight
                    total_weight += weight
            
            # Update equilibrium (dampened for stability)
            if total_weight > 0:
                target_value = weighted_sum / total_weight
                current_equilibrium = 0.8 * current_equilibrium + 0.2 * target_value
            
            # Calculate convergence delta
            delta = abs(current_equilibrium - previous_equilibrium)
            
            self.iteration_history.append({{
                'iteration': iteration,
                'equilibrium': current_equilibrium,
                'delta': delta
            }})
            
            # Check convergence
            if delta < self.tolerance:
                self.converged = True
                break
        
        return {{
            'value': current_equilibrium,
            'converged': self.converged,
            'iterations': iteration + 1,
            'equilibrium_history': self.iteration_history
        }}
    
    def _validate_inputs(self, data: Any) -> None:
        """Validate algorithm inputs"""
        if data is None:
            raise ValueError("Input data cannot be None")
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary")
    
    def _initialize_calculation(self, data: Any) -> Any:
        """Initialize the calculation with starting values"""
        if isinstance(data, np.ndarray):
            return np.ones_like(data) / len(data)
        else:
            return 0.0
    
    def _iteration_step(self, current_value: Any, data: Any, iteration: int) -> Any:
        """Perform one iteration of the algorithm"""
        # Placeholder - implement specific algorithm logic
        return current_value * 0.9 + 0.1  # Simple example
    
    def _calculate_delta(self, current: Any, previous: Any) -> float:
        """Calculate change between iterations"""
        if hasattr(current, '__len__') and hasattr(previous, '__len__'):
            return np.abs(np.array(current) - np.array(previous)).max()
        else:
            return abs(current - previous)
'''

    def _get_graph_template(self) -> str:
        """Template for graph algorithms - Influence Propagation"""
        return '''import numpy as np
from typing import Dict, List, Optional, Any, Union, Tuple
import logging

class {class_name}:
    """
    {description}
    
    Implements influence propagation algorithm for prospect theory network analysis.
    Models how decision preferences and risk attitudes spread through networks.
    
    Example usage:
        algorithm = {class_name}(damping_factor=0.85)
        adjacency_matrix = np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]])
        result = algorithm.calculate(adjacency_matrix)
        print(f"Node scores: {{result['scores']}}")
    """
    
    def __init__(self, damping_factor: float = 0.85, max_iterations: int = 100, 
                 tolerance: float = 1e-6):
        self.damping_factor = damping_factor
        self.max_iterations = max_iterations
        self.tolerance = tolerance
        self.iteration_history = []
        self.converged = False
    
    def calculate(self, data: Union[np.ndarray, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate influence propagation in prospect theory decision networks
        
        Args:
            data: Dictionary containing adjacency_matrix and node preferences
            
        Returns:
            Dict with influence scores, convergence info, and decision spread patterns
        """
        self._validate_inputs(data)
        
        # Extract network data
        adjacency_matrix = data.get('adjacency_matrix', [[0, 1, 1], [1, 0, 1], [1, 1, 0]])
        node_names = data.get('node_names', ['Node_A', 'Node_B', 'Node_C'])
        
        # Convert to numpy array if needed
        if not isinstance(adjacency_matrix, np.ndarray):
            adjacency_matrix = np.array(adjacency_matrix, dtype=float)
        
        n = len(adjacency_matrix)
        
        # Initialize influence scores with prospect theory bias toward losses
        # Start with loss-averse initial state (negative preference = 0.3, positive = 0.7)
        influence_scores = np.array([0.6, 0.4, 0.5])[:n]  # Risk preferences
        if len(influence_scores) < n:
            influence_scores = np.resize(influence_scores, n)
        
        # Create transition matrix for influence propagation
        row_sums = adjacency_matrix.sum(axis=1)
        transition_matrix = np.divide(adjacency_matrix, row_sums[:, np.newaxis], 
                                    out=np.zeros_like(adjacency_matrix), where=row_sums[:, np.newaxis]!=0)
        
        self.iteration_history = []
        
        for iteration in range(self.max_iterations):
            prev_scores = influence_scores.copy()
            
            # Influence propagation with prospect theory weighting
            # Loss aversion: negative influences spread faster (weight = 1.2)
            # Gain influences spread slower (weight = 0.8)
            propagated_influence = np.zeros(n)
            
            for i in range(n):
                neighbor_influence = 0.0
                for j in range(n):
                    if transition_matrix[i, j] > 0:
                        # Apply prospect theory weighting
                        neighbor_score = prev_scores[j]
                        if neighbor_score < 0.5:  # Loss-leaning influence
                            weight = 1.2  # Loss aversion amplification
                        else:  # Gain-leaning influence  
                            weight = 0.8   # Diminishing sensitivity
                        
                        neighbor_influence += transition_matrix[i, j] * neighbor_score * weight
                
                # Update with damping (mix of self-preference and network influence)
                propagated_influence[i] = (1 - self.damping_factor) * prev_scores[i] + self.damping_factor * neighbor_influence
            
            influence_scores = propagated_influence
            
            # Calculate convergence
            delta = np.abs(influence_scores - prev_scores).max()
            
            self.iteration_history.append({{
                'iteration': iteration,
                'influence_scores': influence_scores.copy(),
                'delta': delta
            }})
            
            if delta < self.tolerance:
                self.converged = True
                break
        
        return {{
            'value': influence_scores,
            'converged': self.converged,
            'iterations': iteration + 1,
            'influence_scores': influence_scores,
            'node_names': node_names,
            'history': self.iteration_history
        }}
    
    def _validate_inputs(self, data: Any) -> None:
        """Validate algorithm inputs"""
        if data is None:
            raise ValueError("Input data cannot be None")
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary")
    
    def _create_transition_matrix(self, adjacency_matrix: np.ndarray) -> np.ndarray:
        """Create transition matrix from adjacency matrix"""
        # Calculate out-degrees
        out_degree = adjacency_matrix.sum(axis=1)
        
        # Handle nodes with no outgoing edges
        out_degree[out_degree == 0] = 1
        
        # Create transition matrix
        transition_matrix = adjacency_matrix / out_degree[:, np.newaxis]
        
        return transition_matrix
'''

    def _get_optimization_template(self) -> str:
        """Template for optimization algorithms"""
        return '''import numpy as np
from typing import Dict, List, Optional, Any, Union, Callable
import logging

class {class_name}:
    """
    {description}
    
    Implements optimization algorithm for finding optimal solutions.
    
    Example usage:
        def objective(x):
            return -(x[0]**2 + x[1]**2)  # Maximize x^2 + y^2
        
        optimizer = {class_name}()
        result = optimizer.optimize(objective, initial_guess=[1.0, 1.0])
        print(f"Optimal value: {{result['optimal_value']}}")
    """
    
    def __init__(self, max_iterations: int = 1000, tolerance: float = 1e-6,
                 step_size: float = 0.01):
        self.max_iterations = max_iterations
        self.tolerance = tolerance
        self.step_size = step_size
        self.optimization_history = []
        self.converged = False
    
    def optimize(self, objective_function: Callable, 
                initial_guess: Union[List, np.ndarray],
                bounds: Optional[List[Tuple[float, float]]] = None) -> Dict[str, Any]:
        """
        Optimize the objective function
        
        Args:
            objective_function: Function to optimize
            initial_guess: Starting point for optimization
            bounds: Optional parameter bounds
            
        Returns:
            Dict with optimal solution, value, and metadata
        """
        self._validate_optimization_inputs(objective_function, initial_guess, bounds)
        
        x = np.array(initial_guess, dtype=float)
        self.optimization_history = []
        
        for iteration in range(self.max_iterations):
            # Calculate current objective value
            current_value = objective_function(x)
            
            # Calculate gradient (finite differences)
            gradient = self._calculate_gradient(objective_function, x)
            
            # Update solution
            x_new = x + self.step_size * gradient
            
            # Apply bounds if specified
            if bounds:
                x_new = self._apply_bounds(x_new, bounds)
            
            # Check convergence
            delta = np.linalg.norm(x_new - x)
            
            self.optimization_history.append({{
                'iteration': iteration,
                'x': x.copy(),
                'objective_value': current_value,
                'gradient_norm': np.linalg.norm(gradient),
                'delta': delta
            }})
            
            if delta < self.tolerance:
                self.converged = True
                break
            
            x = x_new
        
        final_value = objective_function(x)
        
        return {{
            'optimal_solution': x,
            'optimal_value': final_value,
            'converged': self.converged,
            'iterations': iteration + 1,
            'final_delta': delta,
            'history': self.optimization_history
        }}
    
    def _validate_optimization_inputs(self, objective_function: Callable, 
                                    initial_guess: Any, bounds: Any) -> None:
        """Validate optimization inputs"""
        if not callable(objective_function):
            raise TypeError("Objective function must be callable")
        
        if not hasattr(initial_guess, '__len__'):
            raise TypeError("Initial guess must be array-like")
    
    def _calculate_gradient(self, f: Callable, x: np.ndarray, 
                          eps: float = 1e-8) -> np.ndarray:
        """Calculate gradient using finite differences"""
        gradient = np.zeros_like(x)
        
        for i in range(len(x)):
            x_plus = x.copy()
            x_minus = x.copy()
            x_plus[i] += eps
            x_minus[i] -= eps
            
            gradient[i] = (f(x_plus) - f(x_minus)) / (2 * eps)
        
        return gradient
    
    def _apply_bounds(self, x: np.ndarray, 
                     bounds: List[Tuple[float, float]]) -> np.ndarray:
        """Apply parameter bounds"""
        x_bounded = x.copy()
        
        for i, (lower, upper) in enumerate(bounds):
            if i < len(x_bounded):
                x_bounded[i] = np.clip(x_bounded[i], lower, upper)
        
        return x_bounded
'''

    def _get_simulation_template(self) -> str:
        """Template for simulation algorithms"""
        return '''import numpy as np
from typing import Dict, List, Optional, Any, Union
import logging

class {class_name}:
    """
    {description}
    
    Implements simulation-based algorithm.
    
    Example usage:
        simulator = {class_name}(n_simulations=1000)
        result = simulator.simulate(parameters={{'param1': 0.5}})
        print(f"Mean result: {{result['mean']}}")
    """
    
    def __init__(self, n_simulations: int = 1000, random_seed: Optional[int] = None):
        self.n_simulations = n_simulations
        self.random_seed = random_seed
        if random_seed is not None:
            np.random.seed(random_seed)
        
        self.simulation_results = []
    
    def simulate(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run simulation with given parameters
        
        Args:
            parameters: Simulation parameters
            
        Returns:
            Dict with simulation results and statistics
        """
        self._validate_simulation_inputs(parameters)
        
        results = []
        
        for simulation in range(self.n_simulations):
            # Run single simulation
            result = self._single_simulation(parameters, simulation)
            results.append(result)
        
        # Calculate statistics
        results_array = np.array(results)
        
        return {{
            'results': results,
            'mean': np.mean(results_array),
            'std': np.std(results_array),
            'min': np.min(results_array),
            'max': np.max(results_array),
            'percentiles': {{
                '25th': np.percentile(results_array, 25),
                '50th': np.percentile(results_array, 50),
                '75th': np.percentile(results_array, 75)
            }},
            'n_simulations': self.n_simulations,
            'parameters': parameters
        }}
    
    def _validate_simulation_inputs(self, parameters: Dict[str, Any]) -> None:
        """Validate simulation inputs"""
        if not isinstance(parameters, dict):
            raise TypeError("Parameters must be a dictionary")
    
    def _single_simulation(self, parameters: Dict[str, Any], 
                          simulation_id: int) -> float:
        """Run a single simulation"""
        # Placeholder - implement specific simulation logic
        return np.random.normal(0, 1)  # Simple example
'''
    
    def _parse_generated_algorithm(self, code: str, spec: Dict[str, Any], 
                                  algo_type: str) -> GeneratedAlgorithm:
        """Parse generated algorithm code"""
        
        # Clean the code
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
        
        # Parse the class
        try:
            tree = ast.parse(clean_code)
            
            # Find the class definition
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_name = node.name
                    
                    # Extract methods
                    methods = [method.name for method in node.body 
                              if isinstance(method, ast.FunctionDef)]
                    
                    # Extract docstring
                    docstring = ast.get_docstring(node) or "Generated algorithm class"
                    
                    return GeneratedAlgorithm(
                        name=spec.get('name', 'algorithm'),
                        source_code=code,
                        class_name=class_name,
                        methods=methods,
                        parameters=spec.get('parameters', {}),
                        imports=imports,
                        docstring=docstring,
                        algorithm_type=algo_type
                    )
            
            # If no class found, create a wrapper
            class_name = spec.get('name', 'Algorithm').replace(' ', '').title()
            return GeneratedAlgorithm(
                name=spec.get('name', 'algorithm'),
                source_code=code,
                class_name=class_name,
                methods=[],
                parameters=spec.get('parameters', {}),
                imports=imports,
                docstring="Generated algorithm",
                algorithm_type=algo_type
            )
            
        except Exception as e:
            logger.error(f"Failed to parse generated algorithm: {e}")
            # Return basic structure
            return GeneratedAlgorithm(
                name="generated_algorithm",
                source_code=code,
                class_name="GeneratedAlgorithm",
                methods=[],
                parameters={},
                imports=imports,
                docstring="Generated algorithm",
                algorithm_type=algo_type
            )

    def validate_generated_algorithm(self, algorithm: GeneratedAlgorithm) -> Tuple[bool, Optional[str]]:
        """Validate that generated algorithm is safe and executable"""
        
        # Security checks
        forbidden_imports = ['os', 'subprocess', 'eval', 'exec', '__import__']
        for imp in algorithm.imports:
            for forbidden in forbidden_imports:
                if forbidden in imp:
                    return False, f"Forbidden import: {forbidden}"
        
        # Check for dangerous constructs
        dangerous_patterns = ['eval(', 'exec(', '__import__(', 'compile(', 'open(']
        for pattern in dangerous_patterns:
            if pattern in algorithm.source_code:
                return False, f"Dangerous pattern detected: {pattern}"
        
        # Try to compile the code
        try:
            compile(algorithm.source_code, '<generated>', 'exec')
            return True, None
        except SyntaxError as e:
            return False, f"Syntax error: {e}"
        except Exception as e:
            return False, f"Compilation error: {e}"


def test_algorithm_generation():
    """Test the algorithm generation with sample specifications"""
    
    # Test specifications for different algorithm types
    test_specs = [
        {
            "name": "social_influence_calculator",
            "description": "PageRank-style influence propagation in social networks",
            "algorithm_type": "graph",
            "parameters": {
                "damping_factor": 0.85,
                "max_iterations": 100,
                "tolerance": 1e-6
            },
            "steps": [
                "Initialize node scores uniformly",
                "Create transition matrix from adjacency matrix", 
                "Iteratively update scores",
                "Check for convergence"
            ]
        },
        {
            "name": "equilibrium_finder",
            "description": "Find stable equilibrium in dynamic system",
            "algorithm_type": "iterative",
            "parameters": {
                "max_iterations": 1000,
                "tolerance": 1e-8
            },
            "convergence": {
                "type": "absolute_difference",
                "threshold": 1e-8
            }
        }
    ]
    
    generator = AlgorithmGenerator()
    
    print("=" * 60)
    print("ALGORITHM GENERATOR TEST")
    print("=" * 60)
    
    for i, spec in enumerate(test_specs):
        print(f"\n{i+1}. Testing {spec['name']}...")
        
        # Generate algorithm
        algorithm = generator.generate_algorithm_class(spec, "Test Theory")
        
        print(f"   Class name: {algorithm.class_name}")
        print(f"   Type: {algorithm.algorithm_type}")
        print(f"   Methods: {algorithm.methods}")
        
        # Validate
        is_valid, error = generator.validate_generated_algorithm(algorithm)
        print(f"   Validation: {'✓ Passed' if is_valid else f'✗ Failed: {error}'}")
        
        if is_valid:
            print("   Generated code preview:")
            print("   " + "\n   ".join(algorithm.source_code.split('\n')[:10]))
            print("   ...")


if __name__ == "__main__":
    test_algorithm_generation()