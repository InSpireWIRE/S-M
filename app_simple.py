import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({"status": "S!M Backend Running"})

@app.route('/api/upload-deck', methods=['POST', 'OPTIONS'])
def upload_deck():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        file = request.files.get('file')
        if file:
            return jsonify({
                "deck_id": "deck_" + str(hash(file.filename))[:8],
                "status": "success",
                "message": f"Uploaded {file.filename}"
            })
        return jsonify({"error": "No file"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/start-conversation', methods=['POST', 'OPTIONS'])
def start_conversation():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json() or {}
        return jsonify({
            "conversation_id": "conv_123",
            "deck_id": data.get('deck_id'),
            "questions": [
                "What transformation occurs?",
                "Who is your audience?",
                "What's your unique access?"
            ]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
