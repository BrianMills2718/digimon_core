#!/bin/bash
# Development script for KGAS Research UI

echo "🚀 Starting KGAS Research UI Development Server..."

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Start development server
echo "🎨 Starting Vite development server..."
npm run dev