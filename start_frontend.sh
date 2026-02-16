#!/bin/bash
# Startup script for THE FACE (Frontend Client)

cd "$(dirname "$0")/client"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Start the development server
echo "🎨 Starting Gus System - THE FACE..."
npm run dev
