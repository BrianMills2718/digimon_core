#!/usr/bin/env python3
"""
Master script to run all IC-inspired uncertainty feature stress tests
"""

import os
import sys
import subprocess
from datetime import datetime
import json

def run_test(test_name, script_name):
    """Run a single test script and capture results"""
    print(f"\n{'='*70}")
    print(f"Running: {test_name}")
    print(f"{'='*70}")
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            print(f"✓ {test_name} completed successfully")
            return {
                "status": "success",
                "output": result.stdout[-1000:] if len(result.stdout) > 1000 else result.stdout  # Last 1000 chars
            }
        else:
            print(f"✗ {test_name} failed with return code {result.returncode}")
            return {
                "status": "failed",
                "error": result.stderr
            }
            
    except subprocess.TimeoutExpired:
        print(f"✗ {test_name} timed out")
        return {
            "status": "timeout",
            "error": "Test exceeded 5 minute timeout"
        }
    except Exception as e:
        print(f"✗ {test_name} encountered an error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }

def main():
    """Run all stress tests and generate summary report"""
    
    print("IC-Inspired Uncertainty Features - Comprehensive Stress Test Suite")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Define all tests
    tests = [
        ("Information Value Assessment (Heuer's 4 Types)", "test_information_value_assessment.py"),
        ("Stopping Rules for Information Collection", "test_stopping_rules.py"),
        ("ACH Theory Competition", "test_ach_theory_competition.py"),
        ("Calibration System", "test_calibration_system.py"),
        ("Mental Model Auditing", "test_mental_model_auditing.py")
    ]
    
    # Change to test directory
    test_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(test_dir)
    
    # Run all tests
    results = {}
    for test_name, script_name in tests:
        results[test_name] = run_test(test_name, script_name)
    
    # Generate summary report
    summary = {
        "test_suite": "IC-Inspired Uncertainty Features",
        "timestamp": datetime.now().isoformat(),
        "total_tests": len(tests),
        "successful": sum(1 for r in results.values() if r["status"] == "success"),
        "failed": sum(1 for r in results.values() if r["status"] != "success"),
        "test_results": results,
        "overall_assessment": ""
    }
    
    # Determine overall assessment
    if summary["successful"] == summary["total_tests"]:
        summary["overall_assessment"] = "All tests passed successfully! IC-inspired features are working correctly."
    elif summary["successful"] >= summary["total_tests"] * 0.8:
        summary["overall_assessment"] = "Most tests passed. Minor issues to address."
    else:
        summary["overall_assessment"] = "Significant issues detected. Review failed tests."
    
    # Write summary report
    with open("stress_test_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    # Print summary
    print(f"\n\n{'='*70}")
    print("STRESS TEST SUMMARY")
    print(f"{'='*70}")
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Successful: {summary['successful']}")
    print(f"Failed: {summary['failed']}")
    print(f"\nOverall Assessment: {summary['overall_assessment']}")
    
    # Print individual results
    print(f"\nIndividual Test Results:")
    for test_name, result in results.items():
        status_symbol = "✓" if result["status"] == "success" else "✗"
        print(f"{status_symbol} {test_name}: {result['status']}")
    
    print(f"\nDetailed results saved to: stress_test_summary.json")
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return summary["successful"] == summary["total_tests"]

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)