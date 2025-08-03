#!/usr/bin/env python3
"""
Integrated Theory-to-Code System

Complete pipeline that:
1. Loads theory schemas
2. Generates executable code using LLMs
3. Extracts parameters from text using LLMs
4. Dynamically executes the analysis
5. Returns structured results
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

from .llm_code_generator import LLMCodeGenerator, SchemaToCodeBridge
from .structured_extractor import StructuredParameterExtractor, TextSchema, ResolvedParameters
from .simple_executor import SimpleExecutor, ExecutionResult

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TheoryAnalysis:
    """Complete analysis result"""
    theory_name: str
    timestamp: datetime
    input_text: str
    extracted_parameters: List[Dict[str, Any]]
    computational_results: Dict[str, Any]
    insights: str
    confidence_score: float
    execution_metadata: Dict[str, Any]


class IntegratedTheorySystem:
    """Complete system for theory-based text analysis"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        # Initialize components
        self.code_generator = LLMCodeGenerator(api_key=self.api_key)
        self.schema_bridge = SchemaToCodeBridge(self.code_generator)
        self.parameter_extractor = StructuredParameterExtractor()
        self.executor = SimpleExecutor()
        
        # Storage for generated code
        self.generated_theories = {}
    
    def load_and_compile_theory(self, schema_path: str) -> bool:
        """Load a theory schema and generate executable code"""
        
        logger.info(f"Loading theory schema from {schema_path}")
        
        # Generate code from schema
        generated_functions = self.schema_bridge.process_theory_schema(schema_path)
        
        if not generated_functions:
            logger.error("No functions generated from schema")
            return False
        
        # Create module
        module_code = self.schema_bridge.create_theory_module()
        
        # Store generated module
        theory_name = Path(schema_path).stem.replace('_schema', '')
        
        self.generated_theories[theory_name] = {
            'schema_path': schema_path,
            'functions': list(generated_functions.keys()),
            'module_code': module_code
        }
        logger.info(f"Successfully compiled {theory_name} with {len(generated_functions)} functions")
        
        return True
    
    def analyze_text(self, text: str, theory_name: str) -> TheoryAnalysis:
        """Analyze text using a compiled theory"""
        
        start_time = datetime.now()
        
        if theory_name not in self.generated_theories:
            raise ValueError(f"Theory '{theory_name}' not loaded")
        
        theory_info = self.generated_theories[theory_name]
        
        # Step 1: Extract text-schema from text
        logger.info("Extracting text-schema from text...")
        with open(theory_info['schema_path'], 'r') as f:
            schema = json.load(f)
        
        # Extract structured text-schema
        text_schema = self.parameter_extractor.extract_text_schema(text, schema)
        
        # Step 2: Resolve to computational parameters
        logger.info("Resolving parameters...")
        resolved_params = self.parameter_extractor.resolve_parameters(text_schema)
        
        # Step 3: Execute analysis for each prospect
        logger.info("Executing computational analysis...")
        all_results = {}
        module_code = theory_info['module_code']
        
        for params in resolved_params:
            # Execute each function for this prospect
            prospect_results = {}
            
            for func_name in theory_info['functions']:
                # Map parameters to function inputs
                inputs = self._map_parameters_to_function(func_name, params)
                
                # Execute function
                result = self.executor.execute_module_function(
                    module_code, func_name, inputs
                )
                
                prospect_results[func_name] = {
                    'success': result.success,
                    'value': result.result if result.success else None,
                    'error': result.error,
                    'execution_time': result.execution_time
                }
            
            # Store results
            all_results[params.prospect_name] = {
                'parameters': params.model_dump(),
                'results': prospect_results
            }
        
        # Step 3: Generate insights
        logger.info("Generating insights...")
        insights = self._generate_insights(all_results, schema)
        
        # Calculate execution time
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # Create analysis result
        analysis = TheoryAnalysis(
            theory_name=theory_name,
            timestamp=datetime.now(),
            input_text=text,
            extracted_parameters=[p.model_dump() for p in resolved_params],
            computational_results=all_results,
            insights=insights,
            confidence_score=text_schema.confidence,
            execution_metadata={
                'execution_time_seconds': execution_time,
                'num_prospects': len(resolved_params),
                'functions_executed': theory_info['functions'],
                'text_schema': text_schema.model_dump(),
                'extraction_notes': text_schema.extraction_notes
            }
        )
        
        return analysis
    
    def _map_parameters_to_function(self, func_name: str, params: ResolvedParameters) -> Dict[str, Any]:
        """Map resolved parameters to function inputs"""
        
        # Common mappings based on function name patterns
        if 'value' in func_name.lower() and 'prospect' not in func_name.lower():
            # Value function - pass all outcomes as list
            return {
                'outcome_values': params.outcomes,  # All outcomes as list
                'reference_point': params.reference_point
            }
        
        elif 'probability' in func_name.lower() and 'weight' in func_name.lower():
            # Probability weighting function
            return {
                'objective_probabilities': params.probabilities,
                'gamma': 0.61  # Default from theory for gains
            }
        
        elif 'prospect' in func_name.lower() or 'evaluat' in func_name.lower():
            # Full prospect evaluation
            return {
                'outcome_values': params.outcomes,  # Note: LLM used outcome_values
                'probabilities': params.probabilities,
                'reference_point': params.reference_point
            }
        
        # Default: pass all parameters
        return params.model_dump()
    
    def _process_execution_results(self, results: Dict[str, ExecutionResult]) -> Dict[str, Any]:
        """Process execution results into serializable format"""
        
        processed = {}
        
        for func_name, result in results.items():
            if result.success:
                processed[func_name] = {
                    'value': result.result,
                    'execution_time': result.execution_time,
                    'success': True
                }
            else:
                processed[func_name] = {
                    'error': result.error,
                    'success': False
                }
        
        return processed
    
    def _generate_insights(self, results: Dict[str, Any], schema: Dict[str, Any]) -> str:
        """Generate insights from computational results"""
        
        # For now, use rule-based insights
        # In production, could use LLM for more sophisticated analysis
        
        insights = []
        
        # Find best option based on prospect values
        best_option = None
        best_value = float('-inf')
        
        for prospect_name, data in results.items():
            prospect_results = data['results']
            
            # Look for prospect evaluation result
            for func_name, result in prospect_results.items():
                if 'prospect' in func_name.lower() and result['success']:
                    value = result['value']
                    if value > best_value:
                        best_value = value
                        best_option = prospect_name
        
        if best_option:
            insights.append(f"Recommended choice: {best_option} (Value: {best_value:.2f})")
        
        # Add theory-specific insights
        theory_name = schema.get('theory_name', '')
        if 'Prospect Theory' in theory_name:
            insights.append("\nKey behavioral factors:")
            insights.append("- Loss aversion affects perception of negative outcomes")
            insights.append("- Probability weighting distorts objective probabilities")
            insights.append("- Reference point determines gain/loss framing")
        
        return '\n'.join(insights)
    
    def save_analysis(self, analysis: TheoryAnalysis, output_dir: str = "./analysis_outputs") -> str:
        """Save analysis results"""
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Create filename
        filename = f"{analysis.theory_name.lower().replace(' ', '_')}_{analysis.timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        filepath = output_path / filename
        
        # Convert to dict
        analysis_dict = asdict(analysis)
        analysis_dict['timestamp'] = analysis.timestamp.isoformat()
        
        # Save
        with open(filepath, 'w') as f:
            json.dump(analysis_dict, f, indent=2)
        
        logger.info(f"Saved analysis to {filepath}")
        return str(filepath)


def demonstrate_integrated_system():
    """Demonstrate the complete integrated system"""
    
    print("=" * 60)
    print("INTEGRATED THEORY-TO-CODE SYSTEM")
    print("=" * 60)
    
    # Initialize system
    system = IntegratedTheorySystem()
    
    # Load Prospect Theory
    schema_path = "/home/brian/projects/Digimons/config/schemas/prospect_theory_schema.json"
    
    print("\n1. Loading and compiling theory...")
    success = system.load_and_compile_theory(schema_path)
    if not success:
        print("Failed to compile theory!")
        return
    
    print("   ✓ Theory compiled successfully")
    
    # Example text
    test_text = """
    The company faces a critical decision about entering the Asian market. 
    
    Option A involves a bold expansion strategy with a 65% probability of 
    capturing significant market share and achieving major revenue growth. 
    However, there's a 35% chance of facing regulatory challenges that could 
    result in substantial financial losses.
    
    Option B is a partnership approach with established local firms. This is 
    almost certain to succeed (95% probability) but will yield only moderate 
    returns due to profit sharing arrangements. There's a small 5% risk of 
    partnership disputes leading to minor losses.
    
    The board must decide between these strategies, considering the company's 
    current stable position in existing markets.
    """
    
    print("\n2. Analyzing text...")
    print(test_text[:200] + "...")
    
    # Analyze
    try:
        analysis = system.analyze_text(test_text, "prospect_theory")
        
        print("\n3. Analysis Results:")
        print(f"   Prospects identified: {len(analysis.extracted_parameters)}")
        for param in analysis.extracted_parameters:
            print(f"   - {param['prospect_name']}: {param['outcomes']} @ {param['probabilities']}")
        
        print("\n4. Computational Results:")
        for prospect, results in analysis.computational_results.items():
            print(f"   {prospect}:")
            for func, result in results['results'].items():
                if result['success']:
                    print(f"     - {func}: {result['value']:.2f}")
        
        print("\n5. Insights:")
        print(analysis.insights)
        
        print(f"\n6. Confidence Score: {analysis.confidence_score:.0%}")
        
        # Save results
        filepath = system.save_analysis(analysis)
        print(f"\n7. Results saved to: {filepath}")
        
    except Exception as e:
        print(f"Analysis failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n✅ Demonstration complete!")


def test_with_multiple_theories():
    """Test system with multiple theories"""
    
    system = IntegratedTheorySystem()
    
    # Load multiple theories (if available)
    theory_schemas = [
        "/home/brian/projects/Digimons/config/schemas/prospect_theory_schema.json",
        # Add more theory schemas here as they become available
    ]
    
    # Load all theories
    for schema_path in theory_schemas:
        if os.path.exists(schema_path):
            system.load_and_compile_theory(schema_path)
    
    # Test text
    text = "The government must choose between a risky innovation policy or maintaining the status quo..."
    
    # Analyze with each theory
    for theory_name in system.generated_theories:
        print(f"\nAnalyzing with {theory_name}:")
        analysis = system.analyze_text(text, theory_name)
        print(f"Result: {analysis.insights[:100]}...")


if __name__ == "__main__":
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Warning: No OPENAI_API_KEY found. Using fallback generation.")
        print("Set OPENAI_API_KEY environment variable for real LLM integration.")
    
    demonstrate_integrated_system()