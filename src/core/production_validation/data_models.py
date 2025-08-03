"""
Production Validation Data Models

Data structures for production validation results and metrics.
"""

import uuid
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from enum import Enum


class ProductionReadinessLevel(Enum):
    """Production readiness levels"""
    PRODUCTION_READY = "production_ready"
    NEAR_PRODUCTION = "near_production" 
    DEVELOPMENT_READY = "development_ready"
    DEVELOPMENT = "development"
    FAILED = "failed"
    STABILITY_FAILED = "stability_failed"


class StabilityClass(Enum):
    """Stability classification levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    MARGINAL = "marginal"
    POOR = "poor"


class ComponentStatus(Enum):
    """Component test status"""
    WORKING = "working"
    UNSTABLE = "unstable"
    FAILED = "failed"
    NOT_AVAILABLE = "not_available"


@dataclass
class PerformanceMetrics:
    """Performance metrics for operations"""
    average_time: float
    max_time: float
    min_time: float
    variance: float
    total_operations: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "average_time": self.average_time,
            "max_time": self.max_time,
            "min_time": self.min_time,
            "variance": self.variance,
            "total_operations": self.total_operations
        }


@dataclass
class ErrorAnalysis:
    """Error analysis for failed operations"""
    error_patterns: Dict[str, int]
    total_errors: int
    error_rate: float
    most_common_error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "error_patterns": self.error_patterns,
            "total_errors": self.total_errors,
            "error_rate": self.error_rate,
            "most_common_error": self.most_common_error
        }


@dataclass
class StabilityTestResult:
    """Result of a stability test"""
    test_name: str
    successful_operations: int
    total_attempts: int
    stability_score: float
    stability_class: StabilityClass
    performance_metrics: PerformanceMetrics
    error_analysis: ErrorAnalysis
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "test_name": self.test_name,
            "successful_operations": self.successful_operations,
            "total_attempts": self.total_attempts,
            "stability_score": self.stability_score,
            "stability_class": self.stability_class.value,
            "performance_metrics": self.performance_metrics.to_dict(),
            "error_analysis": self.error_analysis.to_dict(),
            "recommendations": self.recommendations
        }


@dataclass 
class ComponentTestResult:
    """Result of a component test"""
    component_name: str
    status: ComponentStatus
    stability_score: float
    response_time: float
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "component_name": self.component_name,
            "status": self.status.value,
            "stability_score": self.stability_score,
            "response_time": self.response_time,
            "error_message": self.error_message,
            "metadata": self.metadata
        }


@dataclass
class DependencyCheckResult:
    """Result of dependency checking"""
    dependency_name: str
    available: bool
    version: Optional[str] = None
    error_message: Optional[str] = None
    check_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "dependency_name": self.dependency_name,
            "available": self.available,
            "version": self.version,
            "error_message": self.error_message,
            "check_time": self.check_time
        }


@dataclass
class ValidationResult:
    """Complete validation result"""
    validation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    dependency_checks: Dict[str, DependencyCheckResult] = field(default_factory=dict)
    stability_tests: Dict[str, StabilityTestResult] = field(default_factory=dict)
    component_tests: Dict[str, ComponentTestResult] = field(default_factory=dict)
    readiness_percentage: float = 0.0
    overall_status: ProductionReadinessLevel = ProductionReadinessLevel.FAILED
    critical_issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    stability_gate_passed: bool = False
    overall_stability: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "validation_id": self.validation_id,
            "timestamp": self.timestamp,
            "dependency_checks": {
                name: result.to_dict() for name, result in self.dependency_checks.items()
            },
            "stability_tests": {
                name: result.to_dict() for name, result in self.stability_tests.items()
            },
            "component_tests": {
                name: result.to_dict() for name, result in self.component_tests.items()
            },
            "readiness_percentage": self.readiness_percentage,
            "overall_status": self.overall_status.value,
            "critical_issues": self.critical_issues,
            "recommendations": self.recommendations,
            "stability_gate_passed": self.stability_gate_passed,
            "overall_stability": self.overall_stability
        }
    
    def add_dependency_result(self, name: str, result: DependencyCheckResult):
        """Add dependency check result"""
        self.dependency_checks[name] = result
    
    def add_stability_result(self, name: str, result: StabilityTestResult):
        """Add stability test result"""
        self.stability_tests[name] = result
    
    def add_component_result(self, name: str, result: ComponentTestResult):
        """Add component test result"""
        self.component_tests[name] = result
    
    def all_dependencies_available(self) -> bool:
        """Check if all dependencies are available"""
        return all(result.available for result in self.dependency_checks.values())
    
    def get_missing_dependencies(self) -> List[str]:
        """Get list of missing dependency names"""
        return [
            name for name, result in self.dependency_checks.items() 
            if not result.available
        ]
    
    def calculate_overall_stability(self) -> float:
        """Calculate overall stability score from all stability tests"""
        if not self.stability_tests:
            return 0.0
        
        scores = [result.stability_score for result in self.stability_tests.values()]
        self.overall_stability = sum(scores) / len(scores) if scores else 0.0
        return self.overall_stability
    
    def update_stability_gate(self, threshold: float = 0.80) -> bool:
        """Update stability gate status based on threshold"""
        overall_stability = self.calculate_overall_stability()
        self.stability_gate_passed = overall_stability >= threshold
        return self.stability_gate_passed


@dataclass
class ProductionMetrics:
    """Production readiness metrics"""
    database_score: float = 0.0
    tool_score: float = 0.0
    service_score: float = 0.0
    configuration_score: float = 0.0
    overall_score: float = 0.0
    
    def calculate_overall_score(self):
        """Calculate overall score from component scores"""
        scores = [
            self.database_score,
            self.tool_score, 
            self.service_score,
            self.configuration_score
        ]
        self.overall_score = sum(scores) / len(scores) if scores else 0.0
        return self.overall_score
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "database_score": self.database_score,
            "tool_score": self.tool_score,
            "service_score": self.service_score,
            "configuration_score": self.configuration_score,
            "overall_score": self.overall_score
        }