# GitHub Actions & Templates - CLAUDE.md

## Overview
The `.github/` directory contains GitHub-specific configuration including CI/CD workflows, pull request templates, and automation scripts. This directory is critical for maintaining code quality, automating deployments, and ensuring consistent development practices.

## Directory Structure

### Workflow Automation (`workflows/`)
- **`ci-tests.yml`**: Continuous integration testing pipeline
- **`docs-ci.yml`**: Documentation validation and deployment
- **`docs_check.yml`**: Documentation consistency checking
- **`integration.yml`**: Integration testing workflow
- **`production-deploy.yml`**: Production deployment automation

### Templates
- **`PULL_REQUEST_TEMPLATE.md`**: Standard pull request template
- **`pull_request_template.md`**: Alternative PR template

## CI/CD Pipeline Architecture

### Pipeline Strategy
```yaml
# Multi-stage pipeline approach:
1. Code Quality    → Linting, formatting, type checking
2. Unit Testing    → Fast feedback on individual components
3. Integration     → Multi-component testing
4. Security        → Vulnerability scanning and secrets detection
5. Documentation   → Docs build and validation
6. Deployment      → Automated production deployment (on main)
```

### Workflow Triggers
- **Push to main**: Full pipeline including deployment
- **Pull requests**: Quality gates and testing (no deployment)
- **Scheduled**: Nightly comprehensive testing and security scans
- **Manual**: On-demand deployment and testing workflows

## Key Workflows

### CI Testing Pipeline (`ci-tests.yml`)
```yaml
# Comprehensive testing workflow
name: CI Tests
triggers:
  - push: [main, develop]
  - pull_request: [main]
  - schedule: "0 2 * * *"  # Nightly at 2 AM

jobs:
  quality:
    - Lint and format checking (black, flake8, isort)
    - Type checking (mypy)
    - Security scanning (bandit, safety)
    - Dependency checking (pip-audit)
  
  unit-tests:
    - Python 3.9, 3.10, 3.11 matrix
    - Fast unit tests with mocking
    - Coverage reporting (>90% required)
    - Contract validation
  
  integration-tests:
    - Real database testing (Neo4j + SQLite)
    - Service integration validation
    - Cross-component workflows
    - Performance benchmarking
```

### Documentation Pipeline (`docs-ci.yml`, `docs_check.yml`)
```yaml
# Documentation validation and deployment
name: Documentation CI
triggers:
  - push: [main]
  - pull_request: [main]
  - paths: ["docs/**", "*.md"]

jobs:
  validation:
    - Markdown linting and link checking
    - Documentation structure validation
    - Architecture consistency checking
    - Planning document synchronization
  
  deployment:
    - Build documentation site
    - Deploy to GitHub Pages (main branch only)
    - Update API documentation
    - Sync with external documentation sites
```

### Integration Testing (`integration.yml`)
```yaml
# Comprehensive integration testing
name: Integration Tests
triggers:
  - push: [main]
  - pull_request: [main]
  - schedule: "0 4 * * *"  # Nightly at 4 AM

jobs:
  database-integration:
    - Neo4j + SQLite coordination testing
    - Transaction integrity validation
    - Performance under load
    - Backup and recovery testing
  
  service-integration:
    - Multi-service workflow testing
    - LLM API integration testing
    - Cross-modal analysis workflows
    - Theory-aware processing validation
  
  ui-integration:
    - Streamlit UI functionality testing
    - End-to-end user workflows
    - Export and visualization testing
    - Performance and responsiveness
```

### Production Deployment (`production-deploy.yml`)
```yaml
# Automated production deployment
name: Production Deploy
triggers:
  - push: [main]
  - workflow_dispatch  # Manual trigger

jobs:
  pre-deployment:
    - Full test suite execution
    - Security vulnerability scanning
    - Performance regression testing
    - Documentation validation
  
  deployment:
    - Docker image building and scanning
    - Kubernetes manifest validation
    - Rolling deployment with health checks
    - Post-deployment validation
  
  post-deployment:
    - Smoke testing in production
    - Performance monitoring setup
    - Alert configuration
    - Rollback preparation
```

## Quality Gates

### Code Quality Requirements
```yaml
# All PRs must pass these gates
quality_gates:
  code_formatting:
    - black: 100% compliance
    - isort: Import sorting compliance
    - flake8: No linting errors
  
  type_checking:
    - mypy: No type errors
    - coverage: >90% for new code
  
  security:
    - bandit: No high/medium security issues
    - safety: No known vulnerabilities
    - secrets: No hardcoded secrets
  
  testing:
    - unit_tests: All passing
    - integration_tests: All passing (for main branch)
    - contract_validation: All tool contracts valid
```

### Documentation Quality
```yaml
# Documentation requirements
docs_quality:
  structure:
    - All CLAUDE.md files present
    - Architecture documentation complete
    - Planning documents synchronized
  
  content:
    - No broken internal links
    - All code examples functional
    - Architecture diagrams up-to-date
  
  standards:
    - Markdown linting compliance
    - Consistent formatting
    - Proper cross-references
```

## Pull Request Workflow

### PR Template Structure
```markdown
## Description
Brief description of changes and motivation.

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that causes existing functionality to change)
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Refactoring (no functional changes)

## Testing
- [ ] Unit tests pass locally
- [ ] Integration tests pass (if applicable)
- [ ] Manual testing completed
- [ ] Contract validation passes (if tool changes)

## Documentation
- [ ] Code comments updated
- [ ] Documentation updated (if needed)
- [ ] CLAUDE.md files updated (if structure changes)
- [ ] Architecture docs updated (if applicable)

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review of code completed
- [ ] Changes generate no new warnings
- [ ] Added tests that prove the fix is effective or feature works
- [ ] New and existing unit tests pass locally
- [ ] Any dependent changes have been merged and published
```

### Review Process
```yaml
# Automated review requirements
review_requirements:
  code_owners:
    - Architecture changes: @architecture-team
    - Core system: @core-team
    - Documentation: @docs-team
    - Security: @security-team
  
  approvals:
    - Minimum 1 approval for documentation
    - Minimum 2 approvals for core system changes
    - Security review for authentication/authorization changes
    - Architecture review for major structural changes
  
  checks:
    - All CI checks must pass
    - No merge conflicts
    - Branch up-to-date with main
    - PR description complete
```

## Security and Compliance

### Security Scanning
```yaml
# Multi-layer security approach
security_scanning:
  code_analysis:
    - bandit: Python security issues
    - safety: Known vulnerability database
    - semgrep: Custom security rules
  
  dependency_scanning:
    - pip-audit: Python package vulnerabilities
    - github_advisory: GitHub security advisories
    - snyk: Commercial vulnerability scanning
  
  secrets_detection:
    - gitguardian: Secret scanning
    - trufflehog: Historical secret detection
    - custom_patterns: API key patterns
  
  container_scanning:
    - trivy: Container vulnerability scanning
    - docker_bench: Container security benchmarks
    - cis_benchmarks: Security configuration validation
```

### Compliance Automation
```yaml
# Automated compliance checking
compliance_checks:
  license_compliance:
    - dependency_license_scanning
    - incompatible_license_detection
    - license_attribution_validation
  
  data_protection:
    - pii_detection_in_code
    - gdpr_compliance_checking
    - data_retention_policy_validation
  
  audit_requirements:
    - change_logging
    - deployment_tracking
    - access_control_validation
```

## Performance and Monitoring

### Performance Testing
```yaml
# Continuous performance monitoring
performance_testing:
  benchmarks:
    - Document processing speed
    - Entity extraction performance
    - Graph query response times
    - Memory usage patterns
  
  regression_detection:
    - Performance comparison with baseline
    - Memory leak detection
    - Resource usage monitoring
    - API response time validation
  
  load_testing:
    - Multi-document processing
    - Concurrent user simulation
    - Database stress testing
    - API rate limit validation
```

### Monitoring Setup
```yaml
# Automated monitoring configuration
monitoring_deployment:
  metrics:
    - Prometheus metrics collection
    - Grafana dashboard deployment
    - Alert rule configuration
    - SLA monitoring setup
  
  logging:
    - Centralized log aggregation
    - Error tracking and alerting
    - Performance log analysis
    - Audit trail maintenance
  
  health_checks:
    - Service availability monitoring
    - Database connectivity checks
    - External API status monitoring
    - Resource utilization tracking
```

## Environment Management

### Multi-Environment Strategy
```yaml
# Environment-specific deployments
environments:
  development:
    trigger: feature/* branches
    config: development settings
    testing: unit + basic integration
    approval: none required
  
  staging:
    trigger: develop branch
    config: production-like settings
    testing: full integration + performance
    approval: team lead approval
  
  production:
    trigger: main branch
    config: production settings
    testing: smoke tests only
    approval: senior team approval + security review
```

### Configuration Management
```yaml
# Environment-specific configurations
config_management:
  secrets:
    - development: test API keys
    - staging: limited production keys
    - production: full production secrets
  
  resources:
    - development: minimal resources
    - staging: production-equivalent resources
    - production: optimized production resources
  
  features:
    - development: all features enabled
    - staging: production feature set
    - production: stable features only
```

## Troubleshooting Workflows

### Common CI/CD Issues

#### **Test Failures**
```bash
# Debug test failures
gh run list --workflow=ci-tests.yml
gh run view <run-id> --log

# Local reproduction
act -W .github/workflows/ci-tests.yml
```

#### **Deployment Issues**
```bash
# Check deployment status
gh run list --workflow=production-deploy.yml
kubectl get pods -n kgas-production

# Rollback if needed
gh workflow run production-deploy.yml -f rollback=true
```

#### **Documentation Build Failures**
```bash
# Check documentation issues
gh run view <docs-run-id> --log
make docs-build-local
```

### Workflow Debugging
```bash
# Common debugging commands
gh workflow list
gh run list --limit 10
gh run view <run-id>
gh run rerun <run-id>

# Local workflow testing
act --list
act -n  # dry run
act -j test  # run specific job
```

## Best Practices

### Workflow Development
1. **Test Locally**: Use `act` to test workflows locally before pushing
2. **Incremental Changes**: Make small, testable changes to workflows
3. **Resource Efficiency**: Optimize workflow resource usage and runtime
4. **Error Handling**: Include proper error handling and cleanup
5. **Documentation**: Document workflow purpose and maintenance procedures

### Security Best Practices
1. **Least Privilege**: Use minimal necessary permissions
2. **Secret Management**: Use GitHub secrets, never hardcode sensitive data
3. **Dependency Management**: Pin action versions, regularly update dependencies
4. **Audit Trail**: Maintain comprehensive logging and monitoring
5. **Access Control**: Restrict workflow modification permissions

### Performance Optimization
1. **Parallel Execution**: Run independent jobs in parallel
2. **Caching**: Cache dependencies and build artifacts
3. **Conditional Execution**: Skip unnecessary jobs based on changes
4. **Resource Limits**: Set appropriate resource limits and timeouts
5. **Monitoring**: Track workflow performance and optimize bottlenecks

The GitHub Actions configuration provides comprehensive automation for code quality, testing, deployment, and operational excellence while maintaining security and compliance standards.