# Super-Digimon Quick Start Guide

## What Is Super-Digimon?

A GraphRAG system that lets you ask questions about graph data in natural language, powered by Claude Code.

## Core Architecture (Simple Version)

```
Your Question → Claude Code → Python Tools → Graph/Vector/SQL → Answer
```

- **Claude Code**: Understands your question and orchestrates tools
- **Python Tools**: 26 operators that search, traverse, and analyze
- **Storage**: Neo4j (graphs) + SQLite (metadata) + FAISS (vectors)

## Why Three Databases?

Each is optimized for different operations:
- **Neo4j**: Graph traversal (find paths, communities)
- **FAISS**: Vector search (find similar entities) - ESSENTIAL for GraphRAG!
- **SQLite**: Simple tables (config, evaluation data)

## The 26 Tools Explained

### Building Tools (T01-T08)
Create and index your graph:
- Load documents → Extract entities → Build graph → Create embeddings

### Search Tools (T09-T13, T17, T19)
Find things in your graph:
- Vector search entities/relationships
- Graph traversal (neighbors, paths)
- Community detection

### Analysis Tools (T14-T16, T18, T20-T26)
Process and present results:
- Generate responses
- Visualize graphs
- Advanced algorithms

## Example Workflow

```
You: "Find influential members of the Celestial Council"

Claude Code thinks: "I need to search for Celestial Council entities, 
                    then run PageRank to find influential ones"

Executes:
1. entity_vdb_search("Celestial Council") → Find relevant entities
2. entity_ppr(seed_entities) → Run PageRank 
3. community_detection() → Find their communities
4. context_retrieval() → Get supporting text
5. response_generation() → Create natural language answer

You get: "The most influential members are Zephyr the Windweaver 
         (PageRank: 0.89) who leads the Air Coalition..."
```

## What Makes This Special?

1. **Natural Language**: Just ask questions, no query languages
2. **Multi-Structure**: Seamlessly combines graph + vector + text analysis
3. **Intelligent**: Claude Code figures out which tools to use
4. **Flexible**: Attributes system handles different graph types

## What This Is NOT

- **Not a database**: It's an analysis layer on top
- **Not production-ready**: It's a research prototype
- **Not optimized**: Functionality over performance
- **Not multi-user**: Single researcher at a time

## Quick Test

```bash
# Load sample data
./super-digimon load celestial_council.json

# Ask a question
./super-digimon "Who are the key bridge figures between factions?"

# Claude Code will:
# 1. Search for faction entities
# 2. Find paths between factions  
# 3. Identify entities on multiple paths
# 4. Return natural language explanation
```

## Why Should I Care?

If you need to:
- Analyze social networks
- Trace influence patterns
- Find hidden connections
- Combine graph analysis with semantic search

Then Super-Digimon lets you do this through conversation, not code.

## Technical Stack (If You Care)

- **Runtime**: Claude Code (via MCP)
- **Language**: Python 3.11+
- **Graph DB**: Neo4j 5+
- **Vector Index**: FAISS
- **Metadata**: SQLite
- **Protocol**: Model Context Protocol (MCP)

## Next Steps

1. See [CANONICAL_ARCHITECTURE.md](SUPER_DIGIMON_CANONICAL_ARCHITECTURE.md) for technical details
2. See [Celestial Council Demo](demos/celestial_council.md) for full example
3. Start with simple questions, build complexity gradually