# Fix the OpenAI API format in academic_frameworks.py

with open('academic_frameworks.py', 'r') as f:
    content = f.read()

# Replace new OpenAI format with old format
content = content.replace('self.openai.chat.completions.create', 'openai.ChatCompletion.create')
content = content.replace('response.choices[0].message.content', 'response.choices[0].message.content')
content = content.replace('model="gpt-3.5-turbo-16k"', 'model="gpt-3.5-turbo-16k"')
content = content.replace('model="gpt-4"', 'model="gpt-3.5-turbo-16k"')  # Use same model as main app

# Remove the openai parameter from __init__ since we'll use the global import
content = content.replace('def __init__(self, openai_client):', 'def __init__(self):')
content = content.replace('self.openai = openai_client', 'pass  # Using global openai')

# Write back
with open('academic_frameworks.py', 'w') as f:
    f.write(content)

print("✅ Fixed OpenAI API format")
