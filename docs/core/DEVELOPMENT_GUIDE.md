# Super-Digimon Development Guide

**Last Updated**: January 13, 2025  
**Purpose**: Practical guide for developers working on Super-Digimon

## Overview

Super-Digimon is a GraphRAG system that enables natural language querying of graph data. This guide consolidates all development-related information into one practical resource.

## System Requirements

- **Python**: 3.11 or higher
- **Docker**: Latest stable version with Docker Compose
- **RAM**: 8GB minimum (Neo4j requires significant memory)
- **Disk**: 10GB free space
- **OS**: Linux, macOS, or Windows with WSL2

## Quick Start

### 1. Clone and Setup

```bash
# Clone repository
git clone https://github.com/BrianMills2718/UKRF_1.git
cd UKRF_1

# Create Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Start Neo4j Database

```bash
# Navigate to tools directory
cd tools/cc_automator

# Start Neo4j via Docker
docker-compose up -d neo4j

# Verify Neo4j is running
docker-compose ps neo4j

# Check logs if needed
docker-compose logs neo4j
```

### 3. Install Dependencies

```bash
# Install current test dependencies
pip install -r requirements.txt

# Test Neo4j connection
pytest test_files/test_simple_neo4j.py -v
```

### 4. Verify Setup

```bash
# Open Neo4j Browser
# Navigate to: http://localhost:7474
# Login: neo4j / password

# Run connection test
python test_files/test_simple_neo4j.py
```

## Environment Setup

### Docker Configuration

The project uses Docker for database services while running Python code locally for faster development:

```yaml
# docker-compose.yml (in tools/cc_automator/)
version: '3.8'

services:
  neo4j:
    image: neo4j:5-community
    container_name: super-digimon-neo4j
    ports:
      - "7474:7474"  # HTTP interface
      - "7687:7687"  # Bolt protocol
    environment:
      - NEO4J_AUTH=neo4j/password
      - NEO4J_PLUGINS=["graph-data-science"]
      - NEO4J_dbms_memory_heap_initial__size=512m
      - NEO4J_dbms_memory_heap_max__size=2G
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs
```

### Environment Variables

Create a `.env` file in `tools/cc_automator/`:

```bash
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
NEO4J_DATABASE=neo4j
COMPOSE_PROJECT_NAME=super-digimon
```

## Development Workflow

### Daily Development Setup

```bash
# 1. Start database services
cd tools/cc_automator
docker-compose up -d neo4j

# 2. Activate Python environment
source venv/bin/activate  # From project root

# 3. Verify everything is working
pytest tools/cc_automator/test_files/test_simple_neo4j.py -v
```

### Project Structure

```
super-digimon/
├── docs/                       # Documentation
│   ├── specifications/        # 106 tool specifications (authoritative)
│   ├── decisions/            # Architectural decisions
│   └── reference/            # Additional guides
├── tools/cc_automator/        # Current development/testing tool
│   ├── test_files/           # Test suite
│   ├── docker-compose.yml    # Docker services
│   └── requirements.txt      # Python dependencies
├── test_data/                 # Sample datasets
│   └── celestial_council/    # Test dataset
├── config/                    # Configuration examples
└── super_digimon/            # Future main package location
    ├── tools/                # Tool implementations (T01-T106)
    ├── mcp_server.py        # MCP server
    └── config.py            # Configuration
```

## Implementing Your First Tool

### Step 1: Understand the Architecture

Read these key documents in order:
1. `docs/specifications/SUPER_DIGIMON_COMPLETE_TOOL_SPECIFICATIONS.md` - All 106 tools
2. `docs/specifications/TOOL_ARCHITECTURE_SUMMARY.md` - Tool organization
3. `docs/decisions/CANONICAL_DECISIONS_2025.md` - Architectural decisions

### Step 2: Create Basic MCP Server

```python
#!/usr/bin/env python3
"""
Basic MCP server for Super-Digimon tool
"""

import asyncio
import json
import sys
from typing import Any, Dict

class SuperDigimonMCPServer:
    def __init__(self):
        self.tools = {
            "T01_LoadDocument": {
                "description": "Load various document formats into the system",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Document path"},
                        "format": {"type": "string", "enum": ["txt", "pdf", "html", "md"]}
                    },
                    "required": ["path", "format"]
                }
            }
        }
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        method = request.get("method")
        
        if method == "tools/list":
            return {"tools": [{"name": name, **info} for name, info in self.tools.items()]}
        
        elif method == "tools/call":
            tool_name = request["params"]["name"]
            arguments = request["params"]["arguments"]
            
            if tool_name == "T01_LoadDocument":
                # Implement actual document loading logic here
                result = f"Loaded {arguments['format']} document from {arguments['path']}"
                return {"content": [{"type": "text", "text": result}]}
        
        return {"error": {"code": -32601, "message": "Method not found"}}
    
    async def run(self):
        while True:
            line = sys.stdin.readline()
            if not line:
                break
            
            try:
                request = json.loads(line)
                response = await self.handle_request(request)
                response["jsonrpc"] = "2.0"
                response["id"] = request.get("id")
                
                print(json.dumps(response))
                sys.stdout.flush()
            except Exception as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {"code": -32603, "message": str(e)}
                }
                print(json.dumps(error_response))
                sys.stdout.flush()

if __name__ == "__main__":
    server = SuperDigimonMCPServer()
    asyncio.run(server.run())
```

### Step 3: Test Your Tool

```python
# test_tool.py
import subprocess
import json

def test_mcp_tool():
    # Start the MCP server
    process = subprocess.Popen(
        ['python', 'mcp_server.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True
    )
    
    # Test tools/list
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list"
    }
    
    process.stdin.write(json.dumps(request) + '\n')
    process.stdin.flush()
    
    response = json.loads(process.stdout.readline())
    print("Tools available:", response)
    
    # Clean up
    process.terminate()

if __name__ == "__main__":
    test_mcp_tool()
```

## Testing Approach

### Test Categories

1. **Unit Tests**: Test individual functions with mocks
   ```bash
   pytest tests/unit/ -v
   ```

2. **Integration Tests**: Test tool interactions
   ```bash
   pytest tests/integration/ -v
   ```

3. **E2E Tests**: Test complete workflows with real databases
   ```bash
   pytest tests/e2e/ -v
   ```

### Writing Tests

```python
# test_document_loader.py
import pytest
from super_digimon.tools import T01_DocumentLoader

def test_load_text_document():
    loader = T01_DocumentLoader()
    result = loader.load("test.txt", format="txt")
    assert result is not None
    assert "content" in result

@pytest.mark.integration
def test_load_document_to_neo4j():
    # Test with real Neo4j connection
    loader = T01_DocumentLoader(neo4j_uri="bolt://localhost:7687")
    result = loader.load_and_store("test.txt")
    assert result["status"] == "success"
```

## Common Commands

### Docker Management

```bash
# Start services
docker-compose up -d neo4j

# Stop services
docker-compose down

# Reset Neo4j (delete all data)
docker-compose down -v
docker-compose up -d neo4j

# View logs
docker-compose logs -f neo4j

# Execute Cypher in Neo4j
docker exec -it super-digimon-neo4j cypher-shell -u neo4j -p password
```

### Python Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests
pytest -v

# Run specific test file
pytest test_files/test_neo4j_integration.py -v

# Run with coverage
pytest --cov=super_digimon tests/

# Format code
black .

# Check types
mypy super_digimon/
```

### MCP Development

```bash
# Test MCP server manually
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python mcp_server.py

# Run MCP server
python -m super_digimon.mcp_server

# Configure Claude Code
# Add to Claude Code's MCP configuration
```

## Troubleshooting

### Neo4j Issues

**Problem**: Neo4j won't start
```bash
# Check if port is in use
lsof -i :7687
lsof -i :7474

# Check Docker logs
docker-compose logs neo4j

# Reset and restart
docker-compose down -v
docker-compose up -d neo4j
```

**Problem**: Connection refused
```bash
# Wait for Neo4j to fully start (can take 30-60 seconds)
# Check status
docker-compose ps neo4j

# Test connection
python -c "from neo4j import GraphDatabase; driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'password')); driver.verify_connectivity()"
```

### Python Issues

**Problem**: Import errors
```bash
# Ensure virtual environment is activated
which python  # Should show venv path

# Reinstall dependencies
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

**Problem**: Tests failing
```bash
# Run in verbose mode
pytest -vv test_file.py

# Check test database is clean
docker-compose down -v
docker-compose up -d neo4j
```

### Docker Issues

**Problem**: Out of memory
```bash
# Increase Docker Desktop memory allocation
# Settings -> Resources -> Memory -> 8GB recommended

# Or reduce Neo4j heap size in docker-compose.yml
NEO4J_dbms_memory_heap_max__size=1G
```

## Implementation Roadmap

Based on the 106 tool specification:

### Phase 0: Infrastructure Setup (Current)
- [ ] Create MCP server framework
- [ ] Set up database connections
- [ ] Implement tool registry system
- [ ] Create basic tool template

### Phase 1: Ingestion Tools (T01-T12)
- [ ] T01_DocumentLoader
- [ ] T02_TextChunker
- [ ] T03_PDFExtractor
- [ ] Continue through T12...

### Phase 2: Processing Tools (T13-T30)
- [ ] T13_TextCleaner
- [ ] T14_SentenceSplitter
- [ ] Continue through T30...

### Phase 3: Construction Tools (T31-T48)
- [ ] T31_GraphBuilder
- [ ] T32_EntityLinker
- [ ] Continue through T48...

### Phase 4: Core GraphRAG (T49-T67)
- [ ] Implement JayLZhou operators
- [ ] Core retrieval functionality

### Phase 5-7: Advanced Features (T68-T106)
- [ ] Analysis tools
- [ ] Interface tools
- [ ] Monitoring and export

## Best Practices

### Code Organization
- One tool per file in `super_digimon/tools/`
- Follow naming convention: `t01_document_loader.py`
- Include comprehensive docstrings
- Add type hints for all functions

### Testing
- Write tests before implementation (TDD)
- Mock external dependencies in unit tests
- Use real connections only in integration tests
- Maintain test coverage above 80%

### Documentation
- Update tool specifications as you implement
- Document any deviations from spec
- Add examples for each tool
- Keep README files current

### Version Control
- Make atomic commits (one logical change)
- Write clear commit messages
- Create feature branches for new tools
- Run tests before pushing

## Resources

### Essential Documentation
- [Tool Specifications](docs/specifications/SUPER_DIGIMON_COMPLETE_TOOL_SPECIFICATIONS.md)
- [Architecture Decisions](docs/decisions/CANONICAL_DECISIONS_2025.md)
- [JayLZhou GraphRAG](https://github.com/JayLZhou/GraphRAG)

### External Resources
- [Neo4j Python Driver](https://neo4j.com/docs/python-manual/current/)
- [MCP Protocol](https://modelcontextprotocol.io/)
- [Docker Documentation](https://docs.docker.com/)
- [pytest Documentation](https://docs.pytest.org/)

## Getting Help

1. **Check existing tests**: Look in `tools/cc_automator/test_files/`
2. **Review specifications**: Ensure you understand the tool requirements
3. **Examine Docker logs**: `docker-compose logs neo4j`
4. **Verify environment**: Ensure all services are running

Remember: This is a prototype system. Focus on functionality over optimization. Build iteratively and test frequently.

---

**Next Steps**: 
1. Complete environment setup
2. Review tool specifications
3. Implement your first tool (T01_DocumentLoader)
4. Create tests for your implementation
5. Submit for review