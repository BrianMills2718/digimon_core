#!/bin/bash
# GraphRAG Service Management Script
# Starts all GraphRAG services in the correct order

echo "🚀 Starting GraphRAG Services..."

# Check if Neo4j is running
echo "📊 Checking Neo4j status..."
if ! docker ps | grep -q neo4j; then
    echo "📊 Starting Neo4j..."
    docker-compose up -d neo4j
    echo "⏳ Waiting for Neo4j to be ready..."
    sleep 10
else
    echo "✅ Neo4j already running"
fi

# Start GraphRAG UI
echo "🖥️  Starting GraphRAG UI..."
python start_graphrag_ui.py &
UI_PID=$!
echo "✅ GraphRAG UI started (PID: $UI_PID)"

# Start MCP Server
echo "🔧 Starting MCP Server..."
python start_t301_mcp_server.py &
MCP_PID=$!
echo "✅ MCP Server started (PID: $MCP_PID)"

echo ""
echo "🎉 All GraphRAG services started successfully!"
echo ""
echo "📋 Service Status:"
echo "   Neo4j:       Running in Docker"
echo "   UI:          http://localhost:8501 (PID: $UI_PID)"
echo "   MCP Server:  Running (PID: $MCP_PID)"
echo ""
echo "🛑 To stop services:"
echo "   kill $UI_PID $MCP_PID"
echo "   docker-compose down"