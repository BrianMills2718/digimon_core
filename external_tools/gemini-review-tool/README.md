# Gemini Code Review Tool

A powerful automated code review tool that uses Google's Gemini AI to analyze your codebase, evaluate claims, and provide comprehensive feedback.

## Features

- 🤖 **AI-Powered Analysis**: Uses Gemini 1.5 Pro for deep code analysis
- 📦 **Smart Packaging**: Leverages repomix to create AI-friendly code bundles
- 🎯 **Critical Evaluation**: Can evaluate specific claims against actual implementation
- ⚙️ **Flexible Configuration**: YAML/JSON config files for project-specific settings
- 📋 **Review Templates**: Pre-defined templates for security, performance, etc.
- 🚫 **Smart Filtering**: Configurable ignore patterns to focus on relevant code
- 📚 **Documentation Aware**: Includes your docs in the analysis for better context

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

# Patterns to ignore
ignore_patterns:
  - "node_modules"
  - "*.pyc"
  - "__pycache__"
  - ".git"
  - "venv"
  - "build"
  - "dist"

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
  --ignore PATTERN     Add ignore pattern (can use multiple times)
  --docs FILE          Include documentation file (can use multiple times)
  --claims TEXT        Claims to evaluate critically
  --prompt TEXT        Custom review prompt
  --api-key KEY        Gemini API key (or use .env file)
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

## Best Practices

1. **Create project-specific configs**: Commit `.gemini-review.yaml` to your repo
2. **Use ignore patterns liberally**: Reduce token usage and focus reviews
3. **Include documentation**: Always include README and architecture docs
4. **Be specific with claims**: The more specific the claims, the better the evaluation
5. **Use templates**: Start with templates and customize as needed

## File Structure

```
gemini-review-tool/
├── gemini_review.py           # Main review script
├── gemini_review_config.py    # Configuration system
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