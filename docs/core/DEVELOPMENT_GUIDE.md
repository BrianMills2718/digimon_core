# Super-Digimon Development Guide

## System Requirements

- **Python**: 3.11 or higher
- **Docker**: 20.10+ with Docker Compose
- **Neo4j**: 5.x (via Docker)
- **Git**: For version control
- **Memory**: Minimum 8GB RAM
- **Storage**: 10GB+ free space

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/BrianMills2718/UKRF_1.git
cd Digimons

# 2. Create Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Create project structure
mkdir -p src/{core,tools,utils}
mkdir -p tests/{unit,integration,e2e}
mkdir -p data scripts

# 4. Start Neo4j database
docker-compose up -d neo4j

# 5. Install dependencies
pip install -r requirements.txt

# 6. Verify Neo4j connection
python -m scripts.test_connection
```

## Environment Setup

### Docker Configuration

Create `docker-compose.yml` in project root:
```yaml
version: '3.8'

services:
  neo4j:
    image: neo4j:5-community
    container_name: super-digimon-neo4j
    ports:
      - "7474:7474"  # HTTP
      - "7687:7687"  # Bolt
    environment:
      - NEO4J_AUTH=neo4j/password
      - NEO4J_PLUGINS=["graph-data-science"]
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs

volumes:
  neo4j_data:
  neo4j_logs:
```

### Python Dependencies

Create `requirements.txt` in project root:
```
# Core dependencies
mcp==0.9.0
neo4j==5.14.0
faiss-cpu==1.7.4
sqlalchemy==2.0.23
pydantic==2.5.0

# NLP tools
spacy==3.7.2
nltk==3.8.1
transformers==4.35.0

# Utilities
python-dotenv==1.0.0
click==8.1.7
rich==13.7.0

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-mock==3.12.0
```

### Environment Variables

Create `.env` in project root:
```bash
# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# FAISS Configuration
FAISS_INDEX_PATH=./data/faiss_index

# SQLite Configuration
SQLITE_DB_PATH=./data/metadata.db

# MCP Server Configuration
MCP_SERVER_PORT=3333
```

## Development Workflow

### 1. Daily Setup
```bash
# Start services
docker-compose up -d

# Activate virtual environment
source venv/bin/activate

# Check service health
docker-compose ps
python -m scripts.health_check
```

### 2. Project Structure
```
Digimons/
├── src/
│   ├── core/           # Core functionality
│   ├── tools/          # Tool implementations (T01-T106)
│   │   ├── phase1/     # Ingestion tools
│   │   ├── phase2/     # Processing tools
│   │   └── ...
│   └── mcp_server.py   # MCP server
├── tests/              # Test files
├── data/               # Local data storage
├── scripts/            # Utility scripts
└── config/             # Configuration files
```

### 3. Development Cycle
1. Pick a tool to implement (start with T01)
2. Write tests first (TDD approach)
3. Implement the tool
4. Test with MCP server
5. Document any changes
6. Commit with descriptive message

## Implementing Your First Tool

### Example: T01 - Text Document Loader

1. **Create tool file** `src/tools/phase1/t01_text_loader.py`:
```python
from pathlib import Path
from typing import Dict, Any
from pydantic import BaseModel, Field

class TextLoaderInput(BaseModel):
    file_path: str = Field(description="Path to text file")
    encoding: str = Field(default="utf-8", description="Text encoding")
    chunk_size: int = Field(default=1000, description="Size of text chunks")

class TextLoaderOutput(BaseModel):
    status: str
    chunks: list[str]
    metadata: Dict[str, Any]

def load_text_document(params: TextLoaderInput) -> TextLoaderOutput:
    """T01: Load text document and split into chunks."""
    try:
        path = Path(params.file_path)
        
        # Read file
        with open(path, 'r', encoding=params.encoding) as f:
            content = f.read()
        
        # Split into chunks
        chunks = [
            content[i:i + params.chunk_size] 
            for i in range(0, len(content), params.chunk_size)
        ]
        
        return TextLoaderOutput(
            status="success",
            chunks=chunks,
            metadata={
                "file_name": path.name,
                "file_size": path.stat().st_size,
                "chunk_count": len(chunks),
                "encoding": params.encoding
            }
        )
    except Exception as e:
        return TextLoaderOutput(
            status="error",
            chunks=[],
            metadata={"error": str(e)}
        )
```

2. **Add to MCP server** `src/mcp_server.py`:
```python
from mcp.server import Server
from mcp.server.stdio import stdio_server
from src.tools.phase1.t01_text_loader import load_text_document, TextLoaderInput

# Create server
server = Server("super-digimon")

# Register tools
@server.tool()
async def t01_text_document_loader(file_path: str, encoding: str = "utf-8", chunk_size: int = 1000) -> dict:
    """Load text documents from local filesystem."""
    params = TextLoaderInput(
        file_path=file_path,
        encoding=encoding,
        chunk_size=chunk_size
    )
    result = load_text_document(params)
    return result.model_dump()

# Run server
async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

3. **Test the tool**:
```python
# tests/unit/test_t01_text_loader.py
import pytest
from src.tools.phase1.t01_text_loader import load_text_document, TextLoaderInput

def test_load_text_document(tmp_path):
    # Create test file
    test_file = tmp_path / "test.txt"
    test_file.write_text("Hello World! " * 100)
    
    # Test loading
    params = TextLoaderInput(
        file_path=str(test_file),
        chunk_size=50
    )
    result = load_text_document(params)
    
    assert result.status == "success"
    assert len(result.chunks) > 1
    assert result.metadata["file_name"] == "test.txt"
```

## Testing Approach

### Unit Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_t01_text_loader.py

# Run with coverage
pytest --cov=src tests/
```

### Integration Tests
```bash
# Test Neo4j connection
python -m pytest tests/integration/test_neo4j.py

# Test MCP server
python -m pytest tests/integration/test_mcp_server.py
```

### End-to-End Tests
```bash
# Test complete workflow
python -m pytest tests/e2e/test_ingestion_pipeline.py -v
```

## Common Commands

### Docker Management
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f neo4j

# Stop services
docker-compose down

# Clean volumes
docker-compose down -v
```

### Neo4j Queries
```bash
# Access Neo4j browser
open http://localhost:7474

# Clear database (Cypher)
MATCH (n) DETACH DELETE n

# Count nodes
MATCH (n) RETURN count(n)
```

### Development Commands
```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type check
mypy src/

# Run MCP server
python -m src.mcp_server
```

## Troubleshooting

### Neo4j Connection Issues
```bash
# Check if Neo4j is running
docker-compose ps

# Test connection
python -c "from neo4j import GraphDatabase; driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'password')); driver.verify_connectivity()"

# Check logs
docker-compose logs neo4j
```

### Python Import Errors
```bash
# Ensure virtual environment is activated
which python  # Should show venv path

# Reinstall dependencies
pip install -r requirements.txt --upgrade

# Add project to Python path
export PYTHONPATH="${PYTHONPATH}:${PWD}"
```

### MCP Server Issues
```bash
# Test MCP server directly
mcp dev src/mcp_server.py

# Check server logs
python -m src.mcp_server 2>&1 | tee mcp_server.log

# Validate tool registration
mcp list-tools src/mcp_server.py
```

## Implementation Roadmap

### Phase 0: Infrastructure (Week 1)
- [ ] Set up development environment
- [ ] Configure Docker services
- [ ] Create basic MCP server
- [ ] Implement logging system
- [ ] Set up testing framework

### Phase 1: Basic Pipeline (Weeks 2-3)
- [ ] Implement T01-T12 (Ingestion tools)
- [ ] Create basic storage managers (T76-T77)
- [ ] Build simple test datasets
- [ ] Verify end-to-end data flow

### Phase 2: Processing (Weeks 4-5)
- [ ] Implement T13-T30 (Processing tools)
- [ ] Add NLP model integration
- [ ] Create processing pipelines
- [ ] Performance optimization

### Phase 3: Graph Construction (Weeks 6-7)
- [ ] Implement T31-T48 (Construction tools)
- [ ] Neo4j integration
- [ ] FAISS index creation
- [ ] Graph validation

### Phase 4: Core Retrieval (Weeks 8-10)
- [ ] Implement T49-T67 (GraphRAG operators)
- [ ] Query optimization
- [ ] Result ranking
- [ ] Performance testing

### Phase 5: Advanced Features (Weeks 11-12)
- [ ] Implement T68-T106 (Analysis & Interface)
- [ ] Natural language interface
- [ ] Monitoring dashboard
- [ ] System optimization

## Best Practices

### Code Organization
- One file per tool
- Clear input/output models
- Comprehensive error handling
- Detailed logging

### Documentation
- Docstrings for all functions
- Type hints everywhere
- Update specs if behavior changes
- Example usage in tests

### Version Control
- Feature branches for new tools
- Descriptive commit messages
- PR reviews before merging
- Tag releases

## Resources

- [MCP Documentation](https://modelcontextprotocol.io/docs)
- [Neo4j Python Driver](https://neo4j.com/docs/python-manual/current/)
- [FAISS Documentation](https://github.com/facebookresearch/faiss/wiki)
- [Project Repository](https://github.com/BrianMills2718/UKRF_1)