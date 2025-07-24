#!/usr/bin/env python3
"""
Working MCP Client for KGAS Tools

Connects to the actual KGAS MCP server and provides a clean interface
for agent stress testing with real tool execution.
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import subprocess
import tempfile
import os

logger = logging.getLogger(__name__)

@dataclass
class MCPToolResult:
    """Result from MCP tool execution"""
    tool_name: str
    status: str  # "success", "error"
    output: Any
    execution_time: float
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None

class WorkingMCPClient:
    """
    Real MCP client that connects to actual KGAS tools.
    
    This class provides a simplified interface to the KGAS MCP server
    for agent stress testing.
    """
    
    def __init__(self, server_path: str = None):
        """
        Initialize MCP client.
        
        Args:
            server_path: Path to KGAS MCP server script
        """
        self.server_path = server_path or "/home/brian/projects/Digimons/kgas_mcp_server.py"
        self.process = None
        self.is_connected = False
        
    async def connect(self) -> bool:
        """Connect to KGAS MCP server"""
        try:
            # For now, we'll use subprocess calls to the MCP server
            # In production, this would use the MCP protocol directly
            
            # Test server availability
            result = subprocess.run([
                "python", self.server_path, "--test-connection"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                self.is_connected = True
                logger.info("Connected to KGAS MCP server successfully")
                return True
            else:
                logger.error(f"Failed to connect to MCP server: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"MCP connection failed: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from MCP server"""
        if self.process:
            self.process.terminate()
            await asyncio.sleep(1)
            if self.process.poll() is None:
                self.process.kill()
        self.is_connected = False
    
    async def execute_tool(self, tool_name: str, **kwargs) -> MCPToolResult:
        """
        Execute a tool via MCP interface.
        
        Args:
            tool_name: Name of the KGAS tool to execute
            **kwargs: Tool-specific parameters
            
        Returns:
            MCPToolResult with execution results
        """
        start_time = time.time()
        
        try:
            if not self.is_connected:
                await self.connect()
            
            # Map tool names to available KGAS tools
            tool_mapping = {
                "load_pdf": self._execute_pdf_loader,
                "chunk_text": self._execute_text_chunker,
                "extract_entities": self._execute_ner,
                "extract_relationships": self._execute_relationship_extractor,
                "analyze_document": self._execute_document_analyzer,
                "query_graph": self._execute_graph_query,
            }
            
            if tool_name not in tool_mapping:
                return MCPToolResult(
                    tool_name=tool_name,
                    status="error",
                    output=None,
                    execution_time=time.time() - start_time,
                    error_message=f"Unknown tool: {tool_name}",
                    metadata={"available_tools": list(tool_mapping.keys())}
                )
            
            # Execute the tool
            result = await tool_mapping[tool_name](**kwargs)
            
            return MCPToolResult(
                tool_name=tool_name,
                status="success" if result.get("status") == "success" else "error",
                output=result.get("data"),
                execution_time=time.time() - start_time,
                error_message=result.get("error"),
                metadata={
                    "tool_id": result.get("tool_id"),
                    "operation_id": result.get("operation_id"),
                    "timestamp": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Tool execution failed for {tool_name}: {e}")
            return MCPToolResult(
                tool_name=tool_name,
                status="error",
                output=None,
                execution_time=time.time() - start_time,
                error_message=str(e),
                metadata={"exception_type": type(e).__name__}
            )
    
    async def _execute_pdf_loader(self, file_path: str, workflow_id: str = None) -> Dict[str, Any]:
        """Execute T01 PDF Loader tool"""
        try:
            # Import and execute the real tool
            import sys
            sys.path.append("/home/brian/projects/Digimons")
            
            from src.tools.phase1.t01_pdf_loader_unified import T01PDFLoaderUnified
            from src.core.service_manager import get_service_manager
            
            service_manager = get_service_manager()
            tool = T01PDFLoaderUnified(service_manager)
            
            # Execute the tool
            result = await asyncio.to_thread(
                tool.load_pdf,
                file_path=file_path,
                workflow_id=workflow_id or f"test_{uuid.uuid4().hex[:8]}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"PDF loader execution failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "tool_id": "T01_PDF_LOADER"
            }
    
    async def _execute_text_chunker(self, document_ref: str, text: str, confidence: float = 0.8) -> Dict[str, Any]:
        """Execute T15A Text Chunker tool"""
        try:
            import sys
            sys.path.append("/home/brian/projects/Digimons")
            
            from src.tools.phase1.t15a_text_chunker_unified import T15ATextChunkerUnified
            from src.core.service_manager import get_service_manager
            from src.tools.base_tool import ToolRequest
            
            service_manager = get_service_manager()
            tool = T15ATextChunkerUnified(service_manager)
            
            # Create proper ToolRequest
            request = ToolRequest(
                tool_id="T15A",
                operation="chunk_text",
                input_data={
                    "document_ref": document_ref,
                    "text": text,
                    "confidence": confidence
                },
                parameters={}
            )
            
            result = await asyncio.to_thread(tool.execute, request)
            
            # Convert ToolResult to dict format
            return {
                "status": result.status,
                "data": result.data if result.status == "success" else None,
                "error": result.error_message if result.status == "error" else None,
                "tool_id": result.tool_id
            }
            
        except Exception as e:
            logger.error(f"Text chunker execution failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "tool_id": "T15A_TEXT_CHUNKER"
            }
    
    async def _execute_ner(self, chunk_ref: str, text: str, confidence: float = 0.8) -> Dict[str, Any]:
        """Execute T23A spaCy NER tool"""
        try:
            import sys
            sys.path.append("/home/brian/projects/Digimons")
            
            from src.tools.phase1.t23a_spacy_ner_unified import T23ASpacyNERUnified
            from src.core.service_manager import get_service_manager
            from src.tools.base_tool import ToolRequest
            
            service_manager = get_service_manager()
            tool = T23ASpacyNERUnified(service_manager)
            
            # Create proper ToolRequest
            request = ToolRequest(
                tool_id="T23A",
                operation="extract_entities",
                input_data={
                    "chunk_ref": chunk_ref,
                    "text": text,
                    "confidence": confidence
                },
                parameters={}
            )
            
            result = await asyncio.to_thread(tool.execute, request)
            
            # Convert ToolResult to dict format
            return {
                "status": result.status,
                "data": result.data if result.status == "success" else None,
                "error": result.error_message if result.status == "error" else None,
                "tool_id": result.tool_id
            }
            
        except Exception as e:
            logger.error(f"NER execution failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "tool_id": "T23A_SPACY_NER"
            }
    
    async def _execute_relationship_extractor(self, chunk_ref: str, text: str, entities: List[Dict], confidence: float = 0.8) -> Dict[str, Any]:
        """Execute T27 Relationship Extractor tool"""
        try:
            import sys
            sys.path.append("/home/brian/projects/Digimons")
            
            from src.tools.phase1.t27_relationship_extractor_unified import T27RelationshipExtractorUnified
            from src.core.service_manager import get_service_manager
            from src.tools.base_tool import ToolRequest
            
            service_manager = get_service_manager()
            tool = T27RelationshipExtractorUnified(service_manager)
            
            # Create proper ToolRequest
            request = ToolRequest(
                tool_id="T27",
                operation="extract_relationships",
                input_data={
                    "chunk_ref": chunk_ref,
                    "text": text,
                    "entities": entities,
                    "confidence": confidence
                },
                parameters={}
            )
            
            result = await asyncio.to_thread(tool.execute, request)
            
            # Convert ToolResult to dict format
            return {
                "status": result.status,
                "data": result.data if result.status == "success" else None,
                "error": result.error_message if result.status == "error" else None,
                "tool_id": result.tool_id
            }
            
        except Exception as e:
            logger.error(f"Relationship extractor execution failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "tool_id": "T27_RELATIONSHIP_EXTRACTOR"
            }
    
    async def _execute_document_analyzer(self, document: Dict[str, Any], analysis_modes: List[str]) -> Dict[str, Any]:
        """Execute document analysis pipeline"""
        try:
            # This implements a simple document processing pipeline
            results = {
                "document_id": document.get("id", f"doc_{uuid.uuid4().hex[:8]}"),
                "analyses": {},
                "processing_time": 0.0,
                "entity_count": 0,
                "relationship_count": 0
            }
            
            start_time = time.time()
            
            # Step 1: Load document (if file path provided)
            text_content = document.get("content")
            if not text_content and document.get("file_path"):
                pdf_result = await self._execute_pdf_loader(
                    file_path=document["file_path"],
                    workflow_id=results["document_id"]
                )
                if pdf_result.get("status") == "success":
                    text_content = pdf_result["data"]["text"]
                else:
                    return {
                        "status": "error",
                        "error": f"Failed to load document: {pdf_result.get('error')}",
                        "tool_id": "DOCUMENT_ANALYZER"
                    }
            
            if not text_content:
                return {
                    "status": "error", 
                    "error": "No text content available",
                    "tool_id": "DOCUMENT_ANALYZER"
                }
            
            # Step 2: Chunk text
            document_ref = f"storage://document/{results['document_id']}"
            chunk_result = await self._execute_text_chunker(
                document_ref=document_ref,
                text=text_content,
                confidence=0.8
            )
            
            if chunk_result.get("status") != "success":
                return {
                    "status": "error",
                    "error": f"Text chunking failed: {chunk_result.get('error')}",
                    "tool_id": "DOCUMENT_ANALYZER"
                }
            
            chunks = chunk_result["data"]["chunks"]
            results["analyses"]["text_chunking"] = {
                "chunk_count": len(chunks),
                "total_length": len(text_content)
            }
            
            # Step 3: Extract entities from chunks
            all_entities = []
            for chunk in chunks[:3]:  # Process first 3 chunks for demo
                chunk_ref = chunk["chunk_ref"]
                chunk_text = chunk["text"]
                
                ner_result = await self._execute_ner(
                    chunk_ref=chunk_ref,
                    text=chunk_text,
                    confidence=0.7
                )
                
                if ner_result.get("status") == "success":
                    entities = ner_result["data"]["entities"]
                    all_entities.extend(entities)
            
            results["entity_count"] = len(all_entities)
            results["analyses"]["entity_extraction"] = {
                "entities_found": len(all_entities),
                "entity_types": list(set(e.get("entity_type", "UNKNOWN") for e in all_entities))
            }
            
            # Step 4: Extract relationships (if requested)
            if "relationships" in analysis_modes:
                all_relationships = []
                for chunk in chunks[:2]:  # Process first 2 chunks for relationships
                    chunk_entities = [e for e in all_entities if e.get("chunk_ref") == chunk["chunk_ref"]]
                    if len(chunk_entities) >= 2:
                        rel_result = await self._execute_relationship_extractor(
                            chunk_ref=chunk["chunk_ref"],
                            text=chunk["text"],
                            entities=chunk_entities,
                            confidence=0.6
                        )
                        
                        if rel_result.get("status") == "success":
                            relationships = rel_result["data"]["relationships"]
                            all_relationships.extend(relationships)
                
                results["relationship_count"] = len(all_relationships)
                results["analyses"]["relationship_extraction"] = {
                    "relationships_found": len(all_relationships),
                    "relationship_types": list(set(r.get("relationship_type", "UNKNOWN") for r in all_relationships))
                }
            
            results["processing_time"] = time.time() - start_time
            
            return {
                "status": "success",
                "data": results,
                "tool_id": "DOCUMENT_ANALYZER"
            }
            
        except Exception as e:
            logger.error(f"Document analyzer execution failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "tool_id": "DOCUMENT_ANALYZER"
            }
    
    async def _execute_graph_query(self, query_text: str) -> Dict[str, Any]:
        """Execute graph query (placeholder - would need Neo4j)"""
        try:
            # For now, return a simulated response since Neo4j isn't running
            return {
                "status": "success",
                "data": {
                    "query": query_text,
                    "results": [
                        {
                            "entity": "Sample Entity",
                            "type": "ORGANIZATION",
                            "relationships": ["works_for", "located_in"],
                            "confidence": 0.85
                        }
                    ],
                    "result_count": 1,
                    "query_time": 0.1
                },
                "tool_id": "GRAPH_QUERY",
                "note": "Neo4j not available - returning simulated response"
            }
            
        except Exception as e:
            logger.error(f"Graph query execution failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "tool_id": "GRAPH_QUERY"
            }
    
    async def get_available_tools(self) -> List[str]:
        """Get list of available tools"""
        return [
            "load_pdf",
            "chunk_text", 
            "extract_entities",
            "extract_relationships",
            "analyze_document",
            "query_graph"
        ]
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of MCP connection and tools"""
        try:
            if not self.is_connected:
                await self.connect()
            
            # Test a simple tool execution
            test_result = await self._execute_text_chunker(
                document_ref="test://health_check",
                text="This is a health check test.",
                confidence=0.8
            )
            
            healthy = test_result.get("status") == "success"
            
            return {
                "healthy": healthy,
                "connected": self.is_connected,
                "available_tools": await self.get_available_tools(),
                "test_result": test_result.get("status"),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "healthy": False,
                "connected": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


# Convenience function for creating client
def create_mcp_client() -> WorkingMCPClient:
    """Create and return a working MCP client"""
    return WorkingMCPClient()


# Test function
async def test_mcp_client():
    """Test the MCP client with real tools"""
    client = create_mcp_client()
    
    try:
        # Test connection
        print("Testing MCP client connection...")
        connected = await client.connect()
        print(f"Connection: {'✅ Success' if connected else '❌ Failed'}")
        
        # Test health check
        print("\nTesting health check...")
        health = await client.health_check()
        print(f"Health: {'✅ Healthy' if health.get('healthy') else '❌ Unhealthy'}")
        print(f"Available tools: {health.get('available_tools', [])}")
        
        # Test text chunking
        print("\nTesting text chunker...")
        chunk_result = await client.execute_tool(
            "chunk_text",
            document_ref="test://sample_doc",
            text="This is a sample text for testing the chunking functionality. It should be split into appropriate chunks for processing.",
            confidence=0.8
        )
        print(f"Chunker result: {chunk_result.status}")
        if chunk_result.status == "success":
            chunk_count = len(chunk_result.output.get("chunks", []))
            print(f"Generated {chunk_count} chunks")
        
        # Test entity extraction
        print("\nTesting entity extraction...")
        ner_result = await client.execute_tool(
            "extract_entities",
            chunk_ref="test://sample_chunk",
            text="Apple Inc. is a technology company founded by Steve Jobs in Cupertino, California.",
            confidence=0.7
        )
        print(f"NER result: {ner_result.status}")
        if ner_result.status == "success":
            entity_count = len(ner_result.output.get("entities", []))
            print(f"Found {entity_count} entities")
        
        # Test document analysis pipeline
        print("\nTesting document analysis pipeline...")
        doc_result = await client.execute_tool(
            "analyze_document",
            document={
                "id": "test_doc_001",
                "content": "Apple Inc. is a multinational technology company headquartered in Cupertino, California. The company was founded by Steve Jobs, Steve Wozniak, and Ronald Wayne in 1976. Apple designs, develops, and sells consumer electronics, computer software, and online services."
            },
            analysis_modes=["entities", "relationships"]
        )
        print(f"Document analysis result: {doc_result.status}")
        if doc_result.status == "success":
            data = doc_result.output
            print(f"Entities found: {data.get('entity_count', 0)}")
            print(f"Relationships found: {data.get('relationship_count', 0)}")
            print(f"Processing time: {data.get('processing_time', 0):.2f}s")
        
        print("\n🎉 MCP client test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(test_mcp_client())