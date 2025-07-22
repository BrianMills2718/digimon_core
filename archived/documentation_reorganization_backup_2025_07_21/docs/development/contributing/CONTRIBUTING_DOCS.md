---
status: living
---

# Documentation Contribution Guide

This guide describes the required style, formatting, and status badge rules for all documentation in this repository.

## Style Guide
- **Line Length**: Wrap all lines at 88 characters maximum.
- **Front-Matter**: Every Markdown file must begin with YAML front-matter:
  ```yaml
  ---
  status: draft  # or 'living', 'stable', etc.
  ---
  ```
- **Status Badge**: Use the `status` field to indicate the document's maturity:
  - `draft`: Early work, not yet reviewed
  - `living`: Maintained and evolving
  - `stable`: Feature-complete, only minor updates expected
  - `archived`: No longer updated, for reference only
- **Badge Placement**: The YAML front-matter must be the first content in the file.
- **No Duplicate Status**: Remove any old "**Doc status**: ..." lines from the body.
- **Section Headers**: Use `##` for major sections, `###` for subsections.
- **Code Blocks**: Use triple backticks for code and CLI examples.
- **References**: Cross-link to other docs using relative paths.

## Example
```markdown
---
status: living
---

# Example Documentation Title

## Overview
All documentation must start with YAML front-matter as shown above.
```

## Badge Policy
- All new documentation must include a status badge.
- Update the badge as the document matures.
- PRs that add or update docs without a badge will be rejected by CI.

## Observability Policy
- Build, don’t buy: use open-source Grafana/Tempo stack rather than New Relic/Datadog.

## Review Process
- Documentation PRs are reviewed for style, badge, and cross-linking.
- Use `make docs-lint` to check badge compliance before submitting.

---
For questions, see `docs/CONTRIBUTING.md` or ask in the project Slack. 