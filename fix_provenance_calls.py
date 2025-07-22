#!/usr/bin/env python3
"""Fix provenance service calls in unified tools to match actual API."""

import re
from pathlib import Path

# Find all unified tool files
tool_files = list(Path("src/tools/phase1").glob("*_unified.py"))

for tool_file in tool_files:
    content = tool_file.read_text()
    
    # Fix start_operation calls
    # Replace inputs=[] with used={}
    content = re.sub(
        r'(self\.provenance_service\.start_operation\([^)]*?)inputs=\[\]',
        r'\1used={}',
        content,
        flags=re.MULTILINE | re.DOTALL
    )
    
    # Replace inputs=[chunk_ref] with used={"chunk": chunk_ref}
    content = re.sub(
        r'(self\.provenance_service\.start_operation\([^)]*?)inputs=\[([^\]]+)\]',
        r'\1used={"source": \2}',
        content,
        flags=re.MULTILINE | re.DOTALL
    )
    
    # Fix complete_operation calls
    # Replace outputs=[...] with generated={...}
    content = re.sub(
        r'(self\.provenance_service\.complete_operation\([^)]*?)outputs=\[([^\]]+)\]',
        r'\1generated={"output": \2}',
        content,
        flags=re.MULTILINE | re.DOTALL
    )
    
    # Write back
    tool_file.write_text(content)
    print(f"Fixed {tool_file}")

print("\nDone! All provenance calls updated.")