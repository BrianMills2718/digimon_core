#!/bin/bash
# Installation script for Gemini Code Review Tool

echo "🚀 Installing Gemini Code Review Tool..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "⚠️  Node.js is required for repomix but not installed."
    echo "   Please install from: https://nodejs.org/"
    echo "   Or via package manager: brew install node (macOS) or apt install nodejs (Ubuntu)"
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Create .env from example if it doesn't exist
if [ ! -f .env ]; then
    echo "📋 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your Gemini API key"
fi

# Make scripts executable
chmod +x gemini_review.py

echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your Gemini API key"
echo "2. Run: python gemini_review.py --help"
echo "3. Initialize for your project: python gemini_review.py --init"