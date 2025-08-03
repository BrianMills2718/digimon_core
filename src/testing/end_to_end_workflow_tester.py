#!/usr/bin/env python3
"""
End-to-End Workflow Testing Framework

Comprehensive testing framework for validating complete document processing pipelines
with infrastructure integration, performance measurement, and quality validation.
"""

import logging
import asyncio
import time
import json
import uuid
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from enum import Enum
import tempfile
import shutil
from contextlib import asynccontextmanager

# Import infrastructure and tools
from ..core.infrastructure_integration import InfrastructureIntegrator, IntegrationConfiguration, IntegrationMode
from ..core.service_manager import ServiceManager
from ..tools.phase1.t01_pdf_loader_unified import T01PDFLoaderUnified
from ..tools.phase1.t15a_text_chunker_unified import T15ATextChunkerUnified
from ..tools.phase1.t23a_spacy_ner_unified import T23ASpacyNERUnified
from ..tools.phase1.t27_relationship_extractor_unified import T27RelationshipExtractorUnified
from ..tools.phase1.t31_entity_builder_unified import T31EntityBuilderUnified
from ..tools.phase1.t34_edge_builder_unified import T34EdgeBuilderUnified
from ..tools.phase1.t68_pagerank_unified import T68PageRankCalculatorUnified
from ..tools.phase1.t49_multihop_query_unified import T49MultiHopQueryUnified
from ..tools.base_tool import ToolRequest, ToolResult

logger = logging.getLogger(__name__)


class WorkflowType(Enum):
    """Types of workflows to test"""
    BASIC_PIPELINE = "basic_pipeline"  # PDF -> PageRank -> Answer
    ENHANCED_PIPELINE = "enhanced_pipeline"  # With infrastructure integration
    PARALLEL_PIPELINE = "parallel_pipeline"  # With parallel processing
    RESEARCH_PIPELINE = "research_pipeline"  # With API enrichment and export
    STRESS_TEST = "stress_test"  # High load testing


class TestStatus(Enum):
    """Test execution status"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class TestConfiguration:
    """Configuration for workflow testing"""
    workflow_type: WorkflowType
    integration_mode: IntegrationMode = IntegrationMode.ENHANCED
    parallel_processing: bool = True
    enable_caching: bool = True
    enable_api_enrichment: bool = False
    max_parallel_workers: int = 4
    timeout_seconds: int = 300
    quality_threshold: float = 0.7
    performance_target_speedup: float = 1.2
    memory_limit_gb: float = 4.0
    test_data_path: str = "test_data"


@dataclass
class WorkflowStepResult:
    """Result of a single workflow step"""
    step_name: str
    tool_id: str
    status: TestStatus
    execution_time: float
    memory_used_mb: float
    input_size: int
    output_size: int
    quality_score: float
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowTestResult:
    """Complete workflow test result"""
    test_id: str
    workflow_type: WorkflowType
    status: TestStatus
    total_execution_time: float
    steps: List[WorkflowStepResult] = field(default_factory=list)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    quality_metrics: Dict[str, Any] = field(default_factory=dict)
    infrastructure_metrics: Dict[str, Any] = field(default_factory=dict)
    error_summary: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class EndToEndWorkflowTester:
    """Comprehensive end-to-end workflow testing framework"""
    
    def __init__(self, config: TestConfiguration = None):
        self.config = config or TestConfiguration(WorkflowType.ENHANCED_PIPELINE)
        self.service_manager = ServiceManager()
        self.integrator = None
        
        # Test data and results
        self.test_results = []
        self.test_data_registry = {}
        self.baseline_metrics = {}
        
        # Workflow definitions
        self.workflow_definitions = {
            WorkflowType.BASIC_PIPELINE: self._define_basic_pipeline,
            WorkflowType.ENHANCED_PIPELINE: self._define_enhanced_pipeline,
            WorkflowType.PARALLEL_PIPELINE: self._define_parallel_pipeline,
            WorkflowType.RESEARCH_PIPELINE: self._define_research_pipeline,
            WorkflowType.STRESS_TEST: self._define_stress_test
        }
        
        logger.info(f"WorkflowTester initialized for {self.config.workflow_type.value}")
    
    async def initialize(self) -> bool:
        """Initialize testing framework and infrastructure"""
        try:
            logger.info("Initializing workflow testing framework...")
            
            # Initialize service manager
            if not await self.service_manager.initialize():
                logger.error("Service manager initialization failed")
                return False
            
            # Initialize infrastructure integrator
            integration_config = IntegrationConfiguration(
                mode=self.config.integration_mode,
                enable_parallel_processing=self.config.parallel_processing,
                enable_caching=self.config.enable_caching,
                enable_external_apis=self.config.enable_api_enrichment,
                max_parallel_workers=self.config.max_parallel_workers,
                memory_limit_gb=self.config.memory_limit_gb
            )
            
            self.integrator = InfrastructureIntegrator(integration_config)
            if not await self.integrator.initialize():
                logger.error("Infrastructure integrator initialization failed")
                return False
            
            # Initialize test data registry
            await self._initialize_test_data()
            
            logger.info("Workflow testing framework initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Workflow tester initialization failed: {e}", exc_info=True)
            return False
    
    async def run_comprehensive_test_suite(self) -> Dict[str, Any]:
        """Run comprehensive test suite across all workflow types"""
        
        logger.info("Starting comprehensive workflow test suite...")
        start_time = time.time()
        
        suite_results = {
            'suite_id': str(uuid.uuid4()),
            'start_time': datetime.now().isoformat(),
            'configuration': {
                'integration_mode': self.config.integration_mode.value,
                'parallel_processing': self.config.parallel_processing,
                'caching_enabled': self.config.enable_caching,
                'api_enrichment': self.config.enable_api_enrichment,
                'timeout_seconds': self.config.timeout_seconds
            },
            'workflow_results': {},
            'summary': {
                'total_workflows': 0,
                'passed_workflows': 0,
                'failed_workflows': 0,
                'total_execution_time': 0.0,
                'average_performance_improvement': 0.0
            }
        }
        
        # Test each workflow type
        workflow_types = [
            WorkflowType.BASIC_PIPELINE,
            WorkflowType.ENHANCED_PIPELINE,
            WorkflowType.PARALLEL_PIPELINE
        ]
        
        # Add research pipeline if API enrichment enabled
        if self.config.enable_api_enrichment:
            workflow_types.append(WorkflowType.RESEARCH_PIPELINE)
        
        for workflow_type in workflow_types:
            logger.info(f"Testing workflow: {workflow_type.value}")
            
            try:
                # Update configuration for this workflow
                workflow_config = TestConfiguration(
                    workflow_type=workflow_type,
                    integration_mode=self.config.integration_mode,
                    parallel_processing=self.config.parallel_processing,
                    enable_caching=self.config.enable_caching,
                    enable_api_enrichment=self.config.enable_api_enrichment,
                    timeout_seconds=self.config.timeout_seconds
                )
                
                # Run workflow test
                workflow_result = await self.test_workflow(workflow_config)
                suite_results['workflow_results'][workflow_type.value] = workflow_result
                
                # Update summary
                suite_results['summary']['total_workflows'] += 1
                if workflow_result.status == TestStatus.PASSED:
                    suite_results['summary']['passed_workflows'] += 1
                else:
                    suite_results['summary']['failed_workflows'] += 1
                
            except Exception as e:
                logger.error(f"Workflow test failed for {workflow_type.value}: {e}")
                suite_results['workflow_results'][workflow_type.value] = {
                    'status': TestStatus.ERROR.value,
                    'error': str(e)
                }
                suite_results['summary']['failed_workflows'] += 1
        
        # Calculate final metrics
        total_time = time.time() - start_time
        suite_results['summary']['total_execution_time'] = total_time
        suite_results['end_time'] = datetime.now().isoformat()
        
        # Calculate average performance improvement
        performance_improvements = []
        for workflow_result in suite_results['workflow_results'].values():
            if isinstance(workflow_result, dict) and 'performance_metrics' in workflow_result:
                speedup = workflow_result['performance_metrics'].get('speedup_factor', 1.0)
                performance_improvements.append(speedup)
        
        if performance_improvements:
            suite_results['summary']['average_performance_improvement'] = sum(performance_improvements) / len(performance_improvements)
        
        # Generate test report
        await self._generate_test_report(suite_results)
        
        logger.info(f"Comprehensive test suite completed in {total_time:.2f}s")
        logger.info(f"Results: {suite_results['summary']['passed_workflows']}/{suite_results['summary']['total_workflows']} workflows passed")
        
        return suite_results
    
    async def test_workflow(self, workflow_config: TestConfiguration = None) -> WorkflowTestResult:
        """Test a specific workflow configuration"""
        
        config = workflow_config or self.config
        test_id = str(uuid.uuid4())
        start_time = time.time()
        
        logger.info(f"Starting workflow test: {config.workflow_type.value} (ID: {test_id})")
        
        result = WorkflowTestResult(
            test_id=test_id,
            workflow_type=config.workflow_type,
            status=TestStatus.RUNNING,
            total_execution_time=0.0
        )
        
        try:
            # Get workflow definition
            workflow_definition = self.workflow_definitions[config.workflow_type]
            steps = await workflow_definition()
            
            # Execute workflow steps
            workflow_context = {
                'test_id': test_id,
                'config': config,
                'data': {},
                'metrics': {}
            }
            
            for i, step in enumerate(steps):
                step_start_time = time.time()
                
                logger.info(f"Executing step {i+1}/{len(steps)}: {step['name']}")
                
                # Execute step with timeout
                try:
                    step_result = await asyncio.wait_for(
                        self._execute_workflow_step(step, workflow_context),
                        timeout=config.timeout_seconds
                    )
                    
                    step_result.step_name = step['name']
                    result.steps.append(step_result)
                    
                    # Update workflow context with step results
                    workflow_context['data'][step['name']] = step_result.metadata.get('output_data')
                    
                    # Check if step failed
                    if step_result.status == TestStatus.FAILED:
                        result.status = TestStatus.FAILED
                        result.error_summary = f"Step '{step['name']}' failed: {step_result.error_message}"
                        break
                    
                except asyncio.TimeoutError:
                    logger.error(f"Step {step['name']} timed out after {config.timeout_seconds}s")
                    step_result = WorkflowStepResult(
                        step_name=step['name'],
                        tool_id=step.get('tool_id', 'unknown'),
                        status=TestStatus.FAILED,
                        execution_time=config.timeout_seconds,
                        memory_used_mb=0,
                        input_size=0,
                        output_size=0,
                        quality_score=0.0,
                        error_message="Step execution timed out"
                    )
                    result.steps.append(step_result)
                    result.status = TestStatus.FAILED
                    result.error_summary = f"Step '{step['name']}' timed out"
                    break
            
            # If all steps completed successfully
            if result.status == TestStatus.RUNNING:
                result.status = TestStatus.PASSED
            
            # Calculate final metrics
            result.total_execution_time = time.time() - start_time
            result.performance_metrics = self._calculate_performance_metrics(result, workflow_context)
            result.quality_metrics = self._calculate_quality_metrics(result, workflow_context)
            
            if self.integrator:
                result.infrastructure_metrics = self.integrator.get_integration_metrics()
            
            # Validate workflow results
            validation_result = await self._validate_workflow_results(result, workflow_context)
            if not validation_result['valid']:
                result.status = TestStatus.FAILED
                result.error_summary = f"Workflow validation failed: {validation_result['reason']}"
            
            logger.info(f"Workflow test completed: {result.status.value} in {result.total_execution_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Workflow test error: {e}", exc_info=True)
            result.status = TestStatus.ERROR
            result.error_summary = str(e)
            result.total_execution_time = time.time() - start_time
        
        # Store result
        self.test_results.append(result)
        
        return result
    
    async def _execute_workflow_step(self, step: Dict[str, Any], 
                                   context: Dict[str, Any]) -> WorkflowStepResult:
        """Execute a single workflow step"""
        
        step_start_time = time.time()
        initial_memory = self._get_memory_usage()
        
        try:
            # Get tool instance
            tool_class = step['tool_class']
            tool_instance = tool_class(self.service_manager)
            
            # Prepare input data
            input_data = await self._prepare_step_input(step, context)
            input_size = len(str(input_data))
            
            # Create tool request
            request = ToolRequest(
                tool_id=step.get('tool_id', tool_instance.tool_id),
                operation=step.get('operation', 'execute'),
                input_data=input_data,
                parameters=step.get('parameters', {}),
                context={'test_id': context['test_id']}
            )
            
            # Execute tool with or without infrastructure integration
            if self.integrator and step.get('use_integration', True):
                result = await self.integrator.enhance_tool_execution(tool_instance, request)
            else:
                result = tool_instance.execute(request)
            
            # Calculate metrics
            execution_time = time.time() - step_start_time
            memory_used = self._get_memory_usage() - initial_memory
            output_size = len(str(result.data)) if result.data else 0
            
            # Calculate quality score
            quality_score = self._calculate_step_quality_score(step, result)
            
            # Create step result
            step_result = WorkflowStepResult(
                step_name=step['name'],
                tool_id=step.get('tool_id', tool_instance.tool_id),
                status=TestStatus.PASSED if result.status == "success" else TestStatus.FAILED,
                execution_time=execution_time,
                memory_used_mb=memory_used,
                input_size=input_size,
                output_size=output_size,
                quality_score=quality_score,
                error_message=result.error_message if result.status != "success" else None,
                metadata={
                    'tool_result': result,
                    'output_data': result.data,
                    'step_config': step
                }
            )
            
            logger.debug(f"Step '{step['name']}' completed: {step_result.status.value} in {execution_time:.2f}s")
            
            return step_result
            
        except Exception as e:
            logger.error(f"Step execution error: {e}", exc_info=True)
            
            return WorkflowStepResult(
                step_name=step['name'],
                tool_id=step.get('tool_id', 'unknown'),
                status=TestStatus.ERROR,
                execution_time=time.time() - step_start_time,
                memory_used_mb=self._get_memory_usage() - initial_memory,
                input_size=0,
                output_size=0,
                quality_score=0.0,
                error_message=str(e)
            )
    
    async def _define_basic_pipeline(self) -> List[Dict[str, Any]]:
        """Define basic PDF -> PageRank -> Answer pipeline"""
        return [
            {
                'name': 'PDF Loading',
                'tool_class': T01PDFLoaderUnified,
                'tool_id': 'T01_PDF_LOADER',
                'operation': 'load_document',
                'use_integration': False,  # Test without integration first
                'input_source': 'test_pdf',
                'expected_output': 'document_content'
            },
            {
                'name': 'Text Chunking',
                'tool_class': T15ATextChunkerUnified,
                'tool_id': 'T15A_TEXT_CHUNKER',
                'operation': 'chunk_text',
                'use_integration': False,
                'input_source': 'document_content',
                'expected_output': 'text_chunks'
            },
            {
                'name': 'Entity Extraction',
                'tool_class': T23ASpacyNERUnified,
                'tool_id': 'T23A_SPACY_NER',
                'operation': 'extract_entities',
                'use_integration': False,
                'input_source': 'text_chunks',
                'expected_output': 'entities'
            },
            {
                'name': 'Relationship Extraction',
                'tool_class': T27RelationshipExtractorUnified,
                'tool_id': 'T27_RELATIONSHIP_EXTRACTOR',
                'operation': 'extract_relationships',
                'use_integration': False,
                'input_source': 'entities',
                'expected_output': 'relationships'
            },
            {
                'name': 'Entity Building',
                'tool_class': T31EntityBuilderUnified,
                'tool_id': 'T31_ENTITY_BUILDER',
                'operation': 'build_entities',
                'use_integration': False,
                'input_source': 'entities',
                'expected_output': 'graph_entities'
            },
            {
                'name': 'Edge Building',
                'tool_class': T34EdgeBuilderUnified,
                'tool_id': 'T34_EDGE_BUILDER',
                'operation': 'build_edges',
                'use_integration': False,
                'input_source': 'relationships',
                'expected_output': 'graph_edges'
            },
            {
                'name': 'PageRank Calculation',
                'tool_class': T68PageRankCalculatorUnified,
                'tool_id': 'T68_PAGERANK_CALCULATOR',
                'operation': 'calculate_pagerank',
                'use_integration': False,
                'input_source': 'graph_entities',
                'expected_output': 'pagerank_scores'
            },
            {
                'name': 'Multi-hop Query',
                'tool_class': T49MultiHopQueryUnified,
                'tool_id': 'T49_MULTIHOP_QUERY',
                'operation': 'query_graph',
                'use_integration': False,
                'input_source': 'test_query',
                'expected_output': 'query_results',
                'parameters': {'query': 'What are the main entities in the document?'}
            }
        ]
    
    async def _define_enhanced_pipeline(self) -> List[Dict[str, Any]]:
        """Define enhanced pipeline with infrastructure integration"""
        steps = await self._define_basic_pipeline()
        
        # Enable integration for all steps
        for step in steps:
            step['use_integration'] = True
        
        return steps
    
    async def _define_parallel_pipeline(self) -> List[Dict[str, Any]]:
        """Define pipeline optimized for parallel processing"""
        steps = await self._define_enhanced_pipeline()
        
        # Add parallel processing hints
        parallel_steps = ['Text Chunking', 'Entity Extraction', 'Relationship Extraction']
        for step in steps:
            if step['name'] in parallel_steps:
                step['parameters'] = step.get('parameters', {})
                step['parameters']['parallel_processing'] = True
        
        return steps
    
    async def _define_research_pipeline(self) -> List[Dict[str, Any]]:
        """Define research-focused pipeline with API enrichment"""
        steps = await self._define_enhanced_pipeline()
        
        # Add API enrichment step after entity extraction
        api_enrichment_step = {
            'name': 'API Enrichment',
            'tool_class': None,  # Will be handled by integrator
            'tool_id': 'API_ENRICHMENT',
            'operation': 'enrich_entities',
            'use_integration': True,
            'input_source': 'entities',
            'expected_output': 'enriched_entities'
        }
        
        # Insert after entity extraction
        entity_index = next(i for i, step in enumerate(steps) if step['name'] == 'Entity Extraction')
        steps.insert(entity_index + 1, api_enrichment_step)
        
        # Add export step at the end
        export_step = {
            'name': 'Research Export',
            'tool_class': None,  # Will be handled by integrator
            'tool_id': 'RESEARCH_EXPORT',
            'operation': 'export_results',
            'use_integration': True,
            'input_source': 'query_results',
            'expected_output': 'exported_results'
        }
        steps.append(export_step)
        
        return steps
    
    async def _define_stress_test(self) -> List[Dict[str, Any]]:
        """Define stress test with high-load scenarios"""
        # Use enhanced pipeline but with larger test data
        steps = await self._define_enhanced_pipeline()
        
        # Modify parameters for stress testing
        for step in steps:
            step['parameters'] = step.get('parameters', {})
            step['parameters']['stress_test'] = True
        
        return steps
    
    async def _prepare_step_input(self, step: Dict[str, Any], context: Dict[str, Any]) -> Any:
        """Prepare input data for a workflow step"""
        
        input_source = step.get('input_source')
        
        if input_source == 'test_pdf':
            # Return path to test PDF
            return self._get_test_document_path()
        
        elif input_source == 'test_query':
            return step['parameters'].get('query', 'What are the main entities?')
        
        elif input_source in context['data']:
            # Use output from previous step
            return context['data'][input_source]
        
        else:
            # Use test data registry
            return self.test_data_registry.get(input_source, {})
    
    def _get_test_document_path(self) -> str:
        """Get path to test document"""
        test_data_dir = Path(self.config.test_data_path)
        
        # Look for test PDF files
        pdf_files = list(test_data_dir.glob("*.pdf"))
        if pdf_files:
            return str(pdf_files[0])
        
        # Create a simple test file if none exists
        test_file = test_data_dir / "test_document.txt"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(test_file, 'w') as f:
            f.write("""
            This is a test document for workflow testing.
            It contains information about John Smith, who works for Acme Corporation.
            The company is located in New York and specializes in technology solutions.
            Jane Doe is the CEO of the organization.
            They have partnerships with Global Tech Inc and Innovation Labs.
            """)
        
        return str(test_file)
    
    def _calculate_step_quality_score(self, step: Dict[str, Any], result: ToolResult) -> float:
        """Calculate quality score for a workflow step"""
        
        if result.status != "success":
            return 0.0
        
        quality_score = 0.8  # Base score
        
        # Adjust based on step type
        if step['name'] == 'Entity Extraction' and result.data:
            entities = result.data.get('entities', [])
            if entities:
                avg_confidence = sum(e.get('confidence', 0) for e in entities) / len(entities)
                quality_score = avg_confidence
        
        elif step['name'] == 'Relationship Extraction' and result.data:
            relationships = result.data.get('relationships', [])
            if relationships:
                avg_confidence = sum(r.get('confidence', 0) for r in relationships) / len(relationships)
                quality_score = avg_confidence
        
        elif step['name'] == 'PageRank Calculation' and result.data:
            pagerank_scores = result.data.get('pagerank_scores', [])
            if pagerank_scores:
                quality_score = 0.9  # High quality if PageRank completed
        
        return min(1.0, max(0.0, quality_score))
    
    def _calculate_performance_metrics(self, result: WorkflowTestResult, 
                                     context: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate performance metrics for workflow"""
        
        if not result.steps:
            return {}
        
        total_time = result.total_execution_time
        step_times = [step.execution_time for step in result.steps]
        memory_usage = [step.memory_used_mb for step in result.steps]
        
        # Calculate baseline comparison
        baseline_time = self.baseline_metrics.get(result.workflow_type.value, total_time)
        speedup_factor = baseline_time / max(total_time, 0.001)
        
        # Update baseline if this is better
        if total_time < baseline_time:
            self.baseline_metrics[result.workflow_type.value] = total_time
        
        return {
            'total_execution_time': total_time,
            'average_step_time': sum(step_times) / len(step_times),
            'max_step_time': max(step_times),
            'total_memory_used_mb': sum(memory_usage),
            'peak_memory_used_mb': max(memory_usage) if memory_usage else 0,
            'speedup_factor': speedup_factor,
            'throughput_steps_per_second': len(result.steps) / max(total_time, 0.001),
            'performance_grade': self._grade_performance(speedup_factor, total_time)
        }
    
    def _calculate_quality_metrics(self, result: WorkflowTestResult, 
                                 context: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate quality metrics for workflow"""
        
        if not result.steps:
            return {}
        
        quality_scores = [step.quality_score for step in result.steps]
        passed_steps = sum(1 for step in result.steps if step.status == TestStatus.PASSED)
        
        return {
            'overall_quality': sum(quality_scores) / len(quality_scores),
            'min_quality': min(quality_scores),
            'max_quality': max(quality_scores),
            'step_success_rate': passed_steps / len(result.steps),
            'quality_grade': self._grade_quality(sum(quality_scores) / len(quality_scores)),
            'failed_steps': [step.step_name for step in result.steps if step.status == TestStatus.FAILED]
        }
    
    def _grade_performance(self, speedup_factor: float, execution_time: float) -> str:
        """Grade performance based on speedup and execution time"""
        if speedup_factor >= 2.0:
            return "A"
        elif speedup_factor >= 1.5:
            return "B"
        elif speedup_factor >= 1.2:
            return "C"
        elif speedup_factor >= 1.0:
            return "D"
        else:
            return "F"
    
    def _grade_quality(self, quality_score: float) -> str:
        """Grade quality based on average quality score"""
        if quality_score >= 0.9:
            return "A"
        elif quality_score >= 0.8:
            return "B"
        elif quality_score >= 0.7:
            return "C"
        elif quality_score >= 0.6:
            return "D"
        else:
            return "F"
    
    async def _validate_workflow_results(self, result: WorkflowTestResult, 
                                       context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate workflow results meet quality requirements"""
        
        validation = {
            'valid': True,
            'reason': None,
            'checks': {}
        }
        
        # Check if all critical steps passed
        critical_steps = ['PDF Loading', 'Entity Extraction', 'PageRank Calculation']
        failed_critical = [
            step.step_name for step in result.steps 
            if step.step_name in critical_steps and step.status == TestStatus.FAILED
        ]
        
        if failed_critical:
            validation['valid'] = False
            validation['reason'] = f"Critical steps failed: {', '.join(failed_critical)}"
            validation['checks']['critical_steps'] = False
        else:
            validation['checks']['critical_steps'] = True
        
        # Check quality threshold
        if result.quality_metrics:
            overall_quality = result.quality_metrics.get('overall_quality', 0.0)
            if overall_quality < self.config.quality_threshold:
                validation['valid'] = False
                validation['reason'] = f"Quality below threshold: {overall_quality:.2f} < {self.config.quality_threshold}"
                validation['checks']['quality_threshold'] = False
            else:
                validation['checks']['quality_threshold'] = True
        
        # Check performance target
        if result.performance_metrics:
            speedup = result.performance_metrics.get('speedup_factor', 0.0)
            if speedup < self.config.performance_target_speedup:
                # This is a warning, not a failure
                validation['checks']['performance_target'] = False
            else:
                validation['checks']['performance_target'] = True
        
        return validation
    
    async def _initialize_test_data(self):
        """Initialize test data registry"""
        
        test_data_dir = Path(self.config.test_data_path)
        test_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Register available test documents
        pdf_files = list(test_data_dir.glob("*.pdf"))
        text_files = list(test_data_dir.glob("*.txt"))
        
        self.test_data_registry = {
            'pdf_documents': [str(f) for f in pdf_files],
            'text_documents': [str(f) for f in text_files],
            'sample_entities': [
                {'surface_form': 'John Smith', 'entity_type': 'PERSON', 'confidence': 0.9},
                {'surface_form': 'Acme Corporation', 'entity_type': 'ORG', 'confidence': 0.85},
                {'surface_form': 'New York', 'entity_type': 'GPE', 'confidence': 0.8}
            ],
            'sample_relationships': [
                {'source': 'John Smith', 'target': 'Acme Corporation', 'type': 'works_for', 'confidence': 0.8}
            ]
        }
    
    async def _generate_test_report(self, suite_results: Dict[str, Any]):
        """Generate comprehensive test report"""
        
        report_dir = Path("test_results") / f"workflow_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        report_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate JSON report
        json_report_path = report_dir / "test_results.json"
        with open(json_report_path, 'w') as f:
            json.dump(suite_results, f, indent=2, default=str)
        
        # Generate markdown report
        md_report_path = report_dir / "test_report.md"
        await self._generate_markdown_report(suite_results, md_report_path)
        
        logger.info(f"Test reports generated in: {report_dir}")
    
    async def _generate_markdown_report(self, suite_results: Dict[str, Any], output_path: Path):
        """Generate markdown test report"""
        
        report_content = f"""# End-to-End Workflow Test Report

**Test Suite ID**: {suite_results['suite_id']}  
**Start Time**: {suite_results['start_time']}  
**End Time**: {suite_results['end_time']}  
**Total Duration**: {suite_results['summary']['total_execution_time']:.2f} seconds

## Summary

- **Total Workflows**: {suite_results['summary']['total_workflows']}
- **Passed**: {suite_results['summary']['passed_workflows']}
- **Failed**: {suite_results['summary']['failed_workflows']}
- **Success Rate**: {(suite_results['summary']['passed_workflows'] / max(1, suite_results['summary']['total_workflows']) * 100):.1f}%
- **Average Performance Improvement**: {suite_results['summary']['average_performance_improvement']:.2f}x

## Configuration

- **Integration Mode**: {suite_results['configuration']['integration_mode']}
- **Parallel Processing**: {suite_results['configuration']['parallel_processing']}
- **Caching Enabled**: {suite_results['configuration']['caching_enabled']}
- **API Enrichment**: {suite_results['configuration']['api_enrichment']}
- **Timeout**: {suite_results['configuration']['timeout_seconds']} seconds

## Workflow Results

"""
        
        for workflow_name, workflow_result in suite_results['workflow_results'].items():
            if isinstance(workflow_result, dict) and 'status' in workflow_result:
                status_emoji = "✅" if workflow_result.get('status') == 'passed' else "❌"
                
                report_content += f"""### {status_emoji} {workflow_name.replace('_', ' ').title()}

**Status**: {workflow_result.get('status', 'unknown')}  
**Execution Time**: {workflow_result.get('total_execution_time', 0):.2f}s  

"""
                
                if 'performance_metrics' in workflow_result:
                    perf = workflow_result['performance_metrics']
                    report_content += f"""**Performance Metrics**:
- Speedup Factor: {perf.get('speedup_factor', 0):.2f}x
- Performance Grade: {perf.get('performance_grade', 'N/A')}
- Peak Memory: {perf.get('peak_memory_used_mb', 0):.1f}MB

"""
                
                if 'quality_metrics' in workflow_result:
                    quality = workflow_result['quality_metrics']
                    report_content += f"""**Quality Metrics**:
- Overall Quality: {quality.get('overall_quality', 0):.2f}
- Quality Grade: {quality.get('quality_grade', 'N/A')}
- Step Success Rate: {quality.get('step_success_rate', 0):.1%}

"""
                
                if workflow_result.get('error_summary'):
                    report_content += f"**Error**: {workflow_result['error_summary']}\n\n"
        
        report_content += """## Recommendations

Based on the test results, consider the following improvements:

1. **Performance Optimization**: Focus on steps with longest execution times
2. **Quality Improvement**: Address any steps with quality scores below 0.8
3. **Error Handling**: Investigate and fix any failed critical steps
4. **Resource Management**: Optimize memory usage for steps with high memory consumption

---

*Report generated by End-to-End Workflow Tester*
"""
        
        with open(output_path, 'w') as f:
            f.write(report_content)
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / (1024 * 1024)
        except:
            return 0.0
    
    async def cleanup(self):
        """Clean up testing resources"""
        logger.info("Cleaning up workflow testing resources...")
        
        if self.integrator:
            await self.integrator.cleanup()
        
        # Clear test results to free memory
        self.test_results.clear()
        self.test_data_registry.clear()


# Factory functions for common testing scenarios
def create_performance_tester() -> EndToEndWorkflowTester:
    """Create tester optimized for performance testing"""
    config = TestConfiguration(
        workflow_type=WorkflowType.ENHANCED_PIPELINE,
        integration_mode=IntegrationMode.PERFORMANCE,
        parallel_processing=True,
        enable_caching=True,
        performance_target_speedup=1.5
    )
    return EndToEndWorkflowTester(config)


def create_research_tester() -> EndToEndWorkflowTester:
    """Create tester for research workflows"""
    config = TestConfiguration(
        workflow_type=WorkflowType.RESEARCH_PIPELINE,
        integration_mode=IntegrationMode.RESEARCH,
        enable_api_enrichment=True,
        timeout_seconds=600  # Longer timeout for API calls
    )
    return EndToEndWorkflowTester(config)


# Example usage
async def run_test_suite():
    """Run comprehensive test suite"""
    
    # Create performance-focused tester
    tester = create_performance_tester()
    
    try:
        # Initialize
        success = await tester.initialize()
        if not success:
            print("Tester initialization failed")
            return
        
        # Run comprehensive test suite
        results = await tester.run_comprehensive_test_suite()
        
        print(f"Test Suite Results:")
        print(f"  Workflows: {results['summary']['passed_workflows']}/{results['summary']['total_workflows']} passed")
        print(f"  Duration: {results['summary']['total_execution_time']:.2f}s")
        print(f"  Performance: {results['summary']['average_performance_improvement']:.2f}x improvement")
        
        return results
        
    finally:
        await tester.cleanup()


# CLI entry point for direct execution
if __name__ == "__main__":
    import sys
    
    # Check if we're already in an async context (like pytest)
    try:
        # Try to get the current event loop
        loop = asyncio.get_running_loop()
        print("Warning: Already in an async context. Use 'await run_test_suite()' instead.")
        sys.exit(1)
    except RuntimeError:
        # No event loop running, safe to use asyncio.run()
        asyncio.run(run_test_suite())