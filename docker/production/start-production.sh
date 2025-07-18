#!/bin/bash

set -e

echo "🚀 Starting GraphRAG System in Production Mode"
echo "=============================================="

# Wait for Neo4j to be ready
echo "⏳ Waiting for Neo4j database..."
until python -c "
from src.core.neo4j_manager import Neo4jManager
try:
    manager = Neo4jManager()
    manager.get_session()
    print('✅ Neo4j connection successful')
except Exception as e:
    print(f'❌ Neo4j not ready: {e}')
    exit(1)
"; do
    echo "   Neo4j not ready, waiting 5 seconds..."
    sleep 5
done

# Run production validation
echo "🔍 Running production readiness validation..."
python -c "
from src.core.production_validator import ProductionValidator
from src.core.config_manager import ConfigManager

config_manager = ConfigManager()
validator = ProductionValidator(config_manager)
is_ready, results = validator.validate_production_readiness()

if not is_ready:
    print('❌ PRODUCTION VALIDATION FAILED')
    for result in results:
        if not result['passed']:
            print(f'  FAIL: {result[\"check\"]}')
            for issue in result['issues']:
                print(f'    - {issue}')
    exit(1)
else:
    print('✅ Production validation passed')
"

# Initialize Neo4j schema
echo "🔧 Initializing Neo4j schema..."
python scripts/init_neo4j_schema.py

# Start background services
echo "🔧 Starting MCP server..."
python src/mcp_server.py &
MCP_PID=$!

# Function to cleanup on exit
cleanup() {
    echo "🛑 Shutting down services..."
    kill $MCP_PID 2>/dev/null || true
    wait
    echo "✅ Cleanup completed"
}
trap cleanup EXIT INT TERM

# Wait a moment for MCP server to start
sleep 5

# Start Streamlit UI
echo "🌐 Starting Streamlit UI..."
exec streamlit run streamlit_app.py \
    --server.port=8501 \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false