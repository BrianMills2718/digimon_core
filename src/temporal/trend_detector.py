"""
Trend Detector for Temporal Pattern Analysis
"""

import logging
from datetime import datetime
from typing import List, Dict, Any
from dataclasses import dataclass
from collections import defaultdict
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class Trend:
    """Represents a detected trend"""
    concept: str
    trend_type: str  # "emerging", "declining", "stable", "cyclical"
    start_date: datetime
    end_date: datetime
    strength: float
    confidence: float
    supporting_documents: List[str]


class TrendDetector:
    """Detects trends in temporal data"""
    
    def __init__(self):
        self.logger = logger
        
    async def detect_trends(self,
                           documents: List[Dict[str, Any]],
                           min_support: float = 0.2) -> List[Trend]:
        """Detect trends from documents"""
        self.logger.info(f"Detecting trends with min support {min_support}")
        
        # Extract concept frequencies over time
        concept_timelines = self._extract_concept_timelines(documents)
        
        trends = []
        
        for concept, timeline in concept_timelines.items():
            # For concepts with few data points, check if they're late-emerging
            if len(timeline) < 3:
                if len(timeline) >= 2:
                    # Check if this is a late-emerging concept
                    all_years = sorted(set(self._parse_timestamp(d["timestamp"]).year for d in documents))
                    timeline_years = [t[0].year for t in timeline]
                    
                    # If concept only appears in last 40% of time span, it's emerging
                    if min(timeline_years) > all_years[len(all_years) * 3 // 5]:
                        trend_type = "emerging"
                        strength = 0.8
                        support = len(timeline) / len(documents)
                        if support >= min_support:
                            trends.append(Trend(
                                concept=concept,
                                trend_type=trend_type,
                                start_date=timeline[0][0],
                                end_date=timeline[-1][0],
                                strength=strength,
                                confidence=min(0.9, support * 2),
                                supporting_documents=[point[2] for point in timeline]
                            ))
                continue
            
            # Analyze trend
            trend_type = self._analyze_trend_type(timeline)
            strength = self._calculate_trend_strength(timeline)
            
            # Check support threshold
            support = len(timeline) / len(documents)
            if support < min_support:
                continue
            
            # Get supporting documents
            supporting_docs = [point[2] for point in timeline]
            
            trends.append(Trend(
                concept=concept,
                trend_type=trend_type,
                start_date=timeline[0][0],
                end_date=timeline[-1][0],
                strength=strength,
                confidence=min(0.9, support * 2),
                supporting_documents=supporting_docs
            ))
        
        return trends
    
    def _extract_concept_timelines(self, documents: List[Dict[str, Any]]) -> Dict[str, List]:
        """Extract timelines for each concept"""
        timelines = defaultdict(list)
        
        # Define concepts to track - include multi-word concepts
        concepts = ["AI", "safety", "quantum", "research", "technology", "AI safety"]
        
        for doc in documents:
            timestamp = self._parse_timestamp(doc.get("timestamp"))
            content = doc.get("content", "").lower()
            
            for concept in concepts:
                if concept.lower() in content:
                    # Calculate importance with more weight
                    importance = content.count(concept.lower()) * 0.1
                    timelines[concept].append((timestamp, importance, doc["id"]))
        
        # Sort timelines
        for concept in timelines:
            timelines[concept].sort(key=lambda x: x[0])
        
        return timelines
    
    def _analyze_trend_type(self, timeline: List) -> str:
        """Analyze type of trend"""
        if len(timeline) < 3:
            return "insufficient_data"
        
        # Extract importance values
        values = [point[1] for point in timeline]
        
        # Calculate trend metrics - handle when concept doesn't appear in early period
        early_values = values[:len(values)//3]
        late_values = values[2*len(values)//3:]
        
        early_avg = np.mean(early_values) if early_values else 0.0
        late_avg = np.mean(late_values) if late_values else 0.0
        
        # Special case: concept emerges from nothing
        if early_avg == 0 and late_avg > 0:
            return "emerging"
        
        # Determine trend type with lower threshold for emerging
        if late_avg > early_avg * 1.2 and late_avg > 0.01:  # Must have meaningful late value
            return "emerging"
        elif early_avg > late_avg * 1.5:
            return "declining"
        elif abs(late_avg - early_avg) < 0.1:
            return "stable"
        else:
            # Check for cyclical pattern
            if self._is_cyclical(values):
                return "cyclical"
            else:
                return "stable"
    
    def _calculate_trend_strength(self, timeline: List) -> float:
        """Calculate strength of trend"""
        if len(timeline) < 2:
            return 0.0
        
        values = [point[1] for point in timeline]
        
        # Calculate rate of change
        changes = []
        for i in range(1, len(values)):
            change = abs(values[i] - values[i-1])
            changes.append(change)
        
        avg_change = np.mean(changes)
        
        # Normalize to 0-1 range
        strength = min(1.0, avg_change * 10)
        
        return strength
    
    def _is_cyclical(self, values: List[float]) -> bool:
        """Check if values show cyclical pattern"""
        if len(values) < 6:
            return False
        
        # Simple peak detection
        peaks = []
        for i in range(1, len(values)-1):
            if values[i] > values[i-1] and values[i] > values[i+1]:
                peaks.append(i)
        
        # Check for regular peaks
        if len(peaks) >= 2:
            intervals = []
            for i in range(1, len(peaks)):
                intervals.append(peaks[i] - peaks[i-1])
            
            # Check if intervals are similar
            if intervals:
                avg_interval = np.mean(intervals)
                std_interval = np.std(intervals)
                
                # Low standard deviation indicates regular pattern
                if std_interval < avg_interval * 0.3:
                    return True
        
        return False
    
    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """Parse timestamp string to datetime"""
        if isinstance(timestamp_str, datetime):
            return timestamp_str
        return datetime.fromisoformat(timestamp_str)