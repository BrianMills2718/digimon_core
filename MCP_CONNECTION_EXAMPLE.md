# MCP (Model Context Protocol) Connection Example

This document provides a working example of how to set up an MCP server for Super-Digimon.

## What is MCP?

MCP (Model Context Protocol) is the protocol that allows Claude Code to communicate with external tools. It enables:
- Tool discovery and description
- Parameter validation
- Result formatting
- Error handling

## Basic MCP Server Structure

### 1. Simple MCP Server Example

```python
#!/usr/bin/env python3
"""
simple_mcp_server.py - A minimal MCP server example
"""

import asyncio
import json
import sys
from typing import Any, Dict

class SimpleMCPServer:
    """A minimal MCP server implementation"""
    
    def __init__(self):
        self.tools = {
            "add_numbers": {
                "description": "Add two numbers together",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "a": {"type": "number", "description": "First number"},
                        "b": {"type": "number", "description": "Second number"}
                    },
                    "required": ["a", "b"]
                }
            },
            "greet": {
                "description": "Generate a greeting message",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Name to greet"}
                    },
                    "required": ["name"]
                }
            }
        }
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP requests"""
        method = request.get("method")
        
        if method == "tools/list":
            return {
                "tools": [
                    {"name": name, **info} 
                    for name, info in self.tools.items()
                ]
            }
        
        elif method == "tools/call":
            tool_name = request["params"]["name"]
            arguments = request["params"]["arguments"]
            
            if tool_name == "add_numbers":
                result = arguments["a"] + arguments["b"]
                return {"content": [{"type": "text", "text": f"Result: {result}"}]}
            
            elif tool_name == "greet":
                return {"content": [{"type": "text", "text": f"Hello, {arguments['name']}!"}]}
        
        return {"error": {"code": -32601, "message": "Method not found"}}
    
    async def run(self):
        """Run the MCP server"""
        while True:
            line = sys.stdin.readline()
            if not line:
                break
            
            try:
                request = json.loads(line)
                response = await self.handle_request(request)
                response["jsonrpc"] = "2.0"
                response["id"] = request.get("id")
                
                print(json.dumps(response))
                sys.stdout.flush()
            except Exception as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {"code": -32603, "message": str(e)}
                }
                print(json.dumps(error_response))
                sys.stdout.flush()

if __name__ == "__main__":
    server = SimpleMCPServer()
    asyncio.run(server.run())
```

### 2. GraphRAG Tool Example

```python
#!/usr/bin/env python3
"""
graphrag_mcp_server.py - MCP server with a GraphRAG tool
"""

import asyncio
import json
import sys
from typing import Any, Dict, List
from neo4j import GraphDatabase

class GraphRAGMCPServer:
    """MCP server with GraphRAG tools"""
    
    def __init__(self):
        # In real implementation, these would come from environment variables
        self.driver = None  # Neo4j driver instance
        
        self.tools = {
            "load_document": {
                "description": "Load a document and prepare it for graph processing",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Path to the document file"
                        },
                        "format": {
                            "type": "string",
                            "enum": ["txt", "pdf", "html", "md"],
                            "description": "Document format"
                        }
                    },
                    "required": ["path", "format"]
                }
            },
            "extract_entities": {
                "description": "Extract entities from text using NLP",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Text to extract entities from"
                        },
                        "types": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Entity types to extract (e.g., PERSON, ORG)"
                        }
                    },
                    "required": ["text"]
                }
            },
            "find_similar_entities": {
                "description": "Find entities similar to a given entity",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "entity_name": {
                            "type": "string",
                            "description": "Name of the entity to find similar ones for"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results",
                            "default": 10
                        }
                    },
                    "required": ["entity_name"]
                }
            }
        }
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP requests"""
        method = request.get("method")
        
        if method == "tools/list":
            return {
                "tools": [
                    {"name": name, **info} 
                    for name, info in self.tools.items()
                ]
            }
        
        elif method == "tools/call":
            tool_name = request["params"]["name"]
            arguments = request["params"]["arguments"]
            
            if tool_name == "load_document":
                # Simplified example - real implementation would actually load file
                return {
                    "content": [{
                        "type": "text",
                        "text": f"Loaded document from {arguments['path']} (format: {arguments['format']})"
                    }]
                }
            
            elif tool_name == "extract_entities":
                # Simplified example - real implementation would use NLP
                mock_entities = [
                    {"text": "Celestial Council", "type": "ORG"},
                    {"text": "Zephyr", "type": "PERSON"}
                ]
                return {
                    "content": [{
                        "type": "text",
                        "text": json.dumps(mock_entities, indent=2)
                    }]
                }
            
            elif tool_name == "find_similar_entities":
                # Simplified example - real implementation would query Neo4j
                mock_results = [
                    {"name": "Similar Entity 1", "similarity": 0.95},
                    {"name": "Similar Entity 2", "similarity": 0.87}
                ]
                return {
                    "content": [{
                        "type": "text",
                        "text": json.dumps(mock_results, indent=2)
                    }]
                }
        
        return {"error": {"code": -32601, "message": "Method not found"}}
    
    async def run(self):
        """Run the MCP server"""
        while True:
            line = sys.stdin.readline()
            if not line:
                break
            
            try:
                request = json.loads(line)
                response = await self.handle_request(request)
                response["jsonrpc"] = "2.0"
                response["id"] = request.get("id")
                
                print(json.dumps(response))
                sys.stdout.flush()
            except Exception as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {"code": -32603, "message": str(e)}
                }
                print(json.dumps(error_response))
                sys.stdout.flush()

if __name__ == "__main__":
    server = GraphRAGMCPServer()
    asyncio.run(server.run())
```

### 3. MCP Configuration File

Create `mcp_config.json` to register your MCP servers with Claude Code:

```json
{
  "mcpServers": {
    "super-digimon": {
      "command": "python",
      "args": ["/path/to/graphrag_mcp_server.py"],
      "env": {
        "NEO4J_URI": "bolt://localhost:7687",
        "NEO4J_USER": "neo4j",
        "NEO4J_PASSWORD": "your-password"
      }
    }
  }
}
```

## Installation Steps

1. **Install Dependencies**:
   ```bash
   pip install neo4j
   ```

2. **Create MCP Server File**:
   Save one of the examples above as `mcp_server.py`

3. **Make Executable**:
   ```bash
   chmod +x mcp_server.py
   ```

4. **Configure Claude Code**:
   - Copy `mcp_config.json` to Claude Code's configuration directory
   - Update paths and credentials

5. **Test the Server**:
   ```bash
   # Test manually
   echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python mcp_server.py
   ```

## Key Concepts

### Tool Schema
Each tool must define:
- `description`: What the tool does
- `inputSchema`: JSON Schema for parameters
- `required`: List of required parameters

### Response Format
Tools should return:
```json
{
  "content": [
    {
      "type": "text",
      "text": "Tool output here"
    }
  ]
}
```

### Error Handling
Return errors in JSON-RPC format:
```json
{
  "error": {
    "code": -32603,
    "message": "Error description"
  }
}
```

## Next Steps

1. Implement all 26 core tools following this pattern
2. Add proper Neo4j integration
3. Implement error handling and logging
4. Add tests for each tool
5. Create tool documentation

## Resources

- [MCP Specification](https://modelcontextprotocol.io/docs)
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)
- [JSON Schema](https://json-schema.org/)

## Common Issues

1. **Permission Denied**: Make sure the script is executable
2. **Import Errors**: Install all required dependencies
3. **Connection Refused**: Check Neo4j is running and credentials are correct
4. **Tool Not Found**: Ensure tool name matches exactly in configuration

Remember: Start simple, test often, and build incrementally!