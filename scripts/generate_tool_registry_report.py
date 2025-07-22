#!/usr/bin/env python3
"""Generate Tool Registry Report

This script generates a comprehensive report of all 121 tools in the KGAS ecosystem,
including implementation status, priorities, and dependencies.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.tools.tool_registry import get_tool_registry
from datetime import datetime


def main():
    """Generate and save tool registry report"""
    registry = get_tool_registry()
    
    # Generate the report
    report = registry.generate_implementation_report()
    
    # Save to file
    report_path = "docs/tools/TOOL_REGISTRY_REPORT.md"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    
    with open(report_path, 'w') as f:
        f.write(report)
    
    print(f"Tool registry report generated: {report_path}")
    
    # Also export JSON registry
    json_path = "data/tool_registry.json"
    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    registry.export_registry(json_path)
    print(f"Tool registry JSON exported: {json_path}")
    
    # Print summary
    status = registry.get_implementation_status()
    print(f"\nSummary:")
    print(f"- Total Tools: {status['total']}")
    print(f"- Implemented: {status['implemented_total']} ({status['implementation_percentage']}%)")
    print(f"- Not Started: {status.get('not_started', 0)}")
    
    # Print next priorities
    print(f"\nNext 5 Priority Tools:")
    for tool in registry.get_priority_queue()[:5]:
        print(f"- {tool.tool_id}: {tool.name} (Priority: {tool.priority})")


if __name__ == "__main__":
    main()