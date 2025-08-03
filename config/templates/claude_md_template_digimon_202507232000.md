# [PROJECT_NAME] [PHASE_NAME] - Implementation Guide Template

## 🚀 CURRENT MISSION: [Brief description of current objectives]

**Status**: [Completion percentage] - [Number] critical issues remaining
**Target**: [Specific goal/milestone description]

## 📋 Critical Issues to Fix

### 1. [Issue Name] (Priority: [CRITICAL/HIGH/MEDIUM])
**File**: `[file_path_here]`
**Issue**: [Description of the issue]
**Impact**: [Business/technical impact description]

### 2. [Issue Name] (Priority: [CRITICAL/HIGH/MEDIUM])
**File**: `[file_path_here]` ([CREATE NEW/MODIFY EXISTING])
**Issue**: [Description of the issue]
**Impact**: [Business/technical impact description]

### 3. [Issue Name] (Priority: [CRITICAL/HIGH/MEDIUM])
**File**: `[file_path_here]` ([CREATE NEW/MODIFY EXISTING])
**Issue**: [Description of the issue]
**Impact**: [Business/technical impact description]

## 💡 Coding Philosophy

### Core Principles

1. **No Lazy Implementations**
   - ❌ NO mocking, stubs, or placeholders
   - ❌ NO simplified implementations with reduced functionality
   - ❌ NO pseudo-code or "TODO" comments
   - ✅ Full, production-ready implementations only
   - ✅ Real database connections, real async operations
   - ✅ Complete error handling and edge cases

2. **Fail Fast Approach**
   - ❌ NO silent error suppression
   - ❌ NO default fallbacks that hide problems
   - ✅ Explicit error raising with clear messages
   - ✅ Validate inputs early and comprehensively
   - ✅ Log errors with full context

3. **Evidence-Based Development**
   - ❌ NO claiming success without proof
   - ✅ Every implementation must be tested
   - ✅ Create Evidence.md files with actual logs
   - ✅ Demonstrate functionality with real examples
   - ✅ Include performance metrics and edge cases

4. **Test Everything**
   - Assume nothing works until proven
   - Write tests that actually exercise the code
   - Test error conditions and edge cases
   - Measure and document performance

## 🏗️ Codebase Structure

### Directory Layout
```
[PROJECT_ROOT]/
├── [source_directory]/
│   ├── [core_module]/              # Core services and managers
│   │   ├── [service_1].py
│   │   ├── [service_2].py
│   │   └── [service_n].py
│   ├── [feature_module]/
│   │   ├── [component_1].py
│   │   └── [component_2].py
│   └── [utility_module]/           # Utility components
├── tests/
│   └── [test_category]/            # Test suites
├── [validation_tool_directory]/    # Validation tools
└── Evidence.md files               # Proof of implementation

### Key Entry Points
- `[entry_point_1]` - [Description]
- `[entry_point_2]` - [Description]
- `[entry_point_3]` - [Description]
- `[test_directory]/*` - Test suite for validation

### Service Dependencies
1. [Service A] → [Service B]
2. [Service C] → [Service D]
3. All services → [Core Service]
4. All services → [Base Service]
```

## 🔧 Detailed Implementation Instructions

### Fix 1: [Issue Name] in [Component Name]

**Location**: `[file_path]`

**Current Problem**:
```[language]
# [Line reference]: [Problem description]
[current_problematic_code]
```

**Required Implementation**:
1. [Step 1 description]
2. [Step 2 description]
3. [Step 3 description]

**Step-by-Step Fix**:

```[language]
# [Implementation details with code examples]
# [Detailed implementation goes here]
```

**Integration in [Component Name]**:
```[language]
# [Integration code examples]
# [Show how changes integrate with existing code]
```

### Fix 2: [Issue Name] Implementation

**Create New File**: `[file_path]`

```[language]
"""
[Module description]

[Feature list and capabilities]
"""

# [Complete implementation code goes here]
```

### Fix 3: [Issue Name] Implementation

**Create New File**: `[file_path]`

```[language]
"""
[Module description]

[Feature list and capabilities]
"""

# [Complete implementation code goes here]
```

## 📋 Implementation Checklist

### Step 1: [Fix Description]
- [ ] [Specific task 1]
- [ ] [Specific task 2]
- [ ] [Specific task 3]
- [ ] [Generate evidence file]

### Step 2: [Fix Description]
- [ ] [Specific task 1]
- [ ] [Specific task 2]
- [ ] [Specific task 3]
- [ ] [Generate evidence file]

### Step 3: [Fix Description]
- [ ] [Specific task 1]
- [ ] [Specific task 2]
- [ ] [Specific task 3]
- [ ] [Generate evidence file]

### Step 4: Integration Testing
- [ ] Test all fixes together
- [ ] Verify no performance regression
- [ ] Check thread safety under load
- [ ] Generate Evidence_IntegrationTests.md

## 📊 Evidence Requirements

Each Evidence.md file must contain:

1. **Implementation Proof**
   - Code snippets showing key functionality
   - Test output demonstrating features work
   - Performance metrics where applicable

2. **Error Handling**
   - Examples of error conditions being caught
   - Logs showing proper error messages
   - Recovery mechanism demonstrations

3. **Edge Cases**
   - Concurrent operation tests
   - Resource exhaustion scenarios
   - Invalid input handling

4. **Integration**
   - How component integrates with existing system
   - Dependencies properly managed
   - No breaking changes to existing code

## 🔍 Validation Process

After implementing all fixes:

1. **Create Evidence Files**
   ```bash
   # Run tests and capture output
   [test_command_1] > Evidence_[Feature1].md
   [test_command_2] > Evidence_[Feature2].md
   [test_command_3] > Evidence_[Feature3].md
   ```

2. **Prepare [Validation Tool] Validation**
   ```yaml
   # [validation_config_path]
   verification_config:
     name: "[Phase Name] Final Validation"
     timestamp: "[DATE]"
     
   claims_of_success:
     - claim: "[Claim description]"
       evidence: "[Evidence description]"
       files: ["[file_path]"]
       
     - claim: "[Claim description]"
       evidence: "[Evidence description]"
       files: ["[file_path]"]
       
     - claim: "[Claim description]"
       evidence: "[Evidence description]"
       files: ["[file_path]"]
   
   target_files:
     - [file_path_1]
     - [file_path_2]
     - [file_path_3]
   
   validation_prompt: |
     Validate that all [Phase Name] issues are resolved:
     1. [Validation criterion 1]
     2. [Validation criterion 2]
     3. [Validation criterion 3]
   ```

3. **Run Validation**
   ```bash
   cd [validation_tool_directory]
   [validation_command] --config [config_file]
   ```

4. **If Issues Found**
   - Fix identified issues
   - Update Evidence.md files
   - Re-run validation
   - Repeat until no issues remain

5. **Update This File**
   - When all issues are resolved, update status
   - Remove completed instructions
   - Add next phase implementation guide

## ⚠️ Common Pitfalls to Avoid

1. **Don't Use In-Memory Only Storage**
   - [Data type] must persist
   - [Data type] must survive restarts
   - [Configuration type] must be saved

2. **Don't Ignore Thread Safety**
   - All new code must handle concurrent access
   - Use appropriate locks and async patterns
   - Test under concurrent load

3. **Don't Skip Error Cases**
   - Test what happens when thresholds are exceeded
   - Test recovery from failures
   - Ensure graceful degradation

4. **Don't Claim Success Without Evidence**
   - Run actual tests
   - Capture real output
   - Demonstrate edge cases

Remember: The goal is production-ready code that actually works, not just code that looks like it might work.