---
status: living
---

# Neo4j Setup Guide

**Purpose**: Set up Neo4j database for full GraphRAG functionality  
**Reference**: See [CLAUDE.md Priority 1](../../CLAUDE.md) for complete instructions

## 🎯 **Why Neo4j?**

### **Current State (Without Neo4j)**
- ✅ Entity extraction works (13 entities)
- ✅ Relationship extraction works (21 relationships)
- ✅ UI shows data
- ❌ No graph storage
- ❌ No PageRank calculations
- ❌ No multi-hop queries

### **With Neo4j Enabled**
- ✅ All current features PLUS:
- ✅ Persistent graph storage
- ✅ PageRank importance scores
- ✅ Multi-hop relationship queries
- ✅ Advanced graph analytics
- ✅ Query interface in UI

## 🚀 **Quick Setup (Recommended)**

### **Option A: No Authentication (Development)**
```bash
# Stop any existing Neo4j
docker stop neo4j 2>/dev/null || true
docker rm neo4j 2>/dev/null || true

# Start Neo4j without authentication
docker run -p 7687:7687 -p 7474:7474 --name neo4j -d -e NEO4J_AUTH=none neo4j:latest

# Wait for startup
echo "Waiting for Neo4j to start..."
sleep 30

# Test connection
python -c "from py2neo import Graph; g = Graph('bolt://localhost:7687'); print('✅ Neo4j connected')"
```

### **Option B: With Password (Production)**
```bash
# Start with default credentials
docker run -p 7687:7687 -p 7474:7474 --name neo4j -d neo4j:latest

# Wait for startup
sleep 30

# Set password
docker exec -it neo4j cypher-shell -u neo4j -p neo4j "ALTER USER neo4j SET PASSWORD 'password';"

# Test connection
python -c "from py2neo import Graph; g = Graph('bolt://localhost:7687', auth=('neo4j', 'password')); print('✅ Neo4j connected')"
```

## 🔧 **Verification Steps**

### **1. Test System Integration**
```bash
# Run minimal example - should show no authentication warnings
python examples/minimal_working_example.py

# Expected: No "Neo4j authentication failed" messages
# Expected: PageRank calculations working
```

### **2. Test UI Integration**
```bash
# Launch UI
python ui/launch_ui.py

# Upload a document
# Expected: Enhanced results with graph storage
```

### **3. Test Neo4j Browser**
```bash
# Access Neo4j browser
open http://localhost:7474

# Run test query
MATCH (n) RETURN count(n) as node_count
```

## 🐛 **Troubleshooting**

### **Connection Issues**
```bash
# Check if Neo4j is running
docker ps | grep neo4j

# Check logs
docker logs neo4j

# Test connection manually
python -c "from neo4j import GraphDatabase; driver = GraphDatabase.driver('bolt://localhost:7687', auth=None); driver.verify_connectivity(); print('✅ Connected')"
```

### **Authentication Issues**
```bash
# If you see "authentication failed" errors:

# Option 1: Restart without auth
docker stop neo4j
docker rm neo4j
docker run -p 7687:7687 -p 7474:7474 --name neo4j -d -e NEO4J_AUTH=none neo4j:latest

# Option 2: Reset password
docker exec -it neo4j cypher-shell -u neo4j -p neo4j "ALTER USER neo4j SET PASSWORD 'newpassword';"
```

### **Port Conflicts**
```bash
# Check what's using ports
lsof -i :7687
lsof -i :7474

# Use different ports if needed
docker run -p 7688:7687 -p 7475:7474 --name neo4j -d -e NEO4J_AUTH=none neo4j:latest
```