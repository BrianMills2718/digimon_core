#!/usr/bin/env python3
"""
Error Handling Tests - Production Quality
Tests all error scenarios with 100% pass rate requirement
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.core.error_handler import (
    ProductionErrorHandler, ValidationError, ProcessingError, 
    DatabaseConnectionError, ServiceUnavailableError, SystemError
)

class TestErrorHandling(unittest.TestCase):
    """Test comprehensive error handling scenarios"""
    
    def setUp(self):
        """Set up test environment"""
        self.error_handler = ProductionErrorHandler()
    
    def test_user_input_validation_errors(self):
        """Test user input validation error scenarios"""
        # Test empty required input
        with self.assertRaises(ValidationError):
            self.error_handler.handle_user_input_error("", {"required": True})
        
        # Test None required input
        with self.assertRaises(ValidationError):
            self.error_handler.handle_user_input_error(None, {"required": True})
        
        # Test whitespace-only required input
        with self.assertRaises(ValidationError):
            self.error_handler.handle_user_input_error("   ", {"required": True})
        
        # Test input too long
        with self.assertRaises(ValidationError):
            self.error_handler.handle_user_input_error("x" * 1000, {"max_length": 100})
        
        # Test wrong data type
        with self.assertRaises(ValidationError):
            self.error_handler.handle_user_input_error(123, {"expected_type": str})
    
    def test_security_validation_errors(self):
        """Test security validation error scenarios"""
        dangerous_inputs = [
            "<script>alert('xss')</script>",
            "SELECT * FROM users",
            "DROP TABLE users",
            "INSERT INTO users",
            "UPDATE users SET",
            "DELETE FROM users"
        ]
        
        for dangerous_input in dangerous_inputs:
            with self.assertRaises(ValidationError):
                self.error_handler.handle_user_input_error(dangerous_input, {"required": True})
    
    def test_database_connection_errors(self):
        """Test database connection error scenarios"""
        # Test connection failure
        connection_error = Exception("Connection refused")
        with self.assertRaises(DatabaseConnectionError):
            self.error_handler.handle_database_error(connection_error, "connect", {})
        
        # Test authentication failure
        auth_error = Exception("Authentication failed")
        with self.assertRaises(DatabaseConnectionError):
            self.error_handler.handle_database_error(auth_error, "authenticate", {})
        
        # Test timeout
        timeout_error = Exception("Query timeout")
        with self.assertRaises(DatabaseConnectionError):
            self.error_handler.handle_database_error(timeout_error, "query", {})
        
        # Test constraint violation
        constraint_error = Exception("Constraint violation")
        with self.assertRaises(DatabaseConnectionError):
            self.error_handler.handle_database_error(constraint_error, "insert", {})
    
    def test_service_unavailable_errors(self):
        """Test service unavailable error scenarios"""
        services = [
            "openai_api",
            "gemini_api",
            "neo4j_database",
            "external_api"
        ]
        
        for service in services:
            service_error = Exception(f"{service} is unavailable")
            with self.assertRaises(ServiceUnavailableError):
                self.error_handler.handle_service_unavailable(service, service_error)
    
    def test_configuration_errors(self):
        """Test configuration error scenarios"""
        config_errors = [
            ("api_key", "API key not found"),
            ("database_url", "Database URL invalid"),
            ("model_path", "Model path not found"),
            ("config_file", "Configuration file corrupted")
        ]
        
        for config_key, error_message in config_errors:
            config_error = Exception(error_message)
            with self.assertRaises(SystemError):
                self.error_handler.handle_configuration_error(config_error, config_key)
    
    def test_processing_errors(self):
        """Test processing error scenarios"""
        # Test memory error
        memory_error = MemoryError("Out of memory")
        with self.assertRaises(SystemError):
            self.error_handler.handle_processing_error(memory_error, {"operation": "large_dataset"})
        
        # Test file not found
        file_error = FileNotFoundError("File not found")
        with self.assertRaises(ProcessingError):
            self.error_handler.handle_processing_error(file_error, {"operation": "file_load"})
        
        # Test permission error
        permission_error = PermissionError("Permission denied")
        with self.assertRaises(ProcessingError):
            self.error_handler.handle_processing_error(permission_error, {"operation": "file_write"})
        
        # Test generic processing error
        generic_error = Exception("Processing failed")
        with self.assertRaises(ProcessingError):
            self.error_handler.handle_processing_error(generic_error, {"operation": "data_transform"})
    
    def test_error_statistics_tracking(self):
        """Test error statistics tracking"""
        # Generate some errors
        try:
            self.error_handler.handle_user_input_error("", {"required": True})
        except ValidationError:
            pass
        
        try:
            self.error_handler.handle_database_error(Exception("DB error"), "query", {})
        except DatabaseConnectionError:
            pass
        
        # Check statistics
        stats = self.error_handler.get_error_statistics()
        
        self.assertGreater(stats['total_errors'], 0)
        self.assertIn('ValidationError', stats['errors_by_type'])
        self.assertIn('DatabaseError', stats['errors_by_type'])
        self.assertIsNotNone(stats['last_error_time'])
    
    def test_error_statistics_reset(self):
        """Test error statistics reset"""
        # Generate an error
        try:
            self.error_handler.handle_user_input_error("", {"required": True})
        except ValidationError:
            pass
        
        # Verify statistics exist
        stats = self.error_handler.get_error_statistics()
        self.assertGreater(stats['total_errors'], 0)
        
        # Reset statistics
        self.error_handler.reset_error_statistics()
        
        # Verify statistics are reset
        stats = self.error_handler.get_error_statistics()
        self.assertEqual(stats['total_errors'], 0)
        self.assertEqual(len(stats['errors_by_type']), 0)
        self.assertEqual(len(stats['errors_by_severity']), 0)
        self.assertIsNone(stats['last_error_time'])
    
    def test_fail_fast_behavior(self):
        """Test fail-fast behavior - errors should propagate immediately"""
        # Test that errors are not caught and hidden
        with self.assertRaises(ValidationError):
            self.error_handler.handle_user_input_error(None, {"required": True})
        
        with self.assertRaises(DatabaseConnectionError):
            self.error_handler.handle_database_error(Exception("DB error"), "test", {})
        
        with self.assertRaises(ServiceUnavailableError):
            self.error_handler.handle_service_unavailable("test_service", Exception("Service down"))
        
        with self.assertRaises(SystemError):
            self.error_handler.handle_configuration_error(Exception("Config error"), "test_key")
        
        with self.assertRaises(ProcessingError):
            self.error_handler.handle_processing_error(Exception("Process error"), {"op": "test"})
    
    def test_error_context_preservation(self):
        """Test that error context is preserved"""
        context = {
            "user_id": "test_user",
            "operation": "test_operation",
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            self.error_handler.handle_database_error(Exception("Test error"), "test_op", context)
        except DatabaseConnectionError as e:
            # Verify error message contains context information
            self.assertIn("test_op", str(e))
            self.assertIn("Test error", str(e))
        
        # Verify context is recorded in statistics
        stats = self.error_handler.get_error_statistics()
        self.assertGreater(stats['total_errors'], 0)

if __name__ == "__main__":
    unittest.main(verbosity=2)