# GitHub Workflows - CLAUDE.md

## Overview
The `.github/workflows/` directory contains the individual GitHub Actions workflow files that automate testing, deployment, and quality assurance for KGAS. Each workflow serves a specific purpose in the CI/CD pipeline and development process.

## Workflow Files

### Core Workflows
- **`ci-tests.yml`**: Primary continuous integration testing pipeline
- **`integration.yml`**: Integration testing with real services and databases
- **`production-deploy.yml`**: Production deployment automation with safety checks
- **`docs-ci.yml`**: Documentation building and deployment
- **`docs_check.yml`**: Documentation validation and consistency checking

## Workflow Architecture

### Pipeline Flow
```yaml
# Typical workflow progression
Code Push/PR → Quality Gates → Unit Tests → Integration Tests → Documentation → Deployment
     ↓              ↓             ↓              ↓               ↓            ↓
   Triggers    → Lint/Format → Fast Tests → Real Services → Docs Build → Production
   Security    → Type Check  → Coverage  → Performance   → Validation → Monitoring
   Validation  → Secrets     → Contracts → UI Testing    → Links      → Health
```

### Workflow Dependencies
```yaml
# Workflow execution order and dependencies
workflows:
  ci-tests:
    triggers: [push, pull_request]
    depends_on: []
    blocks: [production-deploy]
  
  integration:
    triggers: [push to main, nightly]
    depends_on: [ci-tests]
    blocks: [production-deploy]
  
  docs-ci:
    triggers: [push, pull_request on docs]
    depends_on: []
    blocks: []
  
  production-deploy:
    triggers: [push to main]
    depends_on: [ci-tests, integration, docs-ci]
    blocks: []
```

## Individual Workflow Details

### CI Tests Workflow (`ci-tests.yml`)

#### Purpose
Primary continuous integration pipeline providing fast feedback on code quality and basic functionality.

#### Key Jobs
```yaml
jobs:
  quality-checks:
    # Code formatting and linting
    - black --check src/ tests/
    - isort --check-only src/ tests/
    - flake8 src/ tests/
    - mypy src/
    
  security-scan:
    # Security vulnerability detection
    - bandit -r src/
    - safety check
    - pip-audit
    - secrets detection
    
  unit-tests:
    # Fast unit testing with mocking
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]
    - pytest tests/unit/ --cov=src --cov-report=xml
    - codecov upload
    
  contract-validation:
    # Tool contract compliance
    - python contracts/validation/theory_validator.py
    - validate all tool contracts
    - check contract coverage
```

#### Performance Optimizations
- **Parallel execution**: Quality checks and tests run in parallel
- **Caching**: pip dependencies, mypy cache, pytest cache
- **Conditional execution**: Only run on relevant file changes
- **Fast failure**: Fail fast on critical issues

### Integration Tests Workflow (`integration.yml`)

#### Purpose
Comprehensive integration testing with real services, databases, and external dependencies.

#### Key Jobs
```yaml
jobs:
  setup-services:
    # Start real service dependencies
    services:
      neo4j:
        image: neo4j:5.13
        env:
          NEO4J_AUTH: neo4j/testpassword
        ports: [7687:7687, 7474:7474]
    
  database-integration:
    # Real database testing
    - Neo4j + SQLite coordination
    - Transaction integrity testing
    - Performance benchmarking
    - Backup/restore validation
    
  service-integration:
    # Multi-service workflow testing
    - Pipeline orchestration testing
    - Cross-modal analysis workflows
    - LLM API integration (with test keys)
    - Error handling and recovery
    
  ui-integration:
    # Streamlit UI testing
    - UI component functionality
    - End-to-end user workflows
    - Export and visualization
    - Performance validation
```

#### Resource Management
- **Service containers**: Real Neo4j and other services
- **Timeouts**: Extended timeouts for complex workflows
- **Resource limits**: Appropriate CPU and memory allocation
- **Cleanup**: Proper service shutdown and resource cleanup

### Production Deploy Workflow (`production-deploy.yml`)

#### Purpose
Automated production deployment with comprehensive safety checks and rollback capabilities.

#### Key Jobs
```yaml
jobs:
  pre-deployment-validation:
    # Comprehensive pre-deployment checks
    - Full test suite execution
    - Security vulnerability scanning
    - Performance regression testing
    - Configuration validation
    - Infrastructure readiness check
    
  build-and-scan:
    # Container building and security scanning
    - Docker image building
    - Container vulnerability scanning
    - Image signing and attestation
    - Registry upload
    
  deploy-to-production:
    # Kubernetes deployment
    - Manifest validation
    - Rolling deployment
    - Health check validation
    - Traffic routing
    - Monitoring setup
    
  post-deployment-validation:
    # Production validation
    - Smoke testing
    - Performance monitoring
    - Error rate validation
    - Rollback preparation
```

#### Safety Mechanisms
- **Multi-stage approval**: Manual approval gates for production
- **Canary deployment**: Gradual traffic shifting
- **Health monitoring**: Continuous health validation
- **Automatic rollback**: Rollback on health check failures

### Documentation Workflows (`docs-ci.yml`, `docs_check.yml`)

#### Purpose
Automated documentation building, validation, and deployment to ensure documentation quality and consistency.

#### Key Jobs
```yaml
# docs-ci.yml - Documentation building and deployment
jobs:
  build-docs:
    - MkDocs site building
    - API documentation generation
    - Link validation
    - Asset optimization
    
  deploy-docs:
    - GitHub Pages deployment
    - CDN cache invalidation
    - Search index update
    - Analytics setup

# docs_check.yml - Documentation validation
jobs:
  validate-structure:
    - CLAUDE.md file presence
    - Documentation structure validation
    - Cross-reference validation
    - Consistency checking
    
  validate-content:
    - Markdown linting
    - Link checking (internal and external)
    - Code example validation
    - Image and asset validation
```

#### Documentation Quality
- **Automated validation**: Structure and content validation
- **Link checking**: Comprehensive link validation
- **Consistency**: Cross-document consistency checking
- **Performance**: Optimized documentation site performance

## Workflow Configuration Patterns

### Environment Variables
```yaml
# Common environment variables across workflows
env:
  PYTHON_VERSION: "3.9"
  NODE_VERSION: "18"
  DOCKER_BUILDKIT: "1"
  PYTEST_TIMEOUT: "300"
  
  # Test configuration
  KGAS_TEST_MODE: "true"
  NEO4J_URI: "bolt://localhost:7687"
  NEO4J_USERNAME: "neo4j"
  NEO4J_PASSWORD: "testpassword"
  
  # Security
  PYTHONHASHSEED: "random"
  PYTHONDONTWRITEBYTECODE: "1"
```

### Caching Strategy
```yaml
# Comprehensive caching for performance
caching:
  pip_dependencies:
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}
    paths: ~/.cache/pip
    
  node_modules:
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
    paths: ~/.npm
    
  docker_layers:
    key: ${{ runner.os }}-docker-${{ hashFiles('Dockerfile') }}
    paths: /tmp/.buildx-cache
    
  mypy_cache:
    key: ${{ runner.os }}-mypy-${{ hashFiles('**/*.py') }}
    paths: .mypy_cache
```

### Conditional Execution
```yaml
# Smart conditional execution to optimize CI runtime
conditions:
  python_changes:
    if: contains(github.event.head_commit.modified, '.py') || 
        contains(github.event.head_commit.added, '.py')
    
  docs_changes:
    if: contains(github.event.head_commit.modified, '.md') ||
        startsWith(github.event.head_commit.modified, 'docs/')
    
  config_changes:
    if: contains(github.event.head_commit.modified, '.yml') ||
        contains(github.event.head_commit.modified, '.yaml') ||
        contains(github.event.head_commit.modified, '.toml')
```

## Secrets and Security

### Required Secrets
```yaml
# GitHub repository secrets configuration
secrets:
  api_keys:
    OPENAI_API_KEY: "OpenAI API key for LLM testing"
    ANTHROPIC_API_KEY: "Anthropic API key for Claude testing"
    GOOGLE_API_KEY: "Google API key for Gemini testing"
    
  deployment:
    KUBECONFIG: "Kubernetes configuration for deployment"
    DOCKER_REGISTRY_TOKEN: "Container registry access token"
    
  monitoring:
    SENTRY_DSN: "Error tracking and monitoring"
    DATADOG_API_KEY: "Performance monitoring"
    
  external:
    CODECOV_TOKEN: "Code coverage reporting"
    SONAR_TOKEN: "Code quality analysis"
```

### Security Best Practices
```yaml
# Security configuration in workflows
security:
  permissions:
    contents: read
    security-events: write
    id-token: write  # For OIDC
    
  runner_security:
    runs-on: ubuntu-latest  # Use GitHub-hosted runners
    timeout-minutes: 60     # Prevent runaway jobs
    
  dependency_security:
    - Pin action versions to specific commits
    - Use official actions when possible
    - Regular security scanning of dependencies
    - Automated dependency updates
```

## Performance Monitoring

### Workflow Performance Metrics
```yaml
# Built-in performance monitoring
performance_tracking:
  job_timing:
    - Track individual job execution times
    - Monitor queue times and wait times
    - Identify performance bottlenecks
    - Optimize parallel execution
    
  resource_usage:
    - Monitor memory and CPU usage
    - Track storage and network usage
    - Optimize resource allocation
    - Cost monitoring and optimization
    
  success_rates:
    - Track workflow success/failure rates
    - Monitor flaky test identification
    - Error categorization and analysis
    - Continuous improvement tracking
```

### Optimization Strategies
```yaml
# Workflow optimization techniques
optimization:
  parallelization:
    - Run independent jobs in parallel
    - Use job matrices for multi-version testing
    - Optimize job dependencies
    - Minimize sequential bottlenecks
    
  caching:
    - Cache dependencies and build artifacts
    - Use incremental builds when possible
    - Share caches across related workflows
    - Monitor cache hit rates
    
  conditional_execution:
    - Skip unnecessary jobs based on changes
    - Use path-based triggers
    - Implement smart test selection
    - Avoid redundant work
```

## Troubleshooting and Debugging

### Common Issues

#### **Workflow Failures**
```bash
# Debug workflow failures
gh run list --workflow=ci-tests.yml --limit=10
gh run view <run-id> --log
gh run rerun <run-id>

# Local debugging with act
act -W .github/workflows/ci-tests.yml
act -j quality-checks  # Run specific job
act --list  # List available jobs
```

#### **Test Failures**
```bash
# Investigate test failures
gh run view <run-id> --log-failed
grep -A 10 -B 10 "FAILED" workflow.log

# Reproduce locally
python -m pytest tests/unit/ -v --tb=long
python -m pytest tests/integration/ -v -s
```

#### **Deployment Issues**
```bash
# Check deployment status
kubectl get pods -n kgas-production
kubectl describe deployment kgas-app -n kgas-production

# Review deployment logs
kubectl logs -f deployment/kgas-app -n kgas-production
gh run view <deploy-run-id> --log
```

### Debugging Techniques
```yaml
# Workflow debugging strategies
debugging:
  enhanced_logging:
    - Enable debug logging in workflows
    - Add strategic debug outputs
    - Use step outputs for data passing
    - Log environment and context information
    
  conditional_debugging:
    - Add debug steps that run on failure
    - Collect artifacts and logs
    - Create debug builds
    - Enable verbose modes
    
  local_reproduction:
    - Use act for local workflow testing
    - Set up matching local environments
    - Use same dependency versions
    - Replicate workflow conditions
```

## Maintenance and Updates

### Regular Maintenance Tasks
```yaml
# Workflow maintenance schedule
maintenance:
  weekly:
    - Review workflow performance metrics
    - Check for action version updates
    - Monitor success/failure rates
    - Update dependency versions
    
  monthly:
    - Security audit of actions and dependencies
    - Performance optimization review
    - Cost analysis and optimization
    - Documentation updates
    
  quarterly:
    - Major action version updates
    - Workflow architecture review
    - Security policy updates
    - Disaster recovery testing
```

### Update Procedures
```bash
# Update workflow dependencies
gh workflow run update-dependencies.yml
dependabot: auto-update GitHub Actions

# Test workflow changes
act -W .github/workflows/updated-workflow.yml
gh workflow run updated-workflow.yml --ref feature-branch

# Deploy workflow updates
git push origin main  # Workflows update automatically
```

## Best Practices

### Workflow Design
1. **Modularity**: Design workflows as modular, reusable components
2. **Fail Fast**: Implement early failure detection and fast feedback
3. **Resource Efficiency**: Optimize resource usage and execution time
4. **Error Handling**: Include comprehensive error handling and recovery
5. **Documentation**: Document workflow purpose, inputs, and outputs

### Security Best Practices
1. **Least Privilege**: Use minimal necessary permissions
2. **Secret Management**: Proper secret handling and rotation
3. **Dependency Security**: Pin versions and scan for vulnerabilities
4. **Audit Trail**: Maintain comprehensive logging and monitoring
5. **Access Control**: Restrict workflow modification permissions

### Performance Optimization
1. **Parallel Execution**: Maximize parallel job execution
2. **Intelligent Caching**: Use effective caching strategies
3. **Conditional Logic**: Skip unnecessary work with smart conditions
4. **Resource Management**: Optimize resource allocation and usage
5. **Monitoring**: Continuous performance monitoring and optimization

The GitHub workflows provide comprehensive automation for the entire development lifecycle while maintaining high standards for quality, security, and performance.