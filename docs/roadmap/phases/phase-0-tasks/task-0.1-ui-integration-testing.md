# Task 0.1: UI Integration Testing

**Duration**: Days 1-2  
**Owner**: Frontend/Integration Lead  
**Priority**: CRITICAL

## Objective

Validate that the Streamlit UI successfully orchestrates the complete academic research pipeline from document upload through final export, identifying and documenting all integration issues.

## Detailed Steps

### Day 1 Morning: Environment Setup & Initial Testing

```bash
# 1. Verify all services are running
cd /home/brian/Digimons
python scripts/check_services.py

# Expected output:
# Neo4j: ✓ Connected (bolt://localhost:7687)
# Qdrant: ✓ Connected (localhost:6333)
# MCP Server: ✓ Running (port 3000)
# API Keys: ✓ OpenAI configured

# 2. Start Streamlit application
python -m streamlit run streamlit_app.py

# 3. Open browser to http://localhost:8501
```

### Day 1 Afternoon: Systematic Workflow Testing

#### Test Case 1: Document Upload
```python
# Test checklist:
1. Upload single PDF (< 10 pages)
   - [ ] File uploads successfully
   - [ ] Progress indicator shows
   - [ ] No timeout errors
   - [ ] File metadata extracted

2. Upload larger PDF (50+ pages)
   - [ ] Chunking works correctly
   - [ ] Memory usage acceptable
   - [ ] Processing time logged

3. Error cases:
   - [ ] Non-PDF file rejected gracefully
   - [ ] Corrupted PDF handled
   - [ ] Empty file handled
```

#### Test Case 2: Processing Pipeline
```python
# For each uploaded document, verify:

1. Text Extraction (T01)
   - [ ] Full text extracted
   - [ ] Metadata preserved
   - [ ] Page numbers maintained

2. Text Chunking (T15a)
   - [ ] Chunks created with overlap
   - [ ] Chunk size consistent
   - [ ] Source positions tracked

3. Entity Extraction (T23c)
   - [ ] LLM extraction initiated
   - [ ] Entities displayed in UI
   - [ ] Confidence scores shown
   - [ ] Compare with SpaCy (T23a)

4. Graph Construction (T31, T34)
   - [ ] Entities become nodes
   - [ ] Relationships become edges
   - [ ] Neo4j populated correctly
   - [ ] Graph statistics displayed
```

#### Test Case 3: Analysis & Query
```python
# Test analysis capabilities:

1. Multi-hop Queries (T49)
   - [ ] Sample queries work
   - [ ] Results displayed clearly
   - [ ] Path visualization works
   - [ ] Performance acceptable

2. PageRank Analysis (T68)
   - [ ] Importance scores calculated
   - [ ] Top entities highlighted
   - [ ] Visualization updates

3. Cross-Document Fusion (T301)
   - [ ] Upload second document
   - [ ] Fusion process completes
   - [ ] Unified graph created
   - [ ] Conflicts resolved
```

### Day 2 Morning: Export & Provenance Testing

#### Test Case 4: Export Formats
```python
# Test each export format:

1. CSV Export
   - [ ] Entities exported correctly
   - [ ] Relationships included
   - [ ] Metadata preserved
   - [ ] File downloadable

2. LaTeX Export
   - [ ] Valid LaTeX generated
   - [ ] Tables formatted correctly
   - [ ] Citations included
   - [ ] Compiles without errors

3. BibTeX Export
   - [ ] Valid BibTeX entries
   - [ ] All sources included
   - [ ] Proper formatting

4. JSON Export
   - [ ] Complete graph structure
   - [ ] All properties included
   - [ ] Valid JSON format
```

#### Test Case 5: Provenance Tracking
```python
# Verify provenance chain:

1. Select any entity in results
   - [ ] Source document shown
   - [ ] Page number correct
   - [ ] Text snippet highlighted
   - [ ] Confidence score displayed

2. Trace back relationships
   - [ ] Source passages identified
   - [ ] Extraction method noted
   - [ ] Timestamp recorded

3. Export provenance data
   - [ ] Full audit trail available
   - [ ] Reproducibility verified
```

### Day 2 Afternoon: Performance & Error Testing

#### Performance Metrics Collection
```python
import time
import psutil
import pandas as pd

# Metrics to collect for each operation:
metrics = {
    'operation': [],
    'duration_seconds': [],
    'memory_mb': [],
    'cpu_percent': []
}

# Test operations:
operations = [
    'pdf_upload_10_pages',
    'pdf_upload_50_pages',
    'entity_extraction_spacy',
    'entity_extraction_llm',
    'graph_construction',
    'multi_hop_query',
    'export_csv',
    'export_latex'
]

# Measure each operation
for op in operations:
    start_time = time.time()
    start_memory = psutil.Process().memory_info().rss / 1024 / 1024
    
    # Execute operation...
    
    duration = time.time() - start_time
    memory_used = psutil.Process().memory_info().rss / 1024 / 1024 - start_memory
    
    metrics['operation'].append(op)
    metrics['duration_seconds'].append(duration)
    metrics['memory_mb'].append(memory_used)
    metrics['cpu_percent'].append(psutil.cpu_percent(interval=1))

# Save metrics
df = pd.DataFrame(metrics)
df.to_csv('phase0_performance_baseline.csv', index=False)
```

#### Error Handling Tests
```python
# Test error scenarios:

1. API Failures
   - [ ] Disable OpenAI API - graceful degradation
   - [ ] Rate limit simulation - retry logic works
   - [ ] Invalid API key - clear error message

2. Database Failures  
   - [ ] Stop Neo4j - appropriate error shown
   - [ ] Stop Qdrant - fallback behavior
   - [ ] Connection timeout - handled gracefully

3. Resource Limits
   - [ ] Upload 100MB PDF - size limit enforced
   - [ ] Process 1000 entities - pagination works
   - [ ] Concurrent users - no interference
```

## Bug Documentation Template

For each bug found, document:

```markdown
### Bug ID: UI-001
**Severity**: Critical/Major/Minor
**Component**: Upload/Processing/Analysis/Export
**Description**: Clear description of the issue
**Steps to Reproduce**:
1. Step one
2. Step two
3. Expected vs Actual result
**Error Message**: Any error text
**Screenshot**: Link to screenshot
**Workaround**: Temporary solution if any
```

## Performance Baseline Report

Create summary report with:

1. **Operation Timings**
   - PDF processing: X seconds per page
   - Entity extraction: Y seconds per 1000 words
   - Graph construction: Z seconds per 100 entities

2. **Resource Usage**
   - Peak memory: X GB
   - Average CPU: Y%
   - Disk I/O: Z MB/s

3. **Scalability Limits**
   - Max PDF size: X MB
   - Max entities: Y
   - Max concurrent users: Z

## Deliverables

### End of Day 1
- [ ] Initial test results documented
- [ ] Critical bugs identified
- [ ] Basic workflow validated

### End of Day 2  
- [ ] Complete bug list with priorities
- [ ] Performance baseline established
- [ ] Error handling verified
- [ ] Go/No-Go recommendation

## Success Criteria

- [ ] Complete workflow executes without critical errors
- [ ] All major features accessible through UI
- [ ] Performance acceptable for academic use
- [ ] Error messages helpful and clear
- [ ] Export formats validated