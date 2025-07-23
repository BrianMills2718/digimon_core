"""
T14 Email Parser Unified Tool

Processes email files (.eml, .msg) using email and msg_parser modules for real email parsing.
Implements unified BaseTool interface with comprehensive email processing capabilities.
"""

import email
import email.header
import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import chardet
import re
import base64
import quopri

try:
    import extract_msg  # For .msg file support
    MSG_SUPPORT = True
except ImportError:
    MSG_SUPPORT = False

from src.tools.base_tool import BaseTool, ToolRequest, ToolResult, ToolErrorCode
from src.core.service_manager import ServiceManager

class T14EmailParserUnified(BaseTool):
    """
    Email Parser tool for processing email files (.eml, .msg) with real email parsing.
    
    Features:
    - Real email parsing using email module
    - Header extraction and decoding
    - Attachment processing and extraction
    - Multiple encoding support
    - .msg file support (if extract_msg available)
    - HTML/text content extraction
    - Metadata analysis
    """
    
    def __init__(self, service_manager: ServiceManager):
        super().__init__(service_manager)
        self.tool_id = "T14"
        self.name = "Email Parser"
        self.category = "document_processing"
        self.service_manager = service_manager  # Store for use in methods
        
        # Email processing stats
        self.attachments_extracted = 0
        self.headers_decoded = 0
        self.encoding_detections = 0

    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute email parsing with real email processing"""
        self._start_execution()
        
        try:
            # Validate input
            validation_result = self._validate_input(request.input_data)
            if not validation_result["valid"]:
                execution_time, memory_used = self._end_execution()
                return ToolResult(
                    tool_id=self.tool_id,
                    status="error",
                    data={},
                    error_message=validation_result["error"],
                    error_code=ToolErrorCode.INVALID_INPUT,
                    execution_time=execution_time,
                    memory_used=memory_used
                )
            
            email_path = request.input_data.get("email_path")
            extract_attachments = request.input_data.get("extract_attachments", True)
            output_dir = request.input_data.get("output_dir", None)
            
            # Check file exists
            if not os.path.exists(email_path):
                execution_time, memory_used = self._end_execution()
                return ToolResult(
                    tool_id=self.tool_id,
                    status="error",
                    data={},
                    error_message=f"Email file not found: {email_path}",
                    error_code=ToolErrorCode.FILE_NOT_FOUND,
                    execution_time=execution_time,
                    memory_used=memory_used
                )
            
            # Process email based on file type
            file_ext = Path(email_path).suffix.lower()
            
            if file_ext == '.msg':
                if not MSG_SUPPORT:
                    execution_time, memory_used = self._end_execution()
                    return ToolResult(
                        tool_id=self.tool_id,
                        status="error",
                        data={},
                        error_message="MSG file support requires extract-msg package",
                        error_code=ToolErrorCode.PROCESSING_ERROR,
                        execution_time=execution_time,
                        memory_used=memory_used
                    )
                result_data = self._process_msg_file(email_path, extract_attachments, output_dir)
            else:
                # Handle .eml and other text-based email formats
                result_data = self._process_eml_file(email_path, extract_attachments, output_dir)
            
            # Create mentions for processed data
            self._create_service_mentions(result_data)
            
            # Calculate confidence based on content quality
            confidence = self._calculate_confidence(result_data)
            
            execution_time, memory_used = self._end_execution()
            
            return ToolResult(
                tool_id=self.tool_id,
                status="success",
                data={
                    "email_data": result_data,
                    "stats": {
                        "attachments_extracted": self.attachments_extracted,
                        "headers_decoded": self.headers_decoded,
                        "encoding_detections": self.encoding_detections
                    },
                    "confidence": confidence
                },
                execution_time=execution_time,
                memory_used=memory_used
            )
            
        except Exception as e:
            execution_time, memory_used = self._end_execution()
            logging.error(f"T14 Email Parser error: {str(e)}")
            return ToolResult(
                tool_id=self.tool_id,
                status="error",
                data={},
                error_message=f"Email parsing failed: {str(e)}",
                error_code=ToolErrorCode.PROCESSING_ERROR,
                execution_time=execution_time,
                memory_used=memory_used
            )

    def _process_eml_file(self, email_path: str, extract_attachments: bool, output_dir: Optional[str]) -> Dict[str, Any]:
        """Process .eml file using email module"""
        
        # Read email file with encoding detection
        with open(email_path, 'rb') as f:
            raw_email = f.read()
        
        # Detect encoding
        encoding_result = chardet.detect(raw_email)
        encoding = encoding_result.get('encoding', 'utf-8')
        self.encoding_detections += 1
        
        # Parse email
        try:
            email_str = raw_email.decode(encoding, errors='replace')
        except:
            email_str = raw_email.decode('utf-8', errors='replace')
            
        msg = email.message_from_string(email_str)
        
        # Extract headers
        headers = self._extract_headers(msg)
        
        # Extract body content
        body_data = self._extract_body_content(msg)
        
        # Extract attachments (always extract metadata, conditionally save files)
        attachments = self._extract_attachments(msg, output_dir if extract_attachments else None)
        
        # Extract metadata
        metadata = self._extract_email_metadata(msg, email_path)
        
        return {
            "headers": headers,
            "body": body_data,
            "attachments": attachments,
            "metadata": metadata,
            "message_id": headers.get("message_id"),
            "thread_id": headers.get("in_reply_to"),
            "file_path": email_path,
            "file_type": "eml"
        }

    def _process_msg_file(self, email_path: str, extract_attachments: bool, output_dir: Optional[str]) -> Dict[str, Any]:
        """Process .msg file using extract_msg module"""
        
        msg = extract_msg.openMsg(email_path)
        
        try:
            # Extract headers from MSG
            headers = {
                "from": getattr(msg, 'sender', ''),
                "to": getattr(msg, 'to', ''),
                "cc": getattr(msg, 'cc', ''),
                "bcc": getattr(msg, 'bcc', ''),
                "subject": getattr(msg, 'subject', ''),
                "date": getattr(msg, 'date', ''),
                "message_id": getattr(msg, 'messageId', ''),
                "in_reply_to": getattr(msg, 'inReplyTo', ''),
                "reply_to": getattr(msg, 'replyTo', '')
            }
            self.headers_decoded += len([v for v in headers.values() if v])
            
            # Extract body content
            body_data = {
                "plain_text": getattr(msg, 'body', ''),
                "html_content": getattr(msg, 'htmlBody', ''),
                "rtf_content": getattr(msg, 'rtfBody', '') if hasattr(msg, 'rtfBody') else ''
            }
            
            # Extract attachments from MSG (always extract metadata, conditionally save files)
            attachments = []
            if hasattr(msg, 'attachments'):
                for attachment in msg.attachments:
                    att_data = {
                        "filename": getattr(attachment, 'longFilename') or getattr(attachment, 'shortFilename', 'unknown'),
                        "size": len(getattr(attachment, 'data', b'')),
                        "content_type": "application/octet-stream"
                    }
                    
                    if extract_attachments and output_dir and hasattr(attachment, 'save'):
                        os.makedirs(output_dir, exist_ok=True)
                        save_path = os.path.join(output_dir, att_data["filename"])
                        attachment.save(customPath=save_path)
                        att_data["saved_path"] = save_path
                        self.attachments_extracted += 1
                    
                    attachments.append(att_data)
            
            # Extract metadata
            metadata = {
                "creation_time": getattr(msg, 'creationTime', None),
                "last_modification_time": getattr(msg, 'lastModificationTime', None),
                "message_class": getattr(msg, 'messageClass', ''),
                "importance": getattr(msg, 'importance', 'normal'),
                "priority": getattr(msg, 'priority', 'normal'),
                "sensitivity": getattr(msg, 'sensitivity', 'none'),
                "file_size": os.path.getsize(email_path),
                "encoding_detected": "MSG format"
            }
            
            return {
                "headers": headers,
                "body": body_data,
                "attachments": attachments,
                "metadata": metadata,
                "message_id": headers.get("message_id"),
                "thread_id": headers.get("in_reply_to"),
                "file_path": email_path,
                "file_type": "msg"
            }
            
        finally:
            msg.close()

    def _extract_headers(self, msg: email.message.Message) -> Dict[str, str]:
        """Extract and decode email headers"""
        headers = {}
        
        header_fields = [
            'from', 'to', 'cc', 'bcc', 'subject', 'date', 'message-id',
            'in-reply-to', 'references', 'reply-to', 'return-path',
            'x-mailer', 'x-originating-ip', 'received', 'content-type'
        ]
        
        for field in header_fields:
            value = msg.get(field, '')
            if value:
                # Decode header if needed
                decoded_value = self._decode_header(value)
                headers[field.replace('-', '_')] = decoded_value
                self.headers_decoded += 1
        
        return headers

    def _decode_header(self, header_value: str) -> str:
        """Decode RFC 2047 encoded headers"""
        try:
            decoded_parts = email.header.decode_header(header_value)
            decoded_string = ""
            
            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    if encoding:
                        decoded_string += part.decode(encoding, errors='replace')
                    else:
                        # Try to detect encoding
                        detected = chardet.detect(part)
                        enc = detected.get('encoding', 'utf-8')
                        decoded_string += part.decode(enc, errors='replace')
                else:
                    decoded_string += part
            
            return decoded_string.strip()
        except:
            return header_value

    def _extract_body_content(self, msg: email.message.Message) -> Dict[str, str]:
        """Extract body content from email message"""
        body_data = {
            "plain_text": "",
            "html_content": "",
            "attachments_found": 0
        }
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition", ""))
                
                # Skip attachments in body extraction
                if "attachment" in content_disposition:
                    body_data["attachments_found"] += 1
                    continue
                
                if content_type == "text/plain":
                    payload = self._get_decoded_payload(part)
                    body_data["plain_text"] += payload + "\n"
                elif content_type == "text/html":
                    payload = self._get_decoded_payload(part)
                    body_data["html_content"] += payload + "\n"
        else:
            # Single part message
            content_type = msg.get_content_type()
            payload = self._get_decoded_payload(msg)
            
            if content_type == "text/plain":
                body_data["plain_text"] = payload
            elif content_type == "text/html":
                body_data["html_content"] = payload
            else:
                body_data["plain_text"] = payload
        
        return body_data

    def _get_decoded_payload(self, part: email.message.Message) -> str:
        """Get decoded payload from email part"""
        try:
            payload = part.get_payload(decode=True)
            if isinstance(payload, bytes):
                # Try to get charset from content type
                charset = part.get_content_charset()
                if charset:
                    return payload.decode(charset, errors='replace')
                else:
                    # Detect encoding
                    detected = chardet.detect(payload)
                    encoding = detected.get('encoding', 'utf-8')
                    self.encoding_detections += 1
                    return payload.decode(encoding, errors='replace')
            else:
                return str(payload)
        except:
            # Fallback to string payload
            return str(part.get_payload())

    def _extract_attachments(self, msg: email.message.Message, output_dir: Optional[str]) -> List[Dict[str, Any]]:
        """Extract attachments from email message"""
        attachments = []
        
        for part in msg.walk():
            content_disposition = str(part.get("Content-Disposition", ""))
            
            if "attachment" in content_disposition:
                filename = part.get_filename()
                if filename:
                    # Decode filename if needed
                    filename = self._decode_header(filename)
                    
                    # Get attachment data
                    payload = part.get_payload(decode=True)
                    
                    att_data = {
                        "filename": filename,
                        "size": len(payload) if payload else 0,
                        "content_type": part.get_content_type(),
                        "content_id": part.get("Content-ID", ""),
                        "encoding": part.get("Content-Transfer-Encoding", "")
                    }
                    
                    # Save attachment if output directory specified
                    if output_dir and payload:
                        os.makedirs(output_dir, exist_ok=True)
                        safe_filename = re.sub(r'[^\w\-_\.]', '_', filename)
                        save_path = os.path.join(output_dir, safe_filename)
                        
                        with open(save_path, 'wb') as f:
                            f.write(payload)
                        
                        att_data["saved_path"] = save_path
                        self.attachments_extracted += 1
                    
                    attachments.append(att_data)
        
        return attachments

    def _extract_email_metadata(self, msg: email.message.Message, email_path: str) -> Dict[str, Any]:
        """Extract metadata from email"""
        return {
            "file_size": os.path.getsize(email_path),
            "creation_time": datetime.fromtimestamp(os.path.getctime(email_path)).isoformat(),
            "modification_time": datetime.fromtimestamp(os.path.getmtime(email_path)).isoformat(),
            "is_multipart": msg.is_multipart(),
            "content_type": msg.get_content_type(),
            "encoding_detected": "auto-detected",
            "has_attachments": len([p for p in msg.walk() if p.get_filename()]) > 0,
            "part_count": len(list(msg.walk())) if msg.is_multipart() else 1
        }

    def _calculate_confidence(self, result_data: Dict[str, Any]) -> float:
        """Calculate confidence score based on parsing success"""
        confidence = 0.5  # Base confidence
        
        # Increase confidence based on successful extractions
        if result_data.get("headers", {}).get("subject"):
            confidence += 0.15
        
        if result_data.get("headers", {}).get("from"):
            confidence += 0.1
        
        if result_data.get("body", {}).get("plain_text") or result_data.get("body", {}).get("html_content"):
            confidence += 0.15
        
        if result_data.get("attachments"):
            confidence += 0.1
        
        # Bonus for complete metadata
        if result_data.get("metadata", {}).get("file_size", 0) > 0:
            confidence += 0.05
        
        return min(confidence, 1.0)

    def _create_service_mentions(self, result_data: Dict[str, Any]):
        """Create service mentions for processed email data"""
        try:
            # Create mention for sender
            sender = result_data.get("headers", {}).get("from", "")
            if sender and hasattr(self.service_manager, 'identity_service'):
                self.service_manager.identity_service.create_mention(
                    surface_form=sender,
                    start_pos=0,
                    end_pos=len(sender),
                    source_ref=result_data.get("file_path", ""),
                    entity_type="email_sender",
                    confidence=0.9
                )
                
                # Create provenance record
                if hasattr(self.service_manager, 'provenance_service'):
                    self.service_manager.provenance_service.create_provenance_record(
                        tool_id=self.tool_id,
                        operation="email_processed",
                        input_data=result_data.get("file_path", ""),
                        output_data={"sender": sender}
                    )
        except Exception as e:
            logging.warning(f"Service mention creation failed: {e}")

    def _validate_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input parameters"""
        if not input_data:
            return {"valid": False, "error": "email_path parameter required"}
        
        if "email_path" not in input_data:
            return {"valid": False, "error": "email_path parameter required"}
        
        email_path = input_data["email_path"]
        if not isinstance(email_path, str) or not email_path.strip():
            return {"valid": False, "error": "email_path must be non-empty string"}
        
        # Validate file extension
        valid_extensions = ['.eml', '.msg', '.email', '.mbox']
        file_ext = Path(email_path).suffix.lower()
        if file_ext not in valid_extensions:
            return {"valid": False, "error": f"Unsupported email format: {file_ext}. Supported: {valid_extensions}"}
        
        return {"valid": True}

    def get_contract(self):
        """Return tool contract specification"""
        return {
            "tool_id": self.tool_id,
            "name": self.name,
            "category": self.category,
            "description": "Parse email files (.eml, .msg) and extract headers, body, attachments, and metadata",
            "input_schema": {
                "type": "object",
                "properties": {
                    "email_path": {
                        "type": "string",
                        "description": "Path to email file (.eml, .msg, .email, .mbox)"
                    },
                    "extract_attachments": {
                        "type": "boolean",
                        "description": "Whether to extract attachment data",
                        "default": True
                    },
                    "output_dir": {
                        "type": "string",
                        "description": "Directory to save extracted attachments (optional)"
                    }
                },
                "required": ["email_path"]
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "email_data": {
                        "type": "object",
                        "description": "Parsed email data including headers, body, attachments, metadata"
                    },
                    "stats": {
                        "type": "object",
                        "description": "Processing statistics"
                    }
                }
            },
            "error_codes": [
                ToolErrorCode.INVALID_INPUT,
                ToolErrorCode.FILE_NOT_FOUND,
                ToolErrorCode.PROCESSING_ERROR
            ]
        }

    def health_check(self) -> Dict[str, Any]:
        """Perform health check for email parsing capabilities"""
        try:
            # Test email module availability
            import email
            import email.header
            import email.utils
            
            # Test encoding detection
            import chardet
            
            # Check MSG support
            msg_available = MSG_SUPPORT
            
            # Test creating a simple email
            test_msg = MIMEText("Test email content")
            test_msg["Subject"] = "Test Subject"
            test_msg["From"] = "test@example.com"
            test_msg["To"] = "recipient@example.com"
            
            # Parse it back
            parsed = email.message_from_string(str(test_msg))
            
            return {
                "status": "healthy",
                "email_module": "available",
                "chardet_module": "available",
                "msg_support": msg_available,
                "test_parsing": "successful",
                "supported_formats": [".eml", ".msg" if msg_available else "(.msg requires extract-msg)", ".email", ".mbox"]
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }

    def cleanup(self):
        """Clean up resources"""
        self.attachments_extracted = 0
        self.headers_decoded = 0
        self.encoding_detections = 0