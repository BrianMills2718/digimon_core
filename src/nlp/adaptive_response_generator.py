"""
Adaptive Response Generator

Generates responses from dynamic execution results with intelligent adaptation
to variable tool execution outcomes and execution plan modifications.
"""

import logging
import asyncio
from typing import Dict, List, Set, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path

from .question_complexity_analyzer import ComplexityLevel, ComplexityAnalysisResult
from .advanced_intent_classifier import QuestionIntent
from .result_synthesizer import ResultSynthesizer, SynthesisResult, SynthesisStrategy
from .confidence_aggregator import ConfidenceAggregator, ConfidenceMetrics
from ..execution.execution_planner import ExecutionPlan

logger = logging.getLogger(__name__)


class ResponseAdaptation(Enum):
    """Types of response adaptations"""
    NONE = "none"                          # No adaptation needed
    FILL_GAPS = "fill_gaps"               # Fill in missing information
    ACKNOWLEDGE_FAILURES = "acknowledge_failures"  # Address failed executions
    SIMPLIFY_COMPLEXITY = "simplify_complexity"   # Simplify complex results
    ENHANCE_CONFIDENCE = "enhance_confidence"     # Add confidence indicators
    REORDER_PRIORITIES = "reorder_priorities"     # Reorder information by importance
    ADD_CONTEXT = "add_context"           # Add contextual information
    HIGHLIGHT_UNCERTAINTIES = "highlight_uncertainties"  # Call out uncertain results


@dataclass
class ResponseContext:
    """Context for adaptive response generation"""
    original_question: str
    question_intent: QuestionIntent
    complexity_analysis: ComplexityAnalysisResult
    original_plan: ExecutionPlan
    actual_execution: Dict[str, Any]
    execution_summary: Dict[str, Any]
    synthesis_result: SynthesisResult
    available_data: Dict[str, Any]
    failed_tools: List[str] = field(default_factory=list)
    skipped_tools: List[str] = field(default_factory=list)
    confidence_metrics: Optional[ConfidenceMetrics] = None
    adaptation_history: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class AdaptiveResponse:
    """Adaptive response with metadata"""
    response_text: str
    confidence_score: float
    adaptations_applied: List[ResponseAdaptation]
    information_completeness: float
    response_quality: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    reasoning: str = ""
    limitations: List[str] = field(default_factory=list)
    alternative_suggestions: List[str] = field(default_factory=list)


class AdaptiveResponseGenerator:
    """Generates adaptive responses from dynamic execution results"""
    
    def __init__(self):
        """Initialize adaptive response generator"""
        self.logger = logger
        self.synthesizer = ResultSynthesizer()
        self.confidence_aggregator = ConfidenceAggregator()
        
        # Response adaptation rules
        self.adaptation_rules = self._initialize_adaptation_rules()
        
        # Response templates for different scenarios
        self.response_templates = self._initialize_response_templates()
        
        # Quality thresholds
        self.quality_thresholds = {
            'minimum_confidence': 0.6,
            'minimum_completeness': 0.7,
            'adaptation_trigger': 0.8
        }
        
        self.logger.info("Initialized adaptive response generator")
    
    async def generate_adaptive_response(self, context: ResponseContext) -> AdaptiveResponse:
        """Generate adaptive response based on execution context"""
        
        self.logger.info(f"Generating adaptive response for question: {context.original_question[:100]}...")
        
        # Analyze execution results and determine needed adaptations
        adaptations_needed = await self._analyze_adaptation_needs(context)
        
        # Generate base response from synthesis result
        base_response = await self._generate_base_response(context)
        
        # Apply adaptations to improve response
        adapted_response = await self._apply_adaptations(
            base_response, adaptations_needed, context
        )
        
        # Calculate response quality and confidence
        response_quality = await self._assess_response_quality(adapted_response, context)
        confidence_score = await self._calculate_response_confidence(adapted_response, context)
        
        # Build final adaptive response
        final_response = AdaptiveResponse(
            response_text=adapted_response,
            confidence_score=confidence_score,
            adaptations_applied=adaptations_needed,
            information_completeness=self._calculate_completeness(context),
            response_quality=response_quality,
            reasoning=self._explain_adaptation_reasoning(adaptations_needed, context),
            limitations=self._identify_response_limitations(context),
            alternative_suggestions=self._generate_alternative_suggestions(context)
        )
        
        self.logger.info(f"Generated adaptive response with {len(adaptations_needed)} adaptations")
        return final_response
    
    async def _analyze_adaptation_needs(self, context: ResponseContext) -> List[ResponseAdaptation]:
        """Analyze what adaptations are needed for the response"""
        
        adaptations = []
        
        # Check for failed or skipped tools
        if context.failed_tools or context.skipped_tools:
            adaptations.append(ResponseAdaptation.ACKNOWLEDGE_FAILURES)
            adaptations.append(ResponseAdaptation.FILL_GAPS)
        
        # Check confidence levels
        if context.confidence_metrics and context.confidence_metrics.overall_confidence < self.quality_thresholds['minimum_confidence']:
            adaptations.append(ResponseAdaptation.ENHANCE_CONFIDENCE)
            adaptations.append(ResponseAdaptation.HIGHLIGHT_UNCERTAINTIES)
        
        # Check information completeness
        completeness = self._calculate_completeness(context)
        if completeness < self.quality_thresholds['minimum_completeness']:
            adaptations.append(ResponseAdaptation.FILL_GAPS)
            adaptations.append(ResponseAdaptation.ADD_CONTEXT)
        
        # Check question complexity vs available results
        if context.complexity_analysis.level == ComplexityLevel.COMPLEX:
            findings_count = len([frag for frag in context.synthesis_result.supporting_fragments if frag.fragment_type == "finding"])
            if findings_count < 3:
                adaptations.append(ResponseAdaptation.SIMPLIFY_COMPLEXITY)
            else:
                adaptations.append(ResponseAdaptation.REORDER_PRIORITIES)
        
        # Check execution adaptations made
        if context.adaptation_history:
            adaptations.append(ResponseAdaptation.ADD_CONTEXT)
        
        return list(set(adaptations))  # Remove duplicates
    
    async def _generate_base_response(self, context: ResponseContext) -> str:
        """Generate base response from synthesis result"""
        
        synthesis = context.synthesis_result
        intent = context.question_intent
        
        # Choose appropriate response template
        template_key = self._select_response_template(intent, context.complexity_analysis)
        template = self.response_templates.get(template_key, self.response_templates['default'])
        
        # Build response components
        response_parts = []
        
        # Add primary response
        if synthesis.primary_response:
            response_parts.append(f"**Summary**: {synthesis.primary_response}")
        
        # Add key findings from supporting fragments
        if synthesis.supporting_fragments:
            findings = [frag.content for frag in synthesis.supporting_fragments if frag.fragment_type == "finding"]
            if findings:
                response_parts.append("**Key Findings**:")
                for i, finding in enumerate(findings, 1):
                    response_parts.append(f"{i}. {finding}")
        
        # Add specific answer based on intent
        if intent == QuestionIntent.SPECIFIC_SEARCH:
            # Look for answer fragments
            answers = [frag.content for frag in synthesis.supporting_fragments if frag.fragment_type == "answer"]
            if answers:
                response_parts.append(f"**Answer**: {answers[0]}")
        
        elif intent == QuestionIntent.COMPARATIVE_ANALYSIS:
            # Look for comparison fragments
            comparisons = [frag.content for frag in synthesis.supporting_fragments if frag.fragment_type == "comparison"]
            if comparisons:
                response_parts.append("**Comparison**:")
                for comparison in comparisons:
                    response_parts.append(f"- {comparison}")
        
        elif intent == QuestionIntent.CAUSAL_ANALYSIS:
            # Look for causal relationship fragments
            relationships = [frag.content for frag in synthesis.supporting_fragments if frag.fragment_type == "relationship"]
            if relationships:
                response_parts.append("**Causal Relationships**:")
                for relationship in relationships:
                    response_parts.append(f"- {relationship}")
        
        # Add evidence from supporting evidence
        evidence_fragments = [frag.content for frag in synthesis.supporting_fragments if frag.fragment_type == "evidence"]
        if evidence_fragments:
            response_parts.append("**Supporting Evidence**:")
            for evidence in evidence_fragments[:3]:  # Limit to top 3
                response_parts.append(f"- {evidence}")
        
        return "\n\n".join(response_parts)
    
    async def _apply_adaptations(self, base_response: str, 
                               adaptations: List[ResponseAdaptation],
                               context: ResponseContext) -> str:
        """Apply adaptations to improve response"""
        
        adapted_response = base_response
        
        for adaptation in adaptations:
            if adaptation == ResponseAdaptation.ACKNOWLEDGE_FAILURES:
                adapted_response = await self._apply_failure_acknowledgment(adapted_response, context)
            
            elif adaptation == ResponseAdaptation.FILL_GAPS:
                adapted_response = await self._apply_gap_filling(adapted_response, context)
            
            elif adaptation == ResponseAdaptation.ENHANCE_CONFIDENCE:
                adapted_response = await self._apply_confidence_enhancement(adapted_response, context)
            
            elif adaptation == ResponseAdaptation.HIGHLIGHT_UNCERTAINTIES:
                adapted_response = await self._apply_uncertainty_highlighting(adapted_response, context)
            
            elif adaptation == ResponseAdaptation.SIMPLIFY_COMPLEXITY:
                adapted_response = await self._apply_complexity_simplification(adapted_response, context)
            
            elif adaptation == ResponseAdaptation.REORDER_PRIORITIES:
                adapted_response = await self._apply_priority_reordering(adapted_response, context)
            
            elif adaptation == ResponseAdaptation.ADD_CONTEXT:
                adapted_response = await self._apply_context_addition(adapted_response, context)
        
        return adapted_response
    
    async def _apply_failure_acknowledgment(self, response: str, context: ResponseContext) -> str:
        """Add acknowledgment of failed or skipped tools"""
        
        acknowledgments = []
        
        if context.failed_tools:
            tool_names = [tool.replace('_', ' ').title() for tool in context.failed_tools]
            acknowledgments.append(
                f"*Note: Some analysis tools ({', '.join(tool_names)}) encountered issues, "
                f"which may limit the completeness of this response.*"
            )
        
        if context.skipped_tools:
            tool_names = [tool.replace('_', ' ').title() for tool in context.skipped_tools]
            acknowledgments.append(
                f"*Note: Some analysis steps ({', '.join(tool_names)}) were skipped "
                f"to optimize processing time.*"
            )
        
        if acknowledgments:
            return response + "\n\n" + "\n".join(acknowledgments)
        
        return response
    
    async def _apply_gap_filling(self, response: str, context: ResponseContext) -> str:
        """Fill in information gaps where possible"""
        
        # Check what information is missing and try to fill from available data
        available_data = context.available_data
        
        gap_fillers = []
        
        # Check for entity information
        if 'entities' in available_data and available_data['entities']:
            entities = available_data['entities'][:5]  # Top 5 entities
            gap_fillers.append(
                f"**Key Entities Identified**: {', '.join(entities)}"
            )
        
        # Check for relationship information
        if 'relationships' in available_data and available_data['relationships']:
            rel_count = len(available_data['relationships'])
            gap_fillers.append(
                f"**Relationships Found**: {rel_count} connections between entities were identified."
            )
        
        # Check for temporal information
        if 'temporal_entities' in available_data and available_data['temporal_entities']:
            gap_fillers.append(
                f"**Time Period**: Analysis covers {len(available_data['temporal_entities'])} time-related references."
            )
        
        if gap_fillers:
            return response + "\n\n**Additional Information**:\n" + "\n".join(gap_fillers)
        
        return response
    
    async def _apply_confidence_enhancement(self, response: str, context: ResponseContext) -> str:
        """Add confidence indicators to response"""
        
        if not context.confidence_metrics:
            return response
        
        confidence = context.confidence_metrics.overall_confidence
        
        confidence_note = ""
        if confidence >= 0.8:
            confidence_note = "**Confidence**: High confidence in these findings."
        elif confidence >= 0.6:
            confidence_note = "**Confidence**: Moderate confidence in these findings."
        else:
            confidence_note = "**Confidence**: Lower confidence - these findings should be verified."
        
        # Add confidence breakdown if available
        if context.confidence_metrics.tool_confidences:
            tool_conf = context.confidence_metrics.tool_confidences
            high_conf_tools = [tool for tool, conf in tool_conf.items() if conf > 0.8]
            if high_conf_tools:
                confidence_note += f" Highest confidence from: {', '.join(high_conf_tools[:3])}."
        
        return response + "\n\n" + confidence_note
    
    async def _apply_uncertainty_highlighting(self, response: str, context: ResponseContext) -> str:
        """Highlight areas of uncertainty"""
        
        uncertainties = []
        
        # Check for low confidence areas
        if context.confidence_metrics and context.confidence_metrics.uncertainty_sources:
            for source, uncertainty in context.confidence_metrics.uncertainty_sources.items():
                if uncertainty > 0.3:  # High uncertainty
                    uncertainties.append(f"- Uncertainty in {source.replace('_', ' ')}")
        
        # Check for incomplete data
        if context.failed_tools:
            uncertainties.append("- Some data sources were unavailable")
        
        # Check for conflicting information (from caveats)
        if context.synthesis_result.caveats:
            uncertainties.append("- Some conflicting information was found")
        
        if uncertainties:
            uncertainty_note = "**Areas of Uncertainty**:\n" + "\n".join(uncertainties)
            return response + "\n\n" + uncertainty_note
        
        return response
    
    async def _apply_complexity_simplification(self, response: str, context: ResponseContext) -> str:
        """Simplify complex responses"""
        
        # For complex questions with limited results, provide clearer structure
        lines = response.split('\n')
        simplified_lines = []
        
        current_section = ""
        for line in lines:
            if line.startswith('**') and line.endswith('**:'):
                current_section = line
                simplified_lines.append(line)
            elif line.strip() and not line.startswith('-') and not line.startswith(' '):
                # Add bullet point for better readability
                simplified_lines.append(f"• {line.strip()}")
            else:
                simplified_lines.append(line)
        
        simplified_response = '\n'.join(simplified_lines)
        
        # Add summary note for complex questions
        summary_note = (
            "\n\n**Simplified Summary**: This analysis addresses your complex question "
            "by breaking down the available information into key points above."
        )
        
        return simplified_response + summary_note
    
    async def _apply_priority_reordering(self, response: str, context: ResponseContext) -> str:
        """Reorder information by importance/relevance"""
        
        # For now, ensure most important information comes first
        # This is a simplified implementation - could be enhanced with ML ranking
        
        lines = response.split('\n')
        priority_sections = []
        other_sections = []
        
        current_section = []
        section_title = ""
        
        for line in lines:
            if line.startswith('**') and line.endswith('**:'):
                # Save previous section
                if current_section and section_title:
                    if any(keyword in section_title.lower() for keyword in ['summary', 'answer', 'key findings']):
                        priority_sections.append((section_title, current_section))
                    else:
                        other_sections.append((section_title, current_section))
                
                # Start new section
                section_title = line
                current_section = [line]
            else:
                current_section.append(line)
        
        # Handle last section
        if current_section and section_title:
            if any(keyword in section_title.lower() for keyword in ['summary', 'answer', 'key findings']):
                priority_sections.append((section_title, current_section))
            else:
                other_sections.append((section_title, current_section))
        
        # Reconstruct response with priority sections first
        reordered_lines = []
        for title, section in priority_sections:
            reordered_lines.extend(section)
        
        for title, section in other_sections:
            reordered_lines.extend(section)
        
        return '\n'.join(reordered_lines)
    
    async def _apply_context_addition(self, response: str, context: ResponseContext) -> str:
        """Add relevant context about the analysis process"""
        
        context_notes = []
        
        # Add information about execution adaptations
        if context.adaptation_history:
            adaptation_count = len(context.adaptation_history)
            context_notes.append(
                f"*Analysis Note: The system made {adaptation_count} adaptive adjustments "
                f"during processing to optimize results.*"
            )
        
        # Add information about processing strategy
        if context.execution_summary:
            total_time = context.execution_summary.get('total_time', 0)
            completed_steps = context.execution_summary.get('completed_steps', 0)
            total_steps = context.execution_summary.get('total_steps', 0)
            
            if total_steps > 0:
                context_notes.append(
                    f"*Processing Info: Completed {completed_steps}/{total_steps} analysis steps "
                    f"in {total_time:.1f} seconds.*"
                )
        
        # Add information about question complexity
        if context.complexity_analysis.level == ComplexityLevel.COMPLEX:
            context_notes.append(
                "*Complexity Note: This was identified as a complex question requiring "
                "multi-step analysis.*"
            )
        
        if context_notes:
            return response + "\n\n" + "\n".join(context_notes)
        
        return response
    
    async def _assess_response_quality(self, response: str, context: ResponseContext) -> float:
        """Assess the quality of the generated response"""
        
        quality_factors = []
        
        # Length and structure quality
        word_count = len(response.split())
        if 50 <= word_count <= 500:
            quality_factors.append(0.9)
        elif 20 <= word_count < 50 or 500 < word_count <= 1000:
            quality_factors.append(0.7)
        else:
            quality_factors.append(0.5)
        
        # Information completeness
        completeness = self._calculate_completeness(context)
        quality_factors.append(completeness)
        
        # Confidence alignment
        if context.confidence_metrics:
            confidence_alignment = min(1.0, context.confidence_metrics.overall_confidence + 0.2)
            quality_factors.append(confidence_alignment)
        
        # Structure quality (presence of sections)
        structure_score = 0.6  # Base score
        if '**' in response:  # Has structured sections
            structure_score += 0.2
        if any(keyword in response.lower() for keyword in ['summary', 'findings', 'answer']):
            structure_score += 0.2
        quality_factors.append(min(1.0, structure_score))
        
        return sum(quality_factors) / len(quality_factors)
    
    async def _calculate_response_confidence(self, response: str, context: ResponseContext) -> float:
        """Calculate confidence in the response"""
        
        if context.confidence_metrics:
            base_confidence = context.confidence_metrics.overall_confidence
        else:
            base_confidence = 0.7  # Default moderate confidence
        
        # Adjust based on information completeness
        completeness = self._calculate_completeness(context)
        completeness_factor = 0.8 + (completeness * 0.2)
        
        # Adjust based on failed tools
        failure_penalty = len(context.failed_tools) * 0.1
        
        # Adjust based on adaptations made
        adaptation_bonus = min(0.1, len(context.adaptation_history) * 0.02)
        
        final_confidence = base_confidence * completeness_factor - failure_penalty + adaptation_bonus
        
        return max(0.1, min(1.0, final_confidence))
    
    def _calculate_completeness(self, context: ResponseContext) -> float:
        """Calculate information completeness"""
        
        total_planned_tools = len(context.original_plan.steps)
        failed_tools = len(context.failed_tools)
        skipped_tools = len(context.skipped_tools)
        
        successful_tools = total_planned_tools - failed_tools - skipped_tools
        basic_completeness = successful_tools / total_planned_tools if total_planned_tools > 0 else 0.0
        
        # Adjust based on available data richness
        data_richness = 0.0
        if context.available_data:
            data_sources = len(context.available_data)
            data_richness = min(1.0, data_sources / 5.0)  # Normalize to 5 expected sources
        
        # Combine factors
        return (basic_completeness * 0.7) + (data_richness * 0.3)
    
    def _explain_adaptation_reasoning(self, adaptations: List[ResponseAdaptation], 
                                   context: ResponseContext) -> str:
        """Explain why specific adaptations were applied"""
        
        if not adaptations:
            return "No adaptations were needed - standard response generation was sufficient."
        
        reasoning_parts = []
        
        for adaptation in adaptations:
            if adaptation == ResponseAdaptation.ACKNOWLEDGE_FAILURES:
                reasoning_parts.append("Acknowledged tool failures to set appropriate expectations")
            elif adaptation == ResponseAdaptation.FILL_GAPS:
                reasoning_parts.append("Filled information gaps using available data")
            elif adaptation == ResponseAdaptation.ENHANCE_CONFIDENCE:
                reasoning_parts.append("Added confidence indicators to help assess reliability")
            elif adaptation == ResponseAdaptation.HIGHLIGHT_UNCERTAINTIES:
                reasoning_parts.append("Highlighted areas of uncertainty for transparency")
            elif adaptation == ResponseAdaptation.SIMPLIFY_COMPLEXITY:
                reasoning_parts.append("Simplified presentation for better comprehension")
            elif adaptation == ResponseAdaptation.REORDER_PRIORITIES:
                reasoning_parts.append("Reordered information by importance and relevance")
            elif adaptation == ResponseAdaptation.ADD_CONTEXT:
                reasoning_parts.append("Added contextual information about the analysis process")
        
        return "Applied adaptations: " + "; ".join(reasoning_parts) + "."
    
    def _identify_response_limitations(self, context: ResponseContext) -> List[str]:
        """Identify limitations in the response"""
        
        limitations = []
        
        if context.failed_tools:
            limitations.append(f"Analysis limited by {len(context.failed_tools)} unavailable tools")
        
        if context.skipped_tools:
            limitations.append(f"{len(context.skipped_tools)} analysis steps were skipped for efficiency")
        
        completeness = self._calculate_completeness(context)
        if completeness < 0.8:
            limitations.append("Information completeness below optimal level")
        
        if context.confidence_metrics and context.confidence_metrics.overall_confidence < 0.7:
            limitations.append("Lower than ideal confidence in some findings")
        
        if context.synthesis_result.caveats:
            limitations.append("Some conflicting information found in source data")
        
        return limitations
    
    def _generate_alternative_suggestions(self, context: ResponseContext) -> List[str]:
        """Generate alternative suggestions for the user"""
        
        suggestions = []
        
        # Suggest more specific questions if original was complex
        if context.complexity_analysis.level == ComplexityLevel.COMPLEX:
            suggestions.append("Consider breaking this into more specific sub-questions")
        
        # Suggest alternative approaches if tools failed
        if context.failed_tools:
            suggestions.append("Try rephrasing the question to use different analysis approaches")
        
        # Suggest follow-up questions based on findings
        findings_count = len([frag for frag in context.synthesis_result.supporting_fragments if frag.fragment_type == "finding"])
        if findings_count > 0:
            suggestions.append("Ask follow-up questions about specific findings for deeper analysis")
        
        # Suggest broader or narrower scope
        if findings_count < 2:
            suggestions.append("Try broadening the question scope for more comprehensive results")
        elif findings_count > 8:
            suggestions.append("Try narrowing the question scope for more focused results")
        
        return suggestions[:3]  # Limit to top 3 suggestions
    
    def _select_response_template(self, intent: QuestionIntent, 
                                complexity: ComplexityAnalysisResult) -> str:
        """Select appropriate response template"""
        
        if intent == QuestionIntent.SPECIFIC_SEARCH:
            return 'factual'
        elif intent == QuestionIntent.COMPARATIVE_ANALYSIS:
            return 'comparative'
        elif intent == QuestionIntent.CAUSAL_ANALYSIS:
            return 'causal'
        elif complexity.level == ComplexityLevel.COMPLEX:
            return 'complex'
        else:
            return 'default'
    
    def _initialize_adaptation_rules(self) -> Dict[str, Any]:
        """Initialize adaptation rules"""
        
        return {
            'failure_threshold': 0.3,      # Apply failure adaptations if >30% tools failed
            'confidence_threshold': 0.6,   # Apply confidence adaptations if confidence <60%
            'completeness_threshold': 0.7, # Apply gap filling if completeness <70%
            'complexity_threshold': ComplexityLevel.COMPLEX  # Apply simplification for complex questions
        }
    
    def _initialize_response_templates(self) -> Dict[str, str]:
        """Initialize response templates"""
        
        return {
            'default': "Based on the analysis, here are the key findings:\n\n{findings}",
            'factual': "**Answer**: {answer}\n\n**Details**: {details}",
            'comparative': "**Comparison Results**:\n\n{comparisons}\n\n**Summary**: {summary}",
            'causal': "**Causal Analysis**:\n\n{relationships}\n\n**Explanation**: {explanation}",
            'complex': "**Complex Analysis Results**:\n\n{structured_findings}\n\n**Summary**: {summary}"
        }
    
    def get_adaptation_statistics(self) -> Dict[str, Any]:
        """Get statistics about adaptations applied"""
        
        # This would be implemented to track adaptation usage over time
        return {
            'total_responses_generated': 0,
            'adaptations_applied': {},
            'average_response_quality': 0.0,
            'average_confidence': 0.0
        }