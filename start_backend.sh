#!/bin/bash
# Startup script for THE BRAIN (Backend Server)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "server/venv" ]; then
    echo "Creating virtual environment..."
    cd server
    python3 -m venv venv
    cd ..
fi

# Activate virtual environment
source server/venv/bin/activate

# Install dependencies if needed
if [ ! -f "server/venv/.installed" ]; then
    echo "Installing dependencies..."
    pip install -r server/requirements.txt
    touch server/venv/.installed
fi

# Check for GROQ_API_KEY
if [ -z "$GROQ_API_KEY" ]; then
    echo "⚠️  WARNING: GROQ_API_KEY environment variable not set!"
    echo "Please set it with: export GROQ_API_KEY='your-key-here'"
fi

# Create shared directory if it doesn't exist
mkdir -p shared

# Run the server from project root
echo "🚀 Starting Gus System - THE BRAIN..."
uvicorn server.main:app --reload --host 0.0.0.0 --port 8000
