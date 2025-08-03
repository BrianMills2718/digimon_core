"""
Adapter Utilities for Phase Adapters

Common utilities and helper functions used across all phase adapter implementations.
"""

import logging
import time
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class AdapterUtils:
    """Common utilities for phase adapter implementations"""
    
    @staticmethod
    def validate_document_paths(documents: List[str]) -> List[str]:
        """Validate document paths and return list of errors"""
        errors = []
        
        if not documents:
            errors.append("No documents provided")
            return errors
        
        for doc_path in documents:
            try:
                path = Path(doc_path)
                if not path.exists():
                    errors.append(f"Document not found: {doc_path}")
                elif not path.is_file():
                    errors.append(f"Path is not a file: {doc_path}")
                elif path.stat().st_size == 0:
                    errors.append(f"Document is empty: {doc_path}")
                elif path.stat().st_size > 50_000_000:  # 50MB limit
                    errors.append(f"Document too large (>50MB): {doc_path}")
            except Exception as e:
                errors.append(f"Error accessing document {doc_path}: {str(e)}")
        
        return errors
    
    @staticmethod
    def validate_queries(queries: List[str]) -> List[str]:
        """Validate query list and return list of errors"""
        errors = []
        
        if not queries:
            errors.append("No queries provided")
            return errors
        
        for i, query in enumerate(queries):
            if not query or not isinstance(query, str):
                errors.append(f"Query {i+1} must be a non-empty string")
            elif len(query.strip()) < 3:
                errors.append(f"Query {i+1} too short (minimum 3 characters)")
            elif len(query) > 1000:
                errors.append(f"Query {i+1} too long (maximum 1000 characters)")
        
        return errors
    
    @staticmethod
    def validate_workflow_id(workflow_id: str) -> Optional[str]:
        """Validate workflow ID and return error message if invalid"""
        if not workflow_id or not isinstance(workflow_id, str):
            return "Workflow ID must be a non-empty string"
        
        if len(workflow_id) < 3:
            return "Workflow ID too short (minimum 3 characters)"
        
        if len(workflow_id) > 100:
            return "Workflow ID too long (maximum 100 characters)"
        
        # Check for valid characters (alphanumeric, underscore, hyphen)
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', workflow_id):
            return "Workflow ID contains invalid characters (use alphanumeric, underscore, hyphen only)"
        
        return None
    
    @staticmethod
    def get_document_info(doc_path: str) -> Dict[str, Any]:
        """Get information about a document"""
        try:
            path = Path(doc_path)
            
            return {
                "path": str(path.absolute()),
                "name": path.name,
                "size_bytes": path.stat().st_size,
                "size_mb": round(path.stat().st_size / (1024 * 1024), 2),
                "extension": path.suffix.lower(),
                "exists": path.exists(),
                "is_file": path.is_file(),
                "is_readable": path.is_file() and path.stat().st_size > 0
            }
        except Exception as e:
            return {
                "path": doc_path,
                "error": str(e),
                "exists": False,
                "is_readable": False
            }
    
    @staticmethod
    def create_execution_context(phase_name: str, workflow_id: str) -> Dict[str, Any]:
        """Create execution context for phase processing"""
        return {
            "phase_name": phase_name,
            "workflow_id": workflow_id,
            "start_time": time.time(),
            "execution_id": f"{workflow_id}_{phase_name.lower().replace(' ', '_')}_{int(time.time())}",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    @staticmethod
    def calculate_execution_metrics(context: Dict[str, Any], 
                                   entities_count: int = 0,
                                   relationships_count: int = 0,
                                   documents_processed: int = 0,
                                   queries_answered: int = 0) -> Dict[str, Any]:
        """Calculate execution metrics from context"""
        execution_time = time.time() - context["start_time"]
        
        return {
            "execution_time_seconds": round(execution_time, 3),
            "entities_created": entities_count,
            "relationships_created": relationships_count,
            "documents_processed": documents_processed,
            "queries_answered": queries_answered,
            "throughput": {
                "entities_per_second": round(entities_count / execution_time, 2) if execution_time > 0 else 0,
                "relationships_per_second": round(relationships_count / execution_time, 2) if execution_time > 0 else 0,
                "documents_per_second": round(documents_processed / execution_time, 2) if execution_time > 0 else 0
            },
            "efficiency": {
                "entities_per_document": round(entities_count / documents_processed, 2) if documents_processed > 0 else 0,
                "relationships_per_document": round(relationships_count / documents_processed, 2) if documents_processed > 0 else 0,
                "relationships_per_entity": round(relationships_count / entities_count, 2) if entities_count > 0 else 0
            }
        }
    
    @staticmethod
    def sanitize_error_message(error: Exception) -> str:
        """Sanitize error message for safe logging and user display"""
        error_msg = str(error)
        
        # Remove potentially sensitive information
        import re
        # Remove file paths that might contain user info
        error_msg = re.sub(r'/[^/\s]+/[^/\s]+', '/.../', error_msg)
        # Remove potential API keys or tokens
        error_msg = re.sub(r'[a-zA-Z0-9]{20,}', '[REDACTED]', error_msg)
        
        return error_msg
    
    @staticmethod
    def get_supported_document_formats() -> Dict[str, Dict[str, Any]]:
        """Get information about supported document formats"""
        return {
            ".pdf": {
                "name": "PDF Document",
                "supported": True,
                "max_size_mb": 50,
                "description": "Portable Document Format files"
            },
            ".txt": {
                "name": "Text File",
                "supported": True,
                "max_size_mb": 10,
                "description": "Plain text files"
            },
            ".md": {
                "name": "Markdown File", 
                "supported": False,
                "max_size_mb": 10,
                "description": "Markdown format files (future support)"
            },
            ".docx": {
                "name": "Word Document",
                "supported": False,
                "max_size_mb": 50,
                "description": "Microsoft Word documents (future support)"
            }
        }
    
    @staticmethod
    def check_document_format_support(doc_path: str) -> Dict[str, Any]:
        """Check if document format is supported"""
        path = Path(doc_path)
        extension = path.suffix.lower()
        
        supported_formats = AdapterUtils.get_supported_document_formats()
        
        if extension not in supported_formats:
            return {
                "supported": False,
                "format": extension,
                "reason": f"Unsupported format: {extension}",
                "supported_formats": list(supported_formats.keys())
            }
        
        format_info = supported_formats[extension]
        if not format_info["supported"]:
            return {
                "supported": False,
                "format": extension,
                "reason": f"Format {extension} not yet implemented",
                "planned": True
            }
        
        # Check file size
        try:
            file_size_mb = path.stat().st_size / (1024 * 1024)
            if file_size_mb > format_info["max_size_mb"]:
                return {
                    "supported": False,
                    "format": extension,
                    "reason": f"File too large ({file_size_mb:.1f}MB > {format_info['max_size_mb']}MB limit)",
                    "file_size_mb": file_size_mb,
                    "limit_mb": format_info["max_size_mb"]
                }
        except Exception as e:
            return {
                "supported": False,
                "format": extension,
                "reason": f"Cannot access file: {str(e)}"
            }
        
        return {
            "supported": True,
            "format": extension,
            "format_info": format_info
        }
    
    @staticmethod
    def log_adapter_operation(adapter_name: str, operation: str, 
                             context: Dict[str, Any], 
                             result: Optional[Dict[str, Any]] = None,
                             error: Optional[Exception] = None):
        """Log adapter operation with structured information"""
        log_data = {
            "adapter": adapter_name,
            "operation": operation,
            "workflow_id": context.get("workflow_id", "unknown"),
            "execution_id": context.get("execution_id", "unknown")
        }
        
        if result:
            log_data["result"] = {
                "status": result.get("status", "unknown"),
                "entities": result.get("entities_created", 0),
                "relationships": result.get("relationships_created", 0),
                "execution_time": result.get("execution_time_seconds", 0)
            }
            
            logger.info(f"✅ {adapter_name} {operation} completed successfully", extra=log_data)
            
        elif error:
            log_data["error"] = AdapterUtils.sanitize_error_message(error)
            logger.error(f"❌ {adapter_name} {operation} failed", extra=log_data)
            
        else:
            logger.info(f"🔄 {adapter_name} {operation} started", extra=log_data)
    
    @staticmethod
    def merge_workflow_configs(base_config: Dict[str, Any], 
                              override_config: Dict[str, Any]) -> Dict[str, Any]:
        """Merge workflow configurations with override priority"""
        merged = base_config.copy()
        
        for key, value in override_config.items():
            if isinstance(value, dict) and key in merged and isinstance(merged[key], dict):
                merged[key] = AdapterUtils.merge_workflow_configs(merged[key], value)
            else:
                merged[key] = value
        
        return merged
    
    @staticmethod
    def validate_theory_config(config: Any) -> List[str]:
        """Validate theory configuration object"""
        errors = []
        
        if not config:
            errors.append("Theory configuration is required")
            return errors
        
        # Check required attributes
        required_attrs = ["schema_type", "concept_library_path"]
        for attr in required_attrs:
            if not hasattr(config, attr):
                errors.append(f"Theory config missing required attribute: {attr}")
                continue
            
            value = getattr(config, attr)
            if not value:
                errors.append(f"Theory config attribute {attr} cannot be empty")
        
        # Validate concept library path if provided
        if hasattr(config, "concept_library_path") and config.concept_library_path:
            try:
                path = Path(config.concept_library_path)
                if not path.exists():
                    errors.append(f"Concept library not found: {config.concept_library_path}")
                elif not path.is_file():
                    errors.append(f"Concept library path is not a file: {config.concept_library_path}")
            except Exception as e:
                errors.append(f"Error validating concept library path: {str(e)}")
        
        return errors