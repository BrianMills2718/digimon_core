# TDD Templates for KGAS Development

## Overview

This document provides ready-to-use TDD templates for common KGAS development patterns. Copy and adapt these templates when starting new development work.

## Tool Development Template

### Basic Tool Test Template

```python
# tests/unit/test_t{number}_{tool_name}.py
"""
TDD tests for T{Number} - {Tool Name}

Write these tests FIRST before implementing the tool.
"""

import pytest
from unittest.mock import Mock, patch
from typing import Dict, Any

from src.tools.t{number}_{tool_name} import T{Number}{ToolName}
from src.core.service_manager import ServiceManager


class TestT{Number}{ToolName}:
    """Test-driven development for T{Number} - {Tool Name}"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_services = Mock(spec=ServiceManager)
        self.tool = T{Number}{ToolName}(self.mock_services)
    
    # ===== CONTRACT TESTS (MANDATORY) =====
    
    def test_tool_initialization(self):
        """Tool initializes with required services"""
        assert self.tool is not None
        assert self.tool.tool_id == "T{number}"
        assert self.tool.services == self.mock_services
    
    def test_input_contract_validation(self):
        """Tool validates inputs according to contract"""
        # Invalid input should be rejected
        invalid_inputs = [
            {},  # Empty input
            {"wrong_field": "value"},  # Wrong fields
            None,  # Null input
        ]
        
        for invalid_input in invalid_inputs:
            result = self.tool.execute(invalid_input)
            assert result["status"] == "error"
            assert "validation" in result["error"].lower()
    
    def test_output_contract_compliance(self):
        """Tool output matches contract specification"""
        valid_input = {
            # Define valid input based on contract
            "required_field": "value",
            "optional_field": 123
        }
        
        result = self.tool.execute(valid_input)
        
        # Verify output structure
        assert "status" in result
        assert result["status"] in ["success", "error"]
        
        if result["status"] == "success":
            assert "data" in result
            assert "tool_id" in result
            assert result["tool_id"] == "T{number}"
            assert "confidence" in result
            assert 0.0 <= result["confidence"] <= 1.0
        else:
            assert "error" in result
            assert "recovery" in result
    
    # ===== FUNCTIONALITY TESTS (MANDATORY) =====
    
    def test_core_functionality(self):
        """Tool performs its primary function correctly"""
        # This test defines the expected behavior
        input_data = {
            # Specific test input
        }
        
        result = self.tool.execute(input_data)
        
        assert result["status"] == "success"
        # Add specific assertions for tool's main purpose
        # These assertions define what the tool should do
    
    def test_edge_case_empty_data(self):
        """Tool handles empty data gracefully"""
        input_data = {
            "entities": [],  # Empty list
            "threshold": 0.5
        }
        
        result = self.tool.execute(input_data)
        
        assert result["status"] == "success"
        assert result["data"] == {"processed": 0, "results": []}
    
    def test_edge_case_large_data(self):
        """Tool handles large datasets efficiently"""
        # Create large test dataset
        large_input = {
            "entities": [{"id": f"e{i}", "name": f"Entity {i}"} 
                        for i in range(10000)]
        }
        
        import time
        start_time = time.time()
        result = self.tool.execute(large_input)
        execution_time = time.time() - start_time
        
        assert result["status"] == "success"
        assert execution_time < 5.0  # Performance requirement
    
    # ===== INTEGRATION TESTS (MANDATORY) =====
    
    def test_identity_service_integration(self):
        """Tool integrates with IdentityService correctly"""
        # Mock the identity service behavior
        mock_identity = Mock()
        mock_identity.resolve_entity.return_value = {
            "entity_id": "e123",
            "canonical_name": "Test Entity",
            "confidence": 0.95
        }
        self.mock_services.identity_service = mock_identity
        
        input_data = {
            "entity_name": "Test",
            "context": "testing"
        }
        
        result = self.tool.execute(input_data)
        
        # Verify service was called correctly
        mock_identity.resolve_entity.assert_called_once()
        assert result["status"] == "success"
    
    def test_provenance_tracking(self):
        """Tool tracks provenance correctly"""
        mock_provenance = Mock()
        self.mock_services.provenance_service = mock_provenance
        
        input_data = {"test": "data"}
        result = self.tool.execute(input_data)
        
        # Verify provenance was logged
        mock_provenance.log_execution.assert_called_once()
        call_args = mock_provenance.log_execution.call_args[1]
        assert call_args["tool_id"] == "T{number}"
        assert call_args["inputs"] == input_data
        assert "outputs" in call_args
    
    # ===== PERFORMANCE TESTS (MANDATORY) =====
    
    @pytest.mark.performance
    def test_performance_requirements(self, benchmark):
        """Tool meets performance benchmarks"""
        input_data = {
            # Standard test input
        }
        
        # Benchmark the execution
        result = benchmark.pedantic(
            self.tool.execute,
            args=[input_data],
            iterations=100,
            rounds=5
        )
        
        # Performance assertions
        stats = benchmark.stats
        assert stats["mean"] < 0.1  # 100ms average
        assert stats["max"] < 0.5   # 500ms worst case
        assert stats["stddev"] < 0.05  # Consistent performance
    
    # ===== ERROR HANDLING TESTS =====
    
    def test_handles_service_failure(self):
        """Tool handles service failures gracefully"""
        # Mock service failure
        self.mock_services.identity_service.resolve_entity.side_effect = \
            RuntimeError("Service unavailable")
        
        input_data = {"entity_name": "Test"}
        result = self.tool.execute(input_data)
        
        assert result["status"] == "error"
        assert "Service unavailable" in result["error"]
        assert result["recovery"] == "Check service health and retry"
    
    def test_handles_invalid_data_types(self):
        """Tool handles invalid data types appropriately"""
        invalid_inputs = [
            {"number_field": "not_a_number"},  # Wrong type
            {"text_field": 12345},  # Wrong type
            {"list_field": "not_a_list"},  # Wrong type
        ]
        
        for invalid_input in invalid_inputs:
            result = self.tool.execute(invalid_input)
            assert result["status"] == "error"
            assert "type" in result["error"].lower()
```

## Service Development Template

```python
# tests/unit/test_{service_name}_service.py
"""
TDD tests for {ServiceName}Service

Write these tests FIRST before implementing the service.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any

from src.core.services.{service_name}_service import {ServiceName}Service


class Test{ServiceName}Service:
    """Test-driven development for {ServiceName}Service"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_db = Mock()
        self.service = {ServiceName}Service(db_manager=self.mock_db)
    
    # ===== INITIALIZATION TESTS =====
    
    def test_service_initialization(self):
        """Service initializes with required dependencies"""
        assert self.service is not None
        assert self.service.db_manager == self.mock_db
        assert self.service.is_initialized
    
    def test_health_check(self):
        """Service health check works correctly"""
        health = self.service.health_check()
        
        assert health["status"] in ["healthy", "degraded", "unhealthy"]
        assert "checks" in health
        assert "database" in health["checks"]
        assert "memory" in health["checks"]
        assert "latency" in health
    
    # ===== API CONTRACT TESTS =====
    
    def test_primary_operation_contract(self):
        """Define primary service operation contract"""
        # This test defines what the service should do
        input_data = {
            "operation": "primary",
            "parameters": {"key": "value"}
        }
        
        result = self.service.process(input_data)
        
        # Define expected behavior
        assert result["status"] == "success"
        assert "result" in result
        assert result["operation_id"] is not None
        assert result["duration_ms"] < 100
    
    # ===== CONCURRENCY TESTS =====
    
    @pytest.mark.asyncio
    async def test_concurrent_operations(self):
        """Service handles concurrent operations safely"""
        # Create multiple concurrent operations
        operations = []
        for i in range(10):
            op = self.service.async_process({"id": i})
            operations.append(op)
        
        # Execute concurrently
        results = await asyncio.gather(*operations)
        
        # Verify all succeeded and have unique IDs
        assert len(results) == 10
        assert all(r["status"] == "success" for r in results)
        
        # Check for race conditions
        ids = [r["operation_id"] for r in results]
        assert len(set(ids)) == 10  # All unique
    
    def test_thread_safety(self):
        """Service is thread-safe"""
        import threading
        import queue
        
        results = queue.Queue()
        errors = queue.Queue()
        
        def worker(service, worker_id):
            try:
                for i in range(100):
                    result = service.process({"worker": worker_id, "op": i})
                    results.put(result)
            except Exception as e:
                errors.put(e)
        
        # Start multiple threads
        threads = []
        for i in range(5):
            t = threading.Thread(target=worker, args=(self.service, i))
            threads.append(t)
            t.start()
        
        # Wait for completion
        for t in threads:
            t.join()
        
        # Verify no errors and correct number of results
        assert errors.empty()
        assert results.qsize() == 500
    
    # ===== RESOURCE MANAGEMENT TESTS =====
    
    def test_resource_cleanup(self):
        """Service cleans up resources properly"""
        # Track resource allocation
        initial_connections = self.mock_db.active_connections()
        
        # Perform operations
        for _ in range(10):
            self.service.process({"test": "data"})
        
        # Cleanup
        self.service.cleanup()
        
        # Verify resources released
        final_connections = self.mock_db.active_connections()
        assert final_connections == initial_connections
        assert self.service.is_cleaned_up
    
    def test_connection_pooling(self):
        """Service uses connection pooling efficiently"""
        # Monitor connection usage
        connections_used = []
        
        def track_connection(*args, **kwargs):
            connections_used.append(1)
            return Mock()
        
        self.mock_db.get_connection = Mock(side_effect=track_connection)
        
        # Perform many operations
        for _ in range(100):
            self.service.process({"test": "data"})
        
        # Should reuse connections, not create 100
        assert len(connections_used) < 20
```

## Cross-Modal Analysis Template

```python
# tests/unit/test_cross_modal_{transform}.py
"""
TDD tests for Cross-Modal {Transform} transformation

Write these tests FIRST before implementing the transformation.
"""

import pytest
import numpy as np
from typing import Dict, Any, List

from src.cross_modal.{transform} import {Transform}Transformer


class TestCrossModal{Transform}:
    """Test-driven development for cross-modal transformation"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.transformer = {Transform}Transformer()
        
        # Create test data in source format
        self.test_data = self._create_test_data()
    
    def _create_test_data(self):
        """Create representative test data"""
        # Define test data structure
        return {
            "source_format": "graph",
            "data": {
                "nodes": [
                    {"id": "n1", "label": "Node 1", "properties": {}},
                    {"id": "n2", "label": "Node 2", "properties": {}}
                ],
                "edges": [
                    {"source": "n1", "target": "n2", "label": "connects"}
                ]
            }
        }
    
    # ===== SEMANTIC PRESERVATION TESTS =====
    
    def test_semantic_preservation(self):
        """Transformation preserves semantic meaning"""
        # Transform data
        result = self.transformer.transform(self.test_data)
        
        # Verify semantic equivalence
        assert result["status"] == "success"
        transformed = result["data"]
        
        # Specific semantic checks based on transformation
        # These define what "semantic preservation" means
        assert self._verify_semantic_equivalence(
            self.test_data["data"], 
            transformed
        )
    
    def _verify_semantic_equivalence(self, source, target):
        """Helper to verify semantic equivalence"""
        # Implementation depends on specific transformation
        # Example checks:
        # - Same number of entities
        # - Same relationships preserved
        # - Same properties maintained
        return True
    
    def test_reversibility(self):
        """Transformation can be reversed when applicable"""
        # Forward transformation
        forward_result = self.transformer.transform(self.test_data)
        assert forward_result["status"] == "success"
        
        # Reverse transformation
        reverse_input = {
            "source_format": "table",  # Now the target format
            "data": forward_result["data"]
        }
        reverse_result = self.transformer.reverse_transform(reverse_input)
        
        # Should get back original (with acceptable loss)
        assert reverse_result["status"] == "success"
        assert self._compare_with_tolerance(
            self.test_data["data"],
            reverse_result["data"],
            tolerance=0.01  # 1% acceptable loss
        )
    
    # ===== INFORMATION TRACKING TESTS =====
    
    def test_information_loss_tracking(self):
        """Any information loss is tracked and reported"""
        # Use data that will have information loss
        lossy_data = {
            "source_format": "graph",
            "data": {
                "nodes": [{"id": "n1", "metadata": {"complex": "data"}}],
                "edges": []
            }
        }
        
        result = self.transformer.transform(lossy_data)
        
        assert result["status"] == "success"
        assert "information_loss" in result
        assert result["information_loss"]["has_loss"] == True
        assert "lost_fields" in result["information_loss"]
        assert "loss_percentage" in result["information_loss"]
    
    def test_provenance_preservation(self):
        """Source provenance is maintained through transformation"""
        # Add provenance to test data
        self.test_data["provenance"] = {
            "source_file": "test.pdf",
            "extraction_time": "2024-01-01T00:00:00Z",
            "tool_chain": ["T01", "T23", "T31"]
        }
        
        result = self.transformer.transform(self.test_data)
        
        assert result["status"] == "success"
        assert "provenance" in result["data"]
        assert result["data"]["provenance"]["source_file"] == "test.pdf"
        assert "transformation_added" in result["data"]["provenance"]
    
    # ===== PERFORMANCE TESTS =====
    
    @pytest.mark.performance
    def test_transformation_performance(self, benchmark):
        """Transformation meets performance requirements"""
        # Create larger dataset
        large_data = self._create_large_test_data(nodes=1000, edges=5000)
        
        # Benchmark transformation
        result = benchmark.pedantic(
            self.transformer.transform,
            args=[large_data],
            iterations=10,
            rounds=3
        )
        
        # Performance requirements
        stats = benchmark.stats
        assert stats["mean"] < 1.0  # Less than 1 second average
        assert stats["max"] < 2.0   # Less than 2 seconds worst case
    
    def test_memory_efficiency(self):
        """Transformation is memory efficient"""
        import tracemalloc
        
        # Start memory tracking
        tracemalloc.start()
        
        # Create and transform large dataset
        large_data = self._create_large_test_data(nodes=10000, edges=50000)
        
        snapshot1 = tracemalloc.take_snapshot()
        result = self.transformer.transform(large_data)
        snapshot2 = tracemalloc.take_snapshot()
        
        # Calculate memory usage
        top_stats = snapshot2.compare_to(snapshot1, 'lineno')
        total_memory = sum(stat.size for stat in top_stats)
        
        # Memory should be proportional to data size
        data_size = len(str(large_data))
        memory_ratio = total_memory / data_size
        
        assert memory_ratio < 10  # Less than 10x data size
        tracemalloc.stop()
```

## Theory Validation Template

```python
# tests/unit/test_theory_{theory_name}.py
"""
TDD tests for {TheoryName} theory implementation

Write these tests FIRST to validate theoretical correctness.
"""

import pytest
import numpy as np
from typing import Dict, Any, List

from src.theory.{theory_name} import {TheoryName}Implementation


class TestTheory{TheoryName}:
    """Test-driven development for theory implementation"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.theory = {TheoryName}Implementation()
        
        # Load known theoretical examples
        self.known_examples = self._load_theoretical_examples()
    
    def _load_theoretical_examples(self):
        """Load examples with known theoretical results"""
        return [
            {
                "input": {...},  # Input data
                "expected": {...},  # Expected result from theory
                "source": "Author et al. (2023), Table 2",  # Citation
                "tolerance": 0.001  # Acceptable numerical tolerance
            }
        ]
    
    # ===== THEORETICAL CORRECTNESS TESTS =====
    
    def test_known_theoretical_examples(self):
        """Implementation matches known theoretical results"""
        for example in self.known_examples:
            result = self.theory.calculate(example["input"])
            
            # Verify against theoretical expectation
            assert self._compare_results(
                result,
                example["expected"],
                tolerance=example["tolerance"]
            ), f"Failed for example from {example['source']}"
    
    def test_theoretical_properties(self):
        """Implementation satisfies theoretical properties"""
        # Test specific properties the theory should satisfy
        # Example: commutativity, associativity, bounds, etc.
        
        # Property 1: Bounded output
        test_inputs = self._generate_test_inputs(100)
        for input_data in test_inputs:
            result = self.theory.calculate(input_data)
            assert 0.0 <= result["value"] <= 1.0, "Output not bounded"
        
        # Property 2: Monotonicity (if applicable)
        # Property 3: Symmetry (if applicable)
        # Add properties specific to your theory
    
    def test_edge_cases_from_theory(self):
        """Handle theoretical edge cases correctly"""
        edge_cases = [
            {
                "name": "empty_input",
                "input": {"data": []},
                "expected": {"value": 0.0}  # Or as defined by theory
            },
            {
                "name": "single_element",
                "input": {"data": [1]},
                "expected": {"value": 1.0}  # Or as defined by theory
            },
            # Add edge cases specific to your theory
        ]
        
        for case in edge_cases:
            result = self.theory.calculate(case["input"])
            assert result == case["expected"], \
                f"Failed edge case: {case['name']}"
    
    # ===== NUMERICAL STABILITY TESTS =====
    
    def test_numerical_stability(self):
        """Implementation is numerically stable"""
        # Test with values that might cause numerical issues
        problematic_inputs = [
            {"data": [1e-10, 1e-10, 1e-10]},  # Very small
            {"data": [1e10, 1e10, 1e10]},     # Very large
            {"data": [1e-10, 1e10]},          # Mixed scales
        ]
        
        for input_data in problematic_inputs:
            result = self.theory.calculate(input_data)
            
            # Should not produce NaN or Inf
            assert not np.isnan(result["value"])
            assert not np.isinf(result["value"])
            
            # Should be within theoretical bounds
            assert self._within_theoretical_bounds(result)
    
    # ===== PERFORMANCE FOR RESEARCH SCALE =====
    
    @pytest.mark.performance
    def test_research_scale_performance(self, benchmark):
        """Performance adequate for research-scale data"""
        # Create research-scale dataset
        research_data = self._create_research_dataset(
            entities=10000,
            relationships=50000
        )
        
        # Benchmark calculation
        result = benchmark.pedantic(
            self.theory.calculate,
            args=[research_data],
            iterations=5,
            rounds=3
        )
        
        # Should complete in reasonable time for research
        stats = benchmark.stats
        assert stats["mean"] < 60.0  # Less than 1 minute average
```

## Usage Guidelines

### When to Use Each Template

1. **Tool Development Template**: For any new T-numbered tool
2. **Service Development Template**: For core services (Identity, Provenance, etc.)
3. **Cross-Modal Template**: For transformations between data formats
4. **Theory Template**: For academic theory implementations

### Customization Steps

1. Replace placeholders ({...}) with actual values
2. Add domain-specific test cases
3. Define specific performance requirements
4. Add integration tests for actual services
5. Include theory-specific validation

### TDD Workflow

1. **Copy appropriate template**
2. **Customize for your component**
3. **Run tests - they should FAIL** (Red)
4. **Implement minimal code to pass** (Green)
5. **Refactor and improve** (Refactor)
6. **Add more tests and repeat**

### Best Practices

- Write the simplest test that could possibly fail
- One assertion per test method when possible
- Use descriptive test names that explain the behavior
- Test behavior, not implementation
- Keep tests independent and isolated
- Use mocks for external dependencies
- Run tests frequently during development

These templates ensure consistent, high-quality TDD across the KGAS project.