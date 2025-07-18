"""Performance Benchmarks for Contract and Ontology Validation

This module tests the performance of validation operations with realistic data volumes.
Helps identify bottlenecks and ensure the system can scale.
"""

import time
import random
import string
from typing import List, Dict, Any
import statistics

# Add parent directory to path for imports
import os

from src.core.data_models import Entity, Relationship, Document, Chunk
from src.core.contract_validator import ContractValidator
from src.core.ontology_validator import OntologyValidator
from src.ontology_library.ontology_service import OntologyService


class PerformanceBenchmark:
    """Run performance benchmarks for the validation system."""
    
    def __init__(self):
        self.ontology_service = OntologyService()
        self.ontology_validator = OntologyValidator()
        self.contract_validator = ContractValidator("../contracts")
        
    def generate_random_text(self, length: int = 100) -> str:
        """Generate random text of specified length."""
        return ''.join(random.choices(string.ascii_letters + string.digits + ' ', k=length))
    
    def create_test_entities(self, count: int) -> List[Entity]:
        """Create test entities with realistic data."""
        entities = []
        entity_types = list(self.ontology_service.registry.entities.keys())
        
        for i in range(count):
            entity_type = random.choice(entity_types)
            entity = Entity(
                canonical_name=f"TestEntity_{i}",
                entity_type=entity_type,
                confidence=random.uniform(0.5, 1.0),
                quality_tier=random.choice(["high", "medium", "low"]),
                created_by="test_benchmark",
                workflow_id="benchmark_workflow",
                surface_forms=[f"alias_{i}_1", f"alias_{i}_2"],
                attributes={"test_attr": f"value_{i}"}
            )
            entities.append(entity)
        
        return entities
    
    def create_test_relationships(self, count: int, entities: List[Entity]) -> List[Relationship]:
        """Create test relationships between entities."""
        relationships = []
        relationship_types = list(self.ontology_service.registry.connections.keys())
        
        for i in range(count):
            source = random.choice(entities)
            target = random.choice(entities)
            
            # Get valid relationship types for these entity types
            valid_rels = self.ontology_validator.get_valid_relationships(
                source.entity_type, target.entity_type
            )
            
            if valid_rels:
                rel_type = random.choice(valid_rels)
            else:
                rel_type = random.choice(relationship_types)
            
            relationship = Relationship(
                source_id=source.id,
                target_id=target.id,
                relationship_type=rel_type,
                confidence=random.uniform(0.5, 1.0),
                quality_tier=random.choice(["high", "medium", "low"]),
                created_by="test_benchmark",
                workflow_id="benchmark_workflow",
                weight=random.uniform(0.1, 1.0)
            )
            relationships.append(relationship)
        
        return relationships
    
    def create_test_documents(self, count: int, avg_size: int = 10000) -> List[Document]:
        """Create test documents with realistic sizes."""
        documents = []
        
        for i in range(count):
            content_size = random.randint(avg_size // 2, avg_size * 2)
            document = Document(
                content=self.generate_random_text(content_size),
                original_filename=f"test_doc_{i}.pdf",
                size_bytes=content_size,
                title=f"Test Document {i}",
                confidence=random.uniform(0.8, 1.0),
                quality_tier="high",
                created_by="test_benchmark",
                workflow_id="benchmark_workflow"
            )
            documents.append(document)
        
        return documents
    
    def benchmark_entity_validation(self, entity_count: int = 1000) -> Dict[str, float]:
        """Benchmark entity validation performance."""
        print(f"\nBenchmarking entity validation with {entity_count} entities...")
        
        # Create test entities
        entities = self.create_test_entities(entity_count)
        
        # Measure validation time
        validation_times = []
        errors_count = 0
        
        start_time = time.time()
        for entity in entities:
            entity_start = time.time()
            errors = self.ontology_validator.validate_entity(entity)
            validation_times.append(time.time() - entity_start)
            if errors:
                errors_count += 1
        
        total_time = time.time() - start_time
        
        return {
            "total_entities": entity_count,
            "total_time": total_time,
            "avg_time_per_entity": statistics.mean(validation_times),
            "min_time": min(validation_times),
            "max_time": max(validation_times),
            "entities_per_second": entity_count / total_time,
            "errors_found": errors_count
        }
    
    def benchmark_relationship_validation(self, rel_count: int = 1000) -> Dict[str, float]:
        """Benchmark relationship validation performance."""
        print(f"\nBenchmarking relationship validation with {rel_count} relationships...")
        
        # Create entities first
        entities = self.create_test_entities(100)
        
        # Create relationships
        relationships = self.create_test_relationships(rel_count, entities)
        
        # Measure validation time
        validation_times = []
        errors_count = 0
        
        start_time = time.time()
        for rel in relationships:
            rel_start = time.time()
            errors = self.ontology_validator.validate_relationship(rel)
            validation_times.append(time.time() - rel_start)
            if errors:
                errors_count += 1
        
        total_time = time.time() - start_time
        
        return {
            "total_relationships": rel_count,
            "total_time": total_time,
            "avg_time_per_relationship": statistics.mean(validation_times),
            "min_time": min(validation_times),
            "max_time": max(validation_times),
            "relationships_per_second": rel_count / total_time,
            "errors_found": errors_count
        }
    
    def benchmark_contract_validation(self) -> Dict[str, Any]:
        """Benchmark contract validation performance."""
        print("\nBenchmarking contract validation...")
        
        start_time = time.time()
        results = self.contract_validator.validate_all_contracts()
        total_time = time.time() - start_time
        
        valid_count = sum(1 for r in results.values() if r["valid"])
        
        return {
            "total_contracts": len(results),
            "valid_contracts": valid_count,
            "invalid_contracts": len(results) - valid_count,
            "total_time": total_time,
            "avg_time_per_contract": total_time / len(results) if results else 0
        }
    
    def benchmark_data_model_creation(self, count: int = 10000) -> Dict[str, float]:
        """Benchmark data model creation with validation."""
        print(f"\nBenchmarking data model creation with {count} objects...")
        
        creation_times = []
        
        # Test Document creation
        doc_start = time.time()
        documents = self.create_test_documents(count // 4)
        doc_time = time.time() - doc_start
        
        # Test Entity creation with validation
        entity_start = time.time()
        entities = self.create_test_entities(count // 2)
        entity_time = time.time() - entity_start
        
        # Test Relationship creation with validation
        rel_start = time.time()
        relationships = self.create_test_relationships(count // 4, entities[:100])
        rel_time = time.time() - rel_start
        
        total_time = doc_time + entity_time + rel_time
        
        return {
            "total_objects": count,
            "document_creation_time": doc_time,
            "entity_creation_time": entity_time,
            "relationship_creation_time": rel_time,
            "total_time": total_time,
            "objects_per_second": count / total_time
        }
    
    def benchmark_memory_usage(self, entity_count: int = 10000) -> Dict[str, Any]:
        """Benchmark memory usage with large datasets."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        
        # Get initial memory
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create large dataset
        entities = self.create_test_entities(entity_count)
        relationships = self.create_test_relationships(entity_count // 2, entities[:1000])
        
        # Get memory after creation
        after_creation = process.memory_info().rss / 1024 / 1024  # MB
        
        # Validate all entities
        for entity in entities:
            self.ontology_validator.validate_entity(entity)
        
        # Get final memory
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        return {
            "initial_memory_mb": initial_memory,
            "after_creation_mb": after_creation,
            "final_memory_mb": final_memory,
            "memory_increase_mb": final_memory - initial_memory,
            "entities_created": entity_count,
            "relationships_created": entity_count // 2
        }
    
    def run_all_benchmarks(self):
        """Run all performance benchmarks."""
        print("=" * 60)
        print("PERFORMANCE BENCHMARK RESULTS")
        print("=" * 60)
        
        # Entity validation
        entity_results = self.benchmark_entity_validation(1000)
        print("\n📊 Entity Validation Performance:")
        print(f"  - Total time: {entity_results['total_time']:.2f}s")
        print(f"  - Avg per entity: {entity_results['avg_time_per_entity']*1000:.2f}ms")
        print(f"  - Throughput: {entity_results['entities_per_second']:.0f} entities/second")
        
        # Relationship validation
        rel_results = self.benchmark_relationship_validation(1000)
        print("\n📊 Relationship Validation Performance:")
        print(f"  - Total time: {rel_results['total_time']:.2f}s")
        print(f"  - Avg per relationship: {rel_results['avg_time_per_relationship']*1000:.2f}ms")
        print(f"  - Throughput: {rel_results['relationships_per_second']:.0f} relationships/second")
        
        # Contract validation
        contract_results = self.benchmark_contract_validation()
        print("\n📊 Contract Validation Performance:")
        print(f"  - Total contracts: {contract_results['total_contracts']}")
        print(f"  - Total time: {contract_results['total_time']:.2f}s")
        print(f"  - Avg per contract: {contract_results['avg_time_per_contract']*1000:.2f}ms")
        
        # Data model creation
        creation_results = self.benchmark_data_model_creation(1000)
        print("\n📊 Data Model Creation Performance:")
        print(f"  - Total time: {creation_results['total_time']:.2f}s")
        print(f"  - Throughput: {creation_results['objects_per_second']:.0f} objects/second")
        
        # Memory usage
        memory_results = self.benchmark_memory_usage(5000)
        print("\n📊 Memory Usage:")
        print(f"  - Initial: {memory_results['initial_memory_mb']:.1f}MB")
        print(f"  - After creation: {memory_results['after_creation_mb']:.1f}MB")
        print(f"  - Final: {memory_results['final_memory_mb']:.1f}MB")
        print(f"  - Total increase: {memory_results['memory_increase_mb']:.1f}MB")
        
        # Summary
        print("\n" + "=" * 60)
        print("PERFORMANCE SUMMARY")
        print("=" * 60)
        
        if entity_results['entities_per_second'] > 100:
            print("✅ Entity validation performance: GOOD")
        else:
            print("⚠️ Entity validation performance: NEEDS OPTIMIZATION")
        
        if rel_results['relationships_per_second'] > 100:
            print("✅ Relationship validation performance: GOOD")
        else:
            print("⚠️ Relationship validation performance: NEEDS OPTIMIZATION")
        
        if memory_results['memory_increase_mb'] < 100:
            print("✅ Memory usage: ACCEPTABLE")
        else:
            print("⚠️ Memory usage: HIGH")
        
        print("\n⚠️ Note: This is an experimental system. Performance optimization")
        print("   would be required before production use.")


if __name__ == "__main__":
    benchmark = PerformanceBenchmark()
    benchmark.run_all_benchmarks()