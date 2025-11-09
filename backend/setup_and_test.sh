#!/bin/bash
#
# Backend Setup and Test Script
# One-stop script for backend setup, installation, and testing
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║   AI Learning System - Backend Setup & Test               ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if we're in the backend directory
if [ ! -f "main.py" ] || [ ! -f "requirements.txt" ]; then
    echo -e "${RED}❌ Error: Run this from the backend directory${NC}"
    exit 1
fi

# Detect Python command
if command -v python3 &> /dev/null; then
    PYTHON=python3
elif command -v python &> /dev/null; then
    PYTHON=python
else
    echo -e "${RED}❌ Python not found${NC}"
    exit 1
fi

echo -e "${BLUE}Step 1: Python Environment${NC}"
echo "  Found: $PYTHON ($($PYTHON --version))"
echo "  ✓ Python is available"
echo ""

echo -e "${BLUE}Step 2: Virtual Environment${NC}"
# Create virtual environment if needed
if [ ! -d "venv" ]; then
    echo "  Creating virtual environment..."
    $PYTHON -m venv venv
    echo "  ✓ Virtual environment created"
else
    echo "  ✓ Virtual environment exists"
fi
echo ""

echo -e "${BLUE}Step 3: Activating Environment${NC}"
# Activate virtual environment
source venv/bin/activate
echo "  ✓ Virtual environment activated"
echo ""

echo -e "${BLUE}Step 4: Installing Dependencies${NC}"
# Upgrade pip quietly
pip install -q --upgrade pip
# Install requirements
pip install -q -r requirements.txt
echo "  ✓ Dependencies installed"
echo ""

echo -e "${BLUE}Step 5: Database Setup${NC}"
# Initialize database if needed
if [ ! -f "data/learning_system.db" ]; then
    echo "  Creating and seeding database..."
    # Set PYTHONPATH so imports work correctly
    export PYTHONPATH="$(dirname $(pwd)):$PYTHONPATH"
    $PYTHON seed_data.py
    echo "  ✓ Database created and seeded"
else
    echo "  ✓ Database exists"
fi
echo ""

echo -e "${BLUE}Step 6: Running Tests${NC}"
# Check if tests directory exists
if [ -d "tests" ]; then
    # Run quick tests
    if [ -f "tests/quick_start.sh" ]; then
        bash tests/quick_start.sh
    else
        echo "  ⚠ tests/quick_start.sh not found, skipping tests"
    fi
else
    echo "  ⚠ No tests directory found, skipping tests"
fi
echo ""

echo -e "${GREEN}✅ Setup Complete!${NC}"
echo ""
echo "To start the backend server:"
echo "  1. source venv/bin/activate"
echo "  2. export PYTHONPATH=\"\$(dirname \$(pwd)):\$PYTHONPATH\""
echo "  3. python main.py"
echo ""
echo "Or use the root start.sh script to run both frontend and backend."
echo ""
