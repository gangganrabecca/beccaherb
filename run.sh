#!/bin/bash
# Simple script to run the Herbal Plant Detection server

echo "🌿 Starting Herbal Plant Detection Server..."
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "   Creating .env file with default values..."
    echo "ROBOFLOW_API_KEY=eb6rXUxlCKM7cgv0duMU" > .env
    echo "ROBOFLOW_API_URL=https://serverless.roboflow.com" >> .env
fi

# Check if dependencies are installed
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
fi

echo "🚀 Starting server on http://0.0.0.0:8000"
echo "   Press CTRL+C to stop"
echo ""

python3 main.py

