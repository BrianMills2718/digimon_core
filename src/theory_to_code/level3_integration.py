"""
Level 3 (PROCEDURES) Integration with Levels 1 & 2

This module integrates Level 3 procedures with the existing Level 1 (formulas) and 
Level 2 (algorithms) infrastructure, creating a unified theory-to-code system that 
can execute formulas, algorithms, and procedures together.
"""

from typing import Dict, List, Any, Optional, Set, Union
from dataclasses import dataclass, field
import logging
import json
import time
from datetime import datetime

from .level2_integration import Level2IntegratedSystem, EnhancedTheoryAnalysis
from .procedure_generator import (
    ProcedureGenerator, ProcedureSpec, ProcedureStep, ProcedureType, 
    GeneratedProcedure
)
from .procedure_executor import ProcedureExecutor, ProcedureExecutionResult
from .algorithm_generator import GeneratedAlgorithm
from .simple_executor import ExecutionResult
from .level2_integration import TheoryComponent, ResolvedParameters
from .algorithm_generator import GeneratedAlgorithm

logger = logging.getLogger(__name__)


@dataclass
class Level3EnhancedAnalysis(EnhancedTheoryAnalysis):
    """Enhanced analysis result that includes Level 3 procedures"""
    procedure_results: Dict[str, Any] = field(default_factory=dict)
    workflow_states: Dict[str, str] = field(default_factory=dict)
    decision_paths: List[Dict[str, Any]] = field(default_factory=list)


class Level3IntegratedSystem(Level2IntegratedSystem):
    """
    Complete theory-to-code system with Level 1 (formulas), Level 2 (algorithms), 
    and Level 3 (procedures) integration
    """
    
    def __init__(self):
        super().__init__()
        self.procedure_generator = ProcedureGenerator()
        self.procedure_executor = ProcedureExecutor()
        
    def load_and_compile_theory(self, schema_path: str) -> bool:
        """
        Load and compile theory with Level 1, 2, and 3 components
        
        Args:
            schema_path: Path to theory schema JSON file
            
        Returns:
            True if compilation successful
        """
        try:
            logger.info(f"Loading enhanced theory schema from {schema_path}")
            
            with open(schema_path, 'r') as f:
                schema = json.load(f)
            
            theory_name = schema.get('theory_name', 'unknown_theory').lower().replace(' ', '_')
            
            # Initialize theory storage
            self.theory_components[theory_name] = {
                1: [],  # Formulas
                2: [],  # Algorithms  
                3: []   # Procedures
            }
            
            # Generate Level 1 and 2 components (inherited from Level2IntegratedSystem)
            level1_success = self._generate_level1_components(schema, theory_name)
            level2_success = self._generate_level2_components(schema, theory_name)
            
            # Generate Level 3 components (procedures)
            level3_success = self._generate_level3_components(schema, theory_name)
            
            total_components = (
                len(self.theory_components[theory_name][1]) +
                len(self.theory_components[theory_name][2]) +
                len(self.theory_components[theory_name][3])
            )
            
            logger.info(f"Successfully compiled {theory_name} with {total_components} components")
            logger.info(f"Level 1: {len(self.theory_components[theory_name][1])} components")
            logger.info(f"Level 2: {len(self.theory_components[theory_name][2])} components") 
            logger.info(f"Level 3: {len(self.theory_components[theory_name][3])} components")
            
            return level1_success or level2_success or level3_success
            
        except Exception as e:
            logger.error(f"Failed to compile theory: {e}")
            return False
    
    def _generate_level3_components(self, schema: Dict[str, Any], theory_name: str) -> bool:
        """Generate Level 3 procedure components from schema"""
        
        # Check for explicit procedures section
        if 'procedures' in schema:
            procedures_data = schema['procedures']
            for proc_name, proc_spec in procedures_data.items():
                self._generate_single_procedure(proc_spec, theory_name, proc_name)
        
        # Infer procedures from theory description
        inferred_procedures = self._infer_procedures_from_theory(schema, theory_name)
        
        for proc_spec in inferred_procedures:
            generated_proc = self._generate_single_procedure(proc_spec, theory_name)
            if generated_proc:
                self.theory_components[theory_name][3].append(
                    self._convert_to_theory_component(generated_proc, 'procedure')
                )
        
        return len(self.theory_components[theory_name][3]) > 0
    
    def _infer_procedures_from_theory(self, schema: Dict[str, Any], theory_name: str) -> List[ProcedureSpec]:
        """Infer possible procedures from theory description"""
        
        # Get description from multiple sources
        theory_description = ""
        if 'description' in schema:
            theory_description += schema['description'] + " "
        if 'telos' in schema and 'primary_purpose' in schema['telos']:
            theory_description += schema['telos']['primary_purpose'] + " "
        if 'execution' in schema:
            execution_data = schema['execution']
            # Look for step-based processes
            if isinstance(execution_data, dict):
                for key, value in execution_data.items():
                    if 'step' in key.lower() and isinstance(value, dict):
                        if 'description' in value:
                            theory_description += value['description'] + " "
        
        theory_description = theory_description.lower()
        schema_text = str(schema).lower()
        search_text = theory_description + " " + schema_text
        
        inferred_procedures = []
        
        # Decision procedures
        if any(keyword in search_text for keyword in ['decision', 'choice', 'select', 'evaluate', 'compare']):
            steps = [
                ProcedureStep(
                    step_id="identify_alternatives",
                    name="Identify Alternatives", 
                    description="Identify available decision alternatives",
                    function_name="identify_alternatives",
                    transitions={"default": "evaluate_alternatives"}
                ),
                ProcedureStep(
                    step_id="evaluate_alternatives",
                    name="Evaluate Alternatives",
                    description="Evaluate each alternative against criteria", 
                    function_name="evaluate_alternatives",
                    transitions={"default": "make_decision"}
                ),
                ProcedureStep(
                    step_id="make_decision",
                    name="Make Decision",
                    description="Select the best alternative",
                    function_name="make_decision", 
                    transitions={"default": "complete"}
                )
            ]
            
            inferred_procedures.append(ProcedureSpec(
                name=f"{theory_name}_decision_procedure",
                description=f"Decision-making procedure based on {theory_name}",
                procedure_type=ProcedureType.DECISION,
                steps=steps,
                initial_state="identify_alternatives",
                final_states={"complete", "error"}
            ))
        
        # Communication procedures
        if any(keyword in search_text for keyword in ['communication', 'message', 'inform', 'persuade', 'negotiate']):
            steps = [
                ProcedureStep(
                    step_id="analyze_context",
                    name="Analyze Context",
                    description="Analyze communication context and audience",
                    function_name="analyze_context",
                    transitions={"default": "craft_message"}
                ),
                ProcedureStep(
                    step_id="craft_message", 
                    name="Craft Message",
                    description="Create appropriate message for the context",
                    function_name="craft_message",
                    transitions={"default": "deliver_message"}
                ),
                ProcedureStep(
                    step_id="deliver_message",
                    name="Deliver Message", 
                    description="Deliver message and monitor response",
                    function_name="deliver_message",
                    transitions={"default": "complete"}
                )
            ]
            
            inferred_procedures.append(ProcedureSpec(
                name=f"{theory_name}_communication_procedure", 
                description=f"Communication procedure based on {theory_name}",
                procedure_type=ProcedureType.COMMUNICATION,
                steps=steps,
                initial_state="analyze_context",
                final_states={"complete", "error"}
            ))
        
        # Research procedures
        if any(keyword in search_text for keyword in ['research', 'study', 'analyze', 'investigate', 'collect', 'data']):
            steps = [
                ProcedureStep(
                    step_id="define_research_question",
                    name="Define Research Question",
                    description="Define clear research question and objectives",
                    function_name="define_research_question", 
                    transitions={"default": "collect_data"}
                ),
                ProcedureStep(
                    step_id="collect_data",
                    name="Collect Data", 
                    description="Collect relevant data using appropriate methods",
                    function_name="collect_data",
                    transitions={"default": "analyze_data"}
                ),
                ProcedureStep(
                    step_id="analyze_data",
                    name="Analyze Data",
                    description="Analyze collected data and draw conclusions",
                    function_name="analyze_data",
                    transitions={"default": "complete"}
                )
            ]
            
            inferred_procedures.append(ProcedureSpec(
                name=f"{theory_name}_research_procedure",
                description=f"Research procedure based on {theory_name}", 
                procedure_type=ProcedureType.RESEARCH,
                steps=steps,
                initial_state="define_research_question",
                final_states={"complete", "error"}
            ))
        
        return inferred_procedures
    
    def _generate_single_procedure(self, proc_spec: Union[ProcedureSpec, Dict[str, Any]], 
                                 theory_name: str, proc_name: str = None) -> Optional[GeneratedProcedure]:
        """Generate a single procedure component"""
        
        try:
            if isinstance(proc_spec, dict):
                # Convert dict spec to ProcedureSpec
                proc_spec = self._dict_to_procedure_spec(proc_spec, proc_name)
            
            logger.info(f"Generating Level 3 component: {proc_spec.name}")
            
            generated_proc = self.procedure_generator.generate_procedure_class(proc_spec)
            
            # Validate the generated procedure
            if generated_proc.validation_result.get('syntax_valid', False):
                logger.info(f"✓ Generated Level 3 component: {proc_spec.name}")
                return generated_proc
            else:
                logger.error(f"✗ Level 3 validation failed for {proc_spec.name}: {generated_proc.validation_result.get('errors', [])}")
                return None
                
        except Exception as e:
            logger.error(f"Error generating Level 3 component: {e}")
            return None
    
    def _dict_to_procedure_spec(self, proc_dict: Dict[str, Any], proc_name: str) -> ProcedureSpec:
        """Convert dictionary to ProcedureSpec"""
        
        steps = []
        if 'steps' in proc_dict:
            for i, step_info in enumerate(proc_dict['steps']):
                step = ProcedureStep(
                    step_id=step_info.get('id', f"step_{i}"),
                    name=step_info.get('name', f"Step {i+1}"),
                    description=step_info.get('description', ''),
                    function_name=step_info.get('function', f"step_{i}"),
                    transitions=step_info.get('transitions', {"default": f"step_{i+1}"})
                )
                steps.append(step)
        
        return ProcedureSpec(
            name=proc_name or proc_dict.get('name', 'unknown_procedure'),
            description=proc_dict.get('description', ''),
            procedure_type=ProcedureType(proc_dict.get('type', 'sequential')),
            steps=steps,
            initial_state=proc_dict.get('initial_state', 'start'),
            final_states=set(proc_dict.get('final_states', ['complete']))
        )
    
    def _convert_to_theory_component(self, generated_proc: GeneratedProcedure, 
                                   component_type: str) -> TheoryComponent:
        """Convert GeneratedProcedure to TheoryComponent"""
        
        # Create a procedure object similar to GeneratedAlgorithm structure
        procedure_object = type('GeneratedProcedure', (), {
            'source_code': generated_proc.source_code,
            'class_name': generated_proc.class_name,
            'validation_result': generated_proc.validation_result,
            'metadata': generated_proc.metadata
        })()
        
        return TheoryComponent(
            level=3,
            name=generated_proc.name,
            component_type=component_type,
            generated_code=procedure_object,
            validated=generated_proc.validation_result.get('syntax_valid', False),
            test_cases=[]
        )
    
    def analyze_text(self, text: str, theory_name: str) -> Level3EnhancedAnalysis:
        """
        Analyze text using Level 1, 2, and 3 components
        
        Args:
            text: Text to analyze
            theory_name: Name of theory to use
            
        Returns:
            Level3EnhancedAnalysis with all three levels of results
        """
        start_time = time.time()
        
        # Get Level 1 and 2 analysis (inherited functionality)
        level2_analysis = super().analyze_text(text, theory_name)
        
        # Add Level 3 procedure execution
        procedure_results = {}
        workflow_states = {}
        decision_paths = []
        
        if theory_name in self.theory_components:
            theory_data = self.theory_components[theory_name]
            level3_components = theory_data.get(3, [])
            
            for component in level3_components:
                try:
                    # Prepare context for procedure
                    context = self._prepare_procedure_context(component, text, level2_analysis)
                    
                    # Execute procedure
                    result = self.procedure_executor.execute_procedure(
                        component.generated_code.source_code,
                        component.generated_code.class_name,
                        context
                    )
                    
                    procedure_results[component.name] = {
                        "success": result.success,
                        "final_state": result.final_state,
                        "steps_completed": result.steps_completed,
                        "execution_time": result.execution_time,
                        "context": result.context,
                        "error": result.error
                    }
                    
                    workflow_states[component.name] = result.final_state
                    
                    # Extract decision path if available
                    if result.history:
                        decision_paths.append({
                            "procedure": component.name,
                            "path": result.history,
                            "decision": result.context.get("choice") or result.context.get("decision")
                        })
                    
                except Exception as e:
                    logger.error(f"Failed to execute procedure {component.name}: {e}")
                    procedure_results[component.name] = {
                        "success": False,
                        "error": str(e),
                        "final_state": "error"
                    }
        
        # Combine all analysis results
        components_found = level2_analysis.components_found.copy()
        if procedure_results:
            components_found["Level 3 (Procedures)"] = list(procedure_results.keys())
        
        # Generate enhanced insights
        enhanced_insights = self._generate_level3_insights(
            level2_analysis, procedure_results, decision_paths
        )
        
        return Level3EnhancedAnalysis(
            components_found=components_found,
            computational_results=level2_analysis.computational_results,
            insights=enhanced_insights,
            execution_metadata={
                "execution_time_seconds": time.time() - start_time,
                "levels_executed": [1, 2, 3],
                "total_components": sum(len(components) for components in components_found.values())
            },
            procedure_results=procedure_results,
            workflow_states=workflow_states,
            decision_paths=decision_paths
        )
    
    def _prepare_procedure_context(self, component: TheoryComponent, text: str, 
                                 level2_analysis: EnhancedTheoryAnalysis) -> Dict[str, Any]:
        """Prepare context for procedure execution"""
        
        context = {
            "input_text": text,
            "analysis_results": level2_analysis.computational_results,
            "components_found": level2_analysis.components_found,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add specific context based on procedure type
        procedure_name = component.name.lower()
        
        if "decision" in procedure_name:
            # Extract potential alternatives from text
            context["alternatives"] = self._extract_alternatives_from_text(text)
            context["criteria"] = ["feasibility", "impact", "cost", "risk"]
            
        elif "communication" in procedure_name:
            # Extract communication context
            context["audience"] = self._extract_audience_from_text(text)
            context["message_type"] = self._classify_message_type(text)
            
        elif "research" in procedure_name:
            # Extract research elements
            context["research_question"] = self._extract_research_question(text)
            context["data_sources"] = ["text_analysis", "computational_results"]
        
        return context
    
    def _extract_alternatives_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Extract decision alternatives from text"""
        
        alternatives = []
        
        # Simple pattern matching for options
        import re
        option_patterns = [
            r'option\\s+([a-z])[:.]?\\s*([^.!?\\n]+)',
            r'alternative\\s+([^:]+)[:.]?\\s*([^.!?\\n]+)',
            r'choice\\s+([^:]+)[:.]?\\s*([^.!?\\n]+)'
        ]
        
        for pattern in option_patterns:
            matches = re.findall(pattern, text.lower())
            for match in matches:
                alternatives.append({
                    "id": match[0].strip(),
                    "description": match[1].strip(),
                    "source": "text_extraction"
                })
        
        # If no structured options found, create generic alternatives
        if not alternatives:
            alternatives = [
                {"id": "option_a", "description": "First mentioned approach", "source": "inferred"},
                {"id": "option_b", "description": "Alternative approach", "source": "inferred"}
            ]
        
        return alternatives
    
    def _extract_audience_from_text(self, text: str) -> Dict[str, Any]:
        """Extract communication audience from text"""
        
        audience_keywords = {
            "board": "executive",
            "committee": "executive", 
            "team": "internal",
            "staff": "internal",
            "public": "external",
            "customer": "external",
            "client": "external"
        }
        
        text_lower = text.lower()
        audience_type = "general"
        
        for keyword, aud_type in audience_keywords.items():
            if keyword in text_lower:
                audience_type = aud_type
                break
        
        return {
            "type": audience_type,
            "context": "formal" if any(word in text_lower for word in ["board", "committee", "formal"]) else "informal"
        }
    
    def _classify_message_type(self, text: str) -> str:
        """Classify the type of message"""
        
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["decision", "choose", "select"]):
            return "decision_communication"
        elif any(word in text_lower for word in ["crisis", "urgent", "emergency"]):
            return "crisis_communication"
        elif any(word in text_lower for word in ["inform", "update", "report"]):
            return "informational"
        else:
            return "general"
    
    def _extract_research_question(self, text: str) -> str:
        """Extract research question from text"""
        
        # Look for question patterns
        import re
        question_patterns = [
            r'\\?([^.!?]*\\?)',
            r'how\\s+([^.!?]+)',
            r'why\\s+([^.!?]+)',
            r'what\\s+([^.!?]+)'
        ]
        
        for pattern in question_patterns:
            match = re.search(pattern, text.lower())
            if match:
                return match.group(0).strip()
        
        # Default research question
        return "How can this situation be analyzed and understood?"
    
    def _generate_level3_insights(self, level2_analysis: EnhancedTheoryAnalysis,
                                procedure_results: Dict[str, Any],
                                decision_paths: List[Dict[str, Any]]) -> str:
        """Generate enhanced insights including Level 3 procedures"""
        
        # Start with Level 2 insights
        insights = level2_analysis.insights
        
        # Add procedure execution summary
        if procedure_results:
            insights += f"\\n\\nLevel 3 (Procedure) Results:\\n"
            
            successful_procedures = [name for name, result in procedure_results.items() if result["success"]]
            failed_procedures = [name for name, result in procedure_results.items() if not result["success"]]
            
            insights += f"  Successful procedures: {len(successful_procedures)}/{len(procedure_results)}\\n"
            
            for proc_name, result in procedure_results.items():
                if result["success"]:
                    insights += f"  - {proc_name}: completed in {result['steps_completed']} steps, final state: {result['final_state']}\\n"
                else:
                    insights += f"  - {proc_name}: failed with error: {result.get('error', 'unknown')}\\n"
            
            # Add decision information
            if decision_paths:
                insights += f"\\nDecision Paths:\\n"
                for path in decision_paths:
                    if path["decision"]:
                        insights += f"  - {path['procedure']}: decided on '{path['decision']}'\\n"
        
        return insights


def test_level3_integration():
    """Test the Level 3 integration system"""
    
    print("=" * 60)
    print("LEVEL 3 INTEGRATION TEST")
    print("=" * 60)
    
    # Initialize system
    system = Level3IntegratedSystem()
    
    # Load and compile theory
    schema_path = '/home/brian/projects/Digimons/config/schemas/prospect_theory_schema.json'
    success = system.load_and_compile_theory(schema_path)
    
    print(f"Compilation success: {success}")
    
    # Show what was generated
    if 'prospect_theory' in system.theory_components:
        theory_components = system.theory_components['prospect_theory']
        for level, components in theory_components.items():
            if components:
                print(f"Level {level}: {len(components)} components")
                for comp in components:
                    print(f"  - {comp.name} ({comp.component_type})")
    
    print("\\nNow testing complete analysis workflow with all 3 levels...")
    test_text = '''
    The investment committee faces a strategic decision:

    Option A: Launch an aggressive expansion into emerging markets. This strategy has a 60% 
    chance of generating substantial profits but a 40% chance of significant losses due to 
    regulatory risks.

    Option B: Pursue a conservative partnership approach with established local firms. This 
    provides a 90% probability of moderate, steady returns with only a 10% risk of minor losses.

    The company is currently in a stable financial position with consistent revenue streams.
    '''
    
    try:
        analysis = system.analyze_text(test_text, 'prospect_theory')
        
        print(f"\\nLevel 1-3 Analysis completed successfully!")
        print(f"Components used: {analysis.components_found}")
        print(f"Execution time: {analysis.execution_metadata['execution_time_seconds']:.2f}s")
        
        # Show procedure results
        if analysis.procedure_results:
            print(f"\\nProcedure Results:")
            for proc_name, result in analysis.procedure_results.items():
                print(f"  - {proc_name}: {result['final_state']} ({result['steps_completed']} steps)")
        
        # Show decision paths
        if analysis.decision_paths:
            print(f"\\nDecision Paths:")
            for path in analysis.decision_paths:
                print(f"  - {path['procedure']}: {path.get('decision', 'No decision recorded')}")
        
        print(f"\\nEnhanced Insights:\\n{analysis.insights}")
        
        return True
        
    except Exception as e:
        print(f"Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_level3_integration()