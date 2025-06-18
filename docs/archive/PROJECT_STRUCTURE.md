# Project Structure

After decluttering, the Super-Digimon project follows this organized structure:

```
Digimons/
├── README.md                    # Project overview
├── CLAUDE.md                    # Claude Code guidance
├── IMPLEMENTATION_ROADMAP.md    # Development roadmap
├── PROJECT_STRUCTURE.md         # This file
├── requirements.txt             # Core Python dependencies
├── requirements_llm.txt         # LLM-specific dependencies
├── docker-compose.yml           # Database services
├── main.py                      # MCP server entry point
├── .env.example                 # Environment template
├── .gitignore                   # Git ignore rules
│
├── src/                         # Source code
│   ├── core/                    # Core services (T107-T121)
│   ├── tools/                   # Tool implementations by phase
│   │   ├── phase1/              # Ingestion tools (T01-T12)
│   │   ├── phase2/              # Processing tools (T13-T30)
│   │   └── ...                  # Through phase8
│   ├── utils/                   # Shared utilities
│   └── mcp_server.py            # MCP server implementation
│
├── tests/                       # All test files
│   ├── unit/                    # Unit tests
│   ├── integration/             # Integration tests
│   ├── e2e/                     # End-to-end tests
│   └── fixtures/                # Test data and fixtures
│
├── scripts/                     # Utility scripts
│   ├── demo/                    # Demo and example scripts
│   ├── analysis/                # Analysis scripts
│   └── setup/                   # Setup and maintenance
│
├── ui/                          # User interfaces
│   ├── web_ui.py                # Streamlit web interface
│   ├── cli_tool.py              # CLI interface
│   └── requirements.txt         # UI-specific dependencies
│
├── docs/                        # Documentation
│   ├── core/                    # Technical documentation
│   ├── guides/                  # User guides and tutorials
│   └── planning/                # Planning and design docs
│
├── data/                        # Runtime data (gitignored)
│   ├── neo4j/                   # Graph database files
│   ├── sqlite/                  # Metadata database
│   └── workflows/               # Workflow checkpoints
│
├── examples/                    # Example files
│   ├── pdfs/                    # Sample PDF documents
│   └── queries/                 # Example queries
│
└── test_data/                   # Test datasets
    └── fixtures/                # Test fixtures
```

## What Was Cleaned Up

### Moved to `tests/`:
- All `test_*.py` files
- `proof_test.py`, `quick_test.py`, `minimal_upload_test.py`

### Moved to `ui/`:
- `web_ui.py`, `simple_ui.py`, `cli_tool.py`
- `streamlit_test.py`, `start_ui.sh`
- `requirements_ui.txt`

### Moved to `scripts/demo/`:
- `show_*.py` scripts
- `find_*.py` scripts
- `create_*.py` scripts
- `run_*.py`, `answer_*.py`, `query_*.py`
- `demo_*.py`, `debug_*.py`

### Moved to `examples/`:
- PDF files (`climate_report.pdf`, `wiki1.pdf`, etc.)
- Output files (`climate_report.txt`, `climate_report_results.json`)
- `test_document.txt`

### Moved to `docs/planning/`:
- `2025.06172110_planning_needs_to_be_integrated.md`
- `DOCUMENTATION_REVIEW_SUMMARY.md`
- `PHASE0_ADVERSARIAL_TEST_RESULTS.md`
- `ADVERSARIAL_TEST_RESULTS.md`

### Moved to `docs/guides/`:
- `EXTRACTION_EXPLAINED.md`
- `NEO4J_BROWSER_GUIDE.md`
- `USAGE_GUIDE.md`

## Old Implementations (Preserved but Gitignored)

- `archive/` - Historical documentation
- `cc_automator4/` - Previous automation attempt
- `super_digimon_implementation/` - Original implementation

These directories are preserved for reference but excluded from version control.