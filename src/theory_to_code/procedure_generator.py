"""
Level 3 (PROCEDURES) Implementation - State Machine and Workflow Generator

This module generates executable procedures and state machines from theory descriptions,
enabling automated workflow execution with decision points, transitions, and rollback capabilities.
"""

from typing import Dict, List, Any, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime
import json
import logging
import traceback
from enum import Enum

from .algorithm_generator import GeneratedAlgorithm, AlgorithmGenerator
from .algorithm_executor import AlgorithmExecutionResult

logger = logging.getLogger(__name__)


class ProcedureType(Enum):
    """Types of procedures that can be generated"""
    DECISION = "decision"
    COMMUNICATION = "communication"
    RESEARCH = "research"
    ORGANIZATIONAL = "organizational"
    SEQUENTIAL = "sequential"
    CONDITIONAL = "conditional"


@dataclass
class ProcedureStep:
    """Represents a single step in a procedure"""
    step_id: str
    name: str
    description: str
    function_name: str
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    conditions: Dict[str, Any] = field(default_factory=dict)
    transitions: Dict[str, str] = field(default_factory=dict)  # condition -> next_step
    rollback_actions: List[str] = field(default_factory=list)


@dataclass
class ProcedureSpec:
    """Specification for generating a procedure"""
    name: str
    description: str
    procedure_type: ProcedureType
    steps: List[ProcedureStep]
    initial_state: str
    final_states: Set[str]
    context_schema: Dict[str, Any] = field(default_factory=dict)
    decision_rules: Dict[str, Any] = field(default_factory=dict)
    error_handling: Dict[str, str] = field(default_factory=dict)


@dataclass
class GeneratedProcedure:
    """A generated procedure class"""
    name: str
    class_name: str
    source_code: str
    procedure_type: ProcedureType
    steps: List[ProcedureStep]
    validation_result: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProcedureExecutionResult:
    """Result of executing a procedure"""
    success: bool
    final_state: str
    context: Dict[str, Any]
    history: List[Dict[str, Any]]
    execution_time: float
    error: Optional[str] = None
    rollback_performed: bool = False
    steps_completed: int = 0


class ProcedureGenerator(AlgorithmGenerator):
    """Generate executable procedures and state machines from theory descriptions"""
    
    def __init__(self):
        super().__init__()
        self.procedure_templates = self._load_procedure_templates()
        
    def generate_procedure_class(self, procedure_spec: ProcedureSpec) -> GeneratedProcedure:
        """
        Generate a Python class implementing the specified procedure
        
        Args:
            procedure_spec: Specification of the procedure to generate
            
        Returns:
            GeneratedProcedure with executable Python class
        """
        try:
            logger.info(f"Generating procedure: {procedure_spec.name}")
            
            # Classify procedure type if not specified
            if not procedure_spec.procedure_type:
                procedure_spec.procedure_type = self._classify_procedure_type(procedure_spec)
            
            # Force template-based generation for reliability
            logger.info("Using template-based procedure generation for reliability")
            return self._generate_with_template(procedure_spec)
            
            # Disable LLM generation temporarily due to incorrect class generation
            # try:
            #     return self._generate_with_llm(procedure_spec)
            # except Exception as e:
            #     logger.warning(f"LLM generation failed: {e}, falling back to template")
            #     return self._generate_with_template(procedure_spec)
            
        except Exception as e:
            logger.error(f"Failed to generate procedure {procedure_spec.name}: {e}")
            raise
    
    def _generate_with_llm(self, procedure_spec: ProcedureSpec) -> GeneratedProcedure:
        """Generate procedure using LLM"""
        
        prompt = self._build_procedure_prompt(procedure_spec)
        
        try:
            response = self._call_llm(prompt)
            return self._parse_generated_procedure(response, procedure_spec)
        except Exception as e:
            logger.error(f"LLM procedure generation failed: {e}")
            raise
    
    def _build_procedure_prompt(self, procedure_spec: ProcedureSpec) -> str:
        """Build LLM prompt for procedure generation"""
        
        steps_description = "\n".join([
            f"- {step.step_id}: {step.name} -> {step.transitions}"
            for step in procedure_spec.steps
        ])
        
        template = f"""You are generating a PROCEDURE class for state machine workflow execution, NOT an algorithm class.

PROCEDURE NAME: {procedure_spec.name}
PROCEDURE TYPE: {procedure_spec.procedure_type.value}
DESCRIPTION: {procedure_spec.description}

WORKFLOW STEPS:
{steps_description}

INITIAL STATE: {procedure_spec.initial_state}
FINAL STATES: {', '.join(procedure_spec.final_states)}

MANDATORY REQUIREMENTS:
- Class name must be {procedure_spec.name.title().replace('_', '')}Procedure
- Must have execute(self, context) method that returns a dict
- Must implement state machine with transitions
- Must track history and preserve context
- Must handle errors and rollbacks

EXACT TEMPLATE TO FOLLOW:
```python
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class {procedure_spec.name.title().replace('_', '')}Procedure:
    \"\"\"
    {procedure_spec.description}
    
    This is a procedure class that implements a state machine workflow.
    \"\"\"
    
    def __init__(self):
        self.state = "{procedure_spec.initial_state}"
        self.context = {{}}
        self.history = []
        self.transitions = {{
            "{procedure_spec.initial_state}": "identify_alternatives",
            # Add more state transitions here
        }}
        self.final_states = {{{', '.join(f'"{s}"' for s in procedure_spec.final_states)}}}
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"Execute the complete procedure workflow\"\"\"
        self.context = context
        self.history = []
        
        try:
            steps = 0
            while self.state not in self.final_states and steps < 50:
                # Record step
                self.history.append({{
                    "state": self.state,
                    "timestamp": datetime.now().isoformat(),
                    "step": steps
                }})
                
                # Execute current step
                if self.state == "{procedure_spec.initial_state}":
                    self.state = "step_1_complete"
                # Add more state transitions here
                elif self.state == "step_1_complete":
                    self.state = "complete"
                else:
                    self.state = "complete"
                
                steps += 1
            
            return {{
                "success": True,
                "final_state": self.state,
                "context": self.context,
                "history": self.history,
                "steps_completed": steps
            }}
            
        except Exception as e:
            return {{
                "success": False,
                "error": str(e),
                "final_state": "error",
                "context": self.context,
                "history": self.history,
                "steps_completed": steps
            }}
```

Generate the complete class following this exact pattern. Do NOT create an Algorithm class."""

        return template
    
    def _generate_with_template(self, procedure_spec: ProcedureSpec) -> GeneratedProcedure:
        """Generate procedure using templates as fallback"""
        
        procedure_type = procedure_spec.procedure_type
        template = self.procedure_templates.get(procedure_type)
        
        if not template:
            raise ValueError(f"No template available for procedure type: {procedure_type}")
        
        # Fill in template with procedure specification
        class_name = f"{procedure_spec.name.title().replace('_', '')}Procedure"
        
        # Build transitions mapping
        transitions = {}
        for step in procedure_spec.steps:
            transitions[step.step_id] = step.function_name
        
        # Build step methods
        step_methods = []
        for step in procedure_spec.steps:
            method_code = self._generate_step_method(step)
            step_methods.append(method_code)
        
        # Fill template
        source_code = template.format(
            class_name=class_name,
            initial_state=procedure_spec.initial_state,
            final_states=str(list(procedure_spec.final_states)),
            transitions=str(transitions),
            step_methods='\n\n'.join(step_methods),
            description=procedure_spec.description
        )
        
        # Validate generated code
        validation_result = self._validate_procedure_code(source_code, class_name)
        
        return GeneratedProcedure(
            name=procedure_spec.name,
            class_name=class_name,
            source_code=source_code,
            procedure_type=procedure_type,
            steps=procedure_spec.steps,
            validation_result=validation_result,
            metadata={
                'generation_method': 'template',
                'template_type': procedure_type.value
            }
        )
    
    def _generate_step_method(self, step: ProcedureStep) -> str:
        """Generate code for a single procedure step"""
        
        method_template = f'''    def {step.function_name}(self):
        """
        {step.description}
        """
        try:
            # Record step entry
            self.history.append({{
                "step_id": "{step.step_id}",
                "step_name": "{step.name}",
                "state": self.state,
                "timestamp": datetime.now().isoformat(),
                "context": self.context.copy()
            }})
            
            # Step implementation placeholder
            # TODO: Add specific step logic here
            
            # Handle transitions
            return "complete"
            
        except Exception as e:
            logger.error(f"Step {step.step_id} failed: {{e}}")
            return "error"'''
        
        return method_template
    
    def _generate_transition_logic(self, step: ProcedureStep) -> str:
        """Generate transition logic for a step"""
        
        if not step.transitions:
            return f'return "{step.step_id}_complete"'
        
        conditions = []
        for condition, next_state in step.transitions.items():
            if condition == 'default':
                conditions.append(f'            return "{next_state}"')
            else:
                conditions.append(f'            if {condition}:')
                conditions.append(f'                return "{next_state}"')
        
        # Add default fallback
        if 'default' not in step.transitions:
            conditions.append(f'            return "{step.step_id}_complete"')
        
        return '\n'.join(conditions)
    
    def _parse_generated_procedure(self, response: str, procedure_spec: ProcedureSpec) -> GeneratedProcedure:
        """Parse LLM response to extract procedure class"""
        
        # Extract Python code from response
        source_code = self._extract_code_from_response(response)
        
        # Extract class name
        class_name = self._extract_class_name(source_code)
        if not class_name:
            class_name = f"{procedure_spec.name.title().replace('_', '')}Procedure"
        
        # Validate generated code
        validation_result = self._validate_procedure_code(source_code, class_name)
        
        return GeneratedProcedure(
            name=procedure_spec.name,
            class_name=class_name,
            source_code=source_code,
            procedure_type=procedure_spec.procedure_type,
            steps=procedure_spec.steps,
            validation_result=validation_result,
            metadata={
                'generation_method': 'llm',
                'raw_response': response[:500]  # Store truncated response
            }
        )
    
    def _validate_procedure_code(self, source_code: str, class_name: str) -> Dict[str, Any]:
        """Validate generated procedure code"""
        
        validation_result = {
            'syntax_valid': False,
            'class_found': False,
            'required_methods': [],
            'errors': []
        }
        
        try:
            # Check syntax
            compile(source_code, '<generated>', 'exec')
            validation_result['syntax_valid'] = True
            
            # Check for required methods
            required_methods = ['__init__', 'execute']
            for method in required_methods:
                if f'def {method}(' in source_code:
                    validation_result['required_methods'].append(method)
            
            # Check class definition
            if f'class {class_name}' in source_code:
                validation_result['class_found'] = True
            
        except SyntaxError as e:
            validation_result['errors'].append(f"Syntax error: {e}")
        except Exception as e:
            validation_result['errors'].append(f"Validation error: {e}")
        
        return validation_result
    
    def _extract_code_from_response(self, response: str) -> str:
        """Extract Python code from LLM response"""
        import re
        
        # Try to find code blocks
        code_patterns = [
            r'```python\n(.*?)\n```',
            r'```\n(.*?)\n```',
            r'```python(.*?)```'
        ]
        
        for pattern in code_patterns:
            match = re.search(pattern, response, re.DOTALL)
            if match:
                return match.group(1).strip()
        
        # If no code block found, return the response as-is
        return response
    
    def _extract_class_name(self, source_code: str) -> Optional[str]:
        """Extract class name from source code"""
        import re
        
        class_match = re.search(r'class\s+(\w+)', source_code)
        if class_match:
            return class_match.group(1)
        return None
    
    def _classify_procedure_type(self, procedure_spec: ProcedureSpec) -> ProcedureType:
        """Classify procedure type from description"""
        
        description = procedure_spec.description.lower()
        
        if any(keyword in description for keyword in ['decision', 'choice', 'select', 'choose']):
            return ProcedureType.DECISION
        elif any(keyword in description for keyword in ['communication', 'message', 'inform', 'negotiate']):
            return ProcedureType.COMMUNICATION
        elif any(keyword in description for keyword in ['research', 'study', 'analyze', 'investigate']):
            return ProcedureType.RESEARCH
        elif any(keyword in description for keyword in ['organization', 'manage', 'process', 'workflow']):
            return ProcedureType.ORGANIZATIONAL
        elif any(keyword in description for keyword in ['condition', 'if', 'when', 'depends']):
            return ProcedureType.CONDITIONAL
        else:
            return ProcedureType.SEQUENTIAL
    
    def _load_procedure_templates(self) -> Dict[ProcedureType, str]:
        """Load procedure templates for fallback generation"""
        
        decision_template = '''from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class {class_name}:
    """{description}"""
    
    def __init__(self):
        self.state = "{initial_state}"
        self.context = {{}}
        self.history = []
        self.transitions = {transitions}
        self.final_states = {final_states}
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the complete procedure"""
        self.context = context
        self.history = []
        
        try:
            while self.state not in self.final_states:
                # Get current step function
                step_function = self.transitions.get(self.state)
                if not step_function:
                    raise ValueError(f"Invalid state: {{self.state}}")
                
                # Execute step and get next state
                next_state = getattr(self, step_function)()
                if next_state:
                    self.state = next_state
                
                # Prevent infinite loops
                if len(self.history) > 100:
                    raise RuntimeError("Maximum procedure steps exceeded")
            
            return {{
                "success": True,
                "final_state": self.state,
                "context": self.context,
                "history": self.history,
                "steps_completed": len(self.history)
            }}
            
        except Exception as e:
            logger.error(f"Procedure execution failed: {{e}}")
            return {{
                "success": False,
                "error": str(e),
                "final_state": self.state,
                "context": self.context,
                "history": self.history,
                "steps_completed": len(self.history)
            }}
    
    def _handle_step_error(self, step_id: str, error: Exception) -> str:
        """Handle errors during step execution"""
        self.context["last_error"] = {{
            "step_id": step_id,
            "error": str(error),
            "timestamp": datetime.now().isoformat()
        }}
        return "error_state"
    
    def _rollback_to_step(self, target_step: str) -> str:
        """Rollback to a previous step"""
        # Find target step in history
        for i, history_entry in enumerate(reversed(self.history)):
            if history_entry.get("step_id") == target_step:
                # Restore context from that point
                self.context = history_entry["context"].copy()
                # Truncate history
                self.history = self.history[:len(self.history) - i]
                return target_step
        
        # If not found, return to initial state
        return "{initial_state}"

{step_methods}'''

        return {
            ProcedureType.DECISION: decision_template,
            ProcedureType.COMMUNICATION: decision_template,
            ProcedureType.RESEARCH: decision_template,
            ProcedureType.ORGANIZATIONAL: decision_template,
            ProcedureType.SEQUENTIAL: decision_template,
            ProcedureType.CONDITIONAL: decision_template
        }


def test_procedure_generation():
    """Test the procedure generator"""
    
    print("=" * 60)
    print("PROCEDURE GENERATOR TEST")
    print("=" * 60)
    
    # Create test procedure specification
    steps = [
        ProcedureStep(
            step_id="identify_alternatives",
            name="Identify Alternatives",
            description="Identify available decision alternatives",
            function_name="identify_alternatives",
            inputs=["context"],
            outputs=["alternatives"],
            transitions={"len(alternatives) > 0": "evaluate_outcomes", "default": "no_alternatives"}
        ),
        ProcedureStep(
            step_id="evaluate_outcomes",
            name="Evaluate Outcomes",
            description="Evaluate potential outcomes for each alternative",
            function_name="evaluate_outcomes",
            inputs=["alternatives"],
            outputs=["outcomes"],
            transitions={"default": "make_decision"}
        ),
        ProcedureStep(
            step_id="make_decision",
            name="Make Decision",
            description="Select the best alternative",
            function_name="make_decision",
            inputs=["alternatives", "outcomes"],
            outputs=["decision"],
            transitions={"default": "complete"}
        )
    ]
    
    procedure_spec = ProcedureSpec(
        name="rational_choice_decision",
        description="Rational choice decision-making procedure",
        procedure_type=ProcedureType.DECISION,
        steps=steps,
        initial_state="identify_alternatives",
        final_states={"complete", "no_alternatives", "error_state"}
    )
    
    # Test procedure generation
    generator = ProcedureGenerator()
    
    try:
        result = generator.generate_procedure_class(procedure_spec)
        
        print(f"Generated procedure: {result.class_name}")
        print(f"Type: {result.procedure_type.value}")
        print(f"Steps: {len(result.steps)}")
        print(f"Validation: {result.validation_result}")
        print(f"Generation method: {result.metadata.get('generation_method')}")
        
        print("\\nGenerated code preview:")
        print(result.source_code[:500] + "...")
        
        return True
        
    except Exception as e:
        print(f"Test failed: {e}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_procedure_generation()