#!/bin/bash
# Run a single reliability validation

COMPONENT=$1
if [ -z "$COMPONENT" ]; then
    echo "Usage: $0 <component>"
    echo "Components: distributed-tx, entity-id, provenance, async, connection-pool, thread-safety, error-handling, health"
    exit 1
fi

case $COMPONENT in
    "distributed-tx")
        CONFIG="01-distributed-transactions.yaml"
        FILES="src/core/distributed_transaction_manager.py"
        NAME="Distributed Transactions"
        ;;
    "entity-id")
        CONFIG="02-entity-id-mapping.yaml"
        FILES="src/core/entity_id_manager.py"
        NAME="Entity ID Mapping"
        ;;
    "provenance")
        CONFIG="03-provenance-tracking.yaml"
        FILES="src/core/provenance_manager.py"
        NAME="Provenance Tracking"
        ;;
    "async")
        CONFIG="04-async-patterns.yaml"
        FILES="src/core/async_rate_limiter.py,src/core/async_error_handler.py"
        NAME="Async Patterns"
        ;;
    "connection-pool")
        CONFIG="05-connection-pooling.yaml"
        FILES="src/core/connection_pool_manager.py"
        NAME="Connection Pooling"
        ;;
    "thread-safety")
        CONFIG="06-thread-safety.yaml"
        FILES="src/core/thread_safe_service_manager.py"
        NAME="Thread Safety"
        ;;
    "error-handling")
        CONFIG="07-error-handling.yaml"
        FILES="src/core/error_taxonomy.py"
        NAME="Error Handling"
        ;;
    "health")
        CONFIG="08-health-monitoring.yaml"
        FILES="src/core/health_monitor.py"
        NAME="Health Monitoring"
        ;;
    *)
        echo "Unknown component: $COMPONENT"
        exit 1
        ;;
esac

echo "========================================"
echo "Validating: $NAME"
echo "========================================"

# Create bundle
echo "Creating focused bundle..."
npx repomix --include "$FILES" --output "reliability-$COMPONENT.xml" ..

# Check size
SIZE=$(ls -lh "reliability-$COMPONENT.xml" | awk '{print $5}')
echo "Bundle size: $SIZE"

# Run validation
echo "Running validation..."
python gemini_review.py .. --config "reliability-validations/configs/$CONFIG" --include "$FILES"