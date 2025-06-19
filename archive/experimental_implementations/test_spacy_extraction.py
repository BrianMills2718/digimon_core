#!/usr/bin/env python
"""Test what SpaCy is extracting."""

import spacy

nlp = spacy.load("en_core_web_sm")

test_texts = [
    "Musk also founded SpaceX.",
    "Tesla acquired SolarCity in 2016.",
    "Before Tesla, Musk founded X.com in 1999.",
    "Elon Musk founded Tesla in 2003."
]

for text in test_texts:
    print(f"\nText: '{text}'")
    doc = nlp(text)
    
    print("Entities:")
    for ent in doc.ents:
        print(f"  - '{ent.text}' ({ent.label_})")
    
    print("Tokens:")
    for token in doc:
        if token.pos_ in ["PROPN", "NOUN"] and not token.is_stop:
            print(f"  - '{token.text}' ({token.pos_}, {token.dep_})")