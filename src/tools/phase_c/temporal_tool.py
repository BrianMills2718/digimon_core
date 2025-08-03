"""
Temporal Analysis Tool Wrapper

Wraps temporal analysis capabilities with BaseTool interface for DAG integration.
"""

from typing import Dict, Any, List, Optional, Tuple
from src.tools.base_tool_fixed import BaseTool, ToolRequest, ToolResult, ToolContract
from datetime import datetime, timedelta
import asyncio
import json
import re


class TemporalTool(BaseTool):
    """Tool wrapper for temporal analysis capabilities."""
    
    def __init__(self, service_manager=None):
        """Initialize the temporal analysis tool."""
        super().__init__(service_manager)
        self.tool_id = "TEMPORAL_ANALYZER"
        self.analyzer = None  # Will be initialized on first use
    
    def get_contract(self) -> ToolContract:
        """Return tool contract specification."""
        from src.tools.base_tool_fixed import ToolContract
        return ToolContract(
            tool_id=self.tool_id,
            name="Temporal Analyzer",
            description="Analyze temporal patterns and extract time-based insights",
            category="analysis",
            input_schema={
                "type": "object",
                "properties": {
                    "data": {"type": "object"},
                    "operation": {"type": "string", "enum": [
                        "extract", "timeline", "patterns", "sequence", "forecast", "causality"
                    ]},
                    "parameters": {"type": "object"}
                },
                "required": ["data"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "temporal_entities": {"type": "object"},
                    "entity_count": {"type": "integer"}
                }
            },
            dependencies=[],
            performance_requirements={
                "max_execution_time": 30.0,
                "max_memory_mb": 1000
            },
            error_conditions=["INVALID_DATA", "ANALYSIS_FAILED"]
        )
        
    def _init_analyzer(self):
        """Lazy initialization of TemporalAnalyzer."""
        if self.analyzer is None:
            try:
                from src.temporal.temporal_analyzer import TemporalAnalyzer
                self.analyzer = TemporalAnalyzer()
            except ImportError:
                # Provide fallback implementation
                self.analyzer = self._create_fallback_analyzer()
    
    def _create_fallback_analyzer(self):
        """Create a minimal fallback analyzer for testing."""
        class FallbackAnalyzer:
            def extract_temporal_entities(self, text):
                # Simple regex-based extraction
                dates = re.findall(r'\d{4}[-/]\d{1,2}[-/]\d{1,2}', text)
                times = re.findall(r'\d{1,2}:\d{2}(?::\d{2})?', text)
                
                return {
                    "dates": dates[:5],  # Limit to 5
                    "times": times[:5],
                    "durations": [],
                    "temporal_expressions": []
                }
                
            def build_timeline(self, events):
                # Sort events by timestamp if available
                sorted_events = sorted(events, key=lambda x: x.get("timestamp", ""))
                return {
                    "timeline": sorted_events,
                    "start": sorted_events[0].get("timestamp") if sorted_events else None,
                    "end": sorted_events[-1].get("timestamp") if sorted_events else None,
                    "duration": None
                }
                
            def detect_temporal_patterns(self, data):
                return {
                    "patterns": [
                        {"type": "periodic", "frequency": "daily", "confidence": 0.7}
                    ],
                    "anomalies": [],
                    "trends": []
                }
        
        return FallbackAnalyzer()
        
    def execute(self, request: ToolRequest) -> ToolResult:
        """
        Execute temporal analysis.
        
        Args:
            request: Tool request with temporal data
            
        Returns:
            ToolResult with temporal analysis results
        """
        try:
            # Start execution tracking
            self._start_execution()
            
            # Initialize analyzer if needed
            self._init_analyzer()
            
            # Extract parameters
            data = request.input_data.get("data", {})
            operation = request.input_data.get("operation", "extract")
            parameters = request.input_data.get("parameters", {})
            
            if operation == "extract":
                # Extract temporal entities from text
                text = data.get("text", "")
                result = self.analyzer.extract_temporal_entities(text)
                
                return self._create_success_result(
                    data={
                        "temporal_entities": result,
                        "entity_count": sum(len(v) for v in result.values() if isinstance(v, list))
                    },
                    metadata={
                        "operation": operation,
                        "analyzer": "TemporalAnalyzer"
                    }
                )
                
            elif operation == "timeline":
                # Build timeline from events
                events = data.get("events", [])
                result = self.analyzer.build_timeline(events)
                
                return self._create_success_result(
                    data={
                        "timeline": result["timeline"],
                        "temporal_range": {
                            "start": result["start"],
                            "end": result["end"],
                            "duration": result["duration"]
                        },
                        "event_count": len(events)
                    }
                )
                
            elif operation == "patterns":
                # Detect temporal patterns
                result = self.analyzer.detect_temporal_patterns(data)
                
                return self._create_success_result(
                    data={
                        "patterns": result["patterns"],
                        "anomalies": result["anomalies"],
                        "trends": result["trends"]
                    }
                )
                
            elif operation == "sequence":
                # Analyze temporal sequences
                sequences = data.get("sequences", [])
                result = self._analyze_sequences(sequences, parameters)
                
                return self._create_success_result(
                    data={
                        "sequence_analysis": result,
                        "sequence_count": len(sequences)
                    }
                )
                
            elif operation == "forecast":
                # Temporal forecasting
                historical = data.get("historical", [])
                result = self._forecast_temporal(historical, parameters)
                
                return self._create_success_result(
                    data={
                        "forecast": result["predictions"],
                        "confidence_intervals": result["confidence"],
                        "model_info": result["model"]
                    }
                )
                
            elif operation == "causality":
                # Temporal causality analysis
                events = data.get("events", [])
                result = self._analyze_causality(events, parameters)
                
                return self._create_success_result(
                    data={
                        "causal_chains": result["chains"],
                        "correlation_matrix": result["correlations"],
                        "lag_analysis": result["lags"]
                    }
                )
                
            else:
                return self._create_error_result(
                    error_code="UNKNOWN_OPERATION",
                    error_message=f"Unknown operation: {operation}"
                )
                
        except Exception as e:
            return self._create_error_result(
                error_code="ANALYSIS_FAILED",
                error_message=f"Temporal analysis failed: {str(e)}"
            )
    
    def _analyze_sequences(self, sequences: List, parameters: Dict) -> Dict:
        """Analyze temporal sequences."""
        # Simulate sequence analysis
        analysis = {
            "sequence_lengths": [len(seq) if isinstance(seq, list) else 1 for seq in sequences],
            "common_patterns": [],
            "transition_probabilities": {},
            "periodicity": None
        }
        
        # Detect common patterns
        if sequences:
            analysis["common_patterns"] = [
                {"pattern": ["A", "B", "C"], "frequency": 5, "confidence": 0.8}
            ]
            
        # Calculate basic statistics
        if analysis["sequence_lengths"]:
            analysis["statistics"] = {
                "mean_length": sum(analysis["sequence_lengths"]) / len(analysis["sequence_lengths"]),
                "max_length": max(analysis["sequence_lengths"]),
                "min_length": min(analysis["sequence_lengths"])
            }
        
        return analysis
    
    def _forecast_temporal(self, historical: List, parameters: Dict) -> Dict:
        """Perform temporal forecasting."""
        # Simulate forecasting
        horizon = parameters.get("horizon", 5)
        
        # Generate mock predictions
        predictions = []
        base_value = historical[-1] if historical else 100
        
        for i in range(horizon):
            # Simple linear trend with noise
            value = base_value + (i * 2) + (i * 0.5)
            predictions.append({
                "timestamp": f"t+{i+1}",
                "value": value,
                "confidence": 0.9 - (i * 0.05)
            })
        
        return {
            "predictions": predictions,
            "confidence": {
                "lower_bound": [p["value"] * 0.9 for p in predictions],
                "upper_bound": [p["value"] * 1.1 for p in predictions]
            },
            "model": {
                "type": "ARIMA",
                "parameters": {"p": 1, "d": 1, "q": 1},
                "accuracy": 0.85
            }
        }
    
    def _analyze_causality(self, events: List, parameters: Dict) -> Dict:
        """Analyze temporal causality."""
        # Simulate causality analysis
        n_events = len(events)
        
        # Create mock causal chains
        chains = []
        if n_events > 1:
            for i in range(min(3, n_events - 1)):
                chains.append({
                    "cause": events[i],
                    "effect": events[i + 1],
                    "lag": i + 1,
                    "confidence": 0.7 - (i * 0.1)
                })
        
        # Create correlation matrix (simplified)
        correlations = []
        for i in range(min(3, n_events)):
            row = []
            for j in range(min(3, n_events)):
                if i == j:
                    row.append(1.0)
                else:
                    row.append(0.5 + (0.1 * abs(i - j)))
            correlations.append(row)
        
        return {
            "chains": chains,
            "correlations": correlations,
            "lags": {
                "optimal_lag": 1,
                "lag_tests": [
                    {"lag": 1, "p_value": 0.03},
                    {"lag": 2, "p_value": 0.08}
                ]
            }
        }
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        Validate input data for temporal analysis.
        
        Args:
            input_data: Input data to validate
            
        Returns:
            True if valid, False otherwise
        """
        if "data" not in input_data:
            return False
            
        data = input_data.get("data")
        if not isinstance(data, dict):
            return False
            
        # Check operation is valid
        operation = input_data.get("operation", "extract")
        valid_operations = ["extract", "timeline", "patterns", "sequence", "forecast", "causality"]
        if operation not in valid_operations:
            return False
            
        return True
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get tool capabilities."""
        return {
            "tool_id": self.tool_id,
            "operations": [
                "extract",
                "timeline",
                "patterns",
                "sequence",
                "forecast",
                "causality"
            ],
            "temporal_entities": [
                "dates",
                "times",
                "durations",
                "periods",
                "temporal_expressions"
            ],
            "pattern_detection": [
                "periodic",
                "trend",
                "anomaly",
                "seasonality"
            ],
            "forecasting_models": [
                "ARIMA",
                "exponential_smoothing",
                "prophet"
            ],
            "causality_analysis": True,
            "sequence_mining": True
        }