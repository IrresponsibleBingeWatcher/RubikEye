#!/bin/bash
# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install requirements
echo "Checking dependencies..."
pip install -r requirements.txt

# Run the solver
echo "Starting Solver..."
python main.py
