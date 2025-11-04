#!/bin/bash
# ESP Backend Console Startup Script

echo "=================================="
echo "ESP Backend Console - Starting"
echo "=================================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

# Check if config.json exists
if [ ! -f "config.json" ]; then
    echo "Error: config.json not found!"
    exit 1
fi

echo "✓ Python 3 found"
echo "✓ Configuration file found"
echo ""

# Set environment variables if not already set
if [ -z "$ESP_PRIMARY_KEY" ]; then
    echo "Note: ESP_PRIMARY_KEY not set in environment"
fi

if [ -z "$TILDA_API_KEY" ]; then
    echo "Note: TILDA_API_KEY not set in environment"
fi

echo ""
echo "Starting backend server..."
echo ""

# Start the backend
python3 backend.py
