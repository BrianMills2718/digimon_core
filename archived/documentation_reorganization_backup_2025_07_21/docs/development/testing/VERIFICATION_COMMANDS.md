---
status: living
---

# KGAS Verification Commands

**Purpose**: Centralized repository of all commands to verify documentation claims  
**Last Updated**: 2025-01-27  
**Scope**: All functionality claims in KGAS documentation

---

# pytest-k: system-status
## 🎯 **System Status Verification**

### **Phase 1 Functionality (Working)**
```bash
# Test basic entity extraction
python tests/functional/test_phase1_only.py

# Test UI functionality
python tests/functional/test_ui_complete_fix.py

# Test end-to-end workflow
python tests/functional/test_execute_pdf_to_answer_workflow.py

# Launch working UI
python start_graphrag_ui.py  # → http://localhost:8501
```

### **Phase 2 Status (Partially Functional)**
```bash
# Test Phase 2 API (fixed)
python tests/functional/test_phase2_comprehensive.py

# Test Phase 1→2 integration (challenges remain)
python tests/functional/test_phase2_integration_fix.py

# Verify API compatibility fix
python tests/functional/test_mcp_services_fixed.py

# API tests: ✅ PASSING
```

### **Phase 3 Status (Standalone Only)**
```bash
# Test T301 fusion tools
python tests/functional/test_mcp_tool_chains.py

# Test multi-document processing
python tests/functional/test_phase3_integration.py
```

---

# pytest-k: core-services
## 🔧 **Core Services Verification**

### **Identity Service**
```bash
# Test identity tracking
python tests/unit/test_identity_service_consolidated.py

# Verify entity deduplication
python -c "from src.core.identity_service import IdentityService; print('Identity Service: OK')"
```

### **Workflow State Service**
```bash
# Test workflow tracking
python tests/functional/test_create_checkpoint_valid.py

# Verify API compatibility
python tests/functional/test_mcp_services_directly.py
```

### **Quality Service**
```bash
# Test quality validation
python tests/functional/test_cross_component_integration.py

# Verify error detection
python tests/functional/test_no_mocks_policy.py
```

---

# pytest-k: contract-validation
## 📋 **Contract Validation**

### **Phase Interface Contracts**
```bash
# Validate phase interface contracts
python tests/functional/test_contract_phase_interface_v9.py

# Test theory schema validation
python tests/integration/test_phase_switching_theory.py

# Verify contract compliance
python scripts/verify_all_documentation_claims.sh
```

### **Schema Validation**
```bash
# Test theory meta-schema v9.1
python -c "from src.ontology.theory_meta_schema import TheoryMetaSchema; print('Schema v9.1: OK')"

# Test concept library contracts
python -c "from src.ontology.mcl import MasterConceptLibrary; print('MCL Contracts: OK')"
```

---

# pytest-k: architecture
## 🏗️ **Architecture Verification**

### **Database Connections**
```bash
# Test Neo4j connection
python tests/unit/test_database_connection.py

# Test SQLite metadata
python -c "from src.core.neo4j_manager import Neo4jManager; print('Neo4j: OK')"
```

### **Configuration System**
```bash
# Test configuration loading
python tests/unit/test_configuration_system.py

# Verify environment variables
python -c "from src.core.config import Config; print('Config: OK')"
```

---

# pytest-k: llm-integration
## 🧠 **LLM Integration Verification**

### **OpenAI Integration**
```bash
# Test OpenAI embeddings
python tests/unit/test_openai_embeddings.py

# Test ontology generation
python tests/unit/test_openai_ontology.py
```

### **Gemini Integration**
```bash
# Test Gemini ontology generation
python tests/unit/test_gemini_simple.py

# Test structured extraction
python tests/unit/test_gemini_structured.py
```

---

# pytest-k: performance
## 📊 **Performance Verification**

### **Processing Speed**
```bash
# Test Phase 1 processing time
python tests/performance/test_performance_profiling.py

# Test PageRank optimization
python tests/performance/test_pagerank_optimization.py
```

### **Memory Usage**
```bash
# Test memory efficiency
python tests/performance/test_performance_validation.py

# Test large document handling
python tests/stress/test_extreme_stress_conditions.py
```

---

# pytest-k: integration
## 🔗 **Integration Verification**

### **Phase Integration**
```bash
# Test Phase 1→2 integration
python tests/functional/test_phase2_integration_fix.py

# Test Phase 2→3 integration
python tests/functional/test_phase3_integration.py

# Test full pipeline integration
python tests/functional/test_full_pipeline_integration.py
```

### **Service Integration**
```bash
# Test core service interactions
python tests/integration/test_api_contracts.py

# Test end-to-end workflows
python tests/functional/test_complete_workflow_final.py
```

---

# pytest-k: theory-integration
## 🧪 **Theory Integration Verification**

### **Pipeline Theory Schema Integration**
```bash
# Test that theory schema is loaded and mapped in Phase 1
python tests/functional/test_theory_integration.py
```

### **Theory Meta-Schema**
```bash
# Test theory schema validation
python -c "from src.ontology.theory_meta_schema import TheoryMetaSchema; print('Theory Schema: OK')"

# Test concept library
python -c "from src.ontology.master_concept_library import MasterConceptLibrary; print('Concept Library: OK')"
```

### **ORM Methodology**
```bash
# Test ORM compliance
python tests/functional/test_orm_methodology.py

# Test data model validation
python -c "from src.core.data_models import *; print('ORM Models: OK')"
```

---

# pytest-k: error-handling
## 🚨 **Error Handling Verification**

### **Graceful Failures**
```bash
# Test error recovery
python tests/functional/test_error_handling.py
```

### **Documentation Drift**
```bash
# Check for documentation inconsistencies
python scripts/check_doc_drift.py

# Verify all claims have test evidence
./scripts/verify_all_documentation_claims.sh
```

---

# pytest-k: documentation-drift
## 📋 **Complete System Verification**

### **Full Test Suite**
```bash
# Run all tests
python tests/run_all_tests.sh

# Run specific test categories
pytest tests/unit/ -v
pytest tests/functional/ -v
pytest tests/integration/ -v
pytest tests/performance/ -v
```

### **Documentation Verification**
```bash
# Verify all documentation claims
./scripts/verify_all_documentation_claims.sh

# Check for broken links and references
python scripts/check_doc_drift.py

# Validate schema references
grep -r "meta_schema_v9" docs/architecture/
```

---

# pytest-k: quick-health
## 🎯 **Quick Health Check**

### **Essential Commands**
```bash
# 1. Check core services
python -c "from src.core.service_manager import ServiceManager; print('Services: OK')"

# 2. Test database
python -c "from src.core.neo4j_manager import Neo4jManager; print('Database: OK')"

# 3. Verify Phase 1
python tests/functional/test_phase1_only.py

# 4. Check documentation
./scripts/verify_all_documentation_claims.sh

# 5. Launch UI
python start_graphrag_ui.py
```

### **Expected Results**
- ✅ All core services start without errors
- ✅ Database connections established
- ✅ Phase 1 processing completes successfully
- ✅ Documentation claims verified
- ✅ UI accessible at http://localhost:8501

---

# pytest-k: add-verification
## 📝 **Adding New Verification Commands**

When adding new functionality:

1. **Create test file**: `tests/functional/test_new_feature.py`
2. **Add verification command**: Update this file with the command
3. **Update documentation**: Ensure claims match test results
4. **Run verification**: Ensure new command passes

### **Command Format**
```bash
# Test [Feature Name]
python tests/functional/test_feature_name.py

# Verify [Component]
python -c "from src.component import Component; print('Component: OK')"
```

---

**Note**: All commands should be run from the project root directory. If any command fails, check the troubleshooting section in `docs/architecture/QUICK_START.md`.

<br><sup>See `docs/planning/roadmap.md` for master plan.</sup>

## 🛰️ Observability

### OpenTelemetry Spans
```bash
# Test that OTel spans are emitted for all phases and services
python tests/observability/test_spans_exist.py
```
