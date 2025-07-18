# contracts/phase_interfaces/phase_registry.py
from typing import Dict, List, Any
from .base_graphrag_phase import TheoryAwareGraphRAGPhase, TheorySchema

class TheoryAwarePhaseRegistry:
    """Registry for theory-aware phases with capability discovery"""
    
    def __init__(self):
        self._phases: Dict[str, TheoryAwareGraphRAGPhase] = {}
        self._theory_compatibility: Dict[str, List[TheorySchema]] = {}
    
    def register_phase(self, phase: TheoryAwareGraphRAGPhase):
        """Register a theory-aware phase"""
        phase_name = phase.get_name()
        self._phases[phase_name] = phase
        self._theory_compatibility[phase_name] = phase.get_supported_theory_schemas()
    
    def get_phases_for_theory(self, theory_schema: TheorySchema) -> List[str]:
        """Get all phases that support a given theory schema"""
        compatible_phases = []
        for phase_name, schemas in self._theory_compatibility.items():
            if theory_schema in schemas:
                compatible_phases.append(phase_name)
        return compatible_phases
    
    def get_phase_capabilities(self, phase_name: str) -> Dict[str, Any]:
        """Get detailed capabilities of a phase including theory support"""
        if phase_name not in self._phases:
            return {}
        
        phase = self._phases[phase_name]
        capabilities = phase.get_capabilities()
        capabilities["supported_theory_schemas"] = [schema.value for schema in phase.get_supported_theory_schemas()]
        return capabilities
    
    def validate_phase_theory_compatibility(self, phase_name: str, theory_config) -> List[str]:
        """Validate if phase supports the theory configuration"""
        if phase_name not in self._phases:
            return [f"Phase not found: {phase_name}"]
        
        return self._phases[phase_name].validate_theory_config(theory_config)
    
    def get_all_phases(self) -> List[str]:
        """Get all registered phase names"""
        return list(self._phases.keys())
    
    def get_phase(self, phase_name: str) -> TheoryAwareGraphRAGPhase:
        """Get a phase instance by name"""
        return self._phases.get(phase_name)
    
    def get_theory_schemas_overview(self) -> Dict[str, List[str]]:
        """Get an overview of which theory schemas are supported by which phases"""
        schema_overview = {}
        for schema in TheorySchema:
            schema_overview[schema.value] = self.get_phases_for_theory(schema)
        return schema_overview
    
    def get_compatibility_matrix(self) -> Dict[str, Dict[str, bool]]:
        """Get a matrix showing phase-theory compatibility"""
        matrix = {}
        for phase_name in self._phases.keys():
            matrix[phase_name] = {}
            for schema in TheorySchema:
                matrix[phase_name][schema.value] = schema in self._theory_compatibility[phase_name]
        return matrix


# Global registry instance
_global_theory_registry = TheoryAwarePhaseRegistry()

def get_theory_registry() -> TheoryAwarePhaseRegistry:
    """Get the global theory-aware phase registry"""
    return _global_theory_registry

def register_theory_phase(phase: TheoryAwareGraphRAGPhase):
    """Register a phase with the global theory registry"""
    _global_theory_registry.register_phase(phase)

def discover_phases_for_theory(theory_schema: TheorySchema) -> List[str]:
    """Discover phases that support a given theory schema"""
    return _global_theory_registry.get_phases_for_theory(theory_schema)