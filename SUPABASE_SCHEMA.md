# S!M (Story Intelligence Machine) Supabase Database Schema

## Active Tables (8 total)

1. **uploaded_decks** - Document/pitch storage
2. **deck_chunks** - Chunked content for analysis  
3. **conversations** - Analysis sessions
4. **conversation_turns** - Q&A exchanges
5. **deck_synthesis** - Final reports
6. **documentary_patterns** - NLP patterns
7. **frameworks** - Documentary theories
8. **gap_question_mappings** - Gap-specific questions

## Chunking Confirmed Working
- AdvancedDocumentaryChunker active
- Chunks stored with deck_id reference
- Metadata preserved for each chunk
