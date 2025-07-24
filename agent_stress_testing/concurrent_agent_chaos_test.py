#!/usr/bin/env python3
"""
CONCURRENT AGENT CHAOS TEST

This test launches multiple agents simultaneously to find:
1. Database connection pool exhaustion
2. Memory pressure from concurrent processing
3. Race conditions in shared resources
4. Agent coordination failures under load
5. Service overload and cascading failures
6. Resource contention and deadlocks

The goal is to break the system through concurrent chaos.
"""

import asyncio
import json
import time
import uuid
import random
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
from concurrent.futures import ThreadPoolExecutor
import psutil
import gc

class ConcurrentAgentChaosTest:
    """Test multiple agents running simultaneously to find breaking points"""
    
    def __init__(self, max_agents: int = 20):
        self.test_id = f"chaos_{uuid.uuid4().hex[:8]}"
        self.max_agents = max_agents
        self.active_agents = {}
        self.resource_contention_events = []
        self.system_failures = []
        self.performance_degradation = []
        
        # Resource monitoring
        self.monitoring_active = False
        self.resource_metrics = []
        
        # Failure injection
        self.chaos_factor = 0.15  # 15% chance of random failures
        
        print(f"🌪️  CONCURRENT AGENT CHAOS TEST INITIALIZED")
        print(f"   Max Agents: {max_agents}")
        print(f"   Chaos Factor: {self.chaos_factor * 100}%")
        print(f"   Expected: Connection exhaustion, memory pressure, race conditions")
    
    async def execute_concurrent_agent_storm(self) -> Dict[str, Any]:
        """Launch multiple agents simultaneously to create chaos"""
        
        print(f"\n🚨 AGENT STORM TEST")
        print(f"   Launching {self.max_agents} agents simultaneously")
        print(f"   Each agent processes different documents concurrently")
        print(f"   Expected failures: Database exhaustion, memory pressure, deadlocks")
        
        storm_results = {
            "test_id": self.test_id,
            "start_time": datetime.now().isoformat(),
            "max_agents": self.max_agents,
            "agents_launched": 0,
            "agents_completed": 0,
            "agents_failed": 0,
            "system_breaking_points": [],
            "resource_exhaustion_events": [],
            "race_condition_events": [],
            "performance_timeline": []
        }
        
        # Start resource monitoring
        monitoring_task = asyncio.create_task(self._monitor_system_resources())
        
        try:
            # Create different documents for each agent
            agent_documents = self._create_chaos_documents(self.max_agents)
            
            # Launch all agents simultaneously
            agent_tasks = []
            for i in range(self.max_agents):
                agent_id = f"chaos_agent_{i:03d}"
                document = agent_documents[i]
                
                task = asyncio.create_task(
                    self._execute_chaos_agent(agent_id, document, storm_results)
                )
                agent_tasks.append(task)
                
                storm_results["agents_launched"] += 1
                
                # Small stagger to prevent instant overload (but still chaotic)
                if i % 5 == 0:
                    await asyncio.sleep(0.1)
            
            print(f"🚀 Launched {len(agent_tasks)} chaos agents")
            
            # Wait for all agents with timeout
            try:
                results = await asyncio.wait_for(
                    asyncio.gather(*agent_tasks, return_exceptions=True),
                    timeout=180  # 3 minutes max
                )
                
                # Analyze results
                for result in results:
                    if isinstance(result, Exception):
                        storm_results["agents_failed"] += 1
                        self.system_failures.append({
                            "timestamp": datetime.now().isoformat(),
                            "error": str(result),
                            "error_type": type(result).__name__
                        })
                    else:
                        storm_results["agents_completed"] += 1
                
            except asyncio.TimeoutError:
                print(f"🚨 TIMEOUT: Agents exceeded 3-minute deadline")
                storm_results["system_breaking_points"].append({
                    "type": "GLOBAL_TIMEOUT",
                    "description": "System couldn't complete agent processing in 3 minutes",
                    "active_agents": len([t for t in agent_tasks if not t.done()])
                })
            
        except Exception as e:
            print(f"💥 CATASTROPHIC SYSTEM FAILURE: {e}")
            storm_results["system_breaking_points"].append({
                "type": "CATASTROPHIC_FAILURE",
                "description": str(e),
                "error_type": type(e).__name__
            })
        
        finally:
            # Stop monitoring
            self.monitoring_active = False
            if not monitoring_task.done():
                monitoring_task.cancel()
        
        storm_results["end_time"] = datetime.now().isoformat()
        storm_results["resource_exhaustion_events"] = self.resource_contention_events
        storm_results["system_failures"] = self.system_failures
        
        # Analyze concurrent execution patterns
        self._analyze_concurrent_failures(storm_results)
        
        return storm_results
    
    def _create_chaos_documents(self, count: int) -> List[Dict[str, Any]]:
        """Create documents designed to cause maximum chaos"""
        
        documents = []
        
        # Create different types of challenging documents
        for i in range(count):
            if i % 4 == 0:
                # Large documents (memory pressure)
                content = self._create_large_document(i)
                doc_type = "LARGE_MEMORY_INTENSIVE"
            elif i % 4 == 1:
                # Entity-dense documents (CPU intensive)
                content = self._create_entity_dense_document(i)
                doc_type = "ENTITY_DENSE_CPU_INTENSIVE"
            elif i % 4 == 2:
                # Relationship-complex documents (processing intensive)
                content = self._create_relationship_complex_document(i)
                doc_type = "RELATIONSHIP_COMPLEX"
            else:
                # Ambiguous documents (error-prone)
                content = self._create_ambiguous_document(i)
                doc_type = "AMBIGUOUS_ERROR_PRONE"
            
            documents.append({
                "id": f"chaos_doc_{i:03d}",
                "type": doc_type,
                "content": content,
                "expected_processing_time": random.uniform(2.0, 8.0),
                "chaos_factor": random.uniform(0.1, 0.3)
            })
        
        return documents
    
    def _create_large_document(self, doc_id: int) -> str:
        """Create large document to stress memory"""
        
        base_content = f"""
        This is a large document {doc_id} designed to consume significant memory resources.
        It contains repetitive content with many entities and relationships that will stress
        the processing pipeline and potentially cause memory exhaustion issues.
        """
        
        # Repeat content to make it large (but not huge - we want processing, not just size)
        entities = ["GlobalCorp Inc.", "TechSolutions LLC", "Dr. Jane Smith", "Prof. Robert Chen",
                   "New York", "San Francisco", "Microsoft Azure", "Amazon Web Services"]
        
        large_content = base_content
        
        for _ in range(50):  # Create substantial content
            large_content += f"""
            
            In this section, we discuss the partnership between {random.choice(entities)} 
            and {random.choice(entities)}. The collaboration was announced by 
            {random.choice(entities)} during a conference in {random.choice(entities[-2:])}.
            
            The strategic alliance involves {random.choice(entities)} working closely with 
            {random.choice(entities)} to develop innovative solutions for the enterprise market.
            Key personnel including {random.choice(entities[2:4])} will lead the initiative.
            """
        
        return large_content
    
    def _create_entity_dense_document(self, doc_id: int) -> str:
        """Create document with maximum entity density"""
        
        # Create a document packed with entities
        people = ["Dr. Sarah Chen", "Prof. Michael Rodriguez", "Dr. Elena Kowalski", 
                  "Prof. James Thompson", "Dr. Aisha Patel", "Prof. David Kim"]
        
        companies = ["Apple Inc.", "Microsoft Corporation", "Google LLC", "Amazon Web Services",
                     "Meta Platforms", "NVIDIA Corporation", "Intel Corporation", "IBM"]
        
        places = ["Silicon Valley", "New York City", "Boston", "Seattle", "Austin", 
                  "San Francisco", "Cambridge", "Palo Alto", "Mountain View"]
        
        content = f"Entity-dense document {doc_id} with maximum named entity concentration:\n\n"
        
        # Pack entities densely
        for i in range(20):
            content += f"""
            {random.choice(people)} from {random.choice(companies)} met with 
            {random.choice(people)} from {random.choice(companies)} in {random.choice(places)}.
            The meeting was also attended by {random.choice(people)} and {random.choice(people)}.
            Representatives from {random.choice(companies)}, {random.choice(companies)}, and 
            {random.choice(companies)} discussed partnerships. The event took place in 
            {random.choice(places)} with additional participants from {random.choice(places)}.
            """
        
        return content
    
    def _create_relationship_complex_document(self, doc_id: int) -> str:
        """Create document with complex, overlapping relationships"""
        
        return f"""
        Complex relationship document {doc_id} with overlapping and nested relationships:
        
        Apple Inc. CEO Tim Cook announced that Apple Inc. has acquired StartupTech Inc., 
        founded by former Google employee Dr. Sarah Martinez. Dr. Sarah Martinez, who 
        previously worked at Microsoft before joining Google, will now lead Apple's 
        new AI division.
        
        The acquisition was negotiated by Apple's VP of Strategy, John Wilson, who 
        formerly served as CEO of TechVentures Inc. before TechVentures Inc. was 
        acquired by Samsung Electronics. Samsung Electronics CEO Jong-Hee Han had 
        previously worked with Tim Cook when both were at different companies.
        
        This creates a complex web where Dr. Sarah Martinez reports to Tim Cook, 
        while John Wilson coordinates with Dr. Sarah Martinez, and both have 
        historical connections to Jong-Hee Han through various previous roles.
        
        The announcement was made during a conference organized by EventsCorp, 
        which is a subsidiary of MediaGroup Holdings, whose CEO, Lisa Chen, 
        is the former colleague of Dr. Sarah Martinez from their time at 
        Stanford University together.
        """
    
    def _create_ambiguous_document(self, doc_id: int) -> str:
        """Create ambiguous document likely to cause processing errors"""
        
        return f"""
        Ambiguous document {doc_id} with challenging parsing scenarios:
        
        The meeting was attended by Smith, Johnson, and Dr. Smith. Smith from TechCorp 
        disagreed with Smith from InnovateCorp about the proposal. Dr. Smith suggested 
        that both Smith and the other Smith should collaborate.
        
        The company, which was founded in 2010, merged with the company that was 
        founded in 2015. The CEO of the company met with the CEO of the other company 
        to discuss the merger between the company and the company.
        
        He said that he would speak with him about it when he returns from his trip. 
        She mentioned that she had spoken with them about their concerns regarding 
        their proposal. They agreed to meet with them next week.
        
        The document mentions several unnamed individuals and organizations without 
        clear identification, creating ambiguity in entity resolution and relationship 
        extraction processes that may cause errors or infinite loops.
        """
    
    async def _execute_chaos_agent(self, agent_id: str, document: Dict[str, Any], 
                                  results: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single chaos agent with aggressive resource usage"""
        
        agent_start_time = time.time()
        
        try:
            print(f"🤖 Agent {agent_id} starting with {document['type']} document")
            
            # Track this agent
            self.active_agents[agent_id] = {
                "start_time": agent_start_time,
                "document": document,
                "status": "initializing"
            }
            
            # Import tools (this might fail under high concurrent load)
            import sys
            sys.path.append("/home/brian/projects/Digimons")
            
            from src.tools.phase1.t15a_text_chunker_unified import T15ATextChunkerUnified
            from src.tools.phase1.t23a_spacy_ner_unified import T23ASpacyNERUnified
            from src.tools.phase1.t27_relationship_extractor_unified import T27RelationshipExtractorUnified
            from src.core.service_manager import get_service_manager
            from src.tools.base_tool import ToolRequest
            
            # Get service manager (potential connection pool exhaustion point)
            try:
                service_manager = get_service_manager()
                self.active_agents[agent_id]["status"] = "service_manager_acquired"
            except Exception as e:
                self._record_resource_contention("service_manager_exhaustion", agent_id, str(e))
                raise
            
            # Initialize tools (memory intensive - potential OOM point)
            try:
                text_chunker = T15ATextChunkerUnified(service_manager)
                entity_extractor = T23ASpacyNERUnified(service_manager)
                relationship_extractor = T27RelationshipExtractorUnified(service_manager)
                self.active_agents[agent_id]["status"] = "tools_initialized"
            except Exception as e:
                self._record_resource_contention("tool_initialization_failure", agent_id, str(e))
                raise
            
            # Inject random chaos
            if random.random() < document["chaos_factor"]:
                if random.choice([True, False]):
                    raise Exception(f"Injected chaos failure in {agent_id}")
                else:
                    # Simulate network timeout
                    await asyncio.sleep(random.uniform(2.0, 5.0))
            
            # Step 1: Text Chunking (concurrent database access)
            self.active_agents[agent_id]["status"] = "chunking"
            
            chunk_request = ToolRequest(
                tool_id="T15A",
                operation="chunk_text",
                input_data={
                    "document_ref": f"storage://chaos/{document['id']}.txt",
                    "text": document["content"],
                    "confidence": 0.9
                },
                parameters={}
            )
            
            try:
                chunk_result = await asyncio.to_thread(text_chunker.execute, chunk_request)
                if chunk_result.status != "success":
                    raise Exception(f"Chunking failed: {chunk_result.error_message}")
                
                chunks = chunk_result.data.get("chunks", [])
                self.active_agents[agent_id]["chunks"] = len(chunks)
                
            except Exception as e:
                self._record_resource_contention("chunking_failure", agent_id, str(e))
                raise
            
            # Step 2: Entity Extraction (memory and CPU intensive)
            self.active_agents[agent_id]["status"] = "entity_extraction"
            
            # Process chunks concurrently within this agent (double concurrency stress)
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
            
            try:
                entity_results = await asyncio.gather(*entity_tasks, return_exceptions=True)
                
                all_entities = []
                for result in entity_results:
                    if isinstance(result, Exception):
                        self._record_resource_contention("entity_extraction_failure", agent_id, str(result))
                    elif result.status == "success":
                        entities = result.data.get("entities", [])
                        all_entities.extend(entities)
                
                self.active_agents[agent_id]["entities"] = len(all_entities)
                
            except Exception as e:
                self._record_resource_contention("entity_processing_failure", agent_id, str(e))
                raise
            
            # Step 3: Relationship Extraction (most resource intensive)
            self.active_agents[agent_id]["status"] = "relationship_extraction"
            
            relationship_tasks = []
            for chunk in chunks:
                chunk_entities = [e for e in all_entities if e.get("chunk_ref") == chunk["chunk_ref"]]
                
                if len(chunk_entities) >= 2:
                    rel_request = ToolRequest(
                        tool_id="T27",
                        operation="extract_relationships",
                        input_data={
                            "chunk_ref": chunk["chunk_ref"],
                            "text": chunk["text"],
                            "entities": chunk_entities,
                            "confidence": 0.1
                        },
                        parameters={}
                    )
                    
                    task = asyncio.to_thread(relationship_extractor.execute, rel_request)
                    relationship_tasks.append(task)
            
            try:
                relationship_results = await asyncio.gather(*relationship_tasks, return_exceptions=True)
                
                all_relationships = []
                for result in relationship_results:
                    if isinstance(result, Exception):
                        self._record_resource_contention("relationship_extraction_failure", agent_id, str(result))
                    elif result.status == "success":
                        relationships = result.data.get("relationships", [])
                        all_relationships.extend(relationships)
                
                self.active_agents[agent_id]["relationships"] = len(all_relationships)
                
            except Exception as e:
                self._record_resource_contention("relationship_processing_failure", agent_id, str(e))
                raise
            
            # Simulate additional processing load (stress system further)
            if document["type"] == "LARGE_MEMORY_INTENSIVE":
                # Simulate memory-intensive post-processing
                large_data = [entity.copy() for entity in all_entities for _ in range(10)]
                await asyncio.sleep(0.5)  # Simulate processing time
                del large_data  # Cleanup
            
            processing_time = time.time() - agent_start_time
            
            self.active_agents[agent_id]["status"] = "completed"
            self.active_agents[agent_id]["processing_time"] = processing_time
            
            print(f"✅ Agent {agent_id} completed in {processing_time:.2f}s")
            
            return {
                "agent_id": agent_id,
                "status": "success",
                "processing_time": processing_time,
                "chunks": len(chunks),
                "entities": len(all_entities),
                "relationships": len(all_relationships),
                "document_type": document["type"]
            }
            
        except Exception as e:
            processing_time = time.time() - agent_start_time
            
            if agent_id in self.active_agents:
                self.active_agents[agent_id]["status"] = "failed"
                self.active_agents[agent_id]["error"] = str(e)
                self.active_agents[agent_id]["processing_time"] = processing_time
            
            print(f"❌ Agent {agent_id} failed after {processing_time:.2f}s: {e}")
            
            return {
                "agent_id": agent_id,
                "status": "failed",
                "error": str(e),
                "processing_time": processing_time,
                "document_type": document["type"]
            }
    
    def _record_resource_contention(self, event_type: str, agent_id: str, details: str):
        """Record resource contention events"""
        
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "agent_id": agent_id,
            "details": details,
            "active_agents_count": len(self.active_agents)
        }
        
        self.resource_contention_events.append(event)
        print(f"🚨 Resource contention: {event_type} in {agent_id}")
    
    async def _monitor_system_resources(self):
        """Monitor system resources during concurrent execution"""
        
        self.monitoring_active = True
        
        while self.monitoring_active:
            try:
                cpu_percent = psutil.cpu_percent(interval=None)
                memory = psutil.virtual_memory()
                disk_io = psutil.disk_io_counters()
                
                metrics = {
                    "timestamp": datetime.now().isoformat(),
                    "cpu_percent": cpu_percent,
                    "memory_used_mb": memory.used / 1024 / 1024,
                    "memory_percent": memory.percent,
                    "disk_read_mb": disk_io.read_bytes / 1024 / 1024 if disk_io else 0,
                    "disk_write_mb": disk_io.write_bytes / 1024 / 1024 if disk_io else 0,
                    "active_agents": len(self.active_agents)
                }
                
                self.resource_metrics.append(metrics)
                
                # Check for resource exhaustion
                if memory.percent > 90:
                    self._record_resource_contention(
                        "memory_exhaustion", 
                        "system", 
                        f"Memory usage: {memory.percent}%"
                    )
                
                if cpu_percent > 95:
                    self._record_resource_contention(
                        "cpu_exhaustion",
                        "system", 
                        f"CPU usage: {cpu_percent}%"
                    )
                
                await asyncio.sleep(1.0)
                
            except Exception as e:
                print(f"⚠️ Resource monitoring error: {e}")
                await asyncio.sleep(1.0)
    
    def _analyze_concurrent_failures(self, results: Dict[str, Any]):
        """Analyze concurrent execution failure patterns"""
        
        print(f"\n📊 CONCURRENT EXECUTION ANALYSIS:")
        
        agents_launched = results["agents_launched"]
        agents_completed = results["agents_completed"]
        agents_failed = results["agents_failed"]
        
        success_rate = (agents_completed / agents_launched) * 100 if agents_launched > 0 else 0
        
        print(f"   🚀 Agents Launched: {agents_launched}")
        print(f"   ✅ Agents Completed: {agents_completed}")
        print(f"   ❌ Agents Failed: {agents_failed}")
        print(f"   📈 Success Rate: {success_rate:.1f}%")
        
        if success_rate < 70:
            print(f"   🚨 LOW SUCCESS RATE: System struggled with concurrent load")
        
        # Analyze resource contention events
        contention_events = len(self.resource_contention_events)
        if contention_events > 0:
            print(f"   ⚡ Resource Contention Events: {contention_events}")
            
            # Group by event type
            event_types = {}
            for event in self.resource_contention_events:
                event_type = event["event_type"]
                event_types[event_type] = event_types.get(event_type, 0) + 1
            
            print(f"   📊 Contention Breakdown:")
            for event_type, count in event_types.items():
                print(f"     {event_type}: {count} events")
        
        # Analyze resource usage patterns
        if self.resource_metrics:
            max_memory = max(m["memory_percent"] for m in self.resource_metrics)
            max_cpu = max(m["cpu_percent"] for m in self.resource_metrics)
            
            print(f"   💾 Peak Memory Usage: {max_memory:.1f}%")
            print(f"   🖥️ Peak CPU Usage: {max_cpu:.1f}%")
            
            if max_memory > 85:
                print(f"   🚨 MEMORY PRESSURE: System approached memory limits")
            
            if max_cpu > 90:
                print(f"   🚨 CPU OVERLOAD: System CPU was heavily stressed")

async def run_concurrent_chaos_test():
    """Execute the concurrent agent chaos test"""
    
    test = ConcurrentAgentChaosTest(max_agents=15)
    
    print(f"\n🚨 EXECUTING CONCURRENT AGENT CHAOS TEST")
    print(f"   This test launches multiple agents to find resource limits")
    print(f"   Expected failures: Connection exhaustion, memory pressure, race conditions")
    
    try:
        results = await test.execute_concurrent_agent_storm()
        
        # Save results
        results_file = f"concurrent_chaos_results_{test.test_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Add resource metrics to results
        results["resource_metrics"] = test.resource_metrics
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n📄 RESULTS SAVED: {results_file}")
        
        return results
        
    except Exception as e:
        print(f"💥 CHAOS TEST FRAMEWORK FAILURE: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_concurrent_chaos_test())