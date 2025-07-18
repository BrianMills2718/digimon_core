"""Test contract validation integration with main pipeline"""

import unittest
from src.core.pipeline_orchestrator import PipelineOrchestrator
from src.core.tool_factory import create_unified_workflow_config
from src.core.tool_factory import Phase, OptimizationLevel

class TestValidationIntegration(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment"""
        config = create_unified_workflow_config(
            phase=Phase.PHASE1,
            optimization_level=OptimizationLevel.STANDARD
        )
        self.orchestrator = PipelineOrchestrator(config)
    
    def test_contract_validation_enabled(self):
        """Test that contract validation is properly enabled"""
        self.assertTrue(hasattr(self.orchestrator, 'contract_validator'))
        self.assertTrue(self.orchestrator.validation_enabled)
    
    def test_pdf_processing_with_validation(self):
        """Test PDF processing with validation enabled"""
        result = self.orchestrator.execute(
            document_paths=["examples/sample_data/sample_document.txt"],
            queries=["What entities are mentioned?"]
        )
        
        # Should complete successfully with validation
        self.assertEqual(result['execution_metadata']['status'], 'success')
        self.assertIn('final_result', result)

if __name__ == '__main__':
    unittest.main()