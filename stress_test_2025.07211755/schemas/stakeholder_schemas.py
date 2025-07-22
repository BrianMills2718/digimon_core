"""
Stakeholder Theory specific Pydantic schemas
Implements domain-specific data types for stakeholder analysis
"""

from typing import List, Dict, Any, Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum
from .base_schemas import BaseObject, StandardEntity, StandardRelationship

class EvidenceType(str, Enum):
    """Types of evidence for stakeholder claims"""
    LEGAL = "legal"
    MORAL = "moral"
    CONTRACTUAL = "contractual"
    ECONOMIC = "economic"
    SOCIAL = "social"

class StakeholderType(str, Enum):
    """Types of stakeholders"""
    INDIVIDUAL = "individual"
    ORGANIZATION = "organization"
    GROUP = "group"
    INSTITUTION = "institution"
    COMMUNITY = "community"

class InfluenceMechanism(str, Enum):
    """Mechanisms through which influence is exercised"""
    ECONOMIC = "economic"
    LEGAL = "legal"
    SOCIAL = "social"
    POLITICAL = "political"
    MEDIA = "media"
    REGULATORY = "regulatory"

class LegitimacyScore(BaseModel):
    """Stakeholder legitimacy assessment with evidence"""
    
    value: float = Field(..., ge=0.0, le=1.0, description="Legitimacy score 0.0-1.0")
    evidence_type: EvidenceType = Field(..., description="Type of supporting evidence")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in assessment")
    source_mentions: List[str] = Field(default_factory=list, description="Supporting mention IDs")
    
    # Detailed evidence
    legal_basis: Optional[str] = Field(None, description="Legal foundation for claim")
    moral_basis: Optional[str] = Field(None, description="Moral foundation for claim")
    contractual_basis: Optional[str] = Field(None, description="Contractual foundation for claim")
    
    @validator('value')
    def legitimacy_bounds(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Legitimacy must be between 0.0 and 1.0')
        return v

class UrgencyScore(BaseModel):
    """Stakeholder urgency assessment with temporal context"""
    
    value: float = Field(..., ge=0.0, le=1.0, description="Urgency score 0.0-1.0")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in assessment")
    source_mentions: List[str] = Field(default_factory=list, description="Supporting mention IDs")
    
    # Temporal indicators
    time_critical: bool = Field(default=False, description="Whether time-critical")
    deadline_exists: Optional[datetime] = Field(None, description="Specific deadline if any")
    urgency_indicators: List[str] = Field(default_factory=list, description="Textual urgency indicators")
    
    # Decay modeling
    urgency_decay_rate: Optional[float] = Field(None, ge=0.0, description="Rate of urgency decay over time")
    assessment_date: datetime = Field(default_factory=datetime.now, description="When urgency was assessed")

class PowerScore(BaseModel):
    """Stakeholder power assessment with mechanism details"""
    
    value: float = Field(..., ge=0.0, le=1.0, description="Power score 0.0-1.0")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in assessment")
    source_mentions: List[str] = Field(default_factory=list, description="Supporting mention IDs")
    
    # Power mechanisms
    primary_mechanism: InfluenceMechanism = Field(..., description="Primary influence mechanism")
    secondary_mechanisms: List[InfluenceMechanism] = Field(
        default_factory=list, 
        description="Additional influence mechanisms"
    )
    
    # Power indicators
    resource_control: bool = Field(default=False, description="Controls critical resources")
    regulatory_authority: bool = Field(default=False, description="Has regulatory authority")
    media_influence: bool = Field(default=False, description="Has media influence")
    coalition_potential: float = Field(default=0.0, ge=0.0, le=1.0, description="Ability to form coalitions")

class SalienceScore(BaseModel):
    """Mitchell-Agle-Wood stakeholder salience calculation"""
    
    value: float = Field(..., ge=0.0, le=1.0, description="Overall salience score")
    calculation_method: Literal["geometric_mean", "weighted_average", "custom"] = Field(
        default="geometric_mean", 
        description="Method used for calculation"
    )
    
    # Component scores
    legitimacy: float = Field(..., ge=0.0, le=1.0, description="Legitimacy component")
    urgency: float = Field(..., ge=0.0, le=1.0, description="Urgency component")
    power: float = Field(..., ge=0.0, le=1.0, description="Power component")
    
    # Metadata
    calculation_timestamp: datetime = Field(default_factory=datetime.now, description="When calculated")
    edge_case_handling: Optional[str] = Field(None, description="How edge cases were handled")
    
    @validator('value')
    def validate_geometric_mean(cls, v, values):
        """Validate that geometric mean calculation is correct"""
        if all(key in values for key in ['legitimacy', 'urgency', 'power']):
            legitimacy, urgency, power = values['legitimacy'], values['urgency'], values['power']
            
            # Handle zero case
            if any(score == 0.0 for score in [legitimacy, urgency, power]):
                expected = 0.0
            else:
                expected = (legitimacy * urgency * power) ** (1/3)
            
            if abs(v - expected) > 0.001:  # Allow small floating point differences
                raise ValueError(f'Salience {v} does not match geometric mean {expected}')
        return v

class StakeholderEntity(StandardEntity):
    """Stakeholder-specific entity with theory attributes"""
    
    stakeholder_type: StakeholderType = Field(..., description="Type of stakeholder")
    
    # Mitchell-Agle-Wood dimensions
    legitimacy: LegitimacyScore = Field(..., description="Legitimacy assessment")
    urgency: UrgencyScore = Field(..., description="Urgency assessment")
    power: PowerScore = Field(..., description="Power assessment")
    salience: SalienceScore = Field(..., description="Overall salience score")
    
    # Stakeholder classification
    mitchell_category: Optional[str] = Field(None, description="Mitchell typology category")
    priority_tier: Literal["high", "medium", "low"] = Field(..., description="Management priority")
    
    # Relationships
    coalition_members: List[str] = Field(default_factory=list, description="Coalition partner IDs")
    conflicts_with: List[str] = Field(default_factory=list, description="Conflicting stakeholder IDs")
    
    @validator('mitchell_category')
    def validate_mitchell_category(cls, v, values):
        """Validate Mitchell typology classification"""
        valid_categories = [
            "dormant", "discretionary", "demanding", 
            "dominant", "dangerous", "dependent", "definitive"
        ]
        if v is not None and v.lower() not in valid_categories:
            raise ValueError(f'Invalid Mitchell category: {v}')
        return v.lower() if v else v

class StakeholderInfluence(StandardRelationship):
    """Influence relationship between stakeholders"""
    
    # Influence specifics
    influence_strength: float = Field(..., ge=0.0, le=1.0, description="Strength of influence")
    influence_mechanism: InfluenceMechanism = Field(..., description="How influence is exercised")
    conditionality: Optional[str] = Field(None, description="Conditions under which influence applies")
    
    # Temporal aspects
    temporal_scope: Optional[str] = Field(None, description="Time period of influence")
    influence_decay: Optional[float] = Field(None, ge=0.0, description="Rate of influence decay")
    
    # N-ary relation support
    intermediary_actors: List[str] = Field(
        default_factory=list, 
        description="Intermediary actors in influence chain"
    )
    context_factors: Dict[str, str] = Field(
        default_factory=dict, 
        description="Contextual factors affecting influence"
    )

class PolicyDocument(BaseModel):
    """Policy document for stakeholder analysis"""
    
    # Document identification
    document_id: str = Field(..., description="Unique document identifier")
    title: str = Field(..., description="Document title")
    document_type: Literal["policy", "proposal", "regulation", "report", "analysis"] = Field(
        ..., 
        description="Type of policy document"
    )
    
    # Content
    content: str = Field(..., description="Full document text")
    abstract: Optional[str] = Field(None, description="Document abstract or summary")
    
    # Metadata
    organization: Optional[str] = Field(None, description="Publishing organization")
    publication_date: Optional[datetime] = Field(None, description="Publication date")
    policy_domain: Optional[str] = Field(None, description="Policy domain (e.g., healthcare, environment)")
    
    # Analysis metadata
    stakeholder_count: Optional[int] = Field(None, ge=0, description="Number of stakeholders identified")
    complexity_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Document complexity")

class StakeholderAnalysisResult(BaseModel):
    """Complete stakeholder analysis results"""
    
    # Analysis metadata
    analysis_id: str = Field(..., description="Unique analysis identifier")
    document_ref: str = Field(..., description="Source document reference")
    analysis_timestamp: datetime = Field(default_factory=datetime.now, description="Analysis timestamp")
    
    # Results
    stakeholders: List[StakeholderEntity] = Field(..., description="Identified stakeholders")
    relationships: List[StakeholderInfluence] = Field(..., description="Stakeholder relationships")
    
    # Summary statistics
    total_stakeholders: int = Field(..., ge=0, description="Total stakeholders identified")
    high_salience_count: int = Field(..., ge=0, description="High salience stakeholders")
    coalition_count: int = Field(..., ge=0, description="Number of coalitions identified")
    
    # Quality metrics
    analysis_confidence: float = Field(..., ge=0.0, le=1.0, description="Overall analysis confidence")
    coverage_completeness: float = Field(..., ge=0.0, le=1.0, description="Estimated coverage completeness")
    
    # Theory validation
    theory_compliance: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Theory validation results"
    )
    boundary_cases_detected: List[str] = Field(
        default_factory=list, 
        description="Boundary cases encountered"
    )

# Stakeholder schema registry
STAKEHOLDER_SCHEMA_REGISTRY = {
    "LegitimacyScore": LegitimacyScore,
    "UrgencyScore": UrgencyScore,
    "PowerScore": PowerScore,
    "SalienceScore": SalienceScore,
    "StakeholderEntity": StakeholderEntity,
    "StakeholderInfluence": StakeholderInfluence,
    "PolicyDocument": PolicyDocument,
    "StakeholderAnalysisResult": StakeholderAnalysisResult
}

def create_test_stakeholder() -> StakeholderEntity:
    """Create a test stakeholder for validation"""
    return StakeholderEntity(
        id="stakeholder_001",
        object_type="entity",
        confidence=0.85,
        quality_tier="silver",
        created_by="test_system",
        workflow_id="test_workflow",
        canonical_name="Environmental Protection Agency",
        entity_type="organization",
        stakeholder_type=StakeholderType.INSTITUTION,
        legitimacy=LegitimacyScore(
            value=0.9,
            evidence_type=EvidenceType.LEGAL,
            confidence=0.95,
            legal_basis="Federal environmental protection mandate"
        ),
        urgency=UrgencyScore(
            value=0.7,
            confidence=0.8,
            time_critical=True,
            urgency_indicators=["immediate action required", "environmental deadline"]
        ),
        power=PowerScore(
            value=0.8,
            confidence=0.9,
            primary_mechanism=InfluenceMechanism.REGULATORY,
            regulatory_authority=True
        ),
        salience=SalienceScore(
            value=0.787,  # (0.9 * 0.7 * 0.8) ** (1/3)
            legitimacy=0.9,
            urgency=0.7,
            power=0.8
        ),
        priority_tier="high"
    )