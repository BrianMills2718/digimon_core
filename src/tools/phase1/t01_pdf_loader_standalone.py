"""
T01: PDF/Text Document Loader - Standalone Version
Can work without service_manager dependency
"""

from typing import Dict, Any, Optional
import os
from pathlib import Path
import uuid
from datetime import datetime
import logging

# PDF handling
try:
    import pypdf
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False
    logging.warning("pypdf not available - PDF loading will be limited")

# Import the fixed base tool
import sys
sys.path.append(str(Path(__file__).parent.parent))
from base_tool_fixed import BaseTool, ToolRequest, ToolResult, ToolContract, ToolStatus

logger = logging.getLogger(__name__)


class T01PDFLoaderStandalone(BaseTool):
    """T01: PDF/Text Document Loader - works standalone without service_manager"""
    
    def __init__(self, service_manager=None):
        """Initialize with optional service manager"""
        super().__init__(service_manager)
        self.tool_id = "T01_PDF_LOADER"
        self.supported_extensions = ['.pdf', '.txt']
        self._temp_files = []
    
    def get_contract(self) -> ToolContract:
        """Return tool contract specification"""
        return ToolContract(
            tool_id=self.tool_id,
            name="PDF/Text Document Loader",
            description="Load and extract text from PDF and text documents",
            category="document_processing",
            input_schema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to PDF or text file to load"
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
                            "file_path": {"type": "string"},
                            "file_name": {"type": "string"},
                            "file_size": {"type": "integer"},
                            "page_count": {"type": "integer"},
                            "text": {"type": "string"},
                            "text_length": {"type": "integer"},
                            "confidence": {"type": "number"},
                            "format": {"type": "string"}
                        }
                    }
                }
            },
            dependencies=[],  # No hard dependencies for standalone operation
            performance_requirements={
                "max_execution_time": 30.0,
                "max_memory_mb": 2048
            },
            error_conditions=[
                "FILE_NOT_FOUND",
                "INVALID_FILE_TYPE",
                "EXTRACTION_FAILED"
            ]
        )
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute document loading"""
        self._start_execution()
        
        try:
            # Extract parameters
            file_path = request.input_data.get("file_path")
            workflow_id = request.input_data.get("workflow_id", str(uuid.uuid4()))
            
            # Validate file exists
            if not file_path or not os.path.exists(file_path):
                return self._create_error_result(
                    "FILE_NOT_FOUND",
                    f"File not found: {file_path}"
                )
            
            # Get file info
            file_path_obj = Path(file_path)
            file_extension = file_path_obj.suffix.lower()
            file_size = os.path.getsize(file_path)
            
            # Check supported format
            if file_extension not in self.supported_extensions:
                return self._create_error_result(
                    "INVALID_FILE_TYPE",
                    f"Unsupported file type: {file_extension}. Supported: {self.supported_extensions}"
                )
            
            # Load document based on type
            if file_extension == '.pdf':
                result = self._load_pdf(file_path_obj)
            else:  # .txt
                result = self._load_text(file_path_obj)
            
            if not result['success']:
                return self._create_error_result(
                    "EXTRACTION_FAILED",
                    result.get('error', 'Failed to extract text')
                )
            
            # Create document structure
            document = {
                "document_id": f"doc_{workflow_id}_{file_path_obj.stem}",
                "file_path": str(file_path_obj),
                "file_name": file_path_obj.name,
                "file_size": file_size,
                "page_count": result.get('page_count', 1),
                "text": result['text'],
                "text_length": len(result['text']),
                "confidence": self._calculate_confidence(result),
                "format": file_extension[1:],  # Remove the dot
                "created_at": datetime.now().isoformat()
            }
            
            # Log with provenance service (or mock)
            operation_id = self.provenance_service.start_operation(
                tool_id=self.tool_id,
                operation_type="load_document",
                inputs=[str(file_path)],
                parameters={"workflow_id": workflow_id}
            )
            
            self.provenance_service.complete_operation(
                operation_id=operation_id,
                outputs=[document["document_id"]],
                success=True,
                metadata={"text_length": document["text_length"]}
            )
            
            return self._create_success_result(
                data={"document": document},
                metadata={
                    "operation_id": operation_id,
                    "workflow_id": workflow_id,
                    "extraction_method": "pypdf" if file_extension == '.pdf' else "native",
                    "standalone_mode": getattr(self, 'is_standalone', False)
                }
            )
            
        except Exception as e:
            logger.error(f"Unexpected error in PDF loader: {e}", exc_info=True)
            return self._create_error_result(
                "UNEXPECTED_ERROR",
                f"Unexpected error: {str(e)}"
            )
    
    def _load_pdf(self, file_path: Path) -> Dict[str, Any]:
        """Load PDF file and extract text"""
        if not PYPDF_AVAILABLE:
            # Fallback: try to read as text
            logger.warning("pypdf not available, attempting text extraction fallback")
            return {
                "success": False,
                "error": "PDF library not available. Install pypdf: pip install pypdf"
            }
        
        try:
            text_content = []
            page_count = 0
            
            with open(file_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                page_count = len(pdf_reader.pages)
                
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        text = page.extract_text()
                        if text:
                            text_content.append(text)
                    except Exception as e:
                        logger.warning(f"Failed to extract page {page_num}: {e}")
                        text_content.append(f"[Page {page_num + 1} extraction failed]")
            
            return {
                "success": True,
                "text": "\n\n".join(text_content),
                "page_count": page_count
            }
            
        except Exception as e:
            logger.error(f"PDF extraction failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _load_text(self, file_path: Path) -> Dict[str, Any]:
        """Load text file"""
        try:
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'cp1252', 'ascii']
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as file:
                        text = file.read()
                        return {
                            "success": True,
                            "text": text,
                            "page_count": 1,
                            "encoding": encoding
                        }
                except UnicodeDecodeError:
                    continue
            
            # If all encodings fail
            return {
                "success": False,
                "error": "Failed to decode file with common encodings"
            }
            
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _calculate_confidence(self, extraction_result: Dict[str, Any]) -> float:
        """Calculate confidence score for extraction"""
        base_confidence = 0.9 if extraction_result['success'] else 0.0
        
        # Adjust based on content quality
        if extraction_result.get('text'):
            text_length = len(extraction_result['text'])
            if text_length < 100:
                base_confidence *= 0.7  # Very short document
            elif text_length < 500:
                base_confidence *= 0.85  # Short document
            
            # Check for extraction artifacts
            if '[Page' in extraction_result['text'] and 'extraction failed]' in extraction_result['text']:
                base_confidence *= 0.8  # Some pages failed
        
        return min(1.0, base_confidence)
    
    def cleanup(self) -> bool:
        """Clean up any temporary files"""
        for temp_file in self._temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception as e:
                logger.warning(f"Failed to clean up temp file {temp_file}: {e}")
        
        self._temp_files = []
        return super().cleanup()


# Convenience function for testing
def test_standalone_loader():
    """Test the standalone loader"""
    loader = T01PDFLoaderStandalone()  # No service_manager needed!
    print(f"✅ Tool initialized in standalone mode: {loader.tool_id}")
    
    # Test with a text file
    test_file = "/home/brian/projects/Digimons/experiments/lit_review/data/test_texts/carter_anapolis.txt"
    
    if os.path.exists(test_file):
        request = ToolRequest(
            tool_id="T01",
            operation="load",
            input_data={"file_path": test_file}
        )
        
        result = loader.execute(request)
        print(f"Status: {result.status}")
        if result.status == "success":
            doc = result.data["document"]
            print(f"Loaded: {doc['file_name']}")
            print(f"Size: {doc['file_size']} bytes")
            print(f"Text length: {doc['text_length']} characters")
            print(f"Confidence: {doc['confidence']:.2f}")
        else:
            print(f"Error: {result.error_message}")
    else:
        print(f"Test file not found: {test_file}")
    
    return loader


if __name__ == "__main__":
    test_standalone_loader()