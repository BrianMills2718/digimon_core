#!/usr/bin/env python3
"""
EXECUTE PDF WORKFLOW - REAL TEST
Actually execute the PDF workflow with a real PDF and question
"""

import sys
import json
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.tools.phase1.vertical_slice_workflow import VerticalSliceWorkflow

# Initialize workflow
workflow_storage_dir = "./data/workflows"
vertical_slice = VerticalSliceWorkflow(workflow_storage_dir=workflow_storage_dir)

# Test parameters
pdf_path = "examples/pdfs/climate_report.pdf"
query = "What is the main subject of this document?"
workflow_name = "Real_PDF_Test"

print(f"Executing PDF workflow...")
print(f"PDF: {pdf_path}")
print(f"Query: {query}")
print(f"Workflow name: {workflow_name}")
print("-" * 80)

try:
    # Actually execute the workflow
    result = vertical_slice.execute_workflow(
        pdf_path=pdf_path,
        query=query,
        workflow_name=workflow_name
    )
    
    print("RESPONSE:")
    print(json.dumps(result, indent=2, default=str))
    
except Exception as e:
    print(f"ERROR: {str(e)}")
    print(f"Traceback:\n{traceback.format_exc()}")