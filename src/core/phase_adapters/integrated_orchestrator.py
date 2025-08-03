"""
Integrated Pipeline Orchestrator

Orchestrates integrated data flow between phases with comprehensive
error handling and evidence collection.
"""

import logging
from typing import Dict, Any, List

from ..graphrag_phase_interface import ProcessingRequest, PhaseStatus
from .phase1_adapter import Phase1Adapter
from .phase2_adapter import Phase2Adapter
from .phase3_adapter import Phase3Adapter
from .adapter_utils import AdapterUtils
from ..logging_config import get_logger

logger = logging.getLogger(__name__)


class IntegratedPipelineOrchestrator:
    """Orchestrates integrated data flow between phases"""
    
    def __init__(self, auto_start_neo4j: bool = True):
        self.logger = get_logger("core.integrated_orchestrator")
        
        # Auto-start Neo4j if requested and needed
        if auto_start_neo4j:
            try:
                from ..neo4j_manager import ensure_neo4j_for_testing
                ensure_neo4j_for_testing()
            except ImportError:
                self.logger.warning("⚠️  Neo4j auto-start not available - continuing without auto-start")
            except Exception as e:
                self.logger.warning("⚠️  Neo4j auto-start failed: %s - continuing anyway", str(e))
        
        self.phase1 = Phase1Adapter()  # type: ignore[abstract]
        self.phase2 = Phase2Adapter()  # type: ignore[abstract]
        self.phase3 = Phase3Adapter()  # type: ignore[abstract]
    
    def execute_full_pipeline(self, pdf_path: str, query: str, 
                            domain_description: str, 
                            workflow_id: str = "integrated_test") -> Dict[str, Any]:
        """Execute complete P1→P2→P3 pipeline with real data flow"""
        
        errors_list: List[str] = []
        results: Dict[str, Any] = {
            "workflow_id": workflow_id,
            "phases": {},
            "evidence": {},
            "status": "success",
            "errors": errors_list
        }
        
        try:
            # Phase 1: Basic GraphRAG
            self.logger.info("🔄 Executing Phase 1: Basic GraphRAG...")
            p1_request = ProcessingRequest(
                documents=[pdf_path],
                queries=[query],
                workflow_id=f"{workflow_id}_phase1",
                use_mock_apis=False
            )
            
            p1_result = self.phase1.execute(p1_request)
            results["phases"]["phase1"] = p1_result
            
            if p1_result.status != PhaseStatus.SUCCESS:
                results["status"] = "phase1_failed"
                errors_list.append(f"Phase 1 failed: {p1_result.error_message}")
                return results
            
            # Collect Phase 1 evidence
            evidence_dict: Dict[str, Any] = results["evidence"]
            evidence_dict["phase1_entities"] = p1_result.entity_count
            evidence_dict["phase1_relationships"] = p1_result.relationship_count
            evidence_dict["phase1_execution_time"] = p1_result.execution_time
            self.logger.info("✅ Phase 1 complete: %d entities, %d relationships", 
                           p1_result.entity_count, p1_result.relationship_count)
            
            # Phase 2: Enhanced with ontology
            self.logger.info("🔄 Executing Phase 2: Enhanced with ontology...")
            p2_request = ProcessingRequest(
                documents=[pdf_path],
                queries=[query],
                domain_description=domain_description,
                workflow_id=f"{workflow_id}_phase2",
                use_mock_apis=False,
                phase1_graph_data={
                    "entities": p1_result.entity_count,
                    "relationships": p1_result.relationship_count,
                    "graph_metrics": p1_result.results.get("graph_metrics", {}) if p1_result.results else {}
                }
            )
            
            p2_result = self.phase2.execute(p2_request)
            results["phases"]["phase2"] = p2_result
            
            if p2_result.status != PhaseStatus.SUCCESS:
                results["status"] = "phase2_failed"
                errors_list.append(f"Phase 2 failed: {p2_result.error_message}")
                return results
            
            # Collect Phase 2 evidence
            evidence_dict = results["evidence"]
            evidence_dict["phase2_entities"] = p2_result.entity_count
            evidence_dict["phase2_relationships"] = p2_result.relationship_count
            evidence_dict["phase2_execution_time"] = p2_result.execution_time
            evidence_dict["ontology_used"] = p2_result.results.get("ontology_info", {}) if p2_result.results else {}
            self.logger.info("✅ Phase 2 complete: %d entities, %d relationships",
                           p2_result.entity_count, p2_result.relationship_count)
            
            # Phase 3: Multi-document fusion
            self.logger.info("🔄 Executing Phase 3: Multi-document fusion...")
            p3_request = ProcessingRequest(
                documents=[pdf_path],
                queries=[query],
                workflow_id=f"{workflow_id}_phase3",
                fusion_strategy="basic",
                use_mock_apis=False,
                phase1_graph_data={
                    "entities": p1_result.entity_count,
                    "relationships": p1_result.relationship_count,
                    "graph_metrics": p1_result.results.get("graph_metrics", {}) if p1_result.results else {}
                },
                phase2_enhanced_data={
                    "entities": p2_result.entity_count,
                    "relationships": p2_result.relationship_count,
                    "ontology_info": p2_result.results.get("ontology_info", {}) if p2_result.results else {}
                }
            )
            
            p3_result = self.phase3.execute(p3_request)
            results["phases"]["phase3"] = p3_result
            
            if p3_result.status != PhaseStatus.SUCCESS:
                results["status"] = "phase3_failed"
                errors_list.append(f"Phase 3 failed: {p3_result.error_message}")
                return results
            
            # Collect Phase 3 evidence
            evidence_dict = results["evidence"]
            evidence_dict["phase3_entities"] = p3_result.entity_count
            evidence_dict["phase3_relationships"] = p3_result.relationship_count
            evidence_dict["phase3_execution_time"] = p3_result.execution_time
            evidence_dict["fusion_applied"] = p3_result.results.get("fusion_metrics", {}) if p3_result.results else {}
            self.logger.info("✅ Phase 3 complete: %d entities, %d relationships",
                           p3_result.entity_count, p3_result.relationship_count)
            
            # Calculate integration metrics
            total_execution_time = sum([
                p1_result.execution_time,
                p2_result.execution_time, 
                p3_result.execution_time
            ])
            
            evidence_dict["total_execution_time"] = total_execution_time
            evidence_dict["entity_progression"] = [
                p1_result.entity_count,
                p2_result.entity_count,
                p3_result.entity_count
            ]
            evidence_dict["relationship_progression"] = [
                p1_result.relationship_count,
                p2_result.relationship_count,
                p3_result.relationship_count
            ]
            
            self.logger.info("🎯 Integration complete: P1(%de, %dr) → P2(%de, %dr) → P3(%de, %dr)",
                           p1_result.entity_count, p1_result.relationship_count,
                           p2_result.entity_count, p2_result.relationship_count, 
                           p3_result.entity_count, p3_result.relationship_count)
            
            return results
            
        except Exception as e:
            error_msg = AdapterUtils.sanitize_error_message(e)
            results["status"] = "integration_error"
            errors_list.append(f"Integration orchestrator error: {error_msg}")
            return results
    
    def health_check(self) -> Dict[str, Any]:
        """Check health of all phases in the orchestrator"""
        result: Dict[str, Any] = {}
        
        # Check if adapters have health_check method
        if hasattr(self.phase1, 'health_check'):
            result["phase1"] = self.phase1.health_check()
        else:
            result["phase1"] = {"status": "unknown", "message": "health_check not implemented"}
            
        if hasattr(self.phase2, 'health_check'):
            result["phase2"] = self.phase2.health_check()
        else:
            result["phase2"] = {"status": "unknown", "message": "health_check not implemented"}
            
        if hasattr(self.phase3, 'health_check'):
            result["phase3"] = self.phase3.health_check()
        else:
            result["phase3"] = {"status": "unknown", "message": "health_check not implemented"}
            
        return result
    
    def cleanup(self) -> bool:
        """Clean up all phase resources"""
        cleanup_results: List[bool] = []
        
        # Clean up phase 1
        if hasattr(self.phase1, 'cleanup'):
            cleanup_results.append(self.phase1.cleanup())
        else:
            cleanup_results.append(True)  # No cleanup needed
            
        # Clean up phase 2
        if hasattr(self.phase2, 'cleanup'):
            cleanup_results.append(self.phase2.cleanup())
        else:
            cleanup_results.append(True)  # No cleanup needed
            
        # Clean up phase 3
        if hasattr(self.phase3, 'cleanup'):
            cleanup_results.append(self.phase3.cleanup())
        else:
            cleanup_results.append(True)  # No cleanup needed
            
        return all(cleanup_results)