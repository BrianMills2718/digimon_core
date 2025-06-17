#!/usr/bin/env python
"""Verify no mocks in production code."""

import sys
from pathlib import Path

print("=== CHECKING FOR MOCKS IN PRODUCTION ===\n")

# Keywords that indicate mocking
MOCK_KEYWORDS = [
    "mock", "Mock", "MagicMock", 
    "patch", "@patch",
    "fake", "Fake", "stub", "Stub",
    "dummy", "Dummy"
]

# Directories to scan
src_dir = Path(__file__).parent / "src"

# Files to exclude (test files can have mocks)
EXCLUDE_PATTERNS = ["test_", "_test.py", "mock_", "_mock.py"]

violations = []

# Scan all Python files in src
for py_file in src_dir.rglob("*.py"):
    # Skip if it's a test file
    if any(pattern in str(py_file) for pattern in EXCLUDE_PATTERNS):
        continue
    
    try:
        content = py_file.read_text()
        
        # Check each line
        for line_num, line in enumerate(content.splitlines(), 1):
            # Skip comments
            if line.strip().startswith("#"):
                continue
                
            # Check for mock keywords
            for keyword in MOCK_KEYWORDS:
                if keyword in line and "# OK" not in line:  # Allow if explicitly marked OK
                    violations.append({
                        'file': py_file.relative_to(Path(__file__).parent),
                        'line': line_num,
                        'keyword': keyword,
                        'content': line.strip()[:80]
                    })
                    
    except Exception as e:
        print(f"Error reading {py_file}: {e}")

# Report results
if not violations:
    print("✅ No mock-related keywords found in production code!")
    print("\nThis suggests:")
    print("- Database operations are real")
    print("- No fake implementations")
    print("- Production code is mock-free")
else:
    print(f"⚠️  Found {len(violations)} potential mock references:\n")
    
    for v in violations:
        print(f"{v['file']}:{v['line']}")
        print(f"  Keyword: '{v['keyword']}'")
        print(f"  Line: {v['content']}")
        print()
    
    print("\nNote: These might be legitimate uses (e.g., in docstrings).")
    print("Review each case to ensure no mocks in production.")

# Also check for common test patterns in src
print("\n\nChecking for test patterns in production...")

test_patterns = [
    "assert ", "assertEqual", "assertTrue",
    "pytest", "unittest",
    "def test_", "class Test"
]

test_violations = []

for py_file in src_dir.rglob("*.py"):
    if any(pattern in str(py_file) for pattern in EXCLUDE_PATTERNS):
        continue
        
    try:
        content = py_file.read_text()
        
        for pattern in test_patterns:
            if pattern in content:
                test_violations.append({
                    'file': py_file.relative_to(Path(__file__).parent),
                    'pattern': pattern
                })
                break
                
    except:
        pass

if test_violations:
    print(f"\n⚠️  Found test patterns in {len(test_violations)} production files:")
    for v in test_violations:
        print(f"  {v['file']} contains '{v['pattern']}'")
else:
    print("\n✅ No test patterns found in production code!")

print("\n✅ Mock detection complete!")