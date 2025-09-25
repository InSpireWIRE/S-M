#!/usr/bin/env python3
import sys

# Read the current file
with open('app_sophisticated.py', 'r') as f:
    content = f.read()

# Check if enhancement already exists
if 'ACADEMIC FRAMEWORK ENHANCEMENT' in content:
    print("Enhancement already exists!")
    sys.exit(0)

# Find where to insert (after synthesis_text = response.choices[0].message.content)
search_line = 'synthesis_text = response.choices[0].message.content'
if search_line not in content:
    print(f"ERROR: Cannot find '{search_line}'")
    sys.exit(1)

# The enhancement code to add
enhancement = '''
    
    # ============ ACADEMIC FRAMEWORK ENHANCEMENT ============
    ENABLE_ACADEMIC_FRAMEWORKS = True
    if ENABLE_ACADEMIC_FRAMEWORKS:
        try:
            print("Applying academic framework analysis...")
            framework_conversation_data = {
                'questions': questions.data if questions.data else [],
                'answers': answers.data if answers.data else []
            }
            from academic_frameworks import AcademicFrameworkAnalyzer
            analyzer = AcademicFrameworkAnalyzer(openai)
            enhanced_synthesis_text = analyzer.enhance_synthesis(
                synthesis_text,
                framework_conversation_data,
                ['cognitive_load', 'liminality', 'social_identity']
            )
            synthesis_text = enhanced_synthesis_text
            print("Academic frameworks applied successfully")
        except Exception as e:
            print(f"Framework enhancement failed: {e}")
    # ============ END OF ENHANCEMENT ============
'''

# Insert the enhancement
lines = content.split('\n')
new_lines = []
for line in lines:
    new_lines.append(line)
    if search_line in line:
        # Add enhancement after this line
        new_lines.append(enhancement)
        print(f"✅ Inserting enhancement after: {line.strip()}")

# Write back
with open('app_sophisticated.py', 'w') as f:
    f.write('\n'.join(new_lines))

print("✅ Enhancement added successfully!")
print("Now checking if it worked...")

# Verify
with open('app_sophisticated.py', 'r') as f:
    if 'ACADEMIC FRAMEWORK ENHANCEMENT' in f.read():
        print("✅ VERIFIED: Enhancement is now in the file!")
    else:
        print("❌ ERROR: Enhancement still not in file")
