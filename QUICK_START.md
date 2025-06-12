# Super-Digimon Quick Start Guide

## What Is Super-Digimon?

A GraphRAG system that lets you ask questions about graph data in natural language, powered by Claude Code.

## Core Architecture (Simple Version)

```
Your Question → Claude Code → Python Tools → Graph/Vector/SQL → Answer
```

- **Claude Code**: Understands your question and orchestrates tools
- **Python Tools**: 26 core GraphRAG tools (planned: 106 total with extensions)
- **Storage**: Neo4j (primary graph database)

## Storage Architecture

- **Neo4j**: Primary database for graph operations, traversal, and storage
- **Vector Storage**: Handled within tools (embeddings can be stored in Neo4j)
- **Metadata**: Managed by individual tools as needed

## The 26 Core Tools (T01-T26)

### Basic Operations (T01-T15)
- **T01-T03**: Document loading, text chunking, node creation
- **T04-T06**: Entity/relationship extraction, graph building
- **T07-T09**: Embeddings, vector indexing, similarity search
- **T10-T12**: Community detection, summarization, graph traversal
- **T13-T15**: Context retrieval, response generation, result synthesis

### Advanced Operations (T16-T26)
- **T16-T17**: Visualization, Personalized PageRank (PPR)
- **T18-T19**: Advanced algorithms, relationship vector search
- **T20-T21**: Chunk aggregation, hierarchical communities
- **T22-T26**: Specialized GraphRAG operators

### Future Extensions (Planned)
The vision includes expanding to 106 tools with:
- Multi-format data ingestion
- Cross-domain algorithms
- External system integrations
- Advanced analysis capabilities

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

## Implementation Status

```bash
# Super-Digimon is in specification phase
# See STATUS.md for detailed implementation status

# Previous implementations have been archived/removed:
# - StructGPT (removed)
# - GraphRAG_fresh (removed)
# - CC2 (removed)

# Current focus:
# - Building from specifications
# - Clean implementation of 26 core tools
# - MCP server setup for Claude Code integration
```

## Current Status

**Super-Digimon Status:**
- Currently in specification and documentation cleanup phase
- No working implementation yet (see STATUS.md)
- Neo4j integration tested and working
- Target: Build clean implementation from specifications

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
- **Vector Storage**: Tool-specific (embeddings in Neo4j or separate)
- **Development Tool**: cc_automator (for autonomous development)
- **Protocol**: Model Context Protocol (MCP)

## Next Steps

1. See [Canonical Architecture](docs/architecture/CANONICAL_ARCHITECTURE.md) for technical details
2. See [Celestial Council Demo](examples/celestial_council_demo.md) for full example
3. Start with simple questions, build complexity gradually