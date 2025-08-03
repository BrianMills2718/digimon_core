"""
Readiness Calculation Components

Calculate production readiness scores and provide detailed analysis.
"""

import logging
from typing import Dict, Any, List
from statistics import mean

from .data_models import (
    ValidationResult, ComponentTestResult, StabilityTestResult,
    ProductionReadinessLevel, ProductionMetrics, ComponentStatus
)

logger = logging.getLogger(__name__)


class ReadinessCalculator:
    """Calculate production readiness scores"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Component weight factors for overall score
        self.component_weights = {
            "database": 0.30,
            "tools": 0.25,
            "services": 0.25,
            "configuration": 0.20
        }
        
        # Readiness thresholds
        self.readiness_thresholds = {
            ProductionReadinessLevel.PRODUCTION_READY: 95.0,
            ProductionReadinessLevel.NEAR_PRODUCTION: 85.0,
            ProductionReadinessLevel.DEVELOPMENT_READY: 70.0,
            ProductionReadinessLevel.DEVELOPMENT: 50.0
        }
    
    def calculate_component_readiness(self, component_tests: Dict[str, ComponentTestResult]) -> ProductionMetrics:
        """Calculate readiness scores for each component category"""
        metrics = ProductionMetrics()
        
        # Database score
        if "database" in component_tests:
            db_result = component_tests["database"]
            metrics.database_score = self._calculate_component_score(db_result)
        
        # Tool score
        if "tools" in component_tests:
            tool_result = component_tests["tools"]
            metrics.tool_score = self._calculate_component_score(tool_result)
        
        # Service score  
        if "services" in component_tests:
            service_result = component_tests["services"]
            metrics.service_score = self._calculate_component_score(service_result)
        
        # Configuration score (derived from multiple sources)
        config_score = self._calculate_configuration_score(component_tests)
        metrics.configuration_score = config_score
        
        # Calculate overall score
        metrics.calculate_overall_score()
        
        return metrics
    
    def _calculate_component_score(self, result: ComponentTestResult) -> float:
        """Calculate score for individual component"""
        base_score = result.stability_score * 100
        
        # Apply status penalties
        if result.status == ComponentStatus.WORKING:
            status_multiplier = 1.0
        elif result.status == ComponentStatus.UNSTABLE:
            status_multiplier = 0.7
        elif result.status == ComponentStatus.FAILED:
            status_multiplier = 0.1
        else:  # NOT_AVAILABLE
            status_multiplier = 0.0
        
        # Apply response time penalties
        response_time_multiplier = 1.0
        if result.response_time > 5.0:  # Very slow
            response_time_multiplier = 0.6
        elif result.response_time > 2.0:  # Slow
            response_time_multiplier = 0.8
        elif result.response_time > 1.0:  # Acceptable
            response_time_multiplier = 0.9
        
        final_score = base_score * status_multiplier * response_time_multiplier
        return min(100.0, max(0.0, final_score))
    
    def _calculate_configuration_score(self, component_tests: Dict[str, ComponentTestResult]) -> float:
        """Calculate configuration score from available components"""
        # Configuration score is derived from overall system health
        scores = []
        
        for result in component_tests.values():
            if result.stability_score > 0:
                scores.append(result.stability_score * 100)
        
        if scores:
            return mean(scores)
        else:
            return 0.0
    
    def calculate_stability_weighted_readiness(self, 
                                            stability_results: Dict[str, StabilityTestResult],
                                            component_results: Dict[str, ComponentTestResult]) -> float:
        """Calculate readiness with stability test weighting"""
        
        # Base component readiness
        component_metrics = self.calculate_component_readiness(component_results)
        base_readiness = component_metrics.overall_score
        
        # Stability impact
        stability_scores = []
        for result in stability_results.values():
            stability_scores.append(result.stability_score * 100)
        
        avg_stability = mean(stability_scores) if stability_scores else 0.0
        
        # Weight: 60% component readiness, 40% stability
        weighted_readiness = (base_readiness * 0.6) + (avg_stability * 0.4)
        
        return min(100.0, max(0.0, weighted_readiness))
    
    def determine_readiness_level(self, readiness_percentage: float) -> ProductionReadinessLevel:
        """Determine production readiness level from percentage"""
        
        if readiness_percentage >= self.readiness_thresholds[ProductionReadinessLevel.PRODUCTION_READY]:
            return ProductionReadinessLevel.PRODUCTION_READY
        elif readiness_percentage >= self.readiness_thresholds[ProductionReadinessLevel.NEAR_PRODUCTION]:
            return ProductionReadinessLevel.NEAR_PRODUCTION
        elif readiness_percentage >= self.readiness_thresholds[ProductionReadinessLevel.DEVELOPMENT_READY]:
            return ProductionReadinessLevel.DEVELOPMENT_READY
        elif readiness_percentage >= self.readiness_thresholds[ProductionReadinessLevel.DEVELOPMENT]:
            return ProductionReadinessLevel.DEVELOPMENT
        else:
            return ProductionReadinessLevel.FAILED
    
    def identify_critical_issues(self, validation_result: ValidationResult) -> List[str]:
        """Identify critical issues from validation results"""
        critical_issues = []
        
        # Check for failed dependencies
        missing_deps = validation_result.get_missing_dependencies()
        if missing_deps:
            critical_issues.extend([f"Missing dependency: {dep}" for dep in missing_deps])
        
        # Check for stability failures
        for name, result in validation_result.stability_tests.items():
            if result.stability_score < 0.8:
                critical_issues.append(f"{name} stability below threshold: {result.stability_score:.1%}")
        
        # Check for component failures
        for name, result in validation_result.component_tests.items():
            if result.status == ComponentStatus.FAILED:
                critical_issues.append(f"{name} component failed: {result.error_message}")
            elif result.status == ComponentStatus.UNSTABLE:
                critical_issues.append(f"{name} component unstable")
        
        return critical_issues
    
    def generate_recommendations(self, validation_result: ValidationResult) -> List[str]:
        """Generate recommendations based on validation results"""
        recommendations = []
        
        # Overall readiness recommendations
        if validation_result.readiness_percentage < 70:
            recommendations.append("System not ready for production deployment")
        elif validation_result.readiness_percentage < 85:
            recommendations.append("System requires additional stability testing")
        elif validation_result.readiness_percentage < 95:
            recommendations.append("System approaching production readiness")
        
        # Stability recommendations
        if not validation_result.stability_gate_passed:
            recommendations.append("Address stability issues before deployment")
            
            for name, result in validation_result.stability_tests.items():
                recommendations.extend(result.recommendations)
        
        # Component-specific recommendations
        for name, result in validation_result.component_tests.items():
            if result.status == ComponentStatus.FAILED:
                recommendations.append(f"Fix {name} component before deployment")
            elif result.status == ComponentStatus.UNSTABLE:
                recommendations.append(f"Investigate {name} component instability")
            elif result.response_time > 2.0:
                recommendations.append(f"Optimize {name} component performance")
        
        # Dependency recommendations
        if not validation_result.all_dependencies_available():
            recommendations.append("Resolve all dependency issues")
            for dep in validation_result.get_missing_dependencies():
                recommendations.append(f"Install/configure: {dep}")
        
        return recommendations


class ReadinessAnalyzer:
    """Analyze readiness trends and provide insights"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.calculator = ReadinessCalculator()
    
    def analyze_validation_result(self, validation_result: ValidationResult) -> Dict[str, Any]:
        """Perform comprehensive analysis of validation results"""
        
        analysis = {
            "overall_health": self._analyze_overall_health(validation_result),
            "stability_analysis": self._analyze_stability(validation_result),
            "component_analysis": self._analyze_components(validation_result),
            "dependency_analysis": self._analyze_dependencies(validation_result),
            "readiness_breakdown": self._analyze_readiness_breakdown(validation_result),
            "risk_assessment": self._assess_deployment_risks(validation_result)
        }
        
        return analysis
    
    def _analyze_overall_health(self, validation_result: ValidationResult) -> Dict[str, Any]:
        """Analyze overall system health"""
        return {
            "readiness_level": validation_result.overall_status.value,
            "readiness_percentage": validation_result.readiness_percentage,
            "stability_gate_status": "PASSED" if validation_result.stability_gate_passed else "FAILED",
            "overall_stability": validation_result.overall_stability,
            "critical_issue_count": len(validation_result.critical_issues),
            "recommendation_count": len(validation_result.recommendations)
        }
    
    def _analyze_stability(self, validation_result: ValidationResult) -> Dict[str, Any]:
        """Analyze stability test results"""
        stability_summary = {}
        
        for name, result in validation_result.stability_tests.items():
            stability_summary[name] = {
                "score": result.stability_score,
                "classification": result.stability_class.value,
                "success_rate": result.successful_operations / result.total_attempts,
                "avg_response_time": result.performance_metrics.average_time,
                "error_rate": result.error_analysis.error_rate
            }
        
        return {
            "test_summary": stability_summary,
            "overall_stability": validation_result.overall_stability,
            "passing_tests": sum(1 for r in validation_result.stability_tests.values() if r.stability_score >= 0.8),
            "total_tests": len(validation_result.stability_tests)
        }
    
    def _analyze_components(self, validation_result: ValidationResult) -> Dict[str, Any]:
        """Analyze component test results"""
        component_summary = {}
        
        for name, result in validation_result.component_tests.items():
            component_summary[name] = {
                "status": result.status.value,
                "stability_score": result.stability_score,
                "response_time": result.response_time,
                "health_score": self.calculator._calculate_component_score(result)
            }
        
        working_components = sum(1 for r in validation_result.component_tests.values() 
                               if r.status == ComponentStatus.WORKING)
        
        return {
            "component_summary": component_summary,
            "working_components": working_components,
            "total_components": len(validation_result.component_tests),
            "component_health_percentage": (working_components / len(validation_result.component_tests) * 100) 
                                         if validation_result.component_tests else 0
        }
    
    def _analyze_dependencies(self, validation_result: ValidationResult) -> Dict[str, Any]:
        """Analyze dependency check results"""
        available_deps = sum(1 for r in validation_result.dependency_checks.values() if r.available)
        total_deps = len(validation_result.dependency_checks)
        
        return {
            "available_dependencies": available_deps,
            "total_dependencies": total_deps,
            "dependency_health_percentage": (available_deps / total_deps * 100) if total_deps > 0 else 0,
            "missing_dependencies": validation_result.get_missing_dependencies(),
            "all_dependencies_met": validation_result.all_dependencies_available()
        }
    
    def _analyze_readiness_breakdown(self, validation_result: ValidationResult) -> Dict[str, Any]:
        """Analyze readiness score breakdown"""
        component_metrics = self.calculator.calculate_component_readiness(validation_result.component_tests)
        
        return {
            "component_scores": component_metrics.to_dict(),
            "overall_score": validation_result.readiness_percentage,
            "score_factors": {
                "stability_weight": 40,
                "component_weight": 60,
                "stability_score": validation_result.overall_stability * 100,
                "component_score": component_metrics.overall_score
            }
        }
    
    def _assess_deployment_risks(self, validation_result: ValidationResult) -> Dict[str, Any]:
        """Assess deployment risks"""
        risk_level = "LOW"
        risk_factors = []
        
        # High risk factors
        if not validation_result.stability_gate_passed:
            risk_level = "HIGH"
            risk_factors.append("Stability gate failed")
        
        if not validation_result.all_dependencies_available():
            risk_level = "HIGH"
            risk_factors.append("Missing critical dependencies")
        
        # Medium risk factors
        if validation_result.readiness_percentage < 85:
            if risk_level != "HIGH":
                risk_level = "MEDIUM"
            risk_factors.append("Readiness below 85%")
        
        failed_components = [name for name, result in validation_result.component_tests.items() 
                           if result.status == ComponentStatus.FAILED]
        if failed_components:
            if risk_level == "LOW":
                risk_level = "MEDIUM"
            risk_factors.extend([f"Failed component: {comp}" for comp in failed_components])
        
        return {
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "deployment_recommended": risk_level == "LOW" and validation_result.readiness_percentage >= 95,
            "requires_fixes": len(validation_result.critical_issues) > 0
        }