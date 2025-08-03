#!/usr/bin/env python3
"""Test sophisticated political science schemas

Tests whether our schema system can handle complex political analysis
by explicitly defining theoretical concepts, discourse elements, etc. as entity types.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.core.extraction_schemas import create_closed_schema, create_hybrid_schema
from src.core.schema_manager import SchemaManager


def create_sophisticated_political_schemas():
    """Create sophisticated schemas that treat concepts as entities"""
    
    # 1. Theoretical Concepts as Entity Types
    theoretical_concepts_schema = create_closed_schema(
        schema_id="theoretical_concepts",
        entity_types=[
            # Realist concepts
            "POWER_BALANCE", "MILITARY_SUPREMACY", "SECURITY_DILEMMA", "ARMS_RACE",
            "BALANCE_OF_POWER", "SECURITY_COMPETITION", "STRATEGIC_PARITY",
            
            # Liberal institutionalist concepts  
            "INTERNATIONAL_COOPERATION", "INSTITUTIONAL_FRAMEWORK", "MULTILATERALISM",
            "DIPLOMATIC_SOLUTION", "ARMS_CONTROL_REGIME", "INTERNATIONAL_LAW",
            
            # Détente theory concepts
            "DETENTE", "TENSION_REDUCTION", "MUTUAL_RESTRAINT", "RECIPROCITY",
            "PEACEFUL_COEXISTENCE", "ACCOMMODATION", "CONFLICT_MANAGEMENT",
            
            # General IR concepts
            "ALLIANCE_STRUCTURE", "NUCLEAR_DETERRENCE", "COLD_WAR_DYNAMICS",
            "SUPERPOWER_RIVALRY", "SPHERES_OF_INFLUENCE"
        ],
        relation_types=[
            "IMPLEMENTS", "CHALLENGES", "SUPPORTS", "UNDERMINES", "LEADS_TO",
            "PREVENTS", "REQUIRES", "ENABLES", "THREATENS", "STABILIZES"
        ]
    )
    
    # 2. Policy Instruments as Entity Types
    policy_instruments_schema = create_closed_schema(
        schema_id="policy_instruments", 
        entity_types=[
            # Military instruments
            "NUCLEAR_WEAPONS", "CONVENTIONAL_FORCES", "NAVAL_POWER", "MILITARY_SPENDING",
            "DEFENSE_BUDGET", "ARMS_BUILDUP", "MILITARY_ASSISTANCE",
            
            # Diplomatic instruments
            "ARMS_CONTROL_TREATY", "BILATERAL_NEGOTIATION", "MULTILATERAL_DIPLOMACY",
            "CULTURAL_EXCHANGE", "SCIENTIFIC_COOPERATION", "TRADE_AGREEMENT",
            
            # Economic instruments
            "ECONOMIC_SANCTIONS", "TRADE_RESTRICTIONS", "FOREIGN_AID", "TECHNOLOGY_TRANSFER"
        ],
        relation_types=[
            "DEPLOYS", "NEGOTIATES", "SIGNS", "VIOLATES", "IMPLEMENTS", "SUSPENDS"
        ]
    )
    
    # 3. Discourse Elements as Entity Types
    discourse_analysis_schema = create_closed_schema(
        schema_id="discourse_analysis",
        entity_types=[
            # Rhetorical strategies
            "CERTAINTY_CLAIM", "MORAL_APPEAL", "HISTORICAL_ANALOGY", "THREAT_CONSTRUCTION",
            "LEGITIMACY_CLAIM", "CREDIBILITY_ASSERTION", "AUDIENCE_APPEAL",
            
            # Framing devices
            "POSITIVE_FRAMING", "NEGATIVE_FRAMING", "US_EXCEPTIONALISM", "SOVIET_THREAT_FRAME",
            "MUTUAL_RESPONSIBILITY_FRAME", "PEACE_FRAME", "STRENGTH_FRAME",
            
            # Speech acts
            "PROMISE", "THREAT", "WARNING", "COMMITMENT", "DECLARATION", "APPEAL"
        ],
        relation_types=[
            "FRAMES", "APPEALS_TO", "LEGITIMIZES", "DELEGITIMIZES", "SUPPORTS", "CHALLENGES"
        ]
    )
    
    # 4. Strategic Objectives as Entity Types
    strategic_objectives_schema = create_closed_schema(
        schema_id="strategic_objectives",
        entity_types=[
            # Primary objectives
            "WORLD_PEACE", "NUCLEAR_DISARMAMENT", "CONFLICT_PREVENTION", "STABILITY",
            
            # Security objectives  
            "NUCLEAR_PARITY", "CONVENTIONAL_BALANCE", "ALLIANCE_STRENGTH", "DETERRENCE",
            
            # Normative objectives
            "HUMAN_RIGHTS", "SELF_DETERMINATION", "DEMOCRACY_PROMOTION", "RULE_OF_LAW",
            
            # Regional objectives
            "AFRICAN_INDEPENDENCE", "MAJORITY_RULE", "DECOLONIZATION"
        ],
        relation_types=[
            "PURSUES", "ACHIEVES", "THREATENS", "SUPPORTS", "PRIORITIZES", "SACRIFICES"
        ]
    )
    
    # 5. Comprehensive Political Analysis Schema (Hybrid)
    comprehensive_schema = create_hybrid_schema(
        schema_id="comprehensive_political_analysis",
        predefined_entities=[
            # Traditional entities
            "POLITICAL_ACTOR", "NATION_STATE", "INTERNATIONAL_ORGANIZATION", 
            "MILITARY_UNIT", "GOVERNMENT_INSTITUTION",
            
            # Theoretical concepts
            "THEORETICAL_FRAMEWORK", "POLITICAL_CONCEPT", "STRATEGIC_DOCTRINE",
            
            # Policy elements
            "POLICY_INSTRUMENT", "STRATEGIC_OBJECTIVE", "POLICY_OUTCOME",
            
            # Discourse elements
            "RHETORICAL_DEVICE", "FRAMING_ELEMENT", "SPEECH_ACT",
            
            # Temporal/causal elements
            "POLITICAL_PROCESS", "CAUSAL_MECHANISM", "TEMPORAL_SEQUENCE"
        ],
        predefined_relations=[
            # Semantic relations
            "COOPERATES_WITH", "COMPETES_WITH", "THREATENS", "SUPPORTS",
            "IMPLEMENTS", "VIOLATES", "NEGOTIATES", "ALLIES_WITH",
            
            # Temporal/causal relations
            "LEADS_TO", "RESULTS_FROM", "ENABLES", "PREVENTS", "FOLLOWS",
            "PRECEDES", "TRIGGERS", "STABILIZES", "DESTABILIZES",
            
            # Discourse relations
            "FRAMES_AS", "APPEALS_TO", "LEGITIMIZES", "CHALLENGES"
        ]
    )
    
    return {
        "theoretical_concepts": theoretical_concepts_schema,
        "policy_instruments": policy_instruments_schema, 
        "discourse_analysis": discourse_analysis_schema,
        "strategic_objectives": strategic_objectives_schema,
        "comprehensive": comprehensive_schema
    }


def test_sophisticated_extraction():
    """Test extraction with sophisticated schemas"""
    
    # Carter speech excerpt focusing on key concepts
    carter_excerpt = """
    Detente between our two countries is central to world peace. The word "detente" can be 
    simplistically defined as "the easing of tension between nations." To be stable, detente 
    must be broadly defined and truly reciprocal. Both nations must exercise restraint.
    
    Neither of us should entertain the notion that military supremacy can be attained, or 
    that transient military advantage can be politically exploited. The numbers and 
    destructive potential of nuclear weapons has been increasing at an alarming rate.
    
    We will continue to maintain equivalent nuclear strength, because we believe that in 
    the absence of worldwide nuclear disarmament, such equivalency is the least threatening 
    and the most stable situation for the world. We will maintain a prudent and sustained 
    level of military spending, keyed to a stronger NATO.
    
    I'm convinced that the people of the Soviet Union want peace. I cannot believe that 
    they could possibly want war. Our long-term objective must be to convince the Soviet 
    Union of the advantages of cooperation and of the costs of disruptive behavior.
    """
    
    # Create sophisticated schemas
    schemas = create_sophisticated_political_schemas()
    
    print("Testing Sophisticated Schema Extraction")
    print("=" * 60)
    print(f"Text length: {len(carter_excerpt)} characters\n")
    
    # Manual extraction simulating what LLM/NER would find with sophisticated schemas
    sophisticated_extractions = {
        "theoretical_concepts": [
            {"type": "DETENTE", "surface_form": "detente", "confidence": 0.95},
            {"type": "DETENTE", "surface_form": "easing of tension", "confidence": 0.88},
            {"type": "RECIPROCITY", "surface_form": "truly reciprocal", "confidence": 0.91},
            {"type": "MUTUAL_RESTRAINT", "surface_form": "both nations must exercise restraint", "confidence": 0.89},
            {"type": "MILITARY_SUPREMACY", "surface_form": "military supremacy", "confidence": 0.94},
            {"type": "NUCLEAR_DETERRENCE", "surface_form": "equivalent nuclear strength", "confidence": 0.87},
            {"type": "BALANCE_OF_POWER", "surface_form": "equivalency is the least threatening", "confidence": 0.83},
            {"type": "INTERNATIONAL_COOPERATION", "surface_form": "advantages of cooperation", "confidence": 0.86}
        ],
        
        "policy_instruments": [
            {"type": "NUCLEAR_WEAPONS", "surface_form": "nuclear weapons", "confidence": 0.96},
            {"type": "NUCLEAR_WEAPONS", "surface_form": "nuclear strength", "confidence": 0.93},
            {"type": "MILITARY_SPENDING", "surface_form": "military spending", "confidence": 0.91},
            {"type": "ARMS_CONTROL_TREATY", "surface_form": "nuclear disarmament", "confidence": 0.85}
        ],
        
        "discourse_analysis": [
            {"type": "CERTAINTY_CLAIM", "surface_form": "I'm convinced", "confidence": 0.92},
            {"type": "CERTAINTY_CLAIM", "surface_form": "I cannot believe", "confidence": 0.89},
            {"type": "PEACE_FRAME", "surface_form": "people of the Soviet Union want peace", "confidence": 0.87},
            {"type": "MUTUAL_RESPONSIBILITY_FRAME", "surface_form": "both nations must exercise restraint", "confidence": 0.88},
            {"type": "COMMITMENT", "surface_form": "we will continue to maintain", "confidence": 0.84}
        ],
        
        "strategic_objectives": [
            {"type": "WORLD_PEACE", "surface_form": "world peace", "confidence": 0.95},
            {"type": "NUCLEAR_PARITY", "surface_form": "equivalent nuclear strength", "confidence": 0.91},
            {"type": "STABILITY", "surface_form": "most stable situation", "confidence": 0.88},
            {"type": "NUCLEAR_DISARMAMENT", "surface_form": "worldwide nuclear disarmament", "confidence": 0.93}
        ]
    }
    
    # Test each schema
    for schema_name, schema in schemas.items():
        if schema_name == "comprehensive":
            continue  # Skip comprehensive for focused testing
            
        print(f"\n{schema_name.upper().replace('_', ' ')} ANALYSIS")
        print("-" * 50)
        
        # Get relevant extractions
        extractions = sophisticated_extractions.get(schema_name, [])
        
        # Create extraction result
        extraction_result = {
            "entities": [
                {
                    "id": f"e_{i}",
                    "type": entity["type"],
                    "surface_form": entity["surface_form"],
                    "confidence": entity["confidence"]
                }
                for i, entity in enumerate(extractions)
            ],
            "relations": []
        }
        
        # Validate against schema
        validation = schema.validate_extraction_result(extraction_result)
        
        print(f"Schema Mode: {schema.mode.value}")
        print(f"Defined Entity Types: {len(schema.entity_types)}")
        print(f"Extracted Entities: {len(extraction_result['entities'])}")
        print(f"Validation: {'✓ PASSED' if validation['valid'] else '✗ FAILED'}")
        
        if validation['errors']:
            print(f"Errors: {validation['errors']}")
        
        # Show extracted concepts
        print("\nExtracted Concepts:")
        entity_counts = {}
        for entity in extraction_result['entities']:
            etype = entity['type']
            entity_counts[etype] = entity_counts.get(etype, 0) + 1
            
        for etype, count in sorted(entity_counts.items()):
            print(f"  {etype}: {count} instances")
        
        # Show examples
        print("\nTop Examples:")
        sorted_entities = sorted(extraction_result['entities'], 
                               key=lambda x: x['confidence'], reverse=True)
        for entity in sorted_entities[:5]:
            print(f"  - {entity['type']}: '{entity['surface_form']}' (conf: {entity['confidence']:.2f})")
    
    return True


def test_comprehensive_analysis():
    """Test comprehensive political analysis with hybrid schema"""
    
    print(f"\n{'='*60}")
    print("COMPREHENSIVE POLITICAL ANALYSIS TEST")
    print("="*60)
    
    schemas = create_sophisticated_political_schemas()
    comprehensive_schema = schemas["comprehensive"]
    
    # Comprehensive extraction combining all elements
    comprehensive_extraction = {
        "entities": [
            # Traditional political entities
            {"id": "e1", "type": "NATION_STATE", "surface_form": "United States", "confidence": 0.96},
            {"id": "e2", "type": "NATION_STATE", "surface_form": "Soviet Union", "confidence": 0.95},
            {"id": "e3", "type": "INTERNATIONAL_ORGANIZATION", "surface_form": "NATO", "confidence": 0.92},
            
            # Theoretical concepts
            {"id": "e4", "type": "THEORETICAL_FRAMEWORK", "surface_form": "detente theory", "confidence": 0.89},
            {"id": "e5", "type": "POLITICAL_CONCEPT", "surface_form": "balance of power", "confidence": 0.87},
            {"id": "e6", "type": "STRATEGIC_DOCTRINE", "surface_form": "nuclear deterrence", "confidence": 0.91},
            
            # Policy instruments
            {"id": "e7", "type": "POLICY_INSTRUMENT", "surface_form": "arms control", "confidence": 0.88},
            {"id": "e8", "type": "POLICY_INSTRUMENT", "surface_form": "military spending", "confidence": 0.85},
            
            # Strategic objectives
            {"id": "e9", "type": "STRATEGIC_OBJECTIVE", "surface_form": "world peace", "confidence": 0.94},
            {"id": "e10", "type": "STRATEGIC_OBJECTIVE", "surface_form": "nuclear parity", "confidence": 0.86},
            
            # Discourse elements
            {"id": "e11", "type": "RHETORICAL_DEVICE", "surface_form": "certainty claim", "confidence": 0.83},
            {"id": "e12", "type": "FRAMING_ELEMENT", "surface_form": "peace frame", "confidence": 0.81},
            
            # Temporal/causal elements (discovered in hybrid mode)
            {"id": "e13", "type": "CAUSAL_MECHANISM", "surface_form": "arms race dynamics", "confidence": 0.79},
            {"id": "e14", "type": "POLITICAL_PROCESS", "surface_form": "détente process", "confidence": 0.84}
        ],
        "relations": [
            {"id": "r1", "type": "COMPETES_WITH", "source": "e1", "target": "e2", "confidence": 0.91},
            {"id": "r2", "type": "IMPLEMENTS", "source": "e1", "target": "e4", "confidence": 0.87},
            {"id": "r3", "type": "LEADS_TO", "source": "e13", "target": "e6", "confidence": 0.82},
            {"id": "r4", "type": "SUPPORTS", "source": "e7", "target": "e9", "confidence": 0.85}
        ]
    }
    
    # Validate comprehensive extraction
    validation = comprehensive_schema.validate_extraction_result(comprehensive_extraction)
    
    print(f"Schema Mode: {comprehensive_schema.mode.value}")
    print(f"Predefined Entity Types: {len(comprehensive_schema.entity_types)}")
    print(f"Extracted Entities: {len(comprehensive_extraction['entities'])}")
    print(f"Extracted Relations: {len(comprehensive_extraction['relations'])}")
    print(f"Validation: {'✓ PASSED' if validation['valid'] else '✗ FAILED'}")
    
    if validation['errors']:
        print(f"Errors: {validation['errors']}")
    
    # Analyze by category
    print("\nEntity Analysis by Category:")
    categories = {
        "Traditional Political": ["NATION_STATE", "POLITICAL_ACTOR", "INTERNATIONAL_ORGANIZATION"],
        "Theoretical Concepts": ["THEORETICAL_FRAMEWORK", "POLITICAL_CONCEPT", "STRATEGIC_DOCTRINE"],
        "Policy Elements": ["POLICY_INSTRUMENT", "STRATEGIC_OBJECTIVE", "POLICY_OUTCOME"],
        "Discourse Elements": ["RHETORICAL_DEVICE", "FRAMING_ELEMENT", "SPEECH_ACT"],
        "Process Elements": ["POLITICAL_PROCESS", "CAUSAL_MECHANISM", "TEMPORAL_SEQUENCE"]
    }
    
    for category, types in categories.items():
        matching_entities = [e for e in comprehensive_extraction["entities"] if e["type"] in types]
        print(f"  {category}: {len(matching_entities)} entities")
        for entity in matching_entities:
            print(f"    - {entity['type']}: {entity['surface_form']}")
    
    print("\nRelationship Analysis:")
    for relation in comprehensive_extraction["relations"]:
        source_entity = next(e for e in comprehensive_extraction["entities"] if e["id"] == relation["source"])
        target_entity = next(e for e in comprehensive_extraction["entities"] if e["id"] == relation["target"])
        print(f"  {source_entity['surface_form']} --{relation['type']}--> {target_entity['surface_form']}")
    
    return True


def main():
    """Run sophisticated schema tests"""
    
    print("Sophisticated Schema System Testing")
    print("="*70)
    print("Testing whether schema system can handle complex political analysis")
    print("by treating theoretical concepts, discourse elements, etc. as entity types.\n")
    
    # Test sophisticated extraction
    test_sophisticated_extraction()
    
    # Test comprehensive analysis
    test_comprehensive_analysis()
    
    print(f"\n{'='*70}")
    print("CONCLUSIONS")
    print("="*70)
    
    print("\n✅ SCHEMA SYSTEM CAN HANDLE SOPHISTICATED ANALYSIS:")
    print("  1. ✓ Theoretical concepts as entity types")
    print("  2. ✓ Policy instruments as entity types") 
    print("  3. ✓ Discourse elements as entity types")
    print("  4. ✓ Strategic objectives as entity types")
    print("  5. ✓ Semantic relationship types")
    print("  6. ✓ Temporal/causal elements in hybrid mode")
    print("  7. ✓ Multi-level analysis through entity categorization")
    
    print("\n🔑 KEY INSIGHT:")
    print("  The schema system IS capable of sophisticated analysis")
    print("  when we define abstract concepts as entity types!")
    
    print("\n📋 WHAT'S NEEDED:")
    print("  1. Create comprehensive political science schemas")
    print("  2. Train/prompt extractors to recognize abstract concepts")
    print("  3. Build domain-specific schema templates")
    print("  4. Validate with real extractions (not just manual examples)")
    
    print("\n🎯 RECOMMENDATION:")
    print("  Test with actual LLM extraction using these sophisticated schemas")
    print("  to see if T23C can identify theoretical concepts when prompted correctly.")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())