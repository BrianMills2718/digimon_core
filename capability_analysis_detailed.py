#!/usr/bin/env python3
"""
Detailed capability analysis script to identify and categorize every capability
in the codebase with exact counts and locations.
"""

import os
import re
import json
from typing import Dict, List, Tuple
from pathlib import Path

def analyze_python_file(filepath: str) -> Dict[str, List[Dict]]:
    """Analyze a Python file and extract all capabilities (classes, functions, methods)."""
    capabilities = {
        'classes': [],
        'functions': [],
        'methods': []
    }
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for line_num, line in enumerate(lines, 1):
            # Clean line for analysis
            stripped = line.strip()
            
            # Skip empty lines and comments
            if not stripped or stripped.startswith('#'):
                continue
                
            # Match class definitions
            class_match = re.match(r'^class\s+(\w+)(?:\([^)]*\))?:', line)
            if class_match:
                capabilities['classes'].append({
                    'name': class_match.group(1),
                    'line': line_num,
                    'file': filepath,
                    'signature': line.strip()
                })
                continue
            
            # Match function definitions (not indented = top-level functions)
            func_match = re.match(r'^(async\s+)?def\s+(\w+)', line)
            if func_match:
                capabilities['functions'].append({
                    'name': func_match.group(2),
                    'line': line_num,
                    'file': filepath,
                    'signature': line.strip(),
                    'async': func_match.group(1) is not None
                })
                continue
                
            # Match method definitions (indented = class methods)
            method_match = re.match(r'^\s+(async\s+)?def\s+(\w+)', line)
            if method_match:
                capabilities['methods'].append({
                    'name': method_match.group(2),
                    'line': line_num,
                    'file': filepath,
                    'signature': line.strip(),
                    'async': method_match.group(1) is not None
                })
                continue
                
    except Exception as e:
        print(f"Error analyzing {filepath}: {e}")
        
    return capabilities

def analyze_codebase(src_dir: str = "/home/brian/Digimons/src") -> Dict:
    """Analyze entire codebase and return comprehensive capability breakdown."""
    
    all_capabilities = {
        'classes': [],
        'functions': [],
        'methods': [],
        'summary': {
            'total_files': 0,
            'total_classes': 0,
            'total_functions': 0,
            'total_methods': 0,
            'total_capabilities': 0
        },
        'by_directory': {},
        'by_file': {}
    }
    
    # Find all Python files
    python_files = []
    for root, dirs, files in os.walk(src_dir):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    all_capabilities['summary']['total_files'] = len(python_files)
    
    # Analyze each file
    for filepath in python_files:
        file_capabilities = analyze_python_file(filepath)
        
        # Add to global lists
        all_capabilities['classes'].extend(file_capabilities['classes'])
        all_capabilities['functions'].extend(file_capabilities['functions'])
        all_capabilities['methods'].extend(file_capabilities['methods'])
        
        # Track by directory
        rel_path = os.path.relpath(filepath, src_dir)
        dir_name = os.path.dirname(rel_path) or "root"
        
        if dir_name not in all_capabilities['by_directory']:
            all_capabilities['by_directory'][dir_name] = {
                'classes': 0, 'functions': 0, 'methods': 0, 'total': 0, 'files': []
            }
        
        file_total = len(file_capabilities['classes']) + len(file_capabilities['functions']) + len(file_capabilities['methods'])
        
        all_capabilities['by_directory'][dir_name]['classes'] += len(file_capabilities['classes'])
        all_capabilities['by_directory'][dir_name]['functions'] += len(file_capabilities['functions'])
        all_capabilities['by_directory'][dir_name]['methods'] += len(file_capabilities['methods'])
        all_capabilities['by_directory'][dir_name]['total'] += file_total
        all_capabilities['by_directory'][dir_name]['files'].append(rel_path)
        
        # Track by file
        all_capabilities['by_file'][rel_path] = {
            'classes': len(file_capabilities['classes']),
            'functions': len(file_capabilities['functions']),
            'methods': len(file_capabilities['methods']),
            'total': file_total
        }
    
    # Update summary
    all_capabilities['summary']['total_classes'] = len(all_capabilities['classes'])
    all_capabilities['summary']['total_functions'] = len(all_capabilities['functions'])
    all_capabilities['summary']['total_methods'] = len(all_capabilities['methods'])
    all_capabilities['summary']['total_capabilities'] = (
        all_capabilities['summary']['total_classes'] + 
        all_capabilities['summary']['total_functions'] + 
        all_capabilities['summary']['total_methods']
    )
    
    return all_capabilities

def create_numbered_capability_list(capabilities: Dict) -> List[str]:
    """Create a numbered list of all capabilities for easy reference."""
    numbered_list = []
    counter = 1
    
    # Add classes
    for cls in capabilities['classes']:
        numbered_list.append(f"{counter:03d}. Class: {cls['name']} ({os.path.basename(cls['file'])}:{cls['line']})")
        counter += 1
    
    # Add functions
    for func in capabilities['functions']:
        async_prefix = "Async " if func.get('async') else ""
        numbered_list.append(f"{counter:03d}. {async_prefix}Function: {func['name']} ({os.path.basename(func['file'])}:{func['line']})")
        counter += 1
    
    # Add methods
    for method in capabilities['methods']:
        async_prefix = "Async " if method.get('async') else ""
        numbered_list.append(f"{counter:03d}. {async_prefix}Method: {method['name']} ({os.path.basename(method['file'])}:{method['line']})")
        counter += 1
    
    return numbered_list

def main():
    print("🔍 COMPREHENSIVE CAPABILITY ANALYSIS")
    print("=" * 50)
    
    # Analyze the codebase
    capabilities = analyze_codebase()
    
    # Print summary
    summary = capabilities['summary']
    print(f"📊 SUMMARY:")
    print(f"   Total Python Files: {summary['total_files']}")
    print(f"   Total Classes: {summary['total_classes']}")
    print(f"   Total Functions: {summary['total_functions']}")
    print(f"   Total Methods: {summary['total_methods']}")
    print(f"   TOTAL CAPABILITIES: {summary['total_capabilities']}")
    print()
    
    # Print breakdown by directory
    print("📁 BREAKDOWN BY DIRECTORY:")
    for dir_name, stats in sorted(capabilities['by_directory'].items()):
        print(f"   {dir_name}:")
        print(f"      Classes: {stats['classes']}, Functions: {stats['functions']}, Methods: {stats['methods']}")
        print(f"      Total: {stats['total']} capabilities in {len(stats['files'])} files")
    print()
    
    # Show top files by capability count
    print("📋 TOP FILES BY CAPABILITY COUNT:")
    sorted_files = sorted(capabilities['by_file'].items(), key=lambda x: x[1]['total'], reverse=True)
    for i, (filename, stats) in enumerate(sorted_files[:10], 1):
        print(f"   {i:2d}. {filename}: {stats['total']} capabilities")
        print(f"       (Classes: {stats['classes']}, Functions: {stats['functions']}, Methods: {stats['methods']})")
    print()
    
    # Create numbered list
    numbered_list = create_numbered_capability_list(capabilities)
    
    # Save detailed results
    with open('/home/brian/Digimons/capability_analysis_results.json', 'w') as f:
        json.dump(capabilities, f, indent=2)
    
    with open('/home/brian/Digimons/capability_numbered_list.txt', 'w') as f:
        f.write("COMPLETE NUMBERED LIST OF ALL 571 CAPABILITIES\n")
        f.write("=" * 50 + "\n\n")
        for item in numbered_list:
            f.write(item + "\n")
    
    # Print verification
    print(f"✅ VERIFICATION: Found exactly {len(numbered_list)} capabilities")
    print(f"   This {'matches' if len(numbered_list) == 571 else 'does NOT match'} the claimed 571 capabilities")
    print()
    print("📄 FILES CREATED:")
    print("   - capability_analysis_results.json (detailed breakdown)")
    print("   - capability_numbered_list.txt (numbered list of all capabilities)")

if __name__ == "__main__":
    main()