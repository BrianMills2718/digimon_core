"""
Resource Dependency Calculator
Implements the Resource Dependency Theory calculation with edge case handling
"""

import math
import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import sys
import os

# Add project paths for importing schemas
sys.path.append('/home/brian/projects/Digimons/stress_test_2025.07211755')
sys.path.append('/home/brian/projects/Digimons/src')

try:
    from schemas.resource_dependency_schemas import (
        DependencyScore, ResourceCriticalityScore, ResourceScarcityScore, 
        SubstituteAvailabilityScore, DependencyLevel
    )
    from schemas.base_schemas import ValidationResult
except ImportError as e:
    print(f"Warning: Could not import schemas: {e}")
    DependencyScore = dict
    ValidationResult = dict

@dataclass
class DependencyEdgeCaseResult:
    """Result of dependency edge case handling"""
    handled: bool
    strategy: str
    explanation: str
    modified_input: Optional[Dict[str, float]] = None

class DependencyCalculationError(Exception):
    """Custom exception for dependency calculation errors"""
    pass

class ResourceDependencyCalculator:
    """
    Implements Resource Dependency Theory calculation
    Dependency = (resource_criticality * resource_scarcity * (1 - substitute_availability))^(1/3)
    """
    
    def __init__(self, enable_logging: bool = True):
        self.enable_logging = enable_logging
        self.calculation_log = []
        
        # Test cases from theory schema
        self.test_cases = [
            {
                "inputs": {"resource_criticality": 0.9, "resource_scarcity": 0.8, "substitute_availability": 0.2},
                "expected_output": 0.832,  # (0.9 * 0.8 * 0.8)^(1/3)
                "description": "High dependency scenario"
            },
            {
                "inputs": {"resource_criticality": 0.5, "resource_scarcity": 0.3, "substitute_availability": 0.8},
                "expected_output": 0.311,  # (0.5 * 0.3 * 0.2)^(1/3)
                "description": "Low dependency scenario"
            },
            {
                "inputs": {"resource_criticality": 1.0, "resource_scarcity": 1.0, "substitute_availability": 0.0},
                "expected_output": 1.0,
                "description": "Maximum dependency - critical monopoly"
            },
            {
                "inputs": {"resource_criticality": 0.0, "resource_scarcity": 1.0, "substitute_availability": 0.0},
                "expected_output": 0.0,
                "description": "No dependency - non-critical resource"
            },
            {
                "inputs": {"resource_criticality": 0.6, "resource_scarcity": 0.7, "substitute_availability": 1.0},
                "expected_output": 0.0,
                "description": "No dependency - perfect substitutes available"
            }
        ]
    
    def _log(self, message: str):
        """Log calculation steps if logging enabled"""
        if self.enable_logging:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "message": message
            }
            self.calculation_log.append(log_entry)
            print(f"[DEPENDENCY] {message}")
    
    def validate_inputs(self, criticality: float, scarcity: float, substitute_availability: float) -> ValidationResult:
        """
        Validate input parameters for dependency calculation
        
        Args:
            criticality: Resource criticality score (0.0-1.0)
            scarcity: Resource scarcity score (0.0-1.0)
            substitute_availability: Substitute availability (0.0-1.0)
            
        Returns:
            ValidationResult with validation status and any errors
        """
        errors = []
        warnings = []
        
        # Check for required inputs
        if criticality is None:
            errors.append("Resource criticality score is required")
        if scarcity is None:
            errors.append("Resource scarcity score is required")
        if substitute_availability is None:
            errors.append("Substitute availability score is required")
            
        if errors:
            return ValidationResult(
                valid=False,
                errors=errors,
                metadata={"validation_type": "input_validation"}
            )
        
        # Check value ranges
        for name, value in [("criticality", criticality), ("scarcity", scarcity), ("substitute_availability", substitute_availability)]:
            if not isinstance(value, (int, float)):
                errors.append(f"{name} must be a number, got {type(value)}")
            elif value < 0.0:
                errors.append(f"{name} cannot be negative, got {value}")
            elif value > 1.0:
                errors.append(f"{name} cannot exceed 1.0, got {value}")
            elif value == 0.0 and name in ["criticality", "scarcity"]:
                warnings.append(f"{name} is zero, may result in zero dependency")
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            metadata={
                "validation_type": "input_validation",
                "inputs": {"criticality": criticality, "scarcity": scarcity, "substitute_availability": substitute_availability}
            }
        )
    
    def handle_edge_cases(self, criticality: float, scarcity: float, substitute_availability: float) -> DependencyEdgeCaseResult:
        """
        Handle edge cases in dependency calculation
        
        Args:
            criticality: Resource criticality score
            scarcity: Resource scarcity score
            substitute_availability: Substitute availability score
            
        Returns:
            DependencyEdgeCaseResult describing how edge case was handled
        """
        
        # Critical monopoly case - criticality > 0.9 and no substitutes
        if criticality > 0.9 and substitute_availability < 0.1:
            return DependencyEdgeCaseResult(
                handled=True,
                strategy="critical_monopoly",
                explanation="Critical resource with no substitutes - high dependency regardless of scarcity",
                modified_input=None
            )
        
        # Perfect substitutes case - substitute_availability = 1.0
        if substitute_availability >= 0.95:
            return DependencyEdgeCaseResult(
                handled=True,
                strategy="perfect_substitutes",
                explanation="Perfect substitutes available - dependency approaches zero",
                modified_input=None
            )
        
        # Non-critical resource case
        if criticality == 0.0:
            return DependencyEdgeCaseResult(
                handled=True,
                strategy="non_critical_resource",
                explanation="Non-critical resource - dependency is zero regardless of other factors",
                modified_input=None
            )
        
        # Maximum dependency case
        if criticality == 1.0 and scarcity == 1.0 and substitute_availability == 0.0:
            return DependencyEdgeCaseResult(
                handled=True,
                strategy="maximum_dependency",
                explanation="Perfect storm - critical, scarce resource with no substitutes",
                modified_input=None
            )
        
        # No edge cases detected
        return DependencyEdgeCaseResult(
            handled=False,
            strategy="none",
            explanation="No edge cases detected - standard calculation applies"
        )
    
    def calculate_geometric_mean(self, criticality: float, scarcity: float, substitute_availability: float) -> float:
        """
        Calculate geometric mean for dependency score
        Dependency = (criticality * scarcity * (1 - substitute_availability))^(1/3)
        
        Args:
            criticality: Resource criticality score (0.0-1.0)
            scarcity: Resource scarcity score (0.0-1.0)
            substitute_availability: Substitute availability (0.0-1.0)
            
        Returns:
            Dependency score as geometric mean
        """
        
        # Handle zero criticality explicitly
        if criticality == 0.0:
            self._log("Zero criticality detected - dependency equals zero")
            return 0.0
        
        # Handle perfect substitutes
        if substitute_availability >= 1.0:
            self._log("Perfect substitutes available - dependency equals zero")
            return 0.0
        
        # Calculate dependency using resource dependency formula
        substitute_factor = 1 - substitute_availability
        product = criticality * scarcity * substitute_factor
        dependency_score = math.pow(product, 1.0/3.0)
        
        self._log(f"Calculated: ({criticality} * {scarcity} * {substitute_factor})^(1/3) = {dependency_score}")
        
        return dependency_score
    
    def determine_dependency_level(self, dependency_score: float) -> str:
        """
        Determine dependency level category based on score
        
        Args:
            dependency_score: Calculated dependency score (0.0-1.0)
            
        Returns:
            Dependency level string
        """
        
        if dependency_score >= 0.7:
            return "high"
        elif dependency_score >= 0.4:
            return "moderate"
        else:
            return "low"
    
    def calculate_dependency(self, criticality: float, scarcity: float, substitute_availability: float,
                           resource_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Calculate resource dependency with full validation and metadata
        
        Args:
            criticality: Resource criticality score (0.0-1.0)
            scarcity: Resource scarcity score (0.0-1.0)
            substitute_availability: Substitute availability (0.0-1.0)
            resource_id: Optional resource identifier for logging
            
        Returns:
            Dictionary with dependency score and metadata
        """
        
        calculation_start = datetime.now()
        resource_label = resource_id or "unknown"
        
        self._log(f"Starting dependency calculation for resource: {resource_label}")
        self._log(f"Input values - Criticality: {criticality}, Scarcity: {scarcity}, Substitute Availability: {substitute_availability}")
        
        # Validate inputs
        validation = self.validate_inputs(criticality, scarcity, substitute_availability)
        if not validation.valid:
            raise DependencyCalculationError(f"Input validation failed: {validation.errors}")
        
        if validation.warnings:
            self._log(f"Validation warnings: {validation.warnings}")
        
        # Handle edge cases
        edge_case = self.handle_edge_cases(criticality, scarcity, substitute_availability)
        self._log(f"Edge case handling: {edge_case.strategy} - {edge_case.explanation}")
        
        # Calculate dependency
        dependency_score = self.calculate_geometric_mean(criticality, scarcity, substitute_availability)
        
        # Determine dependency level
        dependency_level = self.determine_dependency_level(dependency_score)
        
        calculation_end = datetime.now()
        calculation_time = (calculation_end - calculation_start).total_seconds()
        
        self._log(f"Calculation completed - Dependency: {dependency_score}, Level: {dependency_level}")
        
        # Prepare result
        result = {
            "dependency_score": dependency_score,
            "dependency_level": dependency_level,
            "calculation_method": "geometric_mean",
            "input_components": {
                "criticality": criticality,
                "scarcity": scarcity,
                "substitute_availability": substitute_availability
            },
            "validation": {
                "input_valid": validation.valid,
                "warnings": validation.warnings
            },
            "edge_case_handling": {
                "strategy": edge_case.strategy,
                "explanation": edge_case.explanation,
                "handled": edge_case.handled
            },
            "metadata": {
                "resource_id": resource_id,
                "calculation_timestamp": calculation_end.isoformat(),
                "calculation_time_seconds": calculation_time,
                "algorithm_version": "resource_dependency_v1.0"
            }
        }
        
        return result
    
    def run_test_cases(self) -> Dict[str, Any]:
        """
        Run all test cases and return validation results
        
        Returns:
            Dictionary with test results and validation status
        """
        
        self._log("Running Resource Dependency Theory test cases")
        
        test_results = []
        total_tests = len(self.test_cases)
        passed_tests = 0
        
        for i, test_case in enumerate(self.test_cases):
            test_start = datetime.now()
            
            inputs = test_case["inputs"]
            expected = test_case["expected_output"]
            description = test_case["description"]
            
            self._log(f"Test {i+1}/{total_tests}: {description}")
            
            try:
                result = self.calculate_dependency(
                    criticality=inputs["resource_criticality"],
                    scarcity=inputs["resource_scarcity"],
                    substitute_availability=inputs["substitute_availability"],
                    resource_id=f"test_case_{i+1}"
                )
                
                actual = result["dependency_score"]
                tolerance = 0.01  # Allow reasonable floating point differences
                
                if abs(actual - expected) <= tolerance:
                    test_passed = True
                    passed_tests += 1
                    self._log(f"✓ PASS - Expected: {expected}, Actual: {actual}")
                else:
                    test_passed = False
                    self._log(f"✗ FAIL - Expected: {expected}, Actual: {actual}, Difference: {abs(actual - expected)}")
                
                test_results.append({
                    "test_number": i + 1,
                    "description": description,
                    "inputs": inputs,
                    "expected_output": expected,
                    "actual_output": actual,
                    "passed": test_passed,
                    "difference": abs(actual - expected),
                    "dependency_level": result["dependency_level"],
                    "calculation_time": (datetime.now() - test_start).total_seconds()
                })
                
            except Exception as e:
                test_passed = False
                self._log(f"✗ ERROR - Test failed with exception: {e}")
                
                test_results.append({
                    "test_number": i + 1,
                    "description": description,
                    "inputs": inputs,
                    "expected_output": expected,
                    "actual_output": None,
                    "passed": False,
                    "error": str(e),
                    "calculation_time": (datetime.now() - test_start).total_seconds()
                })
        
        success_rate = passed_tests / total_tests
        
        summary = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": success_rate,
            "all_tests_passed": success_rate == 1.0,
            "test_results": test_results,
            "validation_timestamp": datetime.now().isoformat()
        }
        
        self._log(f"Test summary: {passed_tests}/{total_tests} passed ({success_rate:.1%})")
        
        return summary
    
    def get_calculation_log(self) -> List[Dict[str, Any]]:
        """Return the calculation log"""
        return self.calculation_log
    
    def clear_log(self):
        """Clear the calculation log"""
        self.calculation_log = []

def main():
    """Main function for standalone testing"""
    
    print("Resource Dependency Theory Calculator")
    print("=" * 50)
    
    calculator = ResourceDependencyCalculator(enable_logging=True)
    
    # Run test cases
    test_results = calculator.run_test_cases()
    
    print("\n" + "=" * 50)
    print("TEST RESULTS SUMMARY")
    print("=" * 50)
    print(f"Tests passed: {test_results['passed_tests']}/{test_results['total_tests']}")
    print(f"Success rate: {test_results['success_rate']:.1%}")
    print(f"All tests passed: {test_results['all_tests_passed']}")
    
    if not test_results['all_tests_passed']:
        print("\nFAILED TESTS:")
        for result in test_results['test_results']:
            if not result['passed']:
                print(f"- Test {result['test_number']}: {result['description']}")
                if 'error' in result:
                    print(f"  Error: {result['error']}")
                else:
                    print(f"  Expected: {result['expected_output']}, Got: {result['actual_output']}")
    
    return test_results

if __name__ == "__main__":
    results = main()