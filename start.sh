#!/bin/bash

echo "=========================================="
echo "Student Performance Prediction System"
echo "Quick Start Script"
echo "=========================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "[1/4] Creating virtual environment..."
    python3 -m venv venv
else
    echo "[1/4] Virtual environment already exists"
fi

# Activate virtual environment
echo "[2/4] Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "[3/4] Installing dependencies..."
pip install Flask scikit-learn pandas --quiet

# Train model if not exists
if [ ! -f "model.pkl" ]; then
    echo "[4/4] Training machine learning model..."
    python train_model.py
else
    echo "[4/4] Model already trained"
fi

echo ""
echo "=========================================="
echo "Setup complete! Starting application..."
echo "=========================================="
echo ""

# Run the application
python app.py
