#!/bin/bash

echo "🚀 Starting Super-Digimon Services"
echo "=================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Start Docker services
echo "🐳 Starting Docker services..."
docker-compose up -d

# Wait for Neo4j to be ready
echo "⏳ Waiting for Neo4j to start..."
sleep 10

# Check service health
echo "🏥 Checking service health..."
docker-compose ps

# Initialize databases
echo "🗄️ Initializing databases..."
python -c "
from src.utils.config import Config
from src.utils.database import DatabaseManager
config = Config()
db = DatabaseManager(config)
db.initialize()
health = db.health_check()
print('Database health:', health)
db.close()
"

echo ""
echo "✅ Services started successfully!"
echo ""
echo "📋 Next steps:"
echo "  1. Run the MCP server: python main.py"
echo "  2. Run tests: pytest tests/ -v"
echo "  3. View Neo4j browser: http://localhost:7474"
echo "  4. Stop services: docker-compose down"