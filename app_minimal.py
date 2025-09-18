import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client, Client

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"]}})

# Initialize Supabase
url = "https://izhvyvicvbbuiconxitm.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml6aHZ5dmljdmJidWljb254aXRtIiwicm9sZSI6ImFub24iLCJpYXQiOjE2ODQ4NjQ4MDAsImV4cCI6MjAwMDQ0MDgwMH0.YOUR_KEY_ENDING"
supabase: Client = create_client(url, key)

@app.route('/')
def home():
    return jsonify({"status": "S!M Backend Running with Database"})

@app.route('/api/upload-deck', methods=['POST', 'OPTIONS'])
def upload_deck():
    if request.method == 'OPTIONS':
        return '', 200
    
    # Get file from request
    file = request.files.get('file')
    if file:
        # Store in Supabase
        deck_data = {
            'filename': file.filename,
            'content': file.read().decode('utf-8', errors='ignore')[:1000]  # First 1000 chars for now
        }
        result = supabase.table('uploaded_decks').insert(deck_data).execute()
        
        return jsonify({
            "deck_id": result.data[0]['id'],
            "status": "success",
            "message": f"Uploaded {file.filename}"
        })
    
    return jsonify({"error": "No file provided"}), 400

@app.route('/api/start-conversation', methods=['POST', 'OPTIONS'])
def start_conversation():
    if request.method == 'OPTIONS':
        return '', 200
    
    data = request.get_json() or {}
    deck_id = data.get('deck_id')
    
    # Create conversation in database
    conv_data = {'deck_id': deck_id}
    result = supabase.table('conversations').insert(conv_data).execute()
    
    return jsonify({
        "conversation_id": result.data[0]['id'],
        "deck_id": deck_id,
        "questions": [
            "What transformation does your main character undergo?",
            "What unique access do you have to tell this story?",
            "Why should audiences care about this story now?"
        ]
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
