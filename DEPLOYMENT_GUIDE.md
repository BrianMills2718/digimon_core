# Super-Digimon Deployment Guide

**Last Updated**: January 6, 2025  
**Status**: Development Deployment (No production deployment yet)

## Overview

This guide explains how to set up a development environment for Super-Digimon. Since the system is not yet implemented, this guide focuses on setting up the infrastructure needed for development.

## Prerequisites

- Python 3.11 or higher
- Docker and Docker Compose
- 8GB RAM minimum (for Neo4j with GDS plugin)
- 10GB free disk space

## Development Environment Setup

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd Digimons
```

### Step 2: Set Up Neo4j

Create a `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  neo4j:
    image: neo4j:5-enterprise
    container_name: super-digimon-neo4j
    ports:
      - "7474:7474"  # HTTP
      - "7687:7687"  # Bolt
    environment:
      - NEO4J_AUTH=neo4j/your-password-here
      - NEO4J_ACCEPT_LICENSE_AGREEMENT=yes
      - NEO4J_dbms_memory_heap_initial__size=2G
      - NEO4J_dbms_memory_heap_max__size=4G
      - NEO4J_dbms_memory_pagecache_size=1G
      - NEO4JLABS_PLUGINS=["apoc", "graph-data-science"]
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs
      - neo4j_import:/var/lib/neo4j/import
      - neo4j_plugins:/plugins

volumes:
  neo4j_data:
  neo4j_logs:
  neo4j_import:
  neo4j_plugins:
```

Start Neo4j:

```bash
docker-compose up -d neo4j
```

Verify Neo4j is running:
```bash
# Check logs
docker-compose logs neo4j

# Open browser to http://localhost:7474
# Login with neo4j / your-password-here
```

### Step 3: Python Environment

Create virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

If `requirements.txt` doesn't exist yet, create it:

```txt
neo4j==5.14.0
numpy==1.24.3
scikit-learn==1.3.0
```

### Step 4: Test Neo4j Connection

Create `test_connection.py`:

```python
from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
user = "neo4j"
password = "your-password-here"

driver = GraphDatabase.driver(uri, auth=(user, password))

def test_connection():
    with driver.session() as session:
        result = session.run("RETURN 'Connection successful!' as message")
        print(result.single()["message"])

if __name__ == "__main__":
    test_connection()
    driver.close()
```

Run test:

```bash
python test_connection.py
```

### Step 5: Load Test Data

Load the Celestial Council dataset:

```bash
cd test_data/celestial_council/small
python ../generate_small_dataset.py  # If needed

# Import to Neo4j (when importer is built)
```

## Project Structure Setup

Create the following directory structure:

```
Digimons/
├── super_digimon/          # Main package
│   ├── __init__.py
│   ├── tools/              # Tool implementations
│   │   ├── __init__.py
│   │   ├── t01_document_loader.py
│   │   ├── t02_text_chunker.py
│   │   └── ...
│   ├── mcp_server.py       # MCP server
│   └── config.py           # Configuration
├── tests/                  # Test files
│   ├── __init__.py
│   ├── test_tools.py
│   └── test_integration.py
├── docker-compose.yml      # Docker services
├── requirements.txt        # Python dependencies
├── README.md              # Project documentation
└── STATUS.md              # Current status
```

## Configuration

Create `super_digimon/config.py`:

```python
import os
from dataclasses import dataclass

@dataclass
class Config:
    # Neo4j settings
    neo4j_uri: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user: str = os.getenv("NEO4J_USER", "neo4j")
    neo4j_password: str = os.getenv("NEO4J_PASSWORD", "your-password-here")
    
    # Tool settings
    chunk_size: int = 1000
    chunk_overlap: int = 200
    
    # Model settings
    embedding_model: str = "text-embedding-ada-002"
    
    # Paths
    data_dir: str = "./data"
    cache_dir: str = "./cache"

config = Config()
```

## Environment Variables

Create `.env` file (don't commit this!):

```bash
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password-here
OPENAI_API_KEY=your-key-here  # If using OpenAI embeddings
```

Add to `.gitignore`:
```
.env
venv/
__pycache__/
*.pyc
.DS_Store
data/
cache/
```

## Development Workflow

1. **Start Services**:
   ```bash
   docker-compose up -d
   ```

2. **Activate Python Environment**:
   ```bash
   source venv/bin/activate
   ```

3. **Run Tests**:
   ```bash
   pytest tests/
   ```

4. **Start MCP Server** (when implemented):
   ```bash
   python -m super_digimon.mcp_server
   ```

## Troubleshooting

### Neo4j Won't Start
- Check Docker memory settings (needs at least 4GB)
- Check ports 7474 and 7687 are free
- Check logs: `docker-compose logs neo4j`

### Connection Refused
- Ensure Neo4j is fully started (can take 30-60 seconds)
- Check firewall settings
- Verify credentials match

### Out of Memory
- Reduce Neo4j heap size in docker-compose.yml
- Close other applications
- Increase Docker memory allocation

## Next Steps

Once the development environment is set up:

1. Implement first tool (T01_DocumentLoader)
2. Create MCP server wrapper
3. Test with Claude Code
4. Iterate on remaining tools

## Production Deployment (Future)

Production deployment will require:
- Security hardening
- Performance optimization  
- Monitoring and logging
- Backup strategies
- Load balancing

These will be documented when the system is ready for production use.

## Resources

- [Neo4j Docker Documentation](https://neo4j.com/docs/operations-manual/current/docker/)
- [MCP Specification](https://modelcontextprotocol.io/docs)
- [Python Best Practices](https://docs.python-guide.org/)

Remember: This is a development setup. Do not use these configurations in production!