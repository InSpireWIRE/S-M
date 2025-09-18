# S!M (Story Intelligence Machine)

Documentary intelligence system using sophisticated NLP gap analysis.
Part of the T!M ecosystem.

## What S!M Does
- Analyzes documentary pitches and materials
- Detects documentary styles using NLP patterns
- Generates intelligent, context-aware gap questions
- Provides confidence scoring for detected patterns

## Tech Stack
- Backend: Flask API (Python)
- NLP: SpaCy with custom pattern detection
- Database: Supabase (8 tables)
- Analysis: DocumentaryStyleAnalyzer with 30%+ confidence rates

## Current Status
✅ Production Ready Backend
✅ Sophisticated Gap Analysis Working
✅ Materials Upload (pdf, txt, md, rtf, csv, json)
✅ URL Processing (Google Docs, Vimeo detection ready)
✅ Chunking System Operational

## Achieved Confidence Rates
- ARGUMENT-DRIVEN: 36.1%
- DISCOVERY-FOCUSED: 32.3%
- Style-specific gaps generating correctly

## API Endpoints
- `/api/upload-materials` - Upload pitch materials
- `/api/test-analyzer` - Test gap analysis
- `/api/process-url` - Process URLs
- `/api/start-conversation` - Begin analysis session
- `/api/generate-synthesis` - Create final report
