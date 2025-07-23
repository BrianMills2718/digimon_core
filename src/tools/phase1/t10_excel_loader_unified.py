"""
T10: Excel Document Loader - Unified Interface Implementation

Loads and parses Excel documents (.xlsx, .xls) with comprehensive data extraction and validation.
"""

from typing import Dict, Any, Optional, List, Union
import os
from pathlib import Path
import uuid
from datetime import datetime
import pandas as pd
import openpyxl
import logging
import json

from src.tools.base_tool import BaseTool, ToolRequest, ToolResult, ToolContract, ToolStatus, ToolErrorCode
from src.core.service_manager import ServiceManager
from src.core.advanced_data_models import Document, ObjectType, QualityTier

logger = logging.getLogger(__name__)


class T10ExcelLoaderUnified(BaseTool):
    """T10: Excel Document Loader with unified interface"""
    
    def __init__(self, service_manager: ServiceManager):
        """Initialize with service manager"""
        super().__init__(service_manager)
        self.tool_id = "T10"
        self.identity_service = service_manager.identity_service
        self.provenance_service = service_manager.provenance_service
        self.quality_service = service_manager.quality_service
        self._temp_files = []
    
    def get_contract(self) -> ToolContract:
        """Return tool contract specification"""
        return ToolContract(
            tool_id=self.tool_id,
            name="Excel Document Loader",
            description="Load and parse Excel documents with comprehensive data extraction and validation",
            category="document_processing",
            input_schema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to Excel file to load"
                    },
                    "workflow_id": {
                        "type": "string",
                        "description": "Optional workflow ID for tracking"
                    },
                    "parse_options": {
                        "type": "object",
                        "properties": {
                            "sheet_name": {"type": ["string", "integer", "null"], "default": None},
                            "header_row": {"type": "integer", "default": 0},
                            "include_formulas": {"type": "boolean", "default": False},
                            "include_formatting": {"type": "boolean", "default": False},
                            "max_rows": {"type": ["integer", "null"], "default": None},
                            "skip_empty_rows": {"type": "boolean", "default": True}
                        },
                        "default": {}
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
                            "excel_data": {"type": "object"},
                            "text_content": {"type": "string"},
                            "sheet_count": {"type": "integer"},
                            "total_rows": {"type": "integer"},
                            "total_columns": {"type": "integer"},
                            "confidence": {"type": "number"},
                            "quality_tier": {"type": "string"},
                            "created_at": {"type": "string"}
                        },
                        "required": ["document_id", "excel_data", "text_content", "confidence", "sheet_count"]
                    }
                },
                "required": ["document"]
            },
            dependencies=["identity_service", "provenance_service", "quality_service"],
            performance_requirements={
                "max_execution_time": 120.0,  # 2 minutes for large Excel files
                "max_memory_mb": 2048,        # 2GB for Excel processing
                "min_confidence": 0.8         # Minimum confidence threshold
            },
            error_conditions=[
                "FILE_NOT_FOUND",
                "INVALID_FILE_TYPE",
                "EXCEL_CORRUPTED",
                "EXCEL_PASSWORD_PROTECTED",
                "SHEET_NOT_FOUND",
                "MEMORY_LIMIT_EXCEEDED"
            ]
        )
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute Excel loading with unified interface"""
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
            parse_options = request.input_data.get("parse_options", {})
            
            # Set default parse options
            parse_options = {
                "sheet_name": parse_options.get("sheet_name", None),
                "header_row": parse_options.get("header_row", 0),
                "include_formulas": parse_options.get("include_formulas", False),
                "include_formatting": parse_options.get("include_formatting", False),
                "max_rows": parse_options.get("max_rows", None),
                "skip_empty_rows": parse_options.get("skip_empty_rows", True)
            }
            
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
                operation_type="load_excel_document",
                used={},
                parameters={
                    "file_path": str(file_path),
                    "workflow_id": workflow_id,
                    "parse_options": parse_options
                }
            )
            
            # Generate workflow ID if not provided
            if not workflow_id:
                workflow_id = f"wf_{uuid.uuid4().hex[:8]}"
            
            # Create document ID
            document_id = f"{workflow_id}_{file_path.stem}"
            document_ref = f"storage://document/{document_id}"
            
            # Parse Excel document
            parsing_result = self._parse_excel_document(file_path, parse_options)
            
            if parsing_result["status"] != "success":
                return self._create_error_result(
                    request,
                    parsing_result.get("error_code", "EXCEL_PARSE_ERROR"),
                    parsing_result["error"]
                )
            
            # Calculate confidence
            confidence = self._calculate_confidence(
                excel_data=parsing_result["excel_data"],
                total_rows=parsing_result["total_rows"],
                total_columns=parsing_result["total_columns"],
                file_size=file_path.stat().st_size,
                sheet_count=parsing_result["sheet_count"]
            )
            
            # Create document data
            document_data = {
                "document_id": document_id,
                "document_ref": document_ref,
                "file_path": str(file_path),
                "file_name": file_path.name,
                "file_size": file_path.stat().st_size,
                "excel_data": parsing_result["excel_data"],
                "text_content": parsing_result["text_content"],
                "sheet_count": parsing_result["sheet_count"],
                "total_rows": parsing_result["total_rows"],
                "total_columns": parsing_result["total_columns"],
                "confidence": confidence,
                "created_at": datetime.now().isoformat(),
                "tool_version": "1.0.0",
                "parse_options": parse_options,
                "sheet_names": parsing_result.get("sheet_names", [])
            }
            
            # Assess quality
            quality_result = self.quality_service.assess_confidence(
                object_ref=document_ref,
                base_confidence=confidence,
                factors={
                    "row_count": min(1.0, parsing_result["total_rows"] / 1000),
                    "column_count": min(1.0, parsing_result["total_columns"] / 50),
                    "file_size": min(1.0, file_path.stat().st_size / (10 * 1024 * 1024)),
                    "sheet_count": min(1.0, parsing_result["sheet_count"] / 10)
                },
                metadata={
                    "excel_type": "spreadsheet",
                    "parse_method": "pandas+openpyxl",
                    "has_formulas": parsing_result.get("has_formulas", False)
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
                    "sheet_count": parsing_result["sheet_count"],
                    "total_rows": parsing_result["total_rows"],
                    "total_columns": parsing_result["total_columns"],
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
                    "parse_method": "pandas+openpyxl",
                    "parse_options": parse_options
                },
                execution_time=execution_time,
                memory_used=memory_used
            )
            
        except Exception as e:
            logger.error(f"Unexpected error in {self.tool_id}: {e}", exc_info=True)
            return self._create_error_result(
                request,
                "UNEXPECTED_ERROR",
                f"Unexpected error during Excel loading: {str(e)}"
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
            allowed_extensions = ['.xlsx', '.xls', '.xlsm', '.xlsb']
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
    
    def _parse_excel_document(self, file_path: Path, parse_options: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Excel document using pandas and openpyxl"""
        try:
            # First, get basic Excel information using openpyxl
            try:
                workbook = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
                sheet_names = workbook.sheetnames
                sheet_count = len(sheet_names)
                workbook.close()
            except Exception as e:
                return {
                    "status": "error",
                    "error": f"Failed to read Excel file metadata: {str(e)}",
                    "error_code": "EXCEL_CORRUPTED"
                }
            
            # Determine which sheet(s) to read
            sheet_name = parse_options.get("sheet_name")
            if sheet_name is None:
                # Read all sheets
                sheets_to_read = None
            elif isinstance(sheet_name, str):
                if sheet_name not in sheet_names:
                    return {
                        "status": "error",
                        "error": f"Sheet '{sheet_name}' not found. Available sheets: {sheet_names}",
                        "error_code": "SHEET_NOT_FOUND"
                    }
                sheets_to_read = sheet_name
            elif isinstance(sheet_name, int):
                if sheet_name >= len(sheet_names):
                    return {
                        "status": "error",
                        "error": f"Sheet index {sheet_name} out of range. Available sheets: {len(sheet_names)}",
                        "error_code": "SHEET_NOT_FOUND"
                    }
                sheets_to_read = sheet_names[sheet_name]
            
            # Read Excel data using pandas
            try:
                if sheets_to_read is None:
                    # Read all sheets
                    excel_data_raw = pd.read_excel(
                        file_path,
                        sheet_name=None,  # Read all sheets
                        header=parse_options.get("header_row", 0),
                        nrows=parse_options.get("max_rows"),
                        engine='openpyxl'
                    )
                    excel_data = {}
                    for sheet, df in excel_data_raw.items():
                        excel_data[sheet] = self._process_dataframe(df, parse_options)
                else:
                    # Read specific sheet
                    df = pd.read_excel(
                        file_path,
                        sheet_name=sheets_to_read,
                        header=parse_options.get("header_row", 0),
                        nrows=parse_options.get("max_rows"),
                        engine='openpyxl'
                    )
                    excel_data = {sheets_to_read: self._process_dataframe(df, parse_options)}
                
            except Exception as e:
                if "password" in str(e).lower():
                    return {
                        "status": "error",
                        "error": f"Excel file is password protected: {str(e)}",
                        "error_code": "EXCEL_PASSWORD_PROTECTED"
                    }
                else:
                    return {
                        "status": "error",
                        "error": f"Failed to read Excel data: {str(e)}",
                        "error_code": "EXCEL_CORRUPTED"
                    }
            
            # Calculate statistics
            total_rows = 0
            total_columns = 0
            text_content_parts = []
            has_formulas = False
            
            for sheet_name, sheet_data in excel_data.items():
                data = sheet_data["data"]
                total_rows += sheet_data["row_count"]
                total_columns = max(total_columns, sheet_data["column_count"])
                
                # Extract text content
                text_content_parts.append(f"Sheet: {sheet_name}")
                if sheet_data["headers"]:
                    text_content_parts.append(" ".join(sheet_data["headers"]))
                
                # Add sample data for text content
                for row in data[:10]:  # First 10 rows for text content
                    row_text = " ".join([str(cell) for cell in row if pd.notna(cell)])
                    if row_text.strip():
                        text_content_parts.append(row_text)
            
            text_content = "\n".join(text_content_parts)
            
            return {
                "status": "success",
                "excel_data": excel_data,
                "text_content": text_content,
                "sheet_count": sheet_count,
                "sheet_names": sheet_names,
                "total_rows": total_rows,
                "total_columns": total_columns,
                "has_formulas": has_formulas
            }
            
        except Exception as e:
            logger.error(f"Failed to parse Excel document: {str(e)}")
            return {
                "status": "error",
                "error": f"Failed to parse Excel document: {str(e)}",
                "error_code": "EXCEL_PARSE_ERROR"
            }
    
    def _process_dataframe(self, df: pd.DataFrame, parse_options: Dict[str, Any]) -> Dict[str, Any]:
        """Process a pandas DataFrame and extract relevant information"""
        # Handle empty rows
        if parse_options.get("skip_empty_rows", True):
            df = df.dropna(how='all')
        
        # Get basic statistics
        row_count, column_count = df.shape
        headers = df.columns.tolist()
        
        # Convert to list of lists for JSON serialization
        # Handle NaN values
        data_list = []
        for _, row in df.iterrows():
            row_data = []
            for value in row:
                if pd.isna(value):
                    row_data.append(None)
                elif isinstance(value, (int, float, str, bool)):
                    row_data.append(value)
                else:
                    row_data.append(str(value))
            data_list.append(row_data)
        
        return {
            "data": data_list,
            "headers": headers,
            "row_count": row_count,
            "column_count": column_count,
            "data_types": df.dtypes.astype(str).to_dict()
        }
    
    def _calculate_confidence(self, excel_data: Dict[str, Any], total_rows: int, 
                            total_columns: int, file_size: int, sheet_count: int) -> float:
        """Calculate confidence score for Excel parsing"""
        base_confidence = 0.9  # High confidence for successful Excel parsing
        
        # Factors that affect confidence
        factors = []
        
        # Data volume factor
        if total_rows > 1000:
            factors.append(0.95)
        elif total_rows > 100:
            factors.append(0.9)
        elif total_rows > 10:
            factors.append(0.85)
        else:
            factors.append(0.8)
        
        # Column count factor
        if total_columns > 20:
            factors.append(0.95)
        elif total_columns > 5:
            factors.append(0.9)
        else:
            factors.append(0.85)
        
        # File size factor
        if file_size > 10 * 1024 * 1024:  # > 10MB
            factors.append(0.95)
        elif file_size > 1024 * 1024:  # > 1MB
            factors.append(0.9)
        else:
            factors.append(0.85)
        
        # Sheet count factor
        if sheet_count > 5:
            factors.append(0.95)
        elif sheet_count > 1:
            factors.append(0.9)
        else:
            factors.append(0.85)
        
        # Data quality factor - check for non-empty data
        has_meaningful_data = False
        for sheet_data in excel_data.values():
            if sheet_data["row_count"] > 0 and sheet_data["column_count"] > 0:
                has_meaningful_data = True
                break
        
        if has_meaningful_data:
            factors.append(0.95)
        else:
            factors.append(0.7)
        
        # Calculate average
        if factors:
            final_confidence = sum([base_confidence] + factors) / (len(factors) + 1)
        else:
            final_confidence = base_confidence
        
        # Ensure confidence is in valid range
        return max(0.1, min(1.0, final_confidence))
    
    def validate_input(self, input_data: Any) -> bool:
        """Validate input against tool contract with Excel-specific validation"""
        # Call base validation first
        if not super().validate_input(input_data):
            return False
        
        # Additional validation for Excel loader
        if isinstance(input_data, dict):
            file_path = input_data.get("file_path")
            if not file_path or not file_path.strip():
                return False
        
        return True
    
    def health_check(self) -> ToolResult:
        """Check tool health and readiness"""
        try:
            # Check if pandas and openpyxl are available
            import pandas as pd
            import openpyxl
            pandas_available = True
            openpyxl_available = True
            pandas_version = pd.__version__
            openpyxl_version = openpyxl.__version__
        except ImportError:
            pandas_available = False
            openpyxl_available = False
            pandas_version = 'not_installed'
            openpyxl_version = 'not_installed'
        
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
        
        healthy = pandas_available and openpyxl_available and services_healthy
        
        return ToolResult(
            tool_id=self.tool_id,
            status="success" if healthy else "error",
            data={
                "healthy": healthy,
                "pandas_available": pandas_available,
                "pandas_version": pandas_version,
                "openpyxl_available": openpyxl_available,
                "openpyxl_version": openpyxl_version,
                "services_healthy": services_healthy,
                "supported_formats": [".xlsx", ".xls", ".xlsm", ".xlsb"],
                "status": self.status.value
            },
            metadata={
                "timestamp": datetime.now().isoformat()
            },
            execution_time=0.0,
            memory_used=0
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