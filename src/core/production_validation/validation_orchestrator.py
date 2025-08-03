"""
Validation Orchestrator

Main orchestration component for production validation workflow.
"""

import asyncio
import logging
from typing import Dict, Any, Optional

from .data_models import ValidationResult, ProductionReadinessLevel
from .dependency_checker import ComprehensiveDependencyChecker
from .stability_tester import DatabaseStabilityTester, ToolConsistencyTester, MemoryStabilityTester
from .component_tester import DatabaseComponentTester, ToolComponentTester, ServiceComponentTester
from .readiness_calculator import ReadinessCalculator, ReadinessAnalyzer

logger = logging.getLogger(__name__)


class ValidationOrchestrator:
    """Orchestrate the complete production validation workflow"""
    
    def __init__(self, config_manager=None):
        self.config_manager = config_manager
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize components
        self.dependency_checker = ComprehensiveDependencyChecker()
        self.readiness_calculator = ReadinessCalculator()
        self.readiness_analyzer = ReadinessAnalyzer()
        
        # Initialize testers
        self.stability_testers = {
            "database_stability": DatabaseStabilityTester(),
            "tool_consistency": ToolConsistencyTester(),
            "memory_stability": MemoryStabilityTester()
        }
        
        self.component_testers = {
            "database": DatabaseComponentTester(),
            "tools": ToolComponentTester(),
            "services": ServiceComponentTester()
        }
    
    async def validate_production_readiness(self, stability_threshold: float = 0.80) -> ValidationResult:
        """Orchestrate complete production readiness validation"""
        
        validation_result = ValidationResult()
        self.logger.info(f"Starting production readiness validation {validation_result.validation_id}")
        
        try:
            # Phase 1: Check all dependencies first
            self.logger.info("Phase 1: Checking dependencies...")
            await self._check_dependencies(validation_result)
            
            if not validation_result.all_dependencies_available():
                validation_result.overall_status = ProductionReadinessLevel.FAILED
                validation_result.critical_issues.extend(
                    [f"Missing dependency: {dep}" for dep in validation_result.get_missing_dependencies()]
                )
                validation_result.recommendations.append("Fix missing dependencies before proceeding")
                return validation_result
            
            # Phase 2: Run stability tests with enforcement
            self.logger.info("Phase 2: Running stability tests...")
            await self._run_stability_tests(validation_result)
            
            # Check stability gate
            validation_result.calculate_overall_stability()
            validation_result.update_stability_gate(stability_threshold)
            
            if not validation_result.stability_gate_passed:
                validation_result.overall_status = ProductionReadinessLevel.STABILITY_FAILED
                validation_result.critical_issues.append(
                    f"Stability gate FAILED: {validation_result.overall_stability:.1%} < {stability_threshold:.0%} threshold"
                )
                validation_result.recommendations.extend([
                    "System stability insufficient for production deployment",
                    "Address database connectivity issues",
                    "Fix tool consistency problems",
                    "Resolve memory stability issues"
                ])
                return validation_result
            
            # Phase 3: Test individual components
            self.logger.info("Phase 3: Testing components...")
            await self._test_components(validation_result)
            
            # Phase 4: Calculate final readiness
            self.logger.info("Phase 4: Calculating readiness...")
            await self._calculate_readiness(validation_result)
            
            # Phase 5: Generate analysis and recommendations
            self.logger.info("Phase 5: Generating analysis...")
            await self._generate_final_analysis(validation_result)
            
            self.logger.info(f"Validation complete: {validation_result.overall_status.value} "
                           f"({validation_result.readiness_percentage:.1f}%)")
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Validation failed with error: {e}", exc_info=True)
            validation_result.overall_status = ProductionReadinessLevel.FAILED
            validation_result.critical_issues.append(f"Validation error: {str(e)}")
            validation_result.recommendations.append("Fix validation system errors")
            return validation_result
    
    async def _check_dependencies(self, validation_result: ValidationResult):
        """Check all system dependencies"""
        try:
            dependency_results = self.dependency_checker.check_all_dependencies()
            
            for name, result in dependency_results["dependency_results"].items():
                validation_result.add_dependency_result(name, result)
            
            self.logger.info(f"Dependencies checked: {dependency_results['available_count']}/{dependency_results['total_dependencies']} available")
            
        except Exception as e:
            self.logger.error(f"Dependency checking failed: {e}")
            raise
    
    async def _run_stability_tests(self, validation_result: ValidationResult):
        """Run all stability tests"""
        try:
            stability_tasks = []
            
            for name, tester in self.stability_testers.items():
                task = asyncio.create_task(tester.run_stability_test())
                stability_tasks.append((name, task))
            
            # Wait for all stability tests to complete
            for name, task in stability_tasks:
                try:
                    result = await task
                    validation_result.add_stability_result(name, result)
                    self.logger.info(f"Stability test {name}: {result.stability_score:.1%} ({result.stability_class.value})")
                except Exception as e:
                    self.logger.error(f"Stability test {name} failed: {e}")
                    # Create failed result
                    from .data_models import StabilityTestResult, StabilityClass, PerformanceMetrics, ErrorAnalysis
                    failed_result = StabilityTestResult(
                        test_name=name,
                        successful_operations=0,
                        total_attempts=1,
                        stability_score=0.0,
                        stability_class=StabilityClass.POOR,
                        performance_metrics=PerformanceMetrics(0, 0, 0, 0, 0),
                        error_analysis=ErrorAnalysis({}, 1, 1.0),
                        recommendations=[f"Fix {name} test execution"]
                    )
                    validation_result.add_stability_result(name, failed_result)
                    
        except Exception as e:
            self.logger.error(f"Stability testing failed: {e}")
            raise
    
    async def _test_components(self, validation_result: ValidationResult):
        """Test all system components"""
        try:
            component_tasks = []
            
            for name, tester in self.component_testers.items():
                task = asyncio.create_task(tester.test_component())
                component_tasks.append((name, task))
            
            # Wait for all component tests to complete
            for name, task in component_tasks:
                try:
                    result = await task
                    validation_result.add_component_result(name, result)
                    self.logger.info(f"Component test {name}: {result.status.value} ({result.stability_score:.1%})")
                except Exception as e:
                    self.logger.error(f"Component test {name} failed: {e}")
                    # Create failed result
                    from .data_models import ComponentTestResult, ComponentStatus
                    failed_result = ComponentTestResult(
                        component_name=name,
                        status=ComponentStatus.FAILED,
                        stability_score=0.0,
                        response_time=0.0,
                        error_message=str(e)
                    )
                    validation_result.add_component_result(name, failed_result)
                    
        except Exception as e:
            self.logger.error(f"Component testing failed: {e}")
            raise
    
    async def _calculate_readiness(self, validation_result: ValidationResult):
        """Calculate final readiness score and level"""
        try:
            # Calculate readiness percentage
            readiness_percentage = self.readiness_calculator.calculate_stability_weighted_readiness(
                validation_result.stability_tests,
                validation_result.component_tests
            )
            validation_result.readiness_percentage = readiness_percentage
            
            # Determine readiness level
            readiness_level = self.readiness_calculator.determine_readiness_level(readiness_percentage)
            validation_result.overall_status = readiness_level
            
            self.logger.info(f"Readiness calculated: {readiness_percentage:.1f}% ({readiness_level.value})")
            
        except Exception as e:
            self.logger.error(f"Readiness calculation failed: {e}")
            raise
    
    async def _generate_final_analysis(self, validation_result: ValidationResult):
        """Generate final analysis, issues, and recommendations"""
        try:
            # Identify critical issues
            critical_issues = self.readiness_calculator.identify_critical_issues(validation_result)
            validation_result.critical_issues.extend(critical_issues)
            
            # Generate recommendations
            recommendations = self.readiness_calculator.generate_recommendations(validation_result)
            validation_result.recommendations.extend(recommendations)
            
            # Perform detailed analysis
            detailed_analysis = self.readiness_analyzer.analyze_validation_result(validation_result)
            
            self.logger.info(f"Analysis complete: {len(critical_issues)} critical issues, "
                           f"{len(recommendations)} recommendations")
            
        except Exception as e:
            self.logger.error(f"Final analysis failed: {e}")
            # Continue even if analysis fails
            pass


# Backward compatibility alias
class ProductionValidator(ValidationOrchestrator):
    """Backward compatibility alias for ValidationOrchestrator"""
    
    def __init__(self, config_manager=None):
        super().__init__(config_manager)
        self.logger.warning("ProductionValidator is deprecated, use ValidationOrchestrator instead")
    
    async def validate_production_readiness(self) -> Dict[str, Any]:
        """Validate production readiness with legacy dict return format"""
        validation_result = await super().validate_production_readiness()
        return validation_result.to_dict()