#!/usr/bin/env python3
"""Validate that Markdown docs are stored in the correct top-level folder according to CLAUDE.md rules.

Rules (mirrored from docs/CLAUDE.md):
• Docs root may contain only README.md and CLAUDE.md.
• Top-level doc directories must be in the allowed set.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1] / "docs"
ALLOWED_ROOT_FILES = {"README.md", "CLAUDE.md"}
ALLOWED_TOP_DIRS = {
    "getting-started",
    "architecture",
    "api",
    "development",
    "operations",
    "planning",
    "maintenance",
    "templates",
    "archive",  # archive is allowed but ignored
}

violations: list[str] = []

for path in ROOT.glob("**/*.md"):
    rel = path.relative_to(ROOT)
    parts = rel.parts

    # file directly under docs/
    if len(parts) == 1:
        if parts[0] not in ALLOWED_ROOT_FILES:
            violations.append(f"Docs root contains disallowed file: {rel}")
    else:
        top = parts[0]
        if top not in ALLOWED_TOP_DIRS:
            violations.append(f"Top-level docs directory '{top}' is not allowed (file: {rel})")

if violations:
    print("❌ Documentation structure violations detected:")
    for v in violations:
        print("  -", v)
    sys.exit(1)
print("✅ Documentation directory structure valid.") 