#!/usr/bin/env python3
"""
Contract Validation Script for CI/CD Integration

This script validates all tool contracts in the project and can be integrated
into CI/CD pipelines to ensure tool compatibility is maintained.

Usage:
    python scripts/validate_contracts.py [--contracts-dir contracts] [--verbose] [--output report.json]
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any

# Add src to path for imports

from core.contract_validator import (
    ContractValidator, 
    validate_all_contracts,
    generate_compatibility_matrix
)


def main():
    """Main entry point for contract validation"""
    parser = argparse.ArgumentParser(
        description="Validate tool contracts for compatibility"
    )
    parser.add_argument(
        "--contracts-dir", 
        default="contracts",
        help="Directory containing contract files"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--output",
        help="Output detailed report to JSON file"
    )
    parser.add_argument(
        "--fail-on-invalid",
        action="store_true",
        default=True,
        help="Exit with error code if any contracts are invalid"
    )
    parser.add_argument(
        "--generate-matrix",
        action="store_true",
        help="Generate compatibility matrix"
    )
    
    args = parser.parse_args()
    
    # Resolve contracts directory path
    contracts_dir = Path(args.contracts_dir)
    if not contracts_dir.is_absolute():
        contracts_dir = Path(__file__).parent.parent / contracts_dir
    
    print(f"Validating contracts in: {contracts_dir}")
    
    # Check if contracts directory exists
    if not contracts_dir.exists():
        print(f"Error: Contracts directory not found: {contracts_dir}")
        sys.exit(1)
    
    # Initialize validator
    try:
        validator = ContractValidator(str(contracts_dir))
        print("✓ Contract validator initialized")
    except Exception as e:
        print(f"Error initializing validator: {e}")
        sys.exit(1)
    
    # Perform batch validation
    try:
        results = validator.batch_validate_contracts()
        print("✓ Batch validation completed")
    except Exception as e:
        print(f"Error during validation: {e}")
        sys.exit(1)
    
    # Display summary
    summary = results['summary']
    print(f"\n--- Validation Summary ---")
    print(f"Total contracts: {summary['total']}")
    print(f"Valid contracts: {summary['valid']}")
    print(f"Invalid contracts: {summary['invalid']}")
    
    # Display detailed results if verbose
    if args.verbose:
        print(f"\n--- Tool Contracts ---")
        for tool_id, report in results['tools'].items():
            status = "✓" if report['contract_valid'] else "✗"
            print(f"{status} {tool_id}")
            
            if not report['contract_valid']:
                if 'error' in report:
                    print(f"    Error: {report['error']}")
                if report.get('schema_errors'):
                    for error in report['schema_errors']:
                        print(f"    Schema Error: {error}")
        
        print(f"\n--- Adapter Contracts ---")
        for adapter_id, report in results['adapters'].items():
            status = "✓" if report['contract_valid'] else "✗"
            print(f"{status} {adapter_id}")
            
            if not report['contract_valid']:
                if 'error' in report:
                    print(f"    Error: {report['error']}")
                if report.get('schema_errors'):
                    for error in report['schema_errors']:
                        print(f"    Schema Error: {error}")
    
    # Generate compatibility matrix if requested
    if args.generate_matrix:
        try:
            matrix = generate_compatibility_matrix(str(contracts_dir))
            print(f"\n--- Compatibility Matrix ---")
            print(f"Tools: {len(matrix['tools'])}")
            print(f"Adapters: {len(matrix['adapters'])}")
            
            if args.verbose:
                print("\nTool Input/Output Summary:")
                for tool_id, info in matrix['tools'].items():
                    inputs = ', '.join(info['inputs']) if info['inputs'] else 'None'
                    outputs = ', '.join(info['outputs'])
                    print(f"  {tool_id}: {inputs} → {outputs}")
        except Exception as e:
            print(f"Error generating compatibility matrix: {e}")
    
    # Save detailed report if requested
    if args.output:
        try:
            output_data = {
                'validation_results': results,
                'compatibility_matrix': generate_compatibility_matrix(str(contracts_dir)) if args.generate_matrix else None
            }
            
            with open(args.output, 'w') as f:
                json.dump(output_data, f, indent=2, default=str)
            
            print(f"✓ Detailed report saved to: {args.output}")
        except Exception as e:
            print(f"Error saving report: {e}")
    
    # Exit with appropriate code
    if args.fail_on_invalid and summary['invalid'] > 0:
        print(f"\n❌ Validation failed: {summary['invalid']} invalid contracts found")
        sys.exit(1)
    else:
        print(f"\n✅ All contracts are valid!")
        sys.exit(0)


def check_contract_dependencies():
    """Check if all required dependencies are available"""
    missing_deps = []
    
    try:
        import yaml
    except ImportError:
        missing_deps.append("pyyaml")
    
    try:
        import jsonschema
    except ImportError:
        missing_deps.append("jsonschema")
    
    try:
        import pydantic
    except ImportError:
        missing_deps.append("pydantic")
    
    if missing_deps:
        print("Missing required dependencies:")
        for dep in missing_deps:
            print(f"  - {dep}")
        print("\nInstall with: pip install " + " ".join(missing_deps))
        return False
    
    return True


if __name__ == "__main__":
    # Check dependencies first
    if not check_contract_dependencies():
        sys.exit(1)
    
    main()