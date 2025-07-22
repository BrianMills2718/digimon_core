**Doc status**: Living – auto-checked by doc-governance CI

# Contributing to KGAS

**Document Version**: 1.0  
**Created**: 2025-01-27  
**Purpose**: Guidelines for contributing to the Knowledge Graph Analysis System

---

## Development Setup

### Prerequisites
- **Python**: 3.8 or higher
- **Docker**: Version 20.10 or higher
- **Git**: Latest version
- **RAM**: 16GB minimum

### Environment Setup
```bash
# Clone the repository
git clone https://github.com/your-org/kgas.git
cd kgas

# Set up Python environment
python -m venv kgas_env
source kgas_env/bin/activate  # On Windows: kgas_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start services
docker compose up -d
```

---

## Development Workflow

### 1. Create Feature Branch
```bash
# Create and switch to feature branch
git checkout -b feature/your-feature-name

# Ensure you're on the latest main
git pull origin main
```

### 2. Make Changes
- Follow the coding standards below
- Write tests for new functionality
- Update documentation as needed
- Ensure all tests pass

### 3. Commit Changes
```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: add new feature description"

# Push to remote
git push origin feature/your-feature-name
```

### 4. Create Pull Request
- Create PR against main branch
- Include description of changes
- Link any related issues
- Request review from maintainers

---

## Coding Standards

### Python Code Style
- **PEP 8**: Follow PEP 8 style guidelines
- **Type Hints**: Use type hints for all functions
- **Docstrings**: Include docstrings for all functions and classes
- **Line Length**: Maximum 88 characters per line

### Code Example
```python
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class Entity(BaseModel):
    """Represents an entity in the knowledge graph."""
    
    name: str
    entity_type: str
    confidence: float
    properties: Optional[Dict[str, Any]] = None
    
    def validate_entity(self) -> bool:
        """Validate entity data."""
        return self.confidence >= 0.0 and self.confidence <= 1.0
```

---

## Testing

### Test Requirements
- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test component interactions
- **Functional Tests**: Test end-to-end workflows
- **Test Coverage**: Aim for >90% code coverage

### Running Tests
```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/functional/test_phase1_only.py

# Run with coverage
python -m pytest --cov=src

# Run with verbose output
python -m pytest -v
```

---

## Documentation

### Documentation Standards
- **Clear and Concise**: Write clear, concise documentation
- **Examples**: Include practical examples
- **Up-to-Date**: Keep documentation current with code
- **Consistent Style**: Follow consistent documentation style

### Documentation Types
- **Code Documentation**: Inline comments and docstrings
- **API Documentation**: API reference documentation
- **User Guides**: Step-by-step user guides
- **Technical Documentation**: Technical specifications

---

## Semantic Versioning Policy

### Version Bump Rules

| Bump | Trigger | Compatibility |
|------|---------|---------------|
| MAJOR | remove/rename field, change dolce_parent | breaking |
| MINOR | add optional field, new subclass | backward-compatible |
| PATCH | typo or label edit | metadata-only |

### Version Bump Requirements
**PRs must include a justified version bump in each modified MCL or theory file.**

### Version Bump Examples
```yaml
# MAJOR version bump (breaking change)
theory_schema:
  version: "2.0.0"  # Was 1.0.0
  # Removed field: old_field
  # Changed dolce_parent: new_parent_iri

# MINOR version bump (backward-compatible)
theory_schema:
  version: "1.1.0"  # Was 1.0.0
  # Added optional field: new_optional_field

# PATCH version bump (metadata-only)
theory_schema:
  version: "1.0.1"  # Was 1.0.0
  # Fixed typo in description
```

---

## Theory Schema Development

### Schema Standards
- **DOLCE Alignment**: Every entity must have dolce_parent
- **MCL Integration**: Every entity must have mcl_id
- **Validation**: All schemas must pass validation
- **Documentation**: Include clear descriptions

### Schema Example
```json
{
  "theory_id": "social_identity_theory",
  "theory_name": "Social Identity Theory",
  "version": "1.0.0",
  "classification": {
    "domain": {
      "level": "Meso",
      "component": "Whom",
      "metatheory": "Structural"
    }
  },
  "ontology": {
    "entities": [
      {
        "name": "SocialIdentity",
        "dolce_parent": "http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#Person",
        "mcl_id": "social_identity_001",
        "properties": [
          {
            "name": "group_membership",
            "type": "List[SocialGroup]"
          }
        ]
      }
    ]
  }
}
```

---

## Pull Request Guidelines

### PR Requirements
- **Tests Pass**: All tests must pass
- **Documentation**: Update relevant documentation
- **Code Review**: Address all review comments
- **Version Bump**: Include appropriate version bumps

### PR Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Version Bumps
- [ ] MCL files updated with version bumps
- [ ] Theory schema files updated with version bumps
- [ ] Justification provided for each bump

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
```

---

## Code Review Process

### Review Criteria
- **Functionality**: Does the code work as intended?
- **Quality**: Is the code well-written and maintainable?
- **Security**: Are there any security concerns?
- **Performance**: Are there performance implications?
- **Documentation**: Is the documentation adequate?

### Review Process
1. **Automated Checks**: CI/CD pipeline runs automated checks
2. **Code Review**: Maintainers review the code
3. **Testing**: Ensure all tests pass
4. **Approval**: At least one maintainer must approve
5. **Merge**: Code is merged after approval

---

## CI/Testing Rules
- All pull requests must pass the full verification matrix (see .github/workflows/integration.yml).
- No skipped or xfail tests are allowed in PRs.
- All verification commands in VERIFICATION_COMMANDS.md must be runnable and pass.

---

## Issue Reporting

### Bug Reports
- **Clear Description**: Provide clear description of the bug
- **Reproduction Steps**: Include steps to reproduce
- **Expected vs Actual**: Describe expected vs actual behavior
- **Environment**: Include environment details

### Feature Requests
- **Use Case**: Describe the use case
- **Proposed Solution**: Suggest a solution approach
- **Impact**: Describe the impact of the feature
- **Priority**: Indicate priority level

---

## Community Guidelines

### Communication
- **Respectful**: Be respectful to all community members
- **Constructive**: Provide constructive feedback
- **Inclusive**: Welcome contributors from all backgrounds
- **Professional**: Maintain professional communication

### Code of Conduct
- **No Harassment**: Harassment of any kind is not tolerated
- **Inclusive Environment**: Create an inclusive environment
- **Respectful Disagreement**: Disagree respectfully
- **Reporting**: Report violations to maintainers

---

**Note**: These guidelines help maintain code quality and foster a positive development environment. Please follow them when contributing to KGAS. -e 
<br><sup>See `docs/planning/roadmap.md` for master plan.</sup>

## Writing a ToolPlugin

You can extend KGAS by writing a ToolPlugin or PhasePlugin. Plugins are discovered via setuptools entry points.

### Example: setup.py
```python
from setuptools import setup
setup(
    name='my_kgas_plugin',
    version='0.1',
    py_modules=['my_plugin'],
    entry_points={
        'kgas.plugins': [
            'my_tool = my_plugin:MyToolPlugin',
        ],
    },
)
```

### Example: my_plugin.py
```python
class MyToolPlugin:
    def run(self, *args, **kwargs):
        print('Hello from MyToolPlugin!')
```

- See PLUGIN_SYSTEM.md for contract and loading details.

---

## Documentation Bucket Placement

All documentation must reside in exactly **one** of the three buckets:

1. `docs/architecture/` – evergreen architecture & specs.
2. `docs/roadmap/` – development roadmap and forward-looking planning.
3. `docs/public/` – user-facing guidance and tutorials.

### When adding or updating documentation

- Place the file in the correct bucket and **avoid duplicates**.
- Update the root `TABLE_OF_CONTENTS.md` so newcomers can find it quickly.
- Run the Markdown linter locally (`npm run docs:lint`) or wait for the CI check.
- **Modifying files inside `docs/archive/` is prohibited.**  Create a new doc instead and reference the archived version if needed.
