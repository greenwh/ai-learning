#!/bin/bash
#
# Quick Test Runner
# Fast smoke tests to verify backend is working
#

set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Detect Python
if command -v python3 &> /dev/null; then
    PYTHON=python3
else
    PYTHON=python
fi

# Navigate to backend directory if we're in tests/
if [ -f "../main.py" ]; then
    cd ..
fi

# Verify we're in the right place
if [ ! -f "main.py" ]; then
    echo -e "${RED}❌ Error: Cannot find main.py${NC}"
    echo "Run this from backend or backend/tests directory"
    exit 1
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Set PYTHONPATH so imports work correctly
# This adds the parent directory (project root) to Python's module search path
BACKEND_DIR=$(pwd)
PROJECT_ROOT=$(dirname "$BACKEND_DIR")
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

echo "Running quick smoke tests..."
echo ""

# Test 1: Check Python syntax
echo -n "  [1/5] Python syntax check... "
if $PYTHON -m py_compile main.py 2>/dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    exit 1
fi

# Test 2: Check database imports
echo -n "  [2/5] Database imports... "
if $PYTHON -c "from backend.database import init_db, get_db; from backend.database.models import User, Module" 2>/dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    exit 1
fi

# Test 3: Check learning engine imports
echo -n "  [3/5] Learning engine imports... "
if $PYTHON -c "from backend.learning_engine import StyleEngine, ContentDeliveryEngine, TutorEngine" 2>/dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    exit 1
fi

# Test 4: Check AI provider imports
echo -n "  [4/5] AI provider imports... "
if $PYTHON -c "from backend.ai.provider_manager import AIProviderManager, AIProvider" 2>/dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    exit 1
fi

# Test 5: Quick API validation
echo -n "  [5/5] API startup test... "
TEST_OUTPUT=$($PYTHON -c "
import sys
from fastapi.testclient import TestClient
from backend.database import init_db
from main import app

init_db()
client = TestClient(app)
response = client.get('/')
assert response.status_code == 200, f'Expected 200, got {response.status_code}'
assert response.json()['status'] == 'healthy', 'Health check failed'
print('OK')
" 2>&1)

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    echo "Error: $TEST_OUTPUT"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ All smoke tests passed!${NC}"
echo ""

# If pytest is available and test files exist, offer to run full tests
if command -v pytest &> /dev/null && [ -f "tests/test_integration.py" ]; then
    echo "Full test suite available. Run with:"
    echo "  PYTHONPATH=\"\$(dirname \$(pwd)):\$PYTHONPATH\" pytest tests/ -v"
    echo ""
fi
