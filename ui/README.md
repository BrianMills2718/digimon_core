# GraphRAG Testing UI

A comprehensive web interface for testing and visualizing Super-Digimon GraphRAG capabilities with your own datasets.

## Features

### 🔧 System Status Dashboard
- Real-time status of all phases (Phase 1, 2, 3)
- MCP server connection status
- Configuration controls for testing parameters

### 📄 Document Processing
- **Multi-format support**: PDF, TXT, DOCX files
- **Phase selection**: Choose which phase to use for processing
- **Batch processing**: Upload and process multiple documents
- **Real-time progress**: See processing status and timing
- **Results summary**: Entities found, relationships extracted, processing times

### 🔍 Query Testing
- **Natural language queries**: Test your processed documents
- **Query history**: Track all queries and results
- **Performance metrics**: Query execution times
- **Multi-document search**: Query across all processed documents

### 🕸️ Knowledge Graph Visualization
- **Interactive graphs**: Hover, zoom, pan through your knowledge graphs
- **Multiple layouts**: Spring, circular, hierarchical arrangements
- **Customizable display**: Adjust node sizes, show/hide labels
- **Entity type colors**: Visual distinction between different entity types
- **Relationship visualization**: See connections between entities

### ⚡ Phase Comparison
- **Side-by-side comparison**: Process same document with different phases
- **Performance analysis**: Compare entities found, relationships, and timing
- **Visual charts**: Bar graphs showing phase differences
- **Quality metrics**: Evaluate which phase works best for your data

### 📤 Export & Integration
- **JSON export**: Export all results and processing history
- **Graph data export**: Save knowledge graph structure
- **Analytics reports**: CSV files with processing metrics
- **Integration ready**: Data formats compatible with other tools

## Quick Start

1. **Test your setup**:
   ```bash
   python test_ui_real.py
   ```

2. **Launch the UI**:
   ```bash
   python start_graphrag_ui.py
   ```

3. **Open your browser**: Navigate to http://localhost:8501

4. **Upload documents**: Use the "Document Processing" tab to upload your files

5. **Process documents**: Choose a phase and click "Process Documents"

6. **Visualize results**: See your knowledge graph in the "Graph Visualization" tab

## What Actually Works (No Mocking)

✅ **Document Processing**: Real PDF/TXT processing through Phase 1, 2, or 3 pipelines
✅ **Graph Visualization**: Interactive plots of actual extracted entities and relationships  
✅ **Phase Comparison**: Side-by-side comparison of different phases on same document
✅ **Export Tools**: Download real results as JSON/CSV for external analysis
✅ **System Status**: Honest reporting of what phases are available vs missing

❌ **Query Interface**: Disabled until real graph database integration complete

## Testing Workflow

### Basic Testing
1. Upload a small document (1-2 pages)
2. Process with Phase 1 (basic pipeline)
3. Try some simple queries
4. Examine the knowledge graph

### Advanced Testing
1. Upload the same document multiple times
2. Process with different phases (Phase 1, 2, 3)
3. Compare results in the "Phase Comparison" tab
4. Test complex queries across multiple documents

### Large-Scale Testing
1. Upload multiple documents from your domain
2. Process all with your preferred phase
3. Test domain-specific queries
4. Export results for further analysis

## Supported File Types

- **PDF**: Text extraction with layout preservation
- **TXT**: Plain text files
- **DOCX**: Microsoft Word documents

## Phase Capabilities

### Phase 1: Basic Pipeline
- Text extraction and chunking
- Named Entity Recognition (NER)
- Basic relationship extraction
- Simple graph construction

### Phase 2: Ontology-Aware (if available)
- Domain-specific ontology integration
- Enhanced entity typing
- Ontology-guided relationship extraction
- Improved graph quality

### Phase 3: Multi-Document Fusion (if available)
- Entity deduplication across documents
- Conflict resolution
- Knowledge consolidation
- Cross-document relationship discovery

## Troubleshooting

### Common Issues

1. **"Phase 2/3 Not Available"**
   - Check that required modules are installed
   - Verify MCP server is running
   - See system status in sidebar

2. **Processing Errors**
   - Check file format is supported
   - Ensure files aren't corrupted
   - Try smaller documents first

3. **Visualization Issues**
   - Disable visualization for large graphs
   - Adjust node count in settings
   - Try different layout types

4. **Query Problems**
   - Process documents first
   - Check that graph data exists
   - Try simpler queries initially

### Performance Tips

- Start with small documents (< 10 pages)
- Use Phase 1 for initial testing
- Limit entities displayed for large graphs
- Export data regularly to avoid loss

## Integration with Other Tools

The UI exports data in formats compatible with:
- Jupyter notebooks (JSON format)
- Graph analysis tools (NetworkX-compatible)
- Data science pipelines (CSV analytics)
- Custom applications (structured JSON)

## Development Notes

The UI is built with:
- **Streamlit**: Web framework
- **Plotly**: Interactive visualizations
- **NetworkX**: Graph manipulation
- **Pandas**: Data analysis

For development or customization, see the source code in `ui/graphrag_ui.py`.