"""
Conflict Resolution Logic

Extracted from t301_multi_document_fusion.py (ConflictResolver class)
Handles conflicts between document sources with multiple resolution strategies.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ResolutionStrategy(Enum):
    """Enumeration of conflict resolution strategies."""
    CONFIDENCE_WEIGHTED = "confidence_weighted"
    TIME_BASED = "time_based" 
    EVIDENCE_BASED = "evidence_based"
    LLM_BASED = "llm_based"


class ConflictResolver:
    """Handles conflicts between entity sources using multiple strategies."""
    
    def __init__(self, quality_service=None, llm_service=None):
        """Initialize conflict resolver with optional services."""
        self.quality_service = quality_service
        self.llm_service = llm_service
        self.logger = logging.getLogger(f"{__name__}.ConflictResolver")
        
    def resolve_conflicts(self, conflicts: List[Dict[str, Any]], 
                         strategy: ResolutionStrategy = ResolutionStrategy.CONFIDENCE_WEIGHTED) -> List[Dict[str, Any]]:
        """
        Resolve a list of conflicts using the specified strategy.
        
        Args:
            conflicts: List of conflict dictionaries, each containing conflicting entities/data
            strategy: Resolution strategy to use
            
        Returns:
            List of resolved conflicts with resolution metadata
        """
        self.logger.info(f"Resolving {len(conflicts)} conflicts using {strategy.value} strategy")
        
        resolved_conflicts = []
        
        for i, conflict in enumerate(conflicts):
            try:
                resolved = self.resolve_single_conflict(conflict, strategy)
                resolved['conflict_id'] = f"conflict_{i}"
                resolved['resolution_timestamp'] = datetime.now().isoformat()
                resolved_conflicts.append(resolved)
                
            except Exception as e:
                self.logger.error(f"Failed to resolve conflict {i}: {e}")
                # Create error resolution
                error_resolution = {
                    'conflict_id': f"conflict_{i}",
                    'resolution_status': 'failed',
                    'error': str(e),
                    'original_conflict': conflict,
                    'resolution_timestamp': datetime.now().isoformat()
                }
                resolved_conflicts.append(error_resolution)
        
        self.logger.info(f"Resolved {len(resolved_conflicts)} conflicts")
        return resolved_conflicts
    
    def resolve_single_conflict(self, conflict: Dict[str, Any], 
                               strategy: ResolutionStrategy) -> Dict[str, Any]:
        """
        Resolve a single conflict using the specified strategy.
        
        Args:
            conflict: Dictionary containing conflicting entities/data
            strategy: Resolution strategy to use
            
        Returns:
            Dictionary with resolved data and resolution metadata  
        """
        conflicting_entities = conflict.get('entities', [])
        
        if not conflicting_entities:
            return {
                'resolution_status': 'no_conflict',
                'resolved_entity': None,
                'strategy_used': strategy.value,
                'confidence': 0.0
            }
        
        if len(conflicting_entities) == 1:
            return {
                'resolution_status': 'single_entity',
                'resolved_entity': conflicting_entities[0],
                'strategy_used': strategy.value,
                'confidence': conflicting_entities[0].get('confidence', 0.0)
            }
        
        # Apply resolution strategy
        if strategy == ResolutionStrategy.CONFIDENCE_WEIGHTED:
            resolved = self._resolve_by_confidence(conflicting_entities)
        elif strategy == ResolutionStrategy.TIME_BASED:
            resolved = self._resolve_by_time(conflicting_entities)
        elif strategy == ResolutionStrategy.EVIDENCE_BASED:
            resolved = self._resolve_by_evidence(conflicting_entities)
        elif strategy == ResolutionStrategy.LLM_BASED:
            resolved = self._resolve_by_llm(conflicting_entities)
        else:
            # Fallback to confidence-based
            resolved = self._resolve_by_confidence(conflicting_entities)
        
        return {
            'resolution_status': 'resolved',
            'resolved_entity': resolved['entity'],
            'strategy_used': strategy.value,
            'confidence': resolved['confidence'],
            'resolution_reasoning': resolved.get('reasoning', ''),
            'alternatives_considered': len(conflicting_entities),
            'original_entities': conflicting_entities
        }
    
    def _resolve_by_confidence(self, entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Resolve conflict by choosing entity with highest confidence."""
        if not entities:
            return {'entity': None, 'confidence': 0.0, 'reasoning': 'No entities to resolve'}
        
        # Find entity with highest confidence
        best_entity = max(entities, key=lambda e: e.get('confidence', 0.0))
        
        confidence_scores = [e.get('confidence', 0.0) for e in entities]
        avg_confidence = sum(confidence_scores) / len(confidence_scores)
        
        return {
            'entity': best_entity,
            'confidence': best_entity.get('confidence', 0.0),
            'reasoning': f"Selected entity with highest confidence ({best_entity.get('confidence', 0.0):.3f}) among {len(entities)} options. Average confidence: {avg_confidence:.3f}"
        }
    
    def _resolve_by_time(self, entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Resolve conflict by choosing most recent entity."""
        if not entities:
            return {'entity': None, 'confidence': 0.0, 'reasoning': 'No entities to resolve'}
        
        # Find entity with most recent timestamp
        entities_with_time = []
        for entity in entities:
            timestamp_str = entity.get('timestamp') or entity.get('created_at') or entity.get('last_updated')
            if timestamp_str:
                try:
                    # Try to parse timestamp
                    if isinstance(timestamp_str, str):
                        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    else:
                        timestamp = timestamp_str
                    entities_with_time.append((entity, timestamp))
                except Exception:
                    # If timestamp parsing fails, use current time
                    entities_with_time.append((entity, datetime.min))
            else:
                entities_with_time.append((entity, datetime.min))
        
        # Sort by timestamp (most recent first)
        entities_with_time.sort(key=lambda x: x[1], reverse=True)
        best_entity = entities_with_time[0][0]
        
        return {
            'entity': best_entity,
            'confidence': best_entity.get('confidence', 0.0),
            'reasoning': f"Selected most recent entity from {len(entities)} options based on timestamp"
        }
    
    def _resolve_by_evidence(self, entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Resolve conflict by choosing entity with strongest evidence."""
        if not entities:
            return {'entity': None, 'confidence': 0.0, 'reasoning': 'No entities to resolve'}
        
        # Calculate evidence strength for each entity
        entity_scores = []
        
        for entity in entities:
            evidence_score = 0.0
            
            # Count evidence pieces
            evidence = entity.get('evidence', [])
            if isinstance(evidence, list):
                evidence_score += len(evidence) * 0.1
            elif isinstance(evidence, str) and evidence:
                evidence_score += 0.1
            
            # Count sources
            sources = entity.get('sources', [])
            if isinstance(sources, list):
                evidence_score += len(sources) * 0.2
            
            # Count mentions
            mentions = entity.get('mentions', [])
            if isinstance(mentions, list):
                evidence_score += len(mentions) * 0.05
            
            # Factor in confidence
            confidence = entity.get('confidence', 0.0)
            evidence_score *= (1 + confidence)
            
            entity_scores.append((entity, evidence_score))
        
        # Sort by evidence score (highest first)
        entity_scores.sort(key=lambda x: x[1], reverse=True)
        best_entity = entity_scores[0][0]
        best_score = entity_scores[0][1]
        
        return {
            'entity': best_entity,
            'confidence': best_entity.get('confidence', 0.0),
            'reasoning': f"Selected entity with strongest evidence (score: {best_score:.3f}) from {len(entities)} options"
        }
    
    def _resolve_by_llm(self, entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Resolve conflict using LLM-based reasoning."""
        if not self.llm_service:
            self.logger.warning("LLM service not available, falling back to confidence-based resolution")
            return self._resolve_by_confidence(entities)
        
        if not entities:
            return {'entity': None, 'confidence': 0.0, 'reasoning': 'No entities to resolve'}
        
        try:
            # Prepare context for LLM
            context = self._prepare_llm_context(entities)
            
            # Generate LLM prompt
            prompt = self._generate_resolution_prompt(entities, context)
            
            # Get LLM response
            llm_response = self.llm_service.generate_response(prompt)
            
            # Parse LLM decision
            resolved = self._parse_llm_resolution(llm_response, entities)
            
            return resolved
            
        except Exception as e:
            self.logger.error(f"LLM resolution failed: {e}")
            # Fallback to confidence-based
            fallback = self._resolve_by_confidence(entities)
            fallback['reasoning'] = f"LLM resolution failed ({str(e)}), used confidence-based fallback"
            return fallback
    
    def _prepare_llm_context(self, entities: List[Dict[str, Any]]) -> str:
        """Prepare context for LLM conflict resolution."""
        context_parts = []
        
        for i, entity in enumerate(entities):
            entity_desc = f"Entity {i+1}:\n"
            entity_desc += f"  Name: {entity.get('name', 'Unknown')}\n"
            entity_desc += f"  Type: {entity.get('type', 'Unknown')}\n"
            entity_desc += f"  Confidence: {entity.get('confidence', 0.0):.3f}\n"
            
            sources = entity.get('sources', [])
            if sources:
                entity_desc += f"  Sources: {', '.join(sources[:3])}{'...' if len(sources) > 3 else ''}\n"
            
            evidence = entity.get('evidence', [])
            if evidence:
                if isinstance(evidence, list):
                    evidence_str = '; '.join(evidence[:2]) + ('...' if len(evidence) > 2 else '')
                else:
                    evidence_str = str(evidence)[:100] + ('...' if len(str(evidence)) > 100 else '')
                entity_desc += f"  Evidence: {evidence_str}\n"
            
            context_parts.append(entity_desc)
        
        return '\n'.join(context_parts)
    
    def _generate_resolution_prompt(self, entities: List[Dict[str, Any]], context: str) -> str:
        """Generate prompt for LLM conflict resolution."""
        prompt = f"""You are resolving a conflict between {len(entities)} entities that may refer to the same real-world entity. 

Please analyze the following entities and determine which one is most accurate and complete:

{context}

Please respond with:
1. The number (1-{len(entities)}) of the entity you think is most accurate
2. A brief explanation of your reasoning
3. A confidence score (0.0-1.0) for your decision

Format your response as:
SELECTED: [number]
REASONING: [explanation]
CONFIDENCE: [score]
"""
        return prompt
    
    def _parse_llm_resolution(self, llm_response: str, entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Parse LLM response to extract resolution decision."""
        try:
            # Extract selected entity number
            selected_line = [line for line in llm_response.split('\n') if 'SELECTED:' in line]
            if selected_line:
                selected_num = int(selected_line[0].split('SELECTED:')[1].strip())
                selected_idx = selected_num - 1  # Convert to 0-based index
                
                if 0 <= selected_idx < len(entities):
                    selected_entity = entities[selected_idx]
                else:
                    raise ValueError(f"Invalid entity selection: {selected_num}")
            else:
                # Fallback to first entity
                selected_entity = entities[0]
                selected_idx = 0
            
            # Extract reasoning
            reasoning_lines = [line for line in llm_response.split('\n') if 'REASONING:' in line]
            reasoning = reasoning_lines[0].split('REASONING:')[1].strip() if reasoning_lines else "LLM selection"
            
            # Extract confidence
            confidence_lines = [line for line in llm_response.split('\n') if 'CONFIDENCE:' in line]
            if confidence_lines:
                confidence_str = confidence_lines[0].split('CONFIDENCE:')[1].strip()
                confidence = float(confidence_str)
            else:
                confidence = selected_entity.get('confidence', 0.5)
            
            return {
                'entity': selected_entity,
                'confidence': confidence,
                'reasoning': f"LLM selected entity {selected_idx + 1}: {reasoning}"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to parse LLM response: {e}")
            # Fallback to first entity
            return {
                'entity': entities[0],
                'confidence': entities[0].get('confidence', 0.0),
                'reasoning': f"Failed to parse LLM response ({str(e)}), used first entity as fallback"
            }
    
    def get_supported_strategies(self) -> List[str]:
        """Get list of supported resolution strategies."""
        strategies = [strategy.value for strategy in ResolutionStrategy]
        
        # Remove LLM strategy if service not available
        if not self.llm_service:
            strategies = [s for s in strategies if s != ResolutionStrategy.LLM_BASED.value]
        
        return strategies
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get tool information for MCP compatibility."""
        return {
            'tool_name': 'ConflictResolver',
            'description': 'Resolves conflicts between entities from multiple documents',
            'version': '1.0.0',
            'supported_strategies': self.get_supported_strategies(),
            'capabilities': [
                'confidence_based_resolution',
                'time_based_resolution', 
                'evidence_based_resolution',
                'llm_based_resolution' if self.llm_service else None
            ]
        }