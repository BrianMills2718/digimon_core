#!/usr/bin/env python
"""Debug why relationship patterns aren't matching."""

import re

# Test texts from adversarial test
test_texts = [
    "Elon Musk founded Tesla in 2003. Tesla is headquartered in Austin, Texas.",
    "Musk also founded SpaceX. He sold PayPal to eBay. Peter Thiel was Musk's partner at PayPal.",
    "Tesla acquired SolarCity in 2016. SolarCity was founded by Musk's cousins. This was controversial.",
    "Before Tesla, Musk founded X.com in 1999. X.com merged with Confinity to become PayPal.",
    "Tesla competes with Ford and GM. Ford was founded by Henry Ford in 1903, the same year as Tesla's founding."
]

# Patterns from T24
patterns = {
    "FOUNDED": r"([\w\s]+?)\s+founded\s+([\w\s]+?)(?:\s+in|\s*$|\.|,)",
    "LOCATED_IN": r"([\w\s]+?)\s+(?:is\s+)?(?:located|based|headquartered)\s+in\s+([\w\s]+?)(?:\s*$|\.|,)",
    "ACQUIRED": r"([\w\s]+?)\s+acquired\s+([\w\s]+?)(?:\s+in|\s+for|\s*$|\.|,)",
}

print("Testing pattern matching...\n")

for i, text in enumerate(test_texts):
    print(f"Text {i+1}: '{text}'")
    
    for rel_type, pattern in patterns.items():
        matches = list(re.finditer(pattern, text, re.IGNORECASE))
        if matches:
            print(f"  {rel_type}:")
            for m in matches:
                print(f"    - Full match: '{m.group(0)}'")
                print(f"      Source: '{m.group(1).strip()}'")
                print(f"      Target: '{m.group(2).strip()}'")
    print()

# Test specific cases
print("\nSpecific test cases:")

# Test 1: "Elon Musk founded Tesla"
text1 = "Elon Musk founded Tesla in 2003."
pattern1 = r"([\w\s]+?)\s+founded\s+([\w\s]+?)(?:\s+in|\s*$|\.|,)"
match1 = re.search(pattern1, text1, re.IGNORECASE)
if match1:
    print(f"✓ 'Elon Musk founded Tesla' matches!")
    print(f"  Groups: '{match1.group(1)}' -> '{match1.group(2)}'")
else:
    print("✗ 'Elon Musk founded Tesla' DOES NOT match")

# Test entities that might be extracted
entities = ["Elon Musk", "Tesla", "Austin", "Texas", "SpaceX", "SolarCity", "X.com"]
print(f"\nChecking if extracted entities would match...")
for entity in entities:
    # Check if entity would match in patterns
    if "Elon Musk" in match1.group(1) if match1 else "":
        print(f"  ✓ '{entity}' would match as source")
    elif "Tesla" in match1.group(2) if match1 else "":
        print(f"  ✓ '{entity}' would match as target")