# KGAS Cross-Modal REST API

Local REST API for cross-modal analysis operations, enabling custom tools and automation.

## Overview

This API provides HTTP endpoints for:
- Document analysis (PDF, Word, text) **[Currently using mock data - pipeline integration pending]**
- Format conversion (Graph ↔ Table ↔ Vector) **[Fully functional]**
- AI-powered mode recommendation **[Fully functional with LLM API key]**
- Batch processing **[Structure complete - pipeline integration pending]**
- Service health monitoring **[Fully functional]**

**Security Note**: The API runs on localhost only. Your data never leaves your machine.

## Current Status

The API structure is complete and demonstrates the intended architecture. However:

✅ **Working Features**:
- Format conversion between Graph/Table/Vector
- Mode recommendation (with OpenAI/Anthropic API key)
- Health monitoring
- API structure and endpoints

⚠️ **Pending Integration**:
- Document processing pipeline (requires core service fixes)
- Real entity extraction from PDFs/documents
- Full batch processing capabilities

The document analysis endpoints currently return mock data to demonstrate the API structure. Full pipeline integration will be available after the core services (identity, provenance, quality, workflow state) are brought to production standards.

## Quick Start

### 1. Start the API Server

```bash
# Basic usage
python run_api_server.py

# With options
python run_api_server.py --port 8080 --reload
```

### 2. Access the API

- **API Base**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

### 3. Try the Examples

```bash
# Python client example
python examples/api_client_example.py

# Web UI example (open in browser)
open examples/web_ui_example.html
```

## API Endpoints

### Health Check
```http
GET /api/health
```
Check API and service health status.

### Document Analysis
```http
POST /api/analyze
```
Upload and analyze a document.

**Parameters**:
- `file`: Document file (PDF, DOCX, TXT, MD)
- `target_format`: Output format (graph, table, vector)
- `task`: Analysis task description
- `optimization_level`: speed, balanced, or quality
- `validation_level`: basic, standard, or comprehensive

**Example**:
```python
import requests

with open("paper.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/analyze",
        files={"file": f},
        params={"target_format": "graph"}
    )
    
results = response.json()
```

### Format Conversion
```http
POST /api/convert
```
Convert data between formats.

**Request Body**:
```json
{
    "data": {...},
    "source_format": "graph",
    "target_format": "table",
    "method": "direct"  // optional
}
```

**Example**:
```python
# Convert graph to table
response = requests.post(
    "http://localhost:8000/api/convert",
    json={
        "data": graph_data,
        "source_format": "graph",
        "target_format": "table"
    }
)
```

### Mode Recommendation
```http
POST /api/recommend
```
Get AI recommendation for analysis mode.

**Request Body**:
```json
{
    "task": "analyze social networks",
    "data_type": "entities_and_relationships",
    "size": 1000,
    "performance_priority": "quality"
}
```

### Batch Processing
```http
POST /api/batch/analyze
```
Process multiple documents.

**Returns**: Job ID for tracking

```http
GET /api/jobs/{job_id}
```
Check batch job status and results.

### Statistics
```http
GET /api/stats
```
Get service statistics and metrics.

## Integration Examples

### Python Script
```python
import requests

# Analyze a research paper
with open("research.pdf", "rb") as f:
    result = requests.post(
        "http://localhost:8000/api/analyze",
        files={"file": f},
        params={"target_format": "graph"}
    ).json()

# Extract entities
entities = result["results"]["graph"]["nodes"]
relationships = result["results"]["graph"]["edges"]
```

### JavaScript/Web
```javascript
// Convert data format
const response = await fetch('http://localhost:8000/api/convert', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        data: myGraphData,
        source_format: 'graph',
        target_format: 'table'
    })
});

const tableData = await response.json();
```

### Jupyter Notebook
```python
import requests
import pandas as pd

# Get mode recommendation
rec = requests.post(
    "http://localhost:8000/api/recommend",
    json={
        "task": "statistical analysis",
        "data_type": "numerical_data",
        "size": 10000
    }
).json()

print(f"Recommended: {rec['primary_mode']}")
print(f"Confidence: {rec['confidence']:.2%}")
```

### Shell Script
```bash
#!/bin/bash

# Batch process all PDFs in folder
for pdf in *.pdf; do
    curl -X POST \
        -F "file=@$pdf" \
        -F "target_format=table" \
        "http://localhost:8000/api/analyze" \
        -o "${pdf%.pdf}_analysis.json"
done
```

## Use Cases

### 1. Research Automation
```python
# Process all papers in a conference
for paper in conference_papers:
    analysis = analyze_document(paper, target_format="graph")
    save_to_database(analysis)
    
# Find cross-paper citations
cross_references = find_citations(all_analyses)
```

### 2. Custom Web Dashboard
Build a React/Vue app that visualizes your research:
- Upload documents through the web interface
- Convert to appropriate formats for visualization
- Display interactive graphs and tables

### 3. Integration with R
```r
library(httr)
library(jsonlite)

# Analyze document from R
response <- POST(
    "http://localhost:8000/api/analyze",
    body = list(file = upload_file("data.pdf")),
    query = list(target_format = "table")
)

data <- fromJSON(content(response, "text"))
```

### 4. Automated Reports
```python
# Daily analysis pipeline
def daily_analysis():
    # Get new documents
    new_docs = get_new_documents()
    
    # Batch analyze
    job_id = submit_batch(new_docs)
    
    # Wait for completion
    results = wait_for_job(job_id)
    
    # Generate report
    generate_latex_report(results)
```

## Configuration

### Environment Variables
- `OPENAI_API_KEY`: For OpenAI-based mode selection
- `ANTHROPIC_API_KEY`: For Anthropic-based mode selection

### Server Options
- `--port`: Change port (default: 8000)
- `--reload`: Auto-reload for development
- `--log-level`: Set logging level

## Error Handling

The API returns standard HTTP status codes:
- `200`: Success
- `400`: Bad request (invalid parameters)
- `404`: Not found
- `500`: Server error
- `503`: Service unavailable

Error responses include details:
```json
{
    "detail": "Invalid target format: grph. Use: graph, table, or vector"
}
```

## Performance Tips

1. **Batch Processing**: Use `/api/batch/analyze` for multiple files
2. **Caching**: Results are cached for repeated conversions
3. **Optimization Level**: Use "speed" for quick results, "quality" for accuracy
4. **Format Selection**: Let AI recommend the best format for your task

## Security

- **Localhost Only**: API binds to 127.0.0.1
- **CORS**: Limited to local origins
- **File Validation**: Only accepted file types processed
- **Size Limits**: Large files may be rejected
- **No External Access**: Firewall prevents external connections

## Troubleshooting

### API Won't Start
- Check if port 8000 is already in use
- Verify Python environment is activated
- Check for missing dependencies

### Service Unavailable
- Ensure LLM API keys are set (for mode recommendation)
- Check service health at `/api/health`
- Review server logs for errors

### Slow Performance
- Use appropriate optimization level
- Consider batch processing
- Check system resources

## Further Development

The API is designed for extensibility:
- Add custom endpoints in `cross_modal_api.py`
- Extend validation in request models
- Add new conversion methods
- Implement caching strategies

For questions or issues, check the main KGAS documentation.