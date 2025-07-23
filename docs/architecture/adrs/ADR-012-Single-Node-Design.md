# ADR-012: Single-Node Design

**Status**: Accepted  
**Date**: 2025-07-23  
**Context**: System must choose between single-node local deployment or distributed multi-node architecture based on academic research environment constraints and requirements.

## Decision

We will implement a **single-node architecture** optimized for local deployment on researcher personal or institutional computers:

```python
class SingleNodeArchitecture:
    def __init__(self):
        self.deployment_target = "local_researcher_environment"
        self.database_strategy = "embedded_databases"  # Neo4j + SQLite
        self.processing_model = "sequential_with_async"
        self.resource_constraints = "single_machine_optimization"
        self.user_model = "single_researcher_per_instance"
```

### **Core Design Principles**
1. **Local data processing**: All analysis occurs on researcher's machine
2. **Embedded databases**: Neo4j and SQLite run locally without server administration
3. **Simple deployment**: Single installation command with minimal dependencies
4. **Resource optimization**: Efficient use of typical academic hardware (8-32GB RAM, 4-8 cores)
5. **Offline capability**: Core functionality works without internet connectivity

## Rationale

### **Why Single-Node Architecture?**

**1. Academic Research Environment Reality**:
- **Individual researchers**: Primary users are PhD students, postdocs, faculty working independently
- **Personal computers**: Analysis performed on laptops/desktops, not server infrastructure
- **Institutional constraints**: Many institutions lack resources for distributed research infrastructure
- **Data sensitivity**: Academic research often involves sensitive data requiring local processing

**2. Research Workflow Patterns**:
- **Project-based**: Research projects are discrete, time-bounded efforts (months to years)
- **Dataset sizes**: Typical academic research involves 10-1000 documents, not millions
- **Iterative analysis**: Researchers repeatedly analyze same datasets with different approaches
- **Exploratory nature**: Research involves experimental methods requiring rapid iteration

**3. Academic Computing Constraints**:
- **Limited technical expertise**: Researchers are domain experts, not systems administrators
- **No DevOps support**: Most academic environments lack dedicated infrastructure teams
- **Budget limitations**: Academic budgets cannot support complex distributed infrastructure
- **Reproducibility requirements**: Other researchers must be able to replicate analysis locally

### **Why Not Distributed Architecture?**

**Distributed architectures would create incompatible barriers**:

**1. Infrastructure Requirements**:
- **Server administration**: Requires database server setup, monitoring, maintenance
- **Network configuration**: Requires understanding of distributed system networking
- **Security management**: Requires enterprise-level security expertise
- **Resource provisioning**: Requires understanding of distributed resource allocation

**2. Academic Environment Mismatch**:
- **Single-user focus**: Academic research is typically individual, not multi-tenant
- **Intermittent usage**: Research projects have periods of intensive use followed by dormancy
- **Data locality**: Researchers need direct access to their data and processing results
- **Reproducibility**: Other researchers must replicate analysis without complex infrastructure

**3. Cost and Complexity**:
- **Infrastructure costs**: Distributed systems require significant ongoing operational costs
- **Maintenance overhead**: Requires ongoing system administration and monitoring
- **Deployment complexity**: Complex setup procedures incompatible with academic workflows
- **Failure modes**: Distributed system failures require specialized expertise to diagnose

## Alternatives Considered

### **1. Distributed Multi-Node Architecture**
**Rejected because**:
- **Infrastructure requirements**: Requires server administration expertise beyond typical research environments
- **Cost barriers**: Ongoing infrastructure costs incompatible with academic budgets
- **Deployment complexity**: Setup procedures too complex for individual researchers
- **Reproducibility issues**: Other researchers cannot easily replicate distributed infrastructure

### **2. Cloud-Based SaaS Architecture**
**Rejected because**:
- **Data sensitivity**: Academic research often involves confidential or proprietary data
- **Internet dependency**: Researchers need offline analysis capability
- **Cost concerns**: Per-use costs can become prohibitive for extensive academic research
- **Control limitations**: Researchers lose control over processing parameters and methods

### **3. Hybrid Local/Cloud Architecture**
**Rejected because**:
- **Complexity**: Creates two different deployment and configuration paths
- **Data synchronization**: Complex data management across local and cloud environments
- **Cost unpredictability**: Difficult to predict cloud costs for academic research budgets
- **Reproducibility**: Hybrid environments difficult to replicate by other researchers

### **4. Container-Based Distributed (Docker Swarm/Kubernetes)**
**Rejected because**:
- **Technical complexity**: Requires container orchestration expertise
- **Resource overhead**: Container orchestration adds significant resource requirements
- **Local deployment issues**: Complex local Kubernetes setup inappropriate for researchers
- **Maintenance burden**: Requires ongoing orchestration platform maintenance

## Consequences

### **Positive**
- **Simple deployment**: Single installation command gets researchers running
- **Local data control**: Researchers maintain complete control over their data
- **Offline capability**: Analysis can continue without internet connectivity
- **Reproducible environment**: Other researchers can easily replicate identical local setup
- **Cost-effective**: No ongoing infrastructure or cloud costs
- **Fast iteration**: No network latency or coordination overhead for analysis iterations

### **Negative**
- **Scalability limits**: Cannot handle enterprise-scale datasets (millions of documents)
- **Resource constraints**: Limited by single-machine memory and processing power
- **No multi-user support**: Cannot support multiple concurrent researchers
- **Limited parallelization**: Parallelization constrained to single-machine cores
- **Backup responsibility**: Researchers responsible for their own data backup

## Single-Node Architecture Implementation

### **Database Strategy**
```python
class LocalDatabaseManager:
    def __init__(self, data_directory: Path):
        # Embedded Neo4j - no server required
        self.neo4j = GraphDatabase.driver(
            f"bolt://localhost:7687",
            auth=("neo4j", "password"),
            encrypted=False  # Local deployment
        )
        
        # SQLite file database - no server required
        self.sqlite_path = data_directory / "kgas_metadata.db"
        self.sqlite = sqlite3.connect(str(self.sqlite_path))
```

### **Processing Model**
```python
class SingleNodeProcessor:
    def __init__(self, max_workers: int = None):
        # Use all available cores but respect memory constraints
        self.max_workers = max_workers or min(8, os.cpu_count())
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
    
    async def process_documents(self, documents: List[Path]) -> ProcessingResults:
        """Process documents using single-node async concurrency"""
        # Batch processing to manage memory usage
        results = []
        for batch in self._create_batches(documents, batch_size=10):
            batch_results = await self._process_batch(batch)
            results.extend(batch_results)
            
            # Memory management between batches
            self._cleanup_batch_resources()
            
        return ProcessingResults(results)
```

### **Resource Management**
```python
class ResourceManager:
    def __init__(self):
        self.available_memory = psutil.virtual_memory().available
        self.available_cores = os.cpu_count()
        
    def optimize_for_hardware(self) -> ProcessingConfig:
        """Optimize processing parameters for available hardware"""
        return ProcessingConfig(
            batch_size=self._calculate_optimal_batch_size(),
            worker_threads=min(8, self.available_cores),
            memory_limit=int(self.available_memory * 0.8),  # Leave 20% for OS
            cache_size=self._calculate_cache_size()
        )
```

## Scalability Strategy

### **Current Limitations and Workarounds**
- **Memory limits**: Process documents in batches to manage memory usage
- **Processing time**: Use async processing and progress tracking for large datasets
- **Storage limits**: Implement data archival and cleanup strategies
- **CPU constraints**: Optimize algorithms for single-machine parallelization

### **Future Extension Points**
While maintaining single-node focus, architecture allows for:
- **Cloud processing backends**: Optional cloud processing for very large datasets
- **Cluster computing**: Optional integration with academic computing clusters
- **Batch job systems**: Integration with university computing resources

```python
# Future extension interface (not current implementation)
class ProcessingBackend(ABC):
    @abstractmethod
    async def submit_job(self, job_spec: Dict) -> str:
        pass

class LocalProcessingBackend(ProcessingBackend):
    """Current single-node implementation"""
    pass

class AzureProcessingBackend(ProcessingBackend):
    """Future cloud processing option"""
    pass
```

## Implementation Requirements

### **Local Deployment**
- **One-command setup**: `pip install kgas && kgas init`
- **Automatic database setup**: Embedded databases start automatically
- **Default configuration**: Sensible defaults for typical academic hardware
- **Error recovery**: Graceful handling of resource constraints

### **Resource Optimization**
- **Memory management**: Batch processing to avoid memory exhaustion
- **CPU utilization**: Efficient use of available cores without oversubscription
- **Storage management**: Intelligent caching and cleanup strategies
- **Progress tracking**: Clear progress indication for long-running analyses

### **Data Management**
- **Local storage**: All data stored in researcher-controlled directories
- **Backup guidance**: Clear instructions for data backup and recovery
- **Export capabilities**: Easy export of results for sharing and publication
- **Data privacy**: Local processing ensures data never leaves researcher control

## Validation Criteria

- [ ] Complete system installation in < 5 minutes on typical academic hardware
- [ ] Processing of 100-document corpus completes in < 2 hours
- [ ] Memory usage stays within 80% of available RAM during processing
- [ ] System functions offline after initial setup
- [ ] Other researchers can replicate identical local environment
- [ ] Resource usage scales appropriately with available hardware
- [ ] Clear error messages and recovery guidance for resource limitations

## Related ADRs

- **ADR-011**: Academic Research Focus (single-node aligns with research requirements)
- **ADR-009**: Bi-Store Database Strategy (embedded database strategy)
- **ADR-008**: Core Service Architecture (single-node service management)

**Future Evolution Note**: While current architecture is single-node, the design allows for optional distributed processing backends for researchers with access to cloud or cluster resources, while maintaining the core single-node simplicity for typical academic use cases.