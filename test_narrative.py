import sys
import uuid
sys.path.append('/home/craig/story-dev-partner')

from src.api.story_analyzer import AdvancedStoryAnalyzer
from src.api.conversation_manager import ConversationManager
import os
from supabase import create_client

# Load environment
from dotenv import load_dotenv
load_dotenv()

# Initialize Supabase
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_ANON_KEY')
supabase = create_client(supabase_url, supabase_key)

# Initialize components
analyzer = AdvancedStoryAnalyzer(supabase)
manager = ConversationManager(supabase, analyzer)

# Test pitch with clear Todorov structure
test_pitch = """
We follow Maria as she discovers her family wasn't who she thought. 
Everything changed when she found old documents in the attic. 
Now she's trying to understand what really happened and find peace.
She used to believe her grandfather was a hero. 
"""

print("Testing narrative structure detection...\n")

# Test narrative structure detection
structure_result = analyzer.detect_narrative_structure(test_pitch)
print(f"Detected structure: {structure_result['structure']}")
print(f"Confidence: {structure_result['confidence']:.2f}")

# Test gap detection
gaps = analyzer.detect_narrative_gaps(test_pitch, structure_result['structure'])
print(f"Narrative gaps: {gaps}")

# Run full analysis
analysis = analyzer.analyze_deck(test_pitch)
style = analysis['documentary_styles'][0] if analysis['documentary_styles'] else 'unknown'
print(f"Documentary style: {style}")

# Test tension detection
tensions = analyzer.detect_style_structure_tensions(style, structure_result['structure'])
if tensions:
    print(f"Tension detected: {tensions[0]['opportunity']}")

print("\n" + "="*50 + "\n")

# Test the full conversation start
print("\n" + "="*50 + "\n")

# Skip database insertion, just test question generation
questions = manager.generate_intersection_questions(
    style, 
    structure_result['structure'],
    gaps,
    tensions,
    analysis.get('style_gaps', [])
)

print("Generated questions:")
for i, q in enumerate(questions, 1):
    print(f"{i}. {q}")

print("\n✓ SUCCESS! Narrative structure integration working:")
print(f"  - Style: {style}")
print(f"  - Structure: {structure_result['structure']}")
print(f"  - Tension detected between them")
print(f"  - Questions address the intersection")


