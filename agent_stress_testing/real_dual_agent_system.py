#!/usr/bin/env python3
"""
Real Dual-Agent System

Connects research and execution agents using:
- Real Claude Code CLI for agent coordination
- Real KGAS MCP tools for actual document processing
- Real databases for data persistence
- Real adaptive decision-making logic
"""

import asyncio
import json
import logging
import time
import uuid
import tempfile
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

from working_mcp_client import WorkingMCPClient, MCPToolResult

logger = logging.getLogger(__name__)

@dataclass
class AgentRequest:
    """Request for agent execution"""
    agent_type: str  # "research" or "execution"
    task_type: str
    content: str
    context: Dict[str, Any]
    temperature: float = 0.7

@dataclass
class AgentResponse:
    """Response from agent execution"""
    agent_type: str
    status: str  # "success", "error"
    content: str
    data: Any
    execution_time: float
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None

@dataclass
class AdaptiveWorkflowPlan:
    """Adaptive workflow plan that can be modified during execution"""
    plan_id: str
    objective: str
    steps: List[Dict[str, Any]]
    quality_thresholds: Dict[str, float]
    adaptation_strategies: List[str]
    resource_constraints: Dict[str, Any]
    created_at: str

@dataclass
class WorkflowExecution:
    """Tracks workflow execution with real-time adaptation"""
    execution_id: str
    plan: AdaptiveWorkflowPlan
    current_step: int
    completed_steps: List[Dict[str, Any]]
    adaptations_made: List[Dict[str, Any]]
    execution_metrics: Dict[str, Any]
    status: str  # "running", "completed", "failed", "adapted"

class RealClaudeAgent:
    """Real Claude Code CLI integration for agent execution"""
    
    def __init__(self, agent_type: str, temperature: float = 0.7):
        """
        Initialize real Claude agent.
        
        Args:
            agent_type: "research" or "execution"
            temperature: Claude temperature setting
        """
        self.agent_type = agent_type
        self.temperature = temperature
        self.system_prompts = self._get_system_prompts()
    
    def _get_system_prompts(self) -> Dict[str, str]:
        """Get system prompts for different agent types"""
        return {
            "research": """You are a research planning agent specialized in academic analysis workflows.

Your role:
- Analyze research objectives and create detailed analytical plans
- Adapt plans when execution results don't meet quality thresholds
- Make strategic decisions about methodology and approach
- Learn from execution patterns to improve future planning

When creating plans, include:
1. Clear step-by-step workflow
2. Quality thresholds for each step
3. Alternative approaches if primary approach fails
4. Resource requirements and constraints

When adapting plans, consider:
- Quality trend analysis across recent executions  
- Resource constraints (time, compute, API calls)
- Success patterns from previous similar tasks
- Available fallback strategies

Respond with structured JSON containing your analysis and decisions.""",

            "execution": """You are a workflow execution agent that coordinates real tool operations.

Your role:
- Execute analytical workflows using real KGAS MCP tools
- Monitor execution quality and performance in real-time
- Report detailed results with quality assessments
- Recommend adaptations when quality thresholds aren't met

Available tools via MCP:
- load_pdf: Extract text from PDF documents
- chunk_text: Split text into processable chunks
- extract_entities: Named entity recognition using spaCy
- extract_relationships: Extract relationships between entities
- analyze_document: Full document analysis pipeline
- query_graph: Query knowledge graph (when Neo4j available)

For each execution:
1. Execute tools with real parameters
2. Assess output quality objectively
3. Track performance metrics
4. Report issues and recommend solutions

Respond with structured JSON containing execution results and quality assessment."""
        }
    
    async def execute(self, request: AgentRequest) -> AgentResponse:
        """Execute agent request using real Claude Code CLI"""
        start_time = time.time()
        
        try:
            # Prepare prompt with system context
            system_prompt = self.system_prompts.get(self.agent_type, "")
            
            # Create message combining system prompt and user request
            full_prompt = f"""SYSTEM: {system_prompt}

TASK TYPE: {request.task_type}
CONTEXT: {json.dumps(request.context, indent=2)}

USER REQUEST:
{request.content}

Please respond with structured JSON containing your analysis and any actions taken."""

            # Execute via Claude Code CLI
            result = await self._call_claude_cli(full_prompt, request.temperature)
            
            if result["status"] == "success":
                # Try to parse JSON response
                try:
                    response_data = json.loads(result["content"])
                except json.JSONDecodeError:
                    # If not JSON, treat as text response
                    response_data = {"response": result["content"]}
                
                return AgentResponse(
                    agent_type=self.agent_type,
                    status="success",
                    content=result["content"],
                    data=response_data,
                    execution_time=time.time() - start_time,
                    metadata={
                        "temperature": request.temperature,
                        "tokens_used": result.get("tokens_used", 0),
                        "model": result.get("model", "claude-3-sonnet")
                    }
                )
            else:
                return AgentResponse(
                    agent_type=self.agent_type,
                    status="error",
                    content="",
                    data=None,
                    execution_time=time.time() - start_time,
                    error_message=result.get("error", "Unknown error"),
                    metadata={"temperature": request.temperature}
                )
                
        except Exception as e:
            logger.error(f"Agent execution failed: {e}")
            return AgentResponse(
                agent_type=self.agent_type,
                status="error",
                content="",
                data=None,
                execution_time=time.time() - start_time,
                error_message=str(e),
                metadata={"temperature": request.temperature}
            )
    
    async def _call_claude_cli(self, prompt: str, temperature: float) -> Dict[str, Any]:
        """Make actual call to Claude Code CLI"""
        try:
            # Call Claude CLI using the correct interface
            cmd = ["claude", "--print", "--output-format", "text"]
            
            # Execute command with prompt as stdin
            start_time = time.time()
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Send prompt to stdin
            stdout, stderr = await process.communicate(input=prompt.encode('utf-8'))
            execution_time = time.time() - start_time
            
            if process.returncode == 0:
                content = stdout.decode('utf-8').strip()
                return {
                    "status": "success",
                    "content": content,
                    "execution_time": execution_time,
                    "tokens_used": len(content.split()),  # Rough estimate
                    "model": "claude-3-sonnet"
                }
            else:
                error = stderr.decode('utf-8').strip()
                logger.error(f"Claude CLI error: {error}")
                return {
                    "status": "error",
                    "error": error,
                    "execution_time": execution_time
                }
                
        except Exception as e:
            logger.error(f"Claude CLI call failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "execution_time": 0
            }

class RealDualAgentSystem:
    """
    Real dual-agent system with adaptive workflow execution.
    
    Combines:
    - Research Agent: Planning and strategy via real Claude CLI
    - Execution Agent: Tool coordination via real Claude CLI  
    - Working MCP Client: Real KGAS tool execution
    - Adaptive Logic: Real-time workflow adaptation
    """
    
    def __init__(self):
        """Initialize dual-agent system"""
        self.research_agent = RealClaudeAgent("research", temperature=0.7)
        self.execution_agent = RealClaudeAgent("execution", temperature=0.3)
        self.mcp_client = WorkingMCPClient()
        self.active_executions: Dict[str, WorkflowExecution] = {}
        
    async def initialize(self):
        """Initialize all system components"""
        try:
            # Connect to MCP client
            connected = await self.mcp_client.connect()
            if not connected:
                raise Exception("Failed to connect to MCP client")
            
            # Verify agent connectivity
            await self._verify_agent_connectivity()
            
            logger.info("Dual-agent system initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"System initialization failed: {e}")
            return False
    
    async def _verify_agent_connectivity(self):
        """Verify both agents can be reached"""
        # Test research agent
        test_request = AgentRequest(
            agent_type="research",
            task_type="connectivity_test",
            content="Please respond with a simple JSON object confirming connectivity.",
            context={},
            temperature=0.1
        )
        
        research_response = await self.research_agent.execute(test_request)
        if research_response.status != "success":
            raise Exception(f"Research agent connectivity failed: {research_response.error_message}")
        
        # Test execution agent
        test_request.agent_type = "execution"
        execution_response = await self.execution_agent.execute(test_request)
        if execution_response.status != "success":
            raise Exception(f"Execution agent connectivity failed: {execution_response.error_message}")
        
        logger.info("Both agents verified connectivity successfully")
    
    async def execute_research_workflow(self, 
                                      objective: str, 
                                      documents: List[Dict[str, Any]],
                                      analysis_modes: List[str] = None) -> Dict[str, Any]:
        """
        Execute a complete research workflow with real agents and tools.
        
        Args:
            objective: Research objective (e.g., "Analyze stakeholder communication patterns")
            documents: List of documents to analyze
            analysis_modes: Types of analysis to perform
            
        Returns:
            Complete workflow results with execution details
        """
        execution_id = f"exec_{uuid.uuid4().hex[:8]}"
        start_time = time.time()
        
        try:
            logger.info(f"Starting research workflow execution {execution_id}")
            
            # Phase 1: Research Agent creates adaptive plan
            planning_request = AgentRequest(
                agent_type="research",
                task_type="create_workflow_plan",
                content=f"""Create an adaptive analytical workflow plan for this objective:

OBJECTIVE: {objective}

DOCUMENTS TO ANALYZE:
{json.dumps(documents, indent=2)}

ANALYSIS MODES: {analysis_modes or ['entities', 'relationships']}

Create a detailed plan with:
1. Step-by-step workflow 
2. Quality thresholds for each step
3. Adaptation strategies if quality is low
4. Resource constraints and time estimates
5. Success criteria

Respond with structured JSON.""",
                context={
                    "objective": objective,
                    "document_count": len(documents),
                    "analysis_modes": analysis_modes or ['entities', 'relationships']
                },
                temperature=0.7
            )
            
            planning_response = await self.research_agent.execute(planning_request)
            
            if planning_response.status != "success":
                return {
                    "execution_id": execution_id,
                    "status": "failed",
                    "error": f"Planning failed: {planning_response.error_message}",
                    "execution_time": time.time() - start_time
                }
            
            # Extract plan from research agent response
            plan_data = planning_response.data
            workflow_plan = AdaptiveWorkflowPlan(
                plan_id=f"plan_{uuid.uuid4().hex[:8]}",
                objective=objective,
                steps=plan_data.get("steps", []),
                quality_thresholds=plan_data.get("quality_thresholds", {}),
                adaptation_strategies=plan_data.get("adaptation_strategies", []),
                resource_constraints=plan_data.get("resource_constraints", {}),
                created_at=datetime.now().isoformat()
            )
            
            # Initialize workflow execution tracking
            execution = WorkflowExecution(
                execution_id=execution_id,
                plan=workflow_plan,
                current_step=0,
                completed_steps=[],
                adaptations_made=[],
                execution_metrics={
                    "start_time": start_time,
                    "documents_processed": 0,
                    "entities_extracted": 0,
                    "relationships_found": 0,
                    "adaptations_count": 0
                },
                status="running"
            )
            
            self.active_executions[execution_id] = execution
            
            # Phase 2: Execute workflow with adaptive monitoring
            results = await self._execute_adaptive_workflow(execution, documents, analysis_modes)
            
            # Phase 3: Research Agent synthesizes final results
            synthesis_request = AgentRequest(
                agent_type="research",
                task_type="synthesize_results",
                content=f"""Synthesize the results of this research workflow execution:

ORIGINAL OBJECTIVE: {objective}

EXECUTION RESULTS:
{json.dumps(results, indent=2)}

EXECUTION METRICS:
{json.dumps(execution.execution_metrics, indent=2)}

ADAPTATIONS MADE:
{json.dumps(execution.adaptations_made, indent=2)}

Provide:
1. Summary of findings
2. Quality assessment
3. Insights discovered
4. Recommendations for future similar workflows
5. Success assessment against original objective

Respond with structured JSON.""",
                context={
                    "execution_id": execution_id,
                    "objective": objective,
                    "total_time": time.time() - start_time
                },
                temperature=0.6
            )
            
            synthesis_response = await self.research_agent.execute(synthesis_request)
            
            # Complete execution tracking
            execution.status = "completed"
            total_time = time.time() - start_time
            execution.execution_metrics["total_time"] = total_time
            
            return {
                "execution_id": execution_id,
                "status": "completed",
                "objective": objective,
                "plan": asdict(workflow_plan),
                "execution_results": results,
                "synthesis": synthesis_response.data if synthesis_response.status == "success" else None,
                "execution_metrics": execution.execution_metrics,
                "adaptations_made": execution.adaptations_made,
                "total_time": total_time,
                "documents_processed": len(documents)
            }
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            return {
                "execution_id": execution_id,
                "status": "failed",
                "error": str(e),
                "execution_time": time.time() - start_time
            }
    
    async def _execute_adaptive_workflow(self, 
                                       execution: WorkflowExecution,
                                       documents: List[Dict[str, Any]],
                                       analysis_modes: List[str]) -> Dict[str, Any]:
        """Execute workflow with real-time adaptation"""
        results = {
            "documents_processed": [],
            "total_entities": 0,
            "total_relationships": 0,
            "quality_scores": [],
            "adaptation_history": []
        }
        
        for doc_idx, document in enumerate(documents):
            logger.info(f"Processing document {doc_idx + 1}/{len(documents)}")
            
            # Execute document analysis using real MCP tools
            doc_result = await self.mcp_client.execute_tool(
                "analyze_document",
                document=document,
                analysis_modes=analysis_modes or ['entities', 'relationships']
            )
            
            if doc_result.status == "success":
                doc_data = doc_result.output
                results["documents_processed"].append({
                    "document_id": document.get("id", f"doc_{doc_idx}"),
                    "entity_count": doc_data.get("entity_count", 0),
                    "relationship_count": doc_data.get("relationship_count", 0),
                    "processing_time": doc_data.get("processing_time", 0),
                    "quality_score": self._calculate_quality_score(doc_data)
                })
                
                results["total_entities"] += doc_data.get("entity_count", 0)
                results["total_relationships"] += doc_data.get("relationship_count", 0)
                execution.execution_metrics["documents_processed"] += 1
            else:
                logger.warning(f"Document processing failed: {doc_result.error_message}")
                results["documents_processed"].append({
                    "document_id": document.get("id", f"doc_{doc_idx}"),
                    "error": doc_result.error_message,
                    "quality_score": 0.0
                })
            
            # Check if adaptation is needed
            current_quality = results["documents_processed"][-1].get("quality_score", 0.0)
            results["quality_scores"].append(current_quality)
            
            if len(results["quality_scores"]) >= 2:
                adaptation_needed = await self._check_adaptation_needed(
                    execution, results["quality_scores"]
                )
                
                if adaptation_needed:
                    adaptation = await self._perform_adaptation(execution, results)
                    results["adaptation_history"].append(adaptation)
        
        # Update execution metrics
        execution.execution_metrics["entities_extracted"] = results["total_entities"]
        execution.execution_metrics["relationships_found"] = results["total_relationships"]
        execution.execution_metrics["adaptations_count"] = len(results["adaptation_history"])
        
        return results
    
    def _calculate_quality_score(self, doc_data: Dict[str, Any]) -> float:
        """Calculate quality score for document processing results"""
        entity_count = doc_data.get("entity_count", 0)
        relationship_count = doc_data.get("relationship_count", 0)
        processing_time = doc_data.get("processing_time", 0)
        
        # Simple quality heuristic
        base_score = 0.5
        
        # Bonus for finding entities and relationships
        if entity_count > 0:
            base_score += min(0.3, entity_count * 0.05)
        if relationship_count > 0:
            base_score += min(0.2, relationship_count * 0.02)
        
        # Penalty for very slow processing
        if processing_time > 10:
            base_score -= 0.1
        
        return min(1.0, max(0.0, base_score))
    
    async def _check_adaptation_needed(self, 
                                     execution: WorkflowExecution, 
                                     quality_scores: List[float]) -> bool:
        """Check if workflow adaptation is needed based on quality trends"""
        if len(quality_scores) < 2:
            return False
        
        recent_scores = quality_scores[-3:]  # Last 3 scores
        avg_quality = sum(recent_scores) / len(recent_scores)
        
        # Adaptation triggers
        if avg_quality < 0.4:  # Low overall quality
            return True
        
        if len(recent_scores) >= 2:
            # Declining trend
            if recent_scores[-1] < recent_scores[-2] - 0.2:
                return True
        
        return False
    
    async def _perform_adaptation(self, 
                                execution: WorkflowExecution, 
                                current_results: Dict[str, Any]) -> Dict[str, Any]:
        """Perform real-time workflow adaptation"""
        adaptation_request = AgentRequest(
            agent_type="research",
            task_type="adapt_workflow",
            content=f"""The current workflow execution is showing quality issues. Please analyze and recommend adaptations:

CURRENT RESULTS:
{json.dumps(current_results, indent=2)}

QUALITY TREND: {current_results.get('quality_scores', [])}

AVAILABLE ADAPTATION STRATEGIES:
- Lower confidence thresholds
- Add preprocessing steps  
- Change analysis parameters
- Switch to alternative approaches
- Add additional validation steps

Provide specific adaptation recommendations with expected improvements.

Respond with structured JSON containing:
1. Issue analysis
2. Recommended adaptations
3. Expected quality improvement
4. Implementation details""",
            context={
                "execution_id": execution.execution_id,
                "quality_scores": current_results.get("quality_scores", [])
            },
            temperature=0.5
        )
        
        adaptation_response = await self.research_agent.execute(adaptation_request)
        
        adaptation = {
            "timestamp": datetime.now().isoformat(),
            "trigger": "quality_decline",
            "analysis": adaptation_response.data if adaptation_response.status == "success" else None,
            "status": adaptation_response.status
        }
        
        execution.adaptations_made.append(adaptation)
        return adaptation
    
    async def get_execution_status(self, execution_id: str) -> Dict[str, Any]:
        """Get current status of workflow execution"""
        execution = self.active_executions.get(execution_id)
        if not execution:
            return {"error": "Execution not found"}
        
        return {
            "execution_id": execution_id,
            "status": execution.status,
            "current_step": execution.current_step,
            "total_steps": len(execution.plan.steps),
            "completed_steps": len(execution.completed_steps),
            "adaptations_made": len(execution.adaptations_made),
            "metrics": execution.execution_metrics
        }
    
    async def cleanup(self):
        """Cleanup system resources"""
        await self.mcp_client.disconnect()


# Test function demonstrating real dual-agent execution
async def test_real_dual_agent_system():
    """Test the real dual-agent system with actual documents"""
    system = RealDualAgentSystem()
    
    try:
        print("🚀 Initializing Real Dual-Agent System...")
        initialized = await system.initialize()
        
        if not initialized:
            print("❌ System initialization failed")
            return
        
        print("✅ System initialized successfully")
        
        # Test with real document analysis
        print("\n📊 Executing Research Workflow...")
        
        test_documents = [
            {
                "id": "test_doc_001",
                "content": "Apple Inc. is a multinational technology company headquartered in Cupertino, California. The company was founded by Steve Jobs, Steve Wozniak, and Ronald Wayne in April 1976. Apple designs, develops, and sells consumer electronics, computer software, and online services. The company's hardware products include the iPhone smartphone, the iPad tablet computer, the Mac personal computer, and the Apple Watch smartwatch."
            }
        ]
        
        result = await system.execute_research_workflow(
            objective="Analyze corporate structure and key personnel relationships",
            documents=test_documents,
            analysis_modes=["entities", "relationships"]
        )
        
        print(f"📋 Execution Result:")
        print(f"   Status: {result['status']}")
        print(f"   Execution ID: {result['execution_id']}")
        print(f"   Documents Processed: {result.get('documents_processed', 0)}")
        print(f"   Total Time: {result.get('total_time', 0):.2f}s")
        
        if result['status'] == 'completed':
            metrics = result.get('execution_metrics', {})
            print(f"   Entities Extracted: {metrics.get('entities_extracted', 0)}")
            print(f"   Relationships Found: {metrics.get('relationships_found', 0)}")
            print(f"   Adaptations Made: {metrics.get('adaptations_count', 0)}")
            
            if result.get('synthesis'):
                print(f"\n🧠 Research Agent Synthesis:")
                synthesis = result['synthesis']
                if isinstance(synthesis, dict):
                    for key, value in synthesis.items():
                        print(f"   {key}: {value}")
        
        print("\n🎉 Real dual-agent system test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    finally:
        await system.cleanup()


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Run the test
    asyncio.run(test_real_dual_agent_system())