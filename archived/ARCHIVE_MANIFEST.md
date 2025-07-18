# Archive Manifest

This directory contains archived code and files that have been moved out of the main codebase during the Phase 2 reorganization.

## Archive Structure

```
archived/
├── ARCHIVE_MANIFEST.md              # This file
├── redundant_code/                  # Duplicate or redundant implementations
│   ├── compatability_code/         # Duplicate compatibility code
│   └── archived_theory_implementations/ # Old theory implementations
├── duplicate_structures/            # Duplicate directory structures
│   └── contracts/                   # Nested contracts directory
├── old_experiments/                 # Experimental scripts and files
│   ├── create-combined-architecture.py
│   ├── fix_adapters.py
│   ├── fix_validation_methods.py
│   ├── gemini_review.py
│   └── gemini-review.md
└── temporary_files/                 # Temporary files from development
    ├── kgas_phase2_validation_bundle.json
    ├── phase2_validation_report.py
    ├── simple_validation.py
    ├── test_results_debug.xml
    └── various test_*.py files
```

## Archive Date
**Archived on:** 2025-07-18

## Reason for Archiving
These files were moved during the Phase 2 codebase reorganization to:
1. Eliminate duplicate code structures
2. Remove redundant compatibility layers
3. Clean up temporary development files
4. Consolidate experimental scripts
5. Improve overall codebase organization

## Important Notes

### What's Archived
- **compatability_code/**: Duplicate compatibility implementation that was superseded by the main contracts/ directory
- **contracts/contracts/**: Nested directory structure that was flattened
- **archived_theory_implementations/**: Old theory implementations that were integrated into the main codebase
- **Individual test files**: Test files that were moved to the organized tests/ directory structure
- **Experimental scripts**: Various one-off scripts used during development

### What's NOT Archived
- Active code in src/
- Organized tests in tests/
- Current configuration in config/
- Documentation in docs/
- Working tools and examples

### Recovery Instructions
If any of these files are needed:
1. The files are preserved in this archive directory
2. They can be restored to their original locations if needed
3. Most functionality has been replaced by better implementations in the main codebase
4. Check the main codebase first before restoring archived files

### Safe to Delete
The contents of this archive can be safely deleted after confirming that:
1. All required functionality is available in the main codebase
2. All tests pass without the archived files
3. The system operates correctly without the archived components
4. A backup of the entire repository exists

## Related Documentation
- docs/REORGANIZATION_AUDIT_REPORT.md - Details of the reorganization process
- docs/FINAL_ORGANIZATION_SUMMARY.md - Summary of the final organization
- CLAUDE.md - Implementation requirements and standards