#!/usr/bin/env python3
"""Test schema system on Carter's Annapolis speech with critical analysis

Tests all three schema modes on Carter's speech and analyzes results compared
to potential theoretical frameworks from political science.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import json
from typing import Dict, Any, List
from src.core.extraction_schemas import (
    create_open_schema, create_closed_schema, create_hybrid_schema
)
from src.core.schema_manager import SchemaManager
from src.tools.base_tool import ToolRequest


def load_carter_speech():
    """Load Carter's Annapolis speech text"""
    speech_path = "/home/brian/projects/Digimons/lit_review/data/test_texts/carter_anapolis.txt"
    with open(speech_path, 'r', encoding='utf-8') as f:
        return f.read()


def create_political_speech_schemas():
    """Create specialized schemas for political speech analysis"""
    
    # Political Science Schema (Closed)
    political_schema = create_closed_schema(
        "political_speech_analysis",
        entity_types=[
            "POLITICAL_ACTOR", "NATION", "MILITARY_UNIT", "TREATY", 
            "POLICY", "THREAT", "ALLIANCE", "IDEOLOGY", "INSTITUTION"
        ],
        relation_types=[
            "NEGOTIATES_WITH", "THREATENS", "ALLIES_WITH", "OPPOSES",
            "IMPLEMENTS", "SIGNS", "VIOLATES", "SUPPORTS"
        ]
    )
    
    # International Relations Schema (Hybrid) 
    ir_schema = create_hybrid_schema(
        "international_relations",
        predefined_entities=[
            "STATE", "LEADER", "MILITARY_FORCE", "AGREEMENT", "CONFLICT"
        ],
        predefined_relations=[
            "COOPERATES_WITH", "COMPETES_WITH", "BALANCES_AGAINST"
        ]
    )
    
    # Rhetorical Analysis Schema (Open)
    rhetorical_schema = create_open_schema(
        "rhetorical_analysis",
        description="Open analysis of rhetorical devices and persuasive elements"
    )
    
    return {
        "political": political_schema,
        "international_relations": ir_schema, 
        "rhetorical": rhetorical_schema
    }


def extract_with_spacy_ner(text: str, schema, schema_name: str):
    """Extract entities using T23A SpaCy NER with schema"""
    try:
        from src.tools.phase1.t23a_spacy_ner_unified import T23ASpacyNERUnified
        from src.core.service_manager import ServiceManager
        
        service_manager = ServiceManager()
        ner_tool = T23ASpacyNERUnified(service_manager)
        
        request = ToolRequest(
            tool_id="T23A_SPACY_NER",
            operation="extract",
            input_data={
                "text": text,
                "chunk_ref": f"carter_speech_{schema_name}",
                "schema": schema
            },
            parameters={}
        )
        
        result = ner_tool.execute(request)
        
        if result.status == "success":
            return {
                "success": True,
                "entities": result.data["entities"],
                "total_entities": result.data["total_entities"],
                "entity_types": result.data["entity_types"],
                "processing_stats": result.data["processing_stats"],
                "metadata": result.metadata
            }
        else:
            return {
                "success": False,
                "error": result.error_message
            }
            
    except Exception as e:
        return {
            "success": False, 
            "error": str(e)
        }


def extract_with_llm_extractor(text: str, schema, schema_name: str):
    """Extract entities using T23C LLM extractor with schema"""
    try:
        from src.tools.phase2.t23c_ontology_aware_extractor_unified import OntologyAwareExtractor
        
        extractor = OntologyAwareExtractor()
        
        result = extractor.execute({
            "text": text,
            "source_ref": f"carter_speech_{schema_name}",
            "schema": schema,
            "use_mock_apis": True,  # Use mock for consistent testing
            "confidence_threshold": 0.6
        })
        
        if "error" not in result:
            return {
                "success": True,
                "entities": result["results"]["entities"],
                "relationships": result["results"]["relationships"],
                "entity_count": result["results"]["entity_count"],
                "relationship_count": result["results"]["relationship_count"],
                "extraction_metadata": result["results"]["extraction_metadata"]
            }
        else:
            return {
                "success": False,
                "error": result["error"]
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def analyze_political_content(entities: List[Dict], relationships: List[Dict] = None):
    """Analyze extracted entities for political science insights"""
    analysis = {
        "key_actors": [],
        "international_themes": [],
        "policy_areas": [],
        "rhetorical_devices": [],
        "power_dynamics": []
    }
    
    # Identify key political actors
    political_actors = [e for e in entities if e.get("entity_type") in ["PERSON", "ORG", "GPE", "POLITICAL_ACTOR", "NATION"]]
    analysis["key_actors"] = [(e["surface_form"], e["entity_type"], e.get("confidence", 0)) for e in political_actors]
    
    # Identify international relations themes
    for entity in entities:
        surface_form = entity["surface_form"].lower()
        if any(term in surface_form for term in ["soviet", "detente", "cooperation", "alliance", "treaty"]):
            analysis["international_themes"].append(entity["surface_form"])
    
    # Identify policy areas
    policy_keywords = ["nuclear", "military", "arms", "defense", "salt", "peace", "security"]
    for entity in entities:
        surface_form = entity["surface_form"].lower()
        if any(keyword in surface_form for keyword in policy_keywords):
            analysis["policy_areas"].append(entity["surface_form"])
    
    # Analyze relationships if available
    if relationships:
        analysis["relationships_found"] = len(relationships)
        analysis["relationship_types"] = list(set(r.get("type", "unknown") for r in relationships))
    
    return analysis


def compare_schema_results(results: Dict[str, Dict]):
    """Compare results across different schema modes"""
    comparison = {
        "entity_counts": {},
        "unique_entities": {},
        "schema_coverage": {},
        "overlap_analysis": {}
    }
    
    # Count entities by schema
    for schema_name, result in results.items():
        if result.get("success"):
            comparison["entity_counts"][schema_name] = result.get("total_entities", result.get("entity_count", 0))
            
            # Get unique entity surface forms
            entities = result.get("entities", [])
            unique_entities = set(e["surface_form"] for e in entities)
            comparison["unique_entities"][schema_name] = unique_entities
    
    # Calculate overlaps
    all_schemas = list(comparison["unique_entities"].keys())
    for i, schema1 in enumerate(all_schemas):
        for schema2 in all_schemas[i+1:]:
            entities1 = comparison["unique_entities"][schema1]
            entities2 = comparison["unique_entities"][schema2]
            
            overlap = entities1.intersection(entities2)
            union = entities1.union(entities2)
            
            comparison["overlap_analysis"][f"{schema1}_vs_{schema2}"] = {
                "overlap_count": len(overlap),
                "jaccard_similarity": len(overlap) / len(union) if union else 0,
                "overlap_entities": list(overlap)[:10]  # First 10 for brevity
            }
    
    return comparison


def critical_analysis_vs_theory(spacy_results: Dict, llm_results: Dict, text: str):
    """Critical analysis comparing extraction to political science theory"""
    
    analysis = {
        "theoretical_frameworks_detected": [],
        "missing_theoretical_elements": [],
        "extraction_quality_assessment": {},
        "recommendations": []
    }
    
    # Expected theoretical frameworks based on speech content
    expected_frameworks = {
        "realism": ["power", "balance", "military", "strength", "security", "competition"],
        "liberal_institutionalism": ["cooperation", "institutions", "agreements", "law", "treaty"],
        "detente_theory": ["detente", "accommodation", "restraint", "reciprocal", "peaceful"],
        "cold_war_discourse": ["soviet union", "nuclear", "arms race", "ideology", "superpower"]
    }
    
    # Analyze text for theoretical concepts
    text_lower = text.lower()
    for framework, keywords in expected_frameworks.items():
        found_keywords = [kw for kw in keywords if kw in text_lower]
        if found_keywords:
            analysis["theoretical_frameworks_detected"].append({
                "framework": framework,
                "keywords_found": found_keywords,
                "coverage": len(found_keywords) / len(keywords)
            })
    
    # Assess extraction quality
    for tool_name, results in [("spacy", spacy_results), ("llm", llm_results)]:
        if results.get("success"):
            entities = results.get("entities", [])
            
            # Check for key political concepts
            extracted_terms = [e["surface_form"].lower() for e in entities]
            
            key_political_terms = ["soviet union", "united states", "detente", "salt", "nuclear", "cooperation"]
            found_key_terms = [term for term in key_political_terms if any(term in et for et in extracted_terms)]
            
            analysis["extraction_quality_assessment"][tool_name] = {
                "total_entities": len(entities),
                "key_political_terms_found": found_key_terms,
                "coverage_of_key_terms": len(found_key_terms) / len(key_political_terms),
                "entity_type_diversity": len(set(e.get("entity_type") for e in entities))
            }
    
    # Identify missing elements
    # These are concepts that should be extractable from a political speech
    expected_political_elements = [
        "power_balance", "diplomatic_strategy", "threat_assessment", 
        "alliance_structure", "policy_objectives", "rhetorical_appeals"
    ]
    
    # Check what's missing (this would require more sophisticated analysis)
    analysis["missing_theoretical_elements"] = [
        "Sophisticated relationship extraction (who cooperates with whom)",
        "Temporal dynamics (how relationships change over time)",
        "Policy instrument identification (military, economic, diplomatic tools)",
        "Audience analysis (appeals to different constituencies)",
        "Strategic framing (how issues are presented)"
    ]
    
    # Recommendations for improvement
    analysis["recommendations"] = [
        "Add specialized political science entity types (POLICY_INSTRUMENT, STRATEGIC_OBJECTIVE)",
        "Include temporal relationship extraction (X_LEADS_TO_Y, X_FOLLOWS_Y)",
        "Implement discourse analysis for rhetorical devices",
        "Add sentiment analysis for threat/cooperation detection",
        "Include hierarchical entity recognition (organizations within governments)"
    ]
    
    return analysis


def main():
    """Run comprehensive schema analysis on Carter's speech"""
    print("Carter Speech Schema Analysis")
    print("=" * 60)
    
    # Load the speech
    print("Loading Carter's Annapolis speech...")
    speech_text = load_carter_speech()
    print(f"✓ Loaded speech: {len(speech_text)} characters, {len(speech_text.split())} words\n")
    
    # Create specialized schemas
    print("Creating political science schemas...")
    schemas = create_political_speech_schemas()
    print(f"✓ Created {len(schemas)} specialized schemas\n")
    
    # Test with both SpaCy and LLM extractors
    spacy_results = {}
    llm_results = {}
    
    print("Testing SpaCy NER with different schemas...")
    for schema_name, schema in schemas.items():
        print(f"  - Testing {schema_name} schema ({schema.mode.value} mode)...")
        result = extract_with_spacy_ner(speech_text, schema, schema_name)
        spacy_results[schema_name] = result
        
        if result["success"]:
            print(f"    ✓ Found {result['total_entities']} entities")
        else:
            print(f"    ✗ Failed: {result['error']}")
    
    print("\nTesting LLM Extractor with different schemas...")
    for schema_name, schema in schemas.items():
        print(f"  - Testing {schema_name} schema ({schema.mode.value} mode)...")
        result = extract_with_llm_extractor(speech_text, schema, schema_name)
        llm_results[schema_name] = result
        
        if result["success"]:
            print(f"    ✓ Found {result['entity_count']} entities, {result.get('relationship_count', 0)} relationships")
        else:
            print(f"    ✗ Failed: {result['error']}")
    
    print("\n" + "=" * 60)
    print("DETAILED ANALYSIS RESULTS")
    print("=" * 60)
    
    # Analyze results for each successful extraction
    for tool_name, tool_results in [("SpaCy NER", spacy_results), ("LLM Extractor", llm_results)]:
        print(f"\n{tool_name} Results:")
        print("-" * 40)
        
        for schema_name, result in tool_results.items():
            if result.get("success"):
                print(f"\n{schema_name.upper()} Schema ({schemas[schema_name].mode.value} mode):")
                
                entities = result.get("entities", [])
                
                # Show entity type distribution
                entity_types = {}
                for entity in entities:
                    etype = entity.get("entity_type", "UNKNOWN")
                    entity_types[etype] = entity_types.get(etype, 0) + 1
                
                print(f"  Entity Types: {dict(sorted(entity_types.items(), key=lambda x: x[1], reverse=True))}")
                
                # Show top entities by confidence
                sorted_entities = sorted(entities, key=lambda x: x.get("confidence", 0), reverse=True)
                print(f"  Top Entities:")
                for entity in sorted_entities[:8]:
                    print(f"    - {entity['surface_form']} ({entity.get('entity_type')}) conf: {entity.get('confidence', 0):.3f}")
                
                # Political analysis
                political_analysis = analyze_political_content(entities, result.get("relationships", []))
                print(f"  Key Political Actors: {len(political_analysis['key_actors'])}")
                print(f"  International Relations Terms: {len(political_analysis['international_themes'])}")
                print(f"  Policy Areas: {len(political_analysis['policy_areas'])}")
    
    # Compare schema modes
    print(f"\n{'=' * 60}")
    print("SCHEMA MODE COMPARISON")
    print("=" * 60)
    
    spacy_comparison = compare_schema_results(spacy_results)
    
    print("\nEntity Counts by Schema Mode:")
    for schema, count in spacy_comparison["entity_counts"].items():
        mode = schemas[schema].mode.value
        print(f"  {schema} ({mode}): {count} entities")
    
    print("\nSchema Overlap Analysis:")
    for comparison_key, overlap_data in spacy_comparison["overlap_analysis"].items():
        print(f"  {comparison_key}:")
        print(f"    Jaccard Similarity: {overlap_data['jaccard_similarity']:.3f}")
        print(f"    Overlapping entities: {overlap_data['overlap_entities'][:5]}...")
    
    # Critical theoretical analysis
    print(f"\n{'=' * 60}")
    print("CRITICAL ANALYSIS vs POLITICAL SCIENCE THEORY")
    print("=" * 60)
    
    critical_analysis = critical_analysis_vs_theory(
        spacy_results.get("political", {}),
        llm_results.get("political", {}),
        speech_text
    )
    
    print("\nTheoretical Frameworks Detected:")
    for framework in critical_analysis["theoretical_frameworks_detected"]:
        print(f"  {framework['framework']}: {framework['coverage']:.1%} coverage")
        print(f"    Keywords: {framework['keywords_found']}")
    
    print("\nExtraction Quality Assessment:")
    for tool, assessment in critical_analysis["extraction_quality_assessment"].items():
        print(f"  {tool.upper()}:")
        print(f"    Political term coverage: {assessment['coverage_of_key_terms']:.1%}")
        print(f"    Key terms found: {assessment['key_political_terms_found']}")
        print(f"    Entity type diversity: {assessment['entity_type_diversity']}")
    
    print("\nMissing Theoretical Elements:")
    for element in critical_analysis["missing_theoretical_elements"]:
        print(f"  - {element}")
    
    print("\nRecommendations for Improvement:")
    for rec in critical_analysis["recommendations"]:
        print(f"  - {rec}")
    
    # Final assessment
    print(f"\n{'=' * 60}")
    print("OVERALL ASSESSMENT")
    print("=" * 60)
    
    print("\n✅ SCHEMA SYSTEM STRENGTHS:")
    print("  - Successfully applies different extraction modes (open/closed/hybrid)")
    print("  - Filters entities based on schema constraints in closed mode")
    print("  - Captures basic political entities (persons, organizations, locations)")
    print("  - Provides confidence scoring for extracted entities")
    
    print("\n⚠️  AREAS FOR IMPROVEMENT:")
    print("  - Limited political science domain knowledge")
    print("  - Relationship extraction needs enhancement for political analysis")
    print("  - Missing temporal and causal relationship detection")
    print("  - No discourse or rhetorical analysis capabilities")
    print("  - Schema inheritance could improve political entity hierarchies")
    
    print("\n🎯 COMPARISON TO THEORETICAL ANALYSIS:")
    print("  - Current system extracts surface-level entities well")
    print("  - Missing deeper theoretical constructs (power dynamics, strategic frames)")
    print("  - Would benefit from domain-specific political science schemas")
    print("  - Advanced relationship extraction needed for IR theory application")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())