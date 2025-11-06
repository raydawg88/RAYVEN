#!/bin/bash

# RAYVEN Startup Script

echo "🤖 Starting RAYVEN..."
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install dependencies if needed
if ! python3 -c "import coinbase" 2>/dev/null; then
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt -q
fi

# Check if credentials exist
if [ ! -f "credentials/.env" ]; then
    echo "❌ Error: credentials/.env not found!"
    echo ""
    echo "Please create credentials/.env with your Coinbase API credentials:"
    echo "  COINBASE_API_KEY_NAME=your_key_here"
    echo "  COINBASE_PRIVATE_KEY=your_private_key_here"
    echo "  COINBASE_PROJECT_ID=your_project_id_here"
    echo ""
    exit 1
fi

# Parse mode argument
MODE=""
if [ "$1" == "--dry-run" ] || [ "$1" == "-d" ]; then
    MODE="--dry-run"
    echo "⚠️  Running in DRY RUN mode (no real trades)"
    echo ""
fi

# Run RAYVEN
echo "🚀 Launching RAYVEN..."
echo ""
python3 main.py $MODE
