#!/usr/bin/env python
"""Detect hardcoded values in Python code using AST analysis."""

import ast
import sys
from pathlib import Path
from typing import List, Dict, Any

class HardcodedDetector(ast.NodeVisitor):
    """Detects potential hardcoded values in code."""
    
    # Values that are typically OK to hardcode
    ALLOWED_VALUES = {0, 1, -1, 2, 10, 100, 1000, 0.0, 1.0, 0.5}
    
    # Common parameter names that suggest configurability needed
    PARAM_KEYWORDS = {
        'threshold', 'limit', 'max', 'min', 'timeout', 'iterations',
        'batch_size', 'window', 'score', 'weight', 'confidence',
        'similarity', 'distance', 'radius', 'count', 'size'
    }
    
    def __init__(self, source_code: str, filename: str):
        self.source = source_code
        self.filename = filename
        self.violations = []
        self.current_function = None
        
    def visit_FunctionDef(self, node):
        """Track current function for context."""
        old_function = self.current_function
        self.current_function = node.name
        self.generic_visit(node)
        self.current_function = old_function
        
    def visit_Compare(self, node):
        """Detect comparisons with hardcoded values."""
        for comparator in node.comparators:
            if isinstance(comparator, ast.Constant):
                self._check_value(comparator, node, "comparison")
        self.generic_visit(node)
        
    def visit_Assign(self, node):
        """Detect assignments with suspicious hardcoded values."""
        if isinstance(node.value, ast.Constant):
            # Check if variable name suggests it should be configurable
            for target in node.targets:
                if isinstance(target, ast.Name):
                    name_lower = target.id.lower()
                    if any(keyword in name_lower for keyword in self.PARAM_KEYWORDS):
                        self._check_value(node.value, node, f"assignment to {target.id}")
        self.generic_visit(node)
        
    def visit_Call(self, node):
        """Detect function calls with hardcoded numeric arguments."""
        # Check keyword arguments
        for keyword in node.keywords:
            if isinstance(keyword.value, ast.Constant):
                param_name = keyword.arg.lower() if keyword.arg else ""
                if any(kw in param_name for kw in self.PARAM_KEYWORDS):
                    self._check_value(keyword.value, node, f"parameter {keyword.arg}")
        self.generic_visit(node)
        
    def _check_value(self, value_node: ast.Constant, parent_node: ast.AST, context: str):
        """Check if a value is suspiciously hardcoded."""
        value = value_node.value
        
        # Skip strings, booleans, and None
        if not isinstance(value, (int, float)):
            return
            
        # Skip allowed values
        if value in self.ALLOWED_VALUES:
            return
            
        # Skip if it's a default parameter value (those are OK)
        if self._is_default_parameter(parent_node):
            return
            
        # Record violation
        try:
            code_segment = ast.get_source_segment(self.source, parent_node) or "N/A"
            # Truncate long code segments
            if len(code_segment) > 80:
                code_segment = code_segment[:80] + "..."
        except:
            code_segment = "N/A"
            
        self.violations.append({
            'file': self.filename,
            'line': value_node.lineno,
            'function': self.current_function or '<module>',
            'value': value,
            'context': context,
            'code': code_segment
        })
        
    def _is_default_parameter(self, node):
        """Check if this is a default parameter value in a function definition."""
        # This is a simplified check - could be enhanced
        return False


def check_file(filepath: Path) -> List[Dict[str, Any]]:
    """Check a single Python file for hardcoded values."""
    try:
        source = filepath.read_text()
        tree = ast.parse(source, filename=str(filepath))
        
        detector = HardcodedDetector(source, str(filepath))
        detector.visit(tree)
        
        return detector.violations
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return []


def main():
    """Main entry point."""
    # Get directory to scan from command line or use default
    if len(sys.argv) > 1:
        scan_dir = Path(sys.argv[1])
    else:
        scan_dir = Path(__file__).parent.parent / "src"
    
    print(f"Scanning for hardcoded values in: {scan_dir}")
    print("=" * 80)
    
    all_violations = []
    
    # Scan all Python files
    for py_file in scan_dir.rglob("*.py"):
        # Skip test files and this script
        if "test" in py_file.name or py_file.name == "detect_hardcoded.py":
            continue
            
        violations = check_file(py_file)
        all_violations.extend(violations)
    
    # Report findings
    if not all_violations:
        print("✅ No suspicious hardcoded values found!")
        return 0
    
    print(f"\n❌ Found {len(all_violations)} potential hardcoded values:\n")
    
    # Group by file
    by_file = {}
    for v in all_violations:
        if v['file'] not in by_file:
            by_file[v['file']] = []
        by_file[v['file']].append(v)
    
    # Display violations
    for filename, violations in by_file.items():
        print(f"\n📄 {filename}")
        print("-" * 80)
        
        for v in violations:
            print(f"  Line {v['line']} in {v['function']}():")
            print(f"    Value: {v['value']} (in {v['context']})")
            print(f"    Code: {v['code']}")
            print()
    
    print("\n💡 Suggestions:")
    print("  - Make these values configurable parameters with defaults")
    print("  - Or add them to ALLOWED_VALUES if they're truly constant")
    print("  - Document why the value is hardcoded if necessary")
    
    return 1


if __name__ == "__main__":
    sys.exit(main())