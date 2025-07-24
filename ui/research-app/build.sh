#!/bin/bash
# Build script for KGAS Research UI

echo "🏗️  Building KGAS Research UI for production..."

# Install dependencies
npm install

# Build the app
npm run build

echo "✅ Build complete! Output in ./dist directory"
echo "📌 To preview: npm run preview"
echo "🚀 To deploy: Copy ./dist contents to your web server"
