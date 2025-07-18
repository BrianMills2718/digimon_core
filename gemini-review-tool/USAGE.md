# Gemini Review Tool - Usage Guide

## Overview

The Gemini Review Tool is a secure, robust code review automation system that uses Google's Gemini AI to analyze codebases and provide detailed feedback.

## Features

### 🔒 **Security Features**
- **Secure API Key Management**: Keyring support, environment variables, secure prompting
- **Path Traversal Prevention**: Comprehensive input validation against malicious paths
- **Pattern Injection Protection**: Filters dangerous shell commands and injection attempts
- **Adaptive Rate Limiting**: Protects against API quota exhaustion with dynamic adjustment

### 🛡️ **Robustness Features**
- **Comprehensive Error Handling**: Specific exception types with detailed context
- **Automatic Retry Logic**: Exponential backoff for transient failures
- **Comprehensive Logging**: Multi-level logging with console and file output
- **Fail-Fast Architecture**: Immediate error detection and reporting

### ⚡ **Performance Features**
- **Intelligent Caching**: LRU caching with large file sampling optimization
- **Parallel Processing**: Concurrent file processing for large codebases
- **Memory Optimization**: Prevents resource exhaustion with smart limits
- **Timeout Protection**: Prevents hanging operations

## Quick Start

### Installation

```bash
# Install Node.js dependencies (for repomix)
npm install -g repomix

# Install Python dependencies
pip install -r requirements.txt

# Set up your API key
export GEMINI_API_KEY="your-api-key-here"
```

### Basic Usage

```bash
# Review current directory
python gemini_review.py

# Review specific project
python gemini_review.py /path/to/project

# Use configuration file
python gemini_review.py --config my-review.yaml

# Focus on specific aspects
python gemini_review.py --prompt "Focus on security vulnerabilities"
```

### Configuration

Create a YAML configuration file:

```yaml
project_name: "My Project Review"
project_path: "/path/to/project"
output_format: "markdown"
custom_prompt: "Focus on code quality and security"
ignore_patterns:
  - "*.pyc"
  - "node_modules"
  - ".git"
include_patterns:
  - "*.py"
  - "*.js"
  - "*.md"
```

## Command Line Options

- `--config, -C`: Path to configuration file
- `--prompt, -p`: Custom prompt for specific focus
- `--format, -f`: Output format (xml, markdown)
- `--ignore, -i`: Patterns to ignore
- `--include, -I`: Patterns to include
- `--keep-repomix, -k`: Keep repomix output file
- `--line-numbers`: Add line numbers to output
- `--compress`: Compress code for large codebases
- `--no-cache`: Disable caching
- `--clear-cache`: Clear cache before running

## Security Best Practices

1. **API Key Management**:
   - Use environment variables: `export GEMINI_API_KEY="..."`
   - Or use system keyring for secure storage
   - Avoid passing API keys via command line

2. **Input Validation**:
   - The tool automatically validates all file paths
   - Dangerous patterns are filtered from user input
   - No additional configuration needed

3. **Rate Limiting**:
   - Built-in adaptive rate limiting
   - Automatically adjusts based on API responses
   - No manual configuration required

## Example Configurations

See the `example-configs/` directory for sample configurations:
- `nodejs-project.yaml`: Node.js project review
- `python-project.yaml`: Python project review
- `enterprise-roadmap.yaml`: Enterprise project review

## Testing

Run the comprehensive test suite:

```bash
python test_gemini_review.py
```

## Troubleshooting

### Common Issues

1. **API Key Issues**:
   - Ensure `GEMINI_API_KEY` is set
   - Check API key format and permissions
   - Try interactive mode for secure prompting

2. **Repomix Issues**:
   - Ensure Node.js is installed
   - Install repomix: `npm install -g repomix`
   - Check file permissions in project directory

3. **Large Codebases**:
   - Use `--compress` flag
   - Add appropriate ignore patterns
   - Consider using include patterns for specific files

### Error Handling

The tool provides detailed error messages with specific exception types:
- `ValidationError`: Input validation issues
- `APIError`: Gemini API problems
- `FileSystemError`: File access issues
- `ConfigurationError`: Configuration problems

## Support

For issues and questions:
1. Check the error message for specific guidance
2. Review the configuration examples
3. Ensure all dependencies are installed
4. Verify API key is valid and accessible