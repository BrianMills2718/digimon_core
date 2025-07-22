# External MCP Service Orchestration Architecture

**Purpose**: Define the architecture for integrating external MCP services while preserving KGAS theory-aware capabilities  
**Related ADR**: [ADR-005: Buy vs Build Strategy](../adrs/ADR-005-buy-vs-build-strategy.md)

## Overview

The External MCP Service Orchestration system enables KGAS to leverage external MCP servers for infrastructure acceleration while maintaining core competitive advantages in theory-aware research processing.

## Architectural Principles

### 1. Theory-Aware Integration
All external data flows through KGAS theory-extraction and cross-modal analysis engines to preserve research quality and academic rigor.

### 2. Provenance Preservation
Complete traceability maintained across external service boundaries, ensuring research reproducibility standards.

### 3. Fallback Resilience
Internal implementations available for critical external dependencies to prevent research workflow disruption.

## System Architecture

### Core Components

#### External MCP Orchestrator
```python
class KGASMCPOrchestrator:
    """Central orchestrator for external MCP service integration"""
    
    def __init__(self):
        # External service categories
        self.academic_services = ['arxiv-mcp', 'pubmed-mcp', 'biomcp']
        self.document_services = ['markitdown-mcp', 'content-core-mcp']  
        self.knowledge_services = ['neo4j-mcp', 'chroma-mcp', 'memory-mcp']
        self.analytics_services = ['dbt-mcp', 'vizro-mcp', 'optuna-mcp']
        
        # Core KGAS services (always internal)
        self.core_services = ['theory-extraction', 'cross-modal', 'provenance']
        
    async def orchestrate_analysis(self, request: AnalysisRequest):
        """Route analysis through appropriate service composition"""
        # 1. External data acquisition
        raw_data = await self._acquire_external_data(request)
        
        # 2. External processing (format conversion, parsing)
        processed_data = await self._external_processing(raw_data)
        
        # 3. KGAS theory-aware processing (internal)  
        theory_results = await self._theory_processing(processed_data)
        
        # 4. Cross-modal analysis (internal)
        final_results = await self._cross_modal_analysis(theory_results)
        
        # 5. Provenance tracking throughout
        return self._wrap_with_provenance(final_results, request)
```

### Data Flow Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Academic APIs │    │  Document Parser │    │  Knowledge Graph│
│  (ArXiv/PubMed) │───▶│   (MarkItDown)   │───▶│   (Neo4j/Multi) │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│              KGAS Theory-Aware Processing Engine               │
│  • Automated Theory Extraction (0.910 production score)        │
│  • Cross-Modal Analysis (Graph/Table/Vector)                   │
│  • Multi-Theory Composition & Validation                       │
│  • Complete Provenance & Uncertainty Tracking                  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Visualization │    │   Data Pipeline  │    │   Research      │
│   (External)    │◀───│   (External)     │◀───│   Output        │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Service Integration Patterns

### Academic Data Sources

#### ArXiv Integration
```python
class ArXivMCPIntegration:
    """Integration with ArXiv MCP server for paper discovery"""
    
    async def search_papers(self, query: str, theory_context: str) -> List[Paper]:
        """Search ArXiv with theory-guided query enhancement"""
        # 1. Enhance query using KGAS theory knowledge
        enhanced_query = await self.theory_query_enhancer.enhance(query, theory_context)
        
        # 2. Call external ArXiv MCP
        raw_results = await self.arxiv_mcp.search(enhanced_query)
        
        # 3. Apply KGAS theory filtering and relevance scoring
        filtered_results = await self.theory_relevance_filter.filter(raw_results, theory_context)
        
        return filtered_results
```

#### PubMed Integration
```python
class PubMedMCPIntegration:
    """Integration with PubMed MCP for medical/life sciences research"""
    
    async def medical_literature_search(self, research_question: str) -> List[MedicalPaper]:
        """Search PubMed with research question decomposition"""
        # 1. Decompose research question using KGAS theory framework
        question_components = await self.research_question_analyzer.decompose(research_question)
        
        # 2. Parallel searches across components
        search_tasks = [self.pubmed_mcp.search(component) for component in question_components]
        raw_results = await asyncio.gather(*search_tasks)
        
        # 3. Synthesize results using cross-modal analysis
        synthesized_results = await self.cross_modal_synthesizer.synthesize(raw_results)
        
        return synthesized_results
```

### Document Processing Integration

#### MarkItDown Integration
```python
class MarkItDownMCPIntegration:
    """Integration with Microsoft MarkItDown for document format conversion"""
    
    async def convert_document(self, document_path: str) -> ProcessedDocument:
        """Convert document formats while preserving KGAS metadata"""
        # 1. Pre-processing: Extract KGAS-specific metadata
        metadata = await self.metadata_extractor.extract(document_path)
        
        # 2. External conversion
        converted_content = await self.markitdown_mcp.convert(document_path)
        
        # 3. Post-processing: Restore KGAS context and prepare for theory extraction
        enhanced_document = await self.document_enhancer.enhance(
            converted_content, metadata, self.theory_context
        )
        
        return enhanced_document
```

### Knowledge Infrastructure Integration

#### Multi-Vector Database Strategy
```python
class MultiVectorOrchestrator:
    """Orchestrate multiple vector databases based on use case"""
    
    def __init__(self):
        self.vector_providers = {
            'primary': Neo4jNativeVectors(),      # Current implementation
            'specialized': PineconeVectors(),     # Large-scale research
            'research': ChromaVectors(),          # Experimental features
            'local': QdrantVectors()             # Development/testing
        }
    
    async def optimal_search(self, query_vector: List[float], context: str) -> SearchResults:
        """Route vector search to optimal provider based on context"""
        provider = self._select_optimal_provider(context)
        return await provider.similarity_search(query_vector)
    
    def _select_optimal_provider(self, context: str) -> VectorProvider:
        """LLM-driven provider selection based on research context"""
        if 'large_scale' in context:
            return self.vector_providers['specialized']
        elif 'experimental' in context:
            return self.vector_providers['research']
        else:
            return self.vector_providers['primary']
```

## Quality Assurance Framework

### Theory-Aware Validation
```python
class ExternalServiceValidator:
    """Validate external service results against KGAS quality standards"""
    
    async def validate_external_result(self, result: Any, service_type: str) -> ValidationResult:
        """Validate external service output for research quality"""
        validation_checks = {
            'academic_api': self._validate_academic_metadata,
            'document_processor': self._validate_document_structure,
            'knowledge_service': self._validate_knowledge_integrity
        }
        
        validator = validation_checks.get(service_type)
        if validator:
            return await validator(result)
        
        return ValidationResult(status='unknown', warnings=['Unknown service type'])
    
    async def _validate_academic_metadata(self, paper_data: Dict) -> ValidationResult:
        """Ensure academic papers meet research quality standards"""
        required_fields = ['title', 'authors', 'publication_date', 'doi_or_arxiv_id']
        missing_fields = [field for field in required_fields if field not in paper_data]
        
        if missing_fields:
            return ValidationResult(
                status='invalid', 
                errors=[f'Missing required field: {field}' for field in missing_fields]
            )
        
        return ValidationResult(status='valid')
```

### Provenance Integration
```python
class ExternalServiceProvenance:
    """Track provenance across external service boundaries"""
    
    async def track_external_operation(self, 
                                     operation: str, 
                                     service: str, 
                                     inputs: Dict, 
                                     outputs: Dict) -> ProvenanceRecord:
        """Create provenance record for external service call"""
        return ProvenanceRecord(
            activity_type='external_service_call',
            service_name=service,
            operation_name=operation,
            inputs_hash=self._hash_inputs(inputs),
            outputs_hash=self._hash_outputs(outputs),
            timestamp=datetime.now(),
            kgas_context=self._extract_kgas_context(),
            external_service_version=await self._get_service_version(service)
        )
```

## Performance Optimization

### Caching Strategy
```python
class ExternalServiceCache:
    """Intelligent caching for external service results"""
    
    def __init__(self):
        self.cache_strategies = {
            'academic_api': TTLCache(ttl=3600),  # Papers change infrequently
            'document_processor': LRUCache(maxsize=1000),  # Document conversion results
            'knowledge_service': WriteThruCache()  # Knowledge queries need consistency
        }
    
    async def cached_call(self, service: str, operation: str, **kwargs) -> Any:
        """Execute external service call with intelligent caching"""
        cache_key = self._generate_cache_key(service, operation, kwargs)
        cache = self.cache_strategies.get(service)
        
        if cache and cache_key in cache:
            return cache[cache_key]
        
        # Execute external service call
        result = await self._execute_external_call(service, operation, **kwargs)
        
        # Cache result if appropriate
        if cache:
            cache[cache_key] = result
        
        return result
```

### Error Handling and Fallbacks
```python
class ExternalServiceFallbacks:
    """Fallback strategies for external service failures"""
    
    async def resilient_call(self, service: str, operation: str, **kwargs) -> Any:
        """Execute external service call with fallback strategies"""
        try:
            return await self._primary_service_call(service, operation, **kwargs)
        except ExternalServiceError as e:
            logger.warning(f"External service {service} failed: {e}")
            return await self._fallback_strategy(service, operation, **kwargs)
    
    async def _fallback_strategy(self, service: str, operation: str, **kwargs) -> Any:
        """Route to appropriate fallback based on service type"""
        fallback_strategies = {
            'academic_api': self._local_academic_search,
            'document_processor': self._internal_document_parser,
            'knowledge_service': self._local_knowledge_query
        }
        
        fallback = fallback_strategies.get(service)
        if fallback:
            return await fallback(**kwargs)
        
        raise FallbackNotAvailableError(f"No fallback available for service: {service}")
```

## Deployment Architecture

### Service Discovery
```python
class ExternalMCPServiceRegistry:
    """Registry and discovery for external MCP services"""
    
    def __init__(self):
        self.service_configs = {
            'arxiv-mcp': {
                'command': 'npx blazickjp/arxiv-mcp-server',
                'health_check': '/health',
                'capabilities': ['paper_search', 'paper_details']
            },
            'markitdown-mcp': {
                'command': 'npx microsoft/markitdown',
                'health_check': '/convert/health',
                'capabilities': ['document_conversion']
            }
        }
    
    async def ensure_service_availability(self, service_name: str) -> bool:
        """Ensure external MCP service is running and healthy"""
        config = self.service_configs.get(service_name)
        if not config:
            return False
        
        # Check if service is running
        if not await self._is_service_running(service_name):
            await self._start_service(service_name, config)
        
        # Verify health
        return await self._health_check(service_name, config)
```

## Monitoring and Observability

### Service Health Monitoring
```python
class ExternalServiceMonitor:
    """Monitor health and performance of external MCP services"""
    
    async def monitor_service_health(self) -> Dict[str, ServiceHealth]:
        """Monitor all external services and return health status"""
        health_checks = {}
        
        for service_name in self.registered_services:
            try:
                response_time = await self._measure_response_time(service_name)
                error_rate = await self._calculate_error_rate(service_name)
                
                health_checks[service_name] = ServiceHealth(
                    status='healthy' if error_rate < 0.05 else 'degraded',
                    response_time_ms=response_time,
                    error_rate=error_rate,
                    last_check=datetime.now()
                )
            except Exception as e:
                health_checks[service_name] = ServiceHealth(
                    status='unhealthy',
                    error=str(e),
                    last_check=datetime.now()
                )
        
        return health_checks
```

## Security Considerations

### API Key Management
```python
class ExternalServiceSecurityManager:
    """Secure management of external service credentials"""
    
    async def get_service_credentials(self, service_name: str) -> ServiceCredentials:
        """Retrieve credentials for external service"""
        # Credentials stored in secure vault (not in code)
        encrypted_creds = await self.credential_vault.get(service_name)
        return await self.credential_decoder.decode(encrypted_creds)
    
    async def rotate_service_credentials(self, service_name: str) -> None:
        """Rotate credentials for external service"""
        new_creds = await self.credential_generator.generate(service_name)
        await self.credential_vault.store(service_name, new_creds)
        await self._notify_service_credential_update(service_name)
```

This architecture enables KGAS to leverage external MCP services for accelerated development while preserving core theory-aware research capabilities and maintaining academic research quality standards.