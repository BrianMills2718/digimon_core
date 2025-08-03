"""
Simple graph building and analysis agent using KGAS MCP tools.

This agent handles graph construction and analysis using existing
T31 (Entity Builder), T34 (Edge Builder), and T68 (PageRank) tools.
"""

import time
import logging
from typing import List, Dict, Any, Set

from ..base import BaseAgent, Task, Result
from ..mcp_adapter import MCPToolAdapter

logger = logging.getLogger(__name__)


class SimpleGraphAgent(BaseAgent):
    """
    Simple graph building and analysis agent.
    
    Uses existing KGAS tools:
    - T31: Entity Builder (build_entities)
    - T34: Edge Builder (build_edges)
    - T68: PageRank Calculator (calculate_pagerank)
    """
    
    def __init__(self, mcp_adapter: MCPToolAdapter, agent_id: str = None):
        """
        Initialize graph agent.
        
        Args:
            mcp_adapter: MCP tool adapter instance
            agent_id: Optional agent identifier
        """
        super().__init__(agent_id or "graph_agent")
        self.mcp = mcp_adapter
        self.capabilities = [
            "graph_building",
            "entity_building",
            "edge_building",
            "pagerank_calculation",
            "graph_analysis"
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
        Execute graph building or analysis task.
        
        Supported task types:
        - graph_building: Build complete graph (entities + edges + pagerank)
        - entity_building: Just build entity nodes
        - edge_building: Just build edges
        - pagerank_calculation: Just calculate pagerank
        - graph_analysis: Analyze existing graph
        
        Args:
            task: Task to execute
            
        Returns:
            Result of execution
        """
        start_time = time.time()
        
        try:
            self.logger.info(f"Executing task: {task.task_type}")
            
            if task.task_type == "graph_building":
                return await self._build_complete_graph(task, start_time)
            elif task.task_type == "entity_building":
                return await self._build_entities(task, start_time)
            elif task.task_type == "edge_building":
                return await self._build_edges(task, start_time)
            elif task.task_type == "pagerank_calculation":
                return await self._calculate_pagerank(task, start_time)
            elif task.task_type == "graph_analysis":
                return await self._analyze_graph(task, start_time)
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
    
    async def _build_complete_graph(self, task: Task, start_time: float) -> Result:
        """Build complete graph - entities, edges, and calculate PageRank."""
        # Get entities and relationships from context or parameters
        entities = self._get_entities_from_task(task)
        relationships = self._get_relationships_from_task(task)
        
        if not entities:
            return self._create_result(
                success=False,
                error="No entities provided for graph building",
                execution_time=time.time() - start_time,
                task=task
            )
        
        warnings = []
        
        # Step 1: Build entity nodes
        self.logger.info(f"Building {len(entities)} entity nodes")
        entity_result = await self.mcp.call_tool("build_entities", {
            "entities": entities
        })
        
        if not entity_result.success:
            return self._create_result(
                success=False,
                error=f"Entity building failed: {entity_result.error}",
                execution_time=time.time() - start_time,
                task=task
            )
        
        nodes_created = entity_result.data.get("nodes_created", 0)
        entity_map = entity_result.data.get("entity_map", {})
        
        # Step 2: Build edges (if relationships provided)
        edges_created = 0
        if relationships:
            self.logger.info(f"Building edges from {len(relationships)} relationships")
            edge_result = await self.mcp.call_tool("build_edges", {
                "relationships": relationships,
                "entity_map": entity_map
            })
            
            if edge_result.success:
                edges_created = edge_result.data.get("edges_created", 0)
            else:
                warnings.append(f"Edge building failed: {edge_result.error}")
                self.logger.warning(warnings[-1])
        else:
            self.logger.info("No relationships provided, skipping edge building")
        
        # Step 3: Calculate PageRank
        self.logger.info("Calculating PageRank scores")
        pagerank_result = await self.mcp.call_tool("calculate_pagerank", {})
        
        pagerank_scores = {}
        if pagerank_result.success:
            pagerank_scores = pagerank_result.data.get("pagerank_scores", {})
            self.logger.info(f"Calculated PageRank for {len(pagerank_scores)} nodes")
        else:
            warnings.append(f"PageRank calculation failed: {pagerank_result.error}")
            self.logger.warning(warnings[-1])
        
        # Get top entities by PageRank
        top_entities = self._get_top_entities_by_pagerank(pagerank_scores, entity_map, n=10)
        
        # Compile results
        result_data = {
            "nodes_created": nodes_created,
            "edges_created": edges_created,
            "entity_map": entity_map,
            "pagerank_scores": pagerank_scores,
            "top_entities": top_entities,
            "graph_stats": {
                "total_nodes": nodes_created,
                "total_edges": edges_created,
                "total_entities_provided": len(entities),
                "total_relationships_provided": len(relationships)
            }
        }
        
        self.logger.info(f"Graph building complete: {nodes_created} nodes, {edges_created} edges")
        
        return Result(
            success=True,
            data=result_data,
            warnings=warnings if warnings else None,
            execution_time=time.time() - start_time,
            agent_id=self.agent_id,
            task_id=task.task_id,
            metadata={
                "agent_type": self.agent_type,
                "task_type": task.task_type
            }
        )
    
    async def _build_entities(self, task: Task, start_time: float) -> Result:
        """Just build entity nodes."""
        entities = self._get_entities_from_task(task)
        
        if not entities:
            return self._create_result(
                success=False,
                error="No entities provided",
                execution_time=time.time() - start_time,
                task=task
            )
        
        result = await self.mcp.call_tool("build_entities", {
            "entities": entities
        })
        
        if not result.success:
            return self._create_result(
                success=False,
                error=f"Entity building failed: {result.error}",
                execution_time=time.time() - start_time,
                task=task
            )
        
        return self._create_result(
            success=True,
            data=result.data,
            execution_time=time.time() - start_time,
            task=task
        )
    
    async def _build_edges(self, task: Task, start_time: float) -> Result:
        """Just build edges."""
        relationships = self._get_relationships_from_task(task)
        entity_map = task.parameters.get("entity_map", {})
        
        if not entity_map and task.context:
            # Try to get from context
            if "entity_map" in task.context:
                entity_map = task.context["entity_map"]
            elif "graph_result" in task.context:
                graph_result = task.context["graph_result"]
                if isinstance(graph_result, dict):
                    entity_map = graph_result.get("entity_map", {})
        
        if not relationships:
            return self._create_result(
                success=False,
                error="No relationships provided",
                execution_time=time.time() - start_time,
                task=task
            )
        
        result = await self.mcp.call_tool("build_edges", {
            "relationships": relationships,
            "entity_map": entity_map
        })
        
        if not result.success:
            return self._create_result(
                success=False,
                error=f"Edge building failed: {result.error}",
                execution_time=time.time() - start_time,
                task=task
            )
        
        return self._create_result(
            success=True,
            data=result.data,
            execution_time=time.time() - start_time,
            task=task
        )
    
    async def _calculate_pagerank(self, task: Task, start_time: float) -> Result:
        """Calculate PageRank scores."""
        # PageRank tool doesn't need parameters
        result = await self.mcp.call_tool("calculate_pagerank", {})
        
        if not result.success:
            return self._create_result(
                success=False,
                error=f"PageRank calculation failed: {result.error}",
                execution_time=time.time() - start_time,
                task=task
            )
        
        # Add top entities to result
        pagerank_scores = result.data.get("pagerank_scores", {})
        entity_map = task.context.get("entity_map", {}) if task.context else {}
        
        result.data["top_entities"] = self._get_top_entities_by_pagerank(
            pagerank_scores, entity_map, n=10
        )
        
        return self._create_result(
            success=True,
            data=result.data,
            execution_time=time.time() - start_time,
            task=task
        )
    
    async def _analyze_graph(self, task: Task, start_time: float) -> Result:
        """Analyze existing graph."""
        # For now, just calculate PageRank and get stats
        # Future: Add more analysis capabilities
        return await self._calculate_pagerank(task, start_time)
    
    def _get_entities_from_task(self, task: Task) -> List[Dict]:
        """Get entities from task parameters or context."""
        entities = task.parameters.get("entities", [])
        
        if not entities and task.context:
            if "entities" in task.context:
                entities = task.context["entities"]
            elif "analysis_result" in task.context:
                analysis_result = task.context["analysis_result"]
                if isinstance(analysis_result, dict) and "entities" in analysis_result:
                    entities = analysis_result["entities"]
        
        return entities
    
    def _get_relationships_from_task(self, task: Task) -> List[Dict]:
        """Get relationships from task parameters or context."""
        relationships = task.parameters.get("relationships", [])
        
        if not relationships and task.context:
            if "relationships" in task.context:
                relationships = task.context["relationships"]
            elif "analysis_result" in task.context:
                analysis_result = task.context["analysis_result"]
                if isinstance(analysis_result, dict) and "relationships" in analysis_result:
                    relationships = analysis_result["relationships"]
        
        return relationships
    
    def _get_top_entities_by_pagerank(self, pagerank_scores: Dict[str, float],
                                     entity_map: Dict[str, Any], n: int = 10) -> List[Dict]:
        """Get top N entities by PageRank score."""
        # Sort by PageRank score
        sorted_scores = sorted(pagerank_scores.items(), key=lambda x: x[1], reverse=True)
        
        top_entities = []
        for entity_id, score in sorted_scores[:n]:
            entity_info = {
                "entity_id": entity_id,
                "pagerank_score": score
            }
            
            # Try to get entity details from entity_map
            if entity_id in entity_map:
                entity_details = entity_map[entity_id]
                if isinstance(entity_details, dict):
                    entity_info.update({
                        "text": entity_details.get("text", ""),
                        "type": entity_details.get("type", ""),
                        "confidence": entity_details.get("confidence", 0.0)
                    })
            
            top_entities.append(entity_info)
        
        return top_entities