#!/usr/bin/env python3
"""
Validate Phase RELIABILITY components using focused Gemini validation.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List

# Component mapping
COMPONENTS = {
    "distributed-tx": {
        "config": "01-distributed-transactions.yaml",
        "files": ["src/core/distributed_transaction_manager.py"],
        "name": "Distributed Transactions"
    },
    "entity-id": {
        "config": "02-entity-id-mapping.yaml", 
        "files": ["src/core/entity_id_manager.py"],
        "name": "Entity ID Mapping"
    },
    "provenance": {
        "config": "03-provenance-tracking.yaml",
        "files": ["src/core/provenance_manager.py"],
        "name": "Provenance Tracking"
    },
    "async": {
        "config": "04-async-patterns.yaml",
        "files": ["src/core/async_rate_limiter.py", "src/core/async_error_handler.py"],
        "name": "Async Patterns"
    },
    "connection-pool": {
        "config": "05-connection-pooling.yaml",
        "files": ["src/core/connection_pool_manager.py"],
        "name": "Connection Pooling"
    },
    "thread-safety": {
        "config": "06-thread-safety.yaml",
        "files": ["src/core/thread_safe_service_manager.py"],
        "name": "Thread Safety"
    },
    "error-handling": {
        "config": "07-error-handling.yaml",
        "files": ["src/core/error_taxonomy.py"],
        "name": "Error Handling"
    },
    "health": {
        "config": "08-health-monitoring.yaml",
        "files": ["src/core/health_monitor.py"],
        "name": "Health Monitoring"
    }
}


def create_bundle(component: str, base_dir: Path) -> Path:
    """Create focused repomix bundle for component."""
    comp_info = COMPONENTS[component]
    bundle_path = base_dir / "bundles" / f"{component}-bundle.xml"
    
    # Build file list
    file_list = ",".join(comp_info["files"])
    
    # Run repomix from project root
    project_root = base_dir.parent.parent
    cmd = [
        "npx", "repomix",
        "--include", file_list,
        "--output", str(bundle_path),
        str(project_root)
    ]
    
    print(f"Creating bundle for {comp_info['name']}...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error creating bundle: {result.stderr}")
        sys.exit(1)
    
    # Check bundle size
    size_kb = bundle_path.stat().st_size / 1024
    print(f"Bundle created: {bundle_path.name} ({size_kb:.1f}KB)")
    
    if size_kb > 50:
        print("⚠️  Warning: Bundle exceeds 50KB recommendation")
    
    return bundle_path


def run_validation(component: str, base_dir: Path, bundle_path: Path) -> None:
    """Run Gemini validation for component."""
    comp_info = COMPONENTS[component]
    config_path = base_dir / "configs" / comp_info["config"]
    
    # Run gemini_review.py
    cmd = [
        sys.executable,
        str(base_dir.parent / "gemini_review.py"),
        "--config", str(config_path),
        "--bundle", str(bundle_path)
    ]
    
    print(f"\nValidating {comp_info['name']}...")
    result = subprocess.run(cmd)
    
    if result.returncode != 0:
        print(f"Validation failed with exit code {result.returncode}")
    else:
        print(f"✅ Validation completed for {comp_info['name']}")


def validate_all(base_dir: Path) -> None:
    """Run all validations sequentially."""
    print("Running all Phase RELIABILITY validations...\n")
    
    for component in COMPONENTS:
        print(f"\n{'='*60}")
        print(f"Component: {COMPONENTS[component]['name']}")
        print(f"{'='*60}")
        
        bundle_path = create_bundle(component, base_dir)
        run_validation(component, base_dir, bundle_path)
        
        print("\nPress Enter to continue to next validation...")
        input()


def main():
    parser = argparse.ArgumentParser(
        description="Validate Phase RELIABILITY components"
    )
    parser.add_argument(
        "--component",
        choices=list(COMPONENTS.keys()) + ["all"],
        default="all",
        help="Component to validate (default: all)"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available components"
    )
    
    args = parser.parse_args()
    
    # Get base directory
    base_dir = Path(__file__).parent.parent
    
    if args.list:
        print("Available components:")
        for key, info in COMPONENTS.items():
            print(f"  {key:15} - {info['name']}")
        return
    
    if args.component == "all":
        validate_all(base_dir)
    else:
        bundle_path = create_bundle(args.component, base_dir)
        run_validation(args.component, base_dir, bundle_path)


if __name__ == "__main__":
    main()