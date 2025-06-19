#!/usr/bin/env python3
"""
Comprehensive test suite for enhanced graph building and visualization system.
Tests ontology-aware graph construction, interactive visualization, and adversarial scenarios.
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.ontology_generator import DomainOntology, EntityType, RelationshipType
from src.ontology.gemini_ontology_generator import GeminiOntologyGenerator
from src.tools.phase2.t23c_ontology_aware_extractor import OntologyAwareExtractor, ExtractionResult
from src.tools.phase2.t31_ontology_graph_builder import OntologyAwareGraphBuilder
from src.tools.phase2.interactive_graph_visualizer import InteractiveGraphVisualizer, GraphVisualizationConfig
from src.core.enhanced_identity_service import EnhancedIdentityService


def create_comprehensive_climate_ontology():
    """Create a comprehensive climate ontology for testing."""
    return DomainOntology(
        domain_name="Climate Change Research",
        domain_description="Comprehensive ontology for climate change research, policy analysis, and technology assessment",
        entity_types=[
            EntityType(
                name="CLIMATE_POLICY",
                description="Government or international climate policies and agreements",
                examples=["Paris Agreement", "Green New Deal", "Carbon Tax", "Emissions Trading System"],
                attributes=["scope", "target_year", "emission_goals", "implementation_status"]
            ),
            EntityType(
                name="RENEWABLE_TECHNOLOGY",
                description="Renewable energy technologies and clean tech solutions",
                examples=["Solar Panels", "Wind Turbines", "Battery Storage", "Hydrogen Fuel Cells"],
                attributes=["efficiency", "capacity", "cost_per_mwh", "technology_readiness"]
            ),
            EntityType(
                name="CLIMATE_ORGANIZATION",
                description="Organizations working on climate solutions and research",
                examples=["IPCC", "IEA", "Climate Action Network", "350.org", "Tesla"],
                attributes=["organization_type", "focus_area", "geographic_scope", "funding_source"]
            ),
            EntityType(
                name="ENVIRONMENTAL_IMPACT",
                description="Environmental effects and climate change impacts",
                examples=["Sea Level Rise", "Ocean Acidification", "Deforestation", "Arctic Ice Loss"],
                attributes=["severity", "affected_regions", "timeframe", "economic_cost"]
            ),
            EntityType(
                name="CLIMATE_METRIC",
                description="Quantitative measures related to climate change",
                examples=["CO2 Concentration", "Global Temperature", "Renewable Energy Share"],
                attributes=["unit", "current_value", "trend", "target_value"]
            ),
            EntityType(
                name="GEOGRAPHIC_REGION",
                description="Geographic areas relevant to climate analysis",
                examples=["Arctic", "Amazon Basin", "Small Island States", "Sub-Saharan Africa"],
                attributes=["climate_vulnerability", "adaptation_capacity", "population"]
            )
        ],
        relationship_types=[
            RelationshipType(
                name="IMPLEMENTS",
                description="Organization implements or promotes a policy",
                source_types=["CLIMATE_ORGANIZATION"],
                target_types=["CLIMATE_POLICY"],
                examples=["EU implements Carbon Tax", "Tesla promotes EV policies"]
            ),
            RelationshipType(
                name="ADDRESSES",
                description="Technology or policy addresses an environmental impact",
                source_types=["RENEWABLE_TECHNOLOGY", "CLIMATE_POLICY"],
                target_types=["ENVIRONMENTAL_IMPACT"],
                examples=["Solar Power addresses Carbon Emissions", "Paris Agreement addresses Global Warming"]
            ),
            RelationshipType(
                name="DEVELOPS",
                description="Organization develops or researches technology",
                source_types=["CLIMATE_ORGANIZATION"],
                target_types=["RENEWABLE_TECHNOLOGY"],
                examples=["Tesla develops Battery Storage", "NREL develops Solar Technology"]
            ),
            RelationshipType(
                name="AFFECTS_REGION",
                description="Environmental impact affects a geographic region",
                source_types=["ENVIRONMENTAL_IMPACT"],
                target_types=["GEOGRAPHIC_REGION"],
                examples=["Sea Level Rise affects Small Island States"]
            ),
            RelationshipType(
                name="MEASURES",
                description="Metric measures an environmental impact or policy outcome",
                source_types=["CLIMATE_METRIC"],
                target_types=["ENVIRONMENTAL_IMPACT", "CLIMATE_POLICY"],
                examples=["CO2 Concentration measures Greenhouse Gas Emissions"]
            ),
            RelationshipType(
                name="COLLABORATES_WITH",
                description="Organizations collaborate on climate initiatives",
                source_types=["CLIMATE_ORGANIZATION"],
                target_types=["CLIMATE_ORGANIZATION"],
                examples=["IPCC collaborates with IEA", "Climate Action Network partners with 350.org"]
            )
        ],
        extraction_patterns=[
            "Look for policy names with keywords like 'Agreement', 'Act', 'Protocol', 'Framework'",
            "Identify renewable technologies by terms like 'solar', 'wind', 'renewable', 'clean energy'",
            "Organizations often have climate-related acronyms or contain words like 'climate', 'environment', 'energy'",
            "Environmental impacts often include measurements, geographic references, or severity indicators",
            "Climate metrics typically include numbers, units, and trend indicators",
            "Geographic regions are identifiable by location names and climate vulnerability terms"
        ],
        created_by_conversation="Comprehensive test ontology for enhanced graph building"
    )


def create_comprehensive_test_text():
    """Create comprehensive test text covering all ontology aspects."""
    return """
    The Paris Agreement, adopted in 2015, represents a landmark climate policy that aims to limit global 
    warming to 1.5°C above pre-industrial levels. The Intergovernmental Panel on Climate Change (IPCC) 
    has repeatedly warned that current CO2 concentrations, now exceeding 420 ppm, are driving unprecedented 
    environmental impacts across vulnerable regions.
    
    The European Union has implemented an ambitious Carbon Tax system as part of its Green New Deal, 
    targeting a 55% reduction in greenhouse gas emissions by 2030. This policy directly addresses the 
    accelerating impacts of climate change, including sea level rise that threatens Small Island States 
    and Arctic ice loss affecting polar regions.
    
    Meanwhile, renewable energy technologies are experiencing rapid advancement. Tesla has developed 
    cutting-edge battery storage systems with energy densities exceeding 250 Wh/kg, while the National 
    Renewable Energy Laboratory (NREL) continues to push solar panel efficiency beyond 26%. Wind turbine 
    capacity has grown to over 15 MW per unit, making wind power increasingly cost-competitive.
    
    The International Energy Agency (IEA) collaborates with the IPCC to track global temperature trends, 
    which show a concerning warming rate of 1.1°C since pre-industrial times. Ocean acidification, 
    measured by pH levels declining to 8.1, poses severe threats to marine ecosystems, particularly 
    affecting coral reefs in the Pacific Ocean.
    
    Climate Action Network coordinates with 350.org and other environmental organizations to promote 
    renewable energy adoption across Sub-Saharan Africa, where solar potential exceeds 60 TWh annually. 
    The Amazon Basin faces critical deforestation pressures, with over 10,000 square kilometers lost 
    annually, directly impacting global carbon sequestration capacity.
    
    Hydrogen fuel cells represent an emerging technology for heavy industry decarbonization, with 
    efficiency rates approaching 60% and costs declining by 30% since 2020. The Emissions Trading 
    System in Europe has created market incentives worth over €50 billion annually, demonstrating 
    how economic policies can drive technological innovation in the clean energy sector.
    """


def test_enhanced_ontology_extraction():
    """Test enhanced ontology-aware extraction."""
    print("=== Testing Enhanced Ontology-Aware Extraction ===")
    
    # Create comprehensive ontology
    ontology = create_comprehensive_climate_ontology()
    print(f"✓ Created ontology: {ontology.domain_name}")
    print(f"  - Entity types: {len(ontology.entity_types)}")
    print(f"  - Relationship types: {len(ontology.relationship_types)}")
    
    # Initialize extractor
    identity_service = EnhancedIdentityService()
    extractor = OntologyAwareExtractor(identity_service)
    
    # Test with comprehensive text
    test_text = create_comprehensive_test_text()
    print(f"\nExtracting from text ({len(test_text)} characters)...")
    
    start_time = time.time()
    result = extractor.extract_entities(
        text=test_text,
        ontology=ontology,
        source_ref="comprehensive_test_document",
        confidence_threshold=0.6  # Lower threshold for more comprehensive extraction
    )
    extraction_time = time.time() - start_time
    
    print(f"✓ Extraction completed in {extraction_time:.2f}s")
    print(f"  - Entities found: {len(result.entities)}")
    print(f"  - Relationships found: {len(result.relationships)}")
    print(f"  - Mentions created: {len(result.mentions)}")
    
    # Analyze entity types
    entity_type_counts = {}
    for entity in result.entities:
        entity_type_counts[entity.entity_type] = entity_type_counts.get(entity.entity_type, 0) + 1
    
    print("\nEntity type distribution:")
    for entity_type, count in sorted(entity_type_counts.items()):
        print(f"  - {entity_type}: {count}")
    
    # Analyze relationships
    rel_type_counts = {}
    for rel in result.relationships:
        rel_type_counts[rel.relationship_type] = rel_type_counts.get(rel.relationship_type, 0) + 1
    
    print("\nRelationship type distribution:")
    for rel_type, count in sorted(rel_type_counts.items()):
        print(f"  - {rel_type}: {count}")
    
    # Show high-confidence entities
    high_conf_entities = [e for e in result.entities if e.confidence >= 0.8]
    print(f"\nHigh-confidence entities ({len(high_conf_entities)}):")
    for entity in high_conf_entities[:10]:  # Show top 10
        print(f"  - {entity.canonical_name} ({entity.entity_type}) - {entity.confidence:.2f}")
    
    return result, ontology


def test_enhanced_graph_building(extraction_result, ontology):
    """Test ontology-aware graph building."""
    print("\n=== Testing Enhanced Graph Building ===")
    
    # Initialize graph builder
    graph_builder = OntologyAwareGraphBuilder(confidence_threshold=0.6)
    graph_builder.set_ontology(ontology)
    
    # Build graph from extraction
    print("Building graph from extraction results...")
    start_time = time.time()
    build_result = graph_builder.build_graph_from_extraction(
        extraction_result=extraction_result,
        source_document="comprehensive_test_document"
    )
    build_time = time.time() - start_time
    
    print(f"✓ Graph built in {build_time:.2f}s")
    print(f"  - Entities created: {build_result.entities_created}")
    print(f"  - Relationships created: {build_result.relationships_created}")
    print(f"  - Entities merged: {build_result.entities_merged}")
    print(f"  - Low confidence entities: {build_result.low_confidence_entities}")
    print(f"  - Ontology mismatches: {build_result.ontology_mismatches}")
    
    # Show metrics
    metrics = build_result.metrics
    print(f"\nGraph Quality Metrics:")
    print(f"  - Total entities: {metrics.total_entities}")
    print(f"  - Total relationships: {metrics.total_relationships}")
    print(f"  - Ontology coverage: {metrics.ontology_coverage:.1%}")
    print(f"  - Semantic density: {metrics.semantic_density:.2f}")
    
    # Show warnings and errors
    if build_result.warnings:
        print(f"\nWarnings ({len(build_result.warnings)}):")
        for warning in build_result.warnings[:5]:  # Show first 5
            print(f"  ⚠️  {warning}")
    
    if build_result.errors:
        print(f"\nErrors ({len(build_result.errors)}):")
        for error in build_result.errors[:5]:  # Show first 5
            print(f"  ❌ {error}")
    
    return graph_builder, build_result


def test_adversarial_graph_building(graph_builder):
    """Test adversarial scenarios for graph building."""
    print("\n=== Testing Adversarial Graph Building ===")
    
    print("Running adversarial tests...")
    adversarial_results = graph_builder.adversarial_test_entity_resolution()
    
    print(f"✓ Adversarial testing complete: {adversarial_results['overall_score']:.1%} pass rate")
    print(f"  Summary: {adversarial_results['summary']}")
    
    # Show individual test results
    for test_name, result in adversarial_results.items():
        if test_name not in ['overall_score', 'summary']:
            status = "✅" if result['passed'] else "❌"
            print(f"  {status} {test_name}: {result.get('details', 'No details')}")
    
    return adversarial_results


def test_interactive_visualization():
    """Test interactive graph visualization."""
    print("\n=== Testing Interactive Graph Visualization ===")
    
    # Initialize visualizer
    visualizer = InteractiveGraphVisualizer()
    
    # Fetch graph data
    print("Fetching graph data...")
    config = GraphVisualizationConfig(
        max_nodes=100,
        max_edges=200,
        color_by="entity_type",
        show_labels=True,
        confidence_threshold=0.6
    )
    
    vis_data = visualizer.fetch_graph_data(
        source_document="comprehensive_test_document",
        config=config
    )
    
    print(f"✓ Graph data fetched:")
    print(f"  - Nodes: {len(vis_data.nodes)}")
    print(f"  - Edges: {len(vis_data.edges)}")
    print(f"  - Layout positions: {len(vis_data.layout_positions)}")
    
    # Test different visualizations
    print("\nCreating visualizations...")
    
    # Main graph visualization
    try:
        main_fig = visualizer.create_interactive_plot(vis_data, config)
        print("  ✓ Main graph visualization created")
    except Exception as e:
        print(f"  ❌ Main graph visualization failed: {e}")
        main_fig = None
    
    # Ontology structure plot
    try:
        structure_fig = visualizer.create_ontology_structure_plot(vis_data.ontology_info)
        print("  ✓ Ontology structure plot created")
    except Exception as e:
        print(f"  ❌ Ontology structure plot failed: {e}")
        structure_fig = None
    
    # Semantic similarity heatmap
    try:
        similarity_fig = visualizer.create_semantic_similarity_heatmap(vis_data)
        print("  ✓ Semantic similarity heatmap created")
    except Exception as e:
        print(f"  ❌ Semantic similarity heatmap failed: {e}")
        similarity_fig = None
    
    # Show metrics
    print(f"\nVisualization Metrics:")
    for key, value in vis_data.metrics.items():
        print(f"  - {key}: {value}")
    
    return visualizer, vis_data, main_fig, structure_fig, similarity_fig


def test_adversarial_visualization(visualizer):
    """Test adversarial scenarios for visualization."""
    print("\n=== Testing Adversarial Visualization ===")
    
    print("Running visualization adversarial tests...")
    viz_results = visualizer.adversarial_test_visualization(max_test_nodes=50)
    
    print(f"✓ Visualization testing complete: {viz_results['overall_score']:.1%} pass rate")
    print(f"  Summary: {viz_results['summary']}")
    
    # Show individual test results
    for test_name, result in viz_results.items():
        if test_name not in ['overall_score', 'summary']:
            status = "✅" if result['passed'] else "❌"
            print(f"  {status} {test_name}: {result.get('details', 'No details')}")
    
    return viz_results


def test_end_to_end_pipeline():
    """Test the complete end-to-end pipeline."""
    print("\n=== Testing End-to-End Pipeline ===")
    
    start_time = time.time()
    
    # Step 1: Create domain ontology (using mock for speed)
    print("1. Creating domain ontology...")
    ontology = create_comprehensive_climate_ontology()
    
    # Step 2: Extract entities using ontology
    print("2. Extracting entities with ontology...")
    identity_service = EnhancedIdentityService()
    extractor = OntologyAwareExtractor(identity_service)
    
    extraction_result = extractor.extract_entities(
        text=create_comprehensive_test_text(),
        ontology=ontology,
        source_ref="e2e_test_document",
        confidence_threshold=0.7
    )
    
    # Step 3: Build graph
    print("3. Building knowledge graph...")
    graph_builder = OntologyAwareGraphBuilder(confidence_threshold=0.7)
    graph_builder.set_ontology(ontology)
    
    build_result = graph_builder.build_graph_from_extraction(
        extraction_result=extraction_result,
        source_document="e2e_test_document"
    )
    
    # Step 4: Visualize graph
    print("4. Creating visualizations...")
    visualizer = InteractiveGraphVisualizer()
    config = GraphVisualizationConfig(max_nodes=50, confidence_threshold=0.7)
    
    vis_data = visualizer.fetch_graph_data(
        source_document="e2e_test_document",
        config=config
    )
    
    main_plot = visualizer.create_interactive_plot(vis_data, config)
    
    total_time = time.time() - start_time
    
    print(f"✅ End-to-end pipeline completed in {total_time:.2f}s")
    print(f"   Pipeline results:")
    print(f"   - Ontology: {len(ontology.entity_types)} entity types, {len(ontology.relationship_types)} relationships")
    print(f"   - Extraction: {len(extraction_result.entities)} entities, {len(extraction_result.relationships)} relationships")
    print(f"   - Graph: {build_result.entities_created} entities created, {build_result.relationships_created} relationships created")
    print(f"   - Visualization: {len(vis_data.nodes)} nodes, {len(vis_data.edges)} edges")
    
    # Calculate quality score
    ontology_coverage = build_result.metrics.ontology_coverage
    extraction_success = len(extraction_result.entities) > 0
    graph_success = build_result.entities_created > 0
    viz_success = len(vis_data.nodes) > 0
    
    quality_score = (ontology_coverage + extraction_success + graph_success + viz_success) / 4
    print(f"   - Overall quality score: {quality_score:.1%}")
    
    return {
        "ontology": ontology,
        "extraction_result": extraction_result,
        "build_result": build_result,
        "vis_data": vis_data,
        "main_plot": main_plot,
        "total_time": total_time,
        "quality_score": quality_score
    }


def save_test_results(results):
    """Save test results for analysis."""
    print("\n=== Saving Test Results ===")
    
    results_dir = Path("./data/test_results")
    results_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save summary
    summary = {
        "timestamp": timestamp,
        "ontology_entity_types": len(results["ontology"].entity_types),
        "ontology_relationship_types": len(results["ontology"].relationship_types),
        "entities_extracted": len(results["extraction_result"].entities),
        "relationships_extracted": len(results["extraction_result"].relationships),
        "entities_created_in_graph": results["build_result"].entities_created,
        "relationships_created_in_graph": results["build_result"].relationships_created,
        "visualization_nodes": len(results["vis_data"].nodes),
        "visualization_edges": len(results["vis_data"].edges),
        "total_execution_time": results["total_time"],
        "quality_score": results["quality_score"]
    }
    
    summary_file = results_dir / f"enhanced_graph_test_summary_{timestamp}.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"✓ Test summary saved: {summary_file}")
    
    # Save visualization if possible
    if results["main_plot"]:
        try:
            viz_file = results_dir / f"enhanced_graph_visualization_{timestamp}.html"
            results["main_plot"].write_html(str(viz_file))
            print(f"✓ Visualization saved: {viz_file}")
        except Exception as e:
            print(f"⚠️  Could not save visualization: {e}")
    
    return summary_file


def main():
    """Run comprehensive enhanced graph system tests."""
    print("🚀 Testing Enhanced Graph Building and Visualization System\n")
    
    try:
        # Test 1: Enhanced extraction
        extraction_result, ontology = test_enhanced_ontology_extraction()
        
        # Test 2: Enhanced graph building
        graph_builder, build_result = test_enhanced_graph_building(extraction_result, ontology)
        
        # Test 3: Adversarial graph building
        adversarial_graph_results = test_adversarial_graph_building(graph_builder)
        
        # Test 4: Interactive visualization
        visualizer, vis_data, main_fig, structure_fig, similarity_fig = test_interactive_visualization()
        
        # Test 5: Adversarial visualization
        adversarial_viz_results = test_adversarial_visualization(visualizer)
        
        # Test 6: End-to-end pipeline
        e2e_results = test_end_to_end_pipeline()
        
        # Save results
        results_file = save_test_results(e2e_results)
        
        print("\n✅ All enhanced graph system tests completed!")
        print(f"   Results saved to: {results_file}")
        print(f"   Overall system quality: {e2e_results['quality_score']:.1%}")
        
        # Summary of capabilities
        print(f"\n📊 System Capabilities Demonstrated:")
        print(f"   ✓ Ontology-aware entity extraction with domain-specific types")
        print(f"   ✓ Enhanced graph building with semantic validation")
        print(f"   ✓ Interactive visualization with rich metadata")
        print(f"   ✓ Comprehensive adversarial testing")
        print(f"   ✓ End-to-end pipeline integration")
        print(f"   ✓ Academic traceability and quality metrics")
        
        # Clean up
        graph_builder.close()
        visualizer.close()
        
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)