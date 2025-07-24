#!/usr/bin/env python3
"""
Direct Gemini validation for Phase RELIABILITY using pre-built bundle.
"""

import os
import google.generativeai as genai
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment
load_dotenv()

def run_validation():
    """Run Phase RELIABILITY validation."""
    
    # Read the pre-built bundle
    bundle_path = Path("phase-reliability-bundle.xml")
    if not bundle_path.exists():
        print("❌ Bundle not found. Run: npx repomix --include 'src/core/*.py' --output phase-reliability-bundle.xml ..")
        return
    
    print("📖 Reading Phase RELIABILITY bundle...")
    with open(bundle_path, 'r') as f:
        codebase_content = f.read()
    
    print(f"📊 Bundle size: {len(codebase_content) / 1024:.1f}KB")
    
    # Configure Gemini
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY not found")
        return
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # Create validation prompt
    prompt = """
You are a critical code reviewer. Validate that Phase RELIABILITY implementation is 100% complete with all 8 core components fully implemented and working.

VALIDATION OBJECTIVE: Verify all reliability components are production-ready with no stubs or placeholders.

For each component, verify:
1. Complete implementation (no TODOs, stubs, or placeholders)
2. All required methods present and functional
3. Proper error handling and recovery mechanisms
4. Thread safety where applicable
5. Async patterns correctly implemented

SPECIFIC VALIDATION CRITERIA:

1. **Distributed Transaction Manager** (distributed_transaction_manager.py):
   - Two-phase commit protocol implemented
   - TransactionState enum with all states
   - Methods: begin_transaction, prepare_neo4j, prepare_sqlite, commit_all, rollback_all
   - Proper rollback on failure

2. **Entity ID Manager** (entity_id_manager.py):
   - Bidirectional mapping dictionaries (neo4j_to_sqlite, sqlite_to_neo4j)
   - Collision detection in generate_entity_id
   - Thread-safe ID generation with locks
   - Persistence methods (save_mappings, load_mappings)

3. **Provenance Manager** (provenance_manager.py):
   - Citation tracking with source validation
   - create_citation method validates sources
   - track_modification creates audit trail
   - detect_fabrication checks citation validity

4. **Async Rate Limiter** (async_rate_limiter.py):
   - Token bucket algorithm implementation
   - NO time.sleep() calls
   - Uses asyncio.sleep() for delays
   - acquire() method is truly async

5. **Async Error Handler** (async_error_handler.py):
   - Non-blocking retry mechanism
   - Exponential backoff implementation
   - handle_with_retry is async
   - No blocking operations

6. **Connection Pool Manager** (connection_pool_manager.py):
   - Dynamic pool sizing (min_size, max_size)
   - Health check loop (_health_check_loop)
   - Graceful exhaustion handling
   - acquire_connection with timeout

7. **Thread Safe Service Manager** (thread_safe_service_manager.py):
   - Double-check locking in __new__ for singleton
   - atomic_operation with _instance_lock protection (lines 342-346)
   - Service-specific locks in _service_locks
   - No race conditions

8. **Error Taxonomy** (error_taxonomy.py):
   - ErrorCategory and ErrorSeverity enums
   - CentralizedErrorHandler class
   - Recovery strategies registered with enum values (lines 159-164)
   - _attempt_recovery uses strategy.value for lookup

9. **Health Monitor** (health_monitor.py):
   - SystemHealthMonitor class
   - Background monitoring loop
   - MetricsCollector for CPU/memory/disk
   - AlertManager with thresholds

CLAIMS TO VALIDATE:
- "All 8 core reliability components are fully implemented with no stubs"
- "Distributed transactions use proper two-phase commit protocol"
- "Entity ID mapping prevents data corruption with collision detection"
- "All async operations are non-blocking with no time.sleep() calls"
- "Thread safety fixed with proper locking in atomic_operation"
- "Error recovery strategies correctly mapped using enum values"
- "Connection pooling handles resource exhaustion gracefully"
- "Health monitoring provides real-time system metrics"

CODEBASE:
""" + codebase_content + """

For each claim, provide verdict:
- ✅ FULLY RESOLVED: Implementation complete and meets all requirements
- ⚠️ PARTIALLY RESOLVED: Implementation present but incomplete
- ❌ NOT RESOLVED: Implementation missing or doesn't meet requirements

Be thorough and reference specific line numbers where possible.
"""
    
    print("🤖 Sending to Gemini for validation...")
    try:
        response = model.generate_content(prompt)
        result = response.text
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path(f"outputs/{timestamp}")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / "phase_reliability_validation.md"
        with open(output_file, 'w') as f:
            f.write(f"# Phase RELIABILITY Validation Results\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write(f"Tool: Direct Gemini Validation\n\n")
            f.write("---\n\n")
            f.write(result)
        
        print(f"\n✅ Validation complete!")
        print(f"📄 Results saved to: {output_file}")
        
        # Print summary
        print("\n" + "="*60)
        print("VALIDATION SUMMARY")
        print("="*60 + "\n")
        
        if "✅ FULLY RESOLVED" in result:
            fully_resolved = result.count("✅ FULLY RESOLVED")
            print(f"✅ Fully Resolved Claims: {fully_resolved}")
        if "⚠️ PARTIALLY RESOLVED" in result:
            partial = result.count("⚠️ PARTIALLY RESOLVED")
            print(f"⚠️  Partially Resolved: {partial}")
        if "❌ NOT RESOLVED" in result:
            not_resolved = result.count("❌ NOT RESOLVED")
            print(f"❌ Not Resolved: {not_resolved}")
            
    except Exception as e:
        print(f"❌ Validation failed: {e}")


if __name__ == "__main__":
    run_validation()