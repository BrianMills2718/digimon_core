#!/usr/bin/env python3
"""
Test script for enhanced fact extraction patterns in Level 4
"""

import sys
import os

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, parent_dir)

# Import directly without relative imports
from level4_integration import Level4RuleSystem

def test_fact_extraction():
    """Test the enhanced fact extraction with various text inputs"""
    
    print("=" * 60)
    print("TESTING ENHANCED FACT EXTRACTION")
    print("=" * 60)
    
    # Initialize system
    system = Level4RuleSystem()
    
    # Test theory schema
    test_theory = {
        "theory_id": "social_identity_theory",
        "theoretical_structure": {
            "entities": [
                {"indigenous_name": "Person", "description": "Individual actor"},
                {"indigenous_name": "Group", "description": "Social group"},
                {"indigenous_name": "Leader", "description": "Group leader"}
            ],
            "relations": [
                {"indigenous_name": "belongsTo", "from_entity": "Person", "to_entity": "Group"},
                {"indigenous_name": "influences", "from_entity": "Person", "to_entity": "Person"},
                {"indigenous_name": "leadsGroup", "from_entity": "Leader", "to_entity": "Group"}
            ]
        }
    }
    
    # Test cases with various patterns
    test_cases = [
        # Basic membership patterns
        ("Alice belongs to TeamA. Bob is a member of TeamA.", 
         "Testing basic membership patterns"),
        
        # Various membership variations
        ("Charlie joined TeamB. David is in TeamB. Eve is part of TeamC.",
         "Testing membership pattern variations"),
        
        # Affiliation pattern
        ("Frank is affiliated with Research Group.",
         "Testing affiliation pattern"),
        
        # Influence patterns
        ("Alice influences Bob. Charlie affects David's decisions.",
         "Testing influence patterns"),
        
        # Impact pattern
        ("The new policy impacts all team members.",
         "Testing impact pattern"),
        
        # Class membership patterns
        ("John is a Leader. Mary, a Person in the organization.",
         "Testing class membership patterns"),
        
        # Complex text with multiple patterns
        ("Sarah belongs to TeamX and influences Tom. Tom is a member of TeamY. "
         "Sarah is a Leader who affects multiple teams. John joined TeamX recently.",
         "Testing complex text with multiple patterns"),
        
        # Edge cases
        ("", "Testing empty text"),
        ("No patterns here!", "Testing text with no patterns"),
        ("Alice123 belongs to Team_ABC.", "Testing alphanumeric names")
    ]
    
    for i, (text, description) in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {description}")
        print(f"Text: '{text}'")
        
        try:
            facts = system.extract_facts_from_text(text, test_theory)
            
            print(f"Extracted {len(facts)} facts:")
            
            # Group facts by type
            individuals = [f for f in facts if f['type'] == 'individual']
            properties = [f for f in facts if f['type'] == 'property']
            
            if individuals:
                print("\n  Individuals:")
                for fact in individuals:
                    print(f"    - {fact['name']} is a {fact['class']}")
            
            if properties:
                print("\n  Properties:")
                for fact in properties:
                    print(f"    - {fact['subject']} {fact['property']} {fact['object']}")
            
            if not facts:
                print("  (No facts extracted)")
                
        except Exception as e:
            print(f"  ERROR: {e}")
    
    # Test pattern statistics
    print("\n" + "=" * 60)
    print("PATTERN EXTRACTION STATISTICS")
    print("=" * 60)
    
    # Comprehensive test text
    comprehensive_text = """
    Alice belongs to TeamA. Bob is a member of TeamA. Charlie joined TeamB.
    David is in TeamC. Eve is part of TeamD. Frank is affiliated with TeamE.
    
    Alice influences Bob and Charlie. David affects Eve's work.
    Frank impacts the entire organization.
    
    Alice is a Leader. Bob is a Person. Charlie, a Leader in TeamB.
    """
    
    facts = system.extract_facts_from_text(comprehensive_text, test_theory)
    
    # Count fact types
    fact_types = {}
    relation_types = {}
    class_types = {}
    
    for fact in facts:
        if fact['type'] == 'individual':
            class_name = fact['class']
            class_types[class_name] = class_types.get(class_name, 0) + 1
        elif fact['type'] == 'property':
            prop_name = fact['property']
            relation_types[prop_name] = relation_types.get(prop_name, 0) + 1
    
    print("\nClass Distribution:")
    for class_name, count in sorted(class_types.items()):
        print(f"  {class_name}: {count}")
    
    print("\nRelation Distribution:")
    for rel_name, count in sorted(relation_types.items()):
        print(f"  {rel_name}: {count}")
    
    print(f"\nTotal Facts Extracted: {len(facts)}")
    print(f"  Individuals: {sum(1 for f in facts if f['type'] == 'individual')}")
    print(f"  Properties: {sum(1 for f in facts if f['type'] == 'property')}")
    
    # Test duplicate handling
    print("\n" + "=" * 60)
    print("DUPLICATE HANDLING TEST")
    print("=" * 60)
    
    duplicate_text = "Alice belongs to TeamA. Alice belongs to TeamA. Alice belongs to TeamA."
    facts = system.extract_facts_from_text(duplicate_text, test_theory)
    
    print(f"Text: '{duplicate_text}'")
    print(f"Facts extracted: {len(facts)}")
    
    # Should create Alice and TeamA only once
    alice_count = sum(1 for f in facts if f.get('name') == 'alice' and f['type'] == 'individual')
    teama_count = sum(1 for f in facts if f.get('name') == 'teama' and f['type'] == 'individual')
    belongs_count = sum(1 for f in facts if f.get('property') == 'belongsTo')
    
    print(f"  Alice individuals: {alice_count} (should be 1)")
    print(f"  TeamA individuals: {teama_count} (should be 1)")
    print(f"  belongsTo relations: {belongs_count} (should be 1)")
    
    print("\n" + "=" * 60)
    print("FACT EXTRACTION TESTING COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    test_fact_extraction()