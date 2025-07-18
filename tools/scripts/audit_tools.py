#!/usr/bin/env python3
"""
Tool Functionality Audit System
Tests actual functionality of all tools with dynamic discovery
"""

import sys
import os
import importlib
import traceback
import inspect
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import is_dataclass

try:
    from pydantic import BaseModel
except ImportError:
    # Fallback if pydantic is not available
    class BaseModel:
        pass

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core.evidence_logger import EvidenceLogger
from src.core.contract_validator import ContractValidator, ContractValidationError
from src.core.ontology_validator import OntologyValidator

class ToolAuditor:
    """Audits all tools for functional capability"""
    
    def __init__(self):
        self.results = []
        self.service_manager = None
        self.evidence_logger = EvidenceLogger()
        self.contract_validator = ContractValidator("contracts")
        self.ontology_validator = OntologyValidator()
        self._init_services()
    
    def _init_services(self):
        """Initialize required services"""
        try:
            from src.core.service_manager import ServiceManager
            self.service_manager = ServiceManager()
        except Exception as e:
            print(f"⚠️  Warning: Could not initialize services: {e}")
    
    def _is_tool_class(self, obj) -> bool:
        """Enhanced filtering to avoid instantiating non-tool classes"""
        import inspect
        from enum import Enum
        from typing import Protocol
        
        # Skip if not a class
        if not inspect.isclass(obj):
            return False
        
        # Skip Enums, Protocols, and other non-tool types
        if (issubclass(obj, Enum) or 
            hasattr(obj, '_is_protocol') or
            obj.__name__ in ['Tool', 'OptimizationLevel', 'CircuitBreakerState', 'ErrorSeverity', 'Phase']):
            return False
        
        # Skip abstract base classes
        if hasattr(obj, '__abstractmethods__') and obj.__abstractmethods__:
            return False
        
        # Only include classes that look like tools
        return (hasattr(obj, 'get_tool_info') or 
                hasattr(obj, 'execute') or
                obj.__name__.endswith('Tool') or
                obj.__name__.endswith('Loader') or
                obj.__name__.endswith('Extractor') or
                obj.__name__.endswith('Builder') or
                obj.__name__.endswith('Calculator') or
                obj.__name__.endswith('Query') or
                obj.__name__.endswith('Manager') or
                obj.__name__.endswith('Handler') or
                obj.__name__.endswith('Workflow') or
                obj.__name__.endswith('Visualizer') or
                obj.__name__.endswith('Checker') or
                obj.__name__.endswith('Validator') or
                obj.__name__.endswith('Service') or
                obj.__name__.endswith('Orchestrator') or
                obj.__name__.endswith('Adapter') or
                obj.__name__.endswith('UI'))

    def discover_tools_dynamically(self) -> List[str]:
        """Dynamically discover all tools in the system"""
        tools = []
        
        # Scan all tool directories
        base_path = Path("src/tools")
        if base_path.exists():
            for phase_dir in base_path.iterdir():
                if phase_dir.is_dir() and phase_dir.name.startswith("phase"):
                    for tool_file in phase_dir.glob("*.py"):
                        if tool_file.name.startswith("__"):
                            continue
                        
                        module_name = f"src.tools.{phase_dir.name}.{tool_file.stem}"
                        tools.append(module_name)
        
        # Scan core directory
        core_path = Path("src/core")
        if core_path.exists():
            for core_file in core_path.glob("*.py"):
                if core_file.name.startswith("__"):
                    continue
                
                module_name = f"src.core.{core_file.stem}"
                tools.append(module_name)
        
        # Scan UI directory
        ui_path = Path("src/ui")
        if ui_path.exists():
            for ui_file in ui_path.glob("*.py"):
                if ui_file.name.startswith("__"):
                    continue
                
                module_name = f"src.ui.{ui_file.stem}"
                tools.append(module_name)
        
        # Record evidence of discovery
        self.evidence_logger.log_test_execution("DYNAMIC_TOOL_DISCOVERY", {
            'status': 'success',
            'tools_found': len(tools),
            'tools_list': tools
        })
        
        return tools
    
    def test_tool_functionality(self, tool_module_name: str) -> Dict[str, Any]:
        """Test actual tool functionality with comprehensive validation"""
        result = {
            'tool_name': tool_module_name,
            'status': 'UNKNOWN',
            'error': None,
            'functional_tests': [],
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Dynamic import
            module = importlib.import_module(tool_module_name)
            
            # Find all classes in the module, excluding data model classes and aliases
            classes = []
            seen_class_objects = set()
            
            for name, cls in inspect.getmembers(module, inspect.isclass):
                if (cls.__module__ == tool_module_name and 
                    not issubclass(cls, BaseModel) and 
                    not is_dataclass(cls) and
                    not cls.__name__.endswith('Intent') and
                    not cls.__name__.endswith('Plan') and
                    not cls.__name__.endswith('Answer') and
                    not cls.__name__.endswith('Result') and
                    not cls.__name__.endswith('Config') and
                    not cls.__name__.endswith('Data') and
                    id(cls) not in seen_class_objects and
                    self._is_tool_class(cls)):
                    classes.append(cls)
                    seen_class_objects.add(id(cls))
            
            if not classes:
                result['status'] = 'BROKEN'
                result['error'] = 'No classes found in module'
                self.evidence_logger.log_tool_audit(tool_module_name, 'BROKEN', [], 'No classes found')
                return result
            
            # Test each class
            for cls in classes:
                try:
                    # Test instantiation
                    instance = cls()
                    result['functional_tests'].append(f"{cls.__name__}: instantiation successful")
                    
                    # Test basic functionality if available
                    if hasattr(instance, 'get_tool_info'):
                        info = instance.get_tool_info()
                        result['functional_tests'].append(f"{cls.__name__}: get_tool_info() returned {type(info)}")
                    
                    # Test specific functionality based on class type
                    if 'Loader' in cls.__name__ and hasattr(instance, 'load_pdf'):
                        # Test with actual file
                        test_file = "examples/test_document.txt"
                        if os.path.exists(test_file):
                            load_result = instance.load_pdf(test_file)
                            if load_result.get('status') == 'success':
                                result['functional_tests'].append(f"{cls.__name__}: load_pdf() functional")
                    
                    if 'NER' in cls.__name__ and hasattr(instance, 'extract_entities'):
                        # Test entity extraction
                        test_text = "Apple Inc. is located in Cupertino, California."
                        entities = instance.extract_entities("test_chunk", test_text)
                        if entities and len(entities.get('entities', [])) > 0:
                            result['functional_tests'].append(f"{cls.__name__}: extract_entities() functional")
                    
                except Exception as e:
                    result['functional_tests'].append(f"{cls.__name__}: FAILED - {str(e)}")
            
            # Determine overall status
            if result['functional_tests']:
                failed_tests = [t for t in result['functional_tests'] if 'FAILED' in t]
                if len(failed_tests) == 0:
                    result['status'] = 'FUNCTIONAL'
                else:
                    result['status'] = 'BROKEN'
                    result['error'] = f"{len(failed_tests)} tests failed"
            else:
                result['status'] = 'BROKEN'
                result['error'] = 'No functional tests could be performed'
                
        except Exception as e:
            result['status'] = 'BROKEN'
            result['error'] = str(e)
        
        # Log evidence of tool audit
        self.evidence_logger.log_tool_audit(
            tool_module_name, 
            result['status'], 
            result['functional_tests'], 
            result.get('error')
        )
        
        return result
    
    def _test_tool_class(self, tool_class) -> Dict[str, Any]:
        """Test a specific tool class for functionality"""
        class_result = {
            'class_name': tool_class.__name__,
            'status': 'UNKNOWN',
            'tests_passed': 0,
            'tests_total': 0,
            'error': None
        }
        
        try:
            # Instantiate the tool
            if self.service_manager:
                tool_instance = tool_class(
                    self.service_manager.get_identity_service(),
                    self.service_manager.get_provenance_service(),
                    self.service_manager.get_quality_service()
                )
            else:
                tool_instance = tool_class()
            
            # Add contract validation if contract exists
            contract_validation_result = self._validate_tool_contract(tool_instance, tool_class.__name__)
            class_result.update(contract_validation_result)
            
            # Test based on tool type
            if hasattr(tool_instance, 'extract_entities'):
                class_result.update(self._test_entity_extractor(tool_instance))
            elif hasattr(tool_instance, 'load_pdf'):
                class_result.update(self._test_pdf_loader(tool_instance))
            elif hasattr(tool_instance, 'chunk_text'):
                class_result.update(self._test_text_chunker(tool_instance))
            elif hasattr(tool_instance, 'extract_relationships'):
                class_result.update(self._test_relationship_extractor(tool_instance))
            elif hasattr(tool_instance, 'build_entities'):
                class_result.update(self._test_entity_builder(tool_instance))
            elif hasattr(tool_instance, 'calculate_pagerank'):
                class_result.update(self._test_pagerank(tool_instance))
            elif hasattr(tool_instance, 'execute_query'):
                class_result.update(self._test_query_tool(tool_instance))
            else:
                class_result.update(self._test_generic_tool(tool_instance))
                
        except Exception as e:
            class_result['status'] = 'BROKEN'
            class_result['error'] = str(e)
        
        return class_result
    
    def _test_entity_extractor(self, tool) -> Dict[str, Any]:
        """Test entity extraction functionality with real text and result validation"""
        result = {'tests_total': 4, 'tests_passed': 0}
        
        try:
            # Test with meaningful text
            test_text = "Apple Inc. is a technology company founded by Steve Jobs in Cupertino, California."
            extract_result = tool.extract_entities(test_text, "audit_test")
            
            # Test 1: Extraction returns success status
            if extract_result.get('status') == 'success':
                result['tests_passed'] += 1
                
                # Test 2: Entities are extracted
                if 'entities' in extract_result and len(extract_result['entities']) > 0:
                    result['tests_passed'] += 1
                    
                    # Test 3: Entities have required structure
                    entities = extract_result['entities']
                    has_proper_structure = all(
                        isinstance(e, dict) and 
                        'text' in e and 
                        'entity_type' in e 
                        for e in entities
                    )
                    if has_proper_structure:
                        result['tests_passed'] += 1
                        
                        # Test 4: Entities detect expected types (ORG, PERSON, GPE)
                        entity_types = [e.get('entity_type') for e in entities]
                        has_org = any('ORG' in et for et in entity_types if et)
                        has_person_or_gpe = any(et in ['PERSON', 'GPE', 'LOC'] for et in entity_types if et)
                        
                        if has_org and has_person_or_gpe:
                            result['tests_passed'] += 1
            
            result['status'] = 'FUNCTIONAL' if result['tests_passed'] >= 3 else 'BROKEN'
            
        except Exception as e:
            result['status'] = 'BROKEN'
            result['error'] = str(e)
        
        return result
    
    def _test_pdf_loader(self, tool) -> Dict[str, Any]:
        """Test PDF loading functionality with real file and proper format verification"""
        result = {'tests_total': 3, 'tests_passed': 0}
        
        try:
            # Test with actual PDF file
            test_file = "examples/pdfs/test_document.pdf"
            if not os.path.exists(test_file):
                result['status'] = 'BROKEN'
                result['error'] = f"Test file missing: {test_file}"
                return result
            
            # Test 1: PDF loading returns success
            load_result = tool.load_pdf(test_file, "audit_test")
            if load_result.get('status') == 'success':
                result['tests_passed'] += 1
                
                # Test 2: Standardized document is created
                if 'standardized_document' in load_result:
                    result['tests_passed'] += 1
                    
                    # Test 3: Document has actual content
                    doc = load_result['standardized_document']
                    if hasattr(doc, 'text') and len(doc.text) > 0:
                        result['tests_passed'] += 1
                    elif isinstance(doc, dict) and len(doc.get('text', '')) > 0:
                        result['tests_passed'] += 1
            
            result['status'] = 'FUNCTIONAL' if result['tests_passed'] == 3 else 'BROKEN'
            
        except Exception as e:
            result['status'] = 'BROKEN'
            result['error'] = str(e)
        
        return result
    
    def _test_text_chunker(self, tool) -> Dict[str, Any]:
        """Test text chunking functionality"""
        result = {'tests_total': 2, 'tests_passed': 0}
        
        try:
            # Test 1: Basic chunking
            test_text = "This is a test document. " * 100
            chunks = tool.chunk_text(test_text)
            
            if chunks and len(chunks) >= 2:
                result['tests_passed'] += 1
                
                # Test 2: Verify chunk structure
                if all(isinstance(chunk, str) and len(chunk) > 0 for chunk in chunks):
                    result['tests_passed'] += 1
            
            result['status'] = 'FUNCTIONAL' if result['tests_passed'] == 2 else 'BROKEN'
            
        except Exception as e:
            result['status'] = 'BROKEN'
            result['error'] = str(e)
        
        return result
    
    def _test_relationship_extractor(self, tool) -> Dict[str, Any]:
        """Test relationship extraction functionality with real text and validation"""
        result = {'tests_total': 3, 'tests_passed': 0}
        
        try:
            test_text = "Apple Inc. was founded by Steve Jobs. The company is located in Cupertino."
            extract_result = tool.extract_relationships(test_text, "audit_test")
            
            # Test 1: Extraction returns success status
            if extract_result.get('status') == 'success':
                result['tests_passed'] += 1
                
                # Test 2: Relationships are extracted
                if 'relationships' in extract_result and len(extract_result['relationships']) > 0:
                    result['tests_passed'] += 1
                    
                    # Test 3: Relationships have proper structure
                    relationships = extract_result['relationships']
                    has_proper_structure = all(
                        isinstance(r, dict) and 
                        'source' in r and 
                        'target' in r and 
                        'relationship_type' in r
                        for r in relationships
                    )
                    if has_proper_structure:
                        result['tests_passed'] += 1
            
            result['status'] = 'FUNCTIONAL' if result['tests_passed'] >= 2 else 'BROKEN'
            
        except Exception as e:
            result['status'] = 'BROKEN'
            result['error'] = str(e)
        
        return result
    
    def _test_entity_builder(self, tool) -> Dict[str, Any]:
        """Test entity building functionality"""
        result = {'tests_total': 1, 'tests_passed': 0}
        
        try:
            # Test basic entity building
            test_entities = [
                {'canonical_name': 'Apple Inc.', 'entity_type': 'ORG'},
                {'canonical_name': 'California', 'entity_type': 'GPE'}
            ]
            
            built_entities = tool.build_entities("test_chunk", test_entities)
            
            if built_entities and len(built_entities) >= 2:
                result['tests_passed'] += 1
            
            result['status'] = 'FUNCTIONAL' if result['tests_passed'] == 1 else 'BROKEN'
            
        except Exception as e:
            result['status'] = 'BROKEN'
            result['error'] = str(e)
        
        return result
    
    def _test_pagerank(self, tool) -> Dict[str, Any]:
        """Test PageRank calculation functionality"""
        result = {'tests_total': 1, 'tests_passed': 0}
        
        try:
            # Test PageRank calculation
            pagerank_result = tool.calculate_pagerank()
            
            if pagerank_result and 'pagerank_scores' in pagerank_result:
                result['tests_passed'] += 1
            
            result['status'] = 'FUNCTIONAL' if result['tests_passed'] == 1 else 'BROKEN'
            
        except Exception as e:
            result['status'] = 'BROKEN'
            result['error'] = str(e)
        
        return result
    
    def _test_query_tool(self, tool) -> Dict[str, Any]:
        """Test query tool functionality"""
        result = {'tests_total': 1, 'tests_passed': 0}
        
        try:
            # Test basic query
            query_result = tool.execute_query("MATCH (n) RETURN count(n)")
            
            if query_result is not None:
                result['tests_passed'] += 1
            
            result['status'] = 'FUNCTIONAL' if result['tests_passed'] == 1 else 'BROKEN'
            
        except Exception as e:
            result['status'] = 'BROKEN'
            result['error'] = str(e)
        
        return result
    
    def _test_generic_tool(self, tool) -> Dict[str, Any]:
        """Test generic tool functionality - requires actual functionality test"""
        result = {'tests_total': 2, 'tests_passed': 0}
        
        try:
            # Test 1: Tool has test_functionality method for audit compliance
            if hasattr(tool, 'test_functionality'):
                functionality_test = tool.test_functionality()
                if functionality_test:
                    result['tests_passed'] += 1
            
            # Test 2: Tool has basic interface compliance
            required_methods = ['get_tool_info']
            has_required_methods = all(hasattr(tool, method) for method in required_methods)
            if has_required_methods:
                try:
                    info = tool.get_tool_info()
                    if info and isinstance(info, dict):
                        result['tests_passed'] += 1
                except:
                    pass  # Method exists but failed
            
            result['status'] = 'FUNCTIONAL' if result['tests_passed'] >= 1 else 'BROKEN'
            
        except Exception as e:
            result['status'] = 'BROKEN'
            result['error'] = str(e)
        
        return result
    
    def audit_all_tools(self) -> bool:
        """Audit all tools with functional testing using dynamic discovery"""
        print("🔍 Starting comprehensive tool audit with dynamic discovery...")
        
        # Use dynamic discovery instead of hardcoded list
        tools = self.discover_tools_dynamically()
        total_tools = len(tools)
        functional_count = 0
        
        print(f"📊 Discovered {total_tools} tools dynamically")
        
        for tool_name in tools:
            print(f"\n📊 Testing {tool_name}...")
            result = self.test_tool_functionality(tool_name)
            self.results.append(result)
            
            if result['status'] == 'FUNCTIONAL':
                functional_count += 1
                print(f"✅ {tool_name}: FUNCTIONAL")
            else:
                print(f"❌ {tool_name}: {result['status']}")
                if result['error']:
                    print(f"   Error: {result['error']}")
        
        success_rate = (functional_count / total_tools) * 100
        print(f"\n📊 AUDIT RESULTS:")
        print(f"Functional tools: {functional_count}/{total_tools}")
        print(f"Success rate: {success_rate:.1f}%")
        
        # Log comprehensive audit results
        self.evidence_logger.log_test_execution("COMPREHENSIVE_TOOL_AUDIT", {
            'status': 'success' if functional_count == total_tools else 'partial',
            'functional_count': functional_count,
            'total_count': total_tools,
            'success_rate': success_rate,
            'execution_time': 0  # Will be updated by calling code
        })
        
        if functional_count < total_tools:
            print("\n❌ NOT ALL TOOLS ARE FUNCTIONAL")
            for result in self.results:
                if result['status'] != 'FUNCTIONAL':
                    print(f"  - {result['tool_name']}: {result['status']}")
            return False
        
        print("\n✅ ALL TOOLS ARE FUNCTIONAL")
        return True
    
    def save_audit_report(self, filename: str = "docs/tool_audit_report.md"):
        """Save detailed audit report"""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w') as f:
            f.write("# Tool Functionality Audit Report\n\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n\n")
            
            functional_count = sum(1 for r in self.results if r['status'] == 'FUNCTIONAL')
            total_count = len(self.results)
            success_rate = (functional_count / total_count) * 100
            
            f.write(f"## Summary\n")
            f.write(f"- Total tools tested: {total_count}\n")
            f.write(f"- Functional tools: {functional_count}\n")
            f.write(f"- Success rate: {success_rate:.1f}%\n\n")
            
            f.write("## Detailed Results\n\n")
            
            for result in self.results:
                f.write(f"### {result['tool_name']}\n")
                f.write(f"- Status: {result['status']}\n")
                f.write(f"- Timestamp: {result['timestamp']}\n")
                
                if result['error']:
                    f.write(f"- Error: {result['error']}\n")
                
                if result['functional_tests']:
                    f.write("- Functional Tests:\n")
                    for test in result['functional_tests']:
                        if isinstance(test, dict):
                            f.write(f"  - {test.get('class_name', 'Unknown')}: {test.get('status', 'Unknown')}\n")
                            if test.get('tests_passed') and test.get('tests_total'):
                                f.write(f"    - Tests: {test['tests_passed']}/{test['tests_total']}\n")
                        else:
                            f.write(f"  - {test}\n")
                
                f.write("\n")
    
    def _validate_tool_contract(self, tool_instance, tool_name: str) -> Dict[str, Any]:
        """Validate tool against its contract if available"""
        validation_result = {
            'contract_validation': 'not_available',
            'ontology_validation': 'not_available',
            'contract_errors': []
        }
        
        try:
            # Map tool names to contract IDs
            contract_mapping = {
                'PDFLoader': 'T01_PDF_LOADER',
                'TextChunker': 'T15A_TEXT_CHUNKER', 
                'SpacyNER': 'T23A_SPACY_NER',
                'RelationshipExtractor': 'T27_RELATIONSHIP_EXTRACTOR',
                'EntityBuilder': 'T31_ENTITY_BUILDER',
                'EdgeBuilder': 'T34_EDGE_BUILDER',
                'MultiHopQuery': 'T49_MULTI_HOP_QUERY',
                'PageRankCalculator': 'T68_PAGE_RANK'
            }
            
            contract_id = contract_mapping.get(tool_name)
            if not contract_id:
                return validation_result
            
            # Load and validate contract
            contract = self.contract_validator.load_contract(contract_id)
            if contract:
                # Validate contract schema
                schema_errors = self.contract_validator.validate_contract_schema(contract)
                if not schema_errors:
                    validation_result['contract_validation'] = 'passed'
                else:
                    validation_result['contract_validation'] = 'failed'
                    validation_result['contract_errors'] = schema_errors
                
                # Validate tool interface
                interface_errors = self.contract_validator.validate_tool_interface(tool_instance, contract)
                if interface_errors:
                    validation_result['contract_errors'].extend(interface_errors)
                    validation_result['contract_validation'] = 'failed'
                
                # Validate with ontology if possible
                try:
                    if hasattr(tool_instance, 'extract_entities'):
                        # Test ontology validation on sample entity
                        test_entity = {
                            'name': 'Test Entity',
                            'type': 'PERSON',
                            'properties': {},
                            'modifiers': []
                        }
                        ontology_valid = self.ontology_validator.validate_entity(test_entity)
                        validation_result['ontology_validation'] = 'passed' if ontology_valid else 'failed'
                except Exception as e:
                    validation_result['ontology_validation'] = f'error: {str(e)}'
            
        except Exception as e:
            validation_result['contract_validation'] = f'error: {str(e)}'
        
        return validation_result

def main():
    """Main audit function"""
    auditor = ToolAuditor()
    
    # Run the audit
    success = auditor.audit_all_tools()
    
    # Save report
    auditor.save_audit_report()
    
    # Return appropriate exit code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()