# KGAS Integration with Claude Code as Agent Brain

## Overview

This document explains how to leverage Claude Code as the intelligent orchestration layer for KGAS, using its native capabilities for agent-based research workflows.

## Key Insights from Claude Code Guides

### 1. Subagents for Parallel Processing
- Each subagent gets its own context window (critical for complex analysis)
- Can run up to 10 subagents in parallel
- Automatically handles task queuing when >10 tasks
- Ideal for document-by-document analysis

### 2. MCP Integration
- KGAS tools exposed as MCP server
- Claude Code can use tools via `mcp__kgas__*` namespace
- Full tool discovery and documentation
- Streaming results support

### 3. SDK for Programmatic Control
- Python SDK for non-interactive execution
- Streaming JSON for progressive results
- Session management for multi-turn workflows
- Custom system prompts for specialized behavior

## Architecture Design

```
┌─────────────────────────────────────────────────────────────┐
│                   User Research Request                      │
│              "Analyze these papers for..."                   │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│               Claude Code (Master Agent)                     │
│                                                              │
│  1. Understands research intent                              │
│  2. Generates KGAS workflow                                  │
│  3. Delegates to subagents                                   │
│  4. Synthesizes results                                      │
└─────────────────────────┬───────────────────────────────────┘
                          │
        ┌─────────────────┴─────────────────┐
        │                                   │
        ▼                                   ▼
┌───────────────────┐              ┌───────────────────┐
│   Subagent 1      │              │   Subagent 2      │
│                   │              │                   │
│ Analyze Paper 1   │              │ Analyze Paper 2   │
│ - Load PDF        │              │ - Load PDF        │
│ - Extract theory  │              │ - Extract entities│
│ - Build graph     │              │ - Apply theory    │
└─────────┬─────────┘              └─────────┬─────────┘
          │                                   │
          │         KGAS MCP Tools           │
          ▼                                   ▼
    ┌─────────────────────────────────────────────┐
    │            mcp__kgas__* tools               │
    │  - load_pdf_document                        │
    │  - chunk_text                               │
    │  - extract_entities_from_text               │
    │  - query_graph                              │
    │  - calculate_pagerank                        │
    └─────────────────────────────────────────────┘
```

## Implementation Approaches

### Approach 1: Direct Claude Code Usage (Recommended)

**Use Claude Code directly with custom prompts and MCP configuration:**

```bash
# 1. Configure KGAS as MCP server
claude mcp add kgas python /home/brian/projects/Digimons/kgas_mcp_server.py

# 2. Create research prompt that uses subagents
cat > research_prompt.txt << 'EOF'
Analyze these documents using KGAS tools and subagents:

Documents:
- /home/brian/projects/Digimons/kunst_paper.txt  
- /home/brian/projects/Digimons/lit_review/data/test_texts/texts/carter_speech.txt

Use subagents to:
1. Extract theory from Kunst paper (Subagent 1)
2. Analyze Carter speech (Subagent 2)  
3. Apply theory to speech (Subagent 3)
4. Build knowledge graph (Subagent 4)

Each subagent should use KGAS MCP tools:
- mcp__kgas__load_pdf_document
- mcp__kgas__chunk_text
- mcp__kgas__extract_entities_from_text
- mcp__kgas__query_graph

Synthesize all findings into a research report.
EOF

# 3. Execute with Claude Code
claude --continue < research_prompt.txt
```

### Approach 2: Claude Code SDK Integration

**Use the SDK for programmatic control:**

```python
from claude_code_sdk import query, ClaudeCodeOptions

async def analyze_with_kgas(documents, research_question):
    """Use Claude Code + KGAS for research analysis"""
    
    prompt = f"""
Use subagents to analyze these documents with KGAS tools:

Documents: {documents}
Question: {research_question}

Create parallel subagents for:
1. Document loading and chunking (per document)
2. Theory extraction 
3. Entity and relationship extraction
4. Cross-document synthesis

Use KGAS MCP tools in each subagent:
- mcp__kgas__load_pdf_document
- mcp__kgas__extract_entities_from_text
- mcp__kgas__query_graph

Return structured findings.
"""
    
    async for message in query(
        prompt=prompt,
        options=ClaudeCodeOptions(
            max_turns=10,
            mcp_config="kgas_mcp_config.json",
            allowed_tools=["Task", "mcp__kgas"]  # Allow all KGAS tools
        )
    ):
        # Process streaming results
        yield message
```

### Approach 3: Custom System Prompts

**Configure Claude Code with KGAS-specific behavior:**

```bash
# Create KGAS-aware system prompt
cat > kgas_system_prompt.txt << 'EOF'
You are a research assistant integrated with KGAS (Knowledge Graph Analysis System).

When analyzing documents:
1. Always use subagents for parallel document processing
2. Each subagent should focus on one document or task
3. Use KGAS MCP tools for all analysis:
   - mcp__kgas__load_pdf_document for PDFs
   - mcp__kgas__chunk_text for text processing
   - mcp__kgas__extract_entities_from_text for NER
   - mcp__kgas__query_graph for knowledge queries
4. Synthesize findings across all subagents
5. Generate structured research outputs

Your goal is comprehensive, theory-aware analysis.
EOF

# Use with custom system prompt
claude -p --system-prompt "$(cat kgas_system_prompt.txt)" "Analyze these papers..."
```

## Best Practices

### 1. Subagent Task Design
- **One document per subagent** for deep analysis
- **Specialized subagents** for different analysis types
- **Synthesis subagent** to combine findings
- **Limit to 10 parallel** for optimal performance

### 2. MCP Tool Usage
- Always specify allowed tools explicitly
- Use tool namespacing: `mcp__kgas__toolname`
- Handle tool errors gracefully
- Stream results for large analyses

### 3. Workflow Patterns

**Pattern 1: Document-Parallel Analysis**
```
Master → Subagent per document → Synthesis
```

**Pattern 2: Method-Parallel Analysis**
```
Master → Theory Subagent + Entity Subagent + Graph Subagent → Integration
```

**Pattern 3: Progressive Refinement**
```
Master → Initial Analysis → Refinement Subagents → Final Synthesis
```

### 4. Context Management
- Use `/compact` between major analysis phases
- Save intermediate results to files
- Use session resumption for long workflows
- Clear context before new analysis types

## Example Workflows

### Theory Extraction and Application

```bash
# Step 1: Add KGAS MCP server
claude mcp add kgas python /path/to/kgas_mcp_server.py

# Step 2: Run analysis with subagents
claude << 'EOF'
Create subagents to:

1. **Theory Extraction Subagent**: 
   - Load kunst_paper.txt using mcp__kgas__load_pdf_document
   - Extract psychological theory framework
   - Identify key constructs and relationships

2. **Document Analysis Subagent**:
   - Load carter_speech.txt 
   - Chunk text using mcp__kgas__chunk_text
   - Extract entities with mcp__kgas__extract_entities_from_text

3. **Theory Application Subagent**:
   - Apply extracted theory to speech content
   - Identify psychological factors
   - Calculate risk scores

4. **Knowledge Graph Subagent**:
   - Build graph from all findings
   - Run mcp__kgas__calculate_pagerank
   - Query for key insights with mcp__kgas__query_graph

Synthesize all findings into a research report.
EOF
```

### Multi-Document Comparison

```python
# Using SDK for programmatic control
import asyncio
from claude_code_sdk import query, ClaudeCodeOptions

async def compare_documents(doc_list):
    prompt = f"""
Analyze these {len(doc_list)} documents using parallel subagents:

{chr(10).join([f"- {doc}" for doc in doc_list])}

For each document, create a subagent that:
1. Loads the document with mcp__kgas__load_pdf_document
2. Extracts key themes and entities
3. Builds a document-specific knowledge graph

Then create a synthesis subagent that:
1. Compares findings across all documents
2. Identifies common themes and contradictions
3. Creates a unified knowledge graph
4. Generates comparative insights

Use up to 10 parallel subagents for optimal performance.
"""
    
    async for message in query(
        prompt=prompt,
        options=ClaudeCodeOptions(
            max_turns=15,
            allowed_tools=["Task", "mcp__kgas"]
        )
    ):
        print(message)

# Run analysis
asyncio.run(compare_documents(["doc1.pdf", "doc2.pdf", "doc3.pdf"]))
```

## Advantages of This Approach

1. **Leverages Claude Code's Strengths**
   - Native subagent support
   - Built-in parallelization
   - Context window management
   - Tool orchestration

2. **Maintains KGAS Capabilities**
   - All tools available via MCP
   - Graph-based analysis
   - Theory-aware processing
   - Cross-modal integration

3. **Scalable Architecture**
   - Handles many documents efficiently
   - Progressive result streaming
   - Fault tolerance through subagents
   - Session persistence

4. **Natural Language Interface**
   - Researchers use plain English
   - No need to write YAML workflows
   - Adaptive to different research needs
   - Interactive refinement possible

## Conclusion

By using Claude Code as the agent brain for KGAS, we get:
- Intelligent orchestration without building custom agents
- Parallel processing through subagents
- Natural language research interface  
- Full access to KGAS analytical capabilities
- Operational implementation using existing tools

This approach delivers the vision of KGAS as an autonomous research system while leveraging Claude Code's proven agent capabilities.