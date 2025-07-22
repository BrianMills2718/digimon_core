---
status: living
doc-type: ui-readme
governance: doc-governance
---

# KGAS (Knowledge Graph Analysis System) – UI Guide

This UI is part of the Knowledge Graph Analysis System (KGAS) described in the dissertation 'Theoretical Foundations for LLM-Generated Ontologies and Analysis of Fringe Discourse.'

## Navigation
- [KGAS Evergreen Documentation](KGAS_EVERGREEN_DOCUMENTATION.md)
- [Roadmap](ROADMAP_v2.1.md)
- [Architecture](ARCHITECTURE.md)
- [Compatibility Matrix](COMPATIBILITY_MATRIX.md)

# Ontology Generator UI

This Streamlit-based web interface allows researchers to create domain-specific ontologies through natural conversation with an LLM.

## Features

- **Interactive Chat Interface**: Describe your domain in natural language
- **Real-time Ontology Generation**: Powered by Gemini 2.0 Flash
- **Visual Graph Representation**: Interactive network visualization
- **Ontology Validation**: Test against sample texts
- **Export Options**: JSON format (RDF coming soon)
- **Version History**: Track and reload previous ontologies

## Quick Start

1. **Install UI dependencies**:
   ```bash
   pip install -r requirements_ui.txt
   ```

2. **Start the databases** (if not already running):
   ```bash
   docker-compose up -d
   ```

3. **Run the UI**:
   ```bash
   streamlit run streamlit_app.py
   ```
   
   Or use the convenience script:
   ```bash
   ./start_ui.sh
   ```

4. **Access the UI**:
   Open http://localhost:8501 in your browser

## Usage Guide

### Creating an Ontology

1. In the chat interface, describe your domain:
   ```
   "I need an ontology for analyzing climate change policies and their 
   economic impacts. The domain should cover government policies, emission 
   targets, policy instruments like carbon taxes, and key stakeholders."
   ```

2. The system will generate an initial ontology with:
   - Domain-specific entity types (e.g., CLIMATE_POLICY, EMISSION_TARGET)
   - Meaningful relationships (e.g., IMPLEMENTS, TARGETS)
   - Attributes and examples for each entity type

### Refining the Ontology

Continue the conversation to refine:
- "Add an entity type for renewable energy projects"
- "Include a relationship for policy opposition"
- "Add temporal attributes to track policy evolution"

### Validating Your Ontology

1. Click the "Validation" tab
2. Upload or paste sample text from your domain
3. The system will:
   - Extract entities using your ontology
   - Calculate coverage metrics
   - Suggest improvements

### Configuration Options

In the sidebar, adjust:
- **Model**: Choose between Gemini variants
- **Temperature**: Control creativity (0.0-1.0)
- **Max Entities/Relations**: Set complexity limits
- **Hierarchies**: Enable entity inheritance
- **Auto-suggest**: Let the AI recommend attributes

## Architecture

The UI consists of:

1. **streamlit_app.py**: Main UI application
2. **src/ontology_generator.py**: Core generation logic
3. **Data Classes**:
   - `Ontology`: Complete domain ontology
   - `EntityType`: Named entities with attributes
   - `RelationType`: Connections between entities

## Integration with KGAS

Generated ontologies can be used with:
- **T23c**: Ontology-aware entity extraction
- **T46**: Entity-based graph building
- **T49**: Multi-hop query resolution

## Troubleshooting

### "Module not found" errors
```bash
pip install -r requirements.txt -r requirements_ui.txt
```

### "Cannot connect to databases"
```bash
docker-compose up -d
docker-compose ps  # Check status
```

### Gemini API errors
Ensure your `.env` file contains:
```
GOOGLE_API_KEY=your-api-key-here
```

## Next Steps

After creating your ontology:
1. Export as JSON for use in pipelines
2. Test with real documents from your domain
3. Integrate with the full KGAS pipeline
4. Use for GraphRAG queries on your knowledge base-e 
<br><sup>See `docs/planning/roadmap.md` for master plan.</sup>
