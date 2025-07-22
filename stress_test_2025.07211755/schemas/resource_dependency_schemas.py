"""
Resource Dependency Theory Pydantic Schemas
Implements data structures for Resource Dependency Theory analysis
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from enum import Enum
from .base_schemas import BaseObject, ValidationResult

class ResourceType(str, Enum):
    FINANCIAL = "financial"
    HUMAN = "human" 
    TECHNOLOGICAL = "technological"
    INFORMATION = "information"
    MATERIAL = "material"
    REGULATORY = "regulatory"

class DependencyLevel(str, Enum):
    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"

class ResourceCriticalityScore(BaseModel):
    """Resource criticality assessment"""
    value: float = Field(..., ge=0.0, le=1.0, description="Criticality score 0.0-1.0")
    evidence_type: str = Field(..., description="Type of evidence supporting score")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in assessment")
    business_impact: Optional[str] = Field(None, description="Potential business impact")
    
    @validator('value')
    def validate_criticality(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Resource criticality must be between 0.0 and 1.0')
        return v

class ResourceScarcityScore(BaseModel):
    """Resource scarcity assessment"""
    value: float = Field(..., ge=0.0, le=1.0, description="Scarcity score 0.0-1.0")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in assessment") 
    market_indicators: List[str] = Field(default_factory=list, description="Market scarcity indicators")
    availability_timeframe: Optional[str] = Field(None, description="Expected availability timeframe")
    
    @validator('value')
    def validate_scarcity(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Resource scarcity must be between 0.0 and 1.0')
        return v

class SubstituteAvailabilityScore(BaseModel):
    """Substitute availability assessment"""
    value: float = Field(..., ge=0.0, le=1.0, description="Substitute availability 0.0-1.0")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in assessment")
    substitute_count: int = Field(default=0, description="Number of known substitutes")
    substitute_names: List[str] = Field(default_factory=list, description="Names of substitute resources")
    
    @validator('value')
    def validate_substitutes(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Substitute availability must be between 0.0 and 1.0')
        return v

class DependencyScore(BaseModel):
    """Resource dependency calculation result"""
    value: float = Field(..., ge=0.0, le=1.0, description="Dependency score 0.0-1.0")
    criticality: float = Field(..., ge=0.0, le=1.0)
    scarcity: float = Field(..., ge=0.0, le=1.0)
    substitute_availability: float = Field(..., ge=0.0, le=1.0)
    dependency_level: DependencyLevel = Field(..., description="Categorical dependency level")
    
    @validator('value')
    def validate_geometric_mean(cls, v, values):
        if all(key in values for key in ['criticality', 'scarcity', 'substitute_availability']):
            criticality, scarcity, substitute_availability = values['criticality'], values['scarcity'], values['substitute_availability']
            # Dependency = (criticality * scarcity * (1 - substitute_availability))^(1/3)
            expected = (criticality * scarcity * (1 - substitute_availability)) ** (1/3)
            if abs(v - expected) > 0.001:
                raise ValueError(f'Dependency {v} does not match geometric mean {expected}')
        return v
    
    @validator('dependency_level')
    def validate_dependency_category(cls, v, values):
        if 'value' in values:
            score = values['value']
            if score >= 0.7 and v != DependencyLevel.HIGH:
                raise ValueError('High dependency score must have HIGH level')
            elif 0.4 <= score < 0.7 and v != DependencyLevel.MODERATE:
                raise ValueError('Moderate dependency score must have MODERATE level')
            elif score < 0.4 and v != DependencyLevel.LOW:
                raise ValueError('Low dependency score must have LOW level')
        return v

class OrganizationEntity(BaseObject):
    """Organization entity for resource dependency analysis"""
    canonical_name: str = Field(..., description="Official organization name")
    entity_type: str = Field(default="organization", description="Entity type")
    sector: str = Field(..., description="Business sector")
    size: str = Field(..., description="Organization size")
    founding_year: Optional[int] = Field(None, description="Year founded")
    headquarters: Optional[str] = Field(None, description="Headquarters location")
    revenue: Optional[float] = Field(None, description="Annual revenue")

class ResourceEntity(BaseObject):
    """Resource entity for dependency analysis"""
    canonical_name: str = Field(..., description="Resource name")
    entity_type: str = Field(default="resource", description="Entity type")
    resource_type: ResourceType = Field(..., description="Type of resource")
    criticality_score: ResourceCriticalityScore = Field(..., description="Resource criticality")
    market_value: Optional[float] = Field(None, description="Market value if applicable")
    scarcity_indicators: List[str] = Field(default_factory=list, description="Scarcity indicators")

class SupplierEntity(BaseObject):
    """Supplier entity for resource provision analysis"""
    canonical_name: str = Field(..., description="Supplier name")
    entity_type: str = Field(default="supplier", description="Entity type")
    supplier_type: str = Field(..., description="Type of supplier")
    reliability_score: float = Field(..., ge=0.0, le=1.0, description="Supplier reliability")
    market_share: Optional[float] = Field(None, description="Market share percentage")
    geographic_reach: Optional[str] = Field(None, description="Geographic coverage")

class DependencyRelationship(BaseObject):
    """Dependency relationship between organization and resource"""
    source_id: str = Field(..., description="Organization ID")
    target_id: str = Field(..., description="Resource ID")
    relationship_type: str = Field(default="depends_on", description="Relationship type")
    dependency_strength: DependencyScore = Field(..., description="Dependency calculation")
    strategic_importance: Optional[str] = Field(None, description="Strategic importance assessment")
    mitigation_strategies: List[str] = Field(default_factory=list, description="Dependency mitigation strategies")

class SupplyRelationship(BaseObject):
    """Supply relationship between supplier and resource"""
    source_id: str = Field(..., description="Supplier ID")
    target_id: str = Field(..., description="Resource ID") 
    relationship_type: str = Field(default="supplies", description="Relationship type")
    supply_capacity: float = Field(..., ge=0.0, le=1.0, description="Supply capacity")
    reliability: float = Field(..., ge=0.0, le=1.0, description="Supply reliability")
    exclusivity: bool = Field(default=False, description="Exclusive supply arrangement")

class ResourceDependencyAnalysisResult(BaseObject):
    """Complete resource dependency analysis result"""
    organization_id: str = Field(..., description="Organization being analyzed")
    total_dependency_score: float = Field(..., ge=0.0, le=1.0, description="Overall dependency score")
    critical_dependencies: List[str] = Field(default_factory=list, description="Critical resource dependencies")
    risk_assessment: str = Field(..., description="Overall risk assessment")
    recommended_actions: List[str] = Field(default_factory=list, description="Recommended mitigation actions")
    analysis_metadata: Dict[str, Any] = Field(default_factory=dict, description="Analysis metadata")

class CrossTheoryIntegration(BaseModel):
    """Integration point between resource dependency and stakeholder theory"""
    stakeholder_id: str = Field(..., description="Stakeholder entity ID")
    resource_ids: List[str] = Field(..., description="Resources controlled by stakeholder")
    dependency_weight: float = Field(..., ge=0.0, le=1.0, description="Dependency weighting factor")
    salience_modifier: float = Field(..., ge=0.0, le=2.0, description="Modifier to stakeholder salience based on resource control")
    
    @validator('salience_modifier')
    def validate_modifier(cls, v):
        if not 0.0 <= v <= 2.0:
            raise ValueError('Salience modifier must be between 0.0 and 2.0')
        return v