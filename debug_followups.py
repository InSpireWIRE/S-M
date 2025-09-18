# Add debug logging to see what's happening
with open('src/api/conversation_manager.py', 'r') as f:
    content = f.read()

# Add debug prints to generate_followup_questions
debug_code = '''    def generate_followup_questions(self, answer: str, conversation_context: Dict) -> List[str]:
        """Generate contextual follow-up questions based on the answer and gap type"""
        
        # DEBUG: Print what we received
        print(f"DEBUG: Received context: {conversation_context}")
        print(f"DEBUG: Current question: {conversation_context.get('current_question', 'NONE')}")
        
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
            if current_question and current_question.strip().lower() == q.lower():
                gap_type = gap
                print(f"DEBUG: Matched gap type: {gap_type}")
                break
        
        print(f"DEBUG: Final gap_type: {gap_type}")
        
        # If we found a gap type, use conversational follow-ups
        if gap_type:
            # Determine level based on turn number
            turn_number = conversation_context.get('turn_number', 1)
            level = 2 if turn_number > 2 else 1
            return get_followup_for_gap(gap_type, level)
'''

# Replace the method
import re
pattern = r'    def generate_followup_questions\(self, answer: str, conversation_context: Dict\) -> List\[str\]:.*?(?=    def |\Z)'
content = re.sub(pattern, debug_code, content, flags=re.DOTALL)

with open('src/api/conversation_manager.py', 'w') as f:
    f.write(content)

print("Added debug logging")
