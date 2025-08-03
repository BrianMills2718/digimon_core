"""
Result Analyzer

Analyzes intermediate results from tool execution to inform adaptive decisions.
Provides quality assessment, pattern detection, and performance analysis.
"""

import logging
import statistics
from typing import Dict, List, Set, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import re
import json

logger = logging.getLogger(__name__)


class ResultQuality(Enum):
    """Quality levels for results"""
    EXCELLENT = "excellent"     # >0.9
    GOOD = "good"              # 0.7-0.9
    ACCEPTABLE = "acceptable"   # 0.5-0.7
    POOR = "poor"              # 0.3-0.5
    UNACCEPTABLE = "unacceptable"  # <0.3


class AnalysisType(Enum):
    """Types of result analysis"""
    QUALITY_ASSESSMENT = "quality_assessment"
    PATTERN_DETECTION = "pattern_detection"
    ANOMALY_DETECTION = "anomaly_detection"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    COMPLETENESS_CHECK = "completeness_check"
    CONSISTENCY_VALIDATION = "consistency_validation"


@dataclass
class QualityMetrics:
    """Quality metrics for result analysis"""
    completeness: float = 0.0      # How complete is the result
    accuracy: float = 0.0          # How accurate is the result
    consistency: float = 0.0       # How consistent is the result
    confidence: float = 0.0        # Tool-reported confidence
    relevance: float = 0.0         # How relevant to the question
    uniqueness: float = 0.0        # How unique/novel are the insights
    
    @property
    def overall_quality(self) -> float:
        """Calculate overall quality score"""
        weights = {
            'completeness': 0.25,
            'accuracy': 0.25,
            'consistency': 0.2,
            'confidence': 0.15,
            'relevance': 0.1,
            'uniqueness': 0.05
        }
        
        return (
            self.completeness * weights['completeness'] +
            self.accuracy * weights['accuracy'] +
            self.consistency * weights['consistency'] +
            self.confidence * weights['confidence'] +
            self.relevance * weights['relevance'] +
            self.uniqueness * weights['uniqueness']
        )
    
    @property
    def quality_level(self) -> ResultQuality:
        """Get quality level based on overall score"""
        score = self.overall_quality
        
        if score >= 0.9:
            return ResultQuality.EXCELLENT
        elif score >= 0.7:
            return ResultQuality.GOOD
        elif score >= 0.5:
            return ResultQuality.ACCEPTABLE
        elif score >= 0.3:
            return ResultQuality.POOR
        else:
            return ResultQuality.UNACCEPTABLE


@dataclass
class AnalysisResult:
    """Result of analyzing tool outputs"""
    analysis_type: AnalysisType
    overall_quality: float
    quality_metrics: QualityMetrics
    patterns_detected: List[Dict[str, Any]] = field(default_factory=list)
    anomalies_found: List[Dict[str, Any]] = field(default_factory=list)
    performance_indicators: Dict[str, float] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ComparisonResult:
    """Result of comparing multiple tool outputs"""
    similarity_score: float
    differences_found: List[Dict[str, Any]]
    consensus_items: List[Dict[str, Any]]
    conflicting_items: List[Dict[str, Any]]
    confidence_in_comparison: float


class ResultAnalyzer:
    """Analyzes intermediate results to inform adaptive execution decisions"""
    
    def __init__(self):
        """Initialize result analyzer"""
        self.logger = logger
        
        # Quality thresholds for different analysis types
        self.quality_thresholds = {
            'entity_extraction': 0.7,
            'relationship_analysis': 0.75,
            'sentiment_analysis': 0.6,
            'summarization': 0.8,
            'classification': 0.8
        }
        
        # Pattern detection rules
        self.pattern_rules = self._initialize_pattern_rules()
        
        # Anomaly detection thresholds
        self.anomaly_thresholds = {
            'confidence_drop': 0.3,    # Flag if confidence drops by >30%
            'result_size_variance': 3.0, # Flag if result size varies by >3x
            'processing_time_spike': 2.0  # Flag if processing time spikes >2x
        }
        
        self.logger.info("Initialized result analyzer with quality assessment capabilities")
    
    async def analyze_result_quality(self, results: Dict[str, Any]) -> AnalysisResult:
        """Analyze the quality of tool execution results"""
        
        self.logger.debug(f"Analyzing quality of results from {len(results)} tools")
        
        # Calculate quality metrics
        quality_metrics = await self._calculate_quality_metrics(results)
        
        # Detect patterns in results
        patterns = await self._detect_patterns(results)
        
        # Check for anomalies
        anomalies = await self._detect_anomalies(results)
        
        # Analyze performance indicators
        performance = await self._analyze_performance_indicators(results)
        
        # Generate recommendations
        recommendations = await self._generate_quality_recommendations(quality_metrics, patterns, anomalies)
        
        analysis_result = AnalysisResult(
            analysis_type=AnalysisType.QUALITY_ASSESSMENT,
            overall_quality=quality_metrics.overall_quality,
            quality_metrics=quality_metrics,
            patterns_detected=patterns,
            anomalies_found=anomalies,
            performance_indicators=performance,
            recommendations=recommendations,
            confidence=self._calculate_analysis_confidence(quality_metrics, patterns, anomalies)
        )
        
        self.logger.info(f"Quality analysis complete: {quality_metrics.quality_level.value} "
                        f"({quality_metrics.overall_quality:.2f})")
        
        return analysis_result
    
    async def compare_tool_outputs(self, results1: Dict[str, Any], 
                                 results2: Dict[str, Any]) -> ComparisonResult:
        """Compare outputs from different tools or executions"""
        
        self.logger.debug("Comparing tool outputs for consistency analysis")
        
        # Extract comparable elements
        elements1 = self._extract_comparable_elements(results1)
        elements2 = self._extract_comparable_elements(results2)
        
        # Calculate similarity
        similarity = self._calculate_similarity(elements1, elements2)
        
        # Find differences and consensus
        differences, consensus, conflicts = self._analyze_differences(elements1, elements2)
        
        # Calculate confidence in comparison
        comparison_confidence = self._calculate_comparison_confidence(
            elements1, elements2, similarity
        )
        
        return ComparisonResult(
            similarity_score=similarity,
            differences_found=differences,
            consensus_items=consensus,
            conflicting_items=conflicts,
            confidence_in_comparison=comparison_confidence
        )
    
    async def analyze_execution_patterns(self, execution_history: List[Dict[str, Any]]) -> AnalysisResult:
        """Analyze patterns in execution history"""
        
        self.logger.debug(f"Analyzing execution patterns from {len(execution_history)} steps")
        
        # Analyze timing patterns
        timing_patterns = self._analyze_timing_patterns(execution_history)
        
        # Analyze success/failure patterns
        success_patterns = self._analyze_success_patterns(execution_history)
        
        # Analyze quality trends
        quality_trends = self._analyze_quality_trends(execution_history)
        
        # Detect performance bottlenecks
        bottlenecks = self._detect_performance_bottlenecks(execution_history)
        
        patterns = timing_patterns + success_patterns + quality_trends + bottlenecks
        
        return AnalysisResult(
            analysis_type=AnalysisType.PATTERN_DETECTION,
            overall_quality=0.8,  # Pattern analysis doesn't have inherent quality
            quality_metrics=QualityMetrics(completeness=1.0, accuracy=0.8),
            patterns_detected=patterns,
            confidence=0.9
        )
    
    async def detect_result_anomalies(self, current_results: Dict[str, Any],
                                    historical_results: List[Dict[str, Any]]) -> AnalysisResult:
        """Detect anomalies in current results compared to historical data"""
        
        self.logger.debug("Detecting result anomalies against historical data")
        
        anomalies = []
        
        # Confidence anomalies
        confidence_anomalies = self._detect_confidence_anomalies(current_results, historical_results)
        anomalies.extend(confidence_anomalies)
        
        # Size anomalies
        size_anomalies = self._detect_size_anomalies(current_results, historical_results)
        anomalies.extend(size_anomalies)
        
        # Content anomalies
        content_anomalies = self._detect_content_anomalies(current_results, historical_results)
        anomalies.extend(content_anomalies)
        
        # Performance anomalies
        performance_anomalies = self._detect_performance_anomalies(current_results, historical_results)
        anomalies.extend(performance_anomalies)
        
        return AnalysisResult(
            analysis_type=AnalysisType.ANOMALY_DETECTION,
            overall_quality=0.7,  # Quality based on anomaly severity
            quality_metrics=QualityMetrics(completeness=1.0, accuracy=0.7),
            anomalies_found=anomalies,
            confidence=0.8
        )
    
    async def _calculate_quality_metrics(self, results: Dict[str, Any]) -> QualityMetrics:
        """Calculate comprehensive quality metrics"""
        
        completeness = self._assess_completeness(results)
        accuracy = self._assess_accuracy(results)
        consistency = self._assess_consistency(results)
        confidence = self._extract_confidence_scores(results)
        relevance = self._assess_relevance(results)
        uniqueness = self._assess_uniqueness(results)
        
        return QualityMetrics(
            completeness=completeness,
            accuracy=accuracy,
            consistency=consistency,
            confidence=confidence,
            relevance=relevance,
            uniqueness=uniqueness
        )
    
    def _assess_completeness(self, results: Dict[str, Any]) -> float:
        """Assess how complete the results are"""
        
        total_tools = len(results)
        if total_tools == 0:
            return 0.0
        
        # Count tools with meaningful outputs
        tools_with_outputs = 0
        
        for tool_id, tool_result in results.items():
            if isinstance(tool_result, dict):
                # Check if tool produced meaningful output
                if 'outputs' in tool_result or 'result' in tool_result:
                    tools_with_outputs += 1
                elif 'success' in tool_result and tool_result['success']:
                    tools_with_outputs += 1
        
        return tools_with_outputs / total_tools
    
    def _assess_accuracy(self, results: Dict[str, Any]) -> float:
        """Assess accuracy of results based on confidence scores and validation"""
        
        confidence_scores = []
        
        for tool_id, tool_result in results.items():
            if isinstance(tool_result, dict):
                # Extract confidence scores
                if 'confidence' in tool_result:
                    confidence_scores.append(tool_result['confidence'])
                elif 'outputs' in tool_result:
                    outputs = tool_result['outputs']
                    if isinstance(outputs, dict):
                        for key, value in outputs.items():
                            if 'confidence' in str(key).lower() and isinstance(value, (int, float)):
                                confidence_scores.append(float(value))
        
        if confidence_scores:
            return statistics.mean(confidence_scores)
        else:
            return 0.5  # Default moderate accuracy if no confidence scores
    
    def _assess_consistency(self, results: Dict[str, Any]) -> float:
        """Assess consistency across tool results"""
        
        if len(results) < 2:
            return 1.0  # Single result is always consistent with itself
        
        # Extract comparable elements for consistency check
        tool_confidences = []
        result_sizes = []
        
        for tool_id, tool_result in results.items():
            if isinstance(tool_result, dict):
                # Extract confidence
                if 'confidence' in tool_result:
                    tool_confidences.append(tool_result['confidence'])
                
                # Estimate result size
                result_size = self._estimate_result_size(tool_result)
                if result_size > 0:
                    result_sizes.append(result_size)
        
        consistency_scores = []
        
        # Confidence consistency
        if len(tool_confidences) > 1:
            confidence_variance = statistics.variance(tool_confidences)
            confidence_consistency = max(0, 1.0 - confidence_variance)
            consistency_scores.append(confidence_consistency)
        
        # Size consistency
        if len(result_sizes) > 1:
            size_mean = statistics.mean(result_sizes)
            if size_mean > 0:
                size_cv = statistics.stdev(result_sizes) / size_mean  # Coefficient of variation
                size_consistency = max(0, 1.0 - min(size_cv, 1.0))
                consistency_scores.append(size_consistency)
        
        return statistics.mean(consistency_scores) if consistency_scores else 0.8
    
    def _extract_confidence_scores(self, results: Dict[str, Any]) -> float:
        """Extract and average confidence scores from results"""
        
        confidence_scores = []
        
        for tool_id, tool_result in results.items():
            if isinstance(tool_result, dict):
                # Direct confidence score
                if 'confidence' in tool_result:
                    confidence_scores.append(tool_result['confidence'])
                
                # Confidence in outputs
                if 'outputs' in tool_result and isinstance(tool_result['outputs'], dict):
                    for key, value in tool_result['outputs'].items():
                        if 'confidence' in key.lower() and isinstance(value, (int, float)):
                            confidence_scores.append(float(value))
        
        return statistics.mean(confidence_scores) if confidence_scores else 0.5
    
    def _assess_relevance(self, results: Dict[str, Any]) -> float:
        """Assess relevance of results to the original question"""
        
        # Simple heuristic: tools that produced results are more relevant
        relevant_tools = 0
        total_tools = len(results)
        
        for tool_id, tool_result in results.items():
            if isinstance(tool_result, dict) and tool_result.get('success', False):
                relevant_tools += 1
        
        return relevant_tools / total_tools if total_tools > 0 else 0.0
    
    def _assess_uniqueness(self, results: Dict[str, Any]) -> float:
        """Assess uniqueness/novelty of insights"""
        
        # Simple heuristic: more diverse tool outputs suggest more unique insights
        unique_output_types = set()
        
        for tool_id, tool_result in results.items():
            if isinstance(tool_result, dict) and 'outputs' in tool_result:
                outputs = tool_result['outputs']
                if isinstance(outputs, dict):
                    unique_output_types.update(outputs.keys())
        
        # Normalize by expected output diversity
        max_expected_types = len(results) * 3  # Assume ~3 output types per tool
        uniqueness = len(unique_output_types) / max_expected_types if max_expected_types > 0 else 0
        
        return min(uniqueness, 1.0)
    
    def _estimate_result_size(self, tool_result: Dict[str, Any]) -> int:
        """Estimate the size/amount of data in a tool result"""
        
        try:
            result_str = json.dumps(tool_result)
            return len(result_str)
        except:
            return len(str(tool_result))
    
    async def _detect_patterns(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect patterns in tool results"""
        
        patterns = []
        
        # High confidence pattern
        high_confidence_tools = []
        for tool_id, tool_result in results.items():
            if isinstance(tool_result, dict):
                confidence = tool_result.get('confidence', 0)
                if isinstance(confidence, (int, float)) and confidence > 0.8:
                    high_confidence_tools.append(tool_id)
        
        if len(high_confidence_tools) >= 2:
            patterns.append({
                'type': 'high_confidence_cluster',
                'tools': high_confidence_tools,
                'description': f'{len(high_confidence_tools)} tools showing high confidence',
                'impact': 'positive'
            })
        
        # Low confidence pattern
        low_confidence_tools = []
        for tool_id, tool_result in results.items():
            if isinstance(tool_result, dict):
                confidence = tool_result.get('confidence', 1.0)
                if isinstance(confidence, (int, float)) and confidence < 0.5:
                    low_confidence_tools.append(tool_id)
        
        if len(low_confidence_tools) >= 2:
            patterns.append({
                'type': 'low_confidence_cluster',
                'tools': low_confidence_tools,
                'description': f'{len(low_confidence_tools)} tools showing low confidence',
                'impact': 'negative'
            })
        
        return patterns
    
    async def _detect_anomalies(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect anomalies in current results"""
        
        anomalies = []
        
        # Confidence anomalies
        confidences = []
        for tool_id, tool_result in results.items():
            if isinstance(tool_result, dict) and 'confidence' in tool_result:
                conf = tool_result['confidence']
                if isinstance(conf, (int, float)):
                    confidences.append((tool_id, conf))
        
        if len(confidences) > 1:
            conf_values = [c[1] for c in confidences]
            mean_conf = statistics.mean(conf_values)
            
            for tool_id, conf in confidences:
                if abs(conf - mean_conf) > 0.3:  # Significant deviation
                    anomalies.append({
                        'type': 'confidence_anomaly',
                        'tool_id': tool_id,
                        'value': conf,
                        'expected': mean_conf,
                        'severity': 'high' if abs(conf - mean_conf) > 0.5 else 'medium'
                    })
        
        return anomalies
    
    async def _analyze_performance_indicators(self, results: Dict[str, Any]) -> Dict[str, float]:
        """Analyze performance indicators from results"""
        
        indicators = {}
        
        # Execution time analysis
        execution_times = []
        for tool_id, tool_result in results.items():
            if isinstance(tool_result, dict) and 'execution_time' in tool_result:
                exec_time = tool_result['execution_time']
                if isinstance(exec_time, (int, float)):
                    execution_times.append(exec_time)
        
        if execution_times:
            indicators['avg_execution_time'] = statistics.mean(execution_times)
            indicators['total_execution_time'] = sum(execution_times)
            indicators['max_execution_time'] = max(execution_times)
        
        # Success rate
        successful_tools = sum(
            1 for tool_result in results.values()
            if isinstance(tool_result, dict) and tool_result.get('success', False)
        )
        
        indicators['success_rate'] = successful_tools / len(results) if results else 0
        
        return indicators
    
    async def _generate_quality_recommendations(self, quality_metrics: QualityMetrics,
                                              patterns: List[Dict[str, Any]],
                                              anomalies: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on quality analysis"""
        
        recommendations = []
        
        # Quality-based recommendations
        if quality_metrics.overall_quality < 0.5:
            recommendations.append("Overall result quality is poor - consider retrying with different parameters")
        
        if quality_metrics.completeness < 0.7:
            recommendations.append("Results appear incomplete - verify all required tools executed successfully")
        
        if quality_metrics.consistency < 0.6:
            recommendations.append("Results show low consistency - investigate tool parameter differences")
        
        if quality_metrics.confidence < 0.6:
            recommendations.append("Low confidence scores detected - consider additional validation steps")
        
        # Pattern-based recommendations
        for pattern in patterns:
            if pattern['impact'] == 'negative':
                recommendations.append(f"Negative pattern detected: {pattern['description']} - investigate affected tools")
        
        # Anomaly-based recommendations
        high_severity_anomalies = [a for a in anomalies if a.get('severity') == 'high']
        if high_severity_anomalies:
            recommendations.append(f"High-severity anomalies detected in {len(high_severity_anomalies)} cases - manual review recommended")
        
        return recommendations
    
    def _calculate_analysis_confidence(self, quality_metrics: QualityMetrics,
                                     patterns: List[Dict[str, Any]],
                                     anomalies: List[Dict[str, Any]]) -> float:
        """Calculate confidence in the analysis itself"""
        
        base_confidence = 0.8
        
        # Reduce confidence for poor data quality
        if quality_metrics.completeness < 0.5:
            base_confidence -= 0.2
        
        # Reduce confidence for many anomalies
        if len(anomalies) > 3:
            base_confidence -= 0.1
        
        # Increase confidence for clear patterns
        positive_patterns = [p for p in patterns if p.get('impact') == 'positive']
        if len(positive_patterns) > 2:
            base_confidence += 0.1
        
        return max(0.1, min(1.0, base_confidence))
    
    def _initialize_pattern_rules(self) -> List[Dict[str, Any]]:
        """Initialize pattern detection rules"""
        
        return [
            {
                'name': 'confidence_convergence',
                'description': 'Multiple tools showing similar confidence levels',
                'detector': lambda results: self._detect_confidence_convergence(results)
            },
            {
                'name': 'execution_time_pattern',
                'description': 'Pattern in execution times',
                'detector': lambda results: self._detect_execution_time_patterns(results)
            }
        ]
    
    def _detect_confidence_convergence(self, results: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Detect if multiple tools converge on similar confidence levels"""
        
        confidences = []
        for tool_result in results.values():
            if isinstance(tool_result, dict) and 'confidence' in tool_result:
                conf = tool_result['confidence']
                if isinstance(conf, (int, float)):
                    confidences.append(conf)
        
        if len(confidences) >= 3:
            variance = statistics.variance(confidences)
            if variance < 0.01:  # Very low variance
                return {
                    'type': 'confidence_convergence',
                    'tools_count': len(confidences),
                    'convergence_value': statistics.mean(confidences),
                    'variance': variance
                }
        
        return None
    
    def _detect_execution_time_patterns(self, results: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Detect patterns in execution times"""
        
        times = []
        for tool_result in results.values():
            if isinstance(tool_result, dict) and 'execution_time' in tool_result:
                time_val = tool_result['execution_time']
                if isinstance(time_val, (int, float)):
                    times.append(time_val)
        
        if len(times) >= 3:
            mean_time = statistics.mean(times)
            if all(abs(t - mean_time) / mean_time < 0.2 for t in times):  # Within 20% of mean
                return {
                    'type': 'consistent_execution_times',
                    'tools_count': len(times),
                    'mean_time': mean_time,
                    'consistency': True
                }
        
        return None
    
    def _extract_comparable_elements(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract elements that can be compared between different result sets"""
        
        comparable = {}
        
        for tool_id, tool_result in results.items():
            if isinstance(tool_result, dict):
                # Extract confidence
                if 'confidence' in tool_result:
                    comparable[f'{tool_id}_confidence'] = tool_result['confidence']
                
                # Extract success status
                if 'success' in tool_result:
                    comparable[f'{tool_id}_success'] = tool_result['success']
                
                # Extract execution time
                if 'execution_time' in tool_result:
                    comparable[f'{tool_id}_time'] = tool_result['execution_time']
        
        return comparable
    
    def _calculate_similarity(self, elements1: Dict[str, Any], 
                            elements2: Dict[str, Any]) -> float:
        """Calculate similarity between two sets of elements"""
        
        common_keys = set(elements1.keys()) & set(elements2.keys())
        if not common_keys:
            return 0.0
        
        similarities = []
        
        for key in common_keys:
            val1, val2 = elements1[key], elements2[key]
            
            if isinstance(val1, bool) and isinstance(val2, bool):
                # Boolean similarity
                similarities.append(1.0 if val1 == val2 else 0.0)
            elif isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                # Numeric similarity
                if val1 == 0 and val2 == 0:
                    similarities.append(1.0)
                else:
                    max_val = max(abs(val1), abs(val2), 1.0)
                    similarities.append(1.0 - abs(val1 - val2) / max_val)
        
        return statistics.mean(similarities) if similarities else 0.0
    
    def _analyze_differences(self, elements1: Dict[str, Any], 
                           elements2: Dict[str, Any]) -> Tuple[List, List, List]:
        """Analyze differences, consensus, and conflicts between element sets"""
        
        differences = []
        consensus = []
        conflicts = []
        
        all_keys = set(elements1.keys()) | set(elements2.keys())
        
        for key in all_keys:
            val1 = elements1.get(key)
            val2 = elements2.get(key)
            
            if val1 is None or val2 is None:
                differences.append({
                    'key': key,
                    'type': 'missing',
                    'value1': val1,
                    'value2': val2
                })
            elif val1 == val2:
                consensus.append({
                    'key': key,
                    'value': val1
                })
            else:
                conflicts.append({
                    'key': key,
                    'value1': val1,
                    'value2': val2,
                    'type': 'value_conflict'
                })
        
        return differences, consensus, conflicts
    
    def _calculate_comparison_confidence(self, elements1: Dict[str, Any],
                                       elements2: Dict[str, Any],
                                       similarity: float) -> float:
        """Calculate confidence in the comparison result"""
        
        # Base confidence on similarity and data availability
        data_coverage = len(set(elements1.keys()) & set(elements2.keys())) / max(len(elements1), len(elements2), 1)
        
        confidence = (similarity * 0.7) + (data_coverage * 0.3)
        
        return min(1.0, max(0.0, confidence))
    
    def _analyze_timing_patterns(self, execution_history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze timing patterns in execution history"""
        
        patterns = []
        
        if len(execution_history) < 3:
            return patterns
        
        # Extract execution times
        times = []
        for step in execution_history:
            if 'execution_time' in step and isinstance(step['execution_time'], (int, float)):
                times.append(step['execution_time'])
        
        if len(times) >= 3:
            # Check for increasing execution times
            increasing = all(times[i] <= times[i+1] for i in range(len(times)-1))
            decreasing = all(times[i] >= times[i+1] for i in range(len(times)-1))
            
            if increasing:
                patterns.append({
                    'type': 'increasing_execution_times',
                    'description': 'Execution times are increasing over time',
                    'impact': 'negative',
                    'data': times
                })
            elif decreasing:
                patterns.append({
                    'type': 'decreasing_execution_times',
                    'description': 'Execution times are decreasing over time',
                    'impact': 'positive',
                    'data': times
                })
        
        return patterns
    
    def _analyze_success_patterns(self, execution_history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze success/failure patterns"""
        
        patterns = []
        
        # Extract success status
        successes = []
        for step in execution_history:
            if 'success' in step:
                successes.append(step['success'])
        
        if len(successes) >= 3:
            success_rate = sum(successes) / len(successes)
            
            if success_rate == 1.0:
                patterns.append({
                    'type': 'perfect_success_rate',
                    'description': 'All execution steps successful',
                    'impact': 'positive',
                    'success_rate': success_rate
                })
            elif success_rate < 0.5:
                patterns.append({
                    'type': 'high_failure_rate',
                    'description': f'High failure rate detected ({success_rate:.1%})',
                    'impact': 'negative',
                    'success_rate': success_rate
                })
        
        return patterns
    
    def _analyze_quality_trends(self, execution_history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze quality trends over execution"""
        
        patterns = []
        
        # This would analyze quality metrics over time if available
        # For now, return empty list as quality metrics may not be in execution history
        
        return patterns
    
    def _detect_performance_bottlenecks(self, execution_history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect performance bottlenecks in execution"""
        
        bottlenecks = []
        
        # Find steps that took significantly longer than average
        times = []
        step_info = []
        
        for step in execution_history:
            if 'execution_time' in step and 'step_id' in step:
                time_val = step['execution_time']
                if isinstance(time_val, (int, float)):
                    times.append(time_val)
                    step_info.append((step['step_id'], time_val))
        
        if len(times) >= 3:
            mean_time = statistics.mean(times)
            threshold = mean_time * 2.0  # Steps taking >2x average time
            
            slow_steps = [(step_id, time_val) for step_id, time_val in step_info if time_val > threshold]
            
            if slow_steps:
                bottlenecks.append({
                    'type': 'execution_time_bottleneck',
                    'description': f'{len(slow_steps)} steps taking significantly longer than average',
                    'impact': 'negative',
                    'slow_steps': slow_steps,
                    'threshold': threshold,
                    'average_time': mean_time
                })
        
        return bottlenecks
    
    def _detect_confidence_anomalies(self, current: Dict[str, Any], 
                                   historical: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect confidence anomalies compared to historical data"""
        
        anomalies = []
        
        # Extract current confidences
        current_confidences = {}
        for tool_id, result in current.items():
            if isinstance(result, dict) and 'confidence' in result:
                current_confidences[tool_id] = result['confidence']
        
        # Extract historical confidences
        historical_confidences = {}
        for hist_result in historical:
            for tool_id, result in hist_result.items():
                if isinstance(result, dict) and 'confidence' in result:
                    if tool_id not in historical_confidences:
                        historical_confidences[tool_id] = []
                    historical_confidences[tool_id].append(result['confidence'])
        
        # Compare current to historical averages
        for tool_id, current_conf in current_confidences.items():
            if tool_id in historical_confidences and len(historical_confidences[tool_id]) >= 3:
                hist_mean = statistics.mean(historical_confidences[tool_id])
                
                if abs(current_conf - hist_mean) > self.anomaly_thresholds['confidence_drop']:
                    anomalies.append({
                        'type': 'confidence_anomaly',
                        'tool_id': tool_id,
                        'current_confidence': current_conf,
                        'historical_average': hist_mean,
                        'deviation': abs(current_conf - hist_mean),
                        'severity': 'high' if abs(current_conf - hist_mean) > 0.5 else 'medium'
                    })
        
        return anomalies
    
    def _detect_size_anomalies(self, current: Dict[str, Any],
                             historical: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect result size anomalies"""
        
        anomalies = []
        
        # Calculate current result sizes
        current_sizes = {}
        for tool_id, result in current.items():
            current_sizes[tool_id] = self._estimate_result_size(result)
        
        # Calculate historical sizes
        historical_sizes = {}
        for hist_result in historical:
            for tool_id, result in hist_result.items():
                if tool_id not in historical_sizes:
                    historical_sizes[tool_id] = []
                historical_sizes[tool_id].append(self._estimate_result_size(result))
        
        # Compare sizes
        for tool_id, current_size in current_sizes.items():
            if tool_id in historical_sizes and len(historical_sizes[tool_id]) >= 3:
                hist_mean = statistics.mean(historical_sizes[tool_id])
                
                if hist_mean > 0:
                    size_ratio = current_size / hist_mean
                    
                    if size_ratio > self.anomaly_thresholds['result_size_variance'] or size_ratio < (1.0 / self.anomaly_thresholds['result_size_variance']):
                        anomalies.append({
                            'type': 'size_anomaly',
                            'tool_id': tool_id,
                            'current_size': current_size,
                            'historical_average': hist_mean,
                            'size_ratio': size_ratio,
                            'severity': 'high' if size_ratio > 5.0 or size_ratio < 0.2 else 'medium'
                        })
        
        return anomalies
    
    def _detect_content_anomalies(self, current: Dict[str, Any],
                                historical: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect content-based anomalies"""
        
        # Placeholder for content analysis
        # In a real implementation, this might analyze text patterns, entity distributions, etc.
        return []
    
    def _detect_performance_anomalies(self, current: Dict[str, Any],
                                    historical: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect performance anomalies"""
        
        anomalies = []
        
        # Extract current execution times
        current_times = {}
        for tool_id, result in current.items():
            if isinstance(result, dict) and 'execution_time' in result:
                current_times[tool_id] = result['execution_time']
        
        # Extract historical times
        historical_times = {}
        for hist_result in historical:
            for tool_id, result in hist_result.items():
                if isinstance(result, dict) and 'execution_time' in result:
                    if tool_id not in historical_times:
                        historical_times[tool_id] = []
                    historical_times[tool_id].append(result['execution_time'])
        
        # Compare execution times
        for tool_id, current_time in current_times.items():
            if tool_id in historical_times and len(historical_times[tool_id]) >= 3:
                hist_mean = statistics.mean(historical_times[tool_id])
                
                if hist_mean > 0:
                    time_ratio = current_time / hist_mean
                    
                    if time_ratio > self.anomaly_thresholds['processing_time_spike']:
                        anomalies.append({
                            'type': 'performance_anomaly',
                            'tool_id': tool_id,
                            'current_time': current_time,
                            'historical_average': hist_mean,
                            'time_ratio': time_ratio,
                            'severity': 'high' if time_ratio > 3.0 else 'medium'
                        })
        
        return anomalies