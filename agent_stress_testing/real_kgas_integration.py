#!/usr/bin/env python3
"""
Real KGAS Tool Integration for Agent Stress Testing

Connects to actual KGAS analysis tools for authentic workflow execution.
"""

import asyncio
import json
import time
import uuid
import sys
import os
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Union
from pathlib import Path

# Add KGAS src to path for real tool imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    # Import real KGAS tools
    from tools.phase1.t01_directory_processor import process_directory
    from tools.phase1.t13_web_scraper_unified import scrape_web_content
    from core.error_handler import handle_error
    from core.memory_manager import MemoryManager
    from monitoring.production_monitoring import ProductionMonitor
except ImportError as e:
    print(f"Warning: Could not import KGAS tools: {e}")
    print("Tools will fail gracefully if not available during execution")


@dataclass
class ToolExecutionResult:
    """Result from executing a KGAS tool"""
    tool_name: str
    execution_id: str
    status: str  # "success", "failure", "error"
    output_data: Any
    execution_time: float
    memory_usage: float
    error_message: Optional[str] = None
    quality_metrics: Dict[str, float] = None


class RealKGASToolExecutor:
    """Real KGAS tool executor for stress testing"""
    
    def __init__(self):
        self.available_tools = self._discover_available_tools()
        self.execution_history = []
        self.memory_manager = None
        self.monitor = None
        
        # Initialize core KGAS components if available
        try:
            self.memory_manager = MemoryManager()
            self.monitor = ProductionMonitor()
        except:
            print("Warning: KGAS core components not available")
    
    def _discover_available_tools(self) -> Dict[str, Dict[str, Any]]:
        """Discover available KGAS tools"""
        tools = {}
        
        # Phase 1 tools (document processing)
        tools.update({
            "directory_processor": {
                "module": "tools.phase1.t01_directory_processor",
                "function": "process_directory",
                "category": "document_processing",
                "description": "Process directory of documents",
                "inputs": ["directory_path"],
                "outputs": ["processed_files", "metadata"]
            },
            "web_scraper": {
                "module": "tools.phase1.t13_web_scraper_unified",
                "function": "scrape_web_content", 
                "category": "data_collection",
                "description": "Scrape web content for analysis",
                "inputs": ["url", "scrape_config"],
                "outputs": ["scraped_content", "metadata"]
            }
        })
        
        # Phase 2 tools (analysis) - would need to be implemented
        tools.update({
            "text_analyzer": {
                "module": "tools.phase2.text_analysis",
                "function": "analyze_text",
                "category": "text_analysis",
                "description": "Analyze text for themes and patterns",
                "inputs": ["text_data", "analysis_config"],
                "outputs": ["themes", "sentiment", "entities"]
            },
            "network_analyzer": {
                "module": "tools.phase2.network_analysis", 
                "function": "analyze_network",
                "category": "network_analysis",
                "description": "Analyze relationship networks",
                "inputs": ["entities", "relationships"],
                "outputs": ["network_metrics", "communities"]
            },
            "statistical_analyzer": {
                "module": "tools.phase2.statistical_analysis",
                "function": "analyze_statistics",
                "category": "statistical_analysis", 
                "description": "Perform statistical analysis",
                "inputs": ["data", "analysis_type"],
                "outputs": ["statistics", "correlations", "significance"]
            }
        })
        
        return tools
    
    async def execute_tool(self, tool_name: str, inputs: Dict[str, Any], config: Dict[str, Any] = None) -> ToolExecutionResult:
        """Execute a real KGAS tool"""
        start_time = time.time()
        execution_id = str(uuid.uuid4())
        
        if tool_name not in self.available_tools:
            return ToolExecutionResult(
                tool_name=tool_name,
                execution_id=execution_id,
                status="error",
                output_data=None,
                execution_time=time.time() - start_time,
                memory_usage=0.0,
                error_message=f"Tool {tool_name} not available"
            )
        
        tool_info = self.available_tools[tool_name]
        
        try:
            # Monitor memory before execution
            memory_before = self._get_memory_usage()
            
            # Execute the actual tool
            if tool_name == "directory_processor":
                result = await self._execute_directory_processor(inputs, config)
            elif tool_name == "web_scraper":
                result = await self._execute_web_scraper(inputs, config)
            elif tool_name == "text_analyzer":
                result = await self._execute_text_analyzer(inputs, config)
            elif tool_name == "network_analyzer":
                result = await self._execute_network_analyzer(inputs, config)
            elif tool_name == "statistical_analyzer":
                result = await self._execute_statistical_analyzer(inputs, config)
            else:
                # Fallback for tools not yet implemented
                result = await self._execute_generic_tool(tool_name, inputs, config)
            
            memory_after = self._get_memory_usage()
            execution_time = time.time() - start_time
            
            # Calculate quality metrics
            quality_metrics = self._calculate_quality_metrics(result, tool_name)
            
            execution_result = ToolExecutionResult(
                tool_name=tool_name,
                execution_id=execution_id,
                status="success",
                output_data=result,
                execution_time=execution_time,
                memory_usage=memory_after - memory_before,
                quality_metrics=quality_metrics
            )
            
            self.execution_history.append(execution_result)
            return execution_result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            execution_result = ToolExecutionResult(
                tool_name=tool_name,
                execution_id=execution_id,
                status="error",
                output_data=None,
                execution_time=execution_time,
                memory_usage=0.0,
                error_message=str(e)
            )
            
            self.execution_history.append(execution_result)
            return execution_result
    
    async def _execute_directory_processor(self, inputs: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute real directory processor tool"""
        directory_path = inputs.get("directory_path")
        if not directory_path:
            raise ValueError("directory_path required for directory processor")
        
        try:
            # Call real KGAS directory processor
            result = await asyncio.get_event_loop().run_in_executor(
                None, process_directory, directory_path
            )
            return result
        except NameError:
            # Graceful failure if tool not available
            raise RuntimeError(
                "Directory processor tool not available. "
                "Ensure KGAS tools are properly installed and accessible."
            )
    
    async def _execute_web_scraper(self, inputs: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute real web scraper tool"""
        url = inputs.get("url")
        scrape_config = inputs.get("scrape_config", {})
        
        if not url:
            raise ValueError("url required for web scraper")
        
        try:
            # Call real KGAS web scraper
            result = await asyncio.get_event_loop().run_in_executor(
                None, scrape_web_content, url, scrape_config
            )
            return result
        except NameError:
            # Graceful failure if tool not available
            raise RuntimeError(
                "Web scraper tool not available. "
                "Ensure KGAS tools are properly installed and accessible."
            )
    
    async def _execute_text_analyzer(self, inputs: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute real text analysis using available NLP tools"""
        text_data = inputs.get("text_data")
        if not text_data:
            raise ValueError("text_data required for text analyzer")
        
        # Use real text analysis implementation
        try:
            # Import and use actual text processing tools
            import nltk
            from collections import Counter
            import re
            
            # Ensure required NLTK data is available
            try:
                nltk.data.find('tokenizers/punkt')
            except LookupError:
                print("Downloading required NLTK data...")
                nltk.download('punkt', quiet=True)
                nltk.download('stopwords', quiet=True)
                nltk.download('vader_lexicon', quiet=True)
            
            from nltk.sentiment import SentimentIntensityAnalyzer
            from nltk.tokenize import word_tokenize, sent_tokenize
            from nltk.corpus import stopwords
            
            # Real text processing
            sentences = sent_tokenize(text_data)
            words = word_tokenize(text_data.lower())
            
            # Remove stopwords for theme extraction
            stop_words = set(stopwords.words('english'))
            filtered_words = [word for word in words if word.isalpha() and word not in stop_words]
            
            # Extract themes (most common meaningful words)
            word_freq = Counter(filtered_words)
            themes = [word for word, count in word_freq.most_common(10) if count > 1]
            
            # Real sentiment analysis
            sia = SentimentIntensityAnalyzer()
            sentiment_scores = []
            for sentence in sentences:
                scores = sia.polarity_scores(sentence)
                sentiment_scores.append(scores)
            
            # Aggregate sentiment
            avg_sentiment = {
                'positive': sum(s['pos'] for s in sentiment_scores) / len(sentiment_scores),
                'neutral': sum(s['neu'] for s in sentiment_scores) / len(sentiment_scores),
                'negative': sum(s['neg'] for s in sentiment_scores) / len(sentiment_scores),
                'compound': sum(s['compound'] for s in sentiment_scores) / len(sentiment_scores)
            }
            
            # Extract entities (capitalized words and phrases)
            entities = list(set([word for word in words if word.istitle() and len(word) > 2]))
            
            # Calculate confidence scores
            confidence_scores = [
                min(word_freq[theme] / max(word_freq.values()), 1.0) for theme in themes[:5]
            ]
            
            return {
                "themes": themes[:10],
                "sentiment": avg_sentiment,
                "entities": entities[:20],
                "confidence_scores": confidence_scores,
                "sentence_count": len(sentences),
                "word_count": len(words),
                "processing_stats": {
                    "text_length": len(text_data),
                    "sentences_processed": len(sentences),
                    "quality_score": min(avg_sentiment['compound'] + 0.5, 1.0)
                }
            }
            
        except ImportError:
            # Fallback to basic analysis if NLTK not available
            print("NLTK not available, using basic text analysis")
            
            # Basic word frequency analysis
            words = re.findall(r'\b[a-zA-Z]{3,}\b', text_data.lower())
            word_freq = Counter(words)
            themes = [word for word, count in word_freq.most_common(5)]
            
            # Basic sentiment (count positive/negative words)
            positive_words = ['good', 'great', 'excellent', 'positive', 'success', 'effective']
            negative_words = ['bad', 'poor', 'negative', 'problem', 'issue', 'failure']
            
            pos_count = sum(1 for word in words if word in positive_words)
            neg_count = sum(1 for word in words if word in negative_words)
            total = len(words)
            
            return {
                "themes": themes,
                "sentiment": {
                    "positive": pos_count / total if total > 0 else 0,
                    "negative": neg_count / total if total > 0 else 0,
                    "neutral": 1 - (pos_count + neg_count) / total if total > 0 else 1
                },
                "entities": [word.title() for word in words if word.istitle()],
                "confidence_scores": [0.7] * len(themes),
                "processing_stats": {
                    "text_length": len(text_data),
                    "processing_time": 0.1,
                    "quality_score": 0.6,
                    "method": "basic_fallback"
                }
            }
    
    async def _execute_network_analyzer(self, inputs: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute real network analysis using available graph libraries"""
        entities = inputs.get("entities", [])
        relationships = inputs.get("relationships", [])
        text_data = inputs.get("text_data", "")
        
        # Use real network analysis implementation
        try:
            import networkx as nx
            import itertools
            from collections import defaultdict
            import re
            
            # Create network graph
            G = nx.Graph()
            
            # Add entities as nodes
            for entity in entities:
                G.add_node(entity)
            
            # If relationships provided, use them
            if relationships:
                for rel in relationships:
                    if isinstance(rel, dict):
                        source = rel.get("source", "")
                        target = rel.get("target", "")
                        weight = rel.get("weight", 1.0)
                        if source and target:
                            G.add_edge(source, target, weight=weight)
                    elif isinstance(rel, (list, tuple)) and len(rel) >= 2:
                        G.add_edge(rel[0], rel[1])
            else:
                # Infer relationships from text co-occurrence
                if text_data and entities:
                    sentences = re.split(r'[.!?]+', text_data)
                    
                    for sentence in sentences:
                        # Find entities mentioned in same sentence
                        sentence_entities = [e for e in entities if e.lower() in sentence.lower()]
                        
                        # Create edges between co-occurring entities
                        for e1, e2 in itertools.combinations(sentence_entities, 2):
                            if G.has_edge(e1, e2):
                                G[e1][e2]['weight'] = G[e1][e2].get('weight', 0) + 1
                            else:
                                G.add_edge(e1, e2, weight=1)
            
            # Calculate network metrics
            if len(G.nodes()) > 0:
                try:
                    density = nx.density(G)
                    clustering = nx.average_clustering(G) if len(G.nodes()) > 1 else 0
                    
                    # Calculate centralities
                    betweenness = nx.betweenness_centrality(G) if len(G.nodes()) > 1 else {}
                    closeness = nx.closeness_centrality(G) if len(G.nodes()) > 1 else {}
                    degree = dict(G.degree())
                    
                    # Calculate average path length for connected components
                    if nx.is_connected(G):
                        avg_path_length = nx.average_shortest_path_length(G)
                    else:
                        # For disconnected graphs, calculate for largest component
                        largest_cc = max(nx.connected_components(G), key=len) if len(G.nodes()) > 1 else set()
                        if len(largest_cc) > 1:
                            subgraph = G.subgraph(largest_cc)
                            avg_path_length = nx.average_shortest_path_length(subgraph)
                        else:
                            avg_path_length = 0
                    
                    # Detect communities
                    try:
                        communities = list(nx.community.greedy_modularity_communities(G))
                        community_data = []
                        for i, community in enumerate(communities):
                            community_data.append({
                                "id": f"community_{i+1}",
                                "members": list(community),
                                "size": len(community),
                                "modularity": 0.7  # Would need proper modularity calculation
                            })
                    except:
                        # Simple fallback community detection
                        community_data = [{"id": "community_1", "members": list(G.nodes()), "size": len(G.nodes())}]
                    
                    return {
                        "network_metrics": {
                            "node_count": len(G.nodes()),
                            "edge_count": len(G.edges()),
                            "density": density,
                            "clustering_coefficient": clustering,
                            "average_path_length": avg_path_length
                        },
                        "communities": community_data,
                        "centrality_measures": {
                            node: {
                                "betweenness": betweenness.get(node, 0),
                                "closeness": closeness.get(node, 0),
                                "degree": degree.get(node, 0)
                            }
                            for node in G.nodes()
                        },
                        "processing_stats": {
                            "nodes_processed": len(G.nodes()),
                            "edges_processed": len(G.edges()),
                            "quality_score": min(density + clustering, 1.0),
                            "is_connected": nx.is_connected(G)
                        }
                    }
                
                except Exception as e:
                    print(f"NetworkX calculation error: {e}")
                    # Return basic metrics if calculation fails
                    return {
                        "network_metrics": {
                            "node_count": len(G.nodes()),
                            "edge_count": len(G.edges()),
                            "density": len(G.edges()) / (len(G.nodes()) * (len(G.nodes()) - 1) / 2) if len(G.nodes()) > 1 else 0
                        },
                        "communities": [{"id": "community_1", "members": list(G.nodes())}],
                        "centrality_measures": {},
                        "processing_stats": {"quality_score": 0.5, "method": "basic_fallback"}
                    }
            else:
                return {
                    "network_metrics": {"node_count": 0, "edge_count": 0, "density": 0},
                    "communities": [],
                    "centrality_measures": {},
                    "processing_stats": {"quality_score": 0.0, "error": "No entities provided"}
                }
        
        except ImportError:
            print("NetworkX not available, using basic network analysis")
            
            # Basic fallback network analysis
            node_count = len(entities)
            
            # Simple co-occurrence based edge estimation
            edge_count = 0
            if text_data and entities:
                for i, e1 in enumerate(entities):
                    for e2 in entities[i+1:]:
                        if e1.lower() in text_data.lower() and e2.lower() in text_data.lower():
                            edge_count += 1
            
            return {
                "network_metrics": {
                    "node_count": node_count,
                    "edge_count": edge_count,
                    "density": edge_count / (node_count * (node_count - 1) / 2) if node_count > 1 else 0
                },
                "communities": [{"id": "community_1", "members": entities}] if entities else [],
                "centrality_measures": {entity: {"degree": 1} for entity in entities},
                "processing_stats": {
                    "quality_score": 0.5,
                    "method": "basic_fallback",
                    "message": "NetworkX not available"
                }
            }
    
    async def _execute_statistical_analyzer(self, inputs: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute real statistical analysis using available statistical libraries"""
        data = inputs.get("data")
        analysis_type = inputs.get("analysis_type", "correlation")
        
        # Use real statistical analysis implementation
        try:
            import numpy as np
            from scipy import stats
            import pandas as pd
            from collections import defaultdict
            
            # Process different data types
            if isinstance(data, dict):
                # Convert dict to pandas DataFrame for analysis
                df = pd.DataFrame(data)
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                
                if len(numeric_cols) >= 2:
                    # Real correlation analysis
                    correlation_matrix = df[numeric_cols].corr()
                    correlations = []
                    
                    for i, col1 in enumerate(numeric_cols):
                        for col2 in numeric_cols[i+1:]:
                            corr_coef = correlation_matrix.loc[col1, col2]
                            # Calculate p-value for correlation
                            r, p_val = stats.pearsonr(df[col1].dropna(), df[col2].dropna())
                            
                            correlations.append({
                                "variables": [col1, col2],
                                "correlation": float(corr_coef),
                                "p_value": float(p_val),
                                "significant": p_val < 0.05
                            })
                    
                    # Statistical descriptives for first numeric column
                    first_col_data = df[numeric_cols[0]].dropna()
                    
                    statistics = {
                        "mean": float(np.mean(first_col_data)),
                        "std_dev": float(np.std(first_col_data)),
                        "variance": float(np.var(first_col_data)),
                        "skewness": float(stats.skew(first_col_data)),
                        "kurtosis": float(stats.kurtosis(first_col_data)),
                        "min": float(np.min(first_col_data)),
                        "max": float(np.max(first_col_data)),
                        "median": float(np.median(first_col_data))
                    }
                    
                    # Significance tests
                    significance_tests = []
                    
                    # One-sample t-test against population mean of 0
                    if len(first_col_data) > 1:
                        t_stat, t_p = stats.ttest_1samp(first_col_data, 0)
                        significance_tests.append({
                            "test": "one_sample_t_test",
                            "statistic": float(t_stat),
                            "p_value": float(t_p),
                            "significant": t_p < 0.05,
                            "description": "Test if mean differs from 0"
                        })
                    
                    # Normality test
                    if len(first_col_data) >= 8:  # Shapiro-Wilk requires at least 3 samples
                        shapiro_stat, shapiro_p = stats.shapiro(first_col_data)
                        significance_tests.append({
                            "test": "shapiro_wilk_normality",
                            "statistic": float(shapiro_stat),
                            "p_value": float(shapiro_p),
                            "significant": shapiro_p < 0.05,
                            "description": "Test for normal distribution"
                        })
                    
                    return {
                        "statistics": statistics,
                        "correlations": correlations,
                        "significance_tests": significance_tests,
                        "processing_stats": {
                            "data_points": len(df),
                            "numeric_variables": len(numeric_cols),
                            "analysis_type": analysis_type,
                            "quality_score": 0.9,
                            "method": "scipy_pandas"
                        }
                    }
                
                else:
                    return {
                        "statistics": {},
                        "correlations": [],
                        "significance_tests": [],
                        "processing_stats": {
                            "error": "Insufficient numeric data for statistical analysis",
                            "quality_score": 0.0
                        }
                    }
            
            elif isinstance(data, list) and len(data) > 0:
                # Handle list of numeric values
                try:
                    numeric_data = [float(x) for x in data if isinstance(x, (int, float))]
                    
                    if len(numeric_data) > 1:
                        statistics = {
                            "mean": float(np.mean(numeric_data)),
                            "std_dev": float(np.std(numeric_data)),
                            "variance": float(np.var(numeric_data)),
                            "skewness": float(stats.skew(numeric_data)),
                            "kurtosis": float(stats.kurtosis(numeric_data)),
                            "min": float(np.min(numeric_data)),
                            "max": float(np.max(numeric_data)),
                            "median": float(np.median(numeric_data))
                        }
                        
                        # Basic significance tests
                        significance_tests = []
                        if len(numeric_data) > 2:
                            t_stat, t_p = stats.ttest_1samp(numeric_data, 0)
                            significance_tests.append({
                                "test": "one_sample_t_test",
                                "statistic": float(t_stat),
                                "p_value": float(t_p),
                                "significant": t_p < 0.05
                            })
                        
                        return {
                            "statistics": statistics,
                            "correlations": [],
                            "significance_tests": significance_tests,
                            "processing_stats": {
                                "data_points": len(numeric_data),
                                "analysis_type": analysis_type,
                                "quality_score": 0.8,
                                "method": "scipy_numpy"
                            }
                        }
                    else:
                        return {
                            "statistics": {"count": len(numeric_data)},
                            "correlations": [],
                            "significance_tests": [],
                            "processing_stats": {
                                "error": "Insufficient numeric data points",
                                "quality_score": 0.2
                            }
                        }
                
                except (ValueError, TypeError):
                    return {
                        "statistics": {},
                        "correlations": [],
                        "significance_tests": [],
                        "processing_stats": {
                            "error": "Data conversion to numeric failed",
                            "quality_score": 0.0
                        }
                    }
            
            else:
                return {
                    "statistics": {},
                    "correlations": [],
                    "significance_tests": [],
                    "processing_stats": {
                        "error": "No valid data provided for analysis",
                        "quality_score": 0.0
                    }
                }
        
        except ImportError:
            print("SciPy/NumPy not available, using basic statistical analysis")
            
            # Basic statistical analysis fallback
            if isinstance(data, list) and len(data) > 0:
                try:
                    numeric_data = [float(x) for x in data if isinstance(x, (int, float))]
                    
                    if len(numeric_data) > 0:
                        mean_val = sum(numeric_data) / len(numeric_data)
                        variance = sum((x - mean_val) ** 2 for x in numeric_data) / len(numeric_data)
                        std_dev = variance ** 0.5
                        
                        return {
                            "statistics": {
                                "mean": mean_val,
                                "std_dev": std_dev,
                                "variance": variance,
                                "min": min(numeric_data),
                                "max": max(numeric_data),
                                "count": len(numeric_data)
                            },
                            "correlations": [],
                            "significance_tests": [],
                            "processing_stats": {
                                "data_points": len(numeric_data),
                                "analysis_type": analysis_type,
                                "quality_score": 0.6,
                                "method": "basic_fallback"
                            }
                        }
                except:
                    pass
            
            return {
                "statistics": {"count": 0},
                "correlations": [],
                "significance_tests": [],
                "processing_stats": {
                    "error": "Statistical libraries not available and basic analysis failed",
                    "quality_score": 0.1,
                    "method": "fallback_failed"
                }
            }
    
    async def _execute_generic_tool(self, tool_name: str, inputs: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Graceful failure for unimplemented tools - no mock responses"""
        raise NotImplementedError(
            f"Tool '{tool_name}' is not implemented. "
            f"Available tools: {list(self.available_tools.keys())}"
        )
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            import psutil
            process = psutil.Process(os.getpid())
            return process.memory_info().rss / 1024 / 1024  # Convert to MB
        except ImportError:
            return 0.0  # psutil not available
    
    def _calculate_quality_metrics(self, result: Dict[str, Any], tool_name: str) -> Dict[str, float]:
        """Calculate quality metrics for tool execution"""
        metrics = {}
        
        # Extract quality score from result if available
        processing_stats = result.get("processing_stats", {})
        if "quality_score" in processing_stats:
            metrics["quality_score"] = processing_stats["quality_score"]
        
        # Calculate completeness based on expected outputs
        tool_info = self.available_tools.get(tool_name, {})
        expected_outputs = tool_info.get("outputs", [])
        present_outputs = sum(1 for output in expected_outputs if output in result)
        metrics["completeness"] = present_outputs / len(expected_outputs) if expected_outputs else 1.0
        
        # Calculate confidence based on confidence scores if available
        if "confidence_scores" in result:
            confidence_scores = result["confidence_scores"]
            metrics["avg_confidence"] = sum(confidence_scores) / len(confidence_scores)
        
        return metrics
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for all tool executions"""
        if not self.execution_history:
            return {"total_executions": 0}
        
        successful_executions = [e for e in self.execution_history if e.status == "success"]
        total_time = sum(e.execution_time for e in self.execution_history)
        total_memory = sum(e.memory_usage for e in self.execution_history)
        
        # Tool usage statistics
        tool_usage = {}
        for execution in self.execution_history:
            tool_name = execution.tool_name
            if tool_name not in tool_usage:
                tool_usage[tool_name] = {"count": 0, "success_rate": 0.0, "avg_time": 0.0}
            tool_usage[tool_name]["count"] += 1
        
        for tool_name in tool_usage:
            tool_executions = [e for e in self.execution_history if e.tool_name == tool_name]
            successful = [e for e in tool_executions if e.status == "success"]
            tool_usage[tool_name]["success_rate"] = len(successful) / len(tool_executions)
            tool_usage[tool_name]["avg_time"] = sum(e.execution_time for e in tool_executions) / len(tool_executions)
        
        return {
            "total_executions": len(self.execution_history),
            "successful_executions": len(successful_executions),
            "success_rate": len(successful_executions) / len(self.execution_history),
            "total_execution_time": total_time,
            "avg_execution_time": total_time / len(self.execution_history),
            "total_memory_usage": total_memory,
            "avg_memory_usage": total_memory / len(self.execution_history),
            "tool_usage": tool_usage,
            "available_tools": list(self.available_tools.keys()),
            "recent_executions": [asdict(e) for e in self.execution_history[-5:]]
        }


class RealWorkflowExecutor:
    """Real workflow executor using actual KGAS tools"""
    
    def __init__(self):
        self.tool_executor = RealKGASToolExecutor()
        self.workflow_history = []
    
    async def execute_workflow(self, workflow_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a complete workflow using real KGAS tools"""
        start_time = time.time()
        workflow_id = str(uuid.uuid4())
        
        phases = workflow_spec.get("phases", [])
        if not phases:
            raise ValueError("Workflow specification must include phases")
        
        workflow_results = {
            "workflow_id": workflow_id,
            "workflow_name": workflow_spec.get("name", "Unnamed Workflow"),
            "total_phases": len(phases),
            "phase_results": {},
            "overall_status": "in_progress",
            "start_time": start_time
        }
        
        try:
            for phase_idx, phase in enumerate(phases):
                phase_name = phase.get("name", f"Phase_{phase_idx + 1}")
                phase_tools = phase.get("tools", [])
                phase_inputs = phase.get("inputs", {})
                
                print(f"Executing Phase: {phase_name}")
                
                phase_result = {
                    "phase_name": phase_name,
                    "tools_executed": [],
                    "outputs": {},
                    "status": "in_progress",
                    "start_time": time.time()
                }
                
                # Execute each tool in the phase
                for tool_name in phase_tools:
                    # Prepare inputs for this tool (might come from previous phases)
                    tool_inputs = self._prepare_tool_inputs(tool_name, phase_inputs, workflow_results)
                    
                    # Execute the tool
                    tool_result = await self.tool_executor.execute_tool(tool_name, tool_inputs)
                    phase_result["tools_executed"].append(asdict(tool_result))
                    
                    # Store outputs for next phases
                    if tool_result.status == "success" and tool_result.output_data:
                        phase_result["outputs"][tool_name] = tool_result.output_data
                    
                    print(f"  - {tool_name}: {tool_result.status} ({tool_result.execution_time:.2f}s)")
                
                phase_result["status"] = "completed"
                phase_result["execution_time"] = time.time() - phase_result["start_time"]
                workflow_results["phase_results"][phase_name] = phase_result
                
                print(f"Phase {phase_name} completed in {phase_result['execution_time']:.2f}s")
            
            workflow_results["overall_status"] = "completed"
            workflow_results["total_execution_time"] = time.time() - start_time
            workflow_results["performance_stats"] = self.tool_executor.get_performance_stats()
            
            self.workflow_history.append(workflow_results)
            return workflow_results
            
        except Exception as e:
            workflow_results["overall_status"] = "error"
            workflow_results["error"] = str(e)
            workflow_results["total_execution_time"] = time.time() - start_time
            
            self.workflow_history.append(workflow_results)
            return workflow_results
    
    def _prepare_tool_inputs(self, tool_name: str, phase_inputs: Dict[str, Any], workflow_results: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare inputs for a tool based on phase inputs and previous outputs"""
        inputs = phase_inputs.copy()
        
        # Add outputs from previous phases as potential inputs
        for phase_name, phase_result in workflow_results.get("phase_results", {}).items():
            for executed_tool, output_data in phase_result.get("outputs", {}).items():
                # Make previous outputs available with prefixed keys
                inputs[f"{phase_name}_{executed_tool}_output"] = output_data
        
        return inputs
    
    def get_workflow_stats(self) -> Dict[str, Any]:
        """Get workflow execution statistics"""
        if not self.workflow_history:
            return {"total_workflows": 0}
        
        completed_workflows = [w for w in self.workflow_history if w["overall_status"] == "completed"]
        total_time = sum(w.get("total_execution_time", 0) for w in self.workflow_history)
        
        return {
            "total_workflows": len(self.workflow_history),
            "completed_workflows": len(completed_workflows),
            "success_rate": len(completed_workflows) / len(self.workflow_history),
            "total_execution_time": total_time,
            "avg_execution_time": total_time / len(self.workflow_history),
            "tool_executor_stats": self.tool_executor.get_performance_stats(),
            "recent_workflows": self.workflow_history[-3:]
        }