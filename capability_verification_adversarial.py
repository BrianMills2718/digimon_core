#!/usr/bin/env python3
"""
Adversarial Capability Verification - Assume every capability is broken until proven otherwise
Goal: Try to prove each of the 571 capabilities doesn't work, document evidence when wrong
"""

import tempfile
import json
import time
import traceback
from pathlib import Path
import sys
import os

class AdversarialCapabilityVerifier:
    def __init__(self):
        self.assumptions_proven_wrong = []  # Evidence that capabilities actually work
        self.confirmed_failures = []  # Capabilities that are actually broken
        self.inconclusive = []  # Can't prove either way
        
    def log_wrong_assumption(self, capability, evidence, test_details):
        """Log when our assumption of failure was wrong - capability actually works"""
        print(f"❌ ASSUMPTION WRONG: {capability}")
        print(f"   Evidence: {evidence}")
        print(f"   Details: {test_details}")
        
        self.assumptions_proven_wrong.append({
            "capability": capability,
            "evidence": evidence,
            "test_details": test_details,
            "timestamp": time.time()
        })
    
    def log_confirmed_failure(self, capability, failure_evidence):
        """Log when capability is actually broken as assumed"""
        print(f"✅ ASSUMPTION CORRECT: {capability} is broken")
        print(f"   Failure: {failure_evidence}")
        
        self.confirmed_failures.append({
            "capability": capability,
            "failure_evidence": failure_evidence,
            "timestamp": time.time()
        })
    
    def log_inconclusive(self, capability, reason):
        """Log when we can't prove capability works or fails"""
        print(f"🤷 INCONCLUSIVE: {capability}")
        print(f"   Reason: {reason}")
        
        self.inconclusive.append({
            "capability": capability,
            "reason": reason,
            "timestamp": time.time()
        })

    def test_phase1_imports_adversarial(self):
        """Assume Phase 1 components can't be imported"""
        print("\n🔥 ASSUMING PHASE 1 IMPORTS WILL FAIL")
        print("=" * 50)
        
        expected_failures = [
            "src.tools.phase1.vertical_slice_workflow",
            "src.tools.phase1.t01_pdf_loader", 
            "src.tools.phase1.t15a_text_chunker",
            "src.tools.phase1.t23a_spacy_ner",
            "src.tools.phase1.t23c_llm_entity_extractor",
            "src.tools.phase1.t27_relationship_extractor",
            "src.tools.phase1.t31_entity_builder",
            "src.tools.phase1.t34_edge_builder",
            "src.tools.phase1.t41_text_embedder",
            "src.tools.phase1.t68_pagerank",
            "src.tools.phase1.t49_multihop_query",
            "src.tools.phase1.phase1_mcp_tools"
        ]
        
        for module_name in expected_failures:
            try:
                # Try to prove import will fail
                exec(f"import {module_name}")
                
                # If we get here, our assumption was wrong
                self.log_wrong_assumption(
                    f"Import_{module_name}",
                    f"Module {module_name} imported successfully", 
                    f"Expected import to fail but: import {module_name} worked"
                )
            except ImportError as e:
                # Our assumption was correct - it failed
                self.log_confirmed_failure(
                    f"Import_{module_name}",
                    f"ImportError: {e}"
                )
            except Exception as e:
                # Unexpected error
                self.log_inconclusive(
                    f"Import_{module_name}",
                    f"Unexpected error: {e}"
                )

    def test_phase1_pdf_processing_adversarial(self):
        """Assume PDF processing will fail"""
        print("\n🔥 ASSUMING PDF PROCESSING WILL FAIL")
        print("=" * 50)
        
        # Create test file that should cause failure
        test_content = "Dr. Smith works at MIT."
        
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(test_content)
                test_file = f.name
            
            # Assume PDF loader will fail
            from src.tools.phase1.t01_pdf_loader import PDFLoader
            loader = PDFLoader()
            
            result = loader.load_pdf(test_file)
            
            # If we get here without exception, our assumption was wrong
            if isinstance(result, dict) and "text" in result:
                text = result["text"]
                confidence = result.get("confidence", 0)
                
                self.log_wrong_assumption(
                    "PDFLoader.load_pdf",
                    f"Loaded text with {len(text)} characters, confidence {confidence}",
                    f"Expected load_pdf to fail but got: {text[:100]}..."
                )
            else:
                self.log_confirmed_failure(
                    "PDFLoader.load_pdf", 
                    f"Invalid result format: {type(result)}"
                )
            
            os.unlink(test_file)
            
        except Exception as e:
            self.log_confirmed_failure(
                "PDFLoader.load_pdf",
                f"Exception: {e}"
            )

    def test_phase1_entity_extraction_adversarial(self):
        """Assume entity extraction will fail"""
        print("\n🔥 ASSUMING ENTITY EXTRACTION WILL FAIL")
        print("=" * 50)
        
        test_text = "Dr. John Smith works at MIT in Boston."
        
        try:
            # Assume spaCy NER will fail
            from src.tools.phase1.t23a_spacy_ner import SpacyNER
            ner = SpacyNER()
            
            result = ner.extract_entities("test_chunk", test_text)
            
            # If we get here, check if it actually worked
            if isinstance(result, dict) and "entities" in result:
                entities = result["entities"]
                if len(entities) > 0:
                    entity_names = [e.get("text", "unknown") for e in entities]
                    self.log_wrong_assumption(
                        "SpacyNER.extract_entities",
                        f"Extracted {len(entities)} entities: {entity_names}",
                        f"Expected extraction to fail but got entities: {entities}"
                    )
                else:
                    self.log_confirmed_failure(
                        "SpacyNER.extract_entities",
                        "No entities extracted from obvious entity text"
                    )
            else:
                self.log_confirmed_failure(
                    "SpacyNER.extract_entities",
                    f"Invalid result format: {type(result)}"
                )
                
        except Exception as e:
            self.log_confirmed_failure(
                "SpacyNER.extract_entities",
                f"Exception: {e}"
            )

    def test_phase1_relationship_extraction_adversarial(self):
        """Assume relationship extraction will fail"""
        print("\n🔥 ASSUMING RELATIONSHIP EXTRACTION WILL FAIL")
        print("=" * 50)
        
        # Create obvious relationship text
        test_text = "Dr. Smith works at MIT. MIT is located in Boston."
        entities = [
            {"text": "Dr. Smith", "type": "PERSON", "start": 0, "end": 9},
            {"text": "MIT", "type": "ORG", "start": 19, "end": 22},
            {"text": "Boston", "type": "GPE", "start": 44, "end": 50}
        ]
        
        try:
            from src.tools.phase1.t27_relationship_extractor import RelationshipExtractor
            extractor = RelationshipExtractor()
            
            result = extractor.extract_relationships("test_chunk", test_text, entities)
            
            if isinstance(result, dict) and "relationships" in result:
                relationships = result["relationships"]
                if len(relationships) > 0:
                    rel_summary = [(r.get("subject"), r.get("predicate"), r.get("object")) for r in relationships]
                    self.log_wrong_assumption(
                        "RelationshipExtractor.extract_relationships",
                        f"Extracted {len(relationships)} relationships: {rel_summary}",
                        f"Expected relationship extraction to fail but got: {relationships}"
                    )
                else:
                    self.log_confirmed_failure(
                        "RelationshipExtractor.extract_relationships",
                        "No relationships extracted from obvious relationship text"
                    )
            else:
                self.log_confirmed_failure(
                    "RelationshipExtractor.extract_relationships",
                    f"Invalid result format: {type(result)}"
                )
                
        except Exception as e:
            self.log_confirmed_failure(
                "RelationshipExtractor.extract_relationships",
                f"Exception: {e}"
            )

    def test_phase1_workflow_adversarial(self):
        """Assume complete Phase 1 workflow will fail"""
        print("\n🔥 ASSUMING PHASE 1 WORKFLOW WILL FAIL")
        print("=" * 50)
        
        # Use the celestial council test file 
        test_file = "/home/brian/Digimons/test_data/celestial_council/burisch_timeline.txt"
        
        if not os.path.exists(test_file):
            self.log_inconclusive(
                "Phase1Workflow.execute_workflow",
                f"Test file not found: {test_file}"
            )
            return
        
        try:
            from src.tools.phase1.vertical_slice_workflow import VerticalSliceWorkflow
            workflow = VerticalSliceWorkflow()
            
            start_time = time.time()
            result = workflow.execute_workflow(
                test_file,
                "What are the main entities and relationships?",
                "adversarial_test"
            )
            duration = time.time() - start_time
            
            # Analyze result to see if our failure assumption was wrong
            if isinstance(result, dict):
                status = result.get("status", "unknown")
                steps = result.get("steps", {})
                
                if status == "success":
                    entity_step = steps.get("entity_extraction", {})
                    rel_step = steps.get("relationship_extraction", {})
                    
                    entities = entity_step.get("total_entities", 0)
                    relationships = rel_step.get("total_relationships", 0)
                    
                    if entities > 0 or relationships > 0:
                        self.log_wrong_assumption(
                            "Phase1Workflow.execute_workflow",
                            f"Processed successfully: {entities} entities, {relationships} relationships in {duration:.2f}s",
                            f"Expected workflow to fail but completed with status={status}, entities={entities}, relationships={relationships}"
                        )
                    else:
                        self.log_confirmed_failure(
                            "Phase1Workflow.execute_workflow",
                            "Workflow completed but extracted no entities or relationships"
                        )
                else:
                    self.log_confirmed_failure(
                        "Phase1Workflow.execute_workflow", 
                        f"Workflow failed with status: {status}, error: {result.get('error')}"
                    )
            else:
                self.log_confirmed_failure(
                    "Phase1Workflow.execute_workflow",
                    f"Invalid result type: {type(result)}"
                )
                
        except Exception as e:
            self.log_confirmed_failure(
                "Phase1Workflow.execute_workflow",
                f"Exception: {e}"
            )

    def test_mcp_tools_adversarial(self):
        """Assume MCP tools will fail"""
        print("\n🔥 ASSUMING MCP TOOLS WILL FAIL")
        print("=" * 50)
        
        try:
            from src.tools.phase1.phase1_mcp_tools import Phase1MCPTools
            tools = Phase1MCPTools()
            
            # Test individual MCP tool - assume it will fail
            test_text = "Dr. Smith works at MIT."
            result = tools.extract_entities("test_chunk", test_text)
            
            if isinstance(result, dict) and "entities" in result:
                entities = result["entities"]
                if len(entities) > 0:
                    self.log_wrong_assumption(
                        "MCPTools.extract_entities",
                        f"MCP tool extracted {len(entities)} entities successfully",
                        f"Expected MCP tool to fail but extracted: {entities}"
                    )
                else:
                    self.log_confirmed_failure(
                        "MCPTools.extract_entities",
                        "MCP tool returned no entities"
                    )
            else:
                self.log_confirmed_failure(
                    "MCPTools.extract_entities",
                    f"Invalid MCP result format: {type(result)}"
                )
                
        except Exception as e:
            self.log_confirmed_failure(
                "MCPTools.extract_entities",
                f"Exception: {e}"
            )

    def test_phase2_adversarial(self):
        """Assume Phase 2 capabilities will fail"""
        print("\n🔥 ASSUMING PHASE 2 WILL FAIL")
        print("=" * 50)
        
        # Create simple test file
        test_content = "Dr. Smith works at MIT."
        
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(test_content)
                test_file = f.name
            
            from src.tools.phase2.enhanced_vertical_slice_workflow import EnhancedVerticalSliceWorkflow
            workflow = EnhancedVerticalSliceWorkflow()
            
            result = workflow.execute_enhanced_workflow(
                test_file,
                "What are the main entities?", 
                "adversarial_phase2_test"
            )
            
            # Check if our assumption was wrong
            if isinstance(result, dict):
                entities = result.get("entities", [])
                relationships = result.get("relationships", [])
                
                if len(entities) > 0 or len(relationships) > 0:
                    self.log_wrong_assumption(
                        "Phase2.enhanced_workflow",
                        f"Phase 2 worked: {len(entities)} entities, {len(relationships)} relationships",
                        f"Expected Phase 2 to fail but got entities: {entities}, relationships: {relationships}"
                    )
                else:
                    self.log_confirmed_failure(
                        "Phase2.enhanced_workflow",
                        "Phase 2 completed but extracted no entities or relationships"
                    )
            else:
                self.log_confirmed_failure(
                    "Phase2.enhanced_workflow",
                    f"Invalid result format: {type(result)}"
                )
            
            os.unlink(test_file)
            
        except Exception as e:
            self.log_confirmed_failure(
                "Phase2.enhanced_workflow",
                f"Exception: {e}"
            )

    def test_phase3_adversarial(self):
        """Assume Phase 3 capabilities will fail"""
        print("\n🔥 ASSUMING PHASE 3 WILL FAIL")
        print("=" * 50)
        
        # Create test files
        test_files = []
        test_contents = [
            "Dr. Smith works at MIT.",
            "Dr. Smith is a professor at MIT.", 
        ]
        
        try:
            for i, content in enumerate(test_contents):
                with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                    f.write(content)
                    test_files.append(f.name)
            
            from src.core.phase_adapters import Phase3Adapter
            from src.core.graphrag_phase_interface import ProcessingRequest
            
            phase3 = Phase3Adapter()
            request = ProcessingRequest(
                workflow_id="adversarial_phase3_test",
                documents=test_files,
                queries=["Who is Dr. Smith?"],
                domain_description="Test multi-document processing"
            )
            
            result = phase3.execute(request)
            
            # Check if our assumption was wrong  
            if result.status.name == "SUCCESS":
                processing_summary = result.results.get("processing_summary", {})
                total_entities = processing_summary.get("total_entities_after_fusion", 0)
                
                if total_entities > 0:
                    self.log_wrong_assumption(
                        "Phase3.multi_document_fusion",
                        f"Phase 3 worked: {total_entities} entities after fusion",
                        f"Expected Phase 3 to fail but got fusion result: {processing_summary}"
                    )
                else:
                    self.log_confirmed_failure(
                        "Phase3.multi_document_fusion",
                        "Phase 3 completed but no entities after fusion"
                    )
            else:
                self.log_confirmed_failure(
                    "Phase3.multi_document_fusion",
                    f"Phase 3 failed: {result.error_message}"
                )
            
            # Cleanup
            for f in test_files:
                os.unlink(f)
                
        except Exception as e:
            self.log_confirmed_failure(
                "Phase3.multi_document_fusion",
                f"Exception: {e}"
            )

    def test_neo4j_integration_adversarial(self):
        """Assume Neo4j integration will fail"""
        print("\n🔥 ASSUMING NEO4J INTEGRATION WILL FAIL")
        print("=" * 50)
        
        try:
            from src.tools.base_neo4j_tool import BaseNeo4jTool
            tool = BaseNeo4jTool()
            
            # Try simple query - assume it will fail
            result = tool._execute_read_query("MATCH (n) RETURN count(n) as node_count")
            
            if result is not None and len(result) > 0:
                node_count = result[0].get("node_count", 0)
                self.log_wrong_assumption(
                    "Neo4j.connection_and_query",
                    f"Neo4j connected and returned {node_count} nodes",
                    f"Expected Neo4j to fail but got result: {result}"
                )
            else:
                self.log_confirmed_failure(
                    "Neo4j.connection_and_query",
                    f"Neo4j query returned empty or null result: {result}"
                )
                
        except Exception as e:
            self.log_confirmed_failure(
                "Neo4j.connection_and_query",
                f"Exception: {e}"
            )

    def generate_adversarial_report(self):
        """Generate report showing assumptions that were wrong vs confirmed failures"""
        print("\n" + "=" * 80)
        print("🧪 ADVERSARIAL VERIFICATION REPORT")
        print("=" * 80)
        
        total_tests = len(self.assumptions_proven_wrong) + len(self.confirmed_failures) + len(self.inconclusive)
        
        print(f"📊 SUMMARY:")
        print(f"   Total Capabilities Tested: {total_tests}")
        print(f"   Assumptions WRONG (capabilities work): {len(self.assumptions_proven_wrong)}")
        print(f"   Assumptions CORRECT (capabilities broken): {len(self.confirmed_failures)}")
        print(f"   Inconclusive: {len(self.inconclusive)}")
        
        if len(self.assumptions_proven_wrong) > 0:
            print(f"\n❌ EVIDENCE THAT CONTRADICTS FAILURE ASSUMPTIONS:")
            for item in self.assumptions_proven_wrong:
                print(f"   • {item['capability']}: {item['evidence']}")
        
        if len(self.confirmed_failures) > 0:
            print(f"\n✅ CONFIRMED FAILURES (as expected):")
            for item in self.confirmed_failures:
                print(f"   • {item['capability']}: {item['failure_evidence']}")
        
        if len(self.inconclusive) > 0:
            print(f"\n🤷 INCONCLUSIVE TESTS:")
            for item in self.inconclusive:
                print(f"   • {item['capability']}: {item['reason']}")
        
        # Save detailed report
        report_file = f"adversarial_verification_report_{int(time.time())}.json"
        with open(report_file, 'w') as f:
            json.dump({
                "summary": {
                    "total_tests": total_tests,
                    "assumptions_proven_wrong": len(self.assumptions_proven_wrong),
                    "confirmed_failures": len(self.confirmed_failures),
                    "inconclusive": len(self.inconclusive),
                    "working_capabilities_rate": len(self.assumptions_proven_wrong) / total_tests * 100 if total_tests > 0 else 0
                },
                "evidence_capabilities_work": self.assumptions_proven_wrong,
                "confirmed_failures": self.confirmed_failures,
                "inconclusive": self.inconclusive
            }, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        
        if len(self.assumptions_proven_wrong) > len(self.confirmed_failures):
            print(f"\n🎉 SURPRISING RESULT: More capabilities work than expected!")
            print(f"    Evidence contradicts {len(self.assumptions_proven_wrong)} failure assumptions")
        else:
            print(f"\n⚠️ EXPECTED RESULT: Most capabilities are broken as assumed")
        
        return len(self.assumptions_proven_wrong)

def main():
    print("🔥 ADVERSARIAL CAPABILITY VERIFICATION")
    print("ASSUMPTION: All 571 capabilities are broken until proven otherwise")
    print("GOAL: Find evidence that proves assumptions wrong")
    print("=" * 80)
    
    verifier = AdversarialCapabilityVerifier()
    
    # Run adversarial tests - try to prove everything is broken
    verifier.test_phase1_imports_adversarial()
    verifier.test_phase1_pdf_processing_adversarial()
    verifier.test_phase1_entity_extraction_adversarial()
    verifier.test_phase1_relationship_extraction_adversarial()
    verifier.test_phase1_workflow_adversarial()
    verifier.test_mcp_tools_adversarial()
    verifier.test_phase2_adversarial()
    verifier.test_phase3_adversarial()
    verifier.test_neo4j_integration_adversarial()
    
    # Generate report
    working_capabilities = verifier.generate_adversarial_report()
    
    return 0

if __name__ == "__main__":
    exit(main())