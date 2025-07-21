#!/usr/bin/env python3
"""Unified CLI for Super-Digimon GraphRAG

Example usage::

    python -m src.cli mcp                # Start MCP server
    python -m src.cli ui --port 8501     # Start Streamlit UI
    python -m src.cli dev-ui             # Launch development UI (legacy)
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def _start_mcp_server() -> None:
    """Start the MCP server (original behaviour of main.py)."""
    from config.config_loader import get_settings
    from src.mcp_server import mcp  # type: ignore

    settings = get_settings()
    print("🚀 Starting Super-Digimon MCP Server …")
    print(f"📊 Environment: {settings.environment}")
    print(f"🔗 Database: {settings.database_url}")
    mcp.run()


def _start_streamlit_ui(ui_file: Path, port: int = 8501) -> None:
    if not ui_file.exists():
        print(f"❌ UI file not found: {ui_file}")
        sys.exit(1)

    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(ui_file),
        f"--server.port={port}",
        "--server.address=0.0.0.0",
        "--browser.gatherUsageStats=false",
    ]
    subprocess.run(cmd, check=False)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Super-Digimon GraphRAG CLI")
    sub = parser.add_subparsers(dest="command")

    # MCP command
    sub.add_parser("mcp", help="Start MCP server")

    # UI command
    ui_parser = sub.add_parser("ui", help="Start production UI (Streamlit)")
    ui_parser.add_argument("--port", type=int, default=8501)

    # Dev UI command (legacy streamlit_app.py for experimentation)
    dev_ui_parser = sub.add_parser("dev-ui", help="Start development UI (legacy)")
    dev_ui_parser.add_argument("--port", type=int, default=8502)

    args = parser.parse_args(argv)

    # Default to parser help if no command
    if not args.command:
        parser.print_help()
        parser.exit()

    root = Path(__file__).resolve().parent.parent

    if args.command == "mcp":
        _start_mcp_server()
    elif args.command == "ui":
        ui_file = root / "ui" / "graphrag_ui.py"
        _start_streamlit_ui(ui_file, port=args.port)
    elif args.command == "dev-ui":
        ui_file = root / "streamlit_app.py"
        _start_streamlit_ui(ui_file, port=args.port)
    else:
        parser.error(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main() 