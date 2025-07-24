# Gemini Review Tool Improvement Plan

## Critical Issues Identified

### 1. **Path Resolution Problems**
- **Issue**: Tool runs from different directories causing confusion about which files to process
- **Impact**: Wastes API quota on wrong files, confusing results
- **Root Cause**: Hardcoded output paths and inconsistent working directory handling

### 2. **Poor Context Control**
- **Issue**: No preview or validation of what files will be included
- **Impact**: Rate limit errors, unexpected large contexts, wasted tokens
- **Root Cause**: No dry-run mode, no file matching preview

### 3. **No Size Management**
- **Issue**: No pre-flight size estimation or warnings
- **Impact**: API failures after expensive operations
- **Root Cause**: Size checking happens after repomix, not before

## Priority Fixes

### A. **Critical Path Fixes**

#### A1. Fix Working Directory Handling
```python
# Current problematic code in run_repomix():
output_file = Path(__file__).parent / f"repomix-output.{ext}"  # WRONG

# Should be:
output_file = Path.cwd() / f"repomix-output.{ext}"  # In project dir
```

#### A2. Add Dry-Run Mode
```python
def preview_repomix(self, project_path: str, include_patterns: List[str] = None, 
                   ignore_patterns: List[str] = None) -> Dict[str, Any]:
    """Preview what files will be included without running repomix"""
    # Use glob patterns to match files
    # Estimate size
    # Return preview info
```

#### A3. Add Size Validation
```python
def validate_context_size(self, file_list: List[Path], max_size_mb: float = 1.0) -> bool:
    """Check if files will exceed size limits before processing"""
    total_size = sum(f.stat().st_size for f in file_list if f.exists())
    size_mb = total_size / (1024 * 1024)
    return size_mb <= max_size_mb
```

### B. **UX Improvements**

#### B1. Better Config Validation
```python
def validate_config(config: ReviewConfig) -> List[str]:
    """Validate config and return list of issues"""
    issues = []
    
    # Check if include patterns match any files
    if config.include_patterns:
        for pattern in config.include_patterns:
            matches = list(Path('.').glob(pattern))
            if not matches:
                issues.append(f"Include pattern '{pattern}' matches no files")
    
    return issues
```

#### B2. Interactive Size Management
```python
def interactive_size_check(self, estimated_size_mb: float) -> bool:
    """Warn user about large contexts and get confirmation"""
    if estimated_size_mb > 1.0:
        print(f"⚠️  Large context detected: {estimated_size_mb:.1f}MB")
        print("   This may hit rate limits or be expensive")
        return input("Continue? [y/N]: ").lower().startswith('y')
    return True
```

#### B3. File Preview Mode
```bash
# New command line option
python gemini_review.py --preview --include "*.py" .
# Output:
# 📋 Preview Mode - Files that would be included:
# ✅ src/main.py (2.1KB)
# ✅ src/utils.py (1.8KB)
# ❌ tests/test_main.py (excluded by ignore patterns)
# 📊 Total: 2 files, 3.9KB estimated
```

## Implementation Priority

### Phase 1: Critical Fixes (High Priority)
1. **Fix path resolution** - prevents wrong files being processed
2. **Add dry-run mode** - prevents waste of API quota
3. **Add size validation** - prevents rate limit errors

### Phase 2: UX Improvements (Medium Priority)  
4. **Config validation** - better error messages
5. **Interactive confirmations** - user control over expensive operations
6. **File preview mode** - transparency about what will be processed

### Phase 3: Advanced Features (Low Priority)
7. **Smart context splitting** - auto-split large contexts
8. **Cost estimation** - predict token usage and costs
9. **Template improvements** - better defaults for common use cases

## Specific Code Changes

### 1. Fix Path Resolution in `run_repomix()`

**Location**: `gemini_review.py:640`

**Current Code**:
```python
output_file = Path(__file__).parent / f"repomix-output.{ext}"
```

**Fixed Code**:
```python
# Use project directory, not tool directory
if project_path == ".":
    output_file = Path.cwd() / f"repomix-output.{ext}"
else:
    output_file = Path(project_path) / f"repomix-output.{ext}"
```

### 2. Add Preview Function

**Location**: Add new method to main class

```python
def preview_inclusion(self, project_path: str, include_patterns: List[str] = None,
                     ignore_patterns: List[str] = None) -> Dict[str, Any]:
    """Preview what files would be included"""
    project_dir = Path(project_path)
    
    # Get all files if no include patterns
    if not include_patterns:
        all_files = list(project_dir.rglob("*"))
        candidate_files = [f for f in all_files if f.is_file()]
    else:
        # Apply include patterns
        candidate_files = []
        for pattern in include_patterns:
            matches = list(project_dir.glob(pattern))
            candidate_files.extend([f for f in matches if f.is_file()])
    
    # Apply ignore patterns
    final_files = []
    for file_path in candidate_files:
        relative_path = file_path.relative_to(project_dir)
        ignored = False
        
        if ignore_patterns:
            for ignore_pattern in ignore_patterns:
                if file_path.match(ignore_pattern) or str(relative_path).find(ignore_pattern) != -1:
                    ignored = True
                    break
        
        if not ignored:
            final_files.append(file_path)
    
    # Calculate size
    total_size = sum(f.stat().st_size for f in final_files if f.exists())
    
    return {
        "files": final_files,
        "count": len(final_files),
        "total_size_bytes": total_size,
        "total_size_mb": total_size / (1024 * 1024),
        "estimated_tokens": total_size // 4  # Rough estimate
    }
```

### 3. Add Size Warning

**Location**: Before `run_repomix()` call in `review()` method

```python
# Add before line 944 in review() method
if not preview_mode:  # New parameter
    preview = self.preview_inclusion(
        str(validated_path), include_patterns, ignore_patterns
    )
    
    if preview["total_size_mb"] > 1.0:
        print(f"⚠️  Large context: {preview['total_size_mb']:.1f}MB ({preview['count']} files)")
        print(f"   Estimated tokens: {preview['estimated_tokens']:,}")
        print(f"   This may hit rate limits or incur high costs")
        
        if not force_mode:  # New parameter
            confirm = input("Continue? [y/N]: ")
            if not confirm.lower().startswith('y'):
                print("❌ Operation cancelled")
                return "Operation cancelled by user"
```

### 4. Add Preview CLI Option

**Location**: In argument parser section

```python
# Add to parser around line 1100
parser.add_argument(
    '--preview', 
    action='store_true',
    help='Preview files that would be included without running analysis'
)

parser.add_argument(
    '--force', 
    action='store_true',
    help='Skip size warnings and confirmations'
)
```

### 5. Add Config Validation

**Location**: After config loading around line 1248

```python
# Add after config loading
if config:
    validation_issues = self.validate_config(config)
    if validation_issues:
        print("⚠️  Configuration issues found:")
        for issue in validation_issues:
            print(f"   - {issue}")
        
        if not args.force:
            confirm = input("Continue anyway? [y/N]: ")
            if not confirm.lower().startswith('y'):
                print("❌ Fix configuration issues or use --force")
                sys.exit(1)
```

## Testing the Improvements

### Test Case 1: Path Resolution
```bash
# From project root
python gemini-review-tool/gemini_review.py --include "src/*.py" .
# Should process project src/*.py files, not tool files

# From tool directory  
cd gemini-review-tool
python gemini_review.py --include "src/*.py" ..
# Should process project src/*.py files, not tool files
```

### Test Case 2: Preview Mode
```bash
python gemini-review-tool/gemini_review.py --preview --include "agent_stress_testing/*.py" .
# Should show:
# ✅ agent_stress_testing/real_claude_integration.py (27KB)
# ✅ agent_stress_testing/real_kgas_integration.py (28KB)  
# 📊 Total: 2 files, 55KB estimated
```

### Test Case 3: Size Warnings
```bash
python gemini-review-tool/gemini_review.py --include "**/*.py" .
# Should show warning:
# ⚠️  Large context: 15.2MB (342 files)
# Continue? [y/N]:
```

## Benefits of These Changes

1. **Eliminates Path Confusion**: Clear working directory handling
2. **Prevents Wasted API Calls**: Preview and size validation before expensive operations
3. **Better User Control**: Interactive confirmations for large operations
4. **Transparent Operation**: Users see exactly what will be processed
5. **Faster Iteration**: Dry-run mode for testing configurations
6. **Cost Management**: Size and token estimation before API calls

## Backward Compatibility

All changes maintain backward compatibility:
- Existing configs continue to work
- Default behavior unchanged when new flags not used
- Existing command line arguments unchanged
- Only new optional features added