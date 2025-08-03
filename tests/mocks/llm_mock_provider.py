#!/usr/bin/env python3
"""
Mock LLM API Provider - TEST ONLY

Provides mock LLM responses for testing. This file should NEVER be imported 
by production code - it is for testing purposes only.
"""

from typing import Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class MockAPIProvider:
    """Provides mock LLM responses for testing."""
    
    def __init__(self):
        self.call_count = 0
        
    def mock_extract(self, text: str, ontology: 'DomainOntology') -> Dict[str, Any]:
        """Generate mock extraction results."""
        self.call_count += 1
        
        # Generate mock entities based on ontology types
        mock_entities = []
        mock_relationships = []
        
        # Simple text analysis for mock data
        words = text.lower().split()
        
        # Mock entity generation
        for i, entity_type in enumerate(ontology.entity_types[:3]):  # Limit to 3 types
            if i < len(entity_type.examples):
                mock_entities.append({
                    'text': entity_type.examples[i],
                    'type': entity_type.name,
                    'confidence': 0.8 + (i * 0.05),
                    'context': f"Mock context for {entity_type.examples[i]}"
                })
        
        # Mock relationship generation
        if len(mock_entities) >= 2 and ontology.relationship_types:
            rel_type = ontology.relationship_types[0]
            mock_relationships.append({
                'source': mock_entities[0]['text'],
                'target': mock_entities[1]['text'],
                'relation': rel_type.name,
                'confidence': 0.75,
                'context': f"Mock relationship between entities"
            })
        
        logger.info(f"Mock extraction #{self.call_count}: {len(mock_entities)} entities, {len(mock_relationships)} relationships")
        
        return {
            'entities': mock_entities,
            'relationships': mock_relationships,
            'metadata': {
                'extraction_method': 'mock',
                'call_count': self.call_count,
                'timestamp': datetime.now().isoformat()
            }
        }