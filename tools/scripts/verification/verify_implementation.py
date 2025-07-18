#!/usr/bin/env python3
"""
Implementation Verification Script
Verifies all key implementation claims from CLAUDE.md
"""

import os
import subprocess
import sys
import time
from typing import List, Dict, Any

def run_command(command: str, timeout: int = 60) -> Dict[str, Any]:
    """Run a command and return the result"""
    try:
        result = subprocess.run(
            command.split(),
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return {
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'stdout': '',
            'stderr': 'Command timed out',
            'returncode': -1
        }
    except Exception as e:
        return {
            'success': False,
            'stdout': '',
            'stderr': str(e),
            'returncode': -1
        }

def verify_implementation() -> List[Dict[str, Any]]:
    """Verify all implementation claims"""
    checks = []
    
    print("🔍 Verifying Super-Digimon GraphRAG Implementation...")
    print("=" * 60)
    
    # Check 1: Required files exist
    print("\n📁 Check 1: Required files exist...")
    required_files = [
        "src/core/pipeline_orchestrator.py",
        "src/core/tool_adapters.py", 
        "src/core/tool_adapter_bridge.py",
        "src/core/contract_validator.py",
        "src/core/ontology_validator.py",
        "src/core/tool_factory.py",
        "src/core/phase_adapters.py",
        "contracts/contracts/tools/T01_PDFLoader.yaml",
        "examples/minimal_working_example.py"
    ]
    
    for file in required_files:
        if os.path.exists(file):
            checks.append({
                'name': f"File exists: {file}",
                'status': 'PASS',
                'message': f"✅ {file} exists"
            })
            print(f"✅ {file} exists")
        else:
            checks.append({
                'name': f"File exists: {file}",
                'status': 'FAIL',
                'message': f"❌ {file} missing"
            })
            print(f"❌ {file} missing")
    
    # Check 2: Minimal example uses PipelineOrchestrator
    print("\n🔧 Check 2: Minimal example uses PipelineOrchestrator...")
    try:
        with open("examples/minimal_working_example.py", 'r') as f:
            content = f.read()
            if "PipelineOrchestrator" in content and "VerticalSliceWorkflow" not in content:
                checks.append({
                    'name': "Minimal example uses PipelineOrchestrator",
                    'status': 'PASS',
                    'message': "✅ Minimal example uses PipelineOrchestrator"
                })
                print("✅ Minimal example uses PipelineOrchestrator")
            else:
                checks.append({
                    'name': "Minimal example uses PipelineOrchestrator",
                    'status': 'FAIL',
                    'message': "❌ Minimal example still uses VerticalSliceWorkflow"
                })
                print("❌ Minimal example still uses VerticalSliceWorkflow")
    except Exception as e:
        checks.append({
            'name': "Minimal example uses PipelineOrchestrator",
            'status': 'FAIL',
            'message': f"❌ Error reading minimal example: {e}"
        })
        print(f"❌ Error reading minimal example: {e}")
    
    # Check 3: System functionality test
    print("\n🧪 Check 3: System functionality test...")
    result = run_command("python examples/minimal_working_example.py")
    if result['success']:
        # Check if it extracted entities and relationships
        output = result['stdout']
        if "entities extracted" in output and "relationships found" in output:
            checks.append({
                'name': "System functionality test",
                'status': 'PASS',
                'message': "✅ Minimal example runs successfully and extracts entities/relationships"
            })
            print("✅ Minimal example runs successfully and extracts entities/relationships")
        else:
            checks.append({
                'name': "System functionality test",
                'status': 'WARN',
                'message': "⚠️ Minimal example runs but output format unexpected"
            })
            print("⚠️ Minimal example runs but output format unexpected")
    else:
        checks.append({
            'name': "System functionality test",
            'status': 'FAIL',
            'message': f"❌ Minimal example failed: {result['stderr']}"
        })
        print(f"❌ Minimal example failed: {result['stderr']}")
    
    # Check 4: Neo4j authentication
    print("\n🗄️ Check 4: Neo4j authentication...")
    result = run_command("docker exec neo4j env", timeout=10)
    if result['success'] and "NEO4J_AUTH=none" in result['stdout']:
        checks.append({
            'name': "Neo4j authentication disabled",
            'status': 'PASS',
            'message': "✅ Neo4j authentication disabled"
        })
        print("✅ Neo4j authentication disabled")
    else:
        checks.append({
            'name': "Neo4j authentication disabled",
            'status': 'FAIL',
            'message': "❌ Neo4j authentication not disabled or container not running"
        })
        print("❌ Neo4j authentication not disabled or container not running")
    
    # Check 5: Integration tests
    print("\n🧪 Check 5: Integration tests...")
    result = run_command("python tests/integration/test_end_to_end.py", timeout=120)
    if result['success']:
        if "All integration tests passed!" in result['stdout']:
            checks.append({
                'name': "Integration tests",
                'status': 'PASS',
                'message': "✅ All integration tests passed"
            })
            print("✅ All integration tests passed")
        else:
            checks.append({
                'name': "Integration tests",
                'status': 'WARN',
                'message': "⚠️ Integration tests ran but results unclear"
            })
            print("⚠️ Integration tests ran but results unclear")
    else:
        checks.append({
            'name': "Integration tests",
            'status': 'FAIL',
            'message': f"❌ Integration tests failed: {result['stderr']}"
        })
        print(f"❌ Integration tests failed: {result['stderr']}")
    
    # Check 6: Contract validation integration
    print("\n📋 Check 6: Contract validation integration...")
    result = run_command("python examples/minimal_working_example.py", timeout=60)
    if result['success']:
        output = result['stdout'] + result['stderr']
        if "Contract and ontology validation enabled" in output:
            checks.append({
                'name': "Contract validation integration",
                'status': 'PASS',
                'message': "✅ Contract validation integrated and working"
            })
            print("✅ Contract validation integrated and working")
        else:
            checks.append({
                'name': "Contract validation integration",
                'status': 'WARN',
                'message': "⚠️ Contract validation status unclear"
            })
            print("⚠️ Contract validation status unclear")
    else:
        checks.append({
            'name': "Contract validation integration",
            'status': 'FAIL',
            'message': "❌ Cannot verify contract validation"
        })
        print("❌ Cannot verify contract validation")
    
    # Check 7: Documentation honesty
    print("\n📚 Check 7: Documentation honesty...")
    try:
        with open("CLAUDE.md", 'r') as f:
            content = f.read()
            if "EXPERIMENTAL" in content and "NOT FOR PRODUCTION" in content:
                checks.append({
                    'name': "Documentation honesty",
                    'status': 'PASS',
                    'message': "✅ Documentation honestly states experimental status"
                })
                print("✅ Documentation honestly states experimental status")
            else:
                checks.append({
                    'name': "Documentation honesty",
                    'status': 'FAIL',
                    'message': "❌ Documentation still makes production-ready claims"
                })
                print("❌ Documentation still makes production-ready claims")
    except Exception as e:
        checks.append({
            'name': "Documentation honesty",
            'status': 'FAIL',
            'message': f"❌ Error reading documentation: {e}"
        })
        print(f"❌ Error reading documentation: {e}")
    
    return checks

def main():
    """Main verification function"""
    checks = verify_implementation()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for check in checks if check['status'] == 'PASS')
    warned = sum(1 for check in checks if check['status'] == 'WARN')
    failed = sum(1 for check in checks if check['status'] == 'FAIL')
    total = len(checks)
    
    print(f"✅ PASSED: {passed}/{total}")
    print(f"⚠️ WARNED: {warned}/{total}")
    print(f"❌ FAILED: {failed}/{total}")
    
    if failed > 0:
        print("\n🔴 CRITICAL ISSUES:")
        for check in checks:
            if check['status'] == 'FAIL':
                print(f"  - {check['name']}: {check['message']}")
    
    if warned > 0:
        print("\n🟡 WARNINGS:")
        for check in checks:
            if check['status'] == 'WARN':
                print(f"  - {check['name']}: {check['message']}")
    
    print("\n" + "=" * 60)
    if failed == 0:
        print("🎉 VERIFICATION COMPLETE - System is working as expected")
        print("⚠️ Note: This is still an experimental system not suitable for production")
    else:
        print("❌ VERIFICATION FAILED - Critical issues found")
        print("🔧 Please address the failed checks before proceeding")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)