#!/usr/bin/env python3
import sys
import os
import json
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.tool_factory import ToolFactory
from core.evidence_logger import EvidenceLogger

def main():
    """Verify tool success rate with comprehensive testing"""
    evidence_logger = EvidenceLogger()
    tool_factory = ToolFactory()
    
    print("=== TOOL SUCCESS RATE VERIFICATION ===")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Discover all tools
    print("\n1. Discovering all tools...")
    discovered_tools = tool_factory.discover_all_tools()
    print(f"   Total tools discovered: {len(discovered_tools)}")
    
    # Audit all tools
    print("\n2. Auditing tool functionality...")
    audit_results = tool_factory.audit_all_tools()
    
    # Calculate success rate
    success_rate = tool_factory.get_success_rate()
    
    # Generate detailed report
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_tools": audit_results["total_tools"],
        "working_tools": audit_results["working_tools"],
        "broken_tools": audit_results["broken_tools"],
        "success_rate": success_rate,
        "tool_details": audit_results["tool_results"]
    }
    
    # Log evidence
    evidence_logger.log_with_verification("TOOL_SUCCESS_RATE_VERIFICATION", report)
    
    # Print summary
    print(f"\n=== RESULTS ===")
    print(f"Total Tools: {report['total_tools']}")
    print(f"Working Tools: {report['working_tools']}")
    print(f"Broken Tools: {report['broken_tools']}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    # Print broken tools
    if report['broken_tools'] > 0:
        print(f"\n=== BROKEN TOOLS ===")
        for tool_name, details in report['tool_details'].items():
            if details.get('status') == 'failed':
                print(f"  - {tool_name}: {details.get('error', 'Unknown error')}")
    
    # Save detailed report
    with open('tool_success_rate_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nDetailed report saved to: tool_success_rate_report.json")
    
    # Return exit code based on success rate
    if success_rate >= 75:
        print("✅ SUCCESS: Tool success rate meets minimum threshold (75%)")
        return 0
    else:
        print("❌ FAILURE: Tool success rate below minimum threshold (75%)")
        return 1

if __name__ == "__main__":
    sys.exit(main())