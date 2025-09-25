import re

# Read the file
with open('academic_frameworks.py', 'r') as f:
    content = f.read()

# Find the frameworks dictionary and add the new one
old_dict = """        self.frameworks = {
            'cognitive_load': self._analyze_cognitive_load,
            'liminality': self._analyze_liminality, 
            'social_identity': self._analyze_social_identity
        }"""

new_dict = """        self.frameworks = {
            'cognitive_load': self._analyze_cognitive_load,
            'liminality': self._analyze_liminality, 
            'social_identity': self._analyze_social_identity,
            'documentary_mode': self._analyze_documentary_mode
        }"""

content = content.replace(old_dict, new_dict)

# Write back
with open('academic_frameworks.py', 'w') as f:
    f.write(content)

print("✅ Updated frameworks dictionary")
