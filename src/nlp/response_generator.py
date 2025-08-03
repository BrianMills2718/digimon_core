"""
Natural Language Response Generator
Converts tool outputs and provenance data into natural language responses
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging
from datetime import datetime

from .question_parser import QuestionIntent

logger = logging.getLogger(__name__)

@dataclass
class SynthesizedData:
    """Synthesized data from multiple tool outputs"""
    entities: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    themes: List[str]
    key_insights: List[str]
    document_info: Dict[str, Any]
    confidence_score: float

@dataclass
class ProvenanceInfo:
    """Provenance information for response"""
    tools_used: List[str]
    total_execution_time: float
    entity_count: int
    relationship_count: int
    processing_steps: List[Dict[str, Any]]
    confidence_scores: Dict[str, float]

class ResultSynthesizer:
    """Synthesize results from multiple tool outputs"""
    
    def synthesize(self, tool_results: Dict[str, Any], intent: QuestionIntent) -> SynthesizedData:
        """Synthesize tool results into structured data"""
        
        # Extract entities from T23A results
        entities = self._extract_entities(tool_results.get('T23A_SPACY_NER', {}))
        
        # Extract relationships from T27 results
        relationships = self._extract_relationships(tool_results.get('T27_RELATIONSHIP_EXTRACTOR', {}))
        
        # Extract document info from T01 results
        document_info = self._extract_document_info(tool_results.get('T01_PDF_LOADER', {}))
        
        # Extract themes based on entities and relationships
        themes = self._extract_themes(entities, relationships)
        
        # Generate key insights
        key_insights = self._generate_insights(entities, relationships, intent)
        
        # Calculate overall confidence
        confidence_score = self._calculate_confidence(tool_results)
        
        return SynthesizedData(
            entities=entities,
            relationships=relationships,
            themes=themes,
            key_insights=key_insights,
            document_info=document_info,
            confidence_score=confidence_score
        )
    
    def _extract_entities(self, t23a_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract and format entities from T23A results"""
        entities = []
        
        if 'data' in t23a_result and 'entities' in t23a_result['data']:
            raw_entities = t23a_result['data']['entities']
            
            for entity in raw_entities:
                formatted_entity = {
                    'text': entity.get('surface_form', entity.get('text', 'Unknown')),
                    'type': entity.get('entity_type', 'UNKNOWN'),
                    'confidence': entity.get('confidence', 0.0)
                }
                entities.append(formatted_entity)
        
        return entities
    
    def _extract_relationships(self, t27_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract and format relationships from T27 results"""
        relationships = []
        
        if 'data' in t27_result and 'relationships' in t27_result['data']:
            raw_relationships = t27_result['data']['relationships']
            
            for rel in raw_relationships:
                formatted_rel = {
                    'source': rel.get('entity1', 'Unknown'),
                    'target': rel.get('entity2', 'Unknown'),
                    'type': rel.get('relationship_type', 'RELATED_TO'),
                    'confidence': rel.get('confidence', 0.0),
                    'context': rel.get('context', '')
                }
                relationships.append(formatted_rel)
        
        return relationships
    
    def _extract_document_info(self, t01_result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract document information from T01 results"""
        doc_info = {
            'title': 'Unknown Document',
            'page_count': 0,
            'word_count': 0,
            'file_size': 0
        }
        
        if 'data' in t01_result and 'document' in t01_result['data']:
            document = t01_result['data']['document']
            doc_info.update({
                'title': document.get('file_name', 'Unknown Document'),
                'page_count': document.get('page_count', 1),
                'word_count': max(1, document.get('text_length', 0) // 5),  # Rough word count estimate
                'file_size': document.get('file_size', 0)
            })
        
        return doc_info
    
    def _extract_themes(self, entities: List[Dict[str, Any]], 
                       relationships: List[Dict[str, Any]]) -> List[str]:
        """Extract themes from entities and relationships"""
        themes = []
        
        # Count entity types to identify major themes
        entity_type_counts = {}
        for entity in entities:
            entity_type = entity['type']
            entity_type_counts[entity_type] = entity_type_counts.get(entity_type, 0) + 1
        
        # Convert entity types to theme names
        entity_type_themes = {
            'PERSON': 'People & Leadership',
            'ORG': 'Organizations & Institutions',
            'GPE': 'Locations & Geography',
            'MONEY': 'Financial & Economic',
            'DATE': 'Temporal & Timeline',
            'PRODUCT': 'Products & Services',
            'EVENT': 'Events & Activities'
        }
        
        for entity_type, count in entity_type_counts.items():
            if count >= 2:  # Only include themes with multiple entities
                theme_name = entity_type_themes.get(entity_type, entity_type.title())
                themes.append(theme_name)
        
        # Add relationship-based themes
        relationship_types = [rel['type'] for rel in relationships]
        if 'WORKS_FOR' in relationship_types or 'EMPLOYED_BY' in relationship_types:
            themes.append('Employment & Professional Relationships')
        if 'LOCATED_IN' in relationship_types:
            themes.append('Geographic & Spatial Relationships')
        if 'OWNS' in relationship_types:
            themes.append('Ownership & Control')
        
        return themes[:5]  # Limit to top 5 themes
    
    def _generate_insights(self, entities: List[Dict[str, Any]], 
                          relationships: List[Dict[str, Any]], 
                          intent: QuestionIntent) -> List[str]:
        """Generate key insights based on analysis results"""
        insights = []
        
        if entities:
            # Entity insights
            high_confidence_entities = [e for e in entities if e['confidence'] > 0.8]
            if high_confidence_entities:
                insights.append(f"Found {len(high_confidence_entities)} high-confidence entities")
            
            # Most common entity type
            entity_types = [e['type'] for e in entities]
            if entity_types:
                most_common_type = max(set(entity_types), key=entity_types.count)
                count = entity_types.count(most_common_type)
                insights.append(f"Document focuses heavily on {most_common_type.lower()} entities ({count} found)")
        
        if relationships:
            # Relationship insights
            rel_types = [r['type'] for r in relationships]
            if rel_types:
                most_common_rel = max(set(rel_types), key=rel_types.count)
                count = rel_types.count(most_common_rel)
                insights.append(f"Primary relationship type is {most_common_rel} ({count} instances)")
            
            # Network density insight
            unique_entities_in_rels = set()
            for rel in relationships:
                unique_entities_in_rels.add(rel['source'])
                unique_entities_in_rels.add(rel['target'])
            
            if len(unique_entities_in_rels) > 1:
                density = len(relationships) / len(unique_entities_in_rels)
                if density > 1.5:
                    insights.append("High relationship density - entities are well-connected")
                elif density < 0.5:
                    insights.append("Low relationship density - entities are loosely connected")
        
        # Intent-specific insights
        if intent == QuestionIntent.DOCUMENT_SUMMARY:
            insights.append("Document structure analyzed for comprehensive overview")
        elif intent == QuestionIntent.PAGERANK_ANALYSIS:
            insights.append("Entity importance calculated using network centrality")
        
        return insights[:4]  # Limit to top 4 insights
    
    def _calculate_confidence(self, tool_results: Dict[str, Any]) -> float:
        """Calculate overall confidence score from tool results"""
        confidence_scores = []
        
        for tool_id, result in tool_results.items():
            if isinstance(result, dict) and 'metadata' in result:
                metadata = result['metadata']
                if 'confidence' in metadata:
                    confidence_scores.append(metadata['confidence'])
        
        if confidence_scores:
            return sum(confidence_scores) / len(confidence_scores)
        else:
            return 0.75  # Default confidence if no scores available

class ResponseTemplates:
    """Templates for different types of responses"""
    
    TEMPLATES = {
        QuestionIntent.DOCUMENT_SUMMARY: """Based on my analysis of the document, here's a comprehensive summary:

**Document Overview:**
- Title: {document_title}
- Content: {entity_count} entities analyzed across {page_count} pages

**Key Entities:** {top_entities}

**Main Themes:** {themes}

**Key Insights:**
{insights}

**Summary:** This document appears to focus on {primary_theme} with significant attention to {secondary_focus}. The analysis reveals {relationship_count} relationships between entities, indicating {relationship_analysis}.
""",

        QuestionIntent.ENTITY_ANALYSIS: """I identified {entity_count} key entities in the document:

**Entities by Type:**
{entities_by_type}

**High-Confidence Entities:**
{high_confidence_entities}

**Key Insights:**
{insights}

These entities are connected through {relationship_count} relationships, showing {connectivity_analysis}.
""",

        QuestionIntent.RELATIONSHIP_ANALYSIS: """Here are the key relationships I discovered:

**Relationship Summary:**
- Total relationships found: {relationship_count}
- Primary relationship types: {top_relationship_types}

**Key Connections:**
{key_relationships}

**Network Analysis:**
{network_insights}

The relationship patterns suggest {relationship_conclusion}.
""",

        QuestionIntent.THEME_ANALYSIS: """I identified the following major themes in the document:

**Main Themes:**
{themes_detailed}

**Theme Analysis:**
{theme_insights}

**Supporting Evidence:**
- {entity_count} entities support these themes
- {relationship_count} relationships reinforce thematic connections

**Conclusion:** {theme_conclusion}
""",

        QuestionIntent.SPECIFIC_SEARCH: """Based on your search query, here's what I found:

**Search Results:**
{search_results}

**Related Entities:**
{related_entities}

**Context:**
{search_context}

**Additional Information:**
{additional_info}
""",

        "default": """Analysis Results:

**Entities Found:** {entity_count}
**Relationships:** {relationship_count}
**Key Themes:** {themes}

**Summary:** {summary_text}

**Processing Notes:** {processing_info}
"""
    }
    
    def get_template(self, intent: QuestionIntent) -> str:
        """Get template for specific intent"""
        return self.TEMPLATES.get(intent, self.TEMPLATES["default"])

class ResponseGenerator:
    """Generate natural language responses from tool results"""
    
    def __init__(self):
        self.templates = ResponseTemplates()
        self.synthesizer = ResultSynthesizer()
    
    def generate_response(self, question: str, tool_results: Dict[str, Any], 
                         intent: QuestionIntent, provenance_data: Dict[str, Any] = None) -> str:
        """Convert tool outputs to natural language answer"""
        
        # 1. Synthesize results from multiple tools
        synthesized_data = self.synthesizer.synthesize(tool_results, intent)
        
        # 2. Extract provenance information
        provenance_info = self._extract_provenance_info(tool_results, provenance_data)
        
        # 3. Select appropriate response template
        template = self.templates.get_template(intent)
        
        # 4. Fill template with synthesized data
        response = self._fill_template(template, synthesized_data, provenance_info, intent)
        
        # 5. Add provenance footer
        response += self._generate_provenance_footer(provenance_info)
        
        return response
    
    def _extract_provenance_info(self, tool_results: Dict[str, Any], 
                                provenance_data: Dict[str, Any] = None) -> ProvenanceInfo:
        """Extract provenance information from results"""
        
        tools_used = list(tool_results.keys())
        total_time = 0.0
        entity_count = 0
        relationship_count = 0
        confidence_scores = {}
        
        # Extract counts and metrics
        for tool_id, result in tool_results.items():
            if isinstance(result, dict):
                if 'data' in result:
                    tool_result = result['data']
                    if 'entities' in tool_result:
                        entity_count = len(tool_result['entities'])
                    if 'relationships' in tool_result:
                        relationship_count = len(tool_result['relationships'])
                
                if 'metadata' in result:
                    metadata = result['metadata']
                    if 'execution_time' in metadata:
                        total_time += metadata['execution_time']
                    if 'confidence' in metadata:
                        confidence_scores[tool_id] = metadata['confidence']
        
        # Create processing steps summary
        processing_steps = []
        for tool_id in tools_used:
            step_info = {
                'tool': tool_id,
                'description': self._get_tool_description(tool_id),
                'status': 'completed'
            }
            processing_steps.append(step_info)
        
        return ProvenanceInfo(
            tools_used=tools_used,
            total_execution_time=total_time,
            entity_count=entity_count,
            relationship_count=relationship_count,
            processing_steps=processing_steps,
            confidence_scores=confidence_scores
        )
    
    def _get_tool_description(self, tool_id: str) -> str:
        """Get human-readable description of tool"""
        descriptions = {
            'T01_PDF_LOADER': 'Document loading and text extraction',
            'T15A_TEXT_CHUNKER': 'Text segmentation and chunking',
            'T23A_SPACY_NER': 'Named entity recognition using spaCy',
            'T27_RELATIONSHIP_EXTRACTOR': 'Relationship pattern extraction',
            'T31_ENTITY_BUILDER': 'Entity graph construction',
            'T34_EDGE_BUILDER': 'Relationship graph construction',
            'T68_PAGE_RANK': 'Entity importance calculation',
            'T49_MULTI_HOP_QUERY': 'Complex graph queries'
        }
        return descriptions.get(tool_id, f'Tool {tool_id}')
    
    def _fill_template(self, template: str, synthesized_data: SynthesizedData, 
                      provenance_info: ProvenanceInfo, intent: QuestionIntent) -> str:
        """Fill template with actual data"""
        
        # Prepare template variables
        template_vars = {
            'entity_count': provenance_info.entity_count,
            'relationship_count': provenance_info.relationship_count,
            'document_title': synthesized_data.document_info.get('title', 'Unknown Document'),
            'page_count': synthesized_data.document_info.get('page_count', 'unknown'),
            'themes': ', '.join(synthesized_data.themes) if synthesized_data.themes else 'No specific themes identified',
            'insights': '\n'.join(f"• {insight}" for insight in synthesized_data.key_insights),
            'top_entities': ', '.join([e['text'] for e in synthesized_data.entities[:5]]) if synthesized_data.entities else 'None found',
            'processing_info': f"Processed using {len(provenance_info.tools_used)} tools in {provenance_info.total_execution_time:.2f}s",
            'primary_theme': synthesized_data.themes[0] if synthesized_data.themes else 'general content analysis',
            'secondary_focus': synthesized_data.themes[1] if len(synthesized_data.themes) > 1 else 'document structure',
            'relationship_analysis': self._analyze_relationship_patterns(synthesized_data.relationships)
        }
        
        # Intent-specific variables
        if intent == QuestionIntent.ENTITY_ANALYSIS:
            entities_by_type = self._format_entities_by_type(synthesized_data.entities)
            template_vars.update({
                'entities_by_type': entities_by_type,
                'high_confidence_entities': self._format_high_confidence_entities(synthesized_data.entities),
                'connectivity_analysis': self._analyze_connectivity(synthesized_data.relationships)
            })
        elif intent == QuestionIntent.RELATIONSHIP_ANALYSIS:
            template_vars.update({
                'top_relationship_types': self._get_top_relationship_types(synthesized_data.relationships),
                'key_relationships': self._format_key_relationships(synthesized_data.relationships),
                'network_insights': '\n'.join(f"• {insight}" for insight in synthesized_data.key_insights),
                'relationship_conclusion': self._analyze_relationship_patterns(synthesized_data.relationships)
            })
        
        # Fill template with error handling
        try:
            return template.format(**template_vars)
        except KeyError as e:
            logger.warning(f"Template variable missing: {e}")
            # Fallback to simple response
            return f"""Analysis completed successfully:

• Found {template_vars['entity_count']} entities
• Identified {template_vars['relationship_count']} relationships
• Key themes: {template_vars['themes']}

{template_vars['processing_info']}"""
    
    def _format_entities_by_type(self, entities: List[Dict[str, Any]]) -> str:
        """Format entities grouped by type"""
        type_groups = {}
        for entity in entities:
            entity_type = entity['type']
            if entity_type not in type_groups:
                type_groups[entity_type] = []
            type_groups[entity_type].append(entity['text'])
        
        formatted = []
        for entity_type, entity_list in type_groups.items():
            formatted.append(f"• {entity_type}: {', '.join(entity_list[:3])}")
            if len(entity_list) > 3:
                formatted[-1] += f" (and {len(entity_list) - 3} more)"
        
        return '\n'.join(formatted) if formatted else 'No entities categorized'
    
    def _format_high_confidence_entities(self, entities: List[Dict[str, Any]]) -> str:
        """Format high-confidence entities"""
        high_conf = [e for e in entities if e['confidence'] > 0.8]
        if high_conf:
            return '\n'.join(f"• {e['text']} ({e['type']}) - {e['confidence']:.1%} confidence" 
                           for e in high_conf[:5])
        else:
            return 'No high-confidence entities identified'
    
    def _analyze_connectivity(self, relationships: List[Dict[str, Any]]) -> str:
        """Analyze entity connectivity"""
        if not relationships:
            return "limited connectivity between entities"
        
        unique_entities = set()
        for rel in relationships:
            unique_entities.add(rel['source'])
            unique_entities.add(rel['target'])
        
        if len(unique_entities) > 1:
            density = len(relationships) / len(unique_entities)
            if density > 1.5:
                return "high connectivity with dense relationship networks"
            elif density > 0.8:
                return "moderate connectivity with clear relationship patterns"
            else:
                return "sparse connectivity with few direct relationships"
        else:
            return "minimal connectivity detected"
    
    def _get_top_relationship_types(self, relationships: List[Dict[str, Any]]) -> str:
        """Get most common relationship types"""
        if not relationships:
            return "None identified"
        
        type_counts = {}
        for rel in relationships:
            rel_type = rel['type']
            type_counts[rel_type] = type_counts.get(rel_type, 0) + 1
        
        top_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        return ', '.join(f"{rel_type} ({count})" for rel_type, count in top_types)
    
    def _format_key_relationships(self, relationships: List[Dict[str, Any]]) -> str:
        """Format key relationships for display"""
        if not relationships:
            return "No relationships identified"
        
        formatted = []
        for rel in relationships[:5]:  # Show top 5
            formatted.append(f"• {rel['source']} → {rel['type']} → {rel['target']}")
            if rel.get('confidence', 0) > 0.8:
                formatted[-1] += f" (high confidence)"
        
        return '\n'.join(formatted)
    
    def _analyze_relationship_patterns(self, relationships: List[Dict[str, Any]]) -> str:
        """Analyze overall relationship patterns"""
        if not relationships:
            return "no clear relationship patterns were identified"
        
        # Analyze patterns
        rel_types = [r['type'] for r in relationships]
        if 'WORKS_FOR' in rel_types or 'EMPLOYED_BY' in rel_types:
            return "professional and organizational structures dominate the relationships"
        elif 'LOCATED_IN' in rel_types:
            return "geographic and spatial relationships are prominent"
        elif 'OWNS' in rel_types:
            return "ownership and control relationships are key themes"
        else:
            return f"diverse relationship patterns with {len(set(rel_types))} different types identified"
    
    def _generate_provenance_footer(self, provenance_info: ProvenanceInfo) -> str:
        """Generate provenance information footer"""
        
        footer = f"""

---
**Analysis Provenance:**
• Tools used: {', '.join(provenance_info.tools_used)}
• Processing time: {provenance_info.total_execution_time:.2f} seconds
• Entities processed: {provenance_info.entity_count}
• Relationships identified: {provenance_info.relationship_count}
• Overall confidence: {(sum(provenance_info.confidence_scores.values()) / len(provenance_info.confidence_scores) * 100) if provenance_info.confidence_scores else 75.0:.1f}% (based on {len(provenance_info.confidence_scores)} tools)

*This analysis maintains complete audit trails for research reproducibility.*
"""
        return footer