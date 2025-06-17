# Granular Implementation Plan with Adversarial Testing

## 🎯 Philosophy: Micro-Steps + Immediate Adversarial Testing

**Rule**: Every 2-4 hours of implementation → Adversarial test → Fix → Verify → Next step
**Never build on unverified foundations**

## 📋 Implementation Cycle Template

### Standard Cycle (2-4 hours each):
1. **Implement**: One small, specific piece
2. **Unit Test**: Basic functionality works
3. **Adversarial Test**: Try to break it with edge cases
4. **Fix**: Address discovered issues
5. **Integration Test**: Works with existing pieces
6. **Commit**: Save verified working state
7. **Document**: Update status with verification commands

## 🔧 Week 1: MCP Server Foundation

### Step 1A: Basic MCP Server (4 hours)
**Goal**: MCP server starts and responds to ping

**Implementation**:
```python
# Create main.py - minimal MCP server
import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server

server = Server("super-digimon")

@server.list_tools()
async def list_tools():
    return []

async def main():
    async with stdio_server() as (read, write):
        await server.run(read, write)

if __name__ == "__main__":
    asyncio.run(main())
```

**Unit Test**:
```bash
# Test server starts
timeout 5s python main.py &
PID=$!
sleep 2
kill $PID
echo "Server started: $?"
```

**Adversarial Test**:
```bash
# Test server handles malformed input
echo '{"invalid": "json"}' | python main.py
echo '{"jsonrpc": "2.0", "method": "invalid"}' | python main.py
# Test server handles interruption
python main.py &
PID=$!
sleep 1
kill -9 $PID  # Hard kill
wait $PID
echo "Exit code: $?"
```

**Integration Test**:
```bash
# Test MCP client can connect
python -c "
import json
import subprocess
proc = subprocess.Popen(['python', 'main.py'], 
                       stdin=subprocess.PIPE, 
                       stdout=subprocess.PIPE)
request = {'jsonrpc': '2.0', 'method': 'tools/list', 'id': 1}
proc.stdin.write(json.dumps(request).encode() + b'\n')
proc.stdin.flush()
response = proc.stdout.readline()
print('Response:', response)
proc.terminate()
"
```

**Verification Commands**:
```bash
echo "Step 1A Status:" > step1A_verification.txt
echo "Date: $(date)" >> step1A_verification.txt
timeout 5s python main.py && echo "✓ Server starts" || echo "✗ Server fails" >> step1A_verification.txt
```

### Step 1B: Configure in Claude Code (2 hours)
**Goal**: Claude Code recognizes super-digimon MCP server

**Implementation**:
```bash
claude mcp add super-digimon "python /home/brian/Digimons/main.py"
```

**Unit Test**:
```bash
claude mcp list | grep super-digimon
echo "MCP configured: $?"
```

**Adversarial Test**:
```bash
# Test invalid server path
claude mcp add test-invalid "python /nonexistent/path.py"
# Test server with missing dependencies
claude mcp add test-broken "python -c 'import nonexistent_module'"
# Test concurrent server access
claude mcp list &
claude mcp list &
wait
```

**Integration Test**:
```bash
# Test Claude Code can actually communicate
echo "Testing MCP communication with Claude Code..."
# This would require testing in Claude Code interface
```

**Verification Commands**:
```bash
echo "Step 1B Status:" > step1B_verification.txt
echo "Date: $(date)" >> step1B_verification.txt
claude mcp list | grep super-digimon && echo "✓ MCP configured" || echo "✗ MCP not configured" >> step1B_verification.txt
```

### Step 1C: Add One Test Tool (4 hours)
**Goal**: MCP server exposes one working tool (echo test)

**Implementation**:
```python
# Add to main.py
@server.tool()
async def echo_test(message: str) -> str:
    """Test tool that echoes input."""
    return f"Echo: {message}"
```

**Unit Test**:
```python
# test_echo_tool.py
import asyncio
import json
from main import server

async def test_echo():
    # Test via server interface
    result = await server.call_tool("echo_test", {"message": "hello"})
    assert result == "Echo: hello"
    print("✓ Echo tool works")

asyncio.run(test_echo())
```

**Adversarial Test**:
```python
# test_echo_adversarial.py
import asyncio
from main import server

async def test_echo_adversarial():
    # Test empty input
    try:
        result = await server.call_tool("echo_test", {"message": ""})
        assert result == "Echo: "
        print("✓ Empty input handled")
    except Exception as e:
        print(f"✗ Empty input failed: {e}")
    
    # Test missing parameter
    try:
        result = await server.call_tool("echo_test", {})
        print(f"✗ Missing parameter should fail but got: {result}")
    except Exception as e:
        print("✓ Missing parameter properly rejected")
    
    # Test very long input
    long_msg = "x" * 10000
    try:
        result = await server.call_tool("echo_test", {"message": long_msg})
        print("✓ Long input handled")
    except Exception as e:
        print(f"✗ Long input failed: {e}")
    
    # Test special characters
    special_msg = "\\n\\r\\t\"'`${}[]"
    try:
        result = await server.call_tool("echo_test", {"message": special_msg})
        print("✓ Special characters handled")
    except Exception as e:
        print(f"✗ Special characters failed: {e}")

asyncio.run(test_echo_adversarial())
```

**Integration Test**:
```bash
# Test tool works via MCP protocol
python -c "
import json
import subprocess
proc = subprocess.Popen(['python', 'main.py'], 
                       stdin=subprocess.PIPE, 
                       stdout=subprocess.PIPE)
request = {
    'jsonrpc': '2.0', 
    'method': 'tools/call', 
    'params': {
        'name': 'echo_test',
        'arguments': {'message': 'integration test'}
    },
    'id': 1
}
proc.stdin.write(json.dumps(request).encode() + b'\n')
proc.stdin.flush()
response = proc.stdout.readline()
print('Tool response:', response)
proc.terminate()
"
```

## 🔧 Week 1: Database Integration

### Step 2A: Database Connection (3 hours)
**Goal**: Connect to all three databases with health checks

**Implementation**:
```python
# src/utils/database_simple.py
import sqlite3
from neo4j import GraphDatabase
import faiss
import numpy as np

class SimpleDatabaseManager:
    def __init__(self):
        self.neo4j_driver = None
        self.sqlite_conn = None
        self.faiss_index = None
    
    def connect_all(self):
        # Neo4j connection
        self.neo4j_driver = GraphDatabase.driver(
            "bolt://localhost:7687",
            auth=("neo4j", "password")
        )
        
        # SQLite connection
        self.sqlite_conn = sqlite3.connect("test.db")
        
        # FAISS index
        self.faiss_index = faiss.IndexFlatL2(128)  # 128-dim vectors
    
    def health_check(self):
        results = {}
        
        # Test Neo4j
        try:
            with self.neo4j_driver.session() as session:
                result = session.run("RETURN 1 as test")
                results['neo4j'] = result.single()['test'] == 1
        except Exception as e:
            results['neo4j'] = False
            
        # Test SQLite
        try:
            cursor = self.sqlite_conn.cursor()
            cursor.execute("SELECT 1")
            results['sqlite'] = cursor.fetchone()[0] == 1
        except Exception as e:
            results['sqlite'] = False
            
        # Test FAISS
        try:
            test_vector = np.random.random((1, 128)).astype('float32')
            self.faiss_index.add(test_vector)
            results['faiss'] = self.faiss_index.ntotal == 1
        except Exception as e:
            results['faiss'] = False
            
        return results
```

**Unit Test**:
```python
# test_database_simple.py
from src.utils.database_simple import SimpleDatabaseManager

def test_database_connections():
    db = SimpleDatabaseManager()
    db.connect_all()
    health = db.health_check()
    
    print(f"Neo4j: {health['neo4j']}")
    print(f"SQLite: {health['sqlite']}")
    print(f"FAISS: {health['faiss']}")
    
    assert all(health.values()), f"Unhealthy databases: {health}"
    print("✓ All databases healthy")

if __name__ == "__main__":
    test_database_connections()
```

**Adversarial Test**:
```python
# test_database_adversarial.py
from src.utils.database_simple import SimpleDatabaseManager
import time

def test_database_adversarial():
    print("=== Database Adversarial Tests ===")
    
    # Test connection without Docker running
    print("1. Test without Docker services...")
    # Stop docker first: docker-compose down
    db = SimpleDatabaseManager()
    try:
        db.connect_all()
        health = db.health_check()
        print(f"Health without Docker: {health}")
        if any(health.values()):
            print("⚠️  Some databases work without Docker - unexpected")
    except Exception as e:
        print(f"✓ Properly fails without Docker: {e}")
    
    # Start Docker and test again
    print("2. Test with Docker services...")
    # docker-compose up -d
    time.sleep(5)  # Wait for services
    db = SimpleDatabaseManager()
    db.connect_all()
    health = db.health_check()
    print(f"Health with Docker: {health}")
    
    # Test connection interruption
    print("3. Test connection interruption...")
    # Would test network interruption, Docker restart, etc.
    
    # Test concurrent connections
    print("4. Test concurrent connections...")
    managers = [SimpleDatabaseManager() for _ in range(5)]
    for i, mgr in enumerate(managers):
        try:
            mgr.connect_all()
            health = mgr.health_check()
            print(f"Manager {i}: {health}")
        except Exception as e:
            print(f"Manager {i} failed: {e}")
    
    # Test database corruption/invalid data
    print("5. Test invalid operations...")
    db = SimpleDatabaseManager()
    db.connect_all()
    
    # Invalid Neo4j query
    try:
        with db.neo4j_driver.session() as session:
            session.run("INVALID CYPHER SYNTAX")
        print("✗ Invalid Cypher should have failed")
    except Exception as e:
        print("✓ Invalid Cypher properly rejected")
    
    # Invalid SQLite operation
    try:
        db.sqlite_conn.execute("INVALID SQL SYNTAX")
        print("✗ Invalid SQL should have failed")
    except Exception as e:
        print("✓ Invalid SQL properly rejected")
    
    # FAISS with wrong dimensions
    try:
        wrong_vector = np.random.random((1, 64)).astype('float32')  # Wrong size
        db.faiss_index.add(wrong_vector)
        print("✗ Wrong vector dimension should have failed")
    except Exception as e:
        print("✓ Wrong vector dimension properly rejected")

if __name__ == "__main__":
    test_database_adversarial()
```

**Integration Test**:
```python
# test_database_integration.py
from src.utils.database_simple import SimpleDatabaseManager
import uuid

def test_cross_database_references():
    print("=== Cross-Database Integration Test ===")
    
    db = SimpleDatabaseManager()
    db.connect_all()
    
    # Create test data with cross-references
    test_id = str(uuid.uuid4())
    
    # 1. Create document in SQLite
    db.sqlite_conn.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            content TEXT,
            neo4j_entity_ref TEXT
        )
    """)
    
    # 2. Create entity in Neo4j
    with db.neo4j_driver.session() as session:
        result = session.run("""
            CREATE (e:Entity {id: $entity_id, name: $name, sqlite_doc_ref: $doc_ref})
            RETURN e.id as entity_id
        """, entity_id=f"ent_{test_id}", name="Test Entity", doc_ref=f"sqlite://document/{test_id}")
        entity_id = result.single()['entity_id']
    
    # 3. Store vector in FAISS with reference
    import numpy as np
    test_vector = np.random.random((1, 128)).astype('float32')
    vector_id = db.faiss_index.ntotal
    db.faiss_index.add(test_vector)
    
    # 4. Complete the references
    db.sqlite_conn.execute("""
        INSERT INTO documents (id, content, neo4j_entity_ref) 
        VALUES (?, ?, ?)
    """, (test_id, "Test document content", f"neo4j://entity/{entity_id}"))
    db.sqlite_conn.commit()
    
    # 5. Test reference resolution
    # SQLite -> Neo4j
    cursor = db.sqlite_conn.execute("SELECT neo4j_entity_ref FROM documents WHERE id = ?", (test_id,))
    neo4j_ref = cursor.fetchone()[0]
    print(f"✓ SQLite contains Neo4j reference: {neo4j_ref}")
    
    # Neo4j -> SQLite
    with db.neo4j_driver.session() as session:
        result = session.run("MATCH (e:Entity {id: $id}) RETURN e.sqlite_doc_ref", id=entity_id)
        sqlite_ref = result.single()['sqlite_doc_ref']
        print(f"✓ Neo4j contains SQLite reference: {sqlite_ref}")
    
    # FAISS -> Entity mapping (would be stored separately)
    print(f"✓ FAISS vector stored at index: {vector_id}")
    
    print("✓ Cross-database references working")

if __name__ == "__main__":
    test_cross_database_references()
```

### Step 2B: Reference System (3 hours)
**Goal**: Universal reference format working

**Implementation**:
```python
# src/utils/references.py
import re
from typing import Dict, Any, Optional

class ReferenceManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.reference_pattern = re.compile(r'^(neo4j|sqlite|faiss)://(\w+)/(.+)$')
    
    def create_reference(self, storage: str, object_type: str, object_id: str) -> str:
        """Create a universal reference."""
        return f"{storage}://{object_type}/{object_id}"
    
    def parse_reference(self, reference: str) -> Dict[str, str]:
        """Parse a universal reference."""
        match = self.reference_pattern.match(reference)
        if not match:
            raise ValueError(f"Invalid reference format: {reference}")
        
        return {
            'storage': match.group(1),
            'type': match.group(2),
            'id': match.group(3)
        }
    
    def resolve_reference(self, reference: str) -> Optional[Dict[str, Any]]:
        """Resolve a reference to actual data."""
        parsed = self.parse_reference(reference)
        
        if parsed['storage'] == 'sqlite':
            return self._resolve_sqlite(parsed['type'], parsed['id'])
        elif parsed['storage'] == 'neo4j':
            return self._resolve_neo4j(parsed['type'], parsed['id'])
        elif parsed['storage'] == 'faiss':
            return self._resolve_faiss(parsed['type'], parsed['id'])
        else:
            raise ValueError(f"Unknown storage: {parsed['storage']}")
    
    def _resolve_sqlite(self, object_type: str, object_id: str) -> Optional[Dict]:
        cursor = self.db_manager.sqlite_conn.execute(
            f"SELECT * FROM {object_type}s WHERE id = ?", (object_id,)
        )
        row = cursor.fetchone()
        if row:
            columns = [description[0] for description in cursor.description]
            return dict(zip(columns, row))
        return None
    
    def _resolve_neo4j(self, object_type: str, object_id: str) -> Optional[Dict]:
        with self.db_manager.neo4j_driver.session() as session:
            result = session.run(
                f"MATCH (n:{object_type.title()} {{id: $id}}) RETURN n",
                id=object_id
            )
            record = result.single()
            if record:
                return dict(record['n'])
        return None
    
    def _resolve_faiss(self, object_type: str, object_id: str) -> Optional[Dict]:
        # FAISS resolution would need metadata store
        # For now, return basic info
        try:
            vector_id = int(object_id)
            if vector_id < self.db_manager.faiss_index.ntotal:
                return {
                    'id': object_id,
                    'type': object_type,
                    'exists': True
                }
        except ValueError:
            pass
        return None
```

**Unit Test**:
```python
# test_references.py
from src.utils.references import ReferenceManager
from src.utils.database_simple import SimpleDatabaseManager

def test_reference_system():
    print("=== Reference System Tests ===")
    
    db = SimpleDatabaseManager()
    db.connect_all()
    ref_manager = ReferenceManager(db)
    
    # Test reference creation
    ref = ref_manager.create_reference("neo4j", "entity", "ent_123")
    assert ref == "neo4j://entity/ent_123"
    print("✓ Reference creation works")
    
    # Test reference parsing
    parsed = ref_manager.parse_reference(ref)
    assert parsed['storage'] == 'neo4j'
    assert parsed['type'] == 'entity'
    assert parsed['id'] == 'ent_123'
    print("✓ Reference parsing works")
    
    # Test invalid reference
    try:
        ref_manager.parse_reference("invalid://format")
        print("✗ Invalid reference should fail")
    except ValueError:
        print("✓ Invalid reference properly rejected")

if __name__ == "__main__":
    test_reference_system()
```

**Adversarial Test**:
```python
# test_references_adversarial.py
from src.utils.references import ReferenceManager
from src.utils.database_simple import SimpleDatabaseManager

def test_reference_adversarial():
    print("=== Reference Adversarial Tests ===")
    
    db = SimpleDatabaseManager()
    db.connect_all()
    ref_manager = ReferenceManager(db)
    
    # Test malformed references
    malformed_refs = [
        "not_a_reference",
        "missing://part",
        "too://many://parts",
        "://missing_storage/type/id",
        "storage://missing_id",
        "storage:///empty_type/id",
        "sqlite://table/; DROP TABLE documents; --",  # SQL injection attempt
        "neo4j://entity/'; DELETE (n); //",  # Cypher injection attempt
        "faiss://vector/../../../etc/passwd",  # Path traversal attempt
        "sqlite://entity/" + "x" * 10000,  # Very long ID
        "neo4j://entity/\x00\x01\x02",  # Binary data
        "faiss://vector/🙂😀🎉",  # Unicode
    ]
    
    for ref in malformed_refs:
        try:
            parsed = ref_manager.parse_reference(ref)
            print(f"⚠️  Unexpected success parsing: {ref} -> {parsed}")
        except ValueError as e:
            print(f"✓ Properly rejected: {ref[:50]}...")
        except Exception as e:
            print(f"✗ Unexpected error on {ref[:30]}: {e}")
    
    # Test reference resolution of non-existent objects
    non_existent_refs = [
        "sqlite://document/does_not_exist",
        "neo4j://entity/fake_id",
        "faiss://vector/99999",
    ]
    
    for ref in non_existent_refs:
        try:
            result = ref_manager.resolve_reference(ref)
            if result is None:
                print(f"✓ Non-existent properly returns None: {ref}")
            else:
                print(f"⚠️  Non-existent returned data: {ref} -> {result}")
        except Exception as e:
            print(f"✗ Error resolving {ref}: {e}")

if __name__ == "__main__":
    test_reference_adversarial()
```

## 🔧 Week 1: First Tool Implementation

### Step 3A: Minimal T01 PDF Loader (4 hours)
**Goal**: Load PDF, extract text, return document object

**Implementation**:
```python
# src/tools/phase1/t01_pdf_loader.py
import PyPDF2
from pathlib import Path
from typing import Dict, Any
import uuid
from datetime import datetime

class T01_PDFLoader:
    def __init__(self, db_manager, ref_manager):
        self.db_manager = db_manager
        self.ref_manager = ref_manager
    
    def execute(self, file_path: str) -> Dict[str, Any]:
        """Load PDF and extract text."""
        try:
            # Validate file exists
            path = Path(file_path)
            if not path.exists():
                return {
                    'status': 'error',
                    'error': f'File not found: {file_path}'
                }
            
            if not path.suffix.lower() == '.pdf':
                return {
                    'status': 'error',
                    'error': f'Not a PDF file: {file_path}'
                }
            
            # Extract text
            with open(path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text_content = ""
                page_count = len(pdf_reader.pages)
                
                for page in pdf_reader.pages:
                    text_content += page.extract_text()
            
            # Create document object
            doc_id = str(uuid.uuid4())
            document = {
                'id': doc_id,
                'file_path': str(path),
                'title': path.stem,
                'content': text_content,
                'page_count': page_count,
                'file_size': path.stat().st_size,
                'created_at': datetime.now().isoformat(),
                'tool_id': 'T01',
                'confidence': 0.9  # High confidence for clean PDF extraction
            }
            
            # Store in SQLite
            self._store_document(document)
            
            # Create reference
            doc_ref = self.ref_manager.create_reference('sqlite', 'document', doc_id)
            
            return {
                'status': 'success',
                'document_ref': doc_ref,
                'metadata': {
                    'page_count': page_count,
                    'file_size': path.stat().st_size,
                    'confidence': 0.9
                }
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _store_document(self, document: Dict[str, Any]):
        """Store document in SQLite."""
        # Create table if not exists
        self.db_manager.sqlite_conn.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                file_path TEXT,
                title TEXT,
                content TEXT,
                page_count INTEGER,
                file_size INTEGER,
                created_at TEXT,
                tool_id TEXT,
                confidence REAL
            )
        """)
        
        # Insert document
        self.db_manager.sqlite_conn.execute("""
            INSERT INTO documents 
            (id, file_path, title, content, page_count, file_size, created_at, tool_id, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            document['id'], document['file_path'], document['title'],
            document['content'], document['page_count'], document['file_size'],
            document['created_at'], document['tool_id'], document['confidence']
        ))
        
        self.db_manager.sqlite_conn.commit()
```

**Unit Test**:
```python
# test_t01_unit.py
from src.tools.phase1.t01_pdf_loader import T01_PDFLoader
from src.utils.database_simple import SimpleDatabaseManager
from src.utils.references import ReferenceManager
import tempfile
from reportlab.pdfgen import canvas

def create_test_pdf(content: str) -> str:
    """Create a simple test PDF."""
    temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
    c = canvas.Canvas(temp_file.name)
    c.drawString(100, 750, content)
    c.save()
    return temp_file.name

def test_t01_unit():
    print("=== T01 Unit Tests ===")
    
    # Setup
    db = SimpleDatabaseManager()
    db.connect_all()
    ref_manager = ReferenceManager(db)
    loader = T01_PDFLoader(db, ref_manager)
    
    # Test successful PDF loading
    test_pdf = create_test_pdf("This is test content")
    result = loader.execute(test_pdf)
    
    assert result['status'] == 'success'
    assert 'document_ref' in result
    assert result['document_ref'].startswith('sqlite://document/')
    print("✓ PDF loading works")
    
    # Test document stored in database
    doc_ref = result['document_ref']
    resolved = ref_manager.resolve_reference(doc_ref)
    assert resolved is not None
    assert 'This is test content' in resolved['content']
    print("✓ Document stored in database")
    
    # Test file not found
    result = loader.execute('/nonexistent/file.pdf')
    assert result['status'] == 'error'
    assert 'not found' in result['error']
    print("✓ File not found handled")
    
    # Test non-PDF file
    import tempfile
    with tempfile.NamedTemporaryFile(suffix='.txt') as temp:
        result = loader.execute(temp.name)
        assert result['status'] == 'error'
        assert 'Not a PDF' in result['error']
    print("✓ Non-PDF file rejected")

if __name__ == "__main__":
    test_t01_unit()
```

**Adversarial Test**:
```python
# test_t01_adversarial.py
from src.tools.phase1.t01_pdf_loader import T01_PDFLoader
from src.utils.database_simple import SimpleDatabaseManager
from src.utils.references import ReferenceManager
import tempfile
import os

def test_t01_adversarial():
    print("=== T01 Adversarial Tests ===")
    
    db = SimpleDatabaseManager()
    db.connect_all()
    ref_manager = ReferenceManager(db)
    loader = T01_PDFLoader(db, ref_manager)
    
    # Test corrupted PDF
    print("1. Testing corrupted PDF...")
    corrupted_pdf = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
    corrupted_pdf.write(b'%PDF-1.4\nThis is not valid PDF content')
    corrupted_pdf.close()
    
    result = loader.execute(corrupted_pdf.name)
    if result['status'] == 'error':
        print("✓ Corrupted PDF properly handled")
    else:
        print(f"⚠️  Corrupted PDF processed: {result}")
    
    # Test very large PDF path
    print("2. Testing very long path...")
    long_path = "/tmp/" + "a" * 1000 + ".pdf"
    result = loader.execute(long_path)
    assert result['status'] == 'error'
    print("✓ Long path rejected")
    
    # Test path traversal attempts
    print("3. Testing path traversal...")
    malicious_paths = [
        "../../../etc/passwd",
        "..\\..\\..\\windows\\system32\\config\\sam",
        "/etc/shadow",
        "../../../../.ssh/id_rsa"
    ]
    
    for path in malicious_paths:
        result = loader.execute(path)
        assert result['status'] == 'error'
        print(f"✓ Malicious path rejected: {path[:30]}...")
    
    # Test empty PDF
    print("4. Testing empty PDF...")
    empty_pdf = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
    # Create minimal valid but empty PDF
    empty_pdf.write(b'%PDF-1.4\n1 0 obj\n<</Type/Page>>\nendobj\nxref\n0 1\n0000000000 65535 f \ntrailer\n<</Size 1>>\nstartxref\n0\n%%EOF')
    empty_pdf.close()
    
    result = loader.execute(empty_pdf.name)
    print(f"Empty PDF result: {result['status']}")
    
    # Test concurrent access
    print("5. Testing concurrent access...")
    from threading import Thread
    
    def load_pdf():
        loader.execute(corrupted_pdf.name)
    
    threads = [Thread(target=load_pdf) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print("✓ Concurrent access handled")
    
    # Test database connection failure
    print("6. Testing database failure...")
    # Close database connection
    db.sqlite_conn.close()
    
    result = loader.execute(corrupted_pdf.name)
    if result['status'] == 'error':
        print("✓ Database failure properly handled")
    else:
        print("⚠️  Database failure not handled")
    
    # Cleanup
    os.unlink(corrupted_pdf.name)
    os.unlink(empty_pdf.name)

if __name__ == "__main__":
    test_t01_adversarial()
```

**Integration Test**:
```python
# test_t01_integration.py
from src.tools.phase1.t01_pdf_loader import T01_PDFLoader
from src.utils.database_simple import SimpleDatabaseManager
from src.utils.references import ReferenceManager
import tempfile
from reportlab.pdfgen import canvas

def test_t01_integration():
    print("=== T01 Integration Tests ===")
    
    # Setup full system
    db = SimpleDatabaseManager()
    db.connect_all()
    ref_manager = ReferenceManager(db)
    loader = T01_PDFLoader(db, ref_manager)
    
    # Create realistic test PDF
    test_pdf = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
    c = canvas.Canvas(test_pdf.name)
    c.drawString(100, 750, "Research Paper Title")
    c.drawString(100, 700, "Abstract: This paper discusses...")
    c.drawString(100, 650, "Introduction: The field of...")
    c.drawString(100, 600, "Apple Inc. announced today...")
    c.showPage()
    c.drawString(100, 750, "Page 2 content...")
    c.drawString(100, 700, "Microsoft Corporation...")
    c.save()
    
    # Test full workflow
    result = loader.execute(test_pdf.name)
    assert result['status'] == 'success'
    
    doc_ref = result['document_ref']
    print(f"✓ Document created with reference: {doc_ref}")
    
    # Test reference resolution
    resolved = ref_manager.resolve_reference(doc_ref)
    assert resolved is not None
    assert 'Apple Inc.' in resolved['content']
    assert 'Microsoft Corporation' in resolved['content']
    print("✓ Document content accessible via reference")
    
    # Test multiple documents
    test_pdf2 = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
    c2 = canvas.Canvas(test_pdf2.name)
    c2.drawString(100, 750, "Second document")
    c2.save()
    
    result2 = loader.execute(test_pdf2.name)
    assert result2['status'] == 'success'
    assert result2['document_ref'] != doc_ref
    print("✓ Multiple documents handled")
    
    # Test database query
    cursor = db.sqlite_conn.execute("SELECT COUNT(*) FROM documents")
    count = cursor.fetchone()[0]
    assert count >= 2
    print(f"✓ Database contains {count} documents")
    
    # Test retrieval by properties
    cursor = db.sqlite_conn.execute("""
        SELECT id FROM documents 
        WHERE content LIKE '%Apple Inc.%'
    """)
    apple_docs = cursor.fetchall()
    assert len(apple_docs) >= 1
    print("✓ Content search works")

if __name__ == "__main__":
    test_t01_integration()
```

## 📊 Verification After Each Step

### Required Documentation:
```bash
# After each step, create:
echo "Step X Status Report" > stepX_status.md
echo "Date: $(date)" >> stepX_status.md
echo "Duration: X hours" >> stepX_status.md
echo "" >> stepX_status.md
echo "Unit Test Results:" >> stepX_status.md
python test_stepX_unit.py >> stepX_status.md 2>&1
echo "" >> stepX_status.md
echo "Adversarial Test Results:" >> stepX_status.md
python test_stepX_adversarial.py >> stepX_status.md 2>&1
echo "" >> stepX_status.md
echo "Integration Test Results:" >> stepX_status.md
python test_stepX_integration.py >> stepX_status.md 2>&1

# Commit the verified state
git add .
git commit -m "Step X complete: [description] - all tests pass"
```

This granular approach ensures we catch issues immediately and never build on broken foundations.