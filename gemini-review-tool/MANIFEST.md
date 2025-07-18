# Gemini Review Tool - Distribution Manifest

## Core Files

### **Essential Runtime Files**
- `gemini_review.py` - Main application script
- `gemini_review_cache.py` - Caching system
- `gemini_review_config.py` - Configuration management
- `requirements.txt` - Python dependencies

### **Documentation**
- `README.md` - Project overview and quick start
- `USAGE.md` - Comprehensive usage guide
- `MANIFEST.md` - This file

### **Configuration**
- `install.sh` - Installation script
- `.gitignore` - Git ignore patterns
- `example-configs/` - Example configuration files

### **Testing**
- `test_gemini_review.py` - Comprehensive test suite

## Archived Files

### **Development Artifacts** (`archive/development-artifacts/`)
- `CLAUDE.md` - Development requirements and philosophy
- `Evidence.md` - Implementation validation evidence
- `FINAL_VALIDATION_REPORT.md` - External validation report
- `generate_evidence.py` - Evidence generation script
- `review` - Development artifact

### **Validation Tests** (`archive/validation-tests/`)
- Various `.yaml` configuration files used during development
- Test output files (`.xml`, `.md`)
- Validation reports

### **Documentation Drafts** (`archive/documentation-drafts/`)
- `ADVANCED_FEATURES.md` - Advanced features documentation
- `PERFORMANCE_IMPROVEMENTS.md` - Performance optimization details
- `ROBUSTNESS_IMPROVEMENTS.md` - Robustness feature documentation
- `SECURITY_IMPROVEMENTS.md` - Security feature documentation
- `USABILITY_IMPROVEMENTS.md` - Usability enhancement documentation

## Version Information

- **Version**: 1.0.0
- **Security Features**: Fully implemented and validated
- **Robustness Features**: Comprehensive error handling and retry logic
- **Performance Features**: Intelligent caching and parallel processing
- **Test Coverage**: 100% pass rate on comprehensive test suite

## Dependencies

See `requirements.txt` for Python dependencies:
- `google-generativeai` - Gemini API client
- `python-dotenv` - Environment variable management
- `pyyaml` - YAML configuration support
- `keyring` - Secure credential storage
- `questionary` - Interactive prompting
- `rich` - Rich text formatting
- `psutil` - System information
- `jinja2` - Template engine

**External Dependencies**:
- Node.js and `repomix` for codebase packaging

## Security Validation

All security features have been externally validated:
- ✅ Secure API key handling
- ✅ Path traversal prevention
- ✅ Dangerous pattern filtering
- ✅ Adaptive rate limiting
- ✅ Comprehensive error handling
- ✅ Fail-fast architecture

## Usage

See `USAGE.md` for detailed usage instructions and examples.