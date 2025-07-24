#!/bin/bash
# Run Phase RELIABILITY validation using gemini-review-tool

echo "Creating repomix bundle for Phase RELIABILITY components..."

# Create bundle from project root
cd ..
npx repomix --include "src/core/distributed_transaction_manager.py,src/core/entity_id_manager.py,src/core/provenance_manager.py,src/core/async_rate_limiter.py,src/core/async_error_handler.py,src/core/connection_pool_manager.py,src/core/thread_safe_service_manager.py,src/core/error_taxonomy.py,src/core/health_monitor.py" --output gemini-review-tool/phase-reliability-bundle.xml .

# Go back to gemini-review-tool
cd gemini-review-tool

# Check bundle size
echo "Bundle created:"
ls -lh phase-reliability-bundle.xml

# Run validation using the bundle
echo "Running Gemini validation..."
python gemini_review.py . --config validation-20250723-152600.yaml --no-cache