#!/usr/bin/env python3
"""
Run focused validations for remaining Phase RELIABILITY components.
"""

import subprocess
import os
from datetime import datetime
from pathlib import Path

def run_validation(name, config_file, include_files):
    """Run a single focused validation."""
    print(f"\n{'='*60}")
    print(f"Running validation: {name}")
    print(f"Config: {config_file}")
    print(f"Files: {include_files}")
    print('='*60)
    
    # Create focused repomix bundle
    bundle_name = f"{name.lower().replace(' ', '_')}.xml"
    cmd = f'npx repomix --include "{include_files}" --output {bundle_name} .'
    
    print(f"\nCreating bundle with: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Failed to create bundle: {result.stderr}")
        return False
    
    # Check bundle size
    if os.path.exists(bundle_name):
        size_kb = os.path.getsize(bundle_name) / 1024
        print(f"✅ Bundle created: {bundle_name} ({size_kb:.1f}KB)")
        
        if size_kb > 50:
            print(f"⚠️ Warning: Bundle size {size_kb:.1f}KB exceeds recommended 50KB")
    
    # Run validation
    print(f"\nRunning validation...")
    # Note: Would run actual validation here
    # For now, just show what would be done
    print(f"Would run: python gemini_validation.py --bundle {bundle_name} --config {config_file}")
    
    return True

def main():
    """Run all remaining validations."""
    validations = [
        {
            "name": "Entity ID Mapping",
            "config": "validation-entity-id.yaml",
            "files": "src/core/entity_id_manager.py"
        },
        {
            "name": "Citation Provenance",
            "config": "validation-provenance.yaml", 
            "files": "src/core/provenance_manager.py,src/core/citation_validator.py"
        },
        {
            "name": "Connection Pool",
            "config": "validation-connection-pool.yaml",
            "files": "src/core/connection_pool_manager.py"
        },
        {
            "name": "Health Monitor",
            "config": "validation-health-monitor.yaml",
            "files": "src/core/health_monitor.py"
        },
        {
            "name": "Performance Baselines",
            "config": "validation-performance-baselines.yaml",
            "files": "src/monitoring/performance_tracker.py,src/core/sla_monitor.py"
        }
    ]
    
    print(f"Phase RELIABILITY Remaining Validations")
    print(f"Time: {datetime.now().isoformat()}")
    print(f"Total validations: {len(validations)}")
    
    results = []
    for validation in validations:
        success = run_validation(
            validation["name"],
            validation["config"],
            validation["files"]
        )
        results.append((validation["name"], success))
    
    # Summary
    print(f"\n{'='*60}")
    print("VALIDATION SUMMARY")
    print('='*60)
    
    for name, success in results:
        status = "✅ Ready" if success else "❌ Failed"
        print(f"{status} {name}")
    
    # Next steps
    print(f"\n{'='*60}")
    print("NEXT STEPS")
    print('='*60)
    print("1. Review bundle sizes - ensure all are under 50KB")
    print("2. Run actual validations with gemini_validation.py")
    print("3. Address any issues found in validation feedback")
    print("4. Create fixes for any unresolved issues")
    print("5. Re-run validations after fixes")

if __name__ == "__main__":
    main()