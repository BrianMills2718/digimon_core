# Reliability Tests

This directory contains comprehensive reliability tests for the KGAS system, focusing on fixing critical architectural issues identified in Phase RELIABILITY.

## Test Organization

### Working Tests with Real Databases

1. **`test_distributed_transactions_real.py`** ✅
   - Tests two-phase commit with real Neo4j and SQLite
   - Verifies atomic commits and rollbacks
   - Tests concurrent transaction isolation
   - Tests timeout handling

2. **`test_entity_id_consistency.py`** ✅
   - Tests entity ID generation and uniqueness
   - Tests ID mapping persistence
   - Tests concurrent ID creation
   - Tests orphaned ID detection

### Infrastructure Requirements

- **Neo4j**: Running in Docker container
  ```bash
  docker run --name test-neo4j -d -p 7474:7474 -p 7687:7687 \
    -e NEO4J_AUTH=neo4j/testpassword neo4j:5-community
  ```

- **SQLite**: Created as temporary databases during tests

## Running Tests

```bash
# Run all reliability tests
pytest tests/reliability/ -v

# Run specific test categories
pytest tests/reliability/test_distributed_transactions_real.py -v
pytest tests/reliability/test_entity_id_consistency.py -v

# Run with coverage
pytest tests/reliability/ --cov=src/core --cov-report=html
```

## Implementation Status

### ✅ Completed
- Distributed transaction manager with 2PC protocol
- Entity ID manager with consistent mapping
- Real database integration tests

### 🚧 In Progress
- Citation fabrication prevention
- Async/await pattern fixes
- Connection pool management

### 📋 Pending
- Thread safety fixes
- Unified error handling
- Health monitoring
- Performance baselines

## Key Components

### DistributedTransactionManager
- Location: `src/core/distributed_transaction_manager.py`
- Implements two-phase commit across Neo4j and SQLite
- Handles transaction state tracking and recovery
- Supports concurrent transactions with isolation

### EntityIDManager
- Location: `src/core/entity_id_manager.py`
- Generates unique entity IDs with type prefixes
- Maintains bidirectional ID mappings
- Detects and cleans up orphaned IDs

## Notes

- All tests use real database connections (no mocks for core functionality)
- Tests are designed to be idempotent and can be run repeatedly
- Each test cleans up after itself to avoid state pollution
- Docker must be running with Neo4j container for integration tests