#!/bin/bash

echo "🤖 Starting Super-Digimon Web UI"
echo "================================"

# Check if Neo4j is running
echo "🔍 Checking Neo4j status..."
if ! docker-compose ps neo4j | grep -q "Up"; then
    echo "⚠️  Neo4j not running. Starting it now..."
    docker-compose up -d neo4j
    echo "⏳ Waiting for Neo4j to be ready..."
    sleep 10
else
    echo "✅ Neo4j is already running"
fi

# Install UI requirements if needed
if ! python -c "import streamlit" 2>/dev/null; then
    echo "📦 Installing UI requirements..."
    pip install streamlit pandas plotly
    echo "✅ UI requirements installed"
fi

# Check spaCy model
if ! python -c "import spacy; spacy.load('en_core_web_sm')" 2>/dev/null; then
    echo "📦 Downloading spaCy model..."
    python -m spacy download en_core_web_sm
fi

echo ""
echo "🚀 Starting Streamlit UI..."
echo "📱 Open your browser to: http://localhost:8501"
echo "🛑 Press Ctrl+C to stop"
echo ""

streamlit run web_ui.py --server.port 8501 --server.address localhost