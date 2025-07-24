#!/usr/bin/env python3
"""
Run Adaptive Dual-Agent Demonstration

Shows real intelligent planning and course correction with actual tools and data.
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from real_adaptive_demo import AdaptiveDualAgentDemo

async def main():
    """Run the comprehensive adaptive agent demonstration"""
    
    print("🤖 ADAPTIVE DUAL-AGENT DEMONSTRATION")
    print("="*60)
    print("This demo shows intelligent agents that:")
    print("  ✓ Plan complex multi-tool analytical workflows")
    print("  ✓ Execute real tools with actual data processing") 
    print("  ✓ Adapt plans in real-time based on results")
    print("  ✓ Course-correct when tools fail or data quality is poor")
    print("  ✓ Use real MCP integration and database operations")
    print("="*60)
    
    # Initialize demo
    demo = AdaptiveDualAgentDemo()
    
    # Prepare sample documents (use actual files we created)
    demo_data_dir = Path(__file__).parent / "demo_data"
    sample_documents = [
        str(demo_data_dir / "sample_research_paper.txt"),
        str(demo_data_dir / "sample_research_paper2.txt")
    ]
    
    # Define research objective
    research_objective = """
    Conduct a comprehensive analysis of cognitive science research collaboration patterns by:
    
    1. Processing the provided academic papers to extract key concepts and methodologies
    2. Identifying relationships between different theoretical frameworks 
    3. Building a knowledge graph that connects authors, concepts, and research approaches
    4. Analyzing network properties to understand how collaboration affects innovation
    5. Generating insights about optimal research collaboration strategies
    
    The analysis should demonstrate adaptive planning by adjusting approaches if:
    - Text processing tools encounter formatting issues
    - Named entity recognition produces low-quality results  
    - Relationship extraction fails to find meaningful connections
    - Network analysis reveals unexpected patterns requiring different approaches
    """
    
    print(f"\n📋 Research Objective:")
    print(research_objective)
    
    print(f"\n📄 Sample Documents:")
    for i, doc in enumerate(sample_documents, 1):
        if Path(doc).exists():
            size_kb = Path(doc).stat().st_size / 1024
            print(f"  {i}. {Path(doc).name} ({size_kb:.1f}KB)")
        else:
            print(f"  {i}. {doc} (NOT FOUND)")
    
    print(f"\n🚀 Starting Adaptive Demonstration...")
    print("This will show real-time planning, execution, and course correction.")
    
    # Run the demonstration
    try:
        results = await demo.run_adaptive_demo(research_objective, sample_documents)
        
        print("\n" + "="*60)
        print("🏆 DEMONSTRATION COMPLETED")
        print("="*60)
        
        # Display key results
        if results.get("demo_status") == "completed":
            metrics = results.get("performance_metrics", {})
            
            print(f"📊 Performance Metrics:")
            print(f"  • Total Duration: {metrics.get('total_duration', 0):.1f} seconds")
            print(f"  • Plan Adaptations: {metrics.get('plan_adaptations', 0)}")
            print(f"  • Tools Executed: {metrics.get('tools_executed', 0)}")
            print(f"  • Success Rate: {metrics.get('success_rate', 0):.1%}")
            print(f"  • Data Quality: {metrics.get('data_quality_score', 0):.1%}")
            
            print(f"\n🧠 Adaptations Made:")
            adaptations = results.get("adaptations_made", [])
            if adaptations:
                for i, adaptation in enumerate(adaptations, 1):
                    print(f"  {i}. {adaptation.get('reason', 'Unknown reason')}")
                    print(f"     Type: {adaptation.get('adaptation_type', 'Unknown')}")
                    print(f"     Trigger: {adaptation.get('trigger', 'Unknown')}")
            else:
                print("  No adaptations were needed - plan executed successfully!")
            
            print(f"\n📈 Knowledge Graph Stats:")
            graph_stats = results.get("knowledge_graph_stats", {})
            if "error" not in graph_stats:
                print(f"  • Entities Created: {graph_stats.get('entity_count', 0)}")
                print(f"  • Relationships Found: {graph_stats.get('relationship_count', 0)}")
                print(f"  • Graph Density: {graph_stats.get('density', 0):.3f}")
            else:
                print(f"  Graph statistics unavailable: {graph_stats.get('error', 'Unknown error')}")
            
            print(f"\n🎯 Final Synthesis:")
            synthesis = results.get("final_synthesis", {})
            if synthesis.get("research_success_score"):
                print(f"  • Research Success Score: {synthesis['research_success_score']:.1%}")
            if synthesis.get("key_insights"):
                print(f"  • Key Insights Discovered: {len(synthesis['key_insights'])}")
                for insight in synthesis["key_insights"][:3]:  # Show first 3
                    print(f"    - {insight}")
            
        else:
            print(f"❌ Demo failed: {results.get('error', 'Unknown error')}")
            if "partial_results" in results:
                partial = results["partial_results"]
                print(f"Partial execution log: {len(partial.get('execution_log', []))} steps")
                print(f"Adaptations attempted: {len(partial.get('adaptations', []))}")
        
        # Save detailed results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = Path(__file__).parent / f"demo_results_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Detailed results saved to: {results_file}")
        
        print(f"\n✨ Demonstration Complete!")
        print("This showed real adaptive dual-agent workflow execution with:")
        print("  ✓ Intelligent planning by Research Agent")
        print("  ✓ Real tool execution by Execution Agent")  
        print("  ✓ Course correction based on actual results")
        print("  ✓ Adaptation when tools failed or quality was poor")
        print("  ✓ Real-time coordination between agents")
        
        return results
        
    except Exception as e:
        print(f"\n❌ Demo encountered error: {str(e)}")
        print("This might be due to:")
        print("  - Missing dependencies (Claude Code CLI, MCP server)")
        print("  - API rate limits or authentication issues")
        print("  - Network connectivity problems")
        print("  - File path or permission issues")
        
        import traceback
        print(f"\nFull error trace:")
        traceback.print_exc()
        
        return {"demo_status": "error", "error": str(e)}

if __name__ == "__main__":
    # Ensure demo data directory exists
    demo_data_dir = Path(__file__).parent / "demo_data"
    demo_data_dir.mkdir(exist_ok=True)
    
    # Run the demo
    results = asyncio.run(main())
    
    # Exit with appropriate code
    if results.get("demo_status") == "completed":
        sys.exit(0)
    else:
        sys.exit(1)