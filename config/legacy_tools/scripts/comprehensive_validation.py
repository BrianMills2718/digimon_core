#!/usr/bin/env python3
"""
Comprehensive System Validation
Uses contract validation, ontology validation, and tool auditing for complete verification
"""

import sys
import os
from datetime import datetime
from typing import Dict, List, Any

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core.evidence_logger import EvidenceLogger
from src.core.contract_validator import ContractValidator, ContractValidationError
from src.core.ontology_validator import OntologyValidator

class ComprehensiveValidator:
    """Complete system validation using all available infrastructure"""
    
    def __init__(self):
        self.evidence_logger = EvidenceLogger()
        self.contract_validator = ContractValidator("contracts")
        self.ontology_validator = OntologyValidator()
        self.results = {}
    
    def run_full_validation(self) -> bool:
        """Run comprehensive validation of the entire system"""
        print("🔍 Starting comprehensive system validation...")
        
        success = True
        
        # 1. Validate all contracts
        print("\n📋 Validating Tool Contracts...")
        contract_result = self._validate_all_contracts()
        if not contract_result['success']:
            success = False
        
        # 2. Validate ontology integrity
        print("\n🧠 Validating Ontology System...")
        ontology_result = self._validate_ontology_system()
        if not ontology_result['success']:
            success = False
        
        # 3. Run enhanced tool audit
        print("\n🔧 Running Enhanced Tool Audit...")
        audit_result = self._run_enhanced_audit()
        if not audit_result['success']:
            success = False
        
        # 4. Test integration scenarios
        print("\n🔗 Testing Integration Scenarios...")
        integration_result = self._test_integration_scenarios()
        if not integration_result['success']:
            success = False
        
        # Log final results
        self._log_comprehensive_results(success, {
            'contracts': contract_result,
            'ontology': ontology_result,
            'audit': audit_result,
            'integration': integration_result
        })
        
        if success:
            print("\n✅ COMPREHENSIVE VALIDATION PASSED")
        else:
            print("\n❌ COMPREHENSIVE VALIDATION FAILED")
        
        return success
    
    def _validate_all_contracts(self) -> Dict[str, Any]:
        """Validate all tool contracts"""
        try:
            # Get all available contracts
            contracts = [
                'T01_PDFLoader',
                'T15A_TextChunker', 
                'T23A_SpacyNER',
                'T27_RelationshipExtractor',
                'T31_EntityBuilder',
                'T34_EdgeBuilder',
                'T49_MultiHopQuery',
                'T68_PageRank'
            ]
            
            valid_contracts = 0
            total_contracts = len(contracts)
            validation_errors = []
            
            for contract_id in contracts:
                try:
                    contract = self.contract_validator.load_contract(contract_id)
                    if contract:
                        schema_errors = self.contract_validator.validate_contract_schema(contract)
                        if not schema_errors:
                            valid_contracts += 1
                            print(f"  ✅ {contract_id}: Valid")
                        else:
                            validation_errors.extend(schema_errors)
                            print(f"  ❌ {contract_id}: Schema errors")
                    else:
                        print(f"  ⚠️  {contract_id}: Contract not found")
                except Exception as e:
                    validation_errors.append(f"{contract_id}: {str(e)}")
                    print(f"  ❌ {contract_id}: Error - {e}")
            
            success = valid_contracts == total_contracts
            result = {
                'success': success,
                'valid_contracts': valid_contracts,
                'total_contracts': total_contracts,
                'errors': validation_errors
            }
            
            # Log evidence
            self.evidence_logger.log_test_execution(
                'CONTRACT_VALIDATION_COMPLETE',
                {
                    'status': 'success' if success else 'failed',
                    'details': result,
                    'output': f"Validated {valid_contracts}/{total_contracts} contracts successfully"
                }
            )
            
            return result
            
        except Exception as e:
            result = {
                'success': False,
                'error': str(e)
            }
            
            self.evidence_logger.log_test_execution(
                'CONTRACT_VALIDATION_ERROR',
                {
                    'status': 'error',
                    'error': str(e),
                    'details': result
                }
            )
            
            return result
    
    def _validate_ontology_system(self) -> Dict[str, Any]:
        """Validate the ontology system"""
        try:
            # Test ontology loading
            ontology_service = self.ontology_validator.ontology_service
            
            # Get concept counts
            entities = ontology_service.get_all_entity_types()
            connections = ontology_service.get_all_connection_types()
            properties = ontology_service.get_all_property_types()
            modifiers = ontology_service.get_all_modifier_types()
            
            print(f"  📊 Entities: {len(entities)}")
            print(f"  📊 Connections: {len(connections)}")
            print(f"  📊 Properties: {len(properties)}")
            print(f"  📊 Modifiers: {len(modifiers)}")
            
            # Test entity validation
            test_entity = {
                'name': 'Test Person',
                'type': 'IndividualActor',
                'properties': {},
                'modifiers': []
            }
            
            entity_valid = self.ontology_validator.validate_entity(test_entity)
            
            # Test relationship validation
            test_relationship = {
                'source': 'test_person_1',
                'target': 'test_person_2', 
                'type': 'IdentifiesWith',
                'properties': {},
                'modifiers': []
            }
            
            relationship_valid = self.ontology_validator.validate_relationship(test_relationship)
            
            success = (len(entities) > 0 and len(connections) > 0 and 
                      entity_valid and relationship_valid)
            
            result = {
                'success': success,
                'concept_counts': {
                    'entities': len(entities),
                    'connections': len(connections),
                    'properties': len(properties),
                    'modifiers': len(modifiers)
                },
                'validation_tests': {
                    'entity_validation': entity_valid,
                    'relationship_validation': relationship_valid
                }
            }
            
            # Log evidence
            self.evidence_logger.log_test_execution(
                'ONTOLOGY_VALIDATION_COMPLETE',
                {
                    'status': 'success' if success else 'failed',
                    'details': result,
                    'output': f"Ontology system validation: {len(entities)} entities, {len(connections)} connections"
                }
            )
            
            if success:
                print("  ✅ Ontology system functional")
            else:
                print("  ❌ Ontology system issues detected")
            
            return result
            
        except Exception as e:
            result = {
                'success': False,
                'error': str(e)
            }
            
            self.evidence_logger.log_test_execution(
                'ONTOLOGY_VALIDATION_ERROR',
                {
                    'status': 'error',
                    'error': str(e),
                    'details': result
                }
            )
            
            print(f"  ❌ Ontology validation error: {e}")
            return result
    
    def _run_enhanced_audit(self) -> Dict[str, Any]:
        """Run enhanced tool audit with contract validation"""
        try:
            # Import and run the enhanced audit system
            from audit_tools import ToolAuditor
            
            auditor = ToolAuditor()
            audit_success = auditor.audit_all_tools()
            
            # Get detailed results
            functional_tools = len([r for r in auditor.results if r['status'] == 'FUNCTIONAL'])
            total_tools = len(auditor.results)
            
            result = {
                'success': audit_success,
                'functional_tools': functional_tools,
                'total_tools': total_tools,
                'success_rate': (functional_tools / total_tools * 100) if total_tools > 0 else 0
            }
            
            print(f"  📊 Tools: {functional_tools}/{total_tools} functional ({result['success_rate']:.1f}%)")
            
            # Log evidence
            self.evidence_logger.log_test_execution(
                'ENHANCED_TOOL_AUDIT_COMPLETE',
                {
                    'status': 'success' if audit_success else 'failed',
                    'details': result,
                    'output': f"Enhanced audit: {functional_tools}/{total_tools} tools functional"
                }
            )
            
            return result
            
        except Exception as e:
            result = {
                'success': False,
                'error': str(e)
            }
            
            self.evidence_logger.log_test_execution(
                'ENHANCED_AUDIT_ERROR',
                {
                    'status': 'error',
                    'error': str(e),
                    'details': result
                }
            )
            
            print(f"  ❌ Enhanced audit error: {e}")
            return result
    
    def _test_integration_scenarios(self) -> Dict[str, Any]:
        """Test key integration scenarios"""
        try:
            scenarios_passed = 0
            total_scenarios = 3
            
            # Scenario 1: PDF → Document conversion
            try:
                from src.tools.phase1.t01_pdf_loader import PDFLoader
                from src.core.advanced_data_models import Document, ObjectType
                
                loader = PDFLoader()
                # Test with a known file
                test_file = "examples/pdfs/test_document.pdf"
                if os.path.exists(test_file):
                    result = loader.load_pdf(test_file, "test_workflow")
                    if result['status'] == 'success' and 'standardized_document' in result:
                        scenarios_passed += 1
                        print("  ✅ PDF → Standardized Document conversion")
                    else:
                        print("  ❌ PDF → Standardized Document conversion failed")
                else:
                    print("  ⚠️  Test PDF not found, skipping scenario")
                    total_scenarios -= 1
                    
            except Exception as e:
                print(f"  ❌ PDF integration scenario failed: {e}")
            
            # Scenario 2: Contract-Tool compatibility
            try:
                contract = self.contract_validator.load_contract('T01_PDFLoader')
                if contract:
                    loader = PDFLoader()
                    interface_errors = self.contract_validator.validate_tool_interface(loader, contract)
                    if not interface_errors:
                        scenarios_passed += 1
                        print("  ✅ Contract-Tool interface compatibility")
                    else:
                        print(f"  ❌ Contract-Tool interface issues: {interface_errors}")
                else:
                    print("  ⚠️  Contract not found, skipping scenario")
                    total_scenarios -= 1
                    
            except Exception as e:
                print(f"  ❌ Contract compatibility scenario failed: {e}")
            
            # Scenario 3: Ontology validation
            try:
                test_entity = {
                    'name': 'Apple Inc.',
                    'type': 'Organization',
                    'properties': {},
                    'modifiers': []
                }
                
                if self.ontology_validator.validate_entity(test_entity):
                    scenarios_passed += 1
                    print("  ✅ Ontology entity validation")
                else:
                    print("  ❌ Ontology entity validation failed")
                    
            except Exception as e:
                print(f"  ❌ Ontology validation scenario failed: {e}")
            
            success = scenarios_passed == total_scenarios
            result = {
                'success': success,
                'scenarios_passed': scenarios_passed,
                'total_scenarios': total_scenarios
            }
            
            # Log evidence
            self.evidence_logger.log_test_execution(
                'INTEGRATION_SCENARIOS_COMPLETE',
                {
                    'status': 'success' if success else 'failed',
                    'details': result,
                    'output': f"Integration scenarios: {scenarios_passed}/{total_scenarios} passed"
                }
            )
            
            return result
            
        except Exception as e:
            result = {
                'success': False,
                'error': str(e)
            }
            
            self.evidence_logger.log_test_execution(
                'INTEGRATION_SCENARIOS_ERROR',
                {
                    'status': 'error',
                    'error': str(e),
                    'details': result
                }
            )
            
            return result
    
    def _log_comprehensive_results(self, overall_success: bool, results: Dict[str, Any]):
        """Log comprehensive validation results"""
        self.evidence_logger.log_system_verification_summary(
            success_count=1 if overall_success else 0,
            total_count=1,
            details={
                'validation_type': 'comprehensive_validation_with_contracts_and_ontology',
                'contract_validation': results['contracts']['success'],
                'ontology_validation': results['ontology']['success'],
                'enhanced_audit': results['audit']['success'],
                'integration_scenarios': results['integration']['success'],
                'timestamp': datetime.now().isoformat(),
                'status': 'PASSED' if overall_success else 'FAILED'
            }
        )

def main():
    """Main validation function"""
    validator = ComprehensiveValidator()
    success = validator.run_full_validation()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()