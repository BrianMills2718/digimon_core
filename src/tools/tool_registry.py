"""Complete Tool Registry for KGAS

This registry tracks all 121 tools in the KGAS ecosystem with their
implementation status, dependencies, and metadata.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json
from pathlib import Path


class ToolCategory(Enum):
    """Tool categories in KGAS"""
    GRAPH = "graph"
    TABLE = "table"
    VECTOR = "vector"
    CROSS_MODAL = "cross_modal"


class ImplementationStatus(Enum):
    """Tool implementation status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    IMPLEMENTED = "implemented"
    DEPRECATED = "deprecated"
    UNIFIED = "unified"  # Implements UnifiedTool interface


@dataclass
class ToolRegistryEntry:
    """Registry entry for a single tool"""
    tool_id: str
    name: str
    description: str
    category: ToolCategory
    status: ImplementationStatus
    priority: int  # 1-10, 10 being highest
    dependencies: List[str] = field(default_factory=list)
    file_path: Optional[str] = None
    documentation_path: Optional[str] = None
    test_coverage: float = 0.0
    performance_benchmarks: Dict[str, float] = field(default_factory=dict)
    unified_interface: bool = False
    mcp_exposed: bool = False
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())


class ToolRegistry:
    """Complete registry of all 121 KGAS tools"""
    
    def __init__(self):
        self.tools: Dict[str, ToolRegistryEntry] = {}
        self._initialize_complete_registry()
    
    def _initialize_complete_registry(self):
        """Initialize all 121 tools in the registry"""
        
        # Graph Analysis Tools (T01-T30)
        self._register_graph_tools()
        
        # Table Analysis Tools (T31-T60)
        self._register_table_tools()
        
        # Vector Analysis Tools (T61-T90)
        self._register_vector_tools()
        
        # Cross-Modal Tools (T91-T121)
        self._register_cross_modal_tools()
    
    def _register_graph_tools(self):
        """Register graph analysis tools (T01-T30)"""
        graph_tools = [
            # Document Loaders (T01-T05)
            ("T01", "PDF Loader", "Load and extract text from PDF documents", 10, ImplementationStatus.UNIFIED, ["pypdf", "provenance_service"]),
            ("T02", "Word Loader", "Load and extract text from Word documents", 8, ImplementationStatus.UNIFIED, ["python-docx", "provenance_service"]),
            ("T03", "Text Loader", "Load plain text documents", 6, ImplementationStatus.UNIFIED, ["chardet", "provenance_service"]),
            ("T04", "Markdown Loader", "Load and parse Markdown documents", 5, ImplementationStatus.UNIFIED, ["markdown", "yaml", "provenance_service"]),
            ("T05", "CSV Loader", "Load structured data from CSV files", 7, ImplementationStatus.UNIFIED, ["pandas", "provenance_service"]),
            
            # JSON/HTML Loaders (T06-T07)
            ("T06", "JSON Loader", "Load and process JSON documents", 7, ImplementationStatus.UNIFIED, ["provenance_service"]),
            ("T07", "HTML Loader", "Load and parse HTML documents", 7, ImplementationStatus.UNIFIED, ["beautifulsoup4", "provenance_service"]),
            ("T08", "Closeness Centrality", "Calculate closeness centrality", 6, ImplementationStatus.NOT_STARTED, ["networkx", "neo4j"]),
            ("T09", "Eigenvector Centrality", "Calculate eigenvector centrality", 6, ImplementationStatus.NOT_STARTED, ["networkx", "neo4j"]),
            ("T10", "PageRank Alternative", "Alternative PageRank implementation", 5, ImplementationStatus.NOT_STARTED, ["networkx", "neo4j"]),
            
            # Community Detection (T11-T13)
            ("T11", "Community Detection", "Detect communities using Louvain algorithm", 8, ImplementationStatus.NOT_STARTED, ["python-louvain", "neo4j"]),
            ("T12", "Modularity Calculator", "Calculate network modularity", 6, ImplementationStatus.NOT_STARTED, ["networkx", "neo4j"]),
            ("T13", "Label Propagation", "Community detection via label propagation", 5, ImplementationStatus.NOT_STARTED, ["networkx", "neo4j"]),
            
            # Path Analysis (T14-T16)
            ("T14", "Shortest Path", "Find shortest paths between nodes", 7, ImplementationStatus.NOT_STARTED, ["neo4j"]),
            ("T15", "All Paths", "Find all paths between nodes", 5, ImplementationStatus.NOT_STARTED, ["neo4j"]),
            ("T15A", "Text Chunker", "Split text into overlapping chunks", 10, ImplementationStatus.IMPLEMENTED, ["quality_service"]),
            ("T16", "Path Analysis", "Analyze path patterns and properties", 6, ImplementationStatus.NOT_STARTED, ["neo4j"]),
            
            # Graph Extraction (T17-T19)
            ("T17", "Ego Network", "Extract ego networks around nodes", 6, ImplementationStatus.NOT_STARTED, ["neo4j"]),
            ("T18", "K-hop Neighborhood", "Extract k-hop neighborhoods", 7, ImplementationStatus.NOT_STARTED, ["neo4j"]),
            ("T19", "Subgraph Extraction", "Extract subgraphs by criteria", 7, ImplementationStatus.NOT_STARTED, ["neo4j"]),
            
            # Graph Analysis (T20-T22)
            ("T20", "Graph Clustering", "Cluster nodes by similarity", 6, ImplementationStatus.NOT_STARTED, ["scikit-learn", "neo4j"]),
            ("T21", "Graph Metrics", "Calculate global graph metrics", 5, ImplementationStatus.NOT_STARTED, ["networkx", "neo4j"]),
            ("T22", "Node Similarity", "Calculate node similarity scores", 6, ImplementationStatus.NOT_STARTED, ["neo4j"]),
            
            # Entity Processing (T23-T27)
            ("T23", "Entity Extraction Alt", "Alternative entity extraction method", 5, ImplementationStatus.NOT_STARTED, ["transformers"]),
            ("T23A", "spaCy NER", "Extract named entities using spaCy", 10, ImplementationStatus.IMPLEMENTED, ["spacy", "identity_service"]),
            ("T24", "Relation Extraction Alt", "Alternative relation extraction", 5, ImplementationStatus.NOT_STARTED, ["transformers"]),
            ("T25", "Coreference Resolution", "Resolve entity coreferences", 7, ImplementationStatus.NOT_STARTED, ["neuralcoref", "spacy"]),
            ("T26", "Entity Linking", "Link entities to knowledge bases", 6, ImplementationStatus.NOT_STARTED, ["entity-linker"]),
            ("T27", "Relationship Extractor", "Extract relationships between entities", 9, ImplementationStatus.IMPLEMENTED, ["spacy", "identity_service"]),
            
            # Graph Maintenance (T28-T30)
            ("T28", "Graph Validation", "Validate graph consistency", 6, ImplementationStatus.NOT_STARTED, ["neo4j"]),
            ("T29", "Graph Repair", "Repair graph inconsistencies", 5, ImplementationStatus.NOT_STARTED, ["neo4j"]),
            ("T30", "Graph Export", "Export graphs to various formats", 7, ImplementationStatus.NOT_STARTED, ["neo4j", "networkx"])
        ]
        
        self._register_tools(graph_tools, ToolCategory.GRAPH)
    
    def _register_table_tools(self):
        """Register table analysis tools (T31-T60)"""
        table_tools = [
            # Graph Building (T31-T35)
            ("T31", "Entity Builder", "Build entity nodes in graph", 10, ImplementationStatus.IMPLEMENTED, ["neo4j", "identity_service"]),
            ("T32", "Entity Merger", "Merge duplicate entities", 8, ImplementationStatus.NOT_STARTED, ["neo4j", "identity_service"]),
            ("T33", "Entity Enricher", "Enrich entities with metadata", 6, ImplementationStatus.NOT_STARTED, ["neo4j"]),
            ("T34", "Edge Builder", "Build relationship edges in graph", 10, ImplementationStatus.IMPLEMENTED, ["neo4j", "quality_service"]),
            ("T35", "Edge Enricher", "Enrich edges with metadata", 6, ImplementationStatus.NOT_STARTED, ["neo4j"]),
            
            # Table Operations (T36-T40)
            ("T36", "Table Loader", "Load data from tabular sources", 8, ImplementationStatus.NOT_STARTED, ["pandas"]),
            ("T37", "Table Joiner", "Join multiple tables", 7, ImplementationStatus.NOT_STARTED, ["pandas"]),
            ("T38", "Table Aggregator", "Aggregate table data", 6, ImplementationStatus.NOT_STARTED, ["pandas"]),
            ("T39", "Table Filter", "Filter table rows by criteria", 5, ImplementationStatus.NOT_STARTED, ["pandas"]),
            ("T40", "Table Transformer", "Transform table structure", 6, ImplementationStatus.NOT_STARTED, ["pandas"]),
            
            # Statistical Analysis (T41-T45)
            ("T41", "Descriptive Stats", "Calculate descriptive statistics", 7, ImplementationStatus.NOT_STARTED, ["pandas", "numpy"]),
            ("T42", "Correlation Analysis", "Analyze correlations in data", 7, ImplementationStatus.NOT_STARTED, ["pandas", "scipy"]),
            ("T43", "Regression Analysis", "Perform regression analysis", 6, ImplementationStatus.NOT_STARTED, ["scikit-learn"]),
            ("T44", "Time Series Analysis", "Analyze time series data", 6, ImplementationStatus.NOT_STARTED, ["statsmodels"]),
            ("T45", "Statistical Tests", "Perform statistical hypothesis tests", 5, ImplementationStatus.NOT_STARTED, ["scipy"]),
            
            # Data Quality (T46-T50)
            ("T46", "Data Profiler", "Profile data quality and completeness", 8, ImplementationStatus.NOT_STARTED, ["pandas-profiling"]),
            ("T47", "Anomaly Detector", "Detect anomalies in data", 7, ImplementationStatus.NOT_STARTED, ["scikit-learn"]),
            ("T48", "Data Validator", "Validate data against schemas", 7, ImplementationStatus.NOT_STARTED, ["jsonschema"]),
            ("T49", "Multi-hop Query", "Perform multi-hop graph queries", 9, ImplementationStatus.IMPLEMENTED, ["neo4j"]),
            ("T50", "Data Cleaner", "Clean and standardize data", 6, ImplementationStatus.NOT_STARTED, ["pandas"]),
            
            # Visualization Prep (T51-T55)
            ("T51", "Chart Data Prep", "Prepare data for charting", 6, ImplementationStatus.NOT_STARTED, ["pandas"]),
            ("T52", "Graph Layout", "Calculate graph layout coordinates", 5, ImplementationStatus.NOT_STARTED, ["networkx"]),
            ("T53", "Heatmap Generator", "Generate heatmap data", 5, ImplementationStatus.NOT_STARTED, ["numpy"]),
            ("T54", "Timeline Generator", "Generate timeline visualizations", 5, ImplementationStatus.NOT_STARTED, ["pandas"]),
            ("T55", "Dashboard Aggregator", "Aggregate data for dashboards", 6, ImplementationStatus.NOT_STARTED, ["pandas"]),
            
            # Export/Import (T56-T60)
            ("T56", "Excel Exporter", "Export data to Excel format", 6, ImplementationStatus.NOT_STARTED, ["openpyxl"]),
            ("T57", "JSON Exporter", "Export data to JSON format", 5, ImplementationStatus.NOT_STARTED, []),
            ("T58", "SQL Importer", "Import data from SQL databases", 7, ImplementationStatus.NOT_STARTED, ["sqlalchemy"]),
            ("T59", "API Connector", "Connect to external APIs", 7, ImplementationStatus.NOT_STARTED, ["requests"]),
            ("T60", "Report Generator", "Generate analysis reports", 7, ImplementationStatus.NOT_STARTED, ["jinja2"])
        ]
        
        self._register_tools(table_tools, ToolCategory.TABLE)
    
    def _register_vector_tools(self):
        """Register vector analysis tools (T61-T90)"""
        vector_tools = [
            # Text Embeddings (T61-T65)
            ("T61", "Word2Vec Embedder", "Generate Word2Vec embeddings", 7, ImplementationStatus.NOT_STARTED, ["gensim"]),
            ("T62", "FastText Embedder", "Generate FastText embeddings", 6, ImplementationStatus.NOT_STARTED, ["fasttext"]),
            ("T63", "BERT Embedder", "Generate BERT embeddings", 8, ImplementationStatus.NOT_STARTED, ["transformers"]),
            ("T64", "Sentence Embedder", "Generate sentence embeddings", 8, ImplementationStatus.NOT_STARTED, ["sentence-transformers"]),
            ("T65", "Document Embedder", "Generate document embeddings", 7, ImplementationStatus.NOT_STARTED, ["doc2vec"]),
            
            # Vector Operations (T66-T70)
            ("T66", "Vector Similarity", "Calculate vector similarities", 8, ImplementationStatus.NOT_STARTED, ["numpy", "scipy"]),
            ("T67", "Vector Clustering", "Cluster vectors", 7, ImplementationStatus.NOT_STARTED, ["scikit-learn"]),
            ("T68", "PageRank Calculator", "Calculate PageRank scores", 9, ImplementationStatus.IMPLEMENTED, ["networkx", "neo4j"]),
            ("T69", "Vector Projection", "Project vectors to lower dimensions", 6, ImplementationStatus.NOT_STARTED, ["scikit-learn"]),
            ("T70", "Vector Indexer", "Index vectors for fast search", 7, ImplementationStatus.NOT_STARTED, ["faiss"]),
            
            # Semantic Search (T71-T75)
            ("T71", "Semantic Search", "Perform semantic similarity search", 8, ImplementationStatus.NOT_STARTED, ["faiss", "sentence-transformers"]),
            ("T72", "Query Expansion", "Expand queries with similar terms", 6, ImplementationStatus.NOT_STARTED, ["gensim"]),
            ("T73", "Concept Extraction", "Extract concepts from embeddings", 6, ImplementationStatus.NOT_STARTED, ["scikit-learn"]),
            ("T74", "Topic Modeling", "Discover topics in documents", 7, ImplementationStatus.NOT_STARTED, ["gensim", "scikit-learn"]),
            ("T75", "Semantic Clustering", "Cluster by semantic similarity", 6, ImplementationStatus.NOT_STARTED, ["scikit-learn"]),
            
            # Vector Storage (T76-T80)
            ("T76", "ChromaDB Connector", "Connect to ChromaDB vector store", 8, ImplementationStatus.NOT_STARTED, ["chromadb"]),
            ("T77", "Pinecone Connector", "Connect to Pinecone vector store", 7, ImplementationStatus.NOT_STARTED, ["pinecone-client"]),
            ("T78", "Weaviate Connector", "Connect to Weaviate vector store", 7, ImplementationStatus.NOT_STARTED, ["weaviate-client"]),
            ("T79", "Vector Cache", "Cache frequently used vectors", 6, ImplementationStatus.NOT_STARTED, ["redis"]),
            ("T80", "Vector Persistence", "Persist vectors to disk", 5, ImplementationStatus.NOT_STARTED, ["numpy"]),
            
            # Advanced Vector (T81-T85)
            ("T81", "Cross-lingual Embedder", "Generate cross-lingual embeddings", 6, ImplementationStatus.NOT_STARTED, ["laser"]),
            ("T82", "Multimodal Embedder", "Generate multimodal embeddings", 7, ImplementationStatus.NOT_STARTED, ["clip"]),
            ("T83", "Fine-tuned Embedder", "Fine-tune embeddings for domain", 6, ImplementationStatus.NOT_STARTED, ["transformers"]),
            ("T84", "Embedding Evaluator", "Evaluate embedding quality", 5, ImplementationStatus.NOT_STARTED, ["scipy"]),
            ("T85", "Embedding Visualizer", "Visualize embedding spaces", 5, ImplementationStatus.NOT_STARTED, ["matplotlib", "plotly"]),
            
            # RAG Components (T86-T90)
            ("T86", "Document Chunker Pro", "Advanced document chunking for RAG", 8, ImplementationStatus.NOT_STARTED, ["langchain"]),
            ("T87", "Context Builder", "Build context for RAG queries", 8, ImplementationStatus.NOT_STARTED, ["langchain"]),
            ("T88", "Retrieval Ranker", "Rank retrieved documents", 7, ImplementationStatus.NOT_STARTED, ["sentence-transformers"]),
            ("T89", "Answer Generator", "Generate answers from context", 8, ImplementationStatus.NOT_STARTED, ["transformers"]),
            ("T90", "RAG Evaluator", "Evaluate RAG pipeline quality", 6, ImplementationStatus.NOT_STARTED, ["ragas"])
        ]
        
        self._register_tools(vector_tools, ToolCategory.VECTOR)
    
    def _register_cross_modal_tools(self):
        """Register cross-modal tools (T91-T121)"""
        cross_modal_tools = [
            # Graph-Table Conversions (T91-T95)
            ("T91", "Graph to Table", "Convert graph data to table format", 9, ImplementationStatus.NOT_STARTED, ["neo4j", "pandas"]),
            ("T92", "Table to Graph", "Convert table data to graph format", 9, ImplementationStatus.NOT_STARTED, ["pandas", "neo4j"]),
            ("T93", "Graph Stats Table", "Generate statistics table from graph", 7, ImplementationStatus.NOT_STARTED, ["neo4j", "pandas"]),
            ("T94", "Edge List Generator", "Generate edge lists from graphs", 6, ImplementationStatus.NOT_STARTED, ["neo4j", "pandas"]),
            ("T95", "Adjacency Matrix", "Generate adjacency matrices", 6, ImplementationStatus.NOT_STARTED, ["networkx", "numpy"]),
            
            # Graph-Vector Conversions (T96-T100)
            ("T96", "Node2Vec", "Generate node embeddings", 8, ImplementationStatus.NOT_STARTED, ["node2vec", "gensim"]),
            ("T97", "Graph2Vec", "Generate graph embeddings", 7, ImplementationStatus.NOT_STARTED, ["graph2vec"]),
            ("T98", "Edge Embedder", "Generate edge embeddings", 6, ImplementationStatus.NOT_STARTED, ["numpy"]),
            ("T99", "Subgraph Embedder", "Generate subgraph embeddings", 6, ImplementationStatus.NOT_STARTED, ["torch-geometric"]),
            ("T100", "Graph Similarity Vector", "Calculate graph similarity vectors", 6, ImplementationStatus.NOT_STARTED, ["networkx"]),
            
            # Table-Vector Conversions (T101-T105)
            ("T101", "Table Row Embedder", "Embed table rows as vectors", 7, ImplementationStatus.NOT_STARTED, ["pandas", "scikit-learn"]),
            ("T102", "Column Embedder", "Embed table columns", 6, ImplementationStatus.NOT_STARTED, ["pandas", "numpy"]),
            ("T103", "Feature Extractor", "Extract features from tables", 7, ImplementationStatus.NOT_STARTED, ["pandas", "scikit-learn"]),
            ("T104", "Table Vectorizer", "Vectorize entire tables", 6, ImplementationStatus.NOT_STARTED, ["pandas", "numpy"]),
            ("T105", "Schema Embedder", "Embed table schemas", 5, ImplementationStatus.NOT_STARTED, ["pandas"]),
            
            # Service Tools (T106-T110)
            ("T106", "Format Detector", "Detect data format automatically", 7, ImplementationStatus.NOT_STARTED, []),
            ("T107", "Identity Service Tool", "Entity identity resolution", 9, ImplementationStatus.IMPLEMENTED, ["identity_service"]),
            ("T108", "Provenance Tracker", "Track data provenance", 8, ImplementationStatus.NOT_STARTED, ["provenance_service"]),
            ("T109", "Quality Assessor", "Assess data quality", 7, ImplementationStatus.NOT_STARTED, ["quality_service"]),
            ("T110", "Provenance Service Tool", "Provenance management", 9, ImplementationStatus.IMPLEMENTED, ["provenance_service"]),
            
            # Integration Tools (T111-T115)
            ("T111", "Quality Service Tool", "Quality assessment", 9, ImplementationStatus.IMPLEMENTED, ["quality_service"]),
            ("T112", "Pipeline Composer", "Compose analysis pipelines", 8, ImplementationStatus.NOT_STARTED, ["pipeline_orchestrator"]),
            ("T113", "Workflow Validator", "Validate analysis workflows", 7, ImplementationStatus.NOT_STARTED, ["workflow_service"]),
            ("T114", "Result Aggregator", "Aggregate multi-modal results", 7, ImplementationStatus.NOT_STARTED, []),
            ("T115", "Error Handler", "Centralized error handling", 8, ImplementationStatus.NOT_STARTED, []),
            
            # Advanced Cross-Modal (T116-T121)
            ("T116", "Multi-modal Fusion", "Fuse multi-modal data", 8, ImplementationStatus.NOT_STARTED, ["torch"]),
            ("T117", "Cross-modal Aligner", "Align cross-modal representations", 7, ImplementationStatus.NOT_STARTED, ["torch"]),
            ("T118", "Modal Translator", "Translate between modalities", 7, ImplementationStatus.NOT_STARTED, ["torch"]),
            ("T119", "Consistency Checker", "Check cross-modal consistency", 6, ImplementationStatus.NOT_STARTED, []),
            ("T120", "Performance Monitor", "Monitor tool performance", 8, ImplementationStatus.NOT_STARTED, ["prometheus"]),
            ("T121", "MCP Service Tool", "MCP protocol service", 9, ImplementationStatus.IMPLEMENTED, ["mcp_server"])
        ]
        
        self._register_tools(cross_modal_tools, ToolCategory.CROSS_MODAL)
    
    def _register_tools(self, tools: List[tuple], category: ToolCategory):
        """Register a list of tools in the registry"""
        for tool_data in tools:
            if len(tool_data) == 6:  # With dependencies
                tool_id, name, desc, priority, status, deps = tool_data
            else:  # Without dependencies
                tool_id, name, desc, priority, status = tool_data
                deps = []
            
            # Determine file path if implemented
            file_path = None
            if status in [ImplementationStatus.IMPLEMENTED, ImplementationStatus.UNIFIED]:
                if category == ToolCategory.GRAPH:
                    if tool_id == "T15A":
                        file_path = f"src/tools/phase1/t15a_text_chunker.py"
                    elif tool_id in ["T01", "T02", "T05", "T06", "T07"]:
                        file_path = f"src/tools/phase1/{tool_id.lower()}_{name.lower().replace(' ', '_')}_unified.py"
                    elif tool_id.startswith("T"):
                        file_path = f"src/tools/phase1/{tool_id.lower()}_{name.lower().replace(' ', '_')}.py"
                elif category == ToolCategory.TABLE:
                    file_path = f"src/tools/phase1/{tool_id.lower()}_{name.lower().replace(' ', '_')}.py"
                elif category == ToolCategory.CROSS_MODAL:
                    if tool_id.startswith("T10") or tool_id.startswith("T11") or tool_id == "T121":
                        file_path = f"src/core/{name.lower().replace(' ', '_')}.py"
            
            # Check if tool is exposed via MCP
            mcp_exposed = tool_id in self._get_mcp_exposed_tools()
            
            # Check if tool implements unified interface
            unified = tool_id in ["T01", "T02", "T05", "T06", "T07"] and status == ImplementationStatus.UNIFIED
            
            entry = ToolRegistryEntry(
                tool_id=tool_id,
                name=name,
                description=desc,
                category=category,
                status=status,
                priority=priority,
                dependencies=deps,
                file_path=file_path,
                documentation_path=f"docs/tools/{tool_id.lower()}.md",
                test_coverage=self._get_test_coverage(tool_id),
                performance_benchmarks=self._get_performance_benchmarks(tool_id),
                unified_interface=unified,
                mcp_exposed=mcp_exposed
            )
            
            self.tools[tool_id] = entry
    
    def _get_implemented_tools(self) -> set:
        """Get set of implemented tool IDs"""
        return {
            "T01", "T02", "T05", "T06", "T07", "T15A", "T23A", "T27", "T31", "T34", "T68", "T49",  # Phase 1
            "T107", "T110", "T111", "T121"  # Service tools
        }
    
    def _get_mcp_exposed_tools(self) -> set:
        """Get set of tools exposed via MCP"""
        return {
            "T01", "T02", "T05", "T06", "T07", "T15A", "T23A", "T27", "T31", "T34", "T68", "T49",  # Phase 1 pipeline
            "T107", "T110", "T111", "T121"  # Service tools
        }
    
    def _get_test_coverage(self, tool_id: str) -> float:
        """Get test coverage for tool (mock data for now)"""
        coverage_map = {
            "T01": 95.0,  # Updated with TDD tests
            "T02": 95.0,  # New TDD tests
            "T05": 95.0,  # New TDD tests
            "T06": 95.0,  # New TDD tests
            "T07": 95.0,  # New TDD tests
            "T15A": 90.0,
            "T23A": 88.0,
            "T27": 82.0,
            "T31": 87.0,
            "T34": 85.0,
            "T68": 92.0,
            "T49": 80.0,
            "T107": 95.0,
            "T110": 93.0,
            "T111": 91.0,
            "T121": 78.0
        }
        return coverage_map.get(tool_id, 0.0)
    
    def _get_performance_benchmarks(self, tool_id: str) -> Dict[str, float]:
        """Get performance benchmarks for tool (mock data for now)"""
        if tool_id not in self._get_implemented_tools():
            return {}
        
        # Default benchmarks for implemented tools
        return {
            "avg_execution_time": 0.5,
            "max_memory_mb": 100,
            "throughput_per_sec": 10.0
        }
    
    # Query methods
    
    def get_tool(self, tool_id: str) -> Optional[ToolRegistryEntry]:
        """Get a specific tool by ID"""
        return self.tools.get(tool_id)
    
    def get_tools_by_category(self, category: ToolCategory) -> List[ToolRegistryEntry]:
        """Get all tools in a category"""
        return [tool for tool in self.tools.values() if tool.category == category]
    
    def get_tools_by_status(self, status: ImplementationStatus) -> List[ToolRegistryEntry]:
        """Get all tools with a specific status"""
        return [tool for tool in self.tools.values() if tool.status == status]
    
    def get_implemented_tools(self) -> List[ToolRegistryEntry]:
        """Get all implemented tools"""
        return [
            tool for tool in self.tools.values() 
            if tool.status in [ImplementationStatus.IMPLEMENTED, ImplementationStatus.UNIFIED]
        ]
    
    def get_unified_tools(self) -> List[ToolRegistryEntry]:
        """Get tools that implement the unified interface"""
        return [tool for tool in self.tools.values() if tool.unified_interface]
    
    def get_priority_queue(self) -> List[ToolRegistryEntry]:
        """Get unimplemented tools ordered by priority"""
        unimplemented = [
            tool for tool in self.tools.values()
            if tool.status == ImplementationStatus.NOT_STARTED
        ]
        return sorted(unimplemented, key=lambda t: t.priority, reverse=True)
    
    def get_implementation_status(self) -> Dict[str, int]:
        """Get summary of implementation status"""
        status_counts = {}
        for tool in self.tools.values():
            status_name = tool.status.value
            status_counts[status_name] = status_counts.get(status_name, 0) + 1
        
        # Add summary stats
        total = len(self.tools)
        implemented = len(self.get_implemented_tools())
        status_counts["total"] = total
        status_counts["implemented_total"] = implemented
        status_counts["implementation_percentage"] = round(implemented / total * 100, 1)
        
        return status_counts
    
    def get_category_summary(self) -> Dict[str, Dict[str, int]]:
        """Get implementation summary by category"""
        summary = {}
        
        for category in ToolCategory:
            tools = self.get_tools_by_category(category)
            implemented = [t for t in tools if t.status in [ImplementationStatus.IMPLEMENTED, ImplementationStatus.UNIFIED]]
            
            summary[category.value] = {
                "total": len(tools),
                "implemented": len(implemented),
                "percentage": round(len(implemented) / len(tools) * 100, 1) if tools else 0
            }
        
        return summary
    
    def get_dependency_graph(self) -> Dict[str, List[str]]:
        """Get tool dependency graph"""
        dep_graph = {}
        for tool in self.tools.values():
            dep_graph[tool.tool_id] = tool.dependencies
        return dep_graph
    
    def get_mcp_tools(self) -> List[ToolRegistryEntry]:
        """Get tools exposed via MCP"""
        return [tool for tool in self.tools.values() if tool.mcp_exposed]
    
    def export_registry(self, file_path: str):
        """Export registry to JSON file"""
        data = {
            "metadata": {
                "total_tools": len(self.tools),
                "last_updated": datetime.now().isoformat(),
                "implementation_status": self.get_implementation_status(),
                "category_summary": self.get_category_summary()
            },
            "tools": {
                tool_id: {
                    "name": tool.name,
                    "description": tool.description,
                    "category": tool.category.value,
                    "status": tool.status.value,
                    "priority": tool.priority,
                    "dependencies": tool.dependencies,
                    "file_path": tool.file_path,
                    "test_coverage": tool.test_coverage,
                    "unified_interface": tool.unified_interface,
                    "mcp_exposed": tool.mcp_exposed,
                    "last_updated": tool.last_updated
                }
                for tool_id, tool in self.tools.items()
            }
        }
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def generate_implementation_report(self) -> str:
        """Generate detailed implementation report"""
        report = []
        report.append("# KGAS Tool Implementation Report")
        report.append(f"\nGenerated: {datetime.now().isoformat()}")
        report.append(f"\nTotal Tools: {len(self.tools)}")
        
        # Overall status
        status = self.get_implementation_status()
        report.append(f"\n## Implementation Status")
        report.append(f"- Implemented: {status['implemented_total']} ({status['implementation_percentage']}%)")
        report.append(f"- Not Started: {status.get('not_started', 0)}")
        report.append(f"- In Progress: {status.get('in_progress', 0)}")
        report.append(f"- Deprecated: {status.get('deprecated', 0)}")
        
        # Category breakdown
        report.append(f"\n## Category Breakdown")
        for category, stats in self.get_category_summary().items():
            report.append(f"\n### {category.title()} Tools")
            report.append(f"- Total: {stats['total']}")
            report.append(f"- Implemented: {stats['implemented']} ({stats['percentage']}%)")
        
        # High priority unimplemented
        report.append(f"\n## High Priority Unimplemented Tools")
        priority_tools = self.get_priority_queue()[:10]
        for tool in priority_tools:
            report.append(f"- **{tool.tool_id}**: {tool.name} (Priority: {tool.priority})")
        
        # Unified interface adoption
        unified_tools = self.get_unified_tools()
        report.append(f"\n## Unified Interface Adoption")
        report.append(f"- Tools with Unified Interface: {len(unified_tools)}")
        report.append(f"- Adoption Rate: {round(len(unified_tools) / status['implemented_total'] * 100, 1)}%")
        
        # MCP exposure
        mcp_tools = self.get_mcp_tools()
        report.append(f"\n## MCP Protocol Exposure")
        report.append(f"- Tools exposed via MCP: {len(mcp_tools)}")
        report.append(f"- Exposure Rate: {round(len(mcp_tools) / status['implemented_total'] * 100, 1)}%")
        
        return "\n".join(report)


# Singleton instance
_registry_instance = None


def get_tool_registry() -> ToolRegistry:
    """Get the singleton tool registry instance"""
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = ToolRegistry()
    return _registry_instance


# Convenience functions
def get_tool_info(tool_id: str) -> Optional[ToolRegistryEntry]:
    """Get information about a specific tool"""
    return get_tool_registry().get_tool(tool_id)


def list_implemented_tools() -> List[str]:
    """List all implemented tool IDs"""
    return [tool.tool_id for tool in get_tool_registry().get_implemented_tools()]


def get_next_priority_tools(count: int = 5) -> List[ToolRegistryEntry]:
    """Get the next N highest priority unimplemented tools"""
    return get_tool_registry().get_priority_queue()[:count]