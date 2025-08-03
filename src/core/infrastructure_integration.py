#!/usr/bin/env python3
"""
Infrastructure Integration Layer

Connects the new infrastructure components with existing KGAS tools,
providing seamless integration and enhanced functionality for all tool operations.
"""

import logging
import asyncio
import time
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from contextlib import asynccontextmanager
import threading
from enum import Enum

# Import infrastructure components
from .database_optimizer import create_database_optimizer
from .memory_manager import MemoryManager
from .llm_cache_manager import LLMCacheManager
from .parallel_processor import ParallelProcessor, ProcessingStrategy, ParallelTask, TaskPriority
from .resource_monitor import ResourceMonitor
from .document_ingestion import DocumentIngestionManager
from .text_preprocessor import TextPreprocessor
from .entity_linker import EntityLinker
from .research_exporter import ResearchExporter, ExportConfiguration, ExportFormat
from .external_api_integrator import ExternalAPIIntegrator, create_research_integrator

# Import existing KGAS components
from .service_manager import ServiceManager
from ..tools.base_tool import BaseTool, ToolRequest, ToolResult

logger = logging.getLogger(__name__)


class IntegrationMode(Enum):
    """Integration operation modes"""
    ENHANCED = "enhanced"  # Full infrastructure integration
    COMPATIBLE = "compatible"  # Backward compatible mode
    PERFORMANCE = "performance"  # Performance-optimized mode
    RESEARCH = "research"  # Research-focused mode


@dataclass
class IntegrationConfiguration:
    """Configuration for infrastructure integration"""
    mode: IntegrationMode = IntegrationMode.ENHANCED
    enable_caching: bool = True
    enable_parallel_processing: bool = True
    enable_resource_monitoring: bool = True
    enable_database_optimization: bool = True
    enable_external_apis: bool = True
    max_parallel_workers: Optional[int] = None
    cache_ttl_hours: int = 24
    memory_limit_gb: float = 8.0
    performance_monitoring: bool = True
    export_formats: List[ExportFormat] = field(default_factory=lambda: [ExportFormat.JSON_ACADEMIC])


@dataclass
class IntegrationMetrics:
    """Metrics for infrastructure integration"""
    total_operations: int = 0
    enhanced_operations: int = 0
    cached_operations: int = 0
    parallel_operations: int = 0
    average_speedup: float = 1.0
    memory_savings_mb: float = 0.0
    cache_hit_rate: float = 0.0
    api_enrichment_count: int = 0
    export_operations: int = 0


class InfrastructureIntegrator:
    """Main infrastructure integration coordinator"""
    
    def __init__(self, config: IntegrationConfiguration = None):
        self.config = config or IntegrationConfiguration()
        self.service_manager = ServiceManager()
        self.metrics = IntegrationMetrics()
        
        # Infrastructure components
        self.database_optimizer = None
        self.memory_manager = None
        self.llm_cache_manager = None
        self.parallel_processor = None
        self.resource_monitor = None
        self.document_ingestion = None
        self.text_preprocessor = None
        self.entity_linker = None
        self.research_exporter = None
        self.api_integrator = None
        
        # Integration state
        self._initialized = False
        self._operation_history = []
        self._performance_baselines = {}
        
        # Thread safety
        self._lock = threading.RLock()
        
        logger.info(f"InfrastructureIntegrator created with mode: {self.config.mode.value}")
    
    async def initialize(self) -> bool:
        """Initialize all infrastructure components"""
        if self._initialized:
            return True
        
        try:
            logger.info("Initializing infrastructure components...")
            
            # Initialize components based on configuration
            if self.config.enable_database_optimization:
                self.database_optimizer = create_database_optimizer()
                logger.info("Database optimizer initialized")
            
            if self.config.enable_caching:
                self.memory_manager = MemoryManager(
                    max_memory_gb=self.config.memory_limit_gb
                )
                self.llm_cache_manager = LLMCacheManager()
                logger.info("Caching components initialized")
            
            if self.config.enable_parallel_processing:
                strategy = ProcessingStrategy.ADAPTIVE if self.config.mode == IntegrationMode.PERFORMANCE else ProcessingStrategy.THREAD_POOL
                self.parallel_processor = ParallelProcessor(
                    strategy=strategy,
                    max_workers=self.config.max_parallel_workers,
                    enable_monitoring=self.config.performance_monitoring
                )
                logger.info("Parallel processor initialized")
            
            if self.config.enable_resource_monitoring:
                self.resource_monitor = ResourceMonitor()
                await self.resource_monitor.start_monitoring()
                logger.info("Resource monitor initialized")
            
            # Initialize data pipeline components
            self.document_ingestion = DocumentIngestionManager()
            self.text_preprocessor = TextPreprocessor()
            self.entity_linker = EntityLinker()
            self.research_exporter = ResearchExporter()
            
            if self.config.enable_external_apis:
                self.api_integrator = create_research_integrator()
                logger.info("External API integrator initialized")
            
            self._initialized = True
            logger.info("Infrastructure integration initialization complete")
            return True
            
        except Exception as e:
            logger.error(f"Infrastructure initialization failed: {e}", exc_info=True)
            return False
    
    @asynccontextmanager
    async def integrated_tool_execution(self, tool: BaseTool, request: ToolRequest):
        """Context manager for integrated tool execution"""
        operation_start = time.time()
        operation_id = f"op_{int(time.time() * 1000)}"
        
        # Record operation start
        self.metrics.total_operations += 1
        
        try:
            # Pre-execution optimization
            optimized_request = await self._optimize_request(tool, request)
            
            # Check for cached results
            cached_result = None
            if self.config.enable_caching and self.llm_cache_manager:
                cached_result = await self._check_cache(tool, optimized_request)
                if cached_result:
                    self.metrics.cached_operations += 1
                    logger.debug(f"Cache hit for {tool.tool_id}")
            
            # Resource monitoring
            if self.resource_monitor:
                resource_snapshot = self.resource_monitor.get_current_metrics()
            
            yield {
                'operation_id': operation_id,
                'optimized_request': optimized_request,
                'cached_result': cached_result,
                'resource_snapshot': resource_snapshot if self.resource_monitor else None
            }
            
        finally:
            # Post-execution cleanup and metrics
            execution_time = time.time() - operation_start
            
            # Update performance metrics
            baseline_time = self._performance_baselines.get(tool.tool_id, execution_time)
            speedup = baseline_time / max(execution_time, 0.001)
            self.metrics.average_speedup = (
                (self.metrics.average_speedup * (self.metrics.total_operations - 1) + speedup) / 
                self.metrics.total_operations
            )
            
            # Store performance baseline
            if tool.tool_id not in self._performance_baselines:
                self._performance_baselines[tool.tool_id] = execution_time
            
            # Record operation in history
            self._operation_history.append({
                'operation_id': operation_id,
                'tool_id': tool.tool_id,
                'execution_time': execution_time,
                'speedup': speedup,
                'timestamp': datetime.now().isoformat()
            })
            
            # Keep history bounded
            if len(self._operation_history) > 1000:
                self._operation_history = self._operation_history[-500:]
    
    async def enhance_tool_execution(self, tool: BaseTool, request: ToolRequest) -> ToolResult:
        """Execute tool with full infrastructure enhancement"""
        
        async with self.integrated_tool_execution(tool, request) as context:
            operation_id = context['operation_id']
            optimized_request = context['optimized_request']
            cached_result = context['cached_result']
            
            # Return cached result if available
            if cached_result:
                return cached_result
            
            # Determine execution strategy
            if (self.config.enable_parallel_processing and 
                self.parallel_processor and 
                self._should_parallelize(tool, optimized_request)):
                
                result = await self._execute_parallel(tool, optimized_request, operation_id)
                self.metrics.parallel_operations += 1
                
            else:
                # Standard execution with monitoring
                result = await self._execute_monitored(tool, optimized_request, operation_id)
            
            # Post-process result
            enhanced_result = await self._enhance_result(tool, result, operation_id)
            
            # Cache result if appropriate
            if (self.config.enable_caching and 
                self.llm_cache_manager and 
                enhanced_result.status == "success"):
                await self._cache_result(tool, optimized_request, enhanced_result)
            
            self.metrics.enhanced_operations += 1
            return enhanced_result
    
    async def enhance_document_processing(self, document_path: str, 
                                        processing_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Enhanced document processing using infrastructure"""
        
        config = processing_config or {}
        start_time = time.time()
        
        try:
            logger.info(f"Starting enhanced document processing: {document_path}")
            
            # Stage 1: Document Ingestion with format detection
            ingestion_result = await self.document_ingestion.ingest_document(
                file_path=document_path,
                extract_metadata=True,
                quality_assessment=True
            )
            
            if not ingestion_result.success:
                return {
                    'status': 'error',
                    'error': f"Document ingestion failed: {ingestion_result.error_message}",
                    'processing_time': time.time() - start_time
                }
            
            # Stage 2: Text Preprocessing with quality assessment
            preprocessing_result = await self.text_preprocessor.process_text(
                text=ingestion_result.content,
                processing_level='advanced',
                quality_assessment=True,
                domain_specific=config.get('domain', 'general')
            )
            
            # Stage 3: Enhanced entity extraction with linking
            entities = []
            if self.entity_linker:
                linking_result = await self.entity_linker.link_entities(
                    text=preprocessing_result.cleaned_text,
                    entities=preprocessing_result.extracted_entities or [],
                    confidence_threshold=config.get('entity_confidence', 0.7)
                )
                entities = linking_result.consolidated_entities
            
            # Stage 4: External API enrichment (if enabled)
            enriched_entities = entities
            if self.config.enable_external_apis and self.api_integrator:
                entity_names = [e.canonical_name for e in entities[:10]]  # Limit for API calls
                enrichment_results = await self.api_integrator.batch_enrich_entities(
                    entity_names, batch_size=5
                )
                
                # Merge enrichment data
                enrichment_map = {r.original_entity: r for r in enrichment_results}
                for entity in enriched_entities:
                    if entity.canonical_name in enrichment_map:
                        enrichment = enrichment_map[entity.canonical_name]
                        entity.attributes.update(enrichment.enriched_data)
                        entity.confidence_score = max(entity.confidence_score, enrichment.confidence_score)
                
                self.metrics.api_enrichment_count += len(enrichment_results)
            
            # Stage 5: Results compilation
            processing_result = {
                'status': 'success',
                'document_info': {
                    'path': document_path,
                    'format': ingestion_result.format_detected,
                    'size_bytes': ingestion_result.file_size,
                    'quality_score': ingestion_result.quality_metrics.get('overall_quality', 0.0)
                },
                'content': {
                    'raw_text': ingestion_result.content,
                    'cleaned_text': preprocessing_result.cleaned_text,
                    'text_quality': preprocessing_result.quality_metrics,
                    'word_count': len(preprocessing_result.cleaned_text.split())
                },
                'entities': [
                    {
                        'entity_id': e.entity_id,
                        'canonical_name': e.canonical_name,
                        'entity_type': e.entity_type,
                        'confidence': e.confidence_score,
                        'aliases': e.aliases,
                        'attributes': e.attributes,
                        'mentions_count': len(e.mentions)
                    }
                    for e in enriched_entities
                ],
                'relationships': preprocessing_result.relationships or [],
                'processing_metrics': {
                    'total_time': time.time() - start_time,
                    'stages_completed': 5,
                    'entities_extracted': len(entities),
                    'entities_enriched': self.metrics.api_enrichment_count,
                    'quality_improvements': preprocessing_result.quality_improvements
                },
                'infrastructure_metrics': {
                    'memory_used_mb': self.resource_monitor.get_current_metrics().memory_used_mb if self.resource_monitor else 0,
                    'cache_hits': self.metrics.cached_operations,
                    'parallel_operations': self.metrics.parallel_operations
                }
            }
            
            logger.info(f"Enhanced document processing completed in {processing_result['processing_metrics']['total_time']:.2f}s")
            return processing_result
            
        except Exception as e:
            logger.error(f"Enhanced document processing failed: {e}", exc_info=True)
            return {
                'status': 'error',
                'error': str(e),
                'processing_time': time.time() - start_time
            }
    
    async def export_research_results(self, results: Dict[str, Any], 
                                    export_config: ExportConfiguration) -> Dict[str, Any]:
        """Export research results using infrastructure"""
        
        try:
            # Convert results to export format
            entities = [
                self.research_exporter.EntityProfile(
                    entity_id=e['entity_id'],
                    canonical_name=e['canonical_name'],
                    entity_type=e['entity_type'],
                    confidence_score=e['confidence'],
                    aliases=e.get('aliases', []),
                    attributes=e.get('attributes', {}),
                    mentions=e.get('mentions', [])
                )
                for e in results.get('entities', [])
            ]
            
            documents = [
                self.research_exporter.ResearchDocument(
                    document_id=doc.get('id', 'unknown'),
                    title=doc.get('title', 'Untitled'),
                    authors=doc.get('authors', []),
                    publication_year=doc.get('year'),
                    abstract=doc.get('abstract')
                )
                for doc in results.get('documents', [])
            ]
            
            relationships = results.get('relationships', [])
            analysis_results = [
                self.research_exporter.AnalysisResult(
                    analysis_id=f"analysis_{i}",
                    analysis_type="entity_extraction",
                    title="Entity Extraction Results",
                    description="Automated entity extraction and enrichment results",
                    results=results.get('processing_metrics', {}),
                    confidence_metrics=results.get('quality_metrics', {})
                )
            ]
            
            # Perform export
            success = self.research_exporter.export_research_results(
                entities=entities,
                documents=documents,
                relationships=relationships,
                analysis_results=analysis_results,
                config=export_config
            )
            
            if success:
                self.metrics.export_operations += 1
                return {
                    'status': 'success',
                    'export_path': export_config.output_path,
                    'format': export_config.format.value,
                    'entities_exported': len(entities),
                    'documents_exported': len(documents)
                }
            else:
                return {
                    'status': 'error',
                    'error': 'Export operation failed'
                }
                
        except Exception as e:
            logger.error(f"Research export failed: {e}", exc_info=True)
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def _optimize_request(self, tool: BaseTool, request: ToolRequest) -> ToolRequest:
        """Optimize request based on infrastructure capabilities"""
        
        # Memory optimization
        if self.memory_manager:
            optimized_data = self.memory_manager.optimize_data_structure(request.input_data)
            request = ToolRequest(
                tool_id=request.tool_id,
                operation=request.operation,
                input_data=optimized_data,
                parameters=request.parameters,
                context=request.context
            )
        
        # Add infrastructure context
        infrastructure_context = {
            'integration_mode': self.config.mode.value,
            'parallel_available': self.parallel_processor is not None,
            'caching_enabled': self.config.enable_caching,
            'api_enrichment_available': self.api_integrator is not None
        }
        
        enhanced_context = {**(request.context or {}), **infrastructure_context}
        
        return ToolRequest(
            tool_id=request.tool_id,
            operation=request.operation,
            input_data=request.input_data,
            parameters=request.parameters,
            context=enhanced_context
        )
    
    async def _check_cache(self, tool: BaseTool, request: ToolRequest) -> Optional[ToolResult]:
        """Check for cached results"""
        if not self.llm_cache_manager:
            return None
        
        try:
            cache_key = f"{tool.tool_id}:{request.operation}:{hash(str(request.input_data))}"
            cached_response = await self.llm_cache_manager.get_cached_response(
                prompt=cache_key,
                model_params=request.parameters
            )
            
            if cached_response:
                return ToolResult(
                    tool_id=tool.tool_id,
                    status="success",
                    data=cached_response.response,
                    metadata={
                        **cached_response.metadata,
                        'cached': True,
                        'cache_timestamp': cached_response.cached_at.isoformat()
                    },
                    execution_time=0.001  # Minimal cache retrieval time
                )
            
        except Exception as e:
            logger.warning(f"Cache check failed: {e}")
        
        return None
    
    async def _cache_result(self, tool: BaseTool, request: ToolRequest, result: ToolResult):
        """Cache successful result"""
        if not self.llm_cache_manager or result.status != "success":
            return
        
        try:
            cache_key = f"{tool.tool_id}:{request.operation}:{hash(str(request.input_data))}"
            await self.llm_cache_manager.cache_response(
                prompt=cache_key,
                response=result.data,
                model_params=request.parameters,
                metadata={
                    'tool_id': tool.tool_id,
                    'operation': request.operation,
                    'execution_time': result.execution_time
                }
            )
            
        except Exception as e:
            logger.warning(f"Result caching failed: {e}")
    
    def _should_parallelize(self, tool: BaseTool, request: ToolRequest) -> bool:
        """Determine if operation should be parallelized"""
        
        # Check if tool supports parallelization
        parallel_tools = {
            'T01_PDF_LOADER', 'T15A_TEXT_CHUNKER', 'T23A_SPACY_NER', 
            'T27_RELATIONSHIP_EXTRACTOR', 'T31_ENTITY_BUILDER'
        }
        
        if tool.tool_id not in parallel_tools:
            return False
        
        # Check data size for parallelization threshold
        data_size = len(str(request.input_data))
        return data_size > 1000  # Parallelize for larger inputs
    
    async def _execute_parallel(self, tool: BaseTool, request: ToolRequest, 
                              operation_id: str) -> ToolResult:
        """Execute tool using parallel processing"""
        
        task = ParallelTask(
            task_id=operation_id,
            function=tool.execute,
            args=(request,),
            priority=TaskPriority.NORMAL,
            timeout_seconds=300,
            metadata={'tool_id': tool.tool_id}
        )
        
        success = self.parallel_processor.submit_task(task)
        if not success:
            # Fallback to standard execution
            return await self._execute_monitored(tool, request, operation_id)
        
        # Wait for completion
        completed = self.parallel_processor.wait_for_completion(timeout=360)
        if not completed:
            logger.warning(f"Parallel execution timeout for {tool.tool_id}")
            return await self._execute_monitored(tool, request, operation_id)
        
        # Get result
        result = self.parallel_processor.get_task_result(operation_id)
        if result and result.status == "completed":
            return result.result
        else:
            # Fallback to standard execution
            return await self._execute_monitored(tool, request, operation_id)
    
    async def _execute_monitored(self, tool: BaseTool, request: ToolRequest, 
                                operation_id: str) -> ToolResult:
        """Execute tool with resource monitoring"""
        
        start_time = time.time()
        
        # Monitor resource usage during execution
        if self.resource_monitor:
            resource_start = self.resource_monitor.get_current_metrics()
        
        try:
            # Execute tool
            result = tool.execute(request)
            
            # Add monitoring metadata
            execution_time = time.time() - start_time
            
            if self.resource_monitor:
                resource_end = self.resource_monitor.get_current_metrics()
                memory_delta = resource_end.memory_used_mb - resource_start.memory_used_mb
                self.metrics.memory_savings_mb += max(0, memory_delta)
            
            # Enhance result with infrastructure metadata
            enhanced_metadata = {
                **(result.metadata or {}),
                'infrastructure': {
                    'integration_mode': self.config.mode.value,
                    'execution_time': execution_time,
                    'operation_id': operation_id,
                    'enhanced': True
                }
            }
            
            return ToolResult(
                tool_id=result.tool_id,
                status=result.status,
                data=result.data,
                metadata=enhanced_metadata,
                execution_time=result.execution_time,
                memory_used=result.memory_used,
                error_code=result.error_code,
                error_message=result.error_message
            )
            
        except Exception as e:
            logger.error(f"Monitored execution failed: {e}", exc_info=True)
            return ToolResult(
                tool_id=tool.tool_id,
                status="error",
                error_message=str(e),
                execution_time=time.time() - start_time,
                metadata={'operation_id': operation_id}
            )
    
    async def _enhance_result(self, tool: BaseTool, result: ToolResult, 
                            operation_id: str) -> ToolResult:
        """Enhance result with additional infrastructure capabilities"""
        
        if result.status != "success":
            return result
        
        enhanced_data = result.data
        enhanced_metadata = result.metadata or {}
        
        # Add entity linking for NER results
        if (tool.tool_id == "T23A_SPACY_NER" and 
            self.entity_linker and 
            'entities' in enhanced_data):
            
            try:
                entities = enhanced_data['entities']
                entity_names = [e.get('surface_form', '') for e in entities]
                
                linking_result = await self.entity_linker.link_entities(
                    text="",  # Not needed for entity names
                    entities=entity_names,
                    confidence_threshold=0.6
                )
                
                # Enhance entities with linking data
                enhanced_entities = []
                for i, entity in enumerate(entities):
                    enhanced_entity = entity.copy()
                    if i < len(linking_result.consolidated_entities):
                        linked_entity = linking_result.consolidated_entities[i]
                        enhanced_entity['linked_entity_id'] = linked_entity.entity_id
                        enhanced_entity['canonical_name'] = linked_entity.canonical_name
                        enhanced_entity['aliases'] = linked_entity.aliases
                    enhanced_entities.append(enhanced_entity)
                
                enhanced_data['entities'] = enhanced_entities
                enhanced_metadata['entity_linking'] = {
                    'entities_linked': len(linking_result.consolidated_entities),
                    'confidence_threshold': 0.6
                }
                
            except Exception as e:
                logger.warning(f"Entity linking enhancement failed: {e}")
        
        return ToolResult(
            tool_id=result.tool_id,
            status=result.status,
            data=enhanced_data,
            metadata=enhanced_metadata,
            execution_time=result.execution_time,
            memory_used=result.memory_used,
            error_code=result.error_code,
            error_message=result.error_message
        )
    
    def get_integration_metrics(self) -> Dict[str, Any]:
        """Get comprehensive integration metrics"""
        
        # Update cache hit rate
        if self.metrics.total_operations > 0:
            self.metrics.cache_hit_rate = self.metrics.cached_operations / self.metrics.total_operations
        
        return {
            'integration_config': {
                'mode': self.config.mode.value,
                'caching_enabled': self.config.enable_caching,
                'parallel_processing_enabled': self.config.enable_parallel_processing,
                'resource_monitoring_enabled': self.config.enable_resource_monitoring,
                'external_apis_enabled': self.config.enable_external_apis
            },
            'performance_metrics': {
                'total_operations': self.metrics.total_operations,
                'enhanced_operations': self.metrics.enhanced_operations,
                'cached_operations': self.metrics.cached_operations,
                'parallel_operations': self.metrics.parallel_operations,
                'cache_hit_rate': f"{self.metrics.cache_hit_rate:.1%}",
                'average_speedup': f"{self.metrics.average_speedup:.2f}x",
                'memory_savings_mb': self.metrics.memory_savings_mb,
                'api_enrichment_count': self.metrics.api_enrichment_count,
                'export_operations': self.metrics.export_operations
            },
            'component_status': {
                'database_optimizer': self.database_optimizer is not None,
                'memory_manager': self.memory_manager is not None,
                'llm_cache_manager': self.llm_cache_manager is not None,
                'parallel_processor': self.parallel_processor is not None,
                'resource_monitor': self.resource_monitor is not None,
                'document_ingestion': self.document_ingestion is not None,
                'text_preprocessor': self.text_preprocessor is not None,
                'entity_linker': self.entity_linker is not None,
                'research_exporter': self.research_exporter is not None,
                'api_integrator': self.api_integrator is not None
            },
            'recent_operations': self._operation_history[-10:] if self._operation_history else []
        }
    
    async def cleanup(self):
        """Clean up infrastructure resources"""
        logger.info("Cleaning up infrastructure integration...")
        
        try:
            if self.parallel_processor:
                self.parallel_processor.shutdown(wait=True, timeout=30)
            
            if self.resource_monitor:
                await self.resource_monitor.stop_monitoring()
            
            if self.api_integrator:
                await self.api_integrator.close()
            
            if self.llm_cache_manager:
                await self.llm_cache_manager.cleanup_expired()
            
            logger.info("Infrastructure cleanup completed")
            
        except Exception as e:
            logger.error(f"Infrastructure cleanup error: {e}", exc_info=True)


# Factory functions for common integration scenarios
def create_performance_integrator() -> InfrastructureIntegrator:
    """Create integrator optimized for performance"""
    config = IntegrationConfiguration(
        mode=IntegrationMode.PERFORMANCE,
        enable_parallel_processing=True,
        enable_caching=True,
        enable_resource_monitoring=True,
        enable_database_optimization=True,
        max_parallel_workers=8
    )
    return InfrastructureIntegrator(config)


def create_research_integrator() -> InfrastructureIntegrator:
    """Create integrator optimized for research workflows"""
    config = IntegrationConfiguration(
        mode=IntegrationMode.RESEARCH,
        enable_external_apis=True,
        enable_caching=True,
        cache_ttl_hours=48,  # Longer cache for research
        export_formats=[ExportFormat.LATEX_ARTICLE, ExportFormat.BIBTEX, ExportFormat.JSON_ACADEMIC]
    )
    return InfrastructureIntegrator(config)


def create_compatible_integrator() -> InfrastructureIntegrator:
    """Create integrator for backward compatibility"""
    config = IntegrationConfiguration(
        mode=IntegrationMode.COMPATIBLE,
        enable_parallel_processing=False,
        enable_resource_monitoring=True,
        performance_monitoring=True
    )
    return InfrastructureIntegrator(config)


# Example usage and testing
if __name__ == "__main__":
    async def test_integration():
        """Test infrastructure integration"""
        
        # Create performance-optimized integrator
        integrator = create_performance_integrator()
        
        try:
            # Initialize
            success = await integrator.initialize()
            if not success:
                print("Integration initialization failed")
                return
            
            # Test enhanced document processing
            print("Testing enhanced document processing...")
            
            # This would be replaced with actual test document
            test_doc_path = "test_data/sample.pdf"
            if Path(test_doc_path).exists():
                result = await integrator.enhance_document_processing(
                    test_doc_path,
                    {'domain': 'academic', 'entity_confidence': 0.8}
                )
                
                print(f"Processing result: {result['status']}")
                if result['status'] == 'success':
                    print(f"Entities found: {len(result['entities'])}")
                    print(f"Processing time: {result['processing_metrics']['total_time']:.2f}s")
            
            # Show metrics
            metrics = integrator.get_integration_metrics()
            print(f"Integration Metrics:")
            print(f"  Total operations: {metrics['performance_metrics']['total_operations']}")
            print(f"  Cache hit rate: {metrics['performance_metrics']['cache_hit_rate']}")
            print(f"  Average speedup: {metrics['performance_metrics']['average_speedup']}")
            
        finally:
            await integrator.cleanup()
    
    # Run test
    asyncio.run(test_integration())