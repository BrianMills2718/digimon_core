#!/usr/bin/env python
"""Test PDF loading performance."""

import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from src.utils.database import DatabaseManager
from src.tools.phase1.t01_pdf_loader import PDFDocumentLoader

print("=== PDF LOADING TEST ===\n")

# Initialize
db = DatabaseManager()
db.faiss.dimension = 384
db.initialize()

# Clear
with db.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")

# First create the test PDF
print("Creating test PDF...")
import create_test_pdf
create_test_pdf.create_research_paper()

# Time PDF loading
print("\nLoading PDF...")
loader = PDFDocumentLoader(db)
pdf_path = Path("graphrag_research_paper.pdf")

start_time = time.time()
try:
    pdf_result = loader.load_pdf(pdf_path)
    elapsed = time.time() - start_time
    print(f"\n✓ PDF loaded in {elapsed:.2f} seconds")
    print(f"  Pages: {pdf_result['page_count']}")
    print(f"  Document ref: {pdf_result['document_ref']}")
except Exception as e:
    elapsed = time.time() - start_time
    print(f"\n✗ PDF loading failed after {elapsed:.2f} seconds")
    print(f"  Error: {e}")
    import traceback
    traceback.print_exc()

# Cleanup
pdf_path.unlink()
with db.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")
db.close()