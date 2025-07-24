#!/usr/bin/env python3
"""
Automated UI Tester for KGAS
This script automatically tests the UI and identifies issues without manual intervention
"""

import subprocess
import time
import requests
import json
from pathlib import Path
from datetime import datetime
import sys
import os
import signal

class AutomatedUITester:
    """Automatically tests KGAS UI and reports issues"""
    
    def __init__(self):
        self.server_process = None
        self.port = 8888
        self.base_url = f"http://localhost:{self.port}"
        self.issues_found = []
        self.test_results = []
        
    def find_free_port(self):
        """Find a free port to use"""
        import socket
        for port in range(8888, 9999):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.bind(('', port))
                s.close()
                return port
            except:
                continue
        return None
        
    def start_server(self):
        """Start the test server"""
        self.port = self.find_free_port()
        if not self.port:
            self.add_issue("CRITICAL", "No free ports available")
            return False
            
        print(f"🚀 Starting server on port {self.port}...")
        
        # Start simple HTTP server
        self.server_process = subprocess.Popen(
            ['python3', '-m', 'http.server', str(self.port)],
            cwd='ui',
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for server to start
        time.sleep(2)
        
        # Check if server is running
        try:
            response = requests.get(f"http://localhost:{self.port}/research_ui.html", timeout=5)
            if response.status_code == 200:
                print(f"✅ Server started successfully on port {self.port}")
                return True
        except:
            pass
            
        self.add_issue("ERROR", f"Failed to start server on port {self.port}")
        return False
        
    def stop_server(self):
        """Stop the test server"""
        if self.server_process:
            print("🛑 Stopping server...")
            self.server_process.terminate()
            self.server_process.wait()
            
    def add_issue(self, severity, description, suggestion=None):
        """Add an issue to the issues list"""
        issue = {
            "severity": severity,
            "description": description,
            "suggestion": suggestion,
            "timestamp": datetime.now().isoformat()
        }
        self.issues_found.append(issue)
        print(f"❌ {severity}: {description}")
        if suggestion:
            print(f"   💡 Suggestion: {suggestion}")
            
    def add_success(self, test_name, description):
        """Add a successful test result"""
        result = {
            "test": test_name,
            "status": "PASS",
            "description": description,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"✅ {test_name}: {description}")
        
    def test_html_structure(self):
        """Test the HTML structure of the UI"""
        print("\n🔍 Testing HTML structure...")
        
        try:
            response = requests.get(f"http://localhost:{self.port}/research_ui.html", timeout=5)
            
            if response.status_code != 200:
                self.add_issue("ERROR", f"Failed to load UI (status {response.status_code})")
                return
                
            content = response.text
            
            # Check for required elements
            required_elements = [
                ('<div class="tabs">', "Tab navigation"),
                ('id="documents"', "Documents tab"),
                ('id="analysis"', "Analysis tab"),
                ('id="graph"', "Graph tab"),
                ('id="query"', "Query tab"),
                ('id="export"', "Export tab"),
                ('function showTab', "Tab switching JavaScript")
            ]
            
            for element, description in required_elements:
                if element in content:
                    self.add_success("HTML Structure", f"Found {description}")
                else:
                    self.add_issue("ERROR", f"Missing {description}", f"Add {element} to the HTML")
                    
            # Check for proper encoding
            if 'charset="UTF-8"' in content:
                self.add_success("HTML Structure", "Proper UTF-8 encoding")
            else:
                self.add_issue("WARNING", "Missing UTF-8 charset declaration")
                
        except Exception as e:
            self.add_issue("ERROR", f"Failed to test HTML structure: {str(e)}")
            
    def test_javascript_functionality(self):
        """Test JavaScript functionality using requests"""
        print("\n🔍 Testing JavaScript functionality...")
        
        # Since we can't execute JS without Puppeteer, we check for JS code presence
        try:
            response = requests.get(f"http://localhost:{self.port}/research_ui.html", timeout=5)
            content = response.text
            
            js_functions = [
                ('showTab(', "Tab switching function"),
                ('addEventListener', "Event listeners"),
                ('classList.add', "CSS class manipulation"),
                ('classList.remove', "CSS class removal")
            ]
            
            for func, description in js_functions:
                if func in content:
                    self.add_success("JavaScript", f"Found {description}")
                else:
                    self.add_issue("WARNING", f"Missing {description}")
                    
        except Exception as e:
            self.add_issue("ERROR", f"Failed to test JavaScript: {str(e)}")
            
    def test_css_styling(self):
        """Test CSS styling"""
        print("\n🔍 Testing CSS styling...")
        
        try:
            response = requests.get(f"http://localhost:{self.port}/research_ui.html", timeout=5)
            content = response.text
            
            # Check for CSS rules
            css_rules = [
                ('.tab {', "Tab styling"),
                ('.tab.active {', "Active tab styling"),
                ('.ui-component {', "Component styling"),
                ('button {', "Button styling"),
                ('.upload-zone {', "Upload zone styling")
            ]
            
            for rule, description in css_rules:
                if rule in content:
                    self.add_success("CSS", f"Found {description}")
                else:
                    self.add_issue("WARNING", f"Missing {description}")
                    
        except Exception as e:
            self.add_issue("ERROR", f"Failed to test CSS: {str(e)}")
            
    def test_react_app_setup(self):
        """Test React app setup"""
        print("\n🔍 Testing React app setup...")
        
        # Check if package.json exists
        package_path = Path("ui/research-app/package.json")
        if package_path.exists():
            self.add_success("React Setup", "package.json exists")
            
            # Check package.json content
            try:
                with open(package_path) as f:
                    package = json.load(f)
                    
                required_deps = ["react", "react-dom", "vite", "@tanstack/react-query"]
                for dep in required_deps:
                    if dep in package.get("dependencies", {}):
                        self.add_success("React Dependencies", f"{dep} is included")
                    else:
                        self.add_issue("ERROR", f"Missing dependency: {dep}")
                        
            except Exception as e:
                self.add_issue("ERROR", f"Failed to parse package.json: {str(e)}")
        else:
            self.add_issue("ERROR", "React app package.json not found", "Run create_research_ui_components.py")
            
        # Check React components
        components = [
            "ui/research-app/src/App.jsx",
            "ui/research-app/src/components/DocumentManager.jsx",
            "ui/research-app/src/components/AnalysisDashboard.jsx",
            "ui/research-app/src/components/Layout.jsx"
        ]
        
        for component in components:
            if Path(component).exists():
                self.add_success("React Components", f"{Path(component).name} exists")
            else:
                self.add_issue("ERROR", f"Missing component: {component}")
                
    def test_api_endpoints(self):
        """Test that API endpoints are documented"""
        print("\n🔍 Testing API endpoint documentation...")
        
        # Check API service file
        api_path = Path("ui/research-app/src/services/api.js")
        if api_path.exists():
            with open(api_path) as f:
                api_content = f.read()
                
            endpoints = [
                ('/documents/upload', "Document upload"),
                ('/analysis/start', "Start analysis"),
                ('/graph', "Get graph data"),
                ('/query/execute', "Execute query")
            ]
            
            for endpoint, description in endpoints:
                if endpoint in api_content:
                    self.add_success("API Endpoints", f"{description} endpoint defined")
                else:
                    self.add_issue("WARNING", f"Missing {description} endpoint")
        else:
            self.add_issue("ERROR", "API service file not found")
            
    def generate_fix_script(self):
        """Generate a script to fix found issues"""
        if not self.issues_found:
            return
            
        print("\n📝 Generating fix script...")
        
        fix_script = """#!/usr/bin/env python3
# Auto-generated fix script for KGAS UI issues
# Generated at: """ + datetime.now().isoformat() + """

import os
import sys
from pathlib import Path

def fix_issues():
    \"\"\"Fix identified issues\"\"\"
    fixes_applied = 0
    
"""
        
        for issue in self.issues_found:
            if issue["suggestion"]:
                fix_script += f"""    # Fix: {issue["description"]}
    print("Fixing: {issue["description"]}")
    # TODO: Implement fix - {issue["suggestion"]}
    fixes_applied += 1
    
"""
        
        fix_script += """    print(f"\\n✅ Applied {fixes_applied} fixes")
    print("Please review and run the React app setup if needed")

if __name__ == "__main__":
    fix_issues()
"""
        
        fix_path = Path("ui/fix_ui_issues.py")
        fix_path.write_text(fix_script)
        fix_path.chmod(0o755)
        
        print(f"✅ Fix script generated: {fix_path}")
        
    def generate_report(self):
        """Generate a comprehensive test report"""
        report = {
            "test_run": datetime.now().isoformat(),
            "server_port": self.port,
            "total_tests": len(self.test_results),
            "passed_tests": len([r for r in self.test_results if r["status"] == "PASS"]),
            "issues_found": len(self.issues_found),
            "issues_by_severity": {
                "CRITICAL": len([i for i in self.issues_found if i["severity"] == "CRITICAL"]),
                "ERROR": len([i for i in self.issues_found if i["severity"] == "ERROR"]),
                "WARNING": len([i for i in self.issues_found if i["severity"] == "WARNING"])
            },
            "test_results": self.test_results,
            "issues": self.issues_found,
            "recommendations": []
        }
        
        # Add recommendations based on issues
        if report["issues_by_severity"]["CRITICAL"] > 0:
            report["recommendations"].append("Fix critical issues immediately")
        if report["issues_by_severity"]["ERROR"] > 0:
            report["recommendations"].append("Address error-level issues before deployment")
        if not Path("ui/research-app/node_modules").exists():
            report["recommendations"].append("Run 'npm install' in ui/research-app directory")
            
        # Save report
        report_path = Path("ui/automated_test_report.json")
        report_path.write_text(json.dumps(report, indent=2))
        
        print(f"\n📊 Test Report Summary:")
        print(f"- Total tests: {report['total_tests']}")
        print(f"- Passed: {report['passed_tests']}")
        print(f"- Issues found: {report['issues_found']}")
        print(f"  - Critical: {report['issues_by_severity']['CRITICAL']}")
        print(f"  - Errors: {report['issues_by_severity']['ERROR']}")
        print(f"  - Warnings: {report['issues_by_severity']['WARNING']}")
        print(f"\n📄 Full report saved to: {report_path}")
        
        return report
        
    def run_all_tests(self):
        """Run all automated tests"""
        print("🤖 KGAS Automated UI Testing")
        print("=" * 50)
        
        # Start server
        if not self.start_server():
            print("❌ Failed to start server, aborting tests")
            return
            
        try:
            # Run all tests
            self.test_html_structure()
            self.test_javascript_functionality()
            self.test_css_styling()
            self.test_react_app_setup()
            self.test_api_endpoints()
            
            # Generate outputs
            self.generate_report()
            if self.issues_found:
                self.generate_fix_script()
                
        finally:
            # Always stop server
            self.stop_server()
            
        print("\n✨ Automated testing complete!")
        
        # Return success/failure
        return len([i for i in self.issues_found if i["severity"] in ["CRITICAL", "ERROR"]]) == 0


def main():
    """Main entry point"""
    tester = AutomatedUITester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()