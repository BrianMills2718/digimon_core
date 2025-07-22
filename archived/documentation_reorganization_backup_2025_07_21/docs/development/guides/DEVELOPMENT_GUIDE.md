---
status: living
---

# Development Guide

## System Requirements

- **Python**: 3.11 or higher
- **Docker**: 20.10+ with Docker Compose
- **Neo4j**: 5.x (via Docker)
- **Git**: For version control
- **Memory**: Minimum 8GB RAM
- **Storage**: 10GB+ free space

## Quick Start

```bash
# 1. System is already set up and working
cd Digimons

# 2. Install as editable package (already working)
pip install -e .

# 3. Test current functionality
python examples/minimal_working_example.py

# 4. Launch UI
python ui/launch_ui.py

# 5. OPTIONAL: Set up Neo4j for full functionality
# See CLAUDE.md Priority 1 for detailed Neo4j setup instructions
docker run -p 7687:7687 -p 7474:7474 --name neo4j -d -e NEO4J_AUTH=none neo4j:latest
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
fastapi==0.104.1
uvicorn==0.24.0
neo4j==5.14.0
redis==5.0.1
pydantic==2.5.2
python-dotenv==1.0.0
requests==2.31.0
tiktoken==0.5.1
pyyaml==6.0.1

# NLP tools
spacy==3.7.2
nltk==3.8.1
transformers==4.35.0

# Utilities
click==8.1.7
rich==13.7.0

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-docker==2.0.1
testcontainers==3.7.1
```

### Environment Variables

Create `.env` in project root:
```bash
# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379

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

## Testing Approach - Real Databases Only

### Philosophy
- **NO MOCKS**: All tests use real databases (Neo4j, SQLite, FAISS)
- **NO SIMULATIONS**: Actual data flows through actual systems
- **REALISTIC AT EVERY STEP**: If it passes tests, it works in production

### Test Environment Setup
```bash
# Start test databases (separate from dev)
docker-compose -f docker-compose.test.yml up -d

# Verify test services
docker-compose -f docker-compose.test.yml ps

# Run tests
pytest

# Cleanup after tests
docker-compose -f docker-compose.test.yml down -v
```

### Test Database Configuration
Create `docker-compose.test.yml`:
```yaml
version: '3.8'
services:
  neo4j-test:
    image: neo4j:5-community
    ports:
      - "7688:7687"  # Different port for test
      - "7475:7474"
    environment:
      - NEO4J_AUTH=neo4j/testpassword
      - NEO4J_ACCEPT_LICENSE_AGREEMENT=yes
    volumes:
      - neo4j_test_data:/data
      
volumes:
  neo4j_test_data:
```

### Writing Realistic Tests
```python
# tests/conftest.py
import pytest
from neo4j import GraphDatabase
from testcontainers.neo4j import Neo4jContainer

@pytest.fixture(scope="session")
def neo4j_test():
    """Provide real Neo4j instance for tests."""
    with Neo4jContainer("neo4j:5-community") as neo4j:
        yield neo4j.get_connection_url()

@pytest.fixture
def clean_neo4j(neo4j_test):
    """Ensure clean database for each test."""
    driver = GraphDatabase.driver(neo4j_test, auth=("neo4j", "password"))
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
    yield driver
    driver.close()

# tests/test_real_workflow.py
def test_entity_extraction_with_real_neo4j(clean_neo4j):
    """Test entity extraction with actual Neo4j database."""
    # Load real PDF
    doc = load_pdf("test_data/sample.pdf")
    
    # Extract entities using real NLP
    entities = extract_entities(doc.text)
    
    # Store in real Neo4j
    store_entities(clean_neo4j, entities)
    
    # Query from real database
    result = clean_neo4j.session().run(
        "MATCH (e:Entity) RETURN count(e) as count"
    ).single()
    
    assert result["count"] == len(entities)
```

### Test Data Management
```bash
test_data/
├── fixtures/
│   ├── small_graph.json      # Known graph structures
│   ├── sample_entities.csv   # Real entity data
│   └── test_documents.pdf    # Real documents
├── snapshots/
│   ├── expected_graph.json   # Expected results
│   └── pagerank_scores.json  # Known good outputs
└── generators/
    └── create_test_data.py   # Generate consistent test data
```

### Categories of Tests

#### 1. Component Tests (with real databases)
```python
def test_pdf_loader_with_real_file():
    """Test PDF loading with actual PDF file."""
    result = load_pdf("test_data/real_document.pdf")
    assert len(result.text) > 0
    assert result.confidence > 0.8
```

#### 2. Integration Tests (real data flow)
```python
def test_pdf_to_graph_pipeline(clean_neo4j, real_faiss):
    """Test complete pipeline with real components."""
    # Real PDF → Real NLP → Real Neo4j → Real FAISS
    pdf = load_pdf("test_data/sample.pdf")
    chunks = chunk_document(pdf)
    entities = extract_entities(chunks)
    store_in_neo4j(clean_neo4j, entities)
    create_embeddings(real_faiss, entities)
    
    # Verify with actual queries
    assert neo4j_has_entities(clean_neo4j)
    assert faiss_has_vectors(real_faiss)
```

#### 3. End-to-End Tests (complete workflows)
```python
def test_question_answering_workflow(all_services):
    """Test complete Q&A with all real services."""
    # Load real document
    load_document("test_data/research_paper.pdf")
    
    # Ask real question
    answer = ask_question("What are the main findings?")
    
    # Verify real answer
    assert "findings" in answer.text.lower()
    assert answer.confidence > 0.7
    assert len(answer.sources) > 0
```

### Performance Monitoring (Not Hard Limits)
```python
import time
import logging

def test_performance_trend_monitoring():
    """Monitor performance trends, not absolute thresholds."""
    start_time = time.time()
    result = process_test_documents()
    elapsed = time.time() - start_time
    
    # Log for trend analysis, don't fail on absolute time
    logging.info(f"Document processing took {elapsed:.2f}s")
    
    # Only fail on obvious regressions
    assert elapsed < 300, f"Processing too slow: {elapsed}s (likely regression)"
    assert result.success, "Processing failed"

def test_core_service_performance():
    """Monitor core services for bottlenecks."""
    identity_service = IdentityService()
    
    start = time.time()
    for i in range(100):  # Reasonable test size
        identity_service.resolve_mention(f"entity_{i}", "test_context")
    elapsed = time.time() - start
    
    # Log performance, identify trends
    logging.info(f"Identity service: {elapsed/100*1000:.1f}ms per call")
    
    # Only hard fail on extreme slowness
    assert elapsed < 10, f"Identity service too slow: {elapsed}s for 100 calls"
```

## Implementation Risk Mitigation

### Preventing Specification Drift

#### Simple Tool Validation
```python
# tools/base_tool.py
import json
from jsonschema import validate

class BaseTool:
    def __init__(self, tool_id: str):
        self.tool_id = tool_id
        self.schema = self._load_schema()
    
    def _load_schema(self):
        """Load simple JSON schema for tool."""
        with open(f"schemas/{self.tool_id}.json") as f:
            return json.load(f)
    
    def validate_input(self, data):
        """Basic input validation."""
        validate(data, self.schema["input"])
    
    def validate_output(self, data):
        """Basic output validation."""
        validate(data, self.schema["output"])
```

#### Tool Schema Example
```json
# schemas/T01.json
{
  "tool_id": "T01",
  "input": {
    "type": "object",
    "properties": {
      "file_path": {"type": "string"},
      "encoding": {"type": "string", "default": "utf-8"}
    },
    "required": ["file_path"]
  },
  "output": {
    "type": "object",
    "properties": {
      "document_id": {"type": "string"},
      "confidence": {"type": "number", "minimum": 0, "maximum": 1}
    },
    "required": ["document_id", "confidence"]
  }
}
```

### Performance Optimization Strategy

#### Core Services Design Principles
```python
# Simple, fast core services
class IdentityService:
    def __init__(self):
        # Simple in-memory cache for prototype
        self.cache = {}
        self.max_cache_size = 1000
    
    def resolve_mention(self, surface_text: str, context: str) -> str:
        cache_key = f"{surface_text}:{hash(context)}"
        
        # Fast cache lookup
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Simple resolution logic for prototype
        entity_id = self._simple_resolution(surface_text)
        
        # Basic cache management
        if len(self.cache) > self.max_cache_size:
            self.cache.clear()  # Simple eviction
        
        self.cache[cache_key] = entity_id
        return entity_id
    
    def _simple_resolution(self, surface_text: str) -> str:
        # Start with simple exact matching
        # Optimize later based on actual performance data
        return f"entity_{surface_text.lower().replace(' ', '_')}"
```

#### Performance Monitoring (Not Enforcement)
```python
# utils/performance_monitor.py
import time
import logging
from collections import defaultdict

class SimplePerformanceMonitor:
    def __init__(self):
        self.timings = defaultdict(list)
    
    def time_operation(self, operation_name: str):
        """Context manager for timing operations."""
        return self.Timer(operation_name, self.timings)
    
    class Timer:
        def __init__(self, name, timings_dict):
            self.name = name
            self.timings = timings_dict
        
        def __enter__(self):
            self.start = time.time()
            return self
        
        def __exit__(self, *args):
            elapsed = time.time() - self.start
            self.timings[self.name].append(elapsed)
            
            # Log slow operations
            if elapsed > 1.0:
                logging.warning(f"Slow operation {self.name}: {elapsed:.2f}s")
    
    def report(self):
        """Generate simple performance report."""
        for operation, times in self.timings.items():
            avg_time = sum(times) / len(times)
            max_time = max(times)
            logging.info(f"{operation}: avg={avg_time:.3f}s, max={max_time:.3f}s, calls={len(times)}")

# Usage in tools
monitor = SimplePerformanceMonitor()

def some_tool_function():
    with monitor.time_operation("entity_extraction"):
        # Tool implementation
        pass
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