#!/usr/bin/env python3
"""
Direct validation of CLAUDE.md Phase 2 implementation claims
Bypasses repomix permission issues by creating validation bundle directly
"""

import os
import sys
import google.generativeai as genai
from pathlib import Path
import json
from datetime import datetime

def create_validation_bundle():
    """Create a focused validation bundle with only the implementation files"""
    
    bundle_content = """# CLAUDE.md Phase 2 Critical Implementation Validation Bundle

This bundle contains ONLY the 5 specific files containing the implementations being validated.

## Validation Claims:
This bundle validates 15 specific claims from CLAUDE.md Phase 2 implementation fixes.

## Files Included:
1. src/tools/phase2/async_multi_document_processor.py
2. src/core/metrics_collector.py
3. src/core/backup_manager.py  
4. tests/performance/test_real_performance.py
5. requirements.txt

---

"""
    
    # File paths to include
    files_to_include = [
        "src/tools/phase2/async_multi_document_processor.py",
        "src/core/metrics_collector.py",
        "src/core/backup_manager.py",
        "tests/performance/test_real_performance.py",
        "requirements.txt"
    ]
    
    # Add each file content
    for file_path in files_to_include:
        full_path = Path(file_path)
        if full_path.exists():
            bundle_content += f"\n## FILE: {file_path}\n\n"
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Add line numbers
                    lines = content.split('\n')
                    numbered_lines = [f"{i+1:4d}→{line}" for i, line in enumerate(lines)]
                    bundle_content += '\n'.join(numbered_lines)
                    bundle_content += "\n\n---\n"
            except Exception as e:
                bundle_content += f"ERROR reading file: {e}\n\n---\n"
        else:
            bundle_content += f"\n## FILE: {file_path}\n\nERROR: File not found\n\n---\n"
    
    return bundle_content

def get_validation_prompt():
    """Get the validation prompt with specific claims"""
    
    return """You are validating specific implementation claims from CLAUDE.md Phase 2 fixes. 

For each claim below, examine the specified file and provide a precise verdict:

VALIDATION CRITERIA:
- ✅ FULLY RESOLVED: Implementation exists, is complete, and meets all requirements
- ⚠️ PARTIALLY RESOLVED: Implementation exists but is incomplete or doesn't fully meet requirements  
- ❌ NOT RESOLVED: Implementation missing, is a stub/placeholder, or doesn't meet requirements

CLAIMS TO VALIDATE:

### TASK 1: AsyncMultiDocumentProcessor (src/tools/phase2/async_multi_document_processor.py)

**CLAIM_1A_REAL_DOCUMENT_LOADING**: Method `_load_document_async` contains actual document loading logic using PDFLoader for PDF files, aiofiles for text files, and python-docx for Word documents - NOT simulated loading with fake content generation.

**CLAIM_1B_REAL_ENTITY_EXTRACTION**: Method `_extract_entities_for_query_async` uses actual SpaCy NER and RelationshipExtractor from phase1 tools - NOT simulated entity extraction with fake counts.

**CLAIM_1C_REAL_PERFORMANCE_MEASUREMENT**: Method `measure_performance_improvement` contains actual sequential vs parallel processing comparison with genuine timing measurements - NOT simulated timing with asyncio.sleep().

**CLAIM_1D_NO_SIMULATED_PROCESSING**: NO asyncio.sleep() calls used anywhere in the file for simulating processing time.

### TASK 2: MetricsCollector (src/core/metrics_collector.py)

**CLAIM_2A_41_METRICS_IMPLEMENTED**: Method `_initialize_metrics` defines exactly 41 KGAS-specific metrics with proper Prometheus types (Counter, Histogram, Gauge).

**CLAIM_2B_METRIC_VERIFICATION**: Method `verify_metric_count` dynamically counts actual metric objects and compares against expected 41 metrics.

**CLAIM_2C_FAIL_FAST_VALIDATION**: Method `_initialize_metrics` raises ConfigurationError if metric count is not exactly 41.

### TASK 3: BackupManager (src/core/backup_manager.py)

**CLAIM_3A_INCREMENTAL_BACKUP_LOGIC**: Contains `_perform_incremental_backup` method that compares file modification times against last backup timestamp for real incremental processing.

**CLAIM_3B_REAL_ENCRYPTION**: Contains `_encrypt_backup_file` method using actual cryptography library with Fernet encryption and PBKDF2 key derivation.

**CLAIM_3C_ENCRYPTION_KEY_GENERATION**: Contains `_get_encryption_key` method that generates real encryption keys with proper salt and secure storage.

### TASK 4: Performance Testing (tests/performance/test_real_performance.py)

**CLAIM_4A_REAL_PERFORMANCE_TEST**: Method `test_real_parallel_vs_sequential_performance` performs actual sequential vs parallel processing comparison with genuine timing.

**CLAIM_4B_REALISTIC_CONTENT_GENERATION**: Method `_generate_realistic_content` creates documents with named entities and realistic content for testing.

### TASK 6: Dependencies (requirements.txt)

**CLAIM_6A_ASYNC_DEPENDENCIES**: Contains `aiofiles>=23.2.0` and `python-docx>=0.8.11` for async document processing.

**CLAIM_6B_ENCRYPTION_DEPENDENCIES**: Contains `cryptography>=41.0.0` for encryption functionality.

**CLAIM_6C_METRICS_DEPENDENCIES**: Contains `prometheus-client>=0.17.0` and `psutil>=5.9.0` for metrics collection.

VALIDATION REQUIREMENTS:
1. Reference specific line numbers when analyzing code
2. Verify method names match exactly as claimed
3. Check that implementations are complete (not stubs or placeholders)
4. Confirm dependencies are present with correct version requirements
5. Validate that no simulated processing (asyncio.sleep) remains

Provide your verdict for each claim using the exact claim names above.
"""

def run_validation():
    """Run the validation using Gemini API directly"""
    
    # Initialize Gemini
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment")
        return
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # Create validation bundle
    print("📦 Creating validation bundle...")
    bundle_content = create_validation_bundle()
    
    # Get validation prompt  
    validation_prompt = get_validation_prompt()
    
    # Combine prompt and bundle
    full_prompt = f"{validation_prompt}\n\n--- CODE BUNDLE ---\n\n{bundle_content}"
    
    print("🚀 Running Gemini validation...")
    
    try:
        response = model.generate_content(full_prompt)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"validation-reports/claude-phase2-direct-validation-{timestamp}.md"
        
        os.makedirs("validation-reports", exist_ok=True)
        
        with open(output_file, 'w') as f:
            f.write(f"# CLAUDE.md Phase 2 Direct Validation Results\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Method**: Direct Gemini API validation\n")
            f.write(f"**Model**: gemini-2.5-flash\n\n")
            f.write("---\n\n")
            f.write(response.text)
        
        print(f"✅ Validation complete! Results saved to: {output_file}")
        print(f"📄 Results:\n{response.text}")
        
        return output_file
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return None

if __name__ == "__main__":
    run_validation()