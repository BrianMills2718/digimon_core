#!/usr/bin/env bash
set -euo pipefail

# Fail on any broken link; ignore external rate-limit errors.
lychee --no-progress --max-concurrency 32 -a docs/**/*.md -e 'https://github.com' || {
  echo "❌ Broken links found in documentation. Fix the URLs above.";
  exit 1;
}

echo "✅ No broken documentation links detected." 