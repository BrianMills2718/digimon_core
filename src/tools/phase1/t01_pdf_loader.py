"""T01: PDF Document Loader - Minimal Implementation

Loads PDF documents and extracts clean text with confidence scoring.
This is the entry point for the vertical slice workflow.

Minimal implementation focusing on:
- Basic text extraction using pypdf
- Simple confidence scoring (0.9 for clean text)
- Document metadata preservation
- Integration with core services (T107, T110, T111)

Deferred features:
- OCR for scanned PDFs
- Table and image extraction
- Advanced quality assessment
- Multiple PDF processing engines
"""

from typing import Dict, List, Optional, Any
import os
from pathlib import Path
import uuid
from datetime import datetime
import pypdf
import sys

# Import core services
from src.core.identity_service import IdentityService
from src.core.provenance_service import ProvenanceService
from src.core.quality_service import QualityService


class PDFLoader:
    """T01: PDF Document Loader."""
    
    def __init__(
        self,
        identity_service: IdentityService,
        provenance_service: ProvenanceService,
        quality_service: QualityService
    ):
        self.identity_service = identity_service
        self.provenance_service = provenance_service
        self.quality_service = quality_service
        self.tool_id = "T01_PDF_LOADER"
    
    def load_pdf(
        self,
        file_path: str,
        document_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Load and extract text from a PDF document.
        
        Args:
            file_path: Path to PDF file
            document_id: Optional document ID (auto-generated if not provided)
            
        Returns:
            Document data with extracted text and metadata
        """
        # Start operation tracking
        operation_id = self.provenance_service.start_operation(
            tool_id=self.tool_id,
            operation_type="load_document",
            inputs=[],
            parameters={
                "file_path": file_path,
                "document_id": document_id
            }
        )
        
        try:
            # Input validation
            if not file_path:
                return self._complete_with_error(
                    operation_id,
                    "file_path is required"
                )
            
            file_path = Path(file_path)
            if not file_path.exists():
                return self._complete_with_error(
                    operation_id,
                    f"File not found: {file_path}"
                )
            
            # Accept both PDF and text files (for testing)
            allowed_extensions = ['.pdf', '.txt']
            if file_path.suffix.lower() not in allowed_extensions:
                return self._complete_with_error(
                    operation_id,
                    f"File type not supported: {file_path} (allowed: {allowed_extensions})"
                )
            
            # Generate document ID if not provided
            if not document_id:
                document_id = f"doc_{uuid.uuid4().hex[:8]}"
            
            # Create document reference
            document_ref = f"storage://document/{document_id}"
            
            # Extract text from file
            if file_path.suffix.lower() == '.pdf':
                extraction_result = self._extract_text_from_pdf(file_path)
            else:  # .txt file
                extraction_result = self._extract_text_from_txt(file_path)
            
            if extraction_result["status"] != "success":
                return self._complete_with_error(
                    operation_id,
                    extraction_result["error"]
                )
            
            # Calculate confidence based on extraction quality
            confidence = self._calculate_confidence(
                text=extraction_result["text"],
                page_count=extraction_result["page_count"],
                file_size=file_path.stat().st_size
            )
            
            # Create document data
            document_data = {
                "document_id": document_id,
                "document_ref": document_ref,
                "file_path": str(file_path),
                "file_name": file_path.name,
                "file_size": file_path.stat().st_size,
                "page_count": extraction_result["page_count"],
                "text": extraction_result["text"],
                "text_length": len(extraction_result["text"]),
                "confidence": confidence,
                "created_at": datetime.now().isoformat(),
                "tool_version": "1.0.0",
                "extraction_method": "pypdf"
            }
            
            # Assess quality
            quality_result = self.quality_service.assess_confidence(
                object_ref=document_ref,
                base_confidence=confidence,
                factors={
                    "text_length": min(1.0, len(extraction_result["text"]) / 10000),  # Longer text = higher confidence
                    "page_count": min(1.0, extraction_result["page_count"] / 10),      # More pages = higher confidence
                    "file_size": min(1.0, file_path.stat().st_size / (1024 * 1024))  # Larger files = higher confidence (up to 1MB)
                },
                metadata={
                    "extraction_method": "pypdf",
                    "file_type": "pdf"
                }
            )
            
            if quality_result["status"] != "success":
                # Continue with original confidence if quality assessment fails
                pass
            else:
                document_data["confidence"] = quality_result["confidence"]
                document_data["quality_tier"] = quality_result["quality_tier"]
            
            # Complete operation
            completion_result = self.provenance_service.complete_operation(
                operation_id=operation_id,
                outputs=[document_ref],
                success=True,
                metadata={
                    "page_count": extraction_result["page_count"],
                    "text_length": len(extraction_result["text"]),
                    "confidence": document_data["confidence"]
                }
            )
            
            return {
                "status": "success",
                "document": document_data,
                "operation_id": operation_id,
                "provenance": completion_result
            }
            
        except Exception as e:
            return self._complete_with_error(
                operation_id,
                f"Unexpected error during PDF loading: {str(e)}"
            )
    
    def _extract_text_from_pdf(self, file_path: Path) -> Dict[str, Any]:
        """Extract text from PDF using pypdf."""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                
                # Check if PDF is encrypted
                if pdf_reader.is_encrypted:
                    return {
                        "status": "error",
                        "error": "PDF is encrypted and cannot be read"
                    }
                
                # Extract text from all pages
                text_pages = []
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        text_pages.append(page_text)
                    except Exception as e:
                        # Continue with other pages if one fails
                        text_pages.append(f"[Error extracting page {page_num + 1}: {str(e)}]")
                
                # Combine all pages
                full_text = "\n\n".join(text_pages)
                
                # Basic text cleaning
                cleaned_text = self._clean_extracted_text(full_text)
                
                return {
                    "status": "success",
                    "text": cleaned_text,
                    "page_count": len(pdf_reader.pages),
                    "raw_text_length": len(full_text),
                    "cleaned_text_length": len(cleaned_text)
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to extract text from PDF: {str(e)}"
            }
    
    def _extract_text_from_txt(self, file_path: Path) -> Dict[str, Any]:
        """Extract text from text file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            
            # Basic text cleaning
            cleaned_text = self._clean_extracted_text(text)
            
            return {
                "status": "success",
                "text": cleaned_text,
                "page_count": 1,  # Text files are single "page"
                "raw_text_length": len(text),
                "cleaned_text_length": len(cleaned_text)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to extract text from file: {str(e)}"
            }
    
    def _clean_extracted_text(self, text: str) -> str:
        """Basic text cleaning for extracted PDF text."""
        if not text:
            return ""
        
        # Remove excessive whitespace
        import re
        
        # Replace multiple spaces with single space
        text = re.sub(r' +', ' ', text)
        
        # Replace multiple newlines with double newlines
        text = re.sub(r'\n\n+', '\n\n', text)
        
        # Remove leading/trailing whitespace from lines
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)
        
        # Remove empty lines at start and end
        text = text.strip()
        
        return text
    
    def _calculate_confidence(self, text: str, page_count: int, file_size: int) -> float:
        """Calculate confidence score for extracted text."""
        base_confidence = 0.9  # High confidence for pypdf extraction
        
        # Factors that affect confidence
        factors = []
        
        # Text length factor
        if len(text) > 1000:
            factors.append(0.95)  # Good amount of text
        elif len(text) > 100:
            factors.append(0.85)  # Reasonable amount
        else:
            factors.append(0.6)   # Very little text
        
        # Page count factor
        if page_count > 5:
            factors.append(0.95)  # Multi-page document
        elif page_count > 1:
            factors.append(0.9)   # Few pages
        else:
            factors.append(0.8)   # Single page
        
        # File size factor (larger files usually have more content)
        if file_size > 1024 * 1024:  # > 1MB
            factors.append(0.95)
        elif file_size > 100 * 1024:  # > 100KB
            factors.append(0.9)
        else:
            factors.append(0.8)
        
        # Text quality heuristics
        if text and len(text.split()) > 50:  # Has reasonable word count
            factors.append(0.9)
        else:
            factors.append(0.7)
        
        # Calculate weighted average
        if factors:
            final_confidence = (base_confidence + sum(factors)) / (len(factors) + 1)
        else:
            final_confidence = base_confidence
        
        # Ensure confidence is in valid range
        return max(0.1, min(1.0, final_confidence))
    
    def _complete_with_error(self, operation_id: str, error_message: str) -> Dict[str, Any]:
        """Complete operation with error."""
        self.provenance_service.complete_operation(
            operation_id=operation_id,
            outputs=[],
            success=False,
            error_message=error_message
        )
        
        return {
            "status": "error",
            "error": error_message,
            "operation_id": operation_id
        }
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported file formats."""
        return [".pdf"]
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get tool information."""
        return {
            "tool_id": self.tool_id,
            "name": "PDF Document Loader",
            "version": "1.0.0",
            "description": "Extracts text from PDF documents with confidence scoring",
            "supported_formats": self.get_supported_formats(),
            "dependencies": ["pypdf"],
            "output_type": "document"
        }