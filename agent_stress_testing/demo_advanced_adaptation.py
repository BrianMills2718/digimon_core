#!/usr/bin/env python3
"""
Advanced Adaptive Agent Demonstration

Shows sophisticated course correction, multi-path exploration, and intelligent backtracking.
Demonstrates agents making complex decisions about when to retry, when to pivot, and when to abandon approaches.
"""

import asyncio
import json
import time
import uuid
import random
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum

class AdaptationStrategy(Enum):
    RETRY_WITH_FALLBACK = "retry_with_fallback"
    ADD_PREPROCESSING = "add_preprocessing" 
    PARAMETER_ADJUSTMENT = "parameter_adjustment"
    PARALLEL_EXPLORATION = "parallel_exploration"
    APPROACH_PIVOT = "approach_pivot"
    GRACEFUL_DEGRADATION = "graceful_degradation"
    INTELLIGENT_BACKTRACK = "intelligent_backtrack"

@dataclass 
class ExecutionContext:
    """Rich context about execution state and history"""
    step_index: int
    previous_attempts: List[Dict[str, Any]]
    quality_trend: List[float]  # Quality scores over time
    resource_constraints: Dict[str, Any]
    confidence_level: float
    alternative_paths: List[Dict[str, Any]]

@dataclass
class AdaptationDecision:
    """Detailed decision about how to adapt"""
    strategy: AdaptationStrategy
    confidence: float
    reasoning: str
    expected_improvement: float
    resource_cost: float
    risk_assessment: Dict[str, float]
    alternative_strategies: List[AdaptationStrategy]

class AdvancedAdaptiveDemo:
    """Demonstrates sophisticated adaptive decision-making"""
    
    def __init__(self):
        self.execution_history: List[Dict[str, Any]] = []
        self.adaptation_decisions: List[AdaptationDecision] = []
        self.alternative_paths_explored: List[Dict[str, Any]] = []
        self.learning_context: Dict[str, Any] = {}
        
    async def demonstrate_advanced_adaptation(self, complex_scenario: str) -> Dict[str, Any]:
        """Run advanced adaptive workflow with sophisticated decision-making"""
        print("🧠 ADVANCED ADAPTIVE AGENT DEMONSTRATION")
        print("="*70)
        print("This demo shows:")
        print("  ✓ Multi-path exploration when primary approach struggles")
        print("  ✓ Intelligent backtracking and approach pivoting")
        print("  ✓ Risk assessment and resource-aware decision making")
        print("  ✓ Learning from execution patterns to improve future decisions")
        print("="*70)
        
        demo_start = time.time()
        
        # Initialize sophisticated context
        execution_context = ExecutionContext(
            step_index=0,
            previous_attempts=[],
            quality_trend=[],
            resource_constraints={"time_budget": 300, "compute_budget": 1000, "api_calls": 50},
            confidence_level=0.8,
            alternative_paths=[]
        )
        
        # Phase 1: Strategic planning with multiple approaches
        print(f"\n🎯 PHASE 1: Strategic Multi-Path Planning")
        primary_plan, alternative_plans = await self._create_strategic_plan(complex_scenario)
        
        # Phase 2: Adaptive execution with intelligent course correction
        print(f"\n⚡ PHASE 2: Intelligent Adaptive Execution")
        results = await self._execute_with_advanced_adaptation(
            primary_plan, alternative_plans, execution_context
        )
        
        # Phase 3: Learning synthesis
        print(f"\n📚 PHASE 3: Learning and Pattern Recognition")
        learning_insights = await self._synthesize_learning(results, execution_context)
        
        demo_duration = time.time() - demo_start
        
        return {
            "scenario": complex_scenario,
            "primary_plan": primary_plan,
            "alternative_plans": alternative_plans,
            "execution_results": results,
            "adaptation_decisions": [asdict(d) for d in self.adaptation_decisions],
            "alternative_paths_explored": self.alternative_paths_explored,
            "learning_insights": learning_insights,
            "performance_metrics": {
                "duration": demo_duration,
                "total_adaptations": len(self.adaptation_decisions),
                "paths_explored": len(self.alternative_paths_explored) + 1,
                "learning_score": learning_insights.get("learning_effectiveness", 0),
                "final_success_rate": self._calculate_weighted_success_rate(results)
            }
        }
    
    async def _create_strategic_plan(self, scenario: str) -> tuple[List[Dict], List[List[Dict]]]:
        """Create primary plan plus alternative approaches"""
        print("  🎯 Research Agent creating strategic plan with multiple approaches...")
        await asyncio.sleep(1.5)
        
        # Primary approach: Traditional NLP pipeline
        primary_plan = [
            {
                "step_id": "primary_1",
                "name": "Document Processing",
                "tool": "advanced_document_processor",
                "approach": "primary",
                "confidence": 0.85,
                "expected_quality": 0.9,
                "resource_cost": 10
            },
            {
                "step_id": "primary_2", 
                "name": "Multi-Modal NER",
                "tool": "enhanced_ner_system",
                "approach": "primary",
                "confidence": 0.75,
                "expected_quality": 0.8,
                "resource_cost": 25
            },
            {
                "step_id": "primary_3",
                "name": "Relationship Mining",
                "tool": "deep_relationship_extractor", 
                "approach": "primary",
                "confidence": 0.7,
                "expected_quality": 0.75,
                "resource_cost": 30
            },
            {
                "step_id": "primary_4",
                "name": "Network Construction",
                "tool": "dynamic_network_builder",
                "approach": "primary", 
                "confidence": 0.8,
                "expected_quality": 0.85,
                "resource_cost": 20
            }
        ]
        
        # Alternative approach 1: Statistical/ML-heavy
        statistical_approach = [
            {
                "step_id": "stat_1",
                "name": "Statistical Text Analysis", 
                "tool": "statistical_analyzer",
                "approach": "statistical",
                "confidence": 0.9,
                "expected_quality": 0.75,
                "resource_cost": 15
            },
            {
                "step_id": "stat_2",
                "name": "Clustering-Based Entity Discovery",
                "tool": "ml_clustering_system",
                "approach": "statistical",
                "confidence": 0.85,
                "expected_quality": 0.7,
                "resource_cost": 35
            },
            {
                "step_id": "stat_3",
                "name": "Correlation Network Building",
                "tool": "correlation_network_builder",
                "approach": "statistical",
                "confidence": 0.8,
                "expected_quality": 0.8,
                "resource_cost": 25
            }
        ]
        
        # Alternative approach 2: Lightweight/fast
        lightweight_approach = [
            {
                "step_id": "light_1",
                "name": "Keyword Extraction",
                "tool": "fast_keyword_extractor",
                "approach": "lightweight",
                "confidence": 0.9,
                "expected_quality": 0.6,
                "resource_cost": 5
            },
            {
                "step_id": "light_2", 
                "name": "Co-occurrence Analysis",
                "tool": "cooccurrence_analyzer",
                "approach": "lightweight",
                "confidence": 0.85,
                "expected_quality": 0.65,
                "resource_cost": 8
            },
            {
                "step_id": "light_3",
                "name": "Simple Network Assembly",
                "tool": "basic_network_assembler",
                "approach": "lightweight",
                "confidence": 0.9,
                "expected_quality": 0.7,
                "resource_cost": 10
            }
        ]
        
        alternative_plans = [statistical_approach, lightweight_approach]
        
        print(f"    ✅ Created primary plan (4 steps) + 2 alternative approaches")
        print(f"    📊 Primary: Traditional NLP pipeline (high quality, high cost)")  
        print(f"    📊 Alt 1: Statistical/ML approach (medium quality, medium cost)")
        print(f"    📊 Alt 2: Lightweight approach (lower quality, low cost)")
        
        return primary_plan, alternative_plans
    
    async def _execute_with_advanced_adaptation(self, primary_plan: List[Dict], 
                                              alternative_plans: List[List[Dict]],
                                              context: ExecutionContext) -> List[Dict[str, Any]]:
        """Execute with sophisticated adaptation logic"""
        results = []
        current_plan = primary_plan.copy()
        current_approach = "primary"
        step_index = 0
        
        while step_index < len(current_plan) and self._should_continue(context):
            step = current_plan[step_index]
            print(f"\n  🔧 Executing Step {step_index + 1}: {step['name']} ({current_approach} approach)")
            
            # Execute step with rich monitoring
            result = await self._execute_step_with_monitoring(step, context)
            results.append(result)
            context.quality_trend.append(result["quality_score"])
            context.step_index = step_index
            
            print(f"    Status: {result['status']} | Quality: {result['quality_score']:.2f} | Confidence: {result.get('confidence', 0):.2f}")
            
            # Sophisticated adaptation decision
            if self._needs_advanced_adaptation(result, step, context):
                adaptation_decision = await self._make_adaptation_decision(
                    step, result, current_plan, alternative_plans, context
                )
                
                if adaptation_decision:
                    print(f"  🧠 Adaptation Decision: {adaptation_decision.strategy.value}")
                    print(f"    Reasoning: {adaptation_decision.reasoning}")
                    print(f"    Expected Improvement: {adaptation_decision.expected_improvement:.2f}")
                    print(f"    Confidence: {adaptation_decision.confidence:.2f}")
                    
                    # Apply adaptation
                    adaptation_result = await self._apply_adaptation(
                        adaptation_decision, current_plan, alternative_plans, step_index, context
                    )
                    
                    if adaptation_result:
                        current_plan = adaptation_result["new_plan"]
                        current_approach = adaptation_result.get("new_approach", current_approach)
                        
                        # Handle different adaptation strategies
                        if adaptation_decision.strategy == AdaptationStrategy.INTELLIGENT_BACKTRACK:
                            step_index = adaptation_result.get("backtrack_to_step", step_index - 1)
                            print(f"    🔄 Backtracking to step {step_index + 1}")
                        elif adaptation_decision.strategy == AdaptationStrategy.PARALLEL_EXPLORATION:
                            # Launch parallel execution (simulated)
                            parallel_results = await self._explore_parallel_paths(
                                alternative_plans, step_index, context
                            )
                            self.alternative_paths_explored.extend(parallel_results)
                        elif adaptation_decision.strategy == AdaptationStrategy.APPROACH_PIVOT:
                            print(f"    🔄 Pivoting to {current_approach} approach")
                            step_index = 0  # Restart with new approach
                            results.clear()  # Clear previous results
                            continue
                    
                    self.adaptation_decisions.append(adaptation_decision)
            
            step_index += 1
            await asyncio.sleep(0.5)  # Demo pacing
        
        return results
    
    async def _execute_step_with_monitoring(self, step: Dict[str, Any], 
                                          context: ExecutionContext) -> Dict[str, Any]:
        """Execute step with comprehensive monitoring and context awareness"""
        start_time = time.time()
        
        # Determine success probability based on context
        base_success_prob = step.get("confidence", 0.7)
        
        # Adjust based on quality trend
        if len(context.quality_trend) >= 2:
            recent_trend = context.quality_trend[-2:]
            if all(q < 0.6 for q in recent_trend):
                base_success_prob -= 0.2  # Cascading failures
            elif all(q > 0.8 for q in recent_trend): 
                base_success_prob += 0.1  # Success momentum
        
        # Adjust based on resource constraints
        resource_pressure = 1 - (context.resource_constraints["time_budget"] / 300)
        if resource_pressure > 0.7:
            base_success_prob -= 0.15  # Time pressure degrades quality
        
        # Simulate realistic execution scenarios
        scenarios = self._get_realistic_scenarios(step["tool"], base_success_prob)
        selected_scenario = self._select_contextual_scenario(scenarios, context)
        
        # Simulate execution time
        await asyncio.sleep(selected_scenario["duration"])
        
        # Update resource constraints
        context.resource_constraints["time_budget"] -= selected_scenario["duration"]
        context.resource_constraints["compute_budget"] -= step.get("resource_cost", 10)
        context.resource_constraints["api_calls"] -= 1
        
        execution_time = time.time() - start_time
        
        result = {
            "step_id": step["step_id"],
            "step_name": step["name"],
            "tool": step["tool"],
            "approach": step["approach"],
            "status": selected_scenario["status"],
            "quality_score": selected_scenario["quality_score"],
            "confidence": selected_scenario.get("confidence", 0.7),
            "execution_time": execution_time,
            "output_data": selected_scenario["output_data"],
            "issues": selected_scenario["issues"],
            "resource_usage": {
                "time": selected_scenario["duration"],
                "compute": step.get("resource_cost", 10),
                "api_calls": 1
            },
            "context_factors": {
                "quality_trend_impact": len(context.quality_trend),
                "resource_pressure": resource_pressure,
                "step_index": context.step_index
            }
        }
        
        return result
    
    def _get_realistic_scenarios(self, tool_name: str, base_prob: float) -> List[Dict[str, Any]]:
        """Get contextually realistic execution scenarios"""
        scenarios = {
            "advanced_document_processor": [
                {
                    "status": "success", "quality_score": 0.95, "confidence": 0.9,
                    "duration": 2.5, "output_data": {"documents_processed": 15, "extraction_rate": 0.98},
                    "issues": [], "probability": base_prob
                },
                {
                    "status": "partial", "quality_score": 0.7, "confidence": 0.6,
                    "duration": 4.0, "output_data": {"documents_processed": 12, "extraction_rate": 0.85},
                    "issues": ["OCR difficulties with handwritten annotations", "Inconsistent formatting"],
                    "probability": (1 - base_prob) * 0.7
                },
                {
                    "status": "failure", "quality_score": 0.2, "confidence": 0.2,
                    "duration": 1.5, "output_data": {},
                    "issues": ["Unsupported file formats", "Critical parsing errors"],
                    "probability": (1 - base_prob) * 0.3
                }
            ],
            "enhanced_ner_system": [
                {
                    "status": "success", "quality_score": 0.88, "confidence": 0.85,
                    "duration": 3.5, "output_data": {"entities_found": 247, "precision": 0.89, "recall": 0.84},
                    "issues": [], "probability": base_prob
                },
                {
                    "status": "partial", "quality_score": 0.55, "confidence": 0.45,
                    "duration": 4.0, "output_data": {"entities_found": 156, "precision": 0.72, "recall": 0.68},
                    "issues": ["Domain terminology not in training data", "Ambiguous entity boundaries"],
                    "probability": (1 - base_prob) * 0.8
                }
            ],
            "statistical_analyzer": [
                {
                    "status": "success", "quality_score": 0.82, "confidence": 0.9,
                    "duration": 2.0, "output_data": {"patterns_found": 34, "significance_level": 0.95},
                    "issues": [], "probability": base_prob + 0.1  # Generally more reliable
                }
            ]
        }
        
        return scenarios.get(tool_name, scenarios["statistical_analyzer"])
    
    def _select_contextual_scenario(self, scenarios: List[Dict[str, Any]], 
                                  context: ExecutionContext) -> Dict[str, Any]:
        """Select scenario based on rich context"""
        # Weight scenarios by their contextual probability
        weights = [s.get("probability", 0.5) for s in scenarios]
        
        # Adjust for execution history patterns
        if len(context.previous_attempts) > 0:
            # If we've had recent failures, increase failure probability
            recent_failures = sum(1 for attempt in context.previous_attempts[-3:] 
                                if attempt.get("status") == "failure")
            if recent_failures > 1:
                weights[-1] *= 1.5  # Increase failure probability
        
        # Normalize weights
        total_weight = sum(weights)
        if total_weight > 0:
            weights = [w / total_weight for w in weights]
        
        return random.choices(scenarios, weights=weights)[0]
    
    def _needs_advanced_adaptation(self, result: Dict[str, Any], step: Dict[str, Any], 
                                 context: ExecutionContext) -> bool:
        """Sophisticated adaptation need assessment"""
        # Quality-based triggers
        if result["quality_score"] < 0.6:
            return True
        
        # Trend-based triggers
        if len(context.quality_trend) >= 3:
            recent_trend = context.quality_trend[-3:]
            if all(q < 0.7 for q in recent_trend):  # Sustained poor quality
                return True
            if recent_trend[-1] < recent_trend[-2] - 0.2:  # Sharp quality drop
                return True
        
        # Resource-based triggers
        remaining_budget = context.resource_constraints["time_budget"]
        if remaining_budget < 60 and result["quality_score"] < 0.8:  # Time pressure + poor quality
            return True
        
        # Confidence-based triggers
        if result.get("confidence", 1.0) < 0.5:
            return True
        
        return False
    
    async def _make_adaptation_decision(self, step: Dict[str, Any], result: Dict[str, Any],
                                      current_plan: List[Dict], alternative_plans: List[List[Dict]],
                                      context: ExecutionContext) -> Optional[AdaptationDecision]:
        """Make sophisticated adaptation decision with reasoning"""
        print("    🧠 Research Agent conducting deep adaptation analysis...")
        await asyncio.sleep(1.0)
        
        # Analyze situation
        quality_score = result["quality_score"]
        confidence = result.get("confidence", 0.5)
        remaining_resources = context.resource_constraints["time_budget"]
        quality_trend = context.quality_trend[-3:] if len(context.quality_trend) >= 3 else []
        
        # Evaluate adaptation strategies
        strategies = []
        
        # Strategy 1: Retry with fallback
        if quality_score < 0.6 and confidence > 0.3:
            strategies.append(AdaptationDecision(
                strategy=AdaptationStrategy.RETRY_WITH_FALLBACK,
                confidence=0.7,
                reasoning="Low quality but tool shows promise, worth trying fallback approach",
                expected_improvement=0.3,
                resource_cost=15,
                risk_assessment={"failure_risk": 0.3, "time_risk": 0.2},
                alternative_strategies=[]
            ))
        
        # Strategy 2: Parallel exploration
        if remaining_resources > 100 and len(alternative_plans) > 0:
            strategies.append(AdaptationDecision(
                strategy=AdaptationStrategy.PARALLEL_EXPLORATION,
                confidence=0.8,
                reasoning="Sufficient resources to explore alternative approaches in parallel",
                expected_improvement=0.4,
                resource_cost=40,
                risk_assessment={"failure_risk": 0.2, "time_risk": 0.4},
                alternative_strategies=[]
            ))
        
        # Strategy 3: Approach pivot
        if len(quality_trend) >= 2 and all(q < 0.6 for q in quality_trend):
            strategies.append(AdaptationDecision(
                strategy=AdaptationStrategy.APPROACH_PIVOT,
                confidence=0.75,
                reasoning="Sustained poor performance suggests fundamental approach mismatch",
                expected_improvement=0.5,
                resource_cost=30,
                risk_assessment={"failure_risk": 0.4, "time_risk": 0.3},
                alternative_strategies=[]
            ))
        
        # Strategy 4: Intelligent backtrack
        if context.step_index > 1 and quality_score < 0.4:
            strategies.append(AdaptationDecision(
                strategy=AdaptationStrategy.INTELLIGENT_BACKTRACK,
                confidence=0.6,
                reasoning="Critical failure suggests need to reconsider earlier decisions",
                expected_improvement=0.35,
                resource_cost=25,
                risk_assessment={"failure_risk": 0.5, "time_risk": 0.6},
                alternative_strategies=[]
            ))
        
        # Strategy 5: Graceful degradation
        if remaining_resources < 50:
            strategies.append(AdaptationDecision(
                strategy=AdaptationStrategy.GRACEFUL_DEGRADATION,
                confidence=0.9,
                reasoning="Limited resources require accepting lower quality for completion",
                expected_improvement=0.15,
                resource_cost=5,
                risk_assessment={"failure_risk": 0.1, "time_risk": 0.1},
                alternative_strategies=[]
            ))
        
        # Select best strategy
        if strategies:
            # Score strategies by expected value
            best_strategy = max(strategies, key=lambda s: 
                s.expected_improvement * s.confidence - s.resource_cost * 0.01
            )
            
            # Set alternative strategies
            best_strategy.alternative_strategies = [s.strategy for s in strategies if s != best_strategy]
            
            return best_strategy
        
        return None
    
    async def _apply_adaptation(self, decision: AdaptationDecision, current_plan: List[Dict],
                              alternative_plans: List[List[Dict]], step_index: int,
                              context: ExecutionContext) -> Optional[Dict[str, Any]]:
        """Apply the selected adaptation strategy"""
        
        if decision.strategy == AdaptationStrategy.APPROACH_PIVOT:
            # Select best alternative plan
            if alternative_plans:
                # Choose lightweight approach if resources are constrained
                if context.resource_constraints["time_budget"] < 100:
                    new_plan = alternative_plans[-1]  # Lightweight approach
                    new_approach = "lightweight"
                else:
                    new_plan = alternative_plans[0]  # Statistical approach  
                    new_approach = "statistical"
                
                return {
                    "new_plan": new_plan,
                    "new_approach": new_approach,
                    "modification_type": "full_pivot"
                }
        
        elif decision.strategy == AdaptationStrategy.INTELLIGENT_BACKTRACK:
            # Identify optimal backtrack point
            backtrack_step = max(0, step_index - 2)
            modified_plan = current_plan.copy()
            
            # Modify the plan from backtrack point forward
            for i in range(backtrack_step, len(modified_plan)):
                modified_plan[i] = {**modified_plan[i], "modified": True, "approach": "revised"}
            
            return {
                "new_plan": modified_plan,
                "new_approach": "revised",
                "backtrack_to_step": backtrack_step,
                "modification_type": "intelligent_backtrack"
            }
        
        elif decision.strategy == AdaptationStrategy.GRACEFUL_DEGRADATION:
            # Simplify remaining steps
            simplified_plan = current_plan.copy()
            for i in range(step_index + 1, len(simplified_plan)):
                simplified_plan[i] = {
                    **simplified_plan[i],
                    "tool": simplified_plan[i]["tool"].replace("advanced", "basic").replace("enhanced", "simple"),
                    "expected_quality": simplified_plan[i].get("expected_quality", 0.8) * 0.7,
                    "resource_cost": simplified_plan[i].get("resource_cost", 20) * 0.5
                }
            
            return {
                "new_plan": simplified_plan,
                "new_approach": "degraded",
                "modification_type": "graceful_degradation"
            }
        
        # Default: no modification
        return None
    
    async def _explore_parallel_paths(self, alternative_plans: List[List[Dict]], 
                                    current_step: int, context: ExecutionContext) -> List[Dict[str, Any]]:
        """Simulate exploration of alternative paths in parallel"""
        print("    🔄 Launching parallel path exploration...")
        
        parallel_results = []
        for i, alt_plan in enumerate(alternative_plans):
            if current_step < len(alt_plan):
                alt_step = alt_plan[current_step]
                print(f"      Exploring {alt_step['approach']} approach...")
                
                # Simulate parallel execution (faster but lower confidence)
                await asyncio.sleep(1.0)  # Parallel execution time
                
                # Alternative paths generally have different risk/reward profiles
                if alt_step["approach"] == "statistical":
                    quality_score = random.uniform(0.6, 0.85)
                    confidence = 0.8
                elif alt_step["approach"] == "lightweight":
                    quality_score = random.uniform(0.5, 0.75)
                    confidence = 0.9
                else:
                    quality_score = random.uniform(0.4, 0.8)
                    confidence = 0.6
                
                parallel_results.append({
                    "approach": alt_step["approach"],
                    "step_name": alt_step["name"],
                    "quality_score": quality_score,
                    "confidence": confidence,
                    "execution_time": 1.0,
                    "resource_cost": alt_step.get("resource_cost", 10) * 0.3  # Parallel efficiency
                })
                
                print(f"        Result: {quality_score:.2f} quality, {confidence:.2f} confidence")
        
        return parallel_results
    
    async def _synthesize_learning(self, results: List[Dict[str, Any]], 
                                 context: ExecutionContext) -> Dict[str, Any]:
        """Extract learning insights from the execution experience"""
        print("  📚 Research Agent analyzing execution patterns for learning insights...")
        await asyncio.sleep(2.0)
        
        # Analyze adaptation effectiveness
        adaptation_effectiveness = {}
        for decision in self.adaptation_decisions:
            strategy = decision.strategy.value
            if strategy not in adaptation_effectiveness:
                adaptation_effectiveness[strategy] = {"attempts": 0, "improvements": 0}
            adaptation_effectiveness[strategy]["attempts"] += 1
            
            # Rough measure of improvement (simplified for demo)
            if decision.expected_improvement > 0.3:
                adaptation_effectiveness[strategy]["improvements"] += 1
        
        # Quality pattern analysis
        quality_patterns = {
            "average_quality": sum(r["quality_score"] for r in results) / len(results) if results else 0,
            "quality_variance": self._calculate_variance([r["quality_score"] for r in results]),
            "quality_trend": "improving" if self._is_improving_trend(context.quality_trend) else "stable_or_declining"
        }
        
        # Resource efficiency analysis
        total_resource_usage = sum(r.get("resource_usage", {}).get("compute", 0) for r in results)
        resource_efficiency = len([r for r in results if r["status"] == "success"]) / max(1, total_resource_usage) * 100
        
        # Approach effectiveness
        approach_performance = {}
        for result in results:
            approach = result.get("approach", "unknown")
            if approach not in approach_performance:
                approach_performance[approach] = {"attempts": 0, "avg_quality": 0, "successes": 0}
            approach_performance[approach]["attempts"] += 1
            approach_performance[approach]["avg_quality"] += result["quality_score"]
            if result["status"] == "success":
                approach_performance[approach]["successes"] += 1
        
        # Normalize averages
        for approach in approach_performance:
            attempts = approach_performance[approach]["attempts"]
            approach_performance[approach]["avg_quality"] /= attempts
            approach_performance[approach]["success_rate"] = approach_performance[approach]["successes"] / attempts
        
        # Generate insights
        insights = []
        
        if adaptation_effectiveness:
            most_effective = max(adaptation_effectiveness.items(), 
                               key=lambda x: x[1]["improvements"] / max(1, x[1]["attempts"]))
            insights.append(f"Most effective adaptation strategy: {most_effective[0]}")
        
        if quality_patterns["average_quality"] > 0.7:
            insights.append(f"Achieved high average quality ({quality_patterns['average_quality']:.1%})")
        
        if resource_efficiency > 5:
            insights.append(f"Good resource efficiency: {resource_efficiency:.1f} successes per 100 compute units")
        
        best_approach = max(approach_performance.items(), key=lambda x: x[1]["avg_quality"]) if approach_performance else None
        if best_approach:
            insights.append(f"Best performing approach: {best_approach[0]} ({best_approach[1]['avg_quality']:.1%} avg quality)")
        
        learning_effectiveness = len(insights) / 10  # Simple learning effectiveness metric
        
        return {
            "adaptation_effectiveness": adaptation_effectiveness,
            "quality_patterns": quality_patterns,
            "resource_efficiency": resource_efficiency,
            "approach_performance": approach_performance,
            "key_insights": insights,
            "learning_effectiveness": learning_effectiveness,
            "recommendations": self._generate_strategic_recommendations(
                adaptation_effectiveness, quality_patterns, approach_performance
            )
        }
    
    def _should_continue(self, context: ExecutionContext) -> bool:
        """Determine if execution should continue based on context"""
        return (context.resource_constraints["time_budget"] > 10 and 
                context.resource_constraints["api_calls"] > 0)
    
    def _calculate_weighted_success_rate(self, results: List[Dict[str, Any]]) -> float:
        """Calculate success rate weighted by quality scores"""
        if not results:
            return 0.0
        
        weighted_success = sum(r["quality_score"] for r in results if r["status"] in ["success", "partial"])
        max_possible = len(results)
        return weighted_success / max_possible if max_possible > 0 else 0.0
    
    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance of quality scores"""
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        return sum((v - mean) ** 2 for v in values) / len(values)
    
    def _is_improving_trend(self, quality_trend: List[float]) -> bool:
        """Determine if quality trend is improving"""
        if len(quality_trend) < 3:
            return False
        return quality_trend[-1] > quality_trend[-3]
    
    def _generate_strategic_recommendations(self, adaptation_effectiveness: Dict, 
                                          quality_patterns: Dict, 
                                          approach_performance: Dict) -> List[str]:
        """Generate strategic recommendations based on learning"""
        recommendations = []
        
        # Adaptation strategy recommendations
        if adaptation_effectiveness:
            best_adaptation = max(adaptation_effectiveness.items(), 
                                key=lambda x: x[1]["improvements"] / max(1, x[1]["attempts"]))
            recommendations.append(f"Prioritize {best_adaptation[0]} adaptation strategy in future workflows")
        
        # Quality improvement recommendations
        if quality_patterns["quality_variance"] > 0.1:
            recommendations.append("High quality variance suggests need for more consistent preprocessing")
        
        # Approach selection recommendations
        if approach_performance:
            approaches_by_success = sorted(approach_performance.items(), 
                                         key=lambda x: x[1]["success_rate"], reverse=True)
            if len(approaches_by_success) > 1:
                recommendations.append(f"Consider starting with {approaches_by_success[0][0]} approach for similar tasks")
        
        if not recommendations:
            recommendations.append("Execution patterns suggest current strategy is effective")
        
        return recommendations

async def main():
    """Run the advanced adaptive demonstration"""
    demo = AdvancedAdaptiveDemo()
    
    complex_scenario = """
    Conduct a comprehensive meta-analysis of research collaboration networks in cognitive science by:
    
    1. Processing a heterogeneous collection of academic documents (papers, conference proceedings, grant records)
    2. Extracting multi-modal entities (researchers, institutions, concepts, methodologies, funding sources)
    3. Identifying complex relationship patterns (collaborations, citations, theoretical influences, funding flows)
    4. Building a multi-layered knowledge graph with temporal dynamics
    5. Analyzing network evolution patterns and predicting future collaboration opportunities
    
    The analysis must adapt intelligently to:
    - Document format inconsistencies and OCR quality issues
    - Domain-specific terminology and evolving research vocabularies  
    - Sparse relationship data and ambiguous entity boundaries
    - Computational resource constraints and time limitations
    - Unexpected network structures that don't fit standard models
    
    Success requires sophisticated course correction including:
    - Parallel exploration of alternative analytical approaches
    - Intelligent backtracking when fundamental assumptions prove wrong
    - Resource-aware graceful degradation under time/compute pressure
    - Learning from execution patterns to optimize future decisions
    """
    
    results = await demo.demonstrate_advanced_adaptation(complex_scenario)
    
    # Display comprehensive results
    print("\n" + "="*70)
    print("🏆 ADVANCED ADAPTIVE DEMONSTRATION COMPLETE")
    print("="*70)
    
    metrics = results["performance_metrics"]
    print(f"\n📊 Advanced Performance Metrics:")
    print(f"  • Total Duration: {metrics['duration']:.1f} seconds")
    print(f"  • Total Adaptations: {metrics['total_adaptations']}")
    print(f"  • Paths Explored: {metrics['paths_explored']}")
    print(f"  • Learning Score: {metrics['learning_score']:.2f}")
    print(f"  • Weighted Success Rate: {metrics['final_success_rate']:.1%}")
    
    print(f"\n🧠 Sophisticated Adaptation Decisions:")
    for i, decision in enumerate(results["adaptation_decisions"], 1):
        strategy_str = decision['strategy'] if isinstance(decision['strategy'], str) else decision['strategy'].value
        print(f"  {i}. {strategy_str.upper()}")
        print(f"     Reasoning: {decision['reasoning']}")
        print(f"     Expected Improvement: {decision['expected_improvement']:.2f}")
        print(f"     Resource Cost: {decision['resource_cost']}")
    
    if results["alternative_paths_explored"]:
        print(f"\n🔄 Alternative Paths Explored:")
        for i, path in enumerate(results["alternative_paths_explored"], 1):
            print(f"  {i}. {path['approach']} - {path['step_name']}")
            print(f"     Quality: {path['quality_score']:.2f} | Confidence: {path['confidence']:.2f}")
    
    learning = results["learning_insights"]
    print(f"\n📚 Learning Insights:")
    for insight in learning["key_insights"]:
        print(f"  • {insight}")
    
    print(f"\n💡 Strategic Recommendations:")
    for rec in learning["recommendations"]:
        print(f"  • {rec}")
    
    print(f"\n✨ This advanced demonstration showed:")
    print(f"  ✓ Multi-path strategic planning with risk assessment")
    print(f"  ✓ Sophisticated adaptation decision-making with reasoning")
    print(f"  ✓ Parallel exploration of alternative approaches")
    print(f"  ✓ Intelligent backtracking and approach pivoting")
    print(f"  ✓ Resource-aware graceful degradation")
    print(f"  ✓ Learning from execution patterns for future optimization")
    print(f"  ✓ Strategic recommendations based on performance analysis")
    
    # Save detailed results
    with open("advanced_adaptive_demo_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Comprehensive results saved to advanced_adaptive_demo_results.json")

if __name__ == "__main__":
    asyncio.run(main())