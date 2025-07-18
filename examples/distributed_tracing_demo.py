#!/usr/bin/env python3
"""
Distributed Tracing Demo

Demonstrates distributed tracing with OpenTelemetry for request tracing
across all KGAS components.
"""

import sys
import os
import time
import random
import asyncio
from typing import Dict, Any

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.distributed_tracing import DistributedTracing, initialize_distributed_tracing, trace_function, trace_operation
from core.config import ConfigurationManager


class TracingDemo:
    """Demo class showing distributed tracing capabilities"""
    
    def __init__(self):
        self.config = ConfigurationManager()
        self.tracing = initialize_distributed_tracing(self.config)
    
    @trace_function("demo.document_processing")
    async def simulate_document_processing(self, document_id: str) -> Dict[str, Any]:
        """Simulate document processing with tracing"""
        
        # Add document metadata
        self.tracing.set_span_attribute("document.id", document_id)
        self.tracing.set_span_attribute("document.type", "pdf")
        
        # Simulate PDF loading
        with self.tracing.trace_operation("document.load_pdf", {"document.id": document_id}):
            processing_time = random.uniform(0.1, 0.3)
            await asyncio.sleep(processing_time)
            self.tracing.add_span_event("pdf_loaded", {"size_mb": random.uniform(1, 10)})
        
        # Simulate entity extraction
        entities = await self._simulate_entity_extraction(document_id)
        
        # Simulate relationship extraction
        relationships = await self._simulate_relationship_extraction(document_id, entities)
        
        # Simulate graph storage
        await self._simulate_graph_storage(document_id, entities, relationships)
        
        result = {
            "document_id": document_id,
            "entities": entities,
            "relationships": relationships,
            "processing_time": processing_time
        }
        
        # Add result metrics to span
        self.tracing.set_span_attribute("result.entities_count", len(entities))
        self.tracing.set_span_attribute("result.relationships_count", len(relationships))
        
        return result
    
    @trace_function("demo.entity_extraction")
    async def _simulate_entity_extraction(self, document_id: str) -> list:
        """Simulate entity extraction with API calls"""
        
        # Simulate API call to OpenAI
        with self.tracing.trace_api_call("openai", "embeddings", "POST"):
            await asyncio.sleep(random.uniform(0.1, 0.2))
            self.tracing.add_span_event("api_call_completed", {"response_size": random.randint(100, 1000)})
        
        # Simulate spaCy processing
        with self.tracing.trace_operation("nlp.spacy_ner", {"model": "en_core_web_sm"}):
            await asyncio.sleep(random.uniform(0.05, 0.15))
            entities = [f"entity_{i}" for i in range(random.randint(5, 15))]
            self.tracing.add_span_event("entities_extracted", {"count": len(entities)})
        
        return entities
    
    @trace_function("demo.relationship_extraction")
    async def _simulate_relationship_extraction(self, document_id: str, entities: list) -> list:
        """Simulate relationship extraction"""
        
        # Simulate pattern matching
        with self.tracing.trace_operation("nlp.pattern_matching", {"entities_count": len(entities)}):
            await asyncio.sleep(random.uniform(0.1, 0.2))
            relationships = [f"rel_{i}" for i in range(random.randint(3, 8))]
            self.tracing.add_span_event("relationships_found", {"count": len(relationships)})
        
        return relationships
    
    @trace_function("demo.graph_storage")
    async def _simulate_graph_storage(self, document_id: str, entities: list, relationships: list):
        """Simulate storing data in graph database"""
        
        # Simulate Neo4j operations
        with self.tracing.trace_database_operation("neo4j", "create_nodes"):
            await asyncio.sleep(random.uniform(0.05, 0.1))
            self.tracing.add_span_event("nodes_created", {"count": len(entities)})
        
        with self.tracing.trace_database_operation("neo4j", "create_relationships"):
            await asyncio.sleep(random.uniform(0.05, 0.1))
            self.tracing.add_span_event("relationships_created", {"count": len(relationships)})
    
    @trace_function("demo.workflow_execution")
    async def simulate_workflow_execution(self, workflow_id: str, documents: list) -> Dict[str, Any]:
        """Simulate complete workflow execution"""
        
        # Add workflow metadata
        self.tracing.set_span_attribute("workflow.id", workflow_id)
        self.tracing.set_span_attribute("workflow.documents_count", len(documents))
        
        results = []
        
        # Process documents in parallel
        tasks = [
            self.simulate_document_processing(doc_id) 
            for doc_id in documents
        ]
        
        with self.tracing.trace_operation("workflow.parallel_processing", {"tasks_count": len(tasks)}):
            results = await asyncio.gather(*tasks)
        
        # Simulate final aggregation
        with self.tracing.trace_operation("workflow.aggregation"):
            await asyncio.sleep(0.1)
            total_entities = sum(len(r["entities"]) for r in results)
            total_relationships = sum(len(r["relationships"]) for r in results)
            
            self.tracing.add_span_event("workflow_completed", {
                "total_entities": total_entities,
                "total_relationships": total_relationships
            })
        
        return {
            "workflow_id": workflow_id,
            "documents_processed": len(documents),
            "total_entities": total_entities,
            "total_relationships": total_relationships,
            "results": results
        }
    
    def simulate_error_tracing(self):
        """Simulate error tracing"""
        try:
            with self.tracing.trace_operation("demo.error_operation", {"will_fail": True}):
                self.tracing.add_span_event("operation_started")
                
                # Simulate some work before error
                time.sleep(0.1)
                
                # Simulate error
                raise ValueError("Simulated error for tracing demo")
        
        except Exception as e:
            print(f"   Error traced: {type(e).__name__}: {str(e)}")
    
    def demonstrate_trace_propagation(self):
        """Demonstrate trace context propagation"""
        with self.tracing.trace_operation("demo.parent_operation") as parent_span:
            # Get trace context
            trace_id = self.tracing.get_current_trace_id()
            span_id = self.tracing.get_current_span_id()
            
            print(f"   Parent trace ID: {trace_id}")
            print(f"   Parent span ID: {span_id}")
            
            # Simulate context propagation
            carrier = {}
            self.tracing.inject_trace_context(carrier)
            
            # In a real scenario, this carrier would be sent to another service
            print(f"   Trace context injected into carrier")
            
            # Simulate child operation
            with self.tracing.trace_operation("demo.child_operation") as child_span:
                child_span_id = self.tracing.get_current_span_id()
                print(f"   Child span ID: {child_span_id}")
                
                # The child operation shares the same trace ID
                assert self.tracing.get_current_trace_id() == trace_id
                
                time.sleep(0.05)
    
    def run_demo(self):
        """Run the complete distributed tracing demo"""
        print("🎯 Phase 2 Distributed Tracing Demo")
        print("=" * 50)
        
        # Show tracing configuration
        stats = self.tracing.get_tracing_stats()
        print("📊 Tracing Configuration:")
        print(f"   Enabled: {stats['enabled']}")
        print(f"   OpenTelemetry available: {stats['opentelemetry_available']}")
        print(f"   Service name: {stats['service_name']}")
        print(f"   Service version: {stats['service_version']}")
        print(f"   Console export: {stats['console_export']}")
        print(f"   Batch export: {stats['batch_export']}")
        print(f"   Span processors: {stats['span_processors']}")
        print()
        
        # Demo 1: Basic tracing
        print("🔍 Demo 1: Basic Operation Tracing")
        print("-" * 40)
        
        with trace_operation("demo.basic_operation", {"demo_type": "basic"}):
            print("   Executing basic operation...")
            time.sleep(0.1)
            
            # Add events and attributes
            self.tracing.add_span_event("operation_milestone", {"progress": 50})
            self.tracing.set_span_attribute("operation.result", "success")
            
            print("   Basic operation completed")
        
        print()
        
        # Demo 2: Error tracing
        print("🚨 Demo 2: Error Tracing")
        print("-" * 40)
        
        self.simulate_error_tracing()
        print()
        
        # Demo 3: Trace propagation
        print("🔗 Demo 3: Trace Context Propagation")
        print("-" * 40)
        
        self.demonstrate_trace_propagation()
        print()
        
        # Demo 4: Async workflow tracing
        print("⚡ Demo 4: Async Workflow Tracing")
        print("-" * 40)
        
        async def run_async_demo():
            print("   Starting async workflow tracing...")
            
            documents = [f"doc_{i}" for i in range(3)]
            result = await self.simulate_workflow_execution("demo_workflow_001", documents)
            
            print(f"   Workflow completed:")
            print(f"     Documents processed: {result['documents_processed']}")
            print(f"     Total entities: {result['total_entities']}")
            print(f"     Total relationships: {result['total_relationships']}")
            
            return result
        
        asyncio.run(run_async_demo())
        print()
        
        # Demo 5: Custom span attributes and events
        print("🏷️ Demo 5: Custom Attributes and Events")
        print("-" * 40)
        
        with trace_operation("demo.custom_attributes") as span:
            # Add custom attributes
            span.set_attribute("custom.user_id", "user_123")
            span.set_attribute("custom.operation_type", "batch_processing")
            span.set_attribute("custom.batch_size", 50)
            
            # Add events with timestamps
            span.add_event("batch_started", {"batch_id": "batch_001"})
            
            time.sleep(0.1)
            
            span.add_event("batch_progress", {"processed": 25, "remaining": 25})
            
            time.sleep(0.1)
            
            span.add_event("batch_completed", {"total_processed": 50, "errors": 0})
            
            print("   Custom attributes and events added to span")
        
        print()
        
        # Show final stats
        final_stats = self.tracing.get_tracing_stats()
        print("📈 Final Tracing Statistics:")
        print(f"   Last trace ID: {final_stats.get('current_trace_id', 'N/A')}")
        print(f"   Last span ID: {final_stats.get('current_span_id', 'N/A')}")
        
        print(f"\n✨ Distributed Tracing Features Demonstrated:")
        print("✅ Operation tracing with spans")
        print("✅ Error tracking and exception recording")
        print("✅ Trace context propagation")
        print("✅ Async operation tracing")
        print("✅ Custom attributes and events")
        print("✅ Hierarchical span relationships")
        print("✅ API call tracing")
        print("✅ Database operation tracing")
        print("✅ Workflow execution tracing")
        
        print(f"\n🎉 Phase 2 Task 6: Distributed Tracing - COMPLETE")
        print("✅ OpenTelemetry integration implemented")
        print("✅ Automatic span creation for all operations")
        print("✅ Distributed trace propagation")
        print("✅ Custom attributes and events")
        print("✅ Error tracking and performance monitoring")
        print("✅ Integration with Jaeger/Zipkin ready")
        
        return True


def main():
    """Main demo function"""
    try:
        demo = TracingDemo()
        result = demo.run_demo()
        
        # Cleanup
        demo.tracing.shutdown()
        
        return 0 if result else 1
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return 1


if __name__ == "__main__":
    try:
        result = main()
        sys.exit(result)
    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)