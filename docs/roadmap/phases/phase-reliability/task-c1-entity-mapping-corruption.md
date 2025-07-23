# Task C1: Entity ID Mapping Corruption Fix

**Priority**: CATASTROPHIC  
**Timeline**: 4-5 days  
**Status**: Pending  
**Assigned**: Development Team

## 🚨 **CATASTROPHIC ISSUE**

**File**: `src/tools/phase1/t31_entity_builder.py:147-151`  
**Problem**: Concurrent workflows create conflicting entity mappings in memory without database synchronization, causing silent data corruption where different entities get incorrectly merged.

## 📋 **Issue Analysis**

### **Current Problematic Implementation**
```python
# Line 147-151 in t31_entity_builder.py
entity_id_mapping[old_mention_id] = entity_id  # In-memory only, no DB sync

# Multiple workflows can create conflicting mappings:
# Workflow A: entity_id_mapping["Apple Inc"] = "entity_123"
# Workflow B: entity_id_mapping["Apple Inc"] = "entity_456" 
# Result: Same mention mapped to different entities = DATA CORRUPTION
```

### **Data Corruption Scenarios**
1. **Race Condition Corruption**: Two workflows process same entity mention simultaneously
2. **Memory State Loss**: Process restart loses all mapping state, creating duplicates
3. **Partial Failure Recovery**: Failed operations leave inconsistent mapping state
4. **Cross-Workflow Pollution**: One workflow's mappings affect other concurrent workflows

### **Impact Assessment**
- **Severity**: CATASTROPHIC - Silent data corruption
- **Research Impact**: Invalid PageRank calculations, incorrect research results
- **Detection Difficulty**: Corruption happens silently, discovered only during analysis
- **Recovery Complexity**: Corrupted data requires manual reconciliation

## 🎯 **Solution Architecture**

### **Distributed Entity Coordination System**
```python
# src/core/distributed_entity_coordinator.py - New file

import redis
import hashlib
import json
from contextlib import contextmanager
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class EntityMappingLock:
    mention_key: str
    lock_key: str
    expiry_time: datetime
    workflow_id: str

class EntityMappingConflictError(Exception):
    """Raised when entity mapping conflict is detected"""
    pass

class DistributedEntityCoordinator:
    """Coordinates entity mappings across concurrent workflows"""
    
    def __init__(self, neo4j_driver, redis_client=None):
        self.neo4j = neo4j_driver
        self.redis = redis_client or redis.Redis(host='localhost', port=6379, db=0)
        self.lock_timeout = 30  # seconds
        
    def acquire_entity_mapping_lock(self, mention_data: Dict[str, Any], workflow_id: str) -> EntityMappingLock:
        """Acquire distributed lock for entity mapping operations"""
        
        # Create stable key from mention characteristics
        mention_key = self._create_mention_key(mention_data)
        lock_key = f"entity_mapping_lock:{mention_key}"
        
        # Try to acquire lock with workflow ID
        lock_acquired = self.redis.set(
            lock_key, 
            json.dumps({
                "workflow_id": workflow_id,
                "acquired_at": datetime.now().isoformat(),
                "mention_data": mention_data
            }),
            nx=True,  # Only set if not exists
            ex=self.lock_timeout  # Expire after timeout
        )
        
        if not lock_acquired:
            # Check who owns the lock
            current_lock = self.redis.get(lock_key)
            if current_lock:
                lock_info = json.loads(current_lock.decode())
                raise EntityMappingConflictError(
                    f"Entity mapping for '{mention_data.get('surface_form')}' "
                    f"already locked by workflow {lock_info['workflow_id']}"
                )
            else:
                raise EntityMappingConflictError(
                    f"Failed to acquire lock for entity mapping: {mention_key}"
                )
        
        return EntityMappingLock(
            mention_key=mention_key,
            lock_key=lock_key,
            expiry_time=datetime.now() + timedelta(seconds=self.lock_timeout),
            workflow_id=workflow_id
        )
    
    def release_entity_mapping_lock(self, lock: EntityMappingLock) -> None:
        """Release entity mapping lock"""
        # Only release if we still own the lock
        lock_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        
        self.redis.eval(
            lock_script, 
            1, 
            lock.lock_key, 
            json.dumps({"workflow_id": lock.workflow_id})
        )
    
    @contextmanager
    def entity_mapping_transaction(self, mention_data: Dict[str, Any], workflow_id: str):
        """Context manager for atomic entity mapping operations"""
        lock = None
        try:
            # Acquire distributed lock
            lock = self.acquire_entity_mapping_lock(mention_data, workflow_id)
            
            # Yield control to caller with database transaction
            with self.neo4j.session() as session:
                with session.begin_transaction() as tx:
                    yield tx
                    
        except EntityMappingConflictError:
            # Handle conflicts gracefully
            raise
        except Exception as e:
            # Any other error should be re-raised
            raise
        finally:
            # Always release lock
            if lock:
                self.release_entity_mapping_lock(lock)
    
    def create_or_resolve_entity(self, mention_data: Dict[str, Any], workflow_id: str) -> str:
        """Create new entity or resolve to existing entity with conflict prevention"""
        
        with self.entity_mapping_transaction(mention_data, workflow_id) as tx:
            
            # Step 1: Check if entity already exists in Neo4j
            existing_entity = self._find_existing_entity(tx, mention_data)
            if existing_entity:
                return existing_entity["id"]
            
            # Step 2: Create new entity atomically
            entity_id = self._create_new_entity(tx, mention_data)
            
            # Step 3: Update Redis with persistent mapping
            self._persist_entity_mapping(mention_data, entity_id, workflow_id)
            
            return entity_id
    
    def _create_mention_key(self, mention_data: Dict[str, Any]) -> str:
        """Create stable, deterministic key for mention"""
        # Use surface form + entity type + context for uniqueness
        key_components = [
            mention_data.get("surface_form", "").lower().strip(),
            mention_data.get("entity_type", "").lower(),
            mention_data.get("source_ref", "")[:50]  # First 50 chars of source
        ]
        
        key_string = "|".join(filter(None, key_components))
        return hashlib.sha256(key_string.encode()).hexdigest()[:16]
    
    def _find_existing_entity(self, tx, mention_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find existing entity in Neo4j with similarity matching"""
        surface_form = mention_data.get("surface_form", "").lower()
        entity_type = mention_data.get("entity_type", "")
        
        # Query for exact and similar entities
        query = """
        MATCH (e:Entity)
        WHERE toLower(e.canonical_name) = $surface_form
        AND ($entity_type = '' OR e.entity_type = $entity_type)
        RETURN e.id as id, e.canonical_name as name, e.entity_type as type
        LIMIT 1
        """
        
        result = tx.run(query, surface_form=surface_form, entity_type=entity_type)
        record = result.single()
        
        if record:
            return {
                "id": record["id"],
                "name": record["name"],
                "type": record["type"]
            }
        
        return None
    
    def _create_new_entity(self, tx, mention_data: Dict[str, Any]) -> str:
        """Create new entity in Neo4j"""
        import uuid
        
        entity_id = f"entity_{uuid.uuid4().hex[:12]}"
        
        query = """
        CREATE (e:Entity {
            id: $entity_id,
            canonical_name: $canonical_name,
            entity_type: $entity_type,
            confidence: $confidence,
            created_at: datetime(),
            mention_count: 1
        })
        RETURN e.id as id
        """
        
        result = tx.run(query,
            entity_id=entity_id,
            canonical_name=mention_data.get("surface_form", ""),
            entity_type=mention_data.get("entity_type", ""),
            confidence=mention_data.get("confidence", 0.8)
        )
        
        record = result.single()
        return record["id"]
    
    def _persist_entity_mapping(self, mention_data: Dict[str, Any], entity_id: str, workflow_id: str) -> None:
        """Persist entity mapping to Redis for future lookups"""
        mention_key = self._create_mention_key(mention_data)
        mapping_key = f"entity_mapping:{mention_key}"
        
        mapping_data = {
            "entity_id": entity_id,
            "surface_form": mention_data.get("surface_form"),
            "entity_type": mention_data.get("entity_type"),
            "created_by_workflow": workflow_id,
            "created_at": datetime.now().isoformat()
        }
        
        # Store mapping with 24-hour expiry
        self.redis.setex(
            mapping_key,
            timedelta(hours=24),
            json.dumps(mapping_data)
        )
    
    def get_entity_mapping_stats(self) -> Dict[str, Any]:
        """Get statistics about entity mappings for monitoring"""
        # Count active locks
        active_locks = len(self.redis.keys("entity_mapping_lock:*"))
        
        # Count stored mappings
        stored_mappings = len(self.redis.keys("entity_mapping:*"))
        
        return {
            "active_locks": active_locks,
            "stored_mappings": stored_mappings,
            "redis_connected": self.redis.ping(),
            "timestamp": datetime.now().isoformat()
        }
```

### **Updated EntityBuilder Integration**
```python
# src/tools/phase1/t31_entity_builder.py - Updated sections

class EntityBuilder(BaseNeo4jTool):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize distributed coordinator
        self.entity_coordinator = DistributedEntityCoordinator(
            neo4j_driver=self.driver,
            redis_client=self._get_redis_client()
        )
        self.workflow_id = self._generate_workflow_id()
    
    def _build_entities_from_mentions(self, mentions: List[Dict], source_refs: List[str]) -> List[Dict]:
        """Build entities with distributed coordination"""
        entities_created = []
        
        for mention in mentions:
            try:
                # Use distributed coordinator instead of in-memory mapping
                entity_id = self.entity_coordinator.create_or_resolve_entity(
                    mention_data={
                        "surface_form": mention["surface_form"],
                        "entity_type": mention.get("entity_type", ""),
                        "confidence": mention.get("confidence", 0.8),
                        "source_ref": mention.get("source_ref", "")
                    },
                    workflow_id=self.workflow_id
                )
                
                entities_created.append({
                    "entity_id": entity_id,
                    "surface_form": mention["surface_form"],
                    "entity_type": mention.get("entity_type", ""),
                    "source_mention_id": mention.get("mention_id", ""),
                    "created_via": "distributed_coordination"
                })
                
            except EntityMappingConflictError as e:
                # Handle conflicts gracefully
                logger.warning(f"Entity mapping conflict: {e}")
                # Could implement retry logic or conflict resolution
                continue
            except Exception as e:
                logger.error(f"Entity creation failed for mention {mention.get('mention_id')}: {e}")
                continue
        
        return entities_created
    
    def _generate_workflow_id(self) -> str:
        """Generate unique workflow identifier"""
        import uuid
        import os
        
        pid = os.getpid()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex[:8]
        
        return f"workflow_{timestamp}_{pid}_{unique_id}"
    
    def _get_redis_client(self):
        """Get Redis client for distributed coordination"""
        try:
            import redis
            return redis.Redis(
                host=os.environ.get("REDIS_HOST", "localhost"),
                port=int(os.environ.get("REDIS_PORT", 6379)),
                db=0,
                decode_responses=False  # Keep binary for JSON handling
            )
        except ImportError:
            logger.error("Redis not available - falling back to local coordination")
            return None  # Will need local fallback implementation
```

## 🧪 **Testing Strategy**

### **Concurrency Testing**
```python
# tests/unit/test_entity_mapping_concurrency.py

import asyncio
import pytest
from concurrent.futures import ThreadPoolExecutor
from src.core.distributed_entity_coordinator import DistributedEntityCoordinator

class TestEntityMappingConcurrency:
    
    def test_concurrent_entity_creation_no_conflicts(self):
        """Test that concurrent workflows don't create duplicate entities"""
        coordinator = DistributedEntityCoordinator(self.neo4j_driver, self.redis_client)
        
        # Same entity data processed by multiple workflows
        entity_data = {
            "surface_form": "Apple Inc",
            "entity_type": "ORG",
            "confidence": 0.8
        }
        
        # Create multiple workflows concurrently
        def create_entity_workflow(workflow_id):
            return coordinator.create_or_resolve_entity(entity_data, workflow_id)
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(create_entity_workflow, f"workflow_{i}")
                for i in range(10)
            ]
            
            results = [f.result() for f in futures]
        
        # All workflows should return the same entity ID
        assert len(set(results)) == 1, f"Expected 1 unique entity, got {len(set(results))}"
        
        # Verify only one entity exists in Neo4j
        with self.neo4j_driver.session() as session:
            result = session.run("MATCH (e:Entity {canonical_name: 'Apple Inc'}) RETURN count(e) as count")
            count = result.single()["count"]
            assert count == 1, f"Expected 1 entity in database, found {count}"

    def test_entity_mapping_conflict_detection(self):
        """Test that mapping conflicts are properly detected and handled"""
        coordinator = DistributedEntityCoordinator(self.neo4j_driver, self.redis_client)
        
        entity_data = {
            "surface_form": "Microsoft Corp",
            "entity_type": "ORG"
        }
        
        # First workflow acquires lock
        with coordinator.entity_mapping_transaction(entity_data, "workflow_1") as tx:
            # Second workflow should detect conflict
            with pytest.raises(EntityMappingConflictError):
                coordinator.acquire_entity_mapping_lock(entity_data, "workflow_2")

    def test_lock_expiry_and_recovery(self):
        """Test that expired locks are properly cleaned up"""
        coordinator = DistributedEntityCoordinator(self.neo4j_driver, self.redis_client)
        coordinator.lock_timeout = 1  # 1 second for testing
        
        entity_data = {"surface_form": "Test Entity"}
        
        # Acquire lock
        lock = coordinator.acquire_entity_mapping_lock(entity_data, "workflow_1")
        
        # Wait for lock to expire
        time.sleep(2)
        
        # New workflow should be able to acquire lock
        new_lock = coordinator.acquire_entity_mapping_lock(entity_data, "workflow_2")
        assert new_lock.workflow_id == "workflow_2"

    def test_memory_vs_distributed_consistency(self):
        """Test that distributed coordination prevents in-memory mapping corruption"""
        
        # Simulate old problematic approach
        in_memory_mappings = {}
        
        def old_approach(mention_id, entity_id):
            in_memory_mappings[mention_id] = entity_id  # PROBLEMATIC
        
        # Simulate race condition
        old_approach("Apple Inc", "entity_123")
        old_approach("Apple Inc", "entity_456")  # Overwrites without validation
        
        # In-memory approach creates inconsistency
        assert in_memory_mappings["Apple Inc"] == "entity_456"  # Last write wins
        
        # New distributed approach should prevent this
        coordinator = DistributedEntityCoordinator(self.neo4j_driver, self.redis_client)
        
        entity_data = {"surface_form": "Apple Inc", "entity_type": "ORG"}
        
        # Multiple attempts should return same entity ID
        entity_id_1 = coordinator.create_or_resolve_entity(entity_data, "workflow_1")
        entity_id_2 = coordinator.create_or_resolve_entity(entity_data, "workflow_2")
        
        assert entity_id_1 == entity_id_2, "Distributed coordinator should return consistent entity IDs"
```

## 📝 **Implementation Steps**

### **Day 1: Infrastructure Setup**
1. **Install Redis dependency**: Add Redis to requirements and Docker setup
2. **Create DistributedEntityCoordinator**: Implement base class with locking
3. **Add Redis configuration**: Environment variables and connection handling

### **Day 2-3: Core Implementation**
1. **Implement entity mapping methods**: Lock acquisition, conflict detection
2. **Create mention key generation**: Stable, deterministic key creation
3. **Add transaction coordination**: Neo4j + Redis atomic operations
4. **Error handling**: Comprehensive conflict and failure handling

### **Day 4: Integration**
1. **Update EntityBuilder**: Replace in-memory mappings with coordinator
2. **Add workflow ID generation**: Unique workflow identification
3. **Update service dependencies**: Ensure Redis availability

### **Day 5: Testing and Validation**
1. **Concurrency testing**: Multi-workflow conflict testing
2. **Performance testing**: Ensure coordination doesn't degrade performance
3. **Failure testing**: Test lock expiry, Redis failures, recovery scenarios
4. **Integration testing**: End-to-end workflow validation

## ✅ **Success Criteria**

1. **No Entity Duplication**: Concurrent workflows never create duplicate entities
2. **Conflict Detection**: All mapping conflicts properly detected and handled  
3. **Data Integrity**: No silent data corruption under any concurrency scenario
4. **Performance Maintained**: Coordination overhead <100ms per entity
5. **Failure Recovery**: System recovers gracefully from Redis or Neo4j failures
6. **Monitoring**: Entity mapping statistics available for operational monitoring

## 🚫 **Risks and Mitigation**

### **Risk 1: Redis Dependency**
- **Mitigation**: Implement fallback to Neo4j-based locking if Redis unavailable
- **Validation**: Test system behavior with Redis offline

### **Risk 2: Performance Impact**
- **Mitigation**: Optimize lock acquisition, use connection pooling
- **Validation**: Benchmark coordinator vs direct entity creation

### **Risk 3: Lock Contention**
- **Mitigation**: Fine-grained locking, reasonable timeout values
- **Validation**: Stress test with high concurrent entity creation

## 📚 **References**

- [Redis Distributed Locking](https://redis.io/docs/reference/patterns/distributed-locks/)
- [Neo4j Transaction Management](https://neo4j.com/docs/python-manual/current/transactions/)
- [Entity Resolution Best Practices](https://en.wikipedia.org/wiki/Record_linkage)

This task addresses the single most dangerous reliability issue in the system - silent data corruption that could invalidate all research results.