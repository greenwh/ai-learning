#!/bin/bash

echo "🚀 Starting AI Personalized Learning System"
echo ""

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for Python
if ! command_exists python3 && ! command_exists python; then
    echo "❌ Error: Python is not installed"
    exit 1
fi

# Check for Node.js
if ! command_exists node; then
    echo "❌ Error: Node.js is not installed"
    exit 1
fi

# Set Python command
PYTHON_CMD=$(command_exists python3 && echo "python3" || echo "python")

echo "📦 Setting up backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "  Creating virtual environment..."
    $PYTHON_CMD -m venv venv
fi

# Activate virtual environment
echo "  Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "  Installing Python dependencies..."
pip install -q -r requirements.txt

# Check if database exists, if not seed it
if [ ! -f "data/learning_system.db" ]; then
    echo "  🌱 Seeding database with initial content..."
    $PYTHON_CMD seed_data.py
fi

# Start backend server in background
echo "  🚀 Starting backend server on http://localhost:8000"
$PYTHON_CMD main.py &
BACKEND_PID=$!

cd ..

# Setup frontend
echo ""
echo "📦 Setting up frontend..."
cd frontend

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "  Installing npm dependencies..."
    npm install -q
fi

# Start frontend server
echo "  🚀 Starting frontend server on http://localhost:5173"
npm run dev &
FRONTEND_PID=$!

cd ..

echo ""
echo "✅ System is running!"
echo ""
echo "  🌐 Frontend: http://localhost:5173"
echo "  🔧 Backend:  http://localhost:8000"
echo "  📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Wait for Ctrl+C
trap "echo ''; echo '🛑 Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
