#!/usr/bin/env python3
"""
Collaborative Processing Load Testing Suite

Comprehensive load testing for agent collaboration scenarios including stress testing,
concurrent processing, failure recovery, and scalability validation.
"""

import asyncio
import logging
import time
import json
import statistics
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
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
    from src.orchestration.communication import MessageBus, Message, MessageType
    from src.orchestration.agents.document_agent import DocumentAgent
    from src.orchestration.mcp_adapter import MCPToolAdapter
    from src.orchestration.base import Task, Result
    from src.tools.enhanced_mcp_tools import EnhancedMCPTools
    IMPORTS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Some imports failed: {e}")
    IMPORTS_AVAILABLE = False


@dataclass
class LoadTestMetrics:
    """Metrics for load testing results."""
    test_name: str
    duration_seconds: float
    total_requests: int
    successful_requests: int
    failed_requests: int
    requests_per_second: float
    avg_response_time: float
    p50_response_time: float
    p95_response_time: float
    p99_response_time: float
    max_response_time: float
    error_rate: float
    memory_peak_mb: float
    cpu_peak_percent: float
    concurrent_agents: int
    collaboration_success_rate: float


@dataclass
class LoadTestScenario:
    """Definition of a load test scenario."""
    name: str
    description: str
    concurrent_agents: int
    requests_per_agent: int
    request_rate_per_second: float
    collaboration_mode: str  # 'independent', 'coordinated', 'competitive'
    document_complexity: str  # 'simple', 'medium', 'complex'
    duration_seconds: Optional[float] = None


class LoadTestDocumentGenerator:
    """Generate documents for load testing scenarios."""
    
    @staticmethod
    def create_simple_documents(count: int) -> List[Dict[str, Any]]:
        """Create simple documents for basic load testing."""
        templates = [
            "Company {company} announced a partnership with {partner}.",
            "Researcher {researcher} from {university} published findings on {topic}.",
            "The collaboration between {org1} and {org2} focuses on {domain}.",
            "{person} joins {company} as {role} to lead {initiative}.",
            "New research by {institution} reveals insights about {subject}."
        ]
        
        entities = {
            'company': ['TechCorp', 'InnovateLabs', 'FutureSystems', 'DataDynamics', 'AIAdvanced'],
            'partner': ['GlobalTech', 'ResearchInc', 'UniversityPartners', 'IndustryLeader', 'TechGiant'],
            'researcher': ['Dr. Smith', 'Prof. Johnson', 'Dr. Williams', 'Prof. Brown', 'Dr. Davis'],
            'university': ['Tech University', 'Research Institute', 'Science Academy', 'Innovation College'],
            'person': ['Alex Chen', 'Maria Rodriguez', 'John Kim', 'Sarah Taylor', 'David Wilson'],
            'role': ['CTO', 'Research Director', 'VP Engineering', 'Chief Scientist', 'Lead Developer'],
            'topic': ['machine learning', 'data science', 'artificial intelligence', 'quantum computing'],
            'domain': ['healthcare', 'finance', 'education', 'manufacturing', 'transportation'],
            'org1': ['Microsoft', 'Google', 'Amazon', 'Apple', 'Meta'],
            'org2': ['Stanford', 'MIT', 'Harvard', 'Berkeley', 'CMU'],
            'initiative': ['AI research', 'innovation lab', 'technology development', 'product design'],
            'institution': ['Research Center', 'Technology Institute', 'Innovation Hub', 'Science Lab'],
            'subject': ['neural networks', 'robotics', 'cloud computing', 'cybersecurity']
        }
        
        documents = []
        for i in range(count):
            template = templates[i % len(templates)]
            
            # Fill template with random entities
            content = template
            for key, values in entities.items():
                if f'{{{key}}}' in content:
                    content = content.replace(f'{{{key}}}', values[i % len(values)])
            
            documents.append({
                'id': f'load_test_simple_{i:04d}',
                'title': f'Load Test Document {i+1}',
                'content': content,
                'domain': 'technology',
                'complexity': 'simple',
                'word_count': len(content.split()),
                'expected_entities': 2 + (i % 3)
            })
        
        return documents
    
    @staticmethod
    def create_medium_documents(count: int) -> List[Dict[str, Any]]:
        """Create medium complexity documents."""
        base_content = """
        The recent partnership between {company1} and {company2} represents a significant 
        advancement in {field}. Led by {leader1} from {company1} and {leader2} from {company2}, 
        the collaboration aims to develop innovative solutions for {application}. 
        
        The joint research team, based in {location1} and {location2}, will focus on 
        {technology} with applications in {industry}. Initial funding of ${amount} million 
        has been secured from {investor}. The project is expected to create {jobs} new 
        positions and deliver results by {timeline}.
        
        Key researchers include {researcher1} from {institution1} and {researcher2} from 
        {institution2}. The work builds on previous research in {previous_work} and aims 
        to achieve {goal} through innovative {method} approaches.
        """
        
        entity_pools = {
            'company1': ['Microsoft', 'Google', 'Apple', 'Amazon', 'Tesla', 'Meta'],
            'company2': ['Stanford University', 'MIT', 'Harvard', 'UC Berkeley', 'CMU', 'Caltech'],
            'field': ['artificial intelligence', 'quantum computing', 'biotechnology', 'robotics'],
            'leader1': ['Dr. Sarah Chen', 'Prof. Michael Rodriguez', 'Dr. Lisa Wang', 'Prof. David Kim'],
            'leader2': ['Dr. Robert Johnson', 'Prof. Maria Garcia', 'Dr. James Wilson', 'Prof. Anna Lee'],
            'application': ['healthcare diagnosis', 'autonomous vehicles', 'financial modeling', 'climate research'],
            'location1': ['San Francisco', 'Seattle', 'Boston', 'Austin', 'New York'],
            'location2': ['Palo Alto', 'Cambridge', 'Pittsburgh', 'Atlanta', 'Los Angeles'],
            'technology': ['machine learning', 'neural networks', 'quantum algorithms', 'computer vision'],
            'industry': ['healthcare', 'automotive', 'finance', 'energy', 'education'],
            'amount': ['50', '75', '100', '150', '200'],
            'investor': ['NSF', 'NIH', 'DOE', 'DARPA', 'private investors'],
            'jobs': ['50', '75', '100', '125', '150'],
            'timeline': ['Q4 2024', 'Q1 2025', 'Q2 2025', 'end of 2024', 'mid-2025'],
            'researcher1': ['Dr. Alex Thompson', 'Prof. Jennifer Martinez', 'Dr. Kevin Brown'],
            'institution1': ['Research Institute', 'Innovation Lab', 'Technology Center'],
            'researcher2': ['Dr. Michelle Davis', 'Prof. Steven Clark', 'Dr. Nicole Taylor'],
            'institution2': ['Advanced Research Center', 'Future Tech Lab', 'Science Innovation Hub'],
            'previous_work': ['deep learning', 'reinforcement learning', 'natural language processing'],
            'goal': ['improved accuracy', 'reduced costs', 'enhanced performance', 'better efficiency'],
            'method': ['neural network', 'statistical modeling', 'optimization', 'simulation']
        }
        
        documents = []
        for i in range(count):
            content = base_content
            
            # Fill template with varied entities
            for key, values in entity_pools.items():
                if f'{{{key}}}' in content:
                    content = content.replace(f'{{{key}}}', values[i % len(values)])
            
            content = content.strip()
            
            documents.append({
                'id': f'load_test_medium_{i:04d}',
                'title': f'Medium Complexity Document {i+1}',
                'content': content,
                'domain': 'research_collaboration',
                'complexity': 'medium',
                'word_count': len(content.split()),
                'expected_entities': 8 + (i % 5),
                'expected_relationships': 3 + (i % 4)
            })
        
        return documents
    
    @staticmethod
    def create_complex_documents(count: int) -> List[Dict[str, Any]]:
        """Create complex documents for stress testing."""
        complex_content = """
        The transformative collaboration between {primary_company}, {secondary_company}, 
        and {tertiary_organization} marks a pivotal moment in {primary_field} research. 
        This multi-institutional partnership, spearheaded by {primary_leader}, 
        {secondary_leader}, and {tertiary_leader}, integrates expertise from {discipline1}, 
        {discipline2}, and {discipline3} to address critical challenges in {application_domain}.
        
        The research consortium, headquartered in {primary_location} with satellite 
        facilities in {secondary_location}, {tertiary_location}, and {quaternary_location}, 
        brings together over {researcher_count} researchers across {institution_count} 
        institutions. The initiative focuses on developing {primary_technology} enhanced 
        with {secondary_technology} and {tertiary_technology} capabilities.
        
        Key technical objectives include advancing {objective1}, improving {objective2}, 
        and pioneering {objective3}. The project leverages {methodology1} combined with 
        {methodology2} to achieve {target_metric} improvements in {performance_area}. 
        
        Principal investigators include {pi1} from {affiliation1}, {pi2} from {affiliation2}, 
        {pi3} from {affiliation3}, and {pi4} from {affiliation4}. Industry partners 
        {industry_partner1}, {industry_partner2}, and {industry_partner3} provide 
        expertise in {industry_domain1}, {industry_domain2}, and {industry_domain3}.
        
        The ${funding_amount} million initiative, funded by {funding_source1}, 
        {funding_source2}, and {funding_source3}, aims to deliver {deliverable1}, 
        {deliverable2}, and {deliverable3} by {milestone_date}. Expected outcomes 
        include {outcome1}, {outcome2}, and {outcome3}, with potential applications 
        in {future_application1}, {future_application2}, and {future_application3}.
        
        This groundbreaking collaboration builds upon previous work in {foundation1}, 
        {foundation2}, and {foundation3}, representing a significant advancement in 
        understanding {research_question} and developing practical solutions for 
        {societal_challenge}.
        """
        
        # Extensive entity pools for complex documents
        entity_pools = {
            'primary_company': ['Microsoft Research', 'Google DeepMind', 'OpenAI', 'Anthropic', 'Meta AI'],
            'secondary_company': ['IBM Research', 'Amazon Science', 'Apple ML Research', 'NVIDIA Research'],
            'tertiary_organization': ['MIT', 'Stanford', 'Harvard', 'UC Berkeley', 'CMU', 'Caltech'],
            'primary_field': ['artificial intelligence', 'quantum computing', 'computational biology', 'robotics'],
            'primary_leader': ['Dr. Sarah Elizabeth Chen', 'Prof. Michael Anthony Rodriguez', 'Dr. Lisa Marie Wang'],
            'secondary_leader': ['Dr. Robert James Kim', 'Prof. Maria Fernanda Garcia', 'Dr. David Scott Wilson'],
            'tertiary_leader': ['Prof. Jennifer Lynn Martinez', 'Dr. Kevin Michael Brown', 'Prof. Nicole Ann Taylor'],
            'discipline1': ['computer science', 'electrical engineering', 'applied mathematics', 'physics'],
            'discipline2': ['neuroscience', 'cognitive science', 'computational linguistics', 'statistics'],
            'discipline3': ['materials science', 'mechanical engineering', 'bioengineering', 'chemistry'],
            'application_domain': ['healthcare technology', 'autonomous systems', 'climate modeling', 'space exploration'],
            'primary_location': ['San Francisco Bay Area', 'Boston Metropolitan Area', 'Seattle Region'],
            'secondary_location': ['Austin, Texas', 'Research Triangle, North Carolina', 'Pittsburgh, Pennsylvania'],
            'tertiary_location': ['Toronto, Canada', 'London, United Kingdom', 'Singapore'],
            'quaternary_location': ['Tel Aviv, Israel', 'Tokyo, Japan', 'Sydney, Australia'],
            'researcher_count': ['150', '200', '250', '300', '350'],
            'institution_count': ['12', '15', '18', '20', '25'],
            'primary_technology': ['large language models', 'quantum algorithms', 'neural architectures'],
            'secondary_technology': ['reinforcement learning', 'computer vision', 'natural language processing'],
            'tertiary_technology': ['edge computing', 'distributed systems', 'federated learning'],
            'objective1': ['model interpretability', 'computational efficiency', 'robustness to adversarial attacks'],
            'objective2': ['real-time performance', 'energy efficiency', 'scalability to massive datasets'],
            'objective3': ['human-AI collaboration', 'ethical AI development', 'privacy-preserving computation'],
            'methodology1': ['transformer architectures', 'graph neural networks', 'variational methods'],
            'methodology2': ['meta-learning approaches', 'causal inference techniques', 'optimization algorithms'],
            'target_metric': ['30-40%', '50-60%', '70-80%', '2-3x', '5-10x'],
            'performance_area': ['inference speed', 'model accuracy', 'energy consumption', 'training efficiency']
        }
        
        # Add more entities for complex documents
        more_entities = {
            'pi1': ['Prof. Alexandra Bennett', 'Dr. Christopher Hayes', 'Prof. Diana Foster'],
            'affiliation1': ['Stanford AI Lab', 'MIT CSAIL', 'Harvard Medical School'],
            'pi2': ['Dr. Elena Volkov', 'Prof. Francesco Rossi', 'Dr. Grace Liu'],
            'affiliation2': ['UC Berkeley EECS', 'CMU Machine Learning', 'Caltech Computing'],
            'pi3': ['Prof. Hassan Al-Rashid', 'Dr. Isabella Santos', 'Prof. Jacob Thompson'],
            'affiliation3': ['Oxford Computer Science', 'ETH Zurich AI Center', 'University of Toronto Vector Institute'],
            'pi4': ['Dr. Katherine Moore', 'Prof. Lorenzo Bertinelli', 'Dr. Melody Chang'],
            'affiliation4': ['Technical University of Munich', 'RIKEN Center for AI', 'INRIA Paris'],
            'industry_partner1': ['NVIDIA Corporation', 'Intel Labs', 'AMD Research'],
            'industry_partner2': ['Qualcomm AI Research', 'Samsung Advanced Institute', 'Huawei Research'],
            'industry_partner3': ['Boeing Research', 'General Electric Research', 'Siemens Technology'],
            'industry_domain1': ['hardware acceleration', 'edge AI deployment', 'quantum computing'],
            'industry_domain2': ['autonomous systems', 'IoT integration', 'distributed inference'],
            'industry_domain3': ['industrial automation', 'aerospace applications', 'telecommunications'],
            'funding_amount': ['50', '75', '100', '150', '200', '250'],
            'funding_source1': ['National Science Foundation', 'National Institutes of Health', 'Department of Energy'],
            'funding_source2': ['DARPA', 'European Research Council', 'Canadian Institute for Advanced Research'],
            'funding_source3': ['private foundation grants', 'industry consortium funding', 'international collaboration funds'],
            'deliverable1': ['open-source software platform', 'comprehensive dataset', 'standardized benchmarks'],
            'deliverable2': ['trained model architectures', 'evaluation methodologies', 'best practices guidelines'],
            'deliverable3': ['research publications', 'patent applications', 'technology transfer agreements'],
            'milestone_date': ['December 2025', 'June 2026', 'March 2026', 'September 2025'],
            'outcome1': ['breakthrough algorithmic innovations', 'novel theoretical insights', 'practical deployment solutions'],
            'outcome2': ['improved model performance', 'enhanced computational efficiency', 'better interpretability methods'],
            'outcome3': ['ethical AI frameworks', 'privacy-preserving techniques', 'fairness evaluation tools'],
            'future_application1': ['personalized medicine', 'smart city infrastructure', 'environmental monitoring'],
            'future_application2': ['educational technology', 'scientific discovery', 'creative assistance'],
            'future_application3': ['disaster response', 'accessibility technology', 'sustainable development'],
            'foundation1': ['deep learning theory', 'optimization landscapes', 'information theory'],
            'foundation2': ['neuroscience insights', 'cognitive modeling', 'human-computer interaction'],
            'foundation3': ['distributed computing', 'cryptographic protocols', 'game theory'],
            'research_question': ['artificial general intelligence', 'consciousness in machines', 'computational creativity'],
            'societal_challenge': ['climate change mitigation', 'healthcare accessibility', 'educational equity']
        }
        
        entity_pools.update(more_entities)
        
        documents = []
        for i in range(count):
            content = complex_content
            
            # Fill template with entities
            for key, values in entity_pools.items():
                if f'{{{key}}}' in content:
                    content = content.replace(f'{{{key}}}', values[i % len(values)])
            
            content = content.strip()
            
            documents.append({
                'id': f'load_test_complex_{i:04d}',
                'title': f'Complex Research Collaboration {i+1}',
                'content': content,
                'domain': 'advanced_research',
                'complexity': 'complex',
                'word_count': len(content.split()),
                'expected_entities': 25 + (i % 10),
                'expected_relationships': 12 + (i % 8)
            })
        
        return documents


class CollaborativeLoadTester:
    """Load testing framework for collaborative agent scenarios."""
    
    def __init__(self):
        self.results = []
        self.active_agents = []
        self.message_bus = None
        self.service_manager = None
        
    async def setup_load_test_environment(self, agent_count: int) -> Dict[str, Any]:
        """Set up environment for load testing with specified number of agents."""
        if not IMPORTS_AVAILABLE:
            raise RuntimeError("Required modules not available")
        
        env = {}
        
        # Initialize core services
        env['service_manager'] = ServiceManager()
        await env['service_manager'].initialize()
        
        # Initialize message bus for agent communication
        env['message_bus'] = MessageBus()
        
        # Initialize MCP adapter
        mcp_adapter = MCPToolAdapter()
        
        # Create specified number of agents
        env['agents'] = []
        for i in range(agent_count):
            agent = DocumentAgent(
                mcp_adapter=mcp_adapter,
                agent_id=f"load_test_agent_{i:03d}",
                memory_config={"enable_memory": True, "max_memories": 500},
                reasoning_config={"enable_reasoning": True, "confidence_threshold": 0.7},
                communication_config={"enable_broadcast": True, "max_queue_size": 200},
                message_bus=env['message_bus']
            )
            env['agents'].append(agent)
        
        # Store references for cleanup
        self.active_agents = env['agents']
        self.message_bus = env['message_bus']
        self.service_manager = env['service_manager']
        
        logger.info(f"✅ Load test environment created with {agent_count} agents")
        return env
    
    async def run_independent_processing_load_test(self, scenario: LoadTestScenario) -> LoadTestMetrics:
        """Test independent processing load where agents work separately."""
        logger.info(f"🔄 Running independent processing load test: {scenario.name}")
        
        env = await self.setup_load_test_environment(scenario.concurrent_agents)
        agents = env['agents']
        
        # Generate documents based on complexity
        if scenario.document_complexity == 'simple':
            documents = LoadTestDocumentGenerator.create_simple_documents(scenario.requests_per_agent * scenario.concurrent_agents)
        elif scenario.document_complexity == 'medium':
            documents = LoadTestDocumentGenerator.create_medium_documents(scenario.requests_per_agent * scenario.concurrent_agents)
        else:
            documents = LoadTestDocumentGenerator.create_complex_documents(scenario.requests_per_agent * scenario.concurrent_agents)
        
        # Performance monitoring
        start_time = time.time()
        process = psutil.Process()
        start_memory = process.memory_info().rss / 1024 / 1024  # MB
        peak_memory = start_memory
        peak_cpu = 0.0
        
        response_times = []
        successful_requests = 0
        failed_requests = 0
        
        async def process_agent_batch(agent, agent_documents):
            """Process a batch of documents for a single agent."""
            agent_successes = 0
            agent_failures = 0
            agent_response_times = []
            
            for doc in agent_documents:
                task = Task(
                    task_type="document_processing",
                    parameters={
                        "text": doc["content"],
                        "domain": doc["domain"],
                        "document_id": doc["id"]
                    },
                    context={
                        "load_test": True,
                        "test_scenario": scenario.name,
                        "agent_id": agent.agent_id
                    }
                )
                
                # Rate limiting
                if scenario.request_rate_per_second > 0:
                    await asyncio.sleep(1.0 / scenario.request_rate_per_second)
                
                request_start = time.time()
                try:
                    result = await agent.execute(task)
                    request_time = time.time() - request_start
                    
                    agent_response_times.append(request_time)
                    
                    if result.success:
                        agent_successes += 1
                    else:
                        agent_failures += 1
                        
                except Exception as e:
                    request_time = time.time() - request_start
                    agent_response_times.append(request_time)
                    agent_failures += 1
                    logger.warning(f"Request failed for agent {agent.agent_id}: {e}")
            
            return agent_successes, agent_failures, agent_response_times
        
        # Distribute documents among agents
        docs_per_agent = len(documents) // len(agents)
        agent_tasks = []
        
        for i, agent in enumerate(agents):
            start_idx = i * docs_per_agent
            end_idx = start_idx + docs_per_agent
            if i == len(agents) - 1:  # Last agent gets remaining documents
                end_idx = len(documents)
            
            agent_docs = documents[start_idx:end_idx]
            agent_tasks.append(process_agent_batch(agent, agent_docs))
        
        # Monitor system resources during execution
        async def monitor_resources():
            nonlocal peak_memory, peak_cpu
            while True:
                try:
                    current_memory = process.memory_info().rss / 1024 / 1024
                    current_cpu = process.cpu_percent()
                    
                    peak_memory = max(peak_memory, current_memory)
                    peak_cpu = max(peak_cpu, current_cpu)
                    
                    await asyncio.sleep(0.5)
                except asyncio.CancelledError:
                    break
        
        # Start monitoring
        monitor_task = asyncio.create_task(monitor_resources())
        
        try:
            # Execute all agent tasks concurrently
            results = await asyncio.gather(*agent_tasks)
            
            # Aggregate results
            for agent_successes, agent_failures, agent_response_times in results:
                successful_requests += agent_successes
                failed_requests += agent_failures
                response_times.extend(agent_response_times)
            
        finally:
            monitor_task.cancel()
            try:
                await monitor_task
            except asyncio.CancelledError:
                pass
        
        total_time = time.time() - start_time
        total_requests = successful_requests + failed_requests
        
        # Calculate metrics
        metrics = LoadTestMetrics(
            test_name=scenario.name,
            duration_seconds=total_time,
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            requests_per_second=total_requests / total_time if total_time > 0 else 0,
            avg_response_time=statistics.mean(response_times) if response_times else 0,
            p50_response_time=statistics.median(response_times) if response_times else 0,
            p95_response_time=statistics.quantiles(response_times, n=20)[18] if len(response_times) >= 20 else (max(response_times) if response_times else 0),
            p99_response_time=statistics.quantiles(response_times, n=100)[98] if len(response_times) >= 100 else (max(response_times) if response_times else 0),
            max_response_time=max(response_times) if response_times else 0,
            error_rate=failed_requests / total_requests if total_requests > 0 else 0,
            memory_peak_mb=peak_memory,
            cpu_peak_percent=peak_cpu,
            concurrent_agents=scenario.concurrent_agents,
            collaboration_success_rate=1.0  # No collaboration in independent mode
        )
        
        await self.cleanup_environment()
        return metrics
    
    async def run_coordinated_processing_load_test(self, scenario: LoadTestScenario) -> LoadTestMetrics:
        """Test coordinated processing where agents collaborate on shared workload."""
        logger.info(f"🤝 Running coordinated processing load test: {scenario.name}")
        
        env = await self.setup_load_test_environment(scenario.concurrent_agents)
        agents = env['agents']
        message_bus = env['message_bus']
        
        # Generate shared workload
        if scenario.document_complexity == 'simple':
            documents = LoadTestDocumentGenerator.create_simple_documents(scenario.requests_per_agent * 2)  # Shared workload
        elif scenario.document_complexity == 'medium':
            documents = LoadTestDocumentGenerator.create_medium_documents(scenario.requests_per_agent * 2)
        else:
            documents = LoadTestDocumentGenerator.create_complex_documents(scenario.requests_per_agent * 2)
        
        # Performance monitoring
        start_time = time.time()
        process = psutil.Process()
        start_memory = process.memory_info().rss / 1024 / 1024
        peak_memory = start_memory
        peak_cpu = 0.0
        
        response_times = []
        successful_requests = 0
        failed_requests = 0
        collaboration_attempts = 0
        successful_collaborations = 0
        
        # Shared work queue
        work_queue = asyncio.Queue()
        for doc in documents:
            await work_queue.put(doc)
        
        async def coordinated_worker(agent, worker_id):
            """Worker that processes items from shared queue with coordination."""
            worker_successes = 0
            worker_failures = 0
            worker_response_times = []
            worker_collaborations = 0
            worker_successful_collaborations = 0
            
            while not work_queue.empty():
                try:
                    # Get next document with timeout
                    doc = await asyncio.wait_for(work_queue.get(), timeout=1.0)
                    
                    # Decide whether to collaborate (30% chance for coordinated mode)
                    should_collaborate = random.random() < 0.3 and len(agents) > 1
                    
                    if should_collaborate:
                        worker_collaborations += 1
                        
                        # Simple collaboration: request assistance from another agent
                        other_agents = [a for a in agents if a != agent]
                        if other_agents and hasattr(agent, 'collaborate_with'):
                            collaborator = random.choice(other_agents)
                            
                            collaboration_start = time.time()
                            try:
                                collab_result = await agent.collaborate_with(
                                    agent_id=collaborator.agent_id,
                                    task="document_processing_assistance",
                                    context={
                                        "document_preview": doc["content"][:100] + "...",
                                        "complexity": doc["complexity"],
                                        "load_test": True
                                    }
                                )
                                
                                if collab_result:
                                    worker_successful_collaborations += 1
                                    
                            except Exception as e:
                                logger.warning(f"Collaboration failed: {e}")
                    
                    # Process document
                    task = Task(
                        task_type="document_processing",
                        parameters={
                            "text": doc["content"],
                            "domain": doc["domain"],
                            "document_id": doc["id"]
                        },
                        context={
                            "load_test": True,
                            "coordinated_mode": True,
                            "worker_id": worker_id,
                            "collaborated": should_collaborate
                        }
                    )
                    
                    request_start = time.time()
                    result = await agent.execute(task)
                    request_time = time.time() - request_start
                    
                    worker_response_times.append(request_time)
                    
                    if result.success:
                        worker_successes += 1
                    else:
                        worker_failures += 1
                    
                    # Rate limiting
                    if scenario.request_rate_per_second > 0:
                        await asyncio.sleep(1.0 / scenario.request_rate_per_second)
                        
                except asyncio.TimeoutError:
                    break  # No more work available
                except Exception as e:
                    worker_failures += 1
                    logger.warning(f"Worker {worker_id} failed: {e}")
            
            return worker_successes, worker_failures, worker_response_times, worker_collaborations, worker_successful_collaborations
        
        # Monitor resources
        async def monitor_resources():
            nonlocal peak_memory, peak_cpu
            while True:
                try:
                    current_memory = process.memory_info().rss / 1024 / 1024
                    current_cpu = process.cpu_percent()
                    
                    peak_memory = max(peak_memory, current_memory)
                    peak_cpu = max(peak_cpu, current_cpu)
                    
                    await asyncio.sleep(0.5)
                except asyncio.CancelledError:
                    break
        
        monitor_task = asyncio.create_task(monitor_resources())
        
        try:
            # Start all workers
            worker_tasks = [
                coordinated_worker(agent, i) 
                for i, agent in enumerate(agents)
            ]
            
            results = await asyncio.gather(*worker_tasks)
            
            # Aggregate results
            for worker_successes, worker_failures, worker_response_times, worker_collaborations, worker_successful_collaborations in results:
                successful_requests += worker_successes
                failed_requests += worker_failures
                response_times.extend(worker_response_times)
                collaboration_attempts += worker_collaborations
                successful_collaborations += worker_successful_collaborations
        
        finally:
            monitor_task.cancel()
            try:
                await monitor_task
            except asyncio.CancelledError:
                pass
        
        total_time = time.time() - start_time
        total_requests = successful_requests + failed_requests
        
        metrics = LoadTestMetrics(
            test_name=scenario.name,
            duration_seconds=total_time,
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            requests_per_second=total_requests / total_time if total_time > 0 else 0,
            avg_response_time=statistics.mean(response_times) if response_times else 0,
            p50_response_time=statistics.median(response_times) if response_times else 0,
            p95_response_time=statistics.quantiles(response_times, n=20)[18] if len(response_times) >= 20 else (max(response_times) if response_times else 0),
            p99_response_time=statistics.quantiles(response_times, n=100)[98] if len(response_times) >= 100 else (max(response_times) if response_times else 0),
            max_response_time=max(response_times) if response_times else 0,
            error_rate=failed_requests / total_requests if total_requests > 0 else 0,
            memory_peak_mb=peak_memory,
            cpu_peak_percent=peak_cpu,
            concurrent_agents=scenario.concurrent_agents,
            collaboration_success_rate=successful_collaborations / collaboration_attempts if collaboration_attempts > 0 else 0
        )
        
        await self.cleanup_environment()
        return metrics
    
    async def run_competitive_processing_load_test(self, scenario: LoadTestScenario) -> LoadTestMetrics:
        """Test competitive processing where agents compete for limited resources."""
        logger.info(f"🏁 Running competitive processing load test: {scenario.name}")
        
        env = await self.setup_load_test_environment(scenario.concurrent_agents)
        agents = env['agents']
        
        # Generate limited high-value documents
        document_count = max(1, scenario.requests_per_agent // 2)  # Fewer documents for competition
        
        if scenario.document_complexity == 'simple':
            documents = LoadTestDocumentGenerator.create_simple_documents(document_count)
        elif scenario.document_complexity == 'medium':
            documents = LoadTestDocumentGenerator.create_medium_documents(document_count)
        else:
            documents = LoadTestDocumentGenerator.create_complex_documents(document_count)
        
        # Performance monitoring
        start_time = time.time()
        process = psutil.Process()
        start_memory = process.memory_info().rss / 1024 / 1024
        peak_memory = start_memory
        peak_cpu = 0.0
        
        response_times = []
        successful_requests = 0
        failed_requests = 0
        resource_conflicts = 0
        
        # Shared resource (limited concurrent processing slots)
        max_concurrent_processing = max(1, scenario.concurrent_agents // 2)
        processing_semaphore = asyncio.Semaphore(max_concurrent_processing)
        
        processed_documents = set()
        processing_lock = asyncio.Lock()
        
        async def competitive_agent(agent, agent_id):
            """Agent that competes for document processing opportunities."""
            agent_successes = 0
            agent_failures = 0
            agent_response_times = []
            agent_conflicts = 0
            
            # Each agent tries to process multiple documents
            for attempt in range(scenario.requests_per_agent):
                # Select random document
                doc = random.choice(documents)
                doc_id = doc["id"]
                
                # Try to claim document for processing
                async with processing_lock:
                    if doc_id in processed_documents:
                        agent_conflicts += 1
                        continue  # Document already processed
                    else:
                        processed_documents.add(doc_id)
                
                # Acquire processing resource
                try:
                    async with processing_semaphore:
                        task = Task(
                            task_type="document_processing",
                            parameters={
                                "text": doc["content"],
                                "domain": doc["domain"],
                                "document_id": f"{doc_id}_agent_{agent_id}_attempt_{attempt}"
                            },
                            context={
                                "load_test": True,
                                "competitive_mode": True,
                                "agent_id": agent_id,
                                "attempt": attempt
                            }
                        )
                        
                        request_start = time.time()
                        result = await agent.execute(task)
                        request_time = time.time() - request_start
                        
                        agent_response_times.append(request_time)
                        
                        if result.success:
                            agent_successes += 1
                        else:
                            agent_failures += 1
                        
                        # Brief processing delay to simulate work
                        await asyncio.sleep(0.1)
                        
                except Exception as e:
                    agent_failures += 1
                    logger.warning(f"Competitive agent {agent_id} failed: {e}")
                
                # Rate limiting
                if scenario.request_rate_per_second > 0:
                    await asyncio.sleep(1.0 / scenario.request_rate_per_second)
            
            return agent_successes, agent_failures, agent_response_times, agent_conflicts
        
        # Monitor resources
        async def monitor_resources():
            nonlocal peak_memory, peak_cpu
            while True:
                try:
                    current_memory = process.memory_info().rss / 1024 / 1024
                    current_cpu = process.cpu_percent()
                    
                    peak_memory = max(peak_memory, current_memory)
                    peak_cpu = max(peak_cpu, current_cpu)
                    
                    await asyncio.sleep(0.5)
                except asyncio.CancelledError:
                    break
        
        monitor_task = asyncio.create_task(monitor_resources())
        
        try:
            # Start competitive agents
            competitive_tasks = [
                competitive_agent(agent, i)
                for i, agent in enumerate(agents)
            ]
            
            results = await asyncio.gather(*competitive_tasks)
            
            # Aggregate results
            for agent_successes, agent_failures, agent_response_times, agent_conflicts in results:
                successful_requests += agent_successes
                failed_requests += agent_failures
                response_times.extend(agent_response_times)
                resource_conflicts += agent_conflicts
        
        finally:
            monitor_task.cancel()
            try:
                await monitor_task
            except asyncio.CancelledError:
                pass
        
        total_time = time.time() - start_time
        total_requests = successful_requests + failed_requests
        
        metrics = LoadTestMetrics(
            test_name=scenario.name,
            duration_seconds=total_time,
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            requests_per_second=total_requests / total_time if total_time > 0 else 0,
            avg_response_time=statistics.mean(response_times) if response_times else 0,
            p50_response_time=statistics.median(response_times) if response_times else 0,
            p95_response_time=statistics.quantiles(response_times, n=20)[18] if len(response_times) >= 20 else (max(response_times) if response_times else 0),
            p99_response_time=statistics.quantiles(response_times, n=100)[98] if len(response_times) >= 100 else (max(response_times) if response_times else 0),
            max_response_time=max(response_times) if response_times else 0,
            error_rate=failed_requests / total_requests if total_requests > 0 else 0,
            memory_peak_mb=peak_memory,
            cpu_peak_percent=peak_cpu,
            concurrent_agents=scenario.concurrent_agents,
            collaboration_success_rate=1 - (resource_conflicts / (scenario.concurrent_agents * scenario.requests_per_agent)) if scenario.concurrent_agents * scenario.requests_per_agent > 0 else 0
        )
        
        await self.cleanup_environment()
        return metrics
    
    async def run_stress_test(self, base_scenario: LoadTestScenario) -> List[LoadTestMetrics]:
        """Run escalating stress test to find system breaking points."""
        logger.info(f"💥 Running stress test based on: {base_scenario.name}")
        
        stress_results = []
        
        # Escalating stress levels
        stress_levels = [
            (2, 5, 1.0),    # (agents, requests_per_agent, rate_multiplier)
            (5, 10, 1.5),
            (10, 15, 2.0),
            (15, 20, 3.0),
            (20, 25, 4.0),
            (25, 30, 5.0)
        ]
        
        for agents, requests, rate_mult in stress_levels:
            stress_scenario = LoadTestScenario(
                name=f"stress_test_{agents}agents_{requests}req",
                description=f"Stress test with {agents} agents, {requests} requests each",
                concurrent_agents=agents,
                requests_per_agent=requests,
                request_rate_per_second=base_scenario.request_rate_per_second * rate_mult,
                collaboration_mode=base_scenario.collaboration_mode,
                document_complexity=base_scenario.document_complexity
            )
            
            logger.info(f"🔥 Stress level: {agents} agents, {requests} requests each")
            
            try:
                if stress_scenario.collaboration_mode == 'independent':
                    metrics = await self.run_independent_processing_load_test(stress_scenario)
                elif stress_scenario.collaboration_mode == 'coordinated':
                    metrics = await self.run_coordinated_processing_load_test(stress_scenario)
                else:
                    metrics = await self.run_competitive_processing_load_test(stress_scenario)
                
                stress_results.append(metrics)
                
                # Check if system is breaking down
                if metrics.error_rate > 0.5 or metrics.avg_response_time > 30.0:
                    logger.warning(f"⚠️  System stress detected at {agents} agents - stopping stress test")
                    break
                    
            except Exception as e:
                logger.error(f"❌ Stress test failed at {agents} agents: {e}")
                break
            
            # Brief recovery between stress levels
            await asyncio.sleep(2)
        
        return stress_results
    
    async def cleanup_environment(self):
        """Clean up test environment."""
        try:
            if self.message_bus:
                await self.message_bus.cleanup()
            
            # Force garbage collection
            gc.collect()
            
        except Exception as e:
            logger.warning(f"Cleanup warning: {e}")
    
    async def run_comprehensive_load_tests(self) -> Dict[str, Any]:
        """Run comprehensive suite of collaborative load tests."""
        logger.info("🚀 Starting Comprehensive Collaborative Load Tests")
        logger.info("=" * 80)
        
        if not IMPORTS_AVAILABLE:
            logger.error("❌ Required modules not available")
            return {}
        
        # Define test scenarios
        test_scenarios = [
            LoadTestScenario(
                name="light_independent_load",
                description="Light load with independent agents",
                concurrent_agents=3,
                requests_per_agent=5,
                request_rate_per_second=2.0,
                collaboration_mode='independent',
                document_complexity='simple'
            ),
            LoadTestScenario(
                name="medium_coordinated_load",
                description="Medium load with coordinated agents",
                concurrent_agents=5,
                requests_per_agent=8,
                request_rate_per_second=1.5,
                collaboration_mode='coordinated',
                document_complexity='medium'
            ),
            LoadTestScenario(
                name="heavy_competitive_load",
                description="Heavy load with competitive agents",
                concurrent_agents=8,
                requests_per_agent=10,
                request_rate_per_second=1.0,
                collaboration_mode='competitive',
                document_complexity='complex'
            ),
            LoadTestScenario(
                name="high_throughput_test",
                description="High throughput processing test",
                concurrent_agents=10,
                requests_per_agent=15,
                request_rate_per_second=3.0,
                collaboration_mode='independent',
                document_complexity='simple'
            )
        ]
        
        all_results = {}
        
        try:
            # Run standard load tests
            for scenario in test_scenarios:
                logger.info(f"\n🔬 Running scenario: {scenario.name}")
                
                try:
                    if scenario.collaboration_mode == 'independent':
                        metrics = await self.run_independent_processing_load_test(scenario)
                    elif scenario.collaboration_mode == 'coordinated':
                        metrics = await self.run_coordinated_processing_load_test(scenario)
                    else:
                        metrics = await self.run_competitive_processing_load_test(scenario)
                    
                    all_results[scenario.name] = metrics
                    logger.info(f"✅ {scenario.name} completed")
                    
                except Exception as e:
                    logger.error(f"❌ {scenario.name} failed: {e}")
                    continue
                
                # Brief pause between tests
                await asyncio.sleep(1)
            
            # Run stress test on best performing scenario
            if all_results:
                best_scenario = min(test_scenarios, key=lambda s: all_results.get(s.name, LoadTestMetrics("", 0, 0, 0, 0, 0, 999, 0, 0, 0, 0, 1.0, 0, 0, 0, 0)).error_rate)
                
                logger.info(f"\n💥 Running stress test based on best scenario: {best_scenario.name}")
                stress_results = await self.run_stress_test(best_scenario)
                all_results['stress_test_results'] = stress_results
            
            # Generate comprehensive report
            self._generate_load_test_report(all_results)
            
            return all_results
            
        except Exception as e:
            logger.error(f"❌ Load test execution failed: {e}")
            return {}
        
        finally:
            await self.cleanup_environment()
    
    def _generate_load_test_report(self, results: Dict[str, Any]):
        """Generate comprehensive load test report."""
        logger.info("\n" + "=" * 80)
        logger.info("📊 COLLABORATIVE LOAD TEST REPORT")
        logger.info("=" * 80)
        
        if not results:
            logger.info("❌ No load test results available")
            return
        
        # Summary table for standard tests
        standard_results = {k: v for k, v in results.items() if k != 'stress_test_results' and isinstance(v, LoadTestMetrics)}
        
        if standard_results:
            logger.info("\n📈 LOAD TEST SUMMARY")
            logger.info("-" * 90)
            logger.info(f"{'Test Scenario':<25} {'Agents':<7} {'RPS':<8} {'Success%':<9} {'Avg Latency':<12} {'Error%':<8} {'Memory':<10}")
            logger.info("-" * 90)
            
            for name, metrics in standard_results.items():
                logger.info(f"{name:<25} {metrics.concurrent_agents:<7} {metrics.requests_per_second:>6.1f}  {metrics.successful_requests/metrics.total_requests*100:>6.1f}%    {metrics.avg_response_time:>8.3f}s     {metrics.error_rate*100:>5.1f}%   {metrics.memory_peak_mb:>6.1f}MB")
        
        # Detailed analysis
        logger.info("\n🔍 DETAILED ANALYSIS")
        logger.info("-" * 50)
        
        for name, metrics in standard_results.items():
            logger.info(f"\n{name.upper().replace('_', ' ')}:")
            logger.info(f"  Duration: {metrics.duration_seconds:.2f}s")
            logger.info(f"  Total Requests: {metrics.total_requests}")
            logger.info(f"  Success Rate: {metrics.successful_requests/metrics.total_requests*100:.1f}%")
            logger.info(f"  Throughput: {metrics.requests_per_second:.2f} requests/second")
            logger.info(f"  Latency P50/P95/P99: {metrics.p50_response_time:.3f}s / {metrics.p95_response_time:.3f}s / {metrics.p99_response_time:.3f}s")
            logger.info(f"  Max Response Time: {metrics.max_response_time:.3f}s")
            logger.info(f"  Memory Peak: {metrics.memory_peak_mb:.1f}MB")
            logger.info(f"  CPU Peak: {metrics.cpu_peak_percent:.1f}%")
            logger.info(f"  Collaboration Success: {metrics.collaboration_success_rate*100:.1f}%")
        
        # Stress test analysis
        if 'stress_test_results' in results:
            stress_results = results['stress_test_results']
            logger.info("\n💥 STRESS TEST ANALYSIS")
            logger.info("-" * 50)
            
            if stress_results:
                logger.info(f"Maximum agents tested: {max(m.concurrent_agents for m in stress_results)}")
                logger.info(f"Maximum throughput achieved: {max(m.requests_per_second for m in stress_results):.2f} RPS")
                
                # Find breaking point
                breaking_point = None
                for metrics in stress_results:
                    if metrics.error_rate > 0.2 or metrics.avg_response_time > 10.0:
                        breaking_point = metrics
                        break
                
                if breaking_point:
                    logger.info(f"System stress point: {breaking_point.concurrent_agents} agents")
                    logger.info(f"Stress indicators: {breaking_point.error_rate*100:.1f}% error rate, {breaking_point.avg_response_time:.2f}s avg latency")
                else:
                    logger.info("No clear breaking point found in stress test range")
        
        # Performance recommendations
        logger.info("\n💡 PERFORMANCE RECOMMENDATIONS")
        logger.info("-" * 50)
        
        if standard_results:
            avg_error_rate = statistics.mean(m.error_rate for m in standard_results.values())
            avg_latency = statistics.mean(m.avg_response_time for m in standard_results.values())
            max_memory = max(m.memory_peak_mb for m in standard_results.values())
            
            if avg_error_rate > 0.1:
                logger.info("⚠️  High error rate detected - consider improving error handling and retries")
            
            if avg_latency > 5.0:
                logger.info("⚠️  High average latency - consider optimizing processing pipeline")
            
            if max_memory > 1000:
                logger.info("⚠️  High memory usage - consider implementing memory optimization")
            
            # Find best collaboration mode
            collab_modes = {}
            for name, metrics in standard_results.items():
                if 'independent' in name:
                    collab_modes['independent'] = metrics.requests_per_second
                elif 'coordinated' in name:
                    collab_modes['coordinated'] = metrics.requests_per_second
                elif 'competitive' in name:
                    collab_modes['competitive'] = metrics.requests_per_second
            
            if collab_modes:
                best_mode = max(collab_modes.items(), key=lambda x: x[1])
                logger.info(f"🏆 Best collaboration mode: {best_mode[0]} ({best_mode[1]:.2f} RPS)")
        
        logger.info("\n✅ Collaborative load testing analysis complete!")
        
        # Save results
        self._save_load_test_results(results)
    
    def _save_load_test_results(self, results: Dict[str, Any]):
        """Save load test results to JSON file."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"collaborative_load_test_results_{timestamp}.json"
            
            # Convert results to JSON-serializable format
            json_results = {}
            
            for key, value in results.items():
                if key == 'stress_test_results':
                    json_results[key] = [
                        {
                            'test_name': m.test_name,
                            'duration_seconds': m.duration_seconds,
                            'total_requests': m.total_requests,
                            'successful_requests': m.successful_requests,
                            'failed_requests': m.failed_requests,
                            'requests_per_second': m.requests_per_second,
                            'avg_response_time': m.avg_response_time,
                            'error_rate': m.error_rate,
                            'memory_peak_mb': m.memory_peak_mb,
                            'cpu_peak_percent': m.cpu_peak_percent,
                            'concurrent_agents': m.concurrent_agents,
                            'collaboration_success_rate': m.collaboration_success_rate
                        }
                        for m in value
                    ]
                elif isinstance(value, LoadTestMetrics):
                    json_results[key] = {
                        'test_name': value.test_name,
                        'duration_seconds': value.duration_seconds,
                        'total_requests': value.total_requests,
                        'successful_requests': value.successful_requests,
                        'failed_requests': value.failed_requests,
                        'requests_per_second': value.requests_per_second,
                        'avg_response_time': value.avg_response_time,
                        'p50_response_time': value.p50_response_time,
                        'p95_response_time': value.p95_response_time,
                        'p99_response_time': value.p99_response_time,
                        'max_response_time': value.max_response_time,
                        'error_rate': value.error_rate,
                        'memory_peak_mb': value.memory_peak_mb,
                        'cpu_peak_percent': value.cpu_peak_percent,
                        'concurrent_agents': value.concurrent_agents,
                        'collaboration_success_rate': value.collaboration_success_rate
                    }
            
            with open(filename, 'w') as f:
                json.dump({
                    'load_test_run': {
                        'timestamp': datetime.now().isoformat(),
                        'system_info': {
                            'cpu_count': psutil.cpu_count(),
                            'memory_total_gb': psutil.virtual_memory().total / (1024**3)
                        },
                        'results': json_results
                    }
                }, f, indent=2)
            
            logger.info(f"💾 Load test results saved to: {filename}")
            
        except Exception as e:
            logger.warning(f"Failed to save load test results: {e}")


# Standalone test runner
if __name__ == "__main__":
    async def main():
        """Main entry point for collaborative load testing."""
        load_tester = CollaborativeLoadTester()
        results = await load_tester.run_comprehensive_load_tests()
        
        if results:
            logger.info(f"\n🎯 Successfully completed collaborative load testing!")
            logger.info(f"📊 {len([k for k, v in results.items() if k != 'stress_test_results'])} scenarios tested")
            
            if 'stress_test_results' in results:
                logger.info(f"💥 Stress test completed with {len(results['stress_test_results'])} levels")
        else:
            logger.error("❌ No load tests completed successfully")
    
    asyncio.run(main())