# Gemini Review Tool - Best Practices Guide

## Overview
The Gemini Review Tool automates code validation by packaging codebases with repomix and sending them to Google's Gemini AI for analysis. This guide provides best practices to avoid common pitfalls and maximize validation effectiveness.

## 🚨 **CRITICAL PRINCIPLE: Context Optimization**

**❌ AVOID**: Sending massive, unfocused context hoping the AI will "figure it out"
**✅ DO**: Send precisely what's needed for each specific validation claim

### The Problem with Large Context
- **API Limits**: Large files cause 500 errors and timeouts
- **Unfocused Analysis**: AI gets distracted by irrelevant code
- **Poor Feedback**: Generic responses instead of actionable insights
- **Cost Inefficiency**: Wastes tokens on irrelevant content

### The Solution: Focused Validation
- **One Claim Per Validation**: Validate specific claims individually
- **Minimal File Set**: Include only files directly relevant to the claim
- **Targeted Prompts**: Ask about specific line numbers and functions
- **Evidence-Based**: Request specific evidence for each assessment

## 📋 **Validation Strategy Framework**

### Step 1: Claim Decomposition
Break complex validation into focused claims:

```yaml
# BAD: Monolithic validation
claims: "Fixed async operations, ConfidenceScore integration, unit testing, and pipeline integration"

# GOOD: Decomposed validation
claims:
  - claim_1: "Async Neo4j operations use AsyncGraphDatabase (lines 127-155 in neo4j_manager.py)"
  - claim_2: "Tool auditing uses asyncio.gather concurrency (lines 318-384 in tool_factory.py)"
  - claim_3: "Unit tests use real functionality with minimal mocking (test_async_multi_document_processor.py)"
  - claim_4: "Pipeline tests chain real data flow (test_academic_pipeline_simple.py)"
```

### Step 2: Context Optimization
For each claim, include ONLY relevant files:

```bash
# Claim 1: Async Migration - ONLY async-related files
npx repomix --include "src/core/neo4j_manager.py,src/core/tool_factory.py"

# Claim 2: Testing Quality - ONLY test files  
npx repomix --include "tests/unit/test_async_multi_document_processor.py"

# Claim 3: Pipeline Integration - ONLY integration test
npx repomix --include "tests/integration/test_academic_pipeline_simple.py"
```

### Step 3: Targeted Prompting
Use specific, focused prompts:

```python
# BAD: Generic prompt
prompt = "Validate that all Phase 5.3 issues are resolved"

# GOOD: Targeted prompt
prompt = """
Validate ONLY this specific claim:

**CLAIM**: Neo4j async methods use real AsyncGraphDatabase, not sync driver wrapped in async

SPECIFIC CHECKS:
1. Line 127-155 in neo4j_manager.py: Should use AsyncGraphDatabase.driver()
2. get_session_async() method: Should use await session.run() with async driver
3. NO asyncio.sleep() used as simulation of work

EVIDENCE REQUIRED:
- Imports AsyncGraphDatabase from neo4j
- Creates _async_driver with AsyncGraphDatabase.driver()  
- Uses await with real async operations

IGNORE: Everything not related to Neo4j async operations
"""
```

## 🎯 **Best Practices by Use Case**

### Code Implementation Validation

**Purpose**: Verify specific code changes were implemented correctly

**Best Practices**:
```python
# Focus on 1-3 specific files max
files = ["src/core/security_manager.py", "src/core/auth_service.py"]

# Target specific functions/classes
prompt = """
Validate ONLY the password hashing implementation in SecurityManager.hash_password():
1. Uses bcrypt.hashpw() not plain text
2. Includes proper salt generation  
3. Validates input before hashing

Look specifically at lines 45-67 in src/core/security_manager.py.
"""
```

**File Size Limit**: < 50KB total, < 15,000 tokens

### Testing Quality Validation

**Purpose**: Verify tests use real functionality not excessive mocking

**Best Practices**:
```python
# Include ONLY the test files being validated
files = ["tests/unit/test_security_manager.py"]

# Focus on testing patterns
prompt = """
Validate testing approach in test_security_manager.py:

CRITERIA:
- Tests use real bcrypt operations (not mocked)
- External dependencies mocked minimally (database only)
- Assertions test actual results not mock calls

IGNORE: Implementation files being tested
"""
```

**File Size Limit**: < 30KB per test file

### Architecture Validation

**Purpose**: Verify system design and component interaction

**Best Practices**:
```python
# Include key interface/service files
files = ["src/core/service_manager.py", "src/core/pipeline_orchestrator.py"]

# Focus on architectural patterns
prompt = """
Validate service architecture in ServiceManager:

1. Singleton pattern implementation
2. Dependency injection for services
3. Proper service lifecycle management

Check specific methods: get_service(), register_service(), cleanup()
"""
```

**File Size Limit**: < 100KB total for architecture review

### Performance Validation

**Purpose**: Verify performance optimizations and async patterns

**Best Practices**:
```python
# Include only performance-critical files
files = ["src/core/async_api_client.py", "src/tools/phase2/async_processor.py"]

# Focus on performance patterns
prompt = """
Validate async performance patterns:

1. Uses asyncio.gather() for concurrency
2. Connection pooling implemented  
3. No blocking operations in async functions

Look for: await asyncio.gather(), aiohttp.ClientSession, async with
Avoid: time.sleep(), requests.get(), synchronous I/O
"""
```

**File Size Limit**: < 75KB for performance analysis

## 🔧 **Practical Implementation Patterns**

### Pattern 1: Sequential Focused Validation
```python
def run_focused_validations():
    """Run multiple focused validations instead of one large validation"""
    
    validations = [
        {
            "name": "async_migration",
            "files": ["src/core/neo4j_manager.py"],
            "claim": "Uses AsyncGraphDatabase for real async operations",
            "focus": "get_session_async() method implementation"
        },
        {
            "name": "test_quality", 
            "files": ["tests/unit/test_security_manager.py"],
            "claim": "Tests real cryptographic operations with minimal mocking",
            "focus": "Authentication and password hashing tests"
        }
    ]
    
    for validation in validations:
        run_validation(validation)
```

### Pattern 2: Evidence-Based Validation
```python
def create_evidence_prompt(claim, files, evidence_criteria):
    """Create prompt that requests specific evidence"""
    
    return f"""
    Validate: {claim}
    
    Files to examine: {', '.join(files)}
    
    Evidence Required:
    {chr(10).join(f"- {criteria}" for criteria in evidence_criteria)}
    
    Provide verdict with specific code examples:
    - ✅ FULLY RESOLVED: [evidence from code]
    - ⚠️ PARTIALLY RESOLVED: [what's missing] 
    - ❌ NOT RESOLVED: [specific issues found]
    """
```

### Pattern 3: Iterative Refinement
```python
def iterative_validation(claim, files):
    """Validate, get feedback, fix, re-validate"""
    
    # 1. Initial focused validation
    result = validate_claim(claim, files)
    
    # 2. If partially resolved, get specific feedback
    if result.status == "PARTIALLY_RESOLVED":
        specific_issues = extract_issues(result.feedback)
        
        # 3. Fix specific issues
        fix_issues(specific_issues)
        
        # 4. Re-validate with same focused approach
        result = validate_claim(claim, files)
    
    return result
```

## 🚫 **Common Anti-Patterns to Avoid**

### Anti-Pattern 1: Kitchen Sink Validation
```python
# ❌ BAD: Include everything hoping AI will find issues
files = [
    "src/**/*.py",           # Too broad
    "tests/**/*.py",         # Irrelevant to claim
    "docs/**/*.md",          # Documentation not code
    "config/**/*.yaml"       # Configuration not implementation
]

# ✅ GOOD: Focused on specific claim
files = ["src/core/neo4j_manager.py"]  # Only what's needed
```

### Anti-Pattern 2: Vague Prompts
```python
# ❌ BAD: Generic validation request
prompt = "Check if the code is good and all issues are fixed"

# ✅ GOOD: Specific validation criteria  
prompt = """
Validate async Neo4j implementation:
1. Uses AsyncGraphDatabase.driver() not GraphDatabase.driver()
2. Real async operations with await session.run()
3. No asyncio.sleep() simulation code

Look specifically at get_session_async() method.
"""
```

### Anti-Pattern 3: Mixed Concerns
```python
# ❌ BAD: Multiple unrelated claims in one validation
claims = [
    "Database operations are async",
    "Tests use minimal mocking", 
    "API responses are cached",
    "Documentation is complete"
]

# ✅ GOOD: One focused concern per validation
claim = "Database operations use real async patterns with AsyncGraphDatabase"
```

## 📊 **File Size Guidelines**

### Recommended Limits
- **Single Claim Validation**: < 25KB (≈ 6,000 tokens)
- **Multi-File Validation**: < 75KB (≈ 20,000 tokens)
- **Architecture Review**: < 150KB (≈ 40,000 tokens)
- **Emergency Limit**: 200KB (≈ 50,000 tokens)

### Token Estimation
```bash
# Check file size before validation
ls -la repomix-output.xml

# Estimate tokens (roughly 4 chars per token)
wc -c repomix-output.xml | awk '{print $1/4 " tokens (estimated)"}'

# If over 25,000 tokens, break into smaller validations
```

## 🔍 **Debugging Validation Issues**

### 500 Errors (Server Issues)
```bash
# Usually means file too large or API overloaded
# Solutions:
1. Reduce file size by 50%
2. Wait 10-15 minutes and retry
3. Break into smaller validations
4. Check Google AI service status
```

### Unclear Responses
```bash
# Usually means prompt too vague or context too broad
# Solutions:
1. Make prompt more specific
2. Reduce file scope
3. Ask for specific line numbers
4. Request code examples in response
```

### No Issues Found (False Negative)
```bash
# AI might be missing issues due to context overload
# Solutions:
1. Focus on specific methods/classes
2. Provide line number ranges
3. Ask about specific patterns
4. Use multiple smaller validations
```

## 📝 **Validation Templates**

### Template 1: Code Implementation
```yaml
validation_type: implementation
claim: "Specific functionality implemented correctly"
files: ["path/to/specific/file.py"]
prompt: |
  Validate [specific function/class] implementation:
  
  REQUIREMENTS:
  1. [Specific requirement 1]
  2. [Specific requirement 2]
  3. [Specific requirement 3]
  
  FOCUS: Lines [X-Y] in [filename]
  
  EVIDENCE: Show specific code that proves each requirement
```

### Template 2: Testing Quality
```yaml
validation_type: testing
claim: "Tests use real functionality with minimal mocking"
files: ["tests/unit/test_specific.py"]
prompt: |
  Validate testing approach:
  
  CRITERIA:
  - Real [functionality] execution (not mocked)
  - External dependencies mocked minimally
  - Assertions test actual results
  
  AVOID: Implementation details, focus only on test patterns
```

### Template 3: Performance/Async
```yaml
validation_type: performance
claim: "Async operations implemented correctly"
files: ["src/core/async_component.py"]
prompt: |
  Validate async implementation:
  
  PATTERNS:
  - Uses [specific async library]
  - Real non-blocking operations
  - Proper error handling
  
  ANTI-PATTERNS:
  - Blocking operations in async functions
  - Simulation code (asyncio.sleep for fake work)
```

## 🚀 **Quick Reference Commands**

### Focused Validation Workflow
```bash
# 1. Create minimal repomix for specific claim
npx repomix --include "file1.py,file2.py" --output claim1.xml .

# 2. Check file size
ls -la claim1.xml

# 3. If under 50KB, proceed with validation
python gemini_validation.py --file claim1.xml --claim "specific claim"

# 4. If over 50KB, reduce scope further
npx repomix --include "file1.py" --output claim1-reduced.xml .
```

### Emergency Size Reduction
```bash
# If validation file too large, try these in order:

# Option 1: Single file only
npx repomix --include "most_important_file.py"

# Option 2: Exclude large dependencies  
npx repomix --include "target_files.py" --ignore "tests/*,docs/*"

# Option 3: Manual extraction of specific functions
# Edit repomix output to include only relevant functions
```

## 📚 **Example Successful Validations**

### Example 1: Async Migration (✅ Focused)
```python
# Files: Only neo4j_manager.py (33KB)
# Claim: "Uses AsyncGraphDatabase for real async operations" 
# Result: ⚠️ PARTIALLY RESOLVED with specific feedback on remaining issues
# Action: Fixed specific methods mentioned in feedback
```

### Example 2: Test Quality (✅ Focused)  
```python
# Files: Only test_security_manager.py (15KB)
# Claim: "Tests real cryptographic operations with minimal mocking"
# Result: ✅ FULLY RESOLVED with evidence of real bcrypt usage
# Action: No changes needed
```

### Example 3: Integration Testing (✅ Focused)
```python
# Files: Only test_academic_pipeline_simple.py (22KB) 
# Claim: "Pipeline chains real data flow end-to-end"
# Result: ✅ FULLY RESOLVED with evidence of real workflow
# Action: No changes needed
```

## 🎯 **Success Metrics**

### Quality Indicators
- **Response Time**: < 30 seconds for focused validations
- **Feedback Quality**: Specific line numbers and code examples provided
- **Actionability**: Clear next steps for any issues found
- **Coverage**: Each claim validated thoroughly with evidence

### Efficiency Indicators  
- **Token Usage**: < 25,000 tokens per validation
- **API Success**: No 500 errors due to oversized requests
- **Iteration Speed**: Quick fix-validate cycles
- **Cost Efficiency**: Minimal token waste on irrelevant content

Remember: **Context optimization is the key to effective AI-assisted code validation.** Always ask "What is the minimum context needed to validate this specific claim?" before running any validation.