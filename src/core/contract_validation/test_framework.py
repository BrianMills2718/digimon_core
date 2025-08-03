"""
Contract Test Framework

Framework for creating automated contract tests and test data generation.
"""

from typing import Dict, Any, List

try:
    from ..data_models import (
        BaseObject, Document, Chunk, Entity, Relationship, 
        WorkflowState, TextForLLMProcessing,
        ObjectType, QualityTier
    )
except ImportError:
    # For standalone execution
    from data_models import (
        BaseObject, Document, Chunk, Entity, Relationship, 
        WorkflowState, TextForLLMProcessing,
        ObjectType, QualityTier
    )

from .contract_validator import ContractValidator


class ContractTestFramework:
    """Framework for creating automated contract tests"""
    
    def __init__(self, validator: ContractValidator):
        self.validator = validator
        
        # Data type mapping
        self.data_type_mapping = {
            "Document": Document,
            "Chunk": Chunk,
            "Entity": Entity,
            "Relationship": Relationship,
            "WorkflowState": WorkflowState,
            "TextForLLMProcessing": TextForLLMProcessing
        }
    
    def create_test_data(self, data_type: str, **kwargs) -> BaseObject:
        """
        Create test data objects for contract testing
        
        Args:
            data_type: Type of data object to create
            **kwargs: Additional parameters for the object
            
        Returns:
            Test data object
        """
        data_class = self.data_type_mapping.get(data_type)
        if not data_class:
            raise ValueError(f"Unknown data type: {data_type}")
        
        # Create minimal valid object
        base_params = {
            'object_type': getattr(ObjectType, data_type.upper(), data_type),
            'confidence': kwargs.get('confidence', 0.8),
            'quality_tier': kwargs.get('quality_tier', QualityTier.MEDIUM),
            'created_by': kwargs.get('created_by', 'test_framework'),
            'workflow_id': kwargs.get('workflow_id', 'test_workflow')
        }
        
        # Add type-specific required fields
        if data_type == "Document":
            base_params.update({
                'content': kwargs.get('content', 'Test document content'),
                'original_filename': kwargs.get('original_filename', 'test.txt')
            })
        elif data_type == "Chunk":
            base_params.update({
                'content': kwargs.get('content', 'Test chunk content'),
                'document_ref': kwargs.get('document_ref', 'neo4j://document/test-doc'),
                'position': kwargs.get('position', 0)
            })
        elif data_type == "Entity":
            base_params.update({
                'canonical_name': kwargs.get('canonical_name', 'Test Entity'),
                'entity_type': kwargs.get('entity_type', 'PERSON')
            })
        elif data_type == "Relationship":
            base_params.update({
                'relationship_type': kwargs.get('relationship_type', 'RELATED_TO'),
                'source_entity_ref': kwargs.get('source_entity_ref', 'neo4j://entity/test-source'),
                'target_entity_ref': kwargs.get('target_entity_ref', 'neo4j://entity/test-target')
            })
        
        # Override with any provided kwargs
        base_params.update(kwargs)
        
        return data_class(**base_params)
    
    def create_test_suite(self, tool_id: str, contract_type: str = "tool") -> Dict[str, Any]:
        """
        Create a comprehensive test suite for a tool contract
        
        Args:
            tool_id: Tool identifier
            contract_type: Type of contract
            
        Returns:
            Test suite with various test cases
        """
        contract = self.validator.load_contract(tool_id, contract_type)
        
        test_suite = {
            'tool_id': tool_id,
            'contract_type': contract_type,
            'test_cases': []
        }
        
        # Generate positive test cases
        positive_tests = self._generate_positive_tests(contract)
        test_suite['test_cases'].extend(positive_tests)
        
        # Generate negative test cases
        negative_tests = self._generate_negative_tests(contract)
        test_suite['test_cases'].extend(negative_tests)
        
        # Generate edge case tests
        edge_tests = self._generate_edge_case_tests(contract)
        test_suite['test_cases'].extend(edge_tests)
        
        return test_suite
    
    def _generate_positive_tests(self, contract: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate positive test cases that should pass"""
        tests = []
        
        input_contract = contract.get('input_contract', {})
        required_data_types = input_contract.get('required_data_types', [])
        
        # Create test with all required data types
        if required_data_types:
            test_input = {}
            for i, data_type_spec in enumerate(required_data_types):
                data_type = data_type_spec['type']
                test_object = self.create_test_data(data_type)
                test_input[f"input_{i}"] = test_object
            
            tests.append({
                'name': 'valid_input_all_required_types',
                'type': 'positive',
                'input': test_input,
                'expected_result': 'success'
            })
        
        return tests
    
    def _generate_negative_tests(self, contract: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate negative test cases that should fail"""
        tests = []
        
        input_contract = contract.get('input_contract', {})
        required_data_types = input_contract.get('required_data_types', [])
        
        # Test with missing required data types
        if required_data_types:
            tests.append({
                'name': 'missing_required_data_type',
                'type': 'negative',
                'input': {},  # Empty input
                'expected_result': 'validation_error'
            })
        
        # Test with wrong data types
        if required_data_types:
            wrong_input = {}
            for i, data_type_spec in enumerate(required_data_types):
                # Use wrong data type
                wrong_type = 'Document' if data_type_spec['type'] != 'Document' else 'Entity'
                test_object = self.create_test_data(wrong_type)
                wrong_input[f"input_{i}"] = test_object
            
            tests.append({
                'name': 'wrong_data_types',
                'type': 'negative',
                'input': wrong_input,
                'expected_result': 'validation_error'
            })
        
        return tests
    
    def _generate_edge_case_tests(self, contract: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate edge case test scenarios"""
        tests = []
        
        # Test with minimal valid data
        tests.append({
            'name': 'minimal_valid_input',
            'type': 'edge_case',
            'input': self._create_minimal_input(contract),
            'expected_result': 'success'
        })
        
        # Test with maximum valid data
        tests.append({
            'name': 'maximum_valid_input',
            'type': 'edge_case',
            'input': self._create_maximum_input(contract),
            'expected_result': 'success'
        })
        
        return tests
    
    def _create_minimal_input(self, contract: Dict[str, Any]) -> Dict[str, Any]:
        """Create minimal valid input for the contract"""
        input_contract = contract.get('input_contract', {})
        required_data_types = input_contract.get('required_data_types', [])
        
        minimal_input = {}
        for i, data_type_spec in enumerate(required_data_types):
            data_type = data_type_spec['type']
            # Create object with minimal required attributes
            test_object = self.create_test_data(data_type, confidence=0.1)
            minimal_input[f"input_{i}"] = test_object
        
        return minimal_input
    
    def _create_maximum_input(self, contract: Dict[str, Any]) -> Dict[str, Any]:
        """Create maximum valid input for the contract"""
        input_contract = contract.get('input_contract', {})
        required_data_types = input_contract.get('required_data_types', [])
        
        maximum_input = {}
        for i, data_type_spec in enumerate(required_data_types):
            data_type = data_type_spec['type']
            # Create object with maximum attributes
            if data_type == 'Document':
                test_object = self.create_test_data(data_type, 
                    content='Very long document content ' * 100,
                    confidence=1.0,
                    quality_tier=QualityTier.HIGH
                )
            else:
                test_object = self.create_test_data(data_type, confidence=1.0)
            maximum_input[f"input_{i}"] = test_object
        
        return maximum_input
    
    def run_test_suite(self, test_suite: Dict[str, Any], tool_instance: Any) -> Dict[str, Any]:
        """
        Run a test suite against a tool instance
        
        Args:
            test_suite: Test suite to run
            tool_instance: Tool instance to test
            
        Returns:
            Test results
        """
        results = {
            'tool_id': test_suite['tool_id'],
            'total_tests': len(test_suite['test_cases']),
            'passed': 0,
            'failed': 0,
            'errors': 0,
            'test_results': []
        }
        
        contract = self.validator.load_contract(
            test_suite['tool_id'], 
            test_suite['contract_type']
        )
        
        for test_case in test_suite['test_cases']:
            try:
                # Run the test
                success, errors, output = self.validator.data_flow_validator.validate_data_flow(
                    tool_instance, contract, test_case['input']
                )
                
                # Evaluate result
                if test_case['type'] == 'positive':
                    test_passed = success and not errors
                elif test_case['type'] == 'negative':
                    test_passed = not success or errors
                else:  # edge_case
                    test_passed = success  # Edge cases should generally pass
                
                if test_passed:
                    results['passed'] += 1
                else:
                    results['failed'] += 1
                
                results['test_results'].append({
                    'name': test_case['name'],
                    'type': test_case['type'],
                    'passed': test_passed,
                    'errors': errors,
                    'output': output
                })
                
            except Exception as e:
                results['errors'] += 1
                results['test_results'].append({
                    'name': test_case['name'],
                    'type': test_case['type'],
                    'passed': False,
                    'errors': [f"Test execution error: {str(e)}"],
                    'output': None
                })
        
        return results
    
    def generate_contract_compliance_report(self, tool_id: str, tool_instance: Any) -> Dict[str, Any]:
        """
        Generate comprehensive contract compliance report
        
        Args:
            tool_id: Tool identifier
            tool_instance: Tool instance to test
            
        Returns:
            Compliance report
        """
        # Create and run test suite
        test_suite = self.create_test_suite(tool_id)
        test_results = self.run_test_suite(test_suite, tool_instance)
        
        # Calculate compliance metrics
        total_tests = test_results['total_tests']
        passed_tests = test_results['passed']
        compliance_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        return {
            'tool_id': tool_id,
            'compliance_rate': compliance_rate,
            'test_summary': {
                'total': total_tests,
                'passed': passed_tests,
                'failed': test_results['failed'],
                'errors': test_results['errors']
            },
            'test_results': test_results['test_results'],
            'recommendations': self._generate_recommendations(test_results)
        }
    
    def _generate_recommendations(self, test_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        if test_results['failed'] > 0:
            recommendations.append("Review failed test cases and fix contract violations")
        
        if test_results['errors'] > 0:
            recommendations.append("Fix execution errors in tool implementation")
        
        # Analyze specific failure patterns
        failed_tests = [test for test in test_results['test_results'] if not test['passed']]
        
        negative_test_failures = [test for test in failed_tests if test['type'] == 'negative']
        if negative_test_failures:
            recommendations.append("Improve input validation to properly reject invalid inputs")
        
        positive_test_failures = [test for test in failed_tests if test['type'] == 'positive']
        if positive_test_failures:
            recommendations.append("Fix core functionality to handle valid inputs correctly")
        
        return recommendations
