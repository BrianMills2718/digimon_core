#!/usr/bin/env python3
"""
Prometheus Metrics Collection Demo

Demonstrates the Prometheus metrics collection system for KGAS.
Shows how metrics are collected, exposed, and can be monitored.
"""

import asyncio
import time
import random
import sys
import os
from typing import List

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.metrics_collector import MetricsCollector, initialize_metrics
from src.core.config_manager import ConfigurationManager


class MetricsDemo:
    """Demo class for showing Prometheus metrics collection"""
    
    def __init__(self):
        self.config = ConfigurationManager()
        self.metrics = initialize_metrics(self.config)
        
    def simulate_document_processing(self, num_documents: int = 5):
        """Simulate document processing with metrics collection"""
        print(f"📊 Simulating processing of {num_documents} documents...")
        
        for i in range(num_documents):
            # Simulate document processing time
            processing_time = random.uniform(0.5, 3.0)
            time.sleep(processing_time)
            
            # Record document processing metrics
            self.metrics.record_document_processed(
                component="document_processor",
                phase="phase1",
                operation="pdf_processing",
                document_type="pdf",
                processing_time=processing_time
            )
            
            # Simulate entity extraction
            entities_count = random.randint(5, 25)
            relationships_count = random.randint(2, 15)
            
            self.metrics.record_entities_extracted(
                component="entity_extractor",
                phase="phase1",
                operation="ner_extraction",
                entity_type="person",
                count=entities_count // 2
            )
            
            self.metrics.record_entities_extracted(
                component="entity_extractor",
                phase="phase1",
                operation="ner_extraction",
                entity_type="organization",
                count=entities_count // 2
            )
            
            self.metrics.record_relationships_extracted(
                component="relationship_extractor",
                phase="phase1",
                operation="pattern_matching",
                relationship_type="works_for",
                count=relationships_count
            )
            
            print(f"  📄 Document {i+1}/{num_documents} processed ({processing_time:.2f}s, {entities_count} entities, {relationships_count} relationships)")
    
    def simulate_api_calls(self, num_calls: int = 10):
        """Simulate API calls with metrics collection"""
        print(f"🌐 Simulating {num_calls} API calls...")
        
        api_providers = ["openai", "google", "anthropic"]
        endpoints = ["embeddings", "chat", "models"]
        statuses = ["success", "error", "timeout"]
        
        for i in range(num_calls):
            provider = random.choice(api_providers)
            endpoint = random.choice(endpoints)
            status = random.choices(statuses, weights=[0.8, 0.15, 0.05])[0]  # Mostly success
            duration = random.uniform(0.1, 2.0)
            
            time.sleep(duration)
            
            self.metrics.record_api_call(
                api_provider=provider,
                endpoint=endpoint,
                status=status,
                duration=duration
            )
            
            print(f"  🌐 API call {i+1}/{num_calls}: {provider}/{endpoint} - {status} ({duration:.2f}s)")
    
    def simulate_database_operations(self, num_operations: int = 8):
        """Simulate database operations with metrics collection"""
        print(f"🗄️ Simulating {num_operations} database operations...")
        
        db_types = ["neo4j", "redis", "qdrant"]
        operations = ["insert", "query", "update", "delete"]
        statuses = ["success", "error"]
        
        for i in range(num_operations):
            db_type = random.choice(db_types)
            operation = random.choice(operations)
            status = random.choices(statuses, weights=[0.9, 0.1])[0]  # Mostly success
            duration = random.uniform(0.01, 0.5)
            
            time.sleep(duration)
            
            self.metrics.record_database_operation(
                database_type=db_type,
                operation=operation,
                status=status,
                duration=duration
            )
            
            print(f"  🗄️ DB operation {i+1}/{num_operations}: {db_type} {operation} - {status} ({duration:.3f}s)")
    
    def simulate_workflow_execution(self, num_workflows: int = 3):
        """Simulate workflow executions with metrics collection"""
        print(f"🔄 Simulating {num_workflows} workflow executions...")
        
        workflow_types = ["vertical_slice", "multi_document", "enhanced_workflow"]
        statuses = ["success", "error", "timeout"]
        
        for i in range(num_workflows):
            workflow_type = random.choice(workflow_types)
            status = random.choices(statuses, weights=[0.8, 0.15, 0.05])[0]
            duration = random.uniform(5.0, 30.0)
            
            print(f"  🔄 Executing workflow {i+1}/{num_workflows}: {workflow_type} ({duration:.1f}s)")
            
            # Simulate workflow execution time
            time.sleep(duration / 10)  # Scale down for demo
            
            self.metrics.record_workflow_execution(
                workflow_type=workflow_type,
                status=status,
                duration=duration
            )
            
            print(f"  ✅ Workflow {i+1} completed: {workflow_type} - {status}")
    
    def simulate_errors(self, num_errors: int = 5):
        """Simulate error events with metrics collection"""
        print(f"⚠️ Simulating {num_errors} error events...")
        
        components = ["document_processor", "api_client", "database", "workflow_engine"]
        error_types = ["timeout", "connection_error", "validation_error", "processing_error"]
        
        for i in range(num_errors):
            component = random.choice(components)
            error_type = random.choice(error_types)
            
            self.metrics.record_error(
                component=component,
                error_type=error_type
            )
            
            print(f"  ⚠️ Error {i+1}/{num_errors}: {component} - {error_type}")
    
    def update_component_health(self):
        """Update component health status"""
        print("❤️ Updating component health status...")
        
        components = {
            "neo4j": random.choice([True, False]),
            "redis": random.choice([True, True, False]),  # Mostly healthy
            "api_client": random.choice([True, True, True, False]),  # Mostly healthy
            "document_processor": True,
            "workflow_engine": True
        }
        
        for component, healthy in components.items():
            self.metrics.set_component_health(component, healthy)
            status = "healthy" if healthy else "unhealthy"
            emoji = "✅" if healthy else "❌"
            print(f"  {emoji} {component}: {status}")
    
    def show_metrics_summary(self):
        """Show current metrics summary"""
        print("\n📈 Current Metrics Summary")
        print("=" * 40)
        
        summary = self.metrics.get_metrics_summary()
        
        print(f"Metrics enabled: {summary['metrics_enabled']}")
        print(f"Prometheus available: {summary['prometheus_available']}")
        print(f"HTTP server started: {summary['http_server_started']}")
        
        if summary.get('metrics_endpoint'):
            print(f"Metrics endpoint: {summary['metrics_endpoint']}")
        
        if 'system_metrics' in summary:
            sys_metrics = summary['system_metrics']
            print(f"\nSystem Metrics:")
            print(f"  CPU: {sys_metrics['cpu_percent']:.1f}%")
            print(f"  Memory: {sys_metrics['memory_percent']:.1f}% ({sys_metrics['memory_used_gb']:.1f}GB used)")
            print(f"  Disk: {sys_metrics['disk_percent']:.1f}% ({sys_metrics['disk_used_gb']:.1f}GB used)")
    
    def run_demo(self):
        """Run the complete metrics demo"""
        print("🎯 Phase 2 Prometheus Metrics Collection Demo")
        print("=" * 50)
        
        # Wait for metrics server to start
        print("🚀 Starting metrics server...")
        time.sleep(2)
        
        # Show initial metrics summary
        self.show_metrics_summary()
        
        if self.metrics.http_server_started:
            print(f"\n📊 Metrics are being exposed at: http://localhost:{self.metrics.config.http_port}/metrics")
            print("You can view metrics using:")
            print(f"  curl http://localhost:{self.metrics.config.http_port}/metrics")
            print("  or open the URL in your browser")
        
        print("\n🎬 Starting simulation...")
        
        # Run simulations
        self.simulate_document_processing(5)
        print()
        
        self.simulate_api_calls(8)
        print()
        
        self.simulate_database_operations(6)
        print()
        
        self.simulate_workflow_execution(3)
        print()
        
        self.simulate_errors(3)
        print()
        
        self.update_component_health()
        
        # Show final metrics summary
        self.show_metrics_summary()
        
        print("\n✅ Demo completed successfully!")
        print("📊 Metrics have been collected and are available at the metrics endpoint")
        print("🎉 Phase 2 Task 2: Prometheus Metrics Collection - COMPLETE")
        
        # Keep server running for a bit to allow metrics inspection
        if self.metrics.http_server_started:
            print("\n⏳ Keeping metrics server running for 30 seconds...")
            print("💡 You can now fetch metrics with:")
            print(f"   curl http://localhost:{self.metrics.config.http_port}/metrics")
            time.sleep(30)
        
        return self.metrics.get_metrics_summary()


def main():
    """Main demo function"""
    try:
        demo = MetricsDemo()
        result = demo.run_demo()
        
        # Cleanup
        demo.metrics.shutdown()
        
        return 0
        
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