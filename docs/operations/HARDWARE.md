**Doc status**: Living – auto-checked by doc-governance CI

# KGAS Hardware Requirements

**Document Version**: 1.0  
**Created**: 2025-01-27  
**Purpose**: Hardware specifications and performance benchmarks for KGAS deployment

---

## Minimum Viable Machine

### System Requirements
- **CPU**: 4 vCPU
- **RAM**: 16 GB (holds ~30M Neo4j nodes)
- **Disk**: 100 GB SSD
- **GPU**: optional, only for embedding refresh
- **Tested on MacBook M3** — all Docker containers run, but Qdrant indexing 10 M vectors saturates CPU for 35 min.

### Recommended Configuration
- **CPU**: 8 vCPU
- **RAM**: 32 GB (supports larger knowledge graphs)
- **Disk**: 500 GB NVMe SSD
- **GPU**: NVIDIA RTX 3080 or equivalent (for embedding operations)

---

## Performance Benchmarks

### Toy Dataset (50k nodes)
- **Neo4j load**: 17s
- **Qdrant vector insert**: 11s
- **Total processing time**: ~30s

### Medium Dataset (1M nodes)
- **Neo4j load**: 5m 23s
- **Qdrant vector insert**: 3m 45s
- **Total processing time**: ~10m

### Large Dataset (10M nodes)
- **Neo4j load**: 45m 12s
- **Qdrant vector insert**: 32m 8s
- **Total processing time**: ~80m

---

## Storage Requirements

### Neo4j Database
- **Base storage**: ~2GB for 1M nodes
- **Index storage**: ~500MB for 1M nodes
- **Transaction logs**: ~100MB per day of heavy usage

### Qdrant Vector Database
- **Vector storage**: ~4GB for 1M embeddings (1536 dimensions)
- **Metadata storage**: ~200MB for 1M entities
- **Index storage**: ~1GB for 1M vectors

### PII Vault
- **Encrypted storage**: ~50MB for 10k PII entries
- **Backup storage**: ~100MB for encrypted backups

---

## Network Requirements

### Minimum Bandwidth
- **Upload**: 10 Mbps (for document processing)
- **Download**: 25 Mbps (for model downloads and updates)

### Recommended Bandwidth
- **Upload**: 100 Mbps
- **Download**: 500 Mbps

---

## Scaling Considerations

### Vertical Scaling
- **CPU**: Add more cores for parallel processing
- **RAM**: Increase for larger knowledge graphs
- **Storage**: Use faster SSDs for better I/O performance

### Horizontal Scaling
- **Neo4j**: Use Neo4j Enterprise for clustering
- **Qdrant**: Deploy multiple instances with load balancing
- **Processing**: Use container orchestration (Kubernetes)

---

## Cloud Deployment

### AWS Recommendations
- **EC2**: m5.2xlarge or larger
- **Storage**: EBS gp3 volumes
- **Database**: RDS for PostgreSQL (metadata)
- **Vector DB**: Self-hosted Qdrant on EC2

### Azure Recommendations
- **VM**: Standard_D8s_v3 or larger
- **Storage**: Premium SSD
- **Database**: Azure Database for PostgreSQL
- **Vector DB**: Self-hosted Qdrant on Azure VM

### Google Cloud Recommendations
- **Compute**: n2-standard-8 or larger
- **Storage**: Persistent SSD
- **Database**: Cloud SQL for PostgreSQL
- **Vector DB**: Self-hosted Qdrant on GCE

---

## Performance Optimization

### Neo4j Optimization
- **JVM heap**: Set to 70% of available RAM
- **Page cache**: Set to 25% of available RAM
- **Indexes**: Create indexes on frequently queried properties
- **Cypher optimization**: Use parameterized queries

### Qdrant Optimization
- **Vector dimensions**: Optimize for your embedding model
- **Distance metrics**: Choose appropriate metric for your use case
- **Index type**: Use HNSW for approximate search
- **Payload indexing**: Index frequently filtered fields

### System Optimization
- **File system**: Use XFS or ext4 with noatime
- **I/O scheduler**: Use deadline or noop scheduler
- **Memory management**: Enable transparent huge pages
- **CPU governor**: Use performance governor

---

## Monitoring and Alerts

### Key Metrics
- **CPU usage**: Alert if >80% for 5 minutes
- **Memory usage**: Alert if >85% for 5 minutes
- **Disk usage**: Alert if >90%
- **Response time**: Alert if >5s for queries

### Monitoring Tools
- **System**: Prometheus + Grafana
- **Neo4j**: Neo4j Browser + monitoring plugins
- **Qdrant**: Built-in metrics endpoint
- **Application**: Custom metrics via Python

---

**Note**: These specifications are based on current system requirements and may change as the system evolves. Always test with your specific workload before production deployment. -e 
<br><sup>See `docs/planning/roadmap.md` for master plan.</sup>
