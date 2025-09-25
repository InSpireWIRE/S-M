import re

# Read the file
with open('app_sophisticated.py', 'r') as f:
    lines = f.readlines()

# Find the line with synthesis_text = response.choices[0].message.content
insert_position = None
for i, line in enumerate(lines):
    if 'synthesis_text = response.choices[0].message.content' in line:
        insert_position = i + 1
        # Get the exact indentation from this line
        indent = len(line) - len(line.lstrip())
        break

if insert_position:
    # Create the new code with proper indentation
    spaces = ' ' * indent
    new_code = f'''
{spaces}# ============ STORY METRICS CALCULATION ============
{spaces}try:
{spaces}    from src.api.story_metrics import StoryMetricsAnalyzer
{spaces}    metrics_analyzer = StoryMetricsAnalyzer()
{spaces}    
{spaces}    # Get deck text for metrics
{spaces}    deck_result = supabase.table('pitch_decks').select('*').eq('id', deck_id).single().execute()
{spaces}    deck_text = deck_result.data.get('extracted_text', '') if deck_result.data else ''
{spaces}    
{spaces}    # Get conversation answers
{spaces}    answers_result = supabase.table('conversation_answers').select('*').eq('conversation_id', conversation_id).execute()
{spaces}    
{spaces}    conversation_data = {{
{spaces}        'answers': answers_result.data if answers_result.data else []
{spaces}    }}
{spaces}    
{spaces}    # Calculate metrics
{spaces}    metrics = metrics_analyzer.generate_metrics_summary(deck_text, conversation_data)
{spaces}    print(f"✅ Metrics calculated successfully")
{spaces}    
{spaces}except Exception as e:
{spaces}    print(f"⚠️ Metrics calculation failed: {{e}}")
{spaces}    metrics = None

'''
    
    # Insert the new code
    lines.insert(insert_position, new_code)
    
    # Write back
    with open('app_sophisticated.py', 'w') as f:
        f.writelines(lines)
    
    print(f"✅ Code added successfully at line {insert_position}")
else:
    print("❌ Could not find synthesis_text line")
