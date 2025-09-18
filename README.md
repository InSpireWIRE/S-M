# S!M (Story Intelligence Machine)

Documentary intelligence system using sophisticated NLP gap analysis.
Part of the T!M ecosystem.

## Features
- Analyzes documentary pitches using NLP pattern detection
- Detects styles: ARGUMENT-DRIVEN, DISCOVERY-FOCUSED, PERSONAL-JOURNEY
- Generates context-aware gap questions based on detected style
- Confidence scoring for pattern matches (achieved 30-36% in testing)
- Materials upload supporting multiple formats
- Chunking system for detailed content analysis

## Tech Stack
- Backend: Flask API (Python)
- NLP: SpaCy with custom DocumentaryStyleAnalyzer
- Database: Supabase (8 tables with chunking)
- File Support: pdf, txt, md, rtf, csv, json

## API Endpoints
- `/api/upload-materials` - Upload documentary materials
- `/api/test-analyzer` - Test gap analysis directly
- `/api/process-url` - Process web URLs
- `/api/start-conversation` - Begin coaching session
- `/api/ask-followup` - Generate follow-up questions
- `/api/generate-synthesis` - Create final report

## Status: PRODUCTION READY
All core features tested and operational
