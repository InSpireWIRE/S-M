# Add this to the start_conversation method after analysis = self.analyzer.analyze_deck(deck_text):

# Save documentary style analysis
conversation_data = {
    'id': conversation_id,
    'user_id': user_id,
    'deck_id': deck_id,
    'status': 'active',
    'current_analysis': analysis,
    'documentary_styles': analysis.get('documentary_styles', []),
    'style_gaps': analysis.get('style_gaps', []),
    'style_confidence': analysis.get('analysis_confidence', 0.0)
}

# Update generate_questions to use gap mappings
def generate_style_aware_questions(self, analysis):
    """Generate questions based on sophisticated style gaps"""
    questions = []
    
    # Get questions from detected gaps
    for gap in analysis.get('style_gaps', []):
        gap_type = gap.get('type')
        
        # Query the gap_question_mappings table
        result = self.supabase.table('gap_question_mappings').select("*").eq('gap_type', gap_type).execute()
        if result.data:
            questions.append(result.data[0]['primary_question'])
    
    # Add style-specific questions
    for style in analysis.get('documentary_styles', []):
        style_result = self.supabase.table('documentary_patterns').select("questions").eq('style_name', style).execute()
        if style_result.data:
            style_questions = style_result.data[0]['questions']
            questions.extend(style_questions[:2])  # Add first 2 questions from this style
    
    return questions[:5]  # Return top 5 questions
