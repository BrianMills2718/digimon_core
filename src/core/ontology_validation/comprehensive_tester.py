"""
Comprehensive Ontology Tester

Implements comprehensive testing of DOLCE ontology and Master Concept Library
with extensive real-world scenarios and evidence generation.
"""

import logging
from typing import Dict, Any, List, Tuple
from datetime import datetime

from ..data_models import Entity, Relationship, QualityTier, BaseObject
from .core_validators import DolceValidator

logger = logging.getLogger(__name__)


class ComprehensiveOntologyTester:
    """Comprehensive tester for ontology validation systems"""
    
    def __init__(self, dolce_validator: DolceValidator):
        """Initialize with DOLCE validator"""
        self.dolce_validator = dolce_validator
        self.logger = logging.getLogger("core.ontology_validation.comprehensive_tester")

    def test_dolce_ontology_comprehensive(self) -> Dict[str, Any]:
        """Test DOLCE ontology with extensive real-world scenarios
        
        Returns:
            Dictionary with comprehensive test results
            
        Raises:
            RuntimeError: If DOLCE ontology fails comprehensive testing
        """
        test_start_time = datetime.now()
        
        # Comprehensive test entities covering different domains
        comprehensive_test_entities = [
            # People and roles
            {
                "name": "Dr. Sarah Chen",
                "type": "Person",
                "context": "research scientist",
                "confidence": 0.95
            },
            {
                "name": "CEO John Smith",
                "type": "IndividualActor",
                "context": "business leader",
                "confidence": 0.90
            },
            {
                "name": "Professor Maria Garcia",
                "type": "Academic",
                "context": "university professor",
                "confidence": 0.88
            },
            # Organizations at different scales
            {
                "name": "Microsoft Corporation",
                "type": "Organization",
                "context": "multinational technology company",
                "confidence": 0.98
            },
            {
                "name": "Local Coffee Shop",
                "type": "Business",
                "context": "small local business",
                "confidence": 0.85
            },
            {
                "name": "Stanford University",
                "type": "Institution",
                "context": "educational institution",
                "confidence": 0.95
            },
            # Geographic entities
            {
                "name": "San Francisco",
                "type": "Location",
                "context": "major city",
                "confidence": 0.99
            },
            {
                "name": "Silicon Valley",
                "type": "Region",
                "context": "technology hub",
                "confidence": 0.92
            },
            {
                "name": "Building 42",
                "type": "Facility",
                "context": "office building",
                "confidence": 0.80
            },
            # Abstract concepts
            {
                "name": "Artificial Intelligence",
                "type": "Concept",
                "context": "technology field",
                "confidence": 0.94
            },
            {
                "name": "Innovation",
                "type": "Abstract",
                "context": "business concept",
                "confidence": 0.75
            },
            {
                "name": "Sustainability",
                "type": "Principle",
                "context": "environmental principle",
                "confidence": 0.89
            },
            # Events and processes
            {
                "name": "Product Launch",
                "type": "Event",
                "context": "business event",
                "confidence": 0.83
            },
            {
                "name": "Research Process",
                "type": "Process",
                "context": "scientific methodology",
                "confidence": 0.91
            },
            {
                "name": "Team Meeting",
                "type": "Activity",
                "context": "collaborative activity",
                "confidence": 0.87
            }
        ]
        
        validation_results = {}
        mapping_accuracy_results = {}
        
        try:
            for entity_data in comprehensive_test_entities:
                # Create Entity object
                entity = Entity(
                    id=f"test_{entity_data['name'].lower().replace(' ', '_')}",
                    canonical_name=entity_data["name"],
                    entity_type=entity_data["type"],
                    surface_forms=[entity_data["name"]],
                    confidence=entity_data["confidence"],
                    quality_tier=QualityTier.HIGH,
                    created_by="comprehensive_test",
                    created_at=datetime.now(),
                    workflow_id="comprehensive_dolce_test"
                )
                
                # Test DOLCE mapping
                dolce_mapping = self.dolce_validator.get_dolce_mapping(entity_data["type"])
                mapping_accuracy_results[entity_data["type"]] = {
                    "dolce_concept": dolce_mapping,
                    "is_valid_dolce_concept": dolce_mapping is not None,
                    "entity_example": entity_data["name"]
                }
                
                # Test entity validation
                validation_result = self.dolce_validator.validate_entity_simple(entity)
                validation_results[entity.id] = {
                    "validation_passed": validation_result.get("valid", False),
                    "dolce_concept_assigned": validation_result.get("dolce_concept"),
                    "entity_type": entity_data["type"],
                    "validation_details": validation_result
                }
            
            # Test relationship validation
            test_relationships = [
                ("Dr. Sarah Chen", "works_at", "Stanford University"),
                ("Microsoft Corporation", "located_in", "San Francisco"),
                ("Product Launch", "organized_by", "Microsoft Corporation")
            ]
            
            relationship_results = {}
            for source, relation, target in test_relationships:
                try:
                    # This would normally require a validate_relationship_against_dolce method
                    # For now, we'll test relationship type mapping
                    rel_mapping = self.dolce_validator.get_dolce_mapping(relation)
                    relationship_results[f"{source}_{relation}_{target}"] = {
                        "valid": rel_mapping is not None,
                        "dolce_mapping": rel_mapping
                    }
                except Exception as e:
                    relationship_results[f"{source}_{relation}_{target}"] = {
                        "valid": False,
                        "error": str(e)
                    }
            
            # Calculate comprehensive metrics
            total_entities = len(comprehensive_test_entities)
            unique_entity_types = set(e["type"] for e in comprehensive_test_entities)
            valid_mappings = sum(1 for r in mapping_accuracy_results.values() if r["is_valid_dolce_concept"])
            valid_validations = sum(1 for r in validation_results.values() if r["validation_passed"])
            
            mapping_accuracy = valid_mappings / len(unique_entity_types)
            validation_accuracy = valid_validations / total_entities
            
            # STRICT SUCCESS CRITERIA
            success_criteria = {
                "mapping_accuracy_100_percent": mapping_accuracy == 1.0,
                "validation_accuracy_100_percent": validation_accuracy == 1.0,
                "all_relationships_valid": all(r.get("valid", False) for r in relationship_results.values()),
                "comprehensive_coverage": total_entities >= 15,
                "entity_type_diversity": len(unique_entity_types) >= 10
            }
            
            all_criteria_met = all(success_criteria.values())
            
            test_duration = (datetime.now() - test_start_time).total_seconds()
            
            result = {
                "status": "success" if all_criteria_met else "failed",
                "total_entities_tested": total_entities,
                "entity_types_tested": len(unique_entity_types),
                "mapping_accuracy_percentage": mapping_accuracy * 100,
                "validation_accuracy_percentage": validation_accuracy * 100,
                "success_criteria": success_criteria,
                "all_criteria_met": all_criteria_met,
                "detailed_mapping_results": mapping_accuracy_results,
                "detailed_validation_results": validation_results,
                "relationship_validation_results": relationship_results,
                "test_duration_seconds": test_duration,
                "timestamp": datetime.now().isoformat()
            }
            
            if not all_criteria_met:
                failed_criteria = [k for k, v in success_criteria.items() if not v]
                raise RuntimeError(f"DOLCE ontology failed comprehensive testing. Failed criteria: {failed_criteria}")
            
            self.logger.info(f"DOLCE ontology comprehensive test PASSED: {mapping_accuracy*100:.1f}% mapping accuracy, {validation_accuracy*100:.1f}% validation accuracy")
            
            return result
            
        except Exception as e:
            test_duration = (datetime.now() - test_start_time).total_seconds()
            self.logger.error(f"DOLCE ontology comprehensive test FAILED: {str(e)}")
            raise RuntimeError(f"DOLCE ontology comprehensive test failed: {e}")

    def test_edge_cases_and_stress_scenarios(self) -> Dict[str, Any]:
        """Test ontology validation with edge cases and stress scenarios"""
        test_start_time = datetime.now()
        
        edge_case_tests = {
            "empty_entities": [],
            "malformed_entities": [
                {"name": "", "type": "InvalidType", "confidence": -1.0},
                {"name": None, "type": "", "confidence": 2.0},
                {"type": "Person"}  # Missing name
            ],
            "boundary_confidence_values": [
                {"name": "Test Entity", "type": "Person", "confidence": 0.0},
                {"name": "Test Entity", "type": "Person", "confidence": 1.0},
                {"name": "Test Entity", "type": "Person", "confidence": 0.5}
            ],
            "unicode_and_special_characters": [
                {"name": "José María García-López", "type": "Person", "confidence": 0.9},
                {"name": "北京市", "type": "Location", "confidence": 0.85},
                {"name": "Entity@#$%^&*()", "type": "Concept", "confidence": 0.7}
            ],
            "very_long_names": [
                {"name": "A" * 1000, "type": "Concept", "confidence": 0.8}
            ],
            "case_sensitivity_tests": [
                {"name": "microsoft", "type": "organization", "confidence": 0.9},
                {"name": "MICROSOFT", "type": "ORGANIZATION", "confidence": 0.9},
                {"name": "MiCrOsOfT", "type": "OrGaNiZaTiOn", "confidence": 0.9}
            ]
        }
        
        test_results = {}
        
        try:
            for test_category, test_entities in edge_case_tests.items():
                category_results = {
                    "test_count": len(test_entities),
                    "passed": 0,
                    "failed": 0,
                    "errors": [],
                    "details": []
                }
                
                for i, entity_data in enumerate(test_entities):
                    try:
                        # Create Entity object (may fail for malformed data)
                        entity = Entity(
                            id=f"edge_test_{test_category}_{i}",
                            canonical_name=entity_data.get("name", ""),
                            entity_type=entity_data.get("type", ""),
                            confidence=entity_data.get("confidence", 0.8),
                            quality_tier=QualityTier.LOW,
                            created_by="edge_case_test",
                            created_at=datetime.now(),
                            workflow_id="edge_case_test"
                        )
                        
                        # Test validation
                        validation_result = self.dolce_validator.validate_entity_simple(entity)
                        
                        if validation_result.get("valid", False):
                            category_results["passed"] += 1
                        else:
                            category_results["failed"] += 1
                        
                        category_results["details"].append({
                            "entity_data": entity_data,
                            "validation_result": validation_result
                        })
                        
                    except Exception as e:
                        category_results["failed"] += 1
                        category_results["errors"].append(str(e))
                        category_results["details"].append({
                            "entity_data": entity_data,
                            "error": str(e)
                        })
                
                test_results[test_category] = category_results
            
            # Calculate overall metrics
            total_tests = sum(result["test_count"] for result in test_results.values())
            total_passed = sum(result["passed"] for result in test_results.values())
            total_failed = sum(result["failed"] for result in test_results.values())
            
            test_duration = (datetime.now() - test_start_time).total_seconds()
            
            return {
                "status": "completed",
                "total_edge_case_tests": total_tests,
                "total_passed": total_passed,
                "total_failed": total_failed,
                "pass_rate": total_passed / total_tests if total_tests > 0 else 0,
                "test_categories": test_results,
                "test_duration_seconds": test_duration,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            test_duration = (datetime.now() - test_start_time).total_seconds()
            self.logger.error(f"Edge case testing failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "test_duration_seconds": test_duration,
                "timestamp": datetime.now().isoformat()
            }

    def test_performance_under_load(self, entity_count: int = 1000) -> Dict[str, Any]:
        """Test ontology validation performance under load"""
        test_start_time = datetime.now()
        
        try:
            # Generate large number of test entities
            test_entities = []
            entity_types = ["Person", "Organization", "Location", "Event", "Concept"]
            
            for i in range(entity_count):
                entity_type = entity_types[i % len(entity_types)]
                entity = Entity(
                    id=f"load_test_entity_{i}",
                    canonical_name=f"Test Entity {i}",
                    entity_type=entity_type,
                    confidence=0.5 + (i % 50) / 100.0,  # Vary confidence
                    quality_tier=QualityTier.MEDIUM,
                    created_by="load_test",
                    created_at=datetime.now(),
                    workflow_id="performance_load_test"
                )
                test_entities.append(entity)
            
            # Measure validation performance
            validation_start = datetime.now()
            validation_results = []
            
            for entity in test_entities:
                result = self.dolce_validator.validate_entity_simple(entity)
                validation_results.append(result)
            
            validation_duration = (datetime.now() - validation_start).total_seconds()
            
            # Calculate performance metrics
            successful_validations = sum(1 for r in validation_results if r.get("valid", False))
            avg_validation_time = validation_duration / entity_count
            validations_per_second = entity_count / validation_duration
            
            test_duration = (datetime.now() - test_start_time).total_seconds()
            
            return {
                "status": "completed",
                "entity_count": entity_count,
                "successful_validations": successful_validations,
                "success_rate": successful_validations / entity_count,
                "total_validation_time_seconds": validation_duration,
                "average_validation_time_ms": avg_validation_time * 1000,
                "validations_per_second": validations_per_second,
                "total_test_duration_seconds": test_duration,
                "performance_rating": self._assess_performance_rating(validations_per_second),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            test_duration = (datetime.now() - test_start_time).total_seconds()
            self.logger.error(f"Performance testing failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "test_duration_seconds": test_duration,
                "timestamp": datetime.now().isoformat()
            }

    def _assess_performance_rating(self, validations_per_second: float) -> str:
        """Assess performance rating based on validations per second"""
        if validations_per_second >= 1000:
            return "excellent"
        elif validations_per_second >= 500:
            return "good"
        elif validations_per_second >= 100:
            return "acceptable"
        else:
            return "poor"

    def run_comprehensive_test_suite(self) -> Dict[str, Any]:
        """Run complete comprehensive test suite"""
        suite_start_time = datetime.now()
        
        try:
            # Run all test categories
            dolce_comprehensive_results = self.test_dolce_ontology_comprehensive()
            edge_case_results = self.test_edge_cases_and_stress_scenarios()
            performance_results = self.test_performance_under_load()
            
            # Aggregate results
            all_tests_passed = (
                dolce_comprehensive_results.get("status") == "success" and
                edge_case_results.get("status") == "completed" and
                performance_results.get("status") == "completed"
            )
            
            suite_duration = (datetime.now() - suite_start_time).total_seconds()
            
            return {
                "comprehensive_test_suite_status": "passed" if all_tests_passed else "failed",
                "dolce_comprehensive_test": dolce_comprehensive_results,
                "edge_case_stress_test": edge_case_results,
                "performance_load_test": performance_results,
                "total_suite_duration_seconds": suite_duration,
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "all_tests_passed": all_tests_passed,
                    "dolce_mapping_accuracy": dolce_comprehensive_results.get("mapping_accuracy_percentage", 0),
                    "edge_case_pass_rate": edge_case_results.get("pass_rate", 0) * 100,
                    "performance_rating": performance_results.get("performance_rating", "unknown")
                }
            }
            
        except Exception as e:
            suite_duration = (datetime.now() - suite_start_time).total_seconds()
            self.logger.error(f"Comprehensive test suite failed: {e}")
            return {
                "comprehensive_test_suite_status": "failed",
                "error": str(e),
                "total_suite_duration_seconds": suite_duration,
                "timestamp": datetime.now().isoformat()
            }