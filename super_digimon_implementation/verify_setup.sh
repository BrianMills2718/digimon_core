#!/bin/bash

# Super-Digimon Setup Verification Script
echo "🔍 Verifying Super-Digimon CC_AUTOMATOR4 Setup"
echo "=============================================="

# Check current directory
echo "📁 Current directory: $(pwd)"
echo ""

# Check required files
echo "📋 Checking required files..."
files=("CLAUDE.md" "README.md" "run_automator.sh")
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file (MISSING)"
    fi
done
echo ""

# Check CC_AUTOMATOR4
echo "🤖 Checking CC_AUTOMATOR4..."
if [ -f "../cc_automator4/cli.py" ]; then
    echo "  ✅ CC_AUTOMATOR4 cli.py found"
else
    echo "  ❌ CC_AUTOMATOR4 cli.py not found"
fi
echo ""

# Check documentation
echo "📚 Checking documentation..."
docs=("SPECIFICATIONS.md" "DATABASE_INTEGRATION.md" "IMPLEMENTATION_REQUIREMENTS.md" "COMPATIBILITY_MATRIX.md" "ARCHITECTURE.md" "DESIGN_PATTERNS.md")
for doc in "${docs[@]}"; do
    if [ -f "../docs/core/$doc" ]; then
        echo "  ✅ ../docs/core/$doc"
    else
        echo "  ❌ ../docs/core/$doc (MISSING)"
    fi
done
echo ""

# Check test data
echo "🧪 Checking test data..."
if [ -d "../test_data/celestial_council" ]; then
    echo "  ✅ ../test_data/celestial_council/"
    if [ -d "../test_data/celestial_council/small" ]; then
        echo "    ✅ Small dataset"
    fi
    if [ -d "../test_data/celestial_council/medium" ]; then
        echo "    ✅ Medium dataset"
    fi
    if [ -d "../test_data/celestial_council/large" ]; then
        echo "    ✅ Large dataset"
    fi
else
    echo "  ❌ ../test_data/celestial_council/ (MISSING)"
fi
echo ""

# Check MCP configuration
echo "🤖 Checking MCP server setup..."
if [ -f "mcp_config.json" ]; then
    echo "  ✅ mcp_config.json present"
else
    echo "  ❌ mcp_config.json missing"
fi

# Check if MCP servers are installed
echo "  Checking installed MCP servers..."
if npm list -g @modelcontextprotocol/server-filesystem &> /dev/null; then
    echo "    ✅ Filesystem MCP server installed"
else
    echo "    ❌ Filesystem MCP server not installed"
fi

if npm list -g @modelcontextprotocol/server-brave-search &> /dev/null; then
    echo "    ✅ Brave Search MCP server installed"
else
    echo "    ❌ Brave Search MCP server not installed"
fi

# Check Claude MCP configuration
echo "  Checking Claude MCP configuration..."
if command -v claude &> /dev/null; then
    claude mcp list &> /dev/null
    if [ $? -eq 0 ]; then
        echo "    ✅ Claude MCP configured"
    else
        echo "    ⚠️  Claude MCP may need configuration"
    fi
else
    echo "    ⚠️  Claude CLI not found"
fi
echo ""

# Check environment configuration
echo "🔧 Checking environment configuration..."
if [ -f ".env" ]; then
    echo "  ✅ .env file found"
else
    echo "  ⚠️  .env file not found (optional - defaults will be used)"
fi

if [ -f ".env.example" ]; then
    echo "  ✅ .env.example template available"
fi
echo ""

# Check CLAUDE.md content
echo "📝 Checking CLAUDE.md content..."
if grep -q "121 specialized tools" CLAUDE.md; then
    echo "  ✅ References 121 tools"
fi
if grep -q "Milestone 1: Core Services Foundation" CLAUDE.md; then
    echo "  ✅ Milestone 1 defined"
fi
if grep -q "Milestone 2: Vertical Slice" CLAUDE.md; then
    echo "  ✅ Milestone 2 defined"
fi
if grep -q "Milestone 3: Complete 121-Tool" CLAUDE.md; then
    echo "  ✅ Milestone 3 defined"
fi
if grep -q "../docs/core/SPECIFICATIONS.md" CLAUDE.md; then
    echo "  ✅ References documentation"
fi
if grep -q "../test_data/" CLAUDE.md; then
    echo "  ✅ References test data"
fi
echo ""

# Summary
echo "🎯 Setup Summary:"
echo "  Project: Super-Digimon GraphRAG System"
echo "  Tools: 121 tools across 8 phases"
echo "  Architecture: Neo4j + SQLite + FAISS"
echo "  Implementation: CC_AUTOMATOR4 with 3 milestones"
echo ""

echo "✅ Setup verification complete!"
echo ""
echo "🚀 Ready to run:"
echo "  ./run_automator.sh           # Run all milestones"
echo "  ./run_automator.sh --help    # See all options"
echo ""
echo "🔧 MCP Setup Notes:"
echo "  • MCP servers provide enhanced capabilities for research and file operations"
echo "  • Filesystem MCP: Secure file operations during implementation"
echo "  • Brave Search MCP: Web research (requires API key, falls back to WebSearch)"
echo "  • Context7 MCP: Large codebase context management"
echo ""
echo "📋 Next Steps:"
echo "  1. Optional: Copy .env.example to .env and configure"
echo "  2. Optional: Get Brave Search API key for enhanced research"
echo "  3. Run: ./run_automator.sh to start implementation"
echo "  4. Monitor: tail -f .cc_automator/logs/*.log"