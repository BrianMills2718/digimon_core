# Phase RELIABILITY Validations

This directory contains focused validations for the KGAS Phase RELIABILITY implementation.

## Overview

Each validation is designed to verify a specific reliability component with minimal context, following the best practices for Gemini AI validation.

## Components to Validate

1. **Distributed Transactions** - Two-phase commit across Neo4j and SQLite
2. **Entity ID Mapping** - Bidirectional ID consistency  
3. **Provenance Tracking** - Citation fabrication prevention
4. **Async Patterns** - Non-blocking operations
5. **Connection Pooling** - Resource management
6. **Thread Safety** - Race condition prevention
7. **Error Handling** - Unified error taxonomy
8. **Health Monitoring** - System health checks
9. **Performance Baselines** - SLA monitoring

## Validation Process

1. Generate focused bundle for specific component:
```bash
npx repomix --include "src/core/[component].py" --output [component]-bundle.xml ..
```

2. Run validation with focused config:
```bash
python ../validate_reliability.py --component [component_name]
```

3. Review results in `outputs/[timestamp]/`

## File Structure

```
reliability-validations/
├── configs/           # YAML validation configs
├── bundles/          # Generated repomix bundles
├── scripts/          # Validation scripts
└── results/          # Validation results
```

## Best Practices

- One component per validation
- Include only directly relevant files
- Use specific line number references
- Request concrete evidence
- Keep bundles under 50KB