#!/bin/bash
# Quick start script for Voice Assistant (macOS/Linux)

echo ""
echo "========================================"
echo "Voice Assistant - Quick Start"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found. Please install Python 3.9+"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js not found. Please install Node.js 18+"
    exit 1
fi

# Setup Backend
echo ""
echo "[1/4] Setting up backend..."
cd backend

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

if [ ! -f ".env" ]; then
    echo ""
    echo "ERROR: Backend .env file not found"
    echo "Please copy ../.env.example to .env and configure it"
    echo ""
    exit 1
fi

# Start Backend
echo "Starting backend..."
python -m uvicorn src.main:app --reload --port 8000 &
backend_pid=$!
sleep 2

cd ..

# Setup Frontend
echo ""
echo "[2/4] Setting up frontend..."
cd frontend-next

echo "Installing dependencies..."
npm install

if [ ! -f ".env.local" ]; then
    echo "Creating .env.local..."
    cat > .env.local << EOF
NEXT_PUBLIC_WEBSOCKET_URL=ws://localhost:8000/ws/voice
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF
fi

# Start Frontend
echo "Starting frontend..."
npm run dev &
frontend_pid=$!

cd ..

# All done
echo ""
echo "========================================"
echo "✅ Setup complete!"
echo ""
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop"
echo "========================================"

# Wait for user interruption
wait
