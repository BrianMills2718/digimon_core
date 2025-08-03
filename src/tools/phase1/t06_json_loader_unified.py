"""
T06: JSON Document Loader - Unified Interface Implementation

Loads and processes JSON documents with schema validation and structure analysis.
"""

from typing import Dict, Any, Optional, List, Union
import os
from pathlib import Path
import uuid
from datetime import datetime
import json
import logging
from collections import deque

from src.tools.base_tool import BaseTool, ToolRequest, ToolResult, ToolContract, ToolStatus
from src.core.service_manager import ServiceManager

logger = logging.getLogger(__name__)


class T06JSONLoaderUnified(BaseTool):
    """T06: JSON Document Loader with unified interface"""
    
    def __init__(self, service_manager: ServiceManager):
        """Initialize with service manager"""
        super().__init__(service_manager)
        self.tool_id = "T06_JSON_LOADER"
        self.identity_service = service_manager.identity_service
        self.provenance_service = service_manager.provenance_service
        self.quality_service = service_manager.quality_service
        self._temp_files = []
    
    def get_contract(self) -> ToolContract:
        """Return tool contract specification"""
        return ToolContract(
            tool_id=self.tool_id,
            name="JSON Document Loader",
            description="Load and process JSON documents with schema validation",
            category="document_processing",
            input_schema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to JSON file to load"
                    },
                    "workflow_id": {
                        "type": "string",
                        "description": "Optional workflow ID for tracking"
                    }
                },
                "required": ["file_path"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "document": {
                        "type": "object",
                        "properties": {
                            "document_id": {"type": "string"},
                            "document_ref": {"type": "string"},
                            "file_path": {"type": "string"},
                            "file_name": {"type": "string"},
                            "file_size": {"type": "integer"},
                            "data": {"type": ["object", "array", "string", "number", "boolean", "null"]},
                            "schema": {"type": "object"},
                            "json_type": {"type": "string"},
                            "key_count": {"type": "integer"},
                            "array_length": {"type": "integer"},
                            "depth": {"type": "integer"},
                            "statistics": {"type": "object"},
                            "schema_valid": {"type": "boolean"},
                            "validation_details": {"type": "object"},
                            "confidence": {"type": "number"},
                            "quality_tier": {"type": "string"},
                            "created_at": {"type": "string"}
                        },
                        "required": ["document_id", "data", "schema", "confidence", "json_type"]
                    }
                },
                "required": ["document"]
            },
            dependencies=["identity_service", "provenance_service", "quality_service"],
            performance_requirements={
                "max_execution_time": 10.0,  # 10 seconds for large JSON
                "max_memory_mb": 1024,       # 1GB for JSON processing
                "min_confidence": 0.8        # Minimum confidence threshold
            },
            error_conditions=[
                "FILE_NOT_FOUND",
                "INVALID_FILE_TYPE",
                "JSON_MALFORMED",
                "PARSING_FAILED",
                "ENCODING_ERROR",
                "SCHEMA_VALIDATION_FAILED",
                "MEMORY_LIMIT_EXCEEDED"
            ]
        )
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute JSON loading with unified interface"""
        self._start_execution()
        
        try:
            # Validate input
            if not self.validate_input(request.input_data):
                return self._create_error_result(
                    request,
                    "INVALID_INPUT",
                    "Input validation failed. Required: file_path"
                )
            
            # Extract parameters
            file_path = request.input_data.get("file_path")
            workflow_id = request.input_data.get("workflow_id")
            
            # Validate file path
            validation_result = self._validate_file_path(file_path)
            if not validation_result["valid"]:
                return self._create_error_result(
                    request,
                    validation_result["error_code"],
                    validation_result["error_message"]
                )
            
            file_path = Path(file_path)
            
            # Start provenance tracking
            operation_id = self.provenance_service.start_operation(
                tool_id=self.tool_id,
                operation_type="load_document",
                used={},
                parameters={
                    "file_path": str(file_path),
                    "workflow_id": workflow_id
                }
            )
            
            # Generate workflow ID if not provided
            if not workflow_id:
                workflow_id = f"wf_{uuid.uuid4().hex[:8]}"
            
            # Create document ID
            document_id = f"{workflow_id}_{file_path.stem}"
            document_ref = f"storage://document/{document_id}"
            
            # Load JSON data
            load_result = self._load_json_data(file_path, request.parameters)
            
            if load_result["status"] != "success":
                return self._create_error_result(
                    request,
                    load_result.get("error_code", "EXTRACTION_FAILED"),
                    load_result["error"]
                )
            
            json_data = load_result["data"]
            
            # Analyze JSON structure
            structure_analysis = self._analyze_json_structure(json_data, request.parameters)
            
            # Infer or validate schema
            if request.parameters.get("validate_schema"):
                schema_result = self._validate_schema(json_data, request.parameters["validate_schema"])
                if schema_result["valid"] == False and request.parameters.get("strict_validation", False):
                    return self._create_error_result(
                        request,
                        "SCHEMA_VALIDATION_FAILED",
                        f"Schema validation failed: {schema_result['error']}"
                    )
                schema = request.parameters["validate_schema"]
                schema_valid = schema_result["valid"]
                validation_details = schema_result
            else:
                schema = self._infer_schema(json_data)
                schema_valid = None
                validation_details = None
            
            # Calculate confidence
            confidence = self._calculate_confidence(
                json_data=json_data,
                structure=structure_analysis,
                file_size=file_path.stat().st_size
            )
            
            # Create document data
            document_data = {
                "document_id": document_id,
                "document_ref": document_ref,
                "file_path": str(file_path),
                "file_name": file_path.name,
                "file_size": file_path.stat().st_size,
                "data": json_data,
                "schema": schema,
                "json_type": structure_analysis["json_type"],
                "confidence": confidence,
                "created_at": datetime.now().isoformat(),
                "tool_version": "1.0.0",
                **structure_analysis
            }
            
            # Add optional fields if present
            if schema_valid is not None:
                document_data["schema_valid"] = schema_valid
            if validation_details:
                document_data["validation_details"] = validation_details
            
            # Assess quality
            quality_result = self.quality_service.assess_confidence(
                object_ref=document_ref,
                base_confidence=confidence,
                factors={
                    "structure_complexity": min(1.0, structure_analysis.get("depth", 1) / 10),
                    "data_completeness": self._calculate_completeness(json_data),
                    "file_size": min(1.0, file_path.stat().st_size / (1024 * 1024))
                },
                metadata={
                    "file_type": file_path.suffix.lower(),
                    "json_type": structure_analysis["json_type"]
                }
            )
            
            if quality_result["status"] == "success":
                document_data["confidence"] = quality_result["confidence"]
                document_data["quality_tier"] = quality_result["quality_tier"]
            
            # Complete provenance
            self.provenance_service.complete_operation(
                operation_id=operation_id,
                outputs=[document_ref],
                success=True,
                metadata={
                    "json_type": structure_analysis["json_type"],
                    "structure_depth": structure_analysis.get("depth", 0),
                    "confidence": document_data["confidence"]
                }
            )
            
            # Get execution metrics
            execution_time, memory_used = self._end_execution()
            
            # Create success result
            return ToolResult(
                tool_id=self.tool_id,
                status="success",
                data={
                    "document": document_data
                },
                metadata={
                    "operation_id": operation_id,
                    "workflow_id": workflow_id,
                    "json_type": structure_analysis["json_type"]
                },
                execution_time=execution_time,
                memory_used=memory_used
            )
            
        except Exception as e:
            logger.error(f"Unexpected error in {self.tool_id}: {e}", exc_info=True)
            return self._create_error_result(
                request,
                "UNEXPECTED_ERROR",
                f"Unexpected error during JSON loading: {str(e)}"
            )
    
    def _validate_file_path(self, file_path: str) -> Dict[str, Any]:
        """Validate file path for security and existence"""
        if not file_path:
            return {
                "valid": False,
                "error_code": "INVALID_INPUT",
                "error_message": "File path cannot be empty"
            }
        
        try:
            path = Path(file_path)
            
            # Check if path exists
            if not path.exists():
                return {
                    "valid": False,
                    "error_code": "FILE_NOT_FOUND",
                    "error_message": f"File not found: {file_path}"
                }
            
            # Check if it's a file
            if not path.is_file():
                return {
                    "valid": False,
                    "error_code": "INVALID_INPUT",
                    "error_message": f"Path is not a file: {file_path}"
                }
            
            # Check extension
            allowed_extensions = ['.json']
            if path.suffix.lower() not in allowed_extensions:
                return {
                    "valid": False,
                    "error_code": "INVALID_FILE_TYPE",
                    "error_message": f"Invalid file extension. Allowed: {allowed_extensions}"
                }
            
            # Basic security check - prevent path traversal
            if ".." in str(path) or str(path).startswith("/etc"):
                return {
                    "valid": False,
                    "error_code": "VALIDATION_FAILED",
                    "error_message": "Invalid file path"
                }
            
            return {"valid": True}
            
        except Exception as e:
            return {
                "valid": False,
                "error_code": "VALIDATION_FAILED",
                "error_message": f"Path validation failed: {str(e)}"
            }
    
    def _load_json_data(self, file_path: Path, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Load JSON data from file"""
        try:
            encoding = parameters.get("encoding", "utf-8")
            
            with open(file_path, 'r', encoding=encoding) as f:
                json_data = json.load(f)
            
            return {
                "status": "success",
                "data": json_data
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {str(e)}")
            return {
                "status": "error",
                "error": f"Failed to parse JSON: {str(e)}",
                "error_code": "JSON_MALFORMED"
            }
        except UnicodeDecodeError as e:
            logger.error(f"Encoding error: {str(e)}")
            return {
                "status": "error",
                "error": f"Encoding error: {str(e)}",
                "error_code": "ENCODING_ERROR"
            }
        except Exception as e:
            logger.error(f"Failed to load JSON: {str(e)}")
            return {
                "status": "error",
                "error": f"Failed to load JSON: {str(e)}",
                "error_code": "EXTRACTION_FAILED"
            }
    
    def _analyze_json_structure(self, data: Any, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze JSON structure and statistics"""
        analysis = {
            "json_type": self._get_json_type(data)
        }
        
        if isinstance(data, dict):
            analysis["key_count"] = len(data)
        elif isinstance(data, list):
            analysis["array_length"] = len(data)
        
        # Calculate depth and statistics if requested
        if parameters.get("analyze_depth", True):
            depth_info = self._calculate_depth(data)
            analysis["depth"] = depth_info["depth"]
            
            if parameters.get("analyze_depth", False):  # Detailed analysis
                stats = self._calculate_statistics(data)
                analysis["statistics"] = stats
        
        return analysis
    
    def _get_json_type(self, data: Any) -> str:
        """Get the JSON data type"""
        if isinstance(data, dict):
            return "object"
        elif isinstance(data, list):
            return "array"
        elif isinstance(data, str):
            return "string"
        elif isinstance(data, (int, float)):
            return "number"
        elif isinstance(data, bool):
            return "boolean"
        elif data is None:
            return "null"
        else:
            return "unknown"
    
    def _calculate_depth(self, data: Any) -> Dict[str, int]:
        """Calculate maximum depth of JSON structure"""
        def get_depth(obj, current_depth=0):
            if isinstance(obj, dict):
                if not obj:
                    return current_depth
                return max(get_depth(v, current_depth + 1) for v in obj.values())
            elif isinstance(obj, list):
                if not obj:
                    return current_depth
                return max(get_depth(item, current_depth + 1) for item in obj)
            else:
                return current_depth
        
        return {"depth": get_depth(data)}
    
    def _calculate_statistics(self, data: Any) -> Dict[str, int]:
        """Calculate detailed statistics about JSON structure"""
        stats = {
            "total_keys": 0,
            "total_arrays": 0,
            "total_objects": 0,
            "total_strings": 0,
            "total_numbers": 0,
            "total_booleans": 0,
            "total_nulls": 0
        }
        
        def analyze(obj):
            if isinstance(obj, dict):
                stats["total_objects"] += 1
                stats["total_keys"] += len(obj)
                for value in obj.values():
                    analyze(value)
            elif isinstance(obj, list):
                stats["total_arrays"] += 1
                for item in obj:
                    analyze(item)
            elif isinstance(obj, str):
                stats["total_strings"] += 1
            elif isinstance(obj, (int, float)):
                stats["total_numbers"] += 1
            elif isinstance(obj, bool):
                stats["total_booleans"] += 1
            elif obj is None:
                stats["total_nulls"] += 1
        
        analyze(data)
        return stats
    
    def _infer_schema(self, data: Any) -> Dict[str, Any]:
        """Infer JSON schema from data"""
        def infer_type(obj):
            if isinstance(obj, dict):
                properties = {}
                required = []
                for key, value in obj.items():
                    properties[key] = infer_type(value)
                    required.append(key)
                return {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            elif isinstance(obj, list):
                if obj:
                    # Infer from first item (simplified)
                    return {
                        "type": "array",
                        "items": infer_type(obj[0])
                    }
                else:
                    return {"type": "array"}
            elif isinstance(obj, str):
                return {"type": "string"}
            elif isinstance(obj, bool):
                return {"type": "boolean"}
            elif isinstance(obj, int):
                return {"type": "integer"}
            elif isinstance(obj, float):
                return {"type": "number"}
            elif obj is None:
                return {"type": "null"}
            else:
                return {"type": "string"}  # Default
        
        return infer_type(data)
    
    def _validate_schema(self, data: Any, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Validate JSON data against schema"""
        try:
            import jsonschema
            
            jsonschema.validate(data, schema)
            return {
                "valid": True,
                "error": None
            }
        except jsonschema.ValidationError as e:
            return {
                "valid": False,
                "error": str(e),
                "path": list(e.path)
            }
        except Exception as e:
            return {
                "valid": False,
                "error": f"Schema validation error: {str(e)}"
            }
    
    def _calculate_completeness(self, data: Any) -> float:
        """Calculate data completeness score"""
        if isinstance(data, dict):
            if not data:
                return 0.0
            # Check for empty values
            non_empty = sum(1 for v in data.values() if v not in [None, "", [], {}])
            return non_empty / len(data)
        elif isinstance(data, list):
            if not data:
                return 0.0
            # Check for non-null items
            non_null = sum(1 for item in data if item is not None)
            return non_null / len(data)
        else:
            # Primitive types are complete if not null
            return 1.0 if data is not None else 0.0
    
    def _calculate_confidence(self, json_data: Any, structure: Dict[str, Any], file_size: int) -> float:
        """Calculate confidence score for loaded JSON"""
        base_confidence = 0.9  # High confidence for valid JSON
        
        # Factors that affect confidence
        factors = []
        
        # Structure complexity factor
        depth = structure.get("depth", 0)
        if depth > 0 and depth <= 10:
            factors.append(0.95)
        elif depth > 10:
            factors.append(0.90)
        else:
            factors.append(0.85)
        
        # Data size factor
        if isinstance(json_data, dict):
            size = structure.get("key_count", 0)
        elif isinstance(json_data, list):
            size = structure.get("array_length", 0)
        else:
            size = 1
        
        if size > 10:
            factors.append(0.95)
        elif size > 0:
            factors.append(0.90)
        else:
            factors.append(0.70)
        
        # File size factor
        if file_size > 1024 * 10:  # > 10KB
            factors.append(0.95)
        elif file_size > 100:  # > 100 bytes
            factors.append(0.90)
        else:
            factors.append(0.80)
        
        # Calculate weighted average
        if factors:
            final_confidence = (base_confidence + sum(factors)) / (len(factors) + 1)
        else:
            final_confidence = base_confidence
        
        # Ensure confidence is in valid range
        return max(0.1, min(1.0, final_confidence))
    
    def health_check(self) -> ToolResult:
        """Check tool health and readiness"""
        try:
            # Check if JSON module is available (should always be)
            json_available = True
            json_version = "builtin"
            
            # Check service dependencies
            services_healthy = True
            if self.services:
                try:
                    # Basic check that services exist
                    _ = self.identity_service
                    _ = self.provenance_service
                    _ = self.quality_service
                except:
                    services_healthy = False
            
            # Check optional jsonschema
            try:
                import jsonschema
                jsonschema_available = True
            except ImportError:
                jsonschema_available = False
            
            healthy = json_available and services_healthy
            
            return ToolResult(
                tool_id=self.tool_id,
                status="success" if healthy else "error",
                data={
                    "healthy": healthy,
                    "json_available": json_available,
                    "jsonschema_available": jsonschema_available,
                    "services_healthy": services_healthy,
                    "supported_formats": [".json"],
                    "supported_types": ["object", "array", "string", "number", "boolean", "null"],
                    "status": self.status.value
                },
                metadata={
                    "timestamp": datetime.now().isoformat()
                },
                execution_time=0.0,
                memory_used=0
            )
            
        except Exception as e:
            return ToolResult(
                tool_id=self.tool_id,
                status="error",
                data={"healthy": False},
                metadata={"error": str(e)},
                execution_time=0.0,
                memory_used=0,
                error_code="HEALTH_CHECK_FAILED",
                error_message=str(e)
            )
    
    def cleanup(self) -> bool:
        """Clean up any temporary files"""
        try:
            # Clean up temp files if any
            for temp_file in self._temp_files:
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                except:
                    pass
            
            self._temp_files = []
            self.status = ToolStatus.READY
            return True
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return False