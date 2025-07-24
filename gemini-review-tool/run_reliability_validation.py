#!/usr/bin/env python3
"""
Run focused reliability component validations.
"""

import subprocess
import sys
from pathlib import Path

def run_validation(component_name: str, config_file: str, include_patterns: list):
    """Run a single component validation."""
    print(f"\n{'='*60}")
    print(f"Validating: {component_name}")
    print(f"{'='*60}\n")
    
    # Create repomix bundle
    bundle_name = f"reliability-{component_name.lower().replace(' ', '-')}.xml"
    include_str = ",".join(include_patterns)
    
    cmd = [
        "npx", "repomix",
        "--include", include_str,
        "--output", bundle_name,
        "."
    ]
    
    print(f"Creating bundle with: {include_str}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error creating bundle: {result.stderr}")
        return False
    
    # Check bundle size
    bundle_path = Path(bundle_name)
    if bundle_path.exists():
        size_kb = bundle_path.stat().st_size / 1024
        print(f"Bundle size: {size_kb:.1f}KB")
        
        if size_kb > 50:
            print("⚠️  Warning: Bundle exceeds 50KB - may cause issues")
    
    # Run validation
    cmd = [
        sys.executable,
        "gemini_review.py",
        "--config", config_file
    ]
    
    print(f"\nRunning validation...")
    result = subprocess.run(cmd)
    
    return result.returncode == 0


def main():
    """Run all reliability validations."""
    
    validations = [
        {
            "name": "Distributed Transactions",
            "config": "reliability-validations/configs/01-distributed-transactions.yaml",
            "files": ["src/core/distributed_transaction_manager.py"]
        },
        {
            "name": "Entity ID Mapping",
            "config": "reliability-validations/configs/02-entity-id-mapping.yaml",
            "files": ["src/core/entity_id_manager.py"]
        },
        {
            "name": "Provenance Tracking",
            "config": "reliability-validations/configs/03-provenance-tracking.yaml",
            "files": ["src/core/provenance_manager.py"]
        },
        {
            "name": "Async Patterns",
            "config": "reliability-validations/configs/04-async-patterns.yaml",
            "files": ["src/core/async_rate_limiter.py", "src/core/async_error_handler.py"]
        },
        {
            "name": "Connection Pooling",
            "config": "reliability-validations/configs/05-connection-pooling.yaml",
            "files": ["src/core/connection_pool_manager.py"]
        },
        {
            "name": "Thread Safety",
            "config": "reliability-validations/configs/06-thread-safety.yaml",
            "files": ["src/core/thread_safe_service_manager.py"]
        },
        {
            "name": "Error Handling",
            "config": "reliability-validations/configs/07-error-handling.yaml",
            "files": ["src/core/error_taxonomy.py"]
        },
        {
            "name": "Health Monitoring",
            "config": "reliability-validations/configs/08-health-monitoring.yaml",
            "files": ["src/core/health_monitor.py"]
        }
    ]
    
    print("Phase RELIABILITY Component Validations")
    print("=" * 60)
    print(f"Total validations: {len(validations)}")
    print("Each validation will be run with focused context\n")
    
    success_count = 0
    
    for val in validations:
        if run_validation(val["name"], val["config"], val["files"]):
            success_count += 1
            print(f"✅ {val['name']} validation completed\n")
        else:
            print(f"❌ {val['name']} validation failed\n")
        
        # Pause between validations
        if val != validations[-1]:
            input("Press Enter to continue to next validation...")
    
    print(f"\n{'='*60}")
    print(f"Validation Summary: {success_count}/{len(validations)} successful")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()