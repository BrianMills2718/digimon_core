#!/bin/bash

# Super-Digimon CC_AUTOMATOR4 Runner
# This script runs the CC_AUTOMATOR4 system to implement the Super-Digimon GraphRAG system

echo "🚀 Starting Super-Digimon Implementation with CC_AUTOMATOR4"
echo "============================================================"

# Set environment variables for optimal performance
export USE_SUBPHASES=false  # More stable execution
export DISABLE_MCP=false    # Use MCP servers

# Super-Digimon specific environment variables
export NEO4J_URI=${NEO4J_URI:-"bolt://localhost:7687"}
export NEO4J_USER=${NEO4J_USER:-"neo4j"}
export NEO4J_PASSWORD=${NEO4J_PASSWORD:-"password"}
export SQLITE_DB_PATH=${SQLITE_DB_PATH:-"./data/metadata.db"}
export FAISS_INDEX_PATH=${FAISS_INDEX_PATH:-"./data/faiss_index"}

# Optional: Set BRAVE_SEARCH_API_KEY for web search (falls back to WebSearch tool if not set)
# export BRAVE_SEARCH_API_KEY="your_api_key_here"

# Check if we're in the right directory
if [ ! -f "CLAUDE.md" ]; then
    echo "❌ Error: CLAUDE.md not found. Make sure you're in the super_digimon_implementation directory."
    exit 1
fi

# Parse command line arguments
MILESTONE=""
RESUME=""
VERBOSE="--verbose"

while [[ $# -gt 0 ]]; do
    case $1 in
        --milestone)
            MILESTONE="--milestone $2"
            shift 2
            ;;
        --resume)
            RESUME="--resume"
            shift
            ;;
        --quiet)
            VERBOSE=""
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --milestone N    Run specific milestone only (1, 2, or 3)"
            echo "  --resume         Resume from where you left off"
            echo "  --quiet          Run without verbose output"
            echo "  --help           Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                    # Run all milestones"
            echo "  $0 --milestone 1      # Run only milestone 1 (Core Services)"
            echo "  $0 --milestone 2      # Run only milestone 2 (Vertical Slice)"
            echo "  $0 --milestone 3      # Run only milestone 3 (Complete 121 Tools)"
            echo "  $0 --resume           # Resume from last checkpoint"
            exit 0
            ;;
        *)
            echo "❌ Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Display milestone information
echo "📋 Milestone Overview:"
echo "  Milestone 1: Core Services Foundation (T107, T110, T111, T121)"
echo "  Milestone 2: Vertical Slice (PDF → PageRank → Answer)"  
echo "  Milestone 3: Complete 121-Tool Implementation"
echo ""

if [ -n "$MILESTONE" ]; then
    echo "🎯 Running specific milestone: $MILESTONE"
elif [ -n "$RESUME" ]; then
    echo "🔄 Resuming from last checkpoint"
else
    echo "🚀 Running all milestones"
fi

echo ""
echo "📊 Environment:"
echo "  USE_SUBPHASES: $USE_SUBPHASES"
echo "  DISABLE_MCP: $DISABLE_MCP"
echo ""

# Run CC_AUTOMATOR4
echo "⚡ Executing CC_AUTOMATOR4..."
python ../cc_automator4/cli.py --project . $MILESTONE $RESUME $VERBOSE

# Check exit status
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ CC_AUTOMATOR4 completed successfully!"
    echo ""
    echo "📄 Check the following files:"
    echo "  - main.py (main implementation)"
    echo "  - .cc_automator/final_report.md (detailed report)"
    echo "  - .cc_automator/logs/*.log (execution logs)"
    echo ""
    echo "🧪 Test the implementation:"
    echo "  python main.py"
    echo "  pytest tests/ -v"
else
    echo ""
    echo "❌ CC_AUTOMATOR4 encountered an error."
    echo ""
    echo "🔍 Check the logs:"
    echo "  tail -f .cc_automator/logs/*.log"
    echo ""
    echo "🔄 To resume:"
    echo "  $0 --resume"
fi