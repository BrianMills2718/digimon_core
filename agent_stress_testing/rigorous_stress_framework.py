#!/usr/bin/env python3
"""
RIGOROUS AGENT STRESS TESTING FRAMEWORK

This framework is designed to BREAK the system and reveal real limitations:
1. Multi-document complexity (50-100 documents)
2. Long tool chains (10+ sequential tools)
3. Concurrent agent execution with resource contention
4. Error injection and failure cascade testing
5. Adversarial inputs and edge cases
6. Real decision-making under constraints
7. Performance limits and scalability boundaries

The goal is to find the breaking points, not prove it works.
"""

import asyncio
import json
import time
import uuid
import random
import aiofiles
import psutil
import gc
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
from concurrent.futures import ThreadPoolExecutor
import threading
import queue

class StressTestType(Enum):
    MULTI_DOCUMENT_OVERLOAD = "multi_document_overload"
    LONG_CHAIN_COMPLEXITY = "long_chain_complexity" 
    CONCURRENT_AGENT_CHAOS = "concurrent_agent_chaos"
    ERROR_CASCADE_INJECTION = "error_cascade_injection"
    ADVERSARIAL_INPUT_ATTACK = "adversarial_input_attack"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    DECISION_COMPLEXITY = "decision_complexity"
    TEMPORAL_WORKFLOW = "temporal_workflow"

class StressTestResult(Enum):
    SYSTEM_BROKEN = "system_broken"
    PERFORMANCE_DEGRADED = "performance_degraded"
    PARTIAL_FAILURE = "partial_failure"
    UNEXPECTED_SUCCESS = "unexpected_success"
    TEST_INCONCLUSIVE = "test_inconclusive"

@dataclass
class StressTestMetrics:
    """Comprehensive metrics for stress test evaluation"""
    test_id: str
    test_type: StressTestType
    start_time: datetime
    end_time: Optional[datetime] = None
    
    # Performance Metrics
    total_execution_time: float = 0.0
    peak_memory_mb: float = 0.0
    cpu_utilization: float = 0.0
    disk_io_mb: float = 0.0
    
    # System Metrics
    successful_operations: int = 0
    failed_operations: int = 0
    timeout_operations: int = 0
    error_types: Dict[str, int] = field(default_factory=dict)
    
    # Agent Metrics
    agent_decisions_made: int = 0
    agent_course_corrections: int = 0
    agent_conflicts: int = 0
    
    # Tool Chain Metrics
    tools_executed: int = 0
    chain_length_achieved: int = 0
    chain_breaks: int = 0
    
    # Data Quality Metrics
    entities_extracted: int = 0
    relationships_found: int = 0
    confidence_average: float = 0.0
    data_consistency_score: float = 0.0
    
    # Scalability Metrics
    documents_processed: int = 0
    concurrent_agents: int = 0
    resource_contention_events: int = 0

class RigorousStressTestFramework:
    """Framework designed to break the agent system and find limits"""
    
    def __init__(self, break_system: bool = True):
        self.break_system = break_system
        self.test_id = f"stress_{uuid.uuid4().hex[:8]}"
        self.start_time = time.time()
        self.active_tests = {}
        self.system_limits_found = {}
        self.breaking_points = {}
        
        # Resource monitoring
        self.resource_monitor = ResourceMonitor()
        self.failure_injector = FailureInjector()
        
        # Setup logging for stress testing
        self.logger = self._setup_stress_logging()
        
        print(f"🚨 RIGOROUS STRESS TESTING FRAMEWORK INITIALIZED")
        print(f"   Test ID: {self.test_id}")
        print(f"   Goal: {'BREAK THE SYSTEM' if break_system else 'Find limits gracefully'}")
    
    def _setup_stress_logging(self):
        """Setup comprehensive logging for stress tests"""
        logger = logging.getLogger(f"stress_test_{self.test_id}")
        logger.setLevel(logging.DEBUG)
        
        # File handler for detailed logs
        handler = logging.FileHandler(f"stress_test_{self.test_id}.log")
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)8s | %(name)s | %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger

class MultiDocumentOverloadTest:
    """Test with 50-100 documents to find scalability limits"""
    
    def __init__(self, framework: RigorousStressTestFramework):
        self.framework = framework
        self.logger = framework.logger
        
    async def execute_academic_paper_overload(self, num_documents: int = 75) -> StressTestMetrics:
        """Process 75 academic papers simultaneously to find breaking point"""
        
        self.logger.info(f"🔥 ACADEMIC PAPER OVERLOAD TEST: {num_documents} documents")
        
        metrics = StressTestMetrics(
            test_id=f"{self.framework.test_id}_academic_overload",
            test_type=StressTestType.MULTI_DOCUMENT_OVERLOAD,
            start_time=datetime.now()
        )
        
        # Generate realistic academic papers with complexity
        test_papers = self._generate_complex_academic_papers(num_documents)
        
        print(f"\n🚨 ACADEMIC PAPER OVERLOAD TEST")
        print(f"   Documents: {num_documents}")
        print(f"   Expected Failures: Entity conflicts, memory exhaustion, timeout")
        print(f"   Breaking Point Target: System cannot process all documents")
        
        start_time = time.time()
        
        try:
            # Process all papers simultaneously (this should break something)
            tasks = []
            for paper in test_papers:
                task = self._process_academic_paper_aggressively(paper, metrics)
                tasks.append(task)
            
            # Execute with timeout to prevent infinite hanging
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=300  # 5 minutes max
            )
            
            # Analyze results for failure patterns
            success_count = sum(1 for r in results if not isinstance(r, Exception))
            failure_count = len(results) - success_count
            
            metrics.successful_operations = success_count
            metrics.failed_operations = failure_count
            
            if failure_count > num_documents * 0.3:  # 30% failure rate
                self.logger.error(f"HIGH FAILURE RATE: {failure_count}/{num_documents} failed")
                print(f"🔥 SYSTEM BREAKING POINT FOUND: {failure_count} failures out of {num_documents}")
            
        except asyncio.TimeoutError:
            self.logger.error("TIMEOUT: Academic paper processing exceeded 5 minutes")
            print(f"🚨 TIMEOUT FAILURE: System couldn't complete in 5 minutes")
            metrics.timeout_operations = num_documents
            
        except Exception as e:
            self.logger.error(f"CATASTROPHIC FAILURE: {e}")
            print(f"💥 CATASTROPHIC SYSTEM FAILURE: {e}")
            
        metrics.total_execution_time = time.time() - start_time
        metrics.end_time = datetime.now()
        
        return metrics
    
    def _generate_complex_academic_papers(self, count: int) -> List[Dict[str, Any]]:
        """Generate realistic academic papers with complex entity relationships"""
        
        # Real-world complexity patterns
        authors_pool = [
            "Dr. Sarah Chen", "Prof. Michael Rodriguez", "Dr. Elena Kowalski", 
            "Prof. James Thompson", "Dr. Aisha Patel", "Prof. David Kim",
            "Dr. Maria Gonzalez", "Prof. Robert Johnson", "Dr. Li Wei",
            "Prof. Anna Müller", "Dr. Ahmed Hassan", "Prof. Jennifer Brown"
        ]
        
        institutions_pool = [
            "MIT Computer Science Department", "Stanford AI Lab", "Google DeepMind",
            "Carnegie Mellon University", "UC Berkeley EECS", "Harvard Medical School",
            "Oxford University", "ETH Zurich", "University of Toronto", "INRIA Paris"
        ]
        
        concepts_pool = [
            "machine learning", "natural language processing", "computer vision",
            "reinforcement learning", "deep neural networks", "transformer architectures",
            "knowledge graphs", "semantic parsing", "multi-modal learning",
            "federated learning", "adversarial training", "meta-learning"
        ]
        
        papers = []
        
        for i in range(count):
            # Create complex papers with overlapping authors and institutions
            num_authors = random.randint(2, 8)
            paper_authors = random.sample(authors_pool, min(num_authors, len(authors_pool)))
            
            num_institutions = random.randint(1, 4)
            paper_institutions = random.sample(institutions_pool, min(num_institutions, len(institutions_pool)))
            
            num_concepts = random.randint(3, 8)
            paper_concepts = random.sample(concepts_pool, min(num_concepts, len(concepts_pool)))
            
            # Generate paper with intentional complexity and ambiguity
            content = self._generate_complex_paper_content(
                paper_authors, paper_institutions, paper_concepts, i
            )
            
            papers.append({
                "id": f"paper_{i:03d}",
                "title": f"Advanced {paper_concepts[0].title()} for {paper_concepts[1].title()}",
                "authors": paper_authors,
                "institutions": paper_institutions,
                "concepts": paper_concepts,
                "content": content,
                "complexity_score": len(paper_authors) * len(paper_institutions) * len(paper_concepts),
                "expected_entities": len(paper_authors) + len(paper_institutions) + len(paper_concepts),
                "expected_relationships": num_authors * num_institutions + len(paper_concepts) * 2
            })
        
        return papers
    
    def _generate_complex_paper_content(self, authors: List[str], institutions: List[str], 
                                       concepts: List[str], paper_id: int) -> str:
        """Generate realistic academic paper content with complex entity patterns"""
        
        # Create content with intentional challenges:
        # - Name variations (Dr. vs Prof. vs full name)
        # - Institution abbreviations and full names
        # - Concept relationships and dependencies
        # - Ambiguous pronouns and references
        
        content = f"""
        This research conducted by {', '.join(authors)} at {institutions[0]} presents novel approaches to {concepts[0]}.
        
        The work builds on previous research from {institutions[1] if len(institutions) > 1 else institutions[0]} 
        where {authors[0].split()[-1]} and colleagues demonstrated applications of {concepts[1]} to {concepts[2]}.
        
        Our methodology combines {concepts[0]} with {concepts[-1]} to address limitations in existing approaches.
        {authors[1] if len(authors) > 1 else authors[0]} developed the core algorithm while researchers at 
        {institutions[-1]} contributed the evaluation framework.
        
        The collaboration between {institutions[0]} and {institutions[1] if len(institutions) > 1 else "external partners"} 
        enabled comprehensive validation across multiple domains including {', '.join(concepts[:3])}.
        
        Future work will explore connections between {concepts[0]} and {concepts[-2] if len(concepts) > 2 else concepts[-1]} 
        with potential applications in {concepts[1]} and related fields.
        
        Acknowledgments: Special thanks to Prof. {authors[-1].split()[-1]} and the team at {institutions[0]} 
        for their contributions to this research.
        """
        
        # Add intentional complexity and ambiguity
        if paper_id % 3 == 0:
            content += f"\n\nNote: {authors[0]} is also affiliated with {random.choice(institutions)} as a visiting researcher."
        
        if paper_id % 5 == 0:
            content += f"\n\nCorresponding author: {random.choice(authors)} (email: {authors[0].lower().replace(' ', '').replace('.', '')}@{institutions[0].lower().replace(' ', '').replace('university', 'edu')}.edu)"
        
        return content.strip()
    
    async def _process_academic_paper_aggressively(self, paper: Dict[str, Any], 
                                                  metrics: StressTestMetrics) -> Dict[str, Any]:
        """Process single paper with aggressive resource usage to find limits"""
        
        try:
            # Import tools (this might fail under high load)
            import sys
            sys.path.append("/home/brian/projects/Digimons")
            
            from src.tools.phase1.t15a_text_chunker_unified import T15ATextChunkerUnified
            from src.tools.phase1.t23a_spacy_ner_unified import T23ASpacyNERUnified
            from src.tools.phase1.t27_relationship_extractor_unified import T27RelationshipExtractorUnified
            from src.core.service_manager import get_service_manager
            from src.tools.base_tool import ToolRequest
            
            # Get service manager (might fail under concurrent load)
            service_manager = get_service_manager()
            
            # Initialize tools (memory intensive)
            text_chunker = T15ATextChunkerUnified(service_manager)
            entity_extractor = T23ASpacyNERUnified(service_manager)
            relationship_extractor = T27RelationshipExtractorUnified(service_manager)
            
            start_time = time.time()
            
            # Step 1: Aggressive chunking
            chunk_request = ToolRequest(
                tool_id="T15A",
                operation="chunk_text",
                input_data={
                    "document_ref": f"storage://stress/{paper['id']}.txt",
                    "text": paper["content"],
                    "confidence": 0.9
                },
                parameters={}
            )
            
            chunk_result = await asyncio.to_thread(text_chunker.execute, chunk_request)
            
            if chunk_result.status != "success":
                raise Exception(f"Chunking failed: {chunk_result.error_message}")
            
            chunks = chunk_result.data.get("chunks", [])
            metrics.tools_executed += 1
            
            # Step 2: Concurrent entity extraction on all chunks
            entity_tasks = []
            for chunk in chunks:
                entity_request = ToolRequest(
                    tool_id="T23A",
                    operation="extract_entities",
                    input_data={
                        "chunk_ref": chunk["chunk_ref"],
                        "text": chunk["text"],
                        "chunk_confidence": 0.9
                    },
                    parameters={"confidence_threshold": 0.1}
                )
                
                task = asyncio.to_thread(entity_extractor.execute, entity_request)
                entity_tasks.append(task)
            
            # Execute all entity extractions simultaneously (resource intensive)
            entity_results = await asyncio.gather(*entity_tasks, return_exceptions=True)
            
            all_entities = []
            for result in entity_results:
                if isinstance(result, Exception):
                    self.logger.error(f"Entity extraction failed: {result}")
                    metrics.failed_operations += 1
                elif result.status == "success":
                    entities = result.data.get("entities", [])
                    all_entities.extend(entities)
                    metrics.entities_extracted += len(entities)
                    metrics.tools_executed += 1
                else:
                    metrics.failed_operations += 1
            
            # Step 3: Relationship extraction (even more intensive)
            relationship_tasks = []
            for chunk in chunks:
                chunk_entities = [e for e in all_entities if e.get("chunk_ref") == chunk["chunk_ref"]]
                
                if len(chunk_entities) >= 2:
                    # CRITICAL FIX: Convert T23A entity format to T27 expected format
                    def convert_t23a_to_t27_format(t23a_entities):
                        """Convert T23A entity format to T27 expected format"""
                        t27_entities = []
                        for entity in t23a_entities:
                            # T27 expects: ['text', 'label', 'start', 'end']
                            # T23A provides: ['surface_form', 'entity_type', 'start_pos', 'end_pos']
                            t27_entity = {
                                'text': entity.get('surface_form', ''),  # T23A → T27
                                'label': entity.get('entity_type', ''),  # T23A → T27
                                'start': entity.get('start_pos', 0),     # T23A → T27
                                'end': entity.get('end_pos', 0),         # T23A → T27
                                # Preserve original data for debugging
                                '_chunk_ref': entity.get('chunk_ref', ''),
                                '_confidence': entity.get('confidence', 0.0)
                            }
                            t27_entities.append(t27_entity)
                        return t27_entities
                    
                    # Convert entities to T27 format
                    t27_formatted_entities = convert_t23a_to_t27_format(chunk_entities)
                    
                    rel_request = ToolRequest(
                        tool_id="T27",
                        operation="extract_relationships",
                        input_data={
                            "chunk_ref": chunk["chunk_ref"],
                            "text": chunk["text"],
                            "entities": t27_formatted_entities,  # Use converted format!
                            "confidence": 0.1
                        },
                        parameters={}
                    )
                    
                    task = asyncio.to_thread(relationship_extractor.execute, rel_request)
                    relationship_tasks.append(task)
            
            relationship_results = await asyncio.gather(*relationship_tasks, return_exceptions=True)
            
            all_relationships = []
            for result in relationship_results:
                if isinstance(result, Exception):
                    metrics.failed_operations += 1
                elif result.status == "success":
                    relationships = result.data.get("relationships", [])
                    all_relationships.extend(relationships)
                    metrics.relationships_found += len(relationships)
                    metrics.tools_executed += 1
                else:
                    metrics.failed_operations += 1
            
            processing_time = time.time() - start_time
            
            # Success metrics
            metrics.successful_operations += 1
            metrics.documents_processed += 1
            
            return {
                "paper_id": paper["id"],
                "status": "success",
                "processing_time": processing_time,
                "chunks": len(chunks),
                "entities": len(all_entities),
                "relationships": len(all_relationships),
                "expected_entities": paper["expected_entities"],
                "expected_relationships": paper["expected_relationships"],
                "accuracy": {
                    "entity_coverage": len(all_entities) / max(1, paper["expected_entities"]),
                    "relationship_coverage": len(all_relationships) / max(1, paper["expected_relationships"])
                }
            }
            
        except Exception as e:
            metrics.failed_operations += 1
            self.logger.error(f"Paper {paper['id']} processing failed: {e}")
            
            return {
                "paper_id": paper["id"],
                "status": "failed",
                "error": str(e),
                "processing_time": time.time() - start_time if 'start_time' in locals() else 0
            }

class ResourceMonitor:
    """Monitor system resources during stress testing"""
    
    def __init__(self):
        self.monitoring = False
        self.metrics = []
        
    async def start_monitoring(self, interval: float = 1.0):
        """Start continuous resource monitoring"""
        self.monitoring = True
        
        while self.monitoring:
            metrics = {
                "timestamp": datetime.now().isoformat(),
                "cpu_percent": psutil.cpu_percent(),
                "memory_mb": psutil.virtual_memory().used / 1024 / 1024,
                "disk_io_mb": sum(psutil.disk_io_counters()[:2]) / 1024 / 1024,
                "network_bytes": sum(psutil.net_io_counters()[:2])
            }
            
            self.metrics.append(metrics)
            await asyncio.sleep(interval)
    
    def stop_monitoring(self):
        """Stop resource monitoring"""
        self.monitoring = False
    
    def get_peak_usage(self) -> Dict[str, float]:
        """Get peak resource usage during monitoring"""
        if not self.metrics:
            return {}
        
        return {
            "peak_cpu_percent": max(m["cpu_percent"] for m in self.metrics),
            "peak_memory_mb": max(m["memory_mb"] for m in self.metrics),
            "peak_disk_io_mb": max(m["disk_io_mb"] for m in self.metrics)
        }

class FailureInjector:
    """Inject failures to test error handling and recovery"""
    
    def __init__(self):
        self.failure_patterns = {
            "network_timeout": 0.1,      # 10% chance
            "memory_exhaustion": 0.05,   # 5% chance
            "database_connection": 0.08, # 8% chance
            "tool_execution": 0.15,      # 15% chance
            "data_corruption": 0.03      # 3% chance
        }
    
    def should_inject_failure(self, failure_type: str) -> bool:
        """Determine if a failure should be injected"""
        return random.random() < self.failure_patterns.get(failure_type, 0.0)
    
    def inject_network_timeout(self):
        """Simulate network timeout"""
        if self.should_inject_failure("network_timeout"):
            raise asyncio.TimeoutError("Injected network timeout")
    
    def inject_memory_exhaustion(self):
        """Simulate memory exhaustion"""
        if self.should_inject_failure("memory_exhaustion"):
            # Force garbage collection
            gc.collect()
            raise MemoryError("Injected memory exhaustion")

async def run_rigorous_stress_tests():
    """Execute comprehensive stress testing to find system limits"""
    
    framework = RigorousStressTestFramework(break_system=True)
    
    print(f"\n🚨 RIGOROUS AGENT STRESS TESTING")
    print(f"   Goal: Find breaking points and system limits")
    print(f"   Expected: Multiple failures and resource exhaustion")
    print(f"=" * 80)
    
    # Test 1: Multi-Document Overload
    print(f"\n🔥 TEST 1: MULTI-DOCUMENT OVERLOAD")
    overload_test = MultiDocumentOverloadTest(framework)
    
    try:
        overload_metrics = await overload_test.execute_academic_paper_overload(75)
        
        print(f"\n📊 OVERLOAD TEST RESULTS:")
        print(f"   Success Rate: {overload_metrics.successful_operations}/{overload_metrics.successful_operations + overload_metrics.failed_operations}")
        print(f"   Execution Time: {overload_metrics.total_execution_time:.2f}s")
        print(f"   Entities Extracted: {overload_metrics.entities_extracted}")
        print(f"   Relationships Found: {overload_metrics.relationships_found}")
        print(f"   Tools Executed: {overload_metrics.tools_executed}")
        
        if overload_metrics.failed_operations > 20:
            print(f"🚨 SYSTEM LIMIT FOUND: High failure rate indicates scalability boundary")
        
    except Exception as e:
        print(f"💥 OVERLOAD TEST CATASTROPHIC FAILURE: {e}")
    
    print(f"\n🎯 STRESS TESTING COMPLETE")
    print(f"   Time: {time.time() - framework.start_time:.2f}s")
    print(f"   System Limits: {len(framework.breaking_points)} breaking points found")

if __name__ == "__main__":
    asyncio.run(run_rigorous_stress_tests())