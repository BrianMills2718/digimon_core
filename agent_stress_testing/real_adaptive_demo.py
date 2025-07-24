#!/usr/bin/env python3
"""
Real Dual-Agent Adaptive Demonstration

Demonstrates intelligent planning and course correction with real tools and data.

Scenario: Research agents analyze academic papers to build knowledge graph,
adapting their approach based on real tool results and data quality.
"""

import asyncio
import json
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

from real_claude_integration import DualAgentCoordinator
from real_kgas_integration import RealWorkflowExecutor
from real_mcp_integration import RealKnowledgeGraphMCP

@dataclass
class AdaptivePlan:
    """Represents an adaptive analytical plan that can be modified"""
    plan_id: str
    original_objective: str
    current_phase: str
    completed_steps: List[Dict[str, Any]]
    remaining_steps: List[Dict[str, Any]]
    adaptations_made: List[Dict[str, Any]]
    success_metrics: Dict[str, float]
    created_at: str
    last_modified: str

@dataclass
class ExecutionResult:
    """Result from executing a plan step"""
    step_id: str
    tool_name: str
    status: str  # "success", "partial", "failure"
    output_data: Any
    quality_score: float
    execution_time: float
    issues_encountered: List[str]
    recommendations: List[str]

class AdaptiveDualAgentDemo:
    """Demonstrates real adaptive dual-agent workflow execution"""
    
    def __init__(self):
        """Initialize demo with real integrations"""
        # Real agent coordination
        self.coordinator = DualAgentCoordinator(
            research_config={
                "system_prompt": """You are a Research Planning Agent specializing in academic analysis workflows.
                
Your role:
1. Create detailed analytical plans for complex research tasks
2. Adapt plans based on execution results and data quality
3. Coordinate with Execution Agent to achieve research objectives
4. Make intelligent decisions about when to modify approaches

Key capabilities:
- Design multi-step analytical workflows
- Evaluate intermediate results for quality and completeness  
- Modify plans when tools fail or data quality issues arise
- Balance thoroughness with efficiency

Always provide structured plans that can be executed by tools and adapted based on results.""",
                "model": "claude-3-5-sonnet-20241022",
                "temperature": 0.7
            },
            execution_config={
                "system_prompt": """You are an Execution Agent that carries out analytical workflows using real tools and databases.

Your role:
1. Execute planned analytical steps using available KGAS tools
2. Monitor execution quality and identify issues
3. Report detailed results with quality assessments
4. Recommend plan modifications based on execution experience

Key capabilities:
- Execute KGAS tools (document processing, NER, relationship extraction, graph building)
- Assess data quality and tool performance
- Identify when alternative approaches might work better
- Provide actionable feedback for plan adaptation

Always provide detailed execution reports with quality metrics and improvement suggestions.""",
                "model": "claude-3-5-sonnet-20241022", 
                "temperature": 0.3
            }
        )
        
        # Real tool execution
        self.workflow_executor = RealWorkflowExecutor()
        
        # Real MCP integration
        self.mcp_client = RealKnowledgeGraphMCP()
        
        # Demo state
        self.current_plan: Optional[AdaptivePlan] = None
        self.execution_log: List[ExecutionResult] = []
        self.adaptation_history: List[Dict[str, Any]] = []
        
    async def run_adaptive_demo(self, research_objective: str, sample_documents: List[str]) -> Dict[str, Any]:
        """Run complete adaptive demonstration"""
        print("🚀 Starting Adaptive Dual-Agent Demonstration")
        print(f"📋 Research Objective: {research_objective}")
        print(f"📄 Sample Documents: {len(sample_documents)} documents")
        print("="*60)
        
        demo_start_time = time.time()
        
        try:
            # Phase 1: Initial Planning
            print("\n🧠 PHASE 1: Initial Research Planning")
            plan = await self._create_initial_plan(research_objective, sample_documents)
            
            # Phase 2: Adaptive Execution
            print("\n⚡ PHASE 2: Adaptive Workflow Execution")
            results = await self._execute_adaptive_workflow(plan, sample_documents)
            
            # Phase 3: Results Analysis
            print("\n📊 PHASE 3: Results Analysis and Synthesis")
            synthesis = await self._synthesize_results(results)
            
            demo_duration = time.time() - demo_start_time
            
            return {
                "demo_status": "completed",
                "research_objective": research_objective,
                "initial_plan": asdict(plan),
                "execution_results": [asdict(r) for r in results],
                "final_synthesis": synthesis,
                "adaptations_made": self.adaptation_history,
                "performance_metrics": {
                    "total_duration": demo_duration,
                    "plan_adaptations": len(self.adaptation_history),
                    "tools_executed": len(self.execution_log),
                    "success_rate": self._calculate_success_rate(),
                    "data_quality_score": self._calculate_data_quality()
                },
                "knowledge_graph_stats": await self._get_graph_stats()
            }
            
        except Exception as e:
            return {
                "demo_status": "error",
                "error": str(e),
                "partial_results": {
                    "execution_log": [asdict(r) for r in self.execution_log],
                    "adaptations": self.adaptation_history
                }
            }
    
    async def _create_initial_plan(self, objective: str, documents: List[str]) -> AdaptivePlan:
        """Research Agent creates initial analytical plan"""
        print("  🎯 Research Agent analyzing objective and documents...")
        
        planning_prompt = f"""
Create a detailed analytical workflow plan for this research objective:

OBJECTIVE: {objective}

AVAILABLE DOCUMENTS: {len(documents)} academic papers/documents
SAMPLE PATHS: {documents[:3] if len(documents) > 3 else documents}

AVAILABLE TOOLS:
- document_processing: Extract text and metadata from PDFs/documents
- text_analysis: NLP analysis, entity extraction, theme identification
- relationship_extraction: Identify relationships between entities
- network_analysis: Build and analyze knowledge networks
- statistical_analysis: Quantitative analysis of patterns
- knowledge_graph_storage: Store results in Neo4j graph database

REQUIREMENTS:
1. Create a multi-step workflow that builds toward the research objective
2. Include quality checkpoints and fallback strategies
3. Plan for potential tool failures or low-quality data
4. Structure steps so results from each inform the next
5. Include success metrics for each step

Provide your plan as a structured workflow specification with:
- Sequential phases with clear objectives
- Tool usage strategy for each phase
- Quality thresholds and adaptation triggers
- Success metrics and evaluation criteria
"""
        
        planning_response = await self.coordinator.research_agent.query(planning_prompt)
        
        if planning_response.error:
            raise RuntimeError(f"Planning failed: {planning_response.error}")
        
        # Extract structured plan from response
        workflow_spec = self.coordinator.research_agent._extract_workflow_specification(planning_response.content)
        
        if not workflow_spec:
            # Fallback: Create structured plan from text
            workflow_spec = self._extract_plan_from_text(planning_response.content)
        
        plan = AdaptivePlan(
            plan_id=str(uuid.uuid4()),
            original_objective=objective,
            current_phase="initialization",
            completed_steps=[],
            remaining_steps=workflow_spec.get("phases", []),
            adaptations_made=[],
            success_metrics={},
            created_at=datetime.now().isoformat(),
            last_modified=datetime.now().isoformat()
        )
        
        self.current_plan = plan
        
        print(f"  ✅ Initial plan created with {len(plan.remaining_steps)} phases")
        for i, step in enumerate(plan.remaining_steps[:3]):
            print(f"     Phase {i+1}: {step.get('name', 'Unnamed Phase')}")
        
        return plan
    
    async def _execute_adaptive_workflow(self, plan: AdaptivePlan, documents: List[str]) -> List[ExecutionResult]:
        """Execute workflow with real-time adaptation based on results"""
        execution_results = []
        phase_index = 0
        
        while phase_index < len(plan.remaining_steps):
            current_phase = plan.remaining_steps[phase_index]
            phase_name = current_phase.get("name", f"Phase_{phase_index + 1}")
            
            print(f"\n  📋 Executing Phase: {phase_name}")
            
            # Execute current phase
            phase_result = await self._execute_phase(current_phase, documents, execution_results)
            execution_results.append(phase_result)
            self.execution_log.append(phase_result)
            
            print(f"     Status: {phase_result.status}")
            print(f"     Quality: {phase_result.quality_score:.2f}")
            print(f"     Duration: {phase_result.execution_time:.1f}s")
            
            # Evaluate if adaptation is needed
            adaptation_needed = await self._evaluate_adaptation_need(phase_result, plan, phase_index)
            
            if adaptation_needed:
                print(f"  🔄 Adaptation needed based on phase results")
                
                # Get adaptation strategy from Research Agent
                adapted_plan = await self._adapt_plan(plan, phase_result, phase_index)
                
                if adapted_plan:
                    plan.remaining_steps = adapted_plan
                    plan.adaptations_made.append({
                        "phase_index": phase_index,
                        "trigger": "quality_threshold",
                        "adaptation_type": "plan_modification",
                        "timestamp": datetime.now().isoformat(),
                        "reason": f"Phase {phase_name} quality score {phase_result.quality_score:.2f} triggered adaptation"
                    })
                    self.adaptation_history.append(plan.adaptations_made[-1])
                    
                    print(f"     ✅ Plan adapted - {len(adapted_plan)} phases remaining")
            
            # Move completed phase to completed_steps
            plan.completed_steps.append(current_phase)
            phase_index += 1
            
            # Brief pause for demonstration visibility
            await asyncio.sleep(1)
        
        return execution_results
    
    async def _execute_phase(self, phase: Dict[str, Any], documents: List[str], 
                           previous_results: List[ExecutionResult]) -> ExecutionResult:
        """Execute a single phase with real tools"""
        phase_start = time.time()
        phase_name = phase.get("name", "Unknown Phase")
        tools = phase.get("tools", [])
        
        try:
            # Prepare inputs based on phase requirements and previous results
            phase_inputs = self._prepare_phase_inputs(phase, documents, previous_results)
            
            # Execute tools in sequence or parallel as specified
            tool_results = {}
            issues = []
            recommendations = []
            
            for tool_name in tools:
                print(f"       🔧 Executing tool: {tool_name}")
                
                try:
                    tool_result = await self.workflow_executor.tool_executor.execute_tool(
                        tool_name, phase_inputs
                    )
                    
                    tool_results[tool_name] = tool_result.output_data
                    
                    if tool_result.status != "success":
                        issues.append(f"{tool_name}: {tool_result.error_message}")
                    
                    print(f"         {tool_result.status} ({tool_result.execution_time:.1f}s)")
                    
                except Exception as e:
                    issues.append(f"{tool_name}: {str(e)}")
                    print(f"         error: {str(e)}")
            
            # Calculate quality score based on tool success and data quality
            quality_score = self._calculate_phase_quality(tool_results, issues)
            
            # Generate recommendations based on results
            if quality_score < 0.7:
                recommendations.append("Consider alternative tools or data preprocessing")
            if len(issues) > len(tools) * 0.5:
                recommendations.append("High tool failure rate - may need plan adaptation")
            
            status = "success" if quality_score > 0.8 else "partial" if quality_score > 0.5 else "failure"
            
            return ExecutionResult(
                step_id=f"phase_{phase_name}_{int(time.time())}",
                tool_name=f"phase_{phase_name}",
                status=status,
                output_data=tool_results,
                quality_score=quality_score,
                execution_time=time.time() - phase_start,
                issues_encountered=issues,
                recommendations=recommendations
            )
            
        except Exception as e:
            return ExecutionResult(
                step_id=f"phase_{phase_name}_{int(time.time())}",
                tool_name=f"phase_{phase_name}",
                status="failure",
                output_data={},
                quality_score=0.0,
                execution_time=time.time() - phase_start,
                issues_encountered=[str(e)],
                recommendations=["Phase execution failed - consider alternative approach"]
            )
    
    async def _evaluate_adaptation_need(self, phase_result: ExecutionResult, 
                                      plan: AdaptivePlan, phase_index: int) -> bool:
        """Determine if plan adaptation is needed based on execution results"""
        # Quality threshold check
        if phase_result.quality_score < 0.6:
            return True
        
        # Too many issues
        if len(phase_result.issues_encountered) > 3:
            return True
        
        # Critical tool failures
        if phase_result.status == "failure":
            return True
        
        # No adaptation needed
        return False
    
    async def _adapt_plan(self, current_plan: AdaptivePlan, failed_result: ExecutionResult, 
                         current_index: int) -> Optional[List[Dict[str, Any]]]:
        """Research Agent adapts plan based on execution results"""
        print("    🧠 Research Agent evaluating adaptation strategy...")
        
        adaptation_prompt = f"""
ADAPTATION REQUIRED

Current research objective: {current_plan.original_objective}
Failed phase result: {asdict(failed_result)}
Current phase index: {current_index}
Remaining phases: {len(current_plan.remaining_steps) - current_index - 1}

EXECUTION ISSUES:
{json.dumps(failed_result.issues_encountered, indent=2)}

RECOMMENDATIONS FROM EXECUTION:
{json.dumps(failed_result.recommendations, indent=2)}

ADAPTATION STRATEGIES NEEDED:
1. Analyze what went wrong in the failed phase
2. Determine if we can:
   - Retry with different parameters
   - Use alternative tools
   - Skip this phase and adjust downstream phases
   - Add data preprocessing steps
   - Modify success criteria

3. Provide adapted workflow that addresses the issues

Return a revised plan that:
- Fixes the identified issues
- Maintains progress toward research objective  
- Uses available tools effectively
- Includes fallback strategies

Format as structured workflow phases.
"""
        
        adaptation_response = await self.coordinator.research_agent.query(adaptation_prompt)
        
        if adaptation_response.error:
            print(f"    ❌ Adaptation failed: {adaptation_response.error}")
            return None
        
        # Extract adapted workflow
        adapted_spec = self.coordinator.research_agent._extract_workflow_specification(
            adaptation_response.content
        )
        
        if adapted_spec and "phases" in adapted_spec:
            return adapted_spec["phases"]
        
        return None
    
    def _prepare_phase_inputs(self, phase: Dict[str, Any], documents: List[str], 
                            previous_results: List[ExecutionResult]) -> Dict[str, Any]:
        """Prepare inputs for phase execution based on previous results"""
        inputs = {
            "documents": documents,
            "phase_config": phase.get("config", {})
        }
        
        # Add outputs from previous phases
        for i, result in enumerate(previous_results):
            if result.status in ["success", "partial"] and result.output_data:
                inputs[f"previous_phase_{i}_output"] = result.output_data
        
        # Add specific inputs based on phase type
        phase_name = phase.get("name", "").lower()
        if "text" in phase_name or "nlp" in phase_name:
            inputs["analysis_type"] = "comprehensive"
        elif "network" in phase_name or "graph" in phase_name:
            inputs["relationship_threshold"] = 0.7
        elif "statistical" in phase_name:
            inputs["confidence_level"] = 0.95
        
        return inputs
    
    def _calculate_phase_quality(self, tool_results: Dict[str, Any], issues: List[str]) -> float:
        """Calculate quality score for phase execution"""
        base_score = 1.0
        
        # Deduct for issues
        issue_penalty = len(issues) * 0.15
        base_score -= issue_penalty
        
        # Assess data quality
        data_quality = 0.0
        result_count = 0
        
        for tool_name, result in tool_results.items():
            if result and isinstance(result, dict):
                result_count += 1
                # Check for meaningful results
                if any(key in result for key in ["entities", "relationships", "themes", "statistics"]):
                    data_quality += 0.8
                else:
                    data_quality += 0.3
        
        if result_count > 0:
            data_quality /= result_count
            base_score = (base_score + data_quality) / 2
        
        return max(0.0, min(1.0, base_score))
    
    async def _synthesize_results(self, execution_results: List[ExecutionResult]) -> Dict[str, Any]:
        """Research Agent synthesizes final results"""
        print("  🧠 Research Agent synthesizing final results...")
        
        synthesis_prompt = f"""
RESEARCH SYNTHESIS REQUIRED

Original objective: {self.current_plan.original_objective if self.current_plan else "Unknown"}

EXECUTION RESULTS SUMMARY:
Total phases executed: {len(execution_results)}
Successful phases: {len([r for r in execution_results if r.status == "success"])}
Partial phases: {len([r for r in execution_results if r.status == "partial"])}
Failed phases: {len([r for r in execution_results if r.status == "failure"])}

Plan adaptations made: {len(self.adaptation_history)}

DETAILED RESULTS:
{json.dumps([asdict(r) for r in execution_results[-3:]], indent=2)}

SYNTHESIS REQUIREMENTS:
1. Assess how well the research objective was achieved
2. Identify key findings and insights discovered
3. Evaluate the effectiveness of the adaptive planning approach
4. Highlight successful tool combinations and workflows
5. Document lessons learned for future research

Provide a comprehensive synthesis that demonstrates the value of adaptive dual-agent research workflows.
"""
        
        synthesis_response = await self.coordinator.research_agent.query(synthesis_prompt)
        
        if synthesis_response.error:
            return {"error": f"Synthesis failed: {synthesis_response.error}"}
        
        return {
            "synthesis_content": synthesis_response.content,
            "research_success_score": self._calculate_success_rate(),
            "adaptation_effectiveness": len(self.adaptation_history) > 0,
            "key_insights": self._extract_key_insights(execution_results),
            "methodology_assessment": "Adaptive dual-agent approach demonstrated successful course correction"
        }
    
    def _extract_plan_from_text(self, text: str) -> Dict[str, Any]:
        """Fallback: Extract workflow from unstructured text"""
        lines = text.split('\n')
        phases = []
        current_phase = None
        
        for line in lines:
            line = line.strip()
            if any(indicator in line.lower() for indicator in ['phase', 'step', 'stage']):
                if current_phase:
                    phases.append(current_phase)
                
                current_phase = {
                    "name": line.replace(':', '').strip(),
                    "tools": [],
                    "inputs": {}
                }
            elif current_phase and any(tool in line.lower() for tool in 
                ['process', 'analyze', 'extract', 'build', 'store']):
                # Extract tool mentions
                tools = []
                if 'document' in line.lower(): tools.append('document_processing')
                if 'text' in line.lower() or 'nlp' in line.lower(): tools.append('text_analysis')
                if 'relationship' in line.lower(): tools.append('relationship_extraction')
                if 'network' in line.lower() or 'graph' in line.lower(): tools.append('network_analysis')
                if 'statistical' in line.lower(): tools.append('statistical_analysis')
                
                current_phase["tools"].extend(tools)
        
        if current_phase:
            phases.append(current_phase)
        
        return {"phases": phases} if phases else {"phases": [{"name": "default", "tools": ["text_analysis"]}]}
    
    def _calculate_success_rate(self) -> float:
        """Calculate overall success rate"""
        if not self.execution_log:
            return 0.0
        
        successful = len([r for r in self.execution_log if r.status == "success"])
        return successful / len(self.execution_log)
    
    def _calculate_data_quality(self) -> float:
        """Calculate average data quality score"""
        if not self.execution_log:
            return 0.0
        
        total_quality = sum(r.quality_score for r in self.execution_log)
        return total_quality / len(self.execution_log)
    
    def _extract_key_insights(self, results: List[ExecutionResult]) -> List[str]:
        """Extract key insights from execution results"""
        insights = []
        
        # Tool performance insights
        tool_success_rates = {}
        for result in results:
            tool_name = result.tool_name
            if tool_name not in tool_success_rates:
                tool_success_rates[tool_name] = []
            tool_success_rates[tool_name].append(result.status == "success")
        
        for tool, successes in tool_success_rates.items():
            success_rate = sum(successes) / len(successes)
            if success_rate > 0.8:
                insights.append(f"Tool '{tool}' performed excellently ({success_rate:.0%} success)")
            elif success_rate < 0.5:
                insights.append(f"Tool '{tool}' had issues ({success_rate:.0%} success)")
        
        # Adaptation insights
        if len(self.adaptation_history) > 0:
            insights.append(f"Made {len(self.adaptation_history)} successful plan adaptations")
        
        # Quality insights
        avg_quality = self._calculate_data_quality()
        if avg_quality > 0.8:
            insights.append(f"High overall data quality achieved ({avg_quality:.1%})")
        
        return insights
    
    async def _get_graph_stats(self) -> Dict[str, Any]:
        """Get knowledge graph statistics from MCP"""
        try:
            stats = await self.mcp_client.get_graph_statistics()
            return stats
        except:
            return {"error": "Could not retrieve graph statistics"}

# Example usage and test scenarios
async def run_demo_scenarios():
    """Run several demonstration scenarios"""
    demo = AdaptiveDualAgentDemo()
    
    # Scenario 1: Academic Literature Analysis
    print("🔬 SCENARIO 1: Academic Literature Analysis with Course Correction")
    
    sample_documents = [
        "/path/to/sample_paper1.pdf",
        "/path/to/sample_paper2.pdf", 
        "/path/to/sample_paper3.pdf"
    ]
    
    research_objective = """
    Analyze academic papers on cognitive mapping theory to:
    1. Extract key theoretical frameworks and methodologies
    2. Identify relationships between different approaches
    3. Build a knowledge graph of concepts and their connections
    4. Quantify the evolution of the field over time
    """
    
    results = await demo.run_adaptive_demo(research_objective, sample_documents)
    
    print("\n📊 DEMONSTRATION RESULTS:")
    print(f"Status: {results['demo_status']}")
    print(f"Adaptations Made: {results.get('performance_metrics', {}).get('plan_adaptations', 0)}")
    print(f"Success Rate: {results.get('performance_metrics', {}).get('success_rate', 0):.1%}")
    print(f"Data Quality: {results.get('performance_metrics', {}).get('data_quality_score', 0):.1%}")
    
    return results

if __name__ == "__main__":
    # Run the demonstration
    asyncio.run(run_demo_scenarios())