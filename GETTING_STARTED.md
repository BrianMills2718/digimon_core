# Getting Started with Super-Digimon Development

## Prerequisites

### Required Knowledge
- **Python 3.11+** development experience
- **Git** version control
- **Docker** basics (for databases)
- **CLI/Terminal** comfort

### Recommended Knowledge
- **GraphRAG** concepts (helpful but not required)
- **Neo4j** graph databases (will be taught)
- **Model Context Protocol (MCP)** (will be explained)

## Step-by-Step Setup

### 1. Clone and Navigate
```bash
git clone https://github.com/BrianMills2718/UKRF_1.git
cd UKRF_1
```

### 2. Read Essential Documentation
**Critical reading order** (30 minutes total):
1. **[README.md](README.md)** - Project overview (5 min)
2. **[CLAUDE.md](CLAUDE.md)** - Development guidance (10 min)
3. **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture (10 min)
4. **[docs/README.md](docs/README.md)** - Documentation navigation (5 min)

### 3. Understand the System
**Key Concepts**:
- **106 Tools**: Complete system specification across 7 phases
- **Prototype Scope**: Functionally complete, not production-ready
- **MCP Protocol**: How Claude Code communicates with tools
- **Triple Database**: Neo4j (graphs) + SQLite (metadata) + FAISS (vectors)

### 4. Set Up Development Environment

#### 4.1 Install Python Dependencies
```bash
# Navigate to implementation directory
cd tools/cc_automator

# Install requirements
pip install -r requirements.txt
```

#### 4.2 Start Database Services
```bash
# Start Neo4j via Docker
docker-compose up -d neo4j

# Verify Neo4j is running
docker-compose ps neo4j
```

#### 4.3 Test Database Connection
```bash
# Run connection test
pytest test_files/test_simple_neo4j.py -v

# Expected output: Connection successful
```

### 5. Explore the Codebase Structure

#### 5.1 Key Directories
```
super-digimon/
├── README.md                    # Start here
├── CLAUDE.md                    # Development guidance
├── ARCHITECTURE.md              # System design
├── IMPLEMENTATION.md            # Development roadmap
├── docs/                        # Documentation
│   ├── specifications/         # 106 tool specifications
│   ├── decisions/              # Architectural decisions
│   └── reference/              # Analysis and guides
├── tools/cc_automator/         # Development/testing tool (separate)
├── test_data/                  # Sample datasets
└── config/                     # Configuration examples
```

#### 5.2 Review Tool Specifications
```bash
# Read the complete tool specifications
cat docs/specifications/SUPER_DIGIMON_COMPLETE_TOOL_SPECIFICATIONS.md

# Understand tool organization
cat docs/specifications/TOOL_ARCHITECTURE_SUMMARY.md
```

### 6. Understand Current Status

#### 6.1 Implementation Status
- **Super-Digimon**: 0 of 106 tools implemented (target system)
- **CC_Automator**: Existing development tool (separate from target)
- **Phase**: Specification complete, ready for implementation

#### 6.2 Next Steps (Your Work)
According to `IMPLEMENTATION.md`:
1. **Phase 0**: Infrastructure setup (Docker, databases, MCP framework)
2. **Phase 1**: Ingestion tools (T01-T12)
3. **Phase 2**: Processing tools (T13-T30)
4. **Phase 3**: Construction tools (T31-T48)
5. **Phase 4**: Core GraphRAG (T49-T67)
6. **Phase 5-7**: Advanced features (T68-T106)

### 7. Development Workflow

#### 7.1 Daily Development Setup
```bash
# 1. Start databases
cd tools/cc_automator
docker-compose up -d neo4j

# 2. Activate Python environment
# (use your preferred method: venv, conda, etc.)

# 3. Run tests to verify setup
pytest test_files/test_simple_neo4j.py -v
```

#### 7.2 Claude Code Integration
- **Runtime**: Claude Code (claude.ai/code) orchestrates tools
- **Protocol**: MCP (Model Context Protocol) for communication
- **Development**: Local Python + Docker services (hybrid approach)

#### 7.3 Testing Strategy
- **Unit Tests**: Individual tool functionality with mocks
- **Integration Tests**: Multi-tool workflows
- **E2E Tests**: Real database connections, no mocks
- **Evidence Validation**: Automated test result verification

### 8. Your First Contribution

#### 8.1 Recommended Starting Point
**Goal**: Implement Phase 0 infrastructure setup

**Tasks**:
1. Create MCP server framework
2. Set up database connections
3. Implement tool registry system
4. Create basic tool template

#### 8.2 Implementation Guidelines
- **Follow CANONICAL_DECISIONS_2025.md** for architectural decisions
- **Use 106-tool specification** as authoritative source
- **Build prototype, not production** - focus on functionality
- **Single MCP server** architecture (not federated)

### 9. Development Resources

#### 9.1 Key Reference Documents
- **[Canonical Decisions](docs/decisions/CANONICAL_DECISIONS_2025.md)** - Final architectural decisions
- **[Tool Specifications](docs/specifications/SUPER_DIGIMON_COMPLETE_TOOL_SPECIFICATIONS.md)** - Complete 106 tool details
- **[JayLZhou Mapping](docs/specifications/JAYZHOU_MCP_TOOL_MAPPING.md)** - Core GraphRAG operators

#### 9.2 External Resources
- **[JayLZhou GraphRAG](https://github.com/JayLZhou/GraphRAG)** - Original research (19 core operators)
- **[Model Context Protocol](https://modelcontextprotocol.io/)** - MCP documentation
- **[Neo4j Documentation](https://neo4j.com/docs/)** - Graph database guide

### 10. Common Issues and Solutions

#### 10.1 Neo4j Connection Issues
```bash
# Check if Neo4j is running
docker-compose ps neo4j

# View Neo4j logs
docker-compose logs neo4j

# Restart if needed
docker-compose restart neo4j
```

#### 10.2 Port Conflicts
```bash
# Neo4j uses ports 7474 (HTTP) and 7687 (Bolt)
# Check if ports are in use
netstat -an | grep 7474
netstat -an | grep 7687
```

#### 10.3 Python Dependencies
```bash
# If requirements.txt install fails
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### 11. Getting Help

#### 11.1 Documentation Issues
- **Check canonical decisions** first: `docs/decisions/CANONICAL_DECISIONS_2025.md`
- **Use documentation navigation**: `docs/README.md`
- **Verify document is current** (not in `docs/archive/`)

#### 11.2 Technical Issues
- **Review CLAUDE.md** for development guidance
- **Check test files** in `tools/cc_automator/test_files/`
- **Examine existing code** patterns in `tools/cc_automator/`

## Next Steps

1. **✅ Complete this setup guide**
2. **📖 Read IMPLEMENTATION.md** for detailed development roadmap
3. **🔧 Start Phase 0** infrastructure implementation
4. **🧪 Set up testing framework** following evidence validation patterns
5. **⚙️ Create first MCP tool** using the established patterns

**Welcome to Super-Digimon development!** 🚀

---

**Last Updated**: 2025-06-12  
**For**: New developers joining Super-Digimon project  
**Next**: Read IMPLEMENTATION.md for detailed development phases