---
status: living
---

# KGAS Quick Start Guide

**Purpose**: Get new developers up and running with the Knowledge Graph Analysis System quickly  
**Target Audience**: Developers & Research Engineers  
**Prerequisites**: Python 3.8+, basic familiarity with Python and command line

---

## 🚀 **Getting Started (5 Minutes)**

### **1. System Overview**
KGAS is a Knowledge Graph Analysis System with three processing phases:
- **Phase 1**: Basic entity extraction and graph construction (✅ Working)
- **Phase 2**: Ontology-aware processing (⚠️ Partially functional)
- **Phase 3**: Multi-document fusion (🔧 Standalone only)

### **2. Quick System Check**
```bash
# Navigate to project directory
cd /home/brian/Digimons

# Check if system is ready
python -c "
from src.core.service_manager import ServiceManager
from src.core.neo4j_manager import Neo4jManager
from src.core.service_compatibility_layer import ServiceCompatibilityLayer
print('✅ Core services: OK')
print('✅ Database: OK')
print('✅ Service compatibility: OK')
print('✅ System ready for Phase 1 processing')
"
```

### **3. Test Current Functionality**
```bash
# Test Phase 1 (working)
python tests/functional/test_phase1_only.py

# Launch the UI
python start_graphrag_ui.py
# Open http://localhost:8501 in your browser
```

---

## 🎯 **Understanding Current Status**

### **What Works Right Now**
- ✅ **Phase 1**: Complete entity extraction pipeline
- ✅ **UI Interface**: Functional for Phase 1 processing
- ✅ **Core Services**: Identity, Provenance, Quality tracking
- ✅ **Storage**: Neo4j graph and SQLite metadata
- ✅ **Entity Extraction**: 484 entities successfully extracted from test documents

### **What's In Development**
- 🔄 **Phase Integration**: Phase 1→2→3 seamless operation
- 🔄 **Theory Integration**: Theory schemas into processing pipeline
- 🔄 **Contract System**: YAML/JSON contracts with Pydantic validation

### **What's Planned**
- 📋 **Advanced Features**: Multi-document processing, temporal tracking
- 📋 **Performance Optimization**: Processing speed and memory efficiency
- 📋 **Research Evaluation**: Academic-grade evaluation framework

---

## 🛠️ **Development Workflow**

### **Current Development Phase**
We're in **Phase A: Theory-Aware Architecture Foundation** (Week 1-2)

**Current Task**: A1 - Service Compatibility Layer with Theory Support (20% complete)

**Next Actions**:
1. Complete version checking for all core services with theory schema validation
2. Create `contracts/` directory with immutable theory-aware interfaces
3. Design `UIAdapter` class for phase abstraction with theory schema selection

### **How to Contribute**

#### **Understanding the Codebase**
```bash
# Key directories
src/core/           # Core services (Identity, Workflow, Quality)
src/tools/          # Processing tools organized by phase
tests/functional/   # Integration and functional tests
docs/architecture/  # Architecture documentation
```

#### **Running Tests**
```bash
# Test specific functionality
python tests/functional/test_phase1_only.py

# Test integration
python tests/functional/test_phase2_integration_fix.py

# Run all tests
python tests/run_all_tests.sh
```

#### **Making Changes**
1. **Check current status**: Review `ROADMAP_v2.md` for current phase
2. **Run tests**: Ensure existing functionality still works
3. **Update documentation**: Keep `ROADMAP_v2.md` current with progress
4. **Verify claims**: Use commands from `VERIFICATION_COMMANDS.md`

---

## 📚 **Key Documentation**

### **Essential Reading Order**
1. **`ROADMAP_v2.md`** - Current development status and next steps
2. **`ARCHITECTURE.md`** - System design and current vs. target state
3. **`KGAS_EVERGREEN_DOCUMENTATION.md`** - Theoretical foundation
4. **`VERIFICATION_COMMANDS.md`** - Commands to test all functionality

### **Development Process**
- **Single Source of Truth**: All task status tracked in `ROADMAP_v2.md`
- **Verification First**: Every claim must have a test command
- **Theory Integration**: All new features should integrate theoretical concepts
- **No Mocks**: Real functionality only, no placeholder implementations

---

## 🔧 **Common Tasks**

### **Testing Current System**
```bash
# Test Phase 1 functionality
python tests/functional/test_phase1_only.py

# Test UI functionality
python tests/functional/test_ui_complete_fix.py

# Test end-to-end workflow
python tests/functional/test_execute_pdf_to_answer_workflow.py
```

### **Understanding Integration Issues**
```bash
# Test Phase 1→2 integration (shows current challenges)
python tests/functional/test_phase2_integration_fix.py

# Check API compatibility
python tests/functional/test_mcp_services_fixed.py
```

### **Working with the UI**
```bash
# Start the UI
python start_graphrag_ui.py

# Access at http://localhost:8501
# Currently supports Phase 1 processing only
```

### **Database Operations**
```bash
# Check Neo4j connection
python tests/unit/test_database_connection.py

# Verify data models
python -c "from src.core.neo4j_manager import Neo4jManager; print('Neo4j: OK')"
```

---

## 🚨 **Troubleshooting**

### **Common Issues**

#### **Phase 2 Integration Problems**
- **Symptom**: Phase 2 fails to integrate with Phase 1
- **Cause**: API compatibility issues (mostly fixed, integration challenges remain)
- **Check**: `python tests/functional/test_phase2_integration_fix.py`

#### **Theory Integration Not Working**
- **Symptom**: Theory schemas defined but not used in processing
- **Cause**: Theory integration not yet implemented
- **Status**: This is expected - theory integration is planned for Phase A

#### **UI Only Shows Phase 1**
- **Symptom**: UI doesn't allow Phase 2 or 3 selection
- **Cause**: UI hardcoded to Phase 1, adapter pattern not yet implemented
- **Status**: This is expected - UI adapter is planned for Phase A

### **Getting Help**
1. **Check `ROADMAP_v2.md`** for current status and known issues
2. **Run verification commands** from `VERIFICATION_COMMANDS.md`
3. **Review test results** to understand what's working vs. what's not
4. **Check `ARCHITECTURE.md`** for system design and integration patterns

---

## 🎯 **Next Steps for New Contributors**

### **Week 1: Understanding the System**
1. **Read the documentation** in the order listed above
2. **Run the verification commands** to understand current capabilities
3. **Explore the UI** to see what works now
4. **Review the roadmap** to understand development priorities

### **Week 2: Contributing to Development**
1. **Pick a task** from `ROADMAP_v2.md` Phase A
2. **Understand the requirements** and success criteria
3. **Run relevant tests** to understand current state
4. **Implement the feature** following the development principles

### **Development Principles**
- **Theory-Aware**: All new features should integrate theoretical concepts
- **Integration-First**: Design interfaces before implementation
- **Verification-First**: Include test commands for all claims
- **No Mocks**: Real functionality only, no placeholder implementations

---

## 📞 **Support and Resources**

### **Key Files for Understanding**
- **`ROADMAP_v2.md`** - What we're building and current status
- **`ARCHITECTURE.md`** - How the system works
- **`VERIFICATION_COMMANDS.md`** - How to test everything
- **`KGAS_EVERGREEN_DOCUMENTATION.md`** - Theoretical foundation

### **Development Standards**
- **Single Source of Truth**: All status in `ROADMAP_v2.md`
- **Verification Required**: Every claim must have a test command
- **Theory Integration**: All features should use theoretical concepts
- **Honest Documentation**: Document what exists, not what's planned

---

**Remember**: The system is in active development. Phase 1 works well, but Phase 2 and 3 integration is in progress. Focus on understanding the current state and contributing to the next development phase. -e 
<br><sup>See `docs/planning/roadmap.md` for master plan.</sup>
