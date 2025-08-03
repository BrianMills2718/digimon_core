# PostgreSQL Migration Initiative

**Status**: Planned  
**Priority**: Medium (Scale-Driven)  
**Timeline**: 5-7 days implementation when scale requirements reached  
**Context**: Support for 50,000+ entity academic research corpora  

## Overview

Migration from SQLite to PostgreSQL in the bi-store architecture to support large-scale academic research while maintaining all current functionality and adding advanced analytical capabilities.

**Migration Target**: Neo4j + SQLite → Neo4j + PostgreSQL + pgvector

## Business Justification

### Scale Requirements
- **Target Use Case**: Processing 1,000+ academic papers (50,000+ entities)
- **Current SQLite Limitations**: 
  - Performance degradation at scale (45+ seconds for 50K entity correlation analysis)
  - Single-writer bottleneck during batch analysis
  - Memory constraints on complex queries
  - No query parallelization capabilities

### Academic Research Benefits
- **Advanced Analytics**: Native statistical functions (CORR, REGR_*, window functions)
- **Longitudinal Studies**: Time-series analysis with LAG/LEAD functions
- **BI Integration**: Direct R/Python/Tableau connectivity
- **Performance**: 6-15x faster complex queries at scale

## Implementation Strategy

### Phase 1: Core Database Migration (3 days)

**Primary Deliverables:**
- PostgreSQL connection manager with pooling
- SQL dialect conversion layer
- Schema migration scripts with validation
- Backward compatibility during transition

**Key Files to Modify:**
```
src/core/sqlite_manager.py → src/core/postgres_manager.py
src/core/provenance_persistence.py (JSON handling updates)
src/core/service_manager.py (connection configuration)
config/default.yaml (PostgreSQL parameters)
```

**Technical Implementation:**
```python
# Core architectural change
class DatabaseManager:
    def __init__(self, config):
        self.use_postgres = config.get('database', {}).get('use_postgres', False)
        
        if self.use_postgres:
            self.db = PostgresManager(config)  # New implementation
        else:
            self.db = SQLiteManager(config)    # Fallback during migration
```

### Phase 2: Advanced Analytics Integration (2 days)

**Enhanced Capabilities:**
- Window functions for longitudinal analysis
- Native statistical functions (correlation, regression)
- pgvector integration for vector operations
- Optimized indexing for academic workloads

**Academic Research Queries Enabled:**
```sql
-- Longitudinal influence analysis
SELECT 
    entity_id,
    canonical_name,
    measurement_date,
    pagerank_score,
    LAG(pagerank_score) OVER (
        PARTITION BY entity_id ORDER BY measurement_date
    ) as influence_change,
    PERCENT_RANK() OVER (
        PARTITION BY measurement_date ORDER BY pagerank_score
    ) as influence_percentile
FROM entity_metrics_timeseries;

-- Cross-community statistical analysis
SELECT 
    community_id,
    AVG(pagerank_score) as avg_influence,
    CORR(pagerank_score, betweenness_centrality) as centrality_correlation,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY pagerank_score) as top_5_percent
FROM entity_metrics
GROUP BY community_id;
```

### Phase 3: Deployment Automation (2 days)

**Automated Setup:**
- Docker Compose configuration for one-command deployment
- Platform-specific installation scripts (Windows/Mac/Linux)
- Database initialization with pgvector extension
- Migration and rollback procedures

**Docker Configuration:**
```yaml
services:
  kgas-postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: kgas
      POSTGRES_USER: kgas_user
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-scripts:/docker-entrypoint-initdb.d/
    
  kgas-pgvector:
    image: pgvector/pgvector:pg15
    depends_on:
      - kgas-postgres
```

## Performance Benchmarks

### Expected Improvements (50,000 entities)
| Operation | SQLite | PostgreSQL | Improvement |
|---|---|---|---|
| **Correlation Analysis** | 45+ seconds | 3-8 seconds | **6-15x faster** |
| **Complex Joins** | Memory limited | Optimized buffering | **Unlimited scale** |
| **Window Functions** | Not supported | Native support | **New capability** |
| **Concurrent Access** | Single-writer | Multi-connection | **Parallel analytics** |

### Memory Usage Optimization
- Complex query memory usage: 2GB+ → <1GB
- Connection pooling prevents resource exhaustion
- Optimized indexing strategies for academic data patterns

## Risk Assessment and Mitigation

### Technical Risks
**Risk**: Migration complexity and SQL dialect differences  
**Mitigation**: 
- Phased migration with rollback capability
- Comprehensive test suite covering all operations
- Dual database support during transition

**Risk**: PostgreSQL deployment complexity in academic environments  
**Mitigation**: 
- Docker containerization for consistent deployment
- Automated installation scripts for all platforms
- Detailed troubleshooting documentation

### Operational Risks
**Risk**: Performance regression during migration  
**Mitigation**: 
- Comprehensive performance benchmarking
- PostgreSQL tuning for academic workloads
- Gradual migration with validation at each step

**Risk**: Data loss during migration  
**Mitigation**: 
- Complete data export/validation before migration
- Rollback procedures tested and documented
- Backup verification processes

## Trigger Conditions for Migration

### Scale Indicators
- Regular processing of 10,000+ entity documents
- Multi-document comparative studies becoming common
- User performance complaints about query speed
- Memory crashes during statistical analysis

### Performance Thresholds
- Correlation analysis taking >30 seconds consistently
- Complex queries causing memory exhaustion
- Need for concurrent analytical sessions
- Request for advanced statistical functions

## Success Criteria

### Performance Requirements
- [ ] 50,000 entity correlation analysis completes in <10 seconds
- [ ] Window function queries execute in <5 seconds
- [ ] Complex queries use <1GB memory
- [ ] Support 10+ concurrent analytical connections

### Functional Requirements
- [ ] All existing SQLite functionality preserved
- [ ] Advanced statistical functions operational (CORR, REGR_*, PERCENT_RANK)
- [ ] Longitudinal analysis with window functions working
- [ ] Direct R/Python/Tableau connectivity established
- [ ] pgvector integration for semantic search

### Operational Requirements
- [ ] One-command installation for academic environments
- [ ] Docker deployment across all platforms
- [ ] Migration scripts with comprehensive validation
- [ ] Rollback capability tested and documented
- [ ] Performance monitoring and alerting

## Dependencies

### Technical Dependencies
- Docker and Docker Compose for automated deployment
- PostgreSQL 15+ with pgvector extension
- psycopg2 Python driver for PostgreSQL connectivity
- Connection pooling library (psycopg2.pool)

### Architectural Dependencies
- Completion of current bi-store architecture validation
- Service manager stability for database abstraction
- Neo4j integration stability (unaffected by migration)
- Provenance service compatibility testing

### Testing Dependencies
- Performance benchmarking framework
- Large-scale test datasets (50,000+ entities)
- Multi-platform testing environments
- Statistical function validation suite

## Timeline and Milestones

### Immediate Planning Phase (When Triggered)
- [ ] Performance baseline establishment with current SQLite
- [ ] PostgreSQL environment setup and testing
- [ ] Migration script development and validation

### Week 1: Core Migration
- **Days 1-3**: Database layer migration and testing
- **Day 4**: Service integration and validation
- **Day 5**: End-to-end pipeline testing

### Week 2: Enhancement and Deployment
- **Days 1-2**: Advanced analytics integration
- **Days 3-4**: Deployment automation and Docker
- **Day 5**: Documentation and final validation

### Post-Migration
- Performance monitoring and optimization
- User training on new analytical capabilities
- Documentation updates and troubleshooting guides

## Related Documentation

- **[ADR-030: PostgreSQL Migration Strategy](../architecture/adrs/ADR-030-PostgreSQL-Migration-Strategy.md)**: Technical decision rationale
- **[ADR-009: Bi-Store Database Strategy](../architecture/adrs/ADR-009-Bi-Store-Database-Strategy.md)**: Current architecture foundation
- **[Database Schemas](../architecture/data/DATABASE_SCHEMAS.md)**: Current schema documentation

## Notes

This migration is **scale-driven** rather than feature-driven. The current SQLite implementation works perfectly for typical academic use cases (1,000-10,000 entities). Migration should only be triggered when users consistently encounter performance limitations with large-scale research projects.

The phased approach ensures minimal disruption to current users while providing a clear upgrade path for researchers working with large academic corpora.