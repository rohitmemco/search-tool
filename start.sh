#!/bin/bash

echo "===================================="
echo "  Starting PriceNexus Application"
echo "===================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check for Python
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo -e "${RED}✗ Python not found. Please install Python 3.9+${NC}"
    exit 1
fi

# Check for Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}✗ Node.js not found. Please install Node.js 16+${NC}"
    exit 1
fi

# Check for MongoDB
echo "[1/4] Checking MongoDB..."
if command -v mongosh &> /dev/null || command -v mongo &> /dev/null; then
    # Try to start MongoDB (for Mac with Homebrew)
    if command -v brew &> /dev/null; then
        brew services start mongodb-community 2>/dev/null || true
    fi
    echo -e "${GREEN}✓ MongoDB should be running${NC}"
else
    echo -e "${YELLOW}! MongoDB command not found. Make sure MongoDB is installed and running${NC}"
fi
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Start Backend
echo "[2/4] Starting Backend Server..."
cd "$SCRIPT_DIR/backend"

# Install Python dependencies if needed
if [ ! -d "venv" ]; then
    echo "  Creating virtual environment..."
    python3 -m venv venv 2>/dev/null || python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null

# Install requirements
echo "  Installing Python dependencies..."
pip install -q -r requirements.txt

# Start backend in background
echo "  Starting FastAPI server..."
python -m uvicorn server:app --reload --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}✓ Backend started (PID: $BACKEND_PID) at http://localhost:8000${NC}"
echo ""

# Give backend time to start
sleep 3

# Start Frontend
echo "[3/4] Installing Frontend Dependencies..."
cd "$SCRIPT_DIR/frontend"

if [ ! -d "node_modules" ]; then
    echo "  Installing npm packages..."
    npm install
else
    echo -e "${GREEN}✓ Dependencies already installed${NC}"
fi
echo ""

echo "[4/4] Starting Frontend..."
echo -e "${GREEN}✓ Frontend starting at http://localhost:3000${NC}"
echo ""

echo "===================================="
echo "  Application Ready!"
echo "===================================="
echo "  Frontend: http://localhost:3000"
echo "  Backend:  http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo "===================================="
echo ""
echo "Press Ctrl+C to stop all servers..."
echo ""

# Start frontend (this will keep the script running)
npm start

# Cleanup when script exits
cleanup() {
    echo ""
    echo "Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    echo "Done!"
}

trap cleanup EXIT
