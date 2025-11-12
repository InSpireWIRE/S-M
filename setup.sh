#!/bin/bash
echo "Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y tesseract-ocr poppler-utils

echo "Activating virtual environment..."
cd ~/story-dev-partner
source sdp_venv/bin/activate

echo "Setting OpenAI key..."
export OPENAI_API_KEY=$(grep OPENAI_API_KEY .env | cut -d '=' -f2)

echo "Starting Flask..."
PORT=5001 python src/api/app.py
