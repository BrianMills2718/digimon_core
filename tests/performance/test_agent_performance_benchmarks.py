#!/usr/bin/env python3
"""
Agent Performance Benchmarking Suite

Comprehensive performance testing for the agent architecture using realistic document sets
and workloads to validate system performance under various conditions.
"""

import asyncio
import logging
import os
import time
import json
import statistics
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import tempfile
import psutil
import gc

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Test imports with fallback handling
try:
    from src.core.service_manager import ServiceManager
    from src.orchestration.memory import AgentMemory
    from src.orchestration.llm_reasoning import LLMReasoningEngine, ReasoningType
    from src.orchestration.communication import MessageBus
    from src.orchestration.agents.document_agent import DocumentAgent
    from src.orchestration.mcp_adapter import MCPToolAdapter
    from src.orchestration.base import Task, Result
    from src.tools.enhanced_mcp_tools import EnhancedMCPTools
    IMPORTS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Some imports failed: {e}")
    IMPORTS_AVAILABLE = False


@dataclass
class PerformanceMetrics:
    """Container for performance measurement results."""
    execution_time: float
    memory_peak_mb: float
    memory_delta_mb: float
    cpu_percent: float
    success_rate: float
    throughput_docs_per_second: float
    latency_p50: float
    latency_p95: float
    latency_p99: float
    error_count: int
    total_operations: int


@dataclass
class BenchmarkResult:
    """Container for benchmark test results."""
    test_name: str
    metrics: PerformanceMetrics
    details: Dict[str, Any]
    timestamp: datetime
    configuration: Dict[str, Any]


class RealWorldDocumentGenerator:
    """Generate realistic document sets for performance testing."""
    
    @staticmethod
    def create_technology_documents(count: int = 10) -> List[Dict[str, Any]]:
        """Create technology industry documents."""
        base_templates = [
            {
                "title": "AI Partnership Announcement",
                "content": """
                {company1} announced a strategic partnership with {company2} to develop 
                artificial intelligence solutions for {industry}. The collaboration will 
                be led by {person1}, Chief Technology Officer at {company1}, and 
                {person2}, Director of AI Research at {company2}. The partnership aims 
                to create machine learning models that can {capability} and improve 
                {outcome}. The project will be headquartered in {location} with additional 
                research facilities in {location2}. Initial funding of ${amount} million 
                has been secured from {investor}. The companies expect to deploy the 
                first prototype by {timeline}.
                """,
                "domain": "technology_partnerships"
            },
            {
                "title": "Research Breakthrough Publication",
                "content": """
                Researchers at {university} have published groundbreaking research on 
                {research_topic} in the journal {journal}. The study, led by 
                Professor {researcher}, demonstrates significant improvements in {metric}
                compared to existing approaches. The research team included {person1} 
                from {company1} and {person2} from {institute}. The work was funded by 
                a ${amount} grant from {funding_agency}. The findings have implications 
                for {application_area} and could lead to {potential_impact}. The paper 
                has already received {citations} citations since publication.
                """,
                "domain": "academic_research"
            },
            {
                "title": "Corporate Acquisition News",
                "content": """
                {acquiring_company} has completed its acquisition of {target_company} 
                for ${amount} billion. The deal, announced in {month}, brings together 
                {acquiring_company}'s expertise in {domain1} with {target_company}'s 
                leadership in {domain2}. {ceo1}, CEO of {acquiring_company}, stated 
                that the acquisition will accelerate innovation in {technology_area}. 
                {target_company}'s founder {ceo2} will join the executive team. The 
                combined company will have operations in {location1}, {location2}, 
                and {location3}, employing over {employee_count} people.
                """,
                "domain": "business_mergers"
            }
        ]
        
        # Entity pools for realistic variation
        companies = ["Microsoft", "Google", "Apple", "Amazon", "Tesla", "Meta", "OpenAI", "Anthropic", "NVIDIA", "IBM"]
        universities = ["Stanford University", "MIT", "Harvard University", "UC Berkeley", "CMU", "Oxford University"]
        people = ["Dr. Sarah Johnson", "Michael Chen", "Prof. David Rodriguez", "Lisa Wang", "Dr. Robert Kim", "Anna Martinez"]
        locations = ["San Francisco", "Seattle", "Boston", "Austin", "London", "Tokyo", "Singapore", "Toronto"]
        industries = ["healthcare", "automotive", "finance", "education", "manufacturing", "retail"]
        
        documents = []
        for i in range(count):
            template = base_templates[i % len(base_templates)]
            
            # Fill template with realistic entities
            content = template["content"].format(
                company1=companies[i % len(companies)],
                company2=companies[(i + 1) % len(companies)],
                university=universities[i % len(universities)],
                person1=people[i % len(people)],
                person2=people[(i + 1) % len(people)],
                researcher=people[(i + 2) % len(people)],
                location=locations[i % len(locations)],
                location1=locations[i % len(locations)],
                location2=locations[(i + 1) % len(locations)],
                location3=locations[(i + 2) % len(locations)],
                industry=industries[i % len(industries)],
                amount=str(50 + (i * 13) % 500),  # Realistic funding amounts
                timeline="Q" + str((i % 4) + 1) + " 2024",
                capability="analyze large datasets" if i % 2 == 0 else "optimize complex processes",
                outcome="operational efficiency" if i % 2 == 0 else "cost reduction",
                investor="VentureCapital Partners" if i % 2 == 0 else "Innovation Fund",
                research_topic="quantum computing" if i % 3 == 0 else "neural networks" if i % 3 == 1 else "robotics",
                journal="Nature" if i % 2 == 0 else "Science",
                metric="accuracy by 35%" if i % 2 == 0 else "processing speed by 50%",
                institute="Research Institute" if i % 2 == 0 else "Technology Center",
                funding_agency="National Science Foundation" if i % 2 == 0 else "Department of Energy",
                application_area="autonomous vehicles" if i % 3 == 0 else "medical diagnosis" if i % 3 == 1 else "financial modeling",
                potential_impact="improved safety" if i % 2 == 0 else "reduced costs",
                citations=str(15 + (i * 7) % 100),
                acquiring_company=companies[i % len(companies)],
                target_company=companies[(i + 3) % len(companies)],
                month="January" if i % 2 == 0 else "March",
                domain1="cloud computing" if i % 2 == 0 else "artificial intelligence",
                domain2="data analytics" if i % 2 == 0 else "machine learning",
                technology_area="edge computing" if i % 2 == 0 else "quantum algorithms",
                ceo1=people[i % len(people)],
                ceo2=people[(i + 1) % len(people)],
                employee_count=str(1000 + (i * 250) % 5000)
            )
            
            documents.append({
                "id": f"realistic_doc_{i:03d}",
                "title": f"{template['title']} {i+1}",
                "content": content.strip(),
                "domain": template["domain"],
                "word_count": len(content.split()),
                "complexity": "high" if len(content.split()) > 150 else "medium" if len(content.split()) > 100 else "low",
                "expected_entities": 8 + (i % 5),  # Realistic entity counts
                "expected_relationships": 3 + (i % 4)
            })
        
        return documents
    
    @staticmethod
    def create_variable_size_documents() -> List[Dict[str, Any]]:
        """Create documents of varying sizes for scale testing."""
        base_content = """
        Artificial intelligence research has made significant progress in recent years.
        Companies like Microsoft, Google, and OpenAI are leading development efforts.
        Universities such as Stanford and MIT continue to publish groundbreaking research.
        The collaboration between industry and academia has accelerated innovation.
        """
        
        documents = []
        sizes = [
            ("small", 1, 50),      # ~50 words
            ("medium", 3, 200),    # ~200 words  
            ("large", 10, 500),    # ~500 words
            ("xlarge", 25, 1000),  # ~1000 words
            ("xxlarge", 50, 2000)  # ~2000 words
        ]
        
        for size_name, multiplier, target_words in sizes:
            content = (base_content + " ") * multiplier
            content = content.strip()
            
            # Add some size-specific entities
            if multiplier >= 10:
                content += " Additional partnerships include collaborations with Apple, Amazon, Tesla, and NVIDIA. "
                content += "Research teams are located in San Francisco, Seattle, Boston, and Austin. "
                content += "Key researchers include Dr. Sarah Johnson, Prof. Michael Chen, and Dr. Lisa Wang."
            
            documents.append({
                "id": f"size_test_{size_name}",
                "title": f"Size Test Document - {size_name.title()}",
                "content": content,
                "domain": "technology",
                "word_count": len(content.split()),
                "size_category": size_name,
                "complexity": "high" if multiplier >= 25 else "medium" if multiplier >= 10 else "low"
            })
        
        return documents


class PerformanceMonitor:
    """Monitor system performance during tests."""
    
    def __init__(self):
        self.process = psutil.Process()
        self.start_memory = 0
        self.peak_memory = 0
        self.start_time = 0
        self.measurements = []
    
    def start_monitoring(self):
        """Start performance monitoring."""
        self.start_time = time.time()
        self.start_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        self.peak_memory = self.start_memory
        self.measurements = []
        gc.collect()  # Clean up before measurement
    
    def sample(self):
        """Take a performance sample."""
        current_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        cpu_percent = self.process.cpu_percent()
        
        self.peak_memory = max(self.peak_memory, current_memory)
        
        self.measurements.append({
            "timestamp": time.time(),
            "memory_mb": current_memory,
            "cpu_percent": cpu_percent
        })
    
    def get_metrics(self) -> Dict[str, float]:
        """Get performance metrics."""
        if not self.measurements:
            return {
                "peak_memory_mb": self.peak_memory,
                "memory_delta_mb": 0,
                "avg_cpu_percent": 0,
                "execution_time": time.time() - self.start_time
            }
        
        current_memory = self.measurements[-1]["memory_mb"]
        avg_cpu = statistics.mean(m["cpu_percent"] for m in self.measurements)
        
        return {
            "peak_memory_mb": self.peak_memory,
            "memory_delta_mb": current_memory - self.start_memory,
            "avg_cpu_percent": avg_cpu,
            "execution_time": time.time() - self.start_time
        }


class AgentPerformanceBenchmarks:
    """Comprehensive performance benchmarking suite for agent architecture."""
    
    def __init__(self):
        self.results = []
        self.monitor = PerformanceMonitor()
        
    async def setup_test_environment(self) -> Dict[str, Any]:
        """Set up performance test environment."""
        if not IMPORTS_AVAILABLE:
            raise RuntimeError("Required modules not available")
        
        env = {}
        
        # Initialize core services
        env['service_manager'] = ServiceManager()
        await env['service_manager'].initialize()
        
        # Initialize message bus
        env['message_bus'] = MessageBus()
        
        # Initialize enhanced tools
        env['enhanced_tools'] = EnhancedMCPTools(
            service_manager=env['service_manager'],
            agent_id="benchmark_tools",
            memory_config={"enable_memory": True, "max_memories": 2000},
            reasoning_config={"enable_reasoning": True, "confidence_threshold": 0.7},
            communication_config={"enable_broadcast": True},
            message_bus=env['message_bus']
        )
        
        # Create test agents
        mcp_adapter = MCPToolAdapter()
        
        env['agents'] = []
        for i in range(3):  # Create 3 agents for collaborative testing
            agent = DocumentAgent(
                mcp_adapter=mcp_adapter,
                agent_id=f"benchmark_agent_{i}",
                memory_config={"enable_memory": True, "max_memories": 1000},
                reasoning_config={"enable_reasoning": True, "confidence_threshold": 0.7},
                communication_config={"enable_broadcast": True},
                message_bus=env['message_bus']
            )
            env['agents'].append(agent)
        
        return env
    
    async def benchmark_single_document_processing(self, env: Dict[str, Any]) -> BenchmarkResult:
        """Benchmark single document processing performance."""
        logger.info("📄 Benchmarking single document processing...")
        
        # Create realistic test document
        documents = RealWorldDocumentGenerator.create_technology_documents(1)
        doc = documents[0]
        
        agent = env['agents'][0]
        execution_times = []
        success_count = 0
        
        # Run multiple iterations for statistical significance
        iterations = 10
        
        for i in range(iterations):
            self.monitor.start_monitoring()
            
            task = Task(
                task_type="document_processing",
                parameters={
                    "text": doc["content"],
                    "domain": doc["domain"],
                    "document_id": f"{doc['id']}_iter_{i}"
                },
                context={"benchmark": "single_document", "iteration": i}
            )
            
            start_time = time.time()
            result = await agent.execute(task)
            execution_time = time.time() - start_time
            
            execution_times.append(execution_time)
            if result.success:
                success_count += 1
            
            self.monitor.sample()
            
            # Brief pause between iterations
            await asyncio.sleep(0.1)
        
        perf_metrics = self.monitor.get_metrics()
        
        metrics = PerformanceMetrics(
            execution_time=perf_metrics["execution_time"],
            memory_peak_mb=perf_metrics["peak_memory_mb"],
            memory_delta_mb=perf_metrics["memory_delta_mb"],
            cpu_percent=perf_metrics["avg_cpu_percent"],
            success_rate=success_count / iterations,
            throughput_docs_per_second=iterations / perf_metrics["execution_time"],
            latency_p50=statistics.median(execution_times),
            latency_p95=statistics.quantiles(execution_times, n=20)[18] if len(execution_times) >= 20 else max(execution_times),
            latency_p99=statistics.quantiles(execution_times, n=100)[98] if len(execution_times) >= 100 else max(execution_times),
            error_count=iterations - success_count,
            total_operations=iterations
        )
        
        return BenchmarkResult(
            test_name="single_document_processing",
            metrics=metrics,
            details={
                "document_word_count": doc["word_count"],
                "document_complexity": doc["complexity"],
                "iterations": iterations,
                "execution_times": execution_times
            },
            timestamp=datetime.now(),
            configuration={
                "memory_enabled": True,
                "reasoning_enabled": True,
                "communication_enabled": True
            }
        )
    
    async def benchmark_batch_processing(self, env: Dict[str, Any]) -> BenchmarkResult:
        """Benchmark batch document processing performance."""
        logger.info("📚 Benchmarking batch document processing...")
        
        # Create batch of realistic documents
        documents = RealWorldDocumentGenerator.create_technology_documents(20)
        agent = env['agents'][0]
        
        self.monitor.start_monitoring()
        
        execution_times = []
        success_count = 0
        total_entities = 0
        
        start_time = time.time()
        
        for i, doc in enumerate(documents):
            task = Task(
                task_type="document_processing",
                parameters={
                    "text": doc["content"],
                    "domain": doc["domain"],
                    "document_id": doc["id"]
                },
                context={"benchmark": "batch_processing", "doc_index": i}
            )
            
            doc_start = time.time()
            result = await agent.execute(task)
            doc_time = time.time() - doc_start
            
            execution_times.append(doc_time)
            
            if result.success:
                success_count += 1
                entities = result.data.get("entities", []) if result.data else []
                total_entities += len(entities)
            
            self.monitor.sample()
            
            # Small pause to prevent overwhelming
            if i % 5 == 0:
                await asyncio.sleep(0.1)
        
        total_time = time.time() - start_time
        perf_metrics = self.monitor.get_metrics()
        
        metrics = PerformanceMetrics(
            execution_time=total_time,
            memory_peak_mb=perf_metrics["peak_memory_mb"],
            memory_delta_mb=perf_metrics["memory_delta_mb"], 
            cpu_percent=perf_metrics["avg_cpu_percent"],
            success_rate=success_count / len(documents),
            throughput_docs_per_second=len(documents) / total_time,
            latency_p50=statistics.median(execution_times),
            latency_p95=statistics.quantiles(execution_times, n=20)[18] if len(execution_times) >= 20 else max(execution_times),
            latency_p99=statistics.quantiles(execution_times, n=100)[98] if len(execution_times) >= 100 else max(execution_times),
            error_count=len(documents) - success_count,
            total_operations=len(documents)
        )
        
        return BenchmarkResult(
            test_name="batch_processing",
            metrics=metrics,
            details={
                "total_documents": len(documents),
                "total_entities_extracted": total_entities,
                "avg_entities_per_doc": total_entities / success_count if success_count > 0 else 0,
                "execution_times": execution_times,
                "total_word_count": sum(doc["word_count"] for doc in documents)
            },
            timestamp=datetime.now(),
            configuration={
                "batch_size": len(documents),
                "memory_enabled": True,
                "reasoning_enabled": True
            }
        )
    
    async def benchmark_variable_document_sizes(self, env: Dict[str, Any]) -> BenchmarkResult:
        """Benchmark processing performance across different document sizes."""
        logger.info("📏 Benchmarking variable document sizes...")
        
        documents = RealWorldDocumentGenerator.create_variable_size_documents()
        agent = env['agents'][0]
        
        self.monitor.start_monitoring()
        
        size_results = {}
        
        for doc in documents:
            size_category = doc["size_category"]
            
            task = Task(
                task_type="document_processing",
                parameters={
                    "text": doc["content"],
                    "domain": doc["domain"],
                    "document_id": doc["id"]
                },
                context={"benchmark": "size_scaling", "size": size_category}
            )
            
            start_time = time.time()
            result = await agent.execute(task)
            execution_time = time.time() - start_time
            
            size_results[size_category] = {
                "word_count": doc["word_count"],
                "execution_time": execution_time,
                "success": result.success,
                "entities_extracted": len(result.data.get("entities", [])) if result.success and result.data else 0,
                "processing_rate": doc["word_count"] / execution_time if execution_time > 0 else 0
            }
            
            self.monitor.sample()
            await asyncio.sleep(0.1)
        
        perf_metrics = self.monitor.get_metrics()
        
        # Calculate aggregate metrics
        all_times = [r["execution_time"] for r in size_results.values()]
        success_count = sum(1 for r in size_results.values() if r["success"])
        
        metrics = PerformanceMetrics(
            execution_time=perf_metrics["execution_time"],
            memory_peak_mb=perf_metrics["peak_memory_mb"],
            memory_delta_mb=perf_metrics["memory_delta_mb"],
            cpu_percent=perf_metrics["avg_cpu_percent"],
            success_rate=success_count / len(documents),
            throughput_docs_per_second=len(documents) / perf_metrics["execution_time"],
            latency_p50=statistics.median(all_times),
            latency_p95=max(all_times),  # With small sample, use max
            latency_p99=max(all_times),
            error_count=len(documents) - success_count,
            total_operations=len(documents)
        )
        
        return BenchmarkResult(
            test_name="variable_document_sizes",
            metrics=metrics,
            details={
                "size_results": size_results,
                "scaling_analysis": self._analyze_scaling_performance(size_results)
            },
            timestamp=datetime.now(),
            configuration={
                "document_sizes_tested": list(size_results.keys())
            }
        )
    
    def _analyze_scaling_performance(self, size_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze how performance scales with document size."""
        sizes = ["small", "medium", "large", "xlarge", "xxlarge"]
        
        word_counts = []
        exec_times = []
        processing_rates = []
        
        for size in sizes:
            if size in size_results and size_results[size]["success"]:
                word_counts.append(size_results[size]["word_count"])
                exec_times.append(size_results[size]["execution_time"])
                processing_rates.append(size_results[size]["processing_rate"])
        
        if len(word_counts) < 2:
            return {"analysis": "Insufficient data for scaling analysis"}
        
        # Calculate scaling factors
        scaling_factor = exec_times[-1] / exec_times[0] if exec_times[0] > 0 else 0
        size_factor = word_counts[-1] / word_counts[0] if word_counts[0] > 0 else 0
        
        return {
            "execution_time_scaling": scaling_factor,
            "document_size_scaling": size_factor,
            "scaling_efficiency": size_factor / scaling_factor if scaling_factor > 0 else 0,
            "avg_processing_rate": statistics.mean(processing_rates) if processing_rates else 0,
            "processing_rate_stability": statistics.stdev(processing_rates) / statistics.mean(processing_rates) if len(processing_rates) > 1 and statistics.mean(processing_rates) > 0 else 0
        }
    
    async def benchmark_collaborative_processing(self, env: Dict[str, Any]) -> BenchmarkResult:
        """Benchmark collaborative processing between multiple agents."""
        logger.info("🤝 Benchmarking collaborative processing...")
        
        documents = RealWorldDocumentGenerator.create_technology_documents(10)
        agents = env['agents'][:3]  # Use 3 agents for collaboration
        
        self.monitor.start_monitoring()
        
        # Test sequential processing first (baseline)
        sequential_start = time.time()
        sequential_results = []
        
        for doc in documents[:5]:  # Process 5 docs sequentially
            task = Task(
                task_type="document_processing",
                parameters={
                    "text": doc["content"],
                    "domain": doc["domain"],
                    "document_id": f"{doc['id']}_sequential"
                },
                context={"benchmark": "sequential_baseline"}
            )
            
            result = await agents[0].execute(task)
            sequential_results.append(result.success)
        
        sequential_time = time.time() - sequential_start
        
        # Test parallel processing
        parallel_start = time.time()
        
        async def process_document(agent, doc):
            task = Task(
                task_type="document_processing", 
                parameters={
                    "text": doc["content"],
                    "domain": doc["domain"],
                    "document_id": f"{doc['id']}_parallel"
                },
                context={"benchmark": "parallel_collaborative"}
            )
            return await agent.execute(task)
        
        # Distribute documents across agents
        parallel_tasks = []
        for i, doc in enumerate(documents[5:]):  # Process remaining 5 docs in parallel
            agent = agents[i % len(agents)]
            parallel_tasks.append(process_document(agent, doc))
        
        parallel_results = await asyncio.gather(*parallel_tasks, return_exceptions=True)
        parallel_time = time.time() - parallel_start
        
        perf_metrics = self.monitor.get_metrics()
        
        # Analyze results
        sequential_success = sum(sequential_results)
        parallel_success = sum(1 for r in parallel_results if isinstance(r, Result) and r.success)
        
        speedup_factor = sequential_time / parallel_time if parallel_time > 0 else 0
        
        metrics = PerformanceMetrics(
            execution_time=perf_metrics["execution_time"],
            memory_peak_mb=perf_metrics["peak_memory_mb"],
            memory_delta_mb=perf_metrics["memory_delta_mb"],
            cpu_percent=perf_metrics["avg_cpu_percent"],
            success_rate=(sequential_success + parallel_success) / 10,  # Total 10 documents
            throughput_docs_per_second=10 / perf_metrics["execution_time"],
            latency_p50=parallel_time / len(parallel_tasks) if parallel_tasks else 0,
            latency_p95=parallel_time / len(parallel_tasks) if parallel_tasks else 0,
            latency_p99=parallel_time / len(parallel_tasks) if parallel_tasks else 0,
            error_count=5 - sequential_success + len(parallel_tasks) - parallel_success,
            total_operations=10
        )
        
        return BenchmarkResult(
            test_name="collaborative_processing",
            metrics=metrics,
            details={
                "sequential_time": sequential_time,
                "parallel_time": parallel_time,
                "speedup_factor": speedup_factor,
                "sequential_success_rate": sequential_success / 5,
                "parallel_success_rate": parallel_success / len(parallel_tasks) if parallel_tasks else 0,
                "agents_used": len(agents),
                "collaboration_efficiency": speedup_factor / len(agents) if len(agents) > 0 else 0
            },
            timestamp=datetime.now(),
            configuration={
                "collaborative_agents": len(agents),
                "parallel_document_count": len(parallel_tasks)
            }
        )
    
    async def benchmark_memory_performance(self, env: Dict[str, Any]) -> BenchmarkResult:
        """Benchmark memory system performance and learning effects."""
        logger.info("🧠 Benchmarking memory performance...")
        
        agent = env['agents'][0]
        documents = RealWorldDocumentGenerator.create_technology_documents(15)
        
        self.monitor.start_monitoring()
        
        # Phase 1: Initial processing (cold memory)
        cold_times = []
        cold_success = 0
        
        for doc in documents[:5]:
            task = Task(
                task_type="document_processing",
                parameters={
                    "text": doc["content"],
                    "domain": doc["domain"],
                    "document_id": f"{doc['id']}_cold"
                },
                context={"benchmark": "memory_cold", "learning_phase": "initial"}
            )
            
            start_time = time.time()
            result = await agent.execute(task)
            execution_time = time.time() - start_time
            
            cold_times.append(execution_time)
            if result.success:
                cold_success += 1
            
            self.monitor.sample()
        
        # Allow memory consolidation
        await asyncio.sleep(1)
        
        # Phase 2: Similar processing (warm memory)
        warm_times = []
        warm_success = 0
        
        for doc in documents[5:10]:
            task = Task(
                task_type="document_processing",
                parameters={
                    "text": doc["content"],
                    "domain": doc["domain"],  # Same domain for memory benefits
                    "document_id": f"{doc['id']}_warm"
                },
                context={"benchmark": "memory_warm", "learning_phase": "learned"}
            )
            
            start_time = time.time()
            result = await agent.execute(task)
            execution_time = time.time() - start_time
            
            warm_times.append(execution_time)
            if result.success:
                warm_success += 1
            
            self.monitor.sample()
        
        # Phase 3: Different domain processing (transfer learning test)
        transfer_times = []
        transfer_success = 0
        
        # Modify remaining documents to different domain
        for doc in documents[10:]:
            modified_doc = doc.copy()
            modified_doc["domain"] = "academic_research"  # Different domain
            
            task = Task(
                task_type="document_processing",
                parameters={
                    "text": modified_doc["content"],
                    "domain": modified_doc["domain"],
                    "document_id": f"{modified_doc['id']}_transfer"
                },
                context={"benchmark": "memory_transfer", "learning_phase": "transfer"}
            )
            
            start_time = time.time()
            result = await agent.execute(task)
            execution_time = time.time() - start_time
            
            transfer_times.append(execution_time)
            if result.success:
                transfer_success += 1
            
            self.monitor.sample()
        
        perf_metrics = self.monitor.get_metrics()
        
        # Analyze memory performance
        cold_avg = statistics.mean(cold_times) if cold_times else 0
        warm_avg = statistics.mean(warm_times) if warm_times else 0
        transfer_avg = statistics.mean(transfer_times) if transfer_times else 0
        
        learning_improvement = (cold_avg - warm_avg) / cold_avg if cold_avg > 0 else 0
        transfer_penalty = (transfer_avg - warm_avg) / warm_avg if warm_avg > 0 else 0
        
        all_times = cold_times + warm_times + transfer_times
        total_success = cold_success + warm_success + transfer_success
        
        metrics = PerformanceMetrics(
            execution_time=perf_metrics["execution_time"],
            memory_peak_mb=perf_metrics["peak_memory_mb"],
            memory_delta_mb=perf_metrics["memory_delta_mb"],
            cpu_percent=perf_metrics["avg_cpu_percent"],
            success_rate=total_success / len(documents),
            throughput_docs_per_second=len(documents) / perf_metrics["execution_time"],
            latency_p50=statistics.median(all_times),
            latency_p95=statistics.quantiles(all_times, n=20)[18] if len(all_times) >= 20 else max(all_times),
            latency_p99=statistics.quantiles(all_times, n=100)[98] if len(all_times) >= 100 else max(all_times),
            error_count=len(documents) - total_success,
            total_operations=len(documents)
        )
        
        return BenchmarkResult(
            test_name="memory_performance",
            metrics=metrics,
            details={
                "cold_avg_time": cold_avg,
                "warm_avg_time": warm_avg,
                "transfer_avg_time": transfer_avg,
                "learning_improvement_pct": learning_improvement * 100,
                "transfer_penalty_pct": transfer_penalty * 100,
                "cold_success_rate": cold_success / 5,
                "warm_success_rate": warm_success / 5,
                "transfer_success_rate": transfer_success / len(transfer_times) if transfer_times else 0,
                "memory_effectiveness": max(0, learning_improvement)
            },
            timestamp=datetime.now(),
            configuration={
                "memory_learning_enabled": True,
                "phases_tested": ["cold", "warm", "transfer"]
            }
        )
    
    async def benchmark_resource_efficiency(self, env: Dict[str, Any]) -> BenchmarkResult:
        """Benchmark resource efficiency and system limits."""
        logger.info("⚡ Benchmarking resource efficiency...")
        
        agent = env['agents'][0]
        
        # Create documents of increasing complexity
        base_doc = """
        Microsoft Corporation announced a strategic partnership with Stanford University 
        to develop AI-powered healthcare solutions. The collaboration involves researchers 
        from both organizations working on machine learning algorithms for medical diagnosis.
        """
        
        complexity_levels = []
        for multiplier in [1, 2, 5, 10, 20]:
            content = (base_doc + " ") * multiplier
            complexity_levels.append({
                "id": f"complexity_{multiplier}x",
                "content": content,
                "multiplier": multiplier,
                "word_count": len(content.split())
            })
        
        self.monitor.start_monitoring()
        
        efficiency_results = []
        
        for doc in complexity_levels:
            # Measure resource usage for this complexity level
            gc.collect()  # Clean up before measurement
            
            task = Task(
                task_type="document_processing",
                parameters={
                    "text": doc["content"],
                    "domain": "technology",
                    "document_id": doc["id"]
                },
                context={"benchmark": "resource_efficiency", "complexity": doc["multiplier"]}
            )
            
            # Take memory snapshot before
            pre_memory = self.process.memory_info().rss / 1024 / 1024
            
            start_time = time.time()
            result = await agent.execute(task)
            execution_time = time.time() - start_time
            
            # Take memory snapshot after
            post_memory = self.process.memory_info().rss / 1024 / 1024
            memory_used = post_memory - pre_memory
            
            efficiency_results.append({
                "complexity_multiplier": doc["multiplier"],
                "word_count": doc["word_count"],
                "execution_time": execution_time,
                "memory_used_mb": memory_used,
                "success": result.success,
                "entities_extracted": len(result.data.get("entities", [])) if result.success and result.data else 0,
                "efficiency_score": doc["word_count"] / (execution_time * max(1, memory_used)) if execution_time > 0 and memory_used > 0 else 0
            })
            
            self.monitor.sample()
            
            # Clean up between tests
            gc.collect()
            await asyncio.sleep(0.2)
        
        perf_metrics = self.monitor.get_metrics()
        
        # Analyze efficiency trends
        exec_times = [r["execution_time"] for r in efficiency_results if r["success"]]
        memory_usage = [r["memory_used_mb"] for r in efficiency_results if r["success"]]
        efficiency_scores = [r["efficiency_score"] for r in efficiency_results if r["success"]]
        
        success_count = sum(1 for r in efficiency_results if r["success"])
        
        metrics = PerformanceMetrics(
            execution_time=perf_metrics["execution_time"],
            memory_peak_mb=perf_metrics["peak_memory_mb"],
            memory_delta_mb=perf_metrics["memory_delta_mb"],
            cpu_percent=perf_metrics["avg_cpu_percent"],
            success_rate=success_count / len(complexity_levels),
            throughput_docs_per_second=len(complexity_levels) / perf_metrics["execution_time"],
            latency_p50=statistics.median(exec_times) if exec_times else 0,
            latency_p95=max(exec_times) if exec_times else 0,
            latency_p99=max(exec_times) if exec_times else 0,
            error_count=len(complexity_levels) - success_count,
            total_operations=len(complexity_levels)
        )
        
        return BenchmarkResult(
            test_name="resource_efficiency",
            metrics=metrics,
            details={
                "complexity_results": efficiency_results,
                "avg_efficiency_score": statistics.mean(efficiency_scores) if efficiency_scores else 0,
                "memory_scaling": memory_usage[-1] / memory_usage[0] if len(memory_usage) >= 2 and memory_usage[0] > 0 else 0,
                "time_scaling": exec_times[-1] / exec_times[0] if len(exec_times) >= 2 and exec_times[0] > 0 else 0,
                "max_complexity_processed": max(r["complexity_multiplier"] for r in efficiency_results if r["success"]) if success_count > 0 else 0
            },
            timestamp=datetime.now(),
            configuration={
                "complexity_levels_tested": [r["complexity_multiplier"] for r in efficiency_results]
            }
        )
    
    async def run_all_benchmarks(self) -> List[BenchmarkResult]:
        """Run all performance benchmarks."""
        logger.info("🚀 Starting Comprehensive Agent Performance Benchmarks")
        logger.info("=" * 80)
        
        if not IMPORTS_AVAILABLE:
            logger.error("❌ Required modules not available")
            return []
        
        try:
            # Set up test environment
            env = await self.setup_test_environment()
            
            # Run all benchmarks
            benchmarks = [
                ("Single Document Processing", self.benchmark_single_document_processing),
                ("Batch Processing", self.benchmark_batch_processing),
                ("Variable Document Sizes", self.benchmark_variable_document_sizes),
                ("Collaborative Processing", self.benchmark_collaborative_processing),
                ("Memory Performance", self.benchmark_memory_performance),
                ("Resource Efficiency", self.benchmark_resource_efficiency)
            ]
            
            results = []
            
            for name, benchmark_func in benchmarks:
                logger.info(f"\n🔬 Running {name} benchmark...")
                try:
                    result = await benchmark_func(env)
                    results.append(result)
                    logger.info(f"✅ {name} completed successfully")
                except Exception as e:
                    logger.error(f"❌ {name} failed: {e}")
                    # Continue with other benchmarks
            
            # Generate performance report
            self._generate_performance_report(results)
            
            return results
        
        except Exception as e:
            logger.error(f"❌ Benchmark execution failed: {e}")
            return []
        
        finally:
            # Cleanup
            if 'env' in locals() and 'message_bus' in env:
                await env['message_bus'].cleanup()
    
    def _generate_performance_report(self, results: List[BenchmarkResult]):
        """Generate comprehensive performance report."""
        logger.info("\n" + "=" * 80)
        logger.info("📊 AGENT PERFORMANCE BENCHMARK REPORT")
        logger.info("=" * 80)
        
        if not results:
            logger.info("❌ No benchmark results available")
            return
        
        # Summary table
        logger.info("\n📈 PERFORMANCE SUMMARY")
        logger.info("-" * 50)
        logger.info(f"{'Benchmark':<25} {'Success%':<10} {'Latency':<12} {'Throughput':<15} {'Memory':<10}")
        logger.info("-" * 50)
        
        for result in results:
            m = result.metrics
            logger.info(f"{result.test_name:<25} {m.success_rate*100:>6.1f}%    {m.latency_p50:>8.3f}s    {m.throughput_docs_per_second:>10.2f} docs/s  {m.memory_peak_mb:>6.1f}MB")
        
        # Detailed analysis
        logger.info("\n🔍 DETAILED ANALYSIS")
        logger.info("-" * 50)
        
        for result in results:
            logger.info(f"\n{result.test_name.upper().replace('_', ' ')}:")
            m = result.metrics
            
            logger.info(f"  Success Rate: {m.success_rate*100:.1f}%")
            logger.info(f"  Latency P50/P95/P99: {m.latency_p50:.3f}s / {m.latency_p95:.3f}s / {m.latency_p99:.3f}s")
            logger.info(f"  Throughput: {m.throughput_docs_per_second:.2f} documents/second")
            logger.info(f"  Memory Peak: {m.memory_peak_mb:.1f}MB")
            logger.info(f"  CPU Usage: {m.cpu_percent:.1f}%")
            
            # Test-specific insights
            details = result.details
            if result.test_name == "memory_performance":
                improvement = details.get("learning_improvement_pct", 0)
                logger.info(f"  Learning Improvement: {improvement:.1f}%")
                logger.info(f"  Memory Effectiveness: {details.get('memory_effectiveness', 0):.3f}")
            
            elif result.test_name == "collaborative_processing":
                speedup = details.get("speedup_factor", 0)
                efficiency = details.get("collaboration_efficiency", 0)
                logger.info(f"  Speedup Factor: {speedup:.2f}x")
                logger.info(f"  Collaboration Efficiency: {efficiency:.2f}")
            
            elif result.test_name == "variable_document_sizes":
                scaling = details.get("scaling_analysis", {})
                if "scaling_efficiency" in scaling:
                    logger.info(f"  Scaling Efficiency: {scaling['scaling_efficiency']:.2f}")
                    logger.info(f"  Processing Rate: {scaling.get('avg_processing_rate', 0):.1f} words/sec")
        
        # Performance recommendations
        logger.info("\n💡 PERFORMANCE RECOMMENDATIONS")
        logger.info("-" * 50)
        
        avg_success_rate = statistics.mean(r.metrics.success_rate for r in results)
        avg_latency = statistics.mean(r.metrics.latency_p50 for r in results)
        avg_memory = statistics.mean(r.metrics.memory_peak_mb for r in results)
        
        if avg_success_rate < 0.9:
            logger.info("⚠️  Consider improving error handling - success rate below 90%")
        
        if avg_latency > 5.0:
            logger.info("⚠️  Consider performance optimization - average latency above 5s")
        
        if avg_memory > 500:
            logger.info("⚠️  Consider memory optimization - peak memory usage above 500MB")
        
        # Find best performing test
        best_throughput = max(results, key=lambda r: r.metrics.throughput_docs_per_second)
        logger.info(f"🏆 Best Throughput: {best_throughput.test_name} ({best_throughput.metrics.throughput_docs_per_second:.2f} docs/s)")
        
        best_efficiency = min(results, key=lambda r: r.metrics.memory_peak_mb)
        logger.info(f"🏆 Most Memory Efficient: {best_efficiency.test_name} ({best_efficiency.metrics.memory_peak_mb:.1f}MB peak)")
        
        logger.info("\n✅ Performance benchmark analysis complete!")
        
        # Save results to file
        self._save_results_to_file(results)
    
    def _save_results_to_file(self, results: List[BenchmarkResult]):
        """Save benchmark results to JSON file."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"agent_performance_benchmarks_{timestamp}.json"
            
            # Convert results to JSON-serializable format
            json_results = []
            for result in results:
                json_result = {
                    "test_name": result.test_name,
                    "timestamp": result.timestamp.isoformat(),
                    "configuration": result.configuration,
                    "metrics": {
                        "execution_time": result.metrics.execution_time,
                        "memory_peak_mb": result.metrics.memory_peak_mb,
                        "memory_delta_mb": result.metrics.memory_delta_mb,
                        "cpu_percent": result.metrics.cpu_percent,
                        "success_rate": result.metrics.success_rate,
                        "throughput_docs_per_second": result.metrics.throughput_docs_per_second,
                        "latency_p50": result.metrics.latency_p50,
                        "latency_p95": result.metrics.latency_p95,
                        "latency_p99": result.metrics.latency_p99,
                        "error_count": result.metrics.error_count,
                        "total_operations": result.metrics.total_operations
                    },
                    "details": result.details
                }
                json_results.append(json_result)
            
            with open(filename, 'w') as f:
                json.dump({
                    "benchmark_run": {
                        "timestamp": datetime.now().isoformat(),
                        "system_info": {
                            "cpu_count": psutil.cpu_count(),
                            "memory_total_gb": psutil.virtual_memory().total / (1024**3),
                            "platform": os.name
                        },
                        "results": json_results
                    }
                }, f, indent=2)
            
            logger.info(f"💾 Benchmark results saved to: {filename}")
            
        except Exception as e:
            logger.warning(f"Failed to save results to file: {e}")


# Standalone test runner
if __name__ == "__main__":
    async def main():
        """Main entry point for performance benchmarks."""
        benchmarks = AgentPerformanceBenchmarks()
        results = await benchmarks.run_all_benchmarks()
        
        if results:
            logger.info(f"\n🎯 Successfully completed {len(results)} performance benchmarks!")
        else:
            logger.error("❌ No benchmarks completed successfully")
    
    asyncio.run(main())