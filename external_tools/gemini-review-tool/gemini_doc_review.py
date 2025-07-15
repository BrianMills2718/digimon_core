#!/usr/bin/env python3
"""
Gemini Documentation Review Automation Tool

Purpose
-------
Compare selected documentation files/directories against selected source-code
files/directories and ask Gemini 2.5-Pro whether the documentation faithfully
and comprehensively represents the underlying code.

Features
~~~~~~~~
* Accept one or more *documentation* paths (`--docs`) and one or more *code*
  paths (`--code`).
* Optional glob patterns to ignore (`--ignore`).
* Optional additional focus areas via `--prompt`.
* Saves the Gemini response to `doc-review.md` (override with `--output`).
* Uses the same `GEMINI_API_KEY` and `GEMINI_MODEL` env-vars as
  `gemini_review.py`.

Example
~~~~~~~
python gemini_doc_review.py \
    --docs autocoder_cc/docs \
    --code autocoder_cc/autocoder/validation \
    --prompt "Pay special attention to validation error-handling." \
    --output validation-doc-review.md
"""

from __future__ import annotations

import argparse
import os
import sys
import textwrap
import time
from pathlib import Path
from typing import Iterable, List, Optional

import google.generativeai as genai
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Environment & Gemini setup
# ---------------------------------------------------------------------------

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    sys.exit("❌  GEMINI_API_KEY not set in environment or .env file")

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-pro")

genai.configure(api_key=API_KEY)
MODEL = genai.GenerativeModel(MODEL_NAME)


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------

def gather_files(paths: Iterable[str], ignore_patterns: Optional[List[str]] = None) -> List[Path]:
    """Expand the provided *paths* into a list of regular files.

    Each item in *paths* may be a file or directory. Directories are traversed
    recursively. *ignore_patterns* may contain simple Unix shell-style globs
    (e.g. ``*.pyc`` or ``__pycache__``) that will be skipped.
    """
    collected: List[Path] = []
    ignore_patterns = ignore_patterns or []

    def _ignored(p: Path) -> bool:
        return any(p.match(pattern) for pattern in ignore_patterns)

    for p_str in paths:
        p = Path(p_str).expanduser().resolve()
        if not p.exists():
            print(f"⚠️  Path not found: {p}")
            continue

        if p.is_file():
            if not _ignored(p):
                collected.append(p)
            continue

        for sub in p.rglob("*"):
            if sub.is_file() and not _ignored(sub):
                collected.append(sub)

    return collected


def read_files(files: Iterable[Path]) -> str:
    """Return a single string containing all files separated by markers."""
    content_parts: List[str] = []
    for f in files:
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
        except Exception as exc:
            print(f"⚠️  Could not read {f}: {exc}")
            continue
        content_parts.append(f"\n\n--- {f} ---\n\n" + text)
    return "".join(content_parts)


# ---------------------------------------------------------------------------
# Gemini interaction
# ---------------------------------------------------------------------------

def build_prompt(documentation: str, code: str, extra_prompt: Optional[str]) -> str:
    base_prompt = textwrap.dedent(
        """
        You are an expert technical writer and software architect.
        Compare the following *DOCUMENTATION* with the *SOURCE CODE* and
        determine whether the documentation faithfully and comprehensively
        represents the code. For any mismatches, omissions, or inaccuracies,
        explain them clearly and suggest precise improvements to the docs.

        Provide your response in these sections:
        1. Summary verdict (faithful / partially faithful / not faithful)
        2. Missing documented features (code present, docs missing)
        3. Undocumented code behaviour (code behaviour absent from docs)
        4. Inaccuracies (docs describe behaviour that the code contradicts)
        5. Overall recommendations for improving documentation quality
        """
    ).strip()

    if extra_prompt:
        base_prompt += "\n\nAdditional focus areas:\n" + extra_prompt.strip()

    return f"{base_prompt}\n\nDOCUMENTATION:\n{documentation}\n\nSOURCE CODE:\n{code}"


def call_gemini(prompt: str) -> str:
    try:
        response = MODEL.generate_content(prompt)
        return response.text
    except Exception as exc:
        raise RuntimeError(f"Gemini API error: {exc}") from exc


# ---------------------------------------------------------------------------
# Main CLI entry-point
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare documentation to source code using Gemini AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--docs", nargs="+", required=True, help="Documentation files or directories to include")
    parser.add_argument("--code", nargs="+", required=True, help="Source code files or directories to include")
    parser.add_argument("--ignore", nargs="*", default=[], help="Glob patterns to ignore (e.g. *.pyc __pycache__)")
    parser.add_argument("--prompt", help="Additional custom prompt to append")
    parser.add_argument("--output", default="doc-review.md", help="Output file path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    print("🚀 Gathering documentation files...")
    doc_files = gather_files(args.docs, args.ignore)
    documentation = read_files(doc_files)
    print(f"📚 Collected {len(doc_files)} documentation files")

    print("📦 Gathering source code files...")
    code_files = gather_files(args.code, args.ignore)
    code_content = read_files(code_files)
    print(f"📄 Collected {len(code_files)} source files")

    print("🤖 Building prompt and sending to Gemini…")
    prompt = build_prompt(documentation, code_content, args.prompt)
    result = call_gemini(prompt)

    print(f"💾 Saving output to {args.output}…")
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(f"# Gemini Documentation Review\nGenerated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(result)

    print("✅ Review complete! Results saved.")


if __name__ == "__main__":  # pragma: no cover
    main() 