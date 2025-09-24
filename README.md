# S!M - Story !ntelligence Machine

## What is S!M?

S!M is an AI-powered story development assistant designed for documentary filmmakers and producers. It conducts intelligent conversations about documentary projects and generates sophisticated synthesis reports with multiple reading depths.

## How It Works

### 1. Upload Phase
- Users upload a PDF pitch deck or provide a Google Slides URL
- System extracts and analyzes the content

### 2. Conversation Phase
- S!M conducts a 5-turn conversation asking targeted questions
- Questions adapt based on story type and previous answers
- Uses "Story Personalities" to explore different narrative angles

### 3. Synthesis Phase
- Generates comprehensive story analysis with three reading modes:
  - **Quick (30 sec)**: Bullet points of strengths, gaps, and verdict
  - **Standard (2 min)**: Full analysis with detailed insights
  - **Deep (5 min)**: Includes 4 academic framework analyses

## Key Features

### Story Personalities
- Structuralist: Focuses on narrative architecture
- Emotional Archaeologist: Explores character depth
- Access Investigator: Examines feasibility
- Theme Hunter: Identifies deeper meanings
- Conflict Specialist: Analyzes tension and drama

### Academic Framework Enhancement
- **Cognitive Load Theory**: Analyzes information density and pacing
- **Liminality Theory**: Identifies threshold moments and transitions
- **Social Identity Theory**: Maps group dynamics and loyalties
- **Documentary Modes**: Suggests filmmaking approaches (observational, participatory, etc.)

## Technology Stack

- **Backend**: Flask + Python
- **AI**: OpenAI GPT-3.5/4
- **Database**: Supabase (PostgreSQL)
- **Frontend**: HTML/CSS/JavaScript (vanilla)

## Current Status

MVP complete with:
- ✅ File upload and text extraction
- ✅ 5-turn conversation system
- ✅ Baseline synthesis generation
- ✅ Academic framework enhancement
- ✅ Three reading modes UI

Needs implementation:
- ⏳ Frontend-backend connection
- ⏳ User authentication
- ⏳ PDF export functionality
- ⏳ Google Slides import
- ⏳ Session management

## For Developers

See `DEVELOPER_README.md` for technical setup instructions.
See `API_DOCUMENTATION.md` for endpoint specifications.
See `SUPABASE_SCHEMA.md` for database structure.

## Patent Pending

S!M - Story !ntelligence Machine is patent pending technology.

## Multi-Company Authentication (MVP)

The system includes pre-configured company accounts for data separation:

### Test Accounts:
- Company 1: prodco1 / Demo2024!
- Company 2: prodco2 / Test2024!
- Company 3: prodco3 / Pilot2024!
- Company 4: prodco4 / Story2024!
- Company 5: prodco5 / Develop2024!

### Data Separation:
- Each company's conversations are isolated by company_id
- Users table links to companies table
- All queries filter by company_id for data isolation

### Implementation Status:
- ✅ Companies table created
- ✅ User authentication schema
- ✅ Data separation by company_id
- ⏳ Login page UI needs connection
- ⏳ Session management needs implementation

## Test Accounts for Development

For testing the multi-company authentication system, use these pre-configured accounts:

| Username | Password | Company Description |
|----------|----------|-------------------|
| prodco1 | Demo2024! | Documentary House |
| prodco2 | Test2024! | TrueCrime Productions |
| prodco3 | Pilot2024! | Netflix Originals |
| prodco4 | Story2024! | Indie Films Co |
| prodco5 | Develop2024! | Test Company |

**Note:** These accounts are for development and testing only. Production deployment should implement proper user registration and secure authentication.

## Security Notes

- Test passwords are visible in this README for development convenience
- Production deployment must use secure password storage (hashed/salted)
- Implement proper session management before production use
- Add SSL/HTTPS for all authentication endpoints
