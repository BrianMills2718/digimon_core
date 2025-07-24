#!/usr/bin/env python3
"""
Simple runner for Real MCP Adaptive Agents

This script makes it easy to test the real adaptive agent system
with your actual KGAS MCP infrastructure.
"""

import asyncio
import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from agent_stress_testing.real_mcp_adaptive_agents import RealAdaptiveAgentOrchestrator


async def run_demo():
    """Run a simple demo of real adaptive agents"""
    
    print("🚀 REAL MCP ADAPTIVE AGENTS DEMO")
    print("=" * 50)
    print("Prerequisites:")
    print("  1. KGAS MCP server running: python src/mcp_server.py")
    print("  2. Claude Code CLI installed and configured")
    print("  3. Neo4j database available")
    print("=" * 50)
    
    # Initialize orchestrator
    orchestrator = RealAdaptiveAgentOrchestrator()
    
    # Simple research objective
    objective = """
    Analyze research collaboration patterns by processing documents, 
    extracting entities and relationships, building a knowledge graph,
    and generating insights about collaboration effectiveness.
    """
    
    # Use demo documents
    demo_data_dir = Path(__file__).parent / "demo_data"
    demo_data_dir.mkdir(exist_ok=True)
    
    # Create simple demo documents if they don't exist
    doc1_path = demo_data_dir / "cognitive_mapping_paper.txt"
    doc2_path = demo_data_dir / "collaboration_networks_paper.txt"
    
    if not doc1_path.exists():
        with open(doc1_path, 'w') as f:
            f.write("""
            Cognitive Mapping in Decision Making
            
            Abstract: This paper explores how cognitive mapping influences decision-making processes
            in collaborative research environments. We analyze data from 150 research teams
            to understand the relationship between cognitive mapping strategies and research outcomes.
            
            Introduction: Cognitive mapping refers to the mental representation of spatial 
            and conceptual relationships. In research collaboration, effective cognitive mapping
            enables teams to better coordinate their efforts and share knowledge.
            
            Methodology: We surveyed research teams from universities including MIT, Stanford,
            and Harvard. Teams were assessed on their cognitive mapping practices and 
            collaboration effectiveness.
            
            Results: Teams with structured cognitive mapping showed 35% higher productivity
            and better knowledge sharing. The relationship between mapping quality and
            research impact was significant (p < 0.01).
            """)
    
    if not doc2_path.exists():
        with open(doc2_path, 'w') as f:
            f.write("""
            Network Analysis of Scientific Collaboration
            
            Abstract: This study examines collaboration networks in cognitive science research
            using graph analysis techniques. We identify key patterns that predict successful
            research outcomes and innovation.
            
            Introduction: Scientific collaboration has become increasingly important for
            breakthrough discoveries. Understanding network structures helps optimize
            research team formation and knowledge transfer.
            
            Methodology: We analyzed collaboration data from 2,500 publications spanning
            10 years. Network metrics included centrality, clustering, and path analysis.
            Institutions studied include Berkeley, CMU, and Oxford.
            
            Results: Hub researchers with high betweenness centrality facilitated
            knowledge transfer between research communities. Small-world properties
            in collaboration networks predicted higher citation impact.
            """)
    
    documents = [str(doc1_path), str(doc2_path)]
    
    print(f"\\nDemo Setup:")
    print(f"  • Research Objective: {objective.strip()}")
    print(f"  • Documents: {len(documents)} demo files created")
    
    try:
        # Run the real adaptive research
        print(f"\\n🚀 Starting Real Adaptive Research...")
        results = await orchestrator.run_real_adaptive_research(objective, documents)
        
        print(f"\\n📊 Demo Results:")
        if results.get("status") == "completed":
            metrics = results["performance_metrics"]
            print(f"  ✅ Success! Duration: {metrics['total_duration']:.1f}s")
            print(f"  📡 MCP Calls: {metrics['mcp_calls_made']}")
            print(f"  🤖 Claude CLI Calls: {metrics['claude_cli_calls']}")
            print(f"  🔄 Adaptations: {metrics['adaptations_count']}")
            print(f"  ✅ Success Rate: {metrics['success_rate']:.1%}")
            
            # Show key insights
            synthesis = results.get("final_synthesis", {})
            insights = synthesis.get("key_insights", [])
            if insights:
                print(f"\\n🎯 Key Insights Discovered:")
                for insight in insights[:3]:
                    print(f"    • {insight}")
        
        else:
            print(f"  ❌ Failed: {results.get('error')}")
            
        return results
        
    except Exception as e:
        print(f"\\n❌ Demo failed with error: {e}")
        return {"status": "error", "error": str(e)}


async def check_prerequisites():
    """Check if prerequisites are available"""
    
    print("🔍 Checking Prerequisites...")
    
    # Check if MCP server path exists
    mcp_server_path = Path("src/mcp_server.py")
    if mcp_server_path.exists():
        print("  ✅ MCP server file found")
    else:
        print("  ❌ MCP server file not found at src/mcp_server.py")
        return False
    
    # Check if Claude CLI is available
    try:
        import subprocess
        result = subprocess.run(["claude", "--version"], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("  ✅ Claude Code CLI available")
        else:
            print("  ⚠️ Claude Code CLI may not be properly configured")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("  ❌ Claude Code CLI not found in PATH")
        print("      Install with: pip install claude-code")
        return False
    
    # Check Python dependencies
    try:
        import mcp
        print("  ✅ MCP library available")
    except ImportError:
        print("  ❌ MCP library not found")
        print("      Install with: pip install mcp")
        return False
    
    return True


def main():
    """Main entry point"""
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("🤖 Real MCP Adaptive Agents - Demo Runner")
    print("=" * 50)
    
    # Check prerequisites
    if not asyncio.run(check_prerequisites()):
        print("\\n❌ Prerequisites not met. Please install missing components.")
        sys.exit(1)
    
    print("\\n✅ Prerequisites check passed!")
    
    # Run the demo
    results = asyncio.run(run_demo())
    
    if results.get("status") == "completed":
        print("\\n🎉 Demo completed successfully!")
        print("\\nThis demonstrated real adaptive agents using:")
        print("  ✓ Your actual KGAS MCP tools")
        print("  ✓ Real Claude Code CLI coordination")
        print("  ✓ Intelligent LLM-based adaptations")
        print("  ✓ Real database operations")
        sys.exit(0)
    else:
        print("\\n💥 Demo failed. Check the error messages above.")
        sys.exit(1)


if __name__ == "__main__":
    main()