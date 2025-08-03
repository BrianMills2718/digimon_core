"""
Mention Processing Components

Handles mention creation, validation, and surface form normalization.
"""

import re
import uuid
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .data_models import Mention

logger = logging.getLogger(__name__)


class SurfaceFormNormalizer:
    """Handles normalization of surface forms for entity matching"""
    
    @staticmethod
    def normalize(surface_form: str) -> str:
        """Normalize surface form for entity matching"""
        if not surface_form:
            return ""
            
        # Basic normalization: lowercase, collapse whitespace
        normalized = re.sub(r'\s+', ' ', surface_form.strip().lower())
        
        # Remove common punctuation at boundaries
        normalized = re.sub(r'^[^\w]+|[^\w]+$', '', normalized)
        
        return normalized

    @staticmethod
    def normalize_advanced(surface_form: str, remove_articles: bool = True, 
                         remove_punctuation: bool = True) -> str:
        """Advanced normalization with more options"""
        if not surface_form:
            return ""
            
        text = surface_form.strip().lower()
        
        # Remove articles if requested
        if remove_articles:
            text = re.sub(r'\b(?:the|a|an)\b\s*', '', text)
        
        # Remove punctuation if requested
        if remove_punctuation:
            text = re.sub(r'[^\w\s]', '', text)
        
        # Collapse whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

    @classmethod
    def get_normalization_variants(cls, surface_form: str) -> Dict[str, str]:
        """Get multiple normalization variants for better matching"""
        return {
            "basic": cls.normalize(surface_form),
            "no_articles": cls.normalize_advanced(surface_form, remove_articles=True, remove_punctuation=False),
            "no_punctuation": cls.normalize_advanced(surface_form, remove_articles=False, remove_punctuation=True),
            "minimal": cls.normalize_advanced(surface_form, remove_articles=True, remove_punctuation=True)
        }


class MentionValidator:
    """Validates mention creation parameters"""
    
    @staticmethod
    def validate_surface_form(surface_form: str) -> Optional[str]:
        """Validate surface form parameter"""
        if not surface_form:
            return "surface_form cannot be empty"
        
        if not surface_form.strip():
            return "surface_form cannot be only whitespace"
        
        if len(surface_form.strip()) > 1000:  # Reasonable limit
            return "surface_form is too long (max 1000 characters)"
        
        return None

    @staticmethod 
    def validate_positions(start_pos: int, end_pos: int) -> Optional[str]:
        """Validate position parameters"""
        if start_pos < 0:
            return "start_pos cannot be negative"
        
        if end_pos <= start_pos:
            return "end_pos must be greater than start_pos"
        
        if end_pos - start_pos > 1000:  # Reasonable limit
            return "mention span is too large (max 1000 characters)"
        
        return None

    @staticmethod
    def validate_confidence(confidence: float) -> Optional[str]:
        """Validate confidence parameter"""
        if not isinstance(confidence, (int, float)):
            return "confidence must be a number"
        
        if not (0.0 <= confidence <= 1.0):
            return "confidence must be between 0.0 and 1.0"
        
        return None

    @staticmethod
    def validate_source_ref(source_ref: str) -> Optional[str]:
        """Validate source reference parameter"""
        if not source_ref:
            return "source_ref cannot be empty"
        
        if not source_ref.strip():
            return "source_ref cannot be only whitespace"
        
        return None

    @classmethod
    def validate_mention_params(cls, surface_form: str, start_pos: int, end_pos: int,
                              source_ref: str, confidence: float = 0.8) -> Optional[str]:
        """Validate all mention creation parameters"""
        # Check each parameter
        error = cls.validate_surface_form(surface_form)
        if error:
            return error
        
        error = cls.validate_positions(start_pos, end_pos)
        if error:
            return error
        
        error = cls.validate_confidence(confidence)
        if error:
            return error
        
        error = cls.validate_source_ref(source_ref)
        if error:
            return error
        
        return None


class MentionProcessor:
    """Main processor for mention operations"""
    
    def __init__(self):
        """Initialize mention processor"""
        self.normalizer = SurfaceFormNormalizer()
        self.validator = MentionValidator()

    def create_mention_id(self) -> str:
        """Generate unique mention ID"""
        return f"mention_{uuid.uuid4().hex[:8]}"

    def process_mention_creation(
        self, 
        surface_form: str,
        start_pos: int,
        end_pos: int,
        source_ref: str,
        entity_type: Optional[str] = None,
        confidence: float = 0.8,
        context: str = ""
    ) -> Dict[str, Any]:
        """Process mention creation with validation and normalization"""
        
        try:
            # Validate input parameters
            validation_error = self.validator.validate_mention_params(
                surface_form, start_pos, end_pos, source_ref, confidence
            )
            
            if validation_error:
                return {
                    "status": "error",
                    "error": validation_error,
                    "error_code": "VALIDATION_FAILED",
                    "confidence": 0.0
                }
            
            # Normalize surface form
            normalized_form = self.normalizer.normalize(surface_form)
            
            if not normalized_form:
                return {
                    "status": "error",
                    "error": "Surface form normalizes to empty string",
                    "error_code": "NORMALIZATION_FAILED",
                    "confidence": 0.0
                }
            
            # Create mention object
            mention_id = self.create_mention_id()
            mention = Mention(
                id=mention_id,
                surface_form=surface_form,
                normalized_form=normalized_form,
                start_pos=start_pos,
                end_pos=end_pos,
                source_ref=source_ref,
                confidence=confidence,
                entity_type=entity_type,
                context=context
            )
            
            return {
                "status": "success",
                "mention": mention,
                "mention_id": mention_id,
                "normalized_form": normalized_form,
                "processing_metadata": {
                    "validation_passed": True,
                    "normalization_applied": True,
                    "processing_time": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing mention creation: {e}", exc_info=True)
            return {
                "status": "error",
                "error": f"Failed to process mention creation: {str(e)}",
                "error_code": "PROCESSING_FAILED",
                "confidence": 0.0
            }

    def update_mention(self, mention: Mention, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update mention with new values"""
        try:
            # Track what was updated
            updated_fields = []
            
            # Update surface form if provided
            if "surface_form" in updates:
                new_surface_form = updates["surface_form"]
                error = self.validator.validate_surface_form(new_surface_form)
                if error:
                    return {
                        "status": "error",
                        "error": f"Invalid surface_form: {error}",
                        "error_code": "VALIDATION_FAILED"
                    }
                
                mention.surface_form = new_surface_form
                mention.normalized_form = self.normalizer.normalize(new_surface_form)
                updated_fields.extend(["surface_form", "normalized_form"])
            
            # Update positions if provided
            if "start_pos" in updates or "end_pos" in updates:
                new_start = updates.get("start_pos", mention.start_pos)
                new_end = updates.get("end_pos", mention.end_pos)
                
                error = self.validator.validate_positions(new_start, new_end)
                if error:
                    return {
                        "status": "error",
                        "error": f"Invalid positions: {error}",
                        "error_code": "VALIDATION_FAILED"
                    }
                
                mention.start_pos = new_start
                mention.end_pos = new_end
                updated_fields.extend(["start_pos", "end_pos"])
            
            # Update confidence if provided
            if "confidence" in updates:
                new_confidence = updates["confidence"]
                error = self.validator.validate_confidence(new_confidence)
                if error:
                    return {
                        "status": "error",
                        "error": f"Invalid confidence: {error}",
                        "error_code": "VALIDATION_FAILED"
                    }
                
                mention.confidence = new_confidence
                updated_fields.append("confidence")
            
            # Update other simple fields
            simple_fields = ["entity_type", "context", "source_ref"]
            for field in simple_fields:
                if field in updates:
                    setattr(mention, field, updates[field])
                    updated_fields.append(field)
            
            return {
                "status": "success",
                "mention": mention,
                "updated_fields": updated_fields,
                "update_metadata": {
                    "fields_updated": len(updated_fields),
                    "update_time": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error updating mention: {e}", exc_info=True)
            return {
                "status": "error",
                "error": f"Failed to update mention: {str(e)}",
                "error_code": "UPDATE_FAILED"
            }

    def get_mention_summary(self, mention: Mention) -> Dict[str, Any]:
        """Get summary information about a mention"""
        return {
            "mention_id": mention.id,
            "surface_form": mention.surface_form,
            "normalized_form": mention.normalized_form,
            "position": {
                "start": mention.start_pos,
                "end": mention.end_pos,
                "length": mention.end_pos - mention.start_pos
            },
            "source_ref": mention.source_ref,
            "entity_type": mention.entity_type,
            "confidence": mention.confidence,
            "has_context": bool(mention.context.strip()),
            "context_length": len(mention.context),
            "is_pii_redacted": mention.is_pii_redacted,
            "created_at": mention.created_at.isoformat(),
            "age_minutes": (datetime.now() - mention.created_at).total_seconds() / 60
        }

    def compare_mentions(self, mention1: Mention, mention2: Mention) -> Dict[str, Any]:
        """Compare two mentions for similarity analysis"""
        return {
            "surface_forms_match": mention1.surface_form == mention2.surface_form,
            "normalized_forms_match": mention1.normalized_form == mention2.normalized_form,
            "entity_types_match": mention1.entity_type == mention2.entity_type,
            "source_refs_match": mention1.source_ref == mention2.source_ref,
            "positions_overlap": self._positions_overlap(mention1, mention2),
            "confidence_difference": abs(mention1.confidence - mention2.confidence),
            "similarity_score": self._calculate_mention_similarity(mention1, mention2)
        }

    def _positions_overlap(self, mention1: Mention, mention2: Mention) -> bool:
        """Check if two mentions have overlapping positions (same source)"""
        if mention1.source_ref != mention2.source_ref:
            return False
        
        return not (mention1.end_pos <= mention2.start_pos or mention2.end_pos <= mention1.start_pos)

    def _calculate_mention_similarity(self, mention1: Mention, mention2: Mention) -> float:
        """Calculate overall similarity score between mentions"""
        score = 0.0
        
        # Surface form similarity (40% weight)
        if mention1.surface_form == mention2.surface_form:
            score += 0.4
        elif mention1.normalized_form == mention2.normalized_form:
            score += 0.3
        
        # Entity type similarity (20% weight)
        if mention1.entity_type == mention2.entity_type:
            score += 0.2
        
        # Source similarity (20% weight)
        if mention1.source_ref == mention2.source_ref:
            score += 0.2
        
        # Confidence similarity (20% weight)
        confidence_similarity = 1.0 - abs(mention1.confidence - mention2.confidence)
        score += 0.2 * confidence_similarity
        
        return min(1.0, score)