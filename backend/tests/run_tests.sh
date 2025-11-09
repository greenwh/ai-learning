#!/bin/bash
# Automated test runner for AI Learning System

echo "================================================"
echo "AI Learning System - Automated Test Suite"
echo "================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track results
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Change to backend directory
cd "$(dirname "$0")/.." || exit 1

echo "Step 1: Running Diagnostic Checks..."
echo "------------------------------------------------"
python -m tests.diagnostic
DIAG_EXIT=$?

if [ $DIAG_EXIT -eq 0 ]; then
    echo -e "${GREEN}✓ Diagnostics passed${NC}"
else
    echo -e "${YELLOW}⚠ Diagnostics had warnings (this is OK for first run)${NC}"
fi

echo ""
echo "Step 2: Running Thompson Sampling Tests..."
echo "------------------------------------------------"
python -m pytest tests/test_thompson_sampling.py -v --tb=short
TS_EXIT=$?

if [ $TS_EXIT -eq 0 ]; then
    echo -e "${GREEN}✓ Thompson Sampling tests passed${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}✗ Thompson Sampling tests failed${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

echo ""
echo "Step 3: Running Modality Content Tests..."
echo "------------------------------------------------"
python -m pytest tests/test_modality_content.py -v --tb=short
MC_EXIT=$?

if [ $MC_EXIT -eq 0 ]; then
    echo -e "${GREEN}✓ Modality content tests passed${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}✗ Modality content tests failed${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

echo ""
echo "Step 4: Running Integration Tests..."
echo "------------------------------------------------"
python -m pytest tests/test_integration.py -v --tb=short
INT_EXIT=$?

if [ $INT_EXIT -eq 0 ]; then
    echo -e "${GREEN}✓ Integration tests passed${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}✗ Integration tests failed${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

echo ""
echo "================================================"
echo "Test Summary"
echo "================================================"
echo "Total test suites: $TOTAL_TESTS"
echo -e "Passed: ${GREEN}$PASSED_TESTS${NC}"
echo -e "Failed: ${RED}$FAILED_TESTS${NC}"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}All tests passed! ✓${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed. See details above.${NC}"
    exit 1
fi
