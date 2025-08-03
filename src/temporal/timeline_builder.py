"""
Timeline Builder for Temporal Pattern Analysis
"""

import logging
from datetime import datetime
from typing import List, Dict, Any
from dataclasses import dataclass

from src.temporal.temporal_analyzer import Timeline, TemporalEvent

logger = logging.getLogger(__name__)


class TimelineBuilder:
    """Builds timelines for concepts and entities"""
    
    def __init__(self):
        self.logger = logger
        
    async def build_concept_timeline(self,
                                    documents: List[Dict[str, Any]],
                                    concept: str) -> Timeline:
        """Build timeline for a specific concept"""
        self.logger.info(f"Building timeline for concept: {concept}")
        
        events = []
        
        for doc in documents:
            content = doc.get("content", "")
            if concept.lower() in content.lower():
                timestamp = self._parse_timestamp(doc.get("timestamp"))
                
                event = TemporalEvent(
                    event_id=f"timeline_{doc['id']}_{concept}",
                    concept=concept,
                    timestamp=timestamp,
                    document_id=doc["id"],
                    context=self._extract_context(content, concept),
                    confidence=self._calculate_confidence(content, concept)
                )
                events.append(event)
        
        if not events:
            return None
        
        events.sort(key=lambda e: e.timestamp)
        
        return Timeline(
            concept=concept,
            events=events,
            start_date=events[0].timestamp,
            end_date=events[-1].timestamp,
            summary=self._generate_timeline_summary(events, concept)
        )
    
    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """Parse timestamp string to datetime"""
        if isinstance(timestamp_str, datetime):
            return timestamp_str
        return datetime.fromisoformat(timestamp_str)
    
    def _extract_context(self, content: str, concept: str) -> str:
        """Extract context around concept mention"""
        concept_lower = concept.lower()
        content_lower = content.lower()
        
        pos = content_lower.find(concept_lower)
        if pos == -1:
            return content[:100]
        
        # Get 50 chars before and after
        start = max(0, pos - 50)
        end = min(len(content), pos + len(concept) + 50)
        
        return content[start:end]
    
    def _calculate_confidence(self, content: str, concept: str) -> float:
        """Calculate confidence for concept mention"""
        content_lower = content.lower()
        concept_lower = concept.lower()
        
        # Simple confidence based on mention frequency
        mentions = content_lower.count(concept_lower)
        confidence = min(1.0, 0.5 + (mentions * 0.1))
        
        return confidence
    
    def _generate_timeline_summary(self, events: List[TemporalEvent], concept: str) -> str:
        """Generate summary for timeline"""
        if not events:
            return ""
        
        duration = (events[-1].timestamp - events[0].timestamp).days
        
        return f"Timeline for '{concept}' spans {duration} days with {len(events)} events"