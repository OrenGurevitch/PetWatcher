#!/bin/bash
# Training script to run overnight
#
# IMPORTANT: Set your COMET_API_KEY before running:
# export COMET_API_KEY='your-api-key-here'
#
# Then run: ./run_training.sh

# Activate virtual environment
source venv/bin/activate

# Check if API key is set
if [ -z "$COMET_API_KEY" ]; then
    echo "❌ ERROR: COMET_API_KEY environment variable not set!"
    echo ""
    echo "Please set your API key first:"
    echo "  export COMET_API_KEY='your-api-key-here'"
    echo ""
    echo "Then run this script again."
    exit 1
fi

# Set project name
export COMET_PROJECT_NAME='miso-ozzy-detector'

# Run training
python3 scripts/train.py
