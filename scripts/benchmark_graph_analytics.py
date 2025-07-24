#!/usr/bin/env python3
"""
Benchmark Graph Analytics Performance

Run comprehensive performance benchmarks for all Phase 2.1 analytics capabilities
to validate they meet the <2 second response time requirement.
"""

import asyncio
import time
import argparse
import json
import numpy as np
from datetime import datetime
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.neo4j_manager import Neo4jDockerManager
from src.core.distributed_transaction_manager import DistributedTransactionManager
from src.analytics import (
    GraphCentralityAnalyzer,
    CommunityDetector,
    CrossModalEntityLinker,
    ConceptualKnowledgeSynthesizer,
    CitationImpactAnalyzer
)


class AnalyticsBenchmark:
    """Benchmark suite for graph analytics performance"""
    
    def __init__(self):
        self.neo4j_manager = None
        self.dtm = None
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'benchmarks': {},
            'summary': {}
        }
    
    async def setup(self):
        """Initialize connections and services"""
        print("Setting up benchmark environment...")
        
        # Initialize Neo4j manager
        self.neo4j_manager = Neo4jDockerManager()
        await self.neo4j_manager.ensure_started()
        
        # Initialize distributed transaction manager
        self.dtm = DistributedTransactionManager(self.neo4j_manager)
        
        # Create test data if needed
        await self._create_test_data()
        
        print("Setup complete.\n")
    
    async def teardown(self):
        """Clean up resources"""
        if self.neo4j_manager:
            await self.neo4j_manager.cleanup()
    
    async def _create_test_data(self):
        """Create test graph data for benchmarking"""
        print("Creating test data...")
        
        # Check if test data already exists
        query = "MATCH (n:BenchmarkNode) RETURN count(n) as count"
        result = await self.neo4j_manager.execute_read_query(query)
        
        if result and result[0]['count'] > 0:
            print(f"Test data already exists: {result[0]['count']} nodes")
            return
        
        # Create nodes and relationships
        node_count = 1000
        batch_size = 100
        
        for i in range(0, node_count, batch_size):
            create_query = """
            UNWIND range($start, $end) as id
            CREATE (n:BenchmarkNode:Paper {
                id: id,
                name: 'Paper_' + toString(id),
                title: 'Research Paper ' + toString(id),
                year: 2020 + (id % 5),
                field: CASE id % 4
                    WHEN 0 THEN 'Computer Science'
                    WHEN 1 THEN 'Physics'
                    WHEN 2 THEN 'Biology'
                    ELSE 'Mathematics'
                END,
                citations: toInteger(rand() * 100)
            })
            """
            
            await self.neo4j_manager.execute_write_query(
                create_query,
                {'start': i, 'end': min(i + batch_size - 1, node_count - 1)}
            )
        
        # Create relationships
        rel_query = """
        MATCH (a:BenchmarkNode), (b:BenchmarkNode)
        WHERE a.id < b.id AND rand() < 0.01
        CREATE (a)-[:CITES {confidence: rand(), weight: 1 + rand() * 4}]->(b)
        """
        
        await self.neo4j_manager.execute_write_query(rel_query)
        
        # Create collaboration network
        collab_query = """
        MATCH (a:BenchmarkNode), (b:BenchmarkNode)
        WHERE a.id < b.id AND rand() < 0.005 AND a.field = b.field
        CREATE (a)-[:COLLABORATES {strength: rand()}]->(b)
        """
        
        await self.neo4j_manager.execute_write_query(collab_query)
        
        print("Test data created successfully.")
    
    async def benchmark_graph_centrality(self):
        """Benchmark graph centrality algorithms"""
        print("\n=== Graph Centrality Benchmarks ===")
        
        analyzer = GraphCentralityAnalyzer(self.neo4j_manager, self.dtm)
        results = {}
        
        # Benchmark PageRank
        print("\nBenchmarking PageRank...")
        start = time.time()
        try:
            result = await analyzer.calculate_pagerank_centrality(
                entity_type='Paper',
                damping_factor=0.85
            )
            elapsed = time.time() - start
            
            results['pagerank'] = {
                'execution_time': elapsed,
                'nodes_processed': result['metadata']['total_nodes'],
                'method': result['metadata']['method'],
                'passed': elapsed < 2.0
            }
            
            print(f"✓ PageRank: {elapsed:.3f}s ({result['metadata']['method']} method)")
            
        except Exception as e:
            print(f"✗ PageRank failed: {e}")
            results['pagerank'] = {'error': str(e), 'passed': False}
        
        # Benchmark Betweenness Centrality
        print("\nBenchmarking Betweenness Centrality...")
        start = time.time()
        try:
            result = await analyzer.calculate_betweenness_centrality(
                entity_type='Paper'
            )
            elapsed = time.time() - start
            
            results['betweenness'] = {
                'execution_time': elapsed,
                'nodes_processed': result['metadata']['total_nodes'],
                'method': result['metadata']['method'],
                'passed': elapsed < 2.0
            }
            
            print(f"✓ Betweenness: {elapsed:.3f}s ({result['metadata']['method']} method)")
            
        except Exception as e:
            print(f"✗ Betweenness failed: {e}")
            results['betweenness'] = {'error': str(e), 'passed': False}
        
        # Benchmark Closeness Centrality
        print("\nBenchmarking Closeness Centrality...")
        start = time.time()
        try:
            result = await analyzer.calculate_closeness_centrality(
                entity_type='Paper'
            )
            elapsed = time.time() - start
            
            results['closeness'] = {
                'execution_time': elapsed,
                'nodes_processed': result['metadata']['total_nodes'],
                'passed': elapsed < 2.0
            }
            
            print(f"✓ Closeness: {elapsed:.3f}s")
            
        except Exception as e:
            print(f"✗ Closeness failed: {e}")
            results['closeness'] = {'error': str(e), 'passed': False}
        
        self.results['benchmarks']['graph_centrality'] = results
    
    async def benchmark_community_detection(self):
        """Benchmark community detection algorithms"""
        print("\n=== Community Detection Benchmarks ===")
        
        detector = CommunityDetector(self.neo4j_manager, self.dtm)
        results = {}
        
        algorithms = ['louvain', 'label_propagation', 'greedy_modularity']
        
        for algorithm in algorithms:
            print(f"\nBenchmarking {algorithm}...")
            start = time.time()
            
            try:
                result = await detector.detect_research_communities(
                    algorithm=algorithm,
                    min_community_size=5,
                    max_communities=50
                )
                elapsed = time.time() - start
                
                results[algorithm] = {
                    'execution_time': elapsed,
                    'communities_found': len(result['communities']),
                    'total_nodes': result['metadata']['total_nodes'],
                    'modularity': result['analysis'].get('modularity', 0),
                    'passed': elapsed < 2.0
                }
                
                print(f"✓ {algorithm}: {elapsed:.3f}s ({len(result['communities'])} communities)")
                
            except Exception as e:
                print(f"✗ {algorithm} failed: {e}")
                results[algorithm] = {'error': str(e), 'passed': False}
        
        self.results['benchmarks']['community_detection'] = results
    
    async def benchmark_cross_modal_linking(self):
        """Benchmark cross-modal entity linking"""
        print("\n=== Cross-Modal Linking Benchmarks ===")
        
        linker = CrossModalEntityLinker(self.neo4j_manager, self.dtm)
        
        # Create test entity candidates
        entity_candidates = {
            'text': [
                {'text_content': f'Research paper about {topic}', 'entity_id': i}
                for i, topic in enumerate(['AI', 'ML', 'NLP', 'CV', 'RL'] * 20)
            ],
            'image': [
                {'image_path': f'/images/diagram_{i}.png', 'entity_id': 100 + i}
                for i in range(50)
            ],
            'structured': [
                {'structured_data': {'field': f'field_{i}', 'value': i}, 'entity_id': 200 + i}
                for i in range(30)
            ]
        }
        
        print(f"\nLinking {sum(len(v) for v in entity_candidates.values())} entities...")
        start = time.time()
        
        try:
            result = await linker.link_cross_modal_entities(entity_candidates)
            elapsed = time.time() - start
            
            self.results['benchmarks']['cross_modal_linking'] = {
                'execution_time': elapsed,
                'total_entities': result['linking_metrics']['total_entities'],
                'linked_entities': result['linking_metrics']['linked_entities'],
                'clusters_found': result['linking_metrics']['total_clusters'],
                'linking_rate': result['linking_metrics']['linking_rate'],
                'passed': elapsed < 2.0
            }
            
            print(f"✓ Cross-modal linking: {elapsed:.3f}s ({result['linking_metrics']['total_clusters']} clusters)")
            
        except Exception as e:
            print(f"✗ Cross-modal linking failed: {e}")
            self.results['benchmarks']['cross_modal_linking'] = {
                'error': str(e), 'passed': False
            }
    
    async def benchmark_knowledge_synthesis(self):
        """Benchmark knowledge synthesis"""
        print("\n=== Knowledge Synthesis Benchmarks ===")
        
        synthesizer = ConceptualKnowledgeSynthesizer(self.neo4j_manager, self.dtm)
        
        domains = ['Computer Science', 'Physics', 'Biology']
        results = {}
        
        for domain in domains:
            print(f"\nBenchmarking synthesis for {domain}...")
            start = time.time()
            
            try:
                result = await synthesizer.synthesize_research_insights(
                    domain=domain,
                    synthesis_strategy='abductive',
                    max_hypotheses=3
                )
                elapsed = time.time() - start
                
                results[domain] = {
                    'execution_time': elapsed,
                    'evidence_count': result['metadata']['evidence_count'],
                    'hypotheses_generated': result['metadata']['hypothesis_count'],
                    'anomalies_detected': result['synthesis_results'].get('anomalies_detected', 0),
                    'passed': elapsed < 2.0
                }
                
                print(f"✓ {domain}: {elapsed:.3f}s ({result['metadata']['hypothesis_count']} hypotheses)")
                
            except Exception as e:
                print(f"✗ {domain} failed: {e}")
                results[domain] = {'error': str(e), 'passed': False}
        
        self.results['benchmarks']['knowledge_synthesis'] = results
    
    async def benchmark_citation_impact(self):
        """Benchmark citation impact analysis"""
        print("\n=== Citation Impact Benchmarks ===")
        
        analyzer = CitationImpactAnalyzer(self.neo4j_manager, self.dtm)
        
        # Get sample entities
        query = "MATCH (n:BenchmarkNode) RETURN n.id as id LIMIT 5"
        entities = await self.neo4j_manager.execute_read_query(query)
        
        results = {}
        
        for entity in entities:
            entity_id = str(entity['id'])
            print(f"\nBenchmarking impact analysis for entity {entity_id}...")
            start = time.time()
            
            try:
                result = await analyzer.analyze_research_impact(
                    entity_id=entity_id,
                    entity_type='Paper',
                    time_window_years=5
                )
                elapsed = time.time() - start
                
                results[entity_id] = {
                    'execution_time': elapsed,
                    'total_papers': result['metadata']['total_papers'],
                    'total_citations': result['metadata']['total_citations'],
                    'h_index': result['impact_scores'].get('h_index', 0),
                    'passed': elapsed < 2.0
                }
                
                print(f"✓ Entity {entity_id}: {elapsed:.3f}s (h-index: {result['impact_scores'].get('h_index', 0)})")
                
            except Exception as e:
                print(f"✗ Entity {entity_id} failed: {e}")
                results[entity_id] = {'error': str(e), 'passed': False}
        
        self.results['benchmarks']['citation_impact'] = results
    
    def generate_summary(self):
        """Generate benchmark summary"""
        summary = {
            'total_benchmarks': 0,
            'passed': 0,
            'failed': 0,
            'average_execution_time': [],
            'all_passed': True
        }
        
        for category, benchmarks in self.results['benchmarks'].items():
            for name, result in benchmarks.items():
                if isinstance(result, dict):
                    summary['total_benchmarks'] += 1
                    
                    if result.get('passed', False):
                        summary['passed'] += 1
                    else:
                        summary['failed'] += 1
                        summary['all_passed'] = False
                    
                    if 'execution_time' in result:
                        summary['average_execution_time'].append(result['execution_time'])
        
        if summary['average_execution_time']:
            summary['average_execution_time'] = np.mean(summary['average_execution_time'])
        else:
            summary['average_execution_time'] = 0
        
        self.results['summary'] = summary
    
    async def run_all_benchmarks(self):
        """Run all benchmarks"""
        print("Starting Phase 2.1 Analytics Performance Benchmarks")
        print("=" * 50)
        
        await self.setup()
        
        try:
            await self.benchmark_graph_centrality()
            await self.benchmark_community_detection()
            await self.benchmark_cross_modal_linking()
            await self.benchmark_knowledge_synthesis()
            await self.benchmark_citation_impact()
            
            self.generate_summary()
            
            print("\n" + "=" * 50)
            print("BENCHMARK SUMMARY")
            print("=" * 50)
            print(f"Total benchmarks: {self.results['summary']['total_benchmarks']}")
            print(f"Passed: {self.results['summary']['passed']}")
            print(f"Failed: {self.results['summary']['failed']}")
            print(f"Average execution time: {self.results['summary']['average_execution_time']:.3f}s")
            print(f"All benchmarks passed: {'YES' if self.results['summary']['all_passed'] else 'NO'}")
            
            # Save results
            with open('benchmark_results.json', 'w') as f:
                json.dump(self.results, f, indent=2)
            
            print(f"\nDetailed results saved to benchmark_results.json")
            
        finally:
            await self.teardown()
        
        return self.results['summary']['all_passed']


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Benchmark graph analytics performance')
    parser.add_argument('--category', choices=['centrality', 'community', 'linking', 'synthesis', 'impact'],
                       help='Run specific benchmark category')
    args = parser.parse_args()
    
    benchmark = AnalyticsBenchmark()
    
    if args.category:
        await benchmark.setup()
        
        try:
            if args.category == 'centrality':
                await benchmark.benchmark_graph_centrality()
            elif args.category == 'community':
                await benchmark.benchmark_community_detection()
            elif args.category == 'linking':
                await benchmark.benchmark_cross_modal_linking()
            elif args.category == 'synthesis':
                await benchmark.benchmark_knowledge_synthesis()
            elif args.category == 'impact':
                await benchmark.benchmark_citation_impact()
                
            benchmark.generate_summary()
            
        finally:
            await benchmark.teardown()
    else:
        success = await benchmark.run_all_benchmarks()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())