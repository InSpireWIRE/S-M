# Fix the question matching logic
with open('src/api/conversation_manager.py', 'r') as f:
    content = f.read()

# Replace the faulty comparison
old_logic = """        # Find the gap type for this question
        gap_type = None
        for q, gap in question_gap_map.items():
            if current_question and q.lower() in current_question.lower():
                gap_type = gap
                break"""

new_logic = """        # Find the gap type for this question
        gap_type = None
        for q, gap in question_gap_map.items():
            if current_question and current_question.strip().lower() == q.lower():
                gap_type = gap
                break"""

content = content.replace(old_logic, new_logic)

# Also check that save_turn is passing the context correctly
# Find the save_turn method and ensure it passes the question
if 'context_with_question = {' not in content:
    # Need to add the context building
    old_followup_call = 'followup_questions = self.generate_followup_questions(answer, {})'
    new_followup_call = '''        # Build context for follow-up generation
        context_with_question = {
            'current_question': question,
            'turn_number': current_turn,
            'style_gaps': []
        }
        followup_questions = self.generate_followup_questions(answer, context_with_question)'''
    
    content = content.replace('followup_questions = self.generate_followup_questions(answer, {})', new_followup_call)

with open('src/api/conversation_manager.py', 'w') as f:
    f.write(content)

print("Fixed comparison logic")
