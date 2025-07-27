#!/usr/bin/env python3
"""
Complete KGAS Demo - Full Pipeline with All Data Outputs
Shows Neo4j, SQL, Vector, and Final Results
"""

import sys
import os
import time
import json
from pathlib import Path

# Add KGAS to path
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent))

from one_click_kgas_setup import ui_setup_kgas, ui_get_status
from kunst_memory_safe_validator import KunstMemorySafeValidator

def setup_complete_kgas_demo():
    """Set up complete KGAS demo with all components"""
    print("🚀 Complete KGAS Demo - Full Pipeline")
    print("=" * 60)
    
    # Step 1: Auto-setup Neo4j
    print("📋 Step 1: Setting up Neo4j automatically...")
    success, info, error = ui_setup_kgas()
    
    if success:
        print(f"✅ Neo4j ready: {info['http_url']}")
        neo4j_available = True
    else:
        print(f"⚠️  Neo4j setup failed: {error}")
        print("   Demo will continue without graph database")
        neo4j_available = False
    
    # Step 2: Create enhanced psychological profiles for better NER
    print("\n📋 Step 2: Creating rich psychological profiles...")
    
    enhanced_profiles = [
        {
            'user_id': 'demo_001',
            'political_score': -1.2,
            'narcissism_score': 0.8,
            'denialism_score': 1.5,
            'conspiracy_score': 0.9,
            'enhanced_text': """
            John Smith from New York works at Microsoft Corporation and strongly supports 
            the Democratic Party. He frequently posts about climate change denial on Twitter 
            and believes in QAnon conspiracy theories. Smith attended Harvard University 
            and currently lives in San Francisco, California. He has written articles 
            for Breitbart News and frequently mentions Donald Trump in his social media posts.
            Smith's psychological profile shows high narcissistic traits and strong 
            conspiracy mentality scores.
            """
        },
        {
            'user_id': 'demo_002', 
            'political_score': 1.1,
            'narcissism_score': -0.3,
            'denialism_score': -0.8,
            'conspiracy_score': -1.2,
            'enhanced_text': """
            Dr. Sarah Johnson is a professor at Stanford University who works for 
            the World Health Organization. She supports the Republican Party and 
            has published research in Nature magazine about vaccine effectiveness.
            Johnson lives in Washington D.C. and frequently collaborates with 
            the Centers for Disease Control. She has low narcissism scores and 
            shows strong evidence-based thinking patterns. Johnson works with 
            Google Research on AI safety projects.
            """
        }
    ]
    
    # Step 3: Run complete KGAS pipeline
    print("\n📋 Step 3: Running complete KGAS pipeline...")
    
    results = []
    for profile in enhanced_profiles:
        print(f"\n🔄 Processing user: {profile['user_id']}")
        
        # Run through KGAS validator with enhanced profile
        result = run_enhanced_kgas_pipeline(profile)
        results.append(result)
    
    # Step 4: Show all data outputs
    print("\n📋 Step 4: Displaying all data outputs...")
    show_all_outputs(results, neo4j_available)
    
    return results

def run_enhanced_kgas_pipeline(profile):
    """Run enhanced KGAS pipeline on single profile"""
    
    # Create validator
    validator = KunstMemorySafeValidator(chunk_size=1)
    
    # Run real KGAS analysis with enhanced text
    result = validator.real_kgas_analysis(profile)
    
    return {
        'user_profile': profile,
        'kgas_result': result
    }

def show_all_outputs(results, neo4j_available):
    """Display all KGAS outputs comprehensively"""
    
    print("\n" + "="*60)
    print("📊 COMPLETE KGAS PIPELINE OUTPUTS")
    print("="*60)
    
    # 1. Raw Processing Results
    print("\n1️⃣  RAW PROCESSING RESULTS")
    print("-" * 40)
    
    for i, result in enumerate(results, 1):
        user_id = result['user_profile']['user_id']
        kgas_result = result['kgas_result']
        
        print(f"\n👤 User {i}: {user_id}")
        print(f"   Processing time: {kgas_result.get('processing_time', 0):.3f}s")
        print(f"   Entities extracted: {kgas_result.get('entities_extracted', 0)}")
        print(f"   Relationships found: {kgas_result.get('relationships_extracted', 0)}")
        print(f"   Entities built: {kgas_result.get('entities_built', 0)}")
        print(f"   Evidence pieces: {kgas_result.get('evidence_pieces', 0)}")
        print(f"   Bayesian confidence: {kgas_result.get('bayesian_confidence', 0):.3f}")
        print(f"   Quality score: {kgas_result.get('quality_score', 0):.3f}")
        print(f"   Pipeline complete: {kgas_result.get('kgas_pipeline_complete', False)}")
        
        if 'error' in kgas_result:
            print(f"   ⚠️  Error: {kgas_result['error']}")
    
    # 2. Neo4j Graph Data
    print(f"\n2️⃣  NEO4J GRAPH DATABASE")
    print("-" * 40)
    
    if neo4j_available:
        show_neo4j_data()
    else:
        print("❌ Neo4j not available - no graph data stored")
        print("   Run: python one_click_kgas_setup.py setup")
    
    # 3. Vector Data (if any)
    print(f"\n3️⃣  VECTOR EMBEDDINGS")
    print("-" * 40)
    print("⚠️  Vector storage not implemented in current pipeline")
    print("   This would contain text embeddings from processed documents")
    
    # 4. SQL/Structured Data
    print(f"\n4️⃣  STRUCTURED DATA (SQL-equivalent)")
    print("-" * 40)
    
    # Create structured output
    structured_data = []
    for result in results:
        profile = result['user_profile']
        kgas_result = result['kgas_result']
        
        structured_data.append({
            'user_id': profile['user_id'],
            'political_orientation': profile['political_score'],
            'narcissism_level': profile['narcissism_score'], 
            'denialism_tendency': profile['denialism_score'],
            'conspiracy_mentality': profile['conspiracy_score'],
            'entities_found': kgas_result.get('entities_extracted', 0),
            'relationships_found': kgas_result.get('relationships_extracted', 0),
            'processing_time_seconds': kgas_result.get('processing_time', 0),
            'bayesian_confidence': kgas_result.get('bayesian_confidence', 0),
            'quality_assessment': kgas_result.get('quality_score', 0),
            'pipeline_success': kgas_result.get('kgas_pipeline_complete', False)
        })
    
    # Display as table
    print("📋 Structured Results Table:")
    print("-" * 100)
    headers = ['User ID', 'Political', 'Narcissism', 'Entities', 'Relations', 'Confidence', 'Success']
    print(f"{'User ID':<12} {'Political':<10} {'Narcissism':<11} {'Entities':<9} {'Relations':<10} {'Confidence':<11} {'Success':<8}")
    print("-" * 100)
    
    for data in structured_data:
        print(f"{data['user_id']:<12} {data['political_orientation']:<10.2f} {data['narcissism_level']:<11.2f} "
              f"{data['entities_found']:<9} {data['relationships_found']:<10} {data['bayesian_confidence']:<11.3f} "
              f"{'✓' if data['pipeline_success'] else '✗':<8}")
    
    # 5. Final Analysis Output
    print(f"\n5️⃣  FINAL ANALYSIS SUMMARY")
    print("-" * 40)
    
    total_users = len(results)
    successful_pipelines = sum(1 for r in results if r['kgas_result'].get('kgas_pipeline_complete', False))
    avg_processing_time = sum(r['kgas_result'].get('processing_time', 0) for r in results) / total_users
    total_entities = sum(r['kgas_result'].get('entities_extracted', 0) for r in results)
    total_relationships = sum(r['kgas_result'].get('relationships_extracted', 0) for r in results)
    
    print(f"📊 Pipeline Statistics:")
    print(f"   Users processed: {total_users}")
    print(f"   Successful pipelines: {successful_pipelines}/{total_users}")
    print(f"   Average processing time: {avg_processing_time:.3f}s")
    print(f"   Total entities extracted: {total_entities}")
    print(f"   Total relationships found: {total_relationships}")
    print(f"   Neo4j integration: {'✓' if neo4j_available else '✗'}")
    
    # 6. Save outputs to files
    print(f"\n6️⃣  SAVED OUTPUT FILES")
    print("-" * 40)
    
    # Save JSON results
    output_file = f"kgas_demo_results_{int(time.time())}.json"
    with open(output_file, 'w') as f:
        json.dump({
            'timestamp': time.time(),
            'neo4j_available': neo4j_available,
            'results': results,
            'structured_data': structured_data,
            'summary': {
                'total_users': total_users,
                'successful_pipelines': successful_pipelines,
                'avg_processing_time': avg_processing_time,
                'total_entities': total_entities,
                'total_relationships': total_relationships
            }
        }, f, indent=2, default=str)
    
    print(f"✓ JSON results saved: {output_file}")
    
    # Save CSV for analysis
    csv_file = f"kgas_demo_data_{int(time.time())}.csv"
    with open(csv_file, 'w') as f:
        # CSV headers
        f.write("user_id,political_score,narcissism_score,denialism_score,conspiracy_score,")
        f.write("entities_extracted,relationships_extracted,processing_time,bayesian_confidence,")
        f.write("quality_score,pipeline_complete\n")
        
        # CSV data
        for data in structured_data:
            f.write(f"{data['user_id']},{data['political_orientation']},{data['narcissism_level']},")
            f.write(f"{data['denialism_tendency']},{data['conspiracy_mentality']},")
            f.write(f"{data['entities_found']},{data['relationships_found']},{data['processing_time_seconds']},")
            f.write(f"{data['bayesian_confidence']},{data['quality_assessment']},{data['pipeline_success']}\n")
    
    print(f"✓ CSV data saved: {csv_file}")
    
    print(f"\n🎯 Demo complete! Check the saved files for detailed results.")
    
    return structured_data

def show_neo4j_data():
    """Show Neo4j graph data if available"""
    try:
        from neo4j import GraphDatabase
        
        driver = GraphDatabase.driver(
            "bolt://localhost:7687",
            auth=("neo4j", "testpassword")
        )
        
        with driver.session() as session:
            # Count nodes
            result = session.run("MATCH (n) RETURN count(n) as node_count")
            node_count = result.single()["node_count"]
            
            # Count relationships
            result = session.run("MATCH ()-[r]->() RETURN count(r) as rel_count")
            rel_count = result.single()["rel_count"]
            
            # Get sample nodes
            result = session.run("MATCH (n) RETURN n LIMIT 5")
            sample_nodes = [record["n"] for record in result]
            
            print(f"✅ Neo4j Connected: http://localhost:7474")
            print(f"   Nodes in database: {node_count}")
            print(f"   Relationships in database: {rel_count}")
            
            if sample_nodes:
                print(f"   Sample nodes:")
                for i, node in enumerate(sample_nodes[:3], 1):
                    labels = list(node.labels)
                    props = dict(node)
                    print(f"     {i}. Labels: {labels}, Properties: {list(props.keys())}")
            
        driver.close()
        
    except Exception as e:
        print(f"❌ Neo4j connection failed: {e}")
        print("   Check if Neo4j is running: python one_click_kgas_setup.py status")

if __name__ == "__main__":
    results = setup_complete_kgas_demo()