#!/bin/bash
# Training script to run overnight

# Activate virtual environment
source venv/bin/activate

# Set Comet ML API key
export COMET_API_KEY='ISPlcsIm5A8GGUlxXe4AJmfCI'
export COMET_PROJECT_NAME='miso-ozzy-detector'

# Run training
python3 scripts/train.py
