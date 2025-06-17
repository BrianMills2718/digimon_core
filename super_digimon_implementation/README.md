# Super-Digimon GraphRAG System

A comprehensive GraphRAG (Graph Retrieval-Augmented Generation) system with 121 specialized tools for intelligent graph analysis through natural language queries.

## Quick Start

```bash
# Run the complete system
python main.py

# Test with sample document
python main.py --input test_data/sample.pdf --query "What are the main findings?"

# Start MCP server
python main.py --server

# Run specific analysis
python main.py --analysis pagerank --entities "entity1,entity2"
```

## Architecture

- **121 Tools** across 8 phases (Ingestion → Processing → Construction → Retrieval → Analysis → Storage → Interface → Core Services)
- **Triple Database**: Neo4j (graphs) + SQLite (metadata) + FAISS (vectors)
- **MCP Protocol**: Model Context Protocol for tool orchestration
- **Quality Tracking**: Confidence propagation through all operations
- **Reference System**: Universal cross-database references

## Key Features

- Complete PDF → Knowledge Graph → Analysis → Natural Language Answer workflow
- Three-level identity system (Surface → Mention → Entity)
- Format-agnostic processing (Graph ↔ Table ↔ Vector)
- Comprehensive provenance and quality tracking
- Domain-adaptive entity resolution
- Real-time performance monitoring

## Implementation

This system is implemented using CC_AUTOMATOR4 following comprehensive specifications in `../docs/core/` with complete database integration planning and 121-tool architecture.