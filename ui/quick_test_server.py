#!/usr/bin/env python3
"""
Quick test server for KGAS UI
Serves the HTML UI and provides mock API endpoints for testing
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import os
import threading
import time
from pathlib import Path
import socketserver
import urllib.parse

class KGASTestHandler(SimpleHTTPRequestHandler):
    """Custom handler for KGAS UI testing"""
    
    def do_GET(self):
        """Handle GET requests"""
        parsed = urllib.parse.urlparse(self.path)
        
        # API endpoints
        if parsed.path.startswith('/api/'):
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # Mock responses
            if parsed.path == '/api/status':
                response = {
                    "status": "running",
                    "version": "1.0.0",
                    "tools_available": 32,
                    "documents_processed": 0
                }
            elif parsed.path == '/api/collections':
                response = [
                    {"id": "research", "name": "Research Papers", "count": 0},
                    {"id": "technical", "name": "Technical Reports", "count": 0},
                    {"id": "reviews", "name": "Literature Reviews", "count": 0}
                ]
            elif parsed.path == '/api/analysis/status':
                response = {
                    "status": "idle",
                    "progress": 0,
                    "toolStatus": []
                }
            else:
                response = {"message": "Mock endpoint"}
                
            self.wfile.write(json.dumps(response).encode())
            return
            
        # Serve files
        if parsed.path == '/':
            self.path = '/research_ui.html'
        
        return SimpleHTTPRequestHandler.do_GET(self)
    
    def do_POST(self):
        """Handle POST requests"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {"status": "success", "message": "Mock response"}
        self.wfile.write(json.dumps(response).encode())
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()


def run_server(port=8080):
    """Run the test server"""
    os.chdir('ui')  # Change to UI directory
    
    handler = KGASTestHandler
    httpd = socketserver.TCPServer(("", port), handler)
    httpd.allow_reuse_address = True
    
    print(f"🚀 KGAS Test Server running at http://localhost:{port}")
    print(f"📄 Serving UI from: {os.getcwd()}")
    print(f"🔌 Mock API endpoints available at http://localhost:{port}/api/*")
    print("\nPress Ctrl+C to stop the server")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n✋ Server stopped")
        httpd.shutdown()


if __name__ == "__main__":
    run_server()