# GraphRAG Repository Reorganization Plan

**Status**: PARTIALLY COMPLETE - Documentation consolidated, code reorganization pending  
**Note**: Documentation consolidation ongoing per CONSOLIDATION_PROGRESS.md, code structure reorganization remains as future work

## 🎯 Reorganization Goals

### Primary Objectives
1. **Clear Navigation**: Easy file location and referencing system
2. **Development Efficiency**: Streamlined workflow and file management
3. **Maintainability**: Logical organization that scales with project growth
4. **Git History Preservation**: Maintain commit history during reorganization

### Success Criteria
- All files have clear, logical locations
- Documentation is centralized and easy to navigate
- Test files are organized by type and purpose
- Development workflow is clearly defined
- No loss of git history or functionality

## 📁 New Directory Structure

### Root Level Organization
```
/
├── README.md                     # Project overview and quick start
├── PROJECT_STATUS.md             # Real-time system health dashboard  
├── DOCUMENTATION_INDEX.md        # Master navigation for all docs
├── CLAUDE.md                     # Development context and instructions
├── requirements.txt              # Python dependencies
├── docker-compose.yml            # Container orchestration
└── .gitignore                    # Git ignore patterns
```

### Core Directories
```
docs/                             # All Documentation
├── current/                      # Active documentation
│   ├── ARCHITECTURE.md          # System architecture overview
│   ├── ROADMAP_v2.md            # Development roadmap and priorities  
│   ├── TESTING_GUIDE.md         # Testing procedures and standards
│   ├── TROUBLESHOOTING.md       # Common issues and solutions
│   ├── PERFORMANCE_ANALYSIS.md  # Performance metrics and optimization
│   ├── ERROR_HANDLING_BEST_PRACTICES.md  # Error handling patterns
│   └── TABLE_OF_CONTENTS.md     # Legacy navigation (archived)
├── archive/                      # Historical documentation
│   ├── old_roadmaps/            # Previous roadmap versions
│   ├── session_handoffs/        # Session transition documents
│   └── analysis_reports/        # Various analysis reports
├── phase1/                       # Phase 1 specific documentation
├── phase2/                       # Phase 2 specific documentation  
├── phase3/                       # Phase 3 specific documentation
└── api/                          # API documentation and schemas

src/                              # Source Code
├── core/                         # Core services and infrastructure
│   ├── service_manager.py       # Service singleton management
│   ├── identity_service.py      # Entity identity and resolution
│   ├── provenance_service.py    # Operation tracking and history
│   ├── quality_service.py       # Quality assessment and scoring
│   └── workflow_state_service.py # Workflow state management
├── tools/                        # Phase-specific tool implementations
│   ├── phase1/                  # Basic pipeline tools
│   ├── phase2/                  # Ontology-aware tools
│   └── phase3/                  # Multi-document fusion tools
├── ontology/                     # Ontology generation and management
├── testing/                      # Testing frameworks and utilities
└── ui/                           # User interface components

tests/                            # All Test Files
├── functional/                   # Functional integration tests (mandatory)
│   ├── test_phase1_integration.py
│   ├── test_phase2_integration.py
│   └── test_cross_component_integration.py
├── performance/                  # Performance and optimization tests
│   ├── test_optimized_workflow.py
│   ├── test_performance_profiling.py
│   └── test_pagerank_optimization.py
├── stress/                       # Stress and reliability tests
│   ├── test_extreme_conditions.py
│   ├── test_network_failures.py
│   └── test_adversarial_comprehensive.py
├── unit/                         # Unit tests for individual components
├── fixtures/                     # Test data and fixtures
│   ├── sample_pdfs/
│   ├── test_ontologies/
│   └── mock_responses/
└── utilities/                    # Test utilities and helpers

config/                           # Configuration Files
├── development/                  # Development environment configs
├── production/                   # Production environment configs
└── testing/                      # Testing environment configs

scripts/                          # Utility Scripts
├── start_services.sh            # Start all services
├── run_all_tests.sh             # Run complete test suite
└── deployment/                   # Deployment scripts

archive/                          # Archived and Legacy Files
├── old_tests/                   # Archived test files
├── analysis_reports/            # Historical analysis
├── session_documents/           # Old session handoffs
└── deprecated_code/             # Old implementations
```

## 🔄 Migration Strategy

### Phase 1: Create New Structure
```bash
# Create new directory structure
mkdir -p docs/{current,archive,phase1,phase2,phase3,api}
mkdir -p tests/{functional,performance,stress,unit,fixtures,utilities}  
mkdir -p config/{development,production,testing}
mkdir -p scripts/{deployment}
mkdir -p archive/{old_tests,analysis_reports,session_documents,deprecated_code}
```

### Phase 2: Move Documentation
```bash
# Move current documentation
git mv docs/current/ARCHITECTURE.md docs/current/
git mv docs/current/ROADMAP_v2.md docs/current/
git mv docs/current/STATUS.md docs/archive/STATUS_legacy.md

# Archive old documents
git mv EXAMINATION_SUMMARY.md docs/archive/session_documents/
git mv SESSION_HANDOFF.md docs/archive/session_documents/
git mv STRESS_TESTING_SUMMARY_REPORT.md docs/archive/analysis_reports/
git mv UI_ERROR_HANDLING_ANALYSIS_REPORT.md docs/archive/analysis_reports/
git mv neo4j_error_analysis_report.md docs/archive/analysis_reports/
```

### Phase 3: Organize Test Files
```bash
# Move functional integration tests
git mv test_functional_simple.py tests/functional/
git mv test_functional_integration_complete.py tests/functional/
git mv test_cross_component_integration.py tests/functional/
git mv test_ui_complete_user_journeys.py tests/functional/

# Move performance tests  
git mv test_optimized_workflow.py tests/performance/
git mv test_performance_profiling.py tests/performance/
git mv test_pagerank_optimization.py tests/performance/
git mv test_performance_comparison.py tests/performance/

# Move stress tests
git mv test_extreme_stress_conditions.py tests/stress/
git mv test_adversarial_comprehensive.py tests/stress/
git mv test_stress_all_phases.py tests/stress/
git mv test_compatibility_validation.py tests/stress/

# Archive ad-hoc tests
git mv test_*_direct.py archive/old_tests/
git mv test_*_adversarial.py archive/old_tests/
git mv debug_*.py archive/old_tests/
```

### Phase 4: Create Utility Scripts
```bash
# Create service management scripts
cat > scripts/start_services.sh << 'EOF'
#!/bin/bash
# Start all GraphRAG services
echo "Starting Neo4j..."
docker-compose up -d neo4j

echo "Starting GraphRAG UI..."
python start_graphrag_ui.py &

echo "Starting MCP Server..."
python start_t301_mcp_server.py &

echo "All services started"
EOF

# Create comprehensive test runner
cat > scripts/run_all_tests.sh << 'EOF'
#!/bin/bash
echo "Running Functional Integration Tests..."
python tests/functional/test_phase1_integration.py
python tests/functional/test_phase2_integration.py  
python tests/functional/test_cross_component_integration.py

echo "Running Performance Tests..."
python tests/performance/test_optimized_workflow.py

echo "Running Stress Tests..."
python tests/stress/test_extreme_conditions.py

echo "All tests completed"
EOF

chmod +x scripts/*.sh
```

## 📋 File Reference System

### Documentation Navigation
| File Type | Location | Purpose |
|-----------|----------|---------|
| **System Status** | `PROJECT_STATUS.md` | Real-time health dashboard |
| **Master Navigation** | `DOCUMENTATION_INDEX.md` | All documentation links |
| **Development Context** | `CLAUDE.md` | Active development instructions |
| **Architecture** | `docs/current/ARCHITECTURE.md` | System design and components |
| **Roadmap** | `docs/current/ROADMAP_v2.md` | Development priorities |
| **Testing Guide** | `docs/current/TESTING_GUIDE.md` | Testing procedures |

### Test File Navigation
| Test Type | Location | Purpose |
|-----------|----------|---------|
| **Functional Integration** | `tests/functional/` | End-to-end feature validation |
| **Performance** | `tests/performance/` | Speed and optimization tests |
| **Stress/Reliability** | `tests/stress/` | System robustness tests |
| **Unit Tests** | `tests/unit/` | Individual component tests |

### Quick Reference Commands
```bash
# Check system status
cat PROJECT_STATUS.md

# Find all documentation
ls docs/current/

# Run functional tests
python tests/functional/test_phase1_integration.py

# Start all services
./scripts/start_services.sh

# Run complete test suite
./scripts/run_all_tests.sh
```

## 🔧 Development Workflow Integration

### Before Starting Work
1. **Check Status**: `cat PROJECT_STATUS.md`
2. **Review Plan**: `cat docs/current/ROADMAP_v2.md`
3. **Understand Context**: `cat CLAUDE.md`

### Adding New Features
1. **Update Roadmap**: Modify `docs/current/ROADMAP_v2.md`
2. **Create Tests**: Add to `tests/functional/`
3. **Implement**: Follow `CLAUDE.md` guidelines
4. **Update Status**: Modify `PROJECT_STATUS.md`

### Reference Management
- All file references use relative paths from project root
- Documentation cross-references use standard markdown links
- Test files include clear purpose descriptions
- Archive maintains historical context

## ✅ Implementation Checklist

### Pre-Reorganization
- [ ] Create git commit checkpoint: "CHECKPOINT: Pre-reorganization stable state"
- [ ] Verify all tests pass: `python test_final_verification.py`
- [ ] Document current file locations
- [ ] Create new directory structure

### During Reorganization  
- [ ] Move files using `git mv` to preserve history
- [ ] Update all internal file references
- [ ] Test functionality after each major move
- [ ] Create new navigation files

### Post-Reorganization
- [ ] Update CLAUDE.md with new navigation system
- [ ] Test all file references work correctly
- [ ] Run complete test suite to verify functionality
- [ ] Create git commit: "REORGANIZE: Implement clean file structure"
- [ ] Update PROJECT_STATUS.md with new organization

### Validation
- [ ] All documentation links work
- [ ] All test files execute correctly
- [ ] Services start without issues
- [ ] No broken file references
- [ ] Git history preserved for important files

---

**Next Steps**: 
1. Review and approve this reorganization plan
2. Create git checkpoint
3. Execute reorganization in phases
4. Validate functionality throughout process
5. Update all references and documentation