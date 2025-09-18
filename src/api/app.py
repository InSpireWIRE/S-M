import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from supabase import create_client, Client
import sys
from werkzeug.utils import secure_filename
from upload_handler import DeckUploadHandler
from enhanced_synthesis import EnhancedSynthesizer
from story_analyzer import AdvancedStoryAnalyzer
from conversation_manager import ConversationManager
from auth_system import EnterpriseAuthManager

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env.development")
load_dotenv(env_path)

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins=['*'], supports_credentials=True)

# Initialize Supabase client
url = os.environ.get("SDP_SUPABASE_URL")
key = os.environ.get("SDP_SUPABASE_ANON_KEY")

if not url or not key:
    raise ValueError("Missing Supabase credentials")

supabase: Client = create_client(url, key)

# Initialize analyzers and managers
analyzer = AdvancedStoryAnalyzer(supabase)
conversation_mgr = ConversationManager(supabase, analyzer)
auth = EnterpriseAuthManager(supabase)

# File upload configuration
UPLOAD_FOLDER = '/tmp/uploads'
ALLOWED_EXTENSIONS = {'pdf', 'pptx', 'ppt', 'docx', 'doc', 'txt', 'md', 'rtf', 'csv', 'json'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "project": "S!M"})

@app.route("/api/test-db", methods=["GET"])
def test_db():
    try:
        result = supabase.table("users").select("*").limit(1).execute()
        return jsonify({"status": "connected", "message": "Database connection successful"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/upload-deck', methods=['POST'])
def upload_deck():
    """Handle pitch deck uploads"""
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Process the upload
            handler = DeckUploadHandler(supabase)
            
            # For now, use a test user_id
            result = handler.process_upload(
                filepath, 
                filename, 
                'c50f98ec-1234-5678-9abc-def012345678'
            )
            
            # Clean up temp file
            os.remove(filepath)
            
            return jsonify({
                'message': 'File uploaded successfully',
                'deck_id': result['id'],
                'word_count': result['content_extracted']['word_count']
            }), 200
            
        return jsonify({'error': 'Invalid file type'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/process-url', methods=['POST'])
def process_url():
    """Process deck from URL"""
    try:
        data = request.json
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL required'}), 400
        
        # Detect platform from URL and process accordingly
        if 'vimeo.com' in url or 'youtube.com' in url:
            # Handle video platforms - transcript extraction
            return jsonify({'message': 'Video platform detected - transcript extraction coming soon', 'url': url}), 200
        elif 'dropbox.com' in url or 'paper.dropbox' in url:
            # Handle Dropbox
            return jsonify({'message': 'Dropbox support coming soon', 'url': url}), 200
        elif 'notion.so' in url:
            # Handle Notion export
            return jsonify({'message': 'Notion support coming soon', 'url': url}), 200
        else:
            # Process Google Docs and other URLs with existing handler
            handler = DeckUploadHandler(supabase)
            result = handler.process_url(url, 'c50f98ec-1234-5678-9abc-def012345678')
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/start-conversation', methods=['POST'])
def start_conversation():
    """Start analysis conversation for uploaded deck"""
    try:
        data = request.json
        deck_id = data.get('deck_id')
        
        if not deck_id:
            return jsonify({'error': 'deck_id required'}), 400
        
        result = conversation_mgr.start_conversation(
            deck_id, 
            'c50f98ec-1234-5678-9abc-def012345678'
        )
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/save-answer', methods=['POST'])
def save_answer():
    """Save user's answer to conversation"""
    try:
        data = request.json
        result = conversation_mgr.save_turn(
            data.get('conversation_id'),
            data.get('question'),
            data.get('answer')
        )
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/submit-answers', methods=['POST'])
def submit_answers():
    """Process user answers and generate suggestions"""
    data = request.json
    conversation_id = data.get('conversation_id')
    answers = data.get('answers')  # [{question: "...", answer: "..."}]
    
    # Get original analysis
    conv = supabase.table('conversations').select('*').eq('id', conversation_id).execute()
    original_analysis = conv.data[0]['current_analysis']
    
    # Generate suggestions based on answers
    suggestions = analyzer.generate_suggestions(original_analysis, answers)
    
    # Save the turn
    for qa in answers:
        conversation_mgr.save_turn(conversation_id, qa['question'], qa['answer'])
    
    return jsonify({'suggestions': suggestions}), 200

@app.route('/api/test-analyzer', methods=['POST'])
def test_analyzer():
    """Test the documentary analyzer directly"""
    data = request.json
    content = data.get('content', '')
    
    from analysis.documentary_style_analyzer import DocumentaryStyleAnalyzer
    test_analyzer = DocumentaryStyleAnalyzer()
    result = test_analyzer.analyze_pitch(content)
    
    return jsonify({
        'raw_analysis': result,
        'text_length': len(content),
        'detected_styles': result.get('dominant_styles', []),
        'all_scores': result.get('style_scores', {}),
        'gaps': result.get('gaps', []),
        'confidence': result.get('analysis_confidence', 0)
    }), 200

@app.route('/api/upload-materials', methods=['POST'])
def upload_materials():
    """Handle various documentary materials uploads (pitch decks, episode breakdowns, scripts, etc)"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        material_type = request.form.get('type', 'general')  # pitch_deck, episode_breakdown, script, etc
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process different material types
        if material_type == 'episode_breakdown':
            # Extract episode structure and analyze narrative arc
            with open(filepath, 'r') as f:
                content = f.read()
            from analysis.documentary_style_analyzer import DocumentaryStyleAnalyzer
            style_analyzer = DocumentaryStyleAnalyzer()
            analysis = style_analyzer.analyze_pitch(content)
        elif material_type == 'script':
            # Parse script format and identify key scenes
            with open(filepath, 'r') as f:
                content = f.read()
            from analysis.documentary_style_analyzer import DocumentaryStyleAnalyzer
            style_analyzer = DocumentaryStyleAnalyzer()
            analysis = style_analyzer.analyze_pitch(content)
        else:
            # Check if it's a text file
            if filename.endswith('.txt'):
                with open(filepath, 'r') as f:
                    content = f.read()
                from analysis.documentary_style_analyzer import DocumentaryStyleAnalyzer
                style_analyzer = DocumentaryStyleAnalyzer()
                analysis = style_analyzer.analyze_pitch(content)
            else:
                # Use existing deck handler for other formats
                handler = DeckUploadHandler(supabase)
                result = handler.process_upload(filepath, filename, 'c50f98ec-1234-5678-9abc-def012345678')
                analysis = result
        
        # Clean up temp file
        os.remove(filepath)
        
        return jsonify({
            'message': f'{material_type} uploaded successfully',
            'material_type': material_type,
            'analysis': analysis
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ask-followup', methods=['POST'])
def ask_followup():
    """Generate follow-up question based on a single answer"""
    data = request.json
    conversation_id = data.get('conversation_id')
    original_question = data.get('question')
    user_answer = data.get('answer')
    
    # Get conversation context
    conv = supabase.table('conversations').select('*').eq('id', conversation_id).execute()
    original_analysis = conv.data[0]['current_analysis']
    
    # Generate follow-up question based on the answer
    followup = analyzer.generate_followup_question(original_question, user_answer, original_analysis)
    
    # Save this turn
    conversation_mgr.save_turn(conversation_id, original_question, user_answer)
    
    return jsonify({
        'followup_question': followup,
        'conversation_id': conversation_id
    }), 200

@app.route('/api/generate-synthesis', methods=['POST'])
def generate_synthesis():
    """Generate synthesis report from completed conversation"""
    data = request.json
    conversation_id = data.get('conversation_id')
    
    # Get all turns with answers
    turns = supabase.table('conversation_turns')\
        .select('*')\
        .eq('conversation_id', conversation_id)\
        .order('turn_number')\
        .execute()
    
    # Get original conversation data
    conv = supabase.table('conversations')\
        .select('*')\
        .eq('id', conversation_id)\
        .execute()
    
    if not conv.data or not turns.data:
        return jsonify({'error': 'Conversation not found'}), 404
    
    original_gaps = conv.data[0]['metadata'].get('analysis', {}).get('style_gaps', [])
    
    # Build synthesis
    synthesis = {
        'conversation_id': conversation_id,
        'total_exchanges': len([t for t in turns.data if t.get('user_response')]),
        'gaps_identified': original_gaps,
        'gaps_addressed': [],
        'key_insights': [],
        'strengths': [],
        'next_steps': []
    }
    
    # Analyze each Q&A pair
    for turn in turns.data:
        if turn.get('user_response'):
            question = turn['system_prompt']
            answer = turn['user_response']
            
            # Check which gaps were addressed
            if 'conflict' in question.lower() or 'stopping' in question.lower():
                if len(answer) > 20:
                    synthesis['gaps_addressed'].append('missing_conflict')
                    
            if 'change' in question.lower() or 'transformation' in question.lower():
                if len(answer) > 20:
                    synthesis['gaps_addressed'].append('no_transformation')
                    
            if 'care' in question.lower() or 'stakes' in question.lower():
                if len(answer) > 20:
                    synthesis['gaps_addressed'].append('no_stakes')
            
            # Extract insights
            synthesis['key_insights'].append({
                'question': question,
                'answer': answer,
                'turn': turn['turn_number']
            })
    
    # Identify strengths from answers
    all_answers = ' '.join([str(t.get('user_response', '') or '') for t in turns.data if t.get('user_response')])
    if 'trust' in all_answers.lower() or 'relationship' in all_answers.lower():
        synthesis['strengths'].append('Strong relationship with subjects established')
    if 'access' in all_answers.lower() or 'exclusive' in all_answers.lower():
        synthesis['strengths'].append('Unique access or perspective identified')
    if 'years' in all_answers.lower() or 'months' in all_answers.lower():
        synthesis['strengths'].append('Long-term commitment to story demonstrated')
    
    # Generate next steps based on remaining gaps
    remaining_gaps = [g for g in original_gaps 
                      if g['type'] not in synthesis['gaps_addressed']]
    
    for gap in remaining_gaps[:3]:  # Top 3 remaining issues
        synthesis['next_steps'].append({
            'priority': gap['severity'],
            'action': gap['suggestion'],
            'gap_type': gap['type']
        })
    
    # Enhanced AI analysis if requested
    use_ai = data.get('use_ai', False)
    if use_ai:
        enhancer = EnhancedSynthesizer()
        cost = enhancer.estimate_cost(turns.data)
        if cost < 0.10:
            ai_insights = enhancer.analyze_conversation(
                turns.data, 
                conv.data[0]['metadata'].get('analysis', {})
            )
            synthesis['ai_analysis'] = ai_insights
            synthesis['cost'] = cost
    
    # Add standard next steps
    synthesis['next_steps'].append({
        'priority': 'medium',
        'action': 'Create a one-page pitch document incorporating these insights',
        'gap_type': 'documentation'
    })
    
    return jsonify(synthesis), 200

@app.route('/api/register', methods=['POST'])
def register_company():
    """Self-service company registration"""
    data = request.json
    result = auth.register_company(
        data.get('company_name'),
        data.get('email'),
        data.get('password')
    )
    return jsonify(result), 200 if result.get('success') else 400

@app.route('/api/login', methods=['POST'])
def login():
    """User login"""
    data = request.json
    result = auth.login(
        data.get('email'),
        data.get('password')
    )
    return jsonify(result), 200 if result.get('success') else 401

if __name__ == "__main__":
    port = int(os.environ.get("SDP_API_PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=True)