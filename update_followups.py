# Script to update the conversation manager with better follow-ups
import re

# Read the current file
with open('src/api/conversation_manager.py', 'r') as f:
    content = f.read()

# Find and replace the generate_followup_questions method
new_method = '''    def generate_followup_questions(self, answer: str, conversation_context: Dict) -> List[str]:
        """Generate contextual follow-up questions based on the answer and gap type"""
        from followup_questions import get_followup_for_gap
        
        # Try to determine which gap this relates to
        # This is a simple implementation - could be enhanced
        gaps = conversation_context.get('style_gaps', [])
        
        # For now, use the first gap type (could be smarter about matching)
        if gaps:
            gap_type = gaps[0].get('type', '')
            return get_followup_for_gap(gap_type, level=1)
        
        # Fallback to analyzing the answer content
        doc = self.nlp(answer)
        
        # If they mention specific people, ask about them
        people = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
        if people:
            return [
                f"Tell me more about {people[0]}'s role in the story.",
                f"How did you get access to {people[0]}?",
                f"What makes {people[0]} the right subject for this documentary?"
            ]
        
        # Default conversational follow-ups
        return [
            "OK, but dig deeper - what's really going on here?",
            "How does this connect to the bigger story?",
            "What are you NOT telling me yet?"
        ]'''

# Find the method and replace it
pattern = r'def generate_followup_questions\(self.*?\n(?:.*?\n)*?(?=\n    def |\Z)'
content = re.sub(pattern, new_method.strip() + '\n', content, flags=re.DOTALL)

# Write back
with open('src/api/conversation_manager.py', 'w') as f:
    f.write(content)

print("Updated generate_followup_questions method")
