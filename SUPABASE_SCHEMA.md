# Supabase Database Schema

## Required Tables:
- conversations (id, status, created_at)
- uploaded_decks (id, conversation_id, original_filename, extracted_text)
- conversation_questions (id, conversation_id, question_number, question_text)
- conversation_answers (id, conversation_id, question_number, answer_text)  
- conversation_synthesis (id, conversation_id, baseline_synthesis, enhanced_synthesis, frameworks_applied)
