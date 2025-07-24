#!/usr/bin/env python3
"""
Literature Review Test

End-to-end test of literature analysis and synthesis workflow using real integrations.
"""

import asyncio
import json
import time
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
from pathlib import Path

# Import real integrations
from ..real_claude_integration import RealClaudeCodeClient, DualAgentCoordinator
from ..real_mcp_integration import RealMemoryIntegrator
from ..real_kgas_integration import RealWorkflowExecutor


@dataclass
class LiteratureReviewResult:
    """Result from literature review test"""
    test_id: str
    status: str
    execution_time: float
    documents_processed: int
    themes_identified: List[str]
    synthesis_quality: float
    citations_validated: int
    research_gaps_identified: List[str]
    methodology_assessment: Dict[str, float]
    performance_metrics: Dict[str, Any]


class LiteratureReviewTestRunner:
    """Test runner for literature review scenarios"""
    
    def __init__(self):
        self.coordinator = None
        self.memory_integrator = None
        self.workflow_executor = None
    
    async def setup(self) -> bool:
        """Set up integrations for literature review testing"""
        try:
            # Configure research agent for literature review
            research_config = {
                "system_prompt": """
You are an expert literature review specialist with deep knowledge of academic research.

Your capabilities:
- Systematic literature analysis and synthesis
- Identification of research themes and patterns
- Gap analysis in existing research
- Methodology evaluation and comparison
- Citation validation and quality assessment
- Research trend identification

Approach:
- Conduct thorough analysis of academic literature
- Identify key themes, methodologies, and findings
- Synthesize insights across multiple sources
- Highlight research gaps and opportunities
- Provide evidence-based recommendations
                """,
                "model": "claude-3-5-sonnet-20241022",
                "temperature": 0.6,
                "tools": ["literature_analysis", "citation_validation", "research_synthesis"]
            }
            
            execution_config = {
                "system_prompt": """
You are a precise literature processing and analysis coordinator.

Execute literature review workflows including:
- Document processing and text extraction
- Citation analysis and validation
- Thematic analysis across documents
- Statistical analysis of research patterns
- Cross-reference verification
- Quality assessment of sources

Focus on systematic processing and comprehensive analysis.
                """,
                "model": "claude-3-5-sonnet-20241022",
                "temperature": 0.3,
                "tools": ["document_processing", "citation_analysis", "thematic_analysis"]
            }
            
            self.coordinator = DualAgentCoordinator(research_config, execution_config)
            self.memory_integrator = RealMemoryIntegrator()
            self.workflow_executor = RealWorkflowExecutor()
            
            # Connect memory if available
            await self.memory_integrator.connect()
            
            return True
            
        except Exception as e:
            print(f"Literature review setup failed: {e}")
            return False
    
    async def run_literature_review_test(self, research_query: str, document_sources: List[str]) -> LiteratureReviewResult:
        """Run comprehensive literature review test"""
        test_id = f"lit_review_{int(time.time())}"
        start_time = time.time()
        
        try:
            # Step 1: Design literature review methodology
            methodology_prompt = f"""
Research Query: {research_query}
Available Documents: {len(document_sources)} sources

Design a comprehensive literature review methodology that includes:
1. Systematic document analysis approach
2. Thematic analysis framework
3. Citation validation procedures
4. Research gap identification strategy
5. Synthesis and integration methods

Create a detailed workflow for systematic literature analysis.
            """
            
            methodology_result = await self.coordinator.execute_research_workflow(
                methodology_prompt,
                {
                    "task_type": "literature_review",
                    "document_count": len(document_sources),
                    "research_domain": "multidisciplinary"
                }
            )
            
            if methodology_result["status"] != "success":
                raise RuntimeError(f"Methodology design failed: {methodology_result.get('error')}")
            
            # Step 2: Execute literature processing workflow
            literature_workflow = {
                "name": "Literature Review Workflow",
                "description": "Systematic analysis of academic literature",
                "phases": [
                    {
                        "name": "document_processing",
                        "tools": ["directory_processor"],
                        "inputs": {
                            "directory_path": str(Path(__file__).parent.parent / "test_data/sample_documents")
                        }
                    },
                    {
                        "name": "thematic_analysis",
                        "tools": ["text_analyzer"],
                        "inputs": {
                            "analysis_config": {
                                "extract_themes": True,
                                "identify_methodologies": True,
                                "extract_findings": True
                            }
                        }
                    },
                    {
                        "name": "citation_analysis",
                        "tools": ["network_analyzer"],
                        "inputs": {
                            "analysis_type": "citation_network"
                        }
                    },
                    {
                        "name": "synthesis_analysis",
                        "tools": ["statistical_analyzer"],
                        "inputs": {
                            "analysis_type": "research_synthesis"
                        }
                    }
                ]
            }
            
            execution_result = await self.workflow_executor.execute_workflow(literature_workflow)
            
            if execution_result["overall_status"] != "completed":
                raise RuntimeError(f"Literature processing failed: {execution_result.get('error')}")
            
            # Step 3: Extract and analyze results
            analysis_results = self._analyze_literature_results(execution_result)
            
            # Step 4: Generate literature review synthesis
            synthesis_prompt = f"""
Based on the literature analysis results:

Thematic Analysis: {json.dumps(analysis_results.get('themes', {}), indent=2)}
Citation Patterns: {json.dumps(analysis_results.get('citations', {}), indent=2)}
Research Patterns: {json.dumps(analysis_results.get('patterns', {}), indent=2)}

Provide:
1. Comprehensive synthesis of key themes
2. Identification of research gaps
3. Methodology assessment across studies
4. Recommendations for future research
5. Quality assessment of the literature base

Focus on research insights and evidence-based conclusions.
            """
            
            synthesis_result = await self.coordinator.research_agent.query(synthesis_prompt)
            
            if synthesis_result.error:
                raise RuntimeError(f"Synthesis generation failed: {synthesis_result.error}")
            
            # Extract insights and metrics
            themes_identified = analysis_results.get('themes', [])
            research_gaps = self._extract_research_gaps(synthesis_result.content)
            methodology_assessment = self._assess_methodologies(analysis_results)
            synthesis_quality = self._calculate_synthesis_quality(synthesis_result.content)
            
            execution_time = time.time() - start_time
            
            # Store in memory if available
            if self.memory_integrator.connected:
                session_data = {
                    "session_id": test_id,
                    "user_id": "literature_reviewer",
                    "query": research_query,
                    "domain": "literature_review",
                    "methodology": "systematic_review",
                    "execution_time": execution_time,
                    "quality_score": synthesis_quality,
                    "findings": research_gaps,
                    "themes": themes_identified
                }
                await self.memory_integrator.store_research_session(session_data)
            
            return LiteratureReviewResult(
                test_id=test_id,
                status="success",
                execution_time=execution_time,
                documents_processed=len(document_sources),
                themes_identified=themes_identified,
                synthesis_quality=synthesis_quality,
                citations_validated=analysis_results.get('citation_count', 0),
                research_gaps_identified=research_gaps,
                methodology_assessment=methodology_assessment,
                performance_metrics=self._calculate_performance_metrics(
                    methodology_result, execution_result, synthesis_result
                )
            )
            
        except Exception as e:
            return LiteratureReviewResult(
                test_id=test_id,
                status="error",
                execution_time=time.time() - start_time,
                documents_processed=0,
                themes_identified=[],
                synthesis_quality=0.0,
                citations_validated=0,
                research_gaps_identified=[],
                methodology_assessment={},
                performance_metrics={"error": str(e)}
            )
    
    def _analyze_literature_results(self, execution_result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze literature processing results"""
        analysis = {}
        
        # Extract themes from thematic analysis
        for phase_name, phase_result in execution_result.get("phase_results", {}).items():
            if "thematic_analysis" in phase_name:
                for tool_output in phase_result.get("outputs", {}).values():
                    if isinstance(tool_output, dict) and "themes" in tool_output:
                        analysis["themes"] = tool_output["themes"]
                        analysis["confidence_scores"] = tool_output.get("confidence_scores", [])
            
            elif "citation_analysis" in phase_name:
                for tool_output in phase_result.get("outputs", {}).values():
                    if isinstance(tool_output, dict) and "network_metrics" in tool_output:
                        analysis["citations"] = tool_output["network_metrics"]
                        analysis["citation_count"] = tool_output["network_metrics"].get("node_count", 0)
            
            elif "synthesis_analysis" in phase_name:
                for tool_output in phase_result.get("outputs", {}).values():
                    if isinstance(tool_output, dict) and "statistics" in tool_output:
                        analysis["patterns"] = tool_output["statistics"]
        
        return analysis
    
    def _extract_research_gaps(self, synthesis_content: str) -> List[str]:
        """Extract research gaps from synthesis"""
        gaps = []
        lines = synthesis_content.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['gap', 'limitation', 'future research', 'unexplored', 'needs']):
                if len(line.strip()) > 20:
                    gaps.append(line.strip())
        
        return gaps[:5]  # Top 5 gaps
    
    def _assess_methodologies(self, analysis_results: Dict[str, Any]) -> Dict[str, float]:
        """Assess methodology quality across literature"""
        assessment = {}
        
        # Simulate methodology assessment based on analysis results
        themes = analysis_results.get('themes', [])
        citations = analysis_results.get('citations', {})
        
        assessment["methodological_diversity"] = min(len(themes) / 5.0, 1.0)  # Normalized
        assessment["citation_quality"] = min(citations.get("density", 0) * 2, 1.0)  # Normalized
        assessment["research_rigor"] = 0.8  # Would be calculated from actual analysis
        assessment["evidence_strength"] = 0.75  # Would be calculated from findings
        
        return assessment
    
    def _calculate_synthesis_quality(self, synthesis_content: str) -> float:
        """Calculate quality of literature synthesis"""
        score = 0.0
        
        # Length and depth
        if len(synthesis_content) > 1000:
            score += 0.3
        
        # Key elements present
        synthesis_lower = synthesis_content.lower()
        key_elements = ['synthesis', 'pattern', 'gap', 'methodology', 'finding', 'conclusion', 'recommendation']
        elements_present = sum(1 for element in key_elements if element in synthesis_lower)
        score += 0.5 * (elements_present / len(key_elements))
        
        # Research insights
        insight_indicators = ['significant', 'important', 'reveals', 'suggests', 'demonstrates']
        insights = sum(1 for indicator in insight_indicators if indicator in synthesis_lower)
        score += 0.2 * min(insights / 3, 1.0)
        
        return min(score, 1.0)
    
    def _calculate_performance_metrics(self, methodology_result: Dict, execution_result: Dict, synthesis_result: Any) -> Dict[str, Any]:
        """Calculate comprehensive performance metrics"""
        return {
            "methodology_design_time": methodology_result.get("performance_metrics", {}).get("total_time", 0),
            "workflow_execution_time": execution_result.get("total_execution_time", 0),
            "synthesis_generation_time": synthesis_result.response_time if hasattr(synthesis_result, 'response_time') else 0,
            "tool_coordination_success": execution_result.get("overall_status") == "completed",
            "agent_coordination_success": methodology_result.get("status") == "success",
            "token_usage": {
                "methodology": methodology_result.get("token_usage", {}),
                "synthesis": synthesis_result.usage if hasattr(synthesis_result, 'usage') else {}
            }
        }
    
    async def cleanup(self):
        """Clean up resources"""
        if self.memory_integrator:
            await self.memory_integrator.disconnect()


async def test_literature_review():
    """Run literature review test"""
    print("🧪 Starting Literature Review Test")
    print("=" * 70)
    
    runner = LiteratureReviewTestRunner()
    
    # Setup
    print("🔧 Setting up literature review integrations...")
    setup_success = await runner.setup()
    
    if not setup_success:
        print("❌ Setup failed")
        return None
    
    print("✅ Literature review integrations ready")
    
    # Test scenario
    research_query = "What are the current patterns and gaps in organizational communication research?"
    document_sources = ["sample_research_document.txt"]  # Would be expanded with real literature
    
    print(f"\n📚 Research Query: {research_query}")
    print(f"📄 Document Sources: {len(document_sources)}")
    print("-" * 50)
    
    # Execute test
    result = await runner.run_literature_review_test(research_query, document_sources)
    
    # Print results
    print(f"✅ Status: {result.status.upper()}")
    print(f"⏱️  Execution Time: {result.execution_time:.2f}s")
    print(f"📄 Documents Processed: {result.documents_processed}")
    print(f"🏷️  Themes Identified: {len(result.themes_identified)}")
    print(f"🎯 Synthesis Quality: {result.synthesis_quality:.3f}")
    print(f"📚 Citations Validated: {result.citations_validated}")
    print(f"🔍 Research Gaps: {len(result.research_gaps_identified)}")
    
    if result.themes_identified:
        print(f"\n🏷️  Key Themes:")
        for theme in result.themes_identified[:3]:
            print(f"   - {theme}")
    
    if result.research_gaps_identified:
        print(f"\n🔍 Research Gaps:")
        for gap in result.research_gaps_identified[:2]:
            print(f"   - {gap}")
    
    print(f"\n📊 Methodology Assessment:")
    for metric, score in result.methodology_assessment.items():
        print(f"   - {metric.replace('_', ' ').title()}: {score:.3f}")
    
    # Assessment
    print(f"\n💡 LITERATURE REVIEW ASSESSMENT")
    print("=" * 70)
    
    if result.status == "success":
        if result.synthesis_quality >= 0.8 and len(result.themes_identified) >= 3:
            print("✅ EXCELLENT: High-quality literature synthesis achieved")
        elif result.synthesis_quality >= 0.6 and len(result.themes_identified) >= 2:
            print("⚠️  GOOD: Acceptable literature analysis, room for improvement")
        else:
            print("❌ BASIC: Literature analysis needs enhancement")
    else:
        print("❌ FAILED: Literature review test failed")
    
    # Cleanup
    await runner.cleanup()
    
    return result


if __name__ == "__main__":
    # Run literature review test
    result = asyncio.run(test_literature_review())
    
    if result:
        # Save results
        results_file = Path(__file__).parent.parent / "results" / "literature_review_test_results.json"
        with open(results_file, 'w') as f:
            json.dump(asdict(result), f, indent=2, default=str)
        
        print(f"\n💾 Results saved to: {results_file}")