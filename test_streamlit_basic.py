#!/usr/bin/env python3
"""
Basic test to ensure Streamlit app can be imported and initialized
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_streamlit_imports():
    """Test that all required imports work"""
    print("Testing Streamlit app imports...")
    
    try:
        import streamlit as st
        print("✓ Streamlit imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import streamlit: {e}")
        return False
    
    try:
        import pandas as pd
        print("✓ Pandas imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import pandas: {e}")
        return False
    
    try:
        import plotly.graph_objects as go
        print("✓ Plotly imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import plotly: {e}")
        return False
    
    try:
        import networkx as nx
        print("✓ NetworkX imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import networkx: {e}")
        return False
    
    return True

def test_ontology_generator():
    """Test that ontology generator can be imported"""
    print("\nTesting ontology generator module...")
    
    try:
        from src.ontology_generator import OntologyGenerator, Ontology, EntityType, RelationType
        print("✓ Ontology generator imported successfully")
        
        # Try to create an instance
        generator = OntologyGenerator()
        print("✓ OntologyGenerator instance created")
        
        # Test mock generation
        ontology = generator._mock_climate_ontology()
        print(f"✓ Mock ontology created: {ontology.domain}")
        print(f"  - Entity types: {len(ontology.entity_types)}")
        print(f"  - Relation types: {len(ontology.relation_types)}")
        
        return True
    except Exception as e:
        print(f"✗ Failed to use ontology generator: {e}")
        return False

def test_streamlit_app_structure():
    """Test that streamlit app has required functions"""
    print("\nTesting Streamlit app structure...")
    
    try:
        # Import the data classes first
        from streamlit_app import EntityType, RelationType, Ontology
        print("✓ Data classes imported")
        
        # Import functions
        from streamlit_app import (
            init_session_state,
            render_header,
            render_sidebar,
            render_chat_interface,
            render_ontology_preview
        )
        print("✓ All UI functions imported")
        
        return True
    except Exception as e:
        print(f"✗ Failed to import from streamlit_app: {e}")
        return False

def main():
    """Run all tests"""
    print("🔬 Super-Digimon Streamlit App Basic Tests")
    print("=" * 50)
    
    all_passed = True
    
    # Test imports
    if not test_streamlit_imports():
        all_passed = False
    
    # Test ontology generator
    if not test_ontology_generator():
        all_passed = False
    
    # Test app structure
    if not test_streamlit_app_structure():
        all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ All tests passed! The Streamlit app should work.")
        print("\nTo run the app:")
        print("  streamlit run streamlit_app.py")
        print("\nOr use the convenience script:")
        print("  ./start_ui.sh")
    else:
        print("❌ Some tests failed. Please install missing dependencies:")
        print("  pip install -r requirements_ui.txt")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)