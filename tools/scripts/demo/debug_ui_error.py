#!/usr/bin/env python3
"""Debug script to diagnose the UI error"""

import sys
import os
from pathlib import Path
import platform
import tempfile

# No sys.path manipulation needed - using proper imports

print("=== Environment Info ===")
print(f"Platform: {platform.system()}")
print(f"Release: {platform.release()}")
print(f"Is WSL: {'Microsoft' in platform.release() or 'WSL' in platform.release()}")
print(f"Python Version: {sys.version}")
print(f"Working Directory: {os.getcwd()}")
print(f"Temp Directory: {tempfile.gettempdir()}")
print()

# Test file permissions in temp directory
print("=== Testing Temp Directory ===")
temp_dir = Path(tempfile.gettempdir())
print(f"Temp dir exists: {temp_dir.exists()}")
print(f"Temp dir writable: {os.access(temp_dir, os.W_OK)}")

# Create a test file
try:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf", prefix="test_") as f:
        test_path = f.name
        f.write(b"%PDF-1.4\nTest content")
    
    print(f"Created test file: {test_path}")
    print(f"Test file exists: {os.path.exists(test_path)}")
    print(f"Test file size: {os.path.getsize(test_path)} bytes")
    print(f"Test file readable: {os.access(test_path, os.R_OK)}")
    
    # Clean up
    os.unlink(test_path)
    print("Test file deleted successfully")
except Exception as e:
    print(f"Error creating test file: {e}")
    import traceback
    traceback.print_exc()

print()

# Test workflow imports
print("=== Testing Imports ===")
try:
    from tools.phase1.vertical_slice_workflow import VerticalSliceWorkflow
    print("✓ VerticalSliceWorkflow imported")
except Exception as e:
    print(f"✗ VerticalSliceWorkflow import failed: {e}")

try:
    from tools.phase1.t01_pdf_loader import PDFLoader
    print("✓ PDFLoader imported")
except Exception as e:
    print(f"✗ PDFLoader import failed: {e}")

try:
    from core.identity_service import IdentityService
    print("✓ IdentityService imported")
except Exception as e:
    print(f"✗ IdentityService import failed: {e}")

print()

# Test Neo4j connection
print("=== Testing Neo4j ===")
try:
    from neo4j import GraphDatabase
    import sys
    from pathlib import Path
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))
    
    from src.core.config_manager import ConfigManager
    
    config_manager = ConfigManager()
    neo4j_config = config_manager.get_neo4j_config()
    auth = None if neo4j_config['user'] is None else (neo4j_config['user'], neo4j_config['password'])
    driver = GraphDatabase.driver(neo4j_config['uri'], auth=auth)
    with driver.session() as session:
        result = session.run("RETURN 1 as num")
        print(f"✓ Neo4j connected: {result.single()['num']}")
    driver.close()
except Exception as e:
    print(f"✗ Neo4j connection failed: {e}")

print()

# Test PDF processing with a minimal file
print("=== Testing PDF Processing ===")
try:
    # Create a minimal PDF file
    minimal_pdf = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> /MediaBox [0 0 612 792] /Contents 4 0 R >>
endobj
4 0 obj
<< /Length 44 >>
stream
BT
/F1 12 Tf
100 700 Td
(Test PDF) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000293 00000 n 
trailer
<< /Size 5 /Root 1 0 R >>
startxref
381
%%EOF"""

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
        f.write(minimal_pdf)
        pdf_path = f.name
    
    print(f"Created minimal PDF: {pdf_path}")
    
    # Try to initialize workflow
    workflow = VerticalSliceWorkflow(workflow_storage_dir="./data/debug_test")
    print("✓ Workflow initialized")
    
    # Try to process the PDF
    print("Attempting to process PDF...")
    result = workflow.execute_workflow(
        pdf_path=pdf_path,
        query="What is this document about?",
        workflow_name="Debug_Test"
    )
    
    print(f"Result status: {result.get('status')}")
    if result.get('status') == 'error' or result.get('status') == 'failed':
        print(f"Error: {result.get('error')}")
        if 'traceback' in result:
            print("Traceback:")
            print(result['traceback'])
    else:
        print("✓ PDF processed successfully")
        if 'workflow_summary' in result:
            print(f"Summary: {result['workflow_summary']}")
    
    # Clean up
    os.unlink(pdf_path)
    
except Exception as e:
    print(f"✗ PDF processing failed: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Debug Complete ===")