"""
Simple insight generation agent using KGAS MCP tools.

This agent handles graph querying and insight generation using existing
T49 (Multi-hop Query) tool.
"""

import time
import logging
from typing import List, Dict, Any, Optional

from ..base import BaseAgent, Task, Result
from ..mcp_adapter import MCPToolAdapter

logger = logging.getLogger(__name__)


class SimpleInsightAgent(BaseAgent):
    """
    Simple insight generation agent using graph queries.
    
    Uses existing KGAS tools:
    - T49: Multi-hop Query (query_graph)
    """
    
    def __init__(self, mcp_adapter: MCPToolAdapter, agent_id: str = None):
        """
        Initialize insight agent.
        
        Args:
            mcp_adapter: MCP tool adapter instance
            agent_id: Optional agent identifier
        """
        super().__init__(agent_id or "insight_agent")
        self.mcp = mcp_adapter
        self.capabilities = [
            "insight_generation",
            "graph_querying",
            "analysis_summary",
            "question_answering"
        ]
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def can_handle(self, task_type: str) -> bool:
        """Check if agent can handle task type."""
        return task_type in self.capabilities
    
    def get_capabilities(self) -> List[str]:
        """Get list of capabilities."""
        return self.capabilities.copy()
    
    async def execute(self, task: Task) -> Result:
        """
        Execute insight generation task.
        
        Supported task types:
        - insight_generation: Generate insights from graph
        - graph_querying: Execute specific graph queries
        - analysis_summary: Summarize analysis results
        - question_answering: Answer questions using graph
        
        Args:
            task: Task to execute
            
        Returns:
            Result of execution
        """
        start_time = time.time()
        
        try:
            self.logger.info(f"Executing task: {task.task_type}")
            
            if task.task_type in self.capabilities:
                return await self._generate_insights(task, start_time)
            else:
                return self._create_result(
                    success=False,
                    error=f"Unknown task type: {task.task_type}",
                    execution_time=time.time() - start_time,
                    task=task
                )
                
        except Exception as e:
            self.logger.error(f"Task execution failed: {e}")
            return self._create_result(
                success=False,
                error=f"Task execution failed: {str(e)}",
                execution_time=time.time() - start_time,
                task=task
            )
    
    async def _generate_insights(self, task: Task, start_time: float) -> Result:
        """Generate insights based on task type and context."""
        # Get query from parameters or build from context
        query = self._build_query(task)
        
        if not query:
            return self._create_result(
                success=False,
                error="No query provided or could not build query from context",
                execution_time=time.time() - start_time,
                task=task
            )
        
        # Get max hops (depth of graph traversal)
        max_hops = task.parameters.get("max_hops", 3)
        
        # Get top entities from context if available
        top_entities = self._get_top_entities(task)
        
        # Execute multi-hop query
        self.logger.info(f"Executing graph query: '{query}' with max_hops={max_hops}")
        
        query_result = await self.mcp.call_tool("query_graph", {
            "query": query,
            "max_hops": max_hops
        })
        
        if not query_result.success:
            return self._create_result(
                success=False,
                error=f"Graph query failed: {query_result.error}",
                execution_time=time.time() - start_time,
                task=task
            )
        
        # Process query results into insights
        insights = self._process_query_results(query_result.data, task, top_entities)
        
        # Add summary based on task type
        if task.task_type == "analysis_summary":
            insights["summary"] = self._generate_analysis_summary(task, insights)
        
        # Compile final result
        result_data = {
            "query": query,
            "insights": insights,
            "query_results": query_result.data,
            "context_used": {
                "top_entities": len(top_entities) if top_entities else 0,
                "max_hops": max_hops
            }
        }
        
        self.logger.info(f"Generated insights with {len(insights.get('key_findings', []))} key findings")
        
        return Result(
            success=True,
            data=result_data,
            execution_time=time.time() - start_time,
            agent_id=self.agent_id,
            task_id=task.task_id,
            metadata={
                "agent_type": self.agent_type,
                "task_type": task.task_type,
                "query_executed": query
            }
        )
    
    def _build_query(self, task: Task) -> Optional[str]:
        """Build query from task parameters or context."""
        # Check for explicit query in parameters
        query = task.parameters.get("query", "")
        
        if query:
            return query
        
        # Try to build query based on task type and context
        if task.task_type == "insight_generation":
            # Use original request from context
            if task.context and "original_request" in task.context:
                return task.context["original_request"]
            else:
                return "What are the key insights from this analysis?"
        
        elif task.task_type == "analysis_summary":
            return "Summarize the main findings and relationships"
        
        elif task.task_type == "question_answering":
            # Use question from parameters or context
            question = task.parameters.get("question", "")
            if not question and task.context:
                question = task.context.get("question", "")
            return question
        
        elif task.task_type == "graph_querying":
            # Must have explicit query for this type
            return None
        
        # Default query
        return "What are the most important entities and relationships?"
    
    def _get_top_entities(self, task: Task) -> List[Dict]:
        """Get top entities from context."""
        top_entities = []
        
        if task.context:
            # Direct top entities
            if "top_entities" in task.context:
                top_entities = task.context["top_entities"]
            # From graph result
            elif "graph_result" in task.context:
                graph_result = task.context["graph_result"]
                if isinstance(graph_result, dict) and "top_entities" in graph_result:
                    top_entities = graph_result["top_entities"]
        
        return top_entities
    
    def _process_query_results(self, query_data: Dict, task: Task, 
                             top_entities: List[Dict]) -> Dict[str, Any]:
        """Process query results into structured insights."""
        insights = {
            "key_findings": [],
            "entity_mentions": {},
            "relationship_patterns": [],
            "recommendations": []
        }
        
        # Extract paths and results
        paths = query_data.get("paths", [])
        results = query_data.get("results", [])
        
        # Process paths for patterns
        if paths:
            insights["total_paths_found"] = len(paths)
            
            # Find common patterns in paths
            entity_counts = {}
            relationship_types = {}
            
            for path in paths:
                # Count entity occurrences
                for node in path.get("nodes", []):
                    entity_id = node.get("id", "")
                    entity_text = node.get("properties", {}).get("text", "Unknown")
                    entity_counts[entity_text] = entity_counts.get(entity_text, 0) + 1
                
                # Count relationship types
                for rel in path.get("relationships", []):
                    rel_type = rel.get("type", "UNKNOWN")
                    relationship_types[rel_type] = relationship_types.get(rel_type, 0) + 1
            
            # Add most mentioned entities
            top_mentioned = sorted(entity_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            for entity, count in top_mentioned:
                insights["key_findings"].append(
                    f"'{entity}' appears in {count} graph paths"
                )
            
            insights["entity_mentions"] = dict(top_mentioned)
            
            # Add relationship patterns
            for rel_type, count in sorted(relationship_types.items(), 
                                         key=lambda x: x[1], reverse=True):
                insights["relationship_patterns"].append({
                    "type": rel_type,
                    "occurrences": count
                })
        
        # Add insights about top entities if available
        if top_entities:
            insights["key_findings"].append(
                f"Top {len(top_entities)} entities by importance identified"
            )
            
            # Highlight top 3 entities
            for i, entity in enumerate(top_entities[:3]):
                entity_text = entity.get("text", "Unknown")
                score = entity.get("pagerank_score", 0.0)
                insights["key_findings"].append(
                    f"#{i+1} most important: '{entity_text}' (score: {score:.4f})"
                )
        
        # Add task-specific insights
        if task.task_type == "question_answering":
            insights["answer_confidence"] = len(paths) > 0
            if paths:
                insights["recommendations"].append(
                    "Multiple relevant paths found - answer has supporting evidence"
                )
            else:
                insights["recommendations"].append(
                    "No direct paths found - answer may require inference"
                )
        
        return insights
    
    def _generate_analysis_summary(self, task: Task, insights: Dict) -> str:
        """Generate a text summary of the analysis."""
        summary_parts = []
        
        # Start with overview
        if "total_paths_found" in insights:
            summary_parts.append(
                f"Graph analysis found {insights['total_paths_found']} relevant paths."
            )
        
        # Add key findings
        if insights.get("key_findings"):
            summary_parts.append(
                f"Key findings: {'; '.join(insights['key_findings'][:3])}"
            )
        
        # Add entity information
        if insights.get("entity_mentions"):
            total_entities = len(insights["entity_mentions"])
            summary_parts.append(
                f"Identified {total_entities} key entities in the analysis."
            )
        
        # Add relationship patterns
        if insights.get("relationship_patterns"):
            total_patterns = len(insights["relationship_patterns"])
            summary_parts.append(
                f"Found {total_patterns} types of relationships in the graph."
            )
        
        # Join into paragraph
        return " ".join(summary_parts) if summary_parts else "No significant patterns found in the analysis."