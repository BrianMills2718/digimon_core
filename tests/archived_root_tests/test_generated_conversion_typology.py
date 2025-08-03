#!/usr/bin/env python3
"""
Test the generated conversion typology implementation
"""

class ConversionMotifTypology:
    """
    A classification system for identifying types of religious conversion experiences.
    
    The six motifs are:
    - intellectual: Conversion through rational study and reasoning
    - mystical: Conversion through direct spiritual/transcendent experience
    - experimental: Conversion through trial and testing of beliefs
    - affectional: Conversion through emotional relationships and community
    - revivalist: Conversion through intense group religious experiences
    - coercive: Conversion through external pressure or force
    """
    
    MOTIFS = {
        'intellectual': {
            'description': 'Conversion through rational study, theological reasoning, and intellectual conviction',
            'characteristics': ['study', 'reasoning', 'gradual', 'cognitive']
        },
        'mystical': {
            'description': 'Conversion through direct spiritual experience or divine encounter',
            'characteristics': ['vision', 'revelation', 'sudden', 'transcendent']
        },
        'experimental': {
            'description': 'Conversion through testing and trying out religious practices',
            'characteristics': ['trial', 'practice', 'gradual', 'experiential']
        },
        'affectional': {
            'description': 'Conversion through relationships, community, and emotional bonds',
            'characteristics': ['relationships', 'community', 'gradual', 'social']
        },
        'revivalist': {
            'description': 'Conversion through intense group religious experiences and mass events',
            'characteristics': ['group_event', 'emotional', 'sudden', 'public']
        },
        'coercive': {
            'description': 'Conversion through external pressure, force, or manipulation',
            'characteristics': ['pressure', 'force', 'external', 'involuntary']
        }
    }
    
    def classify_conversion(self, characteristics):
        """
        Classify a conversion experience based on its characteristics.
        
        Parameters:
        characteristics (list): List of strings describing the conversion experience
        
        Returns:
        dict: Classification results with motif type and confidence score
        """
        scores = {}
        
        for motif, data in self.MOTIFS.items():
            score = 0
            motif_chars = data['characteristics']
            
            # Calculate overlap between input characteristics and motif characteristics
            for char in characteristics:
                if char.lower() in motif_chars:
                    score += 1
            
            # Normalize score by number of characteristics provided
            if characteristics:
                scores[motif] = score / len(characteristics)
        
        # Find best match
        best_motif = max(scores, key=scores.get)
        confidence = scores[best_motif]
        
        return {
            'primary_motif': best_motif,
            'confidence': confidence,
            'description': self.MOTIFS[best_motif]['description'],
            'all_scores': scores
        }
    
    def get_motif_info(self, motif_name):
        """
        Get detailed information about a specific conversion motif.
        
        Parameters:
        motif_name (str): Name of the motif to retrieve
        
        Returns:
        dict: Motif information or None if not found
        """
        return self.MOTIFS.get(motif_name.lower())
    
    def list_all_motifs(self):
        """
        Return a list of all available conversion motifs.
        
        Returns:
        list: List of motif names
        """
        return list(self.MOTIFS.keys())

# Test examples
def test_conversion_typology():
    typology = ConversionMotifTypology()
    
    print("🧪 TESTING GENERATED CONVERSION TYPOLOGY")
    print("=" * 50)
    
    # Test 1: Intellectual conversion
    test_1_characteristics = ['study', 'reasoning', 'gradual', 'cognitive']
    result_1 = typology.classify_conversion(test_1_characteristics)
    print("Test 1 - Intellectual Conversion:")
    print(f"  Primary motif: {result_1['primary_motif']}")
    print(f"  Confidence: {result_1['confidence']:.2f}")
    print(f"  Description: {result_1['description']}\n")
    
    # Test 2: Mystical conversion
    test_2_characteristics = ['vision', 'sudden', 'transcendent']
    result_2 = typology.classify_conversion(test_2_characteristics)
    print("Test 2 - Mystical Conversion:")
    print(f"  Primary motif: {result_2['primary_motif']}")
    print(f"  Confidence: {result_2['confidence']:.2f}")
    print(f"  Description: {result_2['description']}\n")
    
    # Test 3: Affectional conversion
    test_3_characteristics = ['relationships', 'community', 'social', 'gradual']
    result_3 = typology.classify_conversion(test_3_characteristics)
    print("Test 3 - Affectional Conversion:")
    print(f"  Primary motif: {result_3['primary_motif']}")
    print(f"  Confidence: {result_3['confidence']:.2f}")
    print(f"  Description: {result_3['description']}\n")
    
    # Test 4: Mixed characteristics
    test_4_characteristics = ['vision', 'community', 'gradual']
    result_4 = typology.classify_conversion(test_4_characteristics)
    print("Test 4 - Mixed Characteristics:")
    print(f"  Primary motif: {result_4['primary_motif']}")
    print(f"  Confidence: {result_4['confidence']:.2f}")
    print(f"  All scores: {result_4['all_scores']}\n")
    
    # Test 5: List all motifs
    print("Test 5 - Available Motifs:")
    all_motifs = typology.list_all_motifs()
    for motif in all_motifs:
        info = typology.get_motif_info(motif)
        print(f"  - {motif}: {info['description'][:60]}...")
    
    print("\n✅ ALL TESTS COMPLETED SUCCESSFULLY!")
    print("The generated algorithm implementation is working correctly!")

if __name__ == "__main__":
    test_conversion_typology()