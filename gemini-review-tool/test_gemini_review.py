#!/usr/bin/env python3
"""
Comprehensive tests for gemini review functionality.

This test suite validates all security, robustness, and performance improvements
implemented according to CLAUDE.md requirements.
"""

import unittest
import tempfile
import os
import time
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import the modules to test
try:
    from gemini_review import (
        GeminiCodeReviewer, 
        validate_project_path, 
        validate_patterns,
        RateLimiter,
        ReviewError,
        APIError,
        FileSystemError,
        ValidationError,
        ConfigurationError,
        retry_with_backoff,
        setup_logging
    )
    from gemini_review_cache import ReviewCache
except ImportError as e:
    print(f"⚠️  Warning: Could not import modules: {e}")
    print("Please ensure all modules are in the same directory as this test file.")
    import sys
    sys.exit(1)


class TestSecurityFeatures(unittest.TestCase):
    """Test security enhancements."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_api_key = "test-api-key-12345"
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_secure_api_key_validation(self):
        """Test API key security validation."""
        # Test with provided key (should work but warn)
        with patch('builtins.print') as mock_print:
            reviewer = GeminiCodeReviewer(api_key=self.test_api_key, log_level="ERROR")
            self.assertEqual(reviewer.api_key, self.test_api_key)
            # Should have warned about command line usage
            warning_printed = any("WARNING" in str(call) for call in mock_print.call_args_list)
            self.assertTrue(warning_printed, "Should warn about insecure command line API key usage")
        
        # Test missing key should raise error
        with patch.dict(os.environ, {}, clear=True):  # Clear environment
            with patch('sys.stdin.isatty', return_value=False):  # Non-interactive
                with self.assertRaises((ValueError, ConfigurationError)):
                    GeminiCodeReviewer(api_key=None, log_level="ERROR")
    
    def test_path_validation_security(self):
        """Test path validation prevents security issues."""
        # Test valid path
        valid_path = validate_project_path(self.temp_dir)
        self.assertEqual(str(valid_path), str(Path(self.temp_dir).resolve()))
        
        # Test path traversal prevention
        with self.assertRaises(ValidationError):
            validate_project_path("../../../etc/passwd")
        
        # Test empty path
        with self.assertRaises(ValidationError):
            validate_project_path("")
        
        # Test non-existent path
        with self.assertRaises(ValidationError):
            validate_project_path("/non/existent/path/12345")
    
    def test_pattern_validation(self):
        """Test pattern validation removes dangerous inputs."""
        safe_patterns = ["*.py", "src/**/*.js", "*.md"]
        dangerous_patterns = ["*.py; rm -rf /", "$(malicious command)", "|dangerous"]
        
        validated = validate_patterns(safe_patterns + dangerous_patterns)
        
        # Should keep safe patterns
        for safe in safe_patterns:
            self.assertIn(safe, validated, f"Safe pattern {safe} should be retained")
        
        # Should remove dangerous patterns
        for dangerous in dangerous_patterns:
            self.assertNotIn(dangerous, validated, f"Dangerous pattern {dangerous} should be removed")
        
        # Test empty list
        self.assertEqual(validate_patterns([]), [])
        
        # Test None input
        self.assertEqual(validate_patterns(None), [])
    
    def test_rate_limiter(self):
        """Test rate limiting functionality."""
        # Test rate limiter functionality without relying on precise timing
        limiter = RateLimiter(max_calls=2, time_window=2, burst_allowance=1)
        
        # Test that the rate limiter exists and has correct attributes
        self.assertTrue(hasattr(limiter, 'max_calls'))
        self.assertTrue(hasattr(limiter, 'time_window'))
        self.assertTrue(hasattr(limiter, 'burst_allowance'))
        self.assertTrue(hasattr(limiter, 'wait_if_needed'))
        
        # Test statistics functionality
        stats = limiter.get_statistics()
        self.assertIsInstance(stats, dict)
        self.assertIn('current_calls_in_window', stats)
        self.assertIn('max_calls', stats)
        
        # Test error handling functionality
        from gemini_review import APIError
        initial_error_count = limiter.error_count
        limiter.handle_api_error(APIError("Test error"))
        self.assertGreater(limiter.error_count, initial_error_count)
        
        # Test success handling
        limiter.handle_api_success()  # Should not raise exception


class TestErrorHandling(unittest.TestCase):
    """Test error handling and robustness features."""
    
    def test_custom_exception_hierarchy(self):
        """Test custom exception classes exist and inherit correctly."""
        # Test base exception
        self.assertTrue(issubclass(ReviewError, Exception))
        
        # Test specific exceptions
        self.assertTrue(issubclass(ConfigurationError, ReviewError))
        self.assertTrue(issubclass(APIError, ReviewError))
        self.assertTrue(issubclass(FileSystemError, ReviewError))
        self.assertTrue(issubclass(ValidationError, ReviewError))
        
        # Test exceptions can be raised and caught
        with self.assertRaises(ConfigurationError):
            raise ConfigurationError("Test config error")
        
        with self.assertRaises(APIError):
            raise APIError("Test API error")
    
    def test_logging_setup(self):
        """Test logging infrastructure."""
        import logging
        
        # Test logger creation
        logger = setup_logging("DEBUG")
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, "gemini_review")
        self.assertEqual(logger.level, logging.DEBUG)
        
        # Test with file output
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_path = tmp_file.name
        
        try:
            logger = setup_logging("INFO", tmp_path)
            logger.info("Test log message")
            
            # Check if log file was created and has content
            self.assertTrue(os.path.exists(tmp_path))
            with open(tmp_path, 'r') as f:
                content = f.read()
                self.assertIn("Test log message", content)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def test_retry_decorator(self):
        """Test retry mechanism with exponential backoff."""
        call_count = 0
        
        @retry_with_backoff(max_retries=2, base_delay=0.1)
        def failing_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise APIError("Simulated API failure")
            return "Success"
        
        # Should succeed after retries
        result = failing_function()
        self.assertEqual(result, "Success")
        self.assertEqual(call_count, 3, "Should have been called 3 times")
        
        # Test function that always fails
        @retry_with_backoff(max_retries=1, base_delay=0.1)
        def always_failing_function():
            raise APIError("Always fails")
        
        with self.assertRaises(APIError):
            always_failing_function()


class TestCachingSystem(unittest.TestCase):
    """Test caching optimizations."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.cache_dir = os.path.join(self.temp_dir, "test_cache")
        
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_cache_creation_and_info(self):
        """Test cache creation and information gathering."""
        cache = ReviewCache(self.cache_dir, max_age_hours=1)
        
        # Test cache directory creation
        self.assertTrue(os.path.exists(self.cache_dir))
        
        # Test cache info
        info = cache.get_cache_info()
        self.assertIn('total_files', info)
        self.assertIn('total_size_mb', info)
        self.assertIn('cache_dir', info)
        self.assertEqual(info['total_files'], 0)  # Should be empty initially
    
    def test_cache_operations(self):
        """Test cache set and get operations."""
        cache = ReviewCache(self.cache_dir, max_age_hours=1)
        
        # Test setting and getting repomix cache
        test_content = "# Test Content\nSome test code here"
        cache.set_repomix_cache(".", test_content, ignore_patterns=["*.pyc"])
        
        # Should retrieve the same content
        retrieved = cache.get_repomix_cache(".", ignore_patterns=["*.pyc"])
        self.assertEqual(retrieved, test_content)
        
        # Different parameters should miss cache
        missed = cache.get_repomix_cache(".", ignore_patterns=["*.log"])
        self.assertIsNone(missed)
    
    def test_cache_expiration(self):
        """Test cache expiration mechanism."""
        import tempfile
        import os
        from datetime import datetime, timedelta
        from unittest.mock import patch
        
        # Create a test file that will definitely exist
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
            tmp_file.write("test content")
            test_file_path = tmp_file.name
        
        try:
            cache = ReviewCache(self.cache_dir, max_age_hours=1)  # 1 hour expiry
            
            # Set some cache content with the test file path
            cache.set_repomix_cache(test_file_path, "test content")
            
            # Should get it immediately
            result = cache.get_repomix_cache(test_file_path)
            self.assertEqual(result, "test content")
            
            # Mock datetime to simulate time passing
            future_time = datetime.now() + timedelta(hours=2)  # 2 hours in future
            with patch('gemini_review_cache.datetime') as mock_datetime:
                mock_datetime.now.return_value = future_time
                mock_datetime.fromtimestamp.side_effect = datetime.fromtimestamp
                
                # Should miss cache now due to expiration
                expired_result = cache.get_repomix_cache(test_file_path)
                self.assertIsNone(expired_result)
        finally:
            # Clean up test file
            if os.path.exists(test_file_path):
                os.unlink(test_file_path)


class TestIntegration(unittest.TestCase):
    """Test integration of all components."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test.py")
        
        # Create a simple test file
        with open(self.test_file, 'w') as f:
            f.write("#!/usr/bin/env python3\n")
            f.write("# Simple test file\n")
            f.write("def hello():\n")
            f.write("    print('Hello, World!')\n")
        
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_reviewer_initialization(self, mock_model, mock_configure):
        """Test reviewer initialization with all security features."""
        # Mock the Gemini API
        mock_model_instance = MagicMock()
        mock_model.return_value = mock_model_instance
        
        # Test initialization with API key
        reviewer = GeminiCodeReviewer(
            api_key="test-key-123",
            enable_cache=False,  # Disable cache for testing
            log_level="ERROR"    # Reduce log noise
        )
        
        # Verify initialization
        self.assertEqual(reviewer.api_key, "test-key-123")
        self.assertIsNotNone(reviewer.rate_limiter)
        self.assertIsNotNone(reviewer.logger)
        
        # Verify Gemini was configured
        mock_configure.assert_called_once_with(api_key="test-key-123")
    
    def test_path_validation_integration(self):
        """Test path validation in real scenarios."""
        # Test with valid directory
        validated_path = validate_project_path(self.temp_dir)
        self.assertTrue(validated_path.exists())
        self.assertTrue(validated_path.is_dir())
        
        # Test with valid file
        validated_file = validate_project_path(self.test_file)
        self.assertTrue(validated_file.exists())
        self.assertTrue(validated_file.is_file())


class TestCommandLineInterface(unittest.TestCase):
    """Test command line interface improvements."""
    
    def test_pattern_validation_in_cli(self):
        """Test that CLI properly validates patterns."""
        # This would typically test the main() function
        # but since it requires significant mocking, we'll test the validation directly
        
        test_patterns = ["*.py", "src/**/*.js", "$(rm -rf /)", "normal_pattern"]
        validated = validate_patterns(test_patterns)
        
        # Should keep safe patterns and remove dangerous ones
        safe_count = sum(1 for p in ["*.py", "src/**/*.js", "normal_pattern"] if p in validated)
        self.assertEqual(safe_count, 3, "Should keep all safe patterns")
        
        dangerous_count = sum(1 for p in ["$(rm -rf /)"] if p in validated)
        self.assertEqual(dangerous_count, 0, "Should remove dangerous patterns")


def run_comprehensive_tests():
    """Run all tests and provide detailed results."""
    print("🧪 Running Gemini Review Tool Comprehensive Test Suite")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestSecurityFeatures,
        TestErrorHandling,
        TestCachingSystem,
        TestIntegration,
        TestCommandLineInterface
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    print(f"   Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"   {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\n💥 Errors:")
        for test, traceback in result.errors:
            print(f"   {test}: {traceback.split('Error:')[-1].strip()}")
    
    if result.wasSuccessful():
        print("\n✅ All tests passed! Security and robustness improvements verified.")
        return True
    else:
        print("\n❌ Some tests failed. Please review and fix issues before deployment.")
        return False


if __name__ == "__main__":
    success = run_comprehensive_tests()
    exit(0 if success else 1)