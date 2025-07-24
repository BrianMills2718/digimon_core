#!/usr/bin/env python3
"""
Download and explore SocialMaze dataset for Bayesian uncertainty testing
"""

import os
import json
from datasets import load_dataset
import pandas as pd
from typing import Dict, List, Any

def download_socialmaze():
    """Download SocialMaze dataset from Hugging Face"""
    print("🔄 Downloading SocialMaze dataset...")
    
    try:
        # Load the dataset
        dataset = load_dataset("MBZUAI/SocialMaze")
        
        print(f"✅ Dataset downloaded successfully!")
        print(f"📊 Dataset structure: {dataset}")
        
        # Create data directory
        data_dir = "data/socialmaze"
        os.makedirs(data_dir, exist_ok=True)
        
        # Save dataset splits
        for split_name, split_data in dataset.items():
            print(f"\n📁 Processing {split_name} split:")
            print(f"   Size: {len(split_data)} examples")
            
            # Convert to pandas and save
            df = split_data.to_pandas()
            output_file = f"{data_dir}/{split_name}.json"
            df.to_json(output_file, orient='records', indent=2)
            print(f"   Saved to: {output_file}")
            
            # Show sample
            print(f"   Sample columns: {list(df.columns)}")
            if len(df) > 0:
                print(f"   First example keys: {list(df.iloc[0].keys()) if isinstance(df.iloc[0], dict) else 'Simple structure'}")
        
        return dataset
        
    except Exception as e:
        print(f"❌ Error downloading dataset: {e}")
        return None

def explore_dataset_structure(dataset):
    """Explore the structure and identify Bayesian uncertainty tasks"""
    print("\n🔍 Exploring dataset structure for Bayesian uncertainty tasks...")
    
    for split_name, split_data in dataset.items():
        print(f"\n📋 {split_name.upper()} SPLIT ANALYSIS:")
        
        # Get first few examples
        examples = split_data[:5]
        
        for i, example in enumerate(examples):
            print(f"\n   Example {i+1}:")
            for key, value in example.items():
                if isinstance(value, str) and len(value) > 100:
                    print(f"     {key}: {value[:100]}...")
                elif isinstance(value, list) and len(value) > 3:
                    print(f"     {key}: [{value[0]}, {value[1]}, ...] (length: {len(value)})")
                else:
                    print(f"     {key}: {value}")
            
            if i >= 2:  # Just show first 3 examples
                break

def identify_bayesian_tasks(dataset):
    """Identify specific tasks suitable for Bayesian uncertainty analysis"""
    print("\n🎯 Identifying Bayesian uncertainty analysis opportunities...")
    
    bayesian_opportunities = []
    
    for split_name, split_data in dataset.items():
        example = split_data[0]
        
        # Look for probabilistic elements
        for key, value in example.items():
            if any(term in key.lower() for term in ['prob', 'confidence', 'uncertainty', 'belief', 'likelihood']):
                bayesian_opportunities.append({
                    'split': split_name,
                    'field': key,
                    'type': 'explicit_probability',
                    'sample_value': value
                })
            
            elif any(term in key.lower() for term in ['intent', 'mental', 'theory', 'mind', 'predict']):
                bayesian_opportunities.append({
                    'split': split_name,
                    'field': key,
                    'type': 'theory_of_mind',
                    'sample_value': value
                })
            
            elif any(term in key.lower() for term in ['choice', 'action', 'decision', 'option']):
                bayesian_opportunities.append({
                    'split': split_name,
                    'field': key,
                    'type': 'decision_prediction',
                    'sample_value': value
                })
    
    print(f"🔍 Found {len(bayesian_opportunities)} Bayesian analysis opportunities:")
    for opp in bayesian_opportunities:
        print(f"   - {opp['type']}: {opp['split']}.{opp['field']}")
    
    return bayesian_opportunities

def create_uncertainty_test_plan(dataset, opportunities):
    """Create a test plan for applying uncertainty framework to SocialMaze"""
    print("\n📋 Creating uncertainty analysis test plan...")
    
    test_plan = {
        'dataset_info': {
            'name': 'SocialMaze',
            'splits': list(dataset.keys()),
            'total_examples': sum(len(split) for split in dataset.values()),
            'bayesian_opportunities': len(opportunities)
        },
        'uncertainty_tests': [
            {
                'name': 'Social Intent Inference',
                'description': 'Use Bayesian inference to predict social intentions with uncertainty quantification',
                'method': 'bayesian_aggregation',
                'target_fields': [opp['field'] for opp in opportunities if opp['type'] == 'theory_of_mind'],
                'metrics': ['brier_score', 'calibration_error', 'log_likelihood']
            },
            {
                'name': 'Decision Prediction Calibration', 
                'description': 'Evaluate confidence calibration for predicting social decisions',
                'method': 'calibration_analysis',
                'target_fields': [opp['field'] for opp in opportunities if opp['type'] == 'decision_prediction'],
                'metrics': ['reliability_diagram', 'expected_calibration_error', 'sharpness']
            },
            {
                'name': 'Cognitive Bias Detection',
                'description': 'Apply mental model auditing to detect biases in social reasoning',
                'method': 'bias_analysis',
                'target_fields': ['all_reasoning_fields'],
                'metrics': ['bias_severity', 'debiasing_effectiveness', 'metacognitive_accuracy']
            }
        ],
        'integration_points': [
            'uncertainty_engine.assess_initial_confidence()',
            'bayesian_aggregation_service.update_belief()',
            'mental_model_auditing.detect_social_biases()',
            'calibration_system.evaluate_social_predictions()'
        ]
    }
    
    # Save test plan
    with open('data/socialmaze/uncertainty_test_plan.json', 'w') as f:
        json.dump(test_plan, f, indent=2)
    
    print("✅ Test plan created and saved to data/socialmaze/uncertainty_test_plan.json")
    
    return test_plan

if __name__ == "__main__":
    print("🚀 SocialMaze Dataset Analysis for Bayesian Uncertainty Testing")
    print("=" * 60)
    
    # Download dataset
    dataset = download_socialmaze()
    
    if dataset:
        # Explore structure
        explore_dataset_structure(dataset)
        
        # Identify Bayesian opportunities
        opportunities = identify_bayesian_tasks(dataset)
        
        # Create test plan
        test_plan = create_uncertainty_test_plan(dataset, opportunities)
        
        print("\n🎉 SocialMaze dataset ready for uncertainty analysis!")
        print(f"📁 Data saved in: data/socialmaze/")
        print(f"📋 Test plan: {len(test_plan['uncertainty_tests'])} uncertainty tests planned")
        print("\nNext steps:")
        print("1. Run: python test_socialmaze_uncertainty.py")
        print("2. Analyze results in validation/socialmaze_results/")
    
    else:
        print("❌ Failed to download dataset. Please check your internet connection.")