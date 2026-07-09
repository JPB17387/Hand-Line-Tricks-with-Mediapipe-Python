#!/bin/bash
# Hand Tricks - Launch Script for macOS/Linux
# This script activates the virtual environment and runs the application

cd "$(dirname "$0")"

echo "Activating virtual environment..."
source .venv/bin/activate

echo ""
echo "Starting Hand Tricks..."
echo ""

python main.py
