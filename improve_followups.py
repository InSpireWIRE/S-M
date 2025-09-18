import json

# Read the original conversation manager
with open('src/api/conversation_manager.py', 'r') as f:
    content = f.read()

# First, let's add the import at the top of the file
import_section = """import uuid
from datetime import datetime
from typing import Dict, List
import sys
sys.path.append('src/api')
from followup_questions import get_followup_for_gap"""

content = content.replace("""import uuid
from datetime import datetime
from typing import Dict, List""", import_section)

# Now replace the generate_followup_questions method with a proper implementation
old_method_start = '    def generate_followup_questions(self, answer: str, conversation_context: Dict) -> List[str]:'
old_method_end = '        # Default fallback questions'

# Find where the method starts and ends
start_idx = content.find(old_method_start)
if start_idx == -1:
    print("ERROR: Could not find generate_followup_questions method")
else:
    # Find the next method definition after this one
    next_method_idx = content.find('\n    def ', start_idx + len(old_method_start))
    
    # Replace the entire method
    new_method = '''    def generate_followup_questions(self, answer: str, conversation_context: Dict) -> List[str]:
        """Generate contextual follow-up questions based on the answer and gap type"""
        
        # Map initial questions to their gap types
        question_gap_map = {
            "So what is stopping your characters from getting what they want?": "missing_conflict",
            "Okay but what actually CHANGES from start to finish?": "no_transformation", 
            "Why should anyone care what happens?": "no_stakes",
            "How did you get access no one else has?": "unclear_access"
        }
        
        # Get the current question from context (passed from save_turn)
        current_question = conversation_context.get('current_question', '')
        
        # Find the gap type for this question
        gap_type = None
        for q, gap in question_gap_map.items():
            if current_question and q.lower() in current_question.lower():
                gap_type = gap
                break
        
        # If we found a gap type, use conversational follow-ups
        if gap_type:
            # Determine level based on turn number
            turn_number = conversation_context.get('turn_number', 1)
            level = 2 if turn_number > 2 else 1
            return get_followup_for_gap(gap_type, level)
        
        # Analyze the answer for people mentioned
        doc = self.nlp(answer)
        people = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
        
        # If they mention people, ask conversational questions about them
        if people:
            person = people[0]
            return [
                f"OK but what makes {person} worth following for months?",
                f"What's {person} risking by letting you film?",
                f"How long did it take {person} to trust you?"
            ]
        
        # Default conversational follow-ups
        return [
            "OK, but dig deeper - what's REALLY going on here?",
            "And if nothing changes, then what?",
            "What are you NOT telling me yet?"
        ]
'''
    
    # Replace the method
    content = content[:start_idx] + new_method + content[next_method_idx:]
    
    print("Successfully updated generate_followup_questions method")

# Also update save_turn to pass the question in context
save_turn_old = '        # Generate follow-up questions'
save_turn_new = '''        # Generate follow-up questions with context about the current question
        context_with_question = {
            'current_question': question,
            'turn_number': current_turn,
            'style_gaps': conversation_context.get('style_gaps', [])
        }'''

content = content.replace(save_turn_old, save_turn_new)

# Fix the generate_followup_questions call in save_turn
content = content.replace(
    'followup_questions = self.generate_followup_questions(answer, {})',
    'followup_questions = self.generate_followup_questions(answer, context_with_question)'
)

# Save the updated file
with open('src/api/conversation_manager.py', 'w') as f:
    f.write(content)

print("✓ Complete update applied successfully")
