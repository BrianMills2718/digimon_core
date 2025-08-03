#!/usr/bin/env python3
"""
Cross-Modal Validator - Comprehensive validation framework for cross-modal operations

Implements comprehensive validation for cross-modal conversions, integrity testing,
and performance benchmarking with detailed reporting and error analysis.
"""

import asyncio
import time
import logging
import json
import hashlib
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Union, Tuple, Callable
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
from abc import ABC, abstractmethod

try:
    from ..core.unified_service_interface import CoreService, ServiceResponse, create_service_response
    from ..core.config_manager import get_config
    from ..core.logging_config import get_logger
except ImportError:
    # Fallback for direct execution - ONLY try absolute import, NO stubs
    from src.core.unified_service_interface import CoreService, ServiceResponse, create_service_response
    from src.core.config_manager import get_config
    from src.core.logging_config import get_logger
from .cross_modal_converter import (
    CrossModalConverter, DataFormat, ConversionResult, ValidationResult
)

logger = get_logger("analytics.cross_modal_validator")


class ValidationLevel(Enum):
    """Validation thoroughness levels"""
    BASIC = "basic"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"
    STRESS_TEST = "stress_test"


class ValidationCategory(Enum):
    """Categories of validation tests"""
    STRUCTURAL = "structural"
    SEMANTIC = "semantic"
    PERFORMANCE = "performance"
    INTEGRITY = "integrity"
    ROUND_TRIP = "round_trip"
    STRESS = "stress"


@dataclass
class ValidationTest:
    """Individual validation test definition"""
    test_id: str
    test_name: str
    category: ValidationCategory
    level: ValidationLevel
    description: str
    test_function: Callable
    expected_duration: float
    criticality: str  # "critical", "important", "optional"


@dataclass
class ValidationTestResult:
    """Result of a single validation test"""
    test_id: str
    test_name: str
    passed: bool
    score: float
    execution_time: float
    details: Dict[str, Any]
    errors: List[str]
    warnings: List[str]
    metadata: Dict[str, Any]


@dataclass
class ValidationReport:
    """Comprehensive validation report"""
    validation_id: str
    timestamp: str
    validation_level: ValidationLevel
    overall_passed: bool
    overall_score: float
    total_tests: int
    passed_tests: int
    failed_tests: int
    execution_time: float
    test_results: List[ValidationTestResult]
    performance_metrics: Dict[str, Any]
    recommendations: List[str]
    summary: Dict[str, Any]


@dataclass
class StressTestConfig:
    """Configuration for stress testing"""
    max_data_size: int
    max_execution_time: float
    memory_limit_mb: int
    concurrent_operations: int
    test_iterations: int
    performance_degradation_threshold: float


class CrossModalValidator(CoreService):
    """Comprehensive validation framework for cross-modal operations
    
    Provides thorough validation of cross-modal conversions including:
    - Structural integrity testing
    - Semantic preservation validation
    - Performance benchmarking
    - Round-trip conversion testing
    - Stress testing under various conditions
    """
    
    def __init__(self, converter=None, service_manager=None):
        self.converter = converter or CrossModalConverter(service_manager)
        self.service_manager = service_manager
        self.config = get_config()
        self.logger = get_logger("analytics.cross_modal_validator")
        
        # Test registry
        self.validation_tests = {}
        self._register_validation_tests()
        
        # Performance tracking
        self.validation_history = []
        self.performance_baselines = {}
        
        # Configuration
        self.default_validation_level = ValidationLevel.STANDARD
        self.integrity_threshold = 0.85
        self.performance_threshold = 0.8
        self.stress_test_config = StressTestConfig(
            max_data_size=100000,
            max_execution_time=300.0,
            memory_limit_mb=1000,
            concurrent_operations=5,
            test_iterations=10,
            performance_degradation_threshold=0.5
        )
        
        self.logger.info("CrossModalValidator initialized")
    
    def initialize(self, config: Dict[str, Any]) -> ServiceResponse:
        """Initialize service with configuration"""
        try:
            self.default_validation_level = ValidationLevel(
                config.get('default_validation_level', ValidationLevel.STANDARD.value)
            )
            self.integrity_threshold = config.get('integrity_threshold', 0.85)
            self.performance_threshold = config.get('performance_threshold', 0.8)
            
            # Update stress test configuration
            stress_config = config.get('stress_test_config', {})
            for key, value in stress_config.items():
                if hasattr(self.stress_test_config, key):
                    setattr(self.stress_test_config, key, value)
            
            self.logger.info("CrossModalValidator initialized successfully")
            return create_service_response(
                success=True,
                data={"status": "initialized"},
                metadata={"timestamp": datetime.now().isoformat()}
            )
            
        except Exception as e:
            self.logger.error(f"Failed to initialize CrossModalValidator: {e}")
            return create_service_response(
                success=False,
                data=None,
                error_code="INITIALIZATION_FAILED",
                error_message=str(e)
            )
    
    def health_check(self) -> ServiceResponse:
        """Check service health and readiness"""
        try:
            # Check converter health
            converter_health = self.converter.health_check()
            
            health_data = {
                "service_status": "healthy",
                "converter_status": converter_health.success,
                "registered_tests": len(self.validation_tests),
                "validation_history_size": len(self.validation_history),
                "performance_baselines": len(self.performance_baselines),
                "test_categories": [cat.value for cat in ValidationCategory],
                "validation_levels": [level.value for level in ValidationLevel]
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
            if not self.validation_history:
                stats = {
                    "total_validations": 0,
                    "success_rate": 0.0,
                    "average_score": 0.0,
                    "average_execution_time": 0.0
                }
            else:
                total_validations = len(self.validation_history)
                successful_validations = sum(1 for report in self.validation_history if report.overall_passed)
                average_score = sum(report.overall_score for report in self.validation_history) / total_validations
                average_execution_time = sum(report.execution_time for report in self.validation_history) / total_validations
                
                stats = {
                    "total_validations": total_validations,
                    "successful_validations": successful_validations,
                    "success_rate": successful_validations / total_validations,
                    "average_score": average_score,
                    "average_execution_time": average_execution_time,
                    "validation_levels_used": list(set(report.validation_level.value for report in self.validation_history)),
                    "performance_baselines": list(self.performance_baselines.keys())
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
            # Keep only recent validation history
            if len(self.validation_history) > 100:
                self.validation_history = self.validation_history[-100:]
            
            self.logger.info("CrossModalValidator cleanup completed")
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
            "service_name": "CrossModalValidator",
            "version": "1.0.0",
            "description": "Comprehensive validation framework for cross-modal operations",
            "capabilities": [
                "conversion_validation",
                "integrity_testing",
                "round_trip_validation", 
                "stress_testing",
                "performance_benchmarking"
            ],
            "validation_levels": [level.value for level in ValidationLevel],
            "validation_categories": [cat.value for cat in ValidationCategory],
            "test_types": [
                "structural_integrity",
                "semantic_preservation",
                "performance_benchmark",
                "data_integrity"
            ],
            "features": [
                "comprehensive_reporting",
                "performance_tracking",
                "recommendation_generation",
                "validation_history"
            ]
        }
    
    async def validate_cross_modal_conversion(
        self,
        original_data: Any,
        source_format: DataFormat,
        target_format: DataFormat,
        validation_level: Optional[ValidationLevel] = None,
        **conversion_kwargs
    ) -> ValidationReport:
        """Validate a cross-modal conversion operation
        
        Args:
            original_data: Original data to convert and validate
            source_format: Source data format
            target_format: Target data format
            validation_level: Level of validation thoroughness
            **conversion_kwargs: Additional conversion parameters
            
        Returns:
            ValidationReport with comprehensive validation results
        """
        validation_id = self._generate_validation_id()
        start_time = time.time()
        validation_level = validation_level or self.default_validation_level
        
        self.logger.info(
            f"Starting cross-modal validation {validation_id}: "
            f"{source_format.value} -> {target_format.value} (level: {validation_level.value})"
        )
        
        try:
            # Get applicable tests for this validation
            applicable_tests = self._get_applicable_tests(
                source_format, target_format, validation_level
            )
            
            # Execute validation tests
            test_results = []
            for test in applicable_tests:
                try:
                    result = await self._execute_validation_test(
                        test, original_data, source_format, target_format, **conversion_kwargs
                    )
                    test_results.append(result)
                except Exception as e:
                    self.logger.error(f"Test {test.test_id} failed with error: {e}")
                    test_results.append(ValidationTestResult(
                        test_id=test.test_id,
                        test_name=test.test_name,
                        passed=False,
                        score=0.0,
                        execution_time=0.0,
                        details={},
                        errors=[str(e)],
                        warnings=[],
                        metadata={"test_category": test.category.value}
                    ))
            
            # Calculate overall metrics
            total_tests = len(test_results)
            passed_tests = sum(1 for result in test_results if result.passed)
            failed_tests = total_tests - passed_tests
            overall_score = sum(result.score for result in test_results) / max(1, total_tests)
            overall_passed = (
                passed_tests / max(1, total_tests) >= 0.8 and
                overall_score >= self.integrity_threshold
            )
            execution_time = time.time() - start_time
            
            # Generate performance metrics
            performance_metrics = await self._calculate_performance_metrics(
                test_results, execution_time
            )
            
            # Generate recommendations
            recommendations = self._generate_recommendations(test_results, overall_score)
            
            # Create summary
            summary = self._create_validation_summary(
                test_results, overall_score, performance_metrics
            )
            
            # Create validation report
            report = ValidationReport(
                validation_id=validation_id,
                timestamp=datetime.now().isoformat(),
                validation_level=validation_level,
                overall_passed=overall_passed,
                overall_score=overall_score,
                total_tests=total_tests,
                passed_tests=passed_tests,
                failed_tests=failed_tests,
                execution_time=execution_time,
                test_results=test_results,
                performance_metrics=performance_metrics,
                recommendations=recommendations,
                summary=summary
            )
            
            # Store in history
            self.validation_history.append(report)
            
            self.logger.info(
                f"Validation {validation_id} completed: "
                f"passed={overall_passed}, score={overall_score:.3f}, "
                f"tests={passed_tests}/{total_tests} in {execution_time:.2f}s"
            )
            
            return report
            
        except Exception as e:
            self.logger.error(f"Validation {validation_id} failed: {e}")
            
            # Create error report
            error_report = ValidationReport(
                validation_id=validation_id,
                timestamp=datetime.now().isoformat(),
                validation_level=validation_level,
                overall_passed=False,
                overall_score=0.0,
                total_tests=0,
                passed_tests=0,
                failed_tests=1,
                execution_time=time.time() - start_time,
                test_results=[],
                performance_metrics={},
                recommendations=[f"Fix validation error: {e}"],
                summary={"error": str(e)}
            )
            
            return error_report
    
    async def validate_round_trip_integrity(
        self,
        original_data: Any,
        format_sequence: List[DataFormat],
        validation_level: Optional[ValidationLevel] = None
    ) -> ValidationReport:
        """Validate round-trip conversion integrity
        
        Args:
            original_data: Original data to test
            format_sequence: Sequence of formats to convert through
            validation_level: Level of validation thoroughness
            
        Returns:
            ValidationReport with round-trip validation results
        """
        validation_id = self._generate_validation_id()
        start_time = time.time()
        validation_level = validation_level or self.default_validation_level
        
        self.logger.info(
            f"Starting round-trip validation {validation_id}: "
            f"{' -> '.join(f.value for f in format_sequence)} (level: {validation_level.value})"
        )
        
        try:
            # Perform round-trip conversion validation
            round_trip_result = await self.converter.validate_round_trip_conversion(
                original_data, format_sequence
            )
            
            # Create test result for round-trip validation
            test_results = [ValidationTestResult(
                test_id="round_trip_integrity",
                test_name="Round-trip Conversion Integrity",
                passed=round_trip_result.valid,
                score=round_trip_result.integrity_score,
                execution_time=time.time() - start_time,
                details=round_trip_result.details,
                errors=round_trip_result.errors,
                warnings=round_trip_result.warnings,
                metadata={
                    "preservation_score": round_trip_result.preservation_score,
                    "semantic_match": round_trip_result.semantic_match,
                    "format_sequence": [f.value for f in format_sequence]
                }
            )]
            
            # Add format-specific tests if comprehensive validation
            if validation_level in [ValidationLevel.COMPREHENSIVE, ValidationLevel.STRESS_TEST]:
                # Test each conversion step individually
                for i in range(len(format_sequence) - 1):
                    step_test = await self._validate_conversion_step(
                        original_data, format_sequence[i], format_sequence[i + 1], i + 1
                    )
                    test_results.append(step_test)
            
            # Calculate overall metrics
            total_tests = len(test_results)
            passed_tests = sum(1 for result in test_results if result.passed)
            overall_score = sum(result.score for result in test_results) / max(1, total_tests)
            overall_passed = round_trip_result.valid and passed_tests == total_tests
            execution_time = time.time() - start_time
            
            # Create validation report
            report = ValidationReport(
                validation_id=validation_id,
                timestamp=datetime.now().isoformat(),
                validation_level=validation_level,
                overall_passed=overall_passed,
                overall_score=overall_score,
                total_tests=total_tests,
                passed_tests=passed_tests,
                failed_tests=total_tests - passed_tests,
                execution_time=execution_time,
                test_results=test_results,
                performance_metrics={"round_trip_time": execution_time},
                recommendations=self._generate_round_trip_recommendations(round_trip_result),
                summary={
                    "round_trip_valid": round_trip_result.valid,
                    "preservation_score": round_trip_result.preservation_score,
                    "semantic_match": round_trip_result.semantic_match,
                    "format_sequence": [f.value for f in format_sequence]
                }
            )
            
            self.validation_history.append(report)
            
            self.logger.info(
                f"Round-trip validation {validation_id} completed: "
                f"passed={overall_passed}, score={overall_score:.3f} in {execution_time:.2f}s"
            )
            
            return report
            
        except Exception as e:
            self.logger.error(f"Round-trip validation {validation_id} failed: {e}")
            raise
    
    async def stress_test_conversion(
        self,
        data_generator: Callable,
        source_format: DataFormat,
        target_format: DataFormat,
        stress_config: Optional[StressTestConfig] = None
    ) -> ValidationReport:
        """Perform stress testing on cross-modal conversion
        
        Args:
            data_generator: Function that generates test data of various sizes
            source_format: Source data format
            target_format: Target data format
            stress_config: Stress test configuration
            
        Returns:
            ValidationReport with stress test results
        """
        validation_id = self._generate_validation_id()
        start_time = time.time()
        stress_config = stress_config or self.stress_test_config
        
        self.logger.info(
            f"Starting stress test {validation_id}: "
            f"{source_format.value} -> {target_format.value}"
        )
        
        test_results = []
        
        try:
            # Test with increasing data sizes
            data_sizes = [100, 1000, 10000, stress_config.max_data_size]
            
            for size in data_sizes:
                # Generate test data
                test_data = data_generator(size)
                
                # Test conversion performance
                start_test_time = time.time()
                try:
                    conversion_result = await asyncio.wait_for(
                        self.converter.convert_data(
                            test_data, source_format, target_format
                        ),
                        timeout=stress_config.max_execution_time
                    )
                    
                    test_time = time.time() - start_test_time
                    
                    # Evaluate performance
                    performance_score = self._evaluate_stress_performance(
                        size, test_time, stress_config
                    )
                    
                    test_results.append(ValidationTestResult(
                        test_id=f"stress_test_size_{size}",
                        test_name=f"Stress Test - Data Size {size}",
                        passed=conversion_result.validation_passed and performance_score >= 0.5,
                        score=performance_score,
                        execution_time=test_time,
                        details={
                            "data_size": size,
                            "conversion_successful": conversion_result.validation_passed,
                            "preservation_score": conversion_result.preservation_score
                        },
                        errors=[],
                        warnings=[],
                        metadata={"test_type": "stress_performance"}
                    ))
                    
                except asyncio.TimeoutError:
                    test_results.append(ValidationTestResult(
                        test_id=f"stress_test_size_{size}",
                        test_name=f"Stress Test - Data Size {size}",
                        passed=False,
                        score=0.0,
                        execution_time=stress_config.max_execution_time,
                        details={"data_size": size},
                        errors=["Conversion timed out"],
                        warnings=[],
                        metadata={"test_type": "stress_timeout"}
                    ))
                
                except Exception as e:
                    test_results.append(ValidationTestResult(
                        test_id=f"stress_test_size_{size}",
                        test_name=f"Stress Test - Data Size {size}",
                        passed=False,
                        score=0.0,
                        execution_time=time.time() - start_test_time,
                        details={"data_size": size},
                        errors=[str(e)],
                        warnings=[],
                        metadata={"test_type": "stress_error"}
                    ))
            
            # Test concurrent operations
            if stress_config.concurrent_operations > 1:
                concurrent_result = await self._test_concurrent_conversions(
                    data_generator, source_format, target_format, stress_config
                )
                test_results.append(concurrent_result)
            
            # Calculate overall metrics
            total_tests = len(test_results)
            passed_tests = sum(1 for result in test_results if result.passed)
            overall_score = sum(result.score for result in test_results) / max(1, total_tests)
            overall_passed = passed_tests / max(1, total_tests) >= 0.8
            execution_time = time.time() - start_time
            
            # Create stress test report
            report = ValidationReport(
                validation_id=validation_id,
                timestamp=datetime.now().isoformat(),
                validation_level=ValidationLevel.STRESS_TEST,
                overall_passed=overall_passed,
                overall_score=overall_score,
                total_tests=total_tests,
                passed_tests=passed_tests,
                failed_tests=total_tests - passed_tests,
                execution_time=execution_time,
                test_results=test_results,
                performance_metrics=self._calculate_stress_metrics(test_results),
                recommendations=self._generate_stress_recommendations(test_results),
                summary={
                    "max_data_size_handled": max(
                        result.details.get("data_size", 0) 
                        for result in test_results if result.passed
                    ),
                    "performance_degradation": self._calculate_performance_degradation(test_results)
                }
            )
            
            self.validation_history.append(report)
            
            self.logger.info(
                f"Stress test {validation_id} completed: "
                f"passed={overall_passed}, score={overall_score:.3f} in {execution_time:.2f}s"
            )
            
            return report
            
        except Exception as e:
            self.logger.error(f"Stress test {validation_id} failed: {e}")
            raise
    
    def _register_validation_tests(self):
        """Register all validation tests"""
        
        # Structural validation tests
        self.validation_tests["structural_integrity"] = ValidationTest(
            test_id="structural_integrity",
            test_name="Structural Integrity Check",
            category=ValidationCategory.STRUCTURAL,
            level=ValidationLevel.BASIC,
            description="Validate basic structural properties are preserved",
            test_function=self._test_structural_integrity,
            expected_duration=5.0,
            criticality="critical"
        )
        
        # Semantic validation tests
        self.validation_tests["semantic_preservation"] = ValidationTest(
            test_id="semantic_preservation",
            test_name="Semantic Preservation Check",
            category=ValidationCategory.SEMANTIC,
            level=ValidationLevel.STANDARD,
            description="Validate semantic meaning is preserved",
            test_function=self._test_semantic_preservation,
            expected_duration=10.0,
            criticality="important"
        )
        
        # Performance validation tests
        self.validation_tests["performance_benchmark"] = ValidationTest(
            test_id="performance_benchmark",
            test_name="Performance Benchmark",
            category=ValidationCategory.PERFORMANCE,
            level=ValidationLevel.STANDARD,
            description="Benchmark conversion performance",
            test_function=self._test_performance_benchmark,
            expected_duration=15.0,
            criticality="important"
        )
        
        # Integrity validation tests
        self.validation_tests["data_integrity"] = ValidationTest(
            test_id="data_integrity",
            test_name="Data Integrity Check",
            category=ValidationCategory.INTEGRITY,
            level=ValidationLevel.COMPREHENSIVE,
            description="Comprehensive data integrity validation",
            test_function=self._test_data_integrity,
            expected_duration=20.0,
            criticality="critical"
        )
    
    def _get_applicable_tests(
        self,
        source_format: DataFormat,
        target_format: DataFormat,
        validation_level: ValidationLevel
    ) -> List[ValidationTest]:
        """Get applicable tests for the validation scenario"""
        
        applicable_tests = []
        
        for test in self.validation_tests.values():
            # Check if test level is appropriate
            level_hierarchy = {
                ValidationLevel.BASIC: 1,
                ValidationLevel.STANDARD: 2,
                ValidationLevel.COMPREHENSIVE: 3,
                ValidationLevel.STRESS_TEST: 4
            }
            
            if level_hierarchy[test.level] <= level_hierarchy[validation_level]:
                applicable_tests.append(test)
        
        return sorted(applicable_tests, key=lambda t: t.criticality)
    
    async def _execute_validation_test(
        self,
        test: ValidationTest,
        original_data: Any,
        source_format: DataFormat,
        target_format: DataFormat,
        **kwargs
    ) -> ValidationTestResult:
        """Execute a single validation test"""
        
        start_time = time.time()
        
        try:
            # Execute the test function
            result = await test.test_function(
                original_data, source_format, target_format, **kwargs
            )
            
            execution_time = time.time() - start_time
            
            return ValidationTestResult(
                test_id=test.test_id,
                test_name=test.test_name,
                passed=result.get("passed", False),
                score=result.get("score", 0.0),
                execution_time=execution_time,
                details=result.get("details", {}),
                errors=result.get("errors", []),
                warnings=result.get("warnings", []),
                metadata={
                    "test_category": test.category.value,
                    "test_level": test.level.value,
                    "criticality": test.criticality
                }
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Test {test.test_id} execution failed: {e}")
            
            return ValidationTestResult(
                test_id=test.test_id,
                test_name=test.test_name,
                passed=False,
                score=0.0,
                execution_time=execution_time,
                details={},
                errors=[str(e)],
                warnings=[],
                metadata={
                    "test_category": test.category.value,
                    "test_level": test.level.value,
                    "criticality": test.criticality,
                    "execution_error": True
                }
            )
    
    async def _test_structural_integrity(
        self,
        original_data: Any,
        source_format: DataFormat,
        target_format: DataFormat,
        **kwargs
    ) -> Dict[str, Any]:
        """Test structural integrity of conversion"""
        
        try:
            # Perform conversion
            conversion_result = await self.converter.convert_data(
                original_data, source_format, target_format, **kwargs
            )
            
            # Check basic structural properties
            structure_preserved = True
            details = {}
            
            # Format-specific structural checks
            if source_format == DataFormat.GRAPH and target_format == DataFormat.TABLE:
                if isinstance(original_data, dict) and isinstance(conversion_result.data, pd.DataFrame):
                    original_entities = len(original_data.get('nodes', [])) + len(original_data.get('edges', []))
                    converted_rows = len(conversion_result.data)
                    
                    structure_preserved = converted_rows > 0 and converted_rows <= original_entities * 2
                    details["entity_preservation"] = converted_rows / max(1, original_entities)
            
            elif source_format == DataFormat.TABLE and target_format == DataFormat.GRAPH:
                if isinstance(original_data, pd.DataFrame) and isinstance(conversion_result.data, dict):
                    original_rows = len(original_data)
                    converted_entities = len(conversion_result.data.get('nodes', [])) + len(conversion_result.data.get('edges', []))
                    
                    structure_preserved = converted_entities > 0
                    details["structure_expansion"] = converted_entities / max(1, original_rows)
            
            # Calculate score
            score = 1.0 if structure_preserved else 0.0
            if conversion_result.preservation_score:
                score = (score + conversion_result.preservation_score) / 2
            
            return {
                "passed": structure_preserved and conversion_result.validation_passed,
                "score": score,
                "details": {
                    **details,
                    "conversion_successful": conversion_result.validation_passed,
                    "preservation_score": conversion_result.preservation_score
                },
                "errors": [],
                "warnings": conversion_result.warnings
            }
            
        except Exception as e:
            return {
                "passed": False,
                "score": 0.0,
                "details": {},
                "errors": [str(e)],
                "warnings": []
            }
    
    async def _test_semantic_preservation(
        self,
        original_data: Any,
        source_format: DataFormat,
        target_format: DataFormat,
        **kwargs
    ) -> Dict[str, Any]:
        """Test semantic preservation of conversion"""
        
        try:
            # Perform conversion
            conversion_result = await self.converter.convert_data(
                original_data, source_format, target_format, preserve_semantics=True, **kwargs
            )
            
            # Check semantic integrity
            semantic_preserved = conversion_result.semantic_integrity
            score = conversion_result.preservation_score
            
            details = {
                "semantic_integrity": semantic_preserved,
                "preservation_score": conversion_result.preservation_score,
                "conversion_metadata": asdict(conversion_result.conversion_metadata)
            }
            
            return {
                "passed": semantic_preserved and score >= self.integrity_threshold,
                "score": score,
                "details": details,
                "errors": [],
                "warnings": conversion_result.warnings
            }
            
        except Exception as e:
            return {
                "passed": False,
                "score": 0.0,
                "details": {},
                "errors": [str(e)],
                "warnings": []
            }
    
    async def _test_performance_benchmark(
        self,
        original_data: Any,
        source_format: DataFormat,
        target_format: DataFormat,
        **kwargs
    ) -> Dict[str, Any]:
        """Test conversion performance benchmark"""
        
        try:
            # Measure conversion time
            start_time = time.time()
            conversion_result = await self.converter.convert_data(
                original_data, source_format, target_format, **kwargs
            )
            conversion_time = time.time() - start_time
            
            # Calculate performance metrics
            data_size = self._calculate_data_size(original_data)
            throughput = data_size / max(0.001, conversion_time)  # items per second
            
            # Get baseline performance if available
            baseline_key = f"{source_format.value}_{target_format.value}"
            baseline_time = self.performance_baselines.get(baseline_key, conversion_time)
            
            # Update baseline if this is better
            if conversion_time < baseline_time:
                self.performance_baselines[baseline_key] = conversion_time
            
            # Calculate performance score
            performance_ratio = baseline_time / max(0.001, conversion_time)
            performance_score = min(1.0, performance_ratio)
            
            details = {
                "conversion_time": conversion_time,
                "data_size": data_size,
                "throughput": throughput,
                "baseline_time": baseline_time,
                "performance_ratio": performance_ratio,
                "memory_efficiency": conversion_result.conversion_metadata.quality_metrics.get("size_preservation_ratio", 1.0)
            }
            
            return {
                "passed": performance_score >= self.performance_threshold,
                "score": performance_score,
                "details": details,
                "errors": [],
                "warnings": []
            }
            
        except Exception as e:
            return {
                "passed": False,
                "score": 0.0,
                "details": {},
                "errors": [str(e)],
                "warnings": []
            }
    
    async def _test_data_integrity(
        self,
        original_data: Any,
        source_format: DataFormat,
        target_format: DataFormat,
        **kwargs
    ) -> Dict[str, Any]:
        """Test comprehensive data integrity"""
        
        try:
            # Perform round-trip conversion if possible
            intermediate_format = self._get_intermediate_format(source_format, target_format)
            
            if intermediate_format:
                # Test: original -> target -> intermediate -> original
                format_sequence = [source_format, target_format, intermediate_format, source_format]
                
                round_trip_result = await self.converter.validate_round_trip_conversion(
                    original_data, format_sequence
                )
                
                integrity_score = round_trip_result.integrity_score
                integrity_passed = round_trip_result.valid
                
                details = {
                    "round_trip_valid": round_trip_result.valid,
                    "preservation_score": round_trip_result.preservation_score,
                    "semantic_match": round_trip_result.semantic_match,
                    "integrity_score": integrity_score,
                    "format_sequence": [f.value for f in format_sequence],
                    "conversion_details": round_trip_result.details
                }
                
                return {
                    "passed": integrity_passed,
                    "score": integrity_score,
                    "details": details,
                    "errors": round_trip_result.errors,
                    "warnings": round_trip_result.warnings
                }
            else:
                # Simple conversion integrity test
                conversion_result = await self.converter.convert_data(
                    original_data, source_format, target_format, preserve_semantics=True, **kwargs
                )
                
                integrity_score = (
                    conversion_result.preservation_score + 
                    (1.0 if conversion_result.semantic_integrity else 0.0)
                ) / 2
                
                return {
                    "passed": conversion_result.validation_passed and integrity_score >= self.integrity_threshold,
                    "score": integrity_score,
                    "details": {
                        "preservation_score": conversion_result.preservation_score,
                        "semantic_integrity": conversion_result.semantic_integrity,
                        "validation_passed": conversion_result.validation_passed
                    },
                    "errors": [],
                    "warnings": conversion_result.warnings
                }
                
        except Exception as e:
            return {
                "passed": False,
                "score": 0.0,
                "details": {},
                "errors": [str(e)],
                "warnings": []
            }
    
    def _get_intermediate_format(self, source_format: DataFormat, target_format: DataFormat) -> Optional[DataFormat]:
        """Get intermediate format for round-trip testing"""
        
        all_formats = [DataFormat.GRAPH, DataFormat.TABLE, DataFormat.VECTOR]
        available_formats = [f for f in all_formats if f not in [source_format, target_format]]
        
        return available_formats[0] if available_formats else None
    
    async def _validate_conversion_step(
        self,
        original_data: Any,
        source_format: DataFormat,
        target_format: DataFormat,
        step_number: int
    ) -> ValidationTestResult:
        """Validate individual conversion step"""
        
        start_time = time.time()
        
        try:
            conversion_result = await self.converter.convert_data(
                original_data, source_format, target_format, preserve_semantics=True
            )
            
            execution_time = time.time() - start_time
            
            return ValidationTestResult(
                test_id=f"conversion_step_{step_number}",
                test_name=f"Conversion Step {step_number}: {source_format.value} -> {target_format.value}",
                passed=conversion_result.validation_passed,
                score=conversion_result.preservation_score,
                execution_time=execution_time,
                details={
                    "source_format": source_format.value,
                    "target_format": target_format.value,
                    "preservation_score": conversion_result.preservation_score,
                    "semantic_integrity": conversion_result.semantic_integrity
                },
                errors=[],
                warnings=conversion_result.warnings,
                metadata={"step_number": step_number}
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            return ValidationTestResult(
                test_id=f"conversion_step_{step_number}",
                test_name=f"Conversion Step {step_number}: {source_format.value} -> {target_format.value}",
                passed=False,
                score=0.0,
                execution_time=execution_time,
                details={},
                errors=[str(e)],
                warnings=[],
                metadata={"step_number": step_number}
            )
    
    async def _test_concurrent_conversions(
        self,
        data_generator: Callable,
        source_format: DataFormat,
        target_format: DataFormat,
        stress_config: StressTestConfig
    ) -> ValidationTestResult:
        """Test concurrent conversion operations"""
        
        start_time = time.time()
        
        try:
            # Generate test data for concurrent operations
            test_data_sets = [
                data_generator(1000) 
                for _ in range(stress_config.concurrent_operations)
            ]
            
            # Run concurrent conversions
            tasks = [
                self.converter.convert_data(data, source_format, target_format)
                for data in test_data_sets
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Analyze results
            successful_conversions = sum(
                1 for result in results 
                if not isinstance(result, Exception) and result.validation_passed
            )
            
            success_rate = successful_conversions / len(results)
            execution_time = time.time() - start_time
            
            return ValidationTestResult(
                test_id="concurrent_conversions",
                test_name="Concurrent Conversion Operations",
                passed=success_rate >= 0.8,
                score=success_rate,
                execution_time=execution_time,
                details={
                    "concurrent_operations": stress_config.concurrent_operations,
                    "successful_conversions": successful_conversions,
                    "total_operations": len(results),
                    "success_rate": success_rate
                },
                errors=[str(r) for r in results if isinstance(r, Exception)],
                warnings=[],
                metadata={"test_type": "concurrent_stress"}
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            return ValidationTestResult(
                test_id="concurrent_conversions",
                test_name="Concurrent Conversion Operations",
                passed=False,
                score=0.0,
                execution_time=execution_time,
                details={},
                errors=[str(e)],
                warnings=[],
                metadata={"test_type": "concurrent_error"}
            )
    
    def _evaluate_stress_performance(
        self,
        data_size: int,
        execution_time: float,
        stress_config: StressTestConfig
    ) -> float:
        """Evaluate performance under stress conditions"""
        
        # Calculate expected time based on data size
        base_time = 1.0  # 1 second for 1000 items
        expected_time = base_time * (data_size / 1000)
        
        # Performance score based on how close to expected time
        if execution_time <= expected_time:
            return 1.0
        elif execution_time <= expected_time * 2:
            return 0.8
        elif execution_time <= expected_time * 5:
            return 0.5
        else:
            return 0.2
    
    def _calculate_performance_degradation(self, test_results: List[ValidationTestResult]) -> float:
        """Calculate performance degradation across test results"""
        
        performance_scores = [
            result.score for result in test_results 
            if result.metadata.get("test_type") == "stress_performance"
        ]
        
        if len(performance_scores) < 2:
            return 0.0
        
        # Calculate degradation from best to worst performance
        best_score = max(performance_scores)
        worst_score = min(performance_scores)
        
        return (best_score - worst_score) / max(0.001, best_score)
    
    async def _calculate_performance_metrics(
        self,
        test_results: List[ValidationTestResult],
        total_execution_time: float
    ) -> Dict[str, Any]:
        """Calculate comprehensive performance metrics"""
        
        metrics = {
            "total_execution_time": total_execution_time,
            "average_test_time": sum(r.execution_time for r in test_results) / max(1, len(test_results)),
            "longest_test_time": max((r.execution_time for r in test_results), default=0),
            "shortest_test_time": min((r.execution_time for r in test_results), default=0)
        }
        
        # Category-specific metrics
        by_category = {}
        for result in test_results:
            category = result.metadata.get("test_category", "unknown")
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(result)
        
        for category, results in by_category.items():
            metrics[f"{category}_tests"] = len(results)
            metrics[f"{category}_success_rate"] = sum(1 for r in results if r.passed) / len(results)
            metrics[f"{category}_average_score"] = sum(r.score for r in results) / len(results)
        
        return metrics
    
    def _generate_recommendations(
        self,
        test_results: List[ValidationTestResult],
        overall_score: float
    ) -> List[str]:
        """Generate recommendations based on test results"""
        
        recommendations = []
        
        # Overall score recommendations
        if overall_score < 0.5:
            recommendations.append("Overall validation score is low. Consider reviewing conversion logic.")
        elif overall_score < 0.8:
            recommendations.append("Validation score could be improved. Check specific test failures.")
        
        # Failed test recommendations
        failed_tests = [r for r in test_results if not r.passed]
        if failed_tests:
            critical_failures = [r for r in failed_tests if r.metadata.get("criticality") == "critical"]
            if critical_failures:
                recommendations.append(f"Critical tests failed: {', '.join(r.test_name for r in critical_failures)}")
        
        # Performance recommendations
        slow_tests = [r for r in test_results if r.execution_time > 30.0]
        if slow_tests:
            recommendations.append("Some tests took longer than expected. Consider performance optimization.")
        
        # Category-specific recommendations
        semantic_failures = [r for r in test_results if not r.passed and r.metadata.get("test_category") == "semantic"]
        if semantic_failures:
            recommendations.append("Semantic preservation issues detected. Review embedding and similarity calculations.")
        
        structural_failures = [r for r in test_results if not r.passed and r.metadata.get("test_category") == "structural"]
        if structural_failures:
            recommendations.append("Structural integrity issues detected. Review conversion algorithms.")
        
        return recommendations
    
    def _generate_round_trip_recommendations(self, round_trip_result: ValidationResult) -> List[str]:
        """Generate recommendations for round-trip validation"""
        
        recommendations = []
        
        if not round_trip_result.valid:
            recommendations.append("Round-trip conversion failed. Check conversion reversibility.")
        
        if round_trip_result.preservation_score < 0.8:
            recommendations.append("Information loss detected during round-trip conversion.")
        
        if not round_trip_result.semantic_match:
            recommendations.append("Semantic meaning changed during round-trip conversion.")
        
        if round_trip_result.errors:
            recommendations.append("Conversion errors occurred. Review error handling and data validation.")
        
        return recommendations
    
    def _generate_stress_recommendations(self, test_results: List[ValidationTestResult]) -> List[str]:
        """Generate recommendations for stress test results"""
        
        recommendations = []
        
        # Check for performance degradation
        performance_degradation = self._calculate_performance_degradation(test_results)
        if performance_degradation > 0.5:
            recommendations.append("Significant performance degradation under load. Consider optimization.")
        
        # Check for timeouts
        timeouts = [r for r in test_results if "timeout" in r.metadata.get("test_type", "")]
        if timeouts:
            recommendations.append("Conversion timeouts occurred under stress. Implement better resource management.")
        
        # Check for concurrent operation failures
        concurrent_failures = [r for r in test_results if r.metadata.get("test_type") == "concurrent_error"]
        if concurrent_failures:
            recommendations.append("Concurrent operations failed. Review thread safety and resource locking.")
        
        return recommendations
    
    def _create_validation_summary(
        self,
        test_results: List[ValidationTestResult],
        overall_score: float,
        performance_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create validation summary"""
        
        return {
            "overall_assessment": "PASS" if overall_score >= self.integrity_threshold else "FAIL",
            "score_breakdown": {
                "structural": sum(r.score for r in test_results if r.metadata.get("test_category") == "structural") / max(1, sum(1 for r in test_results if r.metadata.get("test_category") == "structural")),
                "semantic": sum(r.score for r in test_results if r.metadata.get("test_category") == "semantic") / max(1, sum(1 for r in test_results if r.metadata.get("test_category") == "semantic")),
                "performance": sum(r.score for r in test_results if r.metadata.get("test_category") == "performance") / max(1, sum(1 for r in test_results if r.metadata.get("test_category") == "performance")),
                "integrity": sum(r.score for r in test_results if r.metadata.get("test_category") == "integrity") / max(1, sum(1 for r in test_results if r.metadata.get("test_category") == "integrity"))
            },
            "critical_issues": [r.test_name for r in test_results if not r.passed and r.metadata.get("criticality") == "critical"],
            "performance_summary": {
                "total_time": performance_metrics.get("total_execution_time", 0),
                "average_test_time": performance_metrics.get("average_test_time", 0),
                "performance_rating": "GOOD" if performance_metrics.get("average_test_time", 0) < 10 else "NEEDS_IMPROVEMENT"
            }
        }
    
    def _calculate_data_size(self, data: Any) -> int:
        """Calculate approximate size of data"""
        try:
            if isinstance(data, dict):
                return len(json.dumps(data))
            elif isinstance(data, pd.DataFrame):
                return len(data) * len(data.columns)
            elif isinstance(data, np.ndarray):
                return data.size
            elif isinstance(data, list):
                return len(data)
            else:
                return len(str(data))
        except Exception:
            return 0
    
    def _generate_validation_id(self) -> str:
        """Generate unique validation ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_suffix = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
        return f"validation_{timestamp}_{random_suffix}"
    
    async def _test_structural_integrity(self, original_data: Any, converted_data: Any, 
                                       source_format: DataFormat, target_format: DataFormat,
                                       **kwargs) -> ValidationTestResult:
        """Test structural integrity of conversion"""
        start_time = time.time()
        errors = []
        warnings = []
        details = {}
        
        try:
            # Check basic structure preservation
            if source_format == DataFormat.GRAPH and target_format == DataFormat.TABLE:
                # Check node and edge counts
                if isinstance(original_data, dict):
                    original_nodes = len(original_data.get('nodes', []))
                    original_edges = len(original_data.get('edges', []))
                    
                    # Table should have rows for nodes or edges
                    if isinstance(converted_data, pd.DataFrame):
                        converted_rows = len(converted_data)
                        if converted_rows == 0:
                            errors.append("No data in converted table")
                        
                        details['original_nodes'] = original_nodes
                        details['original_edges'] = original_edges
                        details['converted_rows'] = converted_rows
            
            elif source_format == DataFormat.TABLE and target_format == DataFormat.GRAPH:
                # Check that table rows became nodes
                if isinstance(original_data, pd.DataFrame) and isinstance(converted_data, dict):
                    original_rows = len(original_data)
                    converted_nodes = len(converted_data.get('nodes', []))
                    
                    if converted_nodes == 0:
                        errors.append("No nodes in converted graph")
                    
                    details['original_rows'] = original_rows
                    details['converted_nodes'] = converted_nodes
            
            elif source_format == DataFormat.VECTOR:
                # Check vector dimensions preserved
                if isinstance(original_data, np.ndarray):
                    original_shape = original_data.shape
                    
                    if target_format == DataFormat.GRAPH:
                        nodes = converted_data.get('nodes', [])
                        if len(nodes) != original_shape[0]:
                            errors.append(f"Vector count mismatch: {original_shape[0]} -> {len(nodes)}")
                    
                    elif target_format == DataFormat.TABLE:
                        if len(converted_data) != original_shape[0]:
                            errors.append(f"Row count mismatch: {original_shape[0]} -> {len(converted_data)}")
            
            # Calculate score
            score = 1.0 if not errors else max(0.0, 1.0 - (len(errors) * 0.2))
            
            return ValidationTestResult(
                test_id="structural_integrity",
                test_name="Structural Integrity Check",
                passed=len(errors) == 0,
                score=score,
                execution_time=time.time() - start_time,
                details=details,
                errors=errors,
                warnings=warnings,
                metadata={
                    "test_category": "structural",
                    "source_format": source_format.value,
                    "target_format": target_format.value
                }
            )
            
        except Exception as e:
            return ValidationTestResult(
                test_id="structural_integrity",
                test_name="Structural Integrity Check",
                passed=False,
                score=0.0,
                execution_time=time.time() - start_time,
                details={},
                errors=[f"Test failed: {str(e)}"],
                warnings=[],
                metadata={"error": str(e)}
            )
    
    async def _test_semantic_preservation(self, original_data: Any, converted_data: Any,
                                        source_format: DataFormat, target_format: DataFormat,
                                        **kwargs) -> ValidationTestResult:
        """Test semantic preservation in conversion"""
        start_time = time.time()
        errors = []
        warnings = []
        details = {}
        
        try:
            # Extract semantic features from both datasets
            original_features = self._extract_semantic_features(original_data, source_format)
            converted_features = self._extract_semantic_features(converted_data, target_format)
            
            # Compare key semantic properties
            if 'entity_types' in original_features and 'entity_types' in converted_features:
                original_types = set(original_features['entity_types'])
                converted_types = set(converted_features['entity_types'])
                
                missing_types = original_types - converted_types
                if missing_types:
                    errors.append(f"Missing entity types: {missing_types}")
                
                details['entity_type_preservation'] = len(converted_types) / max(1, len(original_types))
            
            # Check relationship preservation
            if 'relationships' in original_features and 'relationships' in converted_features:
                original_rels = original_features['relationships']
                converted_rels = converted_features['relationships']
                
                if abs(original_rels - converted_rels) / max(1, original_rels) > 0.1:
                    warnings.append(f"Relationship count changed: {original_rels} -> {converted_rels}")
                
                details['relationship_preservation'] = min(converted_rels, original_rels) / max(1, original_rels)
            
            # Check value distributions
            if 'value_stats' in original_features and 'value_stats' in converted_features:
                for stat_name in ['mean', 'std', 'min', 'max']:
                    if stat_name in original_features['value_stats'] and stat_name in converted_features['value_stats']:
                        original_val = original_features['value_stats'][stat_name]
                        converted_val = converted_features['value_stats'][stat_name]
                        
                        if original_val != 0:
                            relative_diff = abs(original_val - converted_val) / abs(original_val)
                            if relative_diff > 0.05:  # 5% tolerance
                                warnings.append(f"{stat_name} changed by {relative_diff*100:.1f}%")
            
            # Calculate semantic preservation score
            preservation_scores = []
            if 'entity_type_preservation' in details:
                preservation_scores.append(details['entity_type_preservation'])
            if 'relationship_preservation' in details:
                preservation_scores.append(details['relationship_preservation'])
            
            score = sum(preservation_scores) / len(preservation_scores) if preservation_scores else 0.8
            
            return ValidationTestResult(
                test_id="semantic_preservation",
                test_name="Semantic Preservation Check",
                passed=len(errors) == 0 and score >= 0.8,
                score=score,
                execution_time=time.time() - start_time,
                details=details,
                errors=errors,
                warnings=warnings,
                metadata={
                    "test_category": "semantic",
                    "preservation_score": score
                }
            )
            
        except Exception as e:
            return ValidationTestResult(
                test_id="semantic_preservation",
                test_name="Semantic Preservation Check",
                passed=False,
                score=0.0,
                execution_time=time.time() - start_time,
                details={},
                errors=[f"Test failed: {str(e)}"],
                warnings=[],
                metadata={"error": str(e)}
            )
    
    def _extract_semantic_features(self, data: Any, data_format: DataFormat) -> Dict[str, Any]:
        """Extract semantic features from data"""
        features = {}
        
        try:
            if data_format == DataFormat.GRAPH and isinstance(data, dict):
                nodes = data.get('nodes', [])
                edges = data.get('edges', [])
                
                # Extract entity types
                entity_types = set()
                for node in nodes:
                    if 'type' in node:
                        entity_types.add(node['type'])
                    elif 'entity_type' in node.get('properties', {}):
                        entity_types.add(node['properties']['entity_type'])
                
                features['entity_types'] = list(entity_types)
                features['relationships'] = len(edges)
                features['node_count'] = len(nodes)
                
            elif data_format == DataFormat.TABLE and isinstance(data, pd.DataFrame):
                # Extract column types and statistics
                features['columns'] = list(data.columns)
                features['row_count'] = len(data)
                
                # Get value statistics for numeric columns
                numeric_cols = data.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    features['value_stats'] = {
                        'mean': float(data[numeric_cols].mean().mean()),
                        'std': float(data[numeric_cols].std().mean()),
                        'min': float(data[numeric_cols].min().min()),
                        'max': float(data[numeric_cols].max().max())
                    }
                
            elif data_format == DataFormat.VECTOR and isinstance(data, np.ndarray):
                features['shape'] = data.shape
                features['value_stats'] = {
                    'mean': float(data.mean()),
                    'std': float(data.std()),
                    'min': float(data.min()),
                    'max': float(data.max())
                }
                
        except Exception as e:
            logger.error(f"Error extracting semantic features: {e}")
            
        return features
    
    async def _test_performance_benchmark(self, original_data: Any, converted_data: Any,
                                        source_format: DataFormat, target_format: DataFormat,
                                        **kwargs) -> ValidationTestResult:
        """Benchmark conversion performance"""
        start_time = time.time()
        errors = []
        warnings = []
        details = {}
        
        try:
            # Get data size
            data_size = self._calculate_data_size(original_data)
            details['data_size'] = data_size
            
            # Perform multiple conversion runs for benchmarking
            conversion_times = []
            num_runs = kwargs.get('benchmark_runs', 3)
            
            for i in range(num_runs):
                run_start = time.time()
                
                # Perform conversion
                try:
                    result = await self.converter.convert_data(
                        original_data, source_format, target_format
                    )
                    
                    if result.success:
                        run_time = time.time() - run_start
                        conversion_times.append(run_time)
                    else:
                        errors.append(f"Conversion failed on run {i+1}")
                        
                except Exception as e:
                    errors.append(f"Conversion error on run {i+1}: {e}")
            
            if conversion_times:
                # Calculate performance metrics
                avg_time = sum(conversion_times) / len(conversion_times)
                min_time = min(conversion_times)
                max_time = max(conversion_times)
                
                details['avg_conversion_time'] = avg_time
                details['min_conversion_time'] = min_time
                details['max_conversion_time'] = max_time
                details['throughput_mb_per_sec'] = (data_size / 1024 / 1024) / avg_time if avg_time > 0 else 0
                
                # Performance scoring
                if avg_time < 1.0:
                    performance_score = 1.0
                elif avg_time < 5.0:
                    performance_score = 0.8
                elif avg_time < 10.0:
                    performance_score = 0.6
                else:
                    performance_score = 0.4
                    warnings.append(f"Slow conversion: {avg_time:.2f}s average")
                
            else:
                performance_score = 0.0
                errors.append("No successful conversion runs")
            
            return ValidationTestResult(
                test_id="performance_benchmark",
                test_name="Performance Benchmark",
                passed=len(errors) == 0 and performance_score >= 0.6,
                score=performance_score,
                execution_time=time.time() - start_time,
                details=details,
                errors=errors,
                warnings=warnings,
                metadata={
                    "test_category": "performance",
                    "benchmark_runs": num_runs,
                    "data_size_bytes": data_size
                }
            )
            
        except Exception as e:
            return ValidationTestResult(
                test_id="performance_benchmark",
                test_name="Performance Benchmark",
                passed=False,
                score=0.0,
                execution_time=time.time() - start_time,
                details={},
                errors=[f"Benchmark failed: {str(e)}"],
                warnings=[],
                metadata={"error": str(e)}
            )
    
    async def _test_data_integrity(self, original_data: Any, converted_data: Any,
                                 source_format: DataFormat, target_format: DataFormat,
                                 **kwargs) -> ValidationTestResult:
        """Comprehensive data integrity check"""
        start_time = time.time()
        errors = []
        warnings = []
        details = {}
        
        try:
            # Test round-trip conversion
            round_trip_result = await self._test_round_trip_integrity(
                original_data, source_format, target_format
            )
            
            details['round_trip_score'] = round_trip_result['score']
            if round_trip_result['score'] < 0.9:
                warnings.append(f"Round-trip integrity score: {round_trip_result['score']:.2f}")
            
            # Check data completeness
            completeness = self._check_data_completeness(original_data, converted_data, 
                                                        source_format, target_format)
            details['completeness_score'] = completeness['score']
            
            if completeness['missing_elements']:
                errors.append(f"Missing elements: {completeness['missing_elements']}")
            
            # Check data consistency
            consistency = self._check_data_consistency(converted_data, target_format)
            details['consistency_score'] = consistency['score']
            
            if consistency['inconsistencies']:
                warnings.extend(consistency['inconsistencies'])
            
            # Overall integrity score
            integrity_score = (
                details['round_trip_score'] * 0.4 +
                details['completeness_score'] * 0.4 +
                details['consistency_score'] * 0.2
            )
            
            return ValidationTestResult(
                test_id="data_integrity",
                test_name="Data Integrity Check",
                passed=len(errors) == 0 and integrity_score >= self.integrity_threshold,
                score=integrity_score,
                execution_time=time.time() - start_time,
                details=details,
                errors=errors,
                warnings=warnings,
                metadata={
                    "test_category": "integrity",
                    "integrity_threshold": self.integrity_threshold
                }
            )
            
        except Exception as e:
            return ValidationTestResult(
                test_id="data_integrity",
                test_name="Data Integrity Check",
                passed=False,
                score=0.0,
                execution_time=time.time() - start_time,
                details={},
                errors=[f"Integrity check failed: {str(e)}"],
                warnings=[],
                metadata={"error": str(e)}
            )
    
    async def _test_round_trip_integrity(self, data: Any, source_format: DataFormat, 
                                       target_format: DataFormat) -> Dict[str, Any]:
        """Test round-trip conversion integrity"""
        try:
            # Convert to target format
            conversion1 = await self.converter.convert_data(data, source_format, target_format)
            if not conversion1.success:
                return {'score': 0.0, 'error': 'First conversion failed'}
            
            # Convert back to source format
            conversion2 = await self.converter.convert_data(
                conversion1.data, target_format, source_format
            )
            if not conversion2.success:
                return {'score': 0.0, 'error': 'Return conversion failed'}
            
            # Compare original and round-trip data
            similarity = self._calculate_data_similarity(data, conversion2.data, source_format)
            
            return {
                'score': similarity,
                'conversions': 2,
                'preservation_score': (conversion1.preservation_score + conversion2.preservation_score) / 2
            }
            
        except Exception as e:
            return {'score': 0.0, 'error': str(e)}
    
    def _check_data_completeness(self, original: Any, converted: Any,
                               source_format: DataFormat, target_format: DataFormat) -> Dict[str, Any]:
        """Check if all data elements are preserved"""
        missing_elements = []
        score = 1.0
        
        try:
            if source_format == DataFormat.GRAPH and isinstance(original, dict):
                original_nodes = set(n.get('id', f"node_{i}") for i, n in enumerate(original.get('nodes', [])))
                
                if target_format == DataFormat.TABLE and isinstance(converted, pd.DataFrame):
                    # Check if node IDs are preserved
                    if 'id' in converted.columns:
                        converted_ids = set(converted['id'])
                        missing = original_nodes - converted_ids
                        if missing:
                            missing_elements.extend(list(missing)[:5])  # First 5
                            score *= (len(converted_ids) / len(original_nodes))
                
            return {'score': score, 'missing_elements': missing_elements}
            
        except Exception:
            return {'score': 0.5, 'missing_elements': ['Unable to check completeness']}
    
    def _check_data_consistency(self, data: Any, data_format: DataFormat) -> Dict[str, Any]:
        """Check internal data consistency"""
        inconsistencies = []
        score = 1.0
        
        try:
            if data_format == DataFormat.GRAPH and isinstance(data, dict):
                nodes = data.get('nodes', [])
                edges = data.get('edges', [])
                
                # Check edge consistency
                node_ids = set(n.get('id') for n in nodes)
                for edge in edges:
                    if edge.get('source') not in node_ids:
                        inconsistencies.append(f"Edge source '{edge.get('source')}' not in nodes")
                        score *= 0.9
                    if edge.get('target') not in node_ids:
                        inconsistencies.append(f"Edge target '{edge.get('target')}' not in nodes")
                        score *= 0.9
                        
            elif data_format == DataFormat.TABLE and isinstance(data, pd.DataFrame):
                # Check for null values in critical columns
                if 'id' in data.columns and data['id'].isnull().any():
                    inconsistencies.append("Null values in ID column")
                    score *= 0.8
                    
            return {'score': score, 'inconsistencies': inconsistencies[:5]}  # First 5
            
        except Exception:
            return {'score': 0.5, 'inconsistencies': ['Unable to check consistency']}
    
    def _calculate_data_similarity(self, data1: Any, data2: Any, data_format: DataFormat) -> float:
        """Calculate similarity between two datasets"""
        try:
            if data_format == DataFormat.GRAPH:
                # Compare graph structures
                nodes1 = len(data1.get('nodes', []))
                nodes2 = len(data2.get('nodes', []))
                edges1 = len(data1.get('edges', []))
                edges2 = len(data2.get('edges', []))
                
                node_similarity = min(nodes1, nodes2) / max(nodes1, nodes2) if max(nodes1, nodes2) > 0 else 1.0
                edge_similarity = min(edges1, edges2) / max(edges1, edges2) if max(edges1, edges2) > 0 else 1.0
                
                return (node_similarity + edge_similarity) / 2
                
            elif data_format == DataFormat.TABLE:
                # Compare table structures
                if isinstance(data1, pd.DataFrame) and isinstance(data2, pd.DataFrame):
                    row_similarity = min(len(data1), len(data2)) / max(len(data1), len(data2)) if max(len(data1), len(data2)) > 0 else 1.0
                    col_similarity = len(set(data1.columns) & set(data2.columns)) / len(set(data1.columns) | set(data2.columns)) if len(set(data1.columns) | set(data2.columns)) > 0 else 1.0
                    
                    return (row_similarity + col_similarity) / 2
                    
            elif data_format == DataFormat.VECTOR:
                # Compare vector shapes and values
                if isinstance(data1, np.ndarray) and isinstance(data2, np.ndarray):
                    if data1.shape == data2.shape:
                        # Cosine similarity
                        from sklearn.metrics.pairwise import cosine_similarity
                        similarity = cosine_similarity(data1.reshape(1, -1), data2.reshape(1, -1))[0, 0]
                        return max(0, similarity)  # Ensure non-negative
                    else:
                        return 0.0
                        
            return 0.5  # Default similarity
            
        except Exception:
            return 0.0