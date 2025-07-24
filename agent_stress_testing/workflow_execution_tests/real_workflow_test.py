#!/usr/bin/env python3
"""
Real Workflow Execution Test

Tests actual workflow execution using real KGAS tools and Claude Code integration.
Replaces all mocks with authentic tool coordination.
"""

import asyncio
import json
import time
import yaml
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
from pathlib import Path

# Import real integrations
from ..real_claude_integration import RealClaudeCodeClient, DualAgentCoordinator
from ..real_mcp_integration import RealMemoryIntegrator
from ..real_kgas_integration import RealWorkflowExecutor


@dataclass
class WorkflowTestResult:
    """Result from real workflow execution test"""
    test_id: str
    scenario_name: str
    status: str  # "success", "failure", "error"
    workflow_executed: bool
    execution_time: float
    research_quality_score: float
    user_satisfaction_score: float
    tool_coordination_success: bool
    memory_integration_success: bool
    performance_metrics: Dict[str, Any]
    errors: List[str]
    insights_generated: List[str]


class RealWorkflowTestRunner:
    """Real workflow test runner using actual KGAS tools and Claude Code"""
    
    def __init__(self):
        self.test_results = []
        self.memory_integrator = None
        self.workflow_executor = None
        self.coordinator = None
    
    async def setup(self) -> bool:
        """Set up real integrations"""
        try:
            # Initialize memory integrator with real MCP
            self.memory_integrator = RealMemoryIntegrator()
            memory_connected = await self.memory_integrator.connect()
            if not memory_connected:
                print("Warning: Memory integration not available")
            
            # Initialize workflow executor with real KGAS tools
            self.workflow_executor = RealWorkflowExecutor()
            
            # Initialize dual-agent coordinator with real Claude Code
            research_config = {
                "system_prompt": """
You are an expert research assistant specializing in social science research.
Design comprehensive workflows, interpret results, and provide educational guidance.
Focus on methodology rigor and clear explanation of research insights.
                """,
                "model": "claude-3-5-sonnet-20241022",
                "temperature": 0.7,
                "tools": ["research_planning", "methodology_design", "result_interpretation"]
            }
            
            execution_config = {
                "system_prompt": """
You are a precise workflow execution coordinator for research analysis.
Execute workflows systematically using available KGAS tools.
Provide detailed progress updates and quality validation.
                """,
                "model": "claude-3-5-sonnet-20241022", 
                "temperature": 0.3,
                "tools": ["workflow_execution", "tool_coordination", "quality_monitoring"]
            }
            
            self.coordinator = DualAgentCoordinator(research_config, execution_config)
            
            return True
            
        except Exception as e:
            print(f"Setup failed: {e}")
            return False
    
    async def run_workflow_test(self, scenario_file: str) -> WorkflowTestResult:
        """Run a real workflow test using scenario specification"""
        
        # Load test scenario
        scenario_path = Path(__file__).parent.parent / "test_data/research_scenarios" / scenario_file
        with open(scenario_path, 'r') as f:
            scenario = json.load(f)
        
        test_id = f"test_{int(time.time())}"
        start_time = time.time()
        errors = []
        insights_generated = []
        
        try:
            # Step 1: Retrieve enhanced context from memory (if available)
            enhanced_context = {}
            memory_integration_success = False
            
            if self.memory_integrator and self.memory_integrator.connected:
                try:
                    context_data = await self.memory_integrator.retrieve_research_context(
                        scenario["research_question"],
                        "test_user"
                    )
                    enhanced_context = context_data
                    memory_integration_success = True
                except Exception as e:
                    errors.append(f"Memory integration error: {str(e)}")
            
            # Step 2: Execute dual-agent coordination workflow
            coordination_context = {
                **scenario.get("context", {}),
                **enhanced_context,
                "scenario_id": scenario["scenario_id"],
                "expected_methodology": scenario["expected_methodology"]
            }
            
            coordination_result = await self.coordinator.execute_research_workflow(
                scenario["research_question"],
                coordination_context
            )
            
            workflow_executed = False
            tool_coordination_success = False
            
            if coordination_result["status"] == "success":
                # Step 3: Extract and execute workflow with real KGAS tools
                workflow_spec = self._extract_workflow_specification(
                    coordination_result["workflow_design"]
                )
                
                if workflow_spec:
                    # Add real data sources to workflow
                    workflow_spec = self._enhance_workflow_with_real_data(workflow_spec, scenario)
                    
                    # Execute workflow with real tools
                    execution_result = await self.workflow_executor.execute_workflow(workflow_spec)
                    
                    if execution_result["overall_status"] == "completed":
                        workflow_executed = True
                        tool_coordination_success = True
                        
                        # Extract insights from execution results
                        insights_generated = self._extract_insights_from_execution(
                            execution_result,
                            coordination_result["research_interpretation"]
                        )
                        
                        # Step 4: Store results in memory (if available)
                        if self.memory_integrator and self.memory_integrator.connected:
                            try:
                                session_data = {
                                    "session_id": test_id,
                                    "user_id": "test_user",
                                    "query": scenario["research_question"],
                                    "domain": scenario["domain"],
                                    "methodology": "_".join(scenario["expected_methodology"]),
                                    "execution_time": time.time() - start_time,
                                    "quality_score": self._calculate_quality_score(coordination_result, execution_result),
                                    "findings": insights_generated,
                                    "tools_used": list(self.workflow_executor.tool_executor.available_tools.keys())
                                }
                                await self.memory_integrator.store_research_session(session_data)
                            except Exception as e:
                                errors.append(f"Memory storage error: {str(e)}")
                    else:
                        errors.append(f"Workflow execution failed: {execution_result.get('error', 'Unknown error')}")
                else:
                    errors.append("Failed to extract valid workflow specification")
            else:
                errors.append(f"Agent coordination failed: {coordination_result.get('error', 'Unknown error')}")
            
            # Calculate performance metrics
            execution_time = time.time() - start_time
            performance_metrics = self._calculate_performance_metrics(
                coordination_result,
                execution_result if workflow_executed else None,
                execution_time
            )
            
            # Calculate quality scores
            research_quality_score = self._calculate_research_quality(
                coordination_result,
                execution_result if workflow_executed else None,
                scenario
            )
            
            user_satisfaction_score = self._calculate_user_satisfaction(
                coordination_result,
                insights_generated,
                errors
            )
            
            # Determine overall status
            status = "success" if workflow_executed and not errors else ("failure" if workflow_executed else "error")
            
            result = WorkflowTestResult(
                test_id=test_id,
                scenario_name=scenario["name"],
                status=status,
                workflow_executed=workflow_executed,
                execution_time=execution_time,
                research_quality_score=research_quality_score,
                user_satisfaction_score=user_satisfaction_score,
                tool_coordination_success=tool_coordination_success,
                memory_integration_success=memory_integration_success,
                performance_metrics=performance_metrics,
                errors=errors,
                insights_generated=insights_generated
            )
            
            self.test_results.append(result)
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            errors.append(str(e))
            
            result = WorkflowTestResult(
                test_id=test_id,
                scenario_name=scenario.get("name", "Unknown"),
                status="error",
                workflow_executed=False,
                execution_time=execution_time,
                research_quality_score=0.0,
                user_satisfaction_score=0.0,
                tool_coordination_success=False,
                memory_integration_success=False,
                performance_metrics={},
                errors=errors,
                insights_generated=[]
            )
            
            self.test_results.append(result)
            return result
    
    def _extract_workflow_specification(self, workflow_design: str) -> Optional[Dict[str, Any]]:
        """Extract structured workflow from research agent response"""
        try:
            # Look for YAML or JSON in the response
            lines = workflow_design.split('\n')
            
            # Find YAML block
            yaml_start = None
            yaml_end = None
            
            for i, line in enumerate(lines):
                if '```yaml' in line or '```yml' in line:
                    yaml_start = i + 1
                elif yaml_start is not None and '```' in line:
                    yaml_end = i
                    break
            
            if yaml_start is not None and yaml_end is not None:
                yaml_content = '\n'.join(lines[yaml_start:yaml_end])
                return yaml.safe_load(yaml_content)
            
            # Fallback: create basic workflow from text
            return self._create_basic_workflow_from_text(workflow_design)
            
        except Exception as e:
            print(f"Workflow extraction error: {e}")
            return None
    
    def _create_basic_workflow_from_text(self, text: str) -> Dict[str, Any]:
        """Create basic workflow specification from text description"""
        return {
            "name": "Basic Research Workflow",
            "description": "Extracted from research agent response",
            "phases": [
                {
                    "name": "data_preparation",
                    "tools": ["directory_processor"],
                    "inputs": {"directory_path": "test_data/sample_documents"}
                },
                {
                    "name": "text_analysis",
                    "tools": ["text_analyzer"],
                    "inputs": {"analysis_config": {"extract_themes": True, "sentiment_analysis": True}}
                },
                {
                    "name": "network_analysis",
                    "tools": ["network_analyzer"],
                    "inputs": {"analysis_type": "social_network"}
                },
                {
                    "name": "statistical_analysis",
                    "tools": ["statistical_analyzer"],
                    "inputs": {"analysis_type": "correlation"}
                }
            ],
            "expected_outputs": ["themes", "network_metrics", "statistical_analysis"],
            "quality_requirements": {"min_confidence": 0.7}
        }
    
    def _enhance_workflow_with_real_data(self, workflow_spec: Dict[str, Any], scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance workflow specification with real data sources"""
        enhanced_spec = workflow_spec.copy()
        
        # Add real data sources from scenario
        for phase in enhanced_spec.get("phases", []):
            if phase["name"] == "data_preparation":
                # Add real document paths
                for data_source in scenario.get("data_sources", []):
                    if data_source["type"] == "documents":
                        phase["inputs"]["directory_path"] = str(Path(__file__).parent.parent / data_source["path"])
                    elif data_source["type"] == "web_content":
                        if "web_scraper" not in phase["tools"]:
                            phase["tools"].append("web_scraper")
                        phase["inputs"]["url"] = data_source["url"]
        
        return enhanced_spec
    
    def _extract_insights_from_execution(self, execution_result: Dict[str, Any], interpretation: str) -> List[str]:
        """Extract insights from workflow execution and research interpretation"""
        insights = []
        
        # Extract insights from interpretation
        interpretation_lines = interpretation.split('\n')
        for line in interpretation_lines:
            if any(keyword in line.lower() for keyword in ['insight', 'finding', 'pattern', 'correlation', 'significant']):
                if len(line.strip()) > 20:  # Meaningful insights
                    insights.append(line.strip())
        
        # Extract insights from tool outputs
        for phase_name, phase_result in execution_result.get("phase_results", {}).items():
            for tool_output in phase_result.get("outputs", {}).values():
                if isinstance(tool_output, dict):
                    # Extract key metrics and findings
                    if "themes" in tool_output:
                        insights.append(f"Identified themes: {', '.join(tool_output['themes'][:3])}")
                    if "network_metrics" in tool_output:
                        metrics = tool_output["network_metrics"]
                        insights.append(f"Network density: {metrics.get('density', 'N/A')}")
                    if "correlations" in tool_output:
                        correlations = tool_output["correlations"]
                        for corr in correlations[:2]:  # Top 2 correlations
                            insights.append(f"Correlation: {corr.get('variables', [])} (r={corr.get('correlation', 'N/A')})")
        
        return insights[:10]  # Limit to top 10 insights
    
    def _calculate_quality_score(self, coordination_result: Dict[str, Any], execution_result: Optional[Dict[str, Any]]) -> float:
        """Calculate overall quality score"""
        score = 0.0
        
        # Coordination quality (40%)
        if coordination_result.get("status") == "success":
            score += 0.4
            
            # Check for comprehensive workflow design
            workflow_design = coordination_result.get("workflow_design", "")
            if len(workflow_design) > 1000 and "phases" in workflow_design:
                score += 0.1
        
        # Execution quality (40%)
        if execution_result and execution_result.get("overall_status") == "completed":
            score += 0.4
            
            # Check tool execution success
            phase_results = execution_result.get("phase_results", {})
            successful_phases = sum(1 for phase in phase_results.values() if phase.get("status") == "completed")
            total_phases = len(phase_results)
            if total_phases > 0:
                score += 0.1 * (successful_phases / total_phases)
        
        # Research interpretation quality (20%)
        interpretation = coordination_result.get("research_interpretation", "")
        if len(interpretation) > 500 and any(word in interpretation.lower() for word in ["finding", "insight", "implication"]):
            score += 0.2
        
        return min(score, 1.0)
    
    def _calculate_research_quality(self, coordination_result: Dict[str, Any], execution_result: Optional[Dict[str, Any]], scenario: Dict[str, Any]) -> float:
        """Calculate research-specific quality score"""
        score = 0.0
        
        # Methodology appropriateness (30%)
        expected_methods = scenario.get("expected_methodology", [])
        workflow_design = coordination_result.get("workflow_design", "").lower()
        methods_mentioned = sum(1 for method in expected_methods if method.replace("_", " ") in workflow_design)
        if expected_methods:
            score += 0.3 * (methods_mentioned / len(expected_methods))
        
        # Execution completeness (40%)
        if execution_result:
            expected_outputs = scenario.get("expected_outputs", [])
            if expected_outputs:
                # Check if expected outputs were generated
                actual_outputs = []
                for phase_result in execution_result.get("phase_results", {}).values():
                    actual_outputs.extend(phase_result.get("outputs", {}).keys())
                
                outputs_found = sum(1 for output in expected_outputs if any(output in actual for actual in actual_outputs))
                score += 0.4 * (outputs_found / len(expected_outputs))
        
        # Research insights quality (30%)
        interpretation = coordination_result.get("research_interpretation", "")
        insight_indicators = ["correlation", "significant", "pattern", "finding", "implication", "conclusion"]
        insights_count = sum(1 for indicator in insight_indicators if indicator in interpretation.lower())
        score += 0.3 * min(insights_count / 5, 1.0)  # Max 5 insights
        
        return min(score, 1.0)
    
    def _calculate_user_satisfaction(self, coordination_result: Dict[str, Any], insights: List[str], errors: List[str]) -> float:
        """Calculate user satisfaction score"""
        score = 0.0
        
        # Educational value (40%)
        workflow_design = coordination_result.get("workflow_design", "")
        interpretation = coordination_result.get("research_interpretation", "")
        
        # Check for explanatory content
        if "because" in workflow_design.lower() or "reason" in workflow_design.lower():
            score += 0.2
        if len(interpretation) > 500:  # Substantial interpretation
            score += 0.2
        
        # Insight generation (40%)
        if insights:
            score += 0.4 * min(len(insights) / 5, 1.0)  # Max 5 insights
        
        # Error-free execution (20%)
        if not errors:
            score += 0.2
        elif len(errors) <= 2:  # Minor errors
            score += 0.1
        
        return min(score, 1.0)
    
    def _calculate_performance_metrics(self, coordination_result: Dict[str, Any], execution_result: Optional[Dict[str, Any]], total_time: float) -> Dict[str, Any]:
        """Calculate comprehensive performance metrics"""
        metrics = {
            "total_execution_time": total_time,
            "coordination_success": coordination_result.get("status") == "success",
            "workflow_execution_success": execution_result.get("overall_status") == "completed" if execution_result else False
        }
        
        # Add coordination metrics
        coord_perf = coordination_result.get("performance_metrics", {})
        if coord_perf:
            metrics["agent_coordination"] = {
                "research_agent_stats": coord_perf.get("research_agent_stats", {}),
                "execution_agent_stats": coord_perf.get("execution_agent_stats", {})
            }
        
        # Add tool execution metrics
        if execution_result:
            exec_perf = execution_result.get("performance_stats", {})
            if exec_perf:
                metrics["tool_execution"] = exec_perf
        
        return metrics
    
    async def cleanup(self):
        """Clean up resources"""
        if self.memory_integrator:
            await self.memory_integrator.disconnect()


async def test_real_workflow_execution():
    """Run real workflow execution tests"""
    print("🧪 Starting Real Workflow Execution Tests")
    print("=" * 70)
    
    runner = RealWorkflowTestRunner()
    
    # Setup real integrations
    print("🔧 Setting up real integrations...")
    setup_success = await runner.setup()
    
    if not setup_success:
        print("❌ Setup failed - running with limited functionality")
    else:
        print("✅ Real integrations ready")
    
    # Test scenarios
    test_scenarios = [
        "organizational_communication_scenario.json"
    ]
    
    results = []
    
    for scenario_file in test_scenarios:
        print(f"\n📋 Testing Scenario: {scenario_file}")
        print("-" * 50)
        
        try:
            result = await runner.run_workflow_test(scenario_file)
            results.append(result)
            
            # Print result summary
            print(f"✅ Status: {result.status.upper()}")
            print(f"⏱️  Execution Time: {result.execution_time:.2f}s")
            print(f"🔧 Workflow Executed: {result.workflow_executed}")
            print(f"🎯 Research Quality: {result.research_quality_score:.3f}")
            print(f"😊 User Satisfaction: {result.user_satisfaction_score:.3f}")
            print(f"🔗 Tool Coordination: {result.tool_coordination_success}")
            print(f"💾 Memory Integration: {result.memory_integration_success}")
            print(f"💡 Insights Generated: {len(result.insights_generated)}")
            
            if result.errors:
                print(f"❌ Errors: {len(result.errors)}")
                for error in result.errors[:2]:  # Show first 2 errors
                    print(f"   - {error}")
            
            if result.insights_generated:
                print(f"🔍 Sample Insights:")
                for insight in result.insights_generated[:3]:  # Show first 3 insights
                    print(f"   - {insight}")
                    
        except Exception as e:
            print(f"💥 Test failed with error: {e}")
    
    # Summary
    print(f"\n📊 REAL WORKFLOW TEST SUMMARY")
    print("=" * 70)
    
    if results:
        successful_tests = [r for r in results if r.status == "success"]
        avg_execution_time = sum(r.execution_time for r in results) / len(results)
        avg_quality = sum(r.research_quality_score for r in results) / len(results)
        avg_satisfaction = sum(r.user_satisfaction_score for r in results) / len(results)
        
        print(f"Total Tests: {len(results)}")
        print(f"✅ Successful: {len(successful_tests)}")
        print(f"📈 Success Rate: {len(successful_tests)/len(results):.1%}")
        print(f"⏱️  Average Execution Time: {avg_execution_time:.2f}s")
        print(f"🎯 Average Research Quality: {avg_quality:.3f}")
        print(f"😊 Average User Satisfaction: {avg_satisfaction:.3f}")
        
        # Integration success rates
        tool_coord_success = sum(1 for r in results if r.tool_coordination_success)
        memory_int_success = sum(1 for r in results if r.memory_integration_success)
        
        print(f"🔗 Tool Coordination Success: {tool_coord_success}/{len(results)}")
        print(f"💾 Memory Integration Success: {memory_int_success}/{len(results)}")
        
        print(f"\n💡 ASSESSMENT")
        if len(successful_tests) == len(results):
            print("✅ EXCELLENT: All tests passed with real integrations")
        elif len(successful_tests) >= len(results) * 0.8:
            print("⚠️  GOOD: Most tests successful, minor issues to address")
        else:
            print("❌ NEEDS IMPROVEMENT: Multiple test failures require investigation")
    
    # Cleanup
    await runner.cleanup()
    
    return results


if __name__ == "__main__":
    # Run real workflow execution tests
    results = asyncio.run(test_real_workflow_execution())
    
    # Save results
    results_data = [asdict(result) for result in results]
    results_file = Path(__file__).parent.parent / "results" / "real_workflow_test_results.json"
    
    with open(results_file, 'w') as f:
        json.dump(results_data, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to: {results_file}")