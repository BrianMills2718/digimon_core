#!/usr/bin/env python3
"""
LLM Cache Manager - Intelligent Caching for Repeated Language Model Calls

Provides sophisticated caching strategies for LLM calls including semantic similarity matching,
request normalization, response validation, and intelligent cache invalidation to reduce
costs and improve response times for repeated queries.
"""

import logging
import asyncio
import hashlib
import json
import time
import sqlite3
import pickle
import zlib
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from contextlib import asynccontextmanager
import threading
from abc import ABC, abstractmethod
from enum import Enum

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


class CacheStrategy(Enum):
    """Different caching strategies for LLM calls"""
    EXACT_MATCH = "exact_match"
    SEMANTIC_SIMILARITY = "semantic_similarity"
    PARAMETER_NORMALIZED = "parameter_normalized"
    PROMPT_TEMPLATE = "prompt_template"
    HYBRID = "hybrid"


@dataclass
class LLMRequest:
    """Standardized LLM request structure"""
    prompt: str
    model: str
    temperature: float
    max_tokens: int
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    system_message: Optional[str] = None
    conversation_context: Optional[List[Dict]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def normalize(self) -> str:
        """Create normalized string representation for caching"""
        # Normalize floating point values to reduce precision issues
        normalized = {
            'prompt': self.prompt.strip(),
            'model': self.model,
            'temperature': round(self.temperature, 2),
            'max_tokens': self.max_tokens,
            'top_p': round(self.top_p, 2),
            'frequency_penalty': round(self.frequency_penalty, 2),
            'presence_penalty': round(self.presence_penalty, 2),
            'system_message': self.system_message.strip() if self.system_message else None,
            'conversation_context': self.conversation_context
        }
        
        return json.dumps(normalized, sort_keys=True)
    
    def get_cache_key(self, strategy: CacheStrategy = CacheStrategy.EXACT_MATCH) -> str:
        """Generate cache key based on strategy"""
        if strategy == CacheStrategy.EXACT_MATCH:
            return hashlib.sha256(self.normalize().encode()).hexdigest()
        
        elif strategy == CacheStrategy.PARAMETER_NORMALIZED:
            # Normalize parameters to common values
            normalized_request = LLMRequest(
                prompt=self.prompt.strip(),
                model=self.model,
                temperature=round(self.temperature / 0.1) * 0.1,  # Round to nearest 0.1
                max_tokens=self.max_tokens,
                system_message=self.system_message
            )
            return hashlib.sha256(normalized_request.normalize().encode()).hexdigest()
        
        elif strategy == CacheStrategy.PROMPT_TEMPLATE:
            # Extract template-like structure from prompt
            template_prompt = self._extract_template_structure()
            template_request = LLMRequest(
                prompt=template_prompt,
                model=self.model,
                temperature=0.0,  # Use deterministic settings for templates
                max_tokens=self.max_tokens,
                system_message=self.system_message
            )
            return hashlib.sha256(template_request.normalize().encode()).hexdigest()
        
        else:
            return self.get_cache_key(CacheStrategy.EXACT_MATCH)
    
    def _extract_template_structure(self) -> str:
        """Extract template-like structure from prompt"""
        # This is a simplified template extraction
        # In practice, this could be more sophisticated
        import re
        
        # Replace specific values with placeholders
        template = self.prompt
        
        # Replace numbers with placeholder
        template = re.sub(r'\b\d+\b', '[NUMBER]', template)
        
        # Replace quoted strings with placeholder
        template = re.sub(r'"[^"]*"', '[QUOTED_TEXT]', template)
        template = re.sub(r"'[^']*'", '[QUOTED_TEXT]', template)
        
        # Replace dates with placeholder
        template = re.sub(r'\b\d{4}-\d{2}-\d{2}\b', '[DATE]', template)
        
        return template
    
    def get_embedding_text(self) -> str:
        """Get text for semantic embedding"""
        embedding_text = self.prompt
        if self.system_message:
            embedding_text = f"{self.system_message}\n\n{embedding_text}"
        return embedding_text


@dataclass
class LLMResponse:
    """Standardized LLM response structure"""
    content: str
    model: str
    usage: Dict[str, int]
    finish_reason: str
    created_at: datetime
    cached: bool = False
    cache_hit_type: Optional[str] = None
    confidence_score: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_valid(self) -> bool:
        """Check if response is valid and usable"""
        return (
            bool(self.content and self.content.strip()) and
            self.finish_reason in ['stop', 'length'] and
            self.confidence_score > 0.5
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LLMResponse':
        """Create from dictionary"""
        # Convert datetime string back to datetime object
        if isinstance(data.get('created_at'), str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        return cls(**data)


@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    request_hash: str
    request: LLMRequest
    response: LLMResponse
    created_at: datetime
    accessed_at: datetime
    access_count: int
    embedding: Optional[np.ndarray] = None
    tags: List[str] = field(default_factory=list)
    ttl_hours: float = 24.0
    
    def is_expired(self) -> bool:
        """Check if cache entry has expired"""
        if self.ttl_hours <= 0:  # Never expires
            return False
        
        expiry_time = self.created_at + timedelta(hours=self.ttl_hours)
        return datetime.now() > expiry_time
    
    def update_access(self) -> None:
        """Update access metadata"""
        self.accessed_at = datetime.now()
        self.access_count += 1


class SemanticSimilarityMatcher:
    """Handles semantic similarity matching for LLM requests"""
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2', similarity_threshold: float = 0.85):
        self.model_name = model_name
        self.similarity_threshold = similarity_threshold
        self.encoder = None
        self._initialize_encoder()
        
    def _initialize_encoder(self):
        """Initialize sentence transformer model"""
        try:
            self.encoder = SentenceTransformer(self.model_name)
            logger.info(f"Initialized semantic similarity encoder: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize semantic encoder: {e}")
            self.encoder = None
    
    def get_embedding(self, text: str) -> Optional[np.ndarray]:
        """Get embedding for text"""
        if not self.encoder:
            return None
        
        try:
            embedding = self.encoder.encode([text])[0]
            return embedding
        except Exception as e:
            logger.error(f"Failed to get embedding: {e}")
            return None
    
    def calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Calculate cosine similarity between embeddings"""
        try:
            similarity = cosine_similarity([embedding1], [embedding2])[0][0]
            return float(similarity)
        except Exception as e:
            logger.error(f"Failed to calculate similarity: {e}")
            return 0.0
    
    def find_similar_entries(self, query_embedding: np.ndarray, 
                           cache_entries: List[CacheEntry]) -> List[Tuple[CacheEntry, float]]:
        """Find cache entries with similar embeddings"""
        if not self.encoder or query_embedding is None:
            return []
        
        similar_entries = []
        
        for entry in cache_entries:
            if entry.embedding is None:
                continue
            
            similarity = self.calculate_similarity(query_embedding, entry.embedding)
            
            if similarity >= self.similarity_threshold:
                similar_entries.append((entry, similarity))
        
        # Sort by similarity score (highest first)
        similar_entries.sort(key=lambda x: x[1], reverse=True)
        
        return similar_entries


class CacheStorage(ABC):
    """Abstract base class for cache storage backends"""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[CacheEntry]:
        """Get cache entry by key"""
        pass
    
    @abstractmethod
    async def put(self, key: str, entry: CacheEntry) -> bool:
        """Store cache entry"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete cache entry"""
        pass
    
    @abstractmethod
    async def get_all_entries(self) -> List[CacheEntry]:
        """Get all cache entries"""
        pass
    
    @abstractmethod
    async def cleanup_expired(self) -> int:
        """Clean up expired entries, return count removed"""
        pass
    
    @abstractmethod
    async def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        pass


class SQLiteCacheStorage(CacheStorage):
    """SQLite-based cache storage"""
    
    def __init__(self, db_path: str = "llm_cache.db"):
        self.db_path = Path(db_path)
        self.lock = threading.Lock()
        self._initialize_db()
    
    def _initialize_db(self):
        """Initialize SQLite database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS llm_cache (
                        key TEXT PRIMARY KEY,
                        request_data BLOB NOT NULL,
                        response_data BLOB NOT NULL,
                        embedding BLOB,
                        created_at TIMESTAMP NOT NULL,
                        accessed_at TIMESTAMP NOT NULL,
                        access_count INTEGER DEFAULT 1,
                        tags TEXT,
                        ttl_hours REAL DEFAULT 24.0
                    )
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_created_at ON llm_cache(created_at)
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_accessed_at ON llm_cache(accessed_at)
                """)
                
                conn.commit()
                
            logger.info(f"Initialized SQLite cache database: {self.db_path}")
            
        except Exception as e:
            logger.error(f"Failed to initialize cache database: {e}")
            raise
    
    async def get(self, key: str) -> Optional[CacheEntry]:
        """Get cache entry by key"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT request_data, response_data, embedding, created_at, 
                           accessed_at, access_count, tags, ttl_hours
                    FROM llm_cache WHERE key = ?
                """, (key,))
                
                row = cursor.fetchone()
                if not row:
                    return None
                
                # Deserialize data
                request_data = pickle.loads(row[0])
                response_data = pickle.loads(row[1])
                embedding = pickle.loads(row[2]) if row[2] else None
                
                # Create cache entry
                entry = CacheEntry(
                    request_hash=key,
                    request=LLMRequest(**request_data),
                    response=LLMResponse.from_dict(response_data),
                    created_at=datetime.fromisoformat(row[3]),
                    accessed_at=datetime.fromisoformat(row[4]),
                    access_count=row[5],
                    embedding=embedding,
                    tags=json.loads(row[6] or '[]'),
                    ttl_hours=row[7]
                )
                
                # Update access time
                entry.update_access()
                await self._update_access_metadata(key, entry)
                
                return entry
                
        except Exception as e:
            logger.error(f"Failed to get cache entry {key}: {e}")
            return None
    
    async def put(self, key: str, entry: CacheEntry) -> bool:
        """Store cache entry"""
        try:
            # Serialize data
            request_data = pickle.dumps(asdict(entry.request))
            response_data = pickle.dumps(entry.response.to_dict())
            embedding_data = pickle.dumps(entry.embedding) if entry.embedding is not None else None
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO llm_cache 
                    (key, request_data, response_data, embedding, created_at, 
                     accessed_at, access_count, tags, ttl_hours)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    key,
                    request_data,
                    response_data,
                    embedding_data,
                    entry.created_at.isoformat(),
                    entry.accessed_at.isoformat(),
                    entry.access_count,
                    json.dumps(entry.tags),
                    entry.ttl_hours
                ))
                
                conn.commit()
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to store cache entry {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete cache entry"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("DELETE FROM llm_cache WHERE key = ?", (key,))
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"Failed to delete cache entry {key}: {e}")
            return False
    
    async def get_all_entries(self) -> List[CacheEntry]:
        """Get all cache entries"""
        try:
            entries = []
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT key, request_data, response_data, embedding, created_at,
                           accessed_at, access_count, tags, ttl_hours
                    FROM llm_cache
                """)
                
                for row in cursor.fetchall():
                    try:
                        request_data = pickle.loads(row[1])
                        response_data = pickle.loads(row[2])
                        embedding = pickle.loads(row[3]) if row[3] else None
                        
                        entry = CacheEntry(
                            request_hash=row[0],
                            request=LLMRequest(**request_data),
                            response=LLMResponse.from_dict(response_data),
                            created_at=datetime.fromisoformat(row[4]),
                            accessed_at=datetime.fromisoformat(row[5]),
                            access_count=row[6],
                            embedding=embedding,
                            tags=json.loads(row[7] or '[]'),
                            ttl_hours=row[8]
                        )
                        
                        entries.append(entry)
                        
                    except Exception as e:
                        logger.error(f"Failed to deserialize cache entry: {e}")
                        continue
            
            return entries
            
        except Exception as e:
            logger.error(f"Failed to get all cache entries: {e}")
            return []
    
    async def cleanup_expired(self) -> int:
        """Clean up expired entries"""
        try:
            current_time = datetime.now()
            
            with sqlite3.connect(self.db_path) as conn:
                # Delete entries where current_time > created_at + ttl_hours
                cursor = conn.execute("""
                    DELETE FROM llm_cache 
                    WHERE ttl_hours > 0 
                    AND datetime(created_at, '+' || ttl_hours || ' hours') < ?
                """, (current_time.isoformat(),))
                
                conn.commit()
                return cursor.rowcount
                
        except Exception as e:
            logger.error(f"Failed to cleanup expired entries: {e}")
            return 0
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Total entries
                cursor = conn.execute("SELECT COUNT(*) FROM llm_cache")
                total_entries = cursor.fetchone()[0]
                
                # Database size
                db_size_mb = self.db_path.stat().st_size / (1024 * 1024) if self.db_path.exists() else 0
                
                # Most accessed
                cursor = conn.execute("""
                    SELECT access_count, COUNT(*) 
                    FROM llm_cache 
                    GROUP BY access_count 
                    ORDER BY access_count DESC 
                    LIMIT 5
                """)
                access_distribution = dict(cursor.fetchall())
                
                return {
                    "total_entries": total_entries,
                    "database_size_mb": db_size_mb,
                    "access_distribution": access_distribution,
                    "storage_type": "sqlite"
                }
                
        except Exception as e:
            logger.error(f"Failed to get storage stats: {e}")
            return {"error": str(e)}
    
    async def _update_access_metadata(self, key: str, entry: CacheEntry):
        """Update access metadata for cache entry"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE llm_cache 
                    SET accessed_at = ?, access_count = ?
                    WHERE key = ?
                """, (
                    entry.accessed_at.isoformat(),
                    entry.access_count,
                    key
                ))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to update access metadata for {key}: {e}")


class LLMCacheManager:
    """Comprehensive LLM cache manager with multiple strategies"""
    
    def __init__(self, 
                 storage: Optional[CacheStorage] = None,
                 default_strategy: CacheStrategy = CacheStrategy.HYBRID,
                 similarity_threshold: float = 0.85,
                 default_ttl_hours: float = 24.0,
                 max_cache_size: int = 10000):
        
        self.storage = storage or SQLiteCacheStorage()
        self.default_strategy = default_strategy
        self.default_ttl_hours = default_ttl_hours
        self.max_cache_size = max_cache_size
        
        # Initialize semantic similarity matcher
        self.similarity_matcher = SemanticSimilarityMatcher(
            similarity_threshold=similarity_threshold
        )
        
        # Cache statistics
        self.stats = {
            'cache_hits': 0,
            'cache_misses': 0,
            'cache_hit_types': {},
            'requests_processed': 0,
            'cache_saves': 0,
            'cache_invalidations': 0
        }
        
        # Background cleanup task
        self._cleanup_task = None
        self._initialize_background_tasks()
        
        logger.info(f"LLM Cache Manager initialized with {default_strategy.value} strategy")
    
    def _initialize_background_tasks(self):
        """Initialize background tasks"""
        # Start cleanup task if in async context
        try:
            loop = asyncio.get_event_loop()
            if loop and loop.is_running():
                self._cleanup_task = loop.create_task(self._periodic_cleanup())
        except RuntimeError:
            # No async loop running - cleanup will be manual
            pass
    
    async def _periodic_cleanup(self):
        """Periodic cleanup of expired cache entries"""
        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour
                
                # Clean up expired entries
                expired_count = await self.storage.cleanup_expired()
                if expired_count > 0:
                    logger.info(f"Cleaned up {expired_count} expired cache entries")
                    self.stats['cache_invalidations'] += expired_count
                
                # Enforce cache size limits
                await self._enforce_cache_size_limits()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in periodic cache cleanup: {e}")
    
    async def _enforce_cache_size_limits(self):
        """Enforce maximum cache size by removing least recently used entries"""
        try:
            stats = await self.storage.get_stats()
            total_entries = stats.get('total_entries', 0)
            
            if total_entries > self.max_cache_size:
                # Get all entries and sort by access time
                all_entries = await self.storage.get_all_entries()
                all_entries.sort(key=lambda x: x.accessed_at)
                
                # Remove oldest entries
                entries_to_remove = total_entries - int(self.max_cache_size * 0.9)  # Remove to 90% of limit
                
                for entry in all_entries[:entries_to_remove]:
                    await self.storage.delete(entry.request_hash)
                
                logger.info(f"Cache size enforcement: removed {entries_to_remove} entries")
                self.stats['cache_invalidations'] += entries_to_remove
                
        except Exception as e:
            logger.error(f"Failed to enforce cache size limits: {e}")
    
    async def get_cached_response(self, request: LLMRequest, 
                                strategy: Optional[CacheStrategy] = None) -> Optional[LLMResponse]:
        """Get cached response for LLM request"""
        self.stats['requests_processed'] += 1
        strategy = strategy or self.default_strategy
        
        try:
            if strategy == CacheStrategy.EXACT_MATCH:
                return await self._get_exact_match(request)
            
            elif strategy == CacheStrategy.SEMANTIC_SIMILARITY:
                return await self._get_semantic_match(request)
            
            elif strategy == CacheStrategy.PARAMETER_NORMALIZED:
                return await self._get_parameter_normalized_match(request)
            
            elif strategy == CacheStrategy.PROMPT_TEMPLATE:
                return await self._get_template_match(request)
            
            elif strategy == CacheStrategy.HYBRID:
                return await self._get_hybrid_match(request)
            
            else:
                logger.warning(f"Unknown cache strategy: {strategy}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting cached response: {e}")
            return None
    
    async def _get_exact_match(self, request: LLMRequest) -> Optional[LLMResponse]:
        """Get exact match from cache"""
        cache_key = request.get_cache_key(CacheStrategy.EXACT_MATCH)
        entry = await self.storage.get(cache_key)
        
        if entry and not entry.is_expired() and entry.response.is_valid():
            self._record_cache_hit('exact_match')
            
            # Mark response as cached
            response = entry.response
            response.cached = True
            response.cache_hit_type = 'exact_match'
            
            return response
        
        return None
    
    async def _get_semantic_match(self, request: LLMRequest) -> Optional[LLMResponse]:
        """Get semantically similar response from cache"""
        if not self.similarity_matcher.encoder:
            return None
        
        # Get embedding for current request
        query_text = request.get_embedding_text()
        query_embedding = self.similarity_matcher.get_embedding(query_text)
        
        if query_embedding is None:
            return None
        
        # Get all cache entries
        all_entries = await self.storage.get_all_entries()
        
        # Filter valid, non-expired entries with embeddings
        valid_entries = [
            entry for entry in all_entries
            if (not entry.is_expired() and 
                entry.response.is_valid() and 
                entry.embedding is not None and
                entry.request.model == request.model)  # Same model requirement
        ]
        
        # Find similar entries
        similar_entries = self.similarity_matcher.find_similar_entries(
            query_embedding, valid_entries
        )
        
        if similar_entries:
            best_entry, similarity_score = similar_entries[0]
            self._record_cache_hit('semantic_similarity')
            
            # Update response metadata
            response = best_entry.response
            response.cached = True
            response.cache_hit_type = 'semantic_similarity'
            response.confidence_score = similarity_score
            
            logger.debug(f"Semantic cache hit with similarity {similarity_score:.3f}")
            return response
        
        return None
    
    async def _get_parameter_normalized_match(self, request: LLMRequest) -> Optional[LLMResponse]:
        """Get parameter-normalized match from cache"""
        cache_key = request.get_cache_key(CacheStrategy.PARAMETER_NORMALIZED)
        entry = await self.storage.get(cache_key)
        
        if entry and not entry.is_expired() and entry.response.is_valid():
            self._record_cache_hit('parameter_normalized')
            
            response = entry.response
            response.cached = True
            response.cache_hit_type = 'parameter_normalized'
            
            return response
        
        return None
    
    async def _get_template_match(self, request: LLMRequest) -> Optional[LLMResponse]:
        """Get template-based match from cache"""
        cache_key = request.get_cache_key(CacheStrategy.PROMPT_TEMPLATE)
        entry = await self.storage.get(cache_key)
        
        if entry and not entry.is_expired() and entry.response.is_valid():
            self._record_cache_hit('prompt_template')
            
            response = entry.response
            response.cached = True
            response.cache_hit_type = 'prompt_template'
            
            return response
        
        return None
    
    async def _get_hybrid_match(self, request: LLMRequest) -> Optional[LLMResponse]:
        """Get best match using hybrid strategy"""
        # Try strategies in order of preference
        strategies = [
            CacheStrategy.EXACT_MATCH,
            CacheStrategy.PARAMETER_NORMALIZED,
            CacheStrategy.SEMANTIC_SIMILARITY,
            CacheStrategy.PROMPT_TEMPLATE
        ]
        
        for strategy in strategies:
            if strategy == CacheStrategy.HYBRID:
                continue  # Avoid infinite recursion
            
            response = await self.get_cached_response(request, strategy)
            if response:
                # Update hit type to indicate hybrid
                response.cache_hit_type = f"hybrid_{response.cache_hit_type}"
                return response
        
        return None
    
    async def cache_response(self, request: LLMRequest, response: LLMResponse,
                           ttl_hours: Optional[float] = None,
                           tags: Optional[List[str]] = None) -> bool:
        """Cache LLM response with multiple strategies"""
        if not response.is_valid():
            logger.warning("Skipping cache of invalid response")
            return False
        
        try:
            ttl_hours = ttl_hours or self.default_ttl_hours
            tags = tags or []
            
            # Get embedding for semantic search
            embedding = None
            if self.similarity_matcher.encoder:
                embedding_text = request.get_embedding_text()
                embedding = self.similarity_matcher.get_embedding(embedding_text)
            
            # Cache with multiple strategies
            cache_keys = [
                request.get_cache_key(CacheStrategy.EXACT_MATCH),
                request.get_cache_key(CacheStrategy.PARAMETER_NORMALIZED),
                request.get_cache_key(CacheStrategy.PROMPT_TEMPLATE)
            ]
            
            success_count = 0
            current_time = datetime.now()
            
            for cache_key in cache_keys:
                cache_entry = CacheEntry(
                    request_hash=cache_key,
                    request=request,
                    response=response,
                    created_at=current_time,
                    accessed_at=current_time,
                    access_count=0,
                    embedding=embedding,
                    tags=tags,
                    ttl_hours=ttl_hours
                )
                
                if await self.storage.put(cache_key, cache_entry):
                    success_count += 1
            
            if success_count > 0:
                self.stats['cache_saves'] += 1
                logger.debug(f"Cached response with {success_count} strategies")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to cache response: {e}")
            return False
    
    def _record_cache_hit(self, hit_type: str):
        """Record cache hit statistics"""
        self.stats['cache_hits'] += 1
        self.stats['cache_hit_types'][hit_type] = self.stats['cache_hit_types'].get(hit_type, 0) + 1
    
    def _record_cache_miss(self):
        """Record cache miss statistics"""
        self.stats['cache_misses'] += 1
    
    async def invalidate_cache(self, patterns: Optional[List[str]] = None,
                             tags: Optional[List[str]] = None,
                             older_than_hours: Optional[float] = None) -> int:
        """Invalidate cache entries matching criteria"""
        try:
            all_entries = await self.storage.get_all_entries()
            invalidated_count = 0
            
            for entry in all_entries:
                should_invalidate = False
                
                # Check patterns
                if patterns:
                    for pattern in patterns:
                        if pattern in entry.request.prompt:
                            should_invalidate = True
                            break
                
                # Check tags
                if tags and not should_invalidate:
                    if any(tag in entry.tags for tag in tags):
                        should_invalidate = True
                
                # Check age
                if older_than_hours and not should_invalidate:
                    age_hours = (datetime.now() - entry.created_at).total_seconds() / 3600
                    if age_hours > older_than_hours:
                        should_invalidate = True
                
                if should_invalidate:
                    if await self.storage.delete(entry.request_hash):
                        invalidated_count += 1
            
            self.stats['cache_invalidations'] += invalidated_count
            logger.info(f"Invalidated {invalidated_count} cache entries")
            
            return invalidated_count
            
        except Exception as e:
            logger.error(f"Failed to invalidate cache: {e}")
            return 0
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        try:
            storage_stats = await self.storage.get_stats()
            
            # Calculate hit rate
            total_requests = self.stats['cache_hits'] + self.stats['cache_misses']
            hit_rate = (self.stats['cache_hits'] / total_requests) if total_requests > 0 else 0.0
            
            return {
                "cache_statistics": {
                    "hit_rate": hit_rate,
                    "cache_hits": self.stats['cache_hits'],
                    "cache_misses": self.stats['cache_misses'],
                    "hit_types": self.stats['cache_hit_types'],
                    "requests_processed": self.stats['requests_processed'],
                    "cache_saves": self.stats['cache_saves'],
                    "cache_invalidations": self.stats['cache_invalidations']
                },
                "storage_statistics": storage_stats,
                "configuration": {
                    "default_strategy": self.default_strategy.value,
                    "similarity_threshold": self.similarity_matcher.similarity_threshold,
                    "default_ttl_hours": self.default_ttl_hours,
                    "max_cache_size": self.max_cache_size
                },
                "semantic_matching": {
                    "encoder_model": self.similarity_matcher.model_name,
                    "encoder_available": self.similarity_matcher.encoder is not None
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {"error": str(e)}
    
    async def optimize_cache_settings(self) -> Dict[str, Any]:
        """Analyze cache performance and suggest optimizations"""
        try:
            stats = await self.get_cache_stats()
            cache_stats = stats.get('cache_statistics', {})
            
            recommendations = []
            
            # Hit rate analysis
            hit_rate = cache_stats.get('hit_rate', 0)
            if hit_rate < 0.3:
                recommendations.append({
                    "type": "hit_rate_low",
                    "message": f"Hit rate is low ({hit_rate:.1%}). Consider lowering similarity threshold or increasing TTL.",
                    "suggested_actions": [
                        "Lower semantic similarity threshold to 0.80",
                        "Increase default TTL to 48 hours",
                        "Use HYBRID strategy for better coverage"
                    ]
                })
            
            # Hit type analysis
            hit_types = cache_stats.get('hit_types', {})
            dominant_type = max(hit_types.items(), key=lambda x: x[1])[0] if hit_types else None
            
            if dominant_type == 'exact_match' and hit_types.get('semantic_similarity', 0) == 0:
                recommendations.append({
                    "type": "semantic_underutilized",
                    "message": "Semantic similarity matching is not being used effectively.",
                    "suggested_actions": [
                        "Verify sentence transformer model is loaded",
                        "Check embedding generation is working",
                        "Consider lowering similarity threshold"
                    ]
                })
            
            # Storage analysis
            storage_stats = stats.get('storage_statistics', {})
            db_size_mb = storage_stats.get('database_size_mb', 0)
            
            if db_size_mb > 1000:  # 1GB
                recommendations.append({
                    "type": "storage_large",
                    "message": f"Cache database is large ({db_size_mb:.1f}MB).",
                    "suggested_actions": [
                        "Run cache cleanup",
                        "Reduce default TTL",
                        "Consider compacting database"
                    ]
                })
            
            return {
                "analysis_timestamp": datetime.now().isoformat(),
                "performance_metrics": cache_stats,
                "recommendations": recommendations,
                "optimization_status": "good" if not recommendations else "needs_attention"
            }
            
        except Exception as e:
            logger.error(f"Failed to optimize cache settings: {e}")
            return {"error": str(e)}
    
    async def export_cache_data(self, export_path: str, 
                              include_embeddings: bool = False) -> bool:
        """Export cache data for backup or analysis"""
        try:
            all_entries = await self.storage.get_all_entries()
            
            export_data = []
            for entry in all_entries:
                entry_data = {
                    "request": asdict(entry.request),
                    "response": entry.response.to_dict(),
                    "metadata": {
                        "created_at": entry.created_at.isoformat(),
                        "accessed_at": entry.accessed_at.isoformat(),
                        "access_count": entry.access_count,
                        "tags": entry.tags,
                        "ttl_hours": entry.ttl_hours
                    }
                }
                
                if include_embeddings and entry.embedding is not None:
                    entry_data["embedding"] = entry.embedding.tolist()
                
                export_data.append(entry_data)
            
            # Write to file
            export_path = Path(export_path)
            export_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(export_path, 'w') as f:
                json.dump({
                    "export_timestamp": datetime.now().isoformat(),
                    "total_entries": len(export_data),
                    "entries": export_data
                }, f, indent=2)
            
            logger.info(f"Exported {len(export_data)} cache entries to {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export cache data: {e}")
            return False
    
    def shutdown(self):
        """Shutdown cache manager and cleanup resources"""
        logger.info("Shutting down LLM Cache Manager")
        
        # Cancel background tasks
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
        
        # Final cleanup
        try:
            asyncio.create_task(self.storage.cleanup_expired())
        except RuntimeError:
            pass  # No async loop available
        
        logger.info("LLM Cache Manager shutdown complete")


# Factory function for easy initialization
def create_llm_cache_manager(
    cache_db_path: str = "llm_cache.db",
    strategy: CacheStrategy = CacheStrategy.HYBRID,
    similarity_threshold: float = 0.85,
    default_ttl_hours: float = 24.0,
    max_cache_size: int = 10000
) -> LLMCacheManager:
    """Factory function to create LLM cache manager with optimal settings"""
    
    storage = SQLiteCacheStorage(cache_db_path)
    
    return LLMCacheManager(
        storage=storage,
        default_strategy=strategy,
        similarity_threshold=similarity_threshold,
        default_ttl_hours=default_ttl_hours,
        max_cache_size=max_cache_size
    )


# Example usage and testing
if __name__ == "__main__":
    async def test_llm_cache():
        # Create cache manager
        cache_manager = create_llm_cache_manager()
        
        # Test request
        request = LLMRequest(
            prompt="Analyze the following text for sentiment: 'This is a great product!'",
            model="gpt-3.5-turbo",
            temperature=0.7,
            max_tokens=150,
            system_message="You are a sentiment analysis expert."
        )
        
        # Simulate cache miss and response
        cached_response = await cache_manager.get_cached_response(request)
        if not cached_response:
            print("Cache miss - would make LLM call here")
            
            # Simulate LLM response
            response = LLMResponse(
                content="The sentiment is positive. The phrase 'great product' indicates satisfaction.",
                model="gpt-3.5-turbo",
                usage={"prompt_tokens": 25, "completion_tokens": 15, "total_tokens": 40},
                finish_reason="stop",
                created_at=datetime.now()
            )
            
            # Cache the response
            await cache_manager.cache_response(request, response)
            print("Response cached successfully")
        else:
            print(f"Cache hit! Response: {cached_response.content[:100]}...")
        
        # Test cache statistics
        stats = await cache_manager.get_cache_stats()
        print(f"Cache Statistics: {stats}")
        
        # Test optimization analysis
        optimization = await cache_manager.optimize_cache_settings()
        print(f"Optimization Analysis: {optimization}")
        
        # Cleanup
        cache_manager.shutdown()
    
    asyncio.run(test_llm_cache())