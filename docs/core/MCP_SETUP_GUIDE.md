# MCP Server Setup Guide

Quick reference for setting up Model Context Protocol (MCP) servers with Claude Code.

## Working MCP Server Template

### FastMCP Server (Recommended)
```python
#!/usr/bin/env python3
"""
FastMCP Server Template
"""

from fastmcp import FastMCP

# Create FastMCP instance
mcp = FastMCP("server-name")

@mcp.tool()
def tool_name(param: str) -> str:
    """Tool description."""
    return f"Result: {param}"

@mcp.tool() 
def test_connection() -> str:
    """Test MCP server connection."""
    return "✅ MCP Server Connected!"

if __name__ == "__main__":
    mcp.run()
```

### Setup Commands
```bash
# 1. Install FastMCP
pip install fastmcp

# 2. Create server file (use template above)
# 3. Test server works
timeout 3 python your_server.py

# 4. Add to Claude Code
claude mcp add server-name /path/to/python /path/to/your_server.py

# 5. Verify in Claude Code
# Type /mcp to see servers and tools
```

## Troubleshooting

### Common Issues

**1. "spawn python ENOENT"**
- Use full Python path: `/home/user/miniconda3/bin/python`
- Don't use just `python`

**2. "Connection timed out"**
- Use FastMCP, not low-level MCP server
- Ensure `mcp = FastMCP("name")` is global variable
- Test server runs without errors: `timeout 3 python server.py`

**3. "No MCP servers configured"**
- Restart Claude Code after adding server
- Check logs: `~/.cache/claude-cli-nodejs/*/mcp-logs-*/`

**4. Server shows as "Failed"**
- Check latest log file for specific error
- Ensure all imports work: `python -c "from fastmcp import FastMCP"`
- Verify file permissions: `chmod +x server.py`

### Log Locations
```bash
# View latest MCP logs
ls -la ~/.cache/claude-cli-nodejs/*/mcp-logs-*/
cat ~/.cache/claude-cli-nodejs/*/mcp-logs-*/$(ls -t ~/.cache/claude-cli-nodejs/*/mcp-logs-*/ | head -1)
```

### Quick Commands
```bash
# List configured servers
claude mcp list

# Remove broken server
claude mcp remove server-name

# Debug mode
claude --debug mcp list
```

## Best Practices

1. **Always use FastMCP** - more reliable than low-level MCP
2. **Test server directly first** - before adding to Claude Code
3. **Use full Python paths** - avoid PATH-dependent commands
4. **Include test_connection tool** - for easy verification
5. **Restart Claude Code** - after configuration changes

## Dependencies
```bash
pip install fastmcp  # Installs mcp, fastmcp, and dependencies
```

## File Structure
```
project/
├── mcp_server.py        # Your MCP server
└── requirements.txt     # Include fastmcp
```

This setup process should be reliable and repeatable for future MCP implementations.