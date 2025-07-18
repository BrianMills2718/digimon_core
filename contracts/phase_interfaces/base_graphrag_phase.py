# contracts/phase_interfaces/base_graphrag_phase.py
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class TheorySchema(Enum):
    """Available theory schemas for processing"""
    MASTER_CONCEPTS = "master_concepts"
    THREE_DIMENSIONAL = "three_dimensional"  
    ORM_METHODOLOGY = "orm_methodology"
    CUSTOM = "custom"

@dataclass
class TheoryConfig:
    """Configuration for theory-aware processing"""
    schema_type: TheorySchema
    concept_library_path: str
    validation_enabled: bool = True
    theory_meta_schema_path: Optional[str] = None
    custom_schema_config: Optional[Dict[str, Any]] = None

@dataclass 
class ProcessingRequest:
    """Immutable contract for phase processing requests"""
    documents: List[str]
    queries: List[str]
    workflow_id: str
    theory_config: TheoryConfig
    domain_description: Optional[str] = None
    existing_ontology: Optional[str] = None
    use_mock_apis: bool = False
    phase1_graph_data: Optional[Dict[str, Any]] = None
    phase2_enhanced_data: Optional[Dict[str, Any]] = None

@dataclass
class TheoryValidatedResult:
    """Results with theory validation metadata"""
    entities: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    theory_compliance: Dict[str, Any]
    concept_mapping: Dict[str, str]
    validation_score: float

@dataclass
class ProcessingResult:
    """Immutable contract for phase processing results"""
    phase_name: str
    status: str  # "success", "error", "partial"
    execution_time_seconds: float
    theory_validated_result: TheoryValidatedResult
    workflow_summary: Dict[str, Any]
    query_results: List[Dict[str, Any]]
    error_message: Optional[str] = None
    raw_phase_result: Optional[Dict[str, Any]] = None

class TheoryAwareGraphRAGPhase(ABC):
    """Immutable contract for theory-aware phase implementations"""
    
    @abstractmethod
    def get_name(self) -> str:
        """Return phase name"""
        pass
    
    @abstractmethod
    def get_version(self) -> str:
        """Return phase version"""
        pass
    
    @abstractmethod
    def get_supported_theory_schemas(self) -> List[TheorySchema]:
        """Return list of supported theory schemas"""
        pass
    
    @abstractmethod
    def validate_theory_config(self, config: TheoryConfig) -> List[str]:
        """Validate theory configuration, return errors"""
        pass
    
    @abstractmethod
    def execute(self, request: ProcessingRequest) -> ProcessingResult:
        """Execute phase with theory-aware processing"""
        pass
    
    @abstractmethod 
    def get_capabilities(self) -> Dict[str, Any]:
        """Return phase capabilities including theory support"""
        pass