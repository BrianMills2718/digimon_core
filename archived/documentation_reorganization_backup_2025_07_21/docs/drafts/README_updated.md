# KGAS (Knowledge Graph Analysis System)

## Overview

KGAS is an academic research system for theory-aware knowledge graph analysis with cross-modal capabilities. It enables researchers to analyze documents through multiple analytical lenses (graph, table, vector) while maintaining theoretical grounding and source traceability.

## Current Implementation Status

### Working Today
- ✅ Basic entity extraction using SpaCy NER
- ✅ Neo4j graph database integration
- ✅ PDF document processing
- ✅ Simple relationship extraction
- ✅ Basic Streamlit UI

### In Active Development
- 🚧 Cross-modal analysis framework (graph ↔ table ↔ vector conversions)
- 🚧 Theory-aware extraction with automated schema generation
- 🚧 Uncertainty quantification with CERQual framework
- 🚧 MCP protocol integration for LLM orchestration

### Target Capabilities (See [Architecture Documentation](docs/architecture/))
- Theory-guided entity and relationship extraction
- Fluid movement between graph, table, and vector representations
- Sophisticated uncertainty tracking and propagation
- LLM-driven analysis orchestration via MCP
- Full provenance tracking to source documents

## Quick Start

### Prerequisites
- Python 3.8+
- Docker (for Neo4j)
- Git

### Installation
```bash
# Clone repository
git clone <repository-url>
cd Digimons

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .

# Start Neo4j
docker run -p 7687:7687 -p 7474:7474 -e NEO4J_AUTH=neo4j/password neo4j:latest
```

### Basic Usage
```python
from kgas import KnowledgeGraphAnalysisSystem

# Initialize system
kgas = KnowledgeGraphAnalysisSystem()

# Process documents
results = kgas.process_documents(["paper1.pdf", "paper2.pdf"])

# Query the graph
entities = kgas.query("MATCH (n:Entity) RETURN n LIMIT 10")
```

## Architecture Overview

KGAS implements a sophisticated architecture for academic research:

### Bi-Store Data Architecture
- **Neo4j**: Graph operations, vector similarity search, network analysis
- **SQLite**: Statistical analysis, structured equation modeling, relational operations

### Cross-Modal Analysis
- **Graph Mode**: Network analysis, centrality, community detection
- **Table Mode**: Statistical analysis, regression, SEM
- **Vector Mode**: Semantic similarity, clustering, embeddings

### Theory-Aware Processing
- Automated theory extraction from literature
- Theory-guided entity and relationship extraction
- Domain-specific ontology integration

See [Architecture Documentation](docs/architecture/ARCHITECTURE.md) for detailed design.

## Development Roadmap

See [Roadmap](docs/planning/roadmap.md) for current development status and plans.

## Contributing

This is an academic research project. We welcome contributions in:
- Cross-modal analysis algorithms
- Theory extraction improvements
- Uncertainty quantification methods
- Documentation and examples

See [Contributing Guide](docs/development/contributing/CONTRIBUTING.md) for details.

## License

[Add appropriate license]

## Citation

If you use KGAS in your research, please cite:
```bibtex
@software{kgas2024,
  title={Knowledge Graph Analysis System},
  author={...},
  year={2024},
  url={...}
}
```