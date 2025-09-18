# Read the file
with open('src/api/conversation_manager.py', 'r') as f:
    lines = f.readlines()

# Find save_turn method and fix the followup_questions call
for i in range(len(lines)):
    if 'def save_turn' in lines[i]:
        # Look for the generate_followup_questions call in this method
        for j in range(i, min(i+50, len(lines))):
            if 'self.generate_followup_questions' in lines[j]:
                # Check what's being passed
                if 'answer, {}' in lines[j]:
                    # Replace with proper context
                    lines[j] = '        followup_questions = self.generate_followup_questions(answer, {"current_question": question, "turn_number": current_turn})\n'
                    print(f"Fixed line {j}: passing proper context")
                elif 'conv_context' not in lines[j]:
                    # Need to add context building before this line
                    context_lines = [
                        '        # Build context for follow-up generation\n',
                        '        conv_context = {"current_question": question, "turn_number": current_turn}\n',
                        '        followup_questions = self.generate_followup_questions(answer, conv_context)\n'
                    ]
                    lines[j:j+1] = context_lines
                    print(f"Added context at line {j}")
                break
        break

# Write back
with open('src/api/conversation_manager.py', 'w') as f:
    f.writelines(lines)

print("✓ Fixed save_turn to pass context")
