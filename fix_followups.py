import json

# Read the conversation manager
with open('src/api/conversation_manager.py', 'r') as f:
    lines = f.readlines()

# Find the generate_followup_questions method and update it
new_lines = []
in_method = False
for i, line in enumerate(lines):
    if 'def generate_followup_questions' in line:
        in_method = True
        # Insert the new method
        new_lines.append(line)
        new_lines.append('        """Generate contextual follow-up questions based on the answer"""\n')
        new_lines.append('        import sys\n')
        new_lines.append('        sys.path.append("src/api")\n')
        new_lines.append('        from followup_questions import get_followup_for_gap\n')
        new_lines.append('        \n')
        new_lines.append('        # Map questions to gap types\n')
        new_lines.append('        question_to_gap = {\n')
        new_lines.append('            "So what is stopping your characters from getting what they want?": "missing_conflict",\n')
        new_lines.append('            "Okay but what actually CHANGES from start to finish?": "no_transformation",\n')
        new_lines.append('            "Why should anyone care what happens?": "no_stakes"\n')
        new_lines.append('        }\n')
        new_lines.append('        \n')
        new_lines.append('        # Get the gap type from the current question\n')
        new_lines.append('        current_question = conversation_context.get("current_question", "")\n')
        new_lines.append('        gap_type = question_to_gap.get(current_question)\n')
        new_lines.append('        \n')
        new_lines.append('        if gap_type:\n')
        new_lines.append('            return get_followup_for_gap(gap_type, level=1)\n')
        new_lines.append('        \n')
        continue
    elif in_method and line.strip() and not line.startswith('        '):
        in_method = False
    elif not in_method:
        new_lines.append(line)

# Write back
with open('src/api/conversation_manager.py', 'w') as f:
    f.writelines(new_lines)
    
print("Updated follow-up logic")
