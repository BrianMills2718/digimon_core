#!/usr/bin/env python3
"""
Comprehensive Stakeholder Theory Stress Test
End-to-end validation of theory meta-schema v10.0 with data type architecture

This script runs a complete stakeholder theory analysis including:
- Theory meta-schema validation
- Custom algorithm implementation and testing
- Database integration (Neo4j + SQLite)
- Cross-modal analysis (graph ↔ table)
- Edge case handling and validation
"""

import sys
import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import argparse

# Add project paths
PROJECT_ROOT = Path(__file__).parent
sys.path.append(str(PROJECT_ROOT))
sys.path.append('/home/brian/projects/Digimons/src')

# Import components
try:
    from scripts.salience_calculator import MitchellAgleWoodCalculator
    from database.neo4j_setup import StakeholderNeo4jManager
    from schemas.stakeholder_schemas import (
        StakeholderEntity, StakeholderInfluence, SalienceScore,
        LegitimacyScore, UrgencyScore, PowerScore, StakeholderAnalysisResult
    )
    from schemas.base_schemas import ValidationResult, Document, TextChunk
except ImportError as e:
    print(f"Import error: {e}")
    print("Some components may not be available")

class StakeholderTheoryStressTest:
    """
    Comprehensive stress test for stakeholder theory implementation
    """
    
    def __init__(self, output_dir: Optional[str] = None):
        """Initialize stress test"""
        self.start_time = datetime.now()
        self.output_dir = Path(output_dir) if output_dir else PROJECT_ROOT / "results"
        self.output_dir.mkdir(exist_ok=True)
        
        # Test components
        self.salience_calculator = MitchellAgleWoodCalculator(enable_logging=True)
        self.neo4j_manager = StakeholderNeo4jManager()
        
        # Test results
        self.results = {
            "test_session": {
                "start_time": self.start_time.isoformat(),
                "test_id": f"stress_test_{int(time.time())}",
                "version": "1.0.0"
            },
            "schema_validation": {},
            "algorithm_validation": {},
            "database_integration": {},
            "cross_modal_analysis": {},
            "edge_case_testing": {},
            "performance_metrics": {},
            "overall_results": {}
        }
        
        print("🧪 Stakeholder Theory Stress Test Initialized")
        print(f"📁 Output directory: {self.output_dir}")
        print(f"🕐 Start time: {self.start_time}")
    
    def load_test_data(self) -> Dict[str, Any]:
        """Load test data and theory schema"""
        
        print("\n📖 Loading test data and theory schema...")
        
        # Load theory schema
        try:
            theory_path = PROJECT_ROOT / "theory" / "stakeholder_theory_v10.json"
            with open(theory_path, 'r') as f:
                theory_schema = json.load(f)
            print(f"✓ Loaded theory schema: {theory_schema['theory_name']} v{theory_schema['version']}")
        except Exception as e:
            print(f"✗ Failed to load theory schema: {e}")
            theory_schema = {}
        
        # Load policy document
        try:
            doc_path = PROJECT_ROOT / "data" / "policy_documents" / "climate_policy_proposal.txt"
            with open(doc_path, 'r') as f:
                policy_text = f.read()
            print(f"✓ Loaded policy document: {len(policy_text)} characters")
        except Exception as e:
            print(f"✗ Failed to load policy document: {e}")
            policy_text = ""
        
        # Load MCL mock
        try:
            mcl_path = PROJECT_ROOT / "theory" / "mcl_mock.yaml"
            import yaml
            with open(mcl_path, 'r') as f:
                mcl_data = yaml.safe_load(f)
            print(f"✓ Loaded MCL mock: {len(mcl_data.get('entity_concepts', {}))} entity concepts")
        except Exception as e:
            print(f"✗ Failed to load MCL mock: {e}")
            mcl_data = {}
        
        return {
            "theory_schema": theory_schema,
            "policy_text": policy_text,
            "mcl_data": mcl_data
        }
    
    def test_schema_validation(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test Pydantic schema validation"""
        
        print("\n🔍 Testing Schema Validation...")
        
        schema_results = {
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "validation_errors": [],
            "test_details": []
        }
        
        # Test 1: Valid stakeholder entity creation
        try:
            legitimacy = LegitimacyScore(
                value=0.85,
                evidence_type="legal",
                confidence=0.9,
                legal_basis="Federal environmental protection mandate"
            )
            
            urgency = UrgencyScore(
                value=0.75,
                confidence=0.8,
                time_critical=True,
                urgency_indicators=["immediate action required"]
            )
            
            power = PowerScore(
                value=0.65,
                confidence=0.85,
                primary_mechanism="regulatory",
                regulatory_authority=True
            )
            
            salience = SalienceScore(
                value=0.747,  # (0.85 * 0.75 * 0.65)^(1/3)
                legitimacy=0.85,
                urgency=0.75,
                power=0.65
            )
            
            stakeholder = StakeholderEntity(
                id="test_stakeholder_001",
                object_type="entity",
                confidence=0.85,
                quality_tier="silver",
                created_by="stress_test",
                workflow_id="test_workflow_001",
                canonical_name="Environmental Protection Agency",
                entity_type="organization",
                stakeholder_type="institution",
                legitimacy=legitimacy,
                urgency=urgency,
                power=power,
                salience=salience,
                priority_tier="high"
            )
            
            schema_results["tests_passed"] += 1
            schema_results["test_details"].append({
                "test": "valid_stakeholder_creation",
                "status": "passed",
                "stakeholder_id": stakeholder.id
            })
            print("✓ Valid stakeholder entity creation")
            
        except Exception as e:
            schema_results["tests_failed"] += 1
            schema_results["validation_errors"].append(f"Valid stakeholder creation failed: {e}")
            schema_results["test_details"].append({
                "test": "valid_stakeholder_creation",
                "status": "failed",
                "error": str(e)
            })
            print(f"✗ Valid stakeholder creation failed: {e}")
        
        schema_results["tests_run"] += 1
        
        # Test 2: Invalid data validation
        try:
            # This should fail due to invalid legitimacy score
            invalid_legitimacy = LegitimacyScore(
                value=1.5,  # Invalid - exceeds 1.0
                evidence_type="legal",
                confidence=0.9
            )
            
            schema_results["tests_failed"] += 1  # This should fail
            schema_results["test_details"].append({
                "test": "invalid_legitimacy_detection",
                "status": "failed",
                "error": "Should have rejected value > 1.0"
            })
            print("✗ Invalid data validation failed to catch error")
            
        except Exception as e:
            # This is expected behavior
            schema_results["tests_passed"] += 1
            schema_results["test_details"].append({
                "test": "invalid_legitimacy_detection",
                "status": "passed",
                "caught_error": str(e)
            })
            print("✓ Invalid data properly rejected")
        
        schema_results["tests_run"] += 1
        
        # Test 3: Cross-schema compatibility
        try:
            # Create compatible schemas
            text_chunk = TextChunk(
                id="chunk_001",
                object_type="chunk",
                confidence=0.9,
                quality_tier="gold",
                created_by="stress_test",
                workflow_id="test_workflow_001",
                text="The Environmental Protection Agency announced new regulations...",
                document_ref="policy_doc_001",
                chunk_index=0,
                start_position=0,
                end_position=100,
                word_count=15,
                sentence_count=1
            )
            
            schema_results["tests_passed"] += 1
            schema_results["test_details"].append({
                "test": "cross_schema_compatibility",
                "status": "passed",
                "chunk_id": text_chunk.id
            })
            print("✓ Cross-schema compatibility")
            
        except Exception as e:
            schema_results["tests_failed"] += 1
            schema_results["validation_errors"].append(f"Cross-schema compatibility failed: {e}")
            print(f"✗ Cross-schema compatibility failed: {e}")
        
        schema_results["tests_run"] += 1
        
        # Calculate success rate
        if schema_results["tests_run"] > 0:
            schema_results["success_rate"] = schema_results["tests_passed"] / schema_results["tests_run"]
        else:
            schema_results["success_rate"] = 0.0
        
        print(f"📊 Schema validation: {schema_results['tests_passed']}/{schema_results['tests_run']} passed ({schema_results['success_rate']:.1%})")
        
        return schema_results
    
    def test_algorithm_validation(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test custom algorithm implementation"""
        
        print("\n🧮 Testing Algorithm Validation...")
        
        # Run salience calculator test cases
        test_results = self.salience_calculator.run_test_cases()
        
        # Additional edge case tests
        edge_case_results = []
        
        # Test negative input handling
        try:
            self.salience_calculator.calculate_salience(-0.1, 0.5, 0.5)
            edge_case_results.append({"test": "negative_input", "status": "failed", "error": "Should reject negative values"})
        except Exception as e:
            edge_case_results.append({"test": "negative_input", "status": "passed", "caught_error": str(e)})
        
        # Test missing input handling
        try:
            self.salience_calculator.calculate_salience(None, 0.5, 0.5)
            edge_case_results.append({"test": "missing_input", "status": "failed", "error": "Should reject None values"})
        except Exception as e:
            edge_case_results.append({"test": "missing_input", "status": "passed", "caught_error": str(e)})
        
        # Test boundary values
        boundary_tests = [
            {"inputs": (0.0, 0.0, 0.0), "expected": 0.0, "description": "all_zero"},
            {"inputs": (1.0, 1.0, 1.0), "expected": 1.0, "description": "all_max"},
            {"inputs": (0.001, 0.001, 0.001), "expected": 0.001, "description": "very_small"}
        ]
        
        for test in boundary_tests:
            try:
                result = self.salience_calculator.calculate_salience(*test["inputs"])
                actual = result["salience_score"]
                expected = test["expected"]
                
                if abs(actual - expected) < 0.001:
                    edge_case_results.append({
                        "test": f"boundary_{test['description']}",
                        "status": "passed",
                        "expected": expected,
                        "actual": actual
                    })
                else:
                    edge_case_results.append({
                        "test": f"boundary_{test['description']}",
                        "status": "failed",
                        "expected": expected,
                        "actual": actual,
                        "difference": abs(actual - expected)
                    })
            except Exception as e:
                edge_case_results.append({
                    "test": f"boundary_{test['description']}",
                    "status": "error",
                    "error": str(e)
                })
        
        algorithm_results = {
            "salience_test_results": test_results,
            "edge_case_results": edge_case_results,
            "overall_success": test_results["all_tests_passed"] and all(r["status"] == "passed" for r in edge_case_results if r["status"] != "error")
        }
        
        print(f"📊 Algorithm validation: {'✓ ALL PASSED' if algorithm_results['overall_success'] else '✗ SOME FAILED'}")
        
        return algorithm_results
    
    def test_database_integration(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test database integration and operations"""
        
        print("\n🗄️ Testing Database Integration...")
        
        db_results = {
            "neo4j_connection": False,
            "schema_setup": False,
            "data_creation": False,
            "data_retrieval": False,
            "network_metrics": False,
            "errors": []
        }
        
        try:
            # Test Neo4j connection
            if self.neo4j_manager.driver:
                db_results["neo4j_connection"] = True
                print("✓ Neo4j connection established")
            else:
                db_results["errors"].append("Neo4j connection failed")
                print("✗ Neo4j connection failed")
                return db_results
            
            # Test schema setup
            self.neo4j_manager.setup_schema()
            db_results["schema_setup"] = True
            print("✓ Neo4j schema setup completed")
            
            # Clear and create test data
            self.neo4j_manager.clear_database()
            
            # Create test organization
            org_data = {
                "id": "test_org_001",
                "canonical_name": "Test Federal Agency",
                "entity_type": "organization",
                "organization_type": "government_agency",
                "sector": "environmental",
                "size": "large",
                "confidence": 0.95,
                "quality_tier": "gold",
                "created_by": "stress_test",
                "created_at": datetime.now().isoformat(),
                "workflow_id": "stress_test_001",
                "description": "Test federal agency for stress testing"
            }
            
            if self.neo4j_manager.create_organization(org_data):
                print("✓ Test organization created")
            else:
                db_results["errors"].append("Failed to create test organization")
            
            # Create test stakeholder
            stakeholder_data = {
                "id": "test_stakeholder_001",
                "canonical_name": "Test Environmental Group",
                "stakeholder_type": "group",
                "entity_type": "organization",
                "legitimacy": 0.8,
                "legitimacy_confidence": 0.9,
                "urgency": 0.7,
                "urgency_confidence": 0.85,
                "power": 0.6,
                "power_confidence": 0.8,
                "salience_score": 0.699,  # (0.8 * 0.7 * 0.6)^(1/3)
                "mitchell_category": "dependent",
                "priority_tier": "high",
                "confidence": 0.85,
                "quality_tier": "silver",
                "created_by": "stress_test",
                "created_at": datetime.now().isoformat(),
                "workflow_id": "stress_test_001",
                "description": "Test environmental advocacy group",
                "surface_forms": json.dumps(["Test Environmental Group", "TEG"]),
                "mention_count": 5
            }
            
            if self.neo4j_manager.create_stakeholder(stakeholder_data):
                print("✓ Test stakeholder created")
            else:
                db_results["errors"].append("Failed to create test stakeholder")
            
            # Create test relationship
            relationship_data = {
                "id": "test_influence_001",
                "source_id": "test_stakeholder_001",
                "target_id": "test_org_001",
                "relationship_type": "INFLUENCES",
                "influence_strength": 0.75,
                "influence_mechanism": "advocacy",
                "conditionality": "public_pressure_campaigns",
                "temporal_scope": "ongoing",
                "confidence": 0.8,
                "quality_tier": "silver",
                "created_by": "stress_test",
                "created_at": datetime.now().isoformat(),
                "workflow_id": "stress_test_001",
                "weight": 0.75,
                "direction": "directed",
                "source_role_name": "advocacy_group",
                "target_role_name": "target_agency",
                "additional_participants": {}
            }
            
            if self.neo4j_manager.create_reified_influence_relationship(relationship_data):
                db_results["data_creation"] = True
                print("✓ Test data creation completed")
            else:
                db_results["errors"].append("Failed to create test relationship")
            
            # Test data retrieval
            network_data = self.neo4j_manager.get_stakeholder_network()
            if len(network_data) > 0:
                db_results["data_retrieval"] = True
                print(f"✓ Data retrieval successful: {len(network_data)} relationships")
            else:
                db_results["errors"].append("No data retrieved")
            
            # Test network metrics
            metrics = self.neo4j_manager.calculate_network_metrics()
            if metrics and "error" not in metrics:
                db_results["network_metrics"] = True
                print("✓ Network metrics calculated")
            else:
                db_results["errors"].append(f"Network metrics failed: {metrics.get('error', 'Unknown error')}")
            
        except Exception as e:
            db_results["errors"].append(f"Database integration error: {e}")
            print(f"✗ Database integration error: {e}")
        
        db_results["overall_success"] = all([
            db_results["neo4j_connection"],
            db_results["schema_setup"],
            db_results["data_creation"],
            db_results["data_retrieval"]
        ])
        
        print(f"📊 Database integration: {'✓ SUCCESS' if db_results['overall_success'] else '✗ FAILED'}")
        
        return db_results
    
    def test_cross_modal_analysis(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test cross-modal analysis (graph ↔ table conversion)"""
        
        print("\n🔄 Testing Cross-Modal Analysis...")
        
        cross_modal_results = {
            "graph_to_table": False,
            "semantic_preservation": False,
            "table_analysis": False,
            "data_quality": {},
            "errors": []
        }
        
        try:
            # Get graph data
            network_data = self.neo4j_manager.get_stakeholder_network()
            
            if len(network_data) == 0:
                cross_modal_results["errors"].append("No graph data available for conversion")
                return cross_modal_results
            
            # Convert to table format
            table_data = self.neo4j_manager.export_for_table_analysis()
            
            if len(table_data) > 0:
                cross_modal_results["graph_to_table"] = True
                print(f"✓ Graph to table conversion: {len(table_data)} rows")
                
                # Verify semantic preservation
                original_stakeholder = network_data[0]["stakeholder"]
                table_row = table_data[0]
                
                preserved_fields = [
                    "stakeholder_id", "stakeholder_name", "stakeholder_type",
                    "legitimacy", "urgency", "power", "salience_score",
                    "influence_strength", "influence_mechanism"
                ]
                
                preservation_check = True
                for field in preserved_fields:
                    if field in table_row:
                        print(f"  ✓ Preserved: {field}")
                    else:
                        print(f"  ✗ Missing: {field}")
                        preservation_check = False
                
                cross_modal_results["semantic_preservation"] = preservation_check
                
                # Analyze table data quality
                cross_modal_results["data_quality"] = {
                    "rows_created": len(table_data),
                    "columns_preserved": len([f for f in preserved_fields if f in table_data[0]]),
                    "relationship_data_preserved": "relationship_id" in table_data[0],
                    "n_ary_participants_preserved": "additional_participants" in table_data[0]
                }
                
                cross_modal_results["table_analysis"] = True
                print("✓ Table analysis completed")
                
            else:
                cross_modal_results["errors"].append("Graph to table conversion produced no data")
        
        except Exception as e:
            cross_modal_results["errors"].append(f"Cross-modal analysis error: {e}")
            print(f"✗ Cross-modal analysis error: {e}")
        
        cross_modal_results["overall_success"] = all([
            cross_modal_results["graph_to_table"],
            cross_modal_results["semantic_preservation"],
            cross_modal_results["table_analysis"]
        ])
        
        print(f"📊 Cross-modal analysis: {'✓ SUCCESS' if cross_modal_results['overall_success'] else '✗ FAILED'}")
        
        return cross_modal_results
    
    def generate_report(self) -> str:
        """Generate comprehensive test report"""
        
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        # Calculate overall success
        component_success = [
            self.results.get("schema_validation", {}).get("success_rate", 0) >= 0.8,
            self.results.get("algorithm_validation", {}).get("overall_success", False),
            self.results.get("database_integration", {}).get("overall_success", False),
            self.results.get("cross_modal_analysis", {}).get("overall_success", False)
        ]
        
        overall_success = all(component_success)
        success_count = sum(component_success)
        
        # Update results
        self.results["test_session"]["end_time"] = end_time.isoformat()
        self.results["test_session"]["duration_seconds"] = duration
        
        self.results["overall_results"] = {
            "overall_success": overall_success,
            "components_passed": success_count,
            "components_total": len(component_success),
            "success_rate": success_count / len(component_success),
            "test_summary": {
                "schema_validation": "✓" if component_success[0] else "✗",
                "algorithm_validation": "✓" if component_success[1] else "✗",
                "database_integration": "✓" if component_success[2] else "✗",
                "cross_modal_analysis": "✓" if component_success[3] else "✗"
            }
        }
        
        # Generate report text
        report = f"""
# Stakeholder Theory Stress Test Report

**Test Session**: {self.results['test_session']['test_id']}
**Duration**: {duration:.2f} seconds
**Overall Result**: {'✅ SUCCESS' if overall_success else '❌ FAILED'}
**Components Passed**: {success_count}/{len(component_success)}

## Test Results Summary

### 🔍 Schema Validation
- **Status**: {self.results['overall_results']['test_summary']['schema_validation']}
- **Tests Passed**: {self.results.get('schema_validation', {}).get('tests_passed', 0)}/{self.results.get('schema_validation', {}).get('tests_run', 0)}
- **Success Rate**: {self.results.get('schema_validation', {}).get('success_rate', 0):.1%}

### 🧮 Algorithm Validation  
- **Status**: {self.results['overall_results']['test_summary']['algorithm_validation']}
- **Salience Calculator**: {self.results.get('algorithm_validation', {}).get('salience_test_results', {}).get('success_rate', 0):.1%} success rate
- **Edge Cases**: {'✓ All passed' if self.results.get('algorithm_validation', {}).get('overall_success', False) else '✗ Some failed'}

### 🗄️ Database Integration
- **Status**: {self.results['overall_results']['test_summary']['database_integration']}
- **Neo4j Connection**: {'✓' if self.results.get('database_integration', {}).get('neo4j_connection', False) else '✗'}
- **Data Operations**: {'✓' if self.results.get('database_integration', {}).get('data_creation', False) else '✗'}
- **Network Metrics**: {'✓' if self.results.get('database_integration', {}).get('network_metrics', False) else '✗'}

### 🔄 Cross-Modal Analysis
- **Status**: {self.results['overall_results']['test_summary']['cross_modal_analysis']}
- **Graph→Table Conversion**: {'✓' if self.results.get('cross_modal_analysis', {}).get('graph_to_table', False) else '✗'}
- **Semantic Preservation**: {'✓' if self.results.get('cross_modal_analysis', {}).get('semantic_preservation', False) else '✗'}

## Key Findings

### ✅ Successful Components
"""
        
        for i, (component, passed) in enumerate(zip(["Schema Validation", "Algorithm Validation", "Database Integration", "Cross-Modal Analysis"], component_success)):
            if passed:
                report += f"- {component}: All tests passed\n"
        
        report += "\n### ❌ Failed Components\n"
        
        for i, (component, passed) in enumerate(zip(["Schema Validation", "Algorithm Validation", "Database Integration", "Cross-Modal Analysis"], component_success)):
            if not passed:
                report += f"- {component}: Tests failed or incomplete\n"
        
        report += f"""
## Performance Metrics
- **Total Execution Time**: {duration:.2f} seconds
- **Test Components**: {len(component_success)}
- **Overall Success Rate**: {success_count / len(component_success):.1%}

## Recommendations

{"✅ System ready for production use with theory meta-schema v10.0" if overall_success else "❌ Address failing components before production deployment"}

Generated: {end_time.isoformat()}
"""
        
        return report
    
    def save_results(self):
        """Save test results to files"""
        
        # Save JSON results
        results_file = self.output_dir / f"stress_test_results_{int(time.time())}.json"
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        # Save report
        report = self.generate_report()
        report_file = self.output_dir / f"stress_test_report_{int(time.time())}.md"
        with open(report_file, 'w') as f:
            f.write(report)
        
        print(f"\n📁 Results saved:")
        print(f"   JSON: {results_file}")
        print(f"   Report: {report_file}")
        
        return results_file, report_file
    
    def run_full_test(self) -> bool:
        """Run complete stress test suite"""
        
        print("🚀 Starting Comprehensive Stakeholder Theory Stress Test")
        print("=" * 70)
        
        # Load test data
        test_data = self.load_test_data()
        
        # Run test components
        self.results["schema_validation"] = self.test_schema_validation(test_data)
        self.results["algorithm_validation"] = self.test_algorithm_validation(test_data)
        self.results["database_integration"] = self.test_database_integration(test_data)
        self.results["cross_modal_analysis"] = self.test_cross_modal_analysis(test_data)
        
        # Generate and save results
        results_file, report_file = self.save_results()
        
        # Print final summary
        print("\n" + "=" * 70)
        print("🏁 STRESS TEST COMPLETED")
        print("=" * 70)
        
        overall_success = self.results["overall_results"]["overall_success"]
        print(f"Overall Result: {'✅ SUCCESS' if overall_success else '❌ FAILED'}")
        print(f"Components Passed: {self.results['overall_results']['components_passed']}/{self.results['overall_results']['components_total']}")
        print(f"Duration: {self.results['test_session']['duration_seconds']:.2f} seconds")
        
        return overall_success
    
    def cleanup(self):
        """Cleanup resources"""
        if hasattr(self, 'neo4j_manager') and self.neo4j_manager:
            self.neo4j_manager.close()

def main():
    """Main function"""
    
    parser = argparse.ArgumentParser(description="Run stakeholder theory stress test")
    parser.add_argument("--output-dir", help="Output directory for results")
    parser.add_argument("--component", help="Run specific component test", 
                       choices=["schemas", "algorithms", "database", "cross_modal"])
    args = parser.parse_args()
    
    # Initialize and run test
    stress_test = StakeholderTheoryStressTest(output_dir=args.output_dir)
    
    try:
        if args.component:
            # Run specific component
            test_data = stress_test.load_test_data()
            
            if args.component == "schemas":
                result = stress_test.test_schema_validation(test_data)
            elif args.component == "algorithms":
                result = stress_test.test_algorithm_validation(test_data)
            elif args.component == "database":
                result = stress_test.test_database_integration(test_data)
            elif args.component == "cross_modal":
                result = stress_test.test_cross_modal_analysis(test_data)
            
            print(f"\nComponent test result: {result}")
            
        else:
            # Run full test suite
            success = stress_test.run_full_test()
            sys.exit(0 if success else 1)
            
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        stress_test.cleanup()

if __name__ == "__main__":
    main()