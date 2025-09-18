import sys
import uuid
sys.path.append('/home/craig/story-dev-partner')

from src.api.upload_handler import UploadHandler
from src.api.story_analyzer import AdvancedStoryAnalyzer
from src.api.conversation_manager import ConversationManager
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

# Initialize
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_ANON_KEY')
supabase = create_client(supabase_url, supabase_key)

analyzer = AdvancedStoryAnalyzer(supabase)
manager = ConversationManager(supabase, analyzer)
upload_handler = UploadHandler(supabase, analyzer)

# Simulate a pitch deck upload
test_deck_content = """
Our documentary follows three families in Detroit whose homes were foreclosed.
Everything changed when the 2008 financial crisis hit their neighborhood.
They used to have stable lives and secure jobs.
Now they're trying to rebuild while fighting the banks.
We'll spend 18 months following their legal battles and personal struggles.
The film will show how they eventually find new ways to define home.
"""

print("Testing full upload and processing flow...\n")

# 1. Test deck upload
deck_data = {
    'title': 'Detroit Foreclosure Test',
    'content': test_deck_content,
    'user_id': str(uuid.uuid4())
}

# Insert deck into database
deck_result = supabase.table('uploaded_decks').insert(deck_data).execute()
deck_id = deck_result.data[0]['id']
print(f"✓ Deck uploaded: {deck_id}")

# 2. Analyze the deck
analysis = analyzer.analyze_deck(test_deck_content)
print(f"✓ Style detected: {analysis['documentary_styles']}")

# 3. Test narrative structure detection
structure_result = analyzer.detect_narrative_structure(test_deck_content)
print(f"✓ Structure detected: {structure_result['structure']}")

# 4. Detect gaps
narrative_gaps = analyzer.detect_narrative_gaps(test_deck_content, structure_result['structure'])
print(f"✓ Gaps found: {narrative_gaps}")

# 5. Detect tensions
style = analysis['documentary_styles'][0] if analysis['documentary_styles'] else 'unknown'
tensions = analyzer.detect_style_structure_tensions(style, structure_result['structure'])
if tensions:
    print(f"✓ Tension: {tensions[0]['tension']}")

# 6. Generate questions
questions = manager.generate_intersection_questions(
    style,
    structure_result['structure'],
    narrative_gaps,
    tensions,
    analysis.get('style_gaps', [])
)

print("\n" + "="*50)
print("Generated Questions:")
for i, q in enumerate(questions, 1):
    print(f"{i}. {q}")

# Clean up test data
supabase.table('uploaded_decks').delete().eq('id', deck_id).execute()
print("\n✓ Test deck cleaned up")
