"""
Mock-free unit tests for T09 YAML Loader Unified

Tests the unified YAML loader tool with real YAML processing using PyYAML.
No mocking is used - all functionality is tested with real data and real processing.
"""

import pytest
import tempfile
import yaml
from pathlib import Path
import os

from src.tools.phase1.t09_yaml_loader_unified import T09YAMLLoaderUnified
from src.core.service_manager import ServiceManager
from src.tools.base_tool import ToolRequest


class TestT09YAMLLoaderUnifiedMockFree:
    def setup_method(self):
        """Set up test fixtures with real ServiceManager - NO mocks"""
        # Real ServiceManager - NO mocking
        self.service_manager = ServiceManager()
        self.tool = T09YAMLLoaderUnified(service_manager=self.service_manager)
        
        # Create real test YAML files
        self.test_files = self._create_real_test_yaml_files()
    
    def teardown_method(self):
        """Clean up real test files"""
        for file_path in self.test_files.values():
            try:
                if os.path.exists(file_path):
                    os.unlink(file_path)
            except:
                pass
    
    def _create_real_test_yaml_files(self) -> dict:
        """Create real YAML test files for testing"""
        test_files = {}
        
        # Simple YAML configuration
        simple_yaml = '''
name: Test Application
version: "1.0.0"
description: A simple test application configuration
author:
  name: Test Author
  email: test@example.com
settings:
  debug: true
  port: 8080
  database:
    host: localhost
    port: 5432
    name: testdb
features:
  - authentication
  - logging
  - monitoring
'''
        
        simple_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        simple_file.write(simple_yaml)
        simple_file.close()
        test_files['simple'] = simple_file.name
        
        # Complex YAML with advanced structures
        complex_yaml = '''
%YAML 1.1
---
application:
  name: "Complex Application"
  version: "2.1.3"
  metadata:
    created: 2024-01-01
    updated: 2024-01-15
    tags: [production, stable, featured]
    
environments:
  development:
    database:
      host: dev.db.example.com
      port: 5432
      credentials: &db_creds
        username: dev_user
        password: dev_pass
    services:
      api:
        url: https://dev-api.example.com
        timeout: 30
        retries: 3
      cache:
        type: redis
        host: dev-redis.example.com
        port: 6379
        
  production:
    database:
      host: prod.db.example.com
      port: 5432
      credentials: *db_creds
    services:
      api:
        url: https://api.example.com
        timeout: 10
        retries: 5
      cache:
        type: redis
        host: redis.example.com
        port: 6379
        cluster: true
        
deployment:
  strategy: rolling
  replicas: 3
  resources:
    requests:
      cpu: "500m"
      memory: "1Gi"
    limits:
      cpu: "1000m"
      memory: "2Gi"
  health_checks:
    liveness:
      path: /health
      interval: 30s
    readiness:
      path: /ready
      interval: 10s

monitoring:
  metrics:
    - name: requests_total
      type: counter
      labels: [method, status]
    - name: request_duration
      type: histogram
      buckets: [0.1, 0.5, 1.0, 2.0, 5.0]
  alerts:
    - name: high_error_rate
      condition: rate(errors_total[5m]) > 0.1
      severity: warning
    - name: service_down
      condition: up == 0
      severity: critical
'''
        
        complex_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        complex_file.write(complex_yaml)
        complex_file.close()
        test_files['complex'] = complex_file.name
        
        # Multi-document YAML
        multi_doc_yaml = '''---
document: 1
title: First Document
content:
  type: configuration
  data:
    key1: value1
    key2: value2
---
document: 2
title: Second Document
content:
  type: data
  items:
    - name: item1
      value: 100
    - name: item2
      value: 200
---
document: 3
title: Third Document
content:
  type: metadata
  info:
    created: 2024-01-01
    author: Test User
    version: 1.0
'''
        
        multi_doc_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False)
        multi_doc_file.write(multi_doc_yaml)
        multi_doc_file.close()
        test_files['multi_doc'] = multi_doc_file.name
        
        # List-based YAML
        list_yaml = '''
- name: Task 1
  description: First task to complete
  priority: high
  assigned_to: user1
  due_date: 2024-02-01
  
- name: Task 2
  description: Second task to complete
  priority: medium
  assigned_to: user2
  due_date: 2024-02-15
  
- name: Task 3
  description: Third task to complete
  priority: low
  assigned_to: user1
  due_date: 2024-03-01
'''
        
        list_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        list_file.write(list_yaml)
        list_file.close()
        test_files['list'] = list_file.name
        
        # Malformed YAML for error testing
        malformed_yaml = '''
name: Test Application
version: "1.0.0"
settings:
  debug: true
  port: 8080
  database:
    host: localhost
    port: 5432
    # Missing closing quote and colon
    name: "testdb
  features:
    - authentication
    logging
'''
        
        malformed_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        malformed_file.write(malformed_yaml)
        malformed_file.close()
        test_files['malformed'] = malformed_file.name
        
        return test_files
    
    def test_tool_contract_real(self):
        """Test tool contract with REAL contract validation"""
        contract = self.tool.get_contract()
        
        # Verify contract structure
        assert contract.tool_id == "T09"
        assert contract.name == "YAML Document Loader"
        assert contract.category == "document_processing"
        assert "file_path" in contract.input_schema["required"]
        assert "document" in contract.output_schema["required"]
        assert len(contract.dependencies) > 0
        
        # Verify performance requirements
        assert "max_execution_time" in contract.performance_requirements
        assert "max_memory_mb" in contract.performance_requirements
        assert "min_confidence" in contract.performance_requirements
        
        # Verify error conditions
        assert "YAML_PARSE_ERROR" in contract.error_conditions
        assert "FILE_NOT_FOUND" in contract.error_conditions
    
    def test_simple_yaml_loading_real(self):
        """Test loading simple YAML with REAL processing"""
        request = ToolRequest(
            tool_id="T09",
            operation="load_yaml",
            input_data={
                "file_path": self.test_files['simple'],
                "workflow_id": "test_workflow_simple"
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        # Verify successful execution
        assert result.status == "success"
        assert result.tool_id == "T09"
        assert result.execution_time > 0
        
        # Verify document data
        doc = result.data["document"]
        assert doc["document_id"] == "test_workflow_simple_" + Path(self.test_files['simple']).stem
        assert doc["file_name"] == Path(self.test_files['simple']).name
        assert doc["key_count"] > 0
        assert doc["confidence"] > 0.5
        assert len(doc["text_content"]) > 0
        
        # Verify YAML structure
        yaml_structure = doc["yaml_structure"]
        assert isinstance(yaml_structure, dict)
        assert "name" in yaml_structure
        assert yaml_structure["name"] == "Test Application"
        assert "settings" in yaml_structure
        assert "features" in yaml_structure
        
        # Verify specific content
        assert "Test Application" in doc["text_content"]
        assert "8080" in doc["text_content"]
    
    def test_complex_yaml_with_references_real(self):
        """Test loading complex YAML with anchors and references with REAL processing"""
        request = ToolRequest(
            tool_id="T09",
            operation="load_yaml",
            input_data={
                "file_path": self.test_files['complex'],
                "workflow_id": "test_workflow_complex"
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        # Verify successful execution
        assert result.status == "success"
        
        # Verify document data
        doc = result.data["document"]
        assert doc["key_count"] > 20  # Complex structure
        assert doc["depth"] > 3      # Deep nesting
        assert doc["confidence"] > 0.5
        
        # Verify YAML structure with references
        yaml_structure = doc["yaml_structure"]
        assert "application" in yaml_structure
        assert "environments" in yaml_structure
        
        # Verify anchor/reference resolution
        dev_creds = yaml_structure["environments"]["development"]["database"]["credentials"]
        prod_creds = yaml_structure["environments"]["production"]["database"]["credentials"]
        assert dev_creds == prod_creds  # Should be same due to YAML reference
        assert "dev_user" in str(dev_creds)
    
    def test_multi_document_yaml_real(self):
        """Test multi-document YAML parsing with REAL processing"""
        request = ToolRequest(
            tool_id="T09",
            operation="load_yaml",
            input_data={
                "file_path": self.test_files['multi_doc'],
                "workflow_id": "test_workflow_multi",
                "parse_options": {
                    "multi_document": True
                }
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        # Verify successful execution
        assert result.status == "success"
        
        # Verify multi-document structure
        doc = result.data["document"]
        assert doc["document_count"] == 3  # Three documents
        
        yaml_structure = doc["yaml_structure"]
        assert isinstance(yaml_structure, list)
        assert len(yaml_structure) == 3
        
        # Verify each document
        assert yaml_structure[0]["document"] == 1
        assert yaml_structure[1]["document"] == 2
        assert yaml_structure[2]["document"] == 3
        
        # Verify content from all documents is in text
        assert "First Document" in doc["text_content"]
        assert "Second Document" in doc["text_content"]
        assert "Third Document" in doc["text_content"]
    
    def test_list_yaml_structure_real(self):
        """Test YAML with list structure with REAL processing"""
        request = ToolRequest(
            tool_id="T09",
            operation="load_yaml",
            input_data={
                "file_path": self.test_files['list'],
                "workflow_id": "test_workflow_list"
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        # Verify successful execution
        assert result.status == "success"
        
        # Verify list structure
        doc = result.data["document"]
        yaml_structure = doc["yaml_structure"]
        assert isinstance(yaml_structure, list)
        assert len(yaml_structure) == 3
        
        # Verify each task
        for i, task in enumerate(yaml_structure):
            assert "name" in task
            assert "description" in task
            assert "priority" in task
            assert task["name"] == f"Task {i + 1}"
        
        # Verify text content
        assert "Task 1" in doc["text_content"]
        assert "high" in doc["text_content"]
        assert "user1" in doc["text_content"]
    
    def test_parse_options_functionality_real(self):
        """Test different parse options with REAL processing"""
        # Test with safe_load disabled (if content allows)
        request_unsafe = ToolRequest(
            tool_id="T09",
            operation="load_yaml",
            input_data={
                "file_path": self.test_files['simple'],
                "parse_options": {
                    "safe_load": False
                }
            },
            parameters={}
        )
        
        result_unsafe = self.tool.execute(request_unsafe)
        assert result_unsafe.status == "success"
        
        # Test with single document mode for multi-doc file
        # This should fail because multi-doc YAML can't be loaded as single document
        request_single = ToolRequest(
            tool_id="T09",
            operation="load_yaml",
            input_data={
                "file_path": self.test_files['multi_doc'],
                "parse_options": {
                    "multi_document": False
                }
            },
            parameters={}
        )
        
        result_single = self.tool.execute(request_single)
        # This should fail because multi-document YAML cannot be parsed as single document
        assert result_single.status == "error"
        assert result_single.error_code == "YAML_SYNTAX_ERROR"
    
    def test_error_handling_malformed_yaml_real(self):
        """Test error handling with REAL malformed YAML"""
        request = ToolRequest(
            tool_id="T09",
            operation="load_yaml",
            input_data={
                "file_path": self.test_files['malformed']
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        # Verify error handling
        assert result.status == "error"
        assert result.error_code == "YAML_SYNTAX_ERROR"
        assert "YAML parse error" in result.error_message
    
    def test_file_not_found_error_real(self):
        """Test file not found error with REAL missing file"""
        request = ToolRequest(
            tool_id="T09",
            operation="load_yaml",
            input_data={
                "file_path": "/path/to/nonexistent/file.yaml"
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        # Verify error handling
        assert result.status == "error"
        assert result.error_code == "FILE_NOT_FOUND"
        assert "File not found" in result.error_message
    
    def test_invalid_file_type_error_real(self):
        """Test invalid file type error with REAL non-YAML file"""
        # Create a non-YAML file
        txt_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
        txt_file.write("This is not a YAML file")
        txt_file.close()
        
        try:
            request = ToolRequest(
                tool_id="T09",
                operation="load_yaml",
                input_data={
                    "file_path": txt_file.name
                },
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            # Verify error handling
            assert result.status == "error"
            assert result.error_code == "INVALID_FILE_TYPE"
            assert "Invalid file extension" in result.error_message
        finally:
            os.unlink(txt_file.name)
    
    def test_input_validation_real(self):
        """Test input validation with REAL validation logic"""
        # Test missing file_path
        result = self.tool.validate_input({})
        assert result == False
        
        result = self.tool.validate_input({"file_path": ""})
        assert result == False
        
        # Test valid input
        result = self.tool.validate_input({"file_path": "/some/path.yaml"})
        assert result == True
    
    def test_health_check_real(self):
        """Test health check with REAL service verification"""
        result = self.tool.health_check()
        
        # Verify health check structure
        assert isinstance(result.data, dict)
        assert "healthy" in result.data
        assert "yaml_available" in result.data
        assert "yaml_version" in result.data
        assert "services_healthy" in result.data
        assert "supported_formats" in result.data
        
        # Verify PyYAML is available
        assert result.data["yaml_available"] == True
        
        # Verify supported formats
        supported_formats = result.data["supported_formats"]
        assert ".yaml" in supported_formats
        assert ".yml" in supported_formats
        assert ".conf" in supported_formats
    
    def test_cleanup_functionality_real(self):
        """Test cleanup functionality with REAL resource management"""
        # Add some temp files to the tool
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.close()
        self.tool._temp_files.append(temp_file.name)
        
        # Verify cleanup works
        cleanup_result = self.tool.cleanup()
        assert cleanup_result == True
        assert len(self.tool._temp_files) == 0
        assert not os.path.exists(temp_file.name)
    
    def test_confidence_calculation_real(self):
        """Test confidence calculation with REAL YAML parsing metrics"""
        # Test with simple YAML
        request_simple = ToolRequest(
            tool_id="T09",
            operation="load_yaml",
            input_data={"file_path": self.test_files['simple']},
            parameters={}
        )
        
        result_simple = self.tool.execute(request_simple)
        confidence_simple = result_simple.data["document"]["confidence"]
        
        # Test with complex YAML
        request_complex = ToolRequest(
            tool_id="T09",
            operation="load_yaml",
            input_data={"file_path": self.test_files['complex']},
            parameters={}
        )
        
        result_complex = self.tool.execute(request_complex)
        confidence_complex = result_complex.data["document"]["confidence"]
        
        # Both should have reasonable confidence
        assert confidence_simple > 0.5
        assert confidence_complex > 0.5
        # Complex YAML might have slightly higher confidence due to more structure
        assert confidence_complex >= confidence_simple - 0.1
    
    def test_performance_metrics_real(self):
        """Test performance metrics with REAL execution measurement"""
        request = ToolRequest(
            tool_id="T09",
            operation="load_yaml",
            input_data={"file_path": self.test_files['complex']},
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        # Verify performance metrics are captured
        assert result.execution_time > 0
        assert result.memory_used >= 0
        
        # Verify reasonable execution time
        assert result.execution_time < 1.0
    
    def test_service_integration_real(self):
        """Test service integration with REAL services"""
        request = ToolRequest(
            tool_id="T09",
            operation="load_yaml",
            input_data={
                "file_path": self.test_files['simple'],
                "workflow_id": "test_service_integration"
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        # Verify service integration
        assert result.status == "success"
        assert "operation_id" in result.metadata
        
        # Verify provenance tracking
        operation_id = result.metadata["operation_id"]
        assert operation_id is not None
        
        # Verify quality assessment
        doc = result.data["document"]
        assert "quality_tier" in doc
        assert doc["confidence"] > 0
    
    def test_yaml_structure_depth_calculation_real(self):
        """Test YAML structure depth calculation with REAL parsing"""
        request = ToolRequest(
            tool_id="T09",
            operation="load_yaml",
            input_data={"file_path": self.test_files['complex']},
            parameters={}
        )
        
        result = self.tool.execute(request)
        doc = result.data["document"]
        
        # Verify depth calculation
        assert doc["depth"] > 3  # Complex YAML should have depth > 3
        
        # Test with simple YAML
        request_simple = ToolRequest(
            tool_id="T09",
            operation="load_yaml",
            input_data={"file_path": self.test_files['simple']},
            parameters={}
        )
        
        result_simple = self.tool.execute(request_simple)
        doc_simple = result_simple.data["document"]
        
        # Simple should have less depth than complex
        assert doc_simple["depth"] < doc["depth"]
    
    def test_key_counting_real(self):
        """Test key counting with REAL YAML structures"""
        request = ToolRequest(
            tool_id="T09",
            operation="load_yaml",
            input_data={"file_path": self.test_files['complex']},
            parameters={}
        )
        
        result = self.tool.execute(request)
        doc = result.data["document"]
        
        # Verify key counting
        assert doc["key_count"] > 20  # Complex YAML should have many keys
        
        # Test with list YAML
        request_list = ToolRequest(
            tool_id="T09",
            operation="load_yaml",
            input_data={"file_path": self.test_files['list']},
            parameters={}
        )
        
        result_list = self.tool.execute(request_list)
        doc_list = result_list.data["document"]
        
        # List structure should have fewer top-level keys but nested keys in items
        assert doc_list["key_count"] > 10  # Each list item has multiple keys
    
    def test_text_content_extraction_real(self):
        """Test text content extraction with REAL text processing"""
        request = ToolRequest(
            tool_id="T09",
            operation="load_yaml",
            input_data={"file_path": self.test_files['simple']},
            parameters={}
        )
        
        result = self.tool.execute(request)
        text_content = result.data["document"]["text_content"]
        
        # Verify all expected content is extracted
        assert "Test Application" in text_content
        assert "1.0.0" in text_content
        assert "Test Author" in text_content
        assert "test@example.com" in text_content
        assert "8080" in text_content
        assert "authentication" in text_content
        
        # Verify text is properly formatted
        assert len(text_content.strip()) > 0
        words = text_content.split()
        assert len(words) > 10  # Should have extracted multiple words
    
    def test_yaml_version_detection_real(self):
        """Test YAML version detection with REAL parsing"""
        request = ToolRequest(
            tool_id="T09",
            operation="load_yaml",
            input_data={"file_path": self.test_files['complex']},
            parameters={}
        )
        
        result = self.tool.execute(request)
        doc = result.data["document"]
        
        # Verify YAML version detection
        assert "yaml_version" in doc
        assert doc["yaml_version"] == "1.1"  # Complex file has %YAML 1.1 directive