#!/usr/bin/env python3
"""
Demo script for Tool Registry functionality

This script demonstrates the comprehensive tool registry with 
version conflict management and current tool status.
"""

import json
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.tool_registry import get_tool_registry, ToolStatus

def main():
    """Demonstrate tool registry functionality."""
    
    print("🔧 KGAS Tool Registry Demo")
    print("=" * 60)
    
    # Get the global tool registry
    registry = get_tool_registry()
    
    print(f"📅 Validation Date: {registry.validation_date}")
    print()
    
    # Get registry summary
    summary = registry.get_registry_summary()
    
    print("📊 Registry Summary:")
    print(f"   Current Tools: {summary['registry_metadata']['total_current_tools']}")
    print(f"   Archived Tools: {summary['registry_metadata']['total_archived_tools']}")
    print(f"   Version Conflicts: {summary['registry_metadata']['total_version_conflicts']}")
    print(f"   Missing Tools: {summary['registry_metadata']['total_missing_tools']}")
    print()
    
    # MVRT Status
    mvrt_status = summary['mvrt_status']
    print(f"🎯 MVRT Completion Status:")
    print(f"   Total Required: {mvrt_status['total_required']}")
    print(f"   Functional: {mvrt_status['functional']}")
    print(f"   Completion: {mvrt_status['completion_percentage']:.1f}%")
    print(f"   Broken Tools: {mvrt_status['broken_tools']}")
    print(f"   Version Conflicts: {mvrt_status['version_conflicts']}")
    print()
    
    # Current Tools Status
    print("🔧 Current Tools Status:")
    for tool_id, tool_info in summary['current_tools'].items():
        status_icon = "❌" if tool_info['status'] == ToolStatus.BROKEN else "✅"
        print(f"   {status_icon} {tool_id}: {tool_info['class']} - {tool_info['status'].value}")
        if tool_info.get('issues'):
            for issue in tool_info['issues']:
                print(f"      Issue: {issue}")
    print()
    
    # Version Conflicts
    if summary['version_conflicts']:
        print("⚠️  Version Conflicts Requiring Resolution:")
        for conflict_id in summary['version_conflicts']:
            conflict_detail = summary['version_conflicts_detail'][conflict_id]
            print(f"   🔄 {conflict_id}: {conflict_detail['description']}")
            for version in conflict_detail['versions']:
                print(f"      - {version['path']} ({version['class']}) - {version['status'].value}")
            print(f"      Recommended: {conflict_detail['recommended_primary']}")
            print(f"      Rationale: {conflict_detail['rationale']}")
            print()
    else:
        print("✅ No version conflicts detected.")
        print()
    
    # Functional vs Broken Breakdown
    functional_tools = summary['functional_tools']
    broken_tools = summary['broken_tools']
    
    print(f"📈 Tool Health Summary:")
    print(f"   Functional: {len(functional_tools)} tools")
    print(f"   Broken: {len(broken_tools)} tools")
    print(f"   Health Rate: {(len(functional_tools) / (len(functional_tools) + len(broken_tools)) * 100) if (len(functional_tools) + len(broken_tools)) > 0 else 0:.1f}%")
    print()
    
    # Critical Assessment
    print("🚨 Critical Assessment:")
    if mvrt_status['completion_percentage'] == 0:
        print("   ❌ MVRT is 0% complete - immediate action required")
        print("   🔧 Primary issue: Tools require test data parameters")
        print("   ⚡ Next steps: Fix parameter requirements and missing tool classes")
    elif mvrt_status['completion_percentage'] < 50:
        print("   ⚠️  MVRT is less than 50% complete")
        print("   🔧 Focus on fixing broken tools and resolving conflicts")
    elif mvrt_status['completion_percentage'] < 90:
        print("   📈 MVRT is progressing but not production ready")
        print("   🔧 Focus on achieving 90%+ functionality rate")
    else:
        print("   ✅ MVRT is near completion")
        print("   🔧 Focus on final validation and testing")
    
    print()
    print("💾 Full registry data available via:")
    print("   python -c \"from src.core.tool_registry import get_tool_registry; print(get_tool_registry().get_registry_summary())\"")
    
    return summary

if __name__ == "__main__":
    try:
        result = main()
        print("\n✅ Tool Registry Demo completed successfully")
        exit(0)
    except Exception as e:
        print(f"\n❌ Tool Registry Demo failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)