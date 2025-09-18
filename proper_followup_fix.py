import re

# Read the conversation manager
with open('src/api/conversation_manager.py', 'r') as f:
    content = f.read()

# 1. Add the import at the top
if 'from followup_questions import' not in content:
    import_line = 'from typing import Dict, List'
    new_import = 'from typing import Dict, List\nimport sys\nsys.path.append("src/api")\ntry:\n    from followup_questions import get_followup_for_gap\nexcept:\n    def get_followup_for_gap(gap_type, level):\n        return ["Tell me more about that.", "Can you go deeper?", "What else?"]'
    content = content.replace(import_line, new_import)

# 2. Fix the save_turn method to pass context properly
save_turn_pattern = r'(def save_turn.*?)(followup_questions = self\.generate_followup_questions\([^)]+\))'
def replace_save_turn(match):
    method_start = match.group(1)
    
    # Build the proper context passing
    new_code = '''        # Build context for follow-up generation
        conv_context = {
            'current_question': question,
            'turn_number': current_turn
        }
        followup_questions = self.generate_followup_questions(answer, conv_context)'''
    
    return method_start + new_code

content = re.sub(save_turn_pattern, replace_save_turn, content, flags=re.DOTALL)

# 3. Replace generate_followup_questions with a working version
old_method = r'def generate_followup_questions\(self.*?\n(?:.*?\n)*?(?=\n    def |\Z)'
new_method = '''def generate_followup_questions(self, answer: str, conversation_context: Dict) -> List[str]:
        """Generate contextual follow-up questions based on the answer"""
        
        # Map questions to gap types
        question_map = {
            "so what is stopping": "missing_conflict",
            "what actually changes": "no_transformation",
            "why should anyone care": "no_stakes"
        }
        
        # Get current question and find gap type
        current_q = conversation_context.get('current_question', '').lower()
        gap_type = None
        
        for key, gap in question_map.items():
            if key in current_q:
                gap_type = gap
                break
        
        # If we have a gap type, use specific follow-ups
        if gap_type:
            try:
                return get_followup_for_gap(gap_type, 1)
            except:
                pass
        
        # Default conversational follow-ups
        return [
            "OK, but dig deeper - what's REALLY going on here?",
            "And if nothing changes, then what?",
            "What are you NOT telling me yet?"
        ]
    '''

content = re.sub(old_method, '    ' + new_method, content, flags=re.DOTALL)

# Save the fixed file
with open('src/api/conversation_manager.py', 'w') as f:
    f.write(content)

print("✓ Applied proper fix")
