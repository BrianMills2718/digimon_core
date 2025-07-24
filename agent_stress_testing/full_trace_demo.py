#!/usr/bin/env python3
"""
Full Trace Demo - Complete Dual-Agent Workflow

Shows the complete trace of:
1. Original analytical request
2. Research Agent planning with full reasoning
3. Execution Agent tool coordination with all intermediate outputs
4. Tool call trace with actual inputs/outputs
5. Quality assessment and adaptation decisions
6. Final synthesis with complete provenance
"""

import asyncio
import json
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

from working_mcp_client import WorkingMCPClient, MCPToolResult

class FullTraceLogger:
    """Comprehensive execution trace logger"""
    
    def __init__(self):
        self.trace_id = f"trace_{uuid.uuid4().hex[:8]}"
        self.start_time = time.time()
        self.events = []
        self.tool_calls = []
        self.agent_interactions = []
        self.intermediate_outputs = []
    
    def log_event(self, event_type: str, data: Dict[str, Any], source: str = "system"):
        """Log a trace event with timestamp"""
        event = {
            "trace_id": self.trace_id,
            "event_id": f"evt_{len(self.events)+1:03d}",
            "timestamp": datetime.now().isoformat(),
            "elapsed_seconds": time.time() - self.start_time,
            "event_type": event_type,
            "source": source,
            "data": data
        }
        self.events.append(event)
        
        # Pretty print the event
        print(f"\n🔍 TRACE EVENT #{len(self.events):03d} - {event_type.upper()}")
        print(f"   Source: {source}")
        print(f"   Time: {event['elapsed_seconds']:.2f}s")
        if isinstance(data, dict) and len(str(data)) < 200:
            print(f"   Data: {json.dumps(data, indent=6)}")
        else:
            print(f"   Data: {type(data).__name__} ({len(str(data))} chars)")
    
    def log_tool_call(self, tool_name: str, inputs: Dict[str, Any], result: MCPToolResult):
        """Log detailed tool call with inputs and outputs"""
        call_id = f"tool_{len(self.tool_calls)+1:03d}"
        
        tool_call = {
            "call_id": call_id,
            "trace_id": self.trace_id,
            "timestamp": datetime.now().isoformat(),
            "elapsed_seconds": time.time() - self.start_time,
            "tool_name": tool_name,
            "inputs": inputs,
            "execution_time": result.execution_time,
            "status": result.status,
            "output_summary": self._summarize_output(result.output),
            "full_output": result.output,
            "error": result.error_message,
            "metadata": result.metadata or {}
        }
        
        self.tool_calls.append(tool_call)
        
        print(f"\n🛠️  TOOL CALL #{len(self.tool_calls):03d} - {tool_name.upper()}")
        print(f"   Call ID: {call_id}")
        print(f"   Status: {result.status}")
        print(f"   Execution Time: {result.execution_time:.3f}s")
        print(f"   Inputs:")
        for key, value in inputs.items():
            if isinstance(value, str) and len(value) > 100:
                print(f"     {key}: {value[:100]}... ({len(value)} chars)")
            else:
                print(f"     {key}: {value}")
        
        if result.status == "success" and result.output:
            print(f"   Output Summary: {tool_call['output_summary']}")
        elif result.error_message:
            print(f"   Error: {result.error_message}")
    
    def log_agent_interaction(self, agent_type: str, request: str, response: str, thinking: Dict[str, Any] = None):
        """Log agent request/response with reasoning"""
        interaction_id = f"agent_{len(self.agent_interactions)+1:03d}"
        
        interaction = {
            "interaction_id": interaction_id,
            "trace_id": self.trace_id,
            "timestamp": datetime.now().isoformat(),
            "elapsed_seconds": time.time() - self.start_time,
            "agent_type": agent_type,
            "request": request,
            "response": response,
            "thinking": thinking or {},
            "request_length": len(request),
            "response_length": len(response)
        }
        
        self.agent_interactions.append(interaction)
        
        print(f"\n🤖 AGENT INTERACTION #{len(self.agent_interactions):03d} - {agent_type.upper()} AGENT")
        print(f"   Interaction ID: {interaction_id}")
        print(f"   Request Length: {len(request)} chars")
        print(f"   Response Length: {len(response)} chars")
        
        if thinking:
            print(f"   Agent Reasoning:")
            for key, value in thinking.items():
                print(f"     {key}: {value}")
    
    def _summarize_output(self, output: Any) -> str:
        """Create summary of tool output"""
        if not output:
            return "No output"
        
        if isinstance(output, dict):
            summary_parts = []
            
            # Common output patterns
            if 'entity_count' in output:
                summary_parts.append(f"{output['entity_count']} entities")
            if 'relationship_count' in output:
                summary_parts.append(f"{output['relationship_count']} relationships")
            if 'chunks' in output:
                summary_parts.append(f"{len(output['chunks'])} chunks")
            if 'processing_time' in output:
                summary_parts.append(f"{output['processing_time']:.2f}s processing")
            
            if summary_parts:
                return ", ".join(summary_parts)
            else:
                return f"Dict with {len(output)} keys"
        
        return f"{type(output).__name__}({len(str(output))} chars)"
    
    def save_full_trace(self, filename: str = None):
        """Save complete trace to file"""
        if not filename:
            filename = f"trace_output_{self.trace_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        full_trace = {
            "trace_metadata": {
                "trace_id": self.trace_id,
                "start_time": self.start_time,
                "total_duration": time.time() - self.start_time,
                "total_events": len(self.events),
                "total_tool_calls": len(self.tool_calls),
                "total_agent_interactions": len(self.agent_interactions)
            },
            "events": self.events,
            "tool_calls": self.tool_calls,
            "agent_interactions": self.agent_interactions,
            "intermediate_outputs": self.intermediate_outputs
        }
        
        with open(filename, 'w') as f:
            json.dump(full_trace, f, indent=2, default=str)
        
        print(f"\n📄 FULL TRACE SAVED: {filename}")
        return filename

class MockResearchAgent:
    """Mock research agent that shows realistic planning and reasoning"""
    
    def __init__(self, trace_logger: FullTraceLogger):
        self.trace_logger = trace_logger
        self.agent_type = "research"
    
    async def create_analytical_plan(self, objective: str, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create detailed analytical plan with reasoning trace"""
        
        request = f"""
        ANALYTICAL PLANNING REQUEST:
        
        Objective: {objective}
        
        Documents to analyze:
        {json.dumps([{k: v for k, v in doc.items() if k != 'content'} for doc in documents], indent=2)}
        
        Document content previews:
        {chr(10).join([f"- {doc['id']}: {doc['content'][:200]}..." for doc in documents])}
        
        Please create a detailed analytical workflow plan.
        """
        
        # Simulate research agent reasoning
        thinking = {
            "document_analysis": f"Analyzing {len(documents)} documents with total {sum(len(d['content']) for d in documents)} characters",
            "objective_breakdown": "Need to extract entities, relationships, and analyze patterns",
            "tool_selection": "Will use document_analyzer for comprehensive processing",
            "quality_thresholds": "Expecting at least 5 entities per document for good quality",
            "adaptation_strategies": ["lower_confidence_thresholds", "add_preprocessing", "alternative_approaches"]
        }
        
        response = {
            "plan_id": f"plan_{uuid.uuid4().hex[:8]}",
            "objective": objective,
            "strategy": "comprehensive_document_analysis",
            "steps": [
                {
                    "step_id": "step_001",
                    "name": "Document Analysis",
                    "tool": "analyze_document", 
                    "description": "Extract entities and relationships from each document",
                    "quality_threshold": 0.6,
                    "expected_outputs": ["entities", "relationships", "processing_metrics"]
                },
                {
                    "step_id": "step_002", 
                    "name": "Quality Assessment",
                    "tool": "quality_evaluator",
                    "description": "Assess extraction quality and determine if adaptation needed",
                    "quality_threshold": 0.7,
                    "expected_outputs": ["quality_score", "adaptation_recommendations"]
                },
                {
                    "step_id": "step_003",
                    "name": "Results Synthesis", 
                    "tool": "result_synthesizer",
                    "description": "Combine and analyze results across all documents",
                    "quality_threshold": 0.8,
                    "expected_outputs": ["final_analysis", "insights", "recommendations"]
                }
            ],
            "quality_thresholds": {
                "min_entities_per_doc": 3,
                "min_relationships_per_doc": 1,
                "min_overall_quality": 0.7
            },
            "adaptation_strategies": [
                "lower_confidence_thresholds",
                "add_preprocessing_steps", 
                "try_alternative_approaches",
                "increase_context_window"
            ],
            "success_criteria": {
                "entities_extracted": True,
                "relationships_found": True,
                "processing_completed": True,
                "quality_acceptable": True
            }
        }
        
        self.trace_logger.log_agent_interaction(
            agent_type=self.agent_type,
            request=request,
            response=json.dumps(response, indent=2),
            thinking=thinking
        )
        
        return response
    
    async def assess_and_adapt(self, execution_results: Dict[str, Any], quality_scores: List[float]) -> Dict[str, Any]:
        """Assess execution results and recommend adaptations"""
        
        request = f"""
        ADAPTATION ASSESSMENT REQUEST:
        
        Execution Results Summary:
        - Documents Processed: {execution_results.get('documents_processed', 0)}
        - Total Entities: {execution_results.get('total_entities', 0)}
        - Total Relationships: {execution_results.get('total_relationships', 0)}
        - Quality Scores: {quality_scores}
        - Average Quality: {sum(quality_scores)/len(quality_scores) if quality_scores else 0:.2f}
        
        Please assess if adaptation is needed and recommend specific changes.
        """
        
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        adaptation_needed = avg_quality < 0.6
        
        thinking = {
            "quality_assessment": f"Average quality {avg_quality:.2f}, threshold 0.6",
            "adaptation_needed": adaptation_needed,
            "trend_analysis": "Declining" if len(quality_scores) >= 2 and quality_scores[-1] < quality_scores[-2] else "Stable",
            "recommended_action": "adapt_thresholds" if adaptation_needed else "continue_current_approach"
        }
        
        response = {
            "assessment_id": f"assess_{uuid.uuid4().hex[:8]}",
            "adaptation_needed": adaptation_needed,
            "quality_analysis": {
                "average_quality": avg_quality,
                "quality_trend": "declining" if len(quality_scores) >= 2 and quality_scores[-1] < quality_scores[-2] else "stable",
                "meets_threshold": avg_quality >= 0.6
            },
            "adaptations": [
                {
                    "type": "lower_confidence_threshold",
                    "description": "Reduce entity confidence threshold from 0.8 to 0.6",
                    "expected_improvement": 0.2,
                    "rationale": "May capture more entities that were filtered out"
                },
                {
                    "type": "add_preprocessing",
                    "description": "Add text normalization and entity hint preprocessing",
                    "expected_improvement": 0.15,
                    "rationale": "Better text quality should improve entity recognition"
                }
            ] if adaptation_needed else [],
            "continue_execution": True
        }
        
        self.trace_logger.log_agent_interaction(
            agent_type=self.agent_type,
            request=request,
            response=json.dumps(response, indent=2),
            thinking=thinking
        )
        
        return response
    
    async def synthesize_results(self, all_results: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize final results with insights"""
        
        request = f"""
        RESULTS SYNTHESIS REQUEST:
        
        Complete execution results:
        {json.dumps(all_results, indent=2, default=str)}
        
        Please provide comprehensive synthesis and insights.
        """
        
        thinking = {
            "result_analysis": f"Processed {all_results.get('documents_processed', 0)} documents",
            "pattern_recognition": "Looking for cross-document patterns and insights",
            "quality_evaluation": f"Overall success rate: {all_results.get('success_rate', 0):.2f}",
            "insight_generation": "Identifying key findings and recommendations"
        }
        
        response = {
            "synthesis_id": f"synth_{uuid.uuid4().hex[:8]}",
            "summary": {
                "objective_completed": True,
                "documents_analyzed": all_results.get('documents_processed', 0),
                "total_entities": all_results.get('total_entities', 0),
                "total_relationships": all_results.get('total_relationships', 0),
                "processing_time": all_results.get('total_processing_time', 0),
                "adaptations_made": len(all_results.get('adaptations', []))
            },
            "key_insights": [
                "Document processing pipeline executed successfully",
                "Entity extraction working but may need confidence threshold tuning",
                "System demonstrates good performance and reliability",
                "Adaptive workflow framework is operational"
            ],
            "recommendations": [
                "Fine-tune spaCy NER confidence thresholds for better entity capture",
                "Consider adding domain-specific entity types",
                "Implement caching for repeated document processing",
                "Add batch processing capabilities for large document sets"
            ],
            "quality_assessment": {
                "technical_execution": "Excellent",
                "result_completeness": "Good",
                "processing_efficiency": "Very Good",
                "overall_rating": "Success"
            }
        }
        
        self.trace_logger.log_agent_interaction(
            agent_type=self.agent_type,
            request=request,
            response=json.dumps(response, indent=2),
            thinking=thinking
        )
        
        return response

class MockExecutionAgent:
    """Mock execution agent that coordinates actual tool calls"""
    
    def __init__(self, trace_logger: FullTraceLogger, mcp_client: WorkingMCPClient):
        self.trace_logger = trace_logger
        self.mcp_client = mcp_client
        self.agent_type = "execution"
    
    async def execute_plan_step(self, step: Dict[str, Any], document: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a plan step with detailed tracing"""
        
        request = f"""
        EXECUTION REQUEST:
        
        Step: {step['name']} ({step['step_id']})
        Tool: {step['tool']}
        Description: {step['description']}
        Quality Threshold: {step['quality_threshold']}
        
        Document: {document['id']}
        Content Length: {len(document['content'])} characters
        
        Execute this step and report detailed results.
        """
        
        thinking = {
            "step_analysis": f"Executing {step['name']} using {step['tool']}",
            "document_assessment": f"Processing {len(document['content'])} characters of text",
            "expected_challenge": "Entity extraction may need confidence tuning",
            "monitoring_focus": "Watching for entity count and processing time"
        }
        
        # Execute the actual tool
        if step['tool'] == 'analyze_document':
            tool_result = await self.mcp_client.execute_tool(
                "analyze_document",
                document=document,
                analysis_modes=["entities", "relationships"]
            )
            
            self.trace_logger.log_tool_call(
                tool_name="analyze_document",
                inputs={
                    "document_id": document['id'],
                    "content_length": len(document['content']),
                    "analysis_modes": ["entities", "relationships"]
                },
                result=tool_result
            )
            
            # Calculate quality score
            quality_score = 0.5  # Base score
            if tool_result.status == "success" and tool_result.output:
                entity_count = tool_result.output.get('entity_count', 0)
                relationship_count = tool_result.output.get('relationship_count', 0)
                
                if entity_count > 0:
                    quality_score += 0.3
                if relationship_count > 0:
                    quality_score += 0.2
                    
            execution_result = {
                "step_id": step['step_id'],
                "tool_used": step['tool'],
                "status": tool_result.status,
                "quality_score": quality_score,
                "meets_threshold": quality_score >= step['quality_threshold'],
                "execution_time": tool_result.execution_time,
                "results": tool_result.output,
                "issues": [tool_result.error_message] if tool_result.error_message else [],
                "recommendations": [
                    "Consider lowering confidence threshold" if entity_count == 0 else "Entity extraction working",
                    f"Processing time {tool_result.execution_time:.2f}s is acceptable"
                ]
            }
        
        else:
            # Handle other step types
            execution_result = {
                "step_id": step['step_id'],
                "tool_used": step['tool'],
                "status": "completed",
                "quality_score": 0.8,
                "meets_threshold": True,
                "execution_time": 0.1,
                "results": {"simulated": True},
                "issues": [],
                "recommendations": ["Step completed successfully"]
            }
        
        response = json.dumps(execution_result, indent=2)
        
        self.trace_logger.log_agent_interaction(
            agent_type=self.agent_type,
            request=request,
            response=response,
            thinking=thinking
        )
        
        return execution_result

async def run_full_trace_demo():
    """Run complete dual-agent workflow with full tracing"""
    
    # Initialize tracing
    trace = FullTraceLogger()
    
    print("🚀 FULL TRACE DEMO - Dual-Agent Analytical Workflow")
    print("=" * 80)
    print(f"📋 Trace ID: {trace.trace_id}")
    print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Log initial request
    original_request = {
        "request_id": f"req_{uuid.uuid4().hex[:8]}",
        "timestamp": datetime.now().isoformat(),
        "user_objective": "Analyze corporate leadership and technology partnerships in tech industry documents",
        "analysis_type": "comprehensive_entity_relationship_analysis",
        "expected_outputs": ["leadership_networks", "partnership_patterns", "corporate_relationships"],
        "quality_requirements": {
            "min_entities_per_document": 5,
            "min_relationships_per_document": 2,
            "overall_confidence_threshold": 0.7
        }
    }
    
    trace.log_event(
        event_type="user_request_received",
        data=original_request,
        source="user"
    )
    
    # Define test documents with rich entity content
    documents = [
        {
            "id": "corp_leadership_001",
            "title": "Technology Leadership Analysis",
            "content": """
            Apple Inc. CEO Tim Cook announced a strategic partnership with Microsoft Corporation during 
            a meeting in Cupertino, California. The partnership will focus on enterprise software 
            integration between Apple's iOS platform and Microsoft's Office 365 suite.
            
            Microsoft CEO Satya Nadella expressed enthusiasm about the collaboration, noting that 
            this builds on previous partnerships between the two companies. The agreement was 
            negotiated by Apple's VP of Enterprise Sales, John Smith, and Microsoft's Director 
            of Strategic Partnerships, Sarah Johnson.
            
            This partnership follows similar collaborations between Google LLC and IBM Corporation, 
            where Google CEO Sundar Pichai and IBM CEO Arvind Krishna announced joint AI initiatives. 
            These technology alliances demonstrate the evolving competitive landscape in enterprise software.
            """,
            "metadata": {
                "document_type": "corporate_announcement",
                "publication_date": "2024-01-15",
                "source": "TechNews Weekly"
            }
        },
        {
            "id": "partnership_analysis_002", 
            "title": "Strategic Technology Alliances",
            "content": """
            Amazon Web Services (AWS) has formed a significant partnership with Oracle Corporation 
            to integrate Oracle Database with AWS cloud infrastructure. AWS CEO Andy Jassy and 
            Oracle CEO Safra Catz signed the agreement at Amazon's headquarters in Seattle, Washington.
            
            The partnership includes technical collaboration between Amazon's cloud platform team, 
            led by VP of Engineering Mike Davis, and Oracle's cloud infrastructure division, 
            headed by SVP of Product Development Lisa Chen. This alliance positions both companies 
            to compete more effectively against Microsoft Azure and Google Cloud Platform.
            
            Meanwhile, IBM has announced a joint venture with Red Hat, building on IBM's $34 billion 
            acquisition of the open-source software company. Red Hat CEO Paul Cormier will lead 
            the hybrid cloud initiatives, working closely with IBM's VP of Cloud Strategy, David Martinez.
            """,
            "metadata": {
                "document_type": "industry_analysis",
                "publication_date": "2024-01-20", 
                "source": "Enterprise Tech Report"
            }
        }
    ]
    
    trace.log_event(
        event_type="documents_loaded",
        data={
            "document_count": len(documents),
            "total_content_length": sum(len(d['content']) for d in documents),
            "document_ids": [d['id'] for d in documents]
        },
        source="system"
    )
    
    # Initialize components
    mcp_client = WorkingMCPClient()
    research_agent = MockResearchAgent(trace)
    execution_agent = MockExecutionAgent(trace, mcp_client)
    
    # Connect to real tools
    trace.log_event("mcp_connection_attempt", {"mcp_server": "kgas_mcp_server"}, "system")
    
    connected = await mcp_client.connect()
    if not connected:
        trace.log_event("mcp_connection_failed", {"error": "Cannot connect to MCP server"}, "system")
        return
    
    trace.log_event("mcp_connection_success", {"available_tools": await mcp_client.get_available_tools()}, "system")
    
    try:
        # Phase 1: Research Agent creates analytical plan
        print(f"\n{'='*25} PHASE 1: RESEARCH PLANNING {'='*25}")
        
        trace.log_event("research_planning_start", {"objective": original_request["user_objective"]}, "research_agent")
        
        analytical_plan = await research_agent.create_analytical_plan(
            objective=original_request["user_objective"],
            documents=documents
        )
        
        trace.log_event("research_planning_complete", analytical_plan, "research_agent")
        
        # Phase 2: Execution Agent executes the plan
        print(f"\n{'='*25} PHASE 2: PLAN EXECUTION {'='*25}")
        
        trace.log_event("execution_start", {"plan_id": analytical_plan["plan_id"]}, "execution_agent")
        
        execution_results = {
            "plan_id": analytical_plan["plan_id"],
            "documents_processed": 0,
            "total_entities": 0,
            "total_relationships": 0,
            "step_results": [],
            "quality_scores": [],
            "processing_times": []
        }
        
        # Execute plan for each document
        for doc_idx, document in enumerate(documents):
            trace.log_event(
                "document_processing_start",
                {"document_id": document["id"], "document_index": doc_idx + 1},
                "execution_agent"
            )
            
            # Execute main analysis step
            main_step = analytical_plan["steps"][0]  # Document Analysis step
            step_result = await execution_agent.execute_plan_step(main_step, document)
            
            execution_results["step_results"].append(step_result)
            execution_results["quality_scores"].append(step_result["quality_score"])
            execution_results["processing_times"].append(step_result["execution_time"])
            execution_results["documents_processed"] += 1
            
            if step_result["status"] == "success" and step_result["results"]:
                results = step_result["results"]
                execution_results["total_entities"] += results.get("entity_count", 0)
                execution_results["total_relationships"] += results.get("relationship_count", 0)
            
            trace.log_event(
                "document_processing_complete",
                {
                    "document_id": document["id"],
                    "quality_score": step_result["quality_score"],
                    "entities_found": results.get("entity_count", 0) if step_result.get("results") else 0,
                    "relationships_found": results.get("relationship_count", 0) if step_result.get("results") else 0
                },
                "execution_agent"
            )
        
        trace.log_event("execution_complete", execution_results, "execution_agent")
        
        # Phase 3: Research Agent assesses results and adapts if needed
        print(f"\n{'='*25} PHASE 3: QUALITY ASSESSMENT {'='*25}")
        
        trace.log_event("quality_assessment_start", {"quality_scores": execution_results["quality_scores"]}, "research_agent")
        
        adaptation_analysis = await research_agent.assess_and_adapt(
            execution_results=execution_results,
            quality_scores=execution_results["quality_scores"]
        )
        
        trace.log_event("quality_assessment_complete", adaptation_analysis, "research_agent")
        
        # Phase 4: Research Agent synthesizes final results
        print(f"\n{'='*25} PHASE 4: RESULTS SYNTHESIS {'='*25}")
        
        final_results = {
            **execution_results,
            "adaptation_analysis": adaptation_analysis,
            "total_processing_time": sum(execution_results["processing_times"]),
            "average_quality": sum(execution_results["quality_scores"]) / len(execution_results["quality_scores"]),
            "success_rate": len([r for r in execution_results["step_results"] if r["status"] == "success"]) / len(execution_results["step_results"])
        }
        
        trace.log_event("synthesis_start", {"final_results_summary": {k: v for k, v in final_results.items() if k != "step_results"}}, "research_agent")
        
        synthesis = await research_agent.synthesize_results(final_results)
        
        trace.log_event("synthesis_complete", synthesis, "research_agent")
        
        # Phase 5: Complete workflow summary
        print(f"\n{'='*25} PHASE 5: WORKFLOW COMPLETE {'='*25}")
        
        workflow_summary = {
            "workflow_id": f"workflow_{trace.trace_id}",
            "original_request": original_request,
            "analytical_plan": analytical_plan,
            "execution_results": execution_results,
            "adaptation_analysis": adaptation_analysis,
            "synthesis": synthesis,
            "performance_metrics": {
                "total_duration": time.time() - trace.start_time,
                "documents_processed": execution_results["documents_processed"],
                "total_entities": execution_results["total_entities"],
                "total_relationships": execution_results["total_relationships"],
                "average_quality": final_results["average_quality"],
                "success_rate": final_results["success_rate"],
                "total_tool_calls": len(trace.tool_calls),
                "total_agent_interactions": len(trace.agent_interactions)
            }
        }
        
        trace.log_event("workflow_complete", workflow_summary, "system")
        
        # Print final summary
        print(f"\n📊 WORKFLOW EXECUTION SUMMARY")
        print(f"   Workflow ID: {workflow_summary['workflow_id']}")
        print(f"   Total Duration: {workflow_summary['performance_metrics']['total_duration']:.2f}s")
        print(f"   Documents Processed: {workflow_summary['performance_metrics']['documents_processed']}")
        print(f"   Entities Extracted: {workflow_summary['performance_metrics']['total_entities']}")
        print(f"   Relationships Found: {workflow_summary['performance_metrics']['total_relationships']}")
        print(f"   Average Quality: {workflow_summary['performance_metrics']['average_quality']:.2f}")
        print(f"   Success Rate: {workflow_summary['performance_metrics']['success_rate']:.2f}")
        print(f"   Tool Calls Made: {workflow_summary['performance_metrics']['total_tool_calls']}")
        print(f"   Agent Interactions: {workflow_summary['performance_metrics']['total_agent_interactions']}")
        
    except Exception as e:
        trace.log_event("workflow_error", {"error": str(e), "error_type": type(e).__name__}, "system")
        raise
    
    finally:
        await mcp_client.disconnect()
        
        # Save complete trace
        trace_file = trace.save_full_trace()
        
        print(f"\n🎯 FULL TRACE DEMONSTRATION COMPLETE")
        print(f"📁 Complete trace saved to: {trace_file}")
        print(f"🔍 Trace contains {len(trace.events)} events, {len(trace.tool_calls)} tool calls, {len(trace.agent_interactions)} agent interactions")
        
        return trace_file

if __name__ == "__main__":
    asyncio.run(run_full_trace_demo())