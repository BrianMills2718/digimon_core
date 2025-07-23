"""
Mock-Free Tests for T13 Web Scraper Unified
Tests real web scraping with requests and BeautifulSoup
No mocking - uses real HTTP requests and actual web scraping operations
"""

import pytest
import tempfile
import http.server
import socketserver
import threading
import time
from pathlib import Path
from src.tools.phase1.t13_web_scraper_unified import T13WebScraperUnified
from src.core.service_manager import ServiceManager
from src.tools.base_tool import ToolRequest, ToolErrorCode


class TestT13WebScraperUnifiedMockFree:
    """Mock-free tests using real HTTP requests and web scraping"""
    
    def setup_method(self):
        """Setup with real ServiceManager and test data - NO mocks"""
        self.service_manager = ServiceManager()
        self.tool = T13WebScraperUnified(service_manager=self.service_manager)
        
        # Start a simple HTTP server for testing
        self.test_server = self._start_test_server()
        self.base_url = f"http://localhost:{self.test_server.server_address[1]}"
        
        # Public test URLs for real web requests
        self.public_urls = {
            'httpbin': 'https://httpbin.org/html',  # Reliable test service
            'example': 'http://example.com',  # Simple test page
        }
    
    def teardown_method(self):
        """Clean up test server"""
        if hasattr(self, 'test_server'):
            self.test_server.shutdown()
            self.test_server.server_close()
    
    def _start_test_server(self):
        """Start a simple HTTP server for testing"""
        
        class TestHTTPHandler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/':
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    html = """
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <title>Test Page</title>
                        <meta name="description" content="A test page for web scraping">
                        <meta property="og:title" content="Test Page OG Title">
                    </head>
                    <body>
                        <h1>Main Heading</h1>
                        <h2>Sub Heading</h2>
                        <p>This is a test paragraph with some content.</p>
                        <p>Another paragraph with different content.</p>
                        <a href="/page2" title="Link to page 2">Link to Page 2</a>
                        <div class="custom-content">Custom content for selector testing</div>
                        <script type="application/ld+json">
                        {"@type": "WebPage", "name": "Test Page"}
                        </script>
                    </body>
                    </html>
                    """
                    self.wfile.write(html.encode())
                elif self.path == '/page2':
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    html = """
                    <html>
                    <head><title>Page 2</title></head>
                    <body>
                        <h1>Second Page</h1>
                        <p>Content of the second page.</p>
                        <a href="/">Back to Home</a>
                    </body>
                    </html>
                    """
                    self.wfile.write(html.encode())
                elif self.path == '/timeout':
                    # Simulate slow response
                    time.sleep(2)
                    self.send_response(200)
                    self.end_headers()
                elif self.path == '/error':
                    self.send_response(500)
                    self.end_headers()
                else:
                    self.send_response(404)
                    self.end_headers()
        
        # Find available port
        with socketserver.TCPServer(("", 0), TestHTTPHandler) as server:
            port = server.server_address[1]
        
        # Start server in thread
        server = socketserver.TCPServer(("", port), TestHTTPHandler)
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        
        # Wait for server to start
        time.sleep(0.1)
        
        return server
    
    def test_simple_web_scraping_real(self):
        """Test basic web scraping with real HTTP requests"""
        request = ToolRequest(
            tool_id="T13",
            operation="scrape", 
            input_data={
                "url": f"{self.base_url}/",
                "scrape_links": False,
                "max_pages": 1
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        # Verify successful scraping
        assert result.status == "success"
        assert result.data["pages_scraped"] == 1
        assert result.metadata["confidence"] > 0.7
        assert result.execution_time > 0
        
        # Verify page content
        pages = result.data["pages"]
        assert len(pages) == 1
        
        page = pages[0]
        assert page["url"] == f"{self.base_url}/"
        assert page["title"] == "Test Page"
        assert page["status_code"] == 200
        assert page["content_length"] > 0
        
        # Verify text extraction
        text_content = page["extracted_content"]["text"]
        assert "Main Heading" in text_content["full_text"]
        assert "test paragraph" in text_content["full_text"]
        assert text_content["word_count"] > 10
        
        # Verify headings extraction
        headings = text_content["headings"]
        assert len(headings) >= 2
        assert any(h["text"] == "Main Heading" and h["level"] == 1 for h in headings)
        assert any(h["text"] == "Sub Heading" and h["level"] == 2 for h in headings)
    
    def test_link_extraction_real(self):
        """Test link extraction with real HTML parsing"""
        request = ToolRequest(
            tool_id="T13",
            operation="scrape",
            input_data={
                "url": f"{self.base_url}/",
                "scrape_links": True,
                "max_pages": 1
            }
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        
        # Verify link extraction
        page = result.data["pages"][0]
        links = page["extracted_content"]["links"]
        assert len(links) > 0
        
        # Check for specific link
        page2_link = next((link for link in links if "/page2" in link["url"]), None)
        assert page2_link is not None
        assert page2_link["text"] == "Link to Page 2"
        assert page2_link["title"] == "Link to page 2"
        assert page2_link["internal"] is True
    
    def test_multi_page_scraping_real(self):
        """Test multi-page scraping with real link following"""
        request = ToolRequest(
            tool_id="T13",
            operation="scrape",
            input_data={
                "url": f"{self.base_url}/",
                "scrape_links": True,
                "max_pages": 2
            }
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        assert result.data["pages_scraped"] >= 1  # At least the first page
        
        # Verify scraping summary
        summary = result.data["scraping_summary"]
        assert summary["successful_requests"] >= 1
        assert summary["total_content_length"] > 0
        assert summary["average_response_time"] > 0
    
    def test_custom_selectors_real(self):
        """Test custom CSS selectors with real BeautifulSoup parsing"""
        request = ToolRequest(
            tool_id="T13",
            operation="scrape",
            input_data={
                "url": f"{self.base_url}/",
                "selectors": {
                    "custom_div": ".custom-content",
                    "all_paragraphs": "p",
                    "headings": "h1, h2"
                }
            }  
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        
        # Verify custom content extraction
        custom_content = result.data["pages"][0]["extracted_content"]["custom"]
        
        # Check custom div
        assert "custom_div" in custom_content
        assert len(custom_content["custom_div"]) > 0
        assert "Custom content" in custom_content["custom_div"][0]["text"]
        
        # Check paragraphs
        assert "all_paragraphs" in custom_content
        assert len(custom_content["all_paragraphs"]) >= 2
        
        # Check headings
        assert "headings" in custom_content
        assert len(custom_content["headings"]) >= 2
    
    def test_metadata_extraction_real(self):
        """Test metadata extraction with real HTML parsing"""
        request = ToolRequest(
            tool_id="T13",
            operation="scrape",
            input_data={"url": f"{self.base_url}/"}
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        
        # Verify metadata extraction
        metadata = result.data["pages"][0]["extracted_content"]["metadata"]
        
        # Check meta tags
        assert "meta_tags" in metadata
        assert "description" in metadata["meta_tags"]
        assert "test page" in metadata["meta_tags"]["description"].lower()
        
        # Check OpenGraph tags
        assert "og_tags" in metadata
        assert "og:title" in metadata["og_tags"]
        
        # Check structured data
        assert "structured_data" in metadata
        if metadata["structured_data"]:
            assert metadata["structured_data"][0]["@type"] == "WebPage"
    
    def test_public_website_scraping_real(self):
        """Test scraping a real public website"""
        # Use httpbin.org which is designed for testing
        request = ToolRequest(
            tool_id="T13",
            operation="scrape",
            input_data={
                "url": self.public_urls['httpbin'],
                "timeout": 10
            }
        )
        
        result = self.tool.execute(request)
        
        # Should succeed with real website
        assert result.status == "success"
        assert result.data["pages_scraped"] == 1
        
        page = result.data["pages"][0]
        assert page["status_code"] == 200
        assert page["content_length"] > 0
        assert page["extracted_content"]["text"]["word_count"] > 0
    
    def test_connection_timeout_real(self):
        """Test connection timeout handling with real timeout scenario"""
        request = ToolRequest(
            tool_id="T13",
            operation="scrape",
            input_data={
                "url": f"{self.base_url}/timeout",
                "timeout": 1  # Very short timeout
            }
        )
        
        result = self.tool.execute(request)
        
        # Should timeout and return error
        assert result.status == "error"
        assert result.error_code == ToolErrorCode.CONNECTION_TIMEOUT
        assert result.execution_time > 0
    
    def test_http_error_handling_real(self):
        """Test HTTP error handling with real server error"""
        request = ToolRequest(
            tool_id="T13",
            operation="scrape",
            input_data={
                "url": f"{self.base_url}/error"
            }
        )
        
        result = self.tool.execute(request)
        
        # Should handle server error
        assert result.status == "error"
        assert result.error_code == ToolErrorCode.HTTP_ERROR
        assert result.data.get("status_code") == 500
    
    def test_invalid_url_real(self):
        """Test invalid URL handling with real validation"""
        request = ToolRequest(
            tool_id="T13",
            operation="scrape",
            input_data={
                "url": "not-a-valid-url"
            }
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "error"
        assert result.error_code == ToolErrorCode.INVALID_INPUT
    
    def test_nonexistent_domain_real(self):
        """Test handling of non-existent domain with real connection error"""
        request = ToolRequest(
            tool_id="T13",
            operation="scrape",
            input_data={
                "url": "http://this-domain-definitely-does-not-exist.com"
            }
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "error"
        assert result.error_code == ToolErrorCode.CONNECTION_ERROR
    
    def test_missing_input_data_real(self):
        """Test handling of missing input data with real validation"""
        request = ToolRequest(
            tool_id="T13",
            operation="scrape",
            input_data={}  # Missing url
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "error"
        assert result.error_code == ToolErrorCode.INVALID_INPUT
    
    def test_service_integration_real(self):
        """Test ServiceManager integration with real services"""
        request = ToolRequest(
            tool_id="T13",
            operation="scrape",
            input_data={"url": f"{self.base_url}/"}
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        
        # Verify service integration occurred
        metadata = result.metadata
        assert "identity_tracked" in metadata
        assert "provenance_logged" in metadata  
        assert "quality_assessed" in metadata
        
        # Services should have attempted tracking (success depends on service implementation)
        assert isinstance(metadata["identity_tracked"], bool)
        assert isinstance(metadata["provenance_logged"], bool)
        assert isinstance(metadata["quality_assessed"], bool)
    
    def test_performance_tracking_real(self):
        """Test performance tracking with real execution metrics"""
        request = ToolRequest(
            tool_id="T13",
            operation="scrape",
            input_data={
                "url": self.public_urls['example'],  # Use real external site
                "timeout": 10
            }
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        assert result.execution_time > 0
        assert hasattr(result, 'memory_used')
        
        # Real network request should take measurable time
        assert result.execution_time > 0.01  # At least 10ms
        
        # Check response time tracking
        page = result.data["pages"][0]
        assert page["response_time"] > 0
    
    def test_tool_contract_real(self):
        """Test tool contract specification with real implementation"""
        contract = self.tool.get_contract()
        
        # Verify contract structure
        assert contract["tool_id"] == "T13"
        assert contract["name"] == "Web Scraper"
        assert contract["category"] == "document_processing"
        assert "input_specification" in contract
        assert "output_specification" in contract
        assert "error_codes" in contract
        
        # Verify input specification
        input_spec = contract["input_specification"]
        assert "url" in input_spec
        assert input_spec["url"]["required"] is True
        assert "scrape_links" in input_spec
        assert "max_pages" in input_spec
        
        # Verify error codes
        error_codes = contract["error_codes"]
        assert ToolErrorCode.INVALID_INPUT in error_codes
        assert ToolErrorCode.CONNECTION_ERROR in error_codes
        assert ToolErrorCode.HTTP_ERROR in error_codes
    
    def test_health_check_real(self):
        """Test health check functionality with real HTTP request"""
        health_result = self.tool.health_check()
        
        assert "status" in health_result
        assert health_result["status"] in ["healthy", "unhealthy"]
        assert "requests_available" in health_result
        assert health_result["requests_available"] is True
        assert "beautifulsoup_available" in health_result
        assert health_result["beautifulsoup_available"] is True
        
        # Health check should make real HTTP request
        assert "test_request_successful" in health_result
    
    def test_cleanup_functionality_real(self):
        """Test cleanup functionality with real resource management"""
        # Cleanup should not raise exceptions
        try:
            self.tool.cleanup()
            cleanup_success = True
        except Exception:
            cleanup_success = False
        
        assert cleanup_success is True
    
    def test_confidence_calculation_real(self):
        """Test confidence calculation with different scraping scenarios"""
        # Test high confidence with good content
        request_good = ToolRequest(
            tool_id="T13",
            operation="scrape",
            input_data={"url": f"{self.base_url}/"}
        )
        result_good = self.tool.execute(request_good)
        
        # Test lower confidence with minimal content
        request_minimal = ToolRequest(
            tool_id="T13", 
            operation="scrape",
            input_data={"url": self.public_urls['example']}  # Very minimal page
        )
        result_minimal = self.tool.execute(request_minimal)
        
        assert result_good.status == "success"
        assert result_minimal.status == "success"
        
        # Good content should have higher confidence
        assert result_good.metadata["confidence"] > 0.7
        assert result_minimal.metadata["confidence"] > 0.5
    
    def test_session_management_real(self):
        """Test session management with real HTTP requests"""
        # Make multiple requests to ensure session is reused
        requests_data = [
            {"url": f"{self.base_url}/"},
            {"url": f"{self.base_url}/page2"}
        ]
        
        results = []
        for req_data in requests_data:
            request = ToolRequest(
                tool_id="T13",
                operation="scrape", 
                input_data=req_data
            )
            result = self.tool.execute(request)
            results.append(result)
        
        # All requests should succeed
        for result in results:
            assert result.status == "success"
        
        # Verify session is properly managed
        assert hasattr(self.tool, 'session')
        assert self.tool.session is not None
    
    def test_text_extraction_quality_real(self):
        """Test quality of text extraction with real HTML content"""
        request = ToolRequest(
            tool_id="T13",
            operation="scrape",
            input_data={"url": f"{self.base_url}/"}
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        
        text_content = result.data["pages"][0]["extracted_content"]["text"]
        
        # Should extract meaningful content
        assert text_content["word_count"] > 10
        assert len(text_content["paragraphs"]) >= 2
        assert len(text_content["headings"]) >= 2
        
        # Text should be cleaned properly
        assert not text_content["full_text"].startswith(" ")
        assert not text_content["full_text"].endswith(" ")
        
        # Should not contain script/style content
        assert "<script>" not in text_content["full_text"]
        assert "<style>" not in text_content["full_text"]
    
    def test_url_validation_comprehensive_real(self):
        """Test comprehensive URL validation with real parsing"""
        test_cases = [
            ("https://example.com", True),
            ("http://example.com", True),
            ("ftp://example.com", False),  # Not HTTP/HTTPS
            ("example.com", False),  # No scheme
            ("", False),  # Empty
            ("not-a-url", False),  # Invalid format
        ]
        
        for url, should_be_valid in test_cases:
            request = ToolRequest(
                tool_id="T13",
                operation="scrape",
                input_data={"url": url}
            )
            
            result = self.tool.execute(request)
            
            if should_be_valid:
                # Valid URLs should either succeed or fail with network errors
                assert result.error_code != ToolErrorCode.INVALID_INPUT
            else:
                # Invalid URLs should fail validation
                assert result.status == "error"
                assert result.error_code == ToolErrorCode.INVALID_INPUT