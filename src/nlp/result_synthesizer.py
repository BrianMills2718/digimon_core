"""
Result Synthesizer

Synthesizes complex multi-tool results into coherent, comprehensive responses.
Handles result integration, conflict resolution, and narrative construction.
"""

import logging
from typing import Dict, List, Set, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import statistics
import re
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)


class SynthesisStrategy(Enum):
    """Strategies for result synthesis"""
    COMPREHENSIVE = "comprehensive"     # Include all available information
    FOCUSED = "focused"                # Focus on primary question intent
    COMPARATIVE = "comparative"         # Emphasize comparisons and contrasts
    NARRATIVE = "narrative"            # Construct narrative flow
    ANALYTICAL = "analytical"          # Provide analytical insights
    SUMMARY = "summary"                # Provide concise summary


class ConflictResolution(Enum):
    """Methods for resolving conflicts between tool results"""
    CONFIDENCE_WEIGHTED = "confidence_weighted"  # Weight by confidence scores
    MAJORITY_RULE = "majority_rule"             # Use most common result
    SOURCE_PRIORITY = "source_priority"         # Prioritize certain tools
    CONSENSUS_ONLY = "consensus_only"           # Only include consensus items
    ALL_PERSPECTIVES = "all_perspectives"       # Include all conflicting views


@dataclass
class SynthesisFragment:
    """Individual fragment of synthesized content"""
    content: str
    source_tools: List[str]
    confidence: float
    fragment_type: str  # 'entity', 'relationship', 'theme', 'summary', etc.
    supporting_evidence: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SynthesisResult:
    """Complete synthesis result"""
    primary_response: str
    supporting_fragments: List[SynthesisFragment]
    overall_confidence: float
    synthesis_strategy: SynthesisStrategy
    source_tool_coverage: Dict[str, float]  # Tool contribution percentages
    quality_metrics: Dict[str, float]
    metadata: Dict[str, Any] = field(default_factory=dict)
    alternative_perspectives: List[str] = field(default_factory=list)
    caveats: List[str] = field(default_factory=list)


class ResultSynthesizer:
    """Synthesizes complex multi-tool results into coherent responses"""
    
    def __init__(self):
        """Initialize result synthesizer"""
        self.logger = logger
        
        # Synthesis templates and patterns
        self.synthesis_templates = self._initialize_synthesis_templates()
        
        # Tool priorities for conflict resolution
        self.tool_priorities = {
            'T68_PAGE_RANK': 0.9,         # High priority for centrality analysis
            'T49_MULTI_HOP_QUERY': 0.9,   # High priority for query results
            'T23A_SPACY_NER': 0.8,        # High priority for entity extraction
            'T27_RELATIONSHIP_EXTRACTOR': 0.8,  # High priority for relationships
            'T31_ENTITY_BUILDER': 0.7,    # Medium priority for entity building
            'T34_EDGE_BUILDER': 0.7,      # Medium priority for edge building
            'T15A_TEXT_CHUNKER': 0.6,     # Lower priority for text processing
            'T01_PDF_LOADER': 0.5,        # Lowest priority for basic loading
            'T85_TWITTER_EXPLORER': 0.8   # High priority for social analysis
        }
        
        # Conflict resolution preferences
        self.default_conflict_resolution = ConflictResolution.CONFIDENCE_WEIGHTED
        
        self.logger.info("Initialized result synthesizer with multi-tool integration")
    
    async def synthesize_results(self, execution_results: Dict[str, Any],
                               question: str,
                               strategy: SynthesisStrategy = SynthesisStrategy.COMPREHENSIVE,
                               conflict_resolution: ConflictResolution = None) -> SynthesisResult:
        """Synthesize results from multiple tool executions"""
        
        self.logger.info(f"Synthesizing results from {len(execution_results)} sources using {strategy.value} strategy")
        
        if conflict_resolution is None:
            conflict_resolution = self.default_conflict_resolution
        
        # Extract and organize tool results
        organized_results = self._organize_tool_results(execution_results)
        
        # Resolve conflicts between tool outputs
        resolved_results = await self._resolve_conflicts(organized_results, conflict_resolution)
        
        # Create synthesis fragments
        fragments = await self._create_synthesis_fragments(resolved_results, question)
        
        # Synthesize primary response
        primary_response = await self._synthesize_primary_response(
            fragments, question, strategy
        )
        
        # Calculate quality metrics
        quality_metrics = self._calculate_synthesis_quality(fragments, organized_results)
        
        # Calculate tool coverage
        tool_coverage = self._calculate_tool_coverage(fragments, organized_results)
        
        # Generate alternative perspectives
        alternatives = await self._generate_alternative_perspectives(
            fragments, organized_results, conflict_resolution
        )
        
        # Generate caveats and limitations
        caveats = self._generate_caveats(fragments, organized_results)
        
        synthesis_result = SynthesisResult(
            primary_response=primary_response,
            supporting_fragments=fragments,
            overall_confidence=quality_metrics.get('overall_confidence', 0.8),
            synthesis_strategy=strategy,
            source_tool_coverage=tool_coverage,
            quality_metrics=quality_metrics,
            alternative_perspectives=alternatives,
            caveats=caveats
        )
        
        self.logger.info(f"Synthesis complete: {len(fragments)} fragments, "
                        f"{quality_metrics.get('overall_confidence', 0):.2f} confidence")
        
        return synthesis_result
    
    def _organize_tool_results(self, execution_results: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Organize tool results by content type"""
        
        organized = {
            'entities': [],
            'relationships': [],
            'themes': [],
            'summaries': [],
            'metrics': [],
            'raw_outputs': []
        }
        
        for step_id, step_result in execution_results.items():
            if step_id.startswith('_'):  # Skip meta information
                continue
                
            if not isinstance(step_result, dict) or 'outputs' not in step_result:
                continue
            
            step_outputs = step_result['outputs']
            
            for tool_id, tool_output in step_outputs.items():
                if not isinstance(tool_output, dict):
                    continue
                
                # Extract different types of content
                self._categorize_tool_output(tool_id, tool_output, organized)
        
        return organized
    
    def _categorize_tool_output(self, tool_id: str, tool_output: Dict[str, Any],
                              organized: Dict[str, List[Dict[str, Any]]]) -> None:
        """Categorize tool output by content type"""
        
        # Add source information
        tool_output = tool_output.copy()
        tool_output['source_tool'] = tool_id
        
        # Categorize based on tool type and output content
        if 'T23A_SPACY_NER' in tool_id or 'entities' in str(tool_output).lower():
            organized['entities'].append(tool_output)
        
        elif 'T27_RELATIONSHIP_EXTRACTOR' in tool_id or 'relationships' in str(tool_output).lower():
            organized['relationships'].append(tool_output)
        
        elif 'T68_PAGE_RANK' in tool_id or 'centrality' in str(tool_output).lower():
            organized['metrics'].append(tool_output)
        
        elif 'T49_MULTI_HOP_QUERY' in tool_id or 'query' in str(tool_output).lower():
            organized['summaries'].append(tool_output)
        
        elif 'summary' in str(tool_output).lower() or 'theme' in str(tool_output).lower():
            organized['themes'].append(tool_output)
        
        else:
            organized['raw_outputs'].append(tool_output)
    
    async def _resolve_conflicts(self, organized_results: Dict[str, List[Dict[str, Any]]],
                               resolution_method: ConflictResolution) -> Dict[str, List[Dict[str, Any]]]:
        """Resolve conflicts between tool outputs"""
        
        resolved = {}
        
        for content_type, results in organized_results.items():
            if len(results) <= 1:
                resolved[content_type] = results
                continue
            
            if resolution_method == ConflictResolution.CONFIDENCE_WEIGHTED:
                resolved[content_type] = self._resolve_by_confidence(results)
                
            elif resolution_method == ConflictResolution.MAJORITY_RULE:
                resolved[content_type] = self._resolve_by_majority(results)
                
            elif resolution_method == ConflictResolution.SOURCE_PRIORITY:
                resolved[content_type] = self._resolve_by_priority(results)
                
            elif resolution_method == ConflictResolution.CONSENSUS_ONLY:
                resolved[content_type] = self._resolve_by_consensus(results)
                
            else:  # ALL_PERSPECTIVES
                resolved[content_type] = results  # Keep all perspectives
        
        return resolved
    
    def _resolve_by_confidence(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Resolve conflicts by weighting by confidence scores"""
        
        if not results:
            return []
        
        # Extract confidence scores
        scored_results = []
        for result in results:
            confidence = self._extract_confidence(result)
            scored_results.append((confidence, result))
        
        # Sort by confidence (highest first)
        scored_results.sort(key=lambda x: x[0], reverse=True)
        
        # Take top results or all if confidence is similar
        threshold = scored_results[0][0] * 0.8  # Within 80% of top confidence
        
        return [result for confidence, result in scored_results if confidence >= threshold]
    
    def _resolve_by_majority(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Resolve conflicts by majority rule"""
        
        # Group similar results
        grouped = defaultdict(list)
        
        for result in results:
            # Create a simplified key for grouping
            key = self._create_grouping_key(result)
            grouped[key].append(result)
        
        # Find majority group
        majority_group = max(grouped.values(), key=len)
        
        return majority_group
    
    def _resolve_by_priority(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Resolve conflicts by tool priority"""
        
        # Sort by tool priority
        def get_priority(result):
            tool_id = result.get('source_tool', '')
            return self.tool_priorities.get(tool_id, 0.5)
        
        sorted_results = sorted(results, key=get_priority, reverse=True)
        
        # Take highest priority results
        top_priority = get_priority(sorted_results[0])
        threshold = top_priority * 0.9
        
        return [result for result in sorted_results if get_priority(result) >= threshold]
    
    def _resolve_by_consensus(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Only include results that have consensus"""
        
        if len(results) < 2:
            return results
        
        # Find common elements
        consensus_results = []
        
        # Simple consensus: results that appear in multiple tools
        content_counts = Counter()
        
        for result in results:
            key = self._create_grouping_key(result)
            content_counts[key] += 1
        
        # Only include items with consensus (appearing > 1 time)
        consensus_keys = {key for key, count in content_counts.items() if count > 1}
        
        for result in results:
            key = self._create_grouping_key(result)
            if key in consensus_keys:
                consensus_results.append(result)
        
        return consensus_results
    
    async def _create_synthesis_fragments(self, resolved_results: Dict[str, List[Dict[str, Any]]],
                                        question: str) -> List[SynthesisFragment]:
        """Create synthesis fragments from resolved results"""
        
        fragments = []
        
        # Create entity fragments
        if resolved_results.get('entities'):
            entity_fragments = await self._create_entity_fragments(resolved_results['entities'])
            fragments.extend(entity_fragments)
        
        # Create relationship fragments
        if resolved_results.get('relationships'):
            relationship_fragments = await self._create_relationship_fragments(resolved_results['relationships'])
            fragments.extend(relationship_fragments)
        
        # Create theme fragments
        if resolved_results.get('themes'):
            theme_fragments = await self._create_theme_fragments(resolved_results['themes'])
            fragments.extend(theme_fragments)
        
        # Create metric fragments
        if resolved_results.get('metrics'):
            metric_fragments = await self._create_metric_fragments(resolved_results['metrics'])
            fragments.extend(metric_fragments)
        
        # Create summary fragments
        if resolved_results.get('summaries'):
            summary_fragments = await self._create_summary_fragments(resolved_results['summaries'], question)
            fragments.extend(summary_fragments)
        
        return fragments
    
    async def _create_entity_fragments(self, entities: List[Dict[str, Any]]) -> List[SynthesisFragment]:
        """Create synthesis fragments for entities"""
        
        fragments = []
        
        # Group entities by type or name
        entity_groups = defaultdict(list)
        
        for entity_result in entities:
            # Extract entities from result
            extracted_entities = self._extract_entities_from_result(entity_result)
            
            for entity in extracted_entities:
                entity_groups[entity['name']].append({
                    'entity': entity,
                    'source': entity_result.get('source_tool', 'unknown'),
                    'confidence': self._extract_confidence(entity_result)
                })
        
        # Create fragments for each entity group
        for entity_name, entity_instances in entity_groups.items():
            # Aggregate confidence
            confidences = [inst['confidence'] for inst in entity_instances]
            avg_confidence = statistics.mean(confidences) if confidences else 0.5
            
            # Get source tools
            source_tools = list(set(inst['source'] for inst in entity_instances))
            
            # Create entity description
            entity_types = list(set(
                inst['entity'].get('type', 'entity') 
                for inst in entity_instances
            ))
            
            content = f"{entity_name}"
            if entity_types and entity_types[0] != 'entity':
                content += f" ({', '.join(entity_types)})"
            
            fragment = SynthesisFragment(
                content=content,
                source_tools=source_tools,
                confidence=avg_confidence,
                fragment_type='entity',
                supporting_evidence=[f"Identified by {len(source_tools)} tools"],
                metadata={'entity_name': entity_name, 'types': entity_types}
            )
            
            fragments.append(fragment)
        
        return fragments
    
    async def _create_relationship_fragments(self, relationships: List[Dict[str, Any]]) -> List[SynthesisFragment]:
        """Create synthesis fragments for relationships"""
        
        fragments = []
        
        # Extract and group relationships
        relationship_groups = defaultdict(list)
        
        for rel_result in relationships:
            extracted_relationships = self._extract_relationships_from_result(rel_result)
            
            for relationship in extracted_relationships:
                key = f"{relationship.get('source', '')} -> {relationship.get('target', '')}"
                relationship_groups[key].append({
                    'relationship': relationship,
                    'source_tool': rel_result.get('source_tool', 'unknown'),
                    'confidence': self._extract_confidence(rel_result)
                })
        
        # Create fragments for each relationship
        for rel_key, rel_instances in relationship_groups.items():
            if not rel_instances:
                continue
            
            # Aggregate information
            confidences = [inst['confidence'] for inst in rel_instances]
            avg_confidence = statistics.mean(confidences) if confidences else 0.5
            
            source_tools = list(set(inst['source_tool'] for inst in rel_instances))
            
            # Get relationship details
            rel = rel_instances[0]['relationship']
            source_entity = rel.get('source', 'Unknown')
            target_entity = rel.get('target', 'Unknown')
            rel_type = rel.get('type', 'related to')
            
            content = f"{source_entity} {rel_type} {target_entity}"
            
            fragment = SynthesisFragment(
                content=content,
                source_tools=source_tools,
                confidence=avg_confidence,
                fragment_type='relationship',
                supporting_evidence=[f"Relationship identified by {len(source_tools)} tools"],
                metadata={
                    'source': source_entity,
                    'target': target_entity,
                    'type': rel_type
                }
            )
            
            fragments.append(fragment)
        
        return fragments
    
    async def _create_theme_fragments(self, themes: List[Dict[str, Any]]) -> List[SynthesisFragment]:
        """Create synthesis fragments for themes"""
        
        fragments = []
        
        for theme_result in themes:
            extracted_themes = self._extract_themes_from_result(theme_result)
            
            for theme in extracted_themes:
                content = theme.get('description', theme.get('name', 'Unknown theme'))
                
                fragment = SynthesisFragment(
                    content=content,
                    source_tools=[theme_result.get('source_tool', 'unknown')],
                    confidence=self._extract_confidence(theme_result),
                    fragment_type='theme',
                    supporting_evidence=[theme.get('evidence', 'Theme analysis')],
                    metadata={'theme': theme}
                )
                
                fragments.append(fragment)
        
        return fragments
    
    async def _create_metric_fragments(self, metrics: List[Dict[str, Any]]) -> List[SynthesisFragment]:
        """Create synthesis fragments for metrics"""
        
        fragments = []
        
        for metric_result in metrics:
            extracted_metrics = self._extract_metrics_from_result(metric_result)
            
            for metric_name, metric_value in extracted_metrics.items():
                content = f"{metric_name}: {metric_value}"
                
                fragment = SynthesisFragment(
                    content=content,
                    source_tools=[metric_result.get('source_tool', 'unknown')],
                    confidence=self._extract_confidence(metric_result),
                    fragment_type='metric',
                    supporting_evidence=[f"Calculated {metric_name}"],
                    metadata={'metric_name': metric_name, 'value': metric_value}
                )
                
                fragments.append(fragment)
        
        return fragments
    
    async def _create_summary_fragments(self, summaries: List[Dict[str, Any]], 
                                      question: str) -> List[SynthesisFragment]:
        """Create synthesis fragments for summaries"""
        
        fragments = []
        
        for summary_result in summaries:
            extracted_summaries = self._extract_summaries_from_result(summary_result)
            
            for summary in extracted_summaries:
                content = summary.get('text', summary.get('content', 'Summary not available'))
                
                fragment = SynthesisFragment(
                    content=content,
                    source_tools=[summary_result.get('source_tool', 'unknown')],
                    confidence=self._extract_confidence(summary_result),
                    fragment_type='summary',
                    supporting_evidence=[summary.get('source', 'Summary analysis')],
                    metadata={'summary': summary}
                )
                
                fragments.append(fragment)
        
        return fragments
    
    async def _synthesize_primary_response(self, fragments: List[SynthesisFragment],
                                         question: str,
                                         strategy: SynthesisStrategy) -> str:
        """Synthesize primary response from fragments"""
        
        if not fragments:
            return "No information available to synthesize a response."
        
        # Select appropriate template based on strategy
        template = self.synthesis_templates.get(strategy, self.synthesis_templates[SynthesisStrategy.COMPREHENSIVE])
        
        # Organize fragments by type
        fragments_by_type = defaultdict(list)
        for fragment in fragments:
            fragments_by_type[fragment.fragment_type].append(fragment)
        
        # Build response sections
        response_sections = []
        
        # Add introduction if needed
        if strategy in [SynthesisStrategy.COMPREHENSIVE, SynthesisStrategy.NARRATIVE]:
            intro = self._create_introduction(question, fragments)
            if intro:
                response_sections.append(intro)
        
        # Add entity information
        if fragments_by_type['entity']:
            entity_section = self._synthesize_entity_section(fragments_by_type['entity'], strategy)
            if entity_section:
                response_sections.append(entity_section)
        
        # Add relationship information
        if fragments_by_type['relationship']:
            relationship_section = self._synthesize_relationship_section(fragments_by_type['relationship'], strategy)
            if relationship_section:
                response_sections.append(relationship_section)
        
        # Add theme information
        if fragments_by_type['theme']:
            theme_section = self._synthesize_theme_section(fragments_by_type['theme'], strategy)
            if theme_section:
                response_sections.append(theme_section)
        
        # Add metrics
        if fragments_by_type['metric']:
            metric_section = self._synthesize_metric_section(fragments_by_type['metric'], strategy)
            if metric_section:
                response_sections.append(metric_section)
        
        # Add summary information
        if fragments_by_type['summary']:
            summary_section = self._synthesize_summary_section(fragments_by_type['summary'], strategy)
            if summary_section:
                response_sections.append(summary_section)
        
        # Combine sections
        if strategy == SynthesisStrategy.NARRATIVE:
            response = self._create_narrative_response(response_sections, question)
        else:
            response = "\n\n".join(response_sections)
        
        return response.strip()
    
    def _synthesize_entity_section(self, entity_fragments: List[SynthesisFragment],
                                 strategy: SynthesisStrategy) -> str:
        """Synthesize entity section"""
        
        if not entity_fragments:
            return ""
        
        # Sort by confidence
        sorted_entities = sorted(entity_fragments, key=lambda f: f.confidence, reverse=True)
        
        if strategy == SynthesisStrategy.SUMMARY:
            top_entities = sorted_entities[:3]  # Top 3 for summary
            entity_names = [f.metadata.get('entity_name', f.content) for f in top_entities]
            return f"Key entities: {', '.join(entity_names)}"
        
        elif strategy == SynthesisStrategy.FOCUSED:
            # Focus on highest confidence entities
            high_conf_entities = [f for f in sorted_entities if f.confidence > 0.7]
            if not high_conf_entities:
                high_conf_entities = sorted_entities[:2]
            
            entity_descriptions = [f.content for f in high_conf_entities]
            return f"Primary entities identified: {', '.join(entity_descriptions)}"
        
        else:  # COMPREHENSIVE, ANALYTICAL, etc.
            entity_descriptions = []
            for fragment in sorted_entities[:5]:  # Top 5 entities
                desc = fragment.content
                if len(fragment.source_tools) > 1:
                    desc += f" (identified by {len(fragment.source_tools)} tools)"
                entity_descriptions.append(desc)
            
            return f"Entities identified: {', '.join(entity_descriptions)}"
    
    def _synthesize_relationship_section(self, relationship_fragments: List[SynthesisFragment],
                                       strategy: SynthesisStrategy) -> str:
        """Synthesize relationship section"""
        
        if not relationship_fragments:
            return ""
        
        # Sort by confidence
        sorted_relationships = sorted(relationship_fragments, key=lambda f: f.confidence, reverse=True)
        
        if strategy == SynthesisStrategy.SUMMARY:
            return f"Key relationships identified: {len(sorted_relationships)} connections found"
        
        elif strategy == SynthesisStrategy.COMPARATIVE:
            # Group by relationship types
            rel_types = defaultdict(list)
            for fragment in sorted_relationships:
                rel_type = fragment.metadata.get('type', 'related to')
                rel_types[rel_type].append(fragment)
            
            comparisons = []
            for rel_type, fragments in rel_types.items():
                comparisons.append(f"{len(fragments)} {rel_type} relationships")
            
            return f"Relationship analysis: {', '.join(comparisons)}"
        
        else:  # COMPREHENSIVE, FOCUSED, etc.
            rel_descriptions = []
            for fragment in sorted_relationships[:3]:  # Top 3 relationships
                rel_descriptions.append(fragment.content)
            
            return f"Key relationships: {'. '.join(rel_descriptions)}"
    
    def _synthesize_theme_section(self, theme_fragments: List[SynthesisFragment],
                                strategy: SynthesisStrategy) -> str:
        """Synthesize theme section"""
        
        if not theme_fragments:
            return ""
        
        sorted_themes = sorted(theme_fragments, key=lambda f: f.confidence, reverse=True)
        
        if strategy == SynthesisStrategy.SUMMARY:
            return f"Main themes: {len(sorted_themes)} themes identified"
        
        else:
            theme_descriptions = [f.content for f in sorted_themes[:3]]
            return f"Themes: {'. '.join(theme_descriptions)}"
    
    def _synthesize_metric_section(self, metric_fragments: List[SynthesisFragment],
                                 strategy: SynthesisStrategy) -> str:
        """Synthesize metrics section"""
        
        if not metric_fragments:
            return ""
        
        if strategy == SynthesisStrategy.ANALYTICAL:
            # Provide detailed metrics analysis
            metric_details = []
            for fragment in metric_fragments:
                metric_name = fragment.metadata.get('metric_name', 'metric')
                metric_value = fragment.metadata.get('value', 'unknown')
                metric_details.append(f"{metric_name}: {metric_value}")
            
            return f"Quantitative analysis: {', '.join(metric_details)}"
        
        else:
            # Simplified metrics
            return f"Metrics calculated: {len(metric_fragments)} measurements"
    
    def _synthesize_summary_section(self, summary_fragments: List[SynthesisFragment],
                                  strategy: SynthesisStrategy) -> str:
        """Synthesize summary section"""
        
        if not summary_fragments:
            return ""
        
        # Combine summaries intelligently
        high_conf_summaries = [f for f in summary_fragments if f.confidence > 0.7]
        if not high_conf_summaries:
            high_conf_summaries = summary_fragments[:1]
        
        # Take the best summary
        best_summary = max(high_conf_summaries, key=lambda f: f.confidence)
        
        return best_summary.content
    
    def _create_introduction(self, question: str, fragments: List[SynthesisFragment]) -> str:
        """Create introduction for response"""
        
        if not fragments:
            return "Based on the analysis:"
        
        total_tools = len(set(tool for fragment in fragments for tool in fragment.source_tools))
        fragment_types = set(fragment.fragment_type for fragment in fragments)
        
        intro_parts = []
        
        if 'entity' in fragment_types:
            intro_parts.append("entities")
        if 'relationship' in fragment_types:
            intro_parts.append("relationships")
        if 'theme' in fragment_types:
            intro_parts.append("themes")
        if 'metric' in fragment_types:
            intro_parts.append("metrics")
        
        if intro_parts:
            content_desc = ", ".join(intro_parts)
            return f"Based on analysis from {total_tools} tools examining {content_desc}:"
        
        return f"Based on analysis from {total_tools} tools:"
    
    def _create_narrative_response(self, sections: List[str], question: str) -> str:
        """Create narrative-style response"""
        
        if not sections:
            return "No information available."
        
        # Add narrative connectors
        narrative_sections = []
        
        for i, section in enumerate(sections):
            if i == 0:
                narrative_sections.append(section)
            elif i == len(sections) - 1:
                narrative_sections.append(f"Finally, {section.lower()}")
            else:
                narrative_sections.append(f"Additionally, {section.lower()}")
        
        return " ".join(narrative_sections)
    
    def _calculate_synthesis_quality(self, fragments: List[SynthesisFragment],
                                   organized_results: Dict[str, List[Dict[str, Any]]]) -> Dict[str, float]:
        """Calculate quality metrics for synthesis"""
        
        if not fragments:
            return {'overall_confidence': 0.0, 'coverage': 0.0, 'coherence': 0.0}
        
        # Overall confidence (weighted average)
        confidences = [f.confidence for f in fragments]
        weights = [len(f.source_tools) for f in fragments]  # Weight by number of sources
        
        if confidences and weights:
            overall_confidence = sum(c * w for c, w in zip(confidences, weights)) / sum(weights)
        else:
            overall_confidence = 0.5
        
        # Coverage (how much of original data is represented)
        total_sources = sum(len(results) for results in organized_results.values())
        represented_sources = len(set(tool for fragment in fragments for tool in fragment.source_tools))
        coverage = represented_sources / max(total_sources, 1)
        
        # Coherence (how well fragments work together)
        fragment_types = set(f.fragment_type for f in fragments)
        coherence = len(fragment_types) / 6.0  # Normalize by max expected types
        
        return {
            'overall_confidence': overall_confidence,
            'coverage': coverage,
            'coherence': coherence
        }
    
    def _calculate_tool_coverage(self, fragments: List[SynthesisFragment],
                               organized_results: Dict[str, List[Dict[str, Any]]]) -> Dict[str, float]:
        """Calculate contribution percentage for each tool"""
        
        # Count fragment contributions by tool
        tool_contributions = defaultdict(int)
        total_fragments = len(fragments)
        
        for fragment in fragments:
            for tool in fragment.source_tools:
                tool_contributions[tool] += 1
        
        # Convert to percentages
        coverage = {}
        for tool, count in tool_contributions.items():
            coverage[tool] = count / max(total_fragments, 1)
        
        return coverage
    
    async def _generate_alternative_perspectives(self, fragments: List[SynthesisFragment],
                                               organized_results: Dict[str, List[Dict[str, Any]]],
                                               conflict_resolution: ConflictResolution) -> List[str]:
        """Generate alternative perspectives from conflicting results"""
        
        alternatives = []
        
        if conflict_resolution == ConflictResolution.ALL_PERSPECTIVES:
            # Already included all perspectives
            return alternatives
        
        # Look for conflicting information that was filtered out
        for content_type, results in organized_results.items():
            if len(results) > 1:
                # There were conflicts - provide alternative view
                confidence_scores = [self._extract_confidence(result) for result in results]
                if len(set(confidence_scores)) > 1:  # Different confidence scores
                    min_conf = min(confidence_scores)
                    max_conf = max(confidence_scores)
                    if max_conf - min_conf > 0.2:  # Significant confidence difference
                        alternatives.append(
                            f"Alternative {content_type} interpretations exist with "
                            f"confidence ranging from {min_conf:.2f} to {max_conf:.2f}"
                        )
        
        return alternatives
    
    def _generate_caveats(self, fragments: List[SynthesisFragment],
                         organized_results: Dict[str, List[Dict[str, Any]]]) -> List[str]:
        """Generate caveats and limitations"""
        
        caveats = []
        
        # Low confidence caveat
        low_conf_fragments = [f for f in fragments if f.confidence < 0.6]
        if low_conf_fragments:
            caveats.append(f"{len(low_conf_fragments)} results have low confidence and should be interpreted carefully")
        
        # Limited source caveat
        single_source_fragments = [f for f in fragments if len(f.source_tools) == 1]
        if len(single_source_fragments) > len(fragments) * 0.5:
            caveats.append("Many results are based on single sources and may benefit from additional validation")
        
        # Data completeness caveat
        if not fragments:
            caveats.append("Limited data available for analysis")
        elif len(fragments) < 3:
            caveats.append("Analysis based on limited information")
        
        return caveats
    
    # Helper methods for extracting information from tool results
    
    def _extract_confidence(self, result: Dict[str, Any]) -> float:
        """Extract confidence score from result"""
        
        if 'confidence' in result:
            conf = result['confidence']
            if isinstance(conf, (int, float)):
                return float(conf)
        
        # Look for confidence in outputs
        if 'outputs' in result:
            outputs = result['outputs']
            if isinstance(outputs, dict):
                for key, value in outputs.items():
                    if 'confidence' in key.lower() and isinstance(value, (int, float)):
                        return float(value)
        
        # Default confidence
        return 0.5
    
    def _create_grouping_key(self, result: Dict[str, Any]) -> str:
        """Create key for grouping similar results"""
        
        # Simple hash of main content
        content_parts = []
        
        if 'outputs' in result:
            outputs = result['outputs']
            if isinstance(outputs, dict):
                for key, value in outputs.items():
                    if key != 'confidence':
                        content_parts.append(str(value)[:50])  # First 50 chars
        
        return '|'.join(content_parts)
    
    def _extract_entities_from_result(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract entities from tool result"""
        
        entities = []
        
        if 'outputs' in result:
            outputs = result['outputs']
            if isinstance(outputs, dict):
                for key, value in outputs.items():
                    if 'entities' in key.lower() or 'entity' in key.lower():
                        if isinstance(value, list):
                            for entity in value:
                                if isinstance(entity, str):
                                    entities.append({'name': entity, 'type': 'entity'})
                                elif isinstance(entity, dict):
                                    entities.append(entity)
                        elif isinstance(value, str):
                            # Simple entity name
                            entities.append({'name': value, 'type': 'entity'})
        
        return entities
    
    def _extract_relationships_from_result(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract relationships from tool result"""
        
        relationships = []
        
        if 'outputs' in result:
            outputs = result['outputs']
            if isinstance(outputs, dict):
                for key, value in outputs.items():
                    if 'relationship' in key.lower() or 'relation' in key.lower():
                        if isinstance(value, list):
                            for rel in value:
                                if isinstance(rel, dict):
                                    relationships.append(rel)
                        elif isinstance(value, dict):
                            relationships.append(value)
        
        return relationships
    
    def _extract_themes_from_result(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract themes from tool result"""
        
        themes = []
        
        if 'outputs' in result:
            outputs = result['outputs']
            if isinstance(outputs, dict):
                for key, value in outputs.items():
                    if 'theme' in key.lower() or 'topic' in key.lower():
                        if isinstance(value, list):
                            for theme in value:
                                if isinstance(theme, str):
                                    themes.append({'name': theme, 'description': theme})
                                elif isinstance(theme, dict):
                                    themes.append(theme)
                        elif isinstance(value, str):
                            themes.append({'name': value, 'description': value})
        
        return themes
    
    def _extract_metrics_from_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metrics from tool result"""
        
        metrics = {}
        
        if 'outputs' in result:
            outputs = result['outputs']
            if isinstance(outputs, dict):
                for key, value in outputs.items():
                    if isinstance(value, (int, float)) and key != 'confidence':
                        metrics[key] = value
        
        return metrics
    
    def _extract_summaries_from_result(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract summaries from tool result"""
        
        summaries = []
        
        if 'outputs' in result:
            outputs = result['outputs']
            if isinstance(outputs, dict):
                for key, value in outputs.items():
                    if 'summary' in key.lower() or 'result' in key.lower():
                        if isinstance(value, str) and len(value) > 20:  # Substantial text
                            summaries.append({'text': value, 'type': 'summary'})
                        elif isinstance(value, dict):
                            summaries.append(value)
        
        return summaries
    
    def _initialize_synthesis_templates(self) -> Dict[SynthesisStrategy, str]:
        """Initialize synthesis templates"""
        
        return {
            SynthesisStrategy.COMPREHENSIVE: "comprehensive_template",
            SynthesisStrategy.FOCUSED: "focused_template",
            SynthesisStrategy.COMPARATIVE: "comparative_template",
            SynthesisStrategy.NARRATIVE: "narrative_template",
            SynthesisStrategy.ANALYTICAL: "analytical_template",
            SynthesisStrategy.SUMMARY: "summary_template"
        }