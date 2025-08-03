"""Quality Service Constants

Centralized configuration constants for QualityService to replace magic numbers
and enable easy tuning of system behavior.
"""

# Quality Tier Thresholds
QUALITY_TIER_HIGH_THRESHOLD = 0.8      # confidence >= 0.8 for HIGH tier
QUALITY_TIER_MEDIUM_THRESHOLD = 0.5    # confidence >= 0.5 for MEDIUM tier

# Confidence Factor Weights
CONFIDENCE_FACTOR_WEIGHT = 0.2          # Weight for each additional factor in confidence calculation
BASE_CONFIDENCE_WEIGHT = 1.0            # Weight for base confidence

# Default Confidence Values
DEFAULT_CONFIDENCE_NO_INPUTS = 0.5      # Default confidence for operations with no inputs
DEFAULT_CONFIDENCE_UNKNOWN_OBJECT = 0.7 # Default confidence for unknown objects
DEFAULT_CONFIDENCE_ERROR = 0.5          # Default confidence returned on errors
DEFAULT_CONFIDENCE_CONSERVATIVE = 0.3   # Conservative confidence for error conditions
DEFAULT_OVERALL_HEALTH = 0.5           # Default overall health score

# Quality Rule Defaults
DEFAULT_DEGRADATION_FACTOR = 0.9        # Default degradation for unknown operations
DEFAULT_MIN_CONFIDENCE = 0.1            # Default minimum confidence

# Default Quality Rules Configuration
DEFAULT_QUALITY_RULES = [
    {
        "rule_id": "text_extraction",
        "source_type": "pdf_loader", 
        "degradation_factor": 0.95,     # 5% degradation
        "min_confidence": 0.1,
        "description": "Text extraction from PDF"
    },
    {
        "rule_id": "nlp_processing",
        "source_type": "spacy_ner",
        "degradation_factor": 0.9,      # 10% degradation  
        "min_confidence": 0.1,
        "description": "NLP entity extraction"
    },
    {
        "rule_id": "relationship_extraction", 
        "source_type": "relationship_extractor",
        "degradation_factor": 0.85,     # 15% degradation
        "min_confidence": 0.1,
        "description": "Relationship extraction from text"
    },
    {
        "rule_id": "entity_linking",
        "source_type": "entity_builder",
        "degradation_factor": 0.9,      # 10% degradation
        "min_confidence": 0.1,
        "description": "Entity creation and linking"
    },
    {
        "rule_id": "graph_analysis",
        "source_type": "pagerank",
        "degradation_factor": 0.95,     # 5% degradation
        "min_confidence": 0.1,
        "description": "Graph analysis operations"
    }
]

# Trend Analysis Constants
TREND_SLOPE_IMPROVING_THRESHOLD = 0.01   # Slope > 0.01 considered improving
TREND_SLOPE_DECLINING_THRESHOLD = -0.01  # Slope < -0.01 considered declining

# History Management
CONFIDENCE_HISTORY_MAX_ENTRIES = 10      # Maximum entries to keep in confidence history

# Configuration Keys
CONFIG_KEY_DEFAULT_CONFIDENCE = 'default_confidence'
CONFIG_KEY_QUALITY_TIERS = 'quality_tiers'
CONFIG_KEY_DEGRADATION_SETTINGS = 'degradation_settings'
CONFIG_KEY_HISTORY_RETENTION_DAYS = 'history_retention_days'