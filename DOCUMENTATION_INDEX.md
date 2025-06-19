# GraphRAG System Documentation Index

**Master Navigation for the Digimons GraphRAG Knowledge System**

## 🎯 Quick Start Navigation

### Core Status and Navigation
- **Current System Status**: [PROJECT_STATUS.md](./PROJECT_STATUS.md) - Real-time system health and functionality
- **Development Guide**: [CLAUDE.md](./CLAUDE.md) - Active development instructions and context
- **Master Documentation Index**: [DOCUMENTATION_INDEX.md](./DOCUMENTATION_INDEX.md) ← *You are here*

### Essential Development Files
- **Architecture Overview**: [docs/current/ARCHITECTURE.md](./docs/current/ARCHITECTURE.md)
- **System Roadmap**: [docs/current/ROADMAP_v2.md](./docs/current/ROADMAP_v2.md)
- **Error Handling Guide**: [docs/current/ERROR_HANDLING_BEST_PRACTICES.md](./docs/current/ERROR_HANDLING_BEST_PRACTICES.md)
- **Performance Claims**: [docs/current/PERFORMANCE_CLAIMS_VERIFICATION.md](./docs/current/PERFORMANCE_CLAIMS_VERIFICATION.md)

## 📁 File Organization Structure

### `/docs/` - All Documentation
```
docs/
├── current/           # Active documentation
├── archive/          # Historical documentation
├── phase1/           # Phase 1 specific docs
├── phase2/           # Phase 2 specific docs
├── phase3/           # Phase 3 specific docs
└── api/              # API documentation
```

### `/src/` - Source Code
```
src/
├── core/             # Core services and infrastructure
├── tools/            # Phase-specific tool implementations
├── ontology/         # Ontology generation and management
├── testing/          # Testing frameworks and utilities
└── ui/               # User interface components
```

### `/tests/` - All Test Files
```
tests/
├── functional/       # Functional integration tests
├── performance/      # Performance and optimization tests
├── stress/           # Stress and reliability tests
├── unit/             # Unit tests for individual components
└── fixtures/         # Test data and fixtures
```

### `/config/` - Configuration
```
config/
├── development/      # Development environment configs
├── production/       # Production environment configs
└── testing/          # Testing environment configs
```

## 🔧 Development Workflow Files

### Primary Development References
| File | Purpose | When to Use |
|------|---------|-------------|
| [PROJECT_STATUS.md](./PROJECT_STATUS.md) | Check what's working/broken | Before starting any work |
| [CLAUDE.md](./CLAUDE.md) | Development context and instructions | Active development |
| [docs/current/ROADMAP_v2.md](./docs/current/ROADMAP_v2.md) | Planned work and priorities | Planning sessions |

### Problem-Solving References
| File | Purpose | When to Use |
|------|---------|-------------|
| [docs/current/ERROR_HANDLING_BEST_PRACTICES.md](./docs/current/ERROR_HANDLING_BEST_PRACTICES.md) | Error handling patterns | Implementing error handling |
| [docs/current/PERFORMANCE_CLAIMS_VERIFICATION.md](./docs/current/PERFORMANCE_CLAIMS_VERIFICATION.md) | Performance verification | Validating performance claims |
| [docs/current/TECHNICAL_DEBT_AUDIT.md](./docs/current/TECHNICAL_DEBT_AUDIT.md) | Comprehensive technical debt inventory | Before refactoring, planning work |
| [docs/current/NO_MOCKS_POLICY_VIOLATION.md](./docs/current/NO_MOCKS_POLICY_VIOLATION.md) | Critical policy violation documentation | Immediate action required |
| [docs/current/IDENTITY_SERVICE_CLARIFICATION.md](./docs/current/IDENTITY_SERVICE_CLARIFICATION.md) | Multiple service implementation analysis | Service selection decisions |
| [docs/current/TOOL_COUNT_CLARIFICATION.md](./docs/current/TOOL_COUNT_CLARIFICATION.md) | Resolves tool count discrepancies | Understanding implementation progress |
| [docs/current/INTEGRATION_TESTING_GAP_ANALYSIS.md](./docs/current/INTEGRATION_TESTING_GAP_ANALYSIS.md) | Critical testing coverage gaps | Test planning and honesty |
| [archive/analysis_reports/](./archive/analysis_reports/) | Historical analysis and test reports | Troubleshooting reference |

## 🧪 Testing and Validation

### Functional Integration Tests (Mandatory)
| Test File | Purpose | Success Criteria |
|-----------|---------|-----------------|
| `tests/functional/test_phase1_integration.py` | Phase 1 end-to-end | PDF→entities→graph→query |
| `tests/functional/test_phase2_integration.py` | Phase 2 ontology workflow | Ontology-aware extraction |
| `tests/functional/test_cross_component.py` | Multi-component integration | Cross-phase data flow |

### Performance and Reliability Tests
| Test File | Purpose | Success Criteria |
|-----------|---------|-----------------|
| `tests/performance/test_optimized_workflow.py` | Performance validation | <10s without PageRank |
| `tests/stress/test_extreme_conditions.py` | Stress testing | 100% reliability |
| `tests/stress/test_network_failures.py` | Network failure handling | Clear error messages |

## 📋 Development Procedures

### Adding New Features
1. **Check Status**: Review [PROJECT_STATUS.md](./PROJECT_STATUS.md)
2. **Update Plan**: Add to [docs/current/ROADMAP_v2.md](./docs/current/ROADMAP_v2.md)
3. **Create Tests**: Add functional integration tests FIRST
4. **Implement**: Follow [CLAUDE.md](./CLAUDE.md) guidelines
5. **Validate**: Run all tests and update status
6. **Document**: Update relevant documentation

### Fixing Issues
1. **Identify Root Cause**: Use [archive/analysis_reports/](./archive/analysis_reports/) for historical context
2. **Create Reproduction Test**: Add to appropriate test suite
3. **Implement Fix**: Follow [error handling best practices](./docs/current/ERROR_HANDLING_BEST_PRACTICES.md)
4. **Validate Fix**: Ensure all tests pass
5. **Update Documentation**: Record solution in relevant documentation

### Before Each Commit
1. **Run Functional Tests**: Ensure 100% pass rate
2. **Update Status**: Modify [PROJECT_STATUS.md](./PROJECT_STATUS.md)
3. **Update CLAUDE.md**: Record any context changes
4. **Commit**: Use descriptive commit messages

## 🎯 Project Goals and Success Criteria

### Core System Objectives
- **Phase 1**: Fast, reliable PDF→graph→query pipeline
- **Phase 2**: Ontology-aware entity extraction with LLMs
- **Phase 3**: Multi-document knowledge fusion
- **UI**: Interactive graph visualization and querying

### Success Metrics
- **Functional Integration**: 100% test pass rate
- **Performance**: <10s processing without PageRank
- **Reliability**: No unhandled exceptions in normal operation
- **Usability**: Complete UI workflows functional

## 🔄 Maintenance and Updates

### Regular Maintenance Tasks
- **Weekly**: Review and update [PROJECT_STATUS.md](./PROJECT_STATUS.md)
- **After Major Changes**: Update [docs/current/ARCHITECTURE.md](./docs/current/ARCHITECTURE.md)
- **Before Releases**: Comprehensive testing and documentation review
- **Monthly**: Archive old documentation and clean up test files

### Documentation Standards
- **All features**: Must have functional integration tests
- **All bugs**: Must have reproduction test before fixing
- **All changes**: Must update relevant documentation
- **All commits**: Must include clear description of changes

---

**Last Updated**: Current  
**Maintained By**: Development Team  
**Review Cycle**: After major milestones and monthly maintenance