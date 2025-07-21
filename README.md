---
status: living
doc-type: readme
governance: doc-governance
---

# KGAS (Knowledge Graph Analysis System)

This repository implements the Knowledge Graph Analysis System (KGAS) described in the dissertation 'Theoretical Foundations for LLM-Generated Ontologies and Analysis of Fringe Discourse.'

## Navigation
- [KGAS Evergreen Documentation](docs/architecture/concepts/kgas-evergreen-documentation.md)
- [Roadmap](docs/planning/roadmap.md)
- [Architecture](docs/architecture/KGAS_ARCHITECTURE_V3.md)
- [Compatibility Matrix](docs/architecture/specifications/compatibility-matrix.md)

## Overview

This is an experimental GraphRAG (Graph-based Retrieval-Augmented Generation) system for research and development purposes. It demonstrates entity extraction, relationship mapping, and graph-based query processing using Neo4j.

## 🎯 Academic Research Tool Status

**This system is designed for local, single-node academic research and experimental GraphRAG concepts.**

### Current Status:
- ✅ **Academic Research Capable**: Suitable for local research and experimentation
- ✅ **Development Testing**: 14 tests covering core research functionality validation
- ✅ **Research Functionality**: Genuine research capabilities without production mocks
- ✅ **Academic Evidence**: Research execution logs and academic validation
- 🔄 **Research Enhancement**: Ongoing development of advanced research capabilities

### Research Capabilities:
- Academic document processing with PDF loading and text chunking
- Experimental knowledge graph construction and analysis
- Research-grade entity extraction using SpaCy NER
- Academic relationship extraction and graph building
- Research multi-hop querying capabilities
- Experimental PageRank analysis for academic validation
- Development-grade error handling for research reliability
- Research logging and academic validation monitoring

### What This System Does:
- Extracts entities from text documents
- Identifies relationships between entities
- Stores data in Neo4j graph database
- Provides basic query interface
- Demonstrates GraphRAG concepts

### Known Research Limitations:
- Package installation requires manual fixes for development setup
- Neo4j shows property warnings during research validation
- Development-grade error handling suitable for academic research
- Manual configuration needed for research environment setup
- No production monitoring (not needed for academic research tool)

## Quick Start

### Prerequisites
- Python 3.8+
- Docker (for Neo4j)
- Basic understanding of GraphRAG concepts

### Installation
```bash
# Clone repository
git clone <repository-url>
cd Digimons

# Install package
pip install -e .

# Verify installation
python examples/verify_package_installation.py
```

### Basic Usage
```bash
# Start Neo4j
docker run -p 7687:7687 -p 7474:7474 --name neo4j -d -e NEO4J_AUTH=none neo4j:latest

# Run example
python examples/minimal_working_example.py
```

**Full roadmap**: docs/planning/roadmap.md

## Development Status

### Working Features:
- ✅ Entity extraction (SpaCy NER)
- ✅ Relationship extraction (pattern matching)  
- ✅ Neo4j integration
- ✅ Basic UI (Streamlit)
- ✅ PipelineOrchestrator architecture

### In Development:
- 🚧 Package installation improvements
- 🚧 Error handling enhancements
- 🚧 Documentation clarity
- 🚧 Testing coverage

### Not Applicable for Academic Research Tool:
- ❌ Production error handling (academic tool uses development-grade handling)
- ❌ Enterprise performance optimization (single-node academic research focus)
- ❌ Security hardening (research environment security adequate)
- ❌ Production scalability features (single-node academic research design)
- ❌ Enterprise monitoring (academic validation monitoring sufficient)
- ❌ Enterprise authentication (research environment authentication adequate)

## Contributing

This is a research project. Contributions welcome for:
- Fixing package installation issues
- Improving documentation clarity
- Adding test coverage
- Enhancing error handling

### Development Workflow
- All changes must pass CI checks (unit, integration, doc-governance)
- Update roadmap.md progress status for feature changes
- Follow the PR template in `.github/pull_request_template.md`
- Ensure documentation claims are verified

### CI/CD Pipeline
- **Unit Tests**: Automated unit test suite
- **Integration Tests**: Full integration testing with Neo4j
- **Documentation Governance**: Verifies documentation claims and consistency

## License

[Add appropriate license for experimental software]

## Support

This is experimental software. For issues:
1. Check the Quick Start section above for setup guidance
2. Review docs/operations/OPERATIONS.md for system status
3. Submit issues for bugs/improvements

**Remember**: This is NOT production software. Use at your own risk for research/learning purposes only.