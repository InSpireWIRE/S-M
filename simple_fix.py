with open('src/api/conversation_manager.py', 'r') as f:
    content = f.read()

# Find and replace the generate_followup_questions call with proper context
content = content.replace(
    'followup_questions = self.generate_followup_questions(answer, {})',
    'followup_questions = self.generate_followup_questions(answer, {"current_question": question})'
)

with open('src/api/conversation_manager.py', 'w') as f:
    f.write(content)

print("Applied simple fix")
