with open('academic_frameworks.py', 'r') as f:
    content = f.read()

# Update the start line of Nichols output
old_line = 'Start with: [Framework: Documentary Modes - Bill Nichols]'
new_line = 'Start with: [Framework: Documentary Modes - Bill Nichols]\nImmediately follow with: (Based on Bill Nichols\' theoretical framework)'

content = content.replace(old_line, new_line)

with open('academic_frameworks.py', 'w') as f:
    f.write(content)

print("✅ Added attribution to Nichols section")
