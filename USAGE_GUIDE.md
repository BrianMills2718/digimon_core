# Super-Digimon GraphRAG System - Usage Guide

## Quick Start

Since you're having issues with Streamlit, I've created a command-line tool that works reliably.

### 1. Check System Status

```bash
python cli_tool.py check
```

This verifies that Neo4j is connected and all components are working.

### 2. Process a PDF

```bash
python cli_tool.py process <pdf_file> "<your question>"
```

Example:
```bash
python cli_tool.py process test_document.pdf "Who founded Tesla?"
python cli_tool.py process research_paper.pdf "What are the main findings?"
```

Add `--json` to save results to a file:
```bash
python cli_tool.py process document.pdf "What companies are mentioned?" --json
```

### 3. View Graph Statistics

```bash
python cli_tool.py stats
```

Shows:
- Total entities and their types
- Total relationships and their types  
- Top 10 entities by PageRank score

## How It Works

### Entity Extraction
The system uses spaCy NER to extract 12 entity types:
- **PERSON**: People names (e.g., "Elon Musk")
- **ORG**: Organizations (e.g., "Tesla", "SpaceX")
- **GPE**: Locations (e.g., "Austin", "California")
- **DATE**: Dates (e.g., "2003", "last year")
- **PRODUCT**: Products (e.g., "Model S", "iPhone")
- And 7 more types...

### Relationship Extraction
Three methods find connections between entities:

1. **Pattern-Based** (most reliable):
   - "X founded Y" → CREATED relationship
   - "X is CEO of Y" → WORKS_FOR relationship
   - "X located in Y" → LOCATED_IN relationship

2. **Dependency Parsing**:
   - Analyzes sentence grammar
   - Finds subject-verb-object patterns

3. **Proximity-Based** (fallback):
   - Entities near each other
   - Creates generic RELATED_TO relationships

### Graph Analysis
- Stores entities and relationships in Neo4j
- Calculates PageRank to find important entities
- Traverses graph to answer queries

## Example Output

```
📊 Summary:
  • Chunks created: 1
  • Entities extracted: 24
  • Relationships found: 30
  • Graph entities: 22
  • Graph edges: 30

🎯 Query Results:
1. Elon Musk
   Confidence: 0.85
   Evidence: Tesla Inc. is an American electric vehicle manufacturer founded by Elon Musk...

🏆 Top Entities by PageRank:
  • Tesla (ORG) - Score: 0.0285
  • Elon Musk (PERSON) - Score: 0.0265
  • SpaceX (ORG) - Score: 0.0241
```

## Visualizing the Graph

If you want to see the graph visually, you can:

1. **Use Neo4j Browser**:
   ```
   http://localhost:7474
   Username: neo4j
   Password: password
   ```
   
   Query to see all entities and relationships:
   ```cypher
   MATCH (n)-[r]->(m) 
   RETURN n, r, m 
   LIMIT 100
   ```

2. **Use the Web UI** (if Streamlit works):
   - Go to the "Graph Explorer" tab
   - Click "Load Graph" to see interactive visualization

## Creating Test PDFs

To create a PDF from text:

```python
python create_test_pdf.py
```

This converts `test_document.txt` to `test_document.pdf`.

## Troubleshooting

1. **"Neo4j not connected"**:
   ```bash
   docker-compose up -d neo4j
   ```

2. **"spaCy model not found"**:
   ```bash
   python -m spacy download en_core_web_sm
   ```

3. **Slow processing**:
   - First run downloads models (may take a minute)
   - Subsequent runs are faster
   - Large PDFs take longer (2-5 minutes)

## Understanding Results

- **Confidence Scores**: 0.0 to 1.0 (higher is better)
  - 0.8+: High confidence
  - 0.5-0.8: Medium confidence
  - <0.5: Low confidence

- **PageRank Scores**: Measure entity importance
  - Higher scores = more central/important entities
  - Useful for finding key people, organizations, concepts

- **Relationship Types**:
  - CREATED: Founded, established, built
  - WORKS_FOR: Employment relationships
  - LOCATED_IN: Geographic relationships
  - RELATED_TO: General proximity-based connections