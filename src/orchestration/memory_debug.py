"""
Memory System Debugging and Visualization Tools.

Provides utilities for inspecting, analyzing, and debugging the agent memory system,
including memory usage statistics, pattern analysis, and visualization helpers.
"""

import json
import sqlite3
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

from .memory import AgentMemory, MemoryType, MemoryQuery

logger = logging.getLogger(__name__)


class MemoryDebugger:
    """
    Debugging and analysis tools for agent memory systems.
    
    Provides detailed inspection of memory contents, usage patterns,
    and performance metrics for troubleshooting and optimization.
    """
    
    def __init__(self, agent_id: str = None, db_path: str = None):
        """
        Initialize memory debugger.
        
        Args:
            agent_id: Specific agent to debug (optional)
            db_path: Path to memory database (optional)
        """
        self.agent_id = agent_id
        self.db_path = db_path
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def analyze_agent_memory(self, agent_id: str) -> Dict[str, Any]:
        """
        Perform comprehensive analysis of an agent's memory.
        
        Args:
            agent_id: Agent to analyze
            
        Returns:
            Detailed analysis report
        """
        memory = AgentMemory(agent_id, self.db_path)
        
        # Get basic statistics
        stats = await memory.get_memory_stats()
        
        # Analyze memory patterns
        patterns = await self._analyze_memory_patterns(memory)
        
        # Check memory health
        health = await self._check_memory_health(memory)
        
        # Get recent activity
        recent_activity = await self._get_recent_activity(memory)
        
        return {
            "agent_id": agent_id,
            "timestamp": datetime.now().isoformat(),
            "basic_stats": stats,
            "patterns": patterns,
            "health": health,
            "recent_activity": recent_activity
        }
    
    async def _analyze_memory_patterns(self, memory: AgentMemory) -> Dict[str, Any]:
        """Analyze memory usage patterns."""
        patterns = {
            "learning_velocity": await self._calculate_learning_velocity(memory),
            "memory_distribution": await self._analyze_memory_distribution(memory),
            "access_patterns": await self._analyze_access_patterns(memory),
            "importance_distribution": await self._analyze_importance_distribution(memory)
        }
        
        return patterns
    
    async def _calculate_learning_velocity(self, memory: AgentMemory) -> Dict[str, Any]:
        """Calculate how quickly the agent is learning."""
        # Get memories from different time periods
        now = datetime.now()
        last_24h = now - timedelta(days=1)
        last_7d = now - timedelta(days=7)
        last_30d = now - timedelta(days=30)
        
        # Query memories by time period
        recent_query = MemoryQuery(
            agent_id=memory.agent_id,
            memory_types=[MemoryType.SEMANTIC, MemoryType.PROCEDURAL],
            time_range=(last_24h, now),
            max_results=100
        )
        
        week_query = MemoryQuery(
            agent_id=memory.agent_id,
            memory_types=[MemoryType.SEMANTIC, MemoryType.PROCEDURAL],
            time_range=(last_7d, now),
            max_results=500
        )
        
        month_query = MemoryQuery(
            agent_id=memory.agent_id,
            memory_types=[MemoryType.SEMANTIC, MemoryType.PROCEDURAL],
            time_range=(last_30d, now),
            max_results=1000
        )
        
        recent_memories = await memory.query_memories(recent_query)
        week_memories = await memory.query_memories(week_query)
        month_memories = await memory.query_memories(month_query)
        
        return {
            "memories_last_24h": len(recent_memories),
            "memories_last_7d": len(week_memories),
            "memories_last_30d": len(month_memories),
            "daily_learning_rate": len(recent_memories),
            "weekly_learning_rate": len(week_memories) / 7,
            "monthly_learning_rate": len(month_memories) / 30,
            "learning_trend": self._calculate_trend(recent_memories, week_memories, month_memories)
        }
    
    def _calculate_trend(self, recent: List, week: List, month: List) -> str:
        """Calculate learning trend."""
        daily_rate = len(recent)
        weekly_rate = len(week) / 7
        monthly_rate = len(month) / 30
        
        if daily_rate > weekly_rate * 1.2:
            return "accelerating"
        elif daily_rate < weekly_rate * 0.8:
            return "decelerating"
        else:
            return "stable"
    
    async def _analyze_memory_distribution(self, memory: AgentMemory) -> Dict[str, Any]:
        """Analyze distribution of memory types."""
        all_memories_query = MemoryQuery(
            agent_id=memory.agent_id,
            max_results=1000
        )
        
        memories = await memory.query_memories(all_memories_query)
        
        distribution = {}
        for mem_type in MemoryType:
            type_memories = [m for m in memories if m.memory_type == mem_type]
            distribution[mem_type.value] = {
                "count": len(type_memories),
                "avg_importance": sum(m.importance for m in type_memories) / len(type_memories) if type_memories else 0,
                "avg_access_count": sum(m.access_count for m in type_memories) / len(type_memories) if type_memories else 0
            }
        
        return distribution
    
    async def _analyze_access_patterns(self, memory: AgentMemory) -> Dict[str, Any]:
        """Analyze memory access patterns."""
        # Get all memories with access information
        all_memories_query = MemoryQuery(
            agent_id=memory.agent_id,
            max_results=1000
        )
        
        memories = await memory.query_memories(all_memories_query)
        
        # Calculate access statistics
        access_counts = [m.access_count for m in memories if m.access_count > 0]
        
        if not access_counts:
            return {"no_access_data": True}
        
        return {
            "total_accessed_memories": len(access_counts),
            "avg_access_count": sum(access_counts) / len(access_counts),
            "max_access_count": max(access_counts),
            "highly_accessed_memories": len([c for c in access_counts if c > 5]),
            "rarely_accessed_memories": len([c for c in access_counts if c == 1]),
            "access_distribution": self._create_access_histogram(access_counts)
        }
    
    def _create_access_histogram(self, access_counts: List[int]) -> Dict[str, int]:
        """Create histogram of access counts."""
        histogram = {
            "1_access": 0,
            "2-5_accesses": 0,
            "6-10_accesses": 0,
            "11-20_accesses": 0,
            "20+_accesses": 0
        }
        
        for count in access_counts:
            if count == 1:
                histogram["1_access"] += 1
            elif count <= 5:
                histogram["2-5_accesses"] += 1
            elif count <= 10:
                histogram["6-10_accesses"] += 1
            elif count <= 20:
                histogram["11-20_accesses"] += 1
            else:
                histogram["20+_accesses"] += 1
        
        return histogram
    
    async def _analyze_importance_distribution(self, memory: AgentMemory) -> Dict[str, Any]:
        """Analyze importance score distribution."""
        all_memories_query = MemoryQuery(
            agent_id=memory.agent_id,
            max_results=1000
        )
        
        memories = await memory.query_memories(all_memories_query)
        importance_scores = [m.importance for m in memories]
        
        if not importance_scores:
            return {"no_importance_data": True}
        
        return {
            "avg_importance": sum(importance_scores) / len(importance_scores),
            "max_importance": max(importance_scores),
            "min_importance": min(importance_scores),
            "high_importance_memories": len([s for s in importance_scores if s > 0.8]),
            "medium_importance_memories": len([s for s in importance_scores if 0.5 <= s <= 0.8]),
            "low_importance_memories": len([s for s in importance_scores if s < 0.5]),
            "importance_histogram": self._create_importance_histogram(importance_scores)
        }
    
    def _create_importance_histogram(self, scores: List[float]) -> Dict[str, int]:
        """Create histogram of importance scores."""
        histogram = {
            "0.0-0.2": 0,
            "0.2-0.4": 0,
            "0.4-0.6": 0,
            "0.6-0.8": 0,
            "0.8-1.0": 0
        }
        
        for score in scores:
            if score < 0.2:
                histogram["0.0-0.2"] += 1
            elif score < 0.4:
                histogram["0.2-0.4"] += 1
            elif score < 0.6:
                histogram["0.4-0.6"] += 1
            elif score < 0.8:
                histogram["0.6-0.8"] += 1
            else:
                histogram["0.8-1.0"] += 1
        
        return histogram
    
    async def _check_memory_health(self, memory: AgentMemory) -> Dict[str, Any]:
        """Check overall memory system health."""
        stats = await memory.get_memory_stats()
        
        health_issues = []
        health_score = 1.0
        
        # Check for excessive memory usage
        total_memories = stats.get("total_memories", 0)
        if total_memories > 10000:
            health_issues.append("Excessive memory usage (>10k memories)")
            health_score -= 0.2
        
        # Check for imbalanced memory types
        type_stats = stats.get("memories_by_type", {})
        if type_stats:
            episodic_count = type_stats.get("episodic", {}).get("count", 0)
            semantic_count = type_stats.get("semantic", {}).get("count", 0)
            
            if total_memories > 100:  # Only check if we have significant memories
                if episodic_count > semantic_count * 10:
                    health_issues.append("Too many episodic memories vs semantic learning")
                    health_score -= 0.1
                elif semantic_count == 0 and episodic_count > 50:
                    health_issues.append("No semantic learning detected")
                    health_score -= 0.3
        
        # Check database size
        db_size = stats.get("database_size_bytes", 0)
        if db_size > 100 * 1024 * 1024:  # 100MB
            health_issues.append("Large database size (>100MB)")
            health_score -= 0.1
        
        # Check recent activity
        recent_memories = stats.get("recent_memories_7days", 0)
        if recent_memories == 0 and total_memories > 0:
            health_issues.append("No recent memory activity")
            health_score -= 0.2
        
        return {
            "health_score": max(0.0, health_score),
            "status": "healthy" if health_score > 0.8 else "needs_attention" if health_score > 0.5 else "unhealthy",
            "issues": health_issues,
            "recommendations": self._generate_health_recommendations(health_issues, stats)
        }
    
    def _generate_health_recommendations(self, issues: List[str], stats: Dict) -> List[str]:
        """Generate recommendations based on health issues."""
        recommendations = []
        
        for issue in issues:
            if "Excessive memory usage" in issue:
                recommendations.append("Run memory cleanup to remove old, low-importance memories")
            elif "Too many episodic memories" in issue:
                recommendations.append("Increase learning threshold to generate more semantic memories")
            elif "No semantic learning" in issue:
                recommendations.append("Check learning algorithms - agent may not be extracting patterns")
            elif "Large database size" in issue:
                recommendations.append("Archive old memories or increase cleanup frequency")
            elif "No recent memory activity" in issue:
                recommendations.append("Check if agent is actively processing tasks")
        
        return recommendations
    
    async def _get_recent_activity(self, memory: AgentMemory) -> Dict[str, Any]:
        """Get recent memory activity."""
        recent_query = MemoryQuery(
            agent_id=memory.agent_id,
            time_range=(datetime.now() - timedelta(days=7), datetime.now()),
            max_results=50
        )
        
        recent_memories = await memory.query_memories(recent_query)
        
        # Group by day
        daily_activity = {}
        for memory_entry in recent_memories:
            day = memory_entry.timestamp.date().isoformat()
            if day not in daily_activity:
                daily_activity[day] = {"episodic": 0, "semantic": 0, "procedural": 0, "working": 0}
            daily_activity[day][memory_entry.memory_type.value] += 1
        
        return {
            "total_recent_memories": len(recent_memories),
            "daily_activity": daily_activity,
            "most_recent_memories": [
                {
                    "type": m.memory_type.value,
                    "timestamp": m.timestamp.isoformat(),
                    "importance": m.importance,
                    "content_type": self._extract_content_type(m.content)
                }
                for m in recent_memories[:10]
            ]
        }
    
    def _extract_content_type(self, content: Dict[str, Any]) -> str:
        """Extract readable content type from memory content."""
        if "task_type" in content:
            return f"task: {content['task_type']}"
        elif "pattern_type" in content:
            return f"pattern: {content['pattern_type']}"
        elif "procedure_name" in content:
            return f"procedure: {content['procedure_name']}"
        else:
            return "unknown"
    
    async def dump_agent_memories(self, agent_id: str, output_file: str = None) -> str:
        """
        Dump all memories for an agent to JSON file.
        
        Args:
            agent_id: Agent to dump
            output_file: Output file path (optional)
            
        Returns:
            Path to created file
        """
        memory = AgentMemory(agent_id, self.db_path)
        
        # Get all memories
        all_memories_query = MemoryQuery(
            agent_id=agent_id,
            max_results=10000
        )
        
        memories = await memory.query_memories(all_memories_query)
        
        # Convert to serializable format
        memory_data = []
        for mem in memories:
            memory_data.append({
                "entry_id": mem.entry_id,
                "agent_id": mem.agent_id,
                "memory_type": mem.memory_type.value,
                "content": mem.content,
                "timestamp": mem.timestamp.isoformat(),
                "importance": mem.importance,
                "access_count": mem.access_count,
                "last_accessed": mem.last_accessed.isoformat() if mem.last_accessed else None,
                "tags": mem.tags
            })
        
        # Create output file
        if output_file is None:
            output_file = f"memory_dump_{agent_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump({
                "agent_id": agent_id,
                "dump_timestamp": datetime.now().isoformat(),
                "total_memories": len(memory_data),
                "memories": memory_data
            }, f, indent=2)
        
        self.logger.info(f"Dumped {len(memory_data)} memories to {output_path}")
        return str(output_path)
    
    async def compare_agent_memories(self, agent_id1: str, agent_id2: str) -> Dict[str, Any]:
        """
        Compare memory patterns between two agents.
        
        Args:
            agent_id1: First agent to compare
            agent_id2: Second agent to compare
            
        Returns:
            Comparison analysis
        """
        analysis1 = await self.analyze_agent_memory(agent_id1)
        analysis2 = await self.analyze_agent_memory(agent_id2)
        
        return {
            "agent1": agent_id1,
            "agent2": agent_id2,
            "comparison_timestamp": datetime.now().isoformat(),
            "memory_counts": {
                "agent1": analysis1["basic_stats"]["total_memories"],
                "agent2": analysis2["basic_stats"]["total_memories"]
            },
            "learning_rates": {
                "agent1": analysis1["patterns"]["learning_velocity"]["daily_learning_rate"],
                "agent2": analysis2["patterns"]["learning_velocity"]["daily_learning_rate"]
            },
            "health_scores": {
                "agent1": analysis1["health"]["health_score"],
                "agent2": analysis2["health"]["health_score"]
            },
            "memory_distribution_comparison": self._compare_distributions(
                analysis1["patterns"]["memory_distribution"],
                analysis2["patterns"]["memory_distribution"]
            )
        }
    
    def _compare_distributions(self, dist1: Dict, dist2: Dict) -> Dict[str, Any]:
        """Compare memory type distributions."""
        comparison = {}
        
        for memory_type in MemoryType:
            type_key = memory_type.value
            
            count1 = dist1.get(type_key, {}).get("count", 0)
            count2 = dist2.get(type_key, {}).get("count", 0)
            
            comparison[type_key] = {
                "agent1": count1,
                "agent2": count2,
                "difference": count1 - count2,
                "ratio": count1 / count2 if count2 > 0 else float('inf')
            }
        
        return comparison


class MemoryVisualizer:
    """
    Memory visualization tools for creating charts and reports.
    
    Provides methods to generate visual representations of memory data
    for debugging and analysis purposes.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def create_memory_report(self, analysis: Dict[str, Any]) -> str:
        """
        Create human-readable memory analysis report.
        
        Args:
            analysis: Analysis data from MemoryDebugger
            
        Returns:
            Formatted report string
        """
        report = []
        report.append(f"Memory Analysis Report for Agent: {analysis['agent_id']}")
        report.append("=" * 60)
        report.append(f"Generated: {analysis['timestamp']}")
        report.append("")
        
        # Basic Stats
        stats = analysis["basic_stats"]
        report.append("Basic Statistics:")
        report.append(f"  Total Memories: {stats['total_memories']}")
        report.append(f"  Recent Memories (7 days): {stats['recent_memories_7days']}")
        report.append(f"  Database Size: {self._format_bytes(stats['database_size_bytes'])}")
        report.append("")
        
        # Memory Distribution
        if "memory_distribution" in analysis["patterns"]:
            report.append("Memory Type Distribution:")
            for mem_type, data in analysis["patterns"]["memory_distribution"].items():
                report.append(f"  {mem_type.title()}: {data['count']} memories (avg importance: {data['avg_importance']:.2f})")
            report.append("")
        
        # Learning Velocity
        if "learning_velocity" in analysis["patterns"]:
            velocity = analysis["patterns"]["learning_velocity"]
            report.append("Learning Activity:")
            report.append(f"  Last 24 hours: {velocity['memories_last_24h']} new memories")
            report.append(f"  Daily learning rate: {velocity['daily_learning_rate']:.1f} memories/day")
            report.append(f"  Learning trend: {velocity['learning_trend']}")
            report.append("")
        
        # Health Status
        health = analysis["health"]
        report.append("Health Status:")
        report.append(f"  Overall Score: {health['health_score']:.2f}/1.0 ({health['status']})")
        if health["issues"]:
            report.append("  Issues:")
            for issue in health["issues"]:
                report.append(f"    - {issue}")
        if health["recommendations"]:
            report.append("  Recommendations:")
            for rec in health["recommendations"]:
                report.append(f"    - {rec}")
        report.append("")
        
        # Recent Activity
        if "recent_activity" in analysis:
            activity = analysis["recent_activity"]
            report.append(f"Recent Activity ({activity['total_recent_memories']} memories in last 7 days):")
            if activity["most_recent_memories"]:
                report.append("  Most Recent:")
                for mem in activity["most_recent_memories"][:5]:
                    report.append(f"    {mem['timestamp'][:19]} - {mem['content_type']} (importance: {mem['importance']:.2f})")
        
        return "\n".join(report)
    
    def _format_bytes(self, bytes_value: int) -> str:
        """Format bytes as human-readable string."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_value < 1024:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024
        return f"{bytes_value:.1f} TB"


# Utility functions for easy debugging
async def debug_agent_memory(agent_id: str, output_dir: str = "debug_output") -> str:
    """
    Quick debug function for analyzing agent memory.
    
    Args:
        agent_id: Agent to debug
        output_dir: Directory for output files
        
    Returns:
        Path to generated report
    """
    debugger = MemoryDebugger()
    visualizer = MemoryVisualizer()
    
    # Analyze memory
    analysis = await debugger.analyze_agent_memory(agent_id)
    
    # Create report
    report = visualizer.create_memory_report(analysis)
    
    # Save report
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    report_file = output_path / f"memory_debug_{agent_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"Memory debug report saved to: {report_file}")
    return str(report_file)


async def cleanup_agent_memory(agent_id: str, max_age_days: int = 30, min_importance: float = 0.3) -> int:
    """
    Quick cleanup function for agent memory.
    
    Args:
        agent_id: Agent to clean up
        max_age_days: Maximum age for memories to keep
        min_importance: Minimum importance threshold
        
    Returns:
        Number of memories cleaned up
    """
    memory = AgentMemory(agent_id)
    cleaned = await memory.cleanup_old_memories(max_age_days, min_importance)
    
    print(f"Cleaned up {cleaned} old memories for agent {agent_id}")
    return cleaned