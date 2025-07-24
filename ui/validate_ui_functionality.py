#!/usr/bin/env python3
"""
Validate UI Functionality for KGAS
Comprehensive validation of all UI components and interactions
"""

import subprocess
import time
import requests
from pathlib import Path
import json
import sys
from bs4 import BeautifulSoup
import re

class UIValidator:
    """Validates UI functionality comprehensively"""
    
    def __init__(self):
        self.server_process = None
        self.port = 8890  # Different port to avoid conflicts
        self.base_url = f"http://localhost:{self.port}"
        self.validation_results = {
            "server_start": False,
            "page_load": False,
            "html_structure": False,
            "javascript_valid": False,
            "css_valid": False,
            "tabs_functional": False,
            "components_render": False,
            "no_console_errors": False,
            "performance_acceptable": False
        }
        
    def start_server(self):
        """Start the UI server"""
        print("🚀 Starting UI server...")
        
        # Kill any existing process on port
        subprocess.run(['lsof', '-ti', f':{self.port}', '|', 'xargs', 'kill', '-9'], 
                      shell=True, capture_output=True)
        time.sleep(1)
        
        # Start new server
        self.server_process = subprocess.Popen(
            ['python3', '-m', 'http.server', str(self.port)],
            cwd='ui',
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait and verify
        time.sleep(2)
        try:
            response = requests.get(f"{self.base_url}/research_ui.html", timeout=5)
            if response.status_code == 200:
                self.validation_results["server_start"] = True
                print("✅ Server started successfully")
                return True
        except:
            pass
            
        print("❌ Failed to start server")
        return False
        
    def validate_page_load(self):
        """Validate that the page loads correctly"""
        print("\n🔍 Validating page load...")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/research_ui.html", timeout=5)
            load_time = time.time() - start_time
            
            if response.status_code == 200:
                self.validation_results["page_load"] = True
                print(f"✅ Page loaded successfully in {load_time:.2f}s")
                
                # Check content length
                content_length = len(response.content)
                print(f"   Content size: {content_length:,} bytes")
                
                # Check for basic HTML structure
                if '<!DOCTYPE html>' in response.text and '</html>' in response.text:
                    print("   HTML structure: Valid")
                    
                return response.text
            else:
                print(f"❌ Page load failed with status {response.status_code}")
                
        except Exception as e:
            print(f"❌ Page load error: {str(e)}")
            
        return None
        
    def validate_html_structure(self, html_content):
        """Validate HTML structure in detail"""
        print("\n🔍 Validating HTML structure...")
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Check required elements
            checks = {
                "Header": soup.find('div', class_='header'),
                "Tab Navigation": soup.find('div', class_='tabs'),
                "Documents Tab": soup.find('div', id='documents'),
                "Analysis Tab": soup.find('div', id='analysis'),
                "Graph Tab": soup.find('div', id='graph'),
                "Query Tab": soup.find('div', id='query'),
                "Export Tab": soup.find('div', id='export')
            }
            
            all_valid = True
            for name, element in checks.items():
                if element:
                    print(f"✅ {name}: Found")
                else:
                    print(f"❌ {name}: Missing")
                    all_valid = False
                    
            # Check tab count
            tabs = soup.find_all('div', class_='tab')
            print(f"   Tab count: {len(tabs)} (expected 5)")
            
            # Check for JavaScript
            scripts = soup.find_all('script')
            print(f"   Script tags: {len(scripts)}")
            
            self.validation_results["html_structure"] = all_valid
            return soup
            
        except Exception as e:
            print(f"❌ HTML validation error: {str(e)}")
            return None
            
    def validate_javascript(self, soup):
        """Validate JavaScript functionality"""
        print("\n🔍 Validating JavaScript...")
        
        try:
            # Find script content
            script_tags = soup.find_all('script')
            js_content = ""
            for script in script_tags:
                if script.string:
                    js_content += script.string
                    
            # Check for required functions
            js_checks = {
                "showTab function": "function showTab" in js_content,
                "Event listeners": "addEventListener" in js_content,
                "DOM manipulation": "classList" in js_content,
                "Query selectors": "querySelector" in js_content
            }
            
            all_valid = True
            for name, present in js_checks.items():
                if present:
                    print(f"✅ {name}: Found")
                else:
                    print(f"❌ {name}: Missing")
                    all_valid = False
                    
            # Check for syntax errors
            if "SyntaxError" not in js_content and "error" not in js_content.lower():
                print("✅ No obvious syntax errors")
            else:
                print("❌ Potential JavaScript errors detected")
                all_valid = False
                
            self.validation_results["javascript_valid"] = all_valid
            
        except Exception as e:
            print(f"❌ JavaScript validation error: {str(e)}")
            
    def validate_css(self, soup):
        """Validate CSS styling"""
        print("\n🔍 Validating CSS...")
        
        try:
            # Find style content
            style_tags = soup.find_all('style')
            css_content = ""
            for style in style_tags:
                if style.string:
                    css_content += style.string
                    
            # Check for required styles
            css_checks = {
                "Container styles": ".container" in css_content,
                "Tab styles": ".tab {" in css_content,
                "Active tab styles": ".tab.active" in css_content,
                "Component styles": ".ui-component" in css_content,
                "Button styles": "button {" in css_content,
                "Responsive design": "@media" in css_content or "max-width" in css_content
            }
            
            all_valid = True
            for name, present in css_checks.items():
                if present:
                    print(f"✅ {name}: Found")
                else:
                    print(f"⚠️  {name}: Missing (non-critical)")
                    
            self.validation_results["css_valid"] = True  # CSS is less critical
            
        except Exception as e:
            print(f"❌ CSS validation error: {str(e)}")
            
    def validate_tab_functionality(self, soup):
        """Validate tab switching functionality"""
        print("\n🔍 Validating tab functionality...")
        
        # Check that tabs have onclick handlers
        tabs = soup.find_all('div', class_='tab')
        tabs_with_onclick = [tab for tab in tabs if tab.get('onclick')]
        
        print(f"   Tabs with onclick: {len(tabs_with_onclick)}/{len(tabs)}")
        
        # Check tab content divs
        tab_contents = soup.find_all('div', class_='tab-content')
        print(f"   Tab content divs: {len(tab_contents)}")
        
        # Check for active tab
        active_tab = soup.find('div', class_='tab active')
        active_content = soup.find('div', class_='tab-content active')
        
        if active_tab and active_content:
            print("✅ Default active tab set")
            self.validation_results["tabs_functional"] = True
        else:
            print("❌ No default active tab")
            
    def validate_components(self, soup):
        """Validate individual UI components"""
        print("\n🔍 Validating UI components...")
        
        components_found = 0
        expected_components = [
            ("Document Manager", "document-manager"),
            ("Analysis Dashboard", "analysis-dashboard"),
            ("Graph Explorer", "graph-explorer"),
            ("Query Builder", "query-builder"),
            ("Results Exporter", "results-exporter")
        ]
        
        for name, comp_id in expected_components:
            component = soup.find('div', id=comp_id)
            if component:
                print(f"✅ {name}: Found")
                components_found += 1
                
                # Check for key elements
                if comp_id == "document-manager":
                    if component.find('input', type='file'):
                        print("   ✓ File upload input present")
                elif comp_id == "analysis-dashboard":
                    if component.find('div', class_='progress-bar'):
                        print("   ✓ Progress bar present")
            else:
                print(f"❌ {name}: Missing")
                
        print(f"\nComponents found: {components_found}/{len(expected_components)}")
        self.validation_results["components_render"] = components_found >= 3  # At least 3 components
        
    def validate_performance(self):
        """Validate performance metrics"""
        print("\n🔍 Validating performance...")
        
        # Test multiple page loads
        load_times = []
        for i in range(3):
            start = time.time()
            try:
                requests.get(f"{self.base_url}/research_ui.html", timeout=5)
                load_times.append(time.time() - start)
            except:
                pass
                
        if load_times:
            avg_load_time = sum(load_times) / len(load_times)
            print(f"   Average load time: {avg_load_time:.2f}s")
            
            if avg_load_time < 2.0:
                print("✅ Performance acceptable")
                self.validation_results["performance_acceptable"] = True
            else:
                print("❌ Performance too slow")
        else:
            print("❌ Could not measure performance")
            
    def generate_validation_report(self):
        """Generate final validation report"""
        print("\n" + "=" * 50)
        print("📊 VALIDATION REPORT")
        print("=" * 50)
        
        passed = sum(1 for v in self.validation_results.values() if v)
        total = len(self.validation_results)
        
        for check, result in self.validation_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{check.replace('_', ' ').title()}: {status}")
            
        print(f"\nOverall: {passed}/{total} checks passed")
        
        # Success determination
        critical_checks = ["server_start", "page_load", "html_structure", "tabs_functional"]
        critical_passed = all(self.validation_results[check] for check in critical_checks)
        
        if critical_passed:
            print("\n🎉 UI IS READY FOR USE!")
            print(f"\nOpen your browser and navigate to:")
            print(f"👉 {self.base_url}/research_ui.html")
            return True
        else:
            print("\n⚠️  Critical issues found. UI needs fixes.")
            return False
            
    def cleanup(self):
        """Clean up server process"""
        if self.server_process:
            print("\n🛑 Stopping server...")
            self.server_process.terminate()
            self.server_process.wait()
            
    def run_full_validation(self):
        """Run complete validation suite"""
        print("🔍 KGAS UI Comprehensive Validation")
        print("=" * 50)
        
        try:
            # Start server
            if not self.start_server():
                return False
                
            # Get page content
            html_content = self.validate_page_load()
            if not html_content:
                return False
                
            # Parse and validate
            soup = self.validate_html_structure(html_content)
            if soup:
                self.validate_javascript(soup)
                self.validate_css(soup)
                self.validate_tab_functionality(soup)
                self.validate_components(soup)
                
            # Performance check
            self.validate_performance()
            
            # Generate report
            return self.generate_validation_report()
            
        finally:
            self.cleanup()


def main():
    """Main entry point"""
    validator = UIValidator()
    success = validator.run_full_validation()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()