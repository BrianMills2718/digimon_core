# [PROJECT_NAME] [PHASE_NAME] - Implementation Guide

## 🎯 Mission & Status
**Target**: [Specific goal/milestone]  
**Status**: [X%] complete - [N] issues remaining  
**Priority**: [Issue 1], [Issue 2], [Issue 3]

## ⚡ Quick Commands
```bash
# Essential commands for this phase
[test_command]              # Run tests
[build_command]             # Build/compile
[validation_command]        # Validate implementation
[deploy_command]            # Deploy/release
```

## 💡 Core Principles
1. **Production-Ready Only**: No mocks, stubs, or TODOs
2. **Fail Fast**: Explicit errors with clear messages
3. **Evidence-Based**: Every claim needs proof via tests/logs
4. **Thread-Safe**: All code handles concurrent access

## 📋 Implementation Checklist
- [ ] **[Issue 1]** - [Brief description] `[file_path]`
- [ ] **[Issue 2]** - [Brief description] `[file_path]`  
- [ ] **[Issue 3]** - [Brief description] `[file_path]`
- [ ] **Integration Tests** - All fixes work together
- [ ] **Evidence Files** - Document with actual test output
- [ ] **Validation** - External review passes

## 🏗️ Key Files & Structure
```
[project_root]/
├── [core_dir]/[critical_file_1]     # [Description]
├── [core_dir]/[critical_file_2]     # [Description]  
├── tests/[test_category]/           # Test suites
└── Evidence_[Feature].md            # Implementation proof
```

## 🔍 Validation Requirements
**Evidence Standard**: Each fix needs Evidence_[Name].md with:
- Test output proving functionality works
- Error handling demonstrations  
- Performance metrics
- Integration proof

**Validation Command**:
```bash
cd [validation_dir] && [validation_tool] --config [config_file]
```

## ⚠️ Critical Pitfalls
- **No in-memory-only data** - Must persist across restarts
- **No silent failures** - Always log errors with context
- **No untested claims** - Demonstrate every feature works

---

<details>
<summary>📖 Detailed Implementation Guide (Click to expand)</summary>

### Issue 1: [Name] - [Priority]
**File**: `[path]` | **Impact**: [Description]

**Problem**: [Current issue description]

**Solution**:
1. [Step 1]
2. [Step 2] 
3. [Step 3]

**Code Example**:
```[language]
// Key implementation snippet
[critical_code_example]
```

### Issue 2: [Name] - [Priority]
**File**: `[path]` | **Impact**: [Description]

[Similar structure...]

### Issue 3: [Name] - [Priority]
**File**: `[path]` | **Impact**: [Description]

[Similar structure...]

</details>

---

<details>
<summary>🛠️ Environment & Commands (Click to expand)</summary>

### Development Environment
```bash
# Setup
[env_setup_command_1]
[env_setup_command_2]

# Development workflow  
[dev_start_command]
[dev_test_command]
[dev_lint_command]
```

### Testing Strategy
- **Unit Tests**: `[unit_test_command]`
- **Integration Tests**: `[integration_test_command]` 
- **Performance Tests**: `[perf_test_command]`
- **Coverage**: Target [X]% minimum

### Service Dependencies
- [Service A] → [Service B]
- [Service C] → [Service D]
- All services → [Base Service]

</details>

---

<details>
<summary>🔧 Troubleshooting (Click to expand)</summary>

### Common Issues
**[Error Type]**: [Description]
- **Symptoms**: [What you see]
- **Cause**: [Root cause]  
- **Fix**: [Solution]

**[Performance Issue]**: [Description]
- **Baseline**: [Expected performance]
- **Threshold**: [Acceptable limits]
- **Monitor**: [How to check]

### Debug Commands
```bash
[debug_command_1]           # [What it shows]
[debug_command_2]           # [What it shows]
[log_command]               # View logs
```

</details>