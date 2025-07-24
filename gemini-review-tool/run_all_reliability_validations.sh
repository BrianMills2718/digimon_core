#!/bin/bash
# Create bundles and run all reliability validations

echo "Phase RELIABILITY Complete Validation Suite"
echo "=========================================="

# Create all bundles first
echo -e "\n📦 Creating validation bundles..."

echo -e "\n1. Distributed Transactions"
npx repomix --include "src/core/distributed_transaction_manager.py" --output reliability-distributed-tx.xml .. --quiet

echo -e "\n2. Entity ID Mapping"
npx repomix --include "src/core/entity_id_manager.py" --output reliability-entity-id.xml .. --quiet

echo -e "\n3. Provenance Tracking"
npx repomix --include "src/core/provenance_manager.py" --output reliability-provenance.xml .. --quiet

echo -e "\n4. Async Patterns"
npx repomix --include "src/core/async_rate_limiter.py,src/core/async_error_handler.py" --output reliability-async.xml .. --quiet

echo -e "\n5. Connection Pooling"
npx repomix --include "src/core/connection_pool_manager.py" --output reliability-connection-pool.xml .. --quiet

echo -e "\n6. Thread Safety"
npx repomix --include "src/core/thread_safe_service_manager.py" --output reliability-thread-safety.xml .. --quiet

echo -e "\n7. Error Handling"
npx repomix --include "src/core/error_taxonomy.py" --output reliability-error-handling.xml .. --quiet

echo -e "\n8. Health Monitoring"
npx repomix --include "src/core/health_monitor.py" --output reliability-health.xml .. --quiet

echo -e "\n✅ All bundles created!"
echo -e "\n📊 Bundle sizes:"
ls -lh reliability-*.xml | awk '{print $9 ": " $5}'

echo -e "\n🔍 Running validations..."
python validate_all_reliability.py