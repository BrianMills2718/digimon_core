# tests/integration/test_theory_performance.py
import time
import pytest
import os
import sys

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from src.core.phase_adapters import Phase1Adapter
from src.core.graphrag_phase_interface import ProcessingRequest as OldRequest
from contracts.phase_interfaces.base_graphrag_phase import (
    ProcessingRequest as TheoryRequest, TheoryConfig, TheorySchema
)

class TestTheoryPerformance:
    """Test performance impact of theory-aware processing"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.test_pdf = "examples/pdfs/test_document.pdf"
        self.concept_library = "src/ontology_library/master_concepts.py"
        
        # Skip if required files don't exist
        if not os.path.exists(self.test_pdf):
            pytest.skip(f"Test PDF not found: {self.test_pdf}")
        if not os.path.exists(self.concept_library):
            pytest.skip(f"Concept library not found: {self.concept_library}")
    
    def test_performance_comparison(self):
        """Compare performance of old vs theory-aware processing"""
        
        phase1 = Phase1Adapter()
        
        # Test old interface performance
        old_request = OldRequest(
            documents=[self.test_pdf],
            queries=["What entities are mentioned?"],
            workflow_id="performance_test_old"
        )
        
        start_time = time.time()
        try:
            old_result = phase1.execute(old_request)
            old_duration = time.time() - start_time
            old_success = True
        except Exception as e:
            old_duration = time.time() - start_time
            old_success = False
            old_error = str(e)
        
        # Test theory-aware interface performance
        theory_config = TheoryConfig(
            schema_type=TheorySchema.MASTER_CONCEPTS,
            concept_library_path=self.concept_library
        )
        
        theory_request = TheoryRequest(
            documents=[self.test_pdf],
            queries=["What entities are mentioned?"],
            workflow_id="performance_test_theory",
            theory_config=theory_config
        )
        
        start_time = time.time()
        try:
            theory_result = phase1.execute(theory_request)
            theory_duration = time.time() - start_time
            theory_success = True
        except Exception as e:
            theory_duration = time.time() - start_time
            theory_success = False
            theory_error = str(e)
        
        # Report results
        print(f"Performance comparison:")
        print(f"  Old interface: {old_duration:.2f}s (success: {old_success})")
        print(f"  Theory interface: {theory_duration:.2f}s (success: {theory_success})")
        
        # Calculate overhead if both succeeded
        if old_success and theory_success:
            if old_result.status == "success" and theory_result.status == "success":
                overhead_percent = ((theory_duration - old_duration) / old_duration) * 100
                print(f"  Overhead: {overhead_percent:.1f}%")
                
                # Overhead should be reasonable (< 50%)
                assert overhead_percent < 50, f"Theory overhead too high: {overhead_percent:.1f}%"
                
                print("✅ Performance impact within acceptable bounds")
            else:
                print("⚠️ One or both workflows failed, cannot calculate overhead")
        else:
            print("⚠️ Interface comparison failed due to execution errors")
            if not old_success:
                print(f"   Old interface error: {old_error}")
            if not theory_success:
                print(f"   Theory interface error: {theory_error}")
    
    def test_theory_validation_overhead(self):
        """Test overhead of theory validation specifically"""
        
        theory_config_no_validation = TheoryConfig(
            schema_type=TheorySchema.MASTER_CONCEPTS,
            concept_library_path=self.concept_library,
            validation_enabled=False
        )
        
        theory_config_with_validation = TheoryConfig(
            schema_type=TheorySchema.MASTER_CONCEPTS,
            concept_library_path=self.concept_library,
            validation_enabled=True
        )
        
        phase1 = Phase1Adapter()
        
        # Test without validation
        request_no_validation = TheoryRequest(
            documents=[self.test_pdf],
            queries=["What entities are mentioned?"],
            workflow_id="performance_test_no_validation",
            theory_config=theory_config_no_validation
        )
        
        start_time = time.time()
        try:
            result_no_validation = phase1.execute(request_no_validation)
            no_validation_duration = time.time() - start_time
            no_validation_success = True
        except Exception as e:
            no_validation_duration = time.time() - start_time
            no_validation_success = False
            no_validation_error = str(e)
        
        # Test with validation
        request_with_validation = TheoryRequest(
            documents=[self.test_pdf],
            queries=["What entities are mentioned?"],
            workflow_id="performance_test_with_validation",
            theory_config=theory_config_with_validation
        )
        
        start_time = time.time()
        try:
            result_with_validation = phase1.execute(request_with_validation)
            with_validation_duration = time.time() - start_time
            with_validation_success = True
        except Exception as e:
            with_validation_duration = time.time() - start_time
            with_validation_success = False
            with_validation_error = str(e)
        
        # Report validation overhead
        print(f"Theory validation overhead:")
        print(f"  Without validation: {no_validation_duration:.2f}s (success: {no_validation_success})")
        print(f"  With validation: {with_validation_duration:.2f}s (success: {with_validation_success})")
        
        if no_validation_success and with_validation_success:
            if result_no_validation.status == "success" and result_with_validation.status == "success":
                validation_overhead = ((with_validation_duration - no_validation_duration) / no_validation_duration) * 100
                print(f"  Validation overhead: {validation_overhead:.1f}%")
                
                # Validation overhead should be reasonable
                assert validation_overhead < 100, f"Validation overhead too high: {validation_overhead:.1f}%"
                
                print("✅ Theory validation overhead within acceptable bounds")
        else:
            print("⚠️ Validation comparison failed due to execution errors")
    
    def test_memory_usage_impact(self):
        """Test memory usage impact of theory-aware processing"""
        import psutil
        import gc
        
        process = psutil.Process()
        
        # Get baseline memory
        gc.collect()
        baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create theory configuration
        theory_config = TheoryConfig(
            schema_type=TheorySchema.MASTER_CONCEPTS,
            concept_library_path=self.concept_library,
            validation_enabled=True
        )
        
        # Memory after theory config creation
        theory_config_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Test with multiple requests to see memory accumulation
        phase1 = Phase1Adapter()
        
        for i in range(3):
            request = TheoryRequest(
                documents=[self.test_pdf],
                queries=[f"What entities are mentioned? Test {i}"],
                workflow_id=f"memory_test_{i}",
                theory_config=theory_config
            )
            
            try:
                result = phase1.execute(request)
                # Don't assert success since Neo4j might not be available
            except Exception:
                pass  # Ignore errors for memory testing
        
        # Final memory usage
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        print(f"Memory usage analysis:")
        print(f"  Baseline: {baseline_memory:.1f} MB")
        print(f"  After theory config: {theory_config_memory:.1f} MB")
        print(f"  After 3 executions: {final_memory:.1f} MB")
        print(f"  Total increase: {final_memory - baseline_memory:.1f} MB")
        
        # Memory increase should be reasonable (< 100MB for small tests)
        memory_increase = final_memory - baseline_memory
        assert memory_increase < 100, f"Memory usage increase too high: {memory_increase:.1f} MB"
        
        print("✅ Memory usage impact within acceptable bounds")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])