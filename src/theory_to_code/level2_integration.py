#!/usr/bin/env python3
"""
Level 2 (ALGORITHMS) Integration with Theory-to-Code System

Extends the existing integrated system to support Level 2 algorithmic components
alongside Level 1 mathematical formulas.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .llm_code_generator import LLMCodeGenerator, GeneratedFunction
from .algorithm_generator import AlgorithmGenerator, GeneratedAlgorithm
from .algorithm_executor import AlgorithmExecutor, AlgorithmExecutionResult
from .structured_extractor import StructuredParameterExtractor, ResolvedParameters
from .simple_executor import SimpleExecutor, ExecutionResult

logger = logging.getLogger(__name__)


@dataclass
class TheoryComponent:
    """Represents a component of a theory (formula or algorithm)"""
    level: int  # 1 = formula, 2 = algorithm, 3 = procedure, etc.
    name: str
    component_type: str  # "formula", "algorithm", "procedure", etc.
    generated_code: Union[GeneratedFunction, GeneratedAlgorithm]
    validated: bool
    test_cases: List[Dict[str, Any]]


@dataclass
class EnhancedTheoryAnalysis:
    """Enhanced analysis result supporting multiple component levels"""
    theory_name: str
    timestamp: datetime
    input_text: str
    components_found: Dict[str, List[str]]  # level -> component names
    extracted_parameters: List[Dict[str, Any]]
    computational_results: Dict[str, Any]
    insights: str
    confidence_score: float
    execution_metadata: Dict[str, Any]


class Level2IntegratedSystem:
    """Enhanced system supporting both Level 1 (formulas) and Level 2 (algorithms)"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        # Initialize all generators and executors
        self.formula_generator = LLMCodeGenerator(api_key=self.api_key)
        self.algorithm_generator = AlgorithmGenerator(api_key=self.api_key)
        self.parameter_extractor = StructuredParameterExtractor()
        
        # Executors for different component types
        self.formula_executor = SimpleExecutor()
        self.algorithm_executor = AlgorithmExecutor()
        
        # Storage for generated components
        self.theory_components = {}  # theory_name -> {level -> [components]}
    
    def load_and_compile_theory(self, schema_path: str) -> bool:
        """Load theory schema and generate all types of components"""
        
        logger.info(f"Loading enhanced theory schema from {schema_path}")
        
        # Load schema
        with open(schema_path, 'r') as f:
            schema = json.load(f)
        
        theory_name = Path(schema_path).stem.replace('_schema', '')
        
        # Initialize component storage
        self.theory_components[theory_name] = {
            1: [],  # Level 1: Formulas
            2: [],  # Level 2: Algorithms
            3: [],  # Level 3: Procedures (future)
            4: [],  # Level 4: Rules (future)
            5: [],  # Level 5: Sequences (future)
            6: []   # Level 6: Frameworks (future)
        }
        
        components_generated = 0
        
        # Generate Level 1 components (formulas)
        components_generated += self._generate_level1_components(schema, theory_name)
        
        # Generate Level 2 components (algorithms)
        components_generated += self._generate_level2_components(schema, theory_name)
        
        if components_generated == 0:
            logger.error("No components generated from schema")
            return False
        
        logger.info(f"Successfully compiled {theory_name} with {components_generated} components")
        return True
    
    def _generate_level1_components(self, schema: Dict[str, Any], theory_name: str) -> int:
        """Generate Level 1 (formula) components"""
        
        components_generated = 0
        
        # Extract mathematical algorithms/formulas
        math_algorithms = schema.get('ontology', {}).get('mathematical_algorithms', {})
        if not math_algorithms:
            # Try alternative schema structure
            algorithms_section = schema.get('algorithms', {})
            math_algorithms = algorithms_section.get('mathematical', {})
        
        for formula_name, formula_spec in math_algorithms.items():
            if isinstance(formula_spec, dict) and 'formula' in formula_spec:
                try:
                    logger.info(f"Generating Level 1 component: {formula_name}")
                    
                    # Add name to spec
                    formula_spec['name'] = formula_name
                    
                    # Generate formula function
                    generated_func = self.formula_generator.generate_formula_code(
                        formula_spec, theory_name
                    )
                    
                    # Validate
                    is_valid, error = self.formula_generator.validate_generated_code(generated_func)
                    
                    if is_valid:
                        component = TheoryComponent(
                            level=1,
                            name=formula_name,
                            component_type="formula",
                            generated_code=generated_func,
                            validated=True,
                            test_cases=self._create_formula_test_cases(formula_spec)
                        )
                        
                        self.theory_components[theory_name][1].append(component)
                        components_generated += 1
                        logger.info(f"✓ Generated Level 1 component: {formula_name}")
                    else:
                        logger.error(f"✗ Level 1 validation failed for {formula_name}: {error}")
                        
                except Exception as e:
                    logger.error(f"Error generating Level 1 component {formula_name}: {e}")
        
        return components_generated
    
    def _generate_level2_components(self, schema: Dict[str, Any], theory_name: str) -> int:
        """Generate Level 2 (algorithm) components"""
        
        components_generated = 0
        
        # Extract algorithmic procedures
        algorithms_section = schema.get('algorithms', {})
        
        # Look for computational/procedural algorithms
        algorithmic_specs = []
        
        # Check different possible sections
        if 'computational' in algorithms_section:
            algorithmic_specs.extend(algorithms_section['computational'])
        if 'procedural' in algorithms_section:
            algorithmic_specs.extend(algorithms_section['procedural'])
        if 'iterative' in algorithms_section:
            algorithmic_specs.extend(algorithms_section['iterative'])
        
        # Also check for graph/network algorithms
        if 'network' in algorithms_section:
            algorithmic_specs.extend(algorithms_section['network'])
        
        # Create algorithm specs from description if none found
        if not algorithmic_specs:
            algorithmic_specs = self._infer_algorithms_from_theory(schema, theory_name)
        
        for algo_spec in algorithmic_specs:
            if isinstance(algo_spec, dict):
                try:
                    algo_name = algo_spec.get('name', f"{theory_name}_algorithm")
                    logger.info(f"Generating Level 2 component: {algo_name}")
                    
                    # Generate algorithm class
                    generated_algo = self.algorithm_generator.generate_algorithm_class(
                        algo_spec, theory_name
                    )
                    
                    # Validate
                    is_valid, error = self.algorithm_generator.validate_generated_algorithm(generated_algo)
                    
                    if is_valid:
                        component = TheoryComponent(
                            level=2,
                            name=algo_name,
                            component_type="algorithm",
                            generated_code=generated_algo,
                            validated=True,
                            test_cases=self._create_algorithm_test_cases(algo_spec)
                        )
                        
                        self.theory_components[theory_name][2].append(component)
                        components_generated += 1
                        logger.info(f"✓ Generated Level 2 component: {algo_name}")
                    else:
                        logger.error(f"✗ Level 2 validation failed for {algo_name}: {error}")
                        
                except Exception as e:
                    logger.error(f"Error generating Level 2 component: {e}")
        
        return components_generated
    
    def _infer_algorithms_from_theory(self, schema: Dict[str, Any], theory_name: str) -> List[Dict[str, Any]]:
        """Infer possible algorithms from theory description"""
        
        # Get description from multiple possible sources
        theory_description = ""
        if 'description' in schema:
            theory_description += schema['description'] + " "
        if 'telos' in schema and 'primary_purpose' in schema['telos']:
            theory_description += schema['telos']['primary_purpose'] + " "
        if 'theory_metadata' in schema and 'original_purpose' in schema['theory_metadata']:
            theory_description += schema['theory_metadata']['original_purpose'] + " "
        
        theory_description = theory_description.lower()
        theory_entities = schema.get('theoretical_structure', {}).get('entities', [])
        
        # Also check the entire schema content for keywords
        schema_text = str(schema).lower()
        
        inferred_algorithms = []
        
        # Check for common algorithmic patterns in both description and full schema
        search_text = theory_description + " " + schema_text
        
        if any(keyword in search_text for keyword in ['influence', 'propagation', 'network', 'social']):
            inferred_algorithms.append({
                'name': f"{theory_name.replace(' ', '_')}_influence_calculator",
                'description': f"Calculate influence propagation in {theory_name}",
                'algorithm_type': 'graph',
                'parameters': {
                    'damping_factor': 0.85,
                    'max_iterations': 100
                }
            })
        
        if any(keyword in search_text for keyword in ['equilibrium', 'balance', 'stability']):
            inferred_algorithms.append({
                'name': f"{theory_name.replace(' ', '_')}_equilibrium_finder",
                'description': f"Find equilibrium states in {theory_name}",
                'algorithm_type': 'iterative',
                'parameters': {
                    'max_iterations': 1000,
                    'tolerance': 1e-6
                }
            })
        
        if any(keyword in search_text for keyword in ['simulation', 'agent', 'behavior']):
            inferred_algorithms.append({
                'name': f"{theory_name.replace(' ', '_')}_behavior_simulator",
                'description': f"Simulate behavioral patterns in {theory_name}",
                'algorithm_type': 'simulation',
                'parameters': {
                    'n_simulations': 1000,
                    'random_seed': None
                }
            })
        
        return inferred_algorithms
    
    def _create_formula_test_cases(self, formula_spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create test cases for formula components"""
        
        # Basic test cases based on formula parameters
        test_cases = []
        
        parameters = formula_spec.get('parameters', {})
        
        if 'outcomes' in str(parameters).lower():
            test_cases.extend([
                {'outcome_values': [100, -50], 'reference_point': 0},
                {'outcome_values': [50, 25], 'reference_point': 0},
                {'outcome_values': [-20, -100], 'reference_point': 0}
            ])
        
        if 'probabilities' in str(parameters).lower():
            test_cases.extend([
                {'objective_probabilities': [0.5, 0.5]},
                {'objective_probabilities': [0.7, 0.3]},
                {'objective_probabilities': [0.9, 0.1]}
            ])
        
        # Default test case if none specific
        if not test_cases:
            test_cases.append({'x': 1.0, 'reference_point': 0})
        
        return test_cases
    
    def _create_algorithm_test_cases(self, algo_spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create test cases for algorithm components"""
        
        test_cases = []
        algo_type = algo_spec.get('algorithm_type', 'iterative')
        
        if algo_type == 'graph':
            # Graph algorithm test cases
            test_cases.extend([
                {
                    'adjacency_matrix': [[0, 1, 1], [1, 0, 1], [1, 1, 0]],
                    'max_iterations': 50,
                    'tolerance': 1e-6
                },
                {
                    'adjacency_matrix': [[0, 1, 0, 0], [0, 0, 1, 1], [1, 0, 0, 1], [0, 0, 0, 0]],
                    'damping_factor': 0.85
                }
            ])
        
        elif algo_type == 'iterative':
            # Iterative algorithm test cases
            test_cases.extend([
                {
                    'data': [1.0, 2.0, 3.0],
                    'max_iterations': 100,
                    'tolerance': 1e-6
                },
                {
                    'data': {'initial_value': 1.0, 'target': 2.0},
                    'max_iterations': 50
                }
            ])
        
        elif algo_type == 'simulation':
            # Simulation test cases
            test_cases.extend([
                {
                    'parameters': {'param1': 0.5, 'param2': 1.0},
                    'n_simulations': 100,
                    'random_seed': 42
                }
            ])
        
        elif algo_type == 'optimization':
            # Optimization test cases
            test_cases.extend([
                {
                    'initial_guess': [1.0, 1.0],
                    'max_iterations': 100,
                    'tolerance': 1e-6
                }
            ])
        
        return test_cases
    
    def analyze_text(self, text: str, theory_name: str) -> EnhancedTheoryAnalysis:
        """Analyze text using both Level 1 and Level 2 components"""
        
        start_time = datetime.now()
        
        if theory_name not in self.theory_components:
            raise ValueError(f"Theory '{theory_name}' not loaded")
        
        # Get theory components
        theory_data = self.theory_components[theory_name]
        
        # Extract parameters from text
        schema_path = self._get_schema_path(theory_name)
        with open(schema_path, 'r') as f:
            schema = json.load(f)
        
        text_schema = self.parameter_extractor.extract_text_schema(text, schema)
        resolved_params = self.parameter_extractor.resolve_parameters(text_schema)
        
        # Execute all components
        all_results = {}
        components_found = {}
        
        # Execute Level 1 components (formulas)
        level1_results = self._execute_level1_components(
            theory_data[1], resolved_params
        )
        all_results.update(level1_results)
        components_found['Level 1 (Formulas)'] = [c.name for c in theory_data[1]]
        
        # Execute Level 2 components (algorithms)
        level2_results = self._execute_level2_components(
            theory_data[2], resolved_params, text
        )
        all_results.update(level2_results)
        components_found['Level 2 (Algorithms)'] = [c.name for c in theory_data[2]]
        
        # Generate insights
        insights = self._generate_enhanced_insights(all_results, schema, components_found)
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return EnhancedTheoryAnalysis(
            theory_name=theory_name,
            timestamp=datetime.now(),
            input_text=text,
            components_found=components_found,
            extracted_parameters=[p.model_dump() for p in resolved_params],
            computational_results=all_results,
            insights=insights,
            confidence_score=text_schema.confidence,
            execution_metadata={
                'execution_time_seconds': execution_time,
                'level1_components': len(theory_data[1]),
                'level2_components': len(theory_data[2]),
                'total_components': len(theory_data[1]) + len(theory_data[2])
            }
        )
    
    def _execute_level1_components(self, components: List[TheoryComponent], 
                                  resolved_params: List[ResolvedParameters]) -> Dict[str, Any]:
        """Execute Level 1 formula components"""
        
        results = {}
        
        for component in components:
            if isinstance(component.generated_code, GeneratedFunction):
                
                # Execute for each parameter set
                component_results = {}
                
                for params in resolved_params:
                    # Map parameters to function inputs
                    inputs = self._map_parameters_to_function(component.name, params)
                    
                    # Execute formula
                    result = self.formula_executor.execute_module_function(
                        component.generated_code.source_code,
                        component.generated_code.name,
                        inputs
                    )
                    
                    component_results[params.prospect_name] = {
                        'success': result.success,
                        'value': result.result if result.success else None,
                        'error': result.error,
                        'execution_time': result.execution_time,
                        'component_level': 1,
                        'component_type': 'formula'
                    }
                
                results[f"Level1_{component.name}"] = component_results
        
        return results
    
    def _execute_level2_components(self, components: List[TheoryComponent],
                                  resolved_params: List[ResolvedParameters],
                                  text: str) -> Dict[str, Any]:
        """Execute Level 2 algorithm components"""
        
        results = {}
        
        for component in components:
            if isinstance(component.generated_code, GeneratedAlgorithm):
                
                # Execute for each parameter set (matching Level 1 structure)
                component_results = {}
                
                for params in resolved_params:
                    # Prepare algorithm inputs
                    inputs = self._prepare_algorithm_inputs(component, [params], text)
                    
                    # Execute algorithm
                    result = self.algorithm_executor.execute_algorithm(
                        component.generated_code.source_code,
                        component.generated_code.class_name,
                        inputs
                    )
                    
                    component_results[params.prospect_name] = {
                        'success': result.success,
                        'value': result.result,
                        'error': result.error,
                        'execution_time': result.execution_time,
                        'iterations': result.iterations,
                        'converged': result.converged,
                        'component_level': 2,
                        'component_type': 'algorithm',
                        'metadata': result.metadata
                    }
                
                results[f"Level2_{component.name}"] = component_results
        
        return results
    
    def _prepare_algorithm_inputs(self, component: TheoryComponent,
                                 resolved_params: List[ResolvedParameters],
                                 text: str) -> Dict[str, Any]:
        """Prepare inputs for algorithm execution"""
        
        algo_type = component.generated_code.algorithm_type
        algorithm_name = component.name.lower()
        
        # All generated algorithms expect 'data' parameter - prepare appropriate data structure
        if algo_type == 'graph' or 'influence' in algorithm_name:
            # Provide graph data structure
            data = {
                'adjacency_matrix': [[0, 1, 1], [1, 0, 1], [1, 1, 0]],  # Example graph
                'node_names': ['Strategy A', 'Strategy B', 'Status Quo'],
                'damping_factor': 0.85
            }
        
        elif algo_type == 'iterative' or 'equilibrium' in algorithm_name:
            # Provide iterative calculation data
            data = {
                'outcomes': [p.outcomes for p in resolved_params],
                'probabilities': [p.probabilities for p in resolved_params],
                'tolerance': 1e-6
            }
        
        elif algo_type == 'simulation' or 'behavior' in algorithm_name:
            # Provide simulation parameters
            data = {
                'n_prospects': len(resolved_params),
                'text_complexity': len(text.split()),
                'parameters': [p.model_dump() for p in resolved_params],
                'n_simulations': 100,
                'random_seed': 42
            }
        
        else:
            # Default data structure
            data = {
                'parameters': [p.model_dump() for p in resolved_params],
                'text': text,
                'theory': 'prospect_theory'
            }
        
        # Return only the 'data' parameter as that's what the generated algorithms expect
        return {
            'data': data
        }
    
    def _infer_method_inputs(self, component: TheoryComponent, resolved_params: List[ResolvedParameters]) -> Dict[str, Any]:
        """Infer method inputs by examining the calculate method signature"""
        
        import re
        
        # Extract calculate method signature
        code = component.generated_code.source_code
        calc_pattern = r'def calculate\(self[^)]*\):'
        calc_match = re.search(calc_pattern, code)
        
        if calc_match:
            calc_line = calc_match.group()
            # Look for parameter names (excluding 'self')
            param_pattern = r'(\w+):\s*\w+'
            params = re.findall(param_pattern, calc_line)
            params = [p for p in params if p != 'self']
            
            # Prepare inputs based on detected parameters
            inputs = {}
            for param in params:
                if param in ['data', 'input_data']:
                    inputs[param] = [p.outcomes for p in resolved_params]
                elif param in ['graph', 'adjacency_matrix', 'network']:
                    inputs[param] = [[0, 1, 1], [1, 0, 1], [1, 1, 0]]
                elif param in ['parameters', 'params']:
                    inputs[param] = {'n_prospects': len(resolved_params)}
                else:
                    # Generic fallback
                    inputs[param] = [p.model_dump() for p in resolved_params]
            
            return inputs
        
        # Ultimate fallback
        return {'data': resolved_params[0].model_dump() if resolved_params else {}}
    
    def _map_parameters_to_function(self, func_name: str, params: ResolvedParameters) -> Dict[str, Any]:
        """Map resolved parameters to function inputs (same as Level 1 system)"""
        
        if 'value' in func_name.lower() and 'prospect' not in func_name.lower():
            return {
                'outcome_values': params.outcomes,
                'reference_point': params.reference_point
            }
        elif 'probability' in func_name.lower() and 'weight' in func_name.lower():
            return {
                'objective_probabilities': params.probabilities,
                'gamma': 0.61
            }
        elif 'prospect' in func_name.lower() or 'evaluat' in func_name.lower():
            return {
                'outcome_values': params.outcomes,
                'probabilities': params.probabilities,
                'reference_point': params.reference_point
            }
        
        return params.model_dump()
    
    def _generate_enhanced_insights(self, results: Dict[str, Any], 
                                   schema: Dict[str, Any],
                                   components_found: Dict[str, List[str]]) -> str:
        """Generate insights from both Level 1 and Level 2 results"""
        
        insights = []
        
        # Component summary
        total_components = sum(len(comps) for comps in components_found.values())
        insights.append(f"Analysis completed using {total_components} theory components:")
        
        for level, comp_names in components_found.items():
            if comp_names:
                insights.append(f"  {level}: {len(comp_names)} components")
        
        # Level 1 insights
        level1_results = {k: v for k, v in results.items() if k.startswith('Level1_')}
        if level1_results:
            insights.append("\nLevel 1 (Formula) Results:")
            for comp_name, comp_results in level1_results.items():
                successful_calcs = sum(1 for r in comp_results.values() if r['success'])
                insights.append(f"  {comp_name}: {successful_calcs}/{len(comp_results)} calculations successful")
        
        # Level 2 insights  
        level2_results = {k: v for k, v in results.items() if k.startswith('Level2_')}
        if level2_results:
            insights.append("\nLevel 2 (Algorithm) Results:")
            for comp_name, comp_results in level2_results.items():
                # Count successful executions across all prospects
                successful_calcs = sum(1 for r in comp_results.values() if r['success'])
                total_calcs = len(comp_results)
                
                if successful_calcs > 0:
                    # Show success rate and convergence info from first successful result
                    first_success = next((r for r in comp_results.values() if r['success']), None)
                    if first_success:
                        convergence = "converged" if first_success.get('converged') else "did not converge"
                        iterations = first_success.get('iterations', 'unknown')
                        insights.append(f"  {comp_name}: {successful_calcs}/{total_calcs} successful, {convergence} in {iterations} iterations")
                    else:
                        insights.append(f"  {comp_name}: {successful_calcs}/{total_calcs} successful")
                else:
                    insights.append(f"  {comp_name}: execution failed")
        
        return '\n'.join(insights)
    
    def _get_schema_path(self, theory_name: str) -> str:
        """Get schema path for theory (placeholder implementation)"""
        return f"/home/brian/projects/Digimons/config/schemas/{theory_name}_schema.json"


def test_level2_integration():
    """Test the Level 2 integration system"""
    
    print("=" * 60)
    print("LEVEL 2 INTEGRATION TEST")
    print("=" * 60)
    
    # Initialize system
    system = Level2IntegratedSystem()
    
    # Test with prospect theory (should have both levels)
    schema_path = "/home/brian/projects/Digimons/config/schemas/prospect_theory_schema.json"
    
    if not os.path.exists(schema_path):
        print(f"Schema file not found: {schema_path}")
        return
    
    print("Loading and compiling theory with Level 1 & 2 components...")
    success = system.load_and_compile_theory(schema_path)
    
    if not success:
        print("Failed to compile theory!")
        return
    
    print("✓ Theory compiled successfully")
    
    # Show what was generated
    theory_components = system.theory_components.get('prospect_theory', {})
    for level, components in theory_components.items():
        if components:
            print(f"Level {level}: {len(components)} components")
            for comp in components:
                print(f"  - {comp.name} ({comp.component_type})")
    
    # Test analysis
    test_text = """
    The company must choose between two investment strategies:
    
    Strategy A: 70% chance of $200,000 profit, 30% chance of $50,000 loss
    Strategy B: Guaranteed $120,000 profit
    
    The board needs to make this decision considering risk preferences.
    """
    
    print(f"\nAnalyzing text with enhanced system...")
    
    try:
        analysis = system.analyze_text(test_text, "prospect_theory")
        
        print("\nAnalysis Results:")
        print(f"Components used: {analysis.components_found}")
        print(f"Execution time: {analysis.execution_metadata['execution_time_seconds']:.2f}s")
        print(f"\nInsights:\n{analysis.insights}")
        
    except Exception as e:
        print(f"Analysis failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_level2_integration()