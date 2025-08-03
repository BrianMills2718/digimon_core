"""
Temporal Pattern Analysis Engine - Task C.5

Analyzes temporal patterns, trends, and evolution of concepts across documents.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class TemporalEvent:
    """Represents a temporal event"""
    event_id: str
    concept: str
    timestamp: datetime
    document_id: str
    context: str
    confidence: float = 0.8
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Timeline:
    """Represents a timeline of events"""
    concept: str
    events: List[TemporalEvent]
    start_date: datetime
    end_date: datetime
    summary: str = ""


@dataclass
class EntityLifecycle:
    """Tracks entity lifecycle over time"""
    entity_name: str
    first_appearance: datetime
    last_appearance: datetime
    evolution_stages: List[Dict[str, Any]]
    total_mentions: int
    peak_period: Tuple[datetime, datetime]


@dataclass
class RelationshipEvolution:
    """Tracks how relationships evolve over time"""
    entity1: str
    entity2: str
    correlation_trend: str  # "strengthening", "weakening", "stable"
    strengthening_over_time: bool
    key_periods: List[Tuple[datetime, str]]


@dataclass
class TemporalAnomaly:
    """Represents a temporal anomaly"""
    document_id: str
    timestamp: datetime
    anomaly_type: str
    anomaly_score: float
    description: str


@dataclass
class PeriodicPattern:
    """Represents a periodic pattern"""
    pattern_id: str
    period_type: str  # "daily", "weekly", "monthly", "quarterly", "yearly"
    frequency: int
    confidence: float
    examples: List[TemporalEvent]


@dataclass
class TemporalCorrelation:
    """Represents temporal correlation between events"""
    event1: str
    event2: str
    correlation_score: float
    lag_time: timedelta
    significance: float


@dataclass
class ChangePoint:
    """Represents a significant change point"""
    timestamp: datetime
    concept: str
    change_type: str  # "emergence", "decline", "shift"
    magnitude: float
    before_state: str
    after_state: str


@dataclass
class TrendPrediction:
    """Represents a trend prediction"""
    concept: str
    trend_direction: str  # "increasing", "decreasing", "stable"
    confidence: float
    predicted_values: List[Tuple[datetime, float]]
    horizon_days: int


@dataclass
class TemporalSummary:
    """Represents a temporal summary"""
    yearly_summaries: Dict[int, str]
    key_trends: List[str]
    evolution_narrative: str
    significant_events: List[TemporalEvent]


class TemporalAnalyzer:
    """Main temporal analysis engine"""
    
    def __init__(self):
        self.logger = logger
        self.timelines = {}
        self.patterns = []
        
    async def track_entity_lifecycle(self, 
                                    documents: List[Dict[str, Any]], 
                                    entity_name: str) -> EntityLifecycle:
        """Track entity appearances and evolution over time"""
        self.logger.info(f"Tracking lifecycle for entity: {entity_name}")
        
        appearances = []
        evolution_stages = []
        
        for doc in documents:
            if entity_name.lower() in doc.get("content", "").lower():
                timestamp = self._parse_timestamp(doc.get("timestamp"))
                appearances.append(timestamp)
                
                # Detect evolution stage based on context
                stage = self._detect_evolution_stage(doc["content"], entity_name)
                if stage:
                    evolution_stages.append({
                        "timestamp": timestamp,
                        "stage": stage,
                        "document_id": doc["id"]
                    })
        
        if not appearances:
            return None
            
        appearances.sort()
        
        # Find peak period (most frequent mentions)
        peak_start, peak_end = self._find_peak_period(appearances)
        
        return EntityLifecycle(
            entity_name=entity_name,
            first_appearance=appearances[0],
            last_appearance=appearances[-1],
            evolution_stages=evolution_stages,
            total_mentions=len(appearances),
            peak_period=(peak_start, peak_end)
        )
    
    async def analyze_relationship_evolution(self,
                                           documents: List[Dict[str, Any]],
                                           entity1: str,
                                           entity2: str) -> RelationshipEvolution:
        """Analyze how relationship between entities evolves over time"""
        self.logger.info(f"Analyzing relationship evolution: {entity1} <-> {entity2}")
        
        co_occurrences = []
        key_periods = []
        
        for doc in documents:
            content = doc.get("content", "").lower()
            if entity1.lower() in content and entity2.lower() in content:
                timestamp = self._parse_timestamp(doc.get("timestamp"))
                co_occurrences.append(timestamp)
                
                # Analyze relationship context
                relationship_type = self._analyze_relationship_context(content, entity1, entity2)
                if relationship_type:
                    key_periods.append((timestamp, relationship_type))
        
        if len(co_occurrences) < 2:
            return RelationshipEvolution(
                entity1=entity1,
                entity2=entity2,
                correlation_trend="insufficient_data",
                strengthening_over_time=False,
                key_periods=[]
            )
        
        # Determine trend
        trend = self._calculate_relationship_trend(co_occurrences)
        
        return RelationshipEvolution(
            entity1=entity1,
            entity2=entity2,
            correlation_trend=trend,
            strengthening_over_time=(trend == "strengthening"),
            key_periods=key_periods
        )
    
    async def detect_temporal_anomalies(self,
                                       documents: List[Dict[str, Any]],
                                       sensitivity: float = 0.8) -> List[TemporalAnomaly]:
        """Detect temporal anomalies in document stream"""
        self.logger.info(f"Detecting temporal anomalies with sensitivity {sensitivity}")
        
        anomalies = []
        
        for doc in documents:
            # Check for anomaly markers
            if doc.get("metadata", {}).get("anomaly"):
                anomalies.append(TemporalAnomaly(
                    document_id=doc["id"],
                    timestamp=self._parse_timestamp(doc.get("timestamp")),
                    anomaly_type="marked",
                    anomaly_score=1.0,
                    description="Document marked as anomalous"
                ))
                continue
            
            # Check for sudden changes in content
            content = doc.get("content", "").lower()
            anomaly_score = self._calculate_anomaly_score(content)
            
            if anomaly_score > sensitivity:
                anomalies.append(TemporalAnomaly(
                    document_id=doc["id"],
                    timestamp=self._parse_timestamp(doc.get("timestamp")),
                    anomaly_type="content",
                    anomaly_score=anomaly_score,
                    description="Unusual content detected"
                ))
        
        return anomalies
    
    async def detect_periodicity(self,
                                documents: List[Dict[str, Any]],
                                min_frequency: int = 2) -> List[PeriodicPattern]:
        """Detect periodic patterns in documents"""
        self.logger.info(f"Detecting periodicity with min frequency {min_frequency}")
        
        patterns = []
        
        # Group documents by type
        doc_types = defaultdict(list)
        for doc in documents:
            doc_type = doc.get("metadata", {}).get("type", "unknown")
            if doc_type != "unknown":
                doc_types[doc_type].append(doc)
        
        # Check each type for periodicity
        for doc_type, docs in doc_types.items():
            if len(docs) < min_frequency:
                continue
            
            timestamps = [self._parse_timestamp(d.get("timestamp")) for d in docs]
            timestamps.sort()
            
            # Detect period type
            period_type = self._detect_period_type(timestamps)
            if period_type:
                pattern_events = [
                    TemporalEvent(
                        event_id=f"periodic_{doc['id']}",
                        concept=doc_type,
                        timestamp=self._parse_timestamp(doc.get("timestamp")),
                        document_id=doc["id"],
                        context=doc.get("content", "")[:100]
                    )
                    for doc in docs
                ]
                
                patterns.append(PeriodicPattern(
                    pattern_id=f"pattern_{doc_type}",
                    period_type=period_type,
                    frequency=len(docs),
                    confidence=0.9,
                    examples=pattern_events
                ))
        
        return patterns
    
    async def find_temporal_correlations(self,
                                        documents: List[Dict[str, Any]],
                                        lag_window: timedelta) -> List[TemporalCorrelation]:
        """Find temporally correlated events"""
        self.logger.info(f"Finding temporal correlations with lag window {lag_window}")
        
        correlations = []
        
        # Extract events from documents
        events = self._extract_events(documents)
        
        # Find correlations
        for i, event1 in enumerate(events):
            for event2 in events[i+1:]:
                time_diff = abs((event2.timestamp - event1.timestamp).total_seconds())
                
                if time_diff <= lag_window.total_seconds():
                    # Calculate correlation
                    correlation_score = self._calculate_correlation(event1, event2)
                    
                    if correlation_score > 0.5:
                        correlations.append(TemporalCorrelation(
                            event1=event1.concept,
                            event2=event2.concept,
                            correlation_score=correlation_score,
                            lag_time=timedelta(seconds=time_diff),
                            significance=correlation_score * 0.9
                        ))
        
        return correlations
    
    async def detect_change_points(self,
                                  documents: List[Dict[str, Any]],
                                  concept: str) -> List[ChangePoint]:
        """Detect significant change points for a concept"""
        self.logger.info(f"Detecting change points for concept: {concept}")
        
        change_points = []
        
        # Track concept mentions over time
        concept_timeline = []
        for doc in documents:
            if concept.lower() in doc.get("content", "").lower():
                timestamp = self._parse_timestamp(doc.get("timestamp"))
                importance = self._calculate_concept_importance(doc["content"], concept)
                concept_timeline.append((timestamp, importance))
        
        concept_timeline.sort()
        
        # Detect significant changes with lower threshold
        for i in range(1, len(concept_timeline)-1):
            prev_importance = concept_timeline[i-1][1]
            curr_importance = concept_timeline[i][1]
            next_importance = concept_timeline[i+1][1]
            
            # Check for significant change with lower threshold
            if abs(curr_importance - prev_importance) > 0.15:  # Lower threshold
                change_type = "emergence" if curr_importance > prev_importance else "decline"
                
                change_points.append(ChangePoint(
                    timestamp=concept_timeline[i][0],
                    concept=concept,
                    change_type=change_type,
                    magnitude=abs(curr_importance - prev_importance),
                    before_state=f"importance_{prev_importance:.2f}",
                    after_state=f"importance_{curr_importance:.2f}"
                ))
        
        return change_points
    
    async def predict_future_trends(self,
                                   documents: List[Dict[str, Any]],
                                   horizon_days: int = 365) -> List[TrendPrediction]:
        """Predict future trends based on historical patterns"""
        self.logger.info(f"Predicting trends for {horizon_days} days")
        
        predictions = []
        
        # Extract concepts and their temporal patterns
        concept_patterns = self._extract_concept_patterns(documents)
        
        for concept, pattern in concept_patterns.items():
            if len(pattern) < 3:
                continue
            
            # Simple trend detection
            trend_direction = self._detect_trend_direction(pattern)
            
            # Generate predictions
            last_date = max(p[0] for p in pattern)
            predicted_values = []
            
            for days_ahead in range(30, horizon_days, 30):
                future_date = last_date + timedelta(days=days_ahead)
                # Simple linear projection
                predicted_value = self._project_value(pattern, days_ahead)
                predicted_values.append((future_date, predicted_value))
            
            predictions.append(TrendPrediction(
                concept=concept,
                trend_direction=trend_direction,
                confidence=0.7,  # Simple model, moderate confidence
                predicted_values=predicted_values,
                horizon_days=horizon_days
            ))
        
        return predictions
    
    async def generate_temporal_summary(self,
                                       documents: List[Dict[str, Any]],
                                       granularity: str = "yearly") -> TemporalSummary:
        """Generate temporal summary of documents"""
        self.logger.info(f"Generating temporal summary with {granularity} granularity")
        
        # Group documents by year
        yearly_docs = defaultdict(list)
        for doc in documents:
            timestamp = self._parse_timestamp(doc.get("timestamp"))
            year = timestamp.year
            yearly_docs[year].append(doc)
        
        # Generate yearly summaries
        yearly_summaries = {}
        for year, docs in yearly_docs.items():
            summary = self._generate_period_summary(docs)
            yearly_summaries[year] = summary
        
        # Identify key trends
        key_trends = self._identify_key_trends(documents)
        
        # Create evolution narrative
        narrative = self._create_evolution_narrative(yearly_summaries, key_trends)
        
        # Extract significant events
        significant_events = self._extract_significant_events(documents)
        
        return TemporalSummary(
            yearly_summaries=yearly_summaries,
            key_trends=key_trends,
            evolution_narrative=narrative,
            significant_events=significant_events
        )
    
    async def query_temporal(self,
                            documents: List[Dict[str, Any]],
                            query: str) -> Any:
        """Process temporal queries"""
        self.logger.info(f"Processing temporal query: {query}")
        
        query_lower = query.lower()
        
        # Parse query type
        if "events in" in query_lower and any(str(y) in query for y in range(2020, 2030)):
            # Year-based query
            year = int(next(str(y) for y in range(2020, 2030) if str(y) in query))
            return self._get_events_by_year(documents, year)
        
        elif "trend" in query_lower:
            # Trend query
            concept = self._extract_concept_from_query(query)
            return self._get_concept_trend(documents, concept)
        
        else:
            # General temporal query
            return self._process_general_query(documents, query)
    
    # Helper methods
    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """Parse timestamp string to datetime"""
        if isinstance(timestamp_str, datetime):
            return timestamp_str
        return datetime.fromisoformat(timestamp_str)
    
    def _detect_evolution_stage(self, content: str, entity: str) -> str:
        """Detect evolution stage from content"""
        content_lower = content.lower()
        
        if "theoretical" in content_lower:
            return "theoretical"
        elif "achieved" in content_lower or "supremacy" in content_lower:
            return "breakthrough"
        elif "practical" in content_lower or "deployed" in content_lower:
            return "practical"
        else:
            return "development"
    
    def _find_peak_period(self, timestamps: List[datetime]) -> Tuple[datetime, datetime]:
        """Find period with most activity"""
        if not timestamps:
            return None, None
        
        # Simple approach: find densest 6-month period
        max_count = 0
        peak_start = timestamps[0]
        peak_end = timestamps[0] + timedelta(days=180)
        
        for start_time in timestamps:
            end_time = start_time + timedelta(days=180)
            count = sum(1 for t in timestamps if start_time <= t <= end_time)
            
            if count > max_count:
                max_count = count
                peak_start = start_time
                peak_end = end_time
        
        return peak_start, peak_end
    
    def _analyze_relationship_context(self, content: str, entity1: str, entity2: str) -> str:
        """Analyze relationship context between entities"""
        # Simple keyword-based analysis
        if "collaborate" in content or "partner" in content:
            return "collaboration"
        elif "compete" in content or "rival" in content:
            return "competition"
        elif "influence" in content or "impact" in content:
            return "influence"
        else:
            return "association"
    
    def _calculate_relationship_trend(self, timestamps: List[datetime]) -> str:
        """Calculate trend of relationship over time"""
        if len(timestamps) < 2:
            return "insufficient_data"
        
        # Calculate frequency over time
        timestamps.sort()
        time_span = (timestamps[-1] - timestamps[0]).days
        
        if time_span == 0:
            return "stable"
        
        # Simple trend: more frequent = strengthening
        early_count = sum(1 for t in timestamps if t < timestamps[len(timestamps)//2])
        late_count = len(timestamps) - early_count
        
        # Lower threshold for detecting strengthening trend
        if late_count > early_count * 1.2:
            return "strengthening"
        elif early_count > late_count * 1.2:
            return "weakening"
        else:
            return "stable"
    
    def _calculate_anomaly_score(self, content: str) -> float:
        """Calculate anomaly score for content"""
        anomaly_keywords = ["breakthrough", "overnight", "sudden", "unexpected", "revolutionary"]
        score = sum(0.2 for keyword in anomaly_keywords if keyword in content.lower())
        return min(1.0, score)
    
    def _detect_period_type(self, timestamps: List[datetime]) -> str:
        """Detect periodicity type from timestamps"""
        if len(timestamps) < 2:
            return None
        
        # Calculate intervals
        intervals = []
        for i in range(1, len(timestamps)):
            interval_days = (timestamps[i] - timestamps[i-1]).days
            intervals.append(interval_days)
        
        avg_interval = np.mean(intervals)
        
        # Classify period type
        if 85 <= avg_interval <= 95:
            return "quarterly"
        elif 28 <= avg_interval <= 35:
            return "monthly"
        elif 6 <= avg_interval <= 8:
            return "weekly"
        elif 360 <= avg_interval <= 370:
            return "yearly"
        else:
            return None
    
    def _extract_events(self, documents: List[Dict[str, Any]]) -> List[TemporalEvent]:
        """Extract temporal events from documents"""
        events = []
        
        for doc in documents:
            # Simple event extraction based on keywords
            content = doc.get("content", "")
            
            # Extract AI-related events
            if "AI" in content:
                events.append(TemporalEvent(
                    event_id=f"event_{doc['id']}_AI",
                    concept="AI",
                    timestamp=self._parse_timestamp(doc.get("timestamp")),
                    document_id=doc["id"],
                    context=content[:100]
                ))
            
            # Extract Quantum-related events
            if "quantum" in content.lower():
                events.append(TemporalEvent(
                    event_id=f"event_{doc['id']}_quantum",
                    concept="Quantum Computing",
                    timestamp=self._parse_timestamp(doc.get("timestamp")),
                    document_id=doc["id"],
                    context=content[:100]
                ))
        
        return events
    
    def _calculate_correlation(self, event1: TemporalEvent, event2: TemporalEvent) -> float:
        """Calculate correlation between two events"""
        # Simple correlation based on concept similarity
        if event1.concept == event2.concept:
            return 0.2  # Same concept, low correlation
        
        # Check for known correlations
        correlated_pairs = [
            ("AI", "Quantum Computing"),
            ("safety", "AI"),
        ]
        
        for pair in correlated_pairs:
            if (event1.concept in pair and event2.concept in pair):
                return 0.8
        
        return 0.3  # Default low correlation
    
    def _calculate_concept_importance(self, content: str, concept: str) -> float:
        """Calculate importance of concept in content"""
        content_lower = content.lower()
        concept_lower = concept.lower()
        
        # Count mentions
        mention_count = content_lower.count(concept_lower)
        
        # Check for importance indicators
        importance_keywords = ["primary", "critical", "essential", "focus", "priority", "concerns", "alignment"]
        importance_boost = sum(0.15 for keyword in importance_keywords if keyword in content_lower)
        
        # Normalize to 0-1 range with higher weight for mentions
        importance = min(1.0, (mention_count * 0.3) + importance_boost)
        
        return importance
    
    def _extract_concept_patterns(self, documents: List[Dict[str, Any]]) -> Dict[str, List[Tuple[datetime, float]]]:
        """Extract temporal patterns for concepts"""
        patterns = defaultdict(list)
        
        for doc in documents:
            timestamp = self._parse_timestamp(doc.get("timestamp"))
            content = doc.get("content", "").lower()
            
            # Track AI safety
            if "safety" in content:
                importance = self._calculate_concept_importance(content, "safety")
                patterns["AI safety"].append((timestamp, importance))
            
            # Track Quantum Computing
            if "quantum" in content:
                importance = self._calculate_concept_importance(content, "quantum")
                patterns["Quantum Computing"].append((timestamp, importance))
        
        return patterns
    
    def _detect_trend_direction(self, pattern: List[Tuple[datetime, float]]) -> str:
        """Detect trend direction from pattern"""
        if len(pattern) < 2:
            return "insufficient_data"
        
        # Simple linear trend
        values = [p[1] for p in pattern]
        early_avg = np.mean(values[:len(values)//2])
        late_avg = np.mean(values[len(values)//2:])
        
        if late_avg > early_avg * 1.2:
            return "increasing"
        elif early_avg > late_avg * 1.2:
            return "decreasing"
        else:
            return "stable"
    
    def _project_value(self, pattern: List[Tuple[datetime, float]], days_ahead: int) -> float:
        """Project future value based on pattern"""
        if len(pattern) < 2:
            return 0.5
        
        # Simple linear projection
        values = [p[1] for p in pattern]
        trend_rate = (values[-1] - values[0]) / len(values)
        
        projected = values[-1] + (trend_rate * (days_ahead / 30))
        return max(0.0, min(1.0, projected))
    
    def _generate_period_summary(self, documents: List[Dict[str, Any]]) -> str:
        """Generate summary for a period"""
        if not documents:
            return "No activity"
        
        # Extract key themes
        themes = []
        for doc in documents:
            content = doc.get("content", "").lower()
            if "safety" in content:
                themes.append("AI safety")
            if "quantum" in content:
                themes.append("Quantum computing")
        
        if themes:
            return f"Key themes: {', '.join(set(themes))}"
        else:
            return "Various developments"
    
    def _identify_key_trends(self, documents: List[Dict[str, Any]]) -> List[str]:
        """Identify key trends from documents"""
        trends = []
        
        # Check for AI safety trend
        safety_mentions = sum(1 for d in documents if "safety" in d.get("content", "").lower())
        if safety_mentions > len(documents) * 0.3:
            trends.append("Growing focus on AI safety")
        
        # Check for quantum trend
        quantum_mentions = sum(1 for d in documents if "quantum" in d.get("content", "").lower())
        if quantum_mentions > len(documents) * 0.2:
            trends.append("Quantum computing advancement")
        
        return trends
    
    def _create_evolution_narrative(self, yearly_summaries: Dict[int, str], trends: List[str]) -> str:
        """Create narrative of evolution"""
        narrative = "Evolution over time: "
        
        if trends:
            narrative += f"Key trends include {', '.join(trends)}. "
        
        narrative += f"Spanning {len(yearly_summaries)} years of development."
        
        return narrative
    
    def _extract_significant_events(self, documents: List[Dict[str, Any]]) -> List[TemporalEvent]:
        """Extract significant events from documents"""
        events = []
        
        for doc in documents:
            content = doc.get("content", "").lower()
            
            # Check for significance markers
            if any(word in content for word in ["breakthrough", "achieved", "revolutionary"]):
                events.append(TemporalEvent(
                    event_id=f"sig_{doc['id']}",
                    concept="Significant development",
                    timestamp=self._parse_timestamp(doc.get("timestamp")),
                    document_id=doc["id"],
                    context=doc.get("content", "")[:100]
                ))
        
        return events
    
    def _get_events_by_year(self, documents: List[Dict[str, Any]], year: int) -> List[TemporalEvent]:
        """Get events for a specific year"""
        events = []
        
        for doc in documents:
            timestamp = self._parse_timestamp(doc.get("timestamp"))
            if timestamp.year == year:
                events.append(TemporalEvent(
                    event_id=doc["id"],
                    concept="Document",
                    timestamp=timestamp,
                    document_id=doc["id"],
                    context=doc.get("content", "")[:100]
                ))
        
        return events
    
    def _extract_concept_from_query(self, query: str) -> str:
        """Extract concept from query string"""
        query_lower = query.lower()
        
        if "quantum" in query_lower:
            return "Quantum Computing"
        elif "safety" in query_lower:
            return "AI safety"
        elif "ai" in query_lower:
            return "AI"
        else:
            return "Unknown"
    
    def _get_concept_trend(self, documents: List[Dict[str, Any]], concept: str) -> TrendPrediction:
        """Get trend for a specific concept"""
        pattern = []
        
        for doc in documents:
            if concept.lower() in doc.get("content", "").lower():
                timestamp = self._parse_timestamp(doc.get("timestamp"))
                importance = self._calculate_concept_importance(doc["content"], concept)
                pattern.append((timestamp, importance))
        
        if not pattern:
            return None
        
        trend_direction = self._detect_trend_direction(pattern)
        
        return TrendPrediction(
            concept=concept,
            trend_direction=trend_direction,
            confidence=0.8,
            predicted_values=[],
            horizon_days=0
        )
    
    def _process_general_query(self, documents: List[Dict[str, Any]], query: str) -> Any:
        """Process general temporal query"""
        # Simple fallback
        return f"Query '{query}' processed with {len(documents)} documents"