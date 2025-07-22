"""
Mitchell-Agle-Wood Stakeholder Salience Calculator
Implements the geometric mean calculation with edge case handling and validation
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
    from schemas.stakeholder_schemas import SalienceScore, LegitimacyScore, UrgencyScore, PowerScore
    from schemas.base_schemas import ValidationResult
except ImportError as e:
    print(f"Warning: Could not import schemas: {e}")
    # Fallback for standalone testing
    SalienceScore = dict
    ValidationResult = dict

@dataclass
class EdgeCaseResult:
    """Result of edge case handling"""
    handled: bool
    strategy: str
    explanation: str
    modified_input: Optional[Dict[str, float]] = None

class SalienceCalculationError(Exception):
    """Custom exception for salience calculation errors"""
    pass

class MitchellAgleWoodCalculator:
    """
    Implements the Mitchell-Agle-Wood stakeholder salience calculation
    with comprehensive edge case handling and validation
    """
    
    def __init__(self, enable_logging: bool = True):
        self.enable_logging = enable_logging
        self.calculation_log = []
        
        # Test cases from theory schema
        self.test_cases = [
            {
                "inputs": {"legitimacy": 1.0, "urgency": 1.0, "power": 1.0},
                "expected_output": 1.0,
                "description": "Definitive stakeholder - maximum salience"
            },
            {
                "inputs": {"legitimacy": 0.8, "urgency": 0.6, "power": 0.4},
                "expected_output": 0.573,
                "description": "Moderate salience stakeholder"
            },
            {
                "inputs": {"legitimacy": 0.0, "urgency": 0.0, "power": 0.0},
                "expected_output": 0.0,
                "description": "Non-stakeholder - zero salience"
            },
            {
                "inputs": {"legitimacy": 1.0, "urgency": 0.0, "power": 0.0},
                "expected_output": 0.0,
                "description": "Discretionary stakeholder - zero urgency results in zero salience"
            },
            {
                "inputs": {"legitimacy": 0.0, "urgency": 1.0, "power": 1.0},
                "expected_output": 0.0,
                "description": "Edge case - zero legitimacy results in zero salience"
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
            print(f"[SALIENCE] {message}")
    
    def validate_inputs(self, legitimacy: float, urgency: float, power: float) -> ValidationResult:
        """
        Validate input parameters for salience calculation
        
        Args:
            legitimacy: Legitimacy score (0.0-1.0)
            urgency: Urgency score (0.0-1.0) 
            power: Power score (0.0-1.0)
            
        Returns:
            ValidationResult with validation status and any errors
        """
        errors = []
        warnings = []
        
        # Check for required inputs
        if legitimacy is None:
            errors.append("Legitimacy score is required")
        if urgency is None:
            errors.append("Urgency score is required")
        if power is None:
            errors.append("Power score is required")
            
        if errors:
            return ValidationResult(
                valid=False,
                errors=errors,
                metadata={"validation_type": "input_validation"}
            )
        
        # Check value ranges
        for name, value in [("legitimacy", legitimacy), ("urgency", urgency), ("power", power)]:
            if not isinstance(value, (int, float)):
                errors.append(f"{name} must be a number, got {type(value)}")
            elif value < 0.0:
                errors.append(f"{name} cannot be negative, got {value}")
            elif value > 1.0:
                errors.append(f"{name} cannot exceed 1.0, got {value}")
            elif value == 0.0:
                warnings.append(f"{name} is zero, will result in zero salience")
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            metadata={
                "validation_type": "input_validation",
                "inputs": {"legitimacy": legitimacy, "urgency": urgency, "power": power}
            }
        )
    
    def handle_edge_cases(self, legitimacy: float, urgency: float, power: float) -> EdgeCaseResult:
        """
        Handle edge cases in salience calculation
        
        Args:
            legitimacy: Legitimacy score
            urgency: Urgency score
            power: Power score
            
        Returns:
            EdgeCaseResult describing how edge case was handled
        """
        
        # Zero input handling
        zero_inputs = [name for name, value in [("legitimacy", legitimacy), ("urgency", urgency), ("power", power)] if value == 0.0]
        if zero_inputs:
            return EdgeCaseResult(
                handled=True,
                strategy="zero_geometric_mean",
                explanation=f"Geometric mean with zero inputs ({', '.join(zero_inputs)}) equals zero",
                modified_input=None
            )
        
        # Very small values (potential floating point issues)
        small_threshold = 1e-10
        small_inputs = [name for name, value in [("legitimacy", legitimacy), ("urgency", urgency), ("power", power)] if 0 < value < small_threshold]
        if small_inputs:
            return EdgeCaseResult(
                handled=True,
                strategy="small_value_warning",
                explanation=f"Very small values detected ({', '.join(small_inputs)}) may cause floating point precision issues",
                modified_input=None
            )
        
        # Perfect scores (all 1.0)
        if legitimacy == 1.0 and urgency == 1.0 and power == 1.0:
            return EdgeCaseResult(
                handled=True,
                strategy="perfect_scores",
                explanation="All dimensions at maximum (1.0) - definitive stakeholder",
                modified_input=None
            )
        
        # No edge cases detected
        return EdgeCaseResult(
            handled=False,
            strategy="none",
            explanation="No edge cases detected - standard calculation applies"
        )
    
    def calculate_geometric_mean(self, legitimacy: float, urgency: float, power: float) -> float:
        """
        Calculate geometric mean of three dimensions
        
        Args:
            legitimacy: Legitimacy score (0.0-1.0)
            urgency: Urgency score (0.0-1.0)
            power: Power score (0.0-1.0)
            
        Returns:
            Geometric mean as salience score
        """
        
        # Handle zero case explicitly
        if legitimacy == 0.0 or urgency == 0.0 or power == 0.0:
            self._log("Zero input detected - geometric mean equals zero")
            return 0.0
        
        # Calculate geometric mean
        product = legitimacy * urgency * power
        geometric_mean = math.pow(product, 1.0/3.0)
        
        self._log(f"Calculated: ({legitimacy} * {urgency} * {power})^(1/3) = {geometric_mean}")
        
        return geometric_mean
    
    def determine_mitchell_category(self, legitimacy: float, urgency: float, power: float) -> str:
        """
        Determine Mitchell typology category based on dimension values
        
        Args:
            legitimacy: Legitimacy score (0.0-1.0)
            urgency: Urgency score (0.0-1.0)
            power: Power score (0.0-1.0)
            
        Returns:
            Mitchell category string
        """
        
        # Use threshold of 0.5 to determine "high" vs "low"
        threshold = 0.5
        
        high_legitimacy = legitimacy >= threshold
        high_urgency = urgency >= threshold  
        high_power = power >= threshold
        
        # Mitchell's seven stakeholder types
        if high_legitimacy and high_urgency and high_power:
            return "definitive"
        elif high_legitimacy and high_urgency and not high_power:
            return "dependent"
        elif high_legitimacy and not high_urgency and high_power:
            return "dominant"
        elif not high_legitimacy and high_urgency and high_power:
            return "dangerous"
        elif high_legitimacy and not high_urgency and not high_power:
            return "discretionary"
        elif not high_legitimacy and high_urgency and not high_power:
            return "demanding"
        elif not high_legitimacy and not high_urgency and high_power:
            return "dormant"
        else:
            return "non-stakeholder"
    
    def calculate_salience(self, legitimacy: float, urgency: float, power: float, 
                          stakeholder_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Calculate stakeholder salience with full validation and metadata
        
        Args:
            legitimacy: Legitimacy score (0.0-1.0)
            urgency: Urgency score (0.0-1.0)
            power: Power score (0.0-1.0)
            stakeholder_id: Optional stakeholder identifier for logging
            
        Returns:
            Dictionary with salience score and metadata
        """
        
        calculation_start = datetime.now()
        stakeholder_label = stakeholder_id or "unknown"
        
        self._log(f"Starting salience calculation for stakeholder: {stakeholder_label}")
        self._log(f"Input values - Legitimacy: {legitimacy}, Urgency: {urgency}, Power: {power}")
        
        # Validate inputs
        validation = self.validate_inputs(legitimacy, urgency, power)
        if not validation.valid:
            raise SalienceCalculationError(f"Input validation failed: {validation.errors}")
        
        if validation.warnings:
            self._log(f"Validation warnings: {validation.warnings}")
        
        # Handle edge cases
        edge_case = self.handle_edge_cases(legitimacy, urgency, power)
        self._log(f"Edge case handling: {edge_case.strategy} - {edge_case.explanation}")
        
        # Calculate salience
        salience_score = self.calculate_geometric_mean(legitimacy, urgency, power)
        
        # Determine Mitchell category
        mitchell_category = self.determine_mitchell_category(legitimacy, urgency, power)
        
        calculation_end = datetime.now()
        calculation_time = (calculation_end - calculation_start).total_seconds()
        
        self._log(f"Calculation completed - Salience: {salience_score}, Category: {mitchell_category}")
        
        # Prepare result
        result = {
            "salience_score": salience_score,
            "mitchell_category": mitchell_category,
            "calculation_method": "geometric_mean",
            "input_components": {
                "legitimacy": legitimacy,
                "urgency": urgency,
                "power": power
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
                "stakeholder_id": stakeholder_id,
                "calculation_timestamp": calculation_end.isoformat(),
                "calculation_time_seconds": calculation_time,
                "algorithm_version": "mitchell_agle_wood_v1.0"
            }
        }
        
        return result
    
    def run_test_cases(self) -> Dict[str, Any]:
        """
        Run all test cases and return validation results
        
        Returns:
            Dictionary with test results and validation status
        """
        
        self._log("Running Mitchell-Agle-Wood salience test cases")
        
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
                result = self.calculate_salience(
                    legitimacy=inputs["legitimacy"],
                    urgency=inputs["urgency"], 
                    power=inputs["power"],
                    stakeholder_id=f"test_case_{i+1}"
                )
                
                actual = result["salience_score"]
                tolerance = 0.01   # Allow reasonable floating point differences
                
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
                    "mitchell_category": result["mitchell_category"],
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
    
    print("Mitchell-Agle-Wood Stakeholder Salience Calculator")
    print("=" * 50)
    
    calculator = MitchellAgleWoodCalculator(enable_logging=True)
    
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
    
    # Interactive calculation
    print("\n" + "=" * 50)
    print("INTERACTIVE CALCULATION")
    print("=" * 50)
    
    try:
        print("Enter stakeholder dimensions (0.0-1.0):")
        legitimacy = float(input("Legitimacy: "))
        urgency = float(input("Urgency: "))
        power = float(input("Power: "))
        
        result = calculator.calculate_salience(legitimacy, urgency, power, "interactive_test")
        
        print(f"\nRESULT:")
        print(f"Salience Score: {result['salience_score']:.3f}")
        print(f"Mitchell Category: {result['mitchell_category']}")
        print(f"Edge Case Strategy: {result['edge_case_handling']['strategy']}")
        print(f"Calculation Time: {result['metadata']['calculation_time_seconds']:.4f}s")
        
    except (ValueError, KeyboardInterrupt):
        print("Interactive calculation skipped.")
    
    return test_results

if __name__ == "__main__":
    results = main()