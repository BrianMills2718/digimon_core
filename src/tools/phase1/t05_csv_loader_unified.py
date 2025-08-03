"""
T05: CSV Data Loader - Unified Interface Implementation

Loads and processes structured data from CSV files using pandas.
"""

from typing import Dict, Any, Optional, List
import os
from pathlib import Path
import uuid
from datetime import datetime
import pandas as pd
import numpy as np
import logging

from src.tools.base_tool import BaseTool, ToolRequest, ToolResult, ToolContract, ToolStatus
from src.core.service_manager import ServiceManager

logger = logging.getLogger(__name__)


class T05CSVLoaderUnified(BaseTool):
    """T05: CSV Data Loader with unified interface"""
    
    def __init__(self, service_manager: ServiceManager):
        """Initialize with service manager"""
        super().__init__(service_manager)
        self.tool_id = "T05_CSV_LOADER"
        self.identity_service = service_manager.identity_service
        self.provenance_service = service_manager.provenance_service
        self.quality_service = service_manager.quality_service
        self._temp_files = []
    
    def get_contract(self) -> ToolContract:
        """Return tool contract specification"""
        return ToolContract(
            tool_id=self.tool_id,
            name="CSV Data Loader",
            description="Load and process structured data from CSV files",
            category="document_processing",
            input_schema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to CSV file to load"
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
                    "dataset": {
                        "type": "object",
                        "properties": {
                            "dataset_id": {"type": "string"},
                            "dataset_ref": {"type": "string"},
                            "file_path": {"type": "string"},
                            "file_name": {"type": "string"},
                            "file_size": {"type": "integer"},
                            "rows": {"type": "integer"},
                            "columns": {"type": "integer"},
                            "data": {"type": "array"},
                            "column_names": {"type": "array"},
                            "column_types": {"type": "object"},
                            "missing_values": {"type": "object"},
                            "data_quality": {"type": "object"},
                            "confidence": {"type": "number"},
                            "quality_tier": {"type": "string"},
                            "created_at": {"type": "string"}
                        },
                        "required": ["dataset_id", "rows", "columns", "data", "confidence"]
                    }
                },
                "required": ["dataset"]
            },
            dependencies=["identity_service", "provenance_service", "quality_service"],
            performance_requirements={
                "max_execution_time": 15.0,  # 15 seconds for large CSVs
                "max_memory_mb": 2048,       # 2GB for data processing
                "min_confidence": 0.8        # Minimum confidence threshold
            },
            error_conditions=[
                "FILE_NOT_FOUND",
                "INVALID_FILE_TYPE",
                "CSV_MALFORMED",
                "PARSING_FAILED",
                "ENCODING_ERROR",
                "MEMORY_LIMIT_EXCEEDED"
            ]
        )
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute CSV loading with unified interface"""
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
                operation_type="load_dataset",
                used={},
                parameters={
                    "file_path": str(file_path),
                    "workflow_id": workflow_id
                }
            )
            
            # Generate workflow ID if not provided
            if not workflow_id:
                workflow_id = f"wf_{uuid.uuid4().hex[:8]}"
            
            # Create dataset ID
            dataset_id = f"{workflow_id}_{file_path.stem}"
            dataset_ref = f"storage://dataset/{dataset_id}"
            
            # Load CSV data
            load_result = self._load_csv_data(file_path, request.parameters)
            
            if load_result["status"] != "success":
                return self._create_error_result(
                    request,
                    load_result.get("error_code", "EXTRACTION_FAILED"),
                    load_result["error"]
                )
            
            df = load_result["dataframe"]
            
            # Analyze data quality
            quality_metrics = self._analyze_data_quality(df)
            
            # Calculate confidence
            confidence = self._calculate_confidence(
                rows=len(df),
                columns=len(df.columns),
                completeness=quality_metrics["completeness"],
                file_size=file_path.stat().st_size
            )
            
            # Convert DataFrame to serializable format
            data_list = df.fillna("").to_dict(orient='records')
            
            # Create dataset data
            dataset_data = {
                "dataset_id": dataset_id,
                "dataset_ref": dataset_ref,
                "file_path": str(file_path),
                "file_name": file_path.name,
                "file_size": file_path.stat().st_size,
                "rows": len(df),
                "columns": len(df.columns),
                "data": data_list,
                "column_names": df.columns.tolist(),
                "column_types": self._infer_column_types(df),
                "missing_values": quality_metrics["missing_values"],
                "data_quality": quality_metrics,
                "confidence": confidence,
                "created_at": datetime.now().isoformat(),
                "tool_version": "1.0.0",
                "processing_params": request.parameters
            }
            
            # Assess quality with service
            quality_result = self.quality_service.assess_confidence(
                object_ref=dataset_ref,
                base_confidence=confidence,
                factors={
                    "row_count": min(1.0, len(df) / 1000),
                    "column_count": min(1.0, len(df.columns) / 20),
                    "completeness": quality_metrics["completeness"],
                    "consistency": quality_metrics.get("consistency", 0.9),
                    "file_size": min(1.0, file_path.stat().st_size / (10 * 1024 * 1024))
                },
                metadata={
                    "file_type": file_path.suffix.lower(),
                    "encoding": load_result.get("encoding", "utf-8")
                }
            )
            
            if quality_result["status"] == "success":
                dataset_data["confidence"] = quality_result["confidence"]
                dataset_data["quality_tier"] = quality_result["quality_tier"]
            
            # Complete provenance
            self.provenance_service.complete_operation(
                operation_id=operation_id,
                outputs=[dataset_ref],
                success=True,
                metadata={
                    "rows": len(df),
                    "columns": len(df.columns),
                    "missing_values_total": sum(quality_metrics["missing_values"].values()),
                    "confidence": dataset_data["confidence"]
                }
            )
            
            # Get execution metrics
            execution_time, memory_used = self._end_execution()
            
            # Create success result
            return ToolResult(
                tool_id=self.tool_id,
                status="success",
                data={
                    "dataset": dataset_data
                },
                metadata={
                    "operation_id": operation_id,
                    "workflow_id": workflow_id,
                    "encoding": load_result.get("encoding", "utf-8"),
                    "delimiter": load_result.get("delimiter", ",")
                },
                execution_time=execution_time,
                memory_used=memory_used
            )
            
        except Exception as e:
            logger.error(f"Unexpected error in {self.tool_id}: {e}", exc_info=True)
            return self._create_error_result(
                request,
                "UNEXPECTED_ERROR",
                f"Unexpected error during CSV loading: {str(e)}"
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
            allowed_extensions = ['.csv']
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
    
    def _load_csv_data(self, file_path: Path, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Load CSV data using pandas"""
        try:
            # Extract loading parameters
            delimiter = parameters.get("delimiter", ",")
            encoding = parameters.get("encoding", "utf-8")
            handle_missing = parameters.get("handle_missing", "keep")
            infer_types = parameters.get("infer_types", True)
            
            # Load CSV with pandas
            df = pd.read_csv(
                file_path,
                delimiter=delimiter,
                encoding=encoding,
                na_values=["", "NA", "N/A", "null", "NULL", "None", "NONE"] if handle_missing == "detect" else None,
                dtype=None if infer_types else str,
                low_memory=False
            )
            
            # Handle missing values based on parameter
            if handle_missing == "drop":
                df = df.dropna()
            elif handle_missing == "fill":
                df = df.fillna(parameters.get("fill_value", ""))
            
            return {
                "status": "success",
                "dataframe": df,
                "encoding": encoding,
                "delimiter": delimiter
            }
            
        except pd.errors.ParserError as e:
            error_message = str(e).lower()
            logger.error(f"CSV parsing error: {str(e)}")
            return {
                "status": "error",
                "error": f"Failed to parse CSV: {str(e)}",
                "error_code": "CSV_MALFORMED" if "tokenizing" in error_message else "PARSING_FAILED"
            }
        except UnicodeDecodeError as e:
            logger.error(f"Encoding error: {str(e)}")
            return {
                "status": "error",
                "error": f"Encoding error: {str(e)}",
                "error_code": "ENCODING_ERROR"
            }
        except Exception as e:
            logger.error(f"Failed to load CSV: {str(e)}")
            return {
                "status": "error",
                "error": f"Failed to load CSV: {str(e)}",
                "error_code": "EXTRACTION_FAILED"
            }
    
    def _infer_column_types(self, df: pd.DataFrame) -> Dict[str, str]:
        """Infer column data types"""
        type_mapping = {
            'int64': 'integer',
            'int32': 'integer',
            'int16': 'integer',
            'int8': 'integer',
            'float64': 'float',
            'float32': 'float',
            'float16': 'float',
            'object': 'string',
            'string': 'string',
            'bool': 'boolean',
            'datetime64': 'datetime',
            'datetime64[ns]': 'datetime',
            'timedelta64': 'timedelta',
            'category': 'category'
        }
        
        column_types = {}
        for col in df.columns:
            dtype_name = str(df[col].dtype)
            column_types[col] = type_mapping.get(dtype_name, 'unknown')
        
        return column_types
    
    def _analyze_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze data quality metrics"""
        # Count missing values per column
        missing_values = {}
        for col in df.columns:
            missing_count = df[col].isna().sum()
            if missing_count > 0:
                missing_values[col] = int(missing_count)
        
        # Calculate completeness
        total_cells = len(df) * len(df.columns)
        missing_cells = sum(missing_values.values())
        completeness = 1.0 - (missing_cells / total_cells) if total_cells > 0 else 0.0
        
        # Calculate other quality metrics
        quality_metrics = {
            "completeness": completeness,
            "missing_values": missing_values,
            "total_missing": missing_cells,
            "duplicate_rows": int(df.duplicated().sum()),
            "unique_values": {col: int(df[col].nunique()) for col in df.columns},
            "consistency": self._calculate_consistency(df)
        }
        
        return quality_metrics
    
    def _calculate_consistency(self, df: pd.DataFrame) -> float:
        """Calculate data consistency score"""
        # Simple consistency check based on data types
        consistency_scores = []
        
        for col in df.columns:
            try:
                # Check if numeric columns have consistent types
                if df[col].dtype in ['int64', 'float64']:
                    non_numeric = pd.to_numeric(df[col], errors='coerce').isna().sum()
                    score = 1.0 - (non_numeric / len(df)) if len(df) > 0 else 1.0
                    consistency_scores.append(score)
                else:
                    # For string columns, check for consistent patterns
                    consistency_scores.append(0.95)  # Default high consistency
            except:
                consistency_scores.append(0.9)
        
        return sum(consistency_scores) / len(consistency_scores) if consistency_scores else 0.9
    
    def _calculate_confidence(self, rows: int, columns: int, completeness: float, file_size: int) -> float:
        """Calculate confidence score for loaded data"""
        base_confidence = 0.9  # High confidence for structured data
        
        # Factors that affect confidence
        factors = []
        
        # Row count factor
        if rows > 100:
            factors.append(0.95)
        elif rows > 10:
            factors.append(0.90)
        else:
            factors.append(0.70)
        
        # Column count factor
        if 3 <= columns <= 50:
            factors.append(0.95)
        elif 1 <= columns <= 100:
            factors.append(0.90)
        else:
            factors.append(0.70)
        
        # Completeness factor
        factors.append(completeness)
        
        # File size factor
        if file_size > 1024 * 100:  # > 100KB
            factors.append(0.95)
        elif file_size > 1024:  # > 1KB
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
            # Check if pandas is available
            try:
                import pandas as pd
                pandas_available = True
                pandas_version = pd.__version__
            except ImportError:
                pandas_available = False
                pandas_version = None
            
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
            
            healthy = pandas_available and services_healthy
            
            return ToolResult(
                tool_id=self.tool_id,
                status="success" if healthy else "error",
                data={
                    "healthy": healthy,
                    "pandas_available": pandas_available,
                    "pandas_version": pandas_version,
                    "services_healthy": services_healthy,
                    "supported_formats": [".csv"],
                    "supported_delimiters": [",", ";", "\t", "|"],
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