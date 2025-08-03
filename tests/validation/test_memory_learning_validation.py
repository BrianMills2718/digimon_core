#!/usr/bin/env python3
"""
End-to-End Memory Learning Validation

Long-term validation of agent memory learning capabilities including pattern recognition,
adaptation over time, cross-domain learning transfer, and memory persistence.
"""

import asyncio
import logging
import time
import json
import statistics
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import tempfile
import csv

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
class LearningSession:
    """Represents a learning session with specific parameters."""
    session_id: str
    domain: str
    complexity: str
    document_count: int
    expected_improvement: float
    timestamp: datetime


@dataclass
class PerformanceSnapshot:
    """Performance metrics at a specific point in time."""
    session_id: str
    timestamp: datetime
    avg_execution_time: float
    success_rate: float
    entities_per_document: float
    confidence_score: float
    memory_patterns_count: int
    reasoning_improvements: int


@dataclass
class LearningTrend:
    """Analysis of learning trends over time."""
    domain: str
    improvement_rate: float
    stability_score: float
    transfer_effectiveness: float
    memory_utilization: float
    pattern_discovery_rate: float


class MemoryLearningValidator:
    """Comprehensive validation of memory learning capabilities."""
    
    def __init__(self):
        self.learning_history = []
        self.performance_snapshots = []
        self.agent = None
        self.enhanced_tools = None
        self.service_manager = None
        self.message_bus = None
        
    async def setup_learning_environment(self) -> Dict[str, Any]:
        """Set up environment for long-term learning validation."""
        if not IMPORTS_AVAILABLE:
            raise RuntimeError("Required modules not available")
        
        env = {}
        
        # Initialize core services
        env['service_manager'] = ServiceManager()
        await env['service_manager'].initialize()
        
        # Initialize message bus
        env['message_bus'] = MessageBus()
        
        # Initialize enhanced tools with persistent memory
        env['enhanced_tools'] = EnhancedMCPTools(
            service_manager=env['service_manager'],
            agent_id="learning_validator",
            memory_config={
                "enable_memory": True,
                "max_memories": 5000,  # Large memory for learning
                "consolidation_threshold": 50,
                "cleanup_interval": 7200,  # 2 hours
                "similarity_threshold": 0.6
            },
            reasoning_config={
                "enable_reasoning": True,
                "confidence_threshold": 0.6,  # Lower threshold for learning
                "default_reasoning_type": "adaptive"
            },
            communication_config={"enable_broadcast": True},
            message_bus=env['message_bus']
        )
        
        # Initialize learning-focused agent
        mcp_adapter = MCPToolAdapter()
        env['agent'] = DocumentAgent(
            mcp_adapter=mcp_adapter,
            agent_id="learning_validation_agent",
            memory_config={
                "enable_memory": True,
                "max_memories": 3000,
                "consolidation_threshold": 100,
                "learning_rate": 0.1,  # Faster learning for validation
                "retention_policy": "adaptive"
            },
            reasoning_config={
                "enable_reasoning": True,
                "confidence_threshold": 0.6,
                "learning_enabled": True,
                "adaptation_rate": 0.15
            },
            communication_config={"enable_broadcast": True},
            message_bus=env['message_bus']
        )
        
        # Store references for cleanup
        self.agent = env['agent']
        self.enhanced_tools = env['enhanced_tools']
        self.service_manager = env['service_manager']
        self.message_bus = env['message_bus']
        
        logger.info("✅ Learning validation environment initialized")
        return env
    
    def create_progressive_learning_documents(self) -> Dict[str, List[Dict[str, Any]]]:
        """Create documents designed for progressive learning validation."""
        
        # Phase 1: Simple technology documents (baseline learning)
        technology_docs = []
        tech_templates = [
            "{company} announced a partnership with {partner} to develop {technology} solutions.",
            "Researchers at {university} published breakthrough findings on {research_area}.",
            "{person} joined {organization} as {role} to lead {initiative}.",
            "The collaboration between {org1} and {org2} focuses on {domain} applications.",
            "New funding of ${amount} million supports {project} research at {institution}."
        ]
        
        tech_entities = {
            'company': ['Microsoft', 'Google', 'Apple', 'Amazon', 'Tesla', 'Meta', 'NVIDIA', 'IBM'],
            'partner': ['Stanford', 'MIT', 'Harvard', 'Berkeley', 'CMU', 'Caltech', 'Oxford', 'Cambridge'],
            'university': ['Stanford University', 'MIT', 'Harvard University', 'UC Berkeley', 'Carnegie Mellon'],
            'person': ['Dr. Sarah Chen', 'Prof. Michael Rodriguez', 'Dr. Lisa Wang', 'Prof. David Kim', 'Dr. Anna Martinez'],
            'organization': ['OpenAI', 'Anthropic', 'DeepMind', 'Research Lab', 'Innovation Center'],
            'role': ['Chief Scientist', 'Research Director', 'VP Engineering', 'Lead Researcher', 'Principal Scientist'],
            'technology': ['AI', 'machine learning', 'quantum computing', 'robotics', 'neural networks'],
            'research_area': ['natural language processing', 'computer vision', 'reinforcement learning', 'deep learning'],
            'initiative': ['AI safety research', 'autonomous systems', 'healthcare AI', 'educational technology'],
            'org1': ['Google', 'Microsoft', 'Apple', 'Amazon'],
            'org2': ['Stanford', 'MIT', 'Harvard', 'Berkeley'],
            'domain': ['healthcare', 'education', 'transportation', 'finance'],
            'amount': ['10', '25', '50', '75', '100'],
            'project': ['quantum AI', 'neuromorphic computing', 'edge AI', 'federated learning'],
            'institution': ['Research Institute', 'Technology Center', 'Innovation Lab', 'Science Foundation']
        }
        
        for i in range(20):
            template = tech_templates[i % len(tech_templates)]
            content = template
            
            for key, values in tech_entities.items():
                if f'{{{key}}}' in content:
                    content = content.replace(f'{{{key}}}', values[i % len(values)])
            
            technology_docs.append({
                'id': f'tech_learning_{i:02d}',
                'title': f'Technology Document {i+1}',
                'content': content,
                'domain': 'technology',
                'complexity': 'simple',
                'phase': 'baseline',
                'expected_entities': 3 + (i % 3),
                'learning_objectives': ['entity_recognition', 'pattern_identification']
            })
        
        # Phase 2: Healthcare documents (domain transfer)
        healthcare_docs = []
        health_templates = [
            "{hospital} collaborates with {pharma_company} on {treatment} research for {condition}.",
            "Dr. {doctor} from {medical_center} leads clinical trials for {therapy} treatment.",
            "{research_institute} receives ${funding} million grant for {medical_research} studies.",
            "The partnership between {health_org} and {tech_company} develops {health_tech} solutions.",
            "New {medical_device} technology by {manufacturer} improves {medical_procedure} outcomes."
        ]
        
        health_entities = {
            'hospital': ['Mayo Clinic', 'Cleveland Clinic', 'Johns Hopkins', 'Mass General', 'UCLA Medical'],
            'pharma_company': ['Pfizer', 'Johnson & Johnson', 'Roche', 'Novartis', 'Merck'],
            'medical_center': ['Stanford Medical', 'Harvard Medical', 'UCSF Medical', 'NYU Medical'],
            'doctor': ['Dr. Emily Johnson', 'Dr. Robert Chen', 'Dr. Maria Garcia', 'Dr. James Wilson'],
            'research_institute': ['NIH', 'Cancer Research Institute', 'Heart Institute', 'Brain Research Center'],
            'health_org': ['WHO', 'CDC', 'FDA', 'Health Department'],
            'tech_company': ['Google Health', 'Apple Health', 'Microsoft Healthcare', 'IBM Watson Health'],
            'treatment': ['immunotherapy', 'gene therapy', 'precision medicine', 'targeted therapy'],
            'condition': ['cancer', 'diabetes', 'heart disease', 'neurological disorders'],
            'therapy': ['CAR-T cell', 'monoclonal antibody', 'stem cell', 'regenerative'],
            'funding': ['15', '30', '50', '75', '100'],
            'medical_research': ['oncology', 'cardiology', 'neurology', 'immunology'],
            'health_tech': ['diagnostic AI', 'telemedicine', 'health monitoring', 'drug discovery AI'],
            'medical_device': ['surgical robot', 'diagnostic scanner', 'monitoring system', 'treatment device'],
            'manufacturer': ['Medtronic', 'Abbott', 'Boston Scientific', 'Siemens Healthineers'],
            'medical_procedure': ['surgery', 'diagnosis', 'treatment', 'monitoring']
        }
        
        for i in range(15):
            template = health_templates[i % len(health_templates)]
            content = template
            
            for key, values in health_entities.items():
                if f'{{{key}}}' in content:
                    content = content.replace(f'{{{key}}}', values[i % len(values)])
            
            healthcare_docs.append({
                'id': f'health_learning_{i:02d}',
                'title': f'Healthcare Document {i+1}',
                'content': content,
                'domain': 'healthcare',
                'complexity': 'medium',
                'phase': 'transfer',
                'expected_entities': 4 + (i % 3),
                'learning_objectives': ['domain_transfer', 'pattern_adaptation', 'cross_domain_learning']
            })
        
        # Phase 3: Complex multi-domain documents (integration learning)
        complex_docs = []
        complex_template = """
        The groundbreaking collaboration between {tech_company}, {university}, and {hospital} 
        represents a major advancement in {field}. Led by {tech_leader} from {tech_company}, 
        {academic_leader} from {university}, and {medical_leader} from {hospital}, this initiative 
        combines {technology} with {medical_expertise} to address {healthcare_challenge}.
        
        The ${funding} million project, funded by {funder}, aims to develop {solution} that can 
        {benefit}. The research team includes {researcher1}, {researcher2}, and {researcher3}, 
        who will focus on {research_area1}, {research_area2}, and {research_area3} respectively.
        
        Expected outcomes include {outcome1}, {outcome2}, and {outcome3}, with potential 
        applications in {application1}, {application2}, and {application3}.
        """
        
        complex_entities = {
            'tech_company': ['Google DeepMind', 'Microsoft Research', 'IBM Watson', 'NVIDIA Healthcare'],
            'university': ['Stanford Medicine', 'Harvard Medical School', 'MIT CSAIL', 'UC Berkeley'],
            'hospital': ['Mayo Clinic', 'Cleveland Clinic', 'Johns Hopkins', 'Mass General Brigham'],
            'field': ['AI-powered healthcare', 'precision medicine', 'digital therapeutics', 'medical AI'],
            'tech_leader': ['Dr. Sarah Chen', 'Prof. Michael Rodriguez', 'Dr. Lisa Wang'],
            'academic_leader': ['Prof. David Kim', 'Dr. Emily Johnson', 'Prof. Maria Garcia'],
            'medical_leader': ['Dr. Robert Wilson', 'Dr. Jennifer Martinez', 'Prof. James Taylor'],
            'technology': ['deep learning', 'computer vision', 'natural language processing', 'robotics'],
            'medical_expertise': ['clinical research', 'diagnostic imaging', 'genomics', 'drug discovery'],
            'healthcare_challenge': ['early disease detection', 'personalized treatment', 'drug resistance', 'rare diseases'],
            'funding': ['50', '75', '100', '150', '200'],
            'funder': ['NIH', 'NSF', 'Gates Foundation', 'private investors'],
            'solution': ['AI diagnostic platform', 'personalized medicine system', 'robotic surgery platform'],
            'benefit': ['improve accuracy', 'reduce costs', 'accelerate discovery', 'enhance outcomes'],
            'researcher1': ['Dr. Alex Thompson', 'Prof. Diana Foster', 'Dr. Kevin Brown'],
            'researcher2': ['Dr. Michelle Davis', 'Prof. Steven Clark', 'Dr. Nicole Taylor'],
            'researcher3': ['Prof. Hassan Al-Rashid', 'Dr. Isabella Santos', 'Prof. Jacob Moore'],
            'research_area1': ['machine learning algorithms', 'clinical data analysis', 'imaging processing'],
            'research_area2': ['patient monitoring', 'treatment optimization', 'drug interaction modeling'],
            'research_area3': ['outcome prediction', 'personalization', 'safety validation'],
            'outcome1': ['improved diagnostic accuracy', 'faster treatment selection', 'reduced side effects'],
            'outcome2': ['cost reduction', 'better patient outcomes', 'enhanced quality of care'],
            'outcome3': ['new treatment discoveries', 'personalized therapies', 'predictive capabilities'],
            'application1': ['cancer treatment', 'cardiovascular care', 'neurological disorders'],
            'application2': ['emergency medicine', 'surgical planning', 'mental health'],
            'application3': ['preventive care', 'chronic disease management', 'pediatric medicine']
        }
        
        for i in range(10):
            content = complex_template
            
            for key, values in complex_entities.items():
                if f'{{{key}}}' in content:
                    content = content.replace(f'{{{key}}}', values[i % len(values)])
            
            content = content.strip()
            
            complex_docs.append({
                'id': f'complex_learning_{i:02d}',
                'title': f'Complex Integration Document {i+1}',
                'content': content,
                'domain': 'healthcare_technology',
                'complexity': 'complex',
                'phase': 'integration',
                'expected_entities': 15 + (i % 5),
                'learning_objectives': ['complex_reasoning', 'multi_domain_integration', 'advanced_pattern_recognition']
            })
        
        return {
            'baseline': technology_docs,
            'transfer': healthcare_docs,
            'integration': complex_docs
        }
    
    async def run_learning_session(self, documents: List[Dict[str, Any]], session: LearningSession) -> PerformanceSnapshot:
        """Run a single learning session and capture performance metrics."""
        logger.info(f"📚 Running learning session: {session.session_id}")
        
        execution_times = []
        success_count = 0
        total_entities = 0
        confidence_scores = []
        
        session_start = time.time()
        
        for i, doc in enumerate(documents):
            task = Task(
                task_type="document_processing",
                parameters={
                    "text": doc["content"],
                    "domain": doc["domain"],
                    "document_id": doc["id"],
                    "complexity": doc["complexity"]
                },
                context={
                    "learning_session": session.session_id,
                    "phase": doc["phase"],
                    "learning_objectives": doc["learning_objectives"],
                    "document_index": i
                }
            )
            
            start_time = time.time()
            result = await self.agent.execute(task)
            execution_time = time.time() - start_time
            
            execution_times.append(execution_time)
            
            if result.success:
                success_count += 1
                entities = result.data.get("entities", []) if result.data else []
                total_entities += len(entities)
                
                # Extract confidence scores
                for entity in entities:
                    if "confidence" in entity:
                        confidence_scores.append(entity["confidence"])
            
            # Brief pause for memory consolidation
            if i % 5 == 0:
                await asyncio.sleep(0.1)
        
        # Get memory status
        memory_patterns = 0
        reasoning_improvements = 0
        
        if hasattr(self.agent, 'memory') and self.agent.memory:
            try:
                memory_status = self.agent.memory.get_status()
                memory_patterns = memory_status.get('patterns_stored', 0)
            except:
                pass
        
        if hasattr(self.agent, 'reasoning_engine') and self.agent.reasoning_engine:
            try:
                reasoning_status = self.agent.reasoning_engine.get_performance_metrics()
                reasoning_improvements = reasoning_status.get('improvements_applied', 0)
            except:
                pass
        
        # Create performance snapshot
        snapshot = PerformanceSnapshot(
            session_id=session.session_id,
            timestamp=datetime.now(),
            avg_execution_time=statistics.mean(execution_times) if execution_times else 0,
            success_rate=success_count / len(documents) if documents else 0,
            entities_per_document=total_entities / success_count if success_count > 0 else 0,
            confidence_score=statistics.mean(confidence_scores) if confidence_scores else 0,
            memory_patterns_count=memory_patterns,
            reasoning_improvements=reasoning_improvements
        )
        
        self.performance_snapshots.append(snapshot)
        
        logger.info(f"  ✅ Session completed: {success_count}/{len(documents)} successful, "
                   f"avg time: {snapshot.avg_execution_time:.3f}s")
        
        return snapshot
    
    async def validate_learning_progression(self) -> Dict[str, Any]:
        """Validate learning progression across multiple phases."""
        logger.info("🧠 Starting learning progression validation...")
        
        # Create progressive learning documents
        doc_phases = self.create_progressive_learning_documents()
        
        # Define learning sessions
        sessions = [
            # Baseline learning phase
            LearningSession("baseline_1", "technology", "simple", 10, 0.1, datetime.now()),
            LearningSession("baseline_2", "technology", "simple", 10, 0.15, datetime.now()),
            
            # Domain transfer phase
            LearningSession("transfer_1", "healthcare", "medium", 8, 0.1, datetime.now()),
            LearningSession("transfer_2", "healthcare", "medium", 7, 0.15, datetime.now()),
            
            # Integration phase
            LearningSession("integration_1", "healthcare_technology", "complex", 5, 0.2, datetime.now()),
            LearningSession("integration_2", "healthcare_technology", "complex", 5, 0.25, datetime.now())
        ]
        
        validation_results = {}
        
        for i, session in enumerate(sessions):
            # Select appropriate documents
            if session.domain == "technology":
                docs = doc_phases['baseline'][:session.document_count]
            elif session.domain == "healthcare":
                docs = doc_phases['transfer'][:session.document_count]
            else:
                docs = doc_phases['integration'][:session.document_count]
            
            # Run learning session
            snapshot = await self.run_learning_session(docs, session)
            validation_results[session.session_id] = snapshot
            
            # Add to learning history
            self.learning_history.append(session)
            
            # Brief pause between sessions for memory consolidation
            await asyncio.sleep(2)
            
            logger.info(f"  📊 Session {i+1}/{len(sessions)} completed")
        
        # Analyze learning trends
        trends = self._analyze_learning_trends()
        validation_results['learning_trends'] = trends
        
        return validation_results
    
    async def validate_memory_persistence(self) -> Dict[str, Any]:
        """Validate memory persistence across agent restarts."""
        logger.info("💾 Validating memory persistence...")
        
        # Store some specific learning patterns
        test_documents = [
            {
                'id': 'persistence_test_1',
                'content': 'Apple Inc. partners with Stanford University for AI research led by Dr. Sarah Chen.',
                'domain': 'technology',
                'complexity': 'simple'
            },
            {
                'id': 'persistence_test_2', 
                'content': 'Microsoft collaborates with Harvard Medical School on healthcare AI development.',
                'domain': 'healthcare_technology',
                'complexity': 'medium'
            }
        ]
        
        # Initial processing
        initial_performance = []
        for doc in test_documents:
            task = Task(
                task_type="document_processing",
                parameters={
                    "text": doc["content"],
                    "domain": doc["domain"],
                    "document_id": doc["id"]
                },
                context={"persistence_test": "initial"}
            )
            
            start_time = time.time()
            result = await self.agent.execute(task)
            execution_time = time.time() - start_time
            
            initial_performance.append({
                'document_id': doc['id'],
                'execution_time': execution_time,
                'success': result.success,
                'entities_found': len(result.data.get("entities", [])) if result.success and result.data else 0
            })
        
        # Get pre-restart memory state
        pre_restart_memory = None
        if hasattr(self.agent, 'memory') and self.agent.memory:
            try:
                pre_restart_memory = self.agent.memory.get_status()
            except:
                pre_restart_memory = {'patterns_stored': 0}
        
        # Simulate agent restart by creating new agent instance
        logger.info("  🔄 Simulating agent restart...")
        
        # Create new agent with same configuration
        mcp_adapter = MCPToolAdapter()
        new_agent = DocumentAgent(
            mcp_adapter=mcp_adapter,
            agent_id="learning_validation_agent",  # Same ID for memory access
            memory_config={
                "enable_memory": True,
                "max_memories": 3000,
                "consolidation_threshold": 100,
                "learning_rate": 0.1
            },
            reasoning_config={
                "enable_reasoning": True,
                "confidence_threshold": 0.6,
                "learning_enabled": True
            },
            communication_config={"enable_broadcast": True},
            message_bus=self.message_bus
        )
        
        # Replace agent reference
        old_agent = self.agent
        self.agent = new_agent
        
        # Test processing with restarted agent
        post_restart_performance = []
        for doc in test_documents:
            task = Task(
                task_type="document_processing",
                parameters={
                    "text": doc["content"],
                    "domain": doc["domain"],
                    "document_id": f"{doc['id']}_restart"
                },
                context={"persistence_test": "post_restart"}
            )
            
            start_time = time.time()
            result = await self.agent.execute(task)
            execution_time = time.time() - start_time
            
            post_restart_performance.append({
                'document_id': doc['id'],
                'execution_time': execution_time,
                'success': result.success,
                'entities_found': len(result.data.get("entities", [])) if result.success and result.data else 0
            })
        
        # Get post-restart memory state
        post_restart_memory = None
        if hasattr(self.agent, 'memory') and self.agent.memory:
            try:
                post_restart_memory = self.agent.memory.get_status()
            except:
                post_restart_memory = {'patterns_stored': 0}
        
        # Analyze persistence
        persistence_analysis = {
            'memory_persisted': (post_restart_memory and pre_restart_memory and 
                               post_restart_memory.get('patterns_stored', 0) >= 
                               pre_restart_memory.get('patterns_stored', 0) * 0.8),
            'performance_maintained': True,
            'initial_performance': initial_performance,
            'post_restart_performance': post_restart_performance,
            'pre_restart_memory': pre_restart_memory,
            'post_restart_memory': post_restart_memory
        }
        
        # Check if performance was maintained
        for i, (initial, restart) in enumerate(zip(initial_performance, post_restart_performance)):
            time_ratio = restart['execution_time'] / initial['execution_time'] if initial['execution_time'] > 0 else 1
            entity_ratio = restart['entities_found'] / max(1, initial['entities_found'])
            
            if time_ratio > 1.5 or entity_ratio < 0.7:
                persistence_analysis['performance_maintained'] = False
                break
        
        logger.info(f"  📊 Memory persistence: {'✅' if persistence_analysis['memory_persisted'] else '❌'}")
        logger.info(f"  📊 Performance maintained: {'✅' if persistence_analysis['performance_maintained'] else '❌'}")
        
        return persistence_analysis
    
    async def validate_cross_domain_transfer(self) -> Dict[str, Any]:
        """Validate learning transfer between different domains."""
        logger.info("🔄 Validating cross-domain learning transfer...")
        
        # Technology domain training
        tech_docs = [
            "Microsoft partners with Stanford for AI research.",
            "Google collaborates with MIT on quantum computing.",
            "Apple works with UC Berkeley on chip design."
        ]
        
        # Train on technology domain
        tech_performance = []
        for i, content in enumerate(tech_docs):
            task = Task(
                task_type="document_processing",
                parameters={
                    "text": content,
                    "domain": "technology",
                    "document_id": f"tech_training_{i}"
                },
                context={"transfer_test": "technology_training"}
            )
            
            start_time = time.time()
            result = await self.agent.execute(task)
            execution_time = time.time() - start_time
            
            tech_performance.append({
                'execution_time': execution_time,
                'success': result.success,
                'entities_found': len(result.data.get("entities", [])) if result.success and result.data else 0
            })
        
        # Test transfer to healthcare domain
        health_docs = [
            "Mayo Clinic collaborates with IBM on medical AI.",
            "Johns Hopkins partners with Google Health for diagnostics.",
            "Stanford Medicine works with Microsoft on patient care."
        ]
        
        health_performance = []
        for i, content in enumerate(health_docs):
            task = Task(
                task_type="document_processing",
                parameters={
                    "text": content,
                    "domain": "healthcare",
                    "document_id": f"health_transfer_{i}"
                },
                context={"transfer_test": "healthcare_transfer"}
            )
            
            start_time = time.time()
            result = await self.agent.execute(task)
            execution_time = time.time() - start_time
            
            health_performance.append({
                'execution_time': execution_time,
                'success': result.success,
                'entities_found': len(result.data.get("entities", [])) if result.success and result.data else 0
            })
        
        # Analyze transfer effectiveness
        tech_avg_time = statistics.mean([p['execution_time'] for p in tech_performance])
        health_avg_time = statistics.mean([p['execution_time'] for p in health_performance])
        
        tech_avg_entities = statistics.mean([p['entities_found'] for p in tech_performance])
        health_avg_entities = statistics.mean([p['entities_found'] for p in health_performance])
        
        transfer_analysis = {
            'technology_performance': {
                'avg_execution_time': tech_avg_time,
                'avg_entities_found': tech_avg_entities,
                'success_rate': sum(p['success'] for p in tech_performance) / len(tech_performance)
            },
            'healthcare_performance': {
                'avg_execution_time': health_avg_time,
                'avg_entities_found': health_avg_entities,
                'success_rate': sum(p['success'] for p in health_performance) / len(health_performance)
            },
            'transfer_effectiveness': {
                'time_penalty': (health_avg_time - tech_avg_time) / tech_avg_time if tech_avg_time > 0 else 0,
                'entity_retention': health_avg_entities / tech_avg_entities if tech_avg_entities > 0 else 0,
                'overall_transfer_score': max(0, 1 - abs(health_avg_time - tech_avg_time) / max(tech_avg_time, health_avg_time)) if max(tech_avg_time, health_avg_time) > 0 else 0
            }
        }
        
        logger.info(f"  📊 Transfer effectiveness: {transfer_analysis['transfer_effectiveness']['overall_transfer_score']:.2f}")
        
        return transfer_analysis
    
    def _analyze_learning_trends(self) -> Dict[str, LearningTrend]:
        """Analyze learning trends from performance snapshots."""
        trends_by_domain = {}
        
        # Group snapshots by domain
        domain_snapshots = {}
        for snapshot in self.performance_snapshots:
            session = next((s for s in self.learning_history if s.session_id == snapshot.session_id), None)
            if session:
                domain = session.domain
                if domain not in domain_snapshots:
                    domain_snapshots[domain] = []
                domain_snapshots[domain].append((session, snapshot))
        
        # Analyze trends for each domain
        for domain, snapshots in domain_snapshots.items():
            if len(snapshots) < 2:
                continue
            
            # Sort by timestamp
            snapshots.sort(key=lambda x: x[1].timestamp)
            
            # Calculate improvement rate
            execution_times = [s[1].avg_execution_time for s in snapshots]
            success_rates = [s[1].success_rate for s in snapshots]
            confidence_scores = [s[1].confidence_score for s in snapshots]
            
            # Linear regression for improvement rate
            if len(execution_times) >= 2:
                time_improvement = (execution_times[0] - execution_times[-1]) / execution_times[0] if execution_times[0] > 0 else 0
                success_improvement = success_rates[-1] - success_rates[0]
                confidence_improvement = confidence_scores[-1] - confidence_scores[0] if confidence_scores[0] > 0 else 0
                
                improvement_rate = (success_improvement + confidence_improvement + time_improvement) / 3
            else:
                improvement_rate = 0
            
            # Stability score (consistency of performance)
            stability_score = 1 - (statistics.stdev(success_rates) if len(success_rates) > 1 else 0)
            
            # Memory utilization
            memory_patterns = [s[1].memory_patterns_count for s in snapshots]
            memory_utilization = memory_patterns[-1] / max(1, max(memory_patterns)) if memory_patterns else 0
            
            # Pattern discovery rate
            pattern_discovery_rate = (memory_patterns[-1] - memory_patterns[0]) / len(snapshots) if len(snapshots) > 1 and memory_patterns else 0
            
            trends_by_domain[domain] = LearningTrend(
                domain=domain,
                improvement_rate=improvement_rate,
                stability_score=stability_score,
                transfer_effectiveness=0.8,  # Placeholder - would need cross-domain analysis
                memory_utilization=memory_utilization,
                pattern_discovery_rate=pattern_discovery_rate
            )
        
        return trends_by_domain
    
    async def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run comprehensive memory learning validation."""
        logger.info("🚀 Starting Comprehensive Memory Learning Validation")
        logger.info("=" * 70)
        
        if not IMPORTS_AVAILABLE:
            logger.error("❌ Required modules not available")
            return {}
        
        try:
            # Set up learning environment
            env = await self.setup_learning_environment()
            
            validation_results = {}
            
            # 1. Learning progression validation
            logger.info("\n1️⃣  Testing learning progression...")
            progression_results = await self.validate_learning_progression()
            validation_results['learning_progression'] = progression_results
            
            # 2. Memory persistence validation
            logger.info("\n2️⃣  Testing memory persistence...")
            persistence_results = await self.validate_memory_persistence()
            validation_results['memory_persistence'] = persistence_results
            
            # 3. Cross-domain transfer validation
            logger.info("\n3️⃣  Testing cross-domain transfer...")
            transfer_results = await self.validate_cross_domain_transfer()
            validation_results['cross_domain_transfer'] = transfer_results
            
            # 4. Generate comprehensive report
            self._generate_learning_validation_report(validation_results)
            
            return validation_results
            
        except Exception as e:
            logger.error(f"❌ Memory learning validation failed: {e}")
            import traceback
            traceback.print_exc()
            return {}
        
        finally:
            # Cleanup
            if self.message_bus:
                await self.message_bus.cleanup()
    
    def _generate_learning_validation_report(self, results: Dict[str, Any]):
        """Generate comprehensive learning validation report."""
        logger.info("\n" + "=" * 70)
        logger.info("📊 MEMORY LEARNING VALIDATION REPORT")
        logger.info("=" * 70)
        
        if not results:
            logger.info("❌ No validation results available")
            return
        
        # Learning progression analysis
        if 'learning_progression' in results:
            logger.info("\n📈 LEARNING PROGRESSION ANALYSIS")
            logger.info("-" * 40)
            
            progression = results['learning_progression']
            if 'learning_trends' in progression:
                trends = progression['learning_trends']
                
                for domain, trend in trends.items():
                    logger.info(f"\n{domain.upper()} DOMAIN:")
                    logger.info(f"  Improvement Rate: {trend.improvement_rate:+.3f}")
                    logger.info(f"  Stability Score: {trend.stability_score:.3f}")
                    logger.info(f"  Memory Utilization: {trend.memory_utilization:.3f}")
                    logger.info(f"  Pattern Discovery Rate: {trend.pattern_discovery_rate:.2f} patterns/session")
            
            # Session performance summary
            sessions = [k for k in progression.keys() if k != 'learning_trends']
            if sessions:
                logger.info(f"\n📊 {len(sessions)} learning sessions completed")
                
                avg_success_rate = statistics.mean([
                    progression[s].success_rate for s in sessions 
                    if hasattr(progression[s], 'success_rate')
                ])
                logger.info(f"Average success rate: {avg_success_rate:.1%}")
        
        # Memory persistence analysis
        if 'memory_persistence' in results:
            logger.info("\n💾 MEMORY PERSISTENCE ANALYSIS")
            logger.info("-" * 40)
            
            persistence = results['memory_persistence']
            
            memory_status = "✅ PASSED" if persistence.get('memory_persisted', False) else "❌ FAILED"
            performance_status = "✅ PASSED" if persistence.get('performance_maintained', False) else "❌ FAILED"
            
            logger.info(f"Memory Persistence: {memory_status}")
            logger.info(f"Performance Maintenance: {performance_status}")
            
            if persistence.get('pre_restart_memory') and persistence.get('post_restart_memory'):
                pre_patterns = persistence['pre_restart_memory'].get('patterns_stored', 0)
                post_patterns = persistence['post_restart_memory'].get('patterns_stored', 0)
                retention_rate = post_patterns / max(1, pre_patterns)
                logger.info(f"Pattern Retention Rate: {retention_rate:.1%}")
        
        # Cross-domain transfer analysis
        if 'cross_domain_transfer' in results:
            logger.info("\n🔄 CROSS-DOMAIN TRANSFER ANALYSIS")
            logger.info("-" * 40)
            
            transfer = results['cross_domain_transfer']
            
            if 'transfer_effectiveness' in transfer:
                effectiveness = transfer['transfer_effectiveness']
                
                logger.info(f"Time Penalty: {effectiveness.get('time_penalty', 0):+.1%}")
                logger.info(f"Entity Retention: {effectiveness.get('entity_retention', 0):.1%}")
                logger.info(f"Overall Transfer Score: {effectiveness.get('overall_transfer_score', 0):.3f}")
                
                if effectiveness.get('overall_transfer_score', 0) > 0.7:
                    logger.info("🏆 Excellent transfer learning capability")
                elif effectiveness.get('overall_transfer_score', 0) > 0.5:
                    logger.info("✅ Good transfer learning capability")
                else:
                    logger.info("⚠️  Limited transfer learning capability")
        
        # Overall validation assessment
        logger.info("\n🎯 OVERALL ASSESSMENT")
        logger.info("-" * 40)
        
        validation_score = 0
        max_score = 0
        
        # Score learning progression
        if 'learning_progression' in results and 'learning_trends' in results['learning_progression']:
            trends = results['learning_progression']['learning_trends']
            if trends:
                avg_improvement = statistics.mean([t.improvement_rate for t in trends.values()])
                avg_stability = statistics.mean([t.stability_score for t in trends.values()])
                
                validation_score += max(0, avg_improvement) * 30  # 30 points for improvement
                validation_score += avg_stability * 20  # 20 points for stability
            max_score += 50
        
        # Score memory persistence
        if 'memory_persistence' in results:
            persistence = results['memory_persistence']
            if persistence.get('memory_persisted', False):
                validation_score += 25
            if persistence.get('performance_maintained', False):
                validation_score += 15
            max_score += 40
        
        # Score cross-domain transfer
        if 'cross_domain_transfer' in results:
            transfer = results['cross_domain_transfer']
            if 'transfer_effectiveness' in transfer:
                transfer_score = transfer['transfer_effectiveness'].get('overall_transfer_score', 0)
                validation_score += transfer_score * 10
            max_score += 10
        
        # Final score
        final_score = (validation_score / max_score * 100) if max_score > 0 else 0
        
        logger.info(f"Learning Validation Score: {validation_score:.1f}/{max_score} ({final_score:.1f}%)")
        
        if final_score >= 80:
            logger.info("🏆 EXCELLENT - Memory learning system is highly effective")
        elif final_score >= 65:
            logger.info("✅ GOOD - Memory learning system is performing well")
        elif final_score >= 50:
            logger.info("⚠️  ACCEPTABLE - Memory learning system has room for improvement")
        else:
            logger.info("❌ NEEDS IMPROVEMENT - Memory learning system requires attention")
        
        # Recommendations
        logger.info("\n💡 RECOMMENDATIONS")
        logger.info("-" * 40)
        
        if final_score < 80:
            logger.info("• Consider increasing memory capacity and consolidation frequency")
            logger.info("• Optimize reasoning algorithms for better pattern recognition")
            logger.info("• Implement more sophisticated cross-domain learning strategies")
        
        if 'cross_domain_transfer' in results:
            transfer_score = results['cross_domain_transfer'].get('transfer_effectiveness', {}).get('overall_transfer_score', 0)
            if transfer_score < 0.6:
                logger.info("• Focus on improving domain transfer mechanisms")
                logger.info("• Implement domain-agnostic feature learning")
        
        logger.info("\n✅ Memory learning validation analysis complete!")
        
        # Save detailed results
        self._save_learning_validation_results(results)
    
    def _save_learning_validation_results(self, results: Dict[str, Any]):
        """Save learning validation results to files."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save JSON results
            json_filename = f"memory_learning_validation_{timestamp}.json"
            
            # Convert complex objects to serializable format
            serializable_results = {}
            
            for key, value in results.items():
                if key == 'learning_progression':
                    serializable_results[key] = {}
                    for subkey, subvalue in value.items():
                        if subkey == 'learning_trends':
                            serializable_results[key][subkey] = {
                                domain: {
                                    'domain': trend.domain,
                                    'improvement_rate': trend.improvement_rate,
                                    'stability_score': trend.stability_score,
                                    'transfer_effectiveness': trend.transfer_effectiveness,
                                    'memory_utilization': trend.memory_utilization,
                                    'pattern_discovery_rate': trend.pattern_discovery_rate
                                }
                                for domain, trend in subvalue.items()
                            }
                        elif hasattr(subvalue, '__dict__'):
                            # Convert dataclass to dict
                            serializable_results[key][subkey] = {
                                attr: getattr(subvalue, attr) 
                                for attr in dir(subvalue) 
                                if not attr.startswith('_') and not callable(getattr(subvalue, attr))
                            }
                        else:
                            serializable_results[key][subkey] = subvalue
                else:
                    serializable_results[key] = value
            
            with open(json_filename, 'w') as f:
                json.dump({
                    'validation_run': {
                        'timestamp': datetime.now().isoformat(),
                        'test_type': 'memory_learning_validation',
                        'results': serializable_results
                    }
                }, f, indent=2, default=str)
            
            logger.info(f"💾 Validation results saved to: {json_filename}")
            
            # Save CSV summary for trend analysis
            csv_filename = f"learning_performance_timeline_{timestamp}.csv"
            
            with open(csv_filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'Session ID', 'Timestamp', 'Domain', 'Phase', 
                    'Avg Execution Time', 'Success Rate', 'Entities Per Doc',
                    'Confidence Score', 'Memory Patterns', 'Reasoning Improvements'
                ])
                
                for snapshot in self.performance_snapshots:
                    session = next((s for s in self.learning_history if s.session_id == snapshot.session_id), None)
                    
                    writer.writerow([
                        snapshot.session_id,
                        snapshot.timestamp.isoformat(),
                        session.domain if session else 'unknown',
                        getattr(session, 'phase', 'unknown') if session else 'unknown',
                        snapshot.avg_execution_time,
                        snapshot.success_rate,
                        snapshot.entities_per_document,
                        snapshot.confidence_score,
                        snapshot.memory_patterns_count,
                        snapshot.reasoning_improvements
                    ])
            
            logger.info(f"📈 Performance timeline saved to: {csv_filename}")
            
        except Exception as e:
            logger.warning(f"Failed to save validation results: {e}")


# Standalone test runner
if __name__ == "__main__":
    async def main():
        """Main entry point for memory learning validation."""
        validator = MemoryLearningValidator()
        results = await validator.run_comprehensive_validation()
        
        if results:
            logger.info(f"\n🎯 Memory learning validation completed successfully!")
            logger.info(f"📊 {len(results)} validation categories tested")
        else:
            logger.error("❌ Memory learning validation failed")
    
    asyncio.run(main())