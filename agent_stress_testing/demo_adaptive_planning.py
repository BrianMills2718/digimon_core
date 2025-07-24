#!/usr/bin/env python3
"""
Simplified Adaptive Planning Demonstration

Shows the core adaptive planning behavior without complex integrations.
Simulates tool execution with realistic results to demonstrate course correction logic.
"""

import asyncio
import json
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

@dataclass
class PlanStep:
    """A single step in an analytical plan"""
    step_id: str
    step_name: str
    tool_name: str
    inputs: Dict[str, Any]
    expected_outputs: List[str]
    success_criteria: Dict[str, float]
    fallback_strategies: List[str]

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

class AdaptivePlanningDemo:
    """Demonstrates adaptive planning and course correction logic"""
    
    def __init__(self):
        self.execution_log: List[ExecutionResult] = []
        self.plan_adaptations: List[Dict[str, Any]] = []
        self.current_plan: List[PlanStep] = []
        
    async def demonstrate_adaptive_workflow(self, scenario: str) -> Dict[str, Any]:
        """Run adaptive workflow demonstration"""
        print(f"🧠 ADAPTIVE PLANNING DEMONSTRATION")
        print(f"Scenario: {scenario}")
        print("="*60)
        
        demo_start = time.time()
        
        # Phase 1: Create initial plan
        print("\n📋 PHASE 1: Research Agent creates initial analytical plan")
        initial_plan = await self._create_initial_plan(scenario)
        
        # Phase 2: Execute with adaptation
        print("\n⚡ PHASE 2: Execution Agent runs plan with real-time adaptation")
        results = await self._execute_adaptive_plan(initial_plan)
        
        # Phase 3: Synthesis
        print("\n📊 PHASE 3: Research Agent synthesizes results")
        synthesis = await self._synthesize_results(results)
        
        demo_duration = time.time() - demo_start
        
        return {
            "scenario": scenario,
            "initial_plan": [asdict(step) for step in initial_plan],
            "execution_results": [asdict(r) for r in results],
            "plan_adaptations": self.plan_adaptations,
            "final_synthesis": synthesis,
            "metrics": {
                "duration": demo_duration,
                "adaptations_made": len(self.plan_adaptations),
                "success_rate": self._calculate_success_rate(results),
                "plan_efficiency": len(results) / len(initial_plan)
            }
        }
    
    async def _create_initial_plan(self, scenario: str) -> List[PlanStep]:
        """Research Agent creates structured analytical plan"""
        print("  🎯 Analyzing scenario and available tools...")
        await asyncio.sleep(1)  # Simulate planning time
        
        # Create realistic multi-step plan based on scenario
        if "academic papers" in scenario.lower() or "research" in scenario.lower():
            plan = [
                PlanStep(
                    step_id="step_1",
                    step_name="Document Processing",
                    tool_name="document_processor", 
                    inputs={"documents": ["paper1.txt", "paper2.txt"]},
                    expected_outputs=["extracted_text", "metadata"],
                    success_criteria={"text_extraction_rate": 0.9, "metadata_completeness": 0.8},
                    fallback_strategies=["manual_text_extraction", "alternative_parser"]
                ),
                PlanStep(
                    step_id="step_2",
                    step_name="Named Entity Recognition",
                    tool_name="text_analyzer",
                    inputs={"text_data": "from_step_1", "analysis_type": "entities"},
                    expected_outputs=["entities", "entity_types", "confidence_scores"],
                    success_criteria={"entity_extraction_rate": 0.7, "confidence_threshold": 0.6},
                    fallback_strategies=["alternative_ner_model", "manual_annotation"]
                ),
                PlanStep(
                    step_id="step_3", 
                    step_name="Relationship Extraction",
                    tool_name="relationship_extractor",
                    inputs={"entities": "from_step_2", "text_data": "from_step_1"},
                    expected_outputs=["relationships", "relationship_types", "strength_scores"],
                    success_criteria={"relationship_count": 50, "avg_confidence": 0.7},
                    fallback_strategies=["co_occurrence_analysis", "manual_relationship_mapping"]
                ),
                PlanStep(
                    step_id="step_4",
                    step_name="Network Analysis", 
                    tool_name="network_analyzer",
                    inputs={"entities": "from_step_2", "relationships": "from_step_3"},
                    expected_outputs=["network_metrics", "communities", "centrality_measures"],
                    success_criteria={"network_density": 0.3, "community_modularity": 0.4},
                    fallback_strategies=["simplified_network_analysis", "statistical_correlation"]
                )
            ]
        else:
            # Generic analysis plan
            plan = [
                PlanStep(
                    step_id="step_1",
                    step_name="Data Processing",
                    tool_name="data_processor",
                    inputs={"raw_data": "input_data"},
                    expected_outputs=["processed_data", "quality_metrics"],
                    success_criteria={"data_quality": 0.8},
                    fallback_strategies=["alternative_processing"]
                ),
                PlanStep(
                    step_id="step_2",
                    step_name="Analysis",
                    tool_name="analyzer",
                    inputs={"data": "from_step_1"},
                    expected_outputs=["analysis_results"],
                    success_criteria={"completeness": 0.9},
                    fallback_strategies=["simplified_analysis"]
                )
            ]
        
        self.current_plan = plan
        print(f"  ✅ Created plan with {len(plan)} steps:")
        for i, step in enumerate(plan, 1):
            print(f"    {i}. {step.step_name} ({step.tool_name})")
        
        return plan
    
    async def _execute_adaptive_plan(self, plan: List[PlanStep]) -> List[ExecutionResult]:
        """Execute plan with realistic tool simulation and adaptation"""
        results = []
        current_plan = plan.copy()
        step_index = 0
        
        while step_index < len(current_plan):
            step = current_plan[step_index]
            print(f"\n  🔧 Executing Step {step_index + 1}: {step.step_name}")
            
            # Simulate tool execution with realistic variability
            result = await self._simulate_tool_execution(step, results)
            results.append(result)
            self.execution_log.append(result)
            
            print(f"    Status: {result.status}")
            print(f"    Quality: {result.quality_score:.2f}")
            print(f"    Duration: {result.execution_time:.1f}s")
            
            # Check if adaptation is needed
            if self._needs_adaptation(result, step):
                print(f"  🔄 Course correction needed - quality score {result.quality_score:.2f} below threshold")
                
                # Get adaptation strategy
                adaptation = await self._adapt_plan(step, result, current_plan, step_index)
                
                if adaptation:
                    # Apply adaptation
                    current_plan = adaptation["new_plan"]
                    self.plan_adaptations.append({
                        "step_index": step_index,
                        "trigger": f"Low quality score: {result.quality_score:.2f}",
                        "adaptation_type": adaptation["adaptation_type"],
                        "changes_made": adaptation["changes_made"],
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    print(f"    ✅ Plan adapted: {adaptation['adaptation_type']}")
                    print(f"    Changes: {adaptation['changes_made']}")
                    
                    # If we modified current step, re-execute it
                    if adaptation["adaptation_type"] == "retry_with_fallback":
                        print(f"    🔄 Retrying step with fallback strategy...")
                        step_index -= 1  # Will be incremented at end of loop
            
            step_index += 1
            await asyncio.sleep(0.5)  # Brief pause for demo visibility
        
        return results
    
    async def _simulate_tool_execution(self, step: PlanStep, previous_results: List[ExecutionResult]) -> ExecutionResult:
        """Simulate realistic tool execution with varying quality"""
        start_time = time.time()
        
        # Simulate different execution scenarios based on tool and context
        scenarios = self._get_execution_scenarios(step.tool_name)
        
        # Choose scenario based on step context and previous results
        scenario = self._select_scenario(scenarios, step, previous_results)
        
        # Simulate execution time
        await asyncio.sleep(scenario["duration"])
        
        execution_time = time.time() - start_time
        
        return ExecutionResult(
            step_id=step.step_id,
            tool_name=step.tool_name,
            status=scenario["status"],
            output_data=scenario["output_data"],
            quality_score=scenario["quality_score"],
            execution_time=execution_time,
            issues_encountered=scenario["issues"],
            recommendations=scenario["recommendations"]
        )
    
    def _get_execution_scenarios(self, tool_name: str) -> List[Dict[str, Any]]:
        """Get realistic execution scenarios for different tools"""
        scenarios = {
            "document_processor": [
                {
                    "name": "success",
                    "status": "success",
                    "quality_score": 0.92,
                    "duration": 2.0,
                    "output_data": {"text_extracted": True, "metadata": {"pages": 15, "authors": 3}},
                    "issues": [],
                    "recommendations": ["Text extraction successful", "Metadata complete"]
                },
                {
                    "name": "partial_ocr_issues",
                    "status": "partial", 
                    "quality_score": 0.65,
                    "duration": 3.5,
                    "output_data": {"text_extracted": True, "metadata": {"pages": 15, "authors": 2}},
                    "issues": ["OCR errors in mathematical formulas", "Some metadata fields missing"],
                    "recommendations": ["Consider manual verification of formulas", "Try alternative OCR engine"]
                },
                {
                    "name": "format_failure",
                    "status": "failure",
                    "quality_score": 0.2,
                    "duration": 1.0,
                    "output_data": {},
                    "issues": ["Unsupported document format", "Corrupted file structure"],
                    "recommendations": ["Convert to supported format", "Use alternative processing tool"]
                }
            ],
            "text_analyzer": [
                {
                    "name": "high_quality_ner",
                    "status": "success",
                    "quality_score": 0.88,
                    "duration": 4.0,
                    "output_data": {"entities": ["cognitive mapping", "decision making", "network analysis"], "confidence": [0.92, 0.87, 0.94]},
                    "issues": [],
                    "recommendations": ["High-quality entity extraction", "Good confidence scores"]
                },
                {
                    "name": "domain_mismatch",
                    "status": "partial",
                    "quality_score": 0.55,
                    "duration": 4.5,
                    "output_data": {"entities": ["research", "analysis", "data"], "confidence": [0.60, 0.58, 0.62]},
                    "issues": ["Generic entities extracted", "Low confidence scores", "Domain-specific terms missed"],
                    "recommendations": ["Use domain-specific NER model", "Add custom entity patterns"]
                }
            ],
            "network_analyzer": [
                {
                    "name": "rich_network",
                    "status": "success", 
                    "quality_score": 0.85,
                    "duration": 3.0,
                    "output_data": {"nodes": 45, "edges": 120, "density": 0.12, "communities": 4},
                    "issues": [],
                    "recommendations": ["Well-connected network identified", "Clear community structure"]
                },
                {
                    "name": "sparse_network",
                    "status": "partial",
                    "quality_score": 0.45,
                    "duration": 2.0,
                    "output_data": {"nodes": 15, "edges": 8, "density": 0.04, "communities": 1},
                    "issues": ["Very sparse network", "Limited connectivity", "Single large component"],
                    "recommendations": ["Lower relationship thresholds", "Include indirect relationships"]
                }
            ]
        }
        
        return scenarios.get(tool_name, [scenarios["text_analyzer"][0]])  # Default scenario
    
    def _select_scenario(self, scenarios: List[Dict[str, Any]], step: PlanStep, 
                        previous_results: List[ExecutionResult]) -> Dict[str, Any]:
        """Select appropriate scenario based on context"""
        # If previous steps had quality issues, increase chance of problems
        prev_quality = [r.quality_score for r in previous_results[-2:]]  # Last 2 steps
        avg_prev_quality = sum(prev_quality) / len(prev_quality) if prev_quality else 0.8
        
        # Higher chance of problems if previous quality was low
        if avg_prev_quality < 0.6:
            # 60% chance of problems
            import random
            if random.random() < 0.6:
                return scenarios[-1] if len(scenarios) > 1 else scenarios[0]  # Problem scenario
        
        # For demo purposes, introduce some realistic variability
        import random
        weights = [0.6, 0.3, 0.1]  # 60% success, 30% partial, 10% failure
        if len(scenarios) < 3:
            weights = weights[:len(scenarios)]
        
        return random.choices(scenarios, weights=weights)[0]
    
    def _needs_adaptation(self, result: ExecutionResult, step: PlanStep) -> bool:
        """Determine if plan adaptation is needed"""
        # Check against success criteria
        quality_threshold = step.success_criteria.get("quality_threshold", 0.7)
        
        if result.quality_score < quality_threshold:
            return True
        
        if result.status == "failure":
            return True
        
        if len(result.issues_encountered) > 2:
            return True
        
        return False
    
    async def _adapt_plan(self, failed_step: PlanStep, result: ExecutionResult, 
                         current_plan: List[PlanStep], step_index: int) -> Optional[Dict[str, Any]]:
        """Generate plan adaptation based on execution results"""
        print("    🧠 Research Agent analyzing failure and generating adaptation...")
        await asyncio.sleep(1)  # Simulate thinking time
        
        # Determine adaptation strategy
        if result.status == "failure" and failed_step.fallback_strategies:
            # Try fallback strategy
            adapted_step = PlanStep(
                step_id=failed_step.step_id + "_retry",
                step_name=f"{failed_step.step_name} (Fallback)",
                tool_name=failed_step.fallback_strategies[0],  # Use first fallback
                inputs=failed_step.inputs.copy(),
                expected_outputs=failed_step.expected_outputs,
                success_criteria={k: v * 0.8 for k, v in failed_step.success_criteria.items()},  # Lower thresholds
                fallback_strategies=failed_step.fallback_strategies[1:]  # Remove used fallback
            )
            
            new_plan = current_plan.copy()
            new_plan[step_index] = adapted_step
            
            return {
                "adaptation_type": "retry_with_fallback", 
                "new_plan": new_plan,
                "changes_made": f"Switched to fallback tool: {adapted_step.tool_name}"
            }
        
        elif result.quality_score < 0.6 and "Low confidence" in str(result.issues_encountered):
            # Add preprocessing step
            preprocessing_step = PlanStep(
                step_id=f"preprocess_{failed_step.step_id}",
                step_name="Data Preprocessing",
                tool_name="data_preprocessor",
                inputs=failed_step.inputs.copy(),
                expected_outputs=["cleaned_data"],
                success_criteria={"data_quality": 0.8},
                fallback_strategies=["manual_preprocessing"]
            )
            
            # Update original step inputs
            updated_step = PlanStep(
                step_id=failed_step.step_id,
                step_name=failed_step.step_name,
                tool_name=failed_step.tool_name,
                inputs={**failed_step.inputs, "preprocessed_data": True},
                expected_outputs=failed_step.expected_outputs,
                success_criteria=failed_step.success_criteria,
                fallback_strategies=failed_step.fallback_strategies
            )
            
            new_plan = current_plan.copy()
            new_plan.insert(step_index, preprocessing_step)
            new_plan[step_index + 1] = updated_step
            
            return {
                "adaptation_type": "add_preprocessing",
                "new_plan": new_plan, 
                "changes_made": "Added preprocessing step to improve data quality"
            }
        
        elif len(result.issues_encountered) > 0 and "threshold" in str(result.issues_encountered).lower():
            # Adjust parameters
            new_inputs = failed_step.inputs.copy()
            new_inputs["relaxed_thresholds"] = True
            
            adapted_step = PlanStep(
                step_id=failed_step.step_id + "_adjusted",
                step_name=f"{failed_step.step_name} (Adjusted)",
                tool_name=failed_step.tool_name,
                inputs=new_inputs,
                expected_outputs=failed_step.expected_outputs,
                success_criteria={k: v * 0.7 for k, v in failed_step.success_criteria.items()},
                fallback_strategies=failed_step.fallback_strategies
            )
            
            new_plan = current_plan.copy()
            new_plan[step_index] = adapted_step
            
            return {
                "adaptation_type": "parameter_adjustment",
                "new_plan": new_plan,
                "changes_made": "Relaxed thresholds and adjusted parameters"
            }
        
        # No suitable adaptation found
        return None
    
    async def _synthesize_results(self, results: List[ExecutionResult]) -> Dict[str, Any]:
        """Research Agent synthesizes final results"""
        print("  📊 Research Agent synthesizing results...")
        await asyncio.sleep(1.5)
        
        successful_steps = [r for r in results if r.status == "success"]
        partial_steps = [r for r in results if r.status == "partial"]
        failed_steps = [r for r in results if r.status == "failure"]
        
        avg_quality = sum(r.quality_score for r in results) / len(results) if results else 0
        
        synthesis = {
            "execution_summary": {
                "total_steps": len(results),
                "successful_steps": len(successful_steps),
                "partial_steps": len(partial_steps),
                "failed_steps": len(failed_steps),
                "average_quality": avg_quality
            },
            "adaptation_effectiveness": {
                "adaptations_made": len(self.plan_adaptations),
                "adaptation_success_rate": self._evaluate_adaptation_success(),
                "most_effective_strategy": self._identify_best_adaptation_strategy()
            },
            "key_insights": [
                f"Executed {len(results)} analytical steps with {avg_quality:.1%} average quality",
                f"Made {len(self.plan_adaptations)} plan adaptations to address execution issues",
                f"Achieved {len(successful_steps)}/{len(results)} successful step completions"
            ],
            "recommendations": self._generate_recommendations(results)
        }
        
        print(f"    ✅ Synthesis complete - {avg_quality:.1%} average quality achieved")
        
        return synthesis
    
    def _calculate_success_rate(self, results: List[ExecutionResult]) -> float:
        """Calculate overall success rate"""
        if not results:
            return 0.0
        successful = len([r for r in results if r.status == "success"])
        return successful / len(results)
    
    def _evaluate_adaptation_success(self) -> float:
        """Evaluate how successful the adaptations were"""
        if not self.plan_adaptations:
            return 1.0  # No adaptations needed
        
        # Check if quality improved after adaptations
        adaptation_success = 0
        for adaptation in self.plan_adaptations:
            step_idx = adaptation["step_index"]
            if step_idx < len(self.execution_log) - 1:
                # Compare quality before and after adaptation
                if len(self.execution_log) > step_idx + 1:
                    before_quality = self.execution_log[step_idx].quality_score
                    after_quality = self.execution_log[step_idx + 1].quality_score
                    if after_quality > before_quality:
                        adaptation_success += 1
        
        return adaptation_success / len(self.plan_adaptations) if self.plan_adaptations else 0.0
    
    def _identify_best_adaptation_strategy(self) -> str:
        """Identify most effective adaptation strategy"""
        if not self.plan_adaptations:
            return "No adaptations needed"
        
        strategy_counts = {}
        for adaptation in self.plan_adaptations:
            strategy = adaptation["adaptation_type"]
            strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
        
        return max(strategy_counts.items(), key=lambda x: x[1])[0] if strategy_counts else "Unknown"
    
    def _generate_recommendations(self, results: List[ExecutionResult]) -> List[str]:
        """Generate recommendations based on execution results"""
        recommendations = []
        
        avg_quality = sum(r.quality_score for r in results) / len(results) if results else 0
        
        if avg_quality < 0.7:
            recommendations.append("Consider improving data preprocessing to enhance tool performance")
        
        if len([r for r in results if r.status == "failure"]) > 0:
            recommendations.append("Implement additional fallback strategies for critical tools")
        
        if len(self.plan_adaptations) > len(results) * 0.5:
            recommendations.append("Plan may be too ambitious - consider simpler initial approach")
        
        if not recommendations:
            recommendations.append("Workflow executed successfully with minimal adaptations needed")
        
        return recommendations

async def main():
    """Run the adaptive planning demonstration"""
    demo = AdaptivePlanningDemo()
    
    scenario = """
    Analyze academic research papers on cognitive mapping and network analysis to:
    1. Extract key concepts and theoretical frameworks
    2. Identify relationships between different research approaches  
    3. Build a knowledge network of concepts and methodologies
    4. Analyze collaboration patterns and their impact on research outcomes
    
    The analysis should adapt if tools encounter issues with:
    - Document processing failures or poor OCR quality
    - Named entity recognition producing generic results
    - Relationship extraction finding insufficient connections
    - Network analysis revealing unexpected structural patterns
    """
    
    print("Starting demonstration with realistic tool execution and adaptation...")
    results = await demo.demonstrate_adaptive_workflow(scenario)
    
    # Display results
    print("\n" + "="*60)
    print("🏆 ADAPTIVE PLANNING DEMONSTRATION COMPLETE")
    print("="*60)
    
    metrics = results["metrics"]
    print(f"\n📊 Performance Metrics:")
    print(f"  • Duration: {metrics['duration']:.1f} seconds")
    print(f"  • Plan Adaptations: {metrics['adaptations_made']}")
    print(f"  • Success Rate: {metrics['success_rate']:.1%}")
    print(f"  • Plan Efficiency: {metrics['plan_efficiency']:.2f}")
    
    if results["plan_adaptations"]:
        print(f"\n🔄 Adaptations Made:")
        for i, adaptation in enumerate(results["plan_adaptations"], 1):
            print(f"  {i}. {adaptation['adaptation_type']}: {adaptation['changes_made']}")
    
    synthesis = results["final_synthesis"]
    print(f"\n🎯 Key Insights:")
    for insight in synthesis["key_insights"]:
        print(f"  • {insight}")
    
    print(f"\n💡 This demonstration showed:")
    print(f"  ✓ Intelligent multi-step workflow planning")
    print(f"  ✓ Real-time quality assessment and issue detection")
    print(f"  ✓ Adaptive course correction when tools fail or produce poor results") 
    print(f"  ✓ Multiple adaptation strategies (fallbacks, preprocessing, parameter adjustment)")
    print(f"  ✓ Synthesis and learning from execution experience")
    
    # Save results
    import json
    with open("adaptive_demo_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Detailed results saved to adaptive_demo_results.json")

if __name__ == "__main__":
    asyncio.run(main())