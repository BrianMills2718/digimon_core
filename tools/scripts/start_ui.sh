#!/bin/bash

# Start the Streamlit Ontology Generator UI

echo "🔬 Starting Super-Digimon Ontology Generator..."
echo "================================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please create one first:"
    echo "   python -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt -r requirements_ui.txt"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "❌ Streamlit not found. Installing UI requirements..."
    pip install -r requirements_ui.txt
fi

# Check if databases are running
if ! nc -z localhost 7687 2>/dev/null; then
    echo "⚠️  Neo4j not running on port 7687"
    echo "   Run: docker-compose up -d"
fi

if ! nc -z localhost 6333 2>/dev/null; then
    echo "⚠️  Qdrant not running on port 6333"
    echo "   Run: docker-compose up -d"
fi

# Start Streamlit
echo ""
echo "🚀 Launching Streamlit app..."
echo "   URL: http://localhost:8501"
echo ""

streamlit run streamlit_app.py \
    --server.port=8501 \
    --server.address=localhost \
    --browser.gatherUsageStats=false \
    --theme.primaryColor="#3b82f6" \
    --theme.backgroundColor="#ffffff" \
    --theme.secondaryBackgroundColor="#f9fafb" \
    --theme.textColor="#1f2937"