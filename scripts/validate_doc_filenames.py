#!/usr/bin/env python3
"""Fail CI if any markdown files under docs/ are not kebab-case (lowercase letters, digits and dashes)."""
from pathlib import Path
import re, sys

invalid = []
pattern = re.compile(r"^[a-z0-9][a-z0-9\-]*\.md$")
for md in Path("docs").rglob("*.md"):
    if not pattern.match(md.name):
        invalid.append(str(md))

if invalid:
    print("❌ The following documentation filenames violate kebab-case:")
    for f in invalid:
        print("  -", f)
    print("Rename files to lower-case with dashes (e.g., example-file.md).")
    sys.exit(1)
else:
    print("✅ All documentation filenames are kebab-case.") 