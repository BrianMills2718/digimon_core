#!/usr/bin/env python3
"""
Simple test for fact extraction patterns without full Level 4 system
"""

import re

def test_fact_extraction_patterns():
    """Test the enhanced fact extraction patterns directly"""
    
    print("=" * 60)
    print("TESTING FACT EXTRACTION PATTERNS")
    print("=" * 60)
    
    # Define patterns like in level4_integration.py
    membership_patterns = [
        (r"(\w+)\s+belongs?\s+to\s+(\w+)", "belongsTo"),
        (r"(\w+)\s+is\s+a?\s*members?\s+of\s+(\w+)", "belongsTo"),
        (r"(\w+)\s+joined\s+(\w+)", "belongsTo"),
        (r"(\w+)\s+is\s+in\s+(\w+)", "belongsTo"),
        (r"(\w+)\s+is\s+part\s+of\s+(\w+)", "belongsTo"),
        (r"(\w+)\s+is\s+affiliated\s+with\s+(\w+)", "belongsTo"),
    ]
    
    influence_patterns = [
        (r"(\w+)\s+influences?\s+(\w+)", "influences"),
        (r"(\w+)\s+affects?\s+(\w+)", "affects"),
        (r"(\w+)\s+impacts?\s+(\w+)", "impacts"),
    ]
    
    class_patterns = [
        (r"(\w+)\s+is\s+a?\s*(\w+)", "class"),
        (r"(\w+),?\s+a\s+(\w+)", "class"),
    ]
    
    # Test cases
    test_texts = [
        "Alice belongs to TeamA",
        "Bob is a member of TeamB",
        "Charlie joined TeamC",
        "David is in TeamD",
        "Eve is part of TeamE",
        "Frank is affiliated with Research Group",
        "Alice influences Bob",
        "Charlie affects David",
        "Eve impacts the team",
        "John is a Leader",
        "Mary, a Person",
    ]
    
    for text in test_texts:
        print(f"\nText: '{text}'")
        
        # Test membership patterns
        for pattern, relation in membership_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                for match in matches:
                    print(f"  Membership: {match[0]} {relation} {match[1]}")
        
        # Test influence patterns
        for pattern, relation in influence_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                for match in matches:
                    print(f"  Influence: {match[0]} {relation} {match[1]}")
        
        # Test class patterns
        for pattern, _ in class_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                for match in matches:
                    # Filter out false positives
                    if match[1].lower() not in ['a', 'the', 'in', 'to', 'of', 'part', 'member', 'affiliated']:
                        print(f"  Class: {match[0]} is a {match[1]}")
    
    # Test complex text
    print("\n" + "=" * 60)
    print("COMPLEX TEXT TEST")
    print("=" * 60)
    
    complex_text = """
    Alice belongs to TeamX and influences Bob. Bob is a member of TeamY.
    Charlie joined TeamZ recently. David is in multiple teams.
    Eve is part of the leadership. Frank is affiliated with Research.
    
    Alice affects team dynamics. Charlie impacts productivity.
    
    John is a Leader. Mary, a skilled Person in the organization.
    """
    
    print(f"Text: {complex_text.strip()}")
    print("\nExtracted facts:")
    
    all_facts = []
    
    # Extract all facts
    for pattern, relation in membership_patterns:
        matches = re.findall(pattern, complex_text, re.IGNORECASE)
        for match in matches:
            fact = f"{match[0]} {relation} {match[1]}"
            if fact not in all_facts:
                all_facts.append(fact)
                print(f"  - {fact}")
    
    for pattern, relation in influence_patterns:
        matches = re.findall(pattern, complex_text, re.IGNORECASE)
        for match in matches:
            fact = f"{match[0]} {relation} {match[1]}"
            if fact not in all_facts:
                all_facts.append(fact)
                print(f"  - {fact}")
    
    for pattern, _ in class_patterns:
        matches = re.findall(pattern, complex_text, re.IGNORECASE)
        for match in matches:
            if match[1].lower() not in ['a', 'the', 'in', 'to', 'of', 'part', 'member', 'affiliated', 'skilled']:
                fact = f"{match[0]} is a {match[1]}"
                if fact not in all_facts:
                    all_facts.append(fact)
                    print(f"  - {fact}")
    
    print(f"\nTotal facts extracted: {len(all_facts)}")


if __name__ == "__main__":
    test_fact_extraction_patterns()