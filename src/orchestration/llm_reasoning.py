from src.core.standard_config import get_model
"""
LLM Reasoning Engine for Agent Orchestration.

Provides intelligent reasoning capabilities for agents using LLMs with memory-enhanced
context, enabling agents to make complex decisions and adapt their strategies dynamically.
"""

import json
import time
import logging
import asyncio
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, asdict

from .base import Task, Result
from .memory import MemoryType, MemoryQuery

logger = logging.getLogger(__name__)


class ReasoningType(Enum):
    """Types of reasoning processes."""
    STRATEGIC = "strategic"        # High-level strategy decisions
    TACTICAL = "tactical"          # Task execution optimization  
    ADAPTIVE = "adaptive"          # Learning and adaptation decisions
    DIAGNOSTIC = "diagnostic"      # Problem analysis and debugging
    PREDICTIVE = "predictive"      # Future outcome prediction
    CREATIVE = "creative"          # Novel solution generation


@dataclass
class ReasoningContext:
    """Context for LLM reasoning."""
    agent_id: str
    task: Task
    memory_context: Dict[str, Any]
    reasoning_type: ReasoningType
    constraints: Dict[str, Any] = None
    goals: List[str] = None
    previous_reasoning: List[Dict] = None
    
    def __post_init__(self):
        if self.constraints is None:
            self.constraints = {}
        if self.goals is None:
            self.goals = []
        if self.previous_reasoning is None:
            self.previous_reasoning = []


@dataclass
class ReasoningResult:
    """Result of LLM reasoning process."""
    success: bool
    reasoning_chain: List[Dict[str, Any]]
    decision: Dict[str, Any]
    confidence: float
    explanation: str
    alternatives_considered: List[Dict] = None
    execution_time: float = 0.0
    error: str = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.alternatives_considered is None:
            self.alternatives_considered = []
        if self.metadata is None:
            self.metadata = {}


class LLMReasoningEngine:
    """
    LLM-powered reasoning engine for intelligent agent decision-making.
    
    Integrates with existing KGAS LLM infrastructure and memory system to provide
    context-aware reasoning capabilities for agents.
    """
    
    def __init__(self, llm_config: Dict[str, Any] = None):
        """
        Initialize LLM reasoning engine.
        
        Args:
            llm_config: LLM configuration (provider, model, parameters)
        """
        self.llm_config = llm_config or self._get_default_config()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Cache for reasoning templates
        self._templates = {}
        
        # Performance tracking
        self._reasoning_stats = {
            "total_reasonings": 0,
            "successful_reasonings": 0,
            "avg_reasoning_time": 0.0,
            "reasoning_by_type": {}
        }
        
        self.logger.info(f"Initialized LLM reasoning engine with config: {self.llm_config.get('provider', 'default')}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default LLM configuration."""
        return {
            "provider": "gemini",  # Use Gemini 2.5 Flash
            "model": "gemini-2.5-flash",
            "temperature": 0.1,  # Low temperature for consistent reasoning
            "max_tokens": 32000,  # Proper limit for complex structured output
            "timeout": 30,
            "reasoning_style": "analytical"
        }
    
    async def reason(self, context: ReasoningContext) -> ReasoningResult:
        """
        Perform LLM-powered reasoning for a given context.
        
        Args:
            context: Reasoning context with task, memory, and goals
            
        Returns:
            Structured reasoning result with decision and explanation
        """
        start_time = time.time()
        
        try:
            self.logger.debug(f"Starting {context.reasoning_type.value} reasoning for agent {context.agent_id}")
            
            # Build reasoning prompt from context
            reasoning_prompt = await self._build_reasoning_prompt(context)
            
            # Execute LLM reasoning
            llm_response = await self._execute_llm_reasoning(reasoning_prompt, context)
            
            # Parse and structure the response
            reasoning_result = await self._parse_reasoning_response(llm_response, context)
            
            # Update performance stats
            self._update_reasoning_stats(context.reasoning_type, time.time() - start_time, True)
            
            reasoning_result.execution_time = time.time() - start_time
            
            self.logger.debug(f"Reasoning completed in {reasoning_result.execution_time:.3f}s with confidence {reasoning_result.confidence:.2f}")
            
            return reasoning_result
            
        except Exception as e:
            self.logger.error(f"Reasoning failed: {e}")
            
            # Update error stats
            self._update_reasoning_stats(context.reasoning_type, time.time() - start_time, False)
            
            return ReasoningResult(
                success=False,
                reasoning_chain=[],
                decision={},
                confidence=0.0,
                explanation=f"Reasoning failed: {str(e)}",
                error=str(e),
                execution_time=time.time() - start_time
            )
    
    async def _build_reasoning_prompt(self, context: ReasoningContext) -> str:
        """Build comprehensive reasoning prompt from context."""
        
        # Get reasoning template
        template = await self._get_reasoning_template(context.reasoning_type, context.task.task_type)
        
        # Extract relevant memory insights
        memory_insights = self._extract_memory_insights(context.memory_context)
        
        # Build structured prompt
        prompt_parts = [
            "# Intelligent Agent Reasoning",
            f"Agent: {context.agent_id}",
            f"Reasoning Type: {context.reasoning_type.value}",
            f"Task: {context.task.task_type}",
            "",
            "## Current Situation",
            f"Task Parameters: {json.dumps(context.task.parameters, indent=2)}",
            f"Task Context: {json.dumps(context.task.context or {}, indent=2)}",
            "",
            "## Memory-Based Insights",
        ]
        
        # Add memory insights
        if memory_insights["relevant_executions"]:
            prompt_parts.append("### Previous Executions:")
            for i, exec_info in enumerate(memory_insights["relevant_executions"][:3], 1):
                success_indicator = "✓" if exec_info.get("success") else "✗"
                prompt_parts.append(f"{i}. {exec_info.get('task_type')} {success_indicator} ({exec_info.get('execution_time', 0):.2f}s)")
        
        if memory_insights["learned_patterns"]:
            prompt_parts.append("\n### Learned Patterns:")
            for i, pattern in enumerate(memory_insights["learned_patterns"][:3], 1):
                confidence = pattern.get("confidence", 0)
                prompt_parts.append(f"{i}. {pattern.get('pattern_type')} (confidence: {confidence:.2f})")
        
        if memory_insights["procedures"]:
            prompt_parts.append("\n### Available Procedures:")
            for i, proc in enumerate(memory_insights["procedures"][:2], 1):
                success_rate = proc.get("success_rate", 0)
                prompt_parts.append(f"{i}. {proc.get('procedure_name')} (success rate: {success_rate:.1%})")
        
        # Add constraints and goals
        if context.constraints:
            prompt_parts.extend([
                "",
                "## Constraints",
                json.dumps(context.constraints, indent=2)
            ])
        
        if context.goals:
            prompt_parts.extend([
                "",
                "## Goals",
                "\n".join(f"- {goal}" for goal in context.goals)
            ])
        
        # Add reasoning template
        prompt_parts.extend([
            "",
            "## Reasoning Instructions",
            template,
            "",
            "## Required Response Format",
            "Respond with a JSON object containing:",
            "- reasoning_chain: Array of reasoning steps with 'step', 'analysis', 'conclusion'",
            "- decision: Object with specific decisions/parameters to use",
            "- confidence: Number between 0.0 and 1.0 indicating confidence in decision",
            "- explanation: String explaining the reasoning and decision",
            "- alternatives_considered: Array of alternative approaches considered"
        ])
        
        return "\n".join(prompt_parts)
    
    async def _get_reasoning_template(self, reasoning_type: ReasoningType, task_type: str) -> str:
        """Get reasoning template for specific type and task."""
        
        cache_key = f"{reasoning_type.value}_{task_type}"
        
        if cache_key in self._templates:
            return self._templates[cache_key]
        
        # Build template based on reasoning type
        if reasoning_type == ReasoningType.STRATEGIC:
            template = self._build_strategic_template(task_type)
        elif reasoning_type == ReasoningType.TACTICAL:
            template = self._build_tactical_template(task_type)
        elif reasoning_type == ReasoningType.ADAPTIVE:
            template = self._build_adaptive_template(task_type)
        elif reasoning_type == ReasoningType.DIAGNOSTIC:
            template = self._build_diagnostic_template(task_type)
        elif reasoning_type == ReasoningType.PREDICTIVE:
            template = self._build_predictive_template(task_type)
        else:  # CREATIVE
            template = self._build_creative_template(task_type)
        
        # Cache the template
        self._templates[cache_key] = template
        
        return template
    
    def _build_strategic_template(self, task_type: str) -> str:
        """Build strategic reasoning template."""
        return f"""
You are reasoning strategically about how to approach a {task_type} task.

Consider:
1. **Overall Approach**: What's the best high-level strategy?
2. **Resource Allocation**: How should computational resources be used?
3. **Risk Assessment**: What could go wrong and how to mitigate?
4. **Success Criteria**: How will you measure success?
5. **Learning Opportunities**: What can be learned for future tasks?

Use memory insights to inform your strategic decisions. Focus on long-term optimization over short-term gains.
"""
    
    def _build_tactical_template(self, task_type: str) -> str:
        """Build tactical reasoning template."""
        if task_type == "entity_extraction":
            return """
You are performing entity extraction on the provided text.

IMPORTANT: For entity_extraction tasks, the 'decision' field MUST contain an 'entities' array with the actual extracted entities.

Each entity should have:
- text: The entity text as it appears
- type: The entity type (PERSON, GPE, DATE, ORG, etc.)
- start: Start character position
- end: End character position
- confidence: Confidence score (0.0-1.0)
- reasoning: Brief explanation

Example decision format:
{
  "entities": [
    {"text": "Albert Einstein", "type": "PERSON", "start": 0, "end": 15, "confidence": 0.95, "reasoning": "Full name of a person"},
    {"text": "Germany", "type": "GPE", "start": 30, "end": 37, "confidence": 0.90, "reasoning": "Country name"},
    {"text": "1879", "type": "DATE", "start": 41, "end": 45, "confidence": 0.95, "reasoning": "Year"}
  ]
}

Extract ALL entities from the text provided in the task parameters.
"""
        else:
            return f"""
You are reasoning tactically about the specific execution of a {task_type} task.

Consider:
1. **Parameter Optimization**: What are the optimal parameters based on memory?
2. **Execution Order**: What's the best sequence of operations?  
3. **Quality vs Speed**: How to balance quality and performance?
4. **Error Handling**: How to handle potential failures gracefully?
5. **Output Validation**: How to ensure results meet requirements?

Use learned patterns and procedures to optimize tactical execution decisions.
"""
    
    def _build_adaptive_template(self, task_type: str) -> str:
        """Build adaptive reasoning template.""" 
        return f"""
You are reasoning about how to adapt and improve performance on {task_type} tasks.

Consider:
1. **Performance Analysis**: How is current performance compared to past?
2. **Learning Integration**: How to apply learned patterns effectively?
3. **Parameter Adjustment**: What parameters should be adjusted based on experience?
4. **Strategy Evolution**: How should the approach evolve over time?
5. **Feedback Integration**: How to incorporate results into future decisions?

Focus on continuous improvement and learning from memory insights.
"""
    
    def _build_diagnostic_template(self, task_type: str) -> str:
        """Build diagnostic reasoning template."""
        return f"""
You are diagnosing issues or analyzing performance for a {task_type} task.

Consider:
1. **Problem Identification**: What specific issues need to be addressed?
2. **Root Cause Analysis**: What are the underlying causes?
3. **Pattern Recognition**: Do memory insights reveal recurring issues?
4. **Solution Options**: What are the possible solutions?
5. **Validation Approach**: How to verify the diagnosis and solutions?

Use memory insights to identify patterns and inform diagnostic decisions.
"""
    
    def _build_predictive_template(self, task_type: str) -> str:
        """Build predictive reasoning template."""
        return f"""
You are predicting outcomes and performance for a {task_type} task.

Consider:
1. **Outcome Prediction**: What are the likely results based on parameters?
2. **Performance Estimation**: How long will execution take?
3. **Success Probability**: What's the likelihood of success?
4. **Resource Requirements**: What resources will be needed?
5. **Risk Factors**: What factors could impact success?

Use memory patterns and historical performance to make accurate predictions.
"""
    
    def _build_creative_template(self, task_type: str) -> str:
        """Build creative reasoning template."""
        return f"""
You are creatively reasoning about novel approaches to a {task_type} task.

Consider:
1. **Alternative Approaches**: What unconventional methods could work?
2. **Innovation Opportunities**: How to improve beyond current methods?
3. **Cross-Domain Solutions**: What techniques from other domains apply?
4. **Efficiency Innovations**: How to achieve better results with less effort?
5. **Quality Enhancements**: How to improve output quality creatively?

Balance creativity with practical constraints and memory-based insights.
"""
    
    def _extract_memory_insights(self, memory_context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract actionable insights from memory context."""
        return {
            "relevant_executions": memory_context.get("relevant_executions", []),
            "learned_patterns": memory_context.get("learned_patterns", []),
            "procedures": memory_context.get("procedures", []),
            "working_memory": memory_context.get("working_memory", {}),
            "success_patterns": [
                exec_info for exec_info in memory_context.get("relevant_executions", [])
                if exec_info.get("success")
            ],
            "failure_patterns": [
                exec_info for exec_info in memory_context.get("relevant_executions", [])
                if not exec_info.get("success")
            ]
        }
    
    async def _execute_llm_reasoning(self, prompt: str, context: ReasoningContext) -> str:
        """Execute LLM reasoning with structured output using LiteLLM directly."""
        
        # Import structured output dependencies
        import litellm
        import os
        from dotenv import load_dotenv
        load_dotenv()
        
        # Import reasoning schemas
        import sys
        sys.path.append(os.path.dirname(__file__))
        from reasoning_schema import ReasoningResponse, EntityExtractionResponse
        
        # Choose schema based on task type
        if context.task.task_type == "entity_extraction":
            schema = EntityExtractionResponse
        else:
            schema = ReasoningResponse
        
        # Get schema for structured output
        schema_dict = schema.model_json_schema()
        
        self.logger.info(f"Using structured output with {schema.__name__} schema for {context.reasoning_type.value} reasoning")
        
        # Add schema instruction to prompt
        structured_prompt = f"""{prompt}

IMPORTANT: Respond with valid JSON that matches this exact schema:

{schema.model_json_schema()}

Your response must be valid JSON only, no markdown formatting."""
        
        # Use LiteLLM with structured output directly - NO FALLBACK
        response = litellm.completion(
            model="gemini/gemini-2.5-flash",
            messages=[{"role": "user", "content": structured_prompt}],
            response_format={"type": "json_object"},
            temperature=self.llm_config.get("temperature", 0.1),
            max_tokens=self.llm_config.get("max_tokens", 32000)
        )
        
        response_text = response.choices[0].message.content
        
        self.logger.info(f"Successfully used structured output with LiteLLM")
        return response_text
    
    
    def _extract_json_from_response(self, response: str) -> str:
        """Extract JSON from Gemini 2.5 Flash response with robust handling."""
        import re
        
        # Check for obvious truncation signs - but only at the END of response
        response_end = response.strip()[-200:]  # Check last 200 chars only
        
        truncation_indicators = [
            'content requirements',  # Common truncation point we saw
            '..."',  # Incomplete quotes
        ]
        
        # Only check for truncation if response doesn't end properly with } or ```
        if not (response.strip().endswith('}') or response.strip().endswith('```')):
            for indicator in truncation_indicators:
                if indicator in response_end:
                    self.logger.warning(f"Response appears truncated (contains '{indicator}' near end)")
                    raise ValueError(f"Response appears truncated at '{indicator}' - increase max_output_tokens")
        
        # Remove common markdown artifacts
        cleaned = response.strip()
        
        # Remove markdown code blocks - handle common formats  
        if cleaned.startswith('```json'):
            # Remove ```json from start
            cleaned = cleaned[7:].strip()
            # Remove ending ``` if present
            if cleaned.endswith('```'):
                cleaned = cleaned[:-3].strip()
        elif cleaned.startswith('```') and cleaned.endswith('```'):
            # Remove surrounding ```
            cleaned = cleaned[3:-3].strip()
        
        # Check if JSON looks complete (basic sanity check)
        if cleaned.startswith('{') and not cleaned.endswith('}'):
            self.logger.warning("JSON starts with { but doesn't end with } - likely truncated")
            raise ValueError("JSON appears truncated - missing closing brace")
        
        # Try multiple JSON extraction strategies
        strategies = [
            # Strategy 1: Direct JSON if starts with {
            lambda text: text if text.strip().startswith('{') else None,
            
            # Strategy 2: Find first complete JSON object
            lambda text: self._find_complete_json(text),
            
            # Strategy 3: Extract between first { and last }
            lambda text: self._extract_between_braces(text),
            
            # Strategy 4: Clean and try again
            lambda text: self._clean_and_extract(text)
        ]
        
        for i, strategy in enumerate(strategies):
            try:
                result = strategy(cleaned)
                if result:
                    # Validate it's valid JSON
                    parsed = json.loads(result)
                    
                    # Additional validation for completeness
                    required_fields = ['reasoning_chain', 'decision', 'confidence', 'explanation']
                    missing_fields = [f for f in required_fields if f not in parsed]
                    if missing_fields:
                        self.logger.warning(f"JSON missing required fields: {missing_fields}")
                        raise ValueError(f"Incomplete JSON - missing fields: {missing_fields}")
                    
                    self.logger.debug(f"Strategy {i+1} succeeded")
                    return result
            except json.JSONDecodeError as e:
                self.logger.debug(f"Strategy {i+1} JSON parsing failed: {e}")
                continue
            except Exception as e:
                self.logger.debug(f"Strategy {i+1} failed: {e}")
                continue
        
        self.logger.debug(f"All strategies failed. Cleaned text (first 300 chars): {cleaned[:300]}")
        self.logger.debug(f"Response ends with: '{response[-50:]}'")
        raise ValueError("Could not extract valid JSON from response - check for truncation or format issues")
    
    def _find_complete_json(self, text: str) -> str:
        """Find the first complete JSON object in text."""
        import re
        
        # Look for JSON object with balanced braces
        brace_count = 0
        start_idx = text.find('{')
        if start_idx == -1:
            return None
            
        for i, char in enumerate(text[start_idx:], start_idx):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    return text[start_idx:i+1]
        return None
    
    def _extract_between_braces(self, text: str) -> str:
        """Extract text between first { and last }."""
        first_brace = text.find('{')
        last_brace = text.rfind('}')
        
        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            return text[first_brace:last_brace+1]
        return None
    
    def _clean_and_extract(self, text: str) -> str:
        """Clean text and try to extract JSON.""" 
        # For responses that are mostly JSON, just find the complete object
        return self._find_complete_json(text)

    async def _parse_reasoning_response(self, llm_response: str, context: ReasoningContext) -> ReasoningResult:
        """Parse LLM response into structured reasoning result."""
        
        try:
            # Universal LLM Kit returns structured JSON, so parse directly
            response_data = json.loads(llm_response)
            
            # Handle different response schemas
            if context.task.task_type == "entity_extraction":
                # EntityExtractionResponse schema
                decision = response_data["decision"]
                # Convert to legacy format if needed
                if "entities" in decision:
                    decision = decision  # Already in correct format
            else:
                decision = response_data["decision"]
            
            # Create structured result
            return ReasoningResult(
                success=True,
                reasoning_chain=response_data["reasoning_chain"],
                decision=decision,
                confidence=float(response_data["confidence"]),
                explanation=response_data["explanation"],
                alternatives_considered=response_data.get("alternatives_considered", []),
                metadata={"tokens_used": 1000, "model_used": "universal_llm_kit"}
            )
            
        except Exception as e:
            self.logger.error(f"Failed to parse reasoning response: {e}")
            self.logger.debug(f"Raw LLM response that failed parsing: {llm_response[:1000]}")
            
            # Create fallback result
            return ReasoningResult(
                success=False,
                reasoning_chain=[],
                decision={},
                confidence=0.0,
                explanation=f"Failed to parse reasoning response: {str(e)}",
                error=str(e)
            )
    
    def _update_reasoning_stats(self, reasoning_type: ReasoningType, execution_time: float, success: bool):
        """Update reasoning performance statistics."""
        self._reasoning_stats["total_reasonings"] += 1
        
        if success:
            self._reasoning_stats["successful_reasonings"] += 1
        
        # Update average reasoning time
        current_avg = self._reasoning_stats["avg_reasoning_time"]
        total_count = self._reasoning_stats["total_reasonings"]
        
        self._reasoning_stats["avg_reasoning_time"] = (
            (current_avg * (total_count - 1) + execution_time) / total_count
        )
        
        # Update reasoning by type
        type_key = reasoning_type.value
        if type_key not in self._reasoning_stats["reasoning_by_type"]:
            self._reasoning_stats["reasoning_by_type"][type_key] = {
                "count": 0,
                "success_count": 0,
                "avg_time": 0.0
            }
        
        type_stats = self._reasoning_stats["reasoning_by_type"][type_key]
        type_stats["count"] += 1
        
        if success:
            type_stats["success_count"] += 1
        
        # Update average time for this type
        type_count = type_stats["count"]
        type_stats["avg_time"] = (
            (type_stats["avg_time"] * (type_count - 1) + execution_time) / type_count
        )
    
    def get_reasoning_stats(self) -> Dict[str, Any]:
        """Get reasoning engine performance statistics."""
        total = self._reasoning_stats["total_reasonings"]
        successful = self._reasoning_stats["successful_reasonings"]
        
        return {
            "total_reasonings": total,
            "successful_reasonings": successful,
            "success_rate": successful / total if total > 0 else 0.0,
            "avg_reasoning_time": self._reasoning_stats["avg_reasoning_time"],
            "reasoning_by_type": self._reasoning_stats["reasoning_by_type"].copy()
        }
    
    async def suggest_reasoning_type(self, task: Task, memory_context: Dict[str, Any]) -> ReasoningType:
        """Suggest appropriate reasoning type for a task."""
        
        # Analyze task characteristics
        task_complexity = len(task.parameters)
        memory_richness = len(memory_context.get("relevant_executions", []))
        has_failures = any(
            not exec_info.get("success", True) 
            for exec_info in memory_context.get("relevant_executions", [])
        )
        
        # Decision logic for reasoning type
        if has_failures:
            return ReasoningType.DIAGNOSTIC
        elif memory_richness >= 5:
            return ReasoningType.ADAPTIVE
        elif task_complexity >= 5:
            return ReasoningType.STRATEGIC
        elif memory_richness >= 2:
            return ReasoningType.TACTICAL
        else:
            return ReasoningType.CREATIVE
    
    async def create_custom_reasoning_template(self, template_name: str, template_content: str) -> None:
        """Create custom reasoning template."""
        self._templates[template_name] = template_content
        self.logger.info(f"Created custom reasoning template: {template_name}")
    
    async def clear_reasoning_cache(self) -> None:
        """Clear cached reasoning templates."""
        self._templates.clear()
        self.logger.info("Cleared reasoning template cache")
    
