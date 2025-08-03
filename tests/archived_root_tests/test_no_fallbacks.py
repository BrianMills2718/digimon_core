#!/usr/bin/env python3
"""
Test the no-fallbacks personality system to see where exactly it fails
"""

import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent / "uncertainty_stress_test" / "personality-prediction"))

from quick_test_personality_system import QuickPersonalitySystem

def test_single_user():
    """Test on a single user to see exact failure point"""
    
    print("=== TESTING NO-FALLBACKS SYSTEM ===")
    
    # Load real data
    dataset_path = Path(__file__).parent / "uncertainty_stress_test" / "100_users_500tweets_dataset.json"
    
    with open(dataset_path, 'r') as f:
        data = json.load(f)
    
    test_user = data[0]
    tweets = [t['text'] for t in test_user['tweets'] if t.get('text', '').strip()][:5]  # Just 5 tweets
    
    print(f"Testing user: {test_user['user_info']['twitter_id']}")
    print(f"Political ground truth: {test_user['user_info']['political']}")
    print(f"Using {len(tweets)} tweets")
    
    # Initialize system  
    system = QuickPersonalitySystem()
    
    # Test prediction
    try:
        print("\nMaking prediction...")
        result = system.predict_user_personality(tweets)
        
        print(f"SUCCESS! Result keys: {list(result.keys())}")
        print(f"Full result structure: {json.dumps(result, indent=2, default=str)}")
        
        # Check trait_predictions structure
        if 'trait_predictions' in result:
            trait_predictions = result['trait_predictions']
            print(f"Trait predictions keys: {list(trait_predictions.keys())}")
            
            if 'political' in trait_predictions:
                political_result = trait_predictions['political']
                print(f"Political result: {political_result}")
            else:
                print("Missing political in trait_predictions!")
        else:
            print("Missing trait_predictions!")
            
    except Exception as e:
        print(f"FAILURE: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_single_user()