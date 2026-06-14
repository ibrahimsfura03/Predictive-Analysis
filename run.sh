#!/bin/bash

# Student Performance Prediction System - Startup Script
# This ensures the correct Python virtual environment is used

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting Student Performance Prediction System${NC}"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}✗ Virtual environment not found!${NC}"
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${GREEN}✓ Activating virtual environment${NC}"
source venv/bin/activate

# Check if dependencies are installed
echo -e "${GREEN}✓ Checking dependencies${NC}"
if ! python -c "import flask" 2>/dev/null; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    pip install -r requirements.txt
fi

if ! python -c "import sklearn" 2>/dev/null; then
    echo -e "${RED}✗ scikit-learn not installed${NC}"
    echo "Installing scikit-learn..."
    pip install scikit-learn
fi

# Verify Python being used
PYTHON_PATH=$(which python)
echo -e "${GREEN}✓ Using Python: $PYTHON_PATH${NC}"

# Verify imports work
echo -e "${GREEN}✓ Verifying imports${NC}"
python -c "import flask; import sklearn; import pandas; print('✓ All imports OK')" || {
    echo -e "${RED}✗ Import verification failed${NC}"
    exit 1
}

# Run the application
echo -e "${GREEN}✓ Starting Flask application${NC}"
echo ""
python app.py
