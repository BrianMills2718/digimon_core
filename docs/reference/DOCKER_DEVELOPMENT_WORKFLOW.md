# Super-Digimon Docker Development Workflow

## Overview

Our Docker approach balances development flexibility with production readiness. We use Docker primarily for **services** (Neo4j, databases) while running the Python/TypeScript code locally during development for faster iteration.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Host Machine                       │
│                                                      │
│  ┌─────────────────┐     ┌──────────────────────┐  │
│  │  Claude Code    │     │  Python Environment  │  │
│  │  (MCP Client)   │────▶│  - GraphRAG Server   │  │
│  └─────────────────┘     │  - MCP Servers       │  │
│           │              └──────────────────────┘  │
│           │                                         │
│           ▼                                         │
│  ┌─────────────────────────────────────────────┐  │
│  │            Docker Containers                  │  │
│  │                                               │  │
│  │  ┌─────────────┐    ┌──────────────────┐   │  │
│  │  │   Neo4j     │    │  Vector Store    │   │  │
│  │  │  Database   │    │   (Future)       │   │  │
│  │  └─────────────┘    └──────────────────┘   │  │
│  └─────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

## Development Workflow

### 1. Initial Setup

```bash
# Clone repository
git clone https://github.com/yourusername/super-digimon.git
cd super-digimon

# Create Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start Docker services
docker-compose up -d
```

### 2. Docker Compose Configuration

```yaml
# docker-compose.yml
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
      - NEO4J_dbms_memory_heap_initial__size=512m
      - NEO4J_dbms_memory_heap_max__size=2G
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs
      - neo4j_import:/var/lib/neo4j/import
      - neo4j_plugins:/plugins
    healthcheck:
      test: ["CMD", "neo4j", "status"]
      interval: 10s
      timeout: 10s
      retries: 10

  # Future: Qdrant or Weaviate for vector storage
  # vector-db:
  #   image: qdrant/qdrant
  #   ports:
  #     - "6333:6333"
  #   volumes:
  #     - qdrant_data:/qdrant/storage

volumes:
  neo4j_data:
  neo4j_logs:
  neo4j_import:
  neo4j_plugins:
  # qdrant_data:
```

### 3. Development Scripts

```bash
# scripts/dev.sh
#!/bin/bash
set -e

# Check Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Docker is not running. Please start Docker Desktop."
    exit 1
fi

# Start services
echo "Starting Neo4j..."
docker-compose up -d neo4j

# Wait for Neo4j to be ready
echo "Waiting for Neo4j to be ready..."
until docker exec super-digimon-neo4j neo4j status > /dev/null 2>&1; do
    sleep 2
done

# Initialize Neo4j schema
echo "Initializing Neo4j schema..."
python scripts/init_neo4j.py

# Create data directories
mkdir -p data/{indices,visualizations,cache}

# Initialize SQLite
if [ ! -f "data/graphrag.db" ]; then
    echo "Initializing SQLite database..."
    sqlite3 data/graphrag.db < schema/init_sqlite.sql
fi

echo "Development environment ready!"
echo ""
echo "Neo4j Browser: http://localhost:7474 (neo4j/password)"
echo "Neo4j Bolt:   bolt://localhost:7687"
echo ""
echo "Run 'super-digimon' to start Claude Code with GraphRAG"
```

### 4. MCP Server Development

During development, MCP servers run locally:

```python
# super_digimon/mcp_server.py
import os
from mcp.server import Server
from mcp import MCPClient

class GraphRAGMCPServer(Server):
    def __init__(self):
        super().__init__("graphrag")
        
        # Connect to Docker services
        self.neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.neo4j_user = os.getenv("NEO4J_USER", "neo4j")
        self.neo4j_password = os.getenv("NEO4J_PASSWORD", "password")
        
        # Local file paths
        self.index_path = "./data/indices"
        self.cache_path = "./data/cache"
```

### 5. Testing Workflow

```bash
# scripts/test.sh
#!/bin/bash

# Unit tests (no Docker needed)
pytest tests/unit/ -v

# Integration tests (requires Docker)
docker-compose up -d
pytest tests/integration/ -v

# End-to-end tests
./super-digimon -p "Test entity search" --test-mode
```

## Production Deployment

### 1. Full Docker Image

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js for visualization server
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs

# Create app directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Node dependencies
COPY package*.json .
RUN npm ci --only=production

# Copy application code
COPY . .

# Create data directories
RUN mkdir -p data/{indices,visualizations,cache}

# Expose MCP server port (if needed)
EXPOSE 8080

# Run MCP server
CMD ["python", "-m", "super_digimon.mcp_server"]
```

### 2. Production Docker Compose

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  graphrag:
    build: .
    container_name: super-digimon-graphrag
    environment:
      - NEO4J_URI=bolt://neo4j:7687
      - SQLITE_PATH=/data/graphrag.db
      - VECTOR_INDEX_PATH=/data/indices
      - LOG_LEVEL=INFO
    volumes:
      - ./data:/data
    depends_on:
      neo4j:
        condition: service_healthy
    restart: unless-stopped

  neo4j:
    image: neo4j:5-enterprise
    container_name: super-digimon-neo4j
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      - NEO4J_AUTH=neo4j/${NEO4J_PASSWORD}
      - NEO4J_ACCEPT_LICENSE_AGREEMENT=yes
      - NEO4J_dbms_memory_heap_initial__size=2G
      - NEO4J_dbms_memory_heap_max__size=8G
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs
    healthcheck:
      test: ["CMD", "neo4j", "status"]
      interval: 10s
      timeout: 10s
      retries: 10
    restart: unless-stopped

volumes:
  neo4j_data:
  neo4j_logs:
```

## Key Decisions

### Why This Approach?

1. **Development Speed**: Running Python/TS locally allows instant code reloading
2. **Service Isolation**: Databases in Docker prevent version conflicts
3. **Production Ready**: Same Docker images work in dev and prod
4. **Resource Efficiency**: Only run what you need (Neo4j) not entire stack

### What's NOT in Docker During Dev?

- **Python MCP servers**: Run locally for hot reloading
- **TypeScript visualization**: Run with `npm run dev` for instant updates
- **Claude Code**: Installed globally, not containerized

### What IS in Docker?

- **Neo4j**: Consistent graph database environment
- **Future vector DB**: When we add Qdrant/Weaviate
- **Redis** (future): For distributed caching
- **Monitoring** (future): Prometheus/Grafana stack

## Common Commands

```bash
# Start development environment
./scripts/dev.sh

# Stop all services
docker-compose down

# View Neo4j logs
docker logs -f super-digimon-neo4j

# Reset Neo4j data
docker-compose down -v
docker-compose up -d

# Connect to Neo4j cypher-shell
docker exec -it super-digimon-neo4j cypher-shell -u neo4j -p password

# Build production image
docker build -t super-digimon:latest .

# Run production stack
docker-compose -f docker-compose.prod.yml up -d
```

## Troubleshooting

### Neo4j won't start
```bash
# Check logs
docker logs super-digimon-neo4j

# Common fix: Clear volumes
docker-compose down -v
docker-compose up -d
```

### Port conflicts
```bash
# Check what's using ports
lsof -i :7687  # Neo4j bolt
lsof -i :7474  # Neo4j HTTP

# Change ports in docker-compose.yml if needed
```

### Memory issues
```bash
# Increase Docker Desktop memory allocation
# Settings -> Resources -> Memory -> 8GB recommended

# Or reduce Neo4j heap size in docker-compose.yml
```

## Future Enhancements

1. **Multi-stage builds** for smaller production images
2. **Docker BuildKit** for faster builds with caching
3. **Health check endpoints** for all services
4. **Kubernetes manifests** for cloud deployment
5. **Dev containers** for VS Code integration

This approach gives us the best of both worlds: fast local development with consistent service dependencies, and a clear path to production deployment.