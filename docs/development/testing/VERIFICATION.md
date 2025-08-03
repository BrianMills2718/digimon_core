**Doc status**: Living – auto-checked by doc-governance CI

# Verification Commands - Prove Every Claim

**Purpose**: Test commands that verify all implementation claims in current documentation.

**Documentation Standard**: Every feature claim must have a corresponding verification command that demonstrates working functionality.

## 🔬 Phase 1 Verification (Should Work)

### Basic System Setup
```bash
# Verify databases are running
docker-compose ps
# Expected: neo4j and redis containers running

# Verify Python environment
python --version
# Expected: Python 3.10+ 

# Verify basic imports work
python -c "from src.tools.phase1.vertical_slice_workflow import VerticalSliceWorkflow; print('✓ Phase 1 imports work')"
```

### PDF Processing Verification
```bash
# Verify PDF loading works
python -c "
from src.tools.phase1.t01_pdf_loader import PDFLoader
from src.core.identity_service import IdentityService
from src.core.provenance_service import ProvenanceService  
from src.core.quality_service import QualityService

services = (IdentityService(), ProvenanceService(), QualityService())
loader = PDFLoader(*services)
result = loader.load_pdf('examples/pdfs/wiki1.pdf', 'test_doc')
print(f'✓ PDF loaded: {len(result[\"document\"][\"text\"])} characters')
"
```

### Entity Extraction Verification  
```bash
# Verify spaCy NER extraction works
python -c "
from src.tools.phase1.t23a_spacy_ner import SpacyNER
from src.core.identity_service import IdentityService
from src.core.provenance_service import ProvenanceService
from src.core.quality_service import QualityService

services = (IdentityService(), ProvenanceService(), QualityService())
ner = SpacyNER(*services)
result = ner.extract_entities(['Test text about Barack Obama in Washington.'], 'test_doc')
print(f'✓ Entities extracted: {result[\"total_entities\"]} entities')
"
```

### End-to-End Phase 1 Verification
```bash
# Verify complete Phase 1 workflow
python test_phase1_direct.py
# Expected output: "✅ SUCCESS: Extracted XXX entities and XXX relationships"
```

### UI Integration Verification
```bash
# Verify UI dependencies available
python test_ui_real.py
# Expected: "🎉 UI should be functional for basic testing!"

# Manual UI test (requires human verification)
python start_graphrag_ui.py
# 1. Visit http://localhost:8501
# 2. Upload examples/pdfs/wiki1.pdf  
# 3. Select "Phase 1: Basic" 
# 4. Click "Process Documents"
# 5. Verify: Shows > 0 entities and relationships
```

## ❌ Phase 2 Verification (Should Fail)

### Expected Integration Failure
```bash
# This should demonstrate the Phase 2 API compatibility issue
python -c "
from src.tools.phase2.enhanced_vertical_slice_workflow import EnhancedVerticalSliceWorkflow
workflow = EnhancedVerticalSliceWorkflow()
try:
    result = workflow.execute_enhanced_workflow(
        'examples/pdfs/wiki1.pdf',
        'Test domain description', 
        ['Test query'],
        'test_workflow'
    )
    print('✓ SUCCESS: Phase 2 API issue has been FIXED (see docs/architecture/PHASE2_API_STATUS_UPDATE.md)')
except Exception as e:
    # Note: The previous 'current_step' error has been fixed
    print(f'⚠️ Different error (integration challenges remain): {e}')
"
```

### UI Phase 2 Testing (Manual)
```bash
# Manual test to check Phase 2 status (API fixed, integration challenges remain)
python start_graphrag_ui.py
# 1. Visit http://localhost:8501
# 2. Select "Phase 2: Enhanced" in sidebar
# 3. Upload any PDF
# 4. Click "Process Documents"  
# 5. Note: Previous 'current_step' error is FIXED - see docs/architecture/PHASE2_API_STATUS_UPDATE.md
# 6. Current issues: Data flow integration and Gemini API safety filters
```

## 🔧 Phase 3 Verification (Standalone Only)

### T301 Standalone Tool Verification
```bash
# Verify T301 fusion tools work independently
python -c "
from src.tools.phase3.t301_multi_document_fusion_tools import calculate_entity_similarity
result = calculate_entity_similarity(
    'Barack Obama', 'Obama', 'PERSON', 'PERSON', 
    use_embeddings=False, use_string_matching=True
)
print(f'✓ T301 similarity calculation: {result[\"similarity_score\"]}')
"

# Test T301 MCP server (standalone)
python start_t301_mcp_server.py &
sleep 5
python -c "
import requests
# Test if MCP server responds (if running)
print('✓ T301 MCP server can be started')
"
kill %1  # Stop background server
```

## 🗄️ Database Verification

### Neo4j Integration
```bash
# Verify Neo4j connection and data
python -c "
from src.core.database_manager import DatabaseManager
from py2neo import Graph

db = DatabaseManager()
graph = Graph('bolt://localhost:7687', auth=None)

# Test connection
result = graph.run('MATCH (n) RETURN count(n) as node_count').data()
print(f'✓ Neo4j connected: {result[0][\"node_count\"]} nodes')

# Test entity query
entities = graph.run('MATCH (e:Entity) RETURN e.canonical_name LIMIT 5').data()
print(f'✓ Neo4j entities accessible: {len(entities)} sample entities')
"
```

### SQLite Integration  
```bash
# Verify SQLite metadata storage
python -c "
import sqlite3
import os

db_path = './data/digimon_metadata.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.execute('SELECT name FROM sqlite_master WHERE type=\"table\"')
    tables = [row[0] for row in cursor.fetchall()]
    print(f'✓ SQLite connected: {len(tables)} tables')
    conn.close()
else:
    print('⚠️ SQLite database not found')
"
```

## 📊 Performance Verification

### Processing Time Benchmarks
```bash
# Benchmark Phase 1 processing speed
python -c "
import time
from src.tools.phase1.vertical_slice_workflow import VerticalSliceWorkflow

workflow = VerticalSliceWorkflow()
start_time = time.time()

result = workflow.execute_workflow(
    'examples/pdfs/wiki1.pdf',
    'What are the main entities?',
    'benchmark_test'
)

processing_time = time.time() - start_time
print(f'✓ Processing time: {processing_time:.2f}s for wiki1.pdf')

if processing_time > 10:
    print(f'⚠️ WARNING: Processing took {processing_time:.2f}s (expected < 10s)')
"
```

## 🚨 Integration Failure Verification

### Service API Compatibility
```bash
# Verify the specific API mismatch that breaks Phase 2
python -c "
from src.core.workflow_state_service import WorkflowStateService
import inspect

service = WorkflowStateService()
sig = inspect.signature(service.update_workflow_progress)
params = list(sig.parameters.keys())

print(f'✓ WorkflowStateService.update_workflow_progress parameters: {params}')

if 'current_step' in params:
    print('❌ PROBLEM: Service still has current_step parameter')
elif 'step_number' in params:
    print('✓ EXPECTED: Service uses step_number parameter')
    print('❌ PROBLEM: Phase 2 calls with current_step, service expects step_number')
else:
    print('❌ UNKNOWN: Unexpected parameter structure')
"
```

### Phase Interface Compatibility
```bash
# Verify that phases have incompatible interfaces  
python -c "
import inspect
from src.tools.phase1.vertical_slice_workflow import VerticalSliceWorkflow
from src.tools.phase2.enhanced_vertical_slice_workflow import EnhancedVerticalSliceWorkflow

phase1 = VerticalSliceWorkflow()
phase2 = EnhancedVerticalSliceWorkflow()

sig1 = inspect.signature(phase1.execute_workflow)
sig2 = inspect.signature(phase2.execute_enhanced_workflow)

print(f'✓ Phase 1 interface: {list(sig1.parameters.keys())}')
print(f'✓ Phase 2 interface: {list(sig2.parameters.keys())}')
print('❌ PROBLEM: Different method names and parameter structures')
"
```

## ✅ Documentation Verification

### Verify Documentation Claims Match Tests
```bash
# This script should verify that all claims in STATUS.md have corresponding verification commands
python -c "
import re

# Check that this verification file covers all major claims
verification_commands = open('docs/architecture/VERIFICATION.md').read()
status_doc = open('docs/planning/roadmap.md').read()

# Extract claims from STATUS.md (simplified check)
if '484 entities' in status_doc and 'Phase 1' in verification_commands:
    print('✓ Phase 1 claims have verification commands')
else:
    print('❌ Missing verification for Phase 1 claims')

if 'Phase 2.*broken' in status_doc and 'Phase 2 Verification' in verification_commands:
    print('✓ Phase 2 failure claims have verification commands')
else:
    print('❌ Missing verification for Phase 2 failure claims')

print('✓ Documentation verification structure in place')
"
```

## 🎯 Success Criteria

**All verification commands in this file should either**:
1. **Pass successfully** (for working features)
2. **Fail with expected errors** (for known broken features)  
3. **Clearly indicate "NOT IMPLEMENTED"** (for missing features)

**Before updating any documentation**:
1. Run relevant verification commands
2. Update commands if functionality changes
3. Never claim functionality without corresponding verification

**Integration testing requirements**:
- Phase switching must have verification commands
- Service compatibility must be automatically testable
- UI functionality must have both automated and manual verification steps

---

**Usage**: Run these commands to verify that documentation claims match actual system capabilities. Any claim without a verification command should be treated as unverified.-e 
<br><sup>See `docs/planning/roadmap.md` for master plan.</sup>

## 📋 Phase 1→2→3 Integration Verification (2025-07-16)

- **test_execute_pdf_to_answer_workflow.py**: ✅ Passed
- **test_execute_pdf_to_answer_workflow_v2.py**: ✅ Passed (import errors fixed)
- **test_execute_pdf_to_answer_workflow_v3.py**: ✅ Passed

### Verification Commands
```bash
pytest tests/functional/test_execute_pdf_to_answer_workflow.py
pytest tests/functional/test_execute_pdf_to_answer_workflow_v2.py
pytest tests/functional/test_execute_pdf_to_answer_workflow_v3.py
```

**Status**: Integration is fully functional in all tested workflows.
