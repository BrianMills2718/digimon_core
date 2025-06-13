# Super-Digimon Directory Structure

## Root Directory
```
Digimons/
├── README.md                 # Project overview and entry point
├── GETTING_STARTED.md       # Getting started guide
├── docker-compose.yml       # Docker services configuration
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
│
├── config/                 # Configuration files
│   └── mcp_config.example.json
│
├── docker/                 # Docker files
│   └── Dockerfile.dev
│
├── scripts/                # Utility scripts
│   ├── configure_cc_automator.sh
│   └── test_neo4j.py
│
├── tools/                  # Development tools
│   └── cc_automator/      # Automated development framework
│
├── docs/                   # All documentation
│   ├── architecture/      # Architecture documentation
│   │   ├── CANONICAL_ARCHITECTURE.md
│   │   └── TOOL_ARCHITECTURE_SUMMARY.md
│   ├── development/       # Development guides
│   │   ├── IMPLEMENTATION_STATUS.md
│   │   └── DOCKER_WORKFLOW.md
│   ├── reference/         # Reference documentation
│   │   ├── PROJECT_OVERVIEW.md
│   │   └── agent_research/
│   ├── specifications/    # Technical specifications
│   ├── planning/          # Planning documents
│   ├── analysis/          # Analysis reports
│   ├── integration/       # Integration guides
│   ├── advanced/          # Advanced features
│   └── research/          # Research documents
│
├── examples/              # Example data and demos
│   └── celestial_council/
│
├── test_data/             # Test datasets
│   └── celestial_council/
│
└── misc/                  # Miscellaneous research
    └── ontology_engineering/
```

## Key Locations

### For Users
- Start with `README.md` and `GETTING_STARTED.md`
- Example in `examples/celestial_council/`
- Configuration template in `config/mcp_config.example.json`

### For Developers  
- Architecture: `docs/architecture/CANONICAL_ARCHITECTURE.md`
- Progress: `docs/development/IMPLEMENTATION_STATUS.md`
- Tools specs: `docs/specifications/SUPER_DIGIMON_COMPLETE_TOOL_SPECIFICATIONS.md`
- Docker setup: `docs/development/DOCKER_WORKFLOW.md`

### For Contributors
- cc_automator: `tools/cc_automator/`
- Planning docs: `docs/planning/`
- Test data: `test_data/celestial_council/`

## Quick Commands

```bash
# Start services
docker-compose up -d

# Set up Python environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Test Neo4j connection
python scripts/test_neo4j.py

# Configure cc_automator
./scripts/configure_cc_automator.sh
```