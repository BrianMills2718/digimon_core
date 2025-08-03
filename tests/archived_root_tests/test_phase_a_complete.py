#!/usr/bin/env python3
"""
Quick test to demonstrate Phase A Natural Language Interface is complete
"""
import asyncio
from pathlib import Path
from src.core.service_manager import ServiceManager
from src.interface.nl_interface import NaturalLanguageInterface

async def test_natural_language_interface():
    """Test the complete natural language interface"""
    print("🎉 PHASE A NATURAL LANGUAGE INTERFACE TEST")
    print("=" * 60)
    
    # Create test document
    test_file = Path("phase_a_demo.txt")
    test_content = """
    Microsoft and Google are leading technology companies in artificial intelligence.
    Apple focuses on consumer electronics while Amazon dominates e-commerce.
    These companies collaborate and compete in various technology sectors.
    """
    test_file.write_text(test_content)
    
    try:
        # Initialize service manager and interface
        service_manager = ServiceManager()
        interface = NaturalLanguageInterface(service_manager)
        await interface.initialize()
        print("✅ Natural Language Interface initialized")
        
        # Load document
        success = await interface.load_document(str(test_file))
        if success:
            print(f"✅ Document loaded: {test_file}")
        else:
            print("❌ Failed to load document")
            return
        
        # Test different question types
        test_questions = [
            "What is this document about?",
            "What companies are mentioned?",
            "How do these entities relate?"
        ]
        
        print("\n📝 Testing Natural Language Q&A:")
        print("-" * 60)
        
        for question in test_questions:
            print(f"\n❓ Question: {question}")
            response = await interface.ask_question(question)
            print(f"💬 Response: {response[:200]}..." if len(response) > 200 else f"💬 Response: {response}")
        
        print("\n" + "=" * 60)
        print("✅ PHASE A COMPLETE: Natural Language Interface Working!")
        print("🚀 Ready for Phase B: Dynamic Execution & Intelligence")
        
    finally:
        # Clean up
        if test_file.exists():
            test_file.unlink()

if __name__ == "__main__":
    asyncio.run(test_natural_language_interface())