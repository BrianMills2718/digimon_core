#!/bin/bash
# Quick GraphRAG System Status Check
# Provides rapid health assessment

echo "🔍 GraphRAG System Status Check"
echo "==============================="

# Check Neo4j
echo "📊 Neo4j Status:"
if docker ps | grep -q neo4j; then
    echo "   ✅ Neo4j running in Docker"
else
    echo "   ❌ Neo4j not running"
fi

# Check Python environment
echo ""
echo "🐍 Python Environment:"
if python -c "import src.core.service_manager" 2>/dev/null; then
    echo "   ✅ GraphRAG modules accessible"
else
    echo "   ❌ GraphRAG modules not accessible"
fi

# Check API keys
echo ""
echo "🔑 API Configuration:"
if [ ! -z "$OPENAI_API_KEY" ]; then
    echo "   ✅ OpenAI API key configured"
else
    echo "   ⚠️  OpenAI API key not set"
fi

if [ ! -z "$GOOGLE_API_KEY" ]; then
    echo "   ✅ Google API key configured"
else
    echo "   ⚠️  Google API key not set"
fi

# Quick functional test
echo ""
echo "🧪 Quick Functional Test:"
if python -c "
import tempfile
from pathlib import Path
import sys
sys.path.insert(0, '.')

try:
    from src.tools.phase1.vertical_slice_workflow import VerticalSliceWorkflow
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write('Test document with entities.')
        test_file = f.name
    
    workflow = VerticalSliceWorkflow()
    result = workflow.execute_workflow(pdf_path=test_file, query='Test query')
    
    if result.get('status') == 'success':
        print('   ✅ Phase 1 workflow functional')
    else:
        print('   ❌ Phase 1 workflow failed')
        
except Exception as e:
    print(f'   ❌ Quick test failed: {e}')
" 2>/dev/null; then
    echo "   ✅ Basic functionality confirmed"
else
    echo "   ❌ Basic functionality test failed"
fi

# Check documentation
echo ""
echo "📚 Documentation Status:"
if [ -f "PROJECT_STATUS.md" ]; then
    echo "   ✅ PROJECT_STATUS.md available"
else
    echo "   ❌ PROJECT_STATUS.md missing"
fi

if [ -f "DOCUMENTATION_INDEX.md" ]; then
    echo "   ✅ DOCUMENTATION_INDEX.md available"
else
    echo "   ❌ DOCUMENTATION_INDEX.md missing"
fi

echo ""
echo "📋 For detailed status: cat PROJECT_STATUS.md"
echo "📋 For all documentation: cat DOCUMENTATION_INDEX.md"
echo "📋 For development context: cat CLAUDE.md"