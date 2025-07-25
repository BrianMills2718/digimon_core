"""Temporal Graph Analyzer

Coordinator for temporal analysis using decomposed components.
"""

from typing import Dict, List, Any
from .temporal_data_models import TemporalSnapshot
from .evolution_analyzer import EvolutionAnalyzer
from .centrality_analyzer import CentralityAnalyzer
from src.core.logging_config import get_logger

logger = get_logger(__name__)


class TemporalAnalyzer:
    """Coordinates temporal analysis using decomposed components"""
    
    def __init__(self):
        self.evolution_analyzer = EvolutionAnalyzer()
        self.centrality_analyzer = CentralityAnalyzer()
        self.analysis_cache = {}
    
    def analyze_evolution(self, snapshots: List[TemporalSnapshot], 
                         analysis_params: Dict[str, Any]) -> Dict[str, Any]:
        """Delegate evolution analysis to specialized component"""
        return self.evolution_analyzer.analyze_evolution(snapshots, analysis_params)
    
    def detect_changes(self, snapshots: List[TemporalSnapshot], 
                      analysis_params: Dict[str, Any]) -> Dict[str, Any]:
        """Delegate change detection to evolution analyzer"""
        return self.evolution_analyzer.detect_changes(snapshots, analysis_params)
    
    def analyze_trends(self, snapshots: List[TemporalSnapshot], 
                      analysis_params: Dict[str, Any]) -> Dict[str, Any]:
        """Delegate trend analysis to evolution analyzer"""
        return self.evolution_analyzer.analyze_trends(snapshots, analysis_params)
    
    def analyze_dynamic_centrality(self, snapshots: List[TemporalSnapshot]) -> Dict[str, Any]:
        """Delegate centrality analysis to specialized component"""
        return self.centrality_analyzer.analyze_dynamic_centrality(snapshots)
    
    def analyze_temporal_paths(self, snapshots: List[TemporalSnapshot]) -> Dict[str, Any]:
        """Delegate path analysis to centrality analyzer"""
        return self.centrality_analyzer.analyze_temporal_paths(snapshots)
    
    def analyze_community_evolution(self, snapshots: List[TemporalSnapshot]) -> Dict[str, Any]:
        """Delegate community analysis to centrality analyzer"""
        return self.centrality_analyzer.analyze_community_evolution(snapshots)