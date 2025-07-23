# Gemini Code Review Tool

A powerful automated code review tool that uses Google's Gemini AI to analyze your codebase, evaluate claims, and provide comprehensive feedback.

## Features

- 🤖 **AI-Powered Analysis**: Uses Gemini 1.5 Pro for deep code analysis
- 📦 **Smart Packaging**: Leverages repomix to create AI-friendly code bundles
- 🎯 **Critical Evaluation**: Can evaluate specific claims against actual implementation
- ⚙️ **Flexible Configuration**: YAML/JSON config files for project-specific settings
- 📋 **Review Templates**: Pre-defined templates for security, performance, etc.
- 🚫 **Smart Filtering**: Configurable include/ignore patterns to focus on relevant code
- 📚 **Documentation Aware**: Includes your docs in the analysis for better context
- 💾 **Intelligent Caching**: Caches results to avoid redundant processing

## Quick Start

### 1. Setup

```bash
# Clone or copy this tool to your system
cp -r gemini-review-tool /path/to/your/tools/

# Install dependencies
cd /path/to/your/tools/gemini-review-tool
pip install -r requirements.txt

# Setup API key
cp .env.example .env
# Edit .env and add your Gemini API key
```

### 2. Basic Usage

```bash
# Review current directory
python /path/to/gemini_review.py

# Review a specific project
python /path/to/gemini_review.py /path/to/project

# Initialize config for a project
cd /your/project
python /path/to/gemini_review.py --init
```

### 3. Advanced Usage

```bash
# Use a review template
python gemini_review.py --template security

# Critical evaluation with claims
python gemini_review.py --claims "This code has 100% test coverage"

# Include specific documentation
python gemini_review.py --docs README.md --docs docs/API.md

  # Use custom configuration
  python gemini_review.py --config my-review-config.yaml
  
  # Force fresh analysis (disable cache)
  python gemini_review.py --no-cache
  
  # Show cache information
  python gemini_review.py --cache-info
  
  # Clear cache
  python gemini_review.py --clear-cache
```

## Configuration

### Initialize for Your Project

```bash
cd /your/project
python /path/to/gemini_review.py --init
```

This creates `.gemini-review.yaml` with sensible defaults.

### Configuration File Example

```yaml
project_name: "My Awesome Project"
project_path: "."
output_format: "xml"  # or "markdown" for smaller files
keep_repomix: false

# Patterns to include (if specified, only these files are included)
include_patterns:
  - "src/**/*.py"
  - "*.md"
  - "*.yaml"
  - "*.json"

# Patterns to ignore (applied after include patterns)
ignore_patterns:
  - "node_modules"
  - "*.pyc"
  - "__pycache__"
  - ".git"
  - "venv"
  - "build"
  - "dist"

# Repomix options (optimized for LLM review)
remove_empty_lines: true      # Remove empty lines to save tokens
show_line_numbers: false      # Add line numbers for easier reference
include_diffs: false          # Include git diffs for change review
compress_code: false          # Compress code for large codebases
token_count_encoding: "gemini-pro"  # Token encoding for accurate estimation

# Documentation to include
documentation_files:
  - "README.md"
  - "docs/*.md"

# For critical evaluation
claims_of_success: |
  - Feature X is fully implemented
  - All security vulnerabilities are fixed
  - Performance is optimized

# Custom review focus
custom_prompt: |
  Focus on security and performance issues
```

## Review Templates

The tool includes several pre-configured templates:

- **security**: OWASP top 10 security audit
- **performance**: Performance bottleneck analysis
- **refactoring**: Technical debt and code quality
- **enterprise**: Enterprise architecture compliance

Use with: `python gemini_review.py --template security`

## Command Line Options

```
python gemini_review.py [OPTIONS] [PROJECT_PATH]

Options:
  --init                Initialize config file for project
  --config FILE        Use specific config file
  --template NAME      Use a review template (security, performance, etc.)
  --format FORMAT      Output format: xml or markdown
  --keep-repomix       Keep the repomix output file
  --include PATTERN    Add include pattern (can use multiple times, overrides ignore)
  --ignore PATTERN     Add ignore pattern (can use multiple times)
  --docs FILE          Include documentation file (can use multiple times)
  --no-remove-empty-lines  Keep empty lines (default: remove for token efficiency)
  --line-numbers       Add line numbers to output for easier reference
  --include-diffs      Include git diffs (shows changes since last commit)
  --compress           Compress code to reduce token count
  --token-encoding ENC Token encoding for LLM (default: gemini-pro)
  --claims TEXT        Claims to evaluate critically
  --prompt TEXT        Custom review prompt
  --api-key KEY        Gemini API key (or use .env file)
  --no-cache          Disable caching (force fresh analysis)
  --cache-dir DIR     Cache directory (default: .gemini-cache)
  --cache-max-age H   Cache max age in hours (default: 24)
  --clear-cache       Clear all cache files before running
  --cache-info        Show cache information and exit
```

## Example Workflows

### Security Audit
```bash
python gemini_review.py --template security --format markdown
```

### Architecture Review with Documentation
```bash
python gemini_review.py \
  --docs ARCHITECTURE.md \
  --docs README.md \
  --prompt "Evaluate the architecture for scalability"
```

### Review Only Specific Files
```bash
# Review only Python source files
python gemini_review.py --include "src/**/*.py" --include "*.py"

# Review only configuration files
python gemini_review.py --include "*.yaml" --include "*.json" --include "*.env.example"
```

# Advanced Repomix Options
```bash
# Review with line numbers and git diffs
python gemini_review.py --line-numbers --include-diffs

# Compress large codebase to fit in token limits
python gemini_review.py --compress --include "src/**/*.py"

# Use different token encoding for cost estimation
python gemini_review.py --token-encoding cl100k_base

# Keep empty lines (default: removed for efficiency)
python gemini_review.py --no-remove-empty-lines
```

### Critical Evaluation
```bash
python gemini_review.py \
  --claims "Our code follows all best practices and has no technical debt" \
  --docs docs/roadmap.md
```

### CI/CD Integration
```yaml
# In your CI pipeline
- name: Code Review
  run: |
    pip install -r requirements.txt
    python gemini_review.py --config .gemini-review.ci.yaml
```

## Troubleshooting

### "npx not found"
Install Node.js from https://nodejs.org/ (required for repomix)

### Token limit errors
- Use `--format markdown` for smaller output
- Add more ignore patterns
- Review subdirectories separately

### API key issues
- Ensure GEMINI_API_KEY is set in .env
- Check API key validity
- Verify API quota hasn't been exceeded

## Caching

The tool includes intelligent caching to speed up repeated reviews:

- **Repomix Cache**: Caches the output of repomix to avoid regenerating codebase packages
- **Analysis Cache**: Caches Gemini analysis results based on codebase hash and parameters
- **Smart Invalidation**: Cache expires after 24 hours (configurable)
- **Parameter Awareness**: Different cache entries for different prompts, claims, and documentation

### Cache Commands

```bash
# Show cache information
python gemini_review.py --cache-info

# Clear all cache
python gemini_review.py --clear-cache

# Disable caching for fresh analysis
python gemini_review.py --no-cache

# Custom cache settings
python gemini_review.py --cache-dir /tmp/cache --cache-max-age 48
```

## 🎯 **CRITICAL: Focused Validation Approach**

**⚠️ AVOID**: Sending massive, unfocused context hoping AI will "figure it out"  
**✅ DO**: Send precisely what's needed for each specific validation claim

### The Focused Validation Process

```bash
# Step 1: Create minimal bundle with only relevant files
npx repomix --include "tests/unit/test_specific.py,src/core/specific.py" --output validation.xml .

# Step 2: Run targeted validation  
python gemini_review.py . \
  --include "tests/unit/test_specific.py" \
  --prompt "
CRITICAL VALIDATION: [Your specific claim]

**CONTEXT**: [Why this matters]

**SPECIFIC VALIDATION REQUIRED**:
1. [Specific check 1]
2. [Specific check 2] 
3. [Specific check 3]

**EVIDENCE REQUIRED**: 
- ✅ FULLY RESOLVED / ⚠️ PARTIALLY / ❌ NOT RESOLVED
- Specific code examples with line references
- Score 1-10 for this specific issue
"
```

### Validation Guidelines

**File Size Limits**:
- Single claim validation: < 25KB (≈ 6,000 tokens)
- Multi-file validation: < 75KB (≈ 20,000 tokens)
- If you get 500 errors: **reduce file scope immediately**

**One Claim Per Validation**:
```bash
# ❌ BAD: Multiple unrelated claims
python gemini_review.py . --claims "Fixed async, tests, security, performance"

# ✅ GOOD: One focused claim
python gemini_review.py . \
  --include "tests/unit/test_auth.py" \
  --claims "Authentication tests use real functionality, not mocks"
```

## Best Practices

1. **Use Focused Validation**: One specific claim per validation run
2. **Minimal File Sets**: Include only files directly relevant to the claim  
3. **Targeted Prompts**: Ask about specific line numbers and functions
4. **Evidence-Based**: Request specific evidence for each assessment
5. **Create project-specific configs**: Commit `.gemini-review.yaml` to your repo
6. **Use include/ignore patterns strategically**: Use include patterns for precise control
7. **Include documentation**: Always include README and architecture docs
8. **Leverage caching**: Cache speeds up repeated reviews of the same codebase

## File Structure

```
gemini-review-tool/
├── gemini_review.py           # Main review script
├── gemini_review_config.py    # Configuration system
├── gemini_review_cache.py     # Caching system
├── requirements.txt           # Python dependencies
├── .env.example              # Example environment file
├── .gitignore               # Git ignore patterns
├── README.md                # This file
└── example-configs/         # Example configurations
    ├── python-project.yaml
    ├── nodejs-project.yaml
    └── enterprise-roadmap.yaml
```

## Requirements

- Python 3.7+
- Node.js (for repomix)
- Gemini API key

## License

This tool is provided as-is for code review purposes.