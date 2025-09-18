# Read the file
with open('src/api/conversation_manager.py', 'r') as f:
    lines = f.readlines()

# Find the problem around line 237
for i in range(230, min(245, len(lines))):
    # Fix any lines that have wrong indentation in this area
    if "'conversation_id': conversation_id," in lines[i]:
        # This line should have proper indentation (likely 12 spaces based on context)
        lines[i] = "            'conversation_id': conversation_id,\n"
        print(f"Fixed indentation at line {i}")

# Write back
with open('src/api/conversation_manager.py', 'w') as f:
    f.writelines(lines)

print("✓ Fixed indentation")
