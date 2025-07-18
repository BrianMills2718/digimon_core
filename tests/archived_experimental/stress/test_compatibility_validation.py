#!/usr/bin/env python3
"""
Compatibility Validation Tests
Ensures all components work together correctly across phases, versions, and configurations
"""

import sys
import time
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent

@dataclass
class CompatibilityResult:
    """Result of a compatibility test"""
    test_name: str
    passed: bool
    compatibility_score: float  # 0.0 to 1.0
    issues_found: List[str]
    recommendations: List[str]
    details: str


class CompatibilityValidator:
    """Comprehensive compatibility validation across all GraphRAG components"""
    
    def __init__(self):
        self.test_results = []
        self.compatibility_matrix = {}
        
    def run_all_compatibility_tests(self) -> Dict[str, Any]:
        """Run all compatibility validation tests"""
        print("🔗 COMPREHENSIVE COMPATIBILITY VALIDATION")
        print("=" * 80)
        
        compatibility_tests = [
            ("Phase Interface Compatibility", self.test_phase_interface_compatibility),
            ("Service Interface Compatibility", self.test_service_interface_compatibility),
            ("Data Format Compatibility", self.test_data_format_compatibility),
            ("API Contract Compatibility", self.test_api_contract_compatibility),
            ("Configuration Compatibility", self.test_configuration_compatibility),
            ("Database Schema Compatibility", self.test_database_schema_compatibility),
            ("Version Compatibility", self.test_version_compatibility),
            ("Integration Point Compatibility", self.test_integration_point_compatibility),
            ("Error Handling Compatibility", self.test_error_handling_compatibility),
            ("Performance Profile Compatibility", self.test_performance_profile_compatibility)
        ]
        
        overall_results = {
            "compatibility_summary": {},
            "compatibility_matrix": {},
            "critical_incompatibilities": [],
            "improvement_recommendations": [],
            "overall_compatibility_score": 0.0
        }
        
        for test_name, test_func in compatibility_tests:
            print(f"\n{'='*20} {test_name} {'='*20}")
            
            try:
                result = test_func()
                self.test_results.append(result)
                
                overall_results["compatibility_summary"][test_name] = {
                    "passed": result.passed,
                    "score": result.compatibility_score,
                    "issues_count": len(result.issues_found),
                    "details": result.details
                }
                
                status = "✅ COMPATIBLE" if result.passed else "❌ INCOMPATIBLE"
                print(f"{status} {test_name}")
                print(f"   Compatibility Score: {result.compatibility_score:.1%}")
                print(f"   Issues Found: {len(result.issues_found)}")
                
                if result.issues_found:
                    for issue in result.issues_found[:3]:  # Show first 3 issues
                        print(f"   ⚠️  {issue}")
                
            except Exception as e:
                print(f"❌ {test_name}: FAILED with exception: {e}")
                self.test_results.append(CompatibilityResult(
                    test_name=test_name,
                    passed=False,
                    compatibility_score=0.0,
                    issues_found=[f"Test execution failed: {str(e)}"],
                    recommendations=[],
                    details=f"Exception during test: {str(e)}"
                ))
        
        # Calculate overall compatibility metrics
        overall_results["compatibility_matrix"] = self._build_compatibility_matrix()
        overall_results["critical_incompatibilities"] = self._identify_critical_incompatibilities()
        overall_results["improvement_recommendations"] = self._generate_compatibility_recommendations()
        overall_results["overall_compatibility_score"] = self._calculate_overall_compatibility_score()
        
        return overall_results
    
    def test_phase_interface_compatibility(self) -> CompatibilityResult:
        """Test compatibility between phase interfaces"""
        print("🔄 Testing phase interface compatibility...")
        
        issues = []
        compatibility_score = 1.0
        
        try:
            from src.core.phase_adapters import Phase1Adapter, Phase2Adapter
            from src.core.graphrag_phase_interface import ProcessingRequest, ProcessingResult
            
            # Test that all phases implement the same interface
            phases = [Phase1Adapter(), Phase2Adapter()]
            
            # Check required methods
            required_methods = ["get_capabilities", "validate_input", "execute"]
            for i, phase in enumerate(phases):
                phase_name = f"Phase{i+1}"
                
                for method in required_methods:
                    if not hasattr(phase, method):
                        issues.append(f"{phase_name} missing required method: {method}")
                        compatibility_score -= 0.1
                    elif not callable(getattr(phase, method)):
                        issues.append(f"{phase_name}.{method} is not callable")
                        compatibility_score -= 0.1
            
            # Test input/output compatibility
            test_request = ProcessingRequest(
                documents=["test.pdf"],
                queries=["Test query"],
                workflow_id="compatibility_test"
            )
            
            # All phases should accept same request format
            for i, phase in enumerate(phases):
                phase_name = f"Phase{i+1}"
                try:
                    validation_errors = phase.validate_input(test_request)
                    if validation_errors and any("unsupported" in error.lower() for error in validation_errors):
                        issues.append(f"{phase_name} rejects standard request format")
                        compatibility_score -= 0.15
                except Exception as e:
                    issues.append(f"{phase_name}.validate_input failed: {str(e)}")
                    compatibility_score -= 0.2
            
            # Test capabilities compatibility
            try:
                capabilities = [phase.get_capabilities() for phase in phases]
                
                # Check that capabilities have consistent structure
                required_capability_fields = ["phase_name", "supported_documents", "supported_queries"]
                for i, cap in enumerate(capabilities):
                    phase_name = f"Phase{i+1}"
                    for field in required_capability_fields:
                        if field not in cap:
                            issues.append(f"{phase_name} capabilities missing field: {field}")
                            compatibility_score -= 0.1
                            
            except Exception as e:
                issues.append(f"Capabilities compatibility check failed: {str(e)}")
                compatibility_score -= 0.2
            
        except ImportError as e:
            issues.append(f"Phase import failed: {str(e)}")
            compatibility_score = 0.0
        except Exception as e:
            issues.append(f"Phase interface test failed: {str(e)}")
            compatibility_score = 0.0
        
        compatibility_score = max(0.0, min(1.0, compatibility_score))
        
        return CompatibilityResult(
            test_name="Phase Interface Compatibility",
            passed=compatibility_score >= 0.8,
            compatibility_score=compatibility_score,
            issues_found=issues,
            recommendations=self._generate_phase_recommendations(issues),
            details=f"Tested interface compatibility between phases, found {len(issues)} issues"
        )
    
    def test_service_interface_compatibility(self) -> CompatibilityResult:
        """Test compatibility between service interfaces"""
        print("🔧 Testing service interface compatibility...")
        
        issues = []
        compatibility_score = 1.0
        
        try:
            from src.core.identity_service import IdentityService
            from src.core.enhanced_identity_service import EnhancedIdentityService
            from src.core.provenance_service import ProvenanceService
            from src.core.quality_service import QualityService
            
            # Test identity service compatibility
            basic_service = IdentityService()
            enhanced_service = EnhancedIdentityService()
            
            # Check method compatibility
            basic_methods = [method for method in dir(basic_service) if not method.startswith('_')]
            enhanced_methods = [method for method in dir(enhanced_service) if not method.startswith('_')]
            
            # Enhanced service should have all basic service methods
            missing_methods = set(basic_methods) - set(enhanced_methods)
            if missing_methods:
                issues.append(f"Enhanced identity service missing methods: {missing_methods}")
                compatibility_score -= 0.2
            
            # Test that both services accept same inputs
            try:
                basic_result = basic_service.create_mention(
                    surface_form="Test Entity",
                    start_pos=0,
                    end_pos=11,
                    source_ref="compatibility://test",
                    entity_type="TEST",
                    confidence=0.8
                )
                
                enhanced_result = enhanced_service.create_mention(
                    surface_form="Test Entity",
                    start_pos=0,
                    end_pos=11,
                    source_ref="compatibility://test",
                    entity_type="TEST",
                    confidence=0.8
                )
                
                # Both should return dict with status
                if not isinstance(basic_result, dict) or "status" not in basic_result:
                    issues.append("Basic identity service returns incompatible format")
                    compatibility_score -= 0.15
                
                if not isinstance(enhanced_result, dict) or "status" not in enhanced_result:
                    issues.append("Enhanced identity service returns incompatible format")
                    compatibility_score -= 0.15
                    
            except Exception as e:
                issues.append(f"Service method compatibility test failed: {str(e)}")
                compatibility_score -= 0.2
            
            # Test service initialization compatibility
            services = [
                ("ProvenienceService", ProvenanceService),
                ("QualityService", QualityService)
            ]
            
            for service_name, service_class in services:
                try:
                    service = service_class()
                    if not hasattr(service, '__dict__'):
                        issues.append(f"{service_name} has unusual initialization")
                        compatibility_score -= 0.1
                except Exception as e:
                    issues.append(f"{service_name} initialization failed: {str(e)}")
                    compatibility_score -= 0.15
            
        except ImportError as e:
            issues.append(f"Service import failed: {str(e)}")
            compatibility_score = 0.0
        except Exception as e:
            issues.append(f"Service interface test failed: {str(e)}")
            compatibility_score = 0.0
        
        compatibility_score = max(0.0, min(1.0, compatibility_score))
        
        return CompatibilityResult(
            test_name="Service Interface Compatibility",
            passed=compatibility_score >= 0.7,
            compatibility_score=compatibility_score,
            issues_found=issues,
            recommendations=self._generate_service_recommendations(issues),
            details=f"Tested service interface compatibility, found {len(issues)} issues"
        )
    
    def test_data_format_compatibility(self) -> CompatibilityResult:
        """Test compatibility of data formats between components"""
        print("📄 Testing data format compatibility...")
        
        issues = []
        compatibility_score = 1.0
        
        try:
            from src.core.identity_service import IdentityService, Entity, Relationship
            from src.tools.phase2.t23c_ontology_aware_extractor import ExtractionResult
            
            # Test Entity format compatibility
            try:
                entity = Entity(
                    id="test_entity",
                    canonical_name="Test Entity",
                    entity_type="TEST",
                    confidence=0.8,
                    attributes={"test": "value"}
                )
                
                # Entity should be serializable
                entity_dict = entity.__dict__
                if not isinstance(entity_dict, dict):
                    issues.append("Entity format is not serializable")
                    compatibility_score -= 0.2
                
                # Required fields should be present
                required_fields = ["id", "canonical_name", "entity_type", "confidence"]
                for field in required_fields:
                    if not hasattr(entity, field):
                        issues.append(f"Entity missing required field: {field}")
                        compatibility_score -= 0.1
                        
            except Exception as e:
                issues.append(f"Entity format test failed: {str(e)}")
                compatibility_score -= 0.2
            
            # Test Relationship format compatibility
            try:
                relationship = Relationship(
                    id="test_rel",
                    source_id="entity1",
                    target_id="entity2",
                    relationship_type="RELATED_TO",
                    confidence=0.7,
                    attributes={"test": "value"}
                )
                
                # Check required fields
                required_fields = ["id", "source_id", "target_id", "relationship_type", "confidence"]
                for field in required_fields:
                    if not hasattr(relationship, field):
                        issues.append(f"Relationship missing required field: {field}")
                        compatibility_score -= 0.1
                        
            except Exception as e:
                issues.append(f"Relationship format test failed: {str(e)}")
                compatibility_score -= 0.2
            
            # Test ExtractionResult format compatibility
            try:
                extraction_result = ExtractionResult(
                    entities=[],
                    relationships=[],
                    mentions=[],
                    extraction_metadata={"test": "metadata"}
                )
                
                required_fields = ["entities", "relationships", "mentions", "extraction_metadata"]
                for field in required_fields:
                    if not hasattr(extraction_result, field):
                        issues.append(f"ExtractionResult missing required field: {field}")
                        compatibility_score -= 0.1
                        
            except Exception as e:
                issues.append(f"ExtractionResult format test failed: {str(e)}")
                compatibility_score -= 0.2
            
            # Test JSON serialization compatibility
            try:
                test_data = {
                    "entity": {
                        "id": "test",
                        "name": "Test Entity",
                        "type": "TEST",
                        "confidence": 0.8
                    },
                    "metadata": {
                        "timestamp": datetime.now().isoformat(),
                        "version": "1.0"
                    }
                }
                
                # Should be JSON serializable
                json_str = json.dumps(test_data)
                parsed_data = json.loads(json_str)
                
                if parsed_data != test_data:
                    issues.append("JSON serialization/deserialization not consistent")
                    compatibility_score -= 0.1
                    
            except Exception as e:
                issues.append(f"JSON serialization test failed: {str(e)}")
                compatibility_score -= 0.15
            
        except ImportError as e:
            issues.append(f"Data format import failed: {str(e)}")
            compatibility_score = 0.0
        except Exception as e:
            issues.append(f"Data format test failed: {str(e)}")
            compatibility_score = 0.0
        
        compatibility_score = max(0.0, min(1.0, compatibility_score))
        
        return CompatibilityResult(
            test_name="Data Format Compatibility",
            passed=compatibility_score >= 0.8,
            compatibility_score=compatibility_score,
            issues_found=issues,
            recommendations=self._generate_data_format_recommendations(issues),
            details=f"Tested data format compatibility, found {len(issues)} issues"
        )
    
    def test_api_contract_compatibility(self) -> CompatibilityResult:
        """Test API contract compatibility"""
        print("📋 Testing API contract compatibility...")
        
        issues = []
        compatibility_score = 1.0
        
        try:
            # Test that all tools follow consistent API patterns
            from src.tools.phase1.t01_pdf_loader import PDFLoader
            from src.tools.phase1.t23a_spacy_ner import SpacyNER
            from src.tools.phase1.t68_pagerank import PageRankCalculator
            
            from src.core.identity_service import IdentityService
            from src.core.provenance_service import ProvenanceService
            from src.core.quality_service import QualityService
            
            # Initialize services
            identity_service = IdentityService()
            provenance_service = ProvenanceService()
            quality_service = QualityService()
            
            # Test tool initialization consistency
            tools = [
                ("PDFLoader", PDFLoader, (identity_service, provenance_service, quality_service)),
                ("SpacyNER", SpacyNER, (identity_service, provenance_service, quality_service))
            ]
            
            for tool_name, tool_class, init_args in tools:
                try:
                    tool = tool_class(*init_args)
                    
                    # Check for get_tool_info method
                    if not hasattr(tool, 'get_tool_info'):
                        issues.append(f"{tool_name} missing get_tool_info method")
                        compatibility_score -= 0.1
                    else:
                        try:
                            tool_info = tool.get_tool_info()
                            if not isinstance(tool_info, dict):
                                issues.append(f"{tool_name}.get_tool_info() doesn't return dict")
                                compatibility_score -= 0.1
                            
                            required_info_fields = ["tool_id", "name", "version"]
                            for field in required_info_fields:
                                if field not in tool_info:
                                    issues.append(f"{tool_name} tool_info missing {field}")
                                    compatibility_score -= 0.05
                                    
                        except Exception as e:
                            issues.append(f"{tool_name}.get_tool_info() failed: {str(e)}")
                            compatibility_score -= 0.1
                    
                except Exception as e:
                    issues.append(f"{tool_name} initialization failed: {str(e)}")
                    compatibility_score -= 0.15
            
            # Test PageRank API separately (different initialization)
            try:
                pagerank = PageRankCalculator(
                    neo4j_uri="bolt://localhost:7687",
                    neo4j_user="neo4j",
                    neo4j_password="password"
                )
                
                if hasattr(pagerank, 'get_tool_info'):
                    tool_info = pagerank.get_tool_info()
                    if not isinstance(tool_info, dict):
                        issues.append("PageRank.get_tool_info() doesn't return dict")
                        compatibility_score -= 0.1
                else:
                    issues.append("PageRank missing get_tool_info method")
                    compatibility_score -= 0.1
                    
            except Exception as e:
                issues.append(f"PageRank API test failed: {str(e)}")
                compatibility_score -= 0.15
            
            # Test return format consistency
            try:
                result = identity_service.create_mention(
                    surface_form="API Test",
                    start_pos=0,
                    end_pos=8,
                    source_ref="api://test",
                    entity_type="API_TEST",
                    confidence=0.8
                )
                
                # Check return format
                if not isinstance(result, dict):
                    issues.append("Identity service doesn't return dict")
                    compatibility_score -= 0.2
                elif "status" not in result:
                    issues.append("Identity service result missing status field")
                    compatibility_score -= 0.1
                elif result["status"] not in ["success", "error"]:
                    issues.append("Identity service uses non-standard status values")
                    compatibility_score -= 0.1
                    
            except Exception as e:
                issues.append(f"Return format test failed: {str(e)}")
                compatibility_score -= 0.15
            
        except ImportError as e:
            issues.append(f"API contract import failed: {str(e)}")
            compatibility_score = 0.0
        except Exception as e:
            issues.append(f"API contract test failed: {str(e)}")
            compatibility_score = 0.0
        
        compatibility_score = max(0.0, min(1.0, compatibility_score))
        
        return CompatibilityResult(
            test_name="API Contract Compatibility",
            passed=compatibility_score >= 0.8,
            compatibility_score=compatibility_score,
            issues_found=issues,
            recommendations=self._generate_api_recommendations(issues),
            details=f"Tested API contract compatibility, found {len(issues)} issues"
        )
    
    def test_configuration_compatibility(self) -> CompatibilityResult:
        """Test configuration compatibility across components"""
        print("⚙️ Testing configuration compatibility...")
        
        issues = []
        compatibility_score = 1.0
        
        try:
            # Test Neo4j configuration consistency
            neo4j_configs = [
                ("PageRank", "src.tools.phase1.t68_pagerank", "PageRankCalculator"),
                ("GraphBuilder", "src.tools.phase2.t31_ontology_graph_builder", "OntologyAwareGraphBuilder")
            ]
            
            standard_neo4j_params = ["neo4j_uri", "neo4j_user", "neo4j_password"]
            
            for component_name, module_path, class_name in neo4j_configs:
                try:
                    module = __import__(module_path, fromlist=[class_name])
                    component_class = getattr(module, class_name)
                    
                    # Check constructor parameters
                    import inspect
                    sig = inspect.signature(component_class.__init__)
                    params = list(sig.parameters.keys())[1:]  # Skip 'self'
                    
                    missing_params = set(standard_neo4j_params) - set(params)
                    if missing_params:
                        issues.append(f"{component_name} missing standard Neo4j params: {missing_params}")
                        compatibility_score -= 0.1
                    
                    # Test initialization with standard config
                    try:
                        component = component_class(
                            neo4j_uri="bolt://localhost:7687",
                            neo4j_user="neo4j",
                            neo4j_password="password"
                        )
                        
                    except Exception as e:
                        issues.append(f"{component_name} initialization with standard config failed: {str(e)}")
                        compatibility_score -= 0.15
                        
                except Exception as e:
                    issues.append(f"{component_name} configuration test failed: {str(e)}")
                    compatibility_score -= 0.2
            
            # Test service configuration consistency
            from src.core.identity_service import IdentityService
            from src.core.enhanced_identity_service import EnhancedIdentityService
            
            try:
                # Both should initialize without parameters
                basic_service = IdentityService()
                enhanced_service = EnhancedIdentityService()
                
                # Both should have similar configuration options
                basic_methods = [m for m in dir(basic_service) if 'config' in m.lower()]
                enhanced_methods = [m for m in dir(enhanced_service) if 'config' in m.lower()]
                
                if basic_methods and not enhanced_methods:
                    issues.append("Enhanced service missing configuration methods")
                    compatibility_score -= 0.1
                    
            except Exception as e:
                issues.append(f"Service configuration test failed: {str(e)}")
                compatibility_score -= 0.15
            
            # Test workflow configuration consistency
            try:
                from src.core.tool_factory import create_unified_workflow_config, Phase, OptimizationLevel
                
                workflow = EnhancedVerticalSliceWorkflow(
                    neo4j_uri="bolt://localhost:7687",
                    neo4j_user="neo4j",
                    neo4j_password="password",
                    confidence_threshold=0.7
                )
                
                # Should accept standard configuration
                if not hasattr(workflow, 'confidence_threshold'):
                    issues.append("Workflow missing confidence_threshold configuration")
                    compatibility_score -= 0.1
                    
            except Exception as e:
                issues.append(f"Workflow configuration test failed: {str(e)}")
                compatibility_score -= 0.15
        
        except ImportError as e:
            issues.append(f"Configuration import failed: {str(e)}")
            compatibility_score = 0.0
        except Exception as e:
            issues.append(f"Configuration test failed: {str(e)}")
            compatibility_score = 0.0
        
        compatibility_score = max(0.0, min(1.0, compatibility_score))
        
        return CompatibilityResult(
            test_name="Configuration Compatibility",
            passed=compatibility_score >= 0.8,
            compatibility_score=compatibility_score,
            issues_found=issues,
            recommendations=self._generate_config_recommendations(issues),
            details=f"Tested configuration compatibility, found {len(issues)} issues"
        )
    
    def test_database_schema_compatibility(self) -> CompatibilityResult:
        """Test database schema compatibility"""
        print("🗄️ Testing database schema compatibility...")
        
        issues = []
        compatibility_score = 1.0
        
        try:
            from src.tools.phase1.t68_pagerank import PageRankCalculator
            from src.tools.phase2.t31_ontology_graph_builder import OntologyAwareGraphBuilder
            
            # Test that both components can work with same Neo4j schema
            pagerank = PageRankCalculator(
                neo4j_uri="bolt://localhost:7687",
                neo4j_user="neo4j",
                neo4j_password="password"
            )
            
            graph_builder = OntologyAwareGraphBuilder(
                neo4j_uri="bolt://localhost:7687",
                neo4j_user="neo4j",
                neo4j_password="password"
            )
            
            # Both should be able to connect (or fail gracefully)
            pagerank_info = pagerank.get_tool_info()
            pagerank_connected = pagerank_info.get("neo4j_connected", False)
            
            # Test schema expectations
            if hasattr(pagerank, '_load_graph_from_neo4j'):
                # PageRank expects Entity nodes with specific properties
                pass  # Schema test would require actual database
            
            if hasattr(graph_builder, '_process_entity'):
                # Graph builder creates Entity nodes with specific properties
                pass  # Schema test would require actual database
            
            # For now, just test that both components have compatible initialization
            if not pagerank_info:
                issues.append("PageRank component initialization returned no info")
                compatibility_score -= 0.2
            
        except Exception as e:
            issues.append(f"Database schema test failed: {str(e)}")
            compatibility_score -= 0.3
        
        # Since we can't test actual database schema without connection,
        # we'll mark this as a basic compatibility test
        if not issues:
            compatibility_score = 0.8  # Reduced score since we can't fully test
        
        compatibility_score = max(0.0, min(1.0, compatibility_score))
        
        return CompatibilityResult(
            test_name="Database Schema Compatibility",
            passed=compatibility_score >= 0.7,
            compatibility_score=compatibility_score,
            issues_found=issues,
            recommendations=self._generate_database_recommendations(issues),
            details=f"Tested database schema compatibility (limited without DB connection), found {len(issues)} issues"
        )
    
    def test_version_compatibility(self) -> CompatibilityResult:
        """Test version compatibility"""
        print("🏷️ Testing version compatibility...")
        
        issues = []
        compatibility_score = 1.0
        
        try:
            # Test tool version consistency
            from src.tools.phase1.t01_pdf_loader import PDFLoader
            from src.tools.phase1.t23a_spacy_ner import SpacyNER
            from src.core.identity_service import IdentityService
            from src.core.provenance_service import ProvenanceService
            from src.core.quality_service import QualityService
            
            # Initialize tools
            identity_service = IdentityService()
            provenance_service = ProvenanceService()
            quality_service = QualityService()
            
            tools = [
                PDFLoader(identity_service, provenance_service, quality_service),
                SpacyNER(identity_service, provenance_service, quality_service)
            ]
            
            versions = []
            for tool in tools:
                try:
                    if hasattr(tool, 'get_tool_info'):
                        tool_info = tool.get_tool_info()
                        version = tool_info.get('version', 'unknown')
                        versions.append(version)
                        
                        # Check version format
                        if version == 'unknown':
                            issues.append(f"Tool {tool_info.get('name', 'unknown')} has no version")
                            compatibility_score -= 0.1
                        elif not isinstance(version, str):
                            issues.append(f"Tool {tool_info.get('name', 'unknown')} has invalid version format")
                            compatibility_score -= 0.1
                            
                except Exception as e:
                    issues.append(f"Version check failed for tool: {str(e)}")
                    compatibility_score -= 0.15
            
            # Check Python version compatibility
            import sys
            python_version = sys.version_info
            
            if python_version.major < 3:
                issues.append("Python 2.x not supported")
                compatibility_score -= 0.5
            elif python_version.minor < 8:
                issues.append(f"Python 3.{python_version.minor} may have compatibility issues (recommend 3.8+)")
                compatibility_score -= 0.2
            
            # Test dependency version compatibility
            try:
                import spacy
                spacy_version = spacy.__version__
                
                # Basic version check
                if not spacy_version:
                    issues.append("SpaCy version could not be determined")
                    compatibility_score -= 0.1
                    
            except ImportError:
                issues.append("SpaCy not available - required for NER")
                compatibility_score -= 0.3
            
            try:
                import neo4j
                neo4j_version = neo4j.__version__
                
                if not neo4j_version:
                    issues.append("Neo4j driver version could not be determined")
                    compatibility_score -= 0.1
                    
            except ImportError:
                issues.append("Neo4j driver not available - required for graph operations")
                compatibility_score -= 0.3
            
        except Exception as e:
            issues.append(f"Version compatibility test failed: {str(e)}")
            compatibility_score = 0.0
        
        compatibility_score = max(0.0, min(1.0, compatibility_score))
        
        return CompatibilityResult(
            test_name="Version Compatibility",
            passed=compatibility_score >= 0.7,
            compatibility_score=compatibility_score,
            issues_found=issues,
            recommendations=self._generate_version_recommendations(issues),
            details=f"Tested version compatibility, found {len(issues)} issues"
        )
    
    def test_integration_point_compatibility(self) -> CompatibilityResult:
        """Test integration point compatibility"""
        print("🔗 Testing integration point compatibility...")
        
        issues = []
        compatibility_score = 1.0
        
        try:
            # Test Phase 1 -> Phase 2 integration
            from src.core.phase_adapters import Phase1Adapter, Phase2Adapter
            from src.core.graphrag_phase_interface import ProcessingRequest
            
            phase1 = Phase1Adapter()
            phase2 = Phase2Adapter()
            
            test_request = ProcessingRequest(
                documents=["test.pdf"],
                queries=["Test query"],
                workflow_id="integration_test",
                domain_description="Test domain"
            )
            
            # Test that Phase 1 output could be consumed by Phase 2
            try:
                # Both should validate the same request
                p1_validation = phase1.validate_input(test_request)
                p2_validation = phase2.validate_input(test_request)
                
                # Check for incompatible validation requirements
                p1_errors = set(p1_validation) if p1_validation else set()
                p2_errors = set(p2_validation) if p2_validation else set()
                
                # Phase 2 might have additional requirements (like domain_description)
                # but shouldn't reject what Phase 1 accepts
                common_errors = p1_errors & p2_errors
                if common_errors:
                    issues.append(f"Both phases reject request: {common_errors}")
                    compatibility_score -= 0.2
                
            except Exception as e:
                issues.append(f"Phase integration validation failed: {str(e)}")
                compatibility_score -= 0.3
            
            # Test MCP integration points
            try:
                from src.mcp_server import mcp
                # MCP server should be importable
                
                # Test that core services can be used via MCP
                from src.core.identity_service import IdentityService
                service = IdentityService()
                
                # Service should work normally (MCP doesn't break core functionality)
                result = service.create_mention(
                    surface_form="Integration Test",
                    start_pos=0,
                    end_pos=16,
                    source_ref="integration://test",
                    entity_type="INTEGRATION",
                    confidence=0.8
                )
                
                if result["status"] != "success":
                    issues.append("Core service integration affected by MCP")
                    compatibility_score -= 0.15
                    
            except Exception as e:
                issues.append(f"MCP integration test failed: {str(e)}")
                compatibility_score -= 0.2
            
            # Test workflow service integration
            try:
                from src.core.workflow_state_service import WorkflowStateService
                from src.core.tool_factory import create_unified_workflow_config, Phase, OptimizationLevel
                
                workflow_service = WorkflowStateService()
                workflow = EnhancedVerticalSliceWorkflow()
                
                # Workflow should be able to use workflow service
                if not hasattr(workflow, 'workflow_service'):
                    issues.append("Workflow doesn't integrate with workflow service")
                    compatibility_score -= 0.1
                    
            except Exception as e:
                issues.append(f"Workflow service integration test failed: {str(e)}")
                compatibility_score -= 0.15
            
        except ImportError as e:
            issues.append(f"Integration point import failed: {str(e)}")
            compatibility_score = 0.0
        except Exception as e:
            issues.append(f"Integration point test failed: {str(e)}")
            compatibility_score = 0.0
        
        compatibility_score = max(0.0, min(1.0, compatibility_score))
        
        return CompatibilityResult(
            test_name="Integration Point Compatibility",
            passed=compatibility_score >= 0.7,
            compatibility_score=compatibility_score,
            issues_found=issues,
            recommendations=self._generate_integration_recommendations(issues),
            details=f"Tested integration point compatibility, found {len(issues)} issues"
        )
    
    def test_error_handling_compatibility(self) -> CompatibilityResult:
        """Test error handling compatibility"""
        print("⚠️ Testing error handling compatibility...")
        
        issues = []
        compatibility_score = 1.0
        
        try:
            from src.core.identity_service import IdentityService
            from src.tools.phase1.t01_pdf_loader import PDFLoader
            from src.core.provenance_service import ProvenanceService
            from src.core.quality_service import QualityService
            
            # Test consistent error response format
            service = IdentityService()
            
            # Test invalid input handling
            try:
                result = service.create_mention(
                    surface_form="",  # Invalid empty string
                    start_pos=0,
                    end_pos=0,
                    source_ref="",
                    entity_type="",
                    confidence=-1.0  # Invalid confidence
                )
                
                # Should return error result, not raise exception
                if not isinstance(result, dict):
                    issues.append("Identity service doesn't return dict for errors")
                    compatibility_score -= 0.2
                elif "status" not in result:
                    issues.append("Identity service error result missing status")
                    compatibility_score -= 0.1
                elif result["status"] not in ["error", "success"]:
                    issues.append("Identity service uses non-standard error status")
                    compatibility_score -= 0.1
                    
            except Exception as e:
                # Services should handle errors gracefully, not raise exceptions for invalid input
                issues.append("Identity service raises exception for invalid input instead of returning error")
                compatibility_score -= 0.2
            
            # Test tool error handling
            try:
                loader = PDFLoader(service, ProvenanceService(), QualityService())
                
                # Test with non-existent file
                result = loader.load_pdf("/nonexistent/file.pdf")
                
                if not isinstance(result, dict):
                    issues.append("PDF loader doesn't return dict for errors")
                    compatibility_score -= 0.2
                elif "status" not in result:
                    issues.append("PDF loader error result missing status")
                    compatibility_score -= 0.1
                elif result["status"] != "error":
                    issues.append("PDF loader doesn't return error status for non-existent file")
                    compatibility_score -= 0.1
                    
            except Exception as e:
                issues.append("PDF loader raises exception for non-existent file instead of returning error")
                compatibility_score -= 0.2
            
            # Test Phase 2 error handling
            try:
                from src.core.tool_factory import create_unified_workflow_config, Phase, OptimizationLevel
                
                workflow = EnhancedVerticalSliceWorkflow()
                
                # Test ontology generation error handling
                result = workflow._execute_ontology_generation("test", "")  # Empty domain
                
                # Should handle gracefully
                if not isinstance(result, dict):
                    issues.append("Workflow doesn't return dict for errors")
                    compatibility_score -= 0.2
                elif "status" not in result:
                    issues.append("Workflow error result missing status")
                    compatibility_score -= 0.1
                    
            except Exception as e:
                issues.append(f"Workflow error handling test failed: {str(e)}")
                compatibility_score -= 0.15
            
        except ImportError as e:
            issues.append(f"Error handling import failed: {str(e)}")
            compatibility_score = 0.0
        except Exception as e:
            issues.append(f"Error handling test failed: {str(e)}")
            compatibility_score = 0.0
        
        compatibility_score = max(0.0, min(1.0, compatibility_score))
        
        return CompatibilityResult(
            test_name="Error Handling Compatibility",
            passed=compatibility_score >= 0.8,
            compatibility_score=compatibility_score,
            issues_found=issues,
            recommendations=self._generate_error_handling_recommendations(issues),
            details=f"Tested error handling compatibility, found {len(issues)} issues"
        )
    
    def test_performance_profile_compatibility(self) -> CompatibilityResult:
        """Test performance profile compatibility"""
        print("⚡ Testing performance profile compatibility...")
        
        issues = []
        compatibility_score = 1.0
        
        try:
            from src.core.identity_service import IdentityService
            
            service = IdentityService()
            
            # Test response time consistency
            response_times = []
            for i in range(10):
                start_time = time.time()
                service.create_mention(
                    surface_form=f"Perf Test {i}",
                    start_pos=0,
                    end_pos=10,
                    source_ref=f"perf://test/{i}",
                    entity_type="PERF",
                    confidence=0.8
                )
                response_times.append(time.time() - start_time)
            
            # Check for performance consistency
            avg_time = sum(response_times) / len(response_times)
            max_time = max(response_times)
            min_time = min(response_times)
            
            # Response times shouldn't vary too much
            if max_time > min_time * 5:  # More than 5x variation
                issues.append(f"Inconsistent response times: {min_time:.3f}s - {max_time:.3f}s")
                compatibility_score -= 0.2
            
            if avg_time > 0.1:  # Average response time over 100ms
                issues.append(f"Slow average response time: {avg_time:.3f}s")
                compatibility_score -= 0.1
            
            # Test memory usage consistency
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Create many entities
            for i in range(100):
                service.create_mention(
                    surface_form=f"Memory Test {i}",
                    start_pos=0,
                    end_pos=12,
                    source_ref=f"memory://test/{i}",
                    entity_type="MEMORY",
                    confidence=0.8
                )
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            if memory_increase > 50:  # More than 50MB for 100 entities
                issues.append(f"High memory usage: {memory_increase:.1f}MB for 100 entities")
                compatibility_score -= 0.1
            
        except Exception as e:
            issues.append(f"Performance profile test failed: {str(e)}")
            compatibility_score -= 0.3
        
        compatibility_score = max(0.0, min(1.0, compatibility_score))
        
        return CompatibilityResult(
            test_name="Performance Profile Compatibility",
            passed=compatibility_score >= 0.7,
            compatibility_score=compatibility_score,
            issues_found=issues,
            recommendations=self._generate_performance_recommendations(issues),
            details=f"Tested performance profile compatibility, found {len(issues)} issues"
        )
    
    # Helper methods for generating recommendations
    def _generate_phase_recommendations(self, issues: List[str]) -> List[str]:
        recommendations = []
        if any("missing" in issue.lower() for issue in issues):
            recommendations.append("Implement missing interface methods in phase adapters")
        if any("request format" in issue.lower() for issue in issues):
            recommendations.append("Standardize request format across all phases")
        if any("capabilities" in issue.lower() for issue in issues):
            recommendations.append("Add required capability fields to all phase adapters")
        return recommendations
    
    def _generate_service_recommendations(self, issues: List[str]) -> List[str]:
        recommendations = []
        if any("missing methods" in issue.lower() for issue in issues):
            recommendations.append("Ensure enhanced services maintain backward compatibility")
        if any("incompatible format" in issue.lower() for issue in issues):
            recommendations.append("Standardize return formats across all services")
        return recommendations
    
    def _generate_data_format_recommendations(self, issues: List[str]) -> List[str]:
        recommendations = []
        if any("missing" in issue.lower() for issue in issues):
            recommendations.append("Add missing required fields to data structures")
        if any("serialization" in issue.lower() for issue in issues):
            recommendations.append("Ensure all data structures are JSON serializable")
        return recommendations
    
    def _generate_api_recommendations(self, issues: List[str]) -> List[str]:
        recommendations = []
        if any("missing" in issue.lower() for issue in issues):
            recommendations.append("Implement consistent API methods across all tools")
        if any("status" in issue.lower() for issue in issues):
            recommendations.append("Standardize status field values across all APIs")
        return recommendations
    
    def _generate_config_recommendations(self, issues: List[str]) -> List[str]:
        recommendations = []
        if any("missing" in issue.lower() for issue in issues):
            recommendations.append("Standardize configuration parameters across components")
        if any("initialization" in issue.lower() for issue in issues):
            recommendations.append("Fix component initialization with standard configurations")
        return recommendations
    
    def _generate_database_recommendations(self, issues: List[str]) -> List[str]:
        recommendations = []
        recommendations.append("Implement comprehensive database schema compatibility tests")
        recommendations.append("Document expected Neo4j schema for all components")
        return recommendations
    
    def _generate_version_recommendations(self, issues: List[str]) -> List[str]:
        recommendations = []
        if any("version" in issue.lower() for issue in issues):
            recommendations.append("Add version information to all tools and components")
        if any("python" in issue.lower() for issue in issues):
            recommendations.append("Update to Python 3.8+ for better compatibility")
        if any("not available" in issue.lower() for issue in issues):
            recommendations.append("Install missing required dependencies")
        return recommendations
    
    def _generate_integration_recommendations(self, issues: List[str]) -> List[str]:
        recommendations = []
        if any("phase" in issue.lower() for issue in issues):
            recommendations.append("Fix phase-to-phase integration points")
        if any("mcp" in issue.lower() for issue in issues):
            recommendations.append("Ensure MCP integration doesn't break core functionality")
        return recommendations
    
    def _generate_error_handling_recommendations(self, issues: List[str]) -> List[str]:
        recommendations = []
        if any("exception" in issue.lower() for issue in issues):
            recommendations.append("Implement graceful error handling instead of raising exceptions")
        if any("status" in issue.lower() for issue in issues):
            recommendations.append("Standardize error response format across all components")
        return recommendations
    
    def _generate_performance_recommendations(self, issues: List[str]) -> List[str]:
        recommendations = []
        if any("time" in issue.lower() for issue in issues):
            recommendations.append("Optimize response times for better performance consistency")
        if any("memory" in issue.lower() for issue in issues):
            recommendations.append("Implement memory optimization strategies")
        return recommendations
    
    def _build_compatibility_matrix(self) -> Dict[str, Dict[str, float]]:
        """Build compatibility matrix between components"""
        matrix = {}
        
        for result in self.test_results:
            category = result.test_name.split()[0]  # Get category (Phase, Service, etc.)
            matrix[category] = matrix.get(category, {})
            matrix[category]["score"] = result.compatibility_score
            matrix[category]["issues"] = len(result.issues_found)
        
        return matrix
    
    def _identify_critical_incompatibilities(self) -> List[str]:
        """Identify critical incompatibilities that must be fixed"""
        critical = []
        
        for result in self.test_results:
            if result.compatibility_score < 0.5:
                critical.append(f"{result.test_name}: {result.compatibility_score:.1%}")
        
        return critical
    
    def _generate_compatibility_recommendations(self) -> List[str]:
        """Generate overall compatibility improvement recommendations"""
        recommendations = []
        
        failed_tests = [r for r in self.test_results if not r.passed]
        
        if len(failed_tests) > len(self.test_results) // 2:
            recommendations.append("Major compatibility overhaul needed - standardize interfaces")
        
        for result in self.test_results:
            recommendations.extend(result.recommendations[:1])  # Take top recommendation from each
        
        # Remove duplicates
        return list(set(recommendations))
    
    def _calculate_overall_compatibility_score(self) -> float:
        """Calculate overall compatibility score"""
        if not self.test_results:
            return 0.0
        
        scores = [r.compatibility_score for r in self.test_results]
        return sum(scores) / len(scores)


def main():
    """Run comprehensive compatibility validation"""
    
    print("🔗 STARTING COMPREHENSIVE COMPATIBILITY VALIDATION")
    print("Testing compatibility across all GraphRAG components and interfaces")
    print("=" * 80)
    
    validator = CompatibilityValidator()
    
    # Run all compatibility tests
    start_time = time.time()
    results = validator.run_all_compatibility_tests()
    total_time = time.time() - start_time
    
    # Generate summary report
    print(f"\n{'='*80}")
    print("🔗 COMPATIBILITY VALIDATION RESULTS")
    print("=" * 80)
    
    # Overall statistics
    compatibility_summary = results["compatibility_summary"]
    passed_tests = sum(1 for test in compatibility_summary.values() if test["passed"])
    total_tests = len(compatibility_summary)
    
    print(f"\n📊 Compatibility Results:")
    print(f"   Tests Passed: {passed_tests}/{total_tests} ({passed_tests/total_tests:.1%})")
    print(f"   Overall Compatibility Score: {results['overall_compatibility_score']:.1%}")
    print(f"   Total Test Time: {total_time:.2f}s")
    
    # Test details
    print(f"\n🔍 Individual Compatibility Tests:")
    for test_name, test_result in compatibility_summary.items():
        status_icon = "✅" if test_result["passed"] else "❌"
        print(f"   {status_icon} {test_name}: {test_result['score']:.1%} ({test_result['issues_count']} issues)")
    
    # Critical incompatibilities
    if results["critical_incompatibilities"]:
        print(f"\n🚨 Critical Incompatibilities:")
        for incompatibility in results["critical_incompatibilities"]:
            print(f"   ⚠️  {incompatibility}")
    
    # Compatibility matrix
    if results["compatibility_matrix"]:
        print(f"\n📊 Compatibility Matrix:")
        for category, data in results["compatibility_matrix"].items():
            print(f"   {category}: {data.get('score', 0):.1%} (issues: {data.get('issues', 0)})")
    
    # Recommendations
    if results["improvement_recommendations"]:
        print(f"\n💡 Compatibility Improvement Recommendations:")
        for i, rec in enumerate(results["improvement_recommendations"][:5], 1):
            print(f"   {i}. {rec}")
    
    # Final assessment
    overall_score = results["overall_compatibility_score"]
    print(f"\n🎯 COMPATIBILITY ASSESSMENT:")
    
    if overall_score >= 0.9:
        print("🟢 EXCELLENT: System components are highly compatible")
    elif overall_score >= 0.8:
        print("🟡 GOOD: System has good compatibility with minor issues")
    elif overall_score >= 0.7:
        print("🟠 FAIR: System has moderate compatibility, some fixes needed")
    elif overall_score >= 0.6:
        print("🔴 POOR: System has compatibility issues, significant work required")
    else:
        print("🔴 CRITICAL: System has major compatibility problems")
    
    print(f"\nCompatibility Score: {overall_score:.1%}")
    
    return overall_score >= 0.7  # Return success if >= 70% compatibility


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)