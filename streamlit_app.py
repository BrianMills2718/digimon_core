"""
Streamlit Web UI for LLM-Driven Ontology Generation System
Academic-focused interface for domain-specific ontology creation through natural conversation
"""

import streamlit as st
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import pandas as pd
from dataclasses import dataclass, asdict
import plotly.graph_objects as go
import networkx as nx
import os
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Import ontology components
try:
    from src.ontology.gemini_ontology_generator import GeminiOntologyGenerator
    from src.core.ontology_storage_service import OntologyStorageService, OntologySession
    USE_REAL_GEMINI = bool(os.getenv("GOOGLE_API_KEY"))
except ImportError:
    USE_REAL_GEMINI = False

from src.ontology_generator import OntologyGenerator, DomainOntology

# Page configuration
st.set_page_config(
    page_title="Ontology Generator - Super-Digimon",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for academic styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 600;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #6b7280;
        margin-bottom: 2rem;
    }
    .ontology-preview {
        background-color: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
    }
    .user-message {
        background-color: #eff6ff;
        border-left: 4px solid #3b82f6;
    }
    .assistant-message {
        background-color: #f0fdf4;
        border-left: 4px solid #10b981;
    }
    .metric-card {
        background-color: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# Data classes for ontology structure
@dataclass
class EntityType:
    name: str
    description: str
    attributes: List[str]
    examples: List[str]
    parent: Optional[str] = None

@dataclass
class RelationType:
    name: str
    description: str
    source_types: List[str]
    target_types: List[str]
    examples: List[str]
    properties: Dict[str, str] = None

@dataclass
class Ontology:
    domain: str
    description: str
    entity_types: List[EntityType]
    relation_types: List[RelationType]
    version: str = "1.0"
    created_at: str = None
    modified_at: str = None

# Initialize session state
def init_session_state():
    """Initialize all session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "current_ontology" not in st.session_state:
        st.session_state.current_ontology = None
    
    if "ontology_history" not in st.session_state:
        st.session_state.ontology_history = []
    
    if "generation_config" not in st.session_state:
        st.session_state.generation_config = {
            "model": "gemini-2.0-flash",
            "temperature": 0.7,
            "max_entities": 20,
            "max_relations": 15,
            "include_hierarchies": True,
            "auto_suggest_attributes": True
        }
    
    if "sample_texts" not in st.session_state:
        st.session_state.sample_texts = []
    
    if "validation_results" not in st.session_state:
        st.session_state.validation_results = None

# Import the actual ontology generator
try:
    from src.ontology_generator import OntologyGenerator
    GENERATOR_AVAILABLE = True
except ImportError:
    GENERATOR_AVAILABLE = False
    st.warning("Ontology generator module not available. Using mock data.")

# Initialize the generator
@st.cache_resource
def get_ontology_generator():
    """Get or create the ontology generator instance"""
    if USE_REAL_GEMINI:
        try:
            return GeminiOntologyGenerator()
        except Exception as e:
            st.warning(f"Could not initialize Gemini generator: {e}")
    
    # Fall back to mock generator
    if GENERATOR_AVAILABLE:
        return OntologyGenerator()
    return None

# Initialize storage service
@st.cache_resource
def get_storage_service():
    """Get or create the storage service instance"""
    try:
        return OntologyStorageService()
    except Exception as e:
        st.warning(f"Could not initialize storage service: {e}")
        return None

# Conversion functions
def domain_to_ui_ontology(domain_ont: DomainOntology) -> Ontology:
    """Convert DomainOntology to UI Ontology format"""
    entity_types = []
    for et in domain_ont.entity_types:
        entity_types.append(EntityType(
            name=et.name,
            description=et.description,
            attributes=et.attributes,
            examples=et.examples
        ))
    
    relation_types = []
    for rt in domain_ont.relationship_types:
        relation_types.append(RelationType(
            name=rt.name,
            description=rt.description,
            source_types=rt.source_types,
            target_types=rt.target_types,
            cardinality="many-to-many",
            properties=[]
        ))
    
    return Ontology(
        domain=domain_ont.domain_name,
        description=domain_ont.domain_description,
        entity_types=entity_types,
        relation_types=relation_types,
        version="1.0",
        created_at=datetime.now().isoformat(),
        modified_at=datetime.now().isoformat()
    )

# Ontology generation functions
def generate_ontology_with_gemini(domain_description: str, config: Dict[str, Any]) -> Ontology:
    """Generate ontology using Gemini or mock data"""
    generator = get_ontology_generator()
    
    if generator and isinstance(generator, GeminiOntologyGenerator):
        try:
            # Use conversation history if available
            messages = st.session_state.messages.copy()
            if not messages:
                messages = [{"role": "user", "content": domain_description}]
            
            # Generate with real Gemini
            ontology = generator.generate_from_conversation(
                messages=messages,
                temperature=config.get("temperature", 0.7),
                constraints={
                    "max_entities": config.get("max_entities", 20),
                    "max_relations": config.get("max_relations", 15),
                    "complexity": "medium"
                }
            )
            
            # Save to storage if available
            storage = get_storage_service()
            if storage:
                session = OntologySession(
                    session_id=f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    created_at=datetime.now(),
                    conversation_history=messages,
                    initial_ontology=ontology,
                    refinements=[],
                    final_ontology=ontology,
                    generation_parameters=config
                )
                storage.save_session(session)
            
            return domain_to_ui_ontology(ontology)
            
        except Exception as e:
            st.error(f"Error generating ontology: {str(e)}")
            # Fall back to mock
    
    if generator:
        try:
            return generator.generate_ontology(domain_description, config)
        except Exception as e:
            st.error(f"Error with mock generator: {str(e)}")
            # Fall back to mock
    
    # Mock ontology for demonstration when generator not available
    return Ontology(
        domain="Climate Policy",
        description="Ontology for climate policy analysis",
        entity_types=[
            EntityType(
                name="CLIMATE_POLICY",
                description="Government policies related to climate change",
                attributes=["policy_name", "jurisdiction", "implementation_date", "target_emissions"],
                examples=["Paris Agreement", "EU Green Deal", "US Clean Power Plan"]
            ),
            EntityType(
                name="POLICY_MAKER",
                description="Individuals or organizations that create climate policies",
                attributes=["name", "role", "organization", "country"],
                examples=["European Commission", "EPA", "IPCC"]
            ),
            EntityType(
                name="EMISSION_TARGET",
                description="Specific emission reduction targets",
                attributes=["target_value", "baseline_year", "target_year", "measurement_unit"],
                examples=["Net-zero by 2050", "50% reduction by 2030"]
            )
        ],
        relation_types=[
            RelationType(
                name="IMPLEMENTS",
                description="Policy maker implements climate policy",
                source_types=["POLICY_MAKER"],
                target_types=["CLIMATE_POLICY"],
                examples=["EPA implements Clean Power Plan"]
            ),
            RelationType(
                name="TARGETS",
                description="Policy targets specific emission goals",
                source_types=["CLIMATE_POLICY"],
                target_types=["EMISSION_TARGET"],
                examples=["Paris Agreement targets 1.5°C warming limit"]
            )
        ],
        created_at=datetime.now().isoformat()
    )

def refine_ontology_with_gemini(ontology: Ontology, refinement_request: str) -> Ontology:
    """Refine ontology using Gemini or return unchanged"""
    generator = get_ontology_generator()
    
    if generator and isinstance(generator, GeminiOntologyGenerator):
        try:
            # Convert UI ontology back to DomainOntology
            from src.ontology_generator import EntityType as DomainEntityType, RelationshipType
            
            entity_types = []
            for et in ontology.entity_types:
                entity_types.append(DomainEntityType(
                    name=et.name,
                    description=et.description,
                    examples=et.examples,
                    attributes=et.attributes
                ))
            
            relationship_types = []
            for rt in ontology.relation_types:
                relationship_types.append(RelationshipType(
                    name=rt.name,
                    description=rt.description,
                    source_types=rt.source_types,
                    target_types=rt.target_types,
                    examples=getattr(rt, 'examples', [])
                ))
            
            current_domain_ont = DomainOntology(
                domain_name=ontology.domain,
                domain_description=ontology.description,
                entity_types=entity_types,
                relationship_types=relationship_types,
                extraction_patterns=[],
                created_by_conversation=""
            )
            
            # Refine with Gemini
            refined = generator.refine_ontology(current_domain_ont, refinement_request)
            
            # Update storage if available
            storage = get_storage_service()
            if storage:
                # Would update existing session here
                pass
            
            return domain_to_ui_ontology(refined)
            
        except Exception as e:
            st.error(f"Error refining ontology: {str(e)}")
            return ontology
    
    if generator:
        try:
            return generator.refine_ontology(ontology, refinement_request)
        except Exception as e:
            st.error(f"Error refining ontology: {str(e)}")
    
    # Fallback: return same ontology with updated timestamp
    ontology.modified_at = datetime.now().isoformat()
    return ontology

def validate_ontology_with_text(ontology: Ontology, sample_text: str) -> Dict[str, Any]:
    """Validate ontology against sample text"""
    generator = get_ontology_generator()
    
    if generator and isinstance(generator, GeminiOntologyGenerator):
        try:
            # Convert UI ontology to DomainOntology for validation
            from src.ontology_generator import EntityType as DomainEntityType, RelationshipType
            
            entity_types = []
            for et in ontology.entity_types:
                entity_types.append(DomainEntityType(
                    name=et.name,
                    description=et.description,
                    examples=et.examples,
                    attributes=et.attributes
                ))
            
            relationship_types = []
            for rt in ontology.relation_types:
                relationship_types.append(RelationshipType(
                    name=rt.name,
                    description=rt.description,
                    source_types=rt.source_types,
                    target_types=rt.target_types,
                    examples=getattr(rt, 'examples', [])
                ))
            
            domain_ont = DomainOntology(
                domain_name=ontology.domain,
                domain_description=ontology.description,
                entity_types=entity_types,
                relationship_types=relationship_types,
                extraction_patterns=[],
                created_by_conversation=""
            )
            
            # Validate with Gemini
            validation_result = generator.validate_ontology(domain_ont, sample_text)
            
            # Convert to UI format
            entities_found = len(validation_result.get("entities", []))
            relations_found = len(validation_result.get("relationships", []))
            total_possible = len(ontology.entity_types) + len(ontology.relation_types)
            coverage = (entities_found + relations_found) / max(total_possible, 1)
            
            suggestions = validation_result.get("issues", [])
            if not suggestions:
                suggestions = ["Ontology appears well-suited for this domain"]
            
            return {
                "entities_found": entities_found,
                "relations_found": relations_found,
                "coverage": min(coverage, 1.0),
                "suggestions": suggestions,
                "raw_results": validation_result
            }
            
        except Exception as e:
            st.error(f"Error validating ontology: {str(e)}")
    
    if generator:
        try:
            return generator.validate_with_text(ontology, sample_text)
        except Exception as e:
            st.error(f"Error validating ontology: {str(e)}")
    
    # Fallback mock validation
    return {
        "entities_found": 15,
        "relations_found": 8,
        "coverage": 0.75,
        "suggestions": [
            "Consider adding 'RENEWABLE_ENERGY' entity type",
            "Relation 'OPPOSES' might be useful for policy conflicts"
        ]
    }

# UI Components
def render_header():
    """Render the main header section"""
    st.markdown('<h1 class="main-header">🔬 Ontology Generator</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Create domain-specific ontologies through natural conversation</p>', unsafe_allow_html=True)

def render_sidebar():
    """Render the sidebar with configuration options"""
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Model settings
        st.subheader("Model Settings")
        config = st.session_state.generation_config
        
        config["model"] = st.selectbox(
            "LLM Model",
            ["gemini-2.0-flash", "gemini-1.5-pro", "gpt-4"],
            index=0
        )
        
        config["temperature"] = st.slider(
            "Temperature",
            0.0, 1.0, config["temperature"],
            help="Higher values make output more creative"
        )
        
        # Ontology constraints
        st.subheader("Ontology Constraints")
        config["max_entities"] = st.number_input(
            "Max Entity Types",
            5, 50, config["max_entities"]
        )
        
        config["max_relations"] = st.number_input(
            "Max Relation Types",
            5, 30, config["max_relations"]
        )
        
        config["include_hierarchies"] = st.checkbox(
            "Include Entity Hierarchies",
            config["include_hierarchies"]
        )
        
        config["auto_suggest_attributes"] = st.checkbox(
            "Auto-suggest Attributes",
            config["auto_suggest_attributes"]
        )
        
        # Export options
        st.subheader("Export Options")
        if st.session_state.current_ontology:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📄 Export JSON"):
                    export_ontology_json()
            with col2:
                if st.button("🔗 Export RDF"):
                    st.info("RDF export coming soon")
        
        # History
        st.subheader("📚 History")
        if st.session_state.ontology_history:
            for i, hist in enumerate(st.session_state.ontology_history[-5:]):
                if st.button(f"{hist['domain']} - {hist['timestamp'][:10]}", key=f"hist_{i}"):
                    load_ontology_from_history(i)

def render_chat_interface():
    """Render the main chat interface"""
    st.header("💬 Ontology Design Chat")
    
    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f'<div class="chat-message user-message">👤 <b>You:</b> {message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message assistant-message">🤖 <b>Assistant:</b> {message["content"]}</div>', unsafe_allow_html=True)
    
    # Chat input
    col1, col2 = st.columns([4, 1])
    with col1:
        user_input = st.text_area(
            "Describe your domain or ask for refinements",
            placeholder="e.g., 'I need an ontology for analyzing climate change policies and their economic impacts...'",
            key="user_input",
            height=100
        )
    
    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        if st.button("🚀 Generate/Refine", type="primary", use_container_width=True):
            if user_input:
                process_user_input(user_input)

def render_ontology_preview():
    """Render the ontology preview section"""
    st.header("📊 Ontology Preview")
    
    if st.session_state.current_ontology:
        ontology = st.session_state.current_ontology
        
        # Tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["📋 Structure", "🔍 Details", "📈 Visualization", "✅ Validation"])
        
        with tab1:
            render_ontology_structure(ontology)
        
        with tab2:
            render_ontology_details(ontology)
        
        with tab3:
            render_ontology_graph(ontology)
        
        with tab4:
            render_validation_interface()
    else:
        st.info("💡 Start by describing your domain in the chat above to generate an ontology")

def render_ontology_structure(ontology: Ontology):
    """Render the ontology structure overview"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Entity Types", len(ontology.entity_types))
    with col2:
        st.metric("Relation Types", len(ontology.relation_types))
    with col3:
        total_attrs = sum(len(et.attributes) for et in ontology.entity_types)
        st.metric("Total Attributes", total_attrs)
    
    # Entity types summary
    st.subheader("Entity Types")
    entity_data = []
    for et in ontology.entity_types:
        entity_data.append({
            "Name": et.name,
            "Description": et.description,
            "Attributes": ", ".join(et.attributes),
            "Examples": ", ".join(et.examples[:3])
        })
    
    df_entities = pd.DataFrame(entity_data)
    st.dataframe(df_entities, use_container_width=True)
    
    # Relation types summary
    st.subheader("Relation Types")
    relation_data = []
    for rt in ontology.relation_types:
        relation_data.append({
            "Name": rt.name,
            "Description": rt.description,
            "Source → Target": f"{', '.join(rt.source_types)} → {', '.join(rt.target_types)}",
            "Examples": ", ".join(rt.examples[:2])
        })
    
    df_relations = pd.DataFrame(relation_data)
    st.dataframe(df_relations, use_container_width=True)

def render_ontology_details(ontology: Ontology):
    """Render detailed view of the ontology"""
    # Metadata
    st.subheader("📄 Metadata")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Domain:** {ontology.domain}")
        st.write(f"**Version:** {ontology.version}")
    with col2:
        st.write(f"**Created:** {ontology.created_at[:19] if ontology.created_at else 'N/A'}")
        st.write(f"**Modified:** {ontology.modified_at[:19] if ontology.modified_at else 'N/A'}")
    
    st.write(f"**Description:** {ontology.description}")
    
    # Detailed entity types
    st.subheader("🔤 Entity Types (Detailed)")
    for et in ontology.entity_types:
        with st.expander(f"**{et.name}**"):
            st.write(f"**Description:** {et.description}")
            st.write(f"**Parent:** {et.parent or 'None'}")
            st.write("**Attributes:**")
            for attr in et.attributes:
                st.write(f"  • {attr}")
            st.write("**Examples:**")
            for example in et.examples:
                st.write(f"  • {example}")
    
    # Detailed relation types
    st.subheader("🔗 Relation Types (Detailed)")
    for rt in ontology.relation_types:
        with st.expander(f"**{rt.name}**"):
            st.write(f"**Description:** {rt.description}")
            st.write(f"**Source Types:** {', '.join(rt.source_types)}")
            st.write(f"**Target Types:** {', '.join(rt.target_types)}")
            st.write("**Examples:**")
            for example in rt.examples:
                st.write(f"  • {example}")
            if rt.properties:
                st.write("**Properties:**")
                for prop, desc in rt.properties.items():
                    st.write(f"  • {prop}: {desc}")

def render_ontology_graph(ontology: Ontology):
    """Render interactive graph visualization of the ontology"""
    # Create networkx graph
    G = nx.DiGraph()
    
    # Add entity nodes
    for et in ontology.entity_types:
        G.add_node(et.name, node_type="entity", description=et.description)
    
    # Add relation edges
    for rt in ontology.relation_types:
        for source in rt.source_types:
            for target in rt.target_types:
                G.add_edge(source, target, relation=rt.name, description=rt.description)
    
    # Create plotly figure
    pos = nx.spring_layout(G, k=3, iterations=50)
    
    # Create edge traces
    edge_traces = []
    for edge in G.edges(data=True):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        
        edge_trace = go.Scatter(
            x=[x0, x1, None],
            y=[y0, y1, None],
            mode='lines',
            line=dict(width=2, color='#888'),
            hoverinfo='text',
            text=edge[2].get('relation', ''),
            showlegend=False
        )
        edge_traces.append(edge_trace)
    
    # Create node trace
    node_x = []
    node_y = []
    node_text = []
    node_colors = []
    
    for node in G.nodes(data=True):
        x, y = pos[node[0]]
        node_x.append(x)
        node_y.append(y)
        node_text.append(f"{node[0]}<br>{node[1].get('description', '')}")
        node_colors.append('#3b82f6' if node[1].get('node_type') == 'entity' else '#ef4444')
    
    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        text=[node for node in G.nodes()],
        textposition="top center",
        hoverinfo='text',
        hovertext=node_text,
        marker=dict(
            size=30,
            color=node_colors,
            line=dict(width=2, color='white')
        )
    )
    
    # Create figure
    fig = go.Figure(data=edge_traces + [node_trace])
    fig.update_layout(
        showlegend=False,
        hovermode='closest',
        margin=dict(b=0, l=0, r=0, t=0),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_validation_interface():
    """Render the validation interface for testing the ontology"""
    st.subheader("🧪 Validate Ontology")
    
    # Upload sample text
    uploaded_file = st.file_uploader("Upload sample text file", type=["txt", "pdf"])
    
    # Or paste text
    sample_text = st.text_area(
        "Or paste sample text here",
        placeholder="Paste a sample document from your domain to test entity extraction...",
        height=200
    )
    
    if st.button("🔍 Validate", type="primary"):
        if uploaded_file or sample_text:
            # TODO: Process uploaded file if provided
            text_to_validate = sample_text if sample_text else "File processing not yet implemented"
            
            with st.spinner("Validating ontology against sample text..."):
                results = validate_ontology_with_text(st.session_state.current_ontology, text_to_validate)
                st.session_state.validation_results = results
    
    # Display validation results
    if st.session_state.validation_results:
        results = st.session_state.validation_results
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Entities Found", results["entities_found"])
        with col2:
            st.metric("Relations Found", results["relations_found"])
        with col3:
            st.metric("Coverage", f"{results['coverage']*100:.1f}%")
        
        if results.get("suggestions"):
            st.subheader("💡 Suggestions for Improvement")
            for suggestion in results["suggestions"]:
                st.info(f"• {suggestion}")

# Helper functions
def process_user_input(user_input: str):
    """Process user input and generate/refine ontology"""
    # Add to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    with st.spinner("🤔 Thinking..."):
        if st.session_state.current_ontology is None:
            # Generate new ontology
            ontology = generate_ontology_with_gemini(user_input, st.session_state.generation_config)
            st.session_state.current_ontology = ontology
            response = f"I've generated an ontology for the domain '{ontology.domain}' with {len(ontology.entity_types)} entity types and {len(ontology.relation_types)} relation types."
        else:
            # Refine existing ontology
            ontology = refine_ontology_with_gemini(st.session_state.current_ontology, user_input)
            st.session_state.current_ontology = ontology
            response = "I've refined the ontology based on your feedback. The changes have been applied."
        
        # Add to history
        save_to_history(ontology)
        
        # Add assistant response
        st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Clear input
    st.session_state.user_input = ""
    st.rerun()

def save_to_history(ontology: Ontology):
    """Save ontology to history"""
    history_entry = {
        "domain": ontology.domain,
        "timestamp": datetime.now().isoformat(),
        "ontology": asdict(ontology)
    }
    st.session_state.ontology_history.append(history_entry)

def load_ontology_from_history(index: int):
    """Load ontology from history"""
    history_entry = st.session_state.ontology_history[-(index+1)]
    ontology_dict = history_entry["ontology"]
    
    # Reconstruct ontology from dict
    entity_types = [EntityType(**et) for et in ontology_dict["entity_types"]]
    relation_types = [RelationType(**rt) for rt in ontology_dict["relation_types"]]
    
    st.session_state.current_ontology = Ontology(
        domain=ontology_dict["domain"],
        description=ontology_dict["description"],
        entity_types=entity_types,
        relation_types=relation_types,
        version=ontology_dict["version"],
        created_at=ontology_dict["created_at"],
        modified_at=ontology_dict["modified_at"]
    )
    st.rerun()

def export_ontology_json():
    """Export current ontology as JSON"""
    if st.session_state.current_ontology:
        ontology_dict = asdict(st.session_state.current_ontology)
        json_str = json.dumps(ontology_dict, indent=2)
        
        st.download_button(
            label="Download JSON",
            data=json_str,
            file_name=f"ontology_{st.session_state.current_ontology.domain.lower().replace(' ', '_')}.json",
            mime="application/json"
        )

# Main app
def main():
    """Main application entry point"""
    init_session_state()
    
    # Header
    render_header()
    
    # Sidebar
    render_sidebar()
    
    # Main content area
    col1, col2 = st.columns([1, 1.5])
    
    with col1:
        render_chat_interface()
    
    with col2:
        render_ontology_preview()
    
    # Footer
    st.markdown("---")
    st.markdown("🔬 **Super-Digimon Ontology Generator** | Academic Knowledge Graph Platform")

if __name__ == "__main__":
    main()