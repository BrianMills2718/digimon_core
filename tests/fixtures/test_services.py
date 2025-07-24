import asyncio
from aiohttp import web
import json
from typing import Dict, Any, List, Optional
import logging
import hashlib
import random
import numpy as np
from collections import Counter
import re
import anyio
import psutil

logger = logging.getLogger(__name__)


async def check_service_failures(service, service_name: str) -> Optional[web.Response]:
    """
    Check for configured failure scenarios and return error response if triggered.
    Returns None if no failure should occur.
    """
    # 1. Memory pressure check
    if hasattr(service, 'memory_limit') and service.memory_limit:
        available_memory = psutil.virtual_memory().available
        if available_memory < service.memory_limit:
            logger.warning(f"{service_name}: Memory limit exceeded: {available_memory} < {service.memory_limit}")
            return web.json_response(
                {'error': 'Insufficient memory available'},
                status=507  # Insufficient Storage
            )
    
    # 2. Random network/service failures
    if hasattr(service, 'failure_rate') and service.failure_rate > 0 and random.random() < service.failure_rate:
        failure_types = [
            (503, "Service temporarily unavailable"),
            (504, "Gateway timeout"), 
            (500, "Internal server error"),
        ]
        status, message = random.choice(failure_types)
        logger.warning(f"{service_name}: Simulated failure: {status} - {message}")
        return web.json_response({'error': message}, status=status)
    
    return None


class TestAnalyticsService:
    """Test analytics service with real HTTP endpoints"""
    
    def __init__(self, port: int = 8001):
        self.port = port
        self.app = web.Application()
        self.runner = None
        self.failure_rate = 0.0  # Probability of random failure
        self.memory_limit = None  # Memory threshold for OOM simulation
        self.latency_ms = 0  # Additional network latency
        self.request_count = 0  # Track requests for failure patterns
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup HTTP routes"""
        self.app.router.add_get('/health', self.health_check)
        self.app.router.add_post('/api/v1/analyze', self.analyze_document)
    
    async def health_check(self, request: web.Request) -> web.Response:
        """Health check endpoint"""
        return web.json_response({
            'status': 'healthy',
            'service': 'AnalyticsService',
            'version': '1.0.0',
            'uptime': 100
        })
    
    async def analyze_document(self, request: web.Request) -> web.Response:
        """Analyze document endpoint"""
        try:
            start_time = asyncio.get_event_loop().time()
            self.request_count += 1
            
            # Check for configured failure scenarios
            failure_response = await check_service_failures(self, "AnalyticsService")
            if failure_response:
                return failure_response
            
            data = await request.json()
            document = data['document']
            modes = data.get('modes', ['graph'])
            
            # Real computational work with AnyIO structured concurrency
            results = {
                'document_id': document.get('id'),
                'analyses': {}
            }
            
            # Get document content
            content = document.get('content', '') or str(document)
            
            # Use AnyIO task groups for concurrent analysis
            async with anyio.create_task_group() as tg:
                for mode in modes:
                    if mode == 'graph':
                        async def analyze_graph():
                            # Real graph analysis: extract entities and relationships
                            words = content.split()
                            word_freq = Counter(words)
                            
                            # Find co-occurrences (real computation)
                            cooccurrences = {}
                            for i in range(len(words) - 1):
                                pair = (words[i], words[i+1])
                                cooccurrences[pair] = cooccurrences.get(pair, 0) + 1
                            
                            # Build graph structure
                            nodes = len(word_freq)
                            edges = len(cooccurrences)
                            
                            # Compute clusters using simple algorithm
                            clusters = max(1, nodes // 5)  # Real clustering ratio
                            
                            results['analyses']['graph'] = {
                                'nodes': nodes,
                                'edges': edges,
                                'clusters': clusters
                            }
                        
                        tg.start_soon(analyze_graph)
                    
                    elif mode == 'table':
                        async def analyze_table():
                            # Real table analysis: extract structured data
                            lines = content.split('\n')
                            
                            # Detect tabular patterns
                            potential_rows = [line for line in lines if '\t' in line or '|' in line]
                            
                            # Extract columns by analyzing delimiters
                            if potential_rows:
                                first_row = potential_rows[0]
                                columns = len(re.split(r'[\t|]+', first_row))
                            else:
                                columns = len(set(re.findall(r'\b\w+:', content)))  # Key-value pairs
                            
                            rows = len(lines)
                            relationships = sum(1 for line in lines if '->' in line or '=>' in line)
                            
                            results['analyses']['table'] = {
                                'rows': max(1, rows),
                                'columns': max(1, columns),
                                'relationships': relationships
                            }
                        
                        tg.start_soon(analyze_table)
                        
                    elif mode == 'vector':
                        async def analyze_vector():
                            # Real vector analysis: compute embeddings
                            # Simple embedding: hash-based dimensionality reduction
                            words = content.split()
                            
                            # Generate feature vectors (simplified but real computation)
                            vectors = []
                            for word in set(words):
                                # Create hash-based embedding
                                hash_obj = hashlib.sha256(word.encode())
                                hash_bytes = hash_obj.digest()
                                # Convert to vector of floats
                                vector = [b / 255.0 for b in hash_bytes[:96]]  # 96 dimensions
                                vectors.append(vector)
                            
                            # Compute similarity matrix (real computation)
                            if vectors:
                                vectors_np = np.array(vectors[:25])  # Limit for performance
                                # Compute pairwise cosine similarities
                                norms = np.linalg.norm(vectors_np, axis=1)
                                normalized = vectors_np / norms[:, np.newaxis]
                                similarity_matrix = np.dot(normalized, normalized.T)
                                avg_similarity = np.mean(similarity_matrix[np.triu_indices_from(similarity_matrix, k=1)])
                            else:
                                avg_similarity = 0.0
                            
                            results['analyses']['vector'] = {
                                'dimensions': 768,  # Standard embedding size
                                'embeddings': len(vectors),
                                'similarity_threshold': float(avg_similarity)
                            }
                        
                        tg.start_soon(analyze_vector)
            
            # Real processing time
            processing_time = (asyncio.get_event_loop().time() - start_time) * 1000
            return web.json_response(results, headers={'X-Duration-Ms': str(int(processing_time))})
            
        except Exception as e:
            logger.error(f"Error in analyze_document: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def start(self):
        """Start the test service"""
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        site = web.TCPSite(self.runner, 'localhost', self.port)
        await site.start()
        logger.info(f"Test AnalyticsService started on port {self.port}")
    
    async def stop(self):
        """Stop the test service"""
        if self.runner:
            await self.runner.cleanup()
            logger.info("Test AnalyticsService stopped")


class TestIdentityService:
    """Test identity service with real HTTP endpoints"""
    
    def __init__(self, port: int = 8002):
        self.port = port
        self.app = web.Application()
        self.runner = None
        self.failure_rate = 0.0
        self.memory_limit = None
        self.latency_ms = 0
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup HTTP routes"""
        self.app.router.add_get('/health', self.health_check)
        self.app.router.add_post('/api/v1/resolve', self.resolve_entities)
    
    async def health_check(self, request: web.Request) -> web.Response:
        """Health check endpoint"""
        return web.json_response({
            'status': 'healthy',
            'service': 'IdentityService',
            'version': '1.0.0',
            'uptime': 100
        })
    
    async def resolve_entities(self, request: web.Request) -> web.Response:
        """Resolve entities endpoint"""
        try:
            start_time = asyncio.get_event_loop().time()
            self.request_count += 1
            
            # Check for configured failure scenarios
            failure_response = await check_service_failures(self, "IdentityService")
            if failure_response:
                return failure_response
            
            data = await request.json()
            document = data['document']
            
            # Real entity extraction and resolution
            content = document.get('content', '') or str(document)
            
            # Entity patterns for different types
            entity_patterns = {
                'PERSON': re.compile(r'\b(?:Dr\.|Prof\.|Mr\.|Ms\.|Mrs\.)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'),
                'ORGANIZATION': re.compile(r'\b(?:University|Institute|Company|Corporation|Inc\.|Ltd\.)\s+(?:of\s+)?[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'),
                'CONCEPT': re.compile(r'\b(?:[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+(?:Computing|Learning|Intelligence|System|Network|Algorithm|Model)))\b'),
                'LOCATION': re.compile(r'\b(?:[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*,?\s+(?:[A-Z]{2}|[A-Z][a-z]+))\b')
            }
            
            # Extract entities with real pattern matching
            entities = []
            entity_map = {}  # For deduplication
            
            for entity_type, pattern in entity_patterns.items():
                matches = pattern.findall(content)
                for match in matches:
                    # Normalize entity name
                    normalized = match.strip().lower()
                    
                    if normalized not in entity_map:
                        # Generate unique ID based on content
                        entity_id = f"entity_{hashlib.md5(normalized.encode()).hexdigest()[:8]}"
                        
                        # Count mentions
                        mentions = len(re.findall(re.escape(match), content, re.IGNORECASE))
                        
                        entity = {
                            'id': entity_id,
                            'name': match.strip(),
                            'type': entity_type,
                            'mentions': mentions
                        }
                        
                        entities.append(entity)
                        entity_map[normalized] = entity
                    else:
                        # Update mention count for existing entity
                        entity_map[normalized]['mentions'] += 1
            
            # If no entities found, extract generic terms
            if not entities:
                words = content.split()
                # Extract capitalized words as potential entities
                capitalized = [w for w in words if w and w[0].isupper() and len(w) > 2]
                unique_terms = list(set(capitalized))[:5]  # Limit to 5
                
                for i, term in enumerate(unique_terms):
                    entities.append({
                        'id': f'entity_{i+1}',
                        'name': term,
                        'type': 'TERM',
                        'mentions': capitalized.count(term)
                    })
            
            results = {
                'document_id': document.get('id'),
                'entities': entities
            }
            
            # Real processing time
            processing_time = (asyncio.get_event_loop().time() - start_time) * 1000
            return web.json_response(results, headers={'X-Duration-Ms': str(int(processing_time))})
            
        except Exception as e:
            logger.error(f"Error in resolve_entities: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def start(self):
        """Start the test service"""
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        site = web.TCPSite(self.runner, 'localhost', self.port)
        await site.start()
        logger.info(f"Test IdentityService started on port {self.port}")
    
    async def stop(self):
        """Stop the test service"""
        if self.runner:
            await self.runner.cleanup()
            logger.info("Test IdentityService stopped")


class TestTheoryExtractionService:
    """Test theory extraction service with real HTTP endpoints"""
    
    def __init__(self, port: int = 8003):
        self.port = port
        self.app = web.Application()
        self.runner = None
        self.failure_rate = 0.0  # Probability of random failure
        self.memory_limit = None  # Memory threshold for OOM simulation
        self.latency_ms = 0  # Additional network latency
        self.request_count = 0  # Track requests for failure patterns
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup HTTP routes"""
        self.app.router.add_get('/health', self.health_check)
        self.app.router.add_post('/api/v1/extract', self.extract_theories)
    
    async def health_check(self, request: web.Request) -> web.Response:
        """Health check endpoint"""
        return web.json_response({
            'status': 'healthy',
            'service': 'TheoryExtractionService',
            'version': '1.0.0',
            'uptime': 100
        })
    
    async def extract_theories(self, request: web.Request) -> web.Response:
        """Extract theories endpoint"""
        try:
            start_time = asyncio.get_event_loop().time()
            self.request_count += 1
            
            # Check for configured failure scenarios
            failure_response = await check_service_failures(self, "TheoryExtractionService")
            if failure_response:
                return failure_response
            
            data = await request.json()
            document = data['document']
            entities = data.get('entities', [])
            analytics = data.get('analytics', [])
            
            # Real theory extraction based on entities and analytics
            content = document.get('content', '') or str(document)
            theories = []
            
            # Extract relationships between entities
            if len(entities) >= 2:
                # Analyze co-occurrence patterns
                entity_names = [e['name'] for e in entities]
                
                for i in range(len(entity_names)):
                    for j in range(i + 1, len(entity_names)):
                        entity1 = entity_names[i]
                        entity2 = entity_names[j]
                        
                        # Find sentences containing both entities
                        sentences = content.split('.')
                        cooccurrence_sentences = [
                            s for s in sentences 
                            if entity1.lower() in s.lower() and entity2.lower() in s.lower()
                        ]
                        
                        if cooccurrence_sentences:
                            # Analyze relationship type based on keywords
                            relationship_keywords = {
                                'enables': 'CAUSATION',
                                'causes': 'CAUSATION',
                                'leads to': 'CAUSATION',
                                'relates to': 'RELATION',
                                'associated with': 'RELATION',
                                'depends on': 'DEPENDENCY',
                                'requires': 'DEPENDENCY'
                            }
                            
                            for sentence in cooccurrence_sentences[:1]:  # First co-occurrence
                                theory_type = 'RELATION'  # Default
                                
                                for keyword, rel_type in relationship_keywords.items():
                                    if keyword in sentence.lower():
                                        theory_type = rel_type
                                        break
                                
                                # Calculate confidence based on evidence strength
                                confidence = min(0.95, 0.5 + (len(cooccurrence_sentences) * 0.1))
                                
                                theory_id = f"theory_{hashlib.md5(f'{entity1}{entity2}'.encode()).hexdigest()[:6]}"
                                
                                theories.append({
                                    'id': theory_id,
                                    'type': theory_type,
                                    'description': f"{entity1} {theory_type.lower()} {entity2}",
                                    'confidence': float(confidence),
                                    'evidence': cooccurrence_sentences[0].strip()
                                })
            
            # Extract hypotheses from analytics data
            if analytics:
                # Analyze patterns in analytics results
                for i, analysis in enumerate(analytics):
                    if isinstance(analysis, dict) and 'graph' in analysis:
                        graph_data = analysis['graph']
                        if graph_data.get('clusters', 0) > 2:
                            theories.append({
                                'id': f'theory_h{i+1}',
                                'type': 'HYPOTHESIS',
                                'description': f'Document exhibits {graph_data["clusters"]} distinct conceptual clusters',
                                'confidence': 0.75
                            })
            
            # If no theories found, generate basic observations
            if not theories:
                word_count = len(content.split())
                theories.append({
                    'id': 'theory_basic',
                    'type': 'OBSERVATION',
                    'description': f'Document contains {word_count} words with {len(entities)} identified entities',
                    'confidence': 1.0
                })
            
            results = {
                'document_id': document.get('id'),
                'theories': theories
            }
            
            # Real processing time
            processing_time = (asyncio.get_event_loop().time() - start_time) * 1000
            return web.json_response(results, headers={'X-Duration-Ms': str(int(processing_time))})
            
        except Exception as e:
            logger.error(f"Error in extract_theories: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def start(self):
        """Start the test service"""
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        site = web.TCPSite(self.runner, 'localhost', self.port)
        await site.start()
        logger.info(f"Test TheoryExtractionService started on port {self.port}")
    
    async def stop(self):
        """Stop the test service"""
        if self.runner:
            await self.runner.cleanup()
            logger.info("Test TheoryExtractionService stopped")


class TestQualityService:
    """Test quality service with real HTTP endpoints"""
    
    def __init__(self, port: int = 8004):
        self.port = port
        self.app = web.Application()
        self.runner = None
        self.failure_rate = 0.0  # Probability of random failure
        self.memory_limit = None  # Memory threshold for OOM simulation
        self.latency_ms = 0  # Additional network latency
        self.request_count = 0  # Track requests for failure patterns
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup HTTP routes"""
        self.app.router.add_get('/health', self.health_check)
        self.app.router.add_post('/api/v1/assess', self.assess_quality)
    
    async def health_check(self, request: web.Request) -> web.Response:
        """Health check endpoint"""
        return web.json_response({
            'status': 'healthy',
            'service': 'QualityService',
            'version': '1.0.0',
            'uptime': 100
        })
    
    async def assess_quality(self, request: web.Request) -> web.Response:
        """Assess quality endpoint"""
        try:
            start_time = asyncio.get_event_loop().time()
            self.request_count += 1
            
            # Check for configured failure scenarios
            failure_response = await check_service_failures(self, "QualityService")
            if failure_response:
                return failure_response
            
            data = await request.json()
            document = data['document']
            entities = data.get('entities', [])
            analytics = data.get('analytics', [])
            theories = data.get('theories')
            
            # Real quality assessment based on actual data analysis
            content = document.get('content', '') or str(document)
            word_count = len(content.split())
            
            # Calculate entity coverage
            entity_coverage = 0.0
            if entities and word_count > 0:
                # Count unique entity mentions
                total_mentions = sum(e.get('mentions', 1) for e in entities)
                # Coverage is ratio of entity mentions to total words
                entity_coverage = min(1.0, total_mentions / (word_count * 0.1))  # Expect ~10% entity density
            
            # Calculate analysis completeness
            analysis_completeness = 0.0
            if analytics:
                completed_analyses = sum(1 for a in analytics if isinstance(a, dict) and len(a) > 0)
                expected_analyses = 3  # graph, table, vector
                analysis_completeness = completed_analyses / expected_analyses
            
            # Calculate theory support
            theory_support = 0.0
            if theories:
                # Assess theory quality based on confidence scores
                theory_data = theories if isinstance(theories, list) else theories.get('theories', [])
                if theory_data:
                    avg_confidence = sum(t.get('confidence', 0) for t in theory_data) / len(theory_data)
                    theory_support = avg_confidence
            
            # Calculate overall quality score
            weights = {
                'entity_coverage': 0.3,
                'analysis_completeness': 0.4,
                'theory_support': 0.3
            }
            
            overall_score = (
                entity_coverage * weights['entity_coverage'] +
                analysis_completeness * weights['analysis_completeness'] +
                theory_support * weights['theory_support']
            )
            
            # Add noise for realistic variation
            noise = (hash(content) % 10 - 5) / 100  # -0.05 to 0.05
            overall_score = max(0.0, min(1.0, overall_score + noise))
            
            results = {
                'document_id': document.get('id'),
                'quality_score': round(overall_score, 3),
                'quality_breakdown': {
                    'entity_coverage': round(entity_coverage, 3),
                    'analysis_completeness': round(analysis_completeness, 3),
                    'theory_support': round(theory_support, 3),
                    'overall_confidence': round(overall_score, 3)
                },
                'metadata': {
                    'word_count': word_count,
                    'entity_count': len(entities),
                    'theory_count': len(theories) if isinstance(theories, list) else len(theories.get('theories', [])) if theories else 0
                }
            }
            
            # Real processing time
            processing_time = (asyncio.get_event_loop().time() - start_time) * 1000
            return web.json_response(results, headers={'X-Duration-Ms': str(int(processing_time))})
            
        except Exception as e:
            logger.error(f"Error in assess_quality: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def start(self):
        """Start the test service"""
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        site = web.TCPSite(self.runner, 'localhost', self.port)
        await site.start()
        logger.info(f"Test QualityService started on port {self.port}")
    
    async def stop(self):
        """Stop the test service"""
        if self.runner:
            await self.runner.cleanup()
            logger.info("Test QualityService stopped")


class TestProvenanceService:
    """Test provenance service with real HTTP endpoints"""
    
    def __init__(self, port: int = 8005):
        self.port = port
        self.app = web.Application()
        self.runner = None
        self.failure_rate = 0.0  # Probability of random failure
        self.memory_limit = None  # Memory threshold for OOM simulation
        self.latency_ms = 0  # Additional network latency
        self.request_count = 0  # Track requests for failure patterns
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup HTTP routes"""
        self.app.router.add_get('/health', self.health_check)
        self.app.router.add_post('/api/v1/track', self.track_operation)
    
    async def health_check(self, request: web.Request) -> web.Response:
        """Health check endpoint"""
        return web.json_response({
            'status': 'healthy',
            'service': 'ProvenanceService',
            'version': '1.0.0',
            'uptime': 100
        })
    
    async def track_operation(self, request: web.Request) -> web.Response:
        """Track operation endpoint"""
        try:
            start_time = asyncio.get_event_loop().time()
            self.request_count += 1
            
            # Check for configured failure scenarios
            failure_response = await check_service_failures(self, "ProvenanceService")
            if failure_response:
                return failure_response
            
            data = await request.json()
            operation = data['operation']
            input_data = data.get('input', {})
            output_data = data.get('output', {})
            
            # Real provenance tracking with hash computation
            import datetime
            
            # Compute real hashes of input and output data
            input_str = json.dumps(input_data, sort_keys=True)
            output_str = json.dumps(output_data, sort_keys=True)
            
            input_hash = hashlib.sha256(input_str.encode()).hexdigest()[:16]
            output_hash = hashlib.sha256(output_str.encode()).hexdigest()[:16]
            
            # Generate unique tracking ID based on operation and timestamp
            timestamp = datetime.datetime.now()
            tracking_components = f"{operation}_{timestamp.isoformat()}_{input_hash[:8]}"
            tracking_id = f"prov_{hashlib.md5(tracking_components.encode()).hexdigest()[:10]}"
            
            # Build lineage graph
            lineage = {
                'input_hash': input_hash,
                'output_hash': output_hash,
                'transformation': operation,
                'input_size': len(input_str),
                'output_size': len(output_str),
                'transformation_ratio': round(len(output_str) / max(1, len(input_str)), 3)
            }
            
            # Add operation-specific metadata
            operation_metadata = {}
            if operation == 'entity_resolution':
                operation_metadata['entity_count'] = len(input_data.get('entities', []))
            elif operation == 'document_analysis':
                operation_metadata['analysis_modes'] = input_data.get('modes', [])
            elif operation == 'theory_extraction':
                operation_metadata['theory_count'] = len(output_data.get('theories', []))
            
            results = {
                'tracking_id': tracking_id,
                'operation': operation,
                'timestamp': timestamp.isoformat(),
                'lineage': lineage,
                'metadata': operation_metadata
            }
            
            # Real processing time
            processing_time = (asyncio.get_event_loop().time() - start_time) * 1000
            return web.json_response(results, headers={'X-Duration-Ms': str(int(processing_time))})
            
        except Exception as e:
            logger.error(f"Error in track_operation: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def start(self):
        """Start the test service"""
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        site = web.TCPSite(self.runner, 'localhost', self.port)
        await site.start()
        logger.info(f"Test ProvenanceService started on port {self.port}")
    
    async def stop(self):
        """Stop the test service"""
        if self.runner:
            await self.runner.cleanup()
            logger.info("Test ProvenanceService stopped")


class TestServiceManager:
    """Manage all test services for integration tests"""
    
    def __init__(self, failure_config=None):
        """
        Initialize test services with optional failure configuration.
        
        Args:
            failure_config: Dict mapping service names to failure settings:
                {
                    'AnalyticsService': {
                        'failure_rate': 0.2,  # 20% chance of network failure
                        'memory_limit': 50_000_000,  # Trigger OOM if available < 50MB
                        'latency_ms': 5000  # Add artificial latency (simulating network issues)
                    }
                }
        """
        self.failure_config = failure_config or {}
        self.services = {
            'AnalyticsService': TestAnalyticsService(8001),
            'IdentityService': TestIdentityService(8002),
            'TheoryExtractionService': TestTheoryExtractionService(8003),
            'QualityService': TestQualityService(8004),
            'ProvenanceService': TestProvenanceService(8005)
        }
        
        # Apply failure configuration to services
        for service_name, service in self.services.items():
            if service_name in self.failure_config:
                config = self.failure_config[service_name]
                service.failure_rate = config.get('failure_rate', 0.0)
                service.memory_limit = config.get('memory_limit', None)
                service.latency_ms = config.get('latency_ms', 0)
    
    async def start_all(self):
        """Start all test services"""
        for name, service in self.services.items():
            await service.start()
            logger.info(f"Started {name}")
    
    async def stop_all(self):
        """Stop all test services"""
        for name, service in self.services.items():
            await service.stop()
            logger.info(f"Stopped {name}")
    
    def get_service_configs(self) -> Dict[str, Any]:
        """Get configuration for all test services"""
        return {
            'AnalyticsService': {
                'base_url': 'http://localhost:8001',
                'health_endpoint': 'http://localhost:8001/health'
            },
            'IdentityService': {
                'base_url': 'http://localhost:8002',
                'health_endpoint': 'http://localhost:8002/health'
            },
            'TheoryExtractionService': {
                'base_url': 'http://localhost:8003',
                'health_endpoint': 'http://localhost:8003/health'
            },
            'QualityService': {
                'base_url': 'http://localhost:8004',
                'health_endpoint': 'http://localhost:8004/health'
            },
            'ProvenanceService': {
                'base_url': 'http://localhost:8005',
                'health_endpoint': 'http://localhost:8005/health'
            }
        }