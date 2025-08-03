# Bi-Store Consistency Implementation Plan

**Status**: TENTATIVE PROPOSAL  
**Created**: 2025-01-29  
**Related**: [ADR-009 Bi-Store Database Strategy](../../architecture/adrs/ADR-009-Bi-Store-Database-Strategy.md)  
**Priority**: HIGH - Data integrity critical for research credibility

## Problem Statement

KGAS uses a bi-store architecture (Neo4j + SQLite) that currently lacks:
- Atomic transaction support across databases
- Entity ID synchronization mechanisms
- Rollback procedures for partial failures
- Consistency validation between stores

This creates risks of:
- Data corruption during cross-store operations
- Entity ID mismatches
- Orphaned records
- Inconsistent query results

## Current Architecture

```
┌─────────────────────────────┐
│     Application Layer       │
│  (No transaction coordinator)│
└──────────┬──────────────────┘
           │
    ┌──────┴──────┐
    │             │
    ▼             ▼
┌────────┐    ┌────────┐
│ Neo4j  │    │ SQLite │
│(Graph) │    │(Meta)  │
└────────┘    └────────┘
```

## Proposed Solution

### Two-Phase Commit Pattern

```python
class BiStoreTransactionCoordinator:
    def __init__(self, neo4j_driver, sqlite_conn):
        self.neo4j = neo4j_driver
        self.sqlite = sqlite_conn
        self.transaction_log = TransactionLog()
    
    def execute_transaction(self, operations):
        tx_id = self.transaction_log.begin()
        
        try:
            # Phase 1: Prepare
            neo4j_tx = self.neo4j.begin_transaction()
            sqlite_tx = self.sqlite.begin()
            
            # Execute operations
            for op in operations:
                if op.target == 'neo4j':
                    neo4j_tx.run(op.query, op.params)
                else:
                    sqlite_tx.execute(op.query, op.params)
            
            # Phase 2: Commit
            neo4j_tx.commit()
            sqlite_tx.commit()
            
            self.transaction_log.commit(tx_id)
            
        except Exception as e:
            # Rollback both
            neo4j_tx.rollback()
            sqlite_tx.rollback()
            self.transaction_log.rollback(tx_id)
            raise
```

### Entity ID Synchronization

```python
class EntityIDManager:
    """Ensures consistent entity IDs across stores"""
    
    def __init__(self, id_generator):
        self.id_generator = id_generator
        self.id_cache = {}
        
    def create_entity(self, entity_data):
        # Generate ID once
        entity_id = self.id_generator.next_id()
        
        # Create in both stores with same ID
        neo4j_result = self.create_in_neo4j(entity_id, entity_data)
        sqlite_result = self.create_in_sqlite(entity_id, entity_data)
        
        # Validate consistency
        if not self.validate_entity(entity_id):
            raise ConsistencyError(f"Entity {entity_id} inconsistent")
            
        return entity_id
```

### Consistency Validation

```python
class ConsistencyValidator:
    """Validates data consistency between stores"""
    
    def validate_entity(self, entity_id):
        neo4j_data = self.fetch_from_neo4j(entity_id)
        sqlite_data = self.fetch_from_sqlite(entity_id)
        
        return self.compare_entities(neo4j_data, sqlite_data)
    
    def reconcile_stores(self):
        """Full store reconciliation"""
        neo4j_ids = self.get_all_neo4j_ids()
        sqlite_ids = self.get_all_sqlite_ids()
        
        # Find mismatches
        only_in_neo4j = neo4j_ids - sqlite_ids
        only_in_sqlite = sqlite_ids - neo4j_ids
        
        # Reconcile based on policy
        return self.apply_reconciliation_policy(
            only_in_neo4j, only_in_sqlite
        )
```

## Implementation Phases

### Phase 1: Transaction Coordinator (Days 1-3)

**Tasks**:
1. Implement BiStoreTransactionCoordinator class
2. Add transaction logging for recovery
3. Create rollback procedures
4. Add transaction monitoring

**Deliverables**:
- Working two-phase commit implementation
- Transaction log with recovery capability
- Rollback tested for all failure modes
- Monitoring dashboard for transactions

### Phase 2: ID Synchronization (Days 4-5)

**Tasks**:
1. Implement centralized ID generator
2. Modify all entity creation to use coordinator
3. Add ID validation checks
4. Create ID reconciliation tools

**Deliverables**:
- Consistent ID generation across stores
- Validation of ID consistency
- Tools to fix ID mismatches
- ID generation performance metrics

### Phase 3: Consistency Validation (Days 6-7)

**Tasks**:
1. Implement ConsistencyValidator
2. Add periodic validation jobs
3. Create reconciliation procedures
4. Build consistency monitoring

**Deliverables**:
- Automated consistency checks
- Reconciliation procedures documented
- Monitoring alerts for inconsistencies
- Manual reconciliation tools

### Phase 4: Integration & Testing (Days 8-10)

**Tasks**:
1. Integrate with existing services
2. Update all cross-store operations
3. Comprehensive testing
4. Performance optimization

**Deliverables**:
- All services using transaction coordinator
- Test suite for consistency scenarios
- Performance benchmarks
- Operational documentation

## Testing Strategy

### Unit Tests
```python
def test_transaction_rollback():
    """Test rollback on Neo4j failure"""
    coordinator = BiStoreTransactionCoordinator()
    
    operations = [
        Operation('sqlite', 'INSERT INTO...'),
        Operation('neo4j', 'CREATE (n:Entity)'),
        Operation('neo4j', 'INVALID QUERY')  # Will fail
    ]
    
    with pytest.raises(TransactionError):
        coordinator.execute_transaction(operations)
    
    # Verify nothing committed
    assert sqlite_count() == 0
    assert neo4j_count() == 0
```

### Integration Tests
- Concurrent transaction handling
- Network failure scenarios
- Partial commit recovery
- ID conflict resolution

### Stress Tests
- High transaction volume
- Large entity creation
- Concurrent modifications
- Recovery performance

## Monitoring & Metrics

### Key Metrics
- Transaction success rate
- Average transaction time
- Rollback frequency
- ID conflicts detected
- Consistency check results

### Alerts
- Transaction failure rate > 1%
- Consistency check failures
- ID generation conflicts
- Recovery time > 30 seconds

## Rollback & Recovery Procedures

### Automatic Recovery
1. Transaction log replay
2. Consistency validation
3. Automatic reconciliation
4. Alert on manual intervention needed

### Manual Recovery
1. Identify inconsistent entities
2. Determine authoritative source
3. Apply reconciliation
4. Validate consistency
5. Document resolution

## Performance Considerations

### Optimization Strategies
- Batch operations when possible
- Async consistency checks
- Caching for read operations
- Connection pooling

### Expected Impact
- ~10-20ms overhead per transaction
- Negligible impact on reads
- Improved reliability worth the cost
- Can optimize critical paths later

## Success Criteria

1. **Zero data loss** during failures
2. **100% ID consistency** across stores
3. **<20ms transaction overhead**
4. **Automatic recovery** for common failures
5. **Clear audit trail** for all operations

## Risks & Mitigation

### Technical Risks
- **Complexity**: Start simple, add features incrementally
- **Performance**: Monitor impact, optimize hot paths
- **Deadlocks**: Implement timeout and retry logic

### Operational Risks
- **Training**: Document procedures thoroughly
- **Monitoring**: Comprehensive alerting
- **Recovery**: Practice failure scenarios

## Next Steps

1. Review and approve design
2. Set up development environment
3. Implement Phase 1 (coordinator)
4. Daily progress reviews
5. Incremental deployment

This plan ensures KGAS maintains data integrity across its bi-store architecture, providing the foundation for reliable cross-modal analysis.