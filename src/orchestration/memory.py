"""
Agent Memory System for KGAS Orchestration.

Provides persistent memory capabilities for agents with episodic and semantic
memory patterns, enabling learning and context-aware task execution.
"""

import json
import sqlite3
import hashlib
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

from .base import Task, Result

logger = logging.getLogger(__name__)


class MemoryType(Enum):
    """Types of memory storage."""
    EPISODIC = "episodic"        # Specific task executions
    SEMANTIC = "semantic"        # Learned patterns and facts
    PROCEDURAL = "procedural"    # Learned procedures and strategies
    WORKING = "working"          # Temporary context for current session


@dataclass
class MemoryEntry:
    """Individual memory entry."""
    entry_id: str
    agent_id: str
    memory_type: MemoryType
    content: Dict[str, Any]
    timestamp: datetime
    importance: float = 0.5
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


@dataclass
class MemoryQuery:
    """Query for retrieving memories."""
    agent_id: str
    memory_types: List[MemoryType] = None
    content_keywords: List[str] = None
    tags: List[str] = None
    time_range: Tuple[datetime, datetime] = None
    min_importance: float = 0.0
    max_results: int = 10
    
    def __post_init__(self):
        if self.memory_types is None:
            self.memory_types = list(MemoryType)


class AgentMemory:
    """
    Persistent memory system for agents.
    
    Provides episodic memory (task executions), semantic memory (learned facts),
    procedural memory (strategies), and working memory (current context).
    """
    
    def __init__(self, agent_id: str, db_path: str = None):
        """
        Initialize agent memory.
        
        Args:
            agent_id: Unique agent identifier
            db_path: Path to SQLite database (default: memory/{agent_id}.db)
        """
        self.agent_id = agent_id
        self.logger = logging.getLogger(f"{__name__}.{agent_id}")
        
        # Set up database path
        if db_path is None:
            from ..core.standard_config import get_file_path
            memory_dir = Path(f"{get_file_path('data_dir')}/memory")
            memory_dir.mkdir(parents=True, exist_ok=True)
            db_path = memory_dir / f"{agent_id}.db"
        
        self.db_path = str(db_path)
        self._connection_lock = asyncio.Lock()
        
        # Initialize database
        self._init_database()
        
        self.logger.info(f"Initialized memory for agent {agent_id} at {self.db_path}")
    
    def _init_database(self) -> None:
        """Initialize SQLite database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    entry_id TEXT PRIMARY KEY,
                    agent_id TEXT NOT NULL,
                    memory_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    importance REAL DEFAULT 0.5,
                    access_count INTEGER DEFAULT 0,
                    last_accessed TEXT,
                    tags TEXT DEFAULT '[]',
                    content_hash TEXT NOT NULL
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_agent_type 
                ON memories(agent_id, memory_type)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON memories(timestamp)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_importance 
                ON memories(importance)
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memory_associations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    memory_id1 TEXT NOT NULL,
                    memory_id2 TEXT NOT NULL,
                    association_type TEXT NOT NULL,
                    strength REAL DEFAULT 0.5,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (memory_id1) REFERENCES memories (entry_id),
                    FOREIGN KEY (memory_id2) REFERENCES memories (entry_id)
                )
            """)
            
            conn.commit()
    
    async def store_task_execution(self, task: Task, result: Result, context: Dict[str, Any] = None) -> str:
        """
        Store episodic memory of task execution.
        
        Args:
            task: The executed task
            result: Task execution result
            context: Additional context information
            
        Returns:
            Memory entry ID
        """
        context = context or {}
        
        # Create episodic memory entry
        memory_content = {
            "task_type": task.task_type,
            "task_parameters": task.parameters,
            "task_context": task.context,
            "result_success": result.success,
            "result_data": result.data,
            "result_error": result.error,
            "execution_time": result.execution_time,
            "additional_context": context
        }
        
        # Generate tags from task content
        tags = [
            task.task_type,
            "execution",
            "success" if result.success else "failure"
        ]
        
        # Add parameter-based tags
        for key, value in task.parameters.items():
            if isinstance(value, str) and len(value) < 50:
                tags.append(f"param_{key}_{value}")
        
        entry_id = await self.store_memory(
            memory_type=MemoryType.EPISODIC,
            content=memory_content,
            importance=self._calculate_importance(task, result),
            tags=tags
        )
        
        self.logger.debug(f"Stored episodic memory: {entry_id}")
        return entry_id
    
    async def store_learned_pattern(self, pattern_type: str, pattern_data: Dict[str, Any], importance: float = 0.7) -> str:
        """
        Store semantic memory of learned patterns.
        
        Args:
            pattern_type: Type of pattern (e.g., "entity_resolution", "chunk_strategy")
            pattern_data: Pattern data and metadata
            importance: Pattern importance (0.0-1.0)
            
        Returns:
            Memory entry ID
        """
        memory_content = {
            "pattern_type": pattern_type,
            "pattern_data": pattern_data,
            "learned_at": datetime.now().isoformat(),
            "confidence": pattern_data.get("confidence", 0.5)
        }
        
        tags = [pattern_type, "pattern", "learned"]
        
        entry_id = await self.store_memory(
            memory_type=MemoryType.SEMANTIC,
            content=memory_content,
            importance=importance,
            tags=tags
        )
        
        self.logger.debug(f"Stored semantic memory: {entry_id}")
        return entry_id
    
    async def store_procedure(self, procedure_name: str, procedure_steps: List[Dict], success_rate: float = 0.5) -> str:
        """
        Store procedural memory of successful strategies.
        
        Args:
            procedure_name: Name of the procedure
            procedure_steps: List of procedure steps
            success_rate: Historical success rate
            
        Returns:
            Memory entry ID
        """
        memory_content = {
            "procedure_name": procedure_name,
            "steps": procedure_steps,
            "success_rate": success_rate,
            "usage_count": 1,
            "last_used": datetime.now().isoformat()
        }
        
        tags = [procedure_name, "procedure", "strategy"]
        
        entry_id = await self.store_memory(
            memory_type=MemoryType.PROCEDURAL,
            content=memory_content,
            importance=success_rate,
            tags=tags
        )
        
        self.logger.debug(f"Stored procedural memory: {entry_id}")
        return entry_id
    
    async def store_memory(self, memory_type: MemoryType, content: Dict[str, Any], 
                          importance: float = 0.5, tags: List[str] = None) -> str:
        """
        Store memory entry.
        
        Args:
            memory_type: Type of memory
            content: Memory content
            importance: Memory importance (0.0-1.0)
            tags: Associated tags
            
        Returns:
            Memory entry ID
        """
        tags = tags or []
        
        # Generate entry ID
        content_str = json.dumps(content, sort_keys=True)
        content_hash = hashlib.sha256(content_str.encode()).hexdigest()[:16]
        entry_id = f"{self.agent_id}_{memory_type.value}_{content_hash}"
        
        # Create memory entry
        entry = MemoryEntry(
            entry_id=entry_id,
            agent_id=self.agent_id,
            memory_type=memory_type,
            content=content,
            timestamp=datetime.now(),
            importance=max(0.0, min(1.0, importance)),
            tags=tags
        )
        
        async with self._connection_lock:
            with sqlite3.connect(self.db_path) as conn:
                # Check if entry already exists
                existing = conn.execute(
                    "SELECT entry_id FROM memories WHERE content_hash = ?",
                    (content_hash,)
                ).fetchone()
                
                if existing:
                    # Update access count and importance
                    conn.execute("""
                        UPDATE memories 
                        SET access_count = access_count + 1,
                            importance = MAX(importance, ?),
                            last_accessed = ?
                        WHERE content_hash = ?
                    """, (importance, datetime.now().isoformat(), content_hash))
                    return existing[0]
                
                # Insert new entry
                conn.execute("""
                    INSERT INTO memories 
                    (entry_id, agent_id, memory_type, content, timestamp, 
                     importance, access_count, tags, content_hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    entry.entry_id,
                    entry.agent_id,
                    entry.memory_type.value,
                    json.dumps(entry.content),
                    entry.timestamp.isoformat(),
                    entry.importance,
                    entry.access_count,
                    json.dumps(entry.tags),
                    content_hash
                ))
                
                conn.commit()
        
        return entry_id
    
    async def get_relevant_context(self, task: Task, max_results: int = 5) -> Dict[str, Any]:
        """
        Get relevant memory context for a task.
        
        Args:
            task: Current task
            max_results: Maximum number of memory entries to retrieve
            
        Returns:
            Dictionary with relevant context
        """
        # Build query based on task
        query = MemoryQuery(
            agent_id=self.agent_id,
            content_keywords=[task.task_type],
            tags=[task.task_type],
            min_importance=0.3,
            max_results=max_results
        )
        
        # Get relevant memories
        memories = await self.query_memories(query)
        
        # Organize context
        context = {
            "relevant_executions": [],
            "learned_patterns": [],
            "procedures": [],
            "working_memory": await self.get_working_memory()
        }
        
        for memory in memories:
            if memory.memory_type == MemoryType.EPISODIC:
                context["relevant_executions"].append({
                    "task_type": memory.content.get("task_type"),
                    "success": memory.content.get("result_success"),
                    "execution_time": memory.content.get("execution_time"),
                    "importance": memory.importance
                })
            elif memory.memory_type == MemoryType.SEMANTIC:
                context["learned_patterns"].append({
                    "pattern_type": memory.content.get("pattern_type"),
                    "pattern_data": memory.content.get("pattern_data"),
                    "confidence": memory.content.get("confidence"),
                    "importance": memory.importance
                })
            elif memory.memory_type == MemoryType.PROCEDURAL:
                context["procedures"].append({
                    "procedure_name": memory.content.get("procedure_name"),
                    "success_rate": memory.content.get("success_rate"),
                    "usage_count": memory.content.get("usage_count"),
                    "importance": memory.importance
                })
        
        return context
    
    async def query_memories(self, query: MemoryQuery) -> List[MemoryEntry]:
        """
        Query memories based on criteria.
        
        Args:
            query: Memory query parameters
            
        Returns:
            List of matching memory entries
        """
        async with self._connection_lock:
            with sqlite3.connect(self.db_path) as conn:
                # Build SQL query
                where_clauses = ["agent_id = ?"]
                params = [query.agent_id]
                
                # Memory types filter
                if query.memory_types:
                    type_placeholders = ",".join("?" * len(query.memory_types))
                    where_clauses.append(f"memory_type IN ({type_placeholders})")
                    params.extend([mt.value for mt in query.memory_types])
                
                # Importance filter
                if query.min_importance > 0:
                    where_clauses.append("importance >= ?")
                    params.append(query.min_importance)
                
                # Time range filter
                if query.time_range:
                    where_clauses.append("timestamp BETWEEN ? AND ?")
                    params.extend([dt.isoformat() for dt in query.time_range])
                
                # Content keywords filter
                if query.content_keywords:
                    keyword_conditions = []
                    for keyword in query.content_keywords:
                        keyword_conditions.append("content LIKE ?")
                        params.append(f"%{keyword}%")
                    where_clauses.append(f"({' OR '.join(keyword_conditions)})")
                
                # Tags filter
                if query.tags:
                    tag_conditions = []
                    for tag in query.tags:
                        tag_conditions.append("tags LIKE ?")
                        params.append(f"%{tag}%")
                    where_clauses.append(f"({' OR '.join(tag_conditions)})")
                
                sql = f"""
                    SELECT entry_id, agent_id, memory_type, content, timestamp,
                           importance, access_count, last_accessed, tags
                    FROM memories
                    WHERE {' AND '.join(where_clauses)}
                    ORDER BY importance DESC, timestamp DESC
                    LIMIT ?
                """
                params.append(query.max_results)
                
                cursor = conn.execute(sql, params)
                rows = cursor.fetchall()
                
                # Convert to MemoryEntry objects
                memories = []
                for row in rows:
                    entry = MemoryEntry(
                        entry_id=row[0],
                        agent_id=row[1],
                        memory_type=MemoryType(row[2]),
                        content=json.loads(row[3]),
                        timestamp=datetime.fromisoformat(row[4]),
                        importance=row[5],
                        access_count=row[6],
                        last_accessed=datetime.fromisoformat(row[7]) if row[7] else None,
                        tags=json.loads(row[8])
                    )
                    memories.append(entry)
                
                # Update access counts
                if memories:
                    entry_ids = [m.entry_id for m in memories]
                    placeholders = ",".join("?" * len(entry_ids))
                    conn.execute(f"""
                        UPDATE memories 
                        SET access_count = access_count + 1,
                            last_accessed = ?
                        WHERE entry_id IN ({placeholders})
                    """, [datetime.now().isoformat()] + entry_ids)
                    conn.commit()
                
                return memories
    
    async def get_working_memory(self) -> Dict[str, Any]:
        """Get current working memory (temporary context)."""
        query = MemoryQuery(
            agent_id=self.agent_id,
            memory_types=[MemoryType.WORKING],
            time_range=(datetime.now() - timedelta(hours=1), datetime.now()),
            max_results=20
        )
        
        memories = await self.query_memories(query)
        
        working_memory = {}
        for memory in memories:
            working_memory.update(memory.content)
        
        return working_memory
    
    async def update_working_memory(self, context: Dict[str, Any]) -> None:
        """Update working memory with current context."""
        await self.store_memory(
            memory_type=MemoryType.WORKING,
            content=context,
            importance=0.1,  # Low importance for working memory
            tags=["working", "current"]
        )
    
    def _calculate_importance(self, task: Task, result: Result) -> float:
        """Calculate importance score for a task execution."""
        base_importance = 0.5
        
        # Boost importance for successful results
        if result.success:
            base_importance += 0.2
        else:
            base_importance += 0.3  # Failures are often more important to remember
        
        # Boost importance for complex tasks
        if task.parameters:
            base_importance += min(0.2, len(task.parameters) * 0.05)
        
        # Boost importance for long-running tasks
        if result.execution_time > 10.0:
            base_importance += 0.1
        
        # Boost importance for tasks with warnings
        if result.warnings:
            base_importance += 0.1
        
        return max(0.0, min(1.0, base_importance))
    
    async def cleanup_old_memories(self, max_age_days: int = 30, min_importance: float = 0.3) -> int:
        """
        Clean up old, low-importance memories.
        
        Args:
            max_age_days: Maximum age for memories to keep
            min_importance: Minimum importance threshold
            
        Returns:
            Number of memories cleaned up
        """
        cutoff_date = datetime.now() - timedelta(days=max_age_days)
        
        async with self._connection_lock:
            with sqlite3.connect(self.db_path) as conn:
                # Don't clean up procedural memory (learned strategies)
                cursor = conn.execute("""
                    DELETE FROM memories 
                    WHERE agent_id = ? 
                    AND memory_type != ?
                    AND timestamp < ? 
                    AND importance < ?
                    AND access_count < 2
                """, (
                    self.agent_id,
                    MemoryType.PROCEDURAL.value,
                    cutoff_date.isoformat(),
                    min_importance
                ))
                
                cleaned_count = cursor.rowcount
                conn.commit()
                
                if cleaned_count > 0:
                    self.logger.info(f"Cleaned up {cleaned_count} old memories")
                
                return cleaned_count
    
    async def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory usage statistics."""
        async with self._connection_lock:
            with sqlite3.connect(self.db_path) as conn:
                # Total memories by type
                cursor = conn.execute("""
                    SELECT memory_type, COUNT(*), AVG(importance), AVG(access_count)
                    FROM memories 
                    WHERE agent_id = ?
                    GROUP BY memory_type
                """, (self.agent_id,))
                
                type_stats = {}
                for row in cursor.fetchall():
                    type_stats[row[0]] = {
                        "count": row[1],
                        "avg_importance": round(row[2], 3),
                        "avg_access_count": round(row[3], 1)
                    }
                
                # Recent activity
                cursor = conn.execute("""
                    SELECT COUNT(*) FROM memories 
                    WHERE agent_id = ? AND timestamp > ?
                """, (self.agent_id, (datetime.now() - timedelta(days=7)).isoformat()))
                
                recent_memories = cursor.fetchone()[0]
                
                # Database size
                cursor = conn.execute("SELECT page_count * page_size FROM pragma_page_count(), pragma_page_size()")
                db_size = cursor.fetchone()[0]
                
                return {
                    "agent_id": self.agent_id,
                    "total_memories": sum(stats["count"] for stats in type_stats.values()),
                    "memories_by_type": type_stats,
                    "recent_memories_7days": recent_memories,
                    "database_size_bytes": db_size,
                    "database_path": self.db_path
                }