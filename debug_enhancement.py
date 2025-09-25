# Add debug output to the enhancement section
import fileinput
import sys

search_text = "ENABLE_ACADEMIC_FRAMEWORKS = True"
replacement = """ENABLE_ACADEMIC_FRAMEWORKS = True
    print(f"DEBUG: ENABLE_ACADEMIC_FRAMEWORKS = {ENABLE_ACADEMIC_FRAMEWORKS}")
    print(f"DEBUG: questions.data exists = {bool(questions.data)}")
    print(f"DEBUG: answers.data exists = {bool(answers.data)}")"""

with open('app_sophisticated.py', 'r') as f:
    content = f.read()

content = content.replace(search_text, replacement)

with open('app_sophisticated.py', 'w') as f:
    f.write(content)

print("Debug output added!")
