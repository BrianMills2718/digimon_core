"""
Pydantic schemas for LLM reasoning structured output
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum

class ReasoningStep(BaseModel):
    """Individual reasoning step"""
    step: str = Field(description="Name or identifier of the reasoning step")
    analysis: str = Field(description="Analysis performed in this step")
    conclusion: str = Field(description="Conclusion reached in this step")

class AlternativeApproach(BaseModel):
    """Alternative approach considered"""
    approach: str = Field(description="Name of the alternative approach")
    description: str = Field(description="Description of why it was considered")
    reason_for_rejection: Optional[str] = Field(description="Why this approach was not chosen", default=None)

class ReasoningResponse(BaseModel):
    """Structured response from LLM reasoning"""
    reasoning_chain: List[ReasoningStep] = Field(description="Array of reasoning steps with detailed analysis")
    decision: Dict[str, Any] = Field(description="Specific decisions and parameters to use")
    confidence: float = Field(description="Confidence level between 0.0 and 1.0", ge=0.0, le=1.0)
    explanation: str = Field(description="Clear explanation of the reasoning and final decision")
    alternatives_considered: List[AlternativeApproach] = Field(description="Alternative approaches that were considered", default_factory=list)

class EntityExtractionDecision(BaseModel):
    """Specific decision format for entity extraction tasks"""
    entities: List[Dict[str, Any]] = Field(description="Array of extracted entities with text, type, position, confidence")
    confidence_threshold: float = Field(description="Confidence threshold used for extraction")
    use_learned_filters: bool = Field(description="Whether to apply learned filtering patterns")
    
class EntityExtractionResponse(BaseModel):
    """Structured response for entity extraction reasoning"""
    reasoning_chain: List[ReasoningStep] = Field(description="Steps in entity extraction reasoning")
    decision: EntityExtractionDecision = Field(description="Entity extraction decisions")
    confidence: float = Field(description="Overall confidence in extraction results", ge=0.0, le=1.0)
    explanation: str = Field(description="Explanation of entity extraction approach")
    alternatives_considered: List[AlternativeApproach] = Field(default_factory=list)

# Schema for direct LLM entity extraction (without reasoning wrapper)
class ExtractedEntity(BaseModel):
    """Individual extracted entity"""
    text: str = Field(description="Exact text span from original document")
    type: str = Field(description="Entity type (e.g., PERSON, ORG, GPE, DATE)")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0", ge=0.0, le=1.0)
    context: str = Field(description="Surrounding context where entity was found")
    start_pos: Optional[int] = Field(description="Start character position in text", default=None)
    end_pos: Optional[int] = Field(description="End character position in text", default=None)

class ExtractedRelationship(BaseModel):
    """Individual extracted relationship"""
    source: str = Field(description="Source entity text")
    target: str = Field(description="Target entity text")
    relation: str = Field(description="Relationship type")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0", ge=0.0, le=1.0)
    context: str = Field(description="Context where relationship was found")

class LLMExtractionResponse(BaseModel):
    """Direct LLM extraction response for structured output"""
    entities: List[ExtractedEntity] = Field(description="Array of extracted entities")
    relationships: List[ExtractedRelationship] = Field(description="Array of extracted relationships")
    extraction_confidence: float = Field(description="Overall extraction confidence", ge=0.0, le=1.0)
    text_analyzed: str = Field(description="Summary of text that was analyzed")
    ontology_domain: Optional[str] = Field(description="Domain ontology used", default=None)

# MCP Adapter Structured Output Schemas
class MCPToolResult(BaseModel):
    """Individual MCP tool execution result"""
    tool_name: str = Field(description="Name of the executed tool")
    success: bool = Field(description="Whether tool execution was successful")
    output: Any = Field(description="Tool output data (can be any type)")
    error_message: Optional[str] = Field(description="Error message if execution failed", default=None)
    execution_time: float = Field(description="Time taken to execute tool in seconds")
    metadata: Dict[str, Any] = Field(description="Additional metadata about execution", default_factory=dict)

class MCPBatchToolResult(BaseModel):
    """Result of executing multiple MCP tools in batch"""
    tools_executed: List[MCPToolResult] = Field(description="Results from individual tool executions")
    batch_success: bool = Field(description="Whether the entire batch was successful")
    total_execution_time: float = Field(description="Total time for all tools in seconds")
    successful_tools: int = Field(description="Number of tools that executed successfully")
    failed_tools: int = Field(description="Number of tools that failed")

class MCPToolSelection(BaseModel):
    """LLM decision for tool selection and orchestration"""
    selected_tools: List[str] = Field(description="List of tool names to execute")
    execution_order: List[str] = Field(description="Order to execute tools")
    tool_parameters: Dict[str, Dict[str, Any]] = Field(description="Parameters for each tool")
    rationale: str = Field(description="Explanation for tool selection and ordering")
    expected_outcomes: List[str] = Field(description="Expected outcomes from tool execution")

class MCPOrchestrationResponse(BaseModel):
    """Structured response for MCP tool orchestration decisions"""
    reasoning_chain: List[ReasoningStep] = Field(description="Steps in tool selection reasoning")
    decision: MCPToolSelection = Field(description="Tool selection and orchestration decision")
    confidence: float = Field(description="Confidence in tool selection", ge=0.0, le=1.0)
    explanation: str = Field(description="Explanation of orchestration approach")
    alternatives_considered: List[AlternativeApproach] = Field(default_factory=list)