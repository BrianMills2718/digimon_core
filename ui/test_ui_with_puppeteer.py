#!/usr/bin/env python3
"""
Test KGAS UI using Puppeteer MCP
This script demonstrates how to use Puppeteer MCP to automate UI testing and development
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from ui.puppeteer_ui_automation import PuppeteerUIAutomation


async def test_standalone_ui():
    """Test the standalone research UI with Puppeteer MCP"""
    automation = PuppeteerUIAutomation()
    
    print("🚀 Starting UI automation test sequence...")
    print("=" * 50)
    
    # First create the UI if it doesn't exist
    ui_path = Path("ui/research_ui.html")
    if not ui_path.exists():
        print("📝 Creating research UI...")
        ui_path = await automation.create_standalone_research_ui()
    else:
        print(f"✅ Using existing UI at: {ui_path}")
    
    # Generate test sequence
    test_sequence = await automation.test_ui_with_puppeteer(str(ui_path))
    
    print("\n📋 Test Sequence to Execute with Puppeteer MCP:")
    print("-" * 50)
    
    # Print instructions for using Puppeteer MCP
    print("\nTo execute this test sequence, use the Puppeteer MCP tools in order:\n")
    
    for i, action in enumerate(test_sequence, 1):
        print(f"Step {i}: {action['description']}")
        
        if action['action'] == 'navigate':
            print(f"  Tool: mcp__puppeteer__puppeteer_navigate")
            print(f"  Parameters:")
            print(f"    url: {action['url']}")
            
        elif action['action'] == 'screenshot':
            print(f"  Tool: mcp__puppeteer__puppeteer_screenshot")
            print(f"  Parameters:")
            print(f"    name: {action['name']}")
            print(f"    width: 1200")
            print(f"    height: 800")
            
        elif action['action'] == 'click':
            print(f"  Tool: mcp__puppeteer__puppeteer_click")
            print(f"  Parameters:")
            print(f"    selector: {action['selector']}")
            
        elif action['action'] == 'evaluate':
            print(f"  Tool: mcp__puppeteer__puppeteer_evaluate")
            print(f"  Parameters:")
            print(f"    script: {action['script']}")
        
        print()
    
    print("\n✨ Test sequence ready for execution!")
    print("\nNote: The actual execution needs to be done through the Puppeteer MCP tools")
    print("      This script generates the test plan for manual or automated execution")
    
    # Also save the test sequence for reference
    import json
    test_plan_path = Path("ui/puppeteer_test_plan.json")
    test_plan_path.write_text(json.dumps({
        "ui_path": str(ui_path.absolute()),
        "test_sequence": test_sequence,
        "generated_at": automation.generate_ui_automation_report()["timestamp"]
    }, indent=2))
    
    print(f"\n💾 Test plan saved to: {test_plan_path}")


async def test_streamlit_ui():
    """Test the existing Streamlit UI with Puppeteer MCP"""
    automation = PuppeteerUIAutomation()
    
    print("\n🎯 Streamlit UI Test Sequence:")
    print("=" * 50)
    
    streamlit_tests = [
        {
            "action": "navigate",
            "url": "http://localhost:8501",
            "description": "Navigate to Streamlit UI"
        },
        {
            "action": "screenshot",
            "name": "streamlit_initial",
            "description": "Capture Streamlit initial state"
        },
        await automation.test_document_upload(),
        await automation.test_phase_selection(),
    ]
    
    print("\nTo test Streamlit UI:")
    print("1. First start Streamlit: streamlit run ui/graphrag_ui.py")
    print("2. Then execute these Puppeteer MCP commands:")
    
    for test in streamlit_tests:
        if isinstance(test, list):
            for action in test:
                print(f"\n- {action['description']}")
        else:
            print(f"\n- {test['description']}")


if __name__ == "__main__":
    print("🤖 KGAS UI Testing with Puppeteer MCP")
    print("=" * 70)
    
    # Run both test sequences
    asyncio.run(test_standalone_ui())
    asyncio.run(test_streamlit_ui())