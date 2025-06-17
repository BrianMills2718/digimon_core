#!/usr/bin/env python
"""Debug why patterns aren't matching."""

import re
from src.tools.phase2.t24_relationship_extractor import RelationshipExtractor

# Test text that should have many relationships
test_text = "Microsoft invested $10 billion in OpenAI. Microsoft partners with OpenAI to integrate GPT into Bing."

# Get patterns
patterns = RelationshipExtractor.RELATIONSHIP_PATTERNS

print(f"Testing text: '{test_text}'\n")

# Test each pattern
for rel_type, pattern_list in patterns.items():
    print(f"\n{rel_type}:")
    for pattern in pattern_list:
        matches = list(re.finditer(pattern, test_text, re.IGNORECASE))
        if matches:
            for match in matches:
                print(f"  Pattern: {pattern}")
                print(f"  Match: '{match.group(0)}'")
                print(f"  Groups: {match.groups()}")

# Specific test for INVESTED_IN
print("\n\nDetailed INVESTED_IN test:")
invested_pattern = r"([\w\s]+?)\s+invested\s+(?:\$[\d\.]+[MBK]?\s+)?in\s+([\w\s]+?)(?:\s*$|\.|,)"
text = "Microsoft invested $10 billion in OpenAI."
match = re.search(invested_pattern, text, re.IGNORECASE)
if match:
    print(f"✓ Match found: '{match.group(0)}'")
    print(f"  Source: '{match.group(1)}'")
    print(f"  Target: '{match.group(2)}'")
else:
    print("✗ No match found")

# Test PARTNERS_WITH
print("\n\nDetailed PARTNERS_WITH test:")
partners_pattern = r"([\w\s]+?)\s+partners?\s+with\s+([\w\s]+?)(?:\s*$|\.|,)"
text2 = "Microsoft partners with OpenAI to integrate GPT into Bing."
match2 = re.search(partners_pattern, text2, re.IGNORECASE)
if match2:
    print(f"✓ Match found: '{match2.group(0)}'")
    print(f"  Source: '{match2.group(1)}'")
    print(f"  Target: '{match2.group(2)}'")
else:
    print("✗ No match found")