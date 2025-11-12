#!/bin/bash
echo "🚀 Starting S!M Setup..."

# Install system dependencies if missing
if ! command -v pdftoppm &> /dev/null; then
    echo "📦 Installing OCR dependencies..."
    sudo apt-get update -qq
    sudo apt-get install -y -qq poppler-utils tesseract-ocr
fi

# Navigate to S!M directory
cd ~/story-dev-partner
source sdp_venv/bin/activate

# Install Python packages if missing
python -c "import pdf2image" 2>/dev/null || pip install -q pdf2image
python -c "import pytesseract" 2>/dev/null || pip install -q pytesseract

echo "✅ S!M Ready! Starting server..."
export PORT=5000
python3 app_sophisticated.py
