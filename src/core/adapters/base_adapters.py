"""
Base Tool Adapters

Extracted from tool_adapters.py - Base classes and infrastructure for all tool adapters.
This module provides the fundamental adapter patterns and service management.
"""

from typing import Any, Dict, List, Optional
import uuid
from ..logging_config import get_logger
from ..config_manager import ConfigurationManager, get_config
from ..tool_protocol import Tool, ToolExecutionError, ToolValidationError, ToolValidationResult

logger = get_logger("core.adapters.base")


# Default concept library for entity processing
DEFAULT_CONCEPT_LIBRARY = {
    "PERSON": {
        "description": "Individual human beings",
        "patterns": ["person", "individual", "people", "human"],
        "relationships": ["works_at", "lives_in", "leads", "founded"]
    },
    "ORGANIZATION": {
        "description": "Companies, institutions, groups", 
        "patterns": ["company", "organization", "institution", "corp", "inc"],
        "relationships": ["located_in", "owns", "partners_with", "competes_with"]
    },
    "LOCATION": {
        "description": "Geographic places and locations",
        "patterns": ["city", "country", "state", "region", "place"],
        "relationships": ["contains", "borders", "near"]
    },
    "PRODUCT": {
        "description": "Products, services, technologies",
        "patterns": ["product", "service", "technology", "solution"],
        "relationships": ["produced_by", "used_by", "competes_with"]
    }
}


class SimplifiedToolAdapter(Tool):
    """Simplified adapter that eliminates boilerplate and handles common patterns"""
    
    def __init__(self, tool_class, tool_method, input_key, output_key, config_manager=None):
        self.tool_class = tool_class
        self.tool_method = tool_method
        self.input_key = input_key
        self.output_key = output_key
        self.config_manager = config_manager or get_config()
        self.logger = get_logger(f"core.{tool_class.__name__}")
        
        # Create services
        self.provenance_service = self._create_service("provenance")
        self.quality_service = self._create_service("quality")
        self.identity_service = self._create_service("identity")
        
        # Initialize the actual tool
        self._tool = tool_class(self.identity_service, self.provenance_service, self.quality_service)
        
    def _create_service(self, service_type):
        """Create a service with production error handling"""
        try:
            if service_type == "provenance":
                from ..provenance_service import ProvenanceService
                return ProvenanceService()
            elif service_type == "quality":
                from ..quality_service import QualityService
                return QualityService()
            elif service_type == "identity":
                from ..identity_service import IdentityService
                return IdentityService()
        except ImportError:
            if self.config_manager.is_production_mode():
                raise RuntimeError(f"Critical service {service_type} not available in production")
            else:
                logger.warning(f"Service {service_type} not available, using null service")
                return None
    
    def execute(self, input_data: Any, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute the tool with simplified protocol"""
        try:
            # Get the method from the tool
            method = getattr(self._tool, self.tool_method)
            
            # Handle different input patterns
            if self.input_key in input_data:
                items = input_data[self.input_key]
                if isinstance(items, list):
                    results = []
                    for item in items:
                        result = method(item)
                        if result.get("status") == "success":
                            results.extend(result.get(self.output_key, []))
                    return {self.output_key: results, "status": "success"}
                else:
                    return method(items)
            else:
                return method(input_data)
                
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def validate_input(self, input_data: Dict[str, Any]) -> ToolValidationResult:
        """Simplified validation"""
        errors = []
        if self.input_key not in input_data:
            errors.append(f"Missing required key: {self.input_key}")
        
        return ToolValidationResult(
            is_valid=len(errors) == 0,
            validation_errors=errors,
            method_signatures={},
            execution_test_results={},
            input_schema_validation={"valid": len(errors) == 0, "errors": errors},
            security_validation={"valid": True, "errors": []},
            performance_validation={"valid": True, "errors": []}
        )
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get tool information"""
        return {
            "name": self.tool_class.__name__,
            "version": "1.0.0",
            "description": f"Simplified adapter for {self.tool_class.__name__}",
            "contract_id": "unified",
            "capabilities": [self.tool_method]
        }


class BaseToolAdapter(Tool):
    """Base class for all tool adapters with centralized configuration
    
    Implements the Tool protocol to ensure consistent interface across all tools.
    Optimized to reduce complexity and boilerplate code.
    """
    
    def __init__(self, config_manager: ConfigurationManager = None):
        self.config_manager = config_manager or get_config()
        self.logger = get_logger(f"core.{self.__class__.__name__}")
        
        # Get configuration for this adapter (lazy loading)
        self._neo4j_config = None
        self._api_config = None
        self._entity_config = None
        self._text_config = None
        self._graph_config = None
        
        # Create required services with proper error handling
        self.provenance_service = self._create_provenance_service()
        self.quality_service = self._create_quality_service()
        self.identity_service = self._create_identity_service()
        
        # Add schema enforcement with production mode
        production_mode = self.config_manager.is_production_mode()
        try:
            from ..schema_enforcer import SchemaEnforcer
            self.schema_enforcer = SchemaEnforcer(production_mode=production_mode)
        except ImportError:
            logger.warning("SchemaEnforcer not available, using basic validation")
            self.schema_enforcer = None
    
    @property
    def neo4j_config(self):
        """Lazy-loaded Neo4j configuration"""
        if self._neo4j_config is None:
            self._neo4j_config = self.config_manager.get_neo4j_config()
        return self._neo4j_config
    
    @property
    def api_config(self):
        """Lazy-loaded API configuration"""
        if self._api_config is None:
            self._api_config = self.config_manager.get_api_config()
        return self._api_config
    
    @property
    def entity_config(self):
        """Lazy-loaded entity processing configuration"""
        if self._entity_config is None:
            self._entity_config = self.config_manager.get_entity_processing_config()
        return self._entity_config
    
    @property
    def text_config(self):
        """Lazy-loaded text processing configuration"""
        if self._text_config is None:
            self._text_config = self.config_manager.get_text_processing_config()
        return self._text_config
    
    @property
    def graph_config(self):
        """Lazy-loaded graph construction configuration"""
        if self._graph_config is None:
            self._graph_config = self.config_manager.get_graph_construction_config()
        return self._graph_config
        
    def _create_provenance_service(self):
        """Create provenance service with production error handling"""
        try:
            from ..provenance_service import ProvenanceService
            return ProvenanceService()
        except ImportError as e:
            if self.config_manager.is_production_mode():
                # In production, missing critical services are fatal
                self.logger.critical(f"Critical service ProvenanceService not available in production mode: {e}")
                raise RuntimeError(f"Production deployment error: ProvenanceService required but not available: {e}")
            else:
                # In development, create a null service that logs warnings
                self.logger.warning("ProvenanceService not available, using NullProvenanceService for development")
                return self._create_null_provenance_service()
    
    def _create_quality_service(self):
        """Create quality service with production error handling"""
        try:
            from ..quality_service import QualityService
            return QualityService()
        except ImportError as e:
            if self.config_manager.is_production_mode():
                self.logger.critical(f"Critical service QualityService not available in production mode: {e}")
                raise RuntimeError(f"Production deployment error: QualityService required but not available: {e}")
            else:
                self.logger.warning("QualityService not available, using NullQualityService for development")
                return self._create_null_quality_service()
    
    def _create_identity_service(self):
        """Create identity service with production error handling"""
        try:
            from ..identity_service import IdentityService
            return IdentityService()
        except ImportError as e:
            if self.config_manager.is_production_mode():
                self.logger.critical(f"Critical service IdentityService not available in production mode: {e}")
                raise RuntimeError(f"Production deployment error: IdentityService required but not available: {e}")
            else:
                self.logger.warning("IdentityService not available, using NullIdentityService for development")
                return self._create_null_identity_service()
    
    def _create_null_provenance_service(self):
        """Create a null provenance service for development"""
        class NullProvenanceService:
            def log_operation(self, *args, **kwargs):
                logger.debug("NullProvenanceService.log_operation called")
                return {"status": "success", "logged": False}
            
            def get_provenance(self, *args, **kwargs):
                logger.debug("NullProvenanceService.get_provenance called")
                return {"status": "success", "provenance": []}
        
        return NullProvenanceService()
    
    def _create_null_quality_service(self):
        """Create a null quality service for development"""
        class NullQualityService:
            def assess_quality(self, *args, **kwargs):
                logger.debug("NullQualityService.assess_quality called")
                return {"status": "success", "quality_score": 0.8}
            
            def get_quality_metrics(self, *args, **kwargs):
                logger.debug("NullQualityService.get_quality_metrics called")
                return {"status": "success", "metrics": {}}
        
        return NullQualityService()
    
    def _create_null_identity_service(self):
        """Create a null identity service for development"""
        class NullIdentityService:
            def create_mention(self, *args, **kwargs):
                logger.debug("NullIdentityService.create_mention called")
                return {"status": "success", "entity_id": str(uuid.uuid4()), "mention_id": str(uuid.uuid4())}
            
            def resolve_entity(self, *args, **kwargs):
                logger.debug("NullIdentityService.resolve_entity called")
                return {"status": "success", "entity_id": str(uuid.uuid4())}
        
        return NullIdentityService()
    
    def validate_input_comprehensive(self, input_data: Dict[str, Any]) -> ToolValidationResult:
        """Comprehensive input validation with theory awareness"""
        errors = []
        warnings = []
        
        # Basic type validation
        if not isinstance(input_data, dict):
            errors.append("Input data must be a dictionary")
            return ToolValidationResult(
                is_valid=False,
                validation_errors=errors,
                method_signatures={},
                execution_test_results={},
                input_schema_validation={"valid": False, "errors": errors},
                security_validation={"valid": True, "errors": []},
                performance_validation={"valid": True, "errors": []}
            )
        
        # Schema enforcement if available
        if self.schema_enforcer:
            try:
                schema_result = self.schema_enforcer.validate_input(input_data)
                if not schema_result.get("valid", True):
                    errors.extend(schema_result.get("errors", []))
            except Exception as e:
                warnings.append(f"Schema validation failed: {e}")
        
        # Security validation - check for potentially dangerous content
        security_validation = self._validate_security(input_data)
        
        # Performance validation - check for potentially expensive operations
        performance_validation = self._validate_performance(input_data)
        
        return ToolValidationResult(
            is_valid=len(errors) == 0,
            validation_errors=errors,
            validation_warnings=warnings,
            method_signatures={},
            execution_test_results={},
            input_schema_validation={"valid": len(errors) == 0, "errors": errors},
            security_validation=security_validation,
            performance_validation=performance_validation
        )
    
    def _validate_security(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input for security concerns"""
        errors = []
        warnings = []
        
        # Check for potential injection attacks
        for key, value in input_data.items():
            if isinstance(value, str):
                # Check for SQL injection patterns
                sql_patterns = ["drop table", "delete from", "insert into", "update set", "union select"]
                if any(pattern in value.lower() for pattern in sql_patterns):
                    errors.append(f"Potential SQL injection detected in field '{key}'")
                
                # Check for command injection patterns
                cmd_patterns = ["|", "&", ";", "`", "$()"]
                if any(pattern in value for pattern in cmd_patterns):
                    warnings.append(f"Potential command injection pattern in field '{key}'")
        
        return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}
    
    def _validate_performance(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input for performance concerns"""
        errors = []
        warnings = []
        
        # Check for potentially expensive operations
        for key, value in input_data.items():
            if isinstance(value, list) and len(value) > 1000:
                warnings.append(f"Large list detected in field '{key}' ({len(value)} items)")
            elif isinstance(value, str) and len(value) > 100000:
                warnings.append(f"Large string detected in field '{key}' ({len(value)} characters)")
            elif isinstance(value, dict) and len(value) > 100:
                warnings.append(f"Large dictionary detected in field '{key}' ({len(value)} keys)")
        
        return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}
    
    def execute(self, input_data: Any, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute the tool - must be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement execute method")
    
    def validate_input(self, input_data: Dict[str, Any]) -> ToolValidationResult:
        """Validate input - uses comprehensive validation by default"""
        return self.validate_input_comprehensive(input_data)


def create_simplified_adapter(tool_class, tool_method, input_key, output_key):
    """Factory function to create simplified adapters"""
    return SimplifiedToolAdapter(tool_class, tool_method, input_key, output_key)