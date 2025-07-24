#!/usr/bin/env python3
"""
Complete validation suite for Phase RELIABILITY components.
"""

import os
import sys
import time
import google.generativeai as genai
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment
load_dotenv()

def validate_component(component_name: str, bundle_file: str, validation_prompt: str):
    """Validate a single component."""
    print(f"\n{'='*60}")
    print(f"Validating: {component_name}")
    print(f"{'='*60}\n")
    
    # Check bundle exists
    if not Path(bundle_file).exists():
        print(f"❌ Bundle not found: {bundle_file}")
        return False, "Bundle not found"
    
    # Read bundle
    with open(bundle_file, 'r') as f:
        codebase_content = f.read()
    
    size_kb = len(codebase_content) / 1024
    print(f"📊 Bundle size: {size_kb:.1f}KB")
    
    # Configure Gemini
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY not found")
        return False, "API key missing"
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # Create prompt
    full_prompt = f"""
You are a critical code reviewer. Your task is to validate specific claims about the implementation.

{validation_prompt}

CODEBASE:
{codebase_content}

Provide a verdict:
- ✅ FULLY RESOLVED: If all checks pass with evidence
- ⚠️ PARTIALLY RESOLVED: If some checks pass but others fail
- ❌ NOT RESOLVED: If critical checks fail

Include specific evidence from the code to support your verdict.
"""
    
    # Send to Gemini
    print("🤖 Validating with Gemini AI...")
    try:
        response = model.generate_content(full_prompt)
        result = response.text
        
        # Save result
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path(f"reliability-validations/results/{timestamp}")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / f"{component_name.lower().replace(' ', '_')}_validation.md"
        with open(output_file, 'w') as f:
            f.write(f"# {component_name} Validation\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n\n")
            f.write("---\n\n")
            f.write(result)
        
        # Determine status
        if "✅ FULLY RESOLVED" in result:
            status = "FULLY RESOLVED"
            print("🎉 Component FULLY RESOLVED!")
        elif "⚠️ PARTIALLY RESOLVED" in result:
            status = "PARTIALLY RESOLVED"
            print("⚠️  Component PARTIALLY RESOLVED")
        elif "❌ NOT RESOLVED" in result:
            status = "NOT RESOLVED"
            print("❌ Component NOT RESOLVED")
        else:
            status = "UNKNOWN"
            print("❓ Unable to determine status")
        
        return True, status
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return False, f"Error: {e}"


def main():
    """Run all reliability validations."""
    
    validations = [
        {
            "name": "Distributed Transactions",
            "bundle": "reliability-distributed-tx.xml",
            "prompt": """Validate ONLY this specific claim:

**CLAIM**: Distributed transaction manager implements two-phase commit across Neo4j and SQLite

SPECIFIC CHECKS:
1. TransactionState enum with states: PREPARING, PREPARED, COMMITTING, COMMITTED, ABORTING, ABORTED
2. DistributedTransactionManager class with required methods
3. Two-phase commit protocol in commit_all() method
4. Proper rollback handling in rollback_all() method"""
        },
        {
            "name": "Entity ID Mapping",
            "bundle": "reliability-entity-id.xml",
            "prompt": """Validate ONLY this specific claim:

**CLAIM**: Entity ID manager provides bidirectional mapping with collision detection

SPECIFIC CHECKS:
1. EntityIDManager class with bidirectional mapping dictionaries
2. generate_entity_id() with collision detection
3. Persistent storage of ID mappings
4. Thread-safe ID generation"""
        },
        {
            "name": "Provenance Tracking",
            "bundle": "reliability-provenance.xml",
            "prompt": """Validate ONLY this specific claim:

**CLAIM**: Provenance manager tracks citation sources and prevents fabrication

SPECIFIC CHECKS:
1. ProvenanceManager class with citation tracking
2. create_citation() method with source validation
3. Provenance chain tracking for modifications
4. Fabrication detection logic"""
        },
        {
            "name": "Async Patterns",
            "bundle": "reliability-async.xml",
            "prompt": """Validate ONLY these specific claims:

**CLAIM 1**: AsyncRateLimiter uses non-blocking async patterns
**CLAIM 2**: AsyncErrorHandler implements async retry logic

SPECIFIC CHECKS:
1. NO time.sleep() calls anywhere
2. Uses await asyncio.sleep() for delays
3. Token bucket algorithm in rate limiter
4. Exponential backoff in error handler"""
        },
        {
            "name": "Connection Pooling",
            "bundle": "reliability-connection-pool.xml",
            "prompt": """Validate ONLY this specific claim:

**CLAIM**: Connection pool manager handles resource exhaustion gracefully

SPECIFIC CHECKS:
1. ConnectionPoolManager class with min_size and max_size
2. Dynamic pool resizing capability
3. Health check loop for connections
4. Graceful handling of pool exhaustion"""
        },
        {
            "name": "Thread Safety",
            "bundle": "reliability-thread-safety.xml",
            "prompt": """Validate ONLY this specific claim:

**CLAIM**: ThreadSafeServiceManager eliminates race conditions with proper locking

SPECIFIC CHECKS:
1. Singleton pattern with double-check locking
2. Service-specific locks in _service_locks dictionary
3. Thread-safe service registration and retrieval
4. atomic_operation context manager"""
        },
        {
            "name": "Error Handling",
            "bundle": "reliability-error-handling.xml",
            "prompt": """Validate ONLY this specific claim:

**CLAIM**: Unified error taxonomy with categorization and recovery strategies

SPECIFIC CHECKS:
1. ErrorCategory enum with comprehensive categories
2. ErrorSeverity levels (CRITICAL, HIGH, MEDIUM, LOW)
3. CentralizedErrorHandler class
4. Recovery strategy mapping"""
        },
        {
            "name": "Health Monitoring",
            "bundle": "reliability-health.xml",
            "prompt": """Validate ONLY this specific claim:

**CLAIM**: Health monitor provides real-time system monitoring with alerts

SPECIFIC CHECKS:
1. SystemHealthMonitor class with background monitoring
2. MetricsCollector for CPU, memory, disk usage
3. AlertManager with configurable thresholds
4. Health check endpoint decorator"""
        }
    ]
    
    print("🔧 Phase RELIABILITY Complete Validation Suite")
    print("=" * 60)
    print(f"Total components: {len(validations)}")
    print("Each validation uses focused context (<50KB)\n")
    
    results = []
    
    for i, val in enumerate(validations, 1):
        print(f"\n[{i}/{len(validations)}] {val['name']}")
        success, status = validate_component(val["name"], val["bundle"], val["prompt"])
        results.append({
            "component": val["name"],
            "success": success,
            "status": status
        })
        
        # Brief pause between API calls
        if i < len(validations):
            time.sleep(3)
    
    # Summary
    print(f"\n\n{'='*60}")
    print("VALIDATION SUMMARY")
    print(f"{'='*60}\n")
    
    fully_resolved = sum(1 for r in results if r["status"] == "FULLY RESOLVED")
    partially_resolved = sum(1 for r in results if r["status"] == "PARTIALLY RESOLVED")
    not_resolved = sum(1 for r in results if r["status"] == "NOT RESOLVED")
    failed = sum(1 for r in results if not r["success"])
    
    for r in results:
        status_icon = {
            "FULLY RESOLVED": "✅",
            "PARTIALLY RESOLVED": "⚠️",
            "NOT RESOLVED": "❌",
            "UNKNOWN": "❓"
        }.get(r["status"], "❓")
        
        print(f"{status_icon} {r['component']:25} - {r['status']}")
    
    print(f"\n{'='*60}")
    print(f"✅ Fully Resolved:     {fully_resolved}/{len(validations)}")
    print(f"⚠️  Partially Resolved: {partially_resolved}/{len(validations)}")
    print(f"❌ Not Resolved:       {not_resolved}/{len(validations)}")
    print(f"💥 Failed Validations: {failed}/{len(validations)}")
    print(f"{'='*60}")
    
    if fully_resolved == len(validations):
        print("\n🎉 ALL COMPONENTS FULLY RESOLVED! Phase RELIABILITY is complete!")
    elif fully_resolved + partially_resolved == len(validations):
        print("\n⚠️  Some components need minor fixes. Review partially resolved items.")
    else:
        print("\n❌ Critical issues found. Address not resolved components.")


if __name__ == "__main__":
    main()