#!/usr/bin/env python3
"""
Citation Impact Analyzer - Analyze citation networks for research impact assessment

Implements comprehensive citation analysis including h-index, citation velocity,
cross-disciplinary impact, and temporal patterns with error handling.
"""

import asyncio
import time
import logging
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import statistics

from .graph_centrality_analyzer import AnalyticsError

logger = logging.getLogger(__name__)


class CitationImpactAnalyzer:
    """Analyze citation networks for research impact assessment"""
    
    def __init__(self, neo4j_manager, distributed_tx_manager):
        self.neo4j_manager = neo4j_manager
        self.dtm = distributed_tx_manager
        
        # Initialize real percentile ranker
        from .real_percentile_ranker import RealPercentileRanker
        self.percentile_ranker = RealPercentileRanker(neo4j_manager)
        
        # Impact metrics configuration
        self.impact_metrics = [
            'h_index',
            'citation_velocity',
            'cross_disciplinary_impact',
            'temporal_impact_pattern',
            'collaboration_network_centrality',
            'i10_index',
            'citation_half_life',
            'field_normalized_citation'
        ]
        
        # Time windows for analysis
        self.time_windows = {
            'recent': 2,      # 2 years
            'medium': 5,      # 5 years
            'long': 10,       # 10 years
            'career': None    # All time
        }
        
        logger.info("CitationImpactAnalyzer initialized")
    
    async def analyze_research_impact(self, entity_id: str, 
                                    entity_type: str,
                                    time_window_years: int = 10,
                                    include_self_citations: bool = False) -> Dict[str, Any]:
        """Comprehensive research impact analysis"""
        
        tx_id = f"impact_analysis_{entity_id}_{int(time.time())}"
        logger.info(f"Starting research impact analysis - entity: {entity_id}, type: {entity_type}, tx_id: {tx_id}")
        
        try:
            await self.dtm.begin_distributed_transaction(tx_id)
            
            # Gather citation network data
            citation_network = await self._build_citation_network(
                entity_id, entity_type, time_window_years, include_self_citations
            )
            
            if not citation_network or not citation_network.get('papers'):
                logger.warning(f"No citation data found for entity {entity_id}")
                await self.dtm.commit_distributed_transaction(tx_id)
                return {
                    'entity_id': entity_id,
                    'entity_type': entity_type,
                    'impact_scores': {metric: 0 for metric in self.impact_metrics},
                    'temporal_analysis': {},
                    'influence_analysis': {},
                    'composite_impact_score': 0,
                    'metadata': {
                        'time_window_years': time_window_years,
                        'total_papers': 0,
                        'total_citations': 0
                    }
                }
            
            # Calculate comprehensive impact metrics
            impact_scores = {}
            for metric in self.impact_metrics:
                score = await self._calculate_impact_metric(
                    metric, citation_network, entity_id
                )
                impact_scores[metric] = score
            
            # Analyze temporal impact evolution
            temporal_analysis = await self._analyze_temporal_impact(
                citation_network, time_window_years
            )
            
            # Identify key influential papers/collaborators
            influence_analysis = await self._analyze_influence_patterns(citation_network)
            
            # Generate impact report
            impact_report = await self._generate_impact_report(
                entity_id, entity_type, impact_scores, temporal_analysis, influence_analysis
            )
            
            # Store results
            await self._store_impact_analysis(tx_id, entity_id, impact_scores, temporal_analysis, influence_analysis)
            
            await self.dtm.commit_distributed_transaction(tx_id)
            
            result = {
                'entity_id': entity_id,
                'entity_type': entity_type,
                'impact_scores': impact_scores,
                'temporal_analysis': temporal_analysis,
                'influence_analysis': influence_analysis,
                'impact_report': impact_report,
                'composite_impact_score': await self._calculate_composite_score(impact_scores),
                'metadata': {
                    'time_window_years': time_window_years,
                    'total_papers': len(citation_network.get('papers', [])),
                    'total_citations': citation_network.get('total_citations', 0),
                    'analysis_timestamp': datetime.now().isoformat()
                }
            }
            
            logger.info(f"Research impact analysis completed for entity {entity_id}")
            return result
            
        except Exception as e:
            logger.error(f"Research impact analysis failed: {e}", exc_info=True)
            await self.dtm.rollback_distributed_transaction(tx_id)
            raise AnalyticsError(f"Research impact analysis failed: {e}")
    
    async def _build_citation_network(self, entity_id: str, entity_type: str,
                                    time_window_years: int,
                                    include_self_citations: bool) -> Dict[str, Any]:
        """Build citation network for the entity"""
        
        logger.info(f"Building citation network for {entity_type} {entity_id}")
        
        # Determine the appropriate query based on entity type
        if entity_type.lower() in ['author', 'researcher']:
            papers_query = """
            MATCH (author:Author {id: $entity_id})-[:AUTHORED]->(paper:Paper)
            WHERE paper.year >= $start_year OR $start_year IS NULL
            RETURN paper.id as paper_id, paper.title as title, 
                   paper.year as year, paper.field as field,
                   paper.abstract as abstract
            """
        elif entity_type.lower() in ['institution', 'organization']:
            papers_query = """
            MATCH (inst:Institution {id: $entity_id})-[:AFFILIATED]->(author:Author)-[:AUTHORED]->(paper:Paper)
            WHERE paper.year >= $start_year OR $start_year IS NULL
            RETURN DISTINCT paper.id as paper_id, paper.title as title,
                   paper.year as year, paper.field as field,
                   paper.abstract as abstract
            """
        elif entity_type.lower() in ['paper', 'publication']:
            papers_query = """
            MATCH (paper:Paper {id: $entity_id})
            RETURN paper.id as paper_id, paper.title as title,
                   paper.year as year, paper.field as field,
                   paper.abstract as abstract
            """
        else:
            # Generic entity query
            papers_query = """
            MATCH (entity {id: $entity_id})-[*1..2]-(paper:Paper)
            WHERE paper.year >= $start_year OR $start_year IS NULL
            RETURN DISTINCT paper.id as paper_id, paper.title as title,
                   paper.year as year, paper.field as field,
                   paper.abstract as abstract
            LIMIT 1000
            """
        
        # Calculate start year
        start_year = datetime.now().year - time_window_years if time_window_years else None
        
        params = {
            'entity_id': entity_id,
            'start_year': start_year
        }
        
        # Execute query for papers
        await self.dtm.add_operation(self.dtm.current_tx_id, 'read', 'neo4j', 'papers_data', {
            'query': papers_query,
            'params': params,
            'operation_type': 'citation_papers_fetch'
        })
        
        papers_data = await self.neo4j_manager.execute_read_query(papers_query, params)
        
        if not papers_data:
            return {'papers': [], 'citations': [], 'total_citations': 0}
        
        # Get citations for all papers
        paper_ids = [p['paper_id'] for p in papers_data]
        
        citations_query = """
        MATCH (citing_paper:Paper)-[:CITES]->(cited_paper:Paper)
        WHERE cited_paper.id IN $paper_ids
        """ + ("AND citing_paper.id NOT IN $paper_ids" if not include_self_citations else "") + """
        RETURN citing_paper.id as citing_id, cited_paper.id as cited_id,
               citing_paper.year as citing_year, citing_paper.field as citing_field,
               citing_paper.title as citing_title
        """
        
        citation_params = {'paper_ids': paper_ids}
        
        await self.dtm.add_operation(self.dtm.current_tx_id, 'read', 'neo4j', 'citations_data', {
            'query': citations_query,
            'params': citation_params,
            'operation_type': 'citation_network_fetch'
        })
        
        citations_data = await self.neo4j_manager.execute_read_query(citations_query, citation_params)
        
        # Build citation network structure
        papers = {}
        for paper in papers_data:
            papers[paper['paper_id']] = {
                'id': paper['paper_id'],
                'title': paper['title'],
                'year': paper['year'],
                'field': paper['field'],
                'abstract': paper['abstract'],
                'citations': [],
                'citation_count': 0
            }
        
        # Add citation information
        total_citations = 0
        for citation in citations_data:
            cited_id = citation['cited_id']
            if cited_id in papers:
                papers[cited_id]['citations'].append({
                    'citing_id': citation['citing_id'],
                    'citing_year': citation['citing_year'],
                    'citing_field': citation['citing_field'],
                    'citing_title': citation['citing_title']
                })
                papers[cited_id]['citation_count'] += 1
                total_citations += 1
        
        return {
            'papers': list(papers.values()),
            'citations': citations_data,
            'total_citations': total_citations,
            'paper_count': len(papers)
        }
    
    async def _calculate_impact_metric(self, metric: str, citation_network: Dict,
                                     entity_id: str) -> float:
        """Calculate specific impact metric"""
        
        papers = citation_network.get('papers', [])
        
        if metric == 'h_index':
            return await self._calculate_h_index(papers)
        elif metric == 'i10_index':
            return await self._calculate_i10_index(papers)
        elif metric == 'citation_velocity':
            return await self._calculate_citation_velocity(papers)
        elif metric == 'cross_disciplinary_impact':
            return await self._calculate_cross_disciplinary_impact(papers)
        elif metric == 'temporal_impact_pattern':
            return await self._calculate_temporal_impact_pattern(papers)
        elif metric == 'collaboration_network_centrality':
            return await self._calculate_collaboration_centrality(entity_id)
        elif metric == 'citation_half_life':
            return await self._calculate_citation_half_life(papers)
        elif metric == 'field_normalized_citation':
            return await self._calculate_field_normalized_citation(papers)
        else:
            logger.warning(f"Unknown impact metric: {metric}")
            return 0.0
    
    async def _calculate_h_index(self, papers: List[Dict]) -> int:
        """Calculate h-index: h papers with at least h citations each"""
        
        if not papers:
            return 0
        
        # Sort papers by citation count in descending order
        citation_counts = sorted([p['citation_count'] for p in papers], reverse=True)
        
        h_index = 0
        for i, citations in enumerate(citation_counts, 1):
            if citations >= i:
                h_index = i
            else:
                break
        
        return h_index
    
    async def _calculate_i10_index(self, papers: List[Dict]) -> int:
        """Calculate i10-index: number of papers with at least 10 citations"""
        
        return sum(1 for p in papers if p['citation_count'] >= 10)
    
    async def _calculate_citation_velocity(self, papers: List[Dict]) -> float:
        """Calculate citation velocity (citations per year in recent period)"""
        
        if not papers:
            return 0.0
        
        current_year = datetime.now().year
        recent_years = 3  # Look at last 3 years
        
        recent_citations = 0
        for paper in papers:
            for citation in paper.get('citations', []):
                citing_year = citation.get('citing_year')
                if citing_year and current_year - citing_year <= recent_years:
                    recent_citations += 1
        
        return recent_citations / recent_years
    
    async def _calculate_cross_disciplinary_impact(self, papers: List[Dict]) -> float:
        """Calculate impact across different research fields"""
        
        if not papers:
            return 0.0
        
        # Count citations from different fields
        field_citations = defaultdict(int)
        total_citations = 0
        
        for paper in papers:
            paper_field = paper.get('field', 'unknown')
            for citation in paper.get('citations', []):
                citing_field = citation.get('citing_field', 'unknown')
                if citing_field != paper_field:
                    field_citations[citing_field] += 1
                total_citations += 1
        
        if total_citations == 0:
            return 0.0
        
        # Calculate diversity index (Shannon entropy)
        cross_disciplinary_ratio = len(field_citations) / max(len(set(p.get('field') for p in papers)), 1)
        
        # Calculate entropy
        entropy = 0.0
        for field_count in field_citations.values():
            p = field_count / total_citations
            if p > 0:
                entropy -= p * np.log2(p)
        
        # Normalize by maximum possible entropy
        max_entropy = np.log2(len(field_citations)) if len(field_citations) > 0 else 1
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0
        
        return (cross_disciplinary_ratio + normalized_entropy) / 2
    
    async def _calculate_temporal_impact_pattern(self, papers: List[Dict]) -> float:
        """Calculate temporal pattern score (sustained vs. declining impact)"""
        
        if not papers:
            return 0.0
        
        current_year = datetime.now().year
        
        # Group citations by year
        citations_by_year = defaultdict(int)
        for paper in papers:
            for citation in paper.get('citations', []):
                citing_year = citation.get('citing_year')
                if citing_year:
                    citations_by_year[citing_year] += 1
        
        if not citations_by_year:
            return 0.0
        
        # Calculate trend over last 5 years
        recent_years = sorted([year for year in citations_by_year.keys() 
                             if current_year - year <= 5])
        
        if len(recent_years) < 2:
            return 0.5  # Neutral if insufficient data
        
        # Calculate linear regression slope
        x = np.array(range(len(recent_years)))
        y = np.array([citations_by_year[year] for year in recent_years])
        
        if len(x) > 1:
            slope = np.polyfit(x, y, 1)[0]
            # Normalize slope to 0-1 range
            normalized_slope = (np.tanh(slope / 10) + 1) / 2
            return normalized_slope
        
        return 0.5
    
    async def _calculate_collaboration_centrality(self, entity_id: str) -> float:
        """Calculate centrality in collaboration network using advanced network analysis"""
        
        # Use real network centrality calculation
        return await self.percentile_ranker.calculate_collaboration_network_centrality(entity_id)
    
    async def _calculate_citation_half_life(self, papers: List[Dict]) -> float:
        """Calculate citation half-life (years for citations to drop by half)"""
        
        if not papers:
            return 0.0
        
        current_year = datetime.now().year
        
        # Group citations by years since publication
        citations_by_age = defaultdict(int)
        
        for paper in papers:
            paper_year = paper.get('year')
            if not paper_year:
                continue
                
            for citation in paper.get('citations', []):
                citing_year = citation.get('citing_year')
                if citing_year:
                    age = citing_year - paper_year
                    if age >= 0:
                        citations_by_age[age] += 1
        
        if not citations_by_age:
            return 0.0
        
        # Find half-life
        total_citations = sum(citations_by_age.values())
        half_citations = total_citations / 2
        
        cumulative = 0
        for age in sorted(citations_by_age.keys()):
            cumulative += citations_by_age[age]
            if cumulative >= half_citations:
                return float(age)
        
        # If we haven't reached half, estimate based on trend
        max_age = max(citations_by_age.keys())
        return float(max_age * 2)  # Rough estimate
    
    async def _calculate_field_normalized_citation(self, papers: List[Dict]) -> float:
        """Calculate field-normalized citation impact"""
        
        if not papers:
            return 0.0
        
        # Group papers by field
        field_groups = defaultdict(list)
        for paper in papers:
            field = paper.get('field', 'unknown')
            field_groups[field].append(paper['citation_count'])
        
        # Calculate normalized scores
        normalized_scores = []
        
        for field, citation_counts in field_groups.items():
            if citation_counts:
                # Simple normalization by field average
                field_avg = np.mean(citation_counts)
                field_std = np.std(citation_counts)
                
                for count in citation_counts:
                    if field_std > 0:
                        z_score = (count - field_avg) / field_std
                        normalized_score = (np.tanh(z_score / 2) + 1) / 2
                    else:
                        normalized_score = 0.5
                    
                    normalized_scores.append(normalized_score)
        
        return np.mean(normalized_scores) if normalized_scores else 0.0
    
    async def _analyze_temporal_impact(self, citation_network: Dict,
                                     time_window_years: int) -> Dict[str, Any]:
        """Analyze temporal evolution of research impact"""
        
        papers = citation_network.get('papers', [])
        current_year = datetime.now().year
        
        # Analyze citation patterns over time
        yearly_citations = defaultdict(int)
        yearly_papers = defaultdict(int)
        
        for paper in papers:
            paper_year = paper.get('year')
            if paper_year:
                yearly_papers[paper_year] += 1
            
            for citation in paper.get('citations', []):
                citing_year = citation.get('citing_year')
                if citing_year:
                    yearly_citations[citing_year] += 1
        
        # Calculate metrics for different time windows
        temporal_metrics = {}
        
        for window_name, window_years in self.time_windows.items():
            if window_years is None or window_years <= time_window_years:
                start_year = current_year - window_years if window_years else min(yearly_citations.keys(), default=current_year)
                
                window_citations = sum(count for year, count in yearly_citations.items() 
                                     if year >= start_year)
                window_papers = sum(count for year, count in yearly_papers.items() 
                                  if year >= start_year)
                
                temporal_metrics[window_name] = {
                    'total_citations': window_citations,
                    'total_papers': window_papers,
                    'citations_per_paper': window_citations / window_papers if window_papers > 0 else 0,
                    'years_included': window_years or (current_year - start_year + 1)
                }
        
        # Identify peak impact years
        peak_years = sorted(yearly_citations.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'yearly_citations': dict(yearly_citations),
            'yearly_papers': dict(yearly_papers),
            'temporal_metrics': temporal_metrics,
            'peak_impact_years': peak_years,
            'citation_trend': await self._calculate_citation_trend(yearly_citations)
        }
    
    async def _calculate_citation_trend(self, yearly_citations: Dict[int, int]) -> str:
        """Calculate overall citation trend (increasing, stable, declining)"""
        
        if len(yearly_citations) < 3:
            return 'insufficient_data'
        
        # Get last 5 years of data
        recent_years = sorted(yearly_citations.keys())[-5:]
        recent_counts = [yearly_citations[year] for year in recent_years]
        
        if len(recent_counts) < 2:
            return 'insufficient_data'
        
        # Calculate linear regression
        x = np.arange(len(recent_counts))
        slope = np.polyfit(x, recent_counts, 1)[0]
        
        # Determine trend based on slope
        avg_citations = np.mean(recent_counts)
        slope_ratio = slope / avg_citations if avg_citations > 0 else 0
        
        if slope_ratio > 0.1:
            return 'increasing'
        elif slope_ratio < -0.1:
            return 'declining'
        else:
            return 'stable'
    
    async def _analyze_influence_patterns(self, citation_network: Dict) -> Dict[str, Any]:
        """Analyze patterns of research influence"""
        
        papers = citation_network.get('papers', [])
        
        # Find most cited papers
        top_papers = sorted(papers, key=lambda p: p['citation_count'], reverse=True)[:10]
        
        # Analyze citing fields
        citing_fields = Counter()
        citing_years = Counter()
        
        for paper in papers:
            for citation in paper.get('citations', []):
                field = citation.get('citing_field')
                year = citation.get('citing_year')
                
                if field:
                    citing_fields[field] += 1
                if year:
                    citing_years[year] += 1
        
        # Identify breakthrough papers (sudden citation increase)
        breakthrough_papers = []
        for paper in papers:
            if paper['citation_count'] > 20:  # Minimum threshold
                citations_by_year = defaultdict(int)
                for citation in paper.get('citations', []):
                    year = citation.get('citing_year')
                    if year:
                        citations_by_year[year] += 1
                
                # Check for sudden increase
                if citations_by_year:
                    years = sorted(citations_by_year.keys())
                    for i in range(1, len(years)):
                        prev_citations = citations_by_year[years[i-1]]
                        curr_citations = citations_by_year[years[i]]
                        
                        if prev_citations > 0 and curr_citations / prev_citations > 3:
                            breakthrough_papers.append({
                                'paper_id': paper['id'],
                                'title': paper['title'],
                                'breakthrough_year': years[i],
                                'citation_increase': curr_citations / prev_citations
                            })
                            break
        
        return {
            'top_cited_papers': [
                {
                    'id': p['id'],
                    'title': p['title'],
                    'citations': p['citation_count'],
                    'year': p['year']
                }
                for p in top_papers
            ],
            'citing_field_distribution': dict(citing_fields.most_common(10)),
            'temporal_citation_distribution': dict(citing_years),
            'breakthrough_papers': breakthrough_papers[:5],
            'interdisciplinary_reach': len(citing_fields)
        }
    
    async def _generate_impact_report(self, entity_id: str, entity_type: str,
                                    impact_scores: Dict[str, float],
                                    temporal_analysis: Dict[str, Any],
                                    influence_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive impact report"""
        
        # Calculate percentile rankings (mock implementation)
        percentile_rankings = {
            'h_index': await self._calculate_percentile_rank(impact_scores['h_index'], 'h_index'),
            'citation_velocity': await self._calculate_percentile_rank(impact_scores['citation_velocity'], 'citation_velocity'),
            'cross_disciplinary_impact': await self._calculate_percentile_rank(impact_scores['cross_disciplinary_impact'], 'cross_disciplinary_impact')
        }
        
        # Generate summary
        summary = {
            'entity_id': entity_id,
            'entity_type': entity_type,
            'overall_impact': 'high' if impact_scores['h_index'] > 20 else 'medium' if impact_scores['h_index'] > 10 else 'emerging',
            'key_strengths': [],
            'growth_areas': [],
            'recommendations': []
        }
        
        # Identify strengths
        if impact_scores['h_index'] > 15:
            summary['key_strengths'].append('Strong publication impact with high h-index')
        if impact_scores['citation_velocity'] > 50:
            summary['key_strengths'].append('High recent citation velocity indicates growing influence')
        if impact_scores['cross_disciplinary_impact'] > 0.7:
            summary['key_strengths'].append('Significant cross-disciplinary research impact')
        
        # Identify growth areas
        if impact_scores['collaboration_network_centrality'] < 0.3:
            summary['growth_areas'].append('Expand collaboration network')
        if temporal_analysis.get('citation_trend') == 'declining':
            summary['growth_areas'].append('Revitalize research impact through new directions')
        
        # Generate recommendations
        if impact_scores['citation_velocity'] < 20:
            summary['recommendations'].append('Increase research visibility through conferences and social media')
        if impact_scores['cross_disciplinary_impact'] < 0.5:
            summary['recommendations'].append('Explore interdisciplinary collaboration opportunities')
        
        return {
            'summary': summary,
            'percentile_rankings': percentile_rankings,
            'impact_trajectory': temporal_analysis.get('citation_trend', 'unknown'),
            'breakthrough_potential': len(influence_analysis.get('breakthrough_papers', [])) > 0
        }
    
    async def _calculate_percentile_rank(self, score: float, metric: str) -> float:
        """Calculate percentile rank for a given metric using real statistical analysis"""
        return await self.percentile_ranker.calculate_percentile_rank(score, metric)
    
    async def _calculate_composite_score(self, impact_scores: Dict[str, float]) -> float:
        """Calculate composite impact score from individual metrics"""
        
        # Weight different metrics
        weights = {
            'h_index': 0.25,
            'citation_velocity': 0.20,
            'cross_disciplinary_impact': 0.15,
            'temporal_impact_pattern': 0.10,
            'collaboration_network_centrality': 0.10,
            'i10_index': 0.10,
            'field_normalized_citation': 0.10
        }
        
        # Normalize h_index and i10_index to 0-1 scale
        normalized_scores = {}
        normalized_scores['h_index'] = min(impact_scores.get('h_index', 0) / 50, 1.0)
        normalized_scores['i10_index'] = min(impact_scores.get('i10_index', 0) / 100, 1.0)
        normalized_scores['citation_velocity'] = min(impact_scores.get('citation_velocity', 0) / 100, 1.0)
        
        # Other scores already in 0-1 range
        for metric in ['cross_disciplinary_impact', 'temporal_impact_pattern', 
                      'collaboration_network_centrality', 'field_normalized_citation']:
            normalized_scores[metric] = impact_scores.get(metric, 0)
        
        # Calculate weighted composite
        composite = sum(normalized_scores.get(metric, 0) * weight 
                       for metric, weight in weights.items())
        
        return round(composite, 3)
    
    async def _store_impact_analysis(self, tx_id: str, entity_id: str,
                                   impact_scores: Dict[str, float],
                                   temporal_analysis: Dict[str, Any],
                                   influence_analysis: Dict[str, Any]) -> None:
        """Store impact analysis results with provenance"""
        
        await self.dtm.add_operation(tx_id, 'write', 'neo4j', 'impact_analysis', {
            'entity_id': entity_id,
            'impact_scores': impact_scores,
            'temporal_analysis': temporal_analysis,
            'influence_analysis': influence_analysis,
            'operation_type': 'impact_analysis_storage',
            'timestamp': datetime.now().isoformat()
        })
        
        logger.info(f"Impact analysis results prepared for storage - entity {entity_id}")