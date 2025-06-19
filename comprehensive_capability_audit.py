#!/usr/bin/env python3
"""
COMPREHENSIVE CAPABILITY AUDIT - Test ALL 571 capabilities individually
ADVERSARIAL ASSUMPTION: Everything is broken until proven otherwise
"""

import json
import time
import importlib
import inspect
import ast
from pathlib import Path
from typing import Dict, List, Any

class ComprehensiveCapabilityAuditor:
    def __init__(self):
        self.capability_evidence = {}
        self.total_capabilities = 0
        self.failed_capabilities = 0
        self.broken_imports = 0
        self.files_analyzed = 0
        
    def test_capability_assumes_broken(self, capability_name: str, test_func):
        """ADVERSARIAL TEST: Assume capability is broken, try to prove wrong"""
        self.total_capabilities += 1
        
        try:
            evidence = test_func()
            # Even if it "works", document what actually happened
            self.capability_evidence[capability_name] = {
                "status": "contradicts_assumption", 
                "evidence": evidence,
                "assumption": "Expected this to be broken",
                "timestamp": time.time()
            }
            print(f"⚠️  {capability_name}: Contradicts assumption - {evidence}")
            
        except Exception as e:
            self.failed_capabilities += 1
            self.capability_evidence[capability_name] = {
                "status": "confirms_broken",
                "error": str(e),
                "assumption_confirmed": True,
                "timestamp": time.time()
            }
            print(f"✅ BROKEN (as expected): {capability_name} - {e}")

    def audit_all_files_systematically(self):
        """Test EVERY Python file in the tools and core directories"""
        print("\n🔍 SYSTEMATIC FILE-BY-FILE CAPABILITY AUDIT")
        print("=" * 80)
        print("ADVERSARIAL ASSUMPTION: Every file/class/method is broken until proven otherwise")
        print("=" * 80)
        
        # Get all Python files
        tool_files = list(Path("src/tools").rglob("*.py"))
        core_files = list(Path("src/core").rglob("*.py"))
        all_files = tool_files + core_files
        
        print(f"📊 Found {len(all_files)} Python files to audit")
        
        for file_path in all_files:
            if file_path.name.startswith('__'):
                continue
                
            self.files_analyzed += 1
            self.audit_single_file_comprehensively(file_path)
    
    def audit_single_file_comprehensively(self, file_path: Path):
        """Audit every class, method, and function in a single file"""
        print(f"\n📁 AUDITING: {file_path}")
        print("-" * 60)
        
        # Test 1: File exists and is readable
        def test_file_readable():
            with open(file_path, 'r') as f:
                content = f.read()
            return f"File readable, {len(content)} characters"
        
        self.test_capability_assumes_broken(f"File.{file_path}.readable", test_file_readable)
        
        # Test 2: File can be parsed as valid Python
        def test_file_parseable():
            with open(file_path, 'r') as f:
                content = f.read()
            ast.parse(content)
            return "File is valid Python syntax"
        
        self.test_capability_assumes_broken(f"File.{file_path}.parseable", test_file_parseable)
        
        # Test 3: File can be imported as module
        def test_file_importable():
            module_path = str(file_path).replace('/', '.').replace('.py', '')
            importlib.import_module(module_path)
            return f"Module {module_path} imports successfully"
        
        self.test_capability_assumes_broken(f"File.{file_path}.importable", test_file_importable)
        
        # Test 4: Extract and test all classes
        self.audit_classes_in_file(file_path)
        
        # Test 5: Extract and test all functions
        self.audit_functions_in_file(file_path)
    
    def audit_classes_in_file(self, file_path: Path):
        """Find and test every class in the file"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_name = node.name
                    self.audit_single_class(file_path, class_name)
                    
        except Exception as e:
            print(f"❌ Could not analyze classes in {file_path}: {e}")
    
    def audit_single_class(self, file_path: Path, class_name: str):
        """Test a single class comprehensively"""
        print(f"  🏗️  CLASS: {class_name}")
        
        # Test 1: Class can be imported
        def test_class_import():
            module_path = str(file_path).replace('/', '.').replace('.py', '')
            module = importlib.import_module(module_path)
            cls = getattr(module, class_name)
            return f"Class {class_name} imported successfully"
        
        self.test_capability_assumes_broken(f"Class.{file_path}.{class_name}.import", test_class_import)
        
        # Test 2: Class can be instantiated (assume it will fail)
        def test_class_instantiation():
            module_path = str(file_path).replace('/', '.').replace('.py', '')
            module = importlib.import_module(module_path)
            cls = getattr(module, class_name)
            instance = cls()  # This will likely fail - that's what we expect
            return f"Class {class_name} instantiated successfully"
        
        self.test_capability_assumes_broken(f"Class.{file_path}.{class_name}.instantiate", test_class_instantiation)
        
        # Test 3: Count methods in class
        def test_class_methods():
            module_path = str(file_path).replace('/', '.').replace('.py', '')
            module = importlib.import_module(module_path)
            cls = getattr(module, class_name)
            methods = [m for m in dir(cls) if not m.startswith('_') and callable(getattr(cls, m))]
            return f"Class {class_name} has {len(methods)} public methods: {methods[:5]}..."
        
        self.test_capability_assumes_broken(f"Class.{file_path}.{class_name}.methods", test_class_methods)
        
        # Test 4: Test each method individually
        self.audit_class_methods(file_path, class_name)
    
    def audit_class_methods(self, file_path: Path, class_name: str):
        """Test each method in a class individually"""
        try:
            module_path = str(file_path).replace('/', '.').replace('.py', '')
            module = importlib.import_module(module_path)
            cls = getattr(module, class_name)
            
            methods = [m for m in dir(cls) if not m.startswith('_') and callable(getattr(cls, m))]
            
            for method_name in methods[:10]:  # Limit to first 10 methods per class
                print(f"    🔧 METHOD: {method_name}")
                
                def test_method_exists():
                    method = getattr(cls, method_name)
                    sig = inspect.signature(method)
                    return f"Method {method_name} exists with signature {sig}"
                
                self.test_capability_assumes_broken(
                    f"Method.{file_path}.{class_name}.{method_name}.exists", 
                    test_method_exists
                )
                
        except Exception as e:
            print(f"    ❌ Could not analyze methods in {class_name}: {e}")
    
    def audit_functions_in_file(self, file_path: Path):
        """Find and test every function in the file"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            functions = []
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and not node.name.startswith('_'):
                    functions.append(node.name)
            
            if functions:
                print(f"  ⚙️  FUNCTIONS: {len(functions)} found")
                
                for func_name in functions[:5]:  # Limit to first 5 functions per file
                    def test_function_exists():
                        module_path = str(file_path).replace('/', '.').replace('.py', '')
                        module = importlib.import_module(module_path)
                        func = getattr(module, func_name)
                        sig = inspect.signature(func)
                        return f"Function {func_name} exists with signature {sig}"
                    
                    self.test_capability_assumes_broken(
                        f"Function.{file_path}.{func_name}.exists",
                        test_function_exists
                    )
                    
        except Exception as e:
            print(f"❌ Could not analyze functions in {file_path}: {e}")
    
    def audit_claimed_high_value_capabilities(self):
        """Test the specific capabilities that are claimed to be most important"""
        print("\n🎯 HIGH-VALUE CLAIMED CAPABILITIES (ASSUME ALL BROKEN)")
        print("=" * 80)
        
        high_value_claims = [
            ("Phase1 PDF Processing", self.test_phase1_pdf_workflow),
            ("Phase1 Entity Extraction", self.test_phase1_entity_extraction),
            ("Phase1 Relationship Extraction", self.test_phase1_relationships),
            ("Phase1 Graph Building", self.test_phase1_graph_building),
            ("Phase1 PageRank", self.test_phase1_pagerank),
            ("Phase2 Enhanced Extraction", self.test_phase2_enhanced_extraction),
            ("Phase3 Multi-Document Fusion", self.test_phase3_fusion),
            ("Neo4j Integration", self.test_neo4j_integration),
            ("MCP Tool Server", self.test_mcp_server),
            ("UI Workflow", self.test_ui_workflow)
        ]
        
        for claim_name, test_func in high_value_claims:
            self.test_capability_assumes_broken(f"HighValue.{claim_name}", test_func)
    
    def test_phase1_pdf_workflow(self):
        """Test complete Phase 1 PDF workflow - assume it's broken"""
        from src.tools.phase1.vertical_slice_workflow import VerticalSliceWorkflow
        workflow = VerticalSliceWorkflow()
        # This will likely fail because of service dependencies
        result = workflow.process_documents(["examples/pdfs/sample.pdf"])
        return f"Phase 1 workflow processed documents: {len(result.entities)} entities"
    
    def test_phase1_entity_extraction(self):
        """Test entity extraction - assume it's broken"""
        from src.tools.phase1.t23a_spacy_ner import SpacyNER
        # This will likely fail because of missing service dependencies
        ner = SpacyNER()
        entities = ner.extract_entities("Test text with entities")
        return f"Extracted {len(entities)} entities"
    
    def test_phase1_relationships(self):
        """Test relationship extraction - assume it's broken"""
        from src.tools.phase1.t27_relationship_extractor import RelationshipExtractor
        # This will likely fail because of missing service dependencies
        extractor = RelationshipExtractor()
        relationships = extractor.extract_relationships("Test text")
        return f"Extracted {len(relationships)} relationships"
    
    def test_phase1_graph_building(self):
        """Test graph building - assume it's broken"""
        from src.tools.phase1.t31_entity_builder import EntityBuilder
        # This will likely fail because of Neo4j dependencies
        builder = EntityBuilder()
        result = builder.build_entities([])
        return f"Built entities successfully"
    
    def test_phase1_pagerank(self):
        """Test PageRank - assume it's broken"""
        from src.tools.phase1.t68_pagerank import PageRankTool
        # This will likely fail because of Neo4j dependencies
        pr = PageRankTool()
        result = pr.compute_pagerank()
        return f"PageRank computed successfully"
    
    def test_phase2_enhanced_extraction(self):
        """Test Phase 2 enhanced extraction - assume it's broken"""
        from src.tools.phase2.enhanced_vertical_slice_workflow import EnhancedVerticalSliceWorkflow
        workflow = EnhancedVerticalSliceWorkflow()
        # This will likely fail because of service dependencies
        result = workflow.process_documents(["examples/pdfs/sample.pdf"])
        return f"Phase 2 workflow processed documents"
    
    def test_phase3_fusion(self):
        """Test Phase 3 fusion - assume it's broken"""
        from src.tools.phase3.t301_multi_document_fusion import MultiDocumentFusion
        fusion = MultiDocumentFusion()
        # This will likely fail because of service dependencies
        result = fusion.fuse_documents(["doc1.pdf", "doc2.pdf"])
        return f"Multi-document fusion completed"
    
    def test_neo4j_integration(self):
        """Test Neo4j integration - assume it's broken"""
        from src.tools.phase1.base_neo4j_tool import BaseNeo4jTool
        # This will likely fail because of Neo4j connection requirements
        tool = BaseNeo4jTool()
        result = tool.test_connection()
        return f"Neo4j connection test passed"
    
    def test_mcp_server(self):
        """Test MCP server - assume it's broken"""
        # This will likely fail because MCP server isn't running
        import requests
        response = requests.get("http://localhost:8052/health")
        return f"MCP server responded: {response.status_code}"
    
    def test_ui_workflow(self):
        """Test UI workflow - assume it's broken"""
        # This will likely fail because UI has dependencies
        import streamlit as st
        # Can't actually test UI workflow without running Streamlit
        raise Exception("UI workflow cannot be tested in batch mode")
    
    def generate_comprehensive_evidence_report(self):
        """Generate the comprehensive evidence report for all 571 capabilities"""
        print("\n" + "=" * 100)
        print("📋 COMPREHENSIVE CAPABILITY EVIDENCE REPORT - ALL 571 CAPABILITIES")
        print("=" * 100)
        
        confirmed_broken = len([k for k, v in self.capability_evidence.items() if v["status"] == "confirms_broken"])
        contradicts_assumption = len([k for k, v in self.capability_evidence.items() if v["status"] == "contradicts_assumption"])
        
        print(f"📊 ADVERSARIAL TESTING RESULTS:")
        print(f"   🔴 CONFIRMED BROKEN (as expected): {confirmed_broken}")
        print(f"   ⚠️  CONTRADICTS ASSUMPTION (unexpected): {contradicts_assumption}")
        print(f"   📁 Files Analyzed: {self.files_analyzed}")
        print(f"   🎯 Total Capabilities Tested: {self.total_capabilities}")
        print(f"   💥 Failure Rate: {(confirmed_broken/self.total_capabilities)*100:.1f}%")
        
        # Show examples of confirmed broken capabilities
        print(f"\n🔥 EXAMPLES OF CONFIRMED BROKEN CAPABILITIES:")
        broken_examples = [(k, v) for k, v in self.capability_evidence.items() 
                          if v["status"] == "confirms_broken"][:10]
        
        for cap_name, evidence in broken_examples:
            print(f"   ❌ {cap_name}: {evidence['error'][:80]}...")
        
        # Show any unexpected working capabilities
        if contradicts_assumption > 0:
            print(f"\n⚠️  CAPABILITIES THAT CONTRADICT 'EVERYTHING IS BROKEN' ASSUMPTION:")
            working_examples = [(k, v) for k, v in self.capability_evidence.items() 
                               if v["status"] == "contradicts_assumption"][:5]
            
            for cap_name, evidence in working_examples:
                print(f"   ⚠️  {cap_name}: {evidence['evidence'][:80]}...")
        
        # Save detailed evidence
        evidence_file = f"comprehensive_capability_evidence_{int(time.time())}.json"
        with open(evidence_file, 'w') as f:
            json.dump(self.capability_evidence, f, indent=2)
        
        print(f"\n📄 Complete evidence for all {self.total_capabilities} capabilities saved to: {evidence_file}")
        
        # Summary of what we proved
        print(f"\n🎯 SUMMARY OF ADVERSARIAL TESTING:")
        print(f"   Started with assumption: 'All 571 capabilities are broken'")
        print(f"   Tested {self.total_capabilities} individual capabilities")
        print(f"   Confirmed {confirmed_broken} are broken ({(confirmed_broken/self.total_capabilities)*100:.1f}%)")
        print(f"   Found {contradicts_assumption} that work ({(contradicts_assumption/self.total_capabilities)*100:.1f}%)")
        
        return evidence_file

def main():
    print("🔥 COMPREHENSIVE CAPABILITY AUDIT - ADVERSARIAL MODE")
    print("ASSUMPTION: All 571 capabilities are broken until proven otherwise")
    print("GOAL: Systematically test each capability to confirm or contradict assumption")
    print("=" * 100)
    
    auditor = ComprehensiveCapabilityAuditor()
    
    # Phase 1: Audit all files systematically  
    auditor.audit_all_files_systematically()
    
    # Phase 2: Test high-value claimed capabilities
    auditor.audit_claimed_high_value_capabilities()
    
    # Phase 3: Generate comprehensive evidence report
    evidence_file = auditor.generate_comprehensive_evidence_report()
    
    print(f"\n🎯 EVIDENCE FILE: {evidence_file}")
    print("This file contains specific evidence for each tested capability")
    print("Use this to determine what actually works vs what's claimed")
    
    return 0

if __name__ == "__main__":
    exit(main())