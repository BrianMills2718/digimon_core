"""T54: Graph Visualization Tool - Main Interface

Streamlined graph visualization tool using decomposed components.
Reduced from 1,252 lines to focused interface.
"""

import time
import psutil
from typing import Dict, List, Optional, Any
from datetime import datetime

# Import base tool
from src.tools.base_tool import BaseTool, ToolRequest, ToolResult, ToolContract

# Import core services
try:
    from src.core.service_manager import ServiceManager
    from src.core.confidence_score import ConfidenceScore
except ImportError:
    from core.service_manager import ServiceManager
    from core.confidence_score import ConfidenceScore

# Handle plotly import with graceful fallback
try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    # Fallback for when plotly is not installed
    PLOTLY_AVAILABLE = False
    class MockPlotly:
        def __getattr__(self, name):
            def mock_method(*args, **kwargs):
                return {"error": "Plotly not installed. Install with: pip install plotly>=5.15.0"}
            return mock_method
    go = MockPlotly()
    px = MockPlotly()

# Import decomposed visualization components
try:
    from .visualization import (
        LayoutType,
        ColorScheme,
        VisualizationConfig,
        VisualizationResult,
        VisualizationDataLoader,
        LayoutCalculator,
        AttributeCalculator,
        PlotlyRenderer
    )
except ImportError:
    # Create mock classes for when visualization module is not available
    class LayoutType:
        SPRING = "spring"
        CIRCULAR = "circular"
    
    class ColorScheme:
        ENTITY_TYPE = "entity_type"
        CONFIDENCE = "confidence"
    
    VisualizationConfig = dict
    VisualizationResult = dict
    VisualizationDataLoader = object
    LayoutCalculator = object
    AttributeCalculator = object
    PlotlyRenderer = object

from src.core.logging_config import get_logger

logger = get_logger(__name__)


class GraphVisualizationTool(BaseTool):
    """T54: Advanced Graph Visualization Tool
    
    Implements comprehensive graph visualization using decomposed components:
    - VisualizationDataLoader: Load graph data from various sources
    - LayoutCalculator: Calculate graph layouts using multiple algorithms
    - AttributeCalculator: Calculate node/edge attributes for styling
    - PlotlyRenderer: Create interactive Plotly visualizations
    
    Reduced from 1,252 lines to focused tool interface.
    """
    
    def __init__(self, service_manager: ServiceManager = None):
        """Initialize visualization tool with decomposed components"""
        if service_manager is None:
            service_manager = ServiceManager()
        
        super().__init__(service_manager)
        self.tool_id = "T54_GRAPH_VISUALIZATION"
        self.name = "Advanced Graph Visualization"
        self.category = "advanced_analytics"
        self.version = "2.0.0"
        
        # Initialize decomposed components
        self.data_loader = VisualizationDataLoader(service_manager)
        self.layout_calculator = LayoutCalculator()
        self.attribute_calculator = AttributeCalculator()
        self.plotly_renderer = PlotlyRenderer()
        
        # Performance tracking
        self.execution_count = 0
        
        logger.info(f"Initialized {self.tool_id} v{self.version} with decomposed components")
    
    def get_contract(self) -> ToolContract:
        """Return tool contract specification"""
        return ToolContract(
            tool_id=self.tool_id,
            name=self.name,
            description="Advanced graph visualization with interactive layouts and multiple output formats",
            input_schema={
                "type": "object",
                "properties": {
                    "graph_source": {
                        "type": "string",
                        "enum": ["neo4j", "networkx", "edge_list", "adjacency_matrix"],
                        "description": "Source of graph data"
                    },
                    "graph_data": {
                        "type": "object",
                        "description": "Graph data when not using Neo4j"
                    },
                    "layout": {
                        "type": "string",
                        "enum": ["spring", "circular", "kamada_kawai", "fruchterman_reingold", 
                               "spectral", "planar", "shell", "spiral", "random"],
                        "description": "Graph layout algorithm"
                    },
                    "color_scheme": {
                        "type": "string",
                        "enum": ["entity_type", "confidence", "centrality", "community", 
                               "degree", "pagerank", "custom"],
                        "description": "Node coloring scheme"
                    },
                    "node_size_metric": {
                        "type": "string",
                        "enum": ["degree", "betweenness", "closeness", "eigenvector", 
                               "pagerank", "confidence"],
                        "description": "Metric for node sizing"
                    },
                    "edge_width_metric": {
                        "type": "string",
                        "enum": ["weight", "confidence", "betweenness"],
                        "description": "Metric for edge width"
                    },
                    "max_nodes": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 10000,
                        "description": "Maximum number of nodes to visualize"
                    },
                    "max_edges": {
                        "type": "integer", 
                        "minimum": 1,
                        "maximum": 50000,
                        "description": "Maximum number of edges to visualize"
                    },
                    "show_labels": {
                        "type": "boolean",
                        "description": "Show node labels"
                    },
                    "interactive": {
                        "type": "boolean",
                        "description": "Create interactive visualization"
                    },
                    "output_format": {
                        "type": "string",
                        "enum": ["html", "png", "pdf", "svg", "json", "all"],
                        "description": "Output format for visualization"
                    },
                    "filter_criteria": {
                        "type": "object",
                        "description": "Criteria for filtering graph data"
                    }
                },
                "required": ["graph_source"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "visualization_data": {"type": "object"},
                    "layout_info": {"type": "object"},
                    "statistics": {"type": "object"},
                    "file_paths": {"type": "array"},
                    "metadata": {"type": "object"}
                },
                "required": ["visualization_data", "statistics", "metadata"]
            }
        )
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute graph visualization with decomposed components"""
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss
        
        try:
            # Validate input
            validation_result = self._validate_input(request.input_data)
            if not validation_result["valid"]:
                return self._create_error_result(
                    f"Input validation failed: {validation_result['errors']}",
                    execution_time=time.time() - start_time
                )
            
            # Extract parameters with defaults
            graph_source = request.input_data["graph_source"]
            graph_data = request.input_data.get("graph_data")
            layout_type = LayoutType(request.input_data.get("layout", "spring"))
            color_scheme = ColorScheme(request.input_data.get("color_scheme", "entity_type"))
            node_size_metric = request.input_data.get("node_size_metric", "degree")
            edge_width_metric = request.input_data.get("edge_width_metric", "weight")
            max_nodes = request.input_data.get("max_nodes", 1000)
            max_edges = request.input_data.get("max_edges", 5000)
            show_labels = request.input_data.get("show_labels", True)
            interactive = request.input_data.get("interactive", True)
            output_format = request.input_data.get("output_format", "html")
            filter_criteria = request.input_data.get("filter_criteria", {})
            
            logger.info(f"Starting visualization: {graph_source} source, {layout_type.value} layout")
            
            # Step 1: Load graph data using decomposed loader
            graph = self.data_loader.load_graph_data(graph_source, graph_data)
            
            if graph is None or len(graph.nodes) == 0:
                return self._create_error_result(
                    "Failed to load graph data or graph is empty",
                    execution_time=time.time() - start_time
                )
            
            logger.info(f"Loaded graph: {len(graph.nodes)} nodes, {len(graph.edges)} edges")
            
            # Step 2: Apply filters to reduce graph size
            if filter_criteria or len(graph.nodes) > max_nodes:
                filter_criteria["max_nodes"] = max_nodes
                graph = self.data_loader.apply_filters(graph, filter_criteria)
            
            # Step 3: Calculate layout using decomposed calculator
            layout_data = self.layout_calculator.calculate_layout(graph, layout_type)
            
            if not layout_data.get("success"):
                return self._create_error_result(
                    f"Layout calculation failed: {layout_data.get('error', 'Unknown error')}",
                    execution_time=time.time() - start_time
                )
            
            # Step 4: Calculate node attributes using decomposed calculator
            node_attributes = self.attribute_calculator.calculate_node_attributes(graph, node_size_metric)
            
            # Step 5: Calculate edge attributes using decomposed calculator
            edge_attributes = self.attribute_calculator.calculate_edge_attributes(graph, edge_width_metric)
            
            # Step 6: Generate color mapping using decomposed calculator
            color_mapping = self.attribute_calculator.generate_color_mapping(graph, color_scheme, node_attributes)
            
            # Step 7: Create visualization using decomposed renderer
            config = {
                "show_labels": show_labels,
                "interactive": interactive,
                "output_format": output_format
            }
            
            viz_data = self.plotly_renderer.create_visualization(
                graph, layout_data, node_attributes, edge_attributes, color_mapping, config
            )
            
            if not viz_data.get("success"):
                return self._create_error_result(
                    f"Visualization creation failed: {viz_data.get('error', 'Unknown error')}",
                    execution_time=time.time() - start_time
                )
            
            # Step 8: Save visualization files using decomposed renderer
            file_paths = self.plotly_renderer.save_visualization(viz_data, output_format)
            
            # Step 9: Calculate comprehensive statistics using decomposed renderer
            statistics = self.plotly_renderer.calculate_visualization_statistics(
                graph, layout_data, node_attributes, edge_attributes
            )
            
            # Calculate performance metrics
            execution_time = time.time() - start_time
            memory_used = psutil.Process().memory_info().rss - start_memory
            
            self.execution_count += 1
            logger.info(f"Visualization completed in {execution_time:.2f}s")
            
            # Create visualization result
            result = VisualizationResult(
                visualization_data=viz_data,
                layout_info=layout_data,
                statistics=statistics,
                file_paths=file_paths,
                metadata={
                    "graph_source": graph_source,
                    "layout_algorithm": layout_type.value,
                    "color_scheme": color_scheme.value,
                    "node_size_metric": node_size_metric,
                    "edge_width_metric": edge_width_metric,
                    "interactive": interactive,
                    "output_format": output_format,
                    "execution_time": execution_time,
                    "memory_used": memory_used,
                    "tool_version": self.version,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            return ToolResult(
                tool_id=self.tool_id, status="success", 
                data={
                    "visualization_data": result.visualization_data,
                    "layout_info": result.layout_info,
                    "statistics": result.statistics,
                    "file_paths": result.file_paths,
                    "metadata": result.metadata
                },
                metadata=result.metadata,
                execution_time=execution_time
            )
            
        except Exception as e:
            return self._handle_error(e, request, time.time() - start_time)
    
    def _validate_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate visualization input"""
        errors = []
        
        # Check required fields
        if "graph_source" not in input_data:
            errors.append("graph_source is required")
        
        # Validate graph source
        valid_sources = ["neo4j", "networkx", "edge_list", "adjacency_matrix"]
        if input_data.get("graph_source") not in valid_sources:
            errors.append(f"graph_source must be one of: {valid_sources}")
        
        # Validate layout if provided
        if "layout" in input_data:
            try:
                LayoutType(input_data["layout"])
            except ValueError:
                valid_layouts = [layout.value for layout in LayoutType]
                errors.append(f"layout must be one of: {valid_layouts}")
        
        # Validate color scheme if provided
        if "color_scheme" in input_data:
            try:
                ColorScheme(input_data["color_scheme"])
            except ValueError:
                valid_schemes = [scheme.value for scheme in ColorScheme]
                errors.append(f"color_scheme must be one of: {valid_schemes}")
        
        # Validate numeric parameters
        if "max_nodes" in input_data:
            if not isinstance(input_data["max_nodes"], int) or input_data["max_nodes"] < 1:
                errors.append("max_nodes must be a positive integer")
        
        if "max_edges" in input_data:
            if not isinstance(input_data["max_edges"], int) or input_data["max_edges"] < 1:
                errors.append("max_edges must be a positive integer")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def _create_error_result(self, error_message: str, execution_time: float) -> ToolResult:
        """Create error result"""
        return ToolResult(
            tool_id=self.tool_id, status="error", 
            data=None,
            error_message=error_message,
            metadata={
                "timestamp": datetime.now().isoformat(),
                "execution_time": execution_time,
                "tool_version": self.version
            },
            execution_time=execution_time
        )
    
    def _handle_error(self, error: Exception, request: ToolRequest, execution_time: float) -> ToolResult:
        """Handle errors with detailed context"""
        error_message = f"Graph visualization failed: {str(error)}"
        logger.error(error_message, exc_info=True)
        
        return ToolResult(
            tool_id=self.tool_id, status="error", 
            data=None,
            error_message=error_message,
            metadata={
                "error_type": type(error).__name__,
                "input_data": request.input_data,
                "timestamp": datetime.now().isoformat(),
                "execution_time": execution_time,
                "tool_version": self.version
            },
            execution_time=execution_time
        )
    
    def validate_input(self, input_data: Any) -> bool:
        """Simple input validation"""
        return self._validate_input(input_data)["valid"]