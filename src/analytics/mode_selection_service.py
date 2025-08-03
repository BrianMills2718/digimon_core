#!/usr/bin/env python3
"""
Mode Selection Service - LLM-driven intelligent mode selection for cross-modal analysis

Implements intelligent mode selection using LLM reasoning with fail-fast error handling.
NO FALLBACKS - system fails loudly if LLM unavailable to surface configuration issues.
"""

import asyncio
import time
import logging
import json
import threading
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
from pydantic import ValidationError

try:
    from ..core.unified_service_interface import CoreService, ServiceResponse, create_service_response
    from ..core.config_manager import get_config
    from ..core.logging_config import get_logger
except ImportError:
    # Fallback for direct execution - ONLY try absolute import, NO stubs
    from src.core.unified_service_interface import CoreService, ServiceResponse, create_service_response
    from src.core.config_manager import get_config
    from src.core.logging_config import get_logger

logger = get_logger("analytics.mode_selection_service")


class AnalysisMode(Enum):
    """Available analysis modes for cross-modal processing"""
    GRAPH_ANALYSIS = "graph_analysis"
    TABLE_ANALYSIS = "table_analysis"  
    VECTOR_ANALYSIS = "vector_analysis"
    HYBRID_GRAPH_TABLE = "hybrid_graph_table"
    HYBRID_GRAPH_VECTOR = "hybrid_graph_vector"
    HYBRID_TABLE_VECTOR = "hybrid_table_vector"
    COMPREHENSIVE_MULTIMODAL = "comprehensive_multimodal"


class ConfidenceLevel(Enum):
    """Confidence levels for mode selection decisions"""
    VERY_HIGH = "very_high"  # 0.9+
    HIGH = "high"           # 0.7-0.89
    MEDIUM = "medium"       # 0.5-0.69
    LOW = "low"             # 0.3-0.49
    VERY_LOW = "very_low"   # <0.3


@dataclass
class DataContext:
    """Context information about the data being analyzed"""
    data_size: int
    data_types: List[str]
    entity_count: int
    relationship_count: int
    has_temporal_data: bool
    has_spatial_data: bool
    has_hierarchical_structure: bool
    complexity_score: float
    available_formats: List[str]


@dataclass
class ModeSelectionResult:
    """Result of mode selection analysis"""
    primary_mode: AnalysisMode
    secondary_modes: List[AnalysisMode]
    confidence: float
    confidence_level: ConfidenceLevel
    reasoning: str
    workflow_steps: List[Dict[str, Any]]
    estimated_performance: Dict[str, Any]
    fallback_used: bool
    selection_metadata: Dict[str, Any]


@dataclass
class WorkflowStep:
    """Individual step in analysis workflow"""
    step_id: str
    step_type: str
    operation: str
    parameters: Dict[str, Any]
    dependencies: List[str]
    estimated_duration: float
    required_resources: Dict[str, Any]


class ModeSelectionService(CoreService):
    """LLM-driven intelligent mode selection for cross-modal analysis
    
    Provides intelligent mode selection using LLM reasoning with fail-fast error handling,
    performance optimization, and detailed decision tracking. NO FALLBACKS - system
    fails loudly if LLM unavailable to surface configuration issues.
    """
    
    def __init__(self, service_manager=None, llm_client=None):
        self.service_manager = service_manager
        self.config = get_config()
        self.logger = get_logger("analytics.mode_selection_service")
        
        # Set LLM client - NO AUTOMATIC INITIALIZATION  
        self.llm_client = llm_client
        if llm_client:
            self.logger.info("Using provided LLM client")
        else:
            self.logger.warning("No LLM client provided - service will fail fast on operations requiring LLM")
        
        # Configuration
        self.confidence_threshold = 0.7
        self.max_reasoning_length = 2000
        
        # Mode selection cache for performance
        self._selection_cache = {}
        self._cache_hits = 0
        self._cache_misses = 0
        
        # Performance tracking (thread-safe)
        self._stats_lock = threading.Lock()
        self._selection_times = []
        self._success_count = 0
        
        self.logger.info("ModeSelectionService initialized")
    
    def _get_thread_safe_stats(self) -> Dict[str, Any]:
        """Get performance statistics in a thread-safe manner"""
        with self._stats_lock:
            total_selections = self._success_count
            return {
                "total_selections": total_selections,
                "success_count": self._success_count,
                "success_rate": 1.0 if total_selections > 0 else 0.0,
                "avg_selection_time": sum(self._selection_times) / max(1, len(self._selection_times))
            }
    
    def _get_thread_safe_timing_stats(self) -> Dict[str, Any]:
        """Get timing statistics in a thread-safe manner"""
        with self._stats_lock:
            return {
                "avg_selection_time": sum(self._selection_times) / max(1, len(self._selection_times)),
                "min_selection_time": min(self._selection_times) if self._selection_times else 0,
                "max_selection_time": max(self._selection_times) if self._selection_times else 0
            }
    
    def initialize(self, config: Dict[str, Any]) -> ServiceResponse:
        """Initialize service with configuration"""
        try:
            # Update configuration
            self.confidence_threshold = config.get('confidence_threshold', 0.7)
            self.max_reasoning_length = config.get('max_reasoning_length', 2000)
            
            # LLM client must be provided - no auto-initialization
            if not self.llm_client:
                raise RuntimeError("LLM client must be provided during initialization - no auto-initialization supported")
            
            self.logger.info("ModeSelectionService initialized successfully")
            return create_service_response(
                success=True,
                data={"status": "initialized"},
                metadata={"timestamp": datetime.now().isoformat()}
            )
            
        except Exception as e:
            self.logger.error(f"Failed to initialize ModeSelectionService: {e}")
            return create_service_response(
                success=False,
                data=None,
                error_code="INITIALIZATION_FAILED",
                error_message=str(e)
            )
    
    def health_check(self) -> ServiceResponse:
        """Check service health and readiness"""
        try:
            health_data = {
                "service_status": "healthy",
                "cache_stats": {
                    "cache_size": len(self._selection_cache),
                    "cache_hits": self._cache_hits,
                    "cache_misses": self._cache_misses,
                    "hit_ratio": self._cache_hits / max(1, self._cache_hits + self._cache_misses)
                },
                "performance_stats": self._get_thread_safe_stats(),
                "llm_client_status": "available" if self.llm_client else "unavailable"
            }
            
            return create_service_response(
                success=True,
                data=health_data,
                metadata={"timestamp": datetime.now().isoformat()}
            )
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return create_service_response(
                success=False,
                data=None,
                error_code="HEALTH_CHECK_FAILED",
                error_message=str(e)
            )
    
    def get_statistics(self) -> ServiceResponse:
        """Get service performance statistics"""
        try:
            # Get thread-safe performance stats
            performance_stats = self._get_thread_safe_stats()
            
            stats = {
                "total_requests": performance_stats["total_selections"],
                "successful_llm_selections": performance_stats["success_count"],
                "cache_performance": {
                    "cache_size": len(self._selection_cache),
                    "cache_hits": self._cache_hits,
                    "cache_misses": self._cache_misses,
                    "hit_ratio": self._cache_hits / max(1, self._cache_hits + self._cache_misses)
                },
                "timing_stats": self._get_thread_safe_timing_stats()
            }
            
            return create_service_response(
                success=True,
                data=stats,
                metadata={"timestamp": datetime.now().isoformat()}
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get statistics: {e}")
            return create_service_response(
                success=False,
                data=None,
                error_code="STATISTICS_FAILED",
                error_message=str(e)
            )
    
    def cleanup(self) -> ServiceResponse:
        """Clean up service resources"""
        try:
            self._selection_cache.clear()
            self._selection_times.clear()
            self.logger.info("ModeSelectionService cleanup completed")
            
            return create_service_response(
                success=True,
                data={"status": "cleaned_up"},
                metadata={"timestamp": datetime.now().isoformat()}
            )
            
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")
            return create_service_response(
                success=False,
                data=None,
                error_code="CLEANUP_FAILED",
                error_message=str(e)
            )
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get service information and capabilities"""
        return {
            "service_name": "ModeSelectionService",
            "version": "1.0.0",
            "description": "LLM-driven intelligent mode selection for cross-modal analysis",
            "capabilities": [
                "intelligent_mode_selection",
                "llm_reasoning",
                "confidence_scoring",
                "workflow_generation"
            ],
            "supported_modes": [mode.value for mode in AnalysisMode],
            "confidence_levels": [level.value for level in ConfidenceLevel],
            "performance_features": [
                "caching",
                "performance_tracking",
                "fail_fast_error_handling"
            ]
        }
    
    async def select_optimal_mode(
        self, 
        research_question: str,
        data_context: DataContext,
        preferences: Optional[Dict[str, Any]] = None
    ) -> ModeSelectionResult:
        """Select optimal analysis mode using LLM reasoning - FAIL FAST if LLM unavailable
        
        Args:
            research_question: The research question being answered
            data_context: Context about the data being analyzed
            preferences: Optional user preferences for mode selection
            
        Returns:
            ModeSelectionResult with mode selection and reasoning
            
        Raises:
            RuntimeError: If LLM client not available
            ValidationError: If LLM selection validation fails
            Exception: If LLM request fails
        """
        start_time = time.time()
        
        # Check cache first
        cache_key = self._generate_cache_key(research_question, data_context, preferences)
        cached_result = self._get_cached_selection(cache_key)
        if cached_result:
            self._cache_hits += 1
            return cached_result
        
        self._cache_misses += 1
        
        # FAIL FAST if LLM client not available
        if not self.llm_client:
            raise RuntimeError("LLM client not available - cannot perform mode selection. Check API configuration.")
        
        # Call LLM without timeout - let it take as long as needed
        selection_result = await self._llm_mode_selection(
            research_question, data_context, preferences
        )
        
        # FAIL FAST on validation errors
        if not self._validate_selection(selection_result):
            raise ValidationError(f"LLM selection validation failed: confidence {selection_result.confidence} below threshold {self.confidence_threshold}")
        
        # Success - cache and return
        with self._stats_lock:
            self._success_count += 1
            self._selection_times.append(time.time() - start_time)
        self._cache_selection(cache_key, selection_result)
        
        self.logger.info(f"LLM mode selection successful: {selection_result.primary_mode.value}")
        return selection_result
    
    async def _llm_mode_selection(
        self,
        research_question: str,
        data_context: DataContext,
        preferences: Optional[Dict[str, Any]]
    ) -> ModeSelectionResult:
        """Use LLM to select optimal analysis mode - NO TIMEOUT, NO FALLBACK"""
        
        # Build comprehensive prompt
        prompt = self._build_mode_selection_prompt(research_question, data_context, preferences)
        
        # Query LLM without timeout - let underlying client handle timeouts
        try:
            llm_response = await self.llm_client.complete(prompt)
        except Exception as e:
            self.logger.error(f"LLM request failed: {e}")
            raise RuntimeError(f"LLM request failed: {e}") from e
        
        # Parse LLM response
        selection_result = self._parse_llm_response(llm_response, data_context)
        
        # Enhance with workflow steps
        selection_result.workflow_steps = self._generate_workflow_steps(
            selection_result.primary_mode, 
            selection_result.secondary_modes,
            data_context
        )
        
        # Add performance estimates
        selection_result.estimated_performance = self._estimate_performance(
            selection_result.primary_mode,
            data_context
        )
        
        selection_result.fallback_used = False
        
        return selection_result
    
    
    def _build_mode_selection_prompt(
        self,
        research_question: str,
        data_context: DataContext,
        preferences: Optional[Dict[str, Any]]
    ) -> str:
        """Build comprehensive prompt for LLM mode selection"""
        
        prompt = f"""You are an expert in cross-modal data analysis. Select the optimal analysis mode for the following research scenario.

RESEARCH QUESTION:
{research_question}

DATA CONTEXT:
- Data size: {data_context.data_size:,} records
- Data types: {', '.join(data_context.data_types)}
- Entity count: {data_context.entity_count:,}
- Relationship count: {data_context.relationship_count:,}
- Has temporal data: {data_context.has_temporal_data}
- Has spatial data: {data_context.has_spatial_data}
- Has hierarchical structure: {data_context.has_hierarchical_structure}
- Complexity score: {data_context.complexity_score:.2f}
- Available formats: {', '.join(data_context.available_formats)}

AVAILABLE ANALYSIS MODES:
1. GRAPH_ANALYSIS - Best for relationship-heavy data, network analysis, connected entities
2. TABLE_ANALYSIS - Best for statistical analysis, aggregations, structured queries
3. VECTOR_ANALYSIS - Best for semantic similarity, clustering, embedding-based analysis
4. HYBRID_GRAPH_TABLE - Combines graph relationships with tabular analytics
5. HYBRID_GRAPH_VECTOR - Combines graph structure with semantic analysis
6. HYBRID_TABLE_VECTOR - Combines statistical analysis with semantic similarity
7. COMPREHENSIVE_MULTIMODAL - Uses all modes for complex, multi-faceted analysis

USER PREFERENCES:
{json.dumps(preferences or {}, indent=2)}

Please respond in the following JSON format:
{{
    "primary_mode": "selected_mode",
    "secondary_modes": ["mode1", "mode2"],
    "confidence": 0.85,
    "reasoning": "Detailed explanation of why this mode was selected...",
    "key_factors": ["factor1", "factor2", "factor3"]
}}

Consider:
- The complexity and scale of the data
- The nature of the research question
- Performance implications of each mode
- The availability of different data formats
- User preferences if specified

Provide a confidence score between 0.0 and 1.0, and explain your reasoning in detail.
"""
        
        return prompt
    
    def _parse_llm_response(
        self, 
        llm_response: str,
        data_context: DataContext
    ) -> ModeSelectionResult:
        """Parse LLM response into structured mode selection result"""
        
        try:
            # Clean up response - remove markdown code blocks if present
            response_text = llm_response.strip()
            if response_text.startswith('```json'):
                # Remove markdown JSON code blocks
                response_text = response_text.replace('```json', '').replace('```', '').strip()
            elif response_text.startswith('```'):
                # Remove generic code blocks
                response_text = response_text.replace('```', '').strip()
            
            # Try to parse JSON response
            response_data = json.loads(response_text)
            
            # Extract and validate primary mode
            primary_mode_str = response_data.get('primary_mode', '').upper()
            try:
                primary_mode = AnalysisMode(primary_mode_str.lower())
            except ValueError:
                raise Exception(f"Invalid primary mode: {primary_mode_str}")
            
            # Extract and validate secondary modes
            secondary_modes = []
            for mode_str in response_data.get('secondary_modes', []):
                try:
                    mode = AnalysisMode(mode_str.upper().lower())
                    if mode != primary_mode:
                        secondary_modes.append(mode)
                except ValueError:
                    self.logger.warning(f"Invalid secondary mode: {mode_str}")
            
            # Extract confidence and validate
            confidence = float(response_data.get('confidence', 0.5))
            confidence = max(0.0, min(1.0, confidence))  # Clamp to [0,1]
            
            # Extract reasoning
            reasoning = response_data.get('reasoning', '')
            if len(reasoning) > self.max_reasoning_length:
                reasoning = reasoning[:self.max_reasoning_length] + "..."
            
            confidence_level = self._get_confidence_level(confidence)
            
            return ModeSelectionResult(
                primary_mode=primary_mode,
                secondary_modes=secondary_modes,
                confidence=confidence,
                confidence_level=confidence_level,
                reasoning=reasoning,
                workflow_steps=[],  # Will be filled later
                estimated_performance={},  # Will be filled later
                fallback_used=False,
                selection_metadata={
                    "selection_method": "llm_based",
                    "llm_response_length": len(llm_response),
                    "key_factors": response_data.get('key_factors', []),
                    "timestamp": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            self.logger.error(f"Failed to parse LLM response: {e}")
            raise Exception(f"LLM response parsing failed: {e}")
    
    
    def _get_confidence_level(self, confidence: float) -> ConfidenceLevel:
        """Convert confidence score to confidence level enum"""
        
        if confidence >= 0.9:
            return ConfidenceLevel.VERY_HIGH
        elif confidence >= 0.7:
            return ConfidenceLevel.HIGH
        elif confidence >= 0.5:
            return ConfidenceLevel.MEDIUM
        elif confidence >= 0.3:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW
    
    def _generate_workflow_steps(
        self,
        primary_mode: AnalysisMode,
        secondary_modes: List[AnalysisMode],
        data_context: DataContext
    ) -> List[Dict[str, Any]]:
        """Generate workflow steps for the selected mode"""
        
        steps = []
        
        # Data preparation step
        steps.append({
            "step_id": "data_preparation",
            "step_type": "preparation",
            "operation": "prepare_data_for_analysis",
            "parameters": {
                "primary_format": self._get_primary_format(primary_mode),
                "secondary_formats": [self._get_primary_format(mode) for mode in secondary_modes]
            },
            "dependencies": [],
            "estimated_duration": self._estimate_step_duration("data_preparation", data_context),
            "required_resources": {"memory": "500MB", "cpu": "low"}
        })
        
        # Primary analysis step
        steps.append({
            "step_id": "primary_analysis",
            "step_type": "analysis",
            "operation": f"execute_{primary_mode.value}",
            "parameters": {
                "mode": primary_mode.value,
                "data_context": asdict(data_context)
            },
            "dependencies": ["data_preparation"],
            "estimated_duration": self._estimate_step_duration("primary_analysis", data_context),
            "required_resources": self._estimate_resources(primary_mode, data_context)
        })
        
        # Secondary analysis steps
        for i, mode in enumerate(secondary_modes):
            steps.append({
                "step_id": f"secondary_analysis_{i+1}",
                "step_type": "analysis",
                "operation": f"execute_{mode.value}",
                "parameters": {
                    "mode": mode.value,
                    "data_context": asdict(data_context)
                },
                "dependencies": ["data_preparation"],
                "estimated_duration": self._estimate_step_duration("secondary_analysis", data_context),
                "required_resources": self._estimate_resources(mode, data_context)
            })
        
        # Result aggregation step
        if secondary_modes:
            steps.append({
                "step_id": "result_aggregation",
                "step_type": "aggregation",
                "operation": "aggregate_multimodal_results",
                "parameters": {
                    "primary_mode": primary_mode.value,
                    "secondary_modes": [mode.value for mode in secondary_modes]
                },
                "dependencies": ["primary_analysis"] + [f"secondary_analysis_{i+1}" for i in range(len(secondary_modes))],
                "estimated_duration": self._estimate_step_duration("aggregation", data_context),
                "required_resources": {"memory": "200MB", "cpu": "medium"}
            })
        
        return steps
    
    def _get_primary_format(self, mode: AnalysisMode) -> str:
        """Get primary data format for analysis mode"""
        
        format_map = {
            AnalysisMode.GRAPH_ANALYSIS: "graph",
            AnalysisMode.TABLE_ANALYSIS: "table",
            AnalysisMode.VECTOR_ANALYSIS: "vector",
            AnalysisMode.HYBRID_GRAPH_TABLE: "graph",
            AnalysisMode.HYBRID_GRAPH_VECTOR: "graph",
            AnalysisMode.HYBRID_TABLE_VECTOR: "table",
            AnalysisMode.COMPREHENSIVE_MULTIMODAL: "multimodal"
        }
        
        return format_map.get(mode, "table")
    
    def _estimate_step_duration(self, step_type: str, data_context: DataContext) -> float:
        """Estimate duration for workflow step"""
        
        base_durations = {
            "data_preparation": 30.0,
            "primary_analysis": 120.0,
            "secondary_analysis": 90.0,
            "aggregation": 60.0
        }
        
        base_duration = base_durations.get(step_type, 60.0)
        
        # Scale based on data size
        size_factor = min(5.0, max(0.5, data_context.entity_count / 10000))
        complexity_factor = 1.0 + data_context.complexity_score
        
        return base_duration * size_factor * complexity_factor
    
    def _estimate_resources(self, mode: AnalysisMode, data_context: DataContext) -> Dict[str, str]:
        """Estimate resource requirements for analysis mode"""
        
        # Base resource requirements
        resource_map = {
            AnalysisMode.GRAPH_ANALYSIS: {"memory": "1GB", "cpu": "high"},
            AnalysisMode.TABLE_ANALYSIS: {"memory": "500MB", "cpu": "medium"},
            AnalysisMode.VECTOR_ANALYSIS: {"memory": "2GB", "cpu": "high"},
            AnalysisMode.COMPREHENSIVE_MULTIMODAL: {"memory": "4GB", "cpu": "very_high"}
        }
        
        return resource_map.get(mode, {"memory": "1GB", "cpu": "medium"})
    
    def _estimate_performance(
        self,
        primary_mode: AnalysisMode,
        data_context: DataContext
    ) -> Dict[str, Any]:
        """Estimate performance characteristics for selected mode"""
        
        # Estimate execution time
        base_times = {
            AnalysisMode.GRAPH_ANALYSIS: 300,
            AnalysisMode.TABLE_ANALYSIS: 120,
            AnalysisMode.VECTOR_ANALYSIS: 240,
            AnalysisMode.COMPREHENSIVE_MULTIMODAL: 600
        }
        
        base_time = base_times.get(primary_mode, 180)
        size_factor = data_context.entity_count / 1000
        execution_time = base_time * (1 + size_factor * 0.1)
        
        return {
            "estimated_execution_time": execution_time,
            "memory_requirements": self._estimate_resources(primary_mode, data_context)["memory"],
            "cpu_requirements": self._estimate_resources(primary_mode, data_context)["cpu"],
            "scalability": "high" if primary_mode in [AnalysisMode.TABLE_ANALYSIS, AnalysisMode.VECTOR_ANALYSIS] else "medium",
            "accuracy_expectation": "high" if data_context.complexity_score < 0.8 else "medium"
        }
    
    def _validate_selection(self, selection_result: ModeSelectionResult) -> bool:
        """Validate LLM selection result"""
        
        try:
            # Check required fields
            if not selection_result.primary_mode:
                return False
            
            if not isinstance(selection_result.confidence, (int, float)):
                return False
            
            if not 0.0 <= selection_result.confidence <= 1.0:
                return False
            
            if not selection_result.reasoning or len(selection_result.reasoning.strip()) < 10:
                return False
            
            # Check confidence threshold
            if selection_result.confidence < self.confidence_threshold:
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Selection validation failed: {e}")
            return False
    
    def _generate_cache_key(
        self,
        research_question: str,
        data_context: DataContext,
        preferences: Optional[Dict[str, Any]]
    ) -> str:
        """Generate cache key for mode selection"""
        
        # Create hash of inputs
        content = f"{research_question}|{asdict(data_context)}|{preferences or {}}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_cached_selection(self, cache_key: str) -> Optional[ModeSelectionResult]:
        """Get cached selection result"""
        return self._selection_cache.get(cache_key)
    
    def _cache_selection(self, cache_key: str, result: ModeSelectionResult) -> None:
        """Cache selection result"""
        
        # Limit cache size
        if len(self._selection_cache) > 1000:
            # Remove oldest entries
            keys_to_remove = list(self._selection_cache.keys())[:100]
            for key in keys_to_remove:
                del self._selection_cache[key]
        
        self._selection_cache[cache_key] = result
    
    def _hash_data_context(self, data_context: DataContext) -> str:
        """Generate hash of data context for metadata"""
        content = json.dumps(asdict(data_context), sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()
    
    def _initialize_llm_client(self):
        """Initialize LLM client from service manager"""
        try:
            # Try to get LLM service from service manager
            if hasattr(self.service_manager, 'get_llm_client'):
                llm_client = self.service_manager.get_llm_client()
                if llm_client:
                    self.logger.info("LLM client obtained from service manager")
                    return llm_client
            
            # Initialize real LLM service - NO FALLBACKS
            from .real_llm_service import RealLLMService
            
            # Try OpenAI first, then Anthropic
            for provider in ['openai', 'anthropic']:
                try:
                    llm_service = RealLLMService(provider=provider)
                    if llm_service.client:  # Check if client was initialized
                        self.logger.info(f"Initialized RealLLMService with {provider}")
                        return llm_service
                except Exception as e:
                    self.logger.warning(f"Failed to initialize {provider}: {e}")
                    continue
            
            # If we get here, no LLM service could be initialized
            raise RuntimeError("No LLM provider available. Please set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable.")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize LLM client: {e}")
            raise  # NO FALLBACKS - fail fast


def create_data_context(
    data_size: int,
    data_types: List[str],
    entity_count: int,
    relationship_count: int = 0,
    has_temporal_data: bool = False,
    has_spatial_data: bool = False,
    has_hierarchical_structure: bool = False,
    available_formats: Optional[List[str]] = None
) -> DataContext:
    """Helper function to create DataContext with calculated complexity score"""
    
    # Calculate complexity score based on various factors
    complexity_factors = []
    
    # Data size factor
    if data_size > 100000:
        complexity_factors.append(0.3)
    elif data_size > 10000:
        complexity_factors.append(0.2)
    else:
        complexity_factors.append(0.1)
    
    # Relationship density factor
    if entity_count > 0:
        relationship_density = relationship_count / entity_count
        if relationship_density > 5:
            complexity_factors.append(0.3)
        elif relationship_density > 2:
            complexity_factors.append(0.2)
        else:
            complexity_factors.append(0.1)
    
    # Data type variety factor
    type_variety = len(data_types) / 10  # Normalize by max expected types
    complexity_factors.append(min(0.2, type_variety))
    
    # Special data factors
    if has_temporal_data:
        complexity_factors.append(0.1)
    if has_spatial_data:
        complexity_factors.append(0.1)
    if has_hierarchical_structure:
        complexity_factors.append(0.1)
    
    complexity_score = min(1.0, sum(complexity_factors))
    
    return DataContext(
        data_size=data_size,
        data_types=data_types,
        entity_count=entity_count,
        relationship_count=relationship_count,
        has_temporal_data=has_temporal_data,
        has_spatial_data=has_spatial_data,
        has_hierarchical_structure=has_hierarchical_structure,
        complexity_score=complexity_score,
        available_formats=available_formats or ["graph", "table", "vector"]
    )