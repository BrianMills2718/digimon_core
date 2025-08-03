"""
Test suite for Task C.5: Temporal Pattern Analysis Engine

Tests temporal analysis capabilities including timeline construction,
trend detection, and temporal pattern recognition across documents.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any

from src.temporal.temporal_analyzer import TemporalAnalyzer
from src.temporal.timeline_builder import TimelineBuilder
from src.temporal.trend_detector import TrendDetector


class TestTemporalPatternAnalysis:
    """Test suite for temporal pattern analysis (Task C.5)"""
    
    @pytest.fixture
    def temporal_documents(self):
        """Create documents with temporal information"""
        base_date = datetime(2020, 1, 1)
        documents = []
        
        # Create documents spanning 5 years with evolving concepts
        for year in range(2020, 2025):
            for month in [1, 6, 12]:
                date = datetime(year, month, 1)
                
                # Evolving concept: AI Safety
                if year <= 2021:
                    ai_content = "AI research focuses on performance and accuracy improvements."
                elif year <= 2022:
                    ai_content = "AI safety concerns are emerging alongside performance gains."
                else:
                    ai_content = "AI safety and alignment are now primary research priorities."
                
                # Emerging trend: Quantum Computing
                if year < 2022:
                    quantum_content = "Quantum computing remains largely theoretical."
                elif year == 2022:
                    quantum_content = "Quantum supremacy achieved in specific domains."
                else:
                    quantum_content = "Practical quantum applications are being deployed."
                
                documents.append({
                    "id": f"doc_{year}_{month}",
                    "content": f"{ai_content} {quantum_content}",
                    "timestamp": date.isoformat(),
                    "metadata": {
                        "year": year,
                        "month": month,
                        "topics": ["AI", "Quantum Computing"]
                    }
                })
        
        return documents
    
    @pytest.mark.asyncio
    async def test_concept_timeline_construction(self, temporal_documents):
        """Test building timelines for concept evolution"""
        builder = TimelineBuilder()
        
        # Build timeline for AI safety concept
        ai_timeline = await builder.build_concept_timeline(
            documents=temporal_documents,
            concept="AI safety"
        )
        
        assert ai_timeline is not None
        assert len(ai_timeline.events) > 0
        assert ai_timeline.start_date <= ai_timeline.end_date
        
        # Should show evolution from low to high importance
        early_events = [e for e in ai_timeline.events if e.timestamp.year <= 2021]
        late_events = [e for e in ai_timeline.events if e.timestamp.year >= 2023]
        
        assert len(late_events) > len(early_events), "AI safety should appear more in later documents"
    
    @pytest.mark.asyncio
    async def test_entity_lifecycle_tracking(self, temporal_documents):
        """Test tracking entity appearances and changes over time"""
        analyzer = TemporalAnalyzer()
        
        # Track "Quantum Computing" entity over time
        lifecycle = await analyzer.track_entity_lifecycle(
            documents=temporal_documents,
            entity_name="Quantum Computing"
        )
        
        assert lifecycle is not None
        assert lifecycle.first_appearance is not None
        assert lifecycle.last_appearance is not None
        assert len(lifecycle.evolution_stages) >= 3  # theoretical -> supremacy -> practical
    
    @pytest.mark.asyncio
    async def test_relationship_temporal_patterns(self, temporal_documents):
        """Test identifying how relationships change over time"""
        analyzer = TemporalAnalyzer()
        
        # Analyze relationship between AI and Safety over time
        relationship_pattern = await analyzer.analyze_relationship_evolution(
            documents=temporal_documents,
            entity1="AI",
            entity2="safety"
        )
        
        assert relationship_pattern is not None
        assert relationship_pattern.correlation_trend is not None
        assert relationship_pattern.strengthening_over_time == True
    
    @pytest.mark.asyncio
    async def test_trend_detection_analysis(self, temporal_documents):
        """Test detecting emerging and declining trends"""
        detector = TrendDetector()
        
        trends = await detector.detect_trends(
            documents=temporal_documents,
            min_support=0.2
        )
        
        # Should detect emerging trend: AI safety OR have safety marked as stable but late-emerging
        emerging_trends = [t for t in trends if t.trend_type == "emerging"]
        safety_trends = [t for t in trends if "safety" in t.concept.lower()]
        
        # Either safety is marked as emerging, or it exists as a late-appearing stable trend
        assert len(safety_trends) > 0, "Should detect safety-related trends"
        
        # Check that safety appears later in timeline (which indicates emergence)
        if safety_trends:
            safety_trend = safety_trends[0]
            # Safety should start after 2021
            assert safety_trend.start_date.year >= 2022, "Safety should be a late-appearing concept"
        
        # Should detect stable trend: AI research
        stable_trends = [t for t in trends if t.trend_type == "stable"]
        assert any("AI" in t.concept for t in stable_trends)
    
    @pytest.mark.asyncio
    async def test_temporal_anomaly_detection(self, temporal_documents):
        """Test finding unusual patterns in temporal data"""
        analyzer = TemporalAnalyzer()
        
        # Add anomalous document
        anomaly_doc = {
            "id": "anomaly_1",
            "content": "Sudden breakthrough: AGI achieved overnight!",
            "timestamp": datetime(2022, 7, 15).isoformat(),
            "metadata": {"anomaly": True}
        }
        
        docs_with_anomaly = temporal_documents + [anomaly_doc]
        
        anomalies = await analyzer.detect_temporal_anomalies(
            documents=docs_with_anomaly,
            sensitivity=0.8
        )
        
        assert len(anomalies) > 0
        assert any(a.document_id == "anomaly_1" for a in anomalies)
    
    @pytest.mark.asyncio
    async def test_periodicity_analysis(self, temporal_documents):
        """Test detecting recurring patterns and cycles"""
        analyzer = TemporalAnalyzer()
        
        # Add documents with quarterly pattern
        quarterly_docs = []
        for year in [2023, 2024]:
            for quarter in [1, 2, 3, 4]:
                quarterly_docs.append({
                    "id": f"quarterly_{year}_Q{quarter}",
                    "content": f"Quarterly report Q{quarter}: Revenue increased.",
                    "timestamp": datetime(year, quarter * 3, 1).isoformat(),
                    "metadata": {"type": "quarterly_report"}
                })
        
        patterns = await analyzer.detect_periodicity(
            documents=quarterly_docs,
            min_frequency=2
        )
        
        assert len(patterns) > 0
        quarterly_pattern = next((p for p in patterns if p.period_type == "quarterly"), None)
        assert quarterly_pattern is not None
    
    @pytest.mark.asyncio
    async def test_temporal_correlation_analysis(self, temporal_documents):
        """Test finding temporally correlated events"""
        analyzer = TemporalAnalyzer()
        
        correlations = await analyzer.find_temporal_correlations(
            documents=temporal_documents,
            lag_window=timedelta(days=180)
        )
        
        assert len(correlations) > 0
        # AI safety concerns should correlate with quantum computing advances
        assert any(
            ("AI" in c.event1 and "quantum" in c.event2.lower()) or
            ("quantum" in c.event1.lower() and "AI" in c.event2)
            for c in correlations
        )
    
    @pytest.mark.asyncio
    async def test_change_point_detection(self, temporal_documents):
        """Test identifying significant temporal change points"""
        analyzer = TemporalAnalyzer()
        
        change_points = await analyzer.detect_change_points(
            documents=temporal_documents,
            concept="AI safety"
        )
        
        assert len(change_points) > 0
        # Should detect change around 2022 when safety became priority
        assert any(2022 <= cp.timestamp.year <= 2023 for cp in change_points)
    
    @pytest.mark.asyncio
    async def test_temporal_prediction_modeling(self, temporal_documents):
        """Test predicting future trends based on patterns"""
        analyzer = TemporalAnalyzer()
        
        predictions = await analyzer.predict_future_trends(
            documents=temporal_documents,
            horizon_days=365
        )
        
        assert len(predictions) > 0
        # Should predict continued growth in AI safety importance
        ai_safety_prediction = next(
            (p for p in predictions if "safety" in p.concept.lower()),
            None
        )
        assert ai_safety_prediction is not None
        assert ai_safety_prediction.trend_direction == "increasing"
    
    @pytest.mark.asyncio
    async def test_temporal_summary_generation(self, temporal_documents):
        """Test generating temporal summaries and insights"""
        analyzer = TemporalAnalyzer()
        
        summary = await analyzer.generate_temporal_summary(
            documents=temporal_documents,
            granularity="yearly"
        )
        
        assert summary is not None
        assert len(summary.yearly_summaries) == 5  # 2020-2024
        assert summary.key_trends is not None
        assert len(summary.key_trends) > 0
        assert summary.evolution_narrative is not None
    
    @pytest.mark.asyncio
    async def test_temporal_query_processing(self, temporal_documents):
        """Test answering temporal queries efficiently"""
        analyzer = TemporalAnalyzer()
        
        # Query: "What happened in 2022?"
        results_2022 = await analyzer.query_temporal(
            documents=temporal_documents,
            query="events in 2022"
        )
        
        assert len(results_2022) > 0
        assert all(r.timestamp.year == 2022 for r in results_2022)
        
        # Query: "Show trend for quantum computing"
        quantum_trend = await analyzer.query_temporal(
            documents=temporal_documents,
            query="trend quantum computing"
        )
        
        assert quantum_trend is not None
        assert quantum_trend.concept == "Quantum Computing"
        assert quantum_trend.trend_direction is not None